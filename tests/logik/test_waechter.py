"""Wächter (Herbert, 18.11.2026): Regeln prüfen, Regeln je Steckdose, Stücke des Skripts, Anmeldung, Zustand der
Steckdose, Eingriffe als Text, Stufe 1 (sanft neu starten)."""

from __future__ import annotations

from pathlib import Path

import pytest
from logik import waechter as wa
from logik.sprache import DE, ENG, Ungueltig

SKRIPT = Path(__file__).parents[2] / "custom_components/heimnetz/shelly/waechter.js"

KETTE = {
    "art": "internet",
    "glieder": [
        {
            "typ": "zte_goform",
            "name": "ZTE MC888",
            "adresse": "192.168.0.1",
            "dose": "192.168.178.41",
        },
        {
            "typ": "fritzbox",
            "name": "FRITZ!Box 7530",
            "adresse": "192.168.178.1",
            "dose": "192.168.178.42",
        },
    ],
}


def test_internet_kette_mit_vorgaben():
    w = wa.pruefen(KETTE)
    assert w.art == "internet" and len(w.glieder) == 2 and w.an
    assert w.regeln.stufe1_min == 5 and w.regeln.stufe2_min == 12 and w.regeln.aus_s == 30
    assert [g.sanft for g in w.glieder] == [True, True]
    assert w.dosen == [(0, "192.168.178.41"), (1, "192.168.178.42")]


def test_ha_vorgaben_und_port():
    w = wa.pruefen(
        {
            "art": "ha",
            "glieder": [{"typ": "ha", "adresse": "192.168.178.60:8123", "dose": "192.168.178.43"}],
        }
    )
    assert w.regeln.stufe2_min == 20 and w.regeln.abstand_min == 120 and w.regeln.pruef_s == 120
    assert not w.glieder[0].sanft


@pytest.mark.parametrize(
    ("daten", "text"),
    [
        ({"art": "x"}, "Art des Wächters"),
        ({"art": "internet", "glieder": []}, "Geräte des Wächters fehlen"),
        ({"art": "ha", "glieder": [{"adresse": "192.168.178.60:8123"}]}, "Ohne Steckdose"),
        (
            {"art": "geraet", "glieder": [{"adresse": "8.8.8.8", "dose": "192.168.178.43"}]},
            "private Adresse",
        ),
        (
            {"art": "geraet", "glieder": [{"adresse": "192.168.178.9", "dose": "shelly.local"}]},
            "private Adresse",
        ),
        ({**KETTE, "regeln": {"stufe1_min": 12, "stufe2_min": 12}}, "erst nach dem sanften"),
        ({**KETTE, "regeln": {"aus_s": 1}}, "zwischen 5 und 300"),
        ({**KETTE, "regeln": {"pruef_s": 45}}, "30, 60 oder 120"),
        (
            {
                "art": "internet",
                "glieder": [
                    {**KETTE["glieder"][0], "dose": "192.168.178.9"},
                    {**KETTE["glieder"][1], "dose": "192.168.178.9"},
                ],
            },
            "nur ein Gerät",
        ),
        (
            {"art": "internet", "glieder": [{"typ": "andere", "adresse": "192.168.0.1"}]},
            "Ohne Steckdose",
        ),
    ],
)
def test_ungueltig(daten, text):
    with pytest.raises(Ungueltig, match=text):
        wa.pruefen(daten)


def test_ohne_steckdose_aber_sanft_geht():
    w = wa.pruefen(
        {"art": "internet", "glieder": [{"typ": "fritzbox", "adresse": "192.168.178.1"}]}
    )
    assert w.dosen == []


def test_gespeichert_rund_und_ungueltiges_faellt_weg():
    w = wa.pruefen({**KETTE, "id": "w1"})
    assert wa.pruefen(w.als_dict()) == w
    assert wa.alle_pruefen([w.als_dict(), {"art": "x"}]) == [w]
    assert wa.neue_id([w]) == "w2"


