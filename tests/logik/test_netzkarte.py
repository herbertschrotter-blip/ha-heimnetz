"""Netzkarte (1.9): Mesh-Liste lesen (Buchse, Band, Rate, Repeater, Switch) und Lage der Punkte."""

import json
import math

from logik import netzkarte as nk

# Aufbau wie die Mesh-Liste der FRITZ!Box: Knoten mit Schnittstellen, Verbindungen zwischen Schnittstellen (kbit/s)
BOX = {
    "uid": "n-box",
    "is_meshed": True,
    "mesh_role": "master",
    "device_mac_address": "00:00:00:00:00:01",
    "node_interfaces": [
        {"uid": "i-lan1", "name": "LAN:1", "type": "LAN", "mac_address": "00:00:00:00:00:01"},
        {"uid": "i-lan3", "name": "LAN:3", "type": "LAN", "mac_address": "00:00:00:00:00:01"},
        {"uid": "i-2g", "name": "AP:2G:0", "type": "WLAN", "op_mode": "AP", "current_channel": 6},
        {"uid": "i-5g", "name": "AP:5G:0", "type": "WLAN", "op_mode": "AP", "current_channel": 44},
        {
            "uid": "i-gast",
            "name": "AP_GUEST:2G:0",
            "type": "WLAN",
            "op_mode": "AP_GUEST",
            "current_channel": 6,
        },
    ],
}


def link(a, ia, b, ib, kbit, state="CONNECTED"):
    return {
        "state": state,
        "node_1_uid": a,
        "node_interface_1_uid": ia,
        "node_2_uid": b,
        "node_interface_2_uid": ib,
        "cur_data_rate_rx": kbit,
        "cur_data_rate_tx": kbit // 2,
    }


def client(uid, mac, typ, gegen, gegen_if, kbit, state="CONNECTED"):
    return {
        "uid": uid,
        "is_meshed": False,
        "mesh_role": "unknown",
        "device_mac_address": mac,
        "node_interfaces": [
            {
                "uid": f"{uid}-if",
                "type": typ,
                "mac_address": mac,
                "node_links": [link(gegen, gegen_if, uid, f"{uid}-if", kbit, state)],
            }
        ],
    }


REP = {
    "uid": "n-rep",
    "is_meshed": True,
    "mesh_role": "slave",
    "device_model": "FRITZ!Repeater 1200 AX",
    "device_mac_address": "00:00:00:00:00:0R",
    "node_interfaces": [
        {
            "uid": "r-up",
            "name": "UPLINK:5G:0",
            "type": "WLAN",
            "mac_address": "00:00:00:00:00:0R",
            "node_links": [link("n-box", "i-5g", "n-rep", "r-up", 866_000)],
        },
        {"uid": "r-2g", "name": "AP:2G:0", "type": "WLAN", "op_mode": "AP"},
    ],
}

MESH = json.dumps(
    {
        "nodes": [
            BOX,
            REP,
            client("c-desk", "aa:00:00:00:00:01", "LAN", "n-box", "i-lan1", 1_000_000),
            client("c-nas", "aa:00:00:00:00:02", "LAN", "n-box", "i-lan3", 1_000_000),
            client("c-medi", "aa:00:00:00:00:03", "LAN", "n-box", "i-lan3", 100_000),
            client("c-tab", "aa:00:00:00:00:04", "WLAN", "n-box", "i-2g", 6_000),
            client("c-tv", "aa:00:00:00:00:05", "WLAN", "n-box", "i-5g", 866_000),
            client("c-gast", "aa:00:00:00:00:06", "WLAN", "n-box", "i-gast", 72_000),
            client("c-saug", "aa:00:00:00:00:07", "WLAN", "n-rep", "r-2g", 52_000),
            client(
                "c-weg", "aa:00:00:00:00:08", "WLAN", "n-box", "i-5g", 400_000, state="DISCONNECTED"
            ),
        ]
    }
)


def test_mesh_buchse_band_rate_gast():
    n = nk.mesh_lesen(MESH)
    assert n.geraete["AA:00:00:00:00:01"] == nk.Anschluss("box", "lan", 1, None, 1000)
    assert n.geraete["AA:00:00:00:00:03"].port == 3 and n.geraete["AA:00:00:00:00:03"].mbit == 100
    assert n.geraete["AA:00:00:00:00:04"] == nk.Anschluss("box", "wlan", None, "2,4", 6)
    assert n.geraete["AA:00:00:00:00:05"].band == "5"
    assert n.geraete["AA:00:00:00:00:06"].gast is True
    assert "AA:00:00:00:00:08" not in n.geraete  # getrennt zählt nicht


def test_mesh_repeater_und_seine_geraete():
    n = nk.mesh_lesen(MESH)
    (r,) = n.repeater
    assert (r.id, r.name) == ("r1", "FRITZ!Repeater 1200 AX")
    assert r.uplink == nk.Anschluss("box", "wlan", None, "5", 866)
    assert n.geraete["AA:00:00:00:00:07"] == nk.Anschluss("r1", "wlan", None, "2,4", 52)
    assert "00:00:00:00:00:0R" not in n.geraete


