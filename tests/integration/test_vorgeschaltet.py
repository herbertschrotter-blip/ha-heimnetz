"""WU-0009 Stufe 2: vorgeschaltetes Gerät gegen Home Assistant – Suche, laufender Abruf, Ablehnung, Ausfall, Diagnose.

Kein echtes Gerät: aiohttp-Anfragen beantwortet `aioclient_mock` (conftest.modem_netz), die Bibliothek
huawei-lte-api läuft gegen `requests_mock`, tplinkrouterc6u wird an ihren Clients ersetzt. Die Antworten sind
erfunden, in der Form der öffentlichen Quellen (ZTE ubus: chennest/zte-cpe-go; Huawei: huawei-lte-api;
TP-Link: tplinkrouterc6u). Geprüft wird auch: nur die eine private Adresse, nur lesende Aufrufe, höchstens eine
Anmeldung, das Kennwort in keiner Antwort und in keinem Protokoll.
"""

import asyncio
import base64
import json
import logging
import re

import aiohttp
import pytest
import requests
import requests_mock as rm
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMockResponse

from custom_components.heimnetz.const import CONF_MODEM_KENNWORT, DOMAIN
from custom_components.heimnetz.logik import vorgeschaltet as ve
from custom_components.heimnetz.logik import zugang as zg
from custom_components.heimnetz.logik.vorgeschaltet import zte as lz
from custom_components.heimnetz.vorgeschaltet import netz
from tests.integration.conftest import BEACONDB, OVERPASS, box_daten

ADRESSE = "192.168.0.1"
KENNWORT = "Modem-Geheim-456"
# Box hinter einem Router/Modem: LAN 1 als Zugang, IP-Client, private WAN-Adresse (Vorschlag .1)
HINTER = zg.Meldung(
    zugangsart="Ethernet", link="Up", art_avm="IP-Client", wan_netz="privat", vorschlag=ADRESSE
)
STARTSEITE = (
    "<html><head><title>ZTE G5TC</title><script src='/js/zwrt_web.js'></script></head></html>"
)
NETINFO = {
    "network_type": "ENDC",
    "network_provider": "3 AT",
    "rmcc": "232",
    "rmnc": "05",
    "lte_rsrp": "-97",
    "lte_rsrq": "-11",
    "lte_snr": "8",
    "lte_band": "3",
    "lte_pci": "1A",
    "cell_id": "1A2B3C4",
    "tac": "1A2B",
    "nr5g_rsrp": "-101",
    "nr5g_rsrq": "-12",
    "nr5g_snr": "4.5",
    "nr5g_pci": "200",
    "nr5g_action_band": "n78",
    "imei": "356938035643809",  # wird nie übernommen (und in der Diagnose geschwärzt)
}
SITZUNG = "5" * 32


def _zustand(hass, eintrag, schluessel):
    eid = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{eintrag.entry_id}_{schluessel}"
    )
    return hass.states.get(eid).state if eid else None


async def _frage(client, **msg):
    await client.send_json_auto_id(msg)
    return await client.receive_json()


def _leeren(mock):
    """Antworten neu einstellen; BeaconDB und Overpass bleiben wie in conftest (nichts bekannt)."""
    mock.clear_requests()
    mock.post(BEACONDB, status=404, json={"error": {"code": 404, "message": "Not found"}})
    mock.post(OVERPASS, json={"elements": []})


def _zte_ubus(mock, *, kennwort_ok=True, versuche=5, erreichbar=True, umleiten=False):
    """ZTE G5TC (ubus) unter ADRESSE; jede andere Adresse antwortet nicht. `umleiten`: per http nur eine leere
    Weiterleitung auf https (GitHub #2), die Seite gibt es erst dort."""
    _leeren(mock)
    if umleiten:
        mock.get(
            re.compile(rf"^http://{re.escape(ADRESSE)}/$"),
            status=302,
            headers={"Location": f"https://{ADRESSE}/"},
        )
    if erreichbar:
        mock.get(re.compile(rf"//{re.escape(ADRESSE)}/$"), text=STARTSEITE)
    else:
        mock.get(re.compile(rf"//{re.escape(ADRESSE)}/$"), exc=aiohttp.ClientError())
    mock.get(re.compile(r"goform_get_cmd_process"), status=404, text="<html>404</html>")

    async def ubus(method, url, data):
        sitzung, _objekt, methode, _arg = data[0]["params"]
        angemeldet = sitzung == SITZUNG
        ergebnis = {
            "web_login_info": [0, {"zte_web_sault": "C0FFEE", "login_fail_num": versuche}],
            "web_login": [0, {"result": 0, "ubus_rpc_session": SITZUNG}]
            if kennwort_ok
            else [0, {"result": 1}],
            "nwinfo_get_netinfo": [0, NETINFO] if angemeldet else [6],
            "get_wwaniface": [0, {"connect_status": "connected", "realtime_time": 3600}]
            if angemeldet
            else [6],
            "web_logout": [0],
        }[methode]
        return AiohttpClientMockResponse(
            method, url, json=[{"jsonrpc": "2.0", "id": data[0]["id"], "result": ergebnis}]
        )

    mock.post(re.compile(rf"//{re.escape(ADRESSE)}/ubus/"), side_effect=ubus)
    mock.get(re.compile(r"//192\.168\.\d+\.\d+/$"), exc=aiohttp.ClientError())


