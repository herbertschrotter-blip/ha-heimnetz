"""Karte zum Mast: Kennung für OpenCellID, Antwort, Merken, Kartenausschnitt."""

from daten import ZELLEN
from logik import karte as ka
from logik import mobil as mb

WOHNUNG = ka.Ort(48.2, 16.37)  # Beispielort, nicht der echte
MAST = ka.Ort(48.208, 16.381)


def test_kennung_aus_der_ankerzelle():
    m = mb.aus_antwort({"NewCellList": ZELLEN})
    k = ka.kennung(m.haupt)
    assert k == ka.Kennung(232, 5, 0xC0FC, 0xABCDE * 256 + 0x0B)
    assert k.schluessel == f"232-5-{0xC0FC}-{0xABCDE * 256 + 0x0B}"
    assert ka.kennung(m.nr) is None  # 5G-Zelle: keine LTE-Kennung
    assert ka.kennung(None) is None
    z = m.haupt
    for kaputt in ({"tac": ""}, {"tac": "xyz"}, {"plmn": "23"}, {"zelle": ""}, {"zelle": "abc"}):
        assert ka.kennung(mb.Zelle(**{**z.__dict__, **kaputt})) is None


def test_antwort_von_opencellid():
    m = ka.mast_aus({"lat": 48.208, "lon": 16.381, "range": 350, "mcc": 232})
    assert m == ka.Mast(ka.Ort(48.208, 16.381), 350)
    assert ka.mast_aus({"lat": "48.2", "lon": "16.3"}).genau_m is None
    assert ka.mast_aus({"error": "Cell not found", "code": 1}) is None
    assert ka.mast_aus({"lat": 0, "lon": 0}) is None
    assert ka.mast_aus({"lat": 99, "lon": 0}) is None
    assert ka.mast_aus({"lat": "x", "lon": 1}) is None
    assert ka.mast_aus({}) is None


def test_merken():
    assert ka.faellig(None, 1000, "a")
    gefunden = {"lat": 1.0, "lon": 2.0, "t": 1000, "schluessel": "a"}
    # gefunden bleibt auch mit neuem Schlüssel
    assert not ka.faellig(gefunden, 1000 + ka.GUELTIG_S - 1, "b")
    assert ka.faellig(gefunden, 1000 + ka.GUELTIG_S, "a")
    fehlt = {"stand": "nicht_gefunden", "t": 1000, "schluessel": "a"}
    assert not ka.faellig(fehlt, 1000 + ka.NOCHMAL_S - 1, "a")
    assert ka.faellig(fehlt, 1000 + ka.NOCHMAL_S, "a")
    assert ka.faellig(fehlt, 1001, "b")  # neuer Schlüssel: gleich noch einmal


def test_entfernung_und_richtung():
    assert ka.strecke(ka.entfernung_m(WOHNUNG, MAST)) == "1,2 km"
    assert ka.richtung(WOHNUNG, MAST) == "Nordost"
    assert ka.richtung(WOHNUNG, ka.Ort(48.19, 16.37)) == "Süd"
    assert ka.richtung(WOHNUNG, ka.Ort(48.2, 16.36)) == "West"
    assert [ka.strecke(v) for v in (849.6, 1000, 12_345)] == ["850 m", "1,0 km", "12,3 km"]


