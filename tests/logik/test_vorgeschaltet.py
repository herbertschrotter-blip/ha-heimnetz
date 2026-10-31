"""WU-0009 Stufe 2: Bausteine für ein vorgeschaltetes Gerät – erkennen und umrechnen, ohne Netz.

Alle Antworten sind erfunden, aber in der Form der öffentlichen Quellen (Quelle je Test): Feldnamen und Schreibweise
wie dort, Werte ausgedacht (Zellen `aaaaa-xx`-artig, TAC `1a2b`, keine echten Kennungen).
"""

import pytest
from logik import kontext as kx
from logik import vorgeschaltet as ve
from logik import zugang as zg
from logik.vorgeschaltet import huawei as vh
from logik.vorgeschaltet import integrationen as vi
from logik.vorgeschaltet import tplink as vt
from logik.vorgeschaltet import zte as vz


# ── Erkennen ──
@pytest.mark.parametrize(
    ("startseite", "kopf", "baustein", "modell"),
    [
        # ZTE-Weboberfläche (goform): Titel und Skript wie bei MC801A/MF289F (öffentliche Mitschnitte)
        ("<title>ZTE MC801A</title><script src='js/goform.js'>", {}, "zte", "ZTE MC801A"),
        # neuere ZTE (G5TS/G5TC): Einzelseiten-App, „zwrt“ in den Skripten (chennest/zte-cpe-go: Objekte zwrt_web …)
        ("<html><script src='/js/zwrt_web.js'></script><title>G5TC</title>", {}, "zte", "ZTE G5TC"),
        # Huawei HiLink leitet von „/“ auf /html/index.html weiter (der Weiterleitung folgt Heimnetz nicht)
        ("", {"Location": "/html/index.html"}, "huawei_hilink", ""),
        ("<title>HUAWEI B535-232</title>", {}, "huawei_hilink", "Huawei B535-232"),
        ("<title>Archer MR600</title><meta name='tp-link'>", {}, "tplink", "TP-Link Archer MR600"),
        ("<title>NETGEAR LM1200</title>", {}, "netgear_lte", "Netgear LM1200"),
        ("<title>RUTX11</title> Teltonika", {}, "teltonika", "RUTX11"),
        ("RouterOS router configuration page", {"Server": "mikrotik"}, "mikrotik", "MikroTik"),
        ("<title>Sagemcom F@st</title>", {}, "sagemcom", "Sagemcom"),
        ("<title>Nokia</title> G-010G-Q GPON ONT", {}, "ont_nokia", "G-010G-Q"),
        ("<title>EchoLife HG8010H</title>", {}, "ont_huawei", "HG8010H"),
        ("<title>Zyxel PMG3000</title>", {}, "ont_zyxel", "PMG3000"),
        ("<title>Zyxel NR7101</title>", {}, "zyxel_5g", "Zyxel NR7101"),
        ("<title>FRITZ!Box</title>", {}, "fritzbox", "FRITZ!Box"),
    ],
)
def test_erkennen(startseite, kopf, baustein, modell):
    e = ve.erkennen(startseite, kopf)
    assert e is not None and (e.baustein, e.modell) == (baustein, modell)


def test_erkennen_unbekannt_und_name():
    assert ve.erkennen("<title>Mein Router</title>") is None
    assert ve.Erkennung("zte_ubus", "ZTE G5TC").name == "ZTE G5TC (ubus)"
    assert ve.Erkennung("zte_goform", "").name == "ZTE (goform)"
    assert ve.Erkennung("tplink", "TP-Link Archer MR600").name == "TP-Link Archer MR600"
    assert (
        ve.Erkennung("ont_nokia", "").b.art == "glasfaser" and not ve.Erkennung("ont_nokia").b.werte
    )


def test_zte_schnittstelle_aus_den_proben():
    assert ve.zte_schnittstelle("MC801A", False) == ve.Erkennung("zte_goform", "ZTE MC801A")
    assert ve.zte_schnittstelle("", True, "ZTE G5TC") == ve.Erkennung("zte_goform", "ZTE G5TC")
    assert ve.zte_schnittstelle(None, True, "ZTE G5TC") == ve.Erkennung("zte_ubus", "ZTE G5TC")
    assert ve.zte_schnittstelle(None, False) is None