def test_doppelte_steckdose_ueber_waechter():
    a = wa.pruefen({**KETTE, "id": "w1"})
    b = wa.pruefen(
        {
            "id": "w2",
            "art": "geraet",
            "glieder": [{"adresse": "192.168.178.9", "dose": "192.168.178.42"}],
        }
    )
    assert wa.doppelte_dose(b, [a]) == "192.168.178.42"
    assert wa.doppelte_dose(a, [a]) is None


def test_kvs_kette_modem_und_router():
    w = wa.pruefen(KETTE)
    modem, router = wa.kvs(w, 0, "192.168.178.1"), wa.kvs(w, 1, "192.168.178.1")
    assert modem["rolle"] == "kette" and modem["pos"] == 0 and modem["anzahl"] == 2
    assert modem["eigen"] == "http://192.168.0.1" and modem["nach"] == "http://192.168.178.1"
    assert "vor" not in modem and "partner" not in modem
    assert router["vor"] == "http://192.168.0.1" and router["partner"] == "192.168.178.41"
    assert router["ziele"] == list(wa.ZIELE) and router["stufe2_min"] == 12


def test_kvs_ha_prueft_das_heimnetz_ueber_den_router():
    w = wa.pruefen(
        {
            "art": "ha",
            "glieder": [{"typ": "ha", "adresse": "192.168.178.60:8123", "dose": "192.168.178.43"}],
        }
    )
    d = wa.kvs(w, 0, "192.168.178.1")
    assert (
        d["rolle"] == "ha"
        and d["eigen"] == "http://192.168.178.60:8123"
        and d["netz"] == "http://192.168.178.1"
    )
    assert d["ziele"] == []


def test_stuecke_an_zeilengrenzen_und_ganz():
    code = SKRIPT.read_text()
    st = wa.stuecke(code)
    assert "".join(st) == code
    assert all(len(s.encode()) <= wa.STUECK_BYTES for s in st)
    assert all(s.endswith("\n") for s in st)


def test_version_im_skript_passt():
    assert wa.skript_version(SKRIPT.read_text()) == wa.SKRIPT_VERSION


def test_anmeldung_nach_shelly_beschreibung():
    a = wa.anmeldung("geheim", "shellyplusplugs-abc", 1700000000, "x1")
    assert a["username"] == "admin" and a["algorithm"] == "SHA-256" and len(a["response"]) == 64
    assert a == wa.anmeldung("geheim", "shellyplusplugs-abc", 1700000000, "x1")
    assert (
        a["response"] != wa.anmeldung("anders", "shellyplusplugs-abc", 1700000000, "x1")["response"]
    )


def test_dosenstand_und_veraltet():
    d = wa.dosenstand(
        {"wv": 1, "zustand": "bereit", "eingriffe": 2, "letzte": [{"t": 1, "was": "start"}]}, 9.5
    )
    assert d.erreichbar and d.eingriffe == 2 and not d.veraltet and d.leistung == 9.5
    assert wa.dosenstand({"wv": 0, "zustand": "bereit"}).veraltet
    assert wa.dosenstand(None).fehlt


def test_neue_eingriffe_und_text():
    w = wa.pruefen(KETTE)
    alt = ({"t": 1, "was": "start"},)
    neu = (*alt, {"t": 5, "was": "strom", "grund": "inet_weg"}, {"t": 9, "was": "ok"})
    e = wa.neue_eingriffe(alt, neu)
    assert [x["was"] for x in e] == ["strom", "ok"]
    assert (
        wa.eingriff_text(e[0], w.glieder[1], w)
        == "FRITZ!Box 7530: Strom 30 s aus und wieder ein – kein Internet"
    )
    assert (
        wa.eingriff_text(e[0], w.glieder[1], w, ENG)
        == "FRITZ!Box 7530: power off for 30 s and back on – no internet"
    )
    assert wa.eingriff_text({"was": "pause", "grund": "3"}, w.glieder[0], w).startswith(
        "ZTE MC888: 3 Eingriffe"
    )


