"""Speedtest-Protokoll: eine Messung der Ookla-Integration mit der Grundlast davor.

Gemessen wird von der Ookla-Integration; hier wird nur eingetragen, was sie gemeldet hat, und dazu der Verkehr
über die Box in den Minuten vor der Messung (verkehr.grundlast). So lassen sich Messungen erkennen, bei denen das
Heimnetz schon ausgelastet war.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .verkehr import Zaehlerstand, grundlast
from .werte import kurz


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
