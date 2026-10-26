"""Laden, Entitäten, Ausfall der Box (G-21), Reparatur-Hinweise, Diagnose, Entladen (G-15)."""

from dataclasses import replace

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heimnetz.box import AnmeldungAbgelehnt, BoxDaten, BoxInfo
from custom_components.heimnetz.const import (
    CONF_FRITZ_EINTRAG,
    CONF_OPENCELLID,
    DOMAIN,
    ISSUE_ANMELDUNG,
    ISSUE_FRITZ_FEHLT,
)
from custom_components.heimnetz.diagnostics import async_get_config_entry_diagnostics
from tests.integration.conftest import box_daten


async def _laden(hass: HomeAssistant, eintrag) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()


def _zustand(hass: HomeAssistant, eintrag, plattform: str, schluessel: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(
        plattform, DOMAIN, f"{eintrag.entry_id}_{schluessel}"
    )
    assert entity_id, schluessel
    return hass.states.get(entity_id).state


async def _neu_abrufen(hass: HomeAssistant, eintrag) -> None:
    await eintrag.runtime_data.abruf.async_refresh()
    await hass.async_block_till_done()


async def test_laden_entitaeten_und_entladen(hass: HomeAssistant, eintrag, box, pi) -> None:
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED
    z = lambda p, k: _zustand(hass, eintrag, p, k)  # noqa: E731
    assert z("sensor", "gesamtstand") == "kritisch"  # Beispieldaten: doppelte IP, fremdes Netz
    assert int(z("sensor", "befunde")) >= 3
    assert z("sensor", "geraete_online") == "5"
    assert (z("sensor", "mobil_technik"), z("sensor", "rsrp_anker"), z("sensor", "rsrq_5g")) == (
        "5G-NSA",
        "-100",
        "-10",
    )
    # WU-0002: Zelle, Entfernung, Nachbarzellen, 5G-PCI als Entitäten (fürs Langzeitarchiv)
    assert (
        z("sensor", "mobil_zelle"),
        z("sensor", "mobil_entfernung"),
        z("sensor", "mobil_nachbarzellen"),
        z("sensor", "pci_5g"),
    ) == ("abcde-0b", "1350", "0", "121")
    assert z("binary_sensor", "pi_internet") == "on"
    db = eintrag.runtime_data.datenbank
    assert db.journal_lesen()[-1].ereignis.art == "start" and db.anzahl()["protokoll"] == 2
    assert await hass.config_entries.async_unload(eintrag.entry_id)
    assert eintrag.state is ConfigEntryState.NOT_LOADED
    assert await hass.config_entries.async_setup(eintrag.entry_id)  # neu laden geht
    await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.LOADED


async def test_box_weg_und_zurueck(hass: HomeAssistant, eintrag, box, pi) -> None:
    await _laden(hass, eintrag)
    box.return_value = BoxDaten(fehler=["FRITZ!Box: Zeitüberschreitung"])
    await _neu_abrufen(hass, eintrag)
    assert _zustand(hass, eintrag, "sensor", "gesamtstand") == "box_fehlt"
    assert _zustand(hass, eintrag, "sensor", "geraete_online") == STATE_UNAVAILABLE
    assert _zustand(hass, eintrag, "sensor", "rsrp_anker") == STATE_UNAVAILABLE
    assert (
        _zustand(hass, eintrag, "binary_sensor", "pi_fritzbox") == "on"
    )  # Prüfung des Pi hängt nicht an TR-064
    box.return_value = box_daten()
    await _neu_abrufen(hass, eintrag)
    assert _zustand(hass, eintrag, "sensor", "geraete_online") == "5"


async def test_einzelner_wert_fehlt_ist_unbekannt(hass: HomeAssistant, eintrag, box, pi) -> None:
    box.return_value = box_daten(mobil=box_daten().mobil.__class__("LTE", False, None, None))
    await _laden(hass, eintrag)
    assert _zustand(hass, eintrag, "sensor", "rsrp_5g") == STATE_UNKNOWN


async def test_ohne_mobilfunk_keine_empfangssensoren(hass: HomeAssistant, eintrag, box, pi) -> None:
    box.return_value = box_daten(mobil=None, ohne_mobilfunk=True)
    await _laden(hass, eintrag)
    assert (
        er.async_get(hass).async_get_entity_id("sensor", DOMAIN, f"{eintrag.entry_id}_rsrp_anker")
        is None
    )


async def test_anmeldung_abgelehnt_gibt_hinweis(hass: HomeAssistant, eintrag, box, pi) -> None:
    box.side_effect = AnmeldungAbgelehnt
    await _laden(hass, eintrag)
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_ANMELDUNG)
    assert _zustand(hass, eintrag, "sensor", "gesamtstand") == "box_fehlt"
    box.side_effect = None
    await _neu_abrufen(hass, eintrag)
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_ANMELDUNG) is None


