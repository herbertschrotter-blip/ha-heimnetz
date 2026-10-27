"""Öffentlich auf GitHub melden (WU-0006): Felder des Issues, Datenschutz-Filter, Zell- und Signaldaten nur auf
Wunsch, Kürzen auf die Länge eines Links. Alle Adressen, Namen und Kennungen hier sind erfunden."""

from urllib.parse import parse_qs, urlsplit

import pytest
from logik import github as gh
from logik import mobil as mb
from logik import tickets as tk
from logik.sprache import ENG

BASIS = "https://github.com/beispiel/ha-heimnetz/issues/new"
UMGEBUNG = gh.Umgebung(
    heimnetz="0.23.0",
    ha="2026.10.2",
    kontext="Funk · Mobilfunk",
    geraet="Desktop",
    box_modell="FRITZ!Box 6860 5G",
    box_firmware="8.03",
    netz="LTE",
    ookla=True,
    ticket="FE-0003",
)


def _mobil(nr: bool = False) -> mb.Mobilfunk:
    anker = mb.Zelle("primary", "LTE", "", 312, "4f2a1-17", -97, -11, 1600, "23205", "7d0a")
    zelle_5g = mb.Zelle("secondary", "5G", "", 101, "", -90, -12)
    return mb.Mobilfunk(
        technik="LTE",
        roaming=False,
        haupt=anker,
        nr=zelle_5g if nr else None,
        zellen=(anker, zelle_5g) if nr else (anker,),
    )


def _abfrage(url: str) -> dict[str, str]:
    teile = urlsplit(url)
    return {k: v[0] for k, v in parse_qs(teile.query).items()}


def test_issue_wie_im_mockup():
    i = gh.issue(
        BASIS,
        "fehler",
        "Die Karte zum Mast bleibt grau, obwohl der Schlüssel eingetragen ist.",
        UMGEBUNG,
    )
    assert i.titel == "[Fehler] Die Karte zum Mast bleibt grau, obwohl der Schlüssel …"
    assert i.text == (
        "Die Karte zum Mast bleibt grau, obwohl der Schlüssel eingetragen ist.\n"
        "\n"
        "### Umgebung\n"
        "- Heimnetz 0.23.0 · Home Assistant 2026.10.2\n"
        "- Reiter: Funk · Mobilfunk · Desktop\n"
        "- FRITZ!Box 6860 5G · FRITZ!OS 8.03\n"
        "- Netz: LTE · Ookla Speedtest: ja\n"
        "- Lokales Ticket: FE-0003"
    )
    assert not i.gekuerzt
    assert i.url.startswith(BASIS + "?title=")
    assert _abfrage(i.url) == {"title": i.titel, "body": i.text}
    assert "Zell" not in i.text, "Zelldaten nur auf Wunsch"


def test_leere_werte_fallen_weg_ohne_einrichtung():
    u = gh.Umgebung(
        heimnetz="0.23.0", ha="2026.10.2", kontext="Übersicht", ookla=False, ticket="WU-0002"
    )
    i = gh.issue(BASIS, "wunsch", "Bitte eine Wochenansicht", u)
    assert i.titel == "[Wunsch] Bitte eine Wochenansicht"
    assert i.text.splitlines()[2:] == [
        "### Umgebung",
        "- Heimnetz 0.23.0 · Home Assistant 2026.10.2",
        "- Reiter: Übersicht",
        "- Ookla Speedtest: nein",
        "- Lokales Ticket: WU-0002",
    ]


def test_zell_und_signaldaten_nur_mit_schalter():
    z = gh.zelldaten(_mobil())
    assert z is not None
    i = gh.issue(BASIS, "fehler", "Empfang bricht ab", UMGEBUNG, z)
    assert i.text.endswith(
        "### Zell- und Signaldaten\n"
        "- Ankerzelle: 4f2a1-17 · PCI 312 · TAC 7D0A · PLMN 23205\n"
        "- RSRP -97 dBm · RSRQ -11 dB · 5G: aus\n"
        "- Entfernung laut Box: 1,6 km"
    )
    mit_5g = gh.zelldaten(_mobil(nr=True))
    assert "5G: RSRP -90 dBm" in gh.issue(BASIS, "fehler", "x", UMGEBUNG, mit_5g).text
    assert gh.zelldaten(None) is None
    assert gh.zelldaten(mb.Mobilfunk(technik="", roaming=False, haupt=None, nr=None)) is None


