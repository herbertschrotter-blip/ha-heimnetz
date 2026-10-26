"""Einstellungen der Seite im Integrations-Speicher (G-09): Tarif und „Auswerten ab“. Einziger Schreibweg ist
`async_setzen` (prüft über logik.einstellungen). Ohne gespeicherte Werte gibt es keinen Tarif.

WU-0006: Eine neue Installation (nichts gespeichert, nichts übernommen) startet mit dem zurückhaltenden Messplan
`messplan.NEU` und speichert ihn gleich – ändert sich die Vorgabe in einer späteren Fassung, bleibt der eigene Plan.
Übernommene Einstellungen bleiben, wie sie sind."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .logik import arten as ar
from .logik import einstellungen as es
from .logik import messplan as mp

LOGGER = logging.getLogger(__package__)
VERSION = 1


class Einstellungsdienst:
    def __init__(self, hass: HomeAssistant, entry_id: str, neu: bool = True) -> None:
        self.hass = hass
        self._neu = neu  # False: Umstieg von der alten Integration – deren Plan gilt, auch „aus“
        self._store: Store[dict[str, Any]] = Store(hass, VERSION, f"{DOMAIN}.{entry_id}")
        self.wert = es.Einstellungen()
        self.plan = mp.Messplan()
        self.arten: dict[str, str] = {}  # Geräte-Kennung → selbst gewählte Art (AN-0001)
        self.letzte_serie: dict[str, Any] | None = None  # WU-0001: Ergebnis der letzten Serie

    async def async_laden(self) -> None:
        gespeichert = await self._store.async_load()
        if gespeichert is None:
            if self._neu:
                await self._speichern(plan=mp.NEU)
                self.plan = mp.NEU
            return
        self.letzte_serie = gespeichert.get("letzte_serie")
        self.arten = {
            str(k): str(v) for k, v in (gespeichert.get("arten") or {}).items() if v in ar.TEXT
        }
        try:
            self.plan = mp.pruefen(gespeichert.get("messplan"))
        except es.Ungueltig as err:
            LOGGER.warning("Heimnetz: gespeicherter Messplan ungültig (%s), Plan aus", err)
        try:
            self.wert = es.pruefen(gespeichert, dt_util.now().date())
        except es.Ungueltig as err:
            LOGGER.warning(
                "Heimnetz: gespeicherte Einstellungen ungültig (%s), ohne Tarif weiter", err
            )

    async def async_setzen(self, daten: dict[str, Any]) -> es.Einstellungen:
        """Prüfen und speichern; ungültig → es.Ungueltig mit verständlichem Text."""
        neu = es.pruefen({**self.wert.als_dict(), **daten}, dt_util.now().date())
        await self._speichern(wert=neu)
        self.wert = neu
        return neu

    async def async_plan_setzen(self, daten: dict[str, Any]) -> mp.Messplan:
        """Messplan prüfen und speichern; ungültig → es.Ungueltig mit verständlichem Text."""
        neu = mp.pruefen({**self.plan.als_dict(), **daten})
        await self._speichern(plan=neu)
        self.plan = neu
        return neu

    async def async_art_setzen(self, kennung: str, art: str | None) -> None:
        """Art eines Geräts selbst festlegen; None = wieder automatisch erkennen."""
        if art is not None and art not in ar.TEXT:
            raise es.Ungueltig("art: {werte}", werte=", ".join(ar.TEXT))
        arten = {k: v for k, v in self.arten.items() if k != kennung}
        if art is not None:
            arten[kennung] = art
        await self._speichern(arten=arten)
        self.arten = arten

    async def async_serie_merken(self, ergebnis: dict[str, Any]) -> None:
        await self._speichern(letzte_serie=ergebnis)
        self.letzte_serie = ergebnis

    async def _speichern(
        self,
        wert: es.Einstellungen | None = None,
        plan: mp.Messplan | None = None,
        arten: dict[str, str] | None = None,
        letzte_serie: dict[str, Any] | None = None,
    ) -> None:
        """Alles zusammen speichern; im Speicher übernimmt der Aufrufer erst danach (Speicher == gespeichert)."""
        await self._store.async_save(
            {
                **(wert or self.wert).als_dict(),
                "messplan": (plan or self.plan).als_dict(),
                "arten": self.arten if arten is None else arten,
                "letzte_serie": self.letzte_serie if letzte_serie is None else letzte_serie,
            }
        )

    async def async_entfernen(self) -> None:
        await self._store.async_remove()