async def test_fritzbox_tools_fehlt(hass: HomeAssistant, box, pi) -> None:
    eintrag = MockConfigEntry(domain=DOMAIN, data={CONF_FRITZ_EINTRAG: "weg"}, unique_id="weg")
    eintrag.add_to_hass(hass)
    await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.SETUP_ERROR
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_FRITZ_FEHLT)


async def test_diagnose_ohne_namen_und_adressen(hass: HomeAssistant, eintrag, box, pi) -> None:
    await _laden(hass, eintrag)
    diagnose = str(await async_get_config_entry_diagnostics(hass, eintrag))
    for privat in ("00:11:22", "33:44", "Pi (", "fernseher", "geheim", "192.0.2.1"):
        assert privat not in diagnose
    assert "'online': 5" in diagnose


async def test_diagnose_darf_oeffentlich_sein(hass: HomeAssistant, fritz, box, pi) -> None:
    """WU-0006: auch Fehlertexte, Schlüssel, Zellkennungen und Geräte-Tracker kommen nicht in die Diagnose; was beim
    Fehlersuchen hilft (Box-Modell, Netztechnik, Ookla, Messplan, Versionen), schon."""
    box.return_value = box_daten(info=BoxInfo("FRITZ!Box 6860 5G", "268.08.03", 3600, 0.0))
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_FRITZ_EINTRAG: fritz.entry_id},
        options={CONF_OPENCELLID: "pk.geheimer-schluessel"},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    hass.states.async_set("device_tracker.laptop", "home", {"friendly_name": "Laptop-Wohnzimmer"})
    await _laden(hass, eintrag)
    abruf = eintrag.runtime_data.abruf
    abruf.data = replace(
        abruf.data,
        fehler=(
            "Box: keine Antwort von 192.0.2.1 (fernseher, 00:11:22:33:44:02)",
            "Pi: Laptop-Wohnzimmer bei 47.0707, 15.4395 nicht erreichbar",
        ),
    )
    d = await async_get_config_entry_diagnostics(hass, eintrag)
    text = str(d)
    for privat in (
        "pk.geheimer",
        "192.0.2.1",
        "00:11:22",
        "fernseher",
        "Laptop-Wohnzimmer",
        "47.0707",
        "abcde",  # Zellkennung
        "C0FC",  # TAC
        "geheim",  # Kennwort der Box
    ):
        assert privat not in text, privat
    assert d["optionen"][CONF_OPENCELLID] == "**REDACTED**"
    assert d["box"] == {
        "modell": "FRITZ!Box 6860 5G",
        "firmware": "268.08.03",
        "netztechnik": "5G-NSA",
    }
    assert d["speedtest"]["ookla"] is False and "takt_h" in d["speedtest"]["messplan"]
    assert d["version"]["sprache"] == "de" and d["laufzeit"]["fehler"][0].startswith("Box: keine")


async def test_neues_kennwort_in_fritzbox_tools_gilt_ohne_neu_laden(
    hass: HomeAssistant, eintrag, fritz, box, pi
) -> None:
    await _laden(hass, eintrag)
    hass.config_entries.async_update_entry(fritz, data={**fritz.data, CONF_PASSWORD: "neu"})
    await _neu_abrufen(hass, eintrag)
    assert eintrag.runtime_data.abruf.box.zugang.kennwort == "neu"


async def test_fritzbox_tools_spaeter_entfernt(
    hass: HomeAssistant, eintrag, fritz, box, pi
) -> None:
    await _laden(hass, eintrag)
    hass.config_entries.async_update_entry(fritz, data={})  # wie entfernt: kein Zugang mehr
    await _neu_abrufen(hass, eintrag)
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_FRITZ_FEHLT)
    assert _zustand(hass, eintrag, "sensor", "gesamtstand") == "box_fehlt"


async def test_mobilfunk_sensoren_kommen_nach_wenn_box_beim_start_fehlt(
    hass: HomeAssistant, eintrag, box, pi
) -> None:
    box.return_value = BoxDaten(fehler=["FRITZ!Box: weg"])
    await _laden(hass, eintrag)
    registry = er.async_get(hass)
    assert registry.async_get_entity_id("sensor", DOMAIN, f"{eintrag.entry_id}_rsrp_anker") is None
    box.return_value = box_daten()
    await _neu_abrufen(hass, eintrag)
    assert _zustand(hass, eintrag, "sensor", "rsrp_anker") == "-100"


async def test_neustart_behaelt_gedaechtnis_und_protokoll(
    hass: HomeAssistant, eintrag, box, pi
) -> None:
    """Nach einem Neustart von HA keine „Erfassung gestartet“, keine neuen Geräte, keine doppelten Zeilen."""
    await _laden(hass, eintrag)
    vorher = eintrag.runtime_data.datenbank.anzahl()
    assert await hass.config_entries.async_reload(eintrag.entry_id)
    await hass.async_block_till_done()
    db = eintrag.runtime_data.datenbank
    assert db.anzahl() == vorher
    assert [z.ereignis.art for z in db.journal_lesen()].count("start") == 1


