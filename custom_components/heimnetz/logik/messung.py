"""Speedtest-Protokoll: eine Messung der Ookla-Integration mit der Grundlast davor.

Gemessen wird von der Ookla-Integration; hier wird nur eingetragen, was sie gemeldet hat, und dazu der Verkehr
über die Box in den Minuten vor der Messung (verkehr.grundlast). So lassen sich Messungen erkennen, bei denen das
Heimnetz schon ausgelastet war.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, tzinfo
from typing import Any

from . import sprache as sp
from .ereignis import INFO, Ereignis
from .verkehr import Zaehlerstand, grundlast
from .werte import kurz

# AN-0007: Kennung einer Messung ist ihr Zeitpunkt (Primärschlüssel der Tabelle, so wie die Seite ihn bekommt).
# Zwei Messungen liegen nie weniger als eine Sekunde auseinander; die Spanne fängt Rundung auf dem Weg ab.
GLEICH_S = 0.5


@dataclass(frozen=True)
class Messung:
    """Mbit/s und ms; None = Wert fehlt (Fehlmessung bleibt erhalten). last_* = Grundlast in Mbit/s. kontext =
    Momentaufnahme im Moment der Messung (logik.kontext, WU-0005); leer bei älteren Messungen ohne Nachtrag."""

    t: float
    down: float | None
    up: float | None
    ping: float | None
    server: str
    last_down: float | None
    last_up: float | None
    kontext: dict[str, Any] = field(default_factory=dict, compare=False)


def zahl(wert: Any) -> float | None:
    """Zahl aus einem Zustand; "unavailable", "unknown", "" → None."""
    try:
        return round(float(wert), 2)
    except TypeError, ValueError:
        return None


def eintragen(
    t: float, down: Any, up: Any, ping: Any, server: Any, ring: list[Zaehlerstand]
) -> Messung:
    last = grundlast(ring, t)
    name = "" if server in (None, "unknown", "unavailable") else kurz(server, 80)
    return Messung(
        t=t,
        down=zahl(down),
        up=zahl(up),
        ping=zahl(ping),
        server=name,
        last_down=last.down if last else None,
        last_up=last.up if last else None,
    )


def gleich(t: float, kennung: float) -> bool:
    """AN-0007: Zeitpunkt `t` gehört zur Messung mit der Kennung `kennung`."""
    return abs(t - kennung) < GLEICH_S


def ist_geloescht(t: float, geloescht: Iterable[float]) -> bool:
    """AN-0007: gelöschte Messung – sie darf nicht wieder eingetragen werden (Ookla zeigt sie weiter als letzten
    Test, und nach einem Neustart liest die Integration den noch einmal)."""
    return any(gleich(t, g) for g in geloescht)


def ohne_geloeschte(messungen: Iterable[Messung], geloescht: Iterable[float]) -> list[Messung]:
    """AN-0007: Messungen ohne die gelöschten (Merkliste der Zeitpunkte)."""
    liste = list(geloescht)
    return [m for m in messungen if not ist_geloescht(m.t, liste)]


def geloescht_ereignis(t: float, tz: tzinfo, sprache: str = sp.DE) -> Ereignis:
    """AN-0007: Journalzeile „Messung <Zeit> gelöscht“ – nur der Zeitpunkt, keine Person und kein Gerät."""
    zeit = datetime.fromtimestamp(t, tz).strftime(
        "%d.%m.%Y %H:%M" if sprache == sp.DE else "%Y-%m-%d %H:%M"
    )
    return Ereignis("messung_geloescht", INFO, sp.t("Messung {zeit} gelöscht", sprache, zeit=zeit))