def test_schwaerzen_adressen_kennwoerter_orte_und_geraetenamen():
    text = (
        "Das Tablet-Wohnzimmer (aa:bb:cc:11:22:33, 192.0.2.17, fe80::1a2b) fällt um 14:05:33 aus. "
        "AA-BB-CC-DD-EE-FF ebenso. Kennwort: Sonne123!\nStandort 47.0707, 15.4395. Mein Laptop geht."
    )
    s = gh.schwaerzen(text, ["Tablet-Wohnzimmer", "laptop", "TV", ""])
    for weg in (
        "aa:bb",
        "192.0.2.17",
        "fe80",
        "AA-BB",
        "Sonne123",
        "47.0707",
        "15.4395",
        "Tablet-Wohnzimmer",
        "Laptop",
    ):
        assert weg not in s, weg
    assert "14:05:33" in s, "Uhrzeiten bleiben"
    assert "Kennwort: [entfernt]" in s
    assert s.count("[entfernt]") == 8
    # kurze Namen schwärzen nichts (sonst fiele „TV“ in jedem Wort weg), Teilwörter auch nicht
    assert gh.schwaerzen("TV und Laptops", ["TV", "Laptop"]) == "TV und Laptops"
    assert gh.schwaerzen("Version 0.23.0, 5 Geräte") == "Version 0.23.0, 5 Geräte"


def test_schwaerzen_kennwort_formen_und_eingebettete_ipv4():
    assert gh.schwaerzen("Passwort lautet: geheim123") == "Passwort lautet: [entfernt]"
    assert (
        gh.schwaerzen("WLAN-Kennwort ist Sommer 2026!, sonst nichts")
        == "WLAN-Kennwort ist [entfernt], sonst nichts"
    )
    assert gh.schwaerzen("token=abc def; weiter") == "token=[entfernt]; weiter"
    assert gh.schwaerzen("der Schlüssel ist eingetragen") == "der Schlüssel ist eingetragen", (
        "kein Kennwort"
    )
    s = gh.schwaerzen("Adresse ::ffff:192.168.178.1 und 2001:db8::7")
    assert "192" not in s and "168" not in s and "db8" not in s and "ffff" not in s, s


def test_issue_schwaerzt_text_und_reiter():
    u = gh.Umgebung(heimnetz="0.23.0", ha="2026.10.2", kontext="Geräte · Dialog „Wohnzimmer-PC“")
    i = gh.issue(BASIS, "fehler", "Wohnzimmer-PC hat 10.0.0.5 doppelt", u, namen=["Wohnzimmer-PC"])
    assert "Wohnzimmer-PC" not in i.titel + i.text + i.url
    assert "10.0.0.5" not in i.text
    assert i.titel == "[Fehler] [entfernt] hat [entfernt] doppelt"


def test_langer_text_wird_gekuerzt_bis_der_link_passt():
    lang = "Umlaute äöü und Leerzeichen " * 600
    i = gh.issue(BASIS, "anregung", lang, UMGEBUNG)
    assert i.gekuerzt
    assert len(i.url) <= gh.URL_MAX
    assert len(i.url) > gh.URL_MAX - 200, "nicht unnötig viel weggeschnitten"
    assert "… (gekürzt – der ganze Text steht im lokalen Ticket FE-0003)" in i.text
    assert i.text.endswith("- Lokales Ticket: FE-0003"), "die Umgebung bleibt ganz"
    assert _abfrage(i.url)["body"] == i.text
    assert len(i.titel) < 80