def test_mesh_kaputt_oder_leer():
    assert nk.mesh_lesen("kaputt") == nk.Netz()
    assert nk.mesh_lesen(json.dumps({"nodes": "x"})) == nk.Netz()
    assert nk.mesh_lesen(b'{"nodes": [{"uid": 1}]}') == nk.Netz()


def test_band_aus_kanal_wenn_name_nichts_sagt():
    assert (
        nk._band("WLAN", 36) == "5" and nk._band("", 11) == "2,4" and nk._band(None, None) is None
    )
    assert nk._band("AP:6G:0", 37) == "6"


KAT = [
    ("netz", "🛜 Netzwerk"),
    ("computer", "💻 Computer"),
    ("medien", "📺 Medien"),
    ("mobil", "📱 Handy"),
]


def punkte():
    def p(i, name, kat, **kw):
        return nk.Punkt(
            id=f"id{i}",
            mac=f"aa:00:00:00:00:0{i}",
            name=name,
            symbol="•",
            kat=kat,
            ip=f"192.168.178.{20 + i}",
            aktiv=kw.pop("aktiv", True),
            zustand=kw.pop("zustand", "an"),
            **kw,
        )

    return [
        p(1, "Desktop", "computer", art="LAN"),
        p(2, "NAS", "computer", art="LAN"),
        p(3, "Mediaplayer", "medien", art="LAN"),
        p(4, "Tab", "mobil", art="WLAN", band="2,4", signal=18, mbit=6, schwach=True),
        p(5, "Fernseher", "medien", art="WLAN", band="5", signal=92, mbit=866),
        p(6, "Gast", "mobil", art="WLAN", zustand="neu", signal=80),
        p(7, "Saugroboter", "netz", art="WLAN", signal=46),
        p(8, "Uhr", "mobil", art="WLAN", aktiv=False, zustand="aus"),
        nk.Punkt(
            id="rep",
            mac="00:00:00:00:00:0R",
            name="Repeater",
            symbol="🛜",
            kat="netz",
            ip="",
            aktiv=True,
            zustand="an",
            art="WLAN",
        ),
    ]


def r(e, um=nk.MITTE):
    return math.hypot(e["x"] - um[0], e["y"] - um[1])


def test_karte_switch_an_gemeinsamer_buchse():
    k = nk.zeichnen(punkte(), nk.mesh_lesen(MESH), KAT)
    (s,) = k["switche"]
    assert (s["port"], s["n"], s["mbit"]) == (3, 2, 1000)
    hinter = {g["name"]: g for g in k["geraete"] if g["ueber"] == "switch"}
    assert set(hinter) == {"NAS", "Mediaplayer"}
    assert (hinter["NAS"]["vx"], hinter["NAS"]["vy"]) == (s["x"], s["y"])
    assert hinter["Mediaplayer"]["anbindung"] == "Switch an LAN 3 · 100 Mbit/s"
    desk = next(g for g in k["geraete"] if g["name"] == "Desktop")
    assert desk["ueber"] == "box" and desk["port"] == 1 and desk["anbindung"] == "LAN 1 · 1 Gbit/s"
    assert round(r(desk)) == nk.R_KABEL


def test_karte_ringe_nach_band_und_empfang():
    k = nk.zeichnen(punkte(), nk.mesh_lesen(MESH), KAT)
    g = {x["name"]: x for x in k["geraete"]}
    assert [x["name"] for x in k["ringe"]] == ["Kabel", "5 GHz", "2,4 GHz", "offline"]
    assert r(g["Fernseher"]) < r(g["Tab"])  # 5 GHz innen, 2,4 außen
    assert r(g["Tab"]) > nk.R_WLAN[1]  # schwacher Empfang weiter draußen
    assert (
        g["Tab"]["zustand"] == "schwach"
        and g["Tab"]["anbindung"] == "WLAN 2,4 GHz · 18 % · 6 Mbit/s"
    )
    assert g["Gast"]["gast"] is True and g["Gast"]["zustand"] == "neu"
    (uhr,) = k["aus"]
    assert uhr["name"] == "Uhr" and round(r(uhr)) == nk.R_AUS
    assert k["zahlen"] == {"online": 7, "offline": 1, "auffaellig": 1, "neu": 1, "vpn": 0}


def test_karte_repeater_mit_seinen_geraeten():
    k = nk.zeichnen(punkte(), nk.mesh_lesen(MESH), KAT)
    (rep,) = k["repeater"]
    assert (
        rep["name"] == "FRITZ!Repeater 1200 AX"
        and rep["n"] == 1
        and rep["text"] == "WLAN 5 GHz · 866 Mbit/s"
    )
    saug = next(g for g in k["geraete"] if g["name"] == "Saugroboter")
    assert saug["ueber"] == "repeater" and (saug["vx"], saug["vy"]) == (rep["x"], rep["y"])
    assert round(r(saug, (rep["x"], rep["y"]))) == nk.R_UM_REPEATER
    assert saug["anbindung"].endswith("Repeater")
    assert all(
        g["name"] != "Repeater" for g in k["geraete"]
    )  # der Repeater selbst ist ein eigener Knoten


