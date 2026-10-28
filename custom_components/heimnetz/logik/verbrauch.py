"""Datenverbrauch der ganzen Box je Tag (die Box zählt nicht je Gerät), dazu der Anteil der Speedtests.

Eingang sind die Tageswerte („change“) der Langzeit-Statistik der Zähler von FRITZ!Box Tools in GB; die Speedtests
werden aus dem Messprotokoll geschätzt (auswertung.volumen_mb).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta, tzinfo

from .auswertung import Punkt, volumen_mb


@dataclass(frozen=True)
class Tag:
    tag: date
    down: float  # GB
    up: float
    speedtest: float  # GB, geschätzt; steckt in down/up schon drin


@dataclass(frozen=True)
class Kacheln:
    heute: Tag
    woche: float  # GB seit Montag
    monat: float  # GB seit dem 1.
    schnitt: float  # GB je Tag im gezeigten Zeitraum
    speedtest: float  # GB der Speedtests im gezeigten Zeitraum


def tage(
    down: Iterable[tuple[float, float | None]],
    up: Iterable[tuple[float, float | None]],
    punkte: Iterable[Punkt],
    jetzt: float,
    anzahl: int,
    tz: tzinfo,
) -> list[Tag]:
    """Lückenlos die letzten `anzahl` Tage bis heute (Ortszeit), älteste zuerst. Negative Änderungen (Zähler auf null
    gesetzt) zählen als 0."""
    heute = datetime.fromtimestamp(jetzt, tz).date()
    erster = heute - timedelta(days=anzahl - 1)
    werte: dict[date, list[float]] = {
        erster + timedelta(days=i): [0.0, 0.0, 0.0] for i in range(anzahl)
    }
    for i, reihe in enumerate((down, up)):
        for start, change in reihe:
            tag = datetime.fromtimestamp(start, tz).date()
            if tag in werte and change:
                werte[tag][i] += max(0.0, change)
    for p in punkte:
        tag = datetime.fromtimestamp(p.t, tz).date()
        if tag in werte:
            werte[tag][2] += volumen_mb(p) / 1000
    # „davon Speedtests“ ist eine Schätzung aus den Ookla-Ergebnissen und kann größer sein als die Zähler des Tages
    # (Zähler fehlen am Tag der Einrichtung oder waren kurz nicht verfügbar) – höchstens die Tagesmenge (GitHub #1)
    return [
        Tag(t, round(d, 3), round(u, 3), round(min(s, d + u), 3))
        for t, (d, u, s) in sorted(werte.items())
    ]


def kacheln(alle: Sequence[Tag], gezeigt: int) -> Kacheln | None:
    """`alle` reicht mindestens bis zum Monatsersten zurück; Schnitt und Speedtests gelten für die letzten `gezeigt`
    Tage."""
    if not alle:
        return None
    heute = alle[-1]
    montag = heute.tag - timedelta(days=heute.tag.weekday())
    zeitraum = alle[-gezeigt:]

    def summe(ts: Iterable[Tag]) -> float:
        return round(sum(t.down + t.up for t in ts), 2)

    return Kacheln(
        heute=heute,
        woche=summe(t for t in alle if t.tag >= montag),
        monat=summe(t for t in alle if t.tag >= heute.tag.replace(day=1)),
        schnitt=round(summe(zeitraum) / len(zeitraum), 2),
        speedtest=round(sum(t.speedtest for t in zeitraum), 2),
    )
