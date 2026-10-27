"""Zugang erkennen (WU-0009): aus dem, was die FRITZ!Box über TR-064 meldet, plus die Wahl des Admins.

Testdaten nach der FRITZ!-Doku (TR-064 Support, WANCommonInterfaceConfig: NewWANAccessType DSL, Ethernet,
X_AVM-DE_Fiber, X_AVM-DE_UMTS, X_AVM-DE_Cable, X_AVM-DE_LTE, unknown; X_AVM-DE_GetAddonInfos: Cable, DSL, Ethernet,
Fiber, IP-Client, Mobile, Other). Nur eine FRITZ!Box 6860 5G war zum Ausprobieren da – DSL, Glasfaser und Kabel sind
erfundene Meldungen in dieser Form.
"""

import pytest
from logik import zugang as zg
from logik.sprache import ENG

MOBIL_6860 = zg.Meldung(
    zugangsart="X_AVM-DE_Mobile",  # so meldet sie die echte FRITZ!Box 6860 5G (27.10.2026), nicht X_AVM-DE_LTE
    link="Up",
    down_bit=1_000_000_000,
    up_bit=150_000_000,
    mobil_dienst=True,
    mobil_an=True,
    wan_netz="privat",  # Drei vergibt Adressen aus 10.x – zählt nur bei LAN 1
    vorschlag="10.120.7.1",
)
VDSL_7590 = zg.Meldung(
    zugangsart="DSL",
    link="Up",
    art_avm="DSL",
    down_bit=108_396_000,
    up_bit=38_189_000,
    mobil_dienst=True,  # Stick am USB
    mobil_an=True,
    dsl_dienst=True,
    dsl_status="Up",
    wan_netz="oeffentlich",
)
FASER_5590 = zg.Meldung(
    zugangsart="X_AVM-DE_Fiber",
    link="Up",
    art_avm="Fiber",
    faser_dienst=True,
    faser_modus="GPON",
    wan_netz="anbieter",
)
KABEL_6690 = zg.Meldung(zugangsart="X_AVM-DE_Cable", link="Up", art_avm="Cable")
HINTER_ZTE = zg.Meldung(
    zugangsart="Ethernet",
    link="Up",
    art_avm="IP-Client",
    mobil_dienst=False,
    wan_netz="privat",
    vorschlag="192.168.0.1",
)


@pytest.mark.parametrize(
    ("adresse", "erwartet"),
    [
        ("192.168.0.23", ("privat", "192.168.0.1")),
        ("10.120.7.88", ("privat", "10.120.7.1")),
        ("172.20.1.9", ("privat", "172.20.1.1")),
        ("100.70.12.3", ("anbieter", "")),
        ("203.0.113.5", ("oeffentlich", "")),
        ("", ("", "")),
        ("kaputt", ("", "")),
        ("0.0.0.0", ("", "")),
        ("2001:db8::1", ("", "")),
    ],
)
def test_wan_netz(adresse, erwartet):
    assert zg.wan_netz(adresse) == erwartet


def test_wan_netz_oeffentlich():
    assert zg.wan_netz("84.115.20.7") == ("oeffentlich", "")


@pytest.mark.parametrize(
    ("meldung", "art"),
    [
        (MOBIL_6860, "mobilfunk"),
        (VDSL_7590, "dsl"),
        (FASER_5590, "glasfaser"),
        (KABEL_6690, "kabel"),
        (HINTER_ZTE, "extern"),
        (zg.Meldung(zugangsart="X_AVM-DE_UMTS"), "mobilfunk"),
        (
            zg.Meldung(zugangsart="unknown", art_avm="Mobile"),
            "mobilfunk",
        ),  # neuere Angabe hilft aus
        (zg.Meldung(zugangsart="DSL", art_avm="IP-Client"), "extern"),  # hinter einem Router
        (zg.Meldung(zugangsart="unknown"), ""),
        (zg.Meldung(), ""),
    ],
)
def test_art_erkennen(meldung, art):
    assert zg.art_erkennen(meldung) == (art, False)


