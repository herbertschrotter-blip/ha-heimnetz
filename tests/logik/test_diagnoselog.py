"""Diagnose-Log: Änderungen je Abruf, Hinweise auf Abfrage-Fehler, Häufung und geschwärzte Datei."""

from datetime import UTC

from logik import arten as ar
from logik import diagnoselog as dl
from logik import warnungen as wn

T0 = 1_800_000_000.0


def g(k, aktiv=True, **kw):
    return dl.Geraetstand(k, f"Name {k}", aktiv, **kw)


def a(t, geraete, box=True, internet=True, **kw):
    return dl.Aufnahme(T0 + t, box, internet, tuple(geraete), **kw)


def ereignisse(liste):
    return [e.daten["ereignis"] for e in liste]


def test_erster_abruf_ohne_geraetemeldungen_mit_stand():
    assert ereignisse(dl.Schreiber().schritt(a(0, [g("a"), g("b")]))) == ["start", "stand"]


def test_weg_und_wieder_da_mit_ort_und_dauer():
    s = dl.Schreiber()
    wlan = {"verbindung": "WLAN 2,4 GHz", "knoten": "Repeater", "signal": 42, "mbit": 72}
    s.schritt(a(0, [g("a", **wlan), g("b")]))
    weg = s.schritt(a(60, [g("a", False), g("b")]))
    assert ereignisse(weg) == ["weg"]
    assert dl.zeile(weg[0])["detail"] == "war WLAN 2,4 GHz · Repeater · 42 % · 72 Mbit/s"
    da = s.schritt(a(240, [g("a", **wlan), g("b")]))
    assert ereignisse(da) == ["da"]
    assert dl.zeile(da[0])["detail"] == "WLAN 2,4 GHz · Repeater · nach 3 min"


def test_wechsel_von_band_und_knoten():
    s = dl.Schreiber()
    s.schritt(a(0, [g("a", verbindung="WLAN 5 GHz", knoten="Box"), g("b")]))
    z = s.schritt(a(60, [g("a", verbindung="WLAN 2,4 GHz", knoten="Repeater"), g("b")]))
    assert dl.zeile(z[0])["detail"] == "WLAN 5 GHz → WLAN 2,4 GHz · Box → Repeater"


def test_abruf_luecke_box_und_geschrumpfte_liste_sind_keine_geraetemeldungen():
    s = dl.Schreiber()
    alle = [g(x) for x in "abcd"]
    s.schritt(a(0, alle))
    assert ereignisse(s.schritt(a(300, alle))) == ["luecke"]
    assert ereignisse(s.schritt(a(360, [g("a")]))) == ["liste"]
    assert ereignisse(s.schritt(a(420, [g("a")]))) == []
    assert ereignisse(s.schritt(a(480, alle))) == []
    assert ereignisse(s.schritt(a(500, [], box=False))) == ["box_weg"]
    assert ereignisse(s.schritt(a(560, alle))) == ["box_da"]


def test_internet_modem_warnung_und_box_zeile():
    s = dl.Schreiber()
    s.schritt(a(0, [g("a")], netz="5G-SA", zelle="PCI 1"))
    m = wn.Meldung("offline", T0, "a", "Name a", dauer_s=300)
    neu = s.schritt(
        a(
            60,
            [g("a")],
            internet=False,
            netz="LTE",
            zelle="PCI 2",
            warnungen=((m, False),),
            box_zeilen=(
                (T0 + 5, "wlan", "WLAN-Gerät abgemeldet"),
                (None, "telefon", "Anruf von 0123"),
            ),
        )
    )
    assert ereignisse(neu) == ["internet_weg", "netz", "zelle", "warnung", "zeile"]
    assert all("0123" not in str(e.daten) for e in neu)
    assert neu[-1].t == T0 + 5  # Zeit laut Box, nicht die des Abrufs
    assert dl.zeile(neu[3])["text"] == "🔔 Warnung: offline"
    assert dl.zeile(neu[3])["detail"] == "5 min · nicht verschickt"


def test_stand_alle_zehn_minuten():
    s = dl.Schreiber()
    s.schritt(a(0, [g("a")]))
    assert ereignisse(s.schritt(a(60, [g("a")]))) == []
    assert ereignisse(s.schritt(a(dl.STAND_S, [g("a")]))) == ["luecke", "stand"]


def weg(t, k, **kw):
    return dl.Eintrag(T0 + t, dl.GERAET, k, {"ereignis": "weg", "name": k, **kw})


