"""Befunde und Gesamtstand (übernommen aus den Tests des Altbestands)."""

from dataclasses import replace

import pytest
from daten import HOSTLISTE
from logik import befunde as bf
from logik.geraete import aus_hostliste

LAN = bf.Heimnetz("192.168.170.1", "255.255.255.0", "192.168.170.20", "192.168.170.200", True)
PI_OK = bf.PiVerbindung(box=True, internet=True, dns=True)
FRITZ = bf.Angebot("192.168.170.1", "192.168.170.99", "192.168.170.1")
FREMD = bf.Angebot("192.168.170.38", "192.168.1.5", "192.168.1.1", mac="AA")


@pytest.fixture
def geraete():
    return aus_hostliste(HOSTLISTE)


def stufen(geraete, lan=LAN, dhcp=None, pi=PI_OK):
    return {b.key: b.stufe for b in bf.finden(geraete, lan, dhcp, pi)}


def test_doppelte_ip_fremdnetz_und_sperre(geraete):
    k = stufen(geraete)
    assert k["doppelt:192.168.170.60"] == "kritisch"
    assert k["fremdnetz:02:11:22:33:44:03"] == "kritisch"
    assert k["gesperrt:00:11:22:33:44:04"] == "warnung"


def test_schwerste_zuerst(geraete):
    liste = bf.finden(geraete, LAN, None, PI_OK)
    assert [b.stufe for b in liste] == sorted((b.stufe for b in liste), key=bf.STUFEN.index)


def test_doppelt_nur_warnung_wenn_einer_offline(geraete):
    geraete["00:11:22:33:44:02"] = replace(geraete["00:11:22:33:44:02"], aktiv=False)
    assert stufen(geraete)["doppelt:192.168.170.60"] == "warnung"


def test_feste_ip_im_dhcp_bereich(geraete):
    geraete["00:11:22:33:44:01"] = replace(geraete["00:11:22:33:44:01"], quelle="Static")
    assert stufen(geraete)["fest_im_dhcp:00:11:22:33:44:01"] == "warnung"
    assert "fest_im_dhcp:00:11:22:33:44:01" not in stufen(
        geraete, replace(LAN, dhcp_von="192.168.170.100")
    )
    assert "fest_im_dhcp:00:11:22:33:44:01" not in stufen(geraete, replace(LAN, dhcp_von="kaputt"))


def test_zweiter_dhcp_server(geraete):
    assert (
        stufen(geraete, dhcp=bf.DhcpTest(True, (FRITZ, FREMD)))["dhcp_fremd:192.168.170.38"]
        == "kritisch"
    )
    assert not any(k.startswith("dhcp_") for k in stufen(geraete, dhcp=bf.DhcpTest(True, (FRITZ,))))
    assert "dhcp_stumm" in stufen(geraete, dhcp=bf.DhcpTest(True, ()))
    assert "dhcp_stumm" not in stufen(geraete, dhcp=bf.DhcpTest(False, fehler="x"))


def test_dhcp_aus():
    assert stufen({}, replace(LAN, dhcp_an=False))["dhcp_aus"] == "info"


def test_hardware_adresse_der_box(geraete):
    assert "gw_mac:BB" in stufen(geraete, pi=replace(PI_OK, gw_mac="BB", gw_mac_alt="AA"))
    assert not any(
        k.startswith("gw_mac")
        for k in stufen(geraete, pi=replace(PI_OK, gw_mac="AA", gw_mac_alt="AA"))
    )


def test_kein_internet():
    assert stufen({}, pi=replace(PI_OK, internet=False))["kein_internet"] == "kritisch"


def test_text_ohne_hardware_adresse_der_box(geraete):
    b = bf.finden(geraete, LAN, None, replace(PI_OK, gw_mac="BB:BB", gw_mac_alt="AA:AA"))
    text = next(x.text for x in b if x.key.startswith("gw_mac"))
    assert "AA:AA" not in text and "BB:BB" not in text


@pytest.mark.parametrize(
    ("stufen_", "box", "erwartet"),
    [
        ((), True, "ok"),
        (("info",), True, "ok"),
        (("warnung", "info"), True, "warnung"),
        (("kritisch", "warnung"), True, "kritisch"),
        (("kritisch",), False, "box_fehlt"),
    ],
)
def test_gesamtstand(stufen_, box, erwartet):
    liste = [bf.Befund(f"k{i}", s, "t", "x") for i, s in enumerate(stufen_)]
    assert bf.gesamtstand(liste, box) == erwartet


def test_abgleich_neu_und_erledigt():
    a = bf.Befund("a", "warnung", "A", "x")
    b = bf.Befund("b", "kritisch", "B", "y")
    ereignisse, keys = bf.abgleich({}, [a, b])
    assert [e.art for e in ereignisse] == ["befund", "befund"] and keys == {"a": "A", "b": "B"}
    ereignisse, keys = bf.abgleich(keys, [b])
    assert [(e.art, e.text) for e in ereignisse] == [("befund_weg", "Befund erledigt: A")]
    assert bf.abgleich(keys, [b])[0] == []


def test_dhcp_pruefung():
    assert bf.dhcp_pruefung(None, "192.168.170.1") == (None, "noch nicht gelaufen")
    assert bf.dhcp_pruefung(bf.DhcpTest(fehler="nur unter Linux"), "x") == (None, "nur unter Linux")
    assert bf.dhcp_pruefung(bf.DhcpTest(True, (FRITZ,)), "192.168.170.1") == (
        True,
        "1 Server antwortet",
    )
    assert bf.dhcp_pruefung(bf.DhcpTest(True, (FRITZ, FREMD)), "192.168.170.1") == (
        False,
        "2 Server antworten",
    )
    assert bf.dhcp_pruefung(bf.DhcpTest(True, ()), "192.168.170.1") == (
        False,
        "kein Server antwortet",
    )