def test_kandidaten_nur_wenige_private_adressen_ohne_box():
    k = ve.kandidaten("192.168.8.1", "192.168.0.1", box="192.168.1.1")
    assert k == ("192.168.8.1", "192.168.0.1", "192.168.18.1", "192.168.100.1")
    assert ve.kandidaten("8.8.8.8", "modem.local") == ve.UEBLICHE_ADRESSEN
    assert len(ve.kandidaten(None, None)) == 5, "kein Absuchen weiterer Adressen"


def test_treffer_beleg_und_bester():
    t = (
        ve.Treffer("192.168.8.1", False),
        ve.Treffer("192.168.1.1", True, ve.Erkennung("fritzbox", "FRITZ!Box")),
        ve.Treffer("192.168.18.1", True),
        ve.Treffer("192.168.0.1", True, ve.Erkennung("zte_ubus", "ZTE G5TC")),
    )
    assert [ve.beleg(x) for x in t] == [
        "192.168.8.1 antwortet nicht",
        "192.168.1.1 ist die FRITZ!Box selbst",
        "192.168.18.1 antwortet, Gerät nicht erkannt",
        "192.168.0.1 antwortet: ZTE G5TC (ubus)",
    ]
    assert ve.bester(t) is t[3]
    assert ve.beleg(t[3], "en") == "192.168.0.1 answers: ZTE G5TC (ubus)"


def test_befund_daten_in_beiden_sprachen():
    d = ve.befund_daten("anmeldung_abgelehnt")
    assert d["lage"] == "rot" and d["titel"] == "Anmeldung abgelehnt"
    assert ve.befund_daten("anmeldung_abgelehnt", "en")["titel"] == "Login rejected"
    assert ve.befund_daten(None) is None and ve.befund_daten("gibt_es_nicht") is None
    assert set(ve.REPARATUR) <= set(ve.BEFUNDE)


# ── ZTE goform ──
# Feldnamen wie in den öffentlichen goform-Abfragen (teixeluis/zte-lte-modem, Miononno-Skript für MC801A); PCI und
# Zellkennung hexadezimal, so zeigt sie auch die Weboberfläche
GOFORM = {
    "modem_model": "MC801A",
    "network_type": "ENDC",
    "network_provider": "3 AT",
    "rmcc": "232",
    "rmnc": "5",
    "lte_rsrp": "-97",
    "lte_rsrq": "-11",
    "lte_snr": "8.5",
    "lte_band": "3",
    "lte_pci": "1A",
    "cell_id": "1A2B3C4",
    "tac": "1A2B",
    "nr5g_rsrp": "-101",
    "nr5g_rsrq": "-12",
    "nr5g_snr": "4",
    "nr5g_pci": "200",
    "nr5g_action_band": "n78",
    "realtime_time": "3720",
}


def test_goform_umrechnen():
    m = vz.aus_werten(GOFORM)
    assert m.technik == "5G-NSA" and m.laufzeit_s == 3720
    h, nr = m.haupt, m.nr
    assert (h.art, h.rolle, h.zelle, h.pci, h.rsrp, h.rsrq, h.sinr, h.band) == (
        "LTE",
        "primary",
        "1a2b3-c4",
        26,
        -97,
        -11,
        8.5,
        "B3",
    )
    assert (h.plmn, h.tac, h.anbieter) == ("23205", "1a2b", "3 AT")
    assert (nr.art, nr.rolle, nr.pci, nr.rsrp, nr.sinr, nr.band, nr.zelle) == (
        "5G",
        "secondary",
        512,
        -101,
        4.0,
        "n78",
        "",
    )
    # die Mobilfunk-Ansicht kann die Ankerzelle wie bei der Box nachschlagen
    from logik import karte as ka

    assert ka.kennung(h, h) is not None and ka.sendeanlage(h) == "1a2b3"


def test_goform_leer_und_nur_lte():
    assert vz.aus_werten({"modem_model": "MC801A", "lte_rsrp": ""}) is None
    m = vz.aus_werten({"network_type": "LTE", "lte_rsrp": "-90dBm", "cell_id": "0x1A2B3C4"})
    assert m.technik == "LTE" and m.nr is None and m.haupt.rsrp == -90
    assert vz.aus_werten({"network_type": "SA", "nr5g_rsrp": "-88"}).technik == "5G-SA"
    # ältere Firmware (MC801A) nennt 5G als Z5g_*
    assert vz.aus_werten({"Z5g_rsrp": "-95", "Z5g_SINR": "6"}).nr.sinr == 6.0


