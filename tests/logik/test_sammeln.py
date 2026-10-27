"""Ein ganzer Abruf: Gedächtnis, Journal, Ausfall der Box (G-21)."""

from dataclasses import replace

from daten import GERAETELOG, HOSTLISTE, ZELLEN
from logik import befunde as bf
from logik import geraete as gr
from logik import mobil as mb
from logik import protokoll as pr
from logik import sammeln as sm
from logik import verkehr as vk

LAN = bf.Heimnetz("192.168.170.1", "255.255.255.0", "192.168.170.20", "192.168.170.200", True)
PI = bf.PiVerbindung(box=True, internet=True, dns=True, gw_mac="AA")
T0 = 1_800_000_000.0


def roh(t=T0, **kw):
    werte = {
        "pi": PI,
        "protokoll": pr.aus_xml(GERAETELOG),
        "lan": LAN,
        "geraete": gr.aus_hostliste(HOSTLISTE),
        "mobil": mb.aus_antwort({"NewCurrentAccessTechnology": "5G-NSA", "NewCellList": ZELLEN}),
        "zaehler": vk.Zaehlerstand(t, int(t) * 1000, int(t) * 100),
    }
    werte.update(kw)
    return sm.Rohdaten(jetzt=t, **werte)


def test_erster_abruf():
    g = sm.Gedaechtnis()
    s = sm.auswerten(g, roh())
    assert s.box_erreichbar and s.online == 5 and s.gesamt == "kritisch"
    assert [e.art for e in s.ereignisse][0] == "start"
    assert {e.art for e in s.ereignisse[1:]} == {"befund"}
    assert len(s.protokoll) == 2 and s.rate is None
    assert g.mobil_technik == "5G-NSA" and g.mobil_zelle == "abcde-0b/443"


def test_zweiter_abruf_nur_aenderungen():
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh())
    geraete = gr.aus_hostliste(HOSTLISTE)
    geraete["00:11:22:33:44:04"] = replace(geraete["00:11:22:33:44:04"], aktiv=False)
    s = sm.auswerten(g, roh(T0 + 60, geraete=geraete))
    arten = sorted(e.art for e in s.ereignisse)
    assert arten == [
        "befund_weg",
        "offline",
    ]  # gesperrtes Gerät offline → Befund „gesperrt“ erledigt
    assert s.protokoll == () and s.rate is not None and s.rate.sek == 60


def test_box_weg_und_zurueck():
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh())
    keys = dict(g.befunde)
    weg = sm.auswerten(
        g,
        sm.Rohdaten(
            jetzt=T0 + 60,
            pi=replace(PI, box=False, internet=False),
            fehler=("Gerätetabelle: Zeitüberschreitung",),
        ),
    )
    assert not weg.box_erreichbar and weg.gesamt == "box_fehlt"
    assert weg.geraete == {} and weg.mobil is None
    assert g.befunde == keys  # ohne Gerätetabelle bleibt offen, ob alte Befunde erledigt sind
    assert {e.art for e in weg.ereignisse} == {"pi_box", "pi_internet"}
    assert [b.key for b in weg.befunde] == ["kein_internet"]
    zurueck = sm.auswerten(g, roh(T0 + 120))
    assert zurueck.gesamt == "kritisch" and {e.art for e in zurueck.ereignisse} == {
        "pi_box",
        "pi_internet",
    }


def test_hardware_adresse_bleibt_ohne_arp_eintrag():
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh())
    s = sm.auswerten(g, roh(T0 + 60, pi=replace(PI, gw_mac="")))
    assert s.pi.gw_mac == "AA" and not any(b.key.startswith("gw_mac") for b in s.befunde)


def test_neue_hardware_adresse_bleibt_befund_bis_sie_24h_stabil_ist():
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh())
    for t in (60, 120, sm.GW_STABIL_S - 1):  # nicht schon nach einem Abruf wieder „erledigt“
        s = sm.auswerten(g, roh(T0 + t, pi=replace(PI, gw_mac="BB")))
        assert any(b.key == "gw_mac:BB" for b in s.befunde), t
    s = sm.auswerten(g, roh(T0 + 60 + sm.GW_STABIL_S, pi=replace(PI, gw_mac="BB")))
    assert not any(b.key.startswith("gw_mac") for b in s.befunde) and g.gw_mac_bekannt == "BB"


