"""Gemerkte Abrufe: wann wieder fragen."""

from logik import gemerkt as lg


def test_faellig():
    assert lg.faellig(None, "k", 0, 100, 10)
    assert lg.faellig({"rahmen": "anders", "t": 0}, "k", 1, 100, 10)  # andere Kennung: gleich
    assert not lg.faellig({"rahmen": "k", "t": 0}, "k", 99, 100, 10)
    assert lg.faellig({"rahmen": "k", "t": 0}, "k", 100, 100, 10)
    assert not lg.faellig({"rahmen": "k", "fehler_t": 50}, "k", 59, 100, 10)
    assert lg.faellig({"rahmen": "k", "fehler_t": 50}, "k", 60, 100, 10)
