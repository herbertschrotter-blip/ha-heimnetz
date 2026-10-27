"""Werte der Leitung (WU-0009): DSL und Glasfaser aus TR-064, bewertet.

Erfundene, aber realistische Werte in der Form der FRITZ!-Doku: DSL-Raten in kbit/s, Störabstandsmarge und Dämpfung
in 0,1 dB (WANDSLInterfaceConfig GetInfo), Lichtleistung und Schwellen in dBm/1000 (X_AVM-DE_WANFiber GetInfo).
Typisch: VDSL2 17a/35b mit 100–250 Mbit/s, Marge 6–12 dB; GPON empfängt zwischen −8 und −28 dBm.
"""

import pytest
from logik import leitung as ln
from logik.sprache import ENG

VDSL = ln.Dsl(
    t=1000.0,
    status="Up",
    sync_down=108_396,
    sync_up=38_189,
    max_down=124_620,
    max_up=41_012,
    marge_down=52,
    marge_up=79,
    daempfung_down=140,
    daempfung_up=90,
    modulation="VDSL",
    profil="35b",
    crc=120,
    fec=18_400,
)
GPON = ln.Faser(
    t=1000.0,
    modus="GPON",
    rx=-19_400,
    rx_min=-28_000,
    rx_max=-8_000,
    tx=2_100,
    tx_min=500,
    tx_max=5_000,
    fehler_rx=0,
    fehler_tx=0,
    resyncs=1,
    minuten=30_240,
)


def test_einheiten():
    assert ln.mbit(108_396) == 108.4
    assert ln.db(52) == 5.2
    assert ln.dbm(-19_400) == -19.4
    assert ln.mbit(None) is None and ln.db(None) is None and ln.dbm(None) is None
    assert ln.anteil(108_396, 124_620) == 87
    assert ln.anteil(0, 124_620) is None and ln.anteil(10, None) is None


def test_fehler_je_stunde_und_neusync():
    spaeter = ln.Dsl(**{**VDSL.__dict__, "t": 1600.0, "crc": 122, "fec": 18_584})
    assert ln.dsl_fehler_je_stunde(VDSL, spaeter) == (12.0, 1104.0)
    assert ln.dsl_fehler_je_stunde(None, spaeter) == (None, None)
    assert not ln.dsl_neu_synchron(VDSL, spaeter)
    # Zähler fangen neu an: neu synchronisiert, keine Rate
    neu = ln.Dsl(**{**VDSL.__dict__, "t": 1600.0, "crc": 0, "fec": 3})
    assert ln.dsl_neu_synchron(VDSL, neu)
    assert ln.dsl_fehler_je_stunde(VDSL, neu) == (None, None)
    # nach einem Ausfall wieder „Up“
    weg = ln.Dsl(t=1300.0, status="NoSignal")
    assert ln.dsl_neu_synchron(weg, spaeter)
    assert not ln.dsl_neu_synchron(VDSL, weg)
    assert not ln.dsl_neu_synchron(None, VDSL)
    # weniger als eine Minute dazwischen: keine Rate
    knapp = ln.Dsl(**{**VDSL.__dict__, "t": 1030.0, "crc": 125})
    assert ln.dsl_fehler_je_stunde(VDSL, knapp) == (None, None)


def test_neusync_fortschreiben():
    tag = 86_400.0
    liste = ln.neusync_fortschreiben([1.0, 6 * tag], True, 8 * tag)
    assert liste == [6 * tag, 8 * tag]
    assert ln.neusync_fortschreiben(liste, False, 20 * tag) == []


def test_dsl_reserve_knapp():
    b = ln.dsl_bewerten(VDSL, 12.0, 2)
    assert (b.stufe, b.titel, b.abzeichen) == (
        "knapp",
        "Leitung stabil, aber wenig Reserve",
        "Reserve knapp",
    )
    assert "Die Störabstandsmarge im Download liegt bei 5,2 dB (gut ab 6 dB)." in b.text
    assert "87 % der möglichen Geschwindigkeit" in b.text
    assert "2 Neusynchronisierungen in 7 Tagen." in b.text
    assert "Telefondose" in b.text