def _eigene(caplog):
    """Protokollzeilen von Heimnetz und den Bibliotheken – ohne das Debug-Protokoll der WebSocket-API von Home
    Assistant, das jede empfangene Nachricht wörtlich mitschreibt (auch das eingetippte Kennwort)."""
    return [
        r for r in caplog.records if not r.name.startswith("homeassistant.components.websocket_api")
    ]


def _ubus_aufrufe(mock):
    return [c[2][0]["params"][2] for c in mock.mock_calls if "/ubus/" in str(c[1])]


@pytest.fixture
async def hinter_modem(hass: HomeAssistant, eintrag, box, pi, modem_netz):
    """Heimnetz hinter einem vorgeschalteten Modem: die Box meldet LAN 1 und kein Mobilfunk-Modem. Beim Start
    antwortet noch nichts (die erste Suche findet nichts)."""
    _zte_ubus(modem_netz, erreichbar=False)
    box.return_value = box_daten(zugang=HINTER, mobil=None, ohne_mobilfunk=True)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    return eintrag


async def _modem_festlegen(hass, client, eintrag, **werte):
    antwort = await _frage(
        client,
        type="heimnetz/zugang/setzen",
        **{"wahl": "extern", "adresse": ADRESSE, "kennwort": KENNWORT, **werte},
    )
    assert antwort["success"], antwort
    await hass.async_block_till_done()  # Suche und Lesen laufen im Hintergrund
    await eintrag.runtime_data.abruf.async_refresh()
    await hass.async_block_till_done()
    return antwort


async def test_zte_ubus_gefunden_werte_im_reiter_und_in_entitaeten(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client, caplog
):
    caplog.set_level(logging.DEBUG)
    eintrag = hinter_modem
    _zte_ubus(modem_netz)
    client = await hass_ws_client(hass)
    antwort = await _modem_festlegen(hass, client, eintrag)
    assert KENNWORT not in json.dumps(antwort)

    st = eintrag.runtime_data.abruf.data
    assert st.mobil_quelle == "modem" and st.mobil.haupt.rsrp == -97
    assert st.modem.erkennung == ve.Erkennung("zte_ubus", "ZTE G5TC") and st.modem.angemeldet
    # vorhandene Mobilfunk-Entitäten und die neuen, passend benannten
    assert _zustand(hass, eintrag, "rsrp_anker") == "-97"
    assert _zustand(hass, eintrag, "rsrp_5g") == "-101"
    assert _zustand(hass, eintrag, "sinr_5g") == "4.5"
    assert _zustand(hass, eintrag, "mobil_band") == "B3 · n78"
    assert _zustand(hass, eintrag, "mobil_zelle") == "1a2b3-c4"

    d = (await _frage(client, type="heimnetz/internet", tage=1))["result"]
    assert d["zugang"]["art"] == "extern" and d["zugang"]["geraet"] == "ZTE G5TC (ubus)"
    assert d["mobilfunk"]["herkunft"] == "modem"
    assert d["mobilfunk"]["herkunft_text"] == "vom vorgeschalteten Modem"
    assert (
        d["mobilfunk"]["strecke"]["geraet"] == "Modem" and d["mobilfunk"]["baender"] == "B3 · n78"
    )
    zellen = {z["art"]: z for z in d["mobilfunk"]["zellen"]}
    assert zellen["LTE"]["sinr"] == 8.0 and zellen["5G"]["band"] == "n78"
    assert (
        d["vorgeschaltet"]["geraet"] == "ZTE G5TC (ubus)" and d["vorgeschaltet"]["befund"] is None
    )
    z = (await _frage(client, type="heimnetz/zugang"))["result"]
    assert "192.168.0.1 antwortet: ZTE G5TC (ubus)" in z["belege"]
    assert z["vorgeschaltet"]["adresse"] == ADRESSE

    # nur lesende ubus-Methoden, genau eine Anmeldung, nie eine andere Adresse
    aufrufe = _ubus_aufrufe(modem_netz)
    assert aufrufe.count("web_login") == 1
    assert set(aufrufe) <= {m for _, m in lz.UBUS_ERLAUBT}
    assert all(ADRESSE in str(c[1]) for c in modem_netz.mock_calls if "/ubus/" in str(c[1]))
    assert KENNWORT not in json.dumps(d) and KENNWORT not in json.dumps(z)
    assert not any(KENNWORT in r.getMessage() for r in _eigene(caplog))
    # die Momentaufnahme einer Messung nimmt die Werte vom Modem
    from custom_components.heimnetz import kontext
    from custom_components.heimnetz.logik.messung import Messung

    k = await kontext.momentaufnahme(
        hass, eintrag.runtime_data, Messung(st.zeit, 100.0, 20.0, 30.0, "Wien", 1.0, 0.1)
    )
    assert k["mobil_quelle"] == "modem" and k["modem_modell"] == "ZTE G5TC (ubus)"
    assert k["sinr"] == 8.0 and k["nr_band"] == "n78" and k["rsrp"] == -97


