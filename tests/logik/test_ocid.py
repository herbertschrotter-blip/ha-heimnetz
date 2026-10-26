"""OpenCellID-Datenabzug: Zeilen lesen, Anbieter, Zuordnung zu Masten."""

from logik import karte as ka
from logik import ocid as lc

RAHMEN = (48.1, 16.1, 48.5, 16.5)
KOPF = "radio,mcc,net,area,cell,unit,lon,lat,range,samples,changeable,created,updated,averageSignal"


def test_zeilen_lesen():
    zeilen = [
        KOPF,
        "LTE,232,5,6699,178956800,0,16.37,48.2,1000,5,1,0,0,0",
        "NR,232,5,6699,99,0,16.371,48.201,500,2,1,0,0,0",
        "GSM,232,1,1,1,0,16.0,48.2,1000,1,1,0,0,0",  # außerhalb (West)
        "CDMA,232,1,1,1,0,16.3,48.2,1,1,1,0,0,0",  # unbekannte Technik
        "LTE,232,x,1,1,0,16.3,48.2,1,1,1,0,0,0",  # kaputt
        "zu,kurz",
    ]
    assert lc.zellen_aus(zeilen, RAHMEN) == [
        lc.OcidZelle("LTE", 5, ka.Ort(48.2, 16.37)),
        lc.OcidZelle("5G", 5, ka.Ort(48.201, 16.371)),
    ]
    assert lc.ist_csv(KOPF.encode()) and lc.ist_csv(b"LTE,232,5")
    assert not lc.ist_csv(b'{"error":"RATE_LIMITED"}') and not lc.ist_csv(b"Invalid token")


def test_anbieter_und_zuordnung():
    assert [lc.anbieter(n) for n in (1, 3, 5, 10, 99)] == [
        "A1",
        "Magenta",
        "Drei",
        "Drei",
        "Netz 232 99",
    ]
    mast_a, mast_b = ka.Ort(48.2, 16.37), ka.Ort(48.21, 16.37)  # 1,1 km auseinander
    zellen = [
        lc.OcidZelle("LTE", 5, ka.Ort(48.2005, 16.37)),  # 55 m von A
        lc.OcidZelle("5G", 5, ka.Ort(48.2010, 16.37)),  # 110 m von A
        lc.OcidZelle("LTE", 1, ka.Ort(48.2095, 16.37)),  # 55 m von B
        lc.OcidZelle("LTE", 3, ka.Ort(48.205, 16.37)),  # 555 m von beiden: zu weit
    ]
    a, b = lc.je_mast([mast_a, mast_b], zellen)
    assert a == lc.MastInfo(("Drei",), ("LTE", "5G"), 2)
    assert b == lc.MastInfo(("A1",), ("LTE",), 1)
    assert lc.je_mast([ka.Ort(47.0, 15.0)], zellen) == [None]
    assert lc.je_mast([], zellen) == []


def test_faellig():
    assert lc.faellig(None, "r", 0) and lc.faellig({"rahmen": "x", "t": 0}, "r", 1)
    assert not lc.faellig({"rahmen": "r", "t": 1000}, "r", 1000 + lc.GUELTIG_S - 1)
    assert lc.faellig({"rahmen": "r", "t": 1000}, "r", 1000 + lc.GUELTIG_S)
    f = {"rahmen": "r", "fehler_t": 1000}
    assert not lc.faellig(f, "r", 1000 + lc.NOCHMAL_S - 1) and lc.faellig(
        f, "r", 1000 + lc.NOCHMAL_S
    )