def test_kurzer_wechsel_zurueck_setzt_frist_zurueck():
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh())
    sm.auswerten(g, roh(T0 + 60, pi=replace(PI, gw_mac="BB")))
    s = sm.auswerten(g, roh(T0 + 120))
    assert not any(b.key.startswith("gw_mac") for b in s.befunde) and g.gw_wechsel_seit is None


def test_langsame_pruefungen():
    g = sm.Gedaechtnis()
    assert g.langsam_faellig(T0)
    s = sm.auswerten(g, roh(dhcp=bf.DhcpTest(True, ()), quellen={"00:11:22:33:44:01": "Static"}))
    assert not g.langsam_faellig(T0 + 60) and g.langsam_faellig(T0 + sm.LANGSAM_S)
    assert "dhcp_stumm" in {b.key for b in s.befunde}
    assert "fest_im_dhcp:00:11:22:33:44:01" in {b.key for b in s.befunde}
    s = sm.auswerten(
        g, roh(T0 + 60)
    )  # Ergebnis des DHCP-Tests und Adressquellen gelten bis zum nächsten Test
    assert s.dhcp is not None and "dhcp_stumm" in {b.key for b in s.befunde}
    assert s.geraete["00:11:22:33:44:01"].quelle == "Static"


def test_mobilfunk_dienst_erst_unbekannt():
    g = sm.Gedaechtnis()
    assert g.mobil_dienst is None
    sm.auswerten(g, sm.Rohdaten(jetzt=T0, pi=PI))  # Box nicht erreicht: weiter unbekannt
    assert g.mobil_dienst is None
    sm.auswerten(g, roh())
    assert g.mobil_dienst is True
    g2 = sm.Gedaechtnis()
    sm.auswerten(g2, roh(mobil=None, ohne_mobilfunk=True))
    assert g2.mobil_dienst is False


def test_gedaechtnis_hin_und_zurueck():
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh(dhcp=bf.DhcpTest(True, ())))
    sm.auswerten(g, roh(T0 + 60, pi=replace(PI, gw_mac="BB")))
    d = sm.gedaechtnis_als_dict(g)
    import json

    zurueck = sm.gedaechtnis_aus_dict(json.loads(json.dumps(d)))
    # DHCP-Test, Pi-Prüfung und die langsamen Abfragen laufen nach einem Neustart sofort neu
    assert zurueck == replace(g, dhcp=None, pi=None, langsam_t=0.0)
    assert sm.gedaechtnis_aus_dict({"version": 99}) == sm.Gedaechtnis()


def test_wlan_und_mobilfunk_ueber_mehrere_abrufe():
    from logik import wlan as wl

    g = sm.Gedaechtnis()
    b24, b5 = wl.Band("2,4", True, 6, True, "ax"), wl.Band("5", True, 44, True, "ax")
    handy = wl.Funkgeraet("00:11:22:33:44:02", 44, 80, 866, False)  # in der Gerätetabelle
    mobil = mb.aus_antwort(
        {"NewCurrentAccessTechnology": "5G-NSA", "NewCellList": ZELLEN, "NewUptime": "5000"}
    )
    s = sm.auswerten(
        g,
        roh(
            mobil=mobil,
            mobil_baender="LTE 3",
            wlan_baender=(b24, b5),
            wlan_gast=False,
            wlan_geraete=(handy,),
        ),
    )
    assert s.wlan == wl.Wlan((b24, b5), False, (handy,)) and s.mobil_baender == "LTE 3"
    assert g.wlan_schnell == [handy.mac] and g.wlan_kanaele == {"2,4": 6, "5": 44}
    # nächster Abruf: Bänder nicht gelesen (nur alle 10 min) – die letzten bleiben; Kanal 5 GHz gewechselt später
    neu_mobil = replace(mobil, laufzeit_s=30)
    s = sm.auswerten(g, roh(T0 + 60, mobil=neu_mobil, wlan_geraete=(replace(handy, kanal=6),)))
    assert s.wlan is not None and s.wlan.baender == (b24, b5) and s.mobil_baender == "LTE 3"
    assert [e.art for e in s.ereignisse] == ["mobil_neu"]
    s = sm.auswerten(g, roh(T0 + 120, wlan_baender=(b24, replace(b5, kanal=36)), wlan_geraete=()))
    assert [e.text for e in s.ereignisse] == ["WLAN 5 GHz: Kanal 44 → 36"]
    assert sm.auswerten(g, roh(T0 + 180)).wlan is None  # Box ohne WLAN-Dienst / nicht gelesen
    g.mesh = {"AA:00:00:00:00:02": "FRITZ!Repeater 3000"}
    zurueck = sm.gedaechtnis_aus_dict(sm.gedaechtnis_als_dict(g))
    assert zurueck.mesh == g.mesh
    assert (
        zurueck.wlan_kanaele,
        zurueck.wlan_schnell,
        zurueck.mobil_laufzeit,
        zurueck.mobil_baender,
    ) == (
        {"2,4": 6, "5": 36},
        [handy.mac],
        30,
        "LTE 3",
    )