def test_englisch():
    z = gh.zelldaten(_mobil(), ENG)
    i = gh.issue(BASIS, "fehler", "Map stays grey", UMGEBUNG, z, sprache=ENG)
    assert i.titel == "[Bug] Map stays grey"
    assert "### Environment" in i.text and "- Tab: Funk · Mobilfunk · Desktop" in i.text
    assert "- Network: LTE · Ookla Speedtest: yes" in i.text and "- Local ticket: FE-0003" in i.text
    assert "### Cell and signal data" in i.text and "5G: off" in i.text
    assert "- Distance reported by the box: 1.6 km" in i.text
    assert gh.schwaerzen("pw=geheim", sprache=ENG) == "pw=[removed]"


def test_naechste_nummer_zaehlt_nicht_hoch():
    nummern = {"FE": 2}
    assert tk.naechste_nummer(nummern, "fehler") == "FE-0003"
    assert tk.naechste_nummer(nummern, "anregung") == "AN-0001"
    assert nummern == {"FE": 2}
    assert tk.neue_nummer(nummern, "fehler") == "FE-0003" and nummern == {"FE": 3}


def test_zellkennungen_im_text_auch_ohne_schalter_geschwaerzt():
    m = _mobil()
    i = gh.issue(
        BASIS,
        "fehler",
        "Zelle 4f2a1-17 springt auf aaaaa-64, TAC 1A2B PCI 211; Anlage 4f2a1 und Bereich 7d0a",
        UMGEBUNG,
        None,
        gh.zell_kennungen(m),
    )
    for weg in ("4f2a1", "aaaaa-64", "1A2B", "211", "7d0a"):
        assert weg not in i.text and weg not in i.url, weg
    assert "TAC [entfernt] PCI [entfernt]" in i.text
    assert "Zell- und Signaldaten" not in i.text
    assert gh.zell_kennungen(None) == []
    assert gh.zell_kennungen(m) == ["4f2a1-17", "4f2a1", "7d0a"]
    # Versionen, Uhrzeiten und Daten bleiben
    assert gh.schwaerzen("0.23.0 um 14:05 am 2026-10-25") == "0.23.0 um 14:05 am 2026-10-25"


def test_koordinaten_in_kartenlinks_geschwaerzt():
    for text in (
        "https://www.openstreetmap.org/?mlat=47.07071&mlon=15.43952#map=17/47.07071/15.43952",
        "lat=47.0707&lon=15.4395",
        "latitude: 47.0707, longitude: 15.4395",
    ):
        s = gh.schwaerzen(text)
        assert "47.07" not in s and "15.43" not in s, s
    assert gh.schwaerzen("lat=47.0707") == "lat=[entfernt]"


def test_geraet_nur_bekannte_werte():
    for wert, erwartet in (("Desktop", "Desktop"), ("Handy", "Handy"), ("Phone", "Phone")):
        u = gh.Umgebung(heimnetz="0.23.0", ha="2026.10.2", kontext="Übersicht", geraet=wert)
        assert f"Übersicht · {erwartet}" in gh.issue(BASIS, "fehler", "x", u).text
    u = gh.Umgebung(heimnetz="0.23.0", ha="2026.10.2", kontext="Übersicht", geraet="Tablet-Küche")
    i = gh.issue(BASIS, "fehler", "x", u)
    assert "Tablet" not in i.text and "- Reiter: Übersicht\n" in i.text + "\n"


@pytest.mark.parametrize(
    "roh",
    ["cell id: 123456789", "ECI 268435455", "NCI=68719476735", "eNB 0x1dad8", "Cell-ID: 1A2B3C4D5"],
)
def test_lange_zellkennungen_geschwaerzt(roh):
    """FE-0006: Kennungen mit mehr als 8 Stellen (ECI/NCI dezimal) blieben im öffentlichen Issue stehen."""
    aus = gh.schwaerzen(roh)
    assert "[entfernt]" in aus
    assert not any(
        z in aus for z in ("123456789", "268435455", "68719476735", "1dad8", "1A2B3C4D5")
    )


@pytest.mark.parametrize("roh", ["PCI face", "die tac bad", "cid cafe"])
def test_woerter_nach_tac_pci_bleiben(roh):
    """FE-0006: Wörter aus a–f nach TAC/PCI/CID sind keine Kennung."""
    assert gh.schwaerzen(roh) == roh
