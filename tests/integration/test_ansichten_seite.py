"""Fertige Felder für die Seite, die sie früher selbst gerechnet hat (die Seite rechnet nichts Fachliches)."""

from custom_components.heimnetz.ansichten import _trend_besser


def test_trend_besser_nach_groesse():
    assert _trend_besser(11.5, "down") is True
    assert _trend_besser(-3.0, "up") is False
    assert _trend_besser(-4.0, "ping") is True  # beim Ping ist weniger besser
    assert _trend_besser(2.0, "ping") is False
    assert _trend_besser(0.0, "down") is None and _trend_besser(None, "down") is None
