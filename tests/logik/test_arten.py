"""Art eines Geräts (AN-0001): Reihenfolge der Quellen, Hersteller, Mesh, Name, Gruppen."""

from daten import MESH
from logik import arten as ar

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
