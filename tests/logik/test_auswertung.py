"""Speedtest-Auswertung. Die Sollwerte der Quantile stammen aus der JavaScript-Fassung des Altbestands (gleich
gerechnet mit node), damit beide nachweislich übereinstimmen."""

from datetime import UTC, datetime, timedelta

import pytest
from logik import auswertung as aw

TZ = UTC
MONTAG = datetime(2026, 9, 14, tzinfo=TZ)  # ein Montag


@pytest.mark.parametrize(
    ("paare", "p", "soll"),
    [
        ([(10, 1), (20, 1), (30, 1), (40, 1)], 0.5, 25),
        ([(10, 1), (20, 0.25), (100, 1)], 0.5, 20),
        ([(10, 1), (20, 1), (30, 2)], 0.25, 15),
        ([(10, 0)], 0.5, None),
    ],
)
def test_gewichtetes_quantil_wie_javascript(paare, p, soll):
    assert aw.g_quantil(paare, p) == soll


def test_quantil_wie_javascript():
    assert aw.quantil([4, 1, 3, 2], 0.5) == 2.5
    assert aw.quantil([1, 2, 3, 4, 5], 0.25) == 2
    assert aw.quantil([], 0.5) is None


def test_gewicht_und_schwelle():
    p = aw.Punkt(0, 100, 10, 20, "Wien", 20.0, "p")
    assert aw.schwelle(150) == 15 and aw.schwelle(None) == 10
    assert [aw.gewicht(p, m, None, 15) for m in aw.MODI] == [0, 0.25, 1]
    assert aw.gewicht(p, "mit", "Graz", 15) == 0
    assert (
        aw.gewicht(aw.Punkt(0, 1, 1, 1, None, None, "s"), "aus", None, 15) == 1
    )  # ungeprüft zählt


def test_skala_lage():
    g = aw.GROESSEN["down"]
    assert aw.skala_lage(g, 75, 100, 150) == 0.5
    assert aw.skala_lage(g, 300, 100, 150) == 1.0
    assert aw.skala_lage(g, 100, 100, None) == 0.5
    assert aw.skala_lage(aw.GROESSEN["ping"], 25, 20, None) == pytest.approx(
        0.5 + (0.8 - 1) / 0.9
    )  # weniger ist besser
    assert aw.skala_lage(aw.GROESSEN["ping"], 40, 20, None) == 0.0  # begrenzt
    assert aw.skala_lage(g, None, 100, 150) is None


def _punkt(tag: int, stunde: int, down: float, last: float | None = 1.0, server="Wien"):
    t = (MONTAG + timedelta(days=tag, hours=stunde)).timestamp()
    return aw.Punkt(t, down, down / 4, 20.0, server, last, "p")


def test_auswerten_raster_und_kennzahlen():
    punkte = [
        _punkt(0, 20, 60),
        _punkt(1, 20, 70),
        _punkt(2, 21, 65),
        _punkt(3, 19, 55),  # werktags abends
        _punkt(4, 3, 140),
        _punkt(5, 2, 145),
        _punkt(6, 4, 150),
        _punkt(0, 1, 135),  # nachts
        _punkt(1, 12, 0.1),  # Fehlmessung
        _punkt(2, 12, 120, last=40.0),  # belastet
        _punkt(3, 12, 110, server="Graz"),
    ]
    jetzt = (MONTAG + timedelta(days=7)).timestamp()
    a = aw.auswerten(punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ)
    assert (a.gesamt, a.fehl, a.belastet, a.anzahl) == (11, 1, 1, 9)
    assert a.server == (("Wien", 10), ("Graz", 1))
    assert a.raster[0][20] == aw.Zelle(60, 1, 0.4)
    assert a.raster[2][12].anzahl == 0  # belastet und „weglassen“
    assert a.median == 110 and a.anteil == pytest.approx(110 / 150)
    assert a.auffaellig and "18–22 Uhr" in a.auffaellig
    assert a.letzte is not None and a.letzte.down == 110
    halb = aw.auswerten(punkte, jetzt, 0, 28, "down", "halb", None, 150, 150, TZ)
    assert halb.raster[2][12].anzahl == 1
    graz = aw.auswerten(punkte, jetzt, 0, 28, "down", "mit", "Graz", 150, 150, TZ)
    assert graz.anzahl == 1 and graz.gesamt == 1


