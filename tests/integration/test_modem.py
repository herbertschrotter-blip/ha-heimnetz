"""WS-Befehl `heimnetz/modem` (WU-0008): Rohdaten eines vorgeschalteten Modems abfragen, nur Admins, nur lesen.

Die Antworten des Modems werden mit `aioclient_mock` nachgestellt; eine eigene Session gibt es nicht ans echte Netz.
Geprüft: Erfolg (ohne/mit Anmeldung), Anmeldung abgelehnt, nicht erreichbar, Adresse nicht erlaubt, nur Admins; dazu
dass das Kennwort nirgends in der Antwort steht, die Rohdaten geschwärzt sind und nur LOGIN/LOGOUT als set-Befehl
vorkommt.
"""

import re

import aiohttp
import pytest
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.heimnetz.const import DOMAIN

ADRESSE = "192.168.0.1"
STARTSEITE = "<title>ZTE G5TC</title><script src='/js/goform.js'></script>"
WERTE = {
    "modem_model": "ZTE G5TC",
    "network_type": "ENDC",
    "lte_rsrp": "-97",
    "nr5g_pci": "512",
    "cell_id": "1A2B3C4",
    "tac": "4E21",
    "imsi": "232030000000000",
    "iccid": "8943000000000000000",
    "wan_ipaddr": "203.0.113.7",
    "mac_addr": "AA:BB:CC:DD:EE:FF",
}


@pytest.fixture
def modem_session(modem_netz):
    """Die eigenen Sessions der Diagnose sind Mock-Sessions (conftest.modem_netz)."""
    return modem_netz


def _modem_mocks(aioclient_mock: AiohttpClientMocker, *, login_result: str = "0") -> None:
    aioclient_mock.get(re.compile(rf"{re.escape(ADRESSE)}/$"), text=STARTSEITE)
    aioclient_mock.get(re.compile(r"cmd=LD(&|$)"), json={"LD": "ABCDEF0123456789"})
    aioclient_mock.get(re.compile(r"goform_get_cmd_process"), json=WERTE)
    aioclient_mock.post(re.compile(r"goform_set_cmd_process"), json={"result": login_result})
    aioclient_mock.post(re.compile(r"/ubus"), status=404, text="")


async def _frage(hass, hass_ws_client, token=None, **msg):
    client = await (hass_ws_client(hass, token) if token else hass_ws_client(hass))
    await client.send_json_auto_id({"type": "heimnetz/modem", **msg})
    return await client.receive_json()


async def test_erfolg_mit_anmeldung(hass, hass_ws_client, modem_session):
    assert await async_setup_component(hass, DOMAIN, {})
    _modem_mocks(modem_session)
    antwort = await _frage(hass, hass_ws_client, adresse=ADRESSE, kennwort="geheim")
    assert antwort["success"], antwort
    d = antwort["result"]
    assert d["modell"] == "ZTE G5TC"
    namen_status = [(a["name"], a["status"]) for a in d["abfragen"]]
    assert ("Startseite", "ok") in namen_status
    assert ("Anmeldung", "ok") in namen_status
    assert any(n == "Werte nach Anmeldung" and s == "ok" for n, s in namen_status)
    assert d["befund"] is None
    assert d["summen"]["ok"] >= 3 and d["summen"]["geschwaerzt"] >= 4
    # geschwärzt: IMEI/IMSI/ICCID/MAC/öffentliche IP stehen nicht in der Antwort, Zellkennung bleibt
    roh = str(d["daten"])
    for geheim in (
        "356938035643809",
        "232030000000000",
        "8943000000000000000",
        "203.0.113.7",
        "AA:BB:CC:DD:EE:FF",
    ):
        assert geheim not in roh, geheim
    assert "1A2B3C4" in roh and "4E21" in roh and "512" in roh
    assert "geheim" not in roh  # Kennwort nirgends
    # nur LOGIN/LOGOUT als set-Befehl, keine fremde Adresse
    sets = [c for c in modem_session.mock_calls if "goform_set_cmd_process" in str(c[1])]
    assert sets and all(c[2].get("goformId") in ("LOGIN", "LOGOUT") for c in sets)
    assert all(ADRESSE in str(c[1]) for c in modem_session.mock_calls)


async def test_ohne_kennwort_keine_anmeldung(hass, hass_ws_client, modem_session):
    assert await async_setup_component(hass, DOMAIN, {})
    _modem_mocks(modem_session)
    antwort = await _frage(hass, hass_ws_client, adresse=ADRESSE)
    d = antwort["result"]
    assert d["befund"] is None
    namen = [a["name"] for a in d["abfragen"]]
    assert "Anmeldung" not in namen and "Werte ohne Anmeldung" in namen
    assert not [c for c in modem_session.mock_calls if "goform_set_cmd_process" in str(c[1])]


async def test_anmeldung_abgelehnt(hass, hass_ws_client, modem_session):
    assert await async_setup_component(hass, DOMAIN, {})
    _modem_mocks(modem_session, login_result="3")
    antwort = await _frage(hass, hass_ws_client, adresse=ADRESSE, kennwort="falsch")
    d = antwort["result"]
    assert d["befund"] == "anmeldung_abgelehnt"
    status = {a["name"]: a["status"] for a in d["abfragen"]}
    assert status["Anmeldung"] == "fehler"
    assert status["Werte ohne Anmeldung"] == "ok"  # die Daten ohne Anmeldung bleiben im Ergebnis


async def test_nicht_erreichbar(hass, hass_ws_client, modem_session):
    assert await async_setup_component(hass, DOMAIN, {})
    modem_session.get(re.compile(rf"{re.escape(ADRESSE)}/$"), exc=aiohttp.ClientError())
    antwort = await _frage(hass, hass_ws_client, adresse=ADRESSE, kennwort="geheim")
    d = antwort["result"]
    assert d["befund"] == "nicht_erreichbar"
    assert not [c for c in modem_session.mock_calls if "goform_set_cmd_process" in str(c[1])]


async def test_adresse_nicht_erlaubt(hass, hass_ws_client, modem_session):
    assert await async_setup_component(hass, DOMAIN, {})
    antwort = await _frage(hass, hass_ws_client, adresse="8.8.8.8", kennwort="geheim")
    d = antwort["result"]
    assert d["befund"] == "adresse_nicht_erlaubt"
    assert d["abfragen"] == [] and modem_session.mock_calls == []


async def test_nur_fuer_admins(hass, hass_ws_client, hass_read_only_access_token, modem_session):
    assert await async_setup_component(hass, DOMAIN, {})
    antwort = await _frage(hass, hass_ws_client, hass_read_only_access_token, adresse=ADRESSE)
    assert not antwort["success"] and antwort["error"]["code"] == "unauthorized"
