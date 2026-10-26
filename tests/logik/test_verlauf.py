"""Verlauf je Gerät (Fälle aus dem Altbestand)."""

from logik import verlauf as vl


def test_vorher():
    assert vl.vorher("offline", "online", True) is False
    assert vl.vorher("online", None, False) is True
    assert (
        vl.vorher(None, "offline", False) is True
    )  # erstes Ereignis im Fenster ist „offline“ → davor online
    assert vl.vorher(None, "neu", True) is None  # neues Gerät: davor keine Aufzeichnung
    assert vl.vorher(None, None, True) is True


def test_abschnitte_und_streifen():
    teile = vl.abschnitte(True, [(10, "offline"), (20, "ip_wechsel"), (33, "online")], 0, 48)
    assert [(a.von, a.bis, a.an) for a in teile] == [(0, 10, True), (10, 33, False), (33, 48, True)]
    assert vl.online_s(teile, 0, 48) == 25
    s = vl.streifen(teile, 0, 48, felder=4)  # je 12 s; genau halb online zählt als „an“
    assert s == [vl.AN, vl.AUS, vl.AUS, vl.AN]
    neu = vl.abschnitte(None, [(36, "neu")], 0, 48)
    assert vl.streifen(neu, 0, 48, felder=4) == [vl.LUECKE, vl.LUECKE, vl.LUECKE, vl.AN]


def test_einstufung_und_id():
    assert vl.einstufung(True, 0, True) == "neu"
    assert vl.einstufung(True, vl.WACKELT_AB, False) == "wackelt"
    assert vl.einstufung(False, 1, False) == "aus"
    assert (
        vl.geraete_id("aa:bb", "s") == vl.geraete_id("AA:BB", "s")
        and len(vl.geraete_id("x", "s")) == 16
    )
    assert vl.geraete_id("AA:BB", "salz1") != vl.geraete_id(
        "AA:BB", "salz2"
    )  # ohne Salz nicht zurückzurechnen


def test_streifen_halb_online_ist_an():
    teile = vl.abschnitte(False, [(6, "online")], 0, 12)
    assert vl.streifen(teile, 0, 12, felder=1) == [vl.AN]


def test_tage_mit_zeitumstellung_und_zustand_ueber_mitternacht():
    # drei Tage, der mittlere 25 h lang (Ende der Sommerzeit); offline am ersten Abend, online am dritten Morgen
    grenzen = [(0, 86_400), (86_400, 86_400 + 90_000), (176_400, 262_800)]
    ev = [(80_000, "offline"), (180_000, "online")]
    tage = vl.tage(True, ev, grenzen, jetzt=200_000, felder=4)
    assert [t.online_s for t in tage] == [80_000, 0, 200_000 - 180_000]
    assert tage[1].streifen == (vl.AUS,) * 4  # Zustand „offline“ über Mitternacht getragen
    assert tage[2].streifen[-1] == vl.LUECKE  # nach „jetzt“ keine Aufzeichnung


def test_online_anteil():
    tage = vl.tage(True, [(6, "offline")], [(0, 12), (12, 24)], jetzt=18, felder=2)
    assert vl.online_anteil(tage) == 6 / 18
    assert vl.online_anteil([]) is None


def test_online_anteil_ohne_luecken():
    """Neues Gerät, seit es da ist immer online: ~100 %, nicht der Anteil an der ganzen Woche."""
    tage = vl.tage(None, [(20, "neu")], [(0, 12), (12, 24)], jetzt=24, felder=2)
    assert vl.online_anteil(tage) == 1.0
