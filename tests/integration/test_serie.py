"""Speedtest-Serie (WU-0001) in Home Assistant: n Durchläufe nacheinander, Ergebnis gemerkt, nur Admins."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.heimnetz import coordinator as ko
from tests.integration.test_messplan import _ookla

WERTE = [(118.0, 41.0, 23), (60.0, 39.0, 27), (121.0, 43.0, 22)]


async def _ookla_nachgestellt(hass: HomeAssistant) -> list[ServiceCall]:
    """Ookla-Eintrag; der Dienst setzt wie die echte Integration neue Sensorwerte."""
    ookla = _ookla(hass)
    reg = er.async_get(hass)
    ids = {
        k: reg.async_get_entity_id("sensor", "ookla_speedtest", f"{ookla.entry_id}_{k}")
        for k in ("last_test", "download", "upload", "ping", "server")
    }
    aufrufe: list[ServiceCall] = []

    async def messen(call: ServiceCall) -> None:
        aufrufe.append(call)
        d, u, p = WERTE[(len(aufrufe) - 1) % len(WERTE)]
        t = dt_util.utcnow().replace(microsecond=0).timestamp() + len(aufrufe)
        hass.states.async_set(ids["download"], str(d), {"unit_of_measurement": "Mbit/s"})
        hass.states.async_set(ids["upload"], str(u), {"unit_of_measurement": "Mbit/s"})
        hass.states.async_set(ids["ping"], str(p))
        hass.states.async_set(ids["server"], "Wien – Magenta")
        hass.states.async_set(ids["last_test"], dt_util.utc_from_timestamp(t).isoformat())

    hass.services.async_register("ookla_speedtest", "run_speedtest", messen)
    return aufrufe


async def test_serie_drei_durchlaeufe(
    hass, eintrag, box, pi, hass_ws_client, hass_read_only_access_token
):
    aufrufe = await _ookla_nachgestellt(hass)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    lz = eintrag.runtime_data
    client = await hass_ws_client(hass)

    gast = await hass_ws_client(hass, hass_read_only_access_token)
    await gast.send_json_auto_id({"type": "heimnetz/serie"})
    assert (await gast.receive_json())["error"]["code"] == "unauthorized"

    with patch.object(ko, "SERIE_TAKT_S", 0.01):
        await client.send_json_auto_id({"type": "heimnetz/serie"})
        antwort = await client.receive_json()
        assert antwort["success"] and antwort["result"]["serie"]["n"] == 3
        await client.send_json_auto_id({"type": "heimnetz/serie"})
        assert (await client.receive_json())["error"]["code"] == "nicht_moeglich"  # läuft schon
        await lz.abruf._serie_aufgabe
    assert len(aufrufe) == 3 and lz.abruf.serie_status is None
    s = lz.einstellungen.letzte_serie
    assert s["down"] == {"median": 118.0, "min": 60.0, "max": 121.0} and len(s["laeufe"]) == 3
    assert s["server"] == ["Wien – Magenta"]
    await client.send_json_auto_id({"type": "heimnetz/einstellungen"})
    e = (await client.receive_json())["result"]
    assert (
        e["letzte_serie"]["ping"]["median"] == 23
        and e["ookla"]["tests"] == 1
        and e["serie"] is None
    )
    # Anzahl im Messplan, gemerkt über ein Neuladen
    await client.send_json_auto_id({"type": "heimnetz/messplan/setzen", "serie": 2})
    assert (await client.receive_json())["result"]["messplan"]["serie"] == 2
    await hass.config_entries.async_reload(eintrag.entry_id)
    await hass.async_block_till_done()
    lz = eintrag.runtime_data
    assert lz.einstellungen.plan.serie == 2 and lz.einstellungen.letzte_serie["geplant"] == 3


async def test_durchlauf_ohne_ergebnis_wird_uebersprungen(hass, eintrag, box, pi):
    _ookla(hass)
    hass.services.async_register("ookla_speedtest", "run_speedtest", lambda call: None)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    lz = eintrag.runtime_data
    await lz.einstellungen.async_plan_setzen({"serie": 2})
    with patch.object(ko, "SERIE_TAKT_S", 0.01), patch.object(ko.sr, "WARTEN_S", 0.05):
        assert lz.abruf.serie_starten()
        await lz.abruf._serie_aufgabe
    assert lz.abruf.serie_status is None and lz.einstellungen.letzte_serie is None