def test_internet_stoerung_wird_zusammengefasst():
    """AN-0003: Ausfall bei stehender Mobilfunk-Verbindung → Befund nennt den Anbieter; nach 10 min Ruhe ein Eintrag."""
    from dataclasses import replace as ersetze

    from logik import stoerung as sg

    g = sm.Gedaechtnis()
    sm.auswerten(g, roh(T0))
    weg = ersetze(PI, internet=False)
    s = sm.auswerten(g, roh(T0 + 60, pi=weg))
    befund = next(b for b in s.befunde if b.key == "kein_internet")
    assert "vermutlich beim Anbieter" in befund.text
    sm.auswerten(g, roh(T0 + 120))
    sm.auswerten(g, roh(T0 + 180, pi=weg))
    sm.auswerten(g, roh(T0 + 240))
    zurueck = sm.gedaechtnis_aus_dict(sm.gedaechtnis_als_dict(g))
    assert zurueck.stoerung == g.stoerung and g.stoerung.anzahl == 2  # übersteht einen Neustart
    s = sm.auswerten(g, roh(T0 + 240 + sg.RUHE_S))
    texte = [e.text for e in s.ereignisse]
    assert any(t.startswith("Internet-Störung vorbei: 2 Unterbrechungen") for t in texte), texte
    assert g.stoerung is None


def test_zugang_dsl_ersatz_und_neusync():
    """WU-0009: Zugang und DSL-Werte über mehrere Abrufe – Ersatz springt ein, Neusynchronisierung ins Journal,
    Fehler je Stunde, alles übersteht das Gedächtnis."""
    from logik import leitung as ln
    from logik import zugang as zg

    dsl_meldung = zg.Meldung(
        zugangsart="DSL",
        link="Up",
        mobil_dienst=True,
        mobil_an=True,
        dsl_dienst=True,
        dsl_status="Up",
    )
    leitung = ln.Dsl(t=T0, status="Up", sync_down=108_396, marge_down=52, crc=100, fec=1000)
    g = sm.Gedaechtnis()
    s = sm.auswerten(g, roh(zugang=dsl_meldung, dsl=leitung))
    assert s.zugang_art == "dsl" and not s.ersatz_aktiv and s.dsl == leitung
    assert not {e.art for e in s.ereignisse} & {"zugang", "ersatz_an", "dsl_sync"}

    # 10 min später: Fehler je Stunde
    s = sm.auswerten(
        g, roh(T0 + 600, zugang=dsl_meldung, dsl=replace(leitung, t=T0 + 600, crc=102, fec=1100))
    )
    assert (s.dsl_crc_h, s.dsl_fec_h) == (12.0, 600.0)

    # DSL weg, der Stick trägt
    ausfall = replace(dsl_meldung, zugangsart="X_AVM-DE_LTE", dsl_status="NoSignal")
    s = sm.auswerten(g, roh(T0 + 1200, zugang=ausfall, dsl=ln.Dsl(t=T0 + 1200, status="NoSignal")))
    assert s.zugang_art == "dsl" and s.ersatz_aktiv
    assert "ersatz_an" in {e.art for e in s.ereignisse}

    # zurück: neu synchronisiert, Ersatz aus
    s = sm.auswerten(
        g, roh(T0 + 1800, zugang=dsl_meldung, dsl=replace(leitung, t=T0 + 1800, crc=0, fec=0))
    )
    arten = {e.art for e in s.ereignisse}
    assert {"ersatz_aus", "dsl_sync"} <= arten and not s.ersatz_aktiv
    assert s.dsl_neusync == 1 and s.dsl_seit == T0 + 1800

    # Gedächtnis hin und zurück
    g2 = sm.gedaechtnis_aus_dict(sm.gedaechtnis_als_dict(g))
    assert (g2.zugang, g2.zugang_art, g2.zugang_haupt, g2.dsl, g2.dsl_neusync) == (
        g.zugang,
        g.zugang_art,
        g.zugang_haupt,
        g.dsl,
        g.dsl_neusync,
    )

    # Zwischen den langsamen Abrufen bleibt der Stand; Zugang ohne DSL-Werte → DSL weg
    s = sm.auswerten(g, roh(T0 + 1860))
    assert s.zugang_art == "dsl" and s.dsl is not None
    s = sm.auswerten(g, roh(T0 + 2400, zugang=replace(dsl_meldung, dsl_dienst=False)))
    assert s.dsl is None


