"""Datenbank: Schema-Version, Schreiben/Lesen, keine Doppelten, Sicherung, Aufräumen (G-14). Jede Datei in tmp_path."""

import sqlite3
from datetime import datetime

import pytest

from custom_components.heimnetz import speicher as sp
from custom_components.heimnetz.logik.ereignis import Ereignis
from custom_components.heimnetz.logik.messung import Messung
from custom_components.heimnetz.logik.protokoll import Protokolleintrag

T = 1_800_000_000.0


@pytest.fixture
def db(tmp_path):
    d = sp.Datenbank(tmp_path / "heimnetz" / "heimnetz.db")
    d.oeffnen()
    yield d
    d.schliessen()


def eintrag(text, t=datetime(2026, 9, 19, 10, 5)):
    return Protokolleintrag(t, "19.09.26 10:05:00", "internet", text, f"19.09.26 10:05:00 {text}")


def test_schema_version(db):
    assert (
        int(sqlite3.connect(db.pfad).execute("PRAGMA user_version").fetchone()[0])
        == sp.SCHEMA_VERSION
    )


def test_neueres_schema_wird_nicht_angefasst(tmp_path):
    pfad = tmp_path / "x.db"
    con = sqlite3.connect(pfad)
    con.execute(f"PRAGMA user_version = {sp.SCHEMA_VERSION + 1}")
    con.close()
    with pytest.raises(sp.SchemaZuNeu):
        sp.Datenbank(pfad).oeffnen()


def test_zweimal_oeffnen_aendert_nichts(db):
    db.journal_schreiben([sp.Journalzeile(T, Ereignis("start", "info", "x"))])
    db.schliessen()
    db.oeffnen()
    assert db.anzahl()["journal"] == 1


def test_journal_und_verlauf_je_geraet(db):
    db.journal_schreiben(
        [
            sp.Journalzeile(T, Ereignis("offline", "info", "a offline", "AA")),
            sp.Journalzeile(T + 60, Ereignis("online", "info", "a online", "AA")),
            sp.Journalzeile(T + 120, Ereignis("befund", "kritisch", "B")),
        ]
    )
    assert [z.ereignis.art for z in db.journal_lesen()] == ["befund", "online", "offline"]
    assert [z.ereignis.art for z in db.journal_lesen(nur_wichtig=True)] == ["befund"]
    assert [z.ereignis.art for z in db.geraet_lesen("AA", T + 30)] == ["online"]
    assert db.letzter_zustand("AA", T + 30) == "offline" and db.letzter_zustand("BB", T) is None


def test_protokoll_ohne_doppelte(db):
    assert db.protokoll_schreiben([eintrag("Getrennt."), eintrag("Getrennt.")]) == 1
    assert db.protokoll_schreiben([eintrag("Getrennt."), eintrag("Verbunden.", None)]) == 1
    zeilen = db.protokoll_lesen(("internet",))
    assert [z.text for z in zeilen] == ["Getrennt.", "Verbunden."]  # ohne Zeit am Ende
    assert db.protokoll_lesen(("wlan",)) == []


def test_messungen(db):
    m = Messung(T, 86.5, 20.4, 74.0, "Wien", 30.0, 3.0)
    assert db.messungen_schreiben([m, m]) == 1
    assert db.messungen_lesen() == [m] and db.messungen_lesen(T + 1) == []


def test_messung_mit_momentaufnahme_und_nachtrag(db):
    """WU-0005: Momentaufnahme mit der Messung; nachgetragen wird nur, wo noch keine steht."""
    mit = Messung(T, 1, 1, 1, "", None, None, {"quelle": "messung", "netz": "5G-NSA", "rsrp": -93})
    ohne = Messung(T + 60, 2, 2, 2, "", None, None)
    db.messungen_schreiben([mit, ohne])
    assert [m.kontext for m in db.messungen_lesen()] == [mit.kontext, {}]
    assert db.ohne_kontext(0) == [T + 60]
    assert (
        db.kontext_nachtragen(
            {T: {"quelle": "nachgetragen"}, T + 60: {"quelle": "nachgetragen", "netz": "LTE"}}
        )
        == 1
    )
    assert [m.kontext.get("netz") for m in db.messungen_lesen()] == ["5G-NSA", "LTE"]
    assert db.ohne_kontext(0) == [] and db.kontext_nachtragen({}) == 0


