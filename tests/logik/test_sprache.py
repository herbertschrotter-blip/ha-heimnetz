"""Sprache der Texte aus der Integration (WU-0006): Deutsch oder Englisch nach Home Assistant; jeder Text hat eine
englische Zeile mit denselben Platzhaltern, und die Fachlogik liefert in beiden Sprachen."""

import ast
import re
from datetime import UTC, date
from pathlib import Path

import pytest
from logik import auswertung as aw
from logik import befunde as bf
from logik import geraete as gr
from logik import karte as ka
from logik import kontext as kx
from logik import messplan as mp
from logik import mobil as mb
from logik import sammeln as sm
from logik import stoerung as sg
from logik import tickets as tk
from logik import wlan as wl
from logik.arten import bestimmen, gruppen, kategorien
from logik.einstellungen import Ungueltig
from logik.einstellungen import pruefen as einstellungen_pruefen
from logik.englisch import EN
from logik.sprache import DE, ENG, merke, t, waehle, zahl

QUELLE = Path(__file__).resolve().parents[2] / "custom_components" / "heimnetz"
# Aufrufe, deren Text (erstes bzw. zweites Argument) übersetzt wird
ERSTES = {"t", "tr", "merke", "Ungueltig"}
ZWEITES = {"_tr"}
PLATZHALTER = re.compile(r"\{(\w+)\}")


def _texte(knoten: ast.expr) -> list[str]:
    """Feste Texte eines Arguments – auch beide Zweige von `"a" if x else "b"`."""
    if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str):
        return [knoten.value]
    if isinstance(knoten, ast.IfExp):
        return _texte(knoten.body) + _texte(knoten.orelse)
    return []


def schluessel() -> dict[str, str]:
    """Alle Texte der Integration, die über t(), merke() oder Ungueltig() laufen → Datei."""
    gefunden: dict[str, str] = {}
    for datei in sorted(QUELLE.rglob("*.py")):
        if datei.name == "englisch.py":
            continue
        for k in ast.walk(ast.parse(datei.read_text(encoding="utf-8"))):
            if not isinstance(k, ast.Call):
                continue
            name = (
                k.func.id
                if isinstance(k.func, ast.Name)
                else k.func.attr
                if isinstance(k.func, ast.Attribute)
                else ""
            )
            stelle = 0 if name in ERSTES else 1 if name in ZWEITES else None
            if stelle is None or len(k.args) <= stelle:
                continue
            for text in _texte(k.args[stelle]):
                gefunden.setdefault(text, datei.name)
    return gefunden


def _platzhalter(s: str) -> list[str]:
    return sorted(PLATZHALTER.findall(s))


def test_jeder_text_hat_eine_englische_zeile_mit_denselben_platzhaltern():
    k = schluessel()
    assert len(k) > 150, f"nur {len(k)} Texte gefunden – Suche kaputt?"
    fehlt = [f"{d}: {s}" for s, d in k.items() if s not in EN]
    assert not fehlt, "ohne englische Zeile:\n" + "\n".join(fehlt)
    anders = [s for s in k if _platzhalter(s) != _platzhalter(EN[s])]
    assert not anders, f"Platzhalter weichen ab: {anders}"


def test_keine_englische_zeile_ist_uebrig():
    uebrig = sorted(set(EN) - set(schluessel()))
    assert not uebrig, f"englische Zeilen ohne Text in der Integration: {uebrig}"


def test_sprachwahl_zahlen_und_platzhalter():
    assert [waehle(x) for x in ("de", "de-AT", "de_CH", "DE", "en", "en-GB", "fr", "", None)] == [
        DE,
        DE,
        DE,
        DE,
        ENG,
        ENG,
        ENG,
        ENG,
        ENG,
    ]
    assert (zahl(1234.5, 1, DE), zahl(1234.5, 1, ENG), zahl(1.44, 1, DE)) == (
        "1.234,5",
        "1,234.5",
        "1,4",
    )
    # gemerkter Text als Wert wird mitübersetzt, anderer Text nicht (Gerätenamen bleiben, wie sie sind)
    assert (
        t("{name}: keine Zahl", ENG, name=merke("Tarif Download")) == "Plan download: not a number"
    )
    assert t("{name}: keine Zahl", ENG, name="Tarif Download") == "Tarif Download: not a number"
    assert t("unbekannter Text", ENG) == "unbekannter Text"


