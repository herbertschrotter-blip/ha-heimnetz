"""Ausfälle des Pi (18.11.2026): Herzschlag und Marke beim Beenden, Speicher alle 5 min mit Warnung, Ausfallbericht
nach einem unsauberen Ende – mit nachgebautem Supervisor."""

import time
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.heimnetz import ausfall as ad
from custom_components.heimnetz.logik import ausfall as af

MEM_GUT = "MemTotal: 16384000 kB\nMemAvailable: 11000000 kB\nSwapTotal: 4194304 kB\nSwapFree: 4000000 kB\n"
MEM_KNAPP = (
    "MemTotal: 16384000 kB\nMemAvailable: 900000 kB\nSwapTotal: 4194304 kB\nSwapFree: 0 kB\n"
)


class SupervisorNachbau:
    da = True
    pi = 0.0
    boot = ""

    async def speicher(self):
        return {"Home Assistant": 10900, "Supervisor": 300, "Claude Terminal": 4400}

    async def pi_start(self):
        return SupervisorNachbau.pi

    async def voriger_boot(self):
        return SupervisorNachbau.boot


@pytest.fixture
def supervisor():
    with patch.object(ad, "Supervisor", lambda _h: SupervisorNachbau()):
        yield SupervisorNachbau


async def _laden(hass, eintrag):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    return eintrag.runtime_data


async def test_herzschlag_und_sauber_beim_entladen(
    hass: HomeAssistant, eintrag, box, pi, supervisor
):
    lz = await _laden(hass, eintrag)
    dienst = lz.ausfall
    lebt, sauber = dienst._lauf_lesen()
    assert lebt > time.time() - 60 and sauber is None
    assert await hass.config_entries.async_unload(eintrag.entry_id)
    lebt, sauber = dienst._lauf_lesen()
    assert sauber >= lebt, (
        "Neuladen der Integration ist ein sauberes Ende – kein falscher Ausfallbericht"
    )
    await dienst.abruf()
    assert dienst._lauf_lesen() == (lebt, sauber), "nach dem Ende kein Herzschlag mehr"
    with patch.object(ad.Ausfalldienst, "_bericht_spaeter") as bericht:
        await _laden(hass, eintrag)
    bericht.assert_not_called()


async def test_speicher_mitschreiben_und_warnen(hass: HomeAssistant, eintrag, box, pi, supervisor):
    lz = await _laden(hass, eintrag)
    ereignisse = []
    hass.bus.async_listen("heimnetz_warnung", lambda e: ereignisse.append(e.data))
    with patch.object(ad, "_lesen", return_value=MEM_KNAPP):
        await lz.ausfall._speicher_lesen(time.time())
        await lz.ausfall._speicher_lesen(time.time() + 600)  # binnen einer Stunde nur einmal
    await hass.async_block_till_done()
    s = await hass.async_add_executor_job(lz.datenbank.speicherstand_vor, time.time() + 1000)
    assert s.wer["Claude Terminal"] == 4400 and s.frei_mb == 878
    assert [e["art"] for e in ereignisse] == ["waechter"]
    assert ereignisse[0]["nachricht"].startswith("Wächter: Speicher knapp: frei 0,9 GB von 15,6 GB")


async def test_ausfallbericht_nach_unsauberem_ende(
    hass: HomeAssistant, eintrag, box, pi, supervisor
):
    lz = await _laden(hass, eintrag)
    jetzt = time.time()
    # voriger Lauf: lebte bis vor 30 min, ohne Marke „sauber“; Pi seit 10 min neu, Speicher vorher knapp
    lz.ausfall._vorher = (jetzt - 1800, None)
    SupervisorNachbau.pi = jetzt - 600
    SupervisorNachbau.boot = (
        "2026-11-10 01:50:00.000+01:00 homeassistant kernel: Out of memory: Killed process 1 (MainThread) "
        "total-vm:1kB, anon-rss:11000000kB, file-rss:1kB\n"
    )
    await hass.async_add_executor_job(
        lz.datenbank.speicherstand_schreiben,
        af.Speicherstand(jetzt - 1900, 16000, 900, 4096, 0, {"Home Assistant": 10900}),
    )
    ereignisse = []
    hass.bus.async_listen("heimnetz_warnung", lambda e: ereignisse.append(e.data))
    zeilen = await lz.ausfall.bericht()
    await hass.async_block_till_done()
    assert zeilen[0].startswith("Home Assistant lief zuletzt") and "(30 min weg)" in zeilen[0]
    assert zeilen[1].startswith("Der Pi ist neu gestartet") and "ohne Herunterfahren" in zeilen[1]
    assert "Speicher voll" in zeilen[2] and "MainThread" in zeilen[2]
    assert "am meisten: Home Assistant 10,6 GB" in zeilen[3]
    assert ereignisse and ereignisse[0]["nachricht"].startswith(
        "Wächter: Ausfall: Home Assistant lief zuletzt"
    )
    await lz.abruf.async_refresh()
    texte = await hass.async_add_executor_job(
        lz.datenbank.journal_texte, "waechter", jetzt - 10, jetzt + 3600
    )
    assert any(x.startswith("Ausfall:") for _, x in texte)


async def test_kein_bericht_nach_sauberem_ende(hass: HomeAssistant, eintrag, box, pi, supervisor):
    lz = await _laden(hass, eintrag)
    lz.ausfall._vorher = (time.time() - 1800, time.time() - 1700)
    assert await lz.ausfall.bericht() is None