async def test_kennwort_abgelehnt_kein_zweiter_versuch_bis_neues_kennwort(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    eintrag = hinter_modem
    abruf = eintrag.runtime_data.abruf
    _zte_ubus(modem_netz, kennwort_ok=False)
    client = await hass_ws_client(hass)
    await _modem_festlegen(hass, client, eintrag)
    assert abruf.modem.stand.befund == "anmeldung_abgelehnt"
    assert ir.async_get(hass).async_get_issue(DOMAIN, "modem_anmeldung") is not None
    d = (await _frage(client, type="heimnetz/internet"))["result"]
    assert d["vorgeschaltet"]["befund"]["kennung"] == "anmeldung_abgelehnt"
    assert d["vorgeschaltet"]["befund"]["lage"] == "rot" and d["mobilfunk"] is None

    # nächster Takt: dasselbe Kennwort wird nicht noch einmal geschickt, der Befund bleibt
    assert await abruf.modem_jetzt()
    assert _ubus_aufrufe(modem_netz).count("web_login") == 1
    assert abruf.modem.stand.befund == "anmeldung_abgelehnt"

    # neues Kennwort: genau ein neuer Versuch, angenommen → Hinweis weg
    _zte_ubus(modem_netz)
    await _modem_festlegen(hass, client, eintrag, kennwort="Neu-789")
    assert _ubus_aufrufe(modem_netz).count("web_login") == 1
    assert abruf.modem.stand.befund is None and abruf.data.mobil_quelle == "modem"
    assert ir.async_get(hass).async_get_issue(DOMAIN, "modem_anmeldung") is None


async def test_gesperrt_keine_anmeldung(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    _zte_ubus(modem_netz, versuche=0)
    await _modem_festlegen(hass, await hass_ws_client(hass), hinter_modem)
    assert hinter_modem.runtime_data.abruf.modem.stand.befund == "gesperrt"
    assert "web_login" not in _ubus_aufrufe(modem_netz)


async def test_ausfall_befund_und_reparatur_erst_nach_zwei_takten(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    eintrag = hinter_modem
    abruf = eintrag.runtime_data.abruf
    _zte_ubus(modem_netz)
    await _modem_festlegen(hass, await hass_ws_client(hass), eintrag)
    assert abruf.data.mobil_quelle == "modem"

    _zte_ubus(modem_netz, erreichbar=False)
    await abruf.modem_jetzt()
    assert abruf.modem.stand.befund == "nicht_erreichbar"
    assert ir.async_get(hass).async_get_issue(DOMAIN, "modem_fehlt") is None, (
        "erst nach zwei Takten"
    )
    await abruf.modem_jetzt()
    assert ir.async_get(hass).async_get_issue(DOMAIN, "modem_fehlt") is not None
    await abruf.async_refresh()
    await hass.async_block_till_done()
    assert abruf.data.mobil is None and _zustand(hass, eintrag, "rsrp_anker") == "unavailable"

    _zte_ubus(modem_netz)
    await abruf.modem_jetzt()
    assert ir.async_get(hass).async_get_issue(DOMAIN, "modem_fehlt") is None


async def test_nichts_gefunden_und_box_mit_modem_fragt_kein_geraet(
    hass: HomeAssistant, eintrag, box, pi, modem_netz, hass_ws_client
):
    # Box mit eingebautem Mobilfunk: kein vorgeschaltetes Gerät, es wird nichts gesucht
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    await _frage(client, type="heimnetz/zugang/suchen")
    assert not [c for c in modem_netz.mock_calls if "192.168." in str(c[1])]

    # hinter einem Gerät, das niemand erkennt: alle Kandidaten der Reihe nach, mehr nicht
    box.return_value = box_daten(zugang=HINTER, mobil=None, ohne_mobilfunk=True)
    _leeren(modem_netz)
    modem_netz.get(re.compile(r"//192\.168\.\d+\.\d+/$"), exc=aiohttp.ClientError())
    abruf = eintrag.runtime_data.abruf
    abruf._zugang_gesucht = -1e9  # noqa: SLF001 – Sperre gegen mehrfaches Tippen für den Test aufheben
    z = (await _frage(client, type="heimnetz/zugang/suchen"))["result"]
    gefragt = {str(c[1]).split("/")[2] for c in modem_netz.mock_calls if "192.168." in str(c[1])}
    assert gefragt == set(ve.UEBLICHE_ADRESSEN)
    assert abruf.modem.stand.befund == "nicht_gefunden"
    assert "192.168.18.1 antwortet nicht" in z["belege"]


async def test_huawei_ueber_die_integration_huawei_lte(
    hass: HomeAssistant, hinter_modem, modem_netz
):
    """Ist huawei_lte eingerichtet, gelten deren Entitäten – das Gerät selbst wird nicht gefragt."""
    eintrag = hinter_modem
    huawei = MockConfigEntry(
        domain="huawei_lte", unique_id="SN0001", data={"url": "http://192.168.8.1/"}
    )
    huawei.add_to_hass(hass)
    huawei.mock_state(hass, ConfigEntryState.LOADED)
    reg = er.async_get(hass)
    for feld, wert in (
        ("device_signal.rsrp", "-95"),
        ("device_signal.rsrq", "-11"),
        ("device_signal.sinr", "12"),
        ("device_signal.cell_id", "26917889"),
        ("net_current_plmn.Numeric", "23205"),
    ):
        e = reg.async_get_or_create("sensor", "huawei_lte", f"SN0001-{feld}", config_entry=huawei)
        hass.states.async_set(e.entity_id, wert)
    abruf = eintrag.runtime_data.abruf
    abruf.modem.gemerkt, abruf.modem.adresse = (
        ve.Erkennung("huawei_hilink", "Huawei B535-232"),
        "192.168.8.1",
    )
    _leeren(modem_netz)
    await abruf.modem_jetzt()
    assert not [c for c in modem_netz.mock_calls if "192.168." in str(c[1])], "kein eigener Zugriff"
    s = abruf.modem.stand
    assert s.quelle == "integration" and s.mobil.haupt.rsrp == -95 and s.mobil.haupt.sinr == 12.0


# ── Huawei HiLink über die Bibliothek (Form der XML-Antworten wie in huawei-lte-api) ──
HUAWEI = "http://192.168.8.1/"


def _huawei(m: rm.Mocker, *, kennwort_ok=True):
    m.get(HUAWEI, text='<html><head><meta name="csrf_token" content="tok1"/></head></html>')
    m.get(HUAWEI + "html/index.html", text='<meta name="csrf_token" content="tok1"/>')
    m.get(
        HUAWEI + "api/device/basic_information",
        text="<response><devicename>B535-232</devicename></response>",
    )
    m.get(
        HUAWEI + "api/user/state-login",
        text="<response><State>-1</State><password_type>4</password_type></response>",
    )
    m.post(
        HUAWEI + "api/user/login",
        text="<response>OK</response>"
        if kennwort_ok
        else "<error><code>108006</code><message></message></error>",
    )
    m.get(
        HUAWEI + "api/device/signal",
        text="<response><pci>123</pci><cell_id>26917889</cell_id><rsrp>-95dBm</rsrp><rsrq>-11.0dB</rsrq>"
        "<sinr>12dB</sinr><band>3</band></response>",
    )
    m.get(
        HUAWEI + "api/net/current-plmn",
        text="<response><FullName>3 AT</FullName><Numeric>23205</Numeric></response>",
    )
    m.get(
        HUAWEI + "api/monitoring/traffic-statistics",
        text="<response><CurrentConnectTime>7200</CurrentConnectTime></response>",
    )
    m.post(HUAWEI + "api/user/logout", text="<response>OK</response>")


async def test_diagnose_huawei_hilink_mit_bibliothek(hass, hass_ws_client, modem_netz, caplog):
    from homeassistant.setup import async_setup_component

    caplog.set_level(logging.DEBUG)
    assert await async_setup_component(hass, DOMAIN, {})
    modem_netz.get(
        re.compile(r"//192\.168\.8\.1/$"), status=302, headers={"Location": "/html/index.html"}
    )
    client = await hass_ws_client(hass)
    with rm.Mocker() as m:
        _huawei(m)
        d = (await _frage(client, type="heimnetz/modem", adresse="192.168.8.1", kennwort=KENNWORT))[
            "result"
        ]
        logins = [r for r in m.request_history if r.path.endswith("/user/login")]
    assert d["erkannt"]["baustein"] == "huawei_hilink" and d["modell"] == "Huawei B535-232"
    assert d["befund"] is None and len(logins) == 1
    assert d["umgerechnet"]["rsrp"] == -95 and d["umgerechnet"]["sinr"] == 12.0
    assert all(r.hostname == "192.168.8.1" for r in m.request_history)
    roh = json.dumps(d)
    b64 = base64.b64encode(KENNWORT.encode()).decode()
    assert KENNWORT not in roh and b64 not in roh
    assert not any(KENNWORT in r.getMessage() or b64 in r.getMessage() for r in _eigene(caplog))


async def test_diagnose_huawei_kennwort_abgelehnt(hass, hass_ws_client, modem_netz):
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    modem_netz.get(re.compile(r"//192\.168\.8\.1/$"), text="<title>HUAWEI B535-232</title>")
    client = await hass_ws_client(hass)
    with rm.Mocker() as m:
        _huawei(m, kennwort_ok=False)
        d = (await _frage(client, type="heimnetz/modem", adresse="192.168.8.1", kennwort="falsch"))[
            "result"
        ]
        logins = [r for r in m.request_history if r.path.endswith("/user/login")]
    assert d["befund"] == "anmeldung_abgelehnt" and len(logins) == 1
    assert d["hinweis"]["titel"] == "Anmeldung abgelehnt"


# ── TP-Link: echte Clients der Bibliothek, das Netz über requests_mock; Anmeldungen werden gezählt ──
TPLINK = "http://192.168.1.1/"
GDPR_SCHLUESSEL = '$.ret=0;\nvar ee="010001";\nvar nn="' + "A" * 128 + '";\nvar seq="123456";\n'


@pytest.fixture
def tplink_anmeldungen(monkeypatch):
    """Zählt jedes authorize() aller Clients der Bibliothek; `verhalten` stellt das Ergebnis ein."""
    from tplinkrouterc6u.client import ex, mr, mr200
    from tplinkrouterc6u.common.dataclass import LTEStatus
    from tplinkrouterc6u.common.exception import ClientException

    zaehler = {"n": 0, "klassen": [], "verhalten": "ok"}

    def authorize(self):
        zaehler["n"] += 1
        zaehler["klassen"].append(type(self).__name__)
        if zaehler["verhalten"] == "abgelehnt":
            raise ClientException("TplinkRouter - EX - Login failed, wrong user or password.")
        if zaehler["verhalten"] == "fehler":
            raise ClientException("TplinkRouter - Unknown error rsa_key! Error - timeout")

    for modul in (ex, mr, mr200):
        for name in dir(modul):
            klasse = getattr(modul, name)
            if (
                isinstance(klasse, type)
                and hasattr(klasse, "authorize")
                and klasse.__module__ == modul.__name__
            ):
                monkeypatch.setattr(klasse, "authorize", authorize)
    monkeypatch.setattr(
        ex.TPLinkEXClient,
        "get_lte_status",
        lambda self: LTEStatus(rsrp=-96, rsrq=-10, snr=70, network_type=7, isp_name="3 AT"),
    )
    monkeypatch.setattr(ex.TPLinkEXClient, "logout", lambda self: None)
    return zaehler


def _tplink_netz(m: rm.Mocker):
    """EX-Gerät: nur getGDPRParm liefert einen Schlüssel (ohne Anmeldung), getParm gibt es nicht."""
    m.register_uri(rm.ANY, re.compile(r"/cgi/getGDPRParm"), text=GDPR_SCHLUESSEL)
    m.register_uri(rm.ANY, re.compile(r"/cgi/getParm"), status_code=404, text="")


@pytest.mark.parametrize(
    ("kennwort", "verhalten", "befund", "anmeldungen"),
    [
        (None, "ok", None, 0),  # ohne Kennwort: keine Anmeldung, auch keine mit leerem
        (KENNWORT, "ok", None, 1),
        (KENNWORT, "abgelehnt", "anmeldung_abgelehnt", 1),
        (KENNWORT, "fehler", "fehler", 1),  # Netz/Schlüssel weg: kein Urteil über das Kennwort
    ],
)
async def test_diagnose_tplink_familie_ohne_anmeldung_dann_genau_ein_versuch(
    hass, hass_ws_client, modem_netz, tplink_anmeldungen, kennwort, verhalten, befund, anmeldungen
):
    from homeassistant.setup import async_setup_component

    tplink_anmeldungen["verhalten"] = verhalten
    assert await async_setup_component(hass, DOMAIN, {})
    modem_netz.get(re.compile(r"//192\.168\.1\.1/$"), text="<title>Archer NX200</title> TP-Link")
    client = await hass_ws_client(hass)
    with rm.Mocker() as m:
        _tplink_netz(m)
        msg = {"type": "heimnetz/modem", "adresse": "192.168.1.1"}
        if kennwort:
            msg["kennwort"] = kennwort
        d = (await _frage(client, **msg))["result"]
        pfade = [r.path for r in m.request_history]
    assert d["erkannt"]["baustein"] == "tplink"
    assert tplink_anmeldungen["n"] == anmeldungen, tplink_anmeldungen
    assert set(tplink_anmeldungen["klassen"]) <= {"TPLinkEXClientGCM"}
    assert not any("login" in p or "cgi_gdpr" in p for p in pfade), (
        "Familie ohne Anmeldung bestimmt"
    )
    assert d["befund"] == befund
    assert {a["name"]: a["angabe"] for a in d["abfragen"]}["TP-Link: Gerätefamilie"] == "EX"
    if befund is None and kennwort:
        assert d["umgerechnet"]["rsrp"] == -96
    assert KENNWORT not in json.dumps(d)


async def test_diagnose_ont_nur_erkennen(hass, hass_ws_client, modem_netz):
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    modem_netz.get(re.compile(r"//192\.168\.100\.1/$"), text="<title>EchoLife HG8010H</title>")
    client = await hass_ws_client(hass)
    d = (await _frage(client, type="heimnetz/modem", adresse="192.168.100.1"))["result"]
    assert d["erkannt"]["baustein"] == "ont_huawei" and d["erkannt"]["werte"] is False
    assert d["befund"] == "glasfaser" and "ONT" in d["hinweis"]["text"]
    assert len(modem_netz.mock_calls) == 1, "nur die Startseite"


async def test_diagnose_folgt_weiterleitung_auf_https_derselben_adresse(
    hass, hass_ws_client, modem_netz
):
    """GitHub #2: Das ZTE leitet http auf https weiter – Startseite, Anmeldung und Werte kommen über https."""
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    _zte_ubus(modem_netz, umleiten=True)
    client = await hass_ws_client(hass)
    d = (await _frage(client, type="heimnetz/modem", adresse=ADRESSE, kennwort=KENNWORT))["result"]
    assert d["erkannt"]["baustein"] == "zte_ubus" and d["modell"] == "ZTE G5TC"
    assert d["befund"] is None and d["umgerechnet"]["rsrp"] == -97
    urls = [str(c[1]) for c in modem_netz.mock_calls]
    assert urls[0] == f"http://{ADRESSE}/" and urls[1] == f"https://{ADRESSE}/"
    assert all(u.startswith(f"https://{ADRESSE}/") for u in urls[1:])


async def test_weiterleitung_auf_andere_adresse_wird_nicht_gefolgt(
    hass, hass_ws_client, modem_netz
):
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    _leeren(modem_netz)
    modem_netz.get(
        re.compile(rf"^http://{re.escape(ADRESSE)}/$"),
        status=302,
        headers={"Location": "https://192.168.0.9/"},
    )
    modem_netz.get(re.compile(r"^https://"), text=STARTSEITE)
    modem_netz.get(re.compile(r"goform_get_cmd_process"), status=404, text="<html>404</html>")
    modem_netz.post(re.compile(r"/ubus/"), status=404, text="<html>404</html>")
    client = await hass_ws_client(hass)
    with rm.Mocker() as m:
        m.register_uri(rm.ANY, rm.ANY, status_code=404)
        d = (await _frage(client, type="heimnetz/modem", adresse=ADRESSE))["result"]
    assert d["erkannt"] is None
    assert all(r.scheme == "http" and r.hostname == ADRESSE for r in m.request_history)
    assert all(str(c[1]).startswith(f"http://{ADRESSE}/") for c in modem_netz.mock_calls), (
        "weder https noch eine andere Adresse"
    )


async def test_suche_findet_zte_hinter_weiterleitung(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    eintrag = hinter_modem
    _zte_ubus(modem_netz, umleiten=True)
    client = await hass_ws_client(hass)
    await _modem_festlegen(hass, client, eintrag)
    st = eintrag.runtime_data.abruf.data
    assert st.modem.erkennung == ve.Erkennung("zte_ubus", "ZTE G5TC") and st.modem.angemeldet
    assert st.mobil_quelle == "modem" and st.mobil.haupt.rsrp == -97


def test_requests_nur_diese_adresse():
    """Der Adapter für die Bibliotheken lehnt jede andere Adresse ab – auch nach einer Weiterleitung."""
    s = netz.requests_session("192.168.8.1")
    with pytest.raises(requests.ConnectionError):
        s.get("http://10.0.0.9/", timeout=1)
    with pytest.raises(requests.ConnectionError):
        s.get("http://example.com/", timeout=1)
    assert s.max_redirects <= 3 and s.trust_env is False


async def test_kennwort_hinterlegt_nie_an_die_seite(hass, hinter_modem, modem_netz, hass_ws_client):
    _zte_ubus(modem_netz)
    client = await hass_ws_client(hass)
    await _modem_festlegen(hass, client, hinter_modem)
    assert hinter_modem.options[CONF_MODEM_KENNWORT] == KENNWORT
    for befehl in ("internet", "zugang", "uebersicht", "einstellungen"):
        assert KENNWORT not in json.dumps(
            (await _frage(client, type=f"heimnetz/{befehl}"))["result"]
        )


# ── Nacharbeit Review 0.27.0 ──
def _zte_goform(mock, *, anmeldung):
    """ZTE goform unter ADRESSE; die Anmeldung antwortet mit `anmeldung` (dict) oder wirft (Exception)."""
    _leeren(mock)
    mock.get(
        re.compile(rf"//{re.escape(ADRESSE)}/$"),
        text="<title>ZTE MC801A</title><script src='js/goform.js'>",
    )
    mock.get(re.compile(r"cmd=LD(&|$)"), json={"LD": "ABCDEF"})
    mock.get(
        re.compile(r"goform_get_cmd_process"),
        json={"modem_model": "MC801A", "lte_rsrp": "", "network_type": "LTE"},
    )
    if isinstance(anmeldung, Exception):
        mock.post(re.compile(r"goform_set_cmd_process"), exc=anmeldung)
    else:
        mock.post(re.compile(r"goform_set_cmd_process"), json=anmeldung)
    mock.get(re.compile(r"//192\.168\.\d+\.\d+/$"), exc=aiohttp.ClientError())


def _logins(mock):
    return [
        c
        for c in mock.mock_calls
        if "goform_set_cmd_process" in str(c[1]) and (c[2] or {}).get("goformId") == "LOGIN"
    ]


async def test_goform_netzfehler_bei_anmeldung_ist_kein_abgelehnt(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    abruf = hinter_modem.runtime_data.abruf
    _zte_goform(modem_netz, anmeldung=aiohttp.ClientError())
    await _modem_festlegen(hass, await hass_ws_client(hass), hinter_modem)
    assert abruf.modem.stand.befund == "fehler" and len(_logins(modem_netz)) == 1
    assert ir.async_get(hass).async_get_issue(DOMAIN, "modem_anmeldung") is None
    await abruf.modem_jetzt()
    assert len(_logins(modem_netz)) == 2, (
        "nach einem Netzfehler im nächsten Takt wieder ein Versuch"
    )
    # echte Ablehnung: danach kein Versuch mehr
    _zte_goform(modem_netz, anmeldung={"result": "3"})
    await abruf.modem_jetzt()
    await abruf.modem_jetzt()
    assert len(_logins(modem_netz)) == 1 and abruf.modem.stand.befund == "anmeldung_abgelehnt"


async def test_kein_zweiter_zugriff_ohne_anlass_und_suche_merkt_sich_fehler(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client, monkeypatch
):
    eintrag = hinter_modem
    dienst = eintrag.runtime_data.abruf.modem
    _zte_ubus(modem_netz)
    await _modem_festlegen(hass, await hass_ws_client(hass), eintrag)
    vorher = len(modem_netz.mock_calls)
    # nichts fällig (eben gelesen, kein Anstoß): unter der Sperre wird nichts mehr geholt
    await dienst.arbeiten(("192.168.0.1",), KENNWORT)
    assert len(modem_netz.mock_calls) == vorher
    # zwei Anstöße zugleich laufen nacheinander, nie zwei Anmeldungen gleichzeitig
    dienst.anstossen()
    await asyncio.gather(
        eintrag.runtime_data.abruf.modem_jetzt(), eintrag.runtime_data.abruf.modem_jetzt()
    )
    assert not dienst.sperre.locked()

    # eine Suche, die mit einem Fehler endet, gilt trotzdem als gesucht (nicht jede Minute neu)
    from custom_components.heimnetz import vorgeschaltet as vg

    async def kaputt(*_a):
        raise RuntimeError("kaputt")

    monkeypatch.setattr(vg, "erkennen_an", kaputt)
    dienst.gesucht = None
    with pytest.raises(RuntimeError):
        await dienst.suchen(("192.168.0.1",))
    assert dienst.gesucht is not None and dienst.suchen_noetig is False


async def test_integration_setzt_merker_zurueck_und_diagnose_meldet_sich_nicht_an(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    eintrag = hinter_modem
    abruf = eintrag.runtime_data.abruf
    huawei = MockConfigEntry(
        domain="huawei_lte", unique_id="SN0002", data={"url": "http://192.168.8.1/"}
    )
    huawei.add_to_hass(hass)
    huawei.mock_state(hass, ConfigEntryState.LOADED)
    e = er.async_get(hass).async_get_or_create(
        "sensor", "huawei_lte", "SN0002-device_signal.rsrp", config_entry=huawei
    )
    hass.states.async_set(e.entity_id, "-95")
    abruf.modem.gemerkt, abruf.modem.adresse = (
        ve.Erkennung("huawei_hilink", "Huawei B535-232"),
        "192.168.8.1",
    )
    abruf.modem._abgelehnt = "alt"  # noqa: SLF001
    await abruf.modem_jetzt()
    assert abruf.modem.stand.quelle == "integration" and abruf.modem.stand.befund is None
    assert abruf.modem._abgelehnt is None  # noqa: SLF001

    _leeren(modem_netz)
    modem_netz.get(re.compile(r"//192\.168\.8\.1/$"), text="<title>HUAWEI B535-232</title>")
    client = await hass_ws_client(hass)
    with rm.Mocker() as m:
        _huawei(m)
        d = (await _frage(client, type="heimnetz/modem", adresse="192.168.8.1", kennwort=KENNWORT))[
            "result"
        ]
        logins = [r for r in m.request_history if r.path.endswith("/user/login")]
    assert d["befund"] == "integration_eingerichtet" and logins == []


async def test_diagnose_nimmt_abgelehntes_hinterlegtes_kennwort_nicht_wieder(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    eintrag = hinter_modem
    _zte_ubus(modem_netz, kennwort_ok=False)
    client = await hass_ws_client(hass)
    await _modem_festlegen(hass, client, eintrag)
    assert eintrag.runtime_data.abruf.modem.stand.befund == "anmeldung_abgelehnt"
    vorher = _ubus_aufrufe(modem_netz).count("web_login")
    d = (await _frage(client, type="heimnetz/modem", adresse=ADRESSE))["result"]
    assert _ubus_aufrufe(modem_netz).count("web_login") == vorher, (
        "hinterlegtes, abgelehntes Kennwort nicht gesendet"
    )
    assert d["befund"] == "anmeldung_abgelehnt"
    d = (await _frage(client, type="heimnetz/modem", adresse=ADRESSE, kennwort="frisch-getippt"))[
        "result"
    ]
    assert _ubus_aufrufe(modem_netz).count("web_login") == vorher + 1, (
        "ein frisch eingetipptes schon"
    )


async def test_zusatz_entitaeten_je_wert(
    hass: HomeAssistant, hinter_modem, modem_netz, hass_ws_client
):
    """sinr_5g erst, wenn das Modem genau diesen Wert geliefert hat – nicht schon bei irgendeinem Wert."""
    eintrag = hinter_modem
    ohne_5g_sinr = {k: v for k, v in NETINFO.items() if k != "nr5g_snr"}
    _zte_ubus(modem_netz)
    alt = dict(NETINFO)
    NETINFO.clear()
    NETINFO.update(ohne_5g_sinr)
    try:
        await _modem_festlegen(hass, await hass_ws_client(hass), eintrag)
    finally:
        NETINFO.clear()
        NETINFO.update(alt)
    assert _zustand(hass, eintrag, "sinr_anker") == "8.0"
    assert _zustand(hass, eintrag, "sinr_5g") is None
    assert eintrag.runtime_data.abruf.gedaechtnis.modem_werte == ["sinr_anker", "mobil_band"]
