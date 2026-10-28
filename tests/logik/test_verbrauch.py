"""Verbrauch je Tag."""

from datetime import UTC, date, datetime

from logik import auswertung as aw
from logik import verbrauch as vb

TZ = UTC


def ts(tag: int) -> float:
    return datetime(2026, 10, tag, tzinfo=TZ).timestamp()


def test_tage_lueckenlos_und_speedtest():
    down = [(ts(9), 3.0), (ts(11), 2.0), (ts(12), -100.0)]  # Rücksprung zählt 0
    up = [(ts(11), 0.5)]
    punkte = [aw.Punkt(ts(11) + 3600, 128, 40, 20, None, None, "p")]
    liste = vb.tage(down, up, punkte, ts(12) + 3600, 4, TZ)
    assert [t.tag for t in liste] == [date(2026, 10, d) for d in (9, 10, 11, 12)]
    assert (liste[2].down, liste[2].up, liste[2].speedtest) == (2.0, 0.5, 0.252)
    assert liste[1].down == 0 and liste[3].down == 0


def test_kacheln():
    liste = vb.tage([(ts(d), 1.0) for d in range(1, 13)], [], [], ts(12), 12, TZ)
    k = vb.kacheln(liste, 7)
    assert k is not None
    assert (k.heute.tag, k.woche, k.monat, k.schnitt) == (
        date(2026, 10, 12),
        1.0,
        12.0,
        1.0,
    )  # 12.10.2026 ist Montag
    assert vb.kacheln([], 7) is None


def test_speedtest_hoechstens_tagesmenge():
    """GitHub #1: ohne Zählerwerte am Tag (Einrichtung, Zähler kurz weg) war „davon Speedtests“ größer als der Tag –
    der Balken ragte über das Diagramm hinaus."""
    punkte = [aw.Punkt(ts(11) + 3600, 128, 40, 20, None, None, "p")]
    ohne = vb.tage([], [], punkte, ts(11) + 7200, 1, TZ)
    assert ohne[0].speedtest == 0
    wenig = vb.tage([(ts(11), 0.1)], [], punkte, ts(11) + 7200, 1, TZ)
    assert wenig[0].speedtest == 0.1
