"""OpenCellID-Datenabzug (WU-0002): Zellen eines Landes lesen und Funkmasten aus OpenStreetMap Anbieter und Technik
zuordnen.

Der Abzug ist eine CSV-Datei (gzip) mit radio,mcc,net,area,cell,unit,lon,lat,range,samples,changeable,created,
updated,averageSignal. Die Orte sind Mittel aus Messungen von Nutzern, nicht die Masten selbst – Zellen in höchstens
ZUORDNUNG_M um einen OSM-Mast gelten als „wohl an diesem Mast“. Geladen wird das ganze Land, ausgewertet hier; der
eigene Standort geht dabei nicht hinaus.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from . import gemerkt
from .karte import Ort, entfernung_m

GUELTIG_S = 30 * 86_400  # Abzug einen Monat merken
NOCHMAL_S = 86_400  # Fehler (Limit, Schlüssel, nicht erreichbar): morgen wieder
ZUORDNUNG_M = 500  # Zellen bis zu dieser Entfernung zählen zu einem Mast
# Netzkennungen in Österreich (MCC 232); unbekannte erscheinen als „Netz 232 xx“
# 07 tele.ring und 13 gehören zu Magenta, 11/12 sind Marken von A1 (bob, yesss!), 91 ist der Zugfunk der ÖBB
ANBIETER = {
    1: "A1",
    3: "Magenta",
    5: "Drei",
    7: "Magenta",
    10: "Drei",
    11: "A1",
    12: "A1",
    13: "Magenta",
    91: "ÖBB",
}
TECHNIK = {"GSM": "2G", "UMTS": "3G", "LTE": "LTE", "NR": "5G"}
REIHENFOLGE = ("2G", "3G", "LTE", "5G")


@dataclass(frozen=True)
class OcidZelle:
    technik: str  # 2G, 3G, LTE, 5G
    mnc: int
    ort: Ort


def anbieter(mnc: int) -> str:
    return ANBIETER.get(mnc, f"Netz 232 {mnc:02d}")


def zellen_aus(zeilen: Iterable[str], rahmen: tuple[float, float, float, float]) -> list[OcidZelle]:
    """CSV-Zeilen (mit oder ohne Kopfzeile) → Zellen im Ausschnitt Süd, West, Nord, Ost; Unlesbares fällt weg."""
    s, w, n, o = rahmen
    out: list[OcidZelle] = []
    for feld in csv.reader(zeilen):
        if len(feld) < 8 or feld[0] == "radio":
            continue
        technik = TECHNIK.get(feld[0].strip().upper())
        try:
            mnc, lon, lat = int(feld[2]), float(feld[6]), float(feld[7])
        except ValueError:
            continue
        if technik and s <= lat <= n and w <= lon <= o:
            out.append(OcidZelle(technik, mnc, Ort(lat, lon)))
    return out


def ist_csv(anfang: bytes) -> bool:
    """Liefert OpenCellID statt der Datei eine Fehlermeldung (Limit, Schlüssel)? Eine CSV beginnt mit „radio,“ oder
    einer Technik."""
    kopf = anfang[:16].decode("ascii", "replace").lower()
    return kopf.startswith(("radio,", "gsm,", "umts,", "lte,", "nr,", "cdma,"))


@dataclass(frozen=True)
class MastInfo:
    anbieter: tuple[str, ...]
    technik: tuple[str, ...]
    zellen: int


def je_mast(masten: Sequence[Ort], zellen: Sequence[OcidZelle]) -> list[MastInfo | None]:
    """Je Mast: Anbieter und Technik der Zellen in höchstens ZUORDNUNG_M; None, wenn dort keine Zelle bekannt ist.
    Eine Zelle zählt nur zum nächsten Mast."""
    gruppen: list[list[OcidZelle]] = [[] for _ in masten]
    if not masten:
        return []
    # grob vorsieben: nur Zellen im Rechteck um alle Masten (plus Rand) genau rechnen
    rand = ZUORDNUNG_M / 111_000 * 2
    s_, n_ = min(m.lat for m in masten) - rand, max(m.lat for m in masten) + rand
    breite = rand / max(math.cos(math.radians((s_ + n_) / 2)), 0.2)  # Längengrade sind schmaler
    w_, o_ = min(m.lon for m in masten) - breite, max(m.lon for m in masten) + breite
    for z in zellen:
        if not (s_ <= z.ort.lat <= n_ and w_ <= z.ort.lon <= o_):
            continue
        d, i = min((entfernung_m(m, z.ort), i) for i, m in enumerate(masten))
        if d <= ZUORDNUNG_M:
            gruppen[i].append(z)
    out: list[MastInfo | None] = []
    for g in gruppen:
        if not g:
            out.append(None)
            continue
        namen = sorted({anbieter(z.mnc) for z in g})
        technik = [t for t in REIHENFOLGE if any(z.technik == t for z in g)]
        out.append(MastInfo(tuple(namen), tuple(technik), len(g)))
    return out


def faellig(eintrag: Mapping[str, Any] | None, kennung: str, jetzt: float) -> bool:
    """Neu abrufen? Nach einem Monat, nach einem Fehler nach NOCHMAL_S (siehe logik/gemerkt)."""
    return gemerkt.faellig(eintrag, kennung, jetzt, GUELTIG_S, NOCHMAL_S)