async def test_sicherung_haelt_schreiben_an(hass: HomeAssistant, eintrag, box, pi) -> None:
    from custom_components.heimnetz.backup import async_post_backup, async_pre_backup

    await _laden(hass, eintrag)
    db = eintrag.runtime_data.datenbank
    vorher = db.anzahl()["journal"]
    await async_pre_backup(hass)
    box.return_value = BoxDaten(fehler=["weg"])
    await _neu_abrufen(hass, eintrag)  # Ereignisse pi/befund... – kommen erst nach der Sicherung an
    zwischen = db.anzahl()["journal"]
    await async_post_backup(hass)
    assert zwischen == vorher
    assert db.anzahl()["journal"] >= vorher


async def test_schreibfehler_macht_nichts_unverfuegbar_und_holt_nach(
    hass: HomeAssistant, eintrag, box, pi
) -> None:
    import sqlite3
    from unittest.mock import patch

    await _laden(hass, eintrag)
    db = eintrag.runtime_data.datenbank
    vorher = db.anzahl()["journal"]
    geraete = box_daten().geraete
    from dataclasses import replace

    mac = next(iter(geraete))
    geraete[mac] = replace(geraete[mac], aktiv=not geraete[mac].aktiv)
    box.return_value = box_daten(geraete=geraete)
    with patch.object(
        type(db), "abruf_schreiben", side_effect=sqlite3.OperationalError("disk full")
    ):
        await _neu_abrufen(hass, eintrag)
    assert _zustand(hass, eintrag, "sensor", "geraete_online") != STATE_UNAVAILABLE
    assert db.anzahl()["journal"] == vorher
    await _neu_abrufen(hass, eintrag)  # nächster Abruf schreibt das Ereignis von vorhin mit
    assert any(z.ereignis.mac == mac for z in db.journal_lesen()[:3])


async def test_gedaechtnis_nicht_jede_minute(hass: HomeAssistant, eintrag, box, pi) -> None:
    from unittest.mock import patch

    await _laden(hass, eintrag)
    db = eintrag.runtime_data.datenbank
    with patch.object(type(db), "abruf_schreiben", wraps=db.abruf_schreiben) as schreiben:
        await _neu_abrufen(hass, eintrag)  # nur der Zähler-Ring ändert sich
    assert schreiben.call_args.args[2] is None


async def test_kaputtes_gedaechtnis_in_der_datenbank(
    hass: HomeAssistant, eintrag, box, pi, eigener_ordner
) -> None:
    from custom_components.heimnetz.speicher import Datenbank

    db = Datenbank(eigener_ordner / "heimnetz" / "heimnetz.db")
    db.oeffnen()
    db.gedaechtnis_speichern({"version": 1, "geraete": [{"unbekannt": 1}]})
    db.schliessen()
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED


async def test_seite_in_der_seitenleiste_solange_geladen(
    hass: HomeAssistant, eintrag, box, pi
) -> None:
    from homeassistant.components import frontend

    await _laden(hass, eintrag)
    panel = hass.data[frontend.DATA_PANELS]["heimnetz"]
    assert panel.sidebar_title == "Heimnetz"
    assert "/heimnetz_static/heimnetz-panel.js?v=" in panel.config["_panel_custom"]["module_url"]
    assert await hass.config_entries.async_reload(
        eintrag.entry_id
    )  # zweites Anmelden scheitert nicht
    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(eintrag.entry_id)
    assert "heimnetz" not in hass.data.get(frontend.DATA_PANELS, {})


async def test_gebaute_seite_wird_ausgeliefert(
    hass: HomeAssistant, eintrag, box, pi, hass_client
) -> None:
    await _laden(hass, eintrag)
    client = await hass_client()
    antwort = await client.get("/heimnetz_static/heimnetz-panel.js")
    assert antwort.status == 200
    assert 'customElements.define("heimnetz-panel"' in (
        await antwort.text()
    ) or "heimnetz-panel" in (await antwort.text())


async def test_fremde_seite_unter_derselben_adresse_bleibt(
    hass: HomeAssistant, eintrag, box, pi, caplog
) -> None:
    from homeassistant.components import frontend

    await async_setup_component(hass, "frontend", {})
    frontend.async_register_built_in_panel(
        hass, "iframe", "Fremd", "mdi:x", frontend_url_path="heimnetz"
    )
    await _laden(hass, eintrag)
    assert hass.data[frontend.DATA_PANELS]["heimnetz"].sidebar_title == "Fremd"
    assert "schon belegt" in caplog.text
    assert await hass.config_entries.async_unload(eintrag.entry_id)
    assert "heimnetz" in hass.data[frontend.DATA_PANELS]  # die fremde Seite wird nicht entfernt
