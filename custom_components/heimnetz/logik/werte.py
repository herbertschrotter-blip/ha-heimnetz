"""Kleine Hilfen für Werte aus der FRITZ!Box: fritzconnection liefert je nach Aktion Text, Zahl oder Wahrheitswert."""

from __future__ import annotations

import re
from typing import Any


def text(wert: Any) -> str:
    """Wert als bereinigter Text; None → ""."""
    return "" if wert is None else str(wert).strip()


def ja(wert: Any) -> bool:
    """TR-064-Wahrheitswert: True, 1, "1", "true" → True."""
    if isinstance(wert, bool):
        return wert
    return text(wert).lower() in ("1", "true")


def ganzzahl(wert: Any) -> int | None:
    """Ganzzahl oder None, auch aus "−93.5" oder ""."""
    try:
        return int(float(text(wert)))
    except ValueError:
        return None


def kurz(wert: Any, grenze: int = 300) -> str:
    """Text in einer Zeile, höchstens `grenze` Zeichen."""
    t = re.sub(r"\s+", " ", text(wert))
    return t if len(t) <= grenze else t[: grenze - 1] + "…"


_MAC = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
_MAC_ENDE = re.compile(r"\s*\((?:[0-9A-Fa-f]{2}:){2}[0-9A-Fa-f]{2}\)")


def ohne_mac(wert: str) -> str:
    """Hardware-Adressen aus einem Text entfernen (ganze Adressen und „(…:…:…)“-Endungen älterer Journalzeilen)."""
    return _MAC.sub("[Hardware-Adresse]", _MAC_ENDE.sub("", wert))
