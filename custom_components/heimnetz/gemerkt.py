"""Gemerkter Abruf aus dem Netz, im Hintergrund (OSM-Masten, OpenCellID-Abzug).

Die Seite bekommt sofort, was gemerkt ist; ist es alt oder fehlt es, holt die Integration es nebenbei, und die nächste
Anzeige hat es. Ein Fehler wird mit Zeit gemerkt (`fehler_t`), damit nie eine Dauerschleife entsteht; ins Protokoll
kommt nur die Art des Fehlers (Adressen und Antworten können Schlüssel enthalten).
"""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .logik import gemerkt as lg

LOGGER = logging.getLogger(__package__)


class GemerkterAbruf:
    NAME = ""  # für Protokoll und Aufgabe
    SPEICHER = ""  # heimnetz.<Eintrag>.<SPEICHER>
    FELD = ""  # Liste im Speicher
    GUELTIG_S = 30 * 86_400
    NOCHMAL_S = 86_400

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(
            hass, 1, f"{DOMAIN}.{entry.entry_id}.{self.SPEICHER}"
        )
        self._merk: dict[str, Any] | None = None
        self._laeuft = False

    async def _gemerkt(self, kennung: str, *args: Any) -> list[Any]:
        """Gemerkte Liste zu dieser Kennung (sonst leer); stößt bei Bedarf den Abruf im Hintergrund an."""
        if self._merk is None:
            self._merk = await self._store.async_load() or {}
        if (
            lg.faellig(self._merk, kennung, time.time(), self.GUELTIG_S, self.NOCHMAL_S)
            and not self._laeuft
        ):
            self._laeuft = True
            self.entry.async_create_background_task(
                self.hass, self._lauf(kennung, *args), f"heimnetz_{self.SPEICHER}"
            )
        if self._merk.get("rahmen") != kennung:
            return []
        liste = self._merk.get(self.FELD, [])
        return liste if isinstance(liste, list) else []

    @property
    def stand(self) -> tuple[Any, Any]:
        """Woran man erkennt, dass sich das Gemerkte geändert hat (für Zwischenergebnisse)."""
        m = self._merk or {}
        return m.get("rahmen"), m.get("t")

    async def _abrufen(self, *args: Any) -> list[Any]:
        raise NotImplementedError

    async def _lauf(self, kennung: str, *args: Any) -> None:
        alt = self._merk or {}
        try:
            liste = await self._abrufen(*args)
            self._merk = {"rahmen": kennung, "t": time.time(), self.FELD: liste}
        except Exception as err:  # noqa: BLE001 – jeder Fehler: später noch einmal, nie Dauerschleife
            LOGGER.warning("Heimnetz: %s nicht geladen (%s)", self.NAME, type(err).__name__)
            # bisheriges behalten (gleiche Kennung), später noch einmal
            behalten = alt if alt.get("rahmen") == kennung else {"rahmen": kennung, self.FELD: []}
            self._merk = {**behalten, "fehler_t": time.time()}
        finally:
            self._laeuft = False
        await self._store.async_save(self._merk)

    async def async_entfernen(self) -> None:
        await self._store.async_remove()