def test_ersatz_springt_ein_und_wird_vergessen():
    """DSL fällt aus, der Stick trägt: die Box meldet LTE, der Zugang bleibt DSL – „über Ersatz“."""
    ausfall = zg.Meldung(
        zugangsart="X_AVM-DE_LTE",
        link="Up",
        mobil_dienst=True,
        mobil_an=True,
        dsl_dienst=True,
        dsl_status="NoSignal",
    )
    assert zg.art_erkennen(ausfall, "dsl") == ("dsl", True)
    assert zg.art_erkennen(ausfall, "") == ("mobilfunk", False)  # ohne Gedächtnis: Mobilfunk
    # Glasfaser ohne Glasfaser-Modul: kein Ersatz, sondern Wechsel
    assert zg.art_erkennen(ausfall, "glasfaser") == ("mobilfunk", False)

    haupt, seit = zg.haupt_merken("", None, "dsl", False, 1000.0)
    assert (haupt, seit) == ("dsl", None)
    haupt, seit = zg.haupt_merken(haupt, seit, "dsl", True, 2000.0)
    assert (haupt, seit) == ("dsl", 2000.0)
    haupt, seit = zg.haupt_merken(haupt, seit, "dsl", True, 3000.0)
    assert seit == 2000.0, "Beginn des Ersatzes bleibt"
    assert zg.haupt_merken("dsl", 2000.0, "dsl", True, 2000.0 + zg.ERSATZ_VERGESSEN_S) == ("", None)
    assert zg.haupt_merken("dsl", None, "", False, 1.0) == ("dsl", None), "nichts erkannt: behalten"
    assert zg.haupt_merken("dsl", None, "mobilfunk", False, 1.0) == ("", None)


def test_beschreiben_mobilfunk_der_box():
    z = zg.beschreiben(
        MOBIL_6860, "mobilfunk", False, modell="FRITZ!Box 6860 5G", mobil_technik="5G-NSA"
    )
    assert z.art == "mobilfunk" and z.quelle == "automatisch" and z.weg == "eingebaut"
    assert z.titel == "Internet über Mobilfunk"
    assert z.geraet == "FRITZ!Box 6860 5G" and z.weg_text == "eingebautes Modem"
    assert z.belege[0] == "FRITZ!Box meldet: Internet über Mobilfunk (LTE/5G), verbunden"
    assert "Mobilfunk-Modem der Box: 5G-NSA" in z.belege
    assert not any("Adresse" in b for b in z.belege), "WAN-Adresse zählt nur bei LAN 1"
    assert (z.ersatz, z.adresse, z.abweichung) == ("", "", False)
    assert z.kopf == "FRITZ!Box 6860 5G · Mobilfunk 5G-NSA"
    assert z.vorschlag == "Mobilfunk über FRITZ!Box 6860 5G"


def test_beschreiben_stick_an_einer_box_ohne_modem():
    z = zg.beschreiben(MOBIL_6860, "mobilfunk", False, modell="FRITZ!Box 7530 AX")
    assert z.weg == "stick" and z.weg_text == "Mobilfunk-Stick (USB)"


def test_beschreiben_dsl_mit_ersatz():
    z = zg.beschreiben(VDSL_7590, "dsl", False, modell="FRITZ!Box 7590 AX")
    assert z.titel == "Internet über DSL" and z.weg_text == "eingebautes DSL-Modem"
    assert z.ersatz == "mobilfunk" and not z.ersatz_aktiv
    assert z.ersatz_text == "Mobilfunk an der FRITZ!Box, springt bei Ausfall ein"
    assert "DSL-Anschluss der Box: synchron" in z.belege
    aus = zg.beschreiben(VDSL_7590, "dsl", False, ersatz_wahl="kein", modell="FRITZ!Box 7590 AX")
    assert aus.ersatz == "" and aus.ersatz_text == ""
    aktiv = zg.beschreiben(VDSL_7590, "dsl", True, modell="FRITZ!Box 7590 AX")
    assert aktiv.ersatz_aktiv and aktiv.kopf.endswith("über Ersatz")
    assert any(b.startswith("Gerade aktiv: Ersatz") for b in aktiv.belege)


def test_beschreiben_glasfaser_und_kabel():
    g = zg.beschreiben(FASER_5590, "glasfaser", False, modell="FRITZ!Box 5590 Fiber")
    assert g.weg_text == "eingebautes Glasfaser-Modem (GPON)"
    assert "Glasfaser-Modul der Box: GPON" in g.belege
    k = zg.beschreiben(KABEL_6690, "kabel", False, modell="FRITZ!Box 6690 Cable")
    assert k.titel == "Internet über Kabel" and k.weg_text == "eingebautes Kabelmodem"


def test_beschreiben_vorgeschaltet_erkannt_und_festgelegt():
    z = zg.beschreiben(HINTER_ZTE, "extern", False, modell="FRITZ!Box 7530")
    assert z.titel == "Internet über ein vorgeschaltetes Gerät" and z.weg == "vorgeschaltet"
    assert z.adresse == "192.168.0.1" and z.weg_text == "vorgeschaltet über 192.168.0.1 · Beta"
    assert z.adressen == ("192.168.0.1", "192.168.1.1", "192.168.8.1")
    assert "Betriebsart der Box: IP-Client (hinter einem anderen Router)" in z.belege
    assert any("private Adresse" in b and "192.168.0.1" in b for b in z.belege)
    f = zg.beschreiben(HINTER_ZTE, "extern", False, "extern", "192.168.8.1")
    assert f.quelle == "festgelegt" and f.titel == "Internet über Mobilfunk"
    assert f.geraet == "vorgeschaltetes Modem" and f.adresse == "192.168.8.1"
    assert not f.abweichung


