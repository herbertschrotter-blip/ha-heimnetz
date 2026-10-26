"""Journal: was sich zwischen zwei Abrufen geändert hat."""

from __future__ import annotations

from dataclasses import dataclass

KRITISCH = "kritisch"
WARNUNG = "warnung"
INFO = "info"
STUFEN = (KRITISCH, WARNUNG, INFO)


@dataclass(frozen=True)
class Ereignis:
    """Eine Zeile im Journal. `mac` nur bei Ereignissen eines Geräts (Verlauf je Gerät)."""

    art: str
    stufe: str
    text: str
    mac: str = ""