def test_rahmen():
    assert ka.rahmen(WOHNUNG, None) is None
    s, w, n, o = ka.rahmen(WOHNUNG, 1200, [MAST])
    assert s < WOHNUNG.lat < n and w < WOHNUNG.lon < o
    assert s < MAST.lat < n and w < MAST.lon < o  # Mast im Bild
    hoehe = ka.entfernung_m(ka.Ort(s, WOHNUNG.lon), ka.Ort(n, WOHNUNG.lon))
    breite = ka.entfernung_m(ka.Ort(WOHNUNG.lat, w), ka.Ort(WOHNUNG.lat, o))
    assert (
        abs(hoehe - breite) < 1 and 2 * 1250 < hoehe < 2 * 1700
    )  # 1,2–1,4 km plus Rand, quadratisch
    nur_ring = ka.rahmen(WOHNUNG, 1200)
    assert nur_ring[2] - nur_ring[0] < n - s
    weit = ka.rahmen(
        WOHNUNG, 1200, [ka.Ort(48.3, 16.5)]
    )  # Mast der Hauptzelle weit weg: zählt trotzdem
    assert weit[2] > 48.3 and weit[3] > 16.5
    nah = ka.rahmen(
        WOHNUNG, 1200, [MAST], [ka.Mast(MAST, 500), ka.Mast(ka.Ort(48.22, 16.40), None)]
    )
    assert nah[2] > 48.22 and nah[3] > 16.40  # Zelle in 3 km: im Bild


def test_fehler_und_aufraeumen():
    assert ka.stand_aus({"error": "Cell not found", "code": 1}) == "nicht_gefunden"
    assert ka.stand_aus({"error": "Invalid token", "code": 2}) == "schluessel_ungueltig"
    assert ka.stand_aus({"error": "limit", "code": 7}) == ka.stand_aus({}) == "fehler"
    weg = {"stand": "fehler", "t": 1000, "schluessel": "a"}
    assert not ka.faellig(weg, 1000 + ka.FEHLER_S - 1, "a") and ka.faellig(
        weg, 1000 + ka.FEHLER_S, "a"
    )
    assert ka.mast_aus({"lat": 1, "lon": 2, "range": "inf"}).genau_m is None
    merk = {"alt": {"t": 0}, "neu": {"t": ka.GUELTIG_S}}
    assert list(ka.aufraeumen(merk, ka.GUELTIG_S + 1)) == ["neu"]


def test_alle_zellen_einer_sendeanlage():
    haupt = mb.Zelle("primary", "LTE", "3 AT", 211, "aaaaa-64", -105, -11, plmn="23205", tac="1A2B")
    dazu = mb.Zelle("secondary", "LTE", "3 AT", 214, "AAAAA-00", -113, -13)  # ohne PLMN/TAC
    fremd = mb.Zelle("", "LTE", "3 AT", 101, "bbbbb-01", -110, -12)  # andere Sendeanlage, ohne TAC
    nur_pci = mb.Zelle("secondary", "LTE", "3 AT", 443, "", -101, -15)
    assert ka.sendeanlage(haupt) == ka.sendeanlage(dazu) == "aaaaa"
    assert (
        ka.sendeanlage(nur_pci) is None
        and ka.sendeanlage(mb.Zelle("", "5G", "", 1, "ab-01", None, None)) is None
    )
    assert ka.kennung(dazu, haupt) == ka.Kennung(
        232, 5, 0x1A2B, 0xAAAAA * 256
    )  # PLMN/TAC der Hauptzelle
    assert ka.kennung(dazu) is None  # ohne Hauptzelle fehlen sie
    assert ka.kennung(fremd, haupt) is None  # TAC einer anderen Sendeanlage wird nicht geraten
    assert ka.kennteile(dazu, haupt) == ("23205", "1A2B") and ka.kennteile(fremd, haupt) == ("", "")
    assert ka.kennung(nur_pci, haupt) is None
    assert ka.plmn_text("23205") == "232 05" and ka.plmn_text("310410") == "310 410"
    assert ka.plmn_text("") is None and ka.plmn_text("2320x") is None


def test_antwort_von_beacondb():
    assert ka.beacondb_aus({"location": {"lat": 48.21, "lng": 16.38}, "accuracy": 50}) == ka.Mast(
        ka.Ort(48.21, 16.38), 50
    )
    assert ka.beacondb_aus({"error": {"code": 404, "message": "Not found"}}) is None
    assert ka.beacondb_aus({"location": "x"}) is None
    assert ka.beacondb_aus({"location": {"lat": 0, "lng": 0}, "accuracy": 1}) is None
    assert ka.beacondb_aus({}) is None