def test_zugang_glasfaser_und_wechsel():
    from logik import leitung as ln
    from logik import zugang as zg

    g = sm.Gedaechtnis()
    s = sm.auswerten(g, roh(zugang=zg.Meldung(zugangsart="X_AVM-DE_LTE", mobil_dienst=True)))
    assert s.zugang_art == "mobilfunk" and s.faser is None
    faser = ln.Faser(t=T0 + 600, rx=-19_400, fehler_rx=10)
    s = sm.auswerten(
        g,
        roh(
            T0 + 600,
            zugang=zg.Meldung(zugangsart="X_AVM-DE_Fiber", faser_dienst=True, faser_modus="GPON"),
            faser=faser,
        ),
    )
    assert s.zugang_art == "glasfaser" and s.faser == faser
    assert [e.text for e in s.ereignisse if e.art == "zugang"] == [
        "Internetzugang: jetzt Glasfaser (vorher Mobilfunk)"
    ]


def test_dsl_lesefehler_und_verbunden_seit():
    """Ein einzelner Lesefehler lässt den DSL-Stand stehen; „verbunden seit“ bleibt auch nach 7 Tagen."""
    from logik import leitung as ln
    from logik import zugang as zg

    m = zg.Meldung(zugangsart="DSL", link="Up", dsl_dienst=True, dsl_status="Up")
    leitung = ln.Dsl(t=T0, status="Up", crc=10, fec=10)
    g = sm.Gedaechtnis()
    sm.auswerten(g, roh(zugang=m, dsl=leitung))
    s = sm.auswerten(g, roh(T0 + 600, zugang=m, dsl=replace(leitung, t=T0 + 600, crc=0, fec=0)))
    assert s.dsl_seit == T0 + 600
    s = sm.auswerten(g, roh(T0 + 1200, zugang=m))  # DSL-Abfrage gescheitert
    assert s.dsl is not None and s.dsl_seit == T0 + 600
    spaet = T0 + 9 * 86_400
    s = sm.auswerten(g, roh(spaet, zugang=m, dsl=replace(leitung, t=spaet, crc=5, fec=5)))
    assert s.dsl_neusync == 0 and s.dsl_seit == T0 + 600
    # während des Ausfalls (Ersatz) bleibt die Leitung mit „nicht synchron“
    aus = replace(m, zugangsart="X_AVM-DE_LTE", dsl_status="NoSignal", mobil_dienst=True)
    s = sm.auswerten(g, roh(spaet + 600, zugang=aus, dsl=ln.Dsl(t=spaet + 600, status="NoSignal")))
    assert s.ersatz_aktiv and s.dsl.status == "NoSignal"
    s = sm.auswerten(g, roh(spaet + 1200, zugang=m, dsl=replace(leitung, t=spaet + 1200)))
    assert "dsl_sync" in {e.art for e in s.ereignisse} and s.dsl_seit == spaet + 1200
