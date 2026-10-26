"""Messplan: fällig, Zeitfenster, nächste Messung, Verschieben bei Verkehr."""

from datetime import UTC, datetime

import pytest
from logik import messplan as mp
from logik.einstellungen import Ungueltig

TZ = UTC


def ts(h: int, m: int = 0, tag: int = 12) -> float:
    return datetime(2026, 10, tag, h, m, tzinfo=TZ).timestamp()


def test_pruefen_und_dict():
    p = mp.pruefen({"an": True, "takt_h": 2, "von": "22:00", "bis": "06:00", "verkehr": "messen"})
    assert (p.an, p.takt_h, p.von_min, p.bis_min, p.verkehr) == (True, 2, 1320, 360, "messen")
    assert mp.pruefen(p.als_dict()) == p
    assert mp.pruefen(None) == mp.Messplan()
    assert mp.pruefen({"bis": "24:00"}).bis_min == 1440


@pytest.mark.parametrize(
    "daten",
    [
        {"takt_h": 3},
        {"takt_h": "x"},
        {"verkehr": "egal"},
        {"von": "25:00"},
        {"von": "ab"},
        {"von": "08:00", "bis": "08:00"},
    ],
)
def test_pruefen_ungueltig(daten):
    with pytest.raises(Ungueltig):
        mp.pruefen(daten)


def test_zeitfenster():
    tag = mp.pruefen({"von": "08:00", "bis": "18:00"})
    nacht = mp.pruefen({"von": "22:00", "bis": "06:00"})
    ganz = mp.pruefen({})
    t = lambda h: datetime(2026, 10, 12, h, tzinfo=TZ)  # noqa: E731
    assert mp.im_fenster(tag, t(8)) and not mp.im_fenster(tag, t(18))
    assert (
        mp.im_fenster(nacht, t(23))
        and mp.im_fenster(nacht, t(5))
        and not mp.im_fenster(nacht, t(12))
    )
    assert all(mp.im_fenster(ganz, t(h)) for h in range(24))


def test_naechste():
    plan = mp.pruefen({"an": True, "takt_h": 4})
    assert mp.naechste(plan, None, ts(10), TZ) == ts(10)
    assert mp.naechste(plan, ts(9), ts(10), TZ) == ts(13)
    nachts = mp.pruefen({"an": True, "takt_h": 1, "von": "01:00", "bis": "05:00"})
    assert mp.naechste(nachts, ts(4, 30), ts(10), TZ) == ts(
        1, tag=13
    )  # Fenster heute vorbei → morgen 01:00
    assert mp.naechste(nachts, None, ts(0, 10), TZ) == ts(1)
    assert mp.naechste(mp.pruefen({"an": False}), None, ts(10), TZ) is None


def test_entscheiden_ruhig_und_nicht_faellig():
    plan = mp.pruefen({"an": True, "takt_h": 4})
    assert mp.entscheiden(plan, ts(9), ts(10), TZ, 1.0, 15).aktion == mp.NICHTS
    assert mp.entscheiden(plan, ts(5), ts(10), TZ, 1.0, 15).aktion == mp.MESSEN
    assert (
        mp.entscheiden(plan, ts(5), ts(10), TZ, None, 15).aktion == mp.MESSEN
    )  # Verkehr unbekannt


def test_verschieben_alle_5_minuten_hoechstens_30():
    plan = mp.pruefen({"an": True, "takt_h": 4})
    e = mp.entscheiden(plan, ts(5), ts(10), TZ, 40.0, 15)
    assert (e.aktion, e.wartet_seit, e.neuer_versuch) == (mp.WARTEN, ts(10), ts(10, 5))
    # nach 2 Minuten: nicht neu prüfen, auch wenn es ruhig ist
    assert mp.entscheiden(plan, ts(5), ts(10, 2), TZ, 1.0, 15, e) == e
    # nach 5 Minuten ruhig: messen
    assert mp.entscheiden(plan, ts(5), ts(10, 5), TZ, 1.0, 15, e).aktion == mp.MESSEN
    # immer belastet: nach 30 Minuten trotzdem
    for minute in range(5, 30, 5):
        e = mp.entscheiden(plan, ts(5), ts(10, minute), TZ, 40.0, 15, e)
        assert e.aktion == mp.WARTEN and e.wartet_seit == ts(10)
    assert e.neuer_versuch == ts(10, 30)
    assert mp.entscheiden(plan, ts(5), ts(10, 30), TZ, 40.0, 15, e).aktion == mp.MESSEN


def test_trotzdem_messen_eingestellt():
    plan = mp.pruefen({"an": True, "verkehr": "messen"})
    assert mp.entscheiden(plan, None, ts(10), TZ, 99.0, 15).aktion == mp.MESSEN


def test_beginn_24_uhr_ist_mitternacht():
    plan = mp.pruefen({"an": True, "von": "24:00", "bis": "06:00"})
    assert plan.von_min == 0
    assert mp.naechste(plan, None, ts(12), TZ) == ts(0, tag=13)  # kein Absturz, morgen 00:00


def test_vorgabe_neuer_installationen_misst_4_mal_am_tag():
    """WU-0006: zurückhaltend – jede Messung kostet Datenvolumen."""
    assert mp.NEU.an and mp.tests_am_tag(mp.NEU) == 4
    assert mp.pruefen(mp.NEU.als_dict()) == mp.NEU  # gespeichert und wieder geladen
    assert not mp.Messplan().an  # gespeicherter Plan ohne Feld „an“ bleibt aus


def test_tests_am_tag_nach_fenster_und_takt():
    assert mp.tests_am_tag(mp.Messplan()) == 0  # aus
    assert mp.tests_am_tag(mp.pruefen({"an": True, "takt_h": 1})) == 24
    assert (
        mp.tests_am_tag(mp.pruefen({"an": True, "takt_h": 4, "von": "06:00", "bis": "22:00"})) == 4
    )
    assert (
        mp.tests_am_tag(mp.pruefen({"an": True, "takt_h": 2, "von": "22:00", "bis": "02:00"})) == 2
    )
    assert (
        mp.tests_am_tag(mp.pruefen({"an": True, "takt_h": 24, "von": "08:00", "bis": "09:00"})) == 1
    )
    assert (
        mp.tests_am_tag(mp.pruefen({"an": True, "takt_h": 6, "von": "07:00", "bis": "08:30"})) == 1
    )


def test_volumen_je_messung_und_tag():
    v = mp.volumen(mp.NEU, 150.0, 30.0)
    assert v == {"tests_tag": 4, "je_test_mb": 270, "tag_mb": 1080, "monat_gb": 32.4}
    assert mp.volumen(mp.NEU, None, None) == {
        "tests_tag": 4,
        "je_test_mb": None,
        "tag_mb": None,
        "monat_gb": None,
    }
    assert mp.volumen(mp.Messplan(), 80.0, None)["tag_mb"] == 0  # Plan aus: nur „je Messung“