def test_mast_schaetzen():
    assert ka.schaetzen([]) is None
    genau = ka.Mast(ka.Ort(48.0, 16.0), 50)
    grob = ka.Mast(ka.Ort(48.1, 16.1), 1300)
    m = ka.schaetzen([genau, grob])
    assert m.genau_m == 50  # nicht genauer als der beste Einzelwert
    assert (
        ka.entfernung_m(m.ort, genau.ort) < 50
    )  # die genaue Zelle zieht den Mast fast ganz zu sich
    gleich = ka.schaetzen([ka.Mast(ka.Ort(48.0, 16.0), None), ka.Mast(ka.Ort(48.2, 16.2), None)])
    assert (
        gleich.genau_m is None
        and abs(gleich.ort.lat - 48.1) < 1e-9
        and abs(gleich.ort.lon - 16.1) < 1e-9
    )


def test_fund_aus_beiden_diensten():
    weg, nicht = {"stand": "fehler"}, {"stand": "nicht_gefunden"}
    o = {"lat": 48.0, "lon": 16.0, "genau": 2000}
    b = {"lat": 48.1, "lon": 16.1, "genau": 80}
    assert ka.fund(o, b, True) == ka.Fund("gefunden", ka.Mast(ka.Ort(48.1, 16.1), 80), "BeaconDB")
    assert (
        ka.fund(o, {**b, "genau": None}, True).quelle == "OpenCellID"
    )  # ohne Angabe gilt sie als ungenauer
    assert ka.fund(None, nicht, False).stand == "ohne_schluessel"
    assert ka.fund(nicht, nicht, True).stand == "nicht_gefunden"
    assert (
        ka.fund(nicht, weg, True).stand == "fehler"
    )  # einer antwortete nicht: „unbekannt“ ist nicht sicher
    assert ka.fund(None, weg, False).stand == "fehler"
    ungueltig = ka.fund({"stand": "schluessel_ungueltig"}, b, True)
    assert ungueltig.stand == "gefunden" and ungueltig.schluessel_ungueltig
    assert ka.fund({"stand": "schluessel_ungueltig"}, nicht, True).stand == "schluessel_ungueltig"


def test_gesamtstand_und_text():
    gef = ka.Fund("gefunden", ka.Mast(ka.Ort(48.0, 16.0), 50), "BeaconDB")
    weg, ohne = ka.Fund("fehler"), ka.Fund("ohne_schluessel")
    assert ka.gesamtstand([]) == "ohne_kennung"
    assert ka.gesamtstand([weg, gef]) == "gefunden"
    assert (
        ka.gesamtstand([ohne, weg, weg]) == "fehler"
    )  # Ausfall nicht hinter „kennt sie nicht“ verstecken
    assert ka.gesamtstand([ohne, ka.Fund("nicht_gefunden")]) == "ohne_schluessel"
    assert ka.gesamtstand([ka.Fund("nicht_gefunden")]) == "nicht_gefunden"
    assert (
        ka.gesamtstand([gef, ka.Fund("gefunden", gef.mast, "BeaconDB", True)])
        == "schluessel_ungueltig"
    )
    lte = mb.Zelle("primary", "LTE", "", 1, "ab-01", None, None)
    assert ka.such_text(lte, gef) is None
    assert ka.such_text(lte, weg) == "Dienste nicht erreichbar – später neu"
    assert ka.such_text(lte, ohne) == "nicht gefunden"
    assert ka.such_text(lte, None) == "Kennung unvollständig"
    assert (
        ka.such_text(mb.Zelle("", "LTE", "", 1, "", None, None), None)
        == "nur PCI – nicht nachschlagbar"
    )
    assert (
        ka.such_text(mb.Zelle("", "5G", "", 1, "", None, None), None)
        == "nur PCI – nicht nachschlagbar"
    )
    assert (
        ka.such_text(mb.Zelle("", "5G", "", 1, "abc12-01", None, None), None)
        == "5G – nicht nachschlagbar"
    )


