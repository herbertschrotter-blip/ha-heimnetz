"""Speedtest-Serie (WU-0001): mehrere Durchläufe hintereinander, Ergebnis als Median mit Spanne.

Median statt Mittelwert, damit ein Ausreißer (z. B. ein Durchlauf während eines Downloads im Heimnetz) das Ergebnis
nicht verzieht. Die Durchläufe startet und liest die Integration (Ookla); hier wird nur gerechnet.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from statistics import median
from typing import Any

WARTEN_S = 240  # so lange auf das Ergebnis eines Durchlaufs warten
GROESSEN = ("down", "up", "ping")


@dataclass(frozen=True)
class Lauf:
    t: float
    server: str | None
    down: float | None
    up: float | None
    ping: float | None


def ergebnis(laeufe: Sequence[Lauf], tarif_down: float | None, gewuenscht: int) -> dict[str, Any]:
    """Median und Spanne je Größe; Anteil vom Tarif für den Download. `gewuenscht` = geplante Durchläufe."""
    werte: dict[str, Any] = {}
    for g in GROESSEN:
        zahlen = [x for x in (getattr(lauf, g) for lauf in laeufe) if x is not None]
        werte[g] = (
            {
                "median": round(median(zahlen), 1),
                "min": round(min(zahlen), 1),
                "max": round(max(zahlen), 1),
            }
            if zahlen
            else None
        )
    down = werte["down"]
    return {
        "t": laeufe[0].t if laeufe else None,
        "geplant": gewuenscht,
        "laeufe": [asdict(x) for x in laeufe],
        "server": sorted({x.server for x in laeufe if x.server}),
        "anteil": round(down["median"] / tarif_down * 100) if down and tarif_down else None,
        **werte,
    }
