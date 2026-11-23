"""Übersicht „Lagebild“ (1.1): Kopfzeile, Leitung, Meldezeile, Wächter in einer Zeile."""

from logik import lagebild as lb

MOBIL = lb.Zugang("mobilfunk", "5G-NSA", True, 0.8, "−88 dBm")


def test_kopf():
    assert lb.kopf(True, True, []) == {
        "punkt": "",
        "titel": "Alles in Ordnung",
        "wort": "Alles in Ordnung",
        "chips": [],
    }
    assert lb.kopf(True, True, ["info"])["titel"] == "Alles in Ordnung"  # info zählt nicht
    assert lb.kopf(True, True, ["warnung", "info"])["titel"] == "1 Hinweis"
    assert lb.kopf(True, False, [])["titel"] == "Kein Internet"
    assert lb.kopf(True, True, [], "en")["titel"] == "All good"


def test_kopf_stoerungen_und_hinweise_getrennt():
    """Übersicht und Kopf der anderen Reiter sagen dasselbe: Störungen und Hinweise getrennt gezählt."""
    k = lb.kopf(True, True, ["warnung", "kritisch", "kritisch", "warnung"])
    assert k == {
        "punkt": "rot",
        "titel": "2 Störungen · 2 Hinweise",
        "wort": "Störung",
        "chips": [{"art": "rot", "text": "2 Störungen"}, {"art": "amber", "text": "2 Hinweise"}],
    }
    assert lb.kopf(True, True, ["kritisch"])["titel"] == "1 Störung"
    assert lb.kopf(True, True, ["warnung", "warnung"])["wort"] == "Hinweise"
    en = lb.kopf(True, True, ["kritisch", "warnung"], "en")
    assert (en["titel"], en["wort"]) == ("1 problem · 1 notice", "Problem")


def test_kopf_box_weg_gleicher_wortlaut():
    k = lb.kopf(False, None, ["kritisch"])
    assert (k["punkt"], k["titel"], k["wort"]) == (
        "grau",
        "FRITZ!Box nicht erreichbar",
        "FRITZ!Box nicht erreichbar",
    )
    assert k["chips"] == [{"art": "rot", "text": "1 Störung"}]


def test_leitung_alles_gut():
    l_ = lb.leitung(True, True, True, MOBIL, "FRITZ!Box 6860 5G")
    assert [k["zustand"] for k in l_["knoten"]] == ["gut"] * 4
    assert l_["knoten"][1]["text"] == "6860 5G"
    assert l_["knoten"][2] | {} == {
        "teil": "zugang",
        "zustand": "gut",
        "symbol": "📡",
        "name": "5G-NSA",
        "text": "−88 dBm",
        "balken": 3,
    }
    assert l_["draehte"] == ["", "", ""]


def test_leitung_schwacher_empfang_und_stoerungen():
    schwach = lb.Zugang("mobilfunk", "LTE", True, 0.3, "−107 dBm")
    assert lb.leitung(True, True, True, schwach, "")["knoten"][2]["zustand"] == "warn"
    ohne_netz = lb.Zugang("mobilfunk", "–", False)
    l_ = lb.leitung(True, True, False, ohne_netz, "")
    assert [k["zustand"] for k in l_["knoten"]] == ["gut", "gut", "weg", "weg"]
    assert l_["knoten"][2]["text"] == "kein Netz" and l_["draehte"] == ["", "weg", "weg"]
    box_weg = lb.leitung(False, False, None, MOBIL, "")
    assert [k["zustand"] for k in box_weg["knoten"]] == ["gut", "weg", "", ""]
    assert box_weg["draehte"] == ["weg", "", ""]


def test_leitung_dsl_ohne_empfang():
    l_ = lb.leitung(True, True, True, lb.Zugang("dsl", "DSL", True), "")
    assert l_["knoten"][2]["symbol"] == "☎️" and l_["knoten"][2]["balken"] is None
    assert lb.leitung(True, True, True, None, "")["knoten"][2]["name"] == "Zugang"


def test_balken():
    assert [lb.balken(x) for x in (None, 0, 0.3, 0.5, 1, 2)] == [0, 0, 1, 2, 4, 4]


def test_meldung():
    leer = lb.meldung([], {"t": 5.0, "text": "Mobilfunk wechselt"})
    assert leer == {
        "n": 0,
        "art": "ok",
        "titel": "Nichts Auffälliges",
        "text": "Mobilfunk wechselt",
        "t": 5.0,
    }
    b = [
        {"stufe": "warnung", "titel": "Speicher", "text": "knapp"},
        {"stufe": "kritisch", "titel": "Kein Internet", "text": ""},
    ]
    m = lb.meldung(b, None)
    assert (m["n"], m["art"], m["titel"], m["text"]) == (
        2,
        "rot",
        "Kein Internet",
        "+1 weitere: Speicher",
    )
    assert lb.meldung(b[:1], None)["text"] == "knapp" and lb.meldung(b[:1], None)["art"] == "amber"


def test_waechter():
    assert lb.waechter([], 0)["wort"] == "keiner"
    aus = lb.waechter([lb.Waechterzustand(False, "grau", None, ())], 0)
    assert (aus["wort"], aus["text"]) == ("aus", "1 eingerichtet")
    ruhig = lb.waechter(
        [lb.Waechterzustand(True, "ok", None, ()), lb.Waechterzustand(True, "ok", None, [100.0])],
        10_000,
    )
    assert ruhig == {"wort": "bereit", "text": "2 an · letzter Eingriff", "punkt": "ok", "t": 100.0}
    greift = lb.waechter([lb.Waechterzustand(True, "ok", 9_000.0, ())], 10_000)
    assert (greift["wort"], greift["punkt"], greift["text"]) == (
        "greift ein",
        "amber",
        "1 an · kein Eingriff",
    )
    frisch = lb.waechter([lb.Waechterzustand(True, "ok", None, [9_500.0])], 10_000)
    assert (frisch["wort"], frisch["punkt"], frisch["t"]) == (
        "bereit",
        "ok",
        9_500.0,
    )  # Eingriff vorbei
    rot = lb.waechter([lb.Waechterzustand(True, "rot", None, ())], 10_000)
    assert (rot["wort"], rot["punkt"]) == ("bereit", "rot")
    ungelesen = lb.waechter([lb.Waechterzustand(True, "grau", None, ())], 10_000)
    assert ungelesen["punkt"] == "grau"
