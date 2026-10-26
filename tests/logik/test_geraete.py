"""Gerätetabelle lesen und vergleichen."""

from dataclasses import replace

from daten import HOSTLISTE
from logik import geraete as gr


def test_lesen():
    g = gr.aus_hostliste(HOSTLISTE)
    assert len(g) == 5
    pi = g["00:11:22:33:44:01"]
    assert (pi.name, pi.art, pi.aktiv, pi.kennung) == (
        "Pi",
        "LAN",
        True,
        "Pi",
    )  # ohne Hardware-Adresse
    assert g["00:11:22:33:44:04"].wan == "denied"
    assert g["02:11:22:33:44:05"].art == gr.UNBEKANNT


def test_zufallsadresse():
    assert gr.zufallsadresse("02:11:22:33:44:03")
    assert not gr.zufallsadresse("00:11:22:33:44:01")
    assert not gr.zufallsadresse("zz")


def test_abgleich():
    neu = gr.aus_hostliste(HOSTLISTE)
    alt = dict(neu)
    del alt["00:11:22:33:44:04"]
    alt["00:11:22:33:44:01"] = replace(alt["00:11:22:33:44:01"], ip="192.168.170.61")
    alt["00:11:22:33:44:02"] = replace(alt["00:11:22:33:44:02"], aktiv=False)
    alt["02:11:22:33:44:03"] = replace(alt["02:11:22:33:44:03"], art="LAN")
    arten = sorted((e.art, e.mac[-2:]) for e in gr.abgleich(alt, neu))
    assert arten == [("anschluss", "03"), ("ip_wechsel", "01"), ("neu", "04"), ("online", "02")]


def test_ergaenzen_behaelt_anschluss_und_traegt_quelle_ein():
    neu = gr.aus_hostliste(HOSTLISTE)
    alt = {"02:11:22:33:44:05": replace(neu["02:11:22:33:44:05"], art="WLAN")}
    g = gr.ergaenzen(neu, alt, {"00:11:22:33:44:01": "Static"})
    assert g["02:11:22:33:44:05"].art == "WLAN"
    assert g["00:11:22:33:44:01"].quelle == "Static"
    assert g["00:11:22:33:44:02"].quelle == ""


def test_ohne_namen_nicht_die_hardware_adresse():
    g = gr.aus_hostliste(
        "<List><Item><MACAddress>02:11:22:33:44:09</MACAddress><IPAddress>1.2.3.4</IPAddress><Active>1</Active></Item></List>"
    )
    assert g["02:11:22:33:44:09"].name == gr.OHNE_NAMEN
    assert all("44:09" not in e.text for e in gr.abgleich({}, g))


def test_verbindung_und_gruppen():
    assert gr.verbindung("LAN", True, None) == "LAN"
    assert gr.verbindung("WLAN", True, "5") == "WLAN 5 GHz"
    assert gr.verbindung("WLAN", True, None) == "WLAN"  # Band nicht bestimmbar
    assert (
        gr.verbindung("WLAN", False, "2,4") == gr.NICHT_VERBUNDEN
    )  # Band kennt die Box nur verbunden
    assert gr.verbindung("–", True, None) == "Sonstige"
    assert gr.gruppen(
        [("WLAN 2,4 GHz", True), ("LAN", False), ("WLAN 2,4 GHz", False), ("LAN", True)]
    ) == [
        {"name": "LAN", "text": "LAN", "online": 1, "gesamt": 2},
        {"name": "WLAN 2,4 GHz", "text": "WLAN 2,4 GHz", "online": 1, "gesamt": 2},
    ]
    assert gr.verbindung("WLAN 5 GHz", True, "5") == "WLAN 5 GHz"
    assert gr.gruppen([("WLAN 7 GHz", True)]) == [
        {"name": "WLAN 7 GHz", "text": "WLAN 7 GHz", "online": 1, "gesamt": 1}
    ]


def test_vpn_eigene_gruppe():
    """WU-0003: Geräte, die sich per WireGuard einwählen, stehen in einer eigenen Gruppe ganz oben."""
    assert gr.verbindung("LAN", True, None, vpn=True) == gr.VPN
    assert gr.verbindung("WLAN", False, None, vpn=True) == gr.VPN  # auch offline: bleibt VPN
    assert gr.verbindung("LAN", True, None) == "LAN"
    g = gr.gruppen([("LAN", True), (gr.VPN, True), (gr.VPN, False)])
    assert g[0] == {"name": gr.VPN, "text": gr.VPN, "online": 1, "gesamt": 2}