def test_an0007_messung_loeschen_mit_merkliste_und_journal(db):
    """AN-0007: Messung samt Momentaufnahme weg, Zeitpunkt gemerkt, eine Journalzeile; kommt nicht wieder herein."""
    a = Messung(T, 1, 1, 1, "", None, None, {"quelle": "messung"})
    b = Messung(T + 3600, 2, 2, 2, "", None, None, {"quelle": "messung"})
    db.messungen_schreiben([a, b])

    def text(t):
        return Ereignis("messung_geloescht", "info", f"weg {t}")

    assert db.messung_loeschen(T + 7200, T + 9000, text) is None  # unbekannte Kennung
    assert db.messung_loeschen(T + 3600.2, T + 9000, text) == T + 3600  # Rundung zählt nicht
    assert db.messungen_lesen() == [a] and db.letzte_messung() == T
    assert db.ist_geloescht(T + 3600) and not db.ist_geloescht(T)
    assert [z.ereignis.text for z in db.journal_lesen()] == [f"weg {T + 3600}"]
    assert db.messungen_schreiben([b]) == 0 and db.messungen_lesen() == [
        a
    ]  # nicht wieder eintragen
    assert db.kontext_nachtragen({T + 3600: {"quelle": "nachgetragen"}}) == 0
    assert db.messung_loeschen(T + 3600, T + 9000, text) is None  # schon weg
    assert (
        int(sqlite3.connect(db.pfad).execute("SELECT COUNT(*) FROM messung_kontext").fetchone()[0])
        == 1
    )


def test_an0007_loeschen_waehrend_einer_sicherung(db):
    db.messungen_schreiben([Messung(T, 1, 1, 1, "", None, None)])
    db.anhalten()
    with pytest.raises(sp.Angehalten):  # abgelehnt statt still in die Warteschlange
        db.messung_loeschen(T, T + 1, lambda t: Ereignis("messung_geloescht", "info", "x"))
    db.fortsetzen()
    assert len(db.messungen_lesen()) == 1 and db.anzahl()["journal"] == 0


def test_rueckweg_bleibt_schema_1(tmp_path):
    """Die Momentaufnahme liegt in einer eigenen Tabelle: Schema bleibt 1, eine ältere Fassung öffnet die Datei weiter
    und liest ihre Messungen wie gewohnt (SELECT * über die alte Tabelle)."""
    d = sp.Datenbank(tmp_path / "x.db")
    d.oeffnen()
    d.messungen_schreiben([Messung(T, 1, 2, 3, "Wien", None, None, {"quelle": "messung"})])
    d.schliessen()
    con = sqlite3.connect(tmp_path / "x.db")
    assert con.execute("PRAGMA user_version").fetchone()[0] == 1
    assert con.execute("SELECT * FROM messung").fetchall() == [
        (T, 1.0, 2.0, 3.0, "Wien", None, None)
    ]
    con.close()


def test_gedaechtnis_und_meta(db):
    assert db.gedaechtnis_laden() is None
    db.gedaechtnis_speichern({"version": 1, "befunde": {"a": "Ä"}})
    assert db.gedaechtnis_laden() == {"version": 1, "befunde": {"a": "Ä"}}


def test_sicherung_warteschlange(db):
    db.anhalten()
    assert db.journal_schreiben([sp.Journalzeile(T, Ereignis("start", "info", "x"))]) == 0
    assert db.aufraeumen(T) is None  # ausgelassen, nicht „nichts zu tun“
    assert db.anzahl()["journal"] == 0
    db.fortsetzen()
    assert db.anzahl()["journal"] == 1


def test_aufraeumen_behaelt_messungen(db):
    alt = T - sp.AUFBEWAHREN_S - 1
    db.journal_schreiben(
        [
            sp.Journalzeile(alt, Ereignis("a", "info", "x")),
            sp.Journalzeile(T, Ereignis("b", "info", "y")),
        ]
    )
    db.protokoll_schreiben([eintrag("alt", datetime.fromtimestamp(alt))])
    db.messungen_schreiben([Messung(alt, 1, 1, 1, "", None, None)])
    assert db.aufraeumen(T) == 2
    assert db.anzahl() == {"journal": 1, "protokoll": 0, "messung": 1}


def test_protokoll_ohne_zeit_wird_nach_eintragezeit_geloescht(db):
    db.protokoll_schreiben([eintrag("ohne Zeit", None)], jetzt=T - sp.AUFBEWAHREN_S - 1)
    db.protokoll_schreiben([eintrag("jung ohne Zeit", None)], jetzt=T)
    assert db.aufraeumen(T) == 1
    assert [z.text for z in db.protokoll_lesen(("internet",))] == ["jung ohne Zeit"]


def test_letzte_messung(db):
    assert db.letzte_messung() == 0.0
    db.messungen_schreiben([Messung(T, 1, 1, 1, "", None, None)])
    assert db.letzte_messung() == T


def test_geraete_zaehlen_und_erstes(db):
    db.journal_schreiben(
        [
            sp.Journalzeile(T, Ereignis("neu", "info", "x", "AA")),
            sp.Journalzeile(T + 1, Ereignis("offline", "info", "x", "AA")),
            sp.Journalzeile(T + 2, Ereignis("offline", "info", "x", "AA")),
            sp.Journalzeile(T - 100, Ereignis("offline", "info", "x", "BB")),
        ]
    )
    assert db.geraete_zaehlen(T) == {"AA": (2, True)}
    assert db.erstes("AA") == T and db.erstes("CC") is None


def test_salz_bleibt(db):
    assert db.salz() == db.salz() and len(db.salz()) == 32