def test_goform_probe_und_anmeldung():
    assert vz.goform_modell({"modem_model": "ZTE MC801A"}) == "MC801A"
    assert vz.goform_modell({"modem_model": ""}) == ""
    assert vz.goform_modell(None) is None
    assert vz.goform_angemeldet({"result": "0"}) and not vz.goform_angemeldet({"result": "3"})
    assert not vz.goform_angemeldet(None)


# ── ZTE ubus ──
# Protokoll nach chennest/zte-cpe-go (GPL-3.0, nur nachgebaut): params [sitzung, objekt, methode, argumente],
# result [code, daten]; Anmeldung mit zte_web_sault und SHA-256(SHA-256(Kennwort)·groß + Salz)·groß
def test_ubus_nur_erlaubte_methoden():
    k = vz.ubus_anfrage(vz.NULL_SITZUNG, "zwrt_web", "web_login_info", {}, 7)
    # ein einzelnes Objekt mit Z-Mode/Z-Tag wie die Weboberfläche (Mitschnitt G5TS, GitHub #2)
    assert k == {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "call",
        "params": ["0" * 32, "zwrt_web", "web_login_info", {}],
    }
    assert vz.ubus_kopf("web_login_info") == {"Z-Mode": "0", "Z-Tag": "web_login_info"}
    for objekt, methode in (
        ("zwrt_data", "set_wwaniface"),
        ("zwrt_bsp.sys", "reboot"),
        ("uci", "set"),
    ):
        with pytest.raises(ValueError):
            vz.ubus_anfrage("x", objekt, methode, {}, 1)
    assert all(not m.startswith(("set", "reboot")) for _, m in vz.UBUS_ERLAUBT)


def test_ubus_antworten_lesen():
    assert vz.ubus_ergebnis('[{"jsonrpc":"2.0","id":1,"result":[0,{"a":1}]}]') == (0, {"a": 1})
    assert vz.ubus_ergebnis('{"jsonrpc":"2.0","id":1,"result":[6]}') == (6, {})
    assert vz.ubus_ergebnis(
        '{"jsonrpc":"2.0","id":1,"error":{"code":-32002,"message":"Access denied"}}'
    ) == (
        -32002,
        {},
    )
    assert vz.ubus_ergebnis("<html>") == (None, {})
    assert vz.ubus_login_info({"zte_web_sault": "ab12", "login_fail_num": 5}) == ("ab12", 5)
    assert vz.ubus_sitzung({"result": 0, "ubus_rpc_session": "s1"}) == "s1"
    assert vz.ubus_sitzung({"result": 3}) is None  # jemand anderer ist angemeldet
    assert len(vz.ubus_hash("x", "salz")) == 64 and vz.ubus_hash("x", "salz").isupper()


def test_ubus_umrechnen():
    netinfo = {
        "network_type": "SA",
        "network_provider": "3 AT",
        "nr5g_rsrp": "-82",
        "nr5g_rsrq": "-11",
        "nr5g_snr": "15.5",
        "nr5g_pci": "1F4",
        "nr5g_action_band": "n78",
    }
    m = vz.aus_ubus(netinfo, {"connect_status": "connected", "connect_time": 600})
    assert m.technik == "5G-SA" and m.haupt is m.nr and m.haupt.rolle == "primary"
    assert (m.nr.pci, m.nr.sinr, m.laufzeit_s) == (500, 15.5, 600)


