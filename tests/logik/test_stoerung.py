"""Internet-Störung zusammenfassen (AN-0003) – der Fall vom 13.10.: drei kurze Ausfälle, Mobilfunk stand."""

from logik import befunde as bf
from logik import stoerung as sg

T0 = 1_760_000_000.0


def schritte(folge, lage="steht"):
    st, ereignisse = None, []
    for t, ok in folge:
        st, e = sg.fortschreiben(st, ok, T0 + t, None if ok else lage)
        if e:
            ereignisse.append(e)
    return st, ereignisse


def test_drei_ausfaelle_ein_eintrag_nach_ruhe():
    # 09:03–09:05, 09:06–09:07, 09:08–09:11 (Minuten ab 09:03)
    folge = [(0, False), (130, True), (194, False), (258, True), (320, False), (513, True)]
    st, ereignisse = schritte(folge)
    assert ereignisse == [] and st.anzahl == 3 and round(st.weg_s) == 130 + 64 + 193
    st, e = sg.fortschreiben(st, True, T0 + 513 + sg.RUHE_S - 60, None)
    assert e is None and st is not None  # noch keine 10 min ruhig
    st, e = sg.fortschreiben(st, True, T0 + 513 + sg.RUHE_S, None)
    assert st is None and e.stufe == "warnung"
    assert e.text == (
        "Internet-Störung vorbei: 3 Unterbrechungen in 8 min, zusammen 6 min weg – "
        "Mobilfunk stand (keine Neueinwahl), vermutlich beim Anbieter"
    )


def test_ein_ausfall_und_ursache_nach_gewicht():
    st, _ = schritte([(0, False), (120, True)], lage="steht")
    st, _ = sg.fortschreiben(
        sg.aus_dict({**st.als_dict(), "lagen": ["steht", "neu"]}), True, T0 + 2000, None
    )
    assert st is None
    st, _ = schritte([(0, False), (120, True)], lage="neu")
    assert (
        sg.text(st)
        == "Internet-Störung vorbei: 1 Unterbrechung, 2 min weg – die Box hat sich neu ins Mobilfunknetz eingewählt"
    )


def test_ohne_ausfall_nichts_und_speichern():
    assert schritte([(0, True), (60, True)]) == (None, [])
    st, _ = schritte([(0, False)])
    assert (
        sg.aus_dict(st.als_dict()) == st
        and sg.aus_dict(None) is None
        and sg.aus_dict({"x": 1}) is None
    )


def test_lage():
    assert sg.lage(False, 9999, -90, False, True) == "box"
    assert sg.lage(True, None, None, False, False) is None  # Box ohne Mobilfunk
    assert sg.lage(True, 120, -90, False, True) == "neu"
    assert sg.lage(True, 9999, -90, True, True) == "neu"
    assert sg.lage(True, 9999, -112, False, True) == "schwach"
    assert sg.lage(True, 9999, -101, False, True) == "steht"


def test_befund_text_nach_lage():
    pi = bf.PiVerbindung(box=True, internet=False, dns=True, gw_mac="AA")
    texte = {
        lage: bf.finden({}, bf.Heimnetz(), None, pi, lage)[0].text
        for lage in (None, "steht", "neu", "schwach")
    }
    assert "vermutlich beim Anbieter" in texte["steht"] and "wählt sich gerade neu" in texte["neu"]
    assert (
        "schwach" in texte["schwach"]
        and texte[None] == "Die FRITZ!Box ist erreichbar, aber der Weg ins Internet nicht."
    )
    assert all(
        "wählt sich selbst neu ein" not in t for t in texte.values()
    )  # alter, oft falscher Satz
    ohne_box = bf.finden(
        {}, bf.Heimnetz(), None, bf.PiVerbindung(False, False, False, ""), "steht"
    )[0]
    assert "antwortet dem Pi nicht" in ohne_box.text