def test_ungueltig_deutsch_im_protokoll_englisch_fuer_die_seite():
    with pytest.raises(Ungueltig) as err:
        einstellungen_pruefen({"tarif_down": "x"}, date(2026, 10, 25))
    assert str(err.value) == "Tarif Download: keine Zahl"
    assert err.value.text(ENG) == "Plan download: not a number"
    with pytest.raises(Ungueltig) as err:
        mp.pruefen({"von": "25:00"})
    assert err.value.text(ENG) == "Only between (from): time between 00:00 and 24:00"
    with pytest.raises(tk.Ungueltig) as err:
        tk.meldung_pruefen({"art": "fehler", "text": " "})
    assert err.value.text(ENG) == "text: please describe briefly"
    assert (
        tk.bild_erlaubt({"bilder": ["a", "b", "c"]}, 1000, 900, ENG)
        == "at most 3 images per report"
    )
    assert (tk.status_text("in_arbeit", ENG), tk.art_text("anregung", ENG)) == (
        "in progress",
        "Suggestion",
    )


def test_befunde_und_journal_auf_englisch():
    pi = bf.PiVerbindung(box=True, internet=False, dns=True)
    b = bf.finden({}, bf.Heimnetz(), None, pi, "neu", ENG)
    assert (b[0].titel, b[0].text) == (
        "No internet connection",
        "The FRITZ!Box is reachable and is reconnecting to the mobile network.",
    )
    assert bf.finden({}, bf.Heimnetz(), None, pi, "neu")[0].titel == "Keine Internetverbindung"
    ereignisse, gemerkt = bf.abgleich({"alt": "Alter Titel"}, b, ENG)
    assert [e.text for e in ereignisse] == [
        "Finding: No internet connection – The FRITZ!Box is reachable and is reconnecting to the mobile "
        "network.",
        "Finding resolved: Alter Titel",  # gemerkter Titel bleibt in seiner Sprache
    ]
    assert bf.dhcp_pruefung(bf.DhcpTest(True, ()), "", ENG) == (False, "no server answers")


def test_mobilfunk_auf_englisch():
    assert (mb.dauer(3720, ENG), mb.dauer(86_400, ENG), mb.dauer(2 * 86_400, ENG)) == (
        "1 h 2 min",
        "1 day 0 h",
        "2 days 0 h",
    )
    assert (mb.entfernung(1240, ENG), mb.entfernung(1240)) == ("1.2 km", "1,2 km")
    assert (mb.wort_rsrp(-90, ENG), mb.wort_rsrq(-18, ENG)) == ("good", "weak")
    b = mb.befund("LTE", -110, None, 12.34, 50, ENG)
    assert b.titel == "Weak reception – improve the box’s location first"
    assert b.text.startswith(
        "Signal strength -110 dBm (4G anchor). Download over the last 7 days is typically 12.3 Mbit/s = 25 % of "
        "the plan. At the moment the connection runs over LTE only. With reception this weak"
    )
    anker = mb.Zelle("primary", "LTE", "A1", 1, "aaaaa-64", -90, -10)
    dazu = mb.Zelle("secondary", "5G", "A1", 121, "", -95, -11)
    nachbar = mb.Zelle("", "LTE", "A1", 2, "aaaaa-65", -100, -12)
    assert [mb.rolle_art(z, "5G NSA") for z in (anker, dazu, nachbar)] == [
        "anker",
        "dazu",
        "reichweite",
    ]
    assert mb.rolle_art(anker, "LTE") == "verbunden"
    assert [mb.rolle(z, "5G NSA", ENG) for z in (anker, dazu, nachbar)] == [
        "anchor",
        "aggregated",
        "in range",
    ]
    alt = mb.Mobilfunk("LTE", False, nachbar, None, zellen=(nachbar,))
    neu = mb.Mobilfunk("5G NSA", False, anker, dazu, zellen=(anker, dazu))
    texte = [e.text for e in mb.abgleich(alt.technik, alt.zellkennung, neu, ENG)]
    assert texte == [
        "Mobile: technology changed LTE → 5G NSA",
        "Mobile: cell changed aaaaa-65/2 → aaaaa-64/1 (reception RSRP -90 dBm)",
    ]
    # das Nachtragen der Momentaufnahme liest die Ankerzelle aus deutschen wie englischen Einträgen
    assert kx.zelle_bei([(10.0, texte[1])], 20.0) == "aaaaa-64"
    assert (
        kx.zelle_bei([(10.0, "Mobilfunk: Funkzelle gewechselt a-1/2 → b-2/3 (…)")], 20.0) == "b-2"
    )