def test_karte_ohne_mesh_nach_geraetetabelle():
    k = nk.zeichnen(punkte(), nk.Netz(), KAT)
    assert k["switche"] == [] and k["repeater"] == []
    desk = next(g for g in k["geraete"] if g["name"] == "Desktop")
    assert desk["anbindung"] == "Kabel" and round(r(desk)) == nk.R_KABEL
    assert next(g for g in k["geraete"] if g["name"] == "Repeater")["ueber"] == "box"


def test_karte_bleibt_im_feld_und_oben_frei():
    viele = [
        nk.Punkt(
            id=f"x{i}",
            mac=f"bb:{i:02x}",
            name=f"D{i}",
            symbol="•",
            kat=["computer", "medien", "mobil"][i % 3],
            ip="",
            aktiv=i % 5 != 0,
            zustand="an",
            art="WLAN",
            band="2,4",
            signal=i % 100,
        )
        for i in range(60)
    ]
    k = nk.zeichnen(viele, nk.Netz(), KAT)
    assert k["dot"] == 7
    for g in k["geraete"] + k["aus"]:
        assert 0 <= g["x"] <= nk.BREITE and 0 <= g["y"] <= nk.HOEHE
        w = math.degrees(math.atan2(g["y"] - nk.MITTE[1], g["x"] - nk.MITTE[0])) % 360
        assert not 270 - 25 < w < 270 + 25  # Leitung ins Internet bleibt frei


def test_karte_englisch():
    k = nk.zeichnen(punkte(), nk.mesh_lesen(MESH), KAT, sprache="en")
    assert [x["name"] for x in k["ringe"]][-1] == "offline"
    assert next(g for g in k["geraete"] if g["name"] == "Tab")["anbindung"].startswith(
        "WLAN 2.4 GHz"
    )
    assert k["switche"][0]["text"] == "Switch on LAN 3"


def test_diagnose_ohne_adressen():
    d = nk.diagnose(nk.mesh_lesen(MESH))
    assert d["anschluesse"]["box:lan:3"] == 2 and d["anschluesse"]["r1:wlan:2,4"] == 1
    assert d["repeater"] == [{"name": "FRITZ!Repeater 1200 AX", "uplink": "wlan:5"}]
    assert "LAN:3" in d["schnittstellen"] and "AP:5G:0" in d["schnittstellen"]
    assert not any("AA:" in k or "00:00" in k for k in d["anschluesse"])


def test_vpn_am_tunnel():
    unterwegs = [
        nk.Punkt(
            id="v1",
            mac="cc:01",
            name="Laptop",
            symbol="💻",
            kat="computer",
            ip="10.0.8.2",
            aktiv=True,
            zustand="an",
            art="VPN",
            seit=100.0,
        ),
        nk.Punkt(
            id="v2",
            mac="cc:02",
            name="Alt",
            symbol="📱",
            kat="mobil",
            ip="10.0.8.3",
            aktiv=False,
            zustand="aus",
            art="VPN",
        ),
    ]
    k = nk.zeichnen(punkte(), nk.mesh_lesen(MESH), KAT, vpn=unterwegs)
    (g,) = k["vpn"]["geraete"]
    assert (k["vpn"]["x"], k["vpn"]["y"]) == nk.VPN and (g["vx"], g["vy"]) == nk.VPN
    assert (
        g["ueber"] == "vpn"
        and g["seit"] == 100.0
        and g["anbindung"] == "VPN (WireGuard) · über das Internet"
    )
    assert round(math.hypot(g["x"] - nk.VPN[0], g["y"] - nk.VPN[1])) == nk.R_UM_REPEATER
    assert 0 <= g["x"] <= nk.BREITE and 0 <= g["y"] <= nk.HOEHE
    assert k["zahlen"]["vpn"] == 1 and all(x["id"] != "v1" for x in k["geraete"])
    assert nk.zeichnen(punkte(), nk.Netz(), KAT)["vpn"] is None


def test_sektor_beschriftung_bleibt_im_bild():
    """Am Handy schnitt die Karte lange Sektor-Namen am Rand ab: die Mitte rückt so weit ein, dass der Text passt."""
    lang = "Fernseher & Musik"
    halb = len(lang) * nk.ZEICHEN_SEKTOR / 2
    assert nk._im_bild(20.0, lang) >= halb
    assert nk._im_bild(nk.BREITE - 20.0, lang) <= nk.BREITE - halb
    assert nk._im_bild(220.0, lang) == 220.0  # in der Mitte bleibt alles, wie es ist
    assert (
        nk._im_bild(20.0, "X" * 80) == nk.BREITE / 2
    )  # breiter als die Karte: mittig statt links hinaus