def test_haeufung_nennt_gemeinsamen_ort_repeater_und_internet():
    liste = [
        weg(0, "a", knoten="Repeater", mesh=True),
        weg(30, "b", knoten="Repeater"),
        weg(60, "c", knoten="Box"),
    ]
    h = dl.haeufungen(liste)
    assert len(h) == 1
    assert h[0]["text"] == (
        "3 Geräte in 1 min weg, 2 davon auf Repeater, darunter ein Repeater. "
        "Zur selben Zeit keine Störung bei Internet oder Modem."
    )
    gestoert = [dl.Eintrag(T0 - 10, dl.INTERNET, "", {"ereignis": "internet_weg"}), *liste]
    assert "Internet gestört" in dl.haeufungen(gestoert)[0]["text"]


def test_keine_haeufung_bei_zwei_geraeten_oder_weitem_abstand():
    assert dl.haeufungen([weg(0, "a"), weg(10, "b")]) == []
    assert dl.haeufungen([weg(0, "a"), weg(300, "b"), weg(600, "c")]) == []


def test_datei_ohne_namen_mac_und_ip():
    mac = "AA:BB:CC:DD:EE:FF"
    liste = [
        dl.Eintrag(T0, dl.GERAET, mac, {"ereignis": "weg", "name": "Küche Heizung", "mesh": True}),
        dl.Eintrag(
            T0 + 1,
            dl.BOX,
            "",
            {
                "ereignis": "zeile",
                "text": f"WLAN-Gerät abgemeldet: Küche Heizung, IP 192.168.1.20, 2001:db8::1, MAC {mac}, Laptop",
            },
        ),
    ]
    inhalt = dl.datei(liste, ["Laptop"], UTC)
    text_ = str(inhalt)
    for geheim in ("Küche", "Laptop", "192.168", "2001:db8", "AA:BB"):
        assert geheim not in text_, geheim
    assert inhalt["zeilen"][0]["name"] == "Gerät 1"
    assert inhalt["zeilen"][0]["detail"] == "Repeater"


def test_anzeigen_neueste_zuerst_und_begrenzt():
    liste = [weg(i, "a") for i in range(dl.ZEILEN_SEITE + 5)]
    d = dl.anzeigen(liste)
    assert d["eintraege"] == dl.ZEILEN_SEITE + 5
    assert len(d["zeilen"]) == dl.ZEILEN_SEITE
    assert d["zeilen"][0]["t"] == liste[-1].t


def test_anbindung_aus_mesh_liste():
    roh = """{"nodes": [
      {"uid": "b", "mesh_role": "master", "device_mac_address": "00:00:00:00:00:01"},
      {"uid": "r", "mesh_role": "slave", "device_model": "FRITZ!Repeater 3000", "device_name": "Privat"},
      {"uid": "c", "mesh_role": "unknown", "device_mac_address": "aa:00:00:00:00:02", "node_interfaces": [
        {"node_links": [{"state": "CONNECTED", "node_1_uid": "r", "node_2_uid": "c"}]}]},
      {"uid": "d", "mesh_role": "unknown", "device_mac_address": "aa:00:00:00:00:03", "node_interfaces": [
        {"node_links": [{"state": "DISCONNECTED", "node_1_uid": "b", "node_2_uid": "d"}]}]}
    ]}"""
    assert ar.anbindung_aus(roh) == {"AA:00:00:00:00:02": "FRITZ!Repeater 3000"}
    assert ar.anbindung_aus("kaputt") == {}


def test_unbekannt_ist_kein_wechsel():
    s = dl.Schreiber()
    s.schritt(a(0, [g("a", verbindung="WLAN 5 GHz", knoten="Box"), g("b")]))
    assert s.schritt(a(60, [g("a", verbindung="WLAN"), g("b")])) == []
    assert s.schritt(a(120, [g("a", verbindung="WLAN 5 GHz", knoten="Box"), g("b")])) == []


def test_dauerhaft_kleinere_liste_gilt_wieder():
    s = dl.Schreiber()
    s.schritt(a(0, [g(x) for x in "abcdef"]))
    wenige = [g("a"), g("b")]
    assert ereignisse(s.schritt(a(60, wenige))) == ["liste"]
    for t_ in range(120, 300, 60):
        assert s.schritt(a(t_, wenige)) == []
    assert ereignisse(s.schritt(a(300, wenige))).count("raus") == 4
    assert ereignisse(s.schritt(a(360, [g("a", False), g("b")]))) == ["weg"]