def test_ubus_g5tc_band_zelle_tac():
    """GitHub #2 (Form der echten G5TC-Antwort, Werte erfunden): `lte_band` ist die Liste der freigegebenen Bänder,
    das aktive steht in `wan_active_band`/`lteca`; Zellkennung als Zahl dezimal; TAC als `lac_code` dezimal."""
    netinfo = {
        "network_type": "ENDC",
        "network_provider": "3 AT",
        "rmcc": 232,
        "rmnc": 5,
        "wan_active_band": "LTE BAND 3",
        "lte_band": "1,3,7,8,20,28,38",
        "lteca": "123,3,0,1525,15;456,1,1,500,20;",
        "cell_id": 26917889,  # 0x19ABC01 → eNodeB 19abc, Sektor 01
        "lac_code": 6699,  # 0x1A2B
        "lte_pci": 123,
        "lte_rsrp": -91,
        "lte_rsrq": -12,
        "lte_snr": "5.0",
        "nr5g_pci": 500,
        "nr5g_rsrp": -94,
        "nr5g_snr": "23.4",
        "nr5g_action_band": "n78",
    }
    m = vz.aus_ubus(netinfo)
    h = m.haupt
    assert (h.band, h.zelle, h.tac, h.pci, h.plmn) == ("B3", "19abc-01", "1a2b", 123, "23205")
    assert (m.technik, m.nr.band, m.nr.pci) == ("5G-NSA", "n78", 500)
    ohne_aktiv = {k: v for k, v in netinfo.items() if k != "wan_active_band"}
    assert vz.aus_ubus(ohne_aktiv).haupt.band == "B3", "aus dem ersten Eintrag von lteca"
    nur_liste = {k: v for k, v in ohne_aktiv.items() if k != "lteca"}
    assert vz.aus_ubus(nur_liste).haupt.band == "", "eine Liste ist kein aktives Band"
    assert vz.aus_werten({"lte_rsrp": "-90", "lte_band": "3"}).haupt.band == "B3", (
        "goform: ein Band"
    )
    assert vz.aus_werten({"lte_rsrp": "-90", "cell_id": "1A2B3C4"}).haupt.zelle == "1a2b3-c4", (
        "goform hex"
    )


# ── Huawei HiLink ──
# Form wie huawei-lte-api (Salamek/huawei-lte-api) device/signal, net/current-plmn, monitoring/traffic-statistics;
# Felder wie in der Integration huawei_lte von Home Assistant
SIGNAL = {
    "pci": "123",
    "cell_id": "26917889",  # dezimal: 0x19ABC01 → eNodeB 19abc, Sektor 01
    "rsrp": "-95dBm",
    "rsrq": "-11.0dB",
    "sinr": "12dB",
    "band": "3",
    "tac": "6699",
    "nrrsrp": "-100dBm",
    "nrrsrq": "-12dB",
    "nrsinr": "3dB",
    "nrband": "78",
    "mode": "7",
}


def test_huawei_umrechnen():
    m = vh.aus_hilink(
        SIGNAL,
        {"FullName": "3 AT", "Numeric": "23205"},
        {"CurrentConnectTime": "7200"},
    )
    h = m.haupt
    assert m.technik == "5G-NSA" and m.laufzeit_s == 7200
    assert (h.zelle, h.pci, h.rsrp, h.rsrq, h.sinr, h.band, h.tac, h.plmn) == (
        "19abc-01",
        123,
        -95,
        -11,
        12.0,
        "B3",
        "1a2b",
        "23205",
    )
    assert (m.nr.rsrp, m.nr.band, m.nr.sinr) == (-100, "n78", 3.0)
    assert vh.zahl("&gt;=-44dBm") == -44 and vh.zahl("") is None
    assert vh.aus_hilink({}) is None
    assert vh.modell({"devicename": "B535-232"}) == "Huawei B535-232"


# ── TP-Link ──
# dataclasses.asdict(LTEStatus) aus tplinkrouterc6u (Felder laut tplinkrouterc6u/common/dataclass.py)
def test_tplink_umrechnen():
    d = {
        "enable": 1,
        "connect_status": 4,
        "network_type": 7,
        "sim_status": 3,
        "rsrp": -96,
        "rsrq": -10,
        "snr": 72,
        "isp_name": "3 AT",
        "sig_level": 3,
    }
    m = vt.aus_lte_status(d)
    assert m.technik == "LTE" and m.haupt.rsrp == -96 and m.haupt.anbieter == "3 AT"
    assert m.haupt.zelle == "" and m.haupt.pci is None, "TP-Link nennt keine Zellkennung"
    assert vt.aus_lte_status({**d, "network_type": 8}).nr is not None
    assert vt.aus_lte_status({**d, "rsrp": 0}) is None


