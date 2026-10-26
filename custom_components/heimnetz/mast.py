"""Standort der Zellen bei OpenCellID (nur mit eigenem Schlüssel, Optionen) und BeaconDB (ohne Schlüssel) nachschlagen.

Nach außen geht nur die Kennung der Zelle (MCC, MNC, TAC, Zellkennung), bei OpenCellID dazu der Schlüssel, nie der
Standort der Wohnung (die Kartenkacheln holt der Browser, siehe Seite). Ergebnisse bleiben im Integrations-Speicher
(gefunden einen Monat, nicht erreichbar eine Stunde, sonst einen Tag); gefragt wird nur, wenn die Seite den Mobilfunk
zeigt. Je Zelle zählt der genaueste Fund der beiden Dienste (logik/karte.fund).
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from collections.abc import Awaitable, Sequence
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .const import CONF_OPENCELLID, DOMAIN
from .logik import karte as ka

LOGGER = logging.getLogger(__package__)
URL = "https://opencellid.org/cell/get"
BEACONDB_URL = "https://api.beacondb.net/v1/geolocate"
ZEIT_S = 8  # die Seite wartet darauf – lieber später noch einmal
GLEICHZEITIG = 4  # höchstens so viele Anfragen auf einmal (viele Zellen, leerer Speicher)
OHNE_ID = "-"  # BeaconDB braucht keinen Schlüssel: Gemerktes hängt an keinem
KOPF = {
    "User-Agent": "HomeAssistant-Heimnetz"
}  # BeaconDB bittet Programme, sich zu erkennen zu geben


class Mastsuche:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}.mast")
        self._merk: dict[str, Any] | None = None
        self._sperre = asyncio.Lock()

    async def suchen(self, kennungen: Sequence[ka.Kennung]) -> dict[str, ka.Fund]:
        """Ergebnis je Kennung (Schlüssel: Kennung.schluessel); fragt nur, was nicht frisch gemerkt ist."""
        schluessel = (self.entry.options.get(CONF_OPENCELLID) or "").strip()
        sid = hashlib.sha256(schluessel.encode()).hexdigest()[:8] if schluessel else ""
        eindeutig = list({k.schluessel: k for k in kennungen}.values())
        async with self._sperre:
            if self._merk is None:
                self._merk = await self._store.async_load() or {}
            jetzt = time.time()
            fragen: list[tuple[str, str, Awaitable[dict[str, Any]]]] = []
            for k in eindeutig:
                if schluessel and ka.faellig(self._merk.get(k.schluessel), jetzt, sid):
                    fragen.append((k.schluessel, sid, self._opencellid(k, schluessel)))
                if ka.faellig(self._merk.get(_b(k)), jetzt, OHNE_ID):
                    fragen.append((_b(k), OHNE_ID, self._beacondb(k)))
            if fragen:
                platz = asyncio.Semaphore(GLEICHZEITIG)

                async def begrenzt(f: Awaitable[dict[str, Any]]) -> dict[str, Any]:
                    async with platz:
                        return await f

                antworten = await asyncio.gather(*(begrenzt(f) for _, _, f in fragen))
                neu = {
                    name: {**a, "t": jetzt, "schluessel": s}
                    for (name, s, _), a in zip(fragen, antworten, strict=True)
                }
                self._merk = {**ka.aufraeumen(self._merk, jetzt), **neu}
                await self._store.async_save(self._merk)
            merk = self._merk
        return {
            k.schluessel: ka.fund(
                merk.get(k.schluessel) if schluessel else None, merk.get(_b(k)), bool(schluessel)
            )
            for k in eindeutig
        }

    async def _holen(
        self, dienst: str, methode: str, url: str, **kw: Any
    ) -> tuple[int, dict[str, Any]] | None:
        """Eine Anfrage; None, wenn der Dienst nicht erreichbar war (nur die Art des Fehlers ins Protokoll – die
        Adresse von OpenCellID enthält den Schlüssel)."""
        try:
            async with async_get_clientsession(self.hass).request(
                methode, url, timeout=aiohttp.ClientTimeout(total=ZEIT_S), **kw
            ) as antwort:
                daten = await antwort.json(content_type=None)
                return antwort.status, daten if isinstance(daten, dict) else {}
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            LOGGER.warning("Heimnetz: %s nicht erreichbar (%s)", dienst, type(err).__name__)
            return None

    async def gemerkte_anlagen(self) -> dict[tuple[int, str], list[ka.Mast]]:
        """Früher gefundene Zellen je Sendeanlage (für den geschätzten Mast bei unbekanntem Sektor)."""
        if self._merk is None:
            self._merk = await self._store.async_load() or {}
        return ka.gemerkte_anlagen(self._merk)

    async def _opencellid(self, k: ka.Kennung, schluessel: str) -> dict[str, Any]:
        params = {
            "key": schluessel,
            "mcc": k.mcc,
            "mnc": k.mnc,
            "lac": k.lac,
            "cellid": k.cellid,
            "radio": k.radio,
            "format": "json",
        }
        if (r := await self._holen(ka.OPENCELLID, "GET", URL, params=params)) is None:
            return {"stand": ka.FEHLER}
        status, daten = r
        mast = ka.mast_aus(daten) if status == 200 else None
        if mast is None:
            stand = ka.stand_aus(daten)
            # unbekannte Zelle ist normal; Tageslimit oder abgelehnter Schlüssel gehören ins Protokoll
            (LOGGER.debug if stand == ka.NICHT_GEFUNDEN else LOGGER.warning)(
                "Heimnetz: OpenCellID ohne Standort (HTTP %s, %s)",
                status,
                str(daten.get("error", ""))[:80],
            )
            return {"stand": stand}
        return {"lat": mast.ort.lat, "lon": mast.ort.lon, "genau": mast.genau_m}

    async def _beacondb(self, k: ka.Kennung) -> dict[str, Any]:
        anfrage = {
            "considerIp": False,  # nur die Zelle, nie die eigene Adresse als Ort
            "fallbacks": {"lacf": False, "ipf": False},
            "cellTowers": [
                {
                    "radioType": k.radio.lower(),
                    "mobileCountryCode": k.mcc,
                    "mobileNetworkCode": k.mnc,
                    "locationAreaCode": k.lac,
                    "cellId": k.cellid,
                }
            ],
        }
        r = await self._holen(ka.BEACONDB, "POST", BEACONDB_URL, json=anfrage, headers=KOPF)
        if r is None:
            return {"stand": ka.FEHLER}
        status, daten = r
        mast = ka.beacondb_aus(daten) if status == 200 else None
        if mast is None:
            if status not in (200, 404):
                LOGGER.warning("Heimnetz: BeaconDB ohne Standort (HTTP %s)", status)
            return {"stand": ka.NICHT_GEFUNDEN if status in (200, 404) else ka.FEHLER}
        return {"lat": mast.ort.lat, "lon": mast.ort.lon, "genau": mast.genau_m}

    async def async_entfernen(self) -> None:
        await self._store.async_remove()


def _b(k: ka.Kennung) -> str:
    return f"beacondb:{k.schluessel}"
