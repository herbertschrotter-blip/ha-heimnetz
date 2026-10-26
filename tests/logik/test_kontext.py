"""Momentaufnahme zu einer Speedtest-Messung (WU-0005)."""

from datetime import date

from daten import ZELLEN
from logik import kontext as kx
from logik import mobil as mb

MO, SA = date(2026, 10, 19), date(2026, 10, 24)


def test_mobilfunk_aus_dem_stand():
    m = mb.aus_antwort(
        {"NewCurrentAccessTechnology": "5G-NSA", "NewCellList": ZELLEN, "NewUptime": "3600"}
    )
    d = kx.mobilfunk(m)
    assert d == {
        "netz": "5G-NSA",
        "zelle": "abcde-0b",
        "anlage": "abcde",
        "pci": 443,
        "rsrp": -100,
        "rsrq": -11,
        "nr_aktiv": True,
        "nr_pci": 121,
        "nr_rsrp": -94,
        "nr_rsrq": -10,
        "entfernung_m": 1350,
        "nachbarzellen": 0,
        "plmn": "23205",
        "tac": "C0FC",
        "verbunden_s": 3600,
    }
    ohne_5g = kx.mobilfunk(
        mb.aus_antwort(
            {"NewCurrentAccessTechnology": "LTE", "NewCellList": ZELLEN.replace("nr5g", "lte")}
        )
    )
    assert (
        ohne_5g["nr_aktiv"] is False and "nr_rsrp" not in ohne_5g and ohne_5g["nachbarzellen"] == 1
    )
    assert kx.mobilfunk(None) == {}


def test_ausloeser_und_tagesart():
    assert kx.ausloeser(1000, 990, "von Hand", None) == kx.JETZT
    assert kx.ausloeser(1000, 990, "fällig", None) == kx.PLAN
    assert kx.ausloeser(1000, 990, "fällig", {"n": 3, "lauf": 2}) == kx.SERIE
    assert kx.ausloeser(1000, 1000 - kx.AUSLOESER_FENSTER_S - 1, "fällig", None) == kx.OOKLA
    assert kx.ausloeser(1000, 0, None, None) == kx.OOKLA
    assert kx.tagesart(MO, False) == "werktag" and kx.tagesart(SA, False) == "wochenende"
    assert kx.tagesart(MO, True) == "feiertag"


def test_momentaufnahme_ookla_wetter():
    o = kx.ookla(
        {"jitter": "3.14159", "bufferbloat": "B", "anbieter": "Drei", "jitter_up": "unknown"}
    )
    assert o == {"jitter": 3.14, "bufferbloat": "B", "anbieter": "Drei"}
    w = kx.wetter("partlycloudy", {"temperature": 12.3, "humidity": 78, "cloud_coverage": None})
    assert w == {"wetter": "partlycloudy", "temperatur": 12.3, "feuchte": 78.0}
    assert kx.wetter("unavailable", {}) == {}
    a = kx.momentaufnahme(
        {"netz": "LTE", "fremd": 1, "online": None}, o, w, {"tagesart": "werktag"}
    )
    assert list(a) == [
        "quelle",
        "jitter",
        "bufferbloat",
        "anbieter",
        "netz",
        "wetter",
        "temperatur",
        "feuchte",
        "tagesart",
    ]
    assert a["quelle"] == kx.MESSUNG and "fremd" not in a


def test_wert_und_zelle_aus_verlauf():
    verlauf = [(100.0, "LTE"), (200.0, "unavailable"), (300.0, "5G-NSA")]
    assert kx.wert_bei(verlauf, 50) is None
    assert kx.wert_bei(verlauf, 150) == "LTE" and kx.wert_bei(verlauf, 250) is None
    assert kx.wert_bei(verlauf, 300) == "5G-NSA"
    journal = [
        (100.0, "Mobilfunk: Funkzelle gewechselt aaaaa-64/1 → aaaaa-00/2 (Empfang RSRP -90 dBm)"),
        (200.0, "Mobilfunk: Technik gewechselt LTE → 5G-NSA"),
        (300.0, "Mobilfunk: Funkzelle gewechselt aaaaa-00/2 → bbbbb-0a/3 (Empfang RSRP -95 dBm)"),
    ]
    assert kx.zelle_bei(journal, 50) == "aaaaa-64"  # vor dem ersten Wechsel: dessen Ausgangszelle
    assert kx.zelle_bei(journal, 150) == "aaaaa-00" and kx.zelle_bei(journal, 999) == "bbbbb-0a"
    assert kx.zelle_bei([], 1) is None
    ookla = [(90.0, "alt"), (100.0, "unknown"), (130.0, "neu")]
    assert (
        kx.wert_nach(ookla, 120) == "neu" and kx.wert_nach(ookla, 95) is None
    )  # „unknown“ zählt nicht
    assert kx.wert_nach(ookla, 130) is None and kx.wert_nach(ookla, 120, fenster=5) is None


def test_nachtrag():
    verlaeufe = {
        "netz": [(0.0, "5G-NSA")],
        "rsrp": [(0.0, "-93.0")],
        "nr_rsrp": [(0.0, "-101")],
        "jitter": [(0.0, "9.9"), (55.0, "2.5")],  # 9,9 gehört zur vorigen Messung
        "temperatur": [(0.0, "11.5")],
        "wetter": [(0.0, "rainy")],
    }
    journal = [
        (10.0, "Mobilfunk: Funkzelle gewechselt aaaaa-64/1 → aaaaa-00/2 (Empfang RSRP -90 dBm)")
    ]
    n = kx.nachtrag(50.0, verlaeufe, journal, True, MO)
    assert n == {
        "quelle": kx.NACHGETRAGEN,
        "jitter": 2.5,
        "netz": "5G-NSA",
        "zelle": "aaaaa-00",
        "anlage": "aaaaa",
        "rsrp": -93,
        "nr_aktiv": True,
        "nr_rsrp": -101,
        "wetter": "rainy",
        "temperatur": 11.5,
        "tagesart": "feiertag",
    }
    leer = kx.nachtrag(50.0, {}, [], False, SA)
    assert leer == {"quelle": kx.NACHGETRAGEN, "tagesart": "wochenende"}
