"""Funkmasten aus OpenStreetMap (WU-0002): Ausschnitt, Abfrage an Overpass, Antwort lesen, passenden Mast finden.

OpenStreetMap kennt Masten als Bauwerke (`man_made=mast|tower` mit `tower:type=communication` oder
`communication:mobile_phone`), meist ohne Betreiber. Abgefragt wird ein großer Ausschnitt auf einem festen
Raster (Block von 0,2° plus Rand, etwa 44 × 30 km) – daraus lässt sich die Wohnung nur auf den Block von etwa
22 × 15 km eingrenzen. „Passt“ heißt: am nächsten am
geschätzten Mast der Zellen; ohne den der Mast, dessen Entfernung der laut Box am nächsten liegt.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from . import gemerkt
from .karte import Ort, entfernung_m

BLOCK = 0.2  # Grad: fester Block, in dem die Wohnung liegt (mehr verrät die Abfrage nicht)
RASTER = 0.1  # Grad: Rand um den Block
UMKREIS_M = 10_000  # nur Masten bis zu dieser Entfernung gehen an die Seite …
HOECHSTENS = 100  # … und davon die nächsten
GUELTIG_S = 30 * 86_400  # gefundene Masten einen Monat merken
NOCHMAL_S = 6 * 3600  # Overpass nicht erreichbar: in sechs Stunden noch einmal


@dataclass(frozen=True)
class OsmMast:
    ort: Ort
    betreiber: str | None = None


def rahmen(wohnung: Ort) -> tuple[float, float, float, float]:
    """Süd, West, Nord, Ost: ein Block von 0,2° auf festem Raster (etwa 22 × 15 km), in dem die Wohnung liegt, plus
    0,1° Rand rundum (Masten nahe der Blockgrenze). Für alle Wohnungen im selben Block gleich – mehr als den Block
    verrät die Abfrage nicht."""

    def block(x: float) -> int:
        return math.floor(x / BLOCK + 1e-9)  # 48.2 / 0.2 ist in Gleitkomma knapp über 241

    la, lo = block(wohnung.lat) * BLOCK, block(wohnung.lon) * BLOCK
    return (
        round(la - RASTER, 1),
        round(lo - RASTER, 1),
        round(la + BLOCK + RASTER, 1),
        round(lo + BLOCK + RASTER, 1),
    )


def abfrage(r: tuple[float, float, float, float]) -> str:
    """Overpass-QL für Funkmasten im Ausschnitt."""
    bb = ",".join(f"{x:.1f}" for x in r)
    return (
        "[out:json][timeout:60];("
        f'nwr["man_made"~"^(mast|tower)$"]["tower:type"="communication"]({bb});'
        f'nwr["communication:mobile_phone"]["communication:mobile_phone"!="no"]({bb});'
        ");out center tags;"
    )


def masten_aus(antwort: Mapping[str, Any]) -> list[OsmMast]:
    """Antwort von Overpass; Punkte, Linien und Flächen (dann deren Mitte)."""
    out: list[OsmMast] = []
    elemente = antwort.get("elements")
    for el in elemente if isinstance(elemente, list) else []:
        if not isinstance(el, dict):
            continue
        c = el.get("center")
        mitte: Mapping[str, Any] = c if isinstance(c, dict) else el
        try:
            lat, lon = float(mitte["lat"]), float(mitte["lon"])
        except KeyError, TypeError, ValueError:
            continue
        t = el.get("tags")
        tags: Mapping[str, Any] = t if isinstance(t, dict) else {}
        betreiber = str(tags.get("operator") or "").strip()[:60] or None
        out.append(OsmMast(Ort(lat, lon), betreiber))
    return out


NAH_AM_ZIEL_M = 1500  # so weit darf ein OSM-Mast vom geschätzten Mast weg sein
LAGE = "lage"  # passt zur geschätzten Lage des Masts
ENTFERNUNG = "entfernung"  # passt zur Entfernung laut Box


def passend(
    wohnung: Ort, masten: Sequence[OsmMast], ring_m: float | None, ziel: Ort | None = None
) -> tuple[int, str] | None:
    """Welcher OSM-Mast passt am besten, und warum?

    Ist der geschätzte Mast (aus den Zellen) bekannt, der ihm nächste OSM-Mast bis NAH_AM_ZIEL_M – die Entfernung laut
    Box schwankt je Zelle und Band stark (z. B. 1 km und 4 km für Sektoren derselben Sendeanlage). Sonst der
    Mast, dessen Entfernung am nächsten an der laut Box liegt. None, wenn keiner passt."""
    if not masten:
        return None
    if ziel is not None:
        d, i = min((entfernung_m(ziel, m.ort), i) for i, m in enumerate(masten))
        return (i, LAGE) if d <= NAH_AM_ZIEL_M else None
    if not ring_m:
        return None
    toleranz = max(300.0, 0.35 * ring_m)
    abstand, i = min((abs(entfernung_m(wohnung, m.ort) - ring_m), i) for i, m in enumerate(masten))
    return (i, ENTFERNUNG) if abstand <= toleranz else None


def faellig(eintrag: Mapping[str, Any] | None, kennung: str, jetzt: float) -> bool:
    """Neu abrufen? Nach einem Monat, nach einem Fehler nach NOCHMAL_S (siehe logik/gemerkt)."""
    return gemerkt.faellig(eintrag, kennung, jetzt, GUELTIG_S, NOCHMAL_S)


def in_der_naehe(wohnung: Ort, masten: Sequence[OsmMast]) -> list[OsmMast]:
    """Was an die Seite geht: Masten bis UMKREIS_M, die nächsten HOECHSTENS, nach Entfernung."""
    mit = sorted(((entfernung_m(wohnung, m.ort), m) for m in masten), key=lambda x: x[0])
    return [m for d, m in mit if d <= UMKREIS_M][:HOECHSTENS]


def fehlerantwort(antwort: Mapping[str, Any]) -> bool:
    """Overpass meldet Abbruch (Zeit, Speicher) als „remark“ bei Status 200 – dann ist die Liste unvollständig."""
    return "error" in str(antwort.get("remark") or "").lower()
