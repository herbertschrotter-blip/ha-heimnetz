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
