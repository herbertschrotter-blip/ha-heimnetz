"""Gemerkte Abrufe aus dem Netz (OSM-Masten, OpenCellID-Abzug): wann wieder fragen."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def faellig(
    eintrag: Mapping[str, Any] | None,
    kennung: str,
    jetzt: float,
    gueltig_s: float,
    nochmal_s: float,
) -> bool:
    """Neu abrufen? Andere Kennung (Ausschnitt, Schlüssel) oder nie abgerufen: ja; sonst nach `gueltig_s`, nach einem
    Fehler nach `nochmal_s`."""
    if not eintrag or eintrag.get("rahmen") != kennung:
        return True
    if eintrag.get("fehler_t"):
        return jetzt - float(eintrag["fehler_t"]) >= nochmal_s
    return jetzt - float(eintrag.get("t", 0)) >= gueltig_s
