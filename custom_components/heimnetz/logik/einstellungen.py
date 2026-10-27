"""Einstellungen der Seite (Tarif, Auswerten ab, Grenze für schwachen WLAN-Empfang): prüfen, speichern als dict. Eigentümer ist die Integration
(Integrations-Speicher, G-09); Seite und Übernahme aus dem Altbestand ändern sie nur über `pruefen`."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from . import zugang as zg
from .modem import adresse_erlaubt
from .sprache import Ungueltig, merke

__all__ = ["Einstellungen", "Ungueltig", "pruefen"]

TARIF_HOECHSTENS = 10_000.0  # Mbit/s
WLAN_SCHWACH = (30, 40, 50)  # Prozent (Empfang, wie die Box ihn meldet)


@dataclass(frozen=True)
class Einstellungen:
    tarif_down: float | None = None  # Mbit/s
    tarif_up: float | None = None
    ab: date | None = None  # Messungen davor zählen nicht mit
    wlan_schwach: int = 40  # Empfang darunter gilt als schwach
    # WU-0009: woher kommt das Internet – „auto“ = erkannt; Adresse eines vorgeschalteten Geräts (nur private)
    zugang_wahl: str = "auto"
    zugang_adresse: str | None = None
    zugang_ersatz: str = "auto"

    def als_dict(self) -> dict[str, Any]:
        return {
            "tarif_down": self.tarif_down,
            "tarif_up": self.tarif_up,
            "ab": self.ab.isoformat() if self.ab else None,
            "wlan_schwach": self.wlan_schwach,
            "zugang_wahl": self.zugang_wahl,
            "zugang_adresse": self.zugang_adresse,
            "zugang_ersatz": self.zugang_ersatz,
        }


def _tarif(wert: Any, name: str) -> float | None:
    if wert in (None, ""):
        return None
    try:
        v = float(wert)
    except (TypeError, ValueError) as err:
        raise Ungueltig("{name}: keine Zahl", name=name) from err
    if v == 0:
        return None  # 0 = kein Tarif
    if not 0 < v <= TARIF_HOECHSTENS:
        raise Ungueltig("{name}: zwischen 0 und {n} Mbit/s", name=name, n=f"{TARIF_HOECHSTENS:.0f}")
    return round(v, 1)


def pruefen(daten: dict[str, Any], heute: date) -> Einstellungen:
    """Aus Eingaben (Seite) oder gespeichertem dict; leer/0 = nicht gesetzt."""
    ab = daten.get("ab")
    datum: date | None = None
    if ab:
        try:
            datum = ab if isinstance(ab, date) else date.fromisoformat(str(ab)[:10])
        except ValueError as err:
            raise Ungueltig("Auswerten ab: kein Datum") from err
        if datum > heute:
            raise Ungueltig("Auswerten ab: liegt in der Zukunft")
        if datum.year < 2000:
            datum = None  # „1970“ des alten Helfers = keine Grenze
    roh = daten.get("wlan_schwach")
    try:
        schwach = 40 if roh in (None, "") else float(roh)
    except (TypeError, ValueError) as err:
        raise Ungueltig("Schwacher Empfang: keine Zahl") from err
    if schwach not in WLAN_SCHWACH:
        raise Ungueltig(
            "Schwacher Empfang: {werte} Prozent", werte=", ".join(str(x) for x in WLAN_SCHWACH)
        )
    wahl = daten.get("zugang_wahl") or "auto"
    if wahl not in zg.WAHLEN:
        raise Ungueltig("Zugang: {werte}", werte=", ".join(zg.WAHLEN))
    ersatz = daten.get("zugang_ersatz") or "auto"
    if ersatz not in zg.ERSATZ_WAHLEN:
        raise Ungueltig("Ersatzzugang: {werte}", werte=", ".join(zg.ERSATZ_WAHLEN))
    adresse = str(daten.get("zugang_adresse") or "").strip() or None
    if adresse is not None and not adresse_erlaubt(adresse):
        raise Ungueltig(
            "Adresse nicht erlaubt: nur private Adressen im eigenen Heimnetz (z. B. 192.168.0.1)"
        )
    return Einstellungen(
        _tarif(daten.get("tarif_down"), merke("Tarif Download")),
        _tarif(daten.get("tarif_up"), merke("Tarif Upload")),
        datum,
        int(schwach),
        wahl,
        adresse,
        ersatz,
    )