def test_festgelegt_anders_als_erkannt():
    z = zg.beschreiben(MOBIL_6860, "mobilfunk", False, "dsl", modell="FRITZ!Box 6860 5G")
    assert z.art == "dsl" and z.quelle == "festgelegt" and z.abweichung
    assert z.vorschlag == "Mobilfunk über FRITZ!Box 6860 5G"
    assert zg.wirksam("mobilfunk", "box_mobil") == "mobilfunk"
    assert zg.wirksam("dsl", "auto") == "dsl"


def test_unbekannt():
    z = zg.beschreiben(zg.Meldung(), "", False)
    assert z.art == "" and z.belege[0] == "FRITZ!Box meldet keine Zugangsart"
    assert z.titel == "Zugang nicht erkannt" and z.vorschlag == "unbekannt"


def test_englisch():
    z = zg.beschreiben(VDSL_7590, "dsl", True, modell="FRITZ!Box 7590 AX", s=ENG)
    assert z.titel == "Internet via DSL"
    assert z.belege[0] == "FRITZ!Box reports: internet via DSL, connected"
    assert z.ersatz_text == "mobile on the FRITZ!Box – active now"


def test_journal():
    assert zg.abgleich("", "mobilfunk", False, False) == []
    e = zg.abgleich("mobilfunk", "dsl", False, False)
    assert [x.art for x in e] == ["zugang"]
    assert e[0].text == "Internetzugang: jetzt DSL (vorher Mobilfunk)"
    assert [x.art for x in zg.abgleich("dsl", "dsl", False, True)] == ["ersatz_an"]
    assert [x.art for x in zg.abgleich("dsl", "dsl", True, False)] == ["ersatz_aus"]


def test_ersatz_zeiten():
    tag = 86_400.0
    jetzt = 100 * tag
    ab = jetzt - 30 * tag
    an = [ab - tag, ab + tag, ab + 5 * tag]
    aus = [ab - tag + 600, ab + tag + 1800]
    n, sek, letzte = zg.ersatz_zeiten(an, aus, ab, jetzt, aktiv=True)
    assert n == 2  # die vor dem Zeitraum zählt nicht
    assert sek == 1800 + 25 * tag  # zweite bis jetzt
    assert letzte == ab + 5 * tag
    n, sek, _ = zg.ersatz_zeiten(an[:2], aus, ab, jetzt, aktiv=False)
    assert (n, sek) == (1, 1800)
    assert zg.ersatz_zeiten([], [], ab, jetzt, False) == (0, 0.0, None)


def test_dsl_und_glasfaser_lesen():
    """Werte der Leitung nur, wenn das Internet darüber kommt – auch während eines Ausfalls (Gedächtnis)."""
    ungenutzt = zg.Meldung(zugangsart="X_AVM-DE_LTE", dsl_dienst=True, dsl_status="NoSignal")
    assert not zg.dsl_lesen(ungenutzt)
    assert zg.dsl_lesen(ungenutzt, "dsl"), "Ausfall: weiter lesen, damit „nicht synchron“ erscheint"
    assert zg.dsl_lesen(VDSL_7590) and not zg.dsl_lesen(MOBIL_6860, "dsl")
    assert zg.faser_lesen(FASER_5590) and not zg.faser_lesen(VDSL_7590)
    assert zg.faser_lesen(zg.Meldung(zugangsart="X_AVM-DE_LTE", faser_dienst=True), "glasfaser")


def test_ersatz_vergessen_schliesst_im_journal():
    e = zg.abgleich("dsl", "mobilfunk", True, False)
    assert [x.art for x in e] == ["zugang", "ersatz_aus"]
    assert e[1].text == "Ersatz beendet – Mobilfunk gilt jetzt als Zugang"


def test_6860_wie_gemessen_mobilfunk_mit_beleg():
    """Fehler in 0.26.0: X_AVM-DE_Mobile fehlte in der Tabelle → „Zugang nicht erkannt“, Mobilfunk-Ansicht leer."""
    assert zg.art_erkennen(MOBIL_6860) == ("mobilfunk", False)


@pytest.mark.parametrize("art", ["", "X_AVM-DE_Irgendwas"])
def test_unbekannte_zugangsart_mit_modem_an_ist_mobilfunk(art):
    m = zg.Meldung(zugangsart=art, mobil_dienst=True, mobil_an=True)
    assert zg.art_erkennen(m) == ("mobilfunk", False)


def test_unbekannte_zugangsart_mit_dsl_synchron_bleibt_unbekannt():
    m = zg.Meldung(
        zugangsart="X_AVM-DE_Irgendwas",
        mobil_dienst=True,
        mobil_an=True,
        dsl_dienst=True,
        dsl_status="Up",
    )
    assert zg.art_erkennen(m) == ("", False)