@pytest.mark.parametrize(
    ("aenderung", "crc_h", "neusync", "stufe", "abzeichen"),
    [
        ({"marge_down": 95}, 2.0, 0, "gut", "gut"),
        ({"marge_down": 95}, None, 1, "gut", "gut"),
        ({"marge_down": 25}, 2.0, 0, "schlecht", "instabil"),
        ({"marge_down": 95}, 40.0, 0, "knapp", "auffällig"),
        ({"marge_down": 95}, 500.0, 0, "schlecht", "instabil"),
        ({"marge_down": 95}, 2.0, 5, "schlecht", "instabil"),
        ({"marge_down": 95, "marge_up": 40}, 2.0, 0, "knapp", "Reserve knapp"),
        ({"marge_down": None, "marge_up": None}, None, 0, "gut", "gut"),
    ],
)
def test_dsl_bewerten(aenderung, crc_h, neusync, stufe, abzeichen):
    b = ln.dsl_bewerten(ln.Dsl(**{**VDSL.__dict__, **aenderung}), crc_h, neusync)
    assert (b.stufe, b.abzeichen) == (stufe, abzeichen)


def test_dsl_nicht_synchron():
    b = ln.dsl_bewerten(ln.Dsl(t=1.0, status="NoSignal"), None, 0)
    assert (b.stufe, b.titel, b.abzeichen) == ("schlecht", "DSL nicht synchron", "getrennt")
    assert "NoSignal" in b.text


def test_marge_stufe():
    assert ln.marge_stufe(VDSL) == "knapp"
    assert ln.marge_stufe(ln.Dsl(t=1.0)) == ""


def test_faser_gut():
    b = ln.faser_bewerten(GPON)
    assert (b.stufe, b.titel, b.abzeichen) == ("gut", "Glasfaser in Ordnung", "gut")
    assert b.text.startswith("Das Licht kommt mit −19,4 dBm an".replace("−", "-"))
    assert "(gut zwischen -8,0 und -28,0 dBm laut Box)" in b.text
    assert "Seit 21 Tage 0 h ohne Unterbrechung." in b.text
    assert ln.licht_bereich(GPON) == (-28.0, -8.0)
    assert ln.sende_bereich(GPON) == (0.5, 5.0)


@pytest.mark.parametrize(
    ("rx", "stufe"),
    [(-26_500, "knapp"), (-29_000, "schlecht"), (-7_000, "schlecht"), (-12_000, "gut")],
)
def test_faser_stufen(rx, stufe):
    assert ln.faser_bewerten(ln.Faser(**{**GPON.__dict__, "rx": rx})).stufe == stufe


def test_faser_ohne_schwellen():
    f = ln.Faser(t=1.0, rx=-20_000, rx_min=0, rx_max=0)
    b = ln.faser_bewerten(f)
    assert (b.stufe, b.titel) == ("", "Glasfaser verbunden")
    assert ln.licht_bereich(f) is None
    assert b.text == "Das Licht kommt mit -20,0 dBm an."


def test_faser_fehler_je_stunde():
    spaeter = ln.Faser(**{**GPON.__dict__, "t": 4600.0, "fehler_rx": 3})
    assert ln.faser_fehler_je_stunde(GPON, spaeter) == 3.0
    assert ln.faser_fehler_je_stunde(None, spaeter) is None


def test_dauer():
    assert ln.dauer(30) == "0 min"
    assert ln.dauer(3 * 3600 + 120) == "3 h 2 min"
    assert ln.dauer(86_400 + 3600) == "1 Tag 1 h"
    assert ln.dauer(3 * 86_400) == "3 Tage 0 h"
    assert ln.dauer(3 * 86_400, ENG) == "3 days 0 h"


def test_englisch():
    b = ln.dsl_bewerten(VDSL, 12.0, 1, ENG)
    assert b.titel == "Line stable, but little headroom"
    assert "1 resync in 7 days." in b.text
    assert "The noise margin in the download is 5.2 dB (good from 6 dB)." in b.text
