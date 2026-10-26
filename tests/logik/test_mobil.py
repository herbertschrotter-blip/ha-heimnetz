"""Mobilfunk der Box."""

from daten import ZELLEN
from logik import mobil as mb


def test_lesen():
    m = mb.aus_antwort(
        {
            "NewCurrentAccessTechnology": "5G-NSA",
            "NewRoaming": False,
            "NewCellList": ZELLEN,
            "NewIMSI": "geheim",
        }
    )
    assert (m.technik, m.roaming, m.zellkennung) == ("5G-NSA", False, "abcde-0b/443")
    assert m.haupt is not None and (m.haupt.art, m.haupt.rsrp, m.haupt.rsrq, m.haupt.anbieter) == (
        "LTE",
        -100,
        -11,
        "3 AT",
    )
    assert m.nr is not None and (m.nr.rsrp, m.nr.rsrq, m.nr.zelle) == (-94, -10, "")
    assert "geheim" not in repr(m)


def test_leer_und_kaputt():
    assert mb.aus_antwort({}).haupt is None
    assert mb.aus_antwort({"NewCellList": "<kaputt"}).nr is None


def test_abgleich():
    m = mb.aus_antwort({"NewCurrentAccessTechnology": "LTE", "NewCellList": ZELLEN})
    e = mb.abgleich("5G-NSA", "andere/1", m)
    assert [(x.art, x.stufe) for x in e] == [("mobil_technik", "warnung"), ("mobil_zelle", "info")]
    assert mb.abgleich("", "", m) == []
    assert [
        x.stufe
        for x in mb.abgleich("LTE", "", mb.aus_antwort({"NewCurrentAccessTechnology": "5G-NSA"}))
    ] == ["info"]


def test_befund_wie_altbestand():
    b = mb.befund("5G-NSA", -93, -101, 112.0, 150)
    assert b.titel.startswith("Empfang mittelmäßig") and "112,0 Mbit/s = 75 % vom Tarif" in b.text
    assert b.lage == mb.lage_rsrp(-101)
    assert mb.befund("LTE", -110, None, None, None).titel.startswith("Empfang schwach")
    assert "nur über LTE" in mb.befund("LTE", -110, None, None, None).text
    gut = mb.befund("5G-NSA", -80, -85, 50.0, 150)
    assert (
        gut.titel.startswith("Empfang gut, Geschwindigkeit trotzdem niedrig") and gut.lage == 0.35
    )
    assert mb.befund("5G-NSA", -80, None, 140.0, 150).titel == "Empfang gut"
    assert mb.befund("", None, None, None, None).lage is None


def test_einstufung():
    assert (mb.lage_rsrp(-120), mb.lage_rsrp(-80), mb.lage_rsrp(-60)) == (0.0, 1.0, 1.0)
    assert mb.lage_rsrq(-14) == 0.5
    assert (mb.wort_rsrp(-90), mb.wort_rsrp(-118), mb.wort_rsrq(-12)) == (
        "gut",
        "sehr schwach",
        "mittel",
    )


def test_schwaechster():
    m = mb.aus_antwort({"NewCurrentAccessTechnology": "5G-NSA", "NewCellList": ZELLEN})
    assert mb.schwaechster(m) == -100 and mb.schwaechster(None) is None


def test_antennen_laufzeit_und_abbruch():
    m = mb.aus_antwort({"NewSignalRSRP0": "-91", "NewSignalRSRP1": "0", "NewUptime": "3720"})
    assert m.antennen == (-91, None) and m.laufzeit_s == 3720  # 0 = kein Wert
    assert mb.neu_eingewaehlt(None, m) is None
    assert mb.neu_eingewaehlt(3600, m) is None
    e = mb.neu_eingewaehlt(200_000, m)
    assert e is not None and (e.art, e.stufe) == ("mobil_neu", "warnung")
    assert "2 Tage 7 h" in e.text
    assert (mb.dauer(3720), mb.dauer(420), mb.dauer(86_400)) == ("1 h 2 min", "7 min", "1 Tag 0 h")


def test_baender():
    assert (
        mb.baender({"NewBandCapabilitiesLTE": "1,3,20", "NewBandCapabilities5GNSA": "78"})
        == "LTE 1, 3, 20 · 5G n78"
    )
    assert (
        mb.baender(
            {
                "NewBandCapabilitiesLTE": "0",
                "NewBandCapabilities5GNSA": "unknown",
                "NewBandCapabilities5GSA": "n78",
            }
        )
        == "LTE automatisch · 5G n78"
    )
    assert mb.baender({}) == ""


def test_zellen_entfernung_rolle():
    m = mb.aus_antwort({"NewCurrentAccessTechnology": "5G-NSA", "NewCellList": ZELLEN})
    assert [(z.art, z.entfernung_m) for z in m.zellen] == [("LTE", 1350), ("5G", None)]
    assert [z.art for z in mb.zellen_sortiert(m)] == ["5G", "LTE"]
    assert [mb.rolle(z, m.technik) for z in m.zellen] == ["Anker", "bündelt dazu"]
    assert mb.rolle(m.zellen[0], "LTE") == "verbunden"
    nachbar = mb.Zelle("", "LTE", "", 1, "x", -110, -15)
    assert mb.rolle(nachbar, "LTE") == "in Reichweite"
    assert mb.zellen_sortiert(mb.aus_antwort({})) == []


def test_entfernung_und_stufen():
    assert [mb.entfernung(v) for v in (None, 0, 850, 1000, 1240)] == [
        None,
        None,
        "850 m",
        "1,0 km",
        "1,2 km",
    ]
    assert [mb.stufen(v) for v in (None, -80, -85, -95, -100, -105, -106, -130)] == [
        0,
        4,
        4,
        3,
        2,
        2,
        1,
        1,
    ]
