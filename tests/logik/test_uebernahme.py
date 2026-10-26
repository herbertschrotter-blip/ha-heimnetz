"""Umstieg von „netzwerk“ auf „heimnetz“ (WU-0006): nur in Leeres übernehmen, alte nie parallel."""

from logik import uebernahme as ue


def test_alte_aktiv_solange_eine_nicht_deaktiviert_ist():
    assert not ue.alte_aktiv([])
    assert not ue.alte_aktiv([True])
    assert ue.alte_aktiv([False])
    assert ue.alte_aktiv([True, False])


def test_speicher_schluessel_je_einrichtung():
    assert ue.speicher_schluessel("netzwerk", "alt", "heimnetz", "neu") == [
        ("netzwerk.alt", "heimnetz.neu"),
        ("netzwerk.alt.mast", "heimnetz.neu.mast"),
        ("netzwerk.alt.osm", "heimnetz.neu.osm"),
        ("netzwerk.alt.ocid", "heimnetz.neu.ocid"),
    ]


def test_speicher_nur_in_leeres():
    alt = {"tarif_gb": 100, "messplan": {"an": True}}
    assert ue.speicher_uebernehmen(None, alt) == alt
    assert ue.speicher_uebernehmen({}, alt) == alt
    assert ue.speicher_uebernehmen({"tarif_gb": 50}, alt) is None  # Vorhandenes nie überschreiben
    assert ue.speicher_uebernehmen(None, None) is None
    assert ue.speicher_uebernehmen(None, {}) is None


def test_meldungen_mit_nummern_fortfuehren():
    alt = {"meldungen": [{"ticket": "FE-0006"}], "nummern": {"FE": "6", "WU": 5}}
    assert ue.meldungen_uebernehmen(None, alt) == {
        "meldungen": [{"ticket": "FE-0006"}],
        "nummern": {"FE": 6, "WU": 5},
    }
    # nur Nummern (alle Tickets gelöscht): trotzdem übernehmen, sonst gäbe es FE-0001 doppelt
    assert ue.meldungen_uebernehmen({"meldungen": [], "nummern": {}}, {"nummern": {"FE": 2}}) == {
        "meldungen": [],
        "nummern": {"FE": 2},
    }
    assert ue.meldungen_uebernehmen({"meldungen": [], "nummern": {"AN": 1}}, alt) is None
    assert ue.meldungen_uebernehmen({"meldungen": [{"ticket": "AN-0001"}]}, alt) is None
    assert ue.meldungen_uebernehmen(None, {"meldungen": [], "nummern": {}}) is None
    assert ue.meldungen_uebernehmen(None, None) is None


def test_dateien_ohne_datenbank_und_nur_was_fehlt():
    alt = [
        "netzwerk.db",
        "netzwerk.db-wal",
        "netzwerk.db-shm",
        "netzwerk.db-journal",
        "meldungen.json",
        "meldungen.md",
        "meldungen/FE-0001-1.jpg",
        "meldungen/AN-0002-1.png",
        "sonst.txt",
    ]
    neu = ["meldungen.json", "meldungen/AN-0002-1.png"]
    # meldungen.md fehlt zwar, schreibt Heimnetz aber selbst (siehe test_lesbare_ablage_der_tickets_kommt_nicht_mit)
    assert ue.dateien_planen(alt, neu) == [
        ("meldungen/FE-0001-1.jpg", "meldungen/FE-0001-1.jpg"),
        ("sonst.txt", "sonst.txt"),
    ]
    assert ue.dateien_planen([], []) == []
    # eine Datei, die nur ähnlich heißt, ist keine Begleitdatei
    assert ue.dateien_planen(["netzwerk.db.alt"], []) == [("netzwerk.db.alt", "netzwerk.db.alt")]


def test_datenbank_nur_wenn_heimnetz_keine_hat():
    assert ue.datenbank_planen(True, False)
    assert not ue.datenbank_planen(True, True)
    assert not ue.datenbank_planen(False, False)


def test_optionen_nur_bekannte_mit_wert():
    assert ue.optionen_uebernehmen(
        {"opencellid_schluessel": "x", "fremd": 1}, ["opencellid_schluessel"]
    ) == {"opencellid_schluessel": "x"}
    assert ue.optionen_uebernehmen({"opencellid_schluessel": ""}, ["opencellid_schluessel"]) == {}
    assert ue.optionen_uebernehmen(None, ["opencellid_schluessel"]) == {}


def test_lesbare_ablage_der_tickets_kommt_nicht_mit():
    # Heimnetz schreibt meldungen.json/.md aus dem übernommenen Speicher selbst; nur die Bilder kommen mit
    alt = ["meldungen.json", "meldungen.md", "meldungen/FE-0006-1.jpg", "meldungen/meldungen.json"]
    assert ue.dateien_planen(alt, []) == [
        ("meldungen/FE-0006-1.jpg", "meldungen/FE-0006-1.jpg"),
        ("meldungen/meldungen.json", "meldungen/meldungen.json"),
    ]


def test_datenbank_kaputt_nur_bei_unlesbarer_datei():
    assert ue.datenbank_kaputt("SQLITE_NOTADB")
    assert ue.datenbank_kaputt("SQLITE_CORRUPT")
    assert ue.datenbank_kaputt("SQLITE_CORRUPT_INDEX")
    # vorübergehend: später noch einmal
    for name in (
        "SQLITE_FULL",
        "SQLITE_IOERR",
        "SQLITE_IOERR_WRITE",
        "SQLITE_CANTOPEN",
        "SQLITE_BUSY",
    ):
        assert not ue.datenbank_kaputt(name)
    assert not ue.datenbank_kaputt(None)
    assert not ue.datenbank_kaputt("")
    assert not ue.datenbank_kaputt("SQLITE_CORRUPTX")
