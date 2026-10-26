"""Diagnose-Download (WU-0006): was beim Fehlersuchen hilft, darf öffentlich angehängt werden – etwa an ein Issue.

Deshalb wird alles geschwärzt, was nicht öffentlich sein soll: Schlüssel mit vertraulichem Inhalt (Zugang zur Box,
Kennwörter, Schlüssel für OpenCellID, Zellkennungen, TAC/PCI, Koordinaten, Gerätenamen, Hardware- und IP-Adressen)
werden ersetzt, und in allen übrigen Texten (z. B. Fehlermeldungen) Adressen, Koordinaten, Kennwörter und bekannte
Gerätenamen wie beim öffentlichen Melden (`github.schwaerzen`).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .github import schwaerzen as _text

GESCHWAERZT = "**REDACTED**"  # wie async_redact_data von Home Assistant
# Schlüssel in kleinen Buchstaben; verglichen wird ohne Groß-/Kleinschreibung
VERTRAULICH = frozenset(
    {
        # Zugang und Schlüssel
        "adresse", "host", "username", "user", "benutzer", "passwort", "password", "kennwort", "token",
        "api_key", "schluessel", "opencellid_schluessel",
        # Netz und Geräte
        "ip", "ipv4", "ipv6", "mac", "gw_mac", "name", "namen", "hostname", "geraete_namen", "ssid",
        # Zellen und Ort
        "zelle", "zellen", "cellid", "cell_id", "kennung", "anlage", "tac", "pci", "nr_pci", "plmn", "enb",
        "lat", "lon", "latitude", "longitude", "koordinaten", "standort",
    }
)  # fmt: skip


def schwaerzen(daten: Any, namen: Iterable[str] = ()) -> Any:
    """Tief schwärzen (dict, list, tuple, Text); Zahlen und Wahrheitswerte bleiben. Gibt eine Kopie zurück."""
    bekannt = tuple(namen)
    return _tief(daten, bekannt)


def _tief(wert: Any, namen: tuple[str, ...]) -> Any:
    if isinstance(wert, Mapping):
        return {
            k: GESCHWAERZT
            if str(k).lower() in VERTRAULICH and wert[k] not in (None, "")
            else _tief(wert[k], namen)
            for k in wert
        }
    if isinstance(wert, list | tuple):
        return [_tief(x, namen) for x in wert]
    if isinstance(wert, str):
        return _text(wert, namen)
    return wert
