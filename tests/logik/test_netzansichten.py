"""1.10 Datenfluss und WLAN-Radar (aus dem Ergebnis der Netzkarte)."""

from logik import netzansichten as na


def geraet(id_, **w):
    g = {"id": id_, "name": id_, "symbol": "•", "zustand": "an", "kabel": False, "ueber": "box"}
    g.update(w)
    return g


KARTE = {
    "mitte": {"x": 220.0, "y": 252.0},
    "repeater": [{"id": "r1", "name": "Repeater Keller"}],
    "geraete": [
        geraet("pc", kabel=True, mbit=1000, x=282.0, y=252.0),
        geraet("nas", kabel=True, mbit=1000, x=282.0, y=260.0, switch="s1"),
        geraet("tv", band="5", mbit=866, signal=92, x=220.0, y=360.0),
        geraet("tab", band="2,4", mbit=6, signal=18, zustand="schwach", x=70.0, y=252.0),
        geraet("dose", band="2,4", mbit=72, signal=30, x=370.0, y=252.0),
        geraet(
            "robo", band="2,4", mbit=52, signal=None, x=100.0, y=100.0, rep="r1", vx=120.0, vy=150.0
        ),
    ],
    "vpn": {"geraete": [geraet("handy", ueber="vpn", mbit=None)]},
}


def test_fluss_gruppen_und_reihenfolge():
    f = na.fluss(KARTE, 84.0, 168.0)
    assert [g["id"] for g in f["gruppen"]] == ["kabel", "wlan:5", "wlan:2,4", "rep:r1", "vpn"]
    assert [g["name"] for g in f["gruppen"]][-2:] == ["Repeater Keller", "VPN"]
    ids = [g["id"] for g in f["geraete"]]
    assert ids.index("dose") < ids.index("tab")  # innerhalb einer Gruppe die schnellste zuerst
    assert f["internet"]["anteil"] == 50
    assert f["hoehe"] >= na.F_MIN_HOEHE
    # zwischen zwei Gruppen Luft für den Namen: Abstand der Gruppenknoten mindestens Zeile + Lücke
    ys = [g["y"] for g in f["gruppen"]]
    assert all(b - a >= na.F_ZEILE + na.F_LUECKE for a, b in zip(ys, ys[1:], strict=False))
    assert max(g["y"] for g in f["geraete"]) < f["hoehe"]
    # dünnster Faden: das langsamste Funkgerät, mit seiner Gruppe
    assert f["duennster"] == {"name": "tab", "mbit": 6, "wo": "2,4 GHz"}
    assert f["langsam"] == 1
    breite = {g["id"]: g["breite"] for g in f["geraete"]}
    assert breite["pc"] > breite["dose"] > breite["tab"] >= 1.6


def test_fluss_ohne_tarif_und_ohne_verkehr():
    f = na.fluss({"mitte": {"x": 0, "y": 0}, "geraete": []}, None, None)
    assert f["internet"]["anteil"] is None and f["gruppen"] == [] and f["duennster"] is None


def test_radar_abstand_nach_empfang_und_winkel_wie_karte():
    r = na.radar(KARTE, [("2,4", 6, False), ("5", None, True)])
    p = {x["id"]: x for x in r["geraete"]}
    assert set(p) == {"tv", "tab", "dose"}  # ohne Kabel; ohne Empfangswert nicht auf dem Radar
    assert r["ohne_empfang"] == 1

    def abstand(x):
        return ((x["x"] - 220) ** 2 + (x["y"] - 240) ** 2) ** 0.5

    assert abstand(p["tv"]) < abstand(p["dose"]) < abstand(p["tab"]) <= na.R_RADIUS
    assert (
        p["tab"]["x"] < 220 and p["dose"]["x"] > 220 and p["tv"]["y"] > 240
    )  # Richtung wie auf der Karte
    assert p["tab"]["farbe"] == "schwach" and p["tv"]["farbe"] == "5"
    assert p["dose"]["links"] and not p["tab"]["links"]
    assert all(-na.R_UMLAUF <= x["takt"] <= 0 for x in r["geraete"])
    assert r["kanaele"] == [
        {"band": "2,4 GHz", "kanal": 6, "auto": False, "n": 2},
        {"band": "5 GHz", "kanal": None, "auto": True, "n": 1},
    ]
    assert [x["name"] for x in r["rand"]] == [
        "tab",
        "dose",
    ]  # beide unter der Schwach-Grenze (40 %)


def test_radar_rand_nur_schwache_und_ringe_an_der_grenze():
    r = na.radar(KARTE, [], grenze=25)
    assert [x["name"] for x in r["rand"]] == ["tab"]  # dose (30 %) liegt über der Grenze
    assert [x["name"] for x in r["ringe"]] == ["sehr gut", "gut", "mäßig", "schwach"]
    maessig = r["ringe"][2]["r"]
    p = {x["id"]: x for x in r["geraete"]}

    def abstand(x):
        return ((x["x"] - 220) ** 2 + (x["y"] - 240) ** 2) ** 0.5

    # schwach gefärbt (unter der Grenze) heißt: außerhalb des Rings „mäßig“; der äußerste Ring ist erreichbar
    assert abstand(p["tab"]) > maessig > abstand(p["dose"])
    assert r["ringe"][-1]["r"] == round(na.R_RADIUS * na._abstand(0), 1)
    # Grenze über 60 %: die Zone „gut“ fällt weg
    assert [x["name"] for x in na.radar(KARTE, [], grenze=70)["ringe"]] == [
        "sehr gut",
        "mäßig",
        "schwach",
    ]
    # neu: eigener Merker, die Farbe bleibt das Band
    k = {**KARTE, "geraete": [geraet("neu1", band="5", signal=80, zustand="neu", x=300.0, y=252.0)]}
    q = na.radar(k, [])["geraete"][0]
    assert q["neu"] and q["farbe"] == "5"


def test_fluss_kabel_am_repeater_ist_kein_funk():
    k = {
        **KARTE,
        "geraete": [
            *KARTE["geraete"],
            geraet("drucker", kabel=True, mbit=10, rep="r1", x=0.0, y=0.0, vx=0.0, vy=0.0),
        ],
    }
    f = na.fluss(k, None, None)
    assert f["duennster"]["name"] == "tab" and f["langsam"] == 1


def test_radar_englisch():
    r = na.radar(KARTE, [("2,4", 6, False)], 40, "en")
    assert r["kanaele"][0]["band"] == "2.4 GHz" and r["ringe"][2]["name"] == "fair"
