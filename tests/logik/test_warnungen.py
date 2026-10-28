"""Warnungen (WU-0010): Auswahl nach Art und Ausnahme, Zustand je Gerät mit Verzögerung, kein Flattern, kein Schwall
nach dem Neustart, Ausfall von Box/Internet mit Zustellung danach, neues Gerät höchstens einmal."""

from datetime import UTC

import pytest
from logik import warnungen as wn
from logik.sprache import Ungueltig

MIN = 60.0
T0 = 1_800_000_000.0  # fester Zeitpunkt (UTC)
ARTEN = (
    "netz",
    "smart",
    "haushalt",
    "computer",
    "drucker",
    "mobil",
    "medien",
    "kamera",
    "unbekannt",
    "eigen:1",
)


def einst(**kw):
    return wn.pruefen({"verzoegerung": 5, **kw}, ARTEN)


def b(name, aktiv, zufall=False, verbindung="WLAN 5 GHz", ip="192.168.170.9"):
    return wn.Beobachtung(name, name, ip, aktiv, verbindung if aktiv else "", zufall)


class Lauf:
    """Wächter mit Uhr: jeder Schritt eine Minute später, alle Geräte überwacht (außer `stumm`)."""

    def __init__(self, e=None, stumm=()):
        self.w, self.t, self.e, self.stumm = wn.Waechter(), T0, e or einst(), set(stumm)

    def __call__(self, *geraete, box=True, internet=True, schritt=MIN):
        self.t += schritt
        return self.w.schritt(self.t, box, internet, geraete, self.e, lambda k: k not in self.stumm)


def arten(erg):
    return [(m.art, m.name) for m in erg.neu]


# ── wer überwacht wird ──
def test_auswahl_nach_art_und_ausnahme():
    e = wn.Warneinstellungen()
    assert [k for k in ARTEN if e.art_an(k)] == ["netz", "smart", "haushalt", "kamera"]
    assert not e.art_an("mobil") and not e.art_an(
        "eigen:1"
    )  # Handy aus, eigene Art erst nach dem Einschalten
    e = einst(
        arten={"mobil": True, "netz": False, "weg": True},
        geraete={"a": "immer", "b": "nie", "c": "x"},
    )
    assert e.arten == {"mobil": True, "netz": False}, "unbekannte Art fällt still weg"
    assert e.geraete == {"a": "immer", "b": "nie"}
    assert e.ueberwacht("medien", "a") and not e.ueberwacht("kamera", "b")
    assert e.ueberwacht("mobil", "z") and not e.ueberwacht("netz", "z")
    assert e.ausnahme("a") == "immer" and e.ausnahme("z") == "gruppe"


def test_pruefen_ziel_und_verzoegerung():
    assert einst().ziel == wn.KEINE and einst().verzoegerung == 5
    assert einst(ziel="mobile_app_handy").ziel == "mobile_app_handy"
    with pytest.raises(Ungueltig):
        wn.pruefen({"ziel": "mobile_app_handy"}, ARTEN, dienste=["mobile_app_tablet"])
    with pytest.raises(Ungueltig):
        einst(ziel="notify; rm")
    with pytest.raises(Ungueltig):
        einst(verzoegerung=3)
    with pytest.raises(Ungueltig):
        einst(wieder="ja")
    assert einst(sprache="en-GB").sprache == "en"
    assert wn.pruefen(einst(ziel="alle").als_dict(), ARTEN) == einst(ziel="alle")


def test_ziel_dienste():
    da = ["mobile_app_a", "mobile_app_b", "persistent_notification"]
    assert wn.ziel_dienste(wn.KEINE, da) == []
    assert wn.ziel_dienste(wn.ALLE, da) == ["mobile_app_a", "mobile_app_b"]
    assert wn.ziel_dienste("persistent_notification", da) == ["persistent_notification"]
    assert wn.ziel_dienste("mobile_app_c", da) == []


# ── Zustand je Gerät ──
def test_offline_nach_verzoegerung_genau_einmal_und_wieder_online_mit_dauer():
    lauf = Lauf()
    assert lauf(b("Kamera", True)).neu == ()  # Grundzustand
    lauf(b("Kamera", True))
    for _ in range(5):  # weg gesehen seit 08:03, bis 4 min danach: noch nichts
        assert lauf(b("Kamera", False)).neu == ()
    erg = lauf(b("Kamera", False))  # 5 min
    assert arten(erg) == [("offline", "Kamera")]
    m = erg.neu[0]
    assert m.dauer_s == 5 * MIN and m.verbindung == "WLAN 5 GHz" and erg.senden == erg.neu
    assert m.text("de", UTC) == "Kamera ist seit 5 min offline (zuletzt 08:02, WLAN 5 GHz)"
    for _ in range(30):
        assert lauf(b("Kamera", False)).neu == (), "nur einmal gemeldet"
    erg = lauf(b("Kamera", True))
    assert arten(erg) == [("online", "Kamera")]
    assert erg.neu[0].text("de", UTC) == "Kamera ist wieder online – war 36 min weg (WLAN 5 GHz)"
    assert erg.neu[0].text("en", UTC) == "Kamera is back online – was gone for 36 min (WLAN 5 GHz)"