def test_haeufung_waehrend_laufendem_ausfall_gilt_als_gestoert():
    liste = [
        dl.Eintrag(T0 - 3600, dl.INTERNET, "", {"ereignis": "internet_weg"}),
        weg(0, "a"),
        weg(10, "b"),
        weg(20, "c"),
    ]
    assert "Internet gestört" in dl.haeufungen(liste)[0]["text"]
    davor = [dl.Eintrag(T0 - 1800, dl.INTERNET, "", {"ereignis": "internet_da"})]
    assert "keine Störung" in dl.haeufungen([liste[0], *davor, *liste[1:]])[0]["text"]


def test_schwaerzen_ipv6_kurzformen_und_uhrzeit_bleibt():
    aus = dl.schwaerzen("Gateway fe80::1 und fd00::1234, DNS ::1 um 12:34:56", [])
    assert aus == "Gateway ⟨IP⟩ und ⟨IP⟩, DNS ⟨IP⟩ um 12:34:56"


def test_kurzer_lan_aussetzer_nur_im_stand_langer_mit_frueherer_zeit():
    s = dl.Schreiber()
    lan = {"verbindung": "LAN", "knoten": "Box"}
    s.schritt(a(0, [g("a", **lan), g("b")]))
    assert ereignisse(s.schritt(a(60, [g("a", False), g("b")]))) == []
    assert ereignisse(s.schritt(a(120, [g("a", **lan), g("b")]))) == [], "nach 1 min zurück: still"
    assert ereignisse(s.schritt(a(180, [g("a", False), g("b")]))) == []
    assert ereignisse(s.schritt(a(300, [g("a", False), g("b")]))) == []
    weg_ = s.schritt(a(360, [g("a", False), g("b")]))  # 3 min weg
    assert ereignisse(weg_) == ["weg"] and weg_[0].t == T0 + 180
    assert dl.zeile(weg_[0])["detail"] == "war LAN · Box"
    for t_ in (420, 480, 540):
        assert ereignisse(s.schritt(a(t_, [g("a", False), g("b")]))) == []
    da = s.schritt(a(600, [g("a", **lan), g("b")]))
    assert ereignisse(da) == ["da", "stand"]
    assert dl.zeile(da[0])["detail"] == "LAN · Box · nach 7 min"
    assert dl.zeile(da[1])["detail"].endswith("1 kurze LAN-Aussetzer")
    assert dl.zeile(da[1], "en")["detail"].endswith("1 short LAN dropouts")


def test_box_raeumt_inaktive_still_aus_der_liste_bekannte_sind_nicht_neu():
    s = dl.Schreiber()
    s.schritt(a(0, [g("a"), g("b"), g("c")]))
    assert ereignisse(s.schritt(a(60, [g("a", False), g("b"), g("c")]))) == ["weg"]
    assert ereignisse(s.schritt(a(120, [g("b"), g("c")]))) == [], "inaktiv entfernt: still"
    assert ereignisse(s.schritt(a(180, [g("a", False), g("b"), g("c")]))) == []
    assert ereignisse(s.schritt(a(240, [g("b"), g("c")]))) == []
    da = s.schritt(a(300, [g("a"), g("b"), g("c")]))
    assert ereignisse(da) == ["da"] and da[0].daten["dauer_s"] == 240
    assert ereignisse(s.schritt(a(360, [g("a"), g("b"), g("c"), g("d")]))) == ["neu"]
    assert ereignisse(s.schritt(a(420, [g("a"), g("b"), g("d")]))) == ["raus"], "aktiv verschwunden"


def test_kurzer_lan_aussetzer_auch_wenn_die_box_das_geraet_kurz_entfernt():
    s = dl.Schreiber()
    lan = {"verbindung": "LAN"}
    s.schritt(a(0, [g("a", **lan), g("b"), g("c")]))
    s.schritt(a(60, [g("a", False), g("b"), g("c")]))
    assert ereignisse(s.schritt(a(120, [g("b"), g("c")]))) == []
    assert ereignisse(s.schritt(a(150, [g("a", **lan), g("b"), g("c")]))) == []
    assert s.kurz == 1 and not s.offen


def test_haeufung_mit_nachgetragenem_lan_weg_in_zeitfolge():
    assert len(dl.haeufungen([weg(100, "a"), weg(0, "b"), weg(60, "c")])) == 1
