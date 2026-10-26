"""WU-0006: Diagnose darf öffentlich sein – vertrauliche Schlüssel und Texte werden geschwärzt."""

from logik import diagnose as dg


def test_vertrauliche_schluessel_tief_geschwaerzt():
    roh = {
        "eintrag": {"fritz_eintrag": "01ABC", "Host": "192.0.2.1", "passwort": "geheim"},
        "optionen": {"opencellid_schluessel": "pk.123", "leer": ""},
        "zellen": ["abcde-0b"],
        "anker": {"zelle": "abcde-0b", "TAC": "C0FC", "pci": 443},
        "mast": {"lat": 47.07, "lon": 15.43, "anzahl": 3},
        "geraete": [{"name": "fernseher", "mac": "00:11:22:33:44:02", "online": True}],
        "ohne": {"tac": None, "name": ""},
    }
    d = dg.schwaerzen(roh)
    assert d["eintrag"] == {
        "fritz_eintrag": "01ABC",
        "Host": dg.GESCHWAERZT,
        "passwort": dg.GESCHWAERZT,
    }
    assert d["optionen"] == {"opencellid_schluessel": dg.GESCHWAERZT, "leer": ""}
    assert d["zellen"] == dg.GESCHWAERZT  # ganze Liste
    assert d["anker"] == {"zelle": dg.GESCHWAERZT, "TAC": dg.GESCHWAERZT, "pci": dg.GESCHWAERZT}
    assert d["mast"] == {"lat": dg.GESCHWAERZT, "lon": dg.GESCHWAERZT, "anzahl": 3}
    assert d["geraete"] == [{"name": dg.GESCHWAERZT, "mac": dg.GESCHWAERZT, "online": True}]
    assert d["ohne"] == {"tac": None, "name": ""}  # leer bleibt leer: man sieht, dass nichts da war
    assert roh["eintrag"]["passwort"] == "geheim"  # Kopie, das Original bleibt


def test_texte_ohne_adressen_orte_kennwoerter_und_namen():
    d = dg.schwaerzen(
        {
            "fehler": [
                "Box: keine Antwort von 192.0.2.1 (00:11:22:33:44:02)",
                "Mast bei 47.0707, 15.4395, Kennwort: hunter2",
                "Wohnzimmer TV antwortet nicht",
            ],
            "zahlen": (1, 2.5, False),
            "messplan": {"von": "06:00", "bis": "24:00"},
            "firmware": "268.08.03",
        },
        namen=["Wohnzimmer TV"],
    )
    assert d["fehler"] == [
        "Box: keine Antwort von [entfernt] ([entfernt])",
        "Mast bei [entfernt], Kennwort: [entfernt]",
        "[entfernt] antwortet nicht",
    ]
    assert d["zahlen"] == [1, 2.5, False]
    assert d["messplan"] == {"von": "06:00", "bis": "24:00"} and d["firmware"] == "268.08.03"
