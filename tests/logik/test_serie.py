"""Speedtest-Serie (WU-0001): Median, Spanne, Anteil vom Tarif; Anzahl im Messplan."""

import pytest
from logik import einstellungen as es
from logik import messplan as mp
from logik import serie as sr


def test_median_und_spanne():
    laeufe = [
        sr.Lauf(100.0, "Wien", 118.0, 41.0, 23.0),
        sr.Lauf(160.0, "Wien", 60.0, 39.0, 27.0),  # Ausreißer verzieht den Median nicht
        sr.Lauf(220.0, "Graz", 121.0, None, 22.0),
    ]
    e = sr.ergebnis(laeufe, 150.0, 3)
    assert e["down"] == {"median": 118.0, "min": 60.0, "max": 121.0}
    assert e["up"] == {"median": 40.0, "min": 39.0, "max": 41.0}  # fehlender Wert zählt nicht
    assert (e["anteil"], e["t"], e["geplant"], e["server"]) == (79, 100.0, 3, ["Graz", "Wien"])
    assert len(e["laeufe"]) == 3 and e["laeufe"][0]["down"] == 118.0


def test_ohne_tarif_und_ohne_werte():
    e = sr.ergebnis([sr.Lauf(1.0, None, None, None, None)], None, 2)
    assert e["down"] is None and e["anteil"] is None and e["server"] == []


def test_messplan_serie():
    assert mp.Messplan().serie == 3 and mp.pruefen({}).serie == 3
    assert mp.pruefen({"serie": 5}).als_dict()["serie"] == 5
    for falsch in (1, 6, "x"):
        with pytest.raises(es.Ungueltig, match="Serie"):
            mp.pruefen({"serie": falsch})


def test_an0007_geloeschter_durchlauf_faellt_aus_der_serie():
    laeufe = [
        sr.Lauf(100.0, "Wien", 118.0, 41.0, 23.0),
        sr.Lauf(160.0, "Wien", 60.0, 39.0, 27.0),
        sr.Lauf(220.0, "Graz", 121.0, None, 22.0),
    ]
    gemerkt = sr.ergebnis(laeufe, 150.0, 3)
    rest = sr.ohne_lauf(gemerkt, lambda t: abs(t - 160.0) < 0.5, 150.0)
    assert rest is not None and [x["t"] for x in rest["laeufe"]] == [100.0, 220.0]
    assert rest["down"] == {"median": 119.5, "min": 118.0, "max": 121.0} and rest["geplant"] == 3
    assert sr.ohne_lauf(gemerkt, lambda t: t == 999.0, 150.0) is None  # nicht betroffen
    leer = sr.ohne_lauf(sr.ergebnis(laeufe[:1], None, 1), lambda t: True, None)
    assert leer == {}  # kein Durchlauf mehr: keine Serie zeigen
