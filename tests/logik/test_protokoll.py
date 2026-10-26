"""Ereignisprotokoll der Box."""

from datetime import datetime

from daten import GERAETELOG
from logik import protokoll as pr


def test_xml_aelteste_zuerst_und_abgleich():
    zeilen = pr.aus_xml(GERAETELOG)
    assert [z.zeit for z in zeilen] == ["10:01:00", "10:05:00"]
    gesehen: list[str] = []
    neu = pr.neue_zeilen(zeilen, gesehen)
    assert [n.kategorie for n in neu] == ["wlan", "internet"]
    assert neu[1].zeitpunkt == datetime(2026, 9, 19, 10, 5)
    assert pr.neue_zeilen(zeilen, gesehen) == []


def test_text_und_wiederholung():
    zeilen = pr.aus_text(
        "19.09.26 10:05:00 Anmeldung fehlgeschlagen.\n19.09.26 10:01:00 WLAN-Gerät angemeldet\nMüll"
    )
    assert len(zeilen) == 2
    a = pr.BoxZeile("19.09.26", "10:00:00", "", "", "X fehlgeschlagen.")
    b = pr.BoxZeile(
        "19.09.26", "10:00:00", "", "", "X fehlgeschlagen. [3 Meldungen seit 19.09.26 09:00:00]"
    )
    assert pr.schluessel(a) == pr.schluessel(b)


def test_kategorie():
    assert pr.kategorie("", "Mobilfunk-Verbindung getrennt") == "internet"
    assert pr.kategorie("net", "egal") == "internet"
    assert pr.kategorie("", "Anruf von unbekannt") == "telefon"
    assert pr.kategorie("", "Zeitserver") == "system"


def test_gesehen_wird_gekuerzt():
    gesehen = [f"alt{i}" for i in range(pr.GESEHEN_MERKEN)]
    pr.neue_zeilen([pr.BoxZeile("19.09.26", "10:00:00", "", "", "neu")], gesehen)
    assert len(gesehen) == pr.GESEHEN_MERKEN and gesehen[-1].endswith("neu")


def test_unbekanntes_datum_bleibt_als_rohzeit():
    neu = pr.neue_zeilen([pr.BoxZeile("gestern", "?", "", "", "x")], [])
    assert neu[0].zeitpunkt is None and neu[0].roh_zeit == "gestern ?"
