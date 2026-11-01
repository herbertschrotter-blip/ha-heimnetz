"""Diagnose-Log über die Schnittstelle: aus ab Werk, nur Admins, Aufzeichnung, Frist, löschen."""

import pytest

from custom_components.heimnetz.logik import diagnoselog as dl
from custom_components.heimnetz.speicher import Datenbank

T = 1_800_000_000.0


@pytest.fixture
def db(tmp_path):
    d = Datenbank(tmp_path / "t.db")
    d.oeffnen()
    yield d
    d.schliessen()


def test_speichern_lesen_frist_und_loeschen(db):
    alt = dl.Eintrag(T - dl.AUFBEWAHREN_S - 1, dl.STAND, "", {"ereignis": "stand"})
    neu = dl.Eintrag(T, dl.GERAET, "AA", {"ereignis": "weg", "name": "x"})
    assert db.diagnoselog_schreiben([alt, neu]) == 2
    assert db.aufraeumen(T) == 0  # eigene Frist, zählt beim Journal nicht mit
    assert db.diagnoselog_lesen(0) == [neu]
    db.diagnoselog_loeschen()
    assert db.diagnoselog_lesen(0) == []