def test_stufe1_erst_modem_dann_router_je_einmal():
    w = wa.pruefen(KETTE)
    s = wa.Sanft()
    s, i = wa.sanft_entscheiden(w, s, 0, False, {})
    assert i is None and s.weg_seit == 0
    s, i = wa.sanft_entscheiden(w, s, 4 * 60, False, {})
    assert i is None
    s, i = wa.sanft_entscheiden(w, s, 5 * 60, False, {})
    assert i == 0, "zuerst das Modem"
    s, i = wa.sanft_entscheiden(w, s, 8 * 60, False, {})
    assert i is None, "dem Modem Zeit lassen"
    s, i = wa.sanft_entscheiden(w, s, 10 * 60, False, {})
    assert i == 1, "dann der Router"
    s, i = wa.sanft_entscheiden(w, s, 30 * 60, False, {})
    assert i is None, "jedes Gerät nur einmal je Störung"
    s, i = wa.sanft_entscheiden(w, s, 31 * 60, True, {})
    assert i is None and s.weg_seit is None and s.gemacht == {}


def test_stufe1_ueberspringt_geraete_die_nicht_antworten():
    w = wa.pruefen(KETTE)
    s, _ = wa.sanft_entscheiden(w, wa.Sanft(), 0, False, {})
    s, i = wa.sanft_entscheiden(w, s, 5 * 60, False, {0: False})
    assert i == 1


def test_stufe1_nur_internet_und_nicht_bei_unbekannt():
    ha = wa.pruefen(
        {
            "art": "ha",
            "glieder": [{"typ": "ha", "adresse": "192.168.178.60:8123", "dose": "192.168.178.43"}],
        }
    )
    assert wa.sanft_entscheiden(ha, wa.Sanft(weg_seit=0), 3600, False, {})[1] is None
    w = wa.pruefen(KETTE)
    assert wa.sanft_entscheiden(w, wa.Sanft(weg_seit=0), 3600, None, {})[1] is None


def test_glied_karte():
    w = wa.pruefen(KETTE)
    k = wa.glied_karte(
        w.glieder[1], wa.dosenstand({"wv": 1, "zustand": "stoerung", "grund": "inet_weg"}, 9.0)
    )
    assert (
        k["punkt"] == "amber"
        and k["zustand"] == "Störung erkannt · kein Internet"
        and k["sanft"] == "TR-064"
    )
    assert wa.glied_karte(w.glieder[0], wa.Dosenstand(erreichbar=False))["punkt"] == "rot"
    assert (
        wa.glied_karte(w.glieder[0], wa.dosenstand(None))["zustand"]
        == "Skript fehlt auf der Steckdose"
    )
    assert (
        wa.glied_karte(wa.Glied("andere", "X", "192.168.0.9"), None, DE)["zustand"]
        == "keine Steckdose"
    )


def test_stufe1_bremse_ueber_stoerungen_hinweg():
    w = wa.pruefen(KETTE)
    s, _ = wa.sanft_entscheiden(w, wa.Sanft(), 0, False, {})
    s, i = wa.sanft_entscheiden(w, s, 5 * 60, False, {})
    assert i == 0
    s, _ = wa.sanft_entscheiden(w, s, 6 * 60, True, {})  # kurz wieder da
    s, _ = wa.sanft_entscheiden(w, s, 7 * 60, False, {})
    s, i = wa.sanft_entscheiden(w, s, 12 * 60, False, {})
    assert i == 1, "Modem erst nach 60 min wieder, also gleich der Router"
    s, i = wa.sanft_entscheiden(w, s, 20 * 60, False, {})
    assert i is None


def test_stufe1_ruhe_haelt_an():
    w = wa.pruefen(KETTE)
    s = wa.Sanft(weg_seit=0, ruhe_bis=3600)
    s, i = wa.sanft_entscheiden(w, s, 600, False, {})
    assert i is None and s.weg_seit is None
    s, i = wa.sanft_entscheiden(w, s, 3601, False, {})
    assert i is None and s.weg_seit == 3601, "nach der Ruhe beginnt die Störung neu"
