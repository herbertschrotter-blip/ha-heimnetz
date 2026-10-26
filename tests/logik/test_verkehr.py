"""Verkehr und Grundlast (Fälle aus dem Altbestand)."""

from logik import verkehr as vk

JETZT = 1_800_000_000


def ring(mbit_je_minute):
    """Zählerstände je Minute; letzter Stand = JETZT."""
    t, rx = JETZT - 60 * len(mbit_je_minute), 0
    out = [vk.Zaehlerstand(t, 0, 0)]
    for m in mbit_je_minute:
        t += 60
        rx += int(m * 1e6 / 8 * 60)
        out.append(vk.Zaehlerstand(t, rx, rx // 10))
    return out


def test_grundlast_ohne_die_messung_selbst():
    g = vk.grundlast(ring([2, 2, 2, 2, 2, 2, 2, 120]), JETZT)
    assert g is not None and (g.down, g.up) == (2.0, 0.2)
    g = vk.grundlast(ring([2, 40, 40, 40, 40, 40, 40, 120]), JETZT)
    assert g is not None and g.down == 40.0


def test_grundlast_zu_wenig_daten_oder_ruecksprung():
    assert vk.grundlast(ring([2, 120]), JETZT) is None
    r = ring([2, 2, 2, 2, 2, 2, 2, 120])
    r = r[:4] + [vk.Zaehlerstand(p.t, p.rx - 10**9, p.tx) for p in r[4:]]
    g = vk.grundlast(r, JETZT)
    assert g is not None and g.sek == 240
    assert vk.grundlast([], JETZT) is None


def test_letzte_rate_und_fortschreiben():
    r = ring([8, 16])
    rate = vk.letzte_rate(r)
    assert rate is not None and (rate.down, rate.up, rate.sek) == (16.0, 1.6, 60)
    assert vk.letzte_rate(r[:1]) is None
    assert vk.letzte_rate([r[1], vk.Zaehlerstand(r[1].t + 60, 0, 0)]) is None  # Neustart der Box
    lang = r
    for i in range(30):
        lang = vk.fortschreiben(lang, vk.Zaehlerstand(JETZT + i, 0, 0))
    assert len(lang) == vk.MERKEN