# ── HA-Integrationen ──
def test_integrationen_felder_und_umrechnen():
    assert vi.feld("huawei_lte", "SN123-device_signal.rsrp") == "rsrp"
    assert vi.feld("netgear_lte", "rx_level_SN123") == "rsrp"
    assert vi.feld("teltonika", "eintrag_1-1_sinr") == "sinr"
    assert vi.feld("teltonika", "eintrag_1-1_temperature") is None
    m = vi.aus_zustaenden("huawei_lte", {"rsrp": "-95", "cell_id": "26917889", "Numeric": "23205"})
    assert m.haupt.rsrp == -95 and m.haupt.zelle == "19abc-01" and m.haupt.plmn == "23205"
    t = vi.aus_zustaenden(
        "teltonika", {"rsrp": "-90", "sinr": "11", "netz": "5G-NSA", "band": "N78"}
    )
    assert t.haupt.art == "5G" and t.haupt.band == "n78" and t.haupt.sinr == 11.0
    assert vi.aus_zustaenden("netgear_lte", {"rsrp": "unavailable"}) is None


# ── gemeinsames Format: Momentaufnahme und Zugang ──
def test_momentaufnahme_mit_sinr_und_band():
    k = kx.mobilfunk(vz.aus_werten(GOFORM))
    assert (k["sinr"], k["band"], k["nr_sinr"], k["nr_band"]) == (8.5, "B3", 4.0, "n78")
    assert set(k) <= set(kx.KEYS)


def test_zugang_mit_erkanntem_geraet():
    hinter = zg.Meldung(
        zugangsart="Ethernet", link="Up", wan_netz="privat", vorschlag="192.168.0.1"
    )
    z = zg.beschreiben(
        hinter,
        "extern",
        False,
        mobil_technik="5G-NSA",
        erkannt="ZTE G5TC (ubus)",
        erkannt_art="mobilfunk",
        such_belege=("192.168.0.1 antwortet: ZTE G5TC (ubus)",),
        erkannt_adresse="192.168.0.1",
    )
    assert z.titel == "Internet über Mobilfunk" and z.geraet == "ZTE G5TC (ubus)"
    assert (
        z.vorschlag == "Mobilfunk über ZTE G5TC (ubus)"
        and z.kopf == "FRITZ!Box · ZTE G5TC (ubus) 5G-NSA"
    )
    assert z.belege[-1] == "192.168.0.1 antwortet: ZTE G5TC (ubus)"
    assert not any("Mobilfunk-Modem der Box: 5G" in b for b in z.belege)
    ont = zg.beschreiben(hinter, "extern", False, "ont")
    assert ont.titel == "Internet über Glasfaser" and ont.geraet == "eigenes Glasfaser-Modem (ONT)"
    assert zg.wirksam("", "ont") == "extern"


# ── Nacharbeit Review 0.27.0 ──
def test_ubus_pci_dezimal_und_kaputter_fehlercode():
    m = vz.aus_ubus({"network_type": "SA", "nr5g_rsrp": "-80", "nr5g_pci": "200"})
    assert m.nr.pci == 200, "ubus: nur Ziffern → dezimal (am Gerät prüfen)"
    assert vz.aus_ubus({"nr5g_rsrp": "-80", "nr5g_pci": "1F4"}).nr.pci == 500
    assert vz.aus_werten({"nr5g_rsrp": "-80", "nr5g_pci": "200"}).nr.pci == 512, (
        "goform bleibt hexadezimal"
    )
    assert vz.ubus_ergebnis('{"error":{"code":"abc"}}') == (-1, {})
    assert vz.ubus_ergebnis('{"error":{"code":null}}') == (-1, {})


def test_huawei_dauer_nach_einheit_der_entitaet():
    assert vi.sekunden("2", "h") == "7200" and vi.sekunden("90", "min") == "5400"
    assert vi.sekunden("7200", "s") == "7200" and vi.sekunden("7200", None) == "7200"
    m = vi.aus_zustaenden(
        "huawei_lte", {"rsrp": "-95", "CurrentConnectTime": "2"}, {"CurrentConnectTime": "h"}
    )
    assert m.laufzeit_s == 7200


def test_zusatzwerte_je_wert():
    m = vz.aus_werten({k: v for k, v in GOFORM.items() if k != "nr5g_snr"})
    assert ve.zusatzwerte(m) == ["sinr_anker", "mobil_band"]
    assert ve.zusatzwerte(vz.aus_werten(GOFORM)) == ["sinr_anker", "sinr_5g", "mobil_band"]