def test_kein_flattern_vor_ablauf():
    lauf = Lauf()
    lauf(b("Lampe", True))
    for _ in range(10):
        assert lauf(b("Lampe", False)).neu == ()
        assert lauf(b("Lampe", True)).neu == ()
    lauf2 = Lauf(einst(verzoegerung=2))
    lauf2(b("Lampe", True))
    meldungen = []
    for _ in range(3):
        for zustand in (False, False, False, True):
            meldungen += arten(lauf2(b("Lampe", zustand)))
    assert meldungen == [("offline", "Lampe"), ("online", "Lampe")] * 3, (
        "wieder online nur nach gemeldet"
    )


def test_wieder_online_aus_und_nicht_ueberwacht():
    lauf = Lauf(einst(wieder=False))
    lauf(b("NAS", True))
    lauf(b("NAS", False), schritt=0)
    assert arten(lauf(b("NAS", False), schritt=6 * MIN)) == [("offline", "NAS")]
    assert lauf(b("NAS", True)).neu == (), "Schalter „wieder online“ aus"
    still = Lauf(stumm={"Handy"})
    still(b("Handy", True))
    for _ in range(20):
        assert still(b("Handy", False)).neu == ()
    still.stumm.clear()  # jetzt überwacht: das schon fehlende Handy meldet sich nicht nachträglich
    for _ in range(20):
        assert still(b("Handy", False)).neu == ()
    still(b("Handy", True))
    still(b("Handy", False), schritt=0)
    assert arten(still(b("Handy", False), schritt=6 * MIN)) == [("offline", "Handy")]


def test_neustart_kein_schwall():
    lauf = Lauf()
    geraete = [b(f"G{i}", i % 2 == 0) for i in range(20)]
    assert lauf(*geraete).neu == ()  # erster Abruf nach dem Start: offline sind „aus“
    for _ in range(70):
        assert lauf(*geraete).neu == ()
    # erst die Box nicht erreichbar: kein Grundzustand, keine Meldung
    lauf = Lauf()
    for _ in range(10):
        assert lauf(box=False, internet=False).neu == ()
    assert not lauf.w.grundzustand
    assert lauf(*geraete).neu[0].art == "internet", "nur der Ausfall seit dem Start"
    assert lauf.w.grundzustand
    assert lauf(*geraete).neu == ()


def test_box_weg_keine_geraetemeldungen_dann_ausfall_mit_dauer():
    lauf = Lauf()
    lauf(b("Kamera", True), b("Lampe", True))
    for _ in range(30):
        erg = lauf(box=False, internet=False)
        assert erg.neu == () and erg.senden == ()
    assert lauf.w.geraete["Kamera"].stand == wn.ONLINE, "Zustand bleibt stehen"
    erg = lauf(b("Kamera", True), b("Lampe", True))
    assert arten(erg) == [("internet", "")]
    m = erg.neu[0]
    assert m.box and m.dauer_s == 30 * MIN and erg.senden == erg.neu
    assert m.text("de", UTC) == "FRITZ!Box war 30 min nicht erreichbar (08:02–08:32)"
    assert m.ereignis("de", UTC)["art"] == "internet" and m.ereignis("de", UTC)["dauer"] == 1800


def test_internet_weg_zustellung_erst_danach_kurzer_ausfall_still():
    lauf = Lauf()
    lauf(b("Kamera", True))
    assert lauf(b("Kamera", True), internet=False).neu == ()
    assert lauf(b("Kamera", True)).neu == (), "1 min weg: unter der Verzögerung"
    lauf(b("Kamera", True), internet=False)
    lauf(b("Kamera", False), internet=False)
    erg = lauf(b("Kamera", False), internet=False, schritt=6 * MIN)
    assert arten(erg) == [("offline", "Kamera")] and erg.senden == (), (
        "Ereignis sofort, Push wartet"
    )
    erg = lauf(b("Kamera", False))
    assert [m.art for m in erg.neu] == ["internet"]
    assert [m.art for m in erg.senden] == ["internet", "offline"], (
        "Ausfall zuerst, dann das Zurückgehaltene"
    )
    assert not erg.neu[0].box
    assert erg.neu[0].text("de", UTC) == "Internet war 8 min weg (08:04–08:12)"
    assert lauf(b("Kamera", False)).senden == ()
    aus = Lauf(einst(internet=False))
    aus(b("x", True), internet=False, schritt=0)
    assert aus(b("x", True), schritt=60 * MIN).neu == ()