def test_karte_geraete_und_stoerung_auf_englisch():
    wohnung, mast = ka.Ort(47.0, 15.0), ka.Ort(46.987, 15.0)
    assert (ka.richtung(wohnung, mast, ENG), ka.richtung(wohnung, mast)) == ("south", "Süd")
    assert ka.strecke(1445, ENG) == "1.4 km"
    pci = mb.Zelle("secondary", "5G", "A1", 121, "", -95, -11)
    assert ka.such_text(pci, None, ENG) == "PCI only – cannot be looked up"

    alt = {"AA": gr.Geraet("AA", "192.168.1.2", True, "Pi", "LAN")}
    neu = {"AA": gr.Geraet("AA", "192.168.1.3", False, "Pi", "LAN")}
    assert [e.text for e in gr.abgleich(alt, neu, ENG)] == [
        "Pi: IP address changed 192.168.1.2 → 192.168.1.3",
        "Pi is offline (192.168.1.3, LAN)",
    ]
    ohne = gr.aus_hostliste(
        "<List><Item><MACAddress>02:00:00:00:00:09</MACAddress><IPAddress>192.168.1.9</IPAddress>"
        "<Active>1</Active><InterfaceType>Ethernet</InterfaceType></Item></List>"
    )
    assert [e.text for e in gr.abgleich({}, ohne, ENG)][0].startswith(
        "New device: Device without name, IP"
    )
    assert (gr.anzeigename(gr.OHNE_NAMEN, ENG), gr.anzeigename("Pi", ENG)) == (
        "Device without name",
        "Pi",
    )
    gruppen_ = gr.gruppen([(gr.NICHT_VERBUNDEN, False), ("WLAN 2,4 GHz", True)], ENG)
    assert [(g["name"], g["text"]) for g in gruppen_] == [
        ("WLAN 2,4 GHz", "WLAN 2.4 GHz"),
        ("WLAN, nicht verbunden", "WLAN, not connected"),  # Kennung bleibt deutsch, Text englisch
    ]
    assert gruppen([("netz", True)], ENG)[0]["text"] == "🛜 Network"
    assert kategorien(ENG)[0] == {"name": "netz", "text": "🛜 Network"}
    assert (
        bestimmen("Wohnzimmer", "02:00:00:00:00:01", selbst="medien", sprache=ENG).quelle
        == "chosen by you"
    )
    assert wl.band_text("2,4", ENG) == "2.4"
    kanal, _ = wl.abgleich({"2,4": 1}, [wl.Band("2,4", True, 6, False, "ax")], ENG)
    assert [e.text for e in kanal] == ["WLAN 2.4 GHz: channel 1 → 6"]

    st = sg.Stoerung(von=0.0, weg_seit=None, bis=600.0, anzahl=2, weg_s=120.0, lagen=["neu"])
    assert sg.text(st, ENG) == (
        "Internet outage over: 2 interruptions in 10 min, down for 2 min in total – the box reconnected to the "
        "mobile network"
    )


def test_abruf_schreibt_journal_in_der_sprache_von_home_assistant():
    g = sm.Gedaechtnis()
    pi = bf.PiVerbindung(box=True, internet=True, dns=True)
    geraete = {"AA": gr.Geraet("AA", "192.168.1.2", True, "Pi", "LAN")}
    stand = sm.auswerten(g, sm.Rohdaten(jetzt=1000.0, pi=pi, geraete=geraete, sprache=ENG))
    assert [e.text for e in stand.ereignisse] == ["Recording started: 1 devices known, 1 online"]
    stand = sm.auswerten(
        g,
        sm.Rohdaten(
            jetzt=1060.0, pi=bf.PiVerbindung(box=True, internet=True, dns=False), geraete=geraete
        ),
    )
    assert [e.text for e in stand.ereignisse] == ["Namensauflösung am Pi: NICHT erreichbar"]


def test_tickets_und_auswertung_auf_englisch():
    m = tk.fuer_seite({"art": "wunsch", "status": "in_arbeit"}, ENG)
    assert (m["art_text"], m["status_text"]) == ("Wish", "in progress")
    assert tk.fuer_seite({"art": "wunsch", "status": "geloest"})["status_text"] == "gelöst"
    g = aw.GROESSEN["down"]
    zellen = [[[] for _ in range(24)] for _ in range(7)]
    for wd in range(5):
        for h in range(18, 23):
            zellen[wd][h] = [(20.0, 1.0)]
    for wd in range(7):
        for h in range(7):
            zellen[wd][h] = [(100.0, 1.0)]
    text = aw._auffaellig(g, zellen, 150.0, ENG)
    assert text and text.startswith(
        "Mon–Fri 18–22 h the Download is typically 20 Mbit/s (13 % of the plan), at night 100 Mbit/s (67 % of "
        "the plan)."
    )
    grund = mp.entscheiden(
        mp.Messplan(), None, 0.0, UTC, None, 10.0
    ).grund  # Plan aus: nicht fällig
    assert (grund, t(grund, ENG)) == ("nicht fällig", "not due")
