"""Hilfen für Werte der Box."""

from logik import werte


def test_ohne_mac():
    assert werte.ohne_mac("Pi (33:44:01) ist offline") == "Pi ist offline"
    assert (
        werte.ohne_mac("Gerät 00:11:22:33:44:55 angemeldet")
        == "Gerät [Hardware-Adresse] angemeldet"
    )
    assert werte.ohne_mac("Zeit 10:05:00 bleibt") == "Zeit 10:05:00 bleibt"


def test_zahlen_und_wahrheitswerte():
    assert (
        werte.ganzzahl("-93.5"),
        werte.ganzzahl(""),
        werte.ja("1"),
        werte.ja(True),
        werte.ja("0"),
    ) == (-93, None, True, True, False)
