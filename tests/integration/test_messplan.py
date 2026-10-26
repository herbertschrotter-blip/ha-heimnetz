"""Messplan in Home Assistant: löst Ookla aus, wartet bei Verkehr, nur Admins ändern."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.heimnetz.logik import messplan as mp
from custom_components.heimnetz.logik.verkehr import Zaehlerstand


def _ookla(hass: HomeAssistant, **daten) -> MockConfigEntry:
    """Geladener Ookla-Eintrag mit seinen Sensoren im Register (nur die Daten, die Integration selbst läuft nicht)."""
    ookla = MockConfigEntry(
        domain="ookla_speedtest", data={"manual": True, "scan_interval": 60, **daten}
    )
    ookla.add_to_hass(hass)
    ookla.mock_state(hass, ConfigEntryState.LOADED)
    reg = er.async_get(hass)
    for k in ("last_test", "download", "upload", "ping", "server"):
        reg.async_get_or_create(
            "sensor", "ookla_speedtest", f"{ookla.entry_id}_{k}", config_entry=ookla
        )
    return ookla


async def _laden(hass: HomeAssistant, eintrag, **ookla) -> list[ServiceCall]:
    _ookla(hass, **ookla)
    aufrufe = async_mock_service(hass, "ookla_speedtest", "run_speedtest")
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    return aufrufe


async def _abruf(hass, eintrag):
    await eintrag.runtime_data.abruf.async_refresh()
    await hass.async_block_till_done()


async def test_plan_misst_und_wartet_dann_den_takt_ab(hass, eintrag, box, pi) -> None:
    aufrufe = await _laden(hass, eintrag)
    lz = eintrag.runtime_data
    await lz.einstellungen.async_plan_setzen({"an": True, "takt_h": 4})
    await _abruf(hass, eintrag)
    assert len(aufrufe) == 1  # fällig (noch nie gemessen), Verkehr unbekannt → messen
    ziel = aufrufe[0].data["entity_id"]
    assert (ziel[0] if isinstance(ziel, list) else ziel).endswith(
        "last_test"
    )  # gezielt der eigene Ookla-Eintrag
    await _abruf(hass, eintrag)
    assert len(aufrufe) == 1  # gerade ausgelöst: erst nach dem Takt wieder


async def test_plan_aus_misst_nicht(hass, eintrag, box, pi) -> None:
    aufrufe = await _laden(hass, eintrag)
    await _abruf(hass, eintrag)
    assert aufrufe == []


async def test_bei_verkehr_wird_verschoben(hass, eintrag, box, pi) -> None:
    aufrufe = await _laden(hass, eintrag)
    lz = eintrag.runtime_data
    await lz.einstellungen.async_plan_setzen({"an": True})
    t = dt_util.utcnow().timestamp()
    # 40 Mbit/s in der letzten Minute (Schwelle ohne Tarif 10 Mbit/s)
    lz.abruf.gedaechtnis.ring = [Zaehlerstand(t - 60, 0, 0)]
    box.return_value.zaehler = Zaehlerstand(t, int(40e6 / 8 * 60), 0)
    await _abruf(hass, eintrag)
    assert aufrufe == [] and lz.abruf.plan_status.aktion == mp.WARTEN


async def test_websocket_messplan_und_messen(
    hass, eintrag, box, pi, hass_ws_client, hass_read_only_access_token
) -> None:
    aufrufe = await _laden(hass, eintrag, manual=False)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {
            "type": "heimnetz/messplan/setzen",
            "an": True,
            "takt_h": 6,
            "von": "22:00",
            "bis": "06:00",
        }
    )
    r = (await client.receive_json())["result"]
    assert r["messplan"] == {
        "an": True,
        "takt_h": 6,
        "von": "22:00",
        "bis": "06:00",
        "verkehr": "warten",
        "serie": 3,
    }
    assert r["ookla"]["vorhanden"] and r["ookla"]["misst_selbst"]  # Ookla steht auf „manuell“ aus
    await client.send_json_auto_id({"type": "heimnetz/messplan/setzen", "takt_h": 3})
    assert (await client.receive_json())["error"]["code"] == "ungueltig"
    await client.send_json_auto_id({"type": "heimnetz/messen"})
    r = (await client.receive_json())["result"]
    await hass.async_block_till_done()
    assert len(aufrufe) == 1 and r["plan"]["misst"]
    gast = await hass_ws_client(hass, hass_read_only_access_token)
    for msg in ({"type": "heimnetz/messen"}, {"type": "heimnetz/messplan/setzen", "an": False}):
        await gast.send_json_auto_id(msg)
        assert (await gast.receive_json())["error"]["code"] == "unauthorized"


async def test_messen_ohne_ookla(hass, eintrag, box, pi, hass_ws_client) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/messen"})
    assert (await client.receive_json())["error"]["code"] == "ookla_fehlt"


async def test_plan_bleibt_nach_neustart(hass, eintrag, box, pi) -> None:
    await _laden(hass, eintrag)
    await eintrag.runtime_data.einstellungen.async_plan_setzen({"an": True, "takt_h": 12})
    assert await hass.config_entries.async_reload(eintrag.entry_id)
    await hass.async_block_till_done()
    assert eintrag.runtime_data.einstellungen.plan.takt_h == 12


async def test_nur_der_eigene_ookla_eintrag_misst(hass, eintrag, box, pi) -> None:
    aufrufe = await _laden(hass, eintrag)
    sensoren = eintrag.runtime_data.abruf.speedtest.sensoren
    assert await eintrag.runtime_data.abruf.messen("Test")
    await hass.async_block_till_done()
    ziel = aufrufe[-1].data["entity_id"]
    assert (ziel if isinstance(ziel, list) else [ziel]) == [sensoren.last_test]


async def test_ookla_mit_startzeit_misst_selbst(hass, eintrag, box, pi, hass_ws_client) -> None:
    await _laden(hass, eintrag, manual=True, start_time="03:00")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/einstellungen"})
    o = (await client.receive_json())["result"]["ookla"]
    assert o["misst_selbst"] and o["startzeit"] == "03:00"


async def test_deaktiviertes_ookla_gilt_als_fehlend(hass, eintrag, box, pi, hass_ws_client) -> None:
    ookla = _ookla(hass)
    ookla.mock_state(hass, ConfigEntryState.NOT_LOADED)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/einstellungen"})
    assert (await client.receive_json())["result"]["ookla"]["vorhanden"] is False


async def test_fehler_im_messplan_macht_nichts_unverfuegbar(hass, eintrag, box, pi) -> None:
    await _laden(hass, eintrag)
    with patch(
        "custom_components.heimnetz.logik.messplan.entscheiden", side_effect=ValueError("kaputt")
    ):
        await _abruf(hass, eintrag)
    assert eintrag.runtime_data.abruf.last_update_success
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", "heimnetz", f"{eintrag.entry_id}_gesamtstand"
    )
    assert hass.states.get(entity_id).state != "unavailable"