def test_masten_je_sendeanlage():
    haupt = mb.Zelle("primary", "LTE", "", 1, "aa-01", None, None)
    dazu = mb.Zelle("secondary", "LTE", "", 2, "aa-02", None, None)
    fremd = mb.Zelle("", "LTE", "", 3, "bb-01", None, None)
    m1, m2, m3 = (ka.Mast(ka.Ort(48.0 + i / 100, 16.0), 100) for i in range(3))
    masten = ka.masten_je_anlage([(fremd, m3), (dazu, m2), (haupt, m1)])
    assert [enb for enb, _ in masten] == ["aa", "bb"]  # Sendeanlage der Hauptzelle zuerst
    assert abs(masten[0][1].ort.lat - 48.005) < 1e-9 and masten[1][1] == m3


def test_ferne_zelle_zoomt_nicht_heraus():
    nah = ka.rahmen(WOHNUNG, 1200, [MAST])
    fern = ka.rahmen(WOHNUNG, 1200, [MAST], [ka.Mast(ka.Ort(48.47, 16.37), 10_000)])  # 30 km
    assert fern == nah
    assert (
        ka.rahmen(WOHNUNG, 1200, [MAST, ka.Ort(48.47, 16.37)]) == nah
    )  # ferner zweiter Mast zählt nicht
    allein = ka.rahmen(
        WOHNUNG, None, [], [ka.Mast(ka.Ort(48.27, 16.37), 900)]
    )  # nur eine ferne Zelle
    assert allein is not None and allein[2] > 48.27


def test_fuenf_g_dabei():
    nr = mb.Zelle("secondary", "5G", "", 121, "", -97, -10)
    lte = mb.Zelle("primary", "LTE", "", 211, "aaaaa-0a", -100, -15)
    assert ka.fuenf_g_dabei([lte, nr])
    assert not ka.fuenf_g_dabei(
        [lte, mb.Zelle("", "5G", "", 982, "", -101, -11)]
    )  # nur in Reichweite
    assert not ka.fuenf_g_dabei([lte])


def test_gemerkte_zellen_je_sendeanlage():
    # Merkspeicher der Mastsuche: Zellen aaaaa-00 (OpenCellID und BeaconDB) und aaaaa-64 (BeaconDB) gefunden
    enb = 0xAAAAA
    merk = {
        f"232-5-6699-{enb * 256}": {"lat": 48.21, "lon": 16.38, "genau": 900},
        f"beacondb:232-5-6699-{enb * 256}": {"lat": 48.211, "lon": 16.381, "genau": 50},
        f"beacondb:232-5-6699-{enb * 256 + 0x64}": {"lat": 48.22, "lon": 16.39, "genau": 1300},
        "beacondb:232-5-6699-99": {"stand": "nicht_gefunden", "t": 0},
        "unsinn": {"lat": 1, "lon": 2},
    }
    g = ka.gemerkte_anlagen(merk)
    assert set(g) == {(5, "aaaaa")}
    assert sorted(m.genau_m for m in g[(5, "aaaaa")]) == [50, 1300]  # je Zelle der genauere Fund
    # Box hängt an einem unbekannten Sektor (8c): der Mast kommt aus den gemerkten Zellen
    haupt = mb.Zelle("primary", "LTE", "3 AT", 1, "aaaaa-8c", -100, -12, plmn="23205", tac="1A2B")
    ((name, mast),) = ka.masten_je_anlage([], g, haupt, [haupt])
    assert name == "aaaaa" and mast.genau_m == 50
    assert ka.masten_je_anlage([], {}, haupt, [haupt]) == []
    anderes_netz = mb.Zelle("primary", "LTE", "", 1, "aaaaa-8c", -100, -12, plmn="23201", tac="1")
    assert ka.masten_je_anlage([], g, anderes_netz, [anderes_netz]) == []
