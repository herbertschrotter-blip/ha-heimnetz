"""WU-0006: Vorgaben für neue Nutzer – Messplan einer neuen Installation (4 Messungen am Tag), übernommene
Einstellungen bleiben, und Heimnetz läuft ohne die Ookla-Integration (empfohlen, nicht Pflicht)."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heimnetz.const import CONF_ALT_EINTRAG, CONF_FRITZ_EINTRAG, DOMAIN
from custom_components.heimnetz.logik import messplan as mp

from .test_vertrag_seite import BEFEHLE


@pytest.fixture(autouse=True)
def plan_aus():
    """Hier gilt die echte Vorgabe für neue Installationen (die übrigen Tests schalten sie ab)."""
    return


async def _laden(hass: HomeAssistant, eintrag) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()


async def _ws(client, **msg):
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def test_neue_installation_misst_4_mal_am_tag(
    hass, eintrag, box, pi, hass_storage, hass_ws_client
) -> None:
    await _laden(hass, eintrag)
    plan = eintrag.runtime_data.einstellungen.plan
    assert plan == mp.NEU and plan.an and mp.tests_am_tag(plan) == 4
    # gleich gespeichert: ändert sich die Vorgabe in einer späteren Fassung, bleibt dieser Plan
    assert hass_storage[f"{DOMAIN}.{eintrag.entry_id}"]["data"]["messplan"]["takt_h"] == 6
    client = await hass_ws_client(hass)
    e = (await _ws(client, type="heimnetz/einstellungen"))["result"]
    assert e["volumen"] == {"tests_tag": 4, "je_test_mb": None, "tag_mb": None, "monat_gb": None}
    await eintrag.runtime_data.einstellungen.async_setzen({"tarif_down": 150, "tarif_up": 30})
    e = (await _ws(client, type="heimnetz/einstellungen"))["result"]
    # ohne Messung aus dem Tarif: (150 + 30) Mbit/s × 12 s / 8 = 270 MB je Messung
    assert e["volumen"] == {"tests_tag": 4, "je_test_mb": 270, "tag_mb": 1080, "monat_gb": 32.4}


async def test_umstieg_behaelt_den_alten_plan(hass, fritz, box, pi) -> None:
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_FRITZ_EINTRAG: fritz.entry_id, CONF_ALT_EINTRAG: "alt"},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    await _laden(hass, eintrag)
    assert eintrag.runtime_data.einstellungen.plan.an is False  # nichts übernommen: wie bisher aus


async def test_uebernommene_einstellungen_bleiben(hass, eintrag, box, pi, hass_storage) -> None:
    hass_storage[f"{DOMAIN}.{eintrag.entry_id}"] = {
        "version": 1,
        "minor_version": 1,
        "key": f"{DOMAIN}.{eintrag.entry_id}",
        "data": {"tarif_down": 100, "messplan": {"an": False, "takt_h": 2}},
    }
    await _laden(hass, eintrag)
    plan = eintrag.runtime_data.einstellungen.plan
    assert plan.an is False and plan.takt_h == 2


async def test_ohne_ookla_laeuft_alles(hass, eintrag, box, pi, hass_ws_client) -> None:
    await _laden(hass, eintrag)
    abruf = eintrag.runtime_data.abruf
    assert abruf.speedtest.sensoren is None and eintrag.runtime_data.einstellungen.plan.an
    for _ in range(2):  # Plan an, aber nichts zum Auslösen: weder Fehler noch Ausfall
        await abruf.async_refresh()
        await hass.async_block_till_done()
    assert abruf.last_update_success and abruf.ausgeloest == 0.0
    letzte = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{eintrag.entry_id}_letzte_messung"
    )
    assert letzte and hass.states.get(letzte).state == "unknown"
    client = await hass_ws_client(hass)
    for befehl, parameter in BEFEHLE.items():
        antwort = await _ws(client, type=f"heimnetz/{befehl}", **parameter)
        assert antwort["success"], (befehl, antwort)
    e = (await _ws(client, type="heimnetz/einstellungen"))["result"]
    assert e["ookla"]["vorhanden"] is False and e["ookla"]["tests"] == 0
    s = (await _ws(client, type="heimnetz/speedtest", **BEFEHLE["speedtest"]))["result"]
    assert s["gesamt"] == 0 and s["letzte"] is None
    serie = await _ws(client, type="heimnetz/serie")
    assert not serie["success"]  # verständlicher Fehler statt Absturz
