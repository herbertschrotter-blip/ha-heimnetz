"""Funkmasten aus OpenStreetMap: Ausschnitt, Abfrage, Antwort, passender Mast."""

from logik import karte as ka
from logik import osm as lo

WOHNUNG = ka.Ort(48.2, 16.37)  # Beispielort, nicht der echte


def test_rahmen_auf_festem_raster():
    # Block 48,2–48,4 / 16,2–16,4 plus 0,1° Rand: mehr als den Block verrät die Abfrage nicht
    s, w, n, o = lo.rahmen(WOHNUNG)
    assert (s, w, n, o) == (48.1, 16.1, 48.5, 16.5)
    assert lo.rahmen(ka.Ort(48.3999, 16.3001)) == (
        48.1,
        16.1,
        48.5,
        16.5,
    )  # gleicher Block: gleicher Ausschnitt
    assert s < WOHNUNG.lat < n and w < WOHNUNG.lon < o
    q = lo.abfrage((s, w, n, o))
    assert "(48.1,16.1,48.5,16.5)" in q and '"tower:type"="communication"' in q
    assert "48.2," not in q and "16.37" not in q  # die Wohnung selbst steht nicht drin


def test_masten_aus_overpass():
    antwort = {
        "elements": [
            {
                "type": "node",
                "lat": 48.19,
                "lon": 16.37,
                "tags": {"man_made": "mast", "operator": "Drei"},
            },
            {"type": "way", "center": {"lat": 48.21, "lon": 16.38}, "tags": {}},
            {"type": "node", "tags": {}},  # ohne Ort
            "Unsinn",
        ]
    }
    assert lo.masten_aus(antwort) == [
        lo.OsmMast(ka.Ort(48.19, 16.37), "Drei"),
        lo.OsmMast(ka.Ort(48.21, 16.38), None),
    ]
    assert lo.masten_aus({}) == [] and lo.masten_aus({"elements": "x"}) == []


def test_passender_mast():
    # wie bei Herbert: Kandidaten 1,3 km Süd, 1,4 km Nord, 1,5 km Süd-Südwest, 4,4 km Süd
    sued = lo.OsmMast(ka.Ort(48.2 - 0.0117, 16.37))
    nord = lo.OsmMast(ka.Ort(48.2 + 0.0126, 16.37))
    ssw = lo.OsmMast(ka.Ort(48.2 - 0.0125, 16.37 - 0.009))
    weit = lo.OsmMast(ka.Ort(48.2 - 0.04, 16.37))
    masten = [nord, ssw, sued, weit]
    # geschätzter Mast bekannt: der nächste OSM-Mast bis 1,5 km – die Box-Entfernung zählt nicht (4,3 km statt 1,2)
    ziel = ka.Ort(48.2 - 0.008, 16.37 + 0.012)  # knapp 1 km südöstlich
    assert lo.passend(WOHNUNG, masten, 4300, ziel) == (2, lo.LAGE)
    assert lo.passend(WOHNUNG, [weit], 1200, ziel) is None  # weiter als 1,5 km vom geschätzten Mast
    # ohne geschätzten Mast: Entfernung laut Box
    assert lo.passend(WOHNUNG, masten, 1200) == (2, lo.ENTFERNUNG)
    assert lo.passend(WOHNUNG, masten, 4400) == (3, lo.ENTFERNUNG)
    assert lo.passend(WOHNUNG, [nord], 3000) is None  # Entfernung passt nicht
    assert lo.passend(WOHNUNG, masten, None) is None and lo.passend(WOHNUNG, [], 1200) is None


def test_faellig():
    k = "48.1,16.1,48.5,16.5"
    assert lo.faellig(None, k, 0)
    assert lo.faellig({"rahmen": "anders", "t": 0}, k, 1)
    assert not lo.faellig({"rahmen": k, "t": 1000}, k, 1000 + lo.GUELTIG_S - 1)
    assert lo.faellig({"rahmen": k, "t": 1000}, k, 1000 + lo.GUELTIG_S)
    fehler = {"rahmen": k, "t": 0, "fehler_t": 1000}
    assert not lo.faellig(fehler, k, 1000 + lo.NOCHMAL_S - 1) and lo.faellig(
        fehler, k, 1000 + lo.NOCHMAL_S
    )


def test_in_der_naehe_und_fehlerantwort():
    nah = lo.OsmMast(ka.Ort(48.21, 16.37))
    fern = lo.OsmMast(ka.Ort(48.4, 16.37))  # 22 km
    assert lo.in_der_naehe(WOHNUNG, [fern, nah]) == [nah]
    viele = [lo.OsmMast(ka.Ort(48.2 + i / 10_000, 16.37)) for i in range(150)]
    assert len(lo.in_der_naehe(WOHNUNG, viele)) == lo.HOECHSTENS
    assert lo.fehlerantwort({"remark": 'runtime error: Query timed out in "query"', "elements": []})
    assert not lo.fehlerantwort({"elements": []}) and not lo.fehlerantwort({"remark": "Hinweis"})
