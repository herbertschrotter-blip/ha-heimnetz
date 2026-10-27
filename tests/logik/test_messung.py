"""Speedtest-Messung mit Grundlast."""

from logik import messung as ms
from test_verkehr import JETZT, ring


def test_eintragen_mit_grundlast():
    m = ms.eintragen(
        JETZT, "86.47", 20.41, "74", "Wien – A1", ring([30, 30, 30, 30, 30, 30, 30, 120])
    )
    assert (m.down, m.up, m.ping, m.server, m.last_down, m.last_up) == (
        86.47,
        20.41,
        74.0,
        "Wien – A1",
        30.0,
        3.0,
    )


def test_fehlmessung_und_ohne_grundlast():
    m = ms.eintragen(JETZT, "unavailable", None, "", "unknown", [])
    assert (m.down, m.up, m.ping, m.server, m.last_down) == (None, None, None, "", None)


def test_an0007_geloeschte_kommen_nicht_wieder():
    """AN-0007: Merkliste gelöschter Zeitpunkte – Ookla zeigt die Messung weiter als letzten Test."""
    a, b = (
        ms.Messung(JETZT, 90.0, 20.0, 21.0, "Wien", None, None),
        ms.Messung(JETZT + 3600, 80.0, 20.0, 21.0, "Wien", None, None),
    )
    assert ms.ohne_geloeschte([a, b], [JETZT + 0.2]) == [b]  # Rundung auf dem Weg zählt nicht
    assert ms.ohne_geloeschte([a, b], []) == [a, b]
    assert ms.ist_geloescht(JETZT, [JETZT - 1000, JETZT])
    assert not ms.ist_geloescht(JETZT + 1, [JETZT])  # eine Sekunde daneben ist eine andere Messung
    assert ms.gleich(JETZT, JETZT + 0.49) and not ms.gleich(JETZT, JETZT + 0.5)


def test_an0007_journalzeile_nur_mit_zeit():
    from datetime import UTC

    e = ms.geloescht_ereignis(1_800_000_000.0, UTC)
    assert (e.art, e.stufe, e.mac) == ("messung_geloescht", "info", "")
    assert e.text == "Messung 15.01.2027 08:00 gelöscht"
    assert (
        ms.geloescht_ereignis(1_800_000_000.0, UTC, "en").text
        == "Measurement 2027-01-15 08:00 deleted"
    )
