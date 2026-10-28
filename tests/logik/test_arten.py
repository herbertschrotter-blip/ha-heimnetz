"""Art eines Geräts (AN-0001): Reihenfolge der Quellen, Hersteller, Mesh, Name, Gruppen."""

import pytest
from daten import MESH
from logik import arten as ar
from logik.sprache import Ungueltig

TABELLE = {"00040E": "AVM", "C8C9A3": "Espressif", "B827EB": "Raspberry Pi", "F0D5BF": "Apple"}


def test_reihenfolge_selbst_ha_mesh_hersteller_name():
    mac = "C8:C9:A3:00:00:01"
    assert ar.bestimmen(
        "x", mac, selbst="medien", ha=("Shelly", "Shelly Plug S Gen3"), tabelle=TABELLE
    ) == ar.Art("medien", "selbst gewählt")
    assert ar.bestimmen("x", mac, ha=("Shelly", "Shelly Plug S Gen3"), tabelle=TABELLE) == ar.Art(
        "smart", "Home Assistant: Shelly Shelly Plug S Gen3"
    )
    assert ar.bestimmen("x", mac, mesh="FRITZ!Repeater 3000", tabelle=TABELLE).kat == "netz"
    assert ar.bestimmen("x", mac, tabelle=TABELLE) == ar.Art("smart", "Hersteller (Espressif)")
    assert ar.bestimmen("Galaxy-S24", "F0:D5:BF:00:00:01", tabelle=TABELLE) == ar.Art(
        "mobil", "Name"
    )
    assert ar.bestimmen("x", "F0:D5:BF:00:00:01", tabelle=TABELLE) == ar.Art(
        "unbekannt", "Hersteller (Apple)"
    )
    assert ar.bestimmen("x", "12:34:56:00:00:01", tabelle=TABELLE) == ar.Art(
        "unbekannt", "nicht erkannt"
    )
    assert ar.bestimmen("x", mac, selbst="quatsch", tabelle=TABELLE).quelle != "selbst gewählt"


def test_ha_hersteller_und_modell():
    assert ar.aus_ha("Mammotion", "LUBA 3 AWD 1500") == "haushalt"
    assert ar.aus_ha("Dreametech™", "dreame.vacuum.r6001a") == "haushalt"
    assert ar.aus_ha("NETGEAR", "S8000") == "netz"
    assert ar.aus_ha("FRITZ!", "FRITZ!Box 6860 5G") == "netz"
    assert ar.aus_ha("Samsung", "") is None  # Hersteller allein sagt nichts
    assert (
        ar.aus_ha("TP-Link", "") is None and ar.aus_ha("LG", "") is None
    )  # zu verschiedene Geräte
    assert (
        ar.aus_ha("Shelly", "Shelly Plus Switch") == "smart"
    )  # „switch“ macht es nicht zu Netzwerk
    assert ar.bestimmen("Nintendo-Switch", "12:00:00:00:00:01", tabelle=TABELLE).kat == "medien"
    assert ar.bestimmen("Switch Keller", "12:00:00:00:00:01", tabelle=TABELLE).kat == "netz"


def test_hersteller_und_zufallsadresse():
    assert ar.hersteller("00:04:0e:aa:bb:cc", TABELLE) == "AVM"
    assert ar.zufallsadresse("02:11:22:33:44:03") and ar.zufallsadresse("DA:11:22:33:44:03")
    assert not ar.zufallsadresse("00:04:0E:AA:BB:CC")
    assert ar.hersteller("F2:D5:BF:00:00:01", TABELLE) is None  # lokal vergeben → kein Hersteller
    assert ar.hersteller("00:04:0E:00:00:01") == "AVM"  # mitgelieferte Liste


def test_mesh_nur_mesh_geraete_mit_allen_adressen():
    assert ar.mesh_aus(MESH) == {
        "AA:00:00:00:00:01": "FRITZ!Box 6860 5G",
        "AA:00:00:00:00:02": "FRITZ!Repeater 3000",
        "00:11:22:33:44:04": "FRITZ!Repeater 3000",
    }
    assert ar.mesh_aus("kaputt") == {} and ar.mesh_aus("[]") == {}


def test_gruppen():
    assert ar.gruppen([("smart", True), ("netz", True), ("smart", False)]) == [
        {"name": "netz", "text": "🛜 Netzwerk", "online": 1, "gesamt": 1},
        {"name": "smart", "text": "🔌 Smart Home", "online": 1, "gesamt": 2},
    ]