def test_tagesverlauf_wochentag_und_datum():
    """WU-0004: Median, niedrigste und höchste Messung je Stunde; Wochentag über alle diese Tage, Datum nur ein Tag."""
    punkte = [
        _punkt(0, 20, 60),
        _punkt(7, 20, 90),  # Montag eine Woche später, gleiche Stunde
        _punkt(7, 20, 30),
        _punkt(7, 3, 140),
        _punkt(7, 4, 150, last=40.0),  # belastet und „weglassen“ → zählt nicht
        _punkt(8, 3, 100),  # Dienstag
    ]
    jetzt = (MONTAG + timedelta(days=9)).timestamp()
    ohne = aw.auswerten(punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ)
    assert ohne.verlauf is None
    assert ohne.tage_liste == (("2026-09-22", 1), ("2026-09-21", 3), ("2026-09-14", 1))
    mo = aw.auswerten(punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ, tag=0).verlauf
    assert mo is not None and len(mo.stunden) == 24 and (mo.tag, mo.datum) == (0, None)
    assert mo.stunden[20] == aw.Stunde(60, 30, 90, 3, 60)
    assert mo.stunden[4] == aw.Stunde(None, None, None, 0, 140)  # Nachbar 3 Uhr zählt mit
    assert mo.stunden[21].glatt == 60 and mo.stunden[22].glatt is None
    assert (mo.beste, mo.schwaechste) == (3, 20)
    tag = aw.auswerten(
        punkte,
        jetzt,
        0,
        28,
        "down",
        "aus",
        None,
        150,
        150,
        TZ,
        tag=0,
        datum=(MONTAG + timedelta(days=7)).date(),
    ).verlauf
    assert tag is not None and (tag.tag, tag.datum) == (None, "2026-09-21")  # Datum hat Vorrang
    assert tag.stunden[20] == aw.Stunde(60, 30, 90, 2, 60)
    leer = aw.auswerten(
        punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ, datum=MONTAG.date().replace(day=1)
    )
    assert leer.verlauf is not None and leer.verlauf.beste is None
    assert all(s.anzahl == 0 for s in leer.verlauf.stunden)
    # nur eine Stunde gemessen: keine beste und schwächste (wäre dieselbe Stunde)
    di = aw.auswerten(punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ, tag=1).verlauf
    assert (
        di is not None and di.stunden[3].anzahl == 1 and (di.beste, di.schwaechste) == (None, None)
    )
    # Ping: der kleinere Median ist der bessere
    g = aw.GROESSEN["ping"]
    v = aw.verlauf(g, [[(30.0, 1)], [(18.0, 1)], [(18.0, 1)]] + [[] for _ in range(21)], 0, None)
    assert (v.beste, v.schwaechste) == (1, 0)  # gleicher Median: die frühere Stunde
    # geglättet: gewichteter Mittelwert über ±1 Stunde; Wochentag über Mitternacht, Datum nicht
    w = [[] for _ in range(24)]
    w[0], w[1], w[23] = [(30.0, 1)], [(60.0, 1), (90.0, 0.25)], [(10.0, 1)]
    wt = aw.verlauf(aw.GROESSEN["down"], w, 0, None).stunden
    assert wt[0].glatt == pytest.approx((30 + 60 + 22.5 + 10) / 3.25)
    assert wt[1].glatt == pytest.approx((30 + 60 + 22.5) / 2.25) and wt[2].glatt == pytest.approx(
        82.5 / 1.25
    )
    tg = aw.verlauf(aw.GROESSEN["down"], w, None, MONTAG.date()).stunden
    assert tg[0].glatt == pytest.approx((30 + 60 + 22.5) / 2.25) and tg[22].glatt == 10
    ping = aw.auswerten(punkte, jetzt, 0, 28, "ping", "aus", None, None, 150, TZ, tag=0).verlauf
    assert ping is not None and ping.stunden[3].median == 20.0
    assert (
        aw.auswerten(punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ, tag=9).verlauf is None
    )


def test_kachel_messungen():
    """AN-0005: die Messungen hinter einer Kachel – gleiche Auswahl und Gewichte wie das Raster."""
    punkte = [
        _punkt(0, 20, 60),
        _punkt(7, 20, 90),
        _punkt(7, 20, 30, last=40.0),  # belastet
        _punkt(7, 20, 0.1),  # Fehlmessung: fehlt
        _punkt(7, 20, 80, server="Graz"),
        _punkt(7, 21, 70),  # andere Stunde
        _punkt(8, 20, 70),  # anderer Tag
    ]
    jetzt = (MONTAG + timedelta(days=9)).timestamp()
    k = aw.kachel(punkte, jetzt, 0, 28, "down", "aus", None, 150, TZ, 0, 20)
    raster = aw.auswerten(punkte, jetzt, 0, 28, "down", "aus", None, 150, 150, TZ).raster[0][20]
    assert (k.median, k.anzahl) == (raster.median, raster.anzahl) == (80, 3)
    assert (k.min, k.max, k.belastet, k.weitere) == (60, 90, 1, 0)
    assert k.messungen[0].t >= k.messungen[-1].t and k.messungen[-1].wert == 60  # neueste zuerst
    belastet = next(m for m in k.messungen if m.belastet)
    assert belastet.wert == 30 and belastet.gewicht == 0
    halb = aw.kachel(punkte, jetzt, 0, 28, "down", "halb", None, 150, TZ, 0, 20)
    assert halb.anzahl == 4 and halb.min == 30
    graz = aw.kachel(punkte, jetzt, 0, 28, "down", "mit", "Graz", 150, TZ, 0, 20)
    assert graz.anzahl == 1 and graz.messungen[0].server == "Graz"
    viele = [_punkt(7 * (i % 2), 5, 100.0 + i) for i in range(25)]
    v = aw.kachel(viele, jetzt, 0, 28, "down", "aus", None, 150, TZ, 0, 5)
    assert len(v.messungen) == aw.KACHEL_LISTE and v.weitere == 5 and v.anzahl == 25
    leer = aw.kachel(punkte, jetzt, 0, 28, "down", "aus", None, 150, TZ, 3, 3)
    assert (leer.median, leer.anzahl, leer.messungen) == (None, 0, ())


def test_auswerten_ab_datum_und_ping_ohne_tarif():
    punkte = [_punkt(0, 1, 100), _punkt(6, 1, 100)]
    jetzt = (MONTAG + timedelta(days=7)).timestamp()
    a = aw.auswerten(
        punkte,
        jetzt,
        (MONTAG + timedelta(days=3)).timestamp(),
        28,
        "ping",
        "mit",
        None,
        None,
        150,
        TZ,
    )
    assert a.gesamt == 1 and a.median == 20.0 and a.anteil is None
    assert a.raster[6][1].lage == 0.5  # gegen den Median


def test_volumen():
    assert aw.volumen_mb(aw.Punkt(0, 128, 40, 20, None, None, "p")) == pytest.approx(
        (128 + 40) * aw.MESS_S / 8
    )


def test_anteil():
    assert (
        aw.anteil(75, 150) == 0.5 and aw.anteil(None, 150) is None and aw.anteil(75, None) is None
    )