def test_neues_geraet_hoechstens_einmal():
    lauf = Lauf()
    lauf(b("Pi", True))  # neue Installation: die Geräte von jetzt sind bekannt
    assert set(lauf.w.bekannt) == {"Pi"} and lauf.w.bekannt_geaendert
    erg = lauf(b("Pi", True), b("Fremd", True, ip="192.168.170.77"))
    assert arten(erg) == [("neu", "Fremd")]
    assert (
        erg.neu[0].text("de", UTC)
        == "Neues Gerät im Heimnetz: Fremd, IP 192.168.170.77, WLAN 5 GHz"
    )
    assert lauf(b("Pi", True), b("Fremd", True)).neu == ()
    lauf(b("Pi", True))  # Box vergisst Fremd …
    lauf(b("Pi", True))
    lauf(b("Pi", True))
    assert "Fremd" not in lauf.w.geraete and "Fremd" in lauf.w.bekannt
    assert lauf(b("Pi", True), b("Fremd", True)).neu == (), "… und kennt es wieder: nicht neu"
    assert Lauf(einst(neu=False))(b("Fremd", True)).neu == ()


def test_neu_nach_neustart_aus_gemerkten_und_zufallsadresse():
    lauf = Lauf()
    lauf.w.bekannt = dict.fromkeys(["Pi", "Drucker"])  # gemerkt bzw. aus dem Journal
    erg = lauf(b("Pi", True), b("Drucker", False), b("Gast", True, zufall=True))
    assert arten(erg) == [("neu", "Gast")], "Grundzustand: nur das wirklich Neue"
    assert (
        erg.neu[0]
        .text("de", UTC)
        .endswith("– zufällige Adresse – vermutlich ein bekanntes Handy/Tablet")
    )
    assert "random address" in erg.neu[0].text("en", UTC)


def test_leere_oder_geschrumpfte_tabelle_gilt_als_luecke():
    lauf = Lauf(einst(verzoegerung=2))
    alle = [b(f"G{i}", True) for i in range(10)]
    lauf(*alle)
    lauf(*alle)
    for _ in range(10):
        assert lauf().neu == ()  # Box erreichbar, Tabelle leer
        assert lauf(*alle[:3]).neu == ()  # stark geschrumpft
    assert len(lauf.w.geraete) == 10, "Zustände bleiben"
    assert lauf(*alle).neu == (), "keine Welle „neu“ oder „offline“"
    teil = alle[:6]  # 60 %: brauchbar, die fehlenden vergisst er erst nach drei vollen Abrufen
    lauf(*teil)
    lauf(*teil)
    assert len(lauf.w.geraete) == 10
    lauf(*teil)
    assert len(lauf.w.geraete) == 6


def test_schonfrist_nach_box_ausfall():
    lauf = Lauf(einst(verzoegerung=2, internet=False))
    lauf(b("Kamera", True), b("Lampe", True))
    for _ in range(5):
        lauf(box=False, internet=False)
    # Box neu gestartet: Geräte melden sich nach und nach zurück – keine Welle offline/online
    assert lauf(b("Kamera", False), b("Lampe", False)).neu == ()
    assert lauf(b("Kamera", False), b("Lampe", True)).neu == ()
    assert lauf(b("Kamera", True), b("Lampe", True)).neu == ()
    # bleibt ein Gerät weg, wird es nach der Frist gemeldet
    lauf(b("Kamera", True), b("Lampe", False))
    lauf(b("Kamera", True), b("Lampe", False))
    assert arten(lauf(b("Kamera", True), b("Lampe", False))) == [("offline", "Lampe")]


def test_kuerzen_verwirft_paare():
    m = lambda art, k, t=0: wn.Meldung(art, T0 + t, k, k)  # noqa: E731
    liste = [m("offline", "A"), m("offline", "B", 1), m("online", "A", 2), m("online", "B", 3)]
    assert [(x.art, x.schluessel) for x in wn.kuerzen(liste, 3)] == [
        ("offline", "B"),
        ("online", "B"),
    ]
    assert wn.kuerzen(liste, 4) == liste
    lauf = Lauf(einst(verzoegerung=2))
    geraete = [f"G{i}" for i in range(15)]
    lauf(*[b(k, True) for k in geraete])
    lauf(*[b(k, False) for k in geraete], internet=False)
    lauf(*[b(k, False) for k in geraete], internet=False, schritt=3 * MIN)  # 15 offline
    lauf(*[b(k, True) for k in geraete], internet=False)  # 15 online → 30 > 20
    zurueck = lauf.w.zurueck
    assert len(zurueck) <= wn.ZURUECK_HOECHSTENS
    for x in zurueck:
        if x.art == "online":
            assert any(y.art == "offline" and y.schluessel == x.schluessel for y in zurueck)


def test_dauer_und_ereignis_ohne_adresse():
    assert wn.dauer_text(30) == "1 min"
    assert wn.dauer_text(125 * MIN) == "2 h 5 min"
    assert wn.dauer_text(120 * MIN) == "2 h"
    assert wn.dauer_text(26 * 60 * MIN, "en") == "1 day 2 h"
    assert wn.dauer_text(72 * 60 * MIN) == "3 Tage"
    m = wn.Meldung(
        "offline", T0, "00:11:22:33:44:55", "Gerät 00:11:22:33:44:55", "1.2.3.4", "LAN", 300, T0
    )
    d = m.ereignis("de", UTC)
    assert "00:11:22" not in str(d) and d["geraet"].startswith("Gerät") and d["dauer"] == 300
    assert wn.test(T0).text("en", UTC).startswith("Test message")