def test_drucker_eigene_art():
    """AN-0004: Drucker haben eine eigene Art statt „Computer“."""
    assert "drucker" in ar.TEXT and ar.TEXT["drucker"] == "🖨️ Drucker"
    assert ar.aus_ha("HP", "LaserJet Pro M404") == "drucker"
    assert ar.aus_ha("Brother", "MFC-L2710DW") == "drucker"
    assert ar.aus_ha("Epson", "") == "drucker"
    assert ar.aus_ha("HP", "EliteBook 840") is None  # HP allein sagt nichts
    assert ar.bestimmen("Drucker Büro", "AA:BB:CC:00:00:01", tabelle={}).kat == "drucker"
    assert (
        ar.bestimmen("x", "00:1B:A9:00:00:01", tabelle={"001BA9": "Brother"}).kat == "drucker"
    )  # Hersteller
    assert ar.bestimmen("x", "AA:BB:CC:00:00:01", selbst="drucker").quelle == "selbst gewählt"
    gruppen = ar.gruppen([("drucker", True), ("computer", False)])
    assert [g["name"] for g in gruppen] == ["computer", "drucker"]


# ── WU-0010: eigene Arten ──
def test_eigene_anlegen_aendern_pruefen():
    eigene, k1 = ar.eigene_neu({}, "🏗️", "  Baustelle ")
    assert k1 == "eigen:1" and eigene[k1] == ar.EigeneArt("🏗️", "Baustelle")
    assert eigene[k1].text == "🏗️ Baustelle"
    eigene, k2 = ar.eigene_neu(eigene, "", "Werkstatt")
    assert k2 == "eigen:2" and eigene[k2].symbol == ar.SYMBOL_VORGABE  # ohne Symbol: 🏷️
    for symbol, name in (
        ("x", "baustelle"),
        ("x", ""),
        ("x", "a" * 31),
        ("ab cd", "Neu"),
        ("x", "a\x07b"),
        ("\u202e🏗", "Rtl"),
    ):
        with pytest.raises(Ungueltig):
            ar.eigene_neu(eigene, symbol, name)
    umbenannt = ar.eigene_aendern(eigene, k1, "🚧", "Baustelle Nord")
    assert umbenannt[k1].text == "🚧 Baustelle Nord" and umbenannt[k2] == eigene[k2]
    assert (
        ar.eigene_aendern(eigene, k1, "🏗️", "BAUSTELLE")[k1].name == "BAUSTELLE"
    )  # eigener Name zählt nicht
    with pytest.raises(Ungueltig):
        ar.eigene_aendern(eigene, "eigen:9", "x", "y")
    # Kennung hängt nicht am Namen und zählt weiter hoch, auch nach dem Löschen der höchsten nicht doppelt belegt
    _, k3 = ar.eigene_neu({k2: eigene[k2]}, "x", "Garten")
    assert k3 == "eigen:3"
    voll = {f"eigen:{i}": ar.EigeneArt("x", f"A{i}") for i in range(ar.EIGENE_HOECHSTENS)}
    with pytest.raises(Ungueltig):
        ar.eigene_neu(voll, "x", "Zu viel")


def test_eigene_laden_verwirft_unlesbares():
    roh = {
        "eigen:1": {"symbol": "🏗️", "name": "Baustelle"},
        "eigen:2": {"symbol": "x", "name": ""},
        "netz": {"symbol": "x", "name": "fest"},
        "eigen:3": "kaputt",
    }
    assert ar.eigene_aus(roh) == {"eigen:1": ar.EigeneArt("🏗️", "Baustelle")}
    assert ar.eigene_aus(None) == {}


def test_eigene_gelten_wie_feste():
    eigene = {"eigen:1": ar.EigeneArt("🏗️", "Baustelle")}
    mac = "C8:C9:A3:00:00:01"
    assert ar.bestimmen("x", mac, selbst="eigen:1", tabelle=TABELLE, eigene=eigene) == ar.Art(
        "eigen:1", "selbst gewählt"
    )
    # gelöscht (nicht mehr unter den eigenen): wieder erkannt
    assert ar.bestimmen("x", mac, selbst="eigen:1", tabelle=TABELLE).kat == "smart"
    namen = [k["name"] for k in ar.kategorien("de", eigene)]
    assert namen[-1] == "eigen:1" and namen[: len(ar.KATEGORIEN)] == [k for k, _ in ar.KATEGORIEN]
    g = ar.gruppen([("eigen:1", True), ("netz", False), ("eigen:1", False)], "de", eigene)
    assert [(x["name"], x["text"], x["online"], x["gesamt"]) for x in g] == [
        ("netz", "🛜 Netzwerk", 0, 1),
        ("eigen:1", "🏗️ Baustelle", 1, 2),
    ]
    assert (
        ar.alle("en", eigene)[0] == ("netz", "🛜 Network")
        and ar.alle("en", eigene)[-1][1] == "🏗️ Baustelle"
    )
