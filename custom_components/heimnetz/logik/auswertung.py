"""Speedtest-Auswertung: Wochenraster Wochentag × Stunde, Kennzahlen, Gewichtung nach Grundlast.

Übernommen aus der Speedtest-Karte des Altbestands (`www/netzwerk-cards.js`: quantil, gQuantil, messGewicht, auswerten,
skalaLage, messungenAusStatistik), damit die Seite selbst nichts rechnet. Zeiten in Sekunden seit 1970; Wochentag und
Stunde in der Ortszeit `tz`.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, tzinfo
from typing import Any

from .messung import Messung
from .sprache import DE, t, zahl

MODI = ("aus", "halb", "mit")  # belastete Messungen: weglassen, ¼ zählen, voll zählen
ZEITRAEUME = (7, 28, 84)  # Tage
MESS_S = 12  # geschätzte Dauer je Richtung einer Messung (Datenvolumen ≈ Rate × Dauer)
OHNE_TARIF_SCHWELLE = (
    10.0  # Mbit/s Grundlast, ab der eine Messung „belastet“ ist, wenn kein Tarif gesetzt ist
)
TAGE = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")
GLATT_H = (
    3  # Tagesverlauf: Mittelwert über die Stunde davor, die Stunde selbst und die danach (WU-0004)
)


@dataclass(frozen=True)
class Groesse:
    schluessel: str
    name: str
    einheit: str
    mehr_ist_gut: bool
    gueltig: Callable[[float], bool]


GROESSEN = {
    "down": Groesse("down", "Download", "Mbit/s", True, lambda v: v > 0.5),
    "up": Groesse("up", "Upload", "Mbit/s", True, lambda v: v > 0.5),
    "ping": Groesse("ping", "Ping", "ms", False, lambda v: 0 < v < 1000),
}


@dataclass(frozen=True)
class Punkt:
    """Eine Messung für die Auswertung (aus dem Speedtest-Protokoll, mit Server und Grundlast)."""

    t: float
    down: float | None
    up: float | None
    ping: float | None
    server: str | None
    last: float | None
    quelle: str
    # Momentaufnahme (WU-0005)
    kontext: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def wert(self, groesse: str) -> float | None:
        v: float | None = getattr(self, groesse)
        return v


def aus_messungen(messungen: Iterable[Messung]) -> list[Punkt]:
    return [
        Punkt(m.t, m.down, m.up, m.ping, m.server or None, m.last_down, "p", m.kontext)
        for m in messungen
    ]


def quantil(werte: Sequence[float], p: float) -> float | None:
    """Quantil einer unsortierten Liste, linear zwischen den Nachbarn."""
    if not werte:
        return None
    a = sorted(werte)
    i = (len(a) - 1) * p
    lo, hi = math.floor(i), math.ceil(i)
    return a[lo] + (a[hi] - a[lo]) * (i - lo)


def g_quantil(paare: Sequence[tuple[float, float]], p: float) -> float | None:
    """Gewichtetes Quantil, interpoliert zwischen den Gewichts-Mittelpunkten; Gewicht 0 zählt nicht."""
    a = sorted((x for x in paare if x[1] > 0), key=lambda x: x[0])
    if not a:
        return None
    gesamt = sum(w for _, w in a)
    lauf, pos = 0.0, []
    for _, w in a:
        pos.append((lauf + w / 2) / gesamt)
        lauf += w
    if p <= pos[0]:
        return a[0][0]
    for i in range(1, len(a)):
        if p <= pos[i]:
            return a[i - 1][0] + (a[i][0] - a[i - 1][0]) * (p - pos[i - 1]) / (
                (pos[i] - pos[i - 1]) or 1
            )
    return a[-1][0]


def g_mittel(paare: Sequence[tuple[float, float]]) -> float | None:
    a = [x for x in paare if x[1] > 0]
    g = sum(w for _, w in a)
    return sum(v * w for v, w in a) / g if g else None


def schwelle(tarif_down: float | None) -> float:
    """Grundlast in Mbit/s, ab der eine Messung „belastet“ ist: 10 % vom Download-Tarif, ohne Tarif 10 Mbit/s."""
    return tarif_down * 0.1 if tarif_down else OHNE_TARIF_SCHWELLE


def gewicht(p: Punkt, modus: str, server: str | None, grenze: float) -> float:
    """0 = zählt nicht. Anderer Server als gewählt → 0; belastet → je nach Modus 0, ¼ oder 1."""
    if server and p.server != server:
        return 0.0
    if p.last is not None and p.last > grenze:
        return {"aus": 0.0, "halb": 0.25}.get(modus, 1.0)
    return 1.0


def skala_lage(
    g: Groesse, v: float | None, median: float | None, tarif: float | None
) -> float | None:
    """Lage 0…1 auf der Farbskala rot → gelb → grün. Mit Tarif: Anteil am Tarif. Ohne: gegen den Median (Median =
    0,5, ±45 % = Enden)."""
    if v is None:
        return None
    if tarif:
        return max(0.0, min(1.0, v / tarif))
    if not median or not v:
        return None
    r = v / median if g.mehr_ist_gut else median / v
    return max(0.0, min(1.0, 0.5 + (r - 1) / 0.9))


@dataclass(frozen=True)
class Zelle:
    median: float | None
    anzahl: int
    lage: float | None


@dataclass(frozen=True)
class Stunde:
    """Eine Stunde im Tagesverlauf (WU-0004): Median (gewichtet wie im Raster), niedrigste und höchste gezählte
    Messung, Anzahl; dazu der geglättete Mittelwert über diese Stunde und ihre beiden Nachbarn."""

    median: float | None
    min: float | None
    max: float | None
    anzahl: int
    glatt: float | None = None


@dataclass(frozen=True)
class Verlauf:
    """Tagesverlauf für einen Wochentag (alle diese Tage im Zeitraum) oder ein Datum; beste und schwächste Stunde
    nach Median (beim Ping ist weniger besser)."""

    tag: int | None
    datum: str | None
    stunden: tuple[Stunde, ...]  # 24 Stunden
    beste: int | None
    schwaechste: int | None


@dataclass(frozen=True)
class Auswertung:
    groesse: str
    tage: int
    ab: float
    tarif: float | None
    anzahl: int  # gezählte Messungen (Gewicht > 0) mit gültigem Wert
    fehl: int  # Fehlmessungen (0 Mbit/s, Ping ab 1 s)
    gesamt: int  # Messungen im Zeitraum (nach Server-Filter)
    belastet: int
    ungeprueft: int  # ohne Grundlast (aus der Statistik oder ohne Zählerstände)
    median: float | None
    schnitt: float | None
    anteil: float | None  # Median / Tarif
    server: tuple[tuple[str, int], ...]
    raster: tuple[tuple[Zelle, ...], ...]  # 7 Wochentage (Mo…So) × 24 Stunden
    letzte: Punkt | None
    auffaellig: str | None
    volumen_mb: float  # geschätztes Datenvolumen der Messungen im Zeitraum
    hinweise: tuple[str, ...] = field(default_factory=tuple)
    tage_liste: tuple[
        tuple[str, int], ...
    ] = ()  # Tage mit gezählten Messungen (ISO-Datum, Anzahl), neueste zuerst
    verlauf: Verlauf | None = None


def anteil(wert: float | None, tarif: float | None) -> float | None:
    """Anteil eines Werts am Tarif (1 = 100 %)."""
    return wert / tarif if wert is not None and tarif else None


def volumen_mb(p: Punkt) -> float:
    """Geschätztes Datenvolumen einer Messung: (Download + Upload) × Dauer je Richtung."""
    return ((p.down or 0) + (p.up or 0)) * MESS_S / 8


def _zeit(t: float, tz: tzinfo) -> datetime:
    return datetime.fromtimestamp(t, tz)


def _auffaellig(
    g: Groesse,
    zellen: list[list[list[tuple[float, float]]]],
    tarif: float | None,
    sprache: str = DE,
) -> str | None:
    """Werktags abends (18–22 Uhr) gegen nachts (0–6 Uhr): deutlich schlechter abends → Hinweis auf volle Zelle."""
    abend = [x for wd in range(5) for h in range(18, 23) for x in zellen[wd][h]]
    nacht = [x for wd in range(7) for h in range(0, 7) for x in zellen[wd][h]]
    a, n = g_quantil(abend, 0.5), g_quantil(nacht, 0.5)
    if a is None or n is None or not a or not n or len(abend) < 3 or len(nacht) < 3:
        return None
    schlechter = a / n if g.mehr_ist_gut else n / a
    if schlechter >= 0.7:
        return None

    def wie(v: float) -> str:
        wert = f"{zahl(v, 0, sprache)} {g.einheit}"
        if not (tarif and g.mehr_ist_gut):
            return wert
        return t(
            "{wert} ({anteil} % vom Tarif)",
            sprache,
            wert=wert,
            anteil=zahl(v / tarif * 100, 0, sprache),
        )

    return t(
        "Mo–Fr 18–22 Uhr liegt der {name} typisch bei {abend}, nachts bei {nacht}. Das spricht für eine "
        "ausgelastete Funkzelle. Für eine Beschwerde beim Anbieter in diesen Stunden zusätzlich den RTR-Netztest "
        "machen.",
        sprache,
        name=g.name,
        abend=wie(a),
        nacht=wie(n),
    )


def verlauf(
    g: Groesse,
    stunden: Sequence[Sequence[tuple[float, float]]],
    tag: int | None,
    datum: date | None,
) -> Verlauf:
    """Tagesverlauf aus den gezählten Messungen je Stunde (Wert, Gewicht). Geglättet wird über GLATT_H Stunden
    (gewichteter Mittelwert aller Messungen darin); beim Wochentag läuft das Fenster über Mitternacht weiter (23 Uhr
    liegt neben 0 Uhr desselben Wochentags), bei einem Datum nicht."""
    n, r = len(stunden), GLATT_H // 2

    def fenster(h: int) -> list[tuple[float, float]]:
        nachbarn = (i % n if tag is not None else i for i in range(h - r, h + r + 1))
        return [x for i in nachbarn if 0 <= i < n for x in stunden[i]]

    s = tuple(
        Stunde(
            g_quantil(c, 0.5),
            min((v for v, _ in c), default=None),
            max((v for v, _ in c), default=None),
            len(c),
            g_mittel(fenster(h)),
        )
        for h, c in enumerate(stunden)
    )
    # nach Güte sortiert, bei gleichem Median die frühere Stunde zuerst; ohne Unterschied keine beste/schwächste
    mit = sorted(
        (
            (x.median if g.mehr_ist_gut else -x.median, h)
            for h, x in enumerate(s)
            if x.median is not None
        ),
        key=lambda m: (-m[0], m[1]),
    )
    if len({m for m, _ in mit}) < 2:
        return Verlauf(tag, datum.isoformat() if datum else None, s, None, None)
    return Verlauf(tag, datum.isoformat() if datum else None, s, mit[0][1], mit[-1][1])


KACHEL_LISTE = (
    20  # so viele Messungen zeigt das Popup einer Stundenkachel (AN-0005), neueste zuerst
)


@dataclass(frozen=True)
class KachelMessung:
    t: float
    server: str | None
    wert: float
    last: float | None
    belastet: bool
    gewicht: float  # wie im Raster: 0 zählt nicht, 0,25 zählt ¼, 1 voll
    netz: str | None = None  # aus der Momentaufnahme (WU-0005)
    rsrp: float | None = None


@dataclass(frozen=True)
class Kachel:
    """Die Messungen hinter einer Stundenkachel des Wochenrasters (AN-0005): Kennzahlen der gezählten Messungen und
    die Liste aller gültigen Messungen dieser Stunde, auch der belasteten, die nicht zählen."""

    tag: int
    stunde: int
    median: float | None
    min: float | None
    max: float | None
    anzahl: int  # gezählt (Gewicht > 0)
    belastet: int
    messungen: tuple[KachelMessung, ...]  # neueste zuerst, höchstens KACHEL_LISTE
    weitere: int  # ältere, die nicht in der Liste stehen


def auswahl(
    punkte: Sequence[Punkt], jetzt: float, ab_datum: float, tage: int, server: str | None
) -> tuple[float, list[Punkt], list[Punkt]]:
    """Gemeinsame Auswahl für Raster, Tagesverlauf und Kachel: Beginn des Zeitraums, Messungen im Zeitraum, davon die
    des gewählten Servers."""
    ab = max(jetzt - tage * 86_400, ab_datum)
    im = [p for p in punkte if ab <= p.t <= jetzt + 60]
    return ab, im, [p for p in im if not server or p.server == server]


def kachel(
    punkte: Sequence[Punkt],
    jetzt: float,
    ab_datum: float,
    tage: int,
    groesse: str,
    modus: str,
    server: str | None,
    tarif_down: float | None,
    tz: tzinfo,
    tag: int,
    stunde: int,
) -> Kachel:
    """Gleiche Auswahl wie `auswerten` (Zeitraum, Server, gültige Werte, Gewicht nach Grundlast), nur für eine
    Kachel – Median und Spanne stimmen also mit Raster und Tagesverlauf überein."""
    g = GROESSEN[groesse]
    grenze = schwelle(tarif_down)
    alle: list[KachelMessung] = []
    for p in auswahl(punkte, jetzt, ab_datum, tage, server)[2]:
        v = p.wert(groesse)
        if v is None or not g.gueltig(v):
            continue
        z = _zeit(p.t, tz)
        if z.weekday() != tag or z.hour != stunde:
            continue
        belastet = p.last is not None and p.last > grenze
        alle.append(
            KachelMessung(
                p.t,
                p.server,
                v,
                p.last,
                belastet,
                gewicht(p, modus, server, grenze),
                p.kontext.get("netz"),
                p.kontext.get("rsrp"),
            )
        )
    gezaehlt = [(m.wert, m.gewicht) for m in alle if m.gewicht > 0]
    werte = [v for v, _ in gezaehlt]
    alle.sort(key=lambda m: -m.t)
    return Kachel(
        tag,
        stunde,
        g_quantil(gezaehlt, 0.5),
        min(werte, default=None),
        max(werte, default=None),
        len(gezaehlt),
        sum(1 for m in alle if m.belastet),
        tuple(alle[:KACHEL_LISTE]),
        max(0, len(alle) - KACHEL_LISTE),
    )


def _verlauf_fuer(
    g: Groesse,
    zellen: list[list[list[tuple[float, float]]]],
    am_datum: list[list[tuple[float, float]]],
    tag: int | None,
    datum: date | None,
) -> Verlauf | None:
    """Datum hat Vorrang vor dem Wochentag; ohne beides kein Verlauf."""
    if datum is not None:
        return verlauf(g, am_datum, None, datum)
    if tag is not None and 0 <= tag < 7:
        return verlauf(g, zellen[tag], tag, None)
    return None


def auswerten(
    punkte: Sequence[Punkt],
    jetzt: float,
    ab_datum: float,
    tage: int,
    groesse: str,
    modus: str,
    server: str | None,
    tarif: float | None,
    tarif_down: float | None,
    tz: tzinfo,
    tag: int | None = None,
    datum: date | None = None,
    sprache: str = DE,
) -> Auswertung:
    """Kennzahlen und Raster für einen Zeitraum und eine Größe. `tarif` gilt für die gewählte Größe (Ping: None),
    `tarif_down` bestimmt die Schwelle für „belastet“. Mit `datum` (Vorrang) oder `tag` (Wochentag 0 = Mo) auch der
    Tagesverlauf (WU-0004)."""
    g = GROESSEN[groesse]
    ab, im, gewaehlt = auswahl(punkte, jetzt, ab_datum, tage, server)
    grenze = schwelle(tarif_down)
    zellen: list[list[list[tuple[float, float]]]] = [[[] for _ in range(24)] for _ in range(7)]
    je_tag: dict[date, int] = {}  # gezählte Messungen je Tag
    am_datum: list[list[tuple[float, float]]] = [[] for _ in range(24)]
    alle: list[tuple[float, float]] = []
    fehl = 0
    for p in gewaehlt:
        v = p.wert(groesse)
        if v is None:
            continue
        if not g.gueltig(v):
            fehl += 1
            continue
        w = gewicht(p, modus, server, grenze)
        if not w:
            continue
        z = _zeit(p.t, tz)
        zellen[z.weekday()][z.hour].append((v, w))
        je_tag[z.date()] = je_tag.get(z.date(), 0) + 1
        if z.date() == datum:
            am_datum[z.hour].append((v, w))
        alle.append((v, w))
    median = g_quantil(alle, 0.5)
    raster = tuple(
        tuple(
            Zelle(
                m := g_quantil(c, 0.5),
                len(c),
                skala_lage(g, m, median, tarif if g.mehr_ist_gut else None),
            )
            for c in reihe
        )
        for reihe in zellen
    )
    namen: dict[str, int] = {}
    for p in im:
        if p.server:
            namen[p.server] = namen.get(p.server, 0) + 1
    gueltige = [p for p in gewaehlt if p.wert(groesse) is not None]
    return Auswertung(
        groesse=groesse,
        tage=tage,
        ab=ab,
        tarif=tarif,
        anzahl=len(alle),
        fehl=fehl,
        gesamt=len(gewaehlt),
        belastet=sum(1 for p in gewaehlt if p.last is not None and p.last > grenze),
        ungeprueft=sum(1 for p in gewaehlt if p.last is None),
        median=median,
        schnitt=g_mittel(alle),
        anteil=anteil(median, tarif) if g.mehr_ist_gut else None,
        server=tuple(sorted(namen.items(), key=lambda x: (-x[1], x[0]))),
        raster=raster,
        letzte=gueltige[-1] if gueltige else None,
        auffaellig=_auffaellig(g, zellen, tarif, sprache),
        volumen_mb=round(sum(volumen_mb(p) for p in im), 1),
        tage_liste=tuple((d.isoformat(), je_tag[d]) for d in sorted(je_tag, reverse=True)),
        verlauf=_verlauf_fuer(g, zellen, am_datum, tag, datum),
    )
