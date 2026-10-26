"""Funkmasten aus OpenStreetMap über Overpass holen – im Hintergrund, einmal im Monat (WU-0002).

Hinaus geht nur ein großer Ausschnitt auf festem Raster (logik/osm.rahmen), nie der Standort der Wohnung.
"""

from __future__ import annotations

from typing import Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .gemerkt import GemerkterAbruf
from .logik import karte as ka
from .logik import osm as lo

OVERPASS = "https://overpass-api.de/api/interpreter"
KOPF = {
    "User-Agent": "HomeAssistant-Heimnetz"
}  # Overpass bittet Programme, sich zu erkennen zu geben
ZEIT_S = 90


class OsmMasten(GemerkterAbruf):
    NAME = "OpenStreetMap (Overpass)"
    SPEICHER = "osm"
    FELD = "masten"
    GUELTIG_S = lo.GUELTIG_S
    NOCHMAL_S = lo.NOCHMAL_S

    async def masten(self, wohnung: ka.Ort) -> list[lo.OsmMast]:
        """Gemerkte Masten im Ausschnitt um die Wohnung; stößt bei Bedarf das Holen im Hintergrund an."""
        r = lo.rahmen(wohnung)
        liste = await self._gemerkt(",".join(f"{x:.1f}" for x in r), r)
        return [lo.OsmMast(ka.Ort(lat, lon), betreiber) for lat, lon, betreiber in liste]

    async def _abrufen(self, *args: Any) -> list[Any]:
        (r,) = args
        async with async_get_clientsession(self.hass).post(
            OVERPASS,
            data={"data": lo.abfrage(r)},
            headers=KOPF,
            timeout=aiohttp.ClientTimeout(total=ZEIT_S),
        ) as antwort:
            antwort.raise_for_status()
            daten = await antwort.json(content_type=None)
        daten = daten if isinstance(daten, dict) else {}
        if lo.fehlerantwort(daten):
            raise ValueError("Overpass: Abfrage abgebrochen")
        return [[m.ort.lat, m.ort.lon, m.betreiber] for m in lo.masten_aus(daten)]
