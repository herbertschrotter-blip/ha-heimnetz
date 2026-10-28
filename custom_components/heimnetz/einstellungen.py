"""Einstellungen der Seite im Integrations-Speicher (G-09): Tarif und „Auswerten ab“. Einziger Schreibweg ist
`async_setzen` (prüft über logik.einstellungen). Ohne gespeicherte Werte gibt es keinen Tarif.

WU-0006: Eine neue Installation (nichts gespeichert, nichts übernommen) startet mit dem zurückhaltenden Messplan
`messplan.NEU` und speichert ihn gleich – ändert sich die Vorgabe in einer späteren Fassung, bleibt der eigene Plan.
Übernommene Einstellungen bleiben, wie sie sind.

WU-0010: eigene Arten (`eigene_arten`) und Warnungen (`warnungen`) liegen als weitere Schlüssel im selben Speicher –
ohne neue Version, damit der Rückweg (`ausliefern.py --zurueck`) weiter lädt (die ältere Fassung kennt die Schlüssel
nicht und lässt Zuordnungen zu eigenen Arten beim Laden fallen)."""

from __future__ import annotations

import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable
from dataclasses import replace
from typing import Any, Concatenate

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .logik import arten as ar
from .logik import einstellungen as es
from .logik import messplan as mp
from .logik import warnungen as wn

LOGGER = logging.getLogger(__package__)
VERSION = 1


def _gesperrt[**P, R](
    f: Callable[Concatenate[Einstellungsdienst, P], Awaitable[R]],
) -> Callable[Concatenate[Einstellungsdienst, P], Awaitable[R]]:
    """WU-0010: ändernde Aufrufe nacheinander – jeder liest den Stand, prüft und speichert alles zusammen; zwei
    gleichzeitige (zwei Fenster, Doppeltipp) würden sonst die Änderung des anderen überschreiben."""

    @functools.wraps(f)
    async def mit_sperre(self: Einstellungsdienst, *args: P.args, **kwargs: P.kwargs) -> R:
        async with self._sperre:
            return await f(self, *args, **kwargs)

    return mit_sperre


class Einstellungsdienst:
    def __init__(self, hass: HomeAssistant, entry_id: str, neu: bool = True) -> None:
        self.hass = hass
        self._neu = neu  # False: Umstieg von der alten Integration – deren Plan gilt, auch „aus“
        self._store: Store[dict[str, Any]] = Store(hass, VERSION, f"{DOMAIN}.{entry_id}")
        self.wert = es.Einstellungen()
        self.plan = mp.Messplan()
        self.arten: dict[str, str] = {}  # Geräte-Kennung → selbst gewählte Art (AN-0001)
        self.eigene: dict[str, ar.EigeneArt] = {}  # WU-0010: Kennung „eigen:n“ → Symbol und Name
        self.warnungen = wn.Warneinstellungen()  # WU-0010
        self.letzte_serie: dict[str, Any] | None = None  # WU-0001: Ergebnis der letzten Serie
        self._sperre = asyncio.Lock()

    async def async_laden(self) -> None:
        gespeichert = await self._store.async_load()
        if gespeichert is None:
            if self._neu:
                await self._speichern(plan=mp.NEU)
                self.plan = mp.NEU
            return
        self.letzte_serie = gespeichert.get("letzte_serie")
        self.eigene = ar.eigene_aus(gespeichert.get("eigene_arten"))
        self.arten = {
            str(k): str(v)
            for k, v in (gespeichert.get("arten") or {}).items()
            if v in ar.TEXT or v in self.eigene
        }
        try:
            self.warnungen = wn.pruefen(gespeichert.get("warnungen") or {}, self.art_kennungen)
        except es.Ungueltig as err:
            LOGGER.warning("Heimnetz: gespeicherte Warnungen ungültig (%s), Vorgaben", err)
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

    @_gesperrt
    async def async_setzen(self, daten: dict[str, Any]) -> es.Einstellungen:
        """Prüfen und speichern; ungültig → es.Ungueltig mit verständlichem Text."""
        neu = es.pruefen({**self.wert.als_dict(), **daten}, dt_util.now().date())
        await self._speichern(wert=neu)
        self.wert = neu
        return neu

    @_gesperrt
    async def async_plan_setzen(self, daten: dict[str, Any]) -> mp.Messplan:
        """Messplan prüfen und speichern; ungültig → es.Ungueltig mit verständlichem Text."""
        neu = mp.pruefen({**self.plan.als_dict(), **daten})
        await self._speichern(plan=neu)
        self.plan = neu
        return neu

    @property
    def art_kennungen(self) -> list[str]:
        """Alle Arten: feste und eigene (WU-0010)."""
        return [*ar.TEXT, *self.eigene]

    @_gesperrt
    async def async_art_setzen(self, kennung: str, art: str | None) -> None:
        """Art eines Geräts selbst festlegen; None = wieder automatisch erkennen."""
        if art is not None and art not in self.art_kennungen:
            raise es.Ungueltig("art: {werte}", werte=", ".join(self.art_kennungen))
        arten = {k: v for k, v in self.arten.items() if k != kennung}
        if art is not None:
            arten[kennung] = art
        await self._speichern(arten=arten)
        self.arten = arten

    # ── WU-0010: eigene Arten ──
    @_gesperrt
    async def async_eigene_neu(self, symbol: str, name: str) -> str:
        eigene, kennung = ar.eigene_neu(self.eigene, symbol, name)
        await self._speichern(eigene=eigene)
        self.eigene = eigene
        return kennung

    @_gesperrt
    async def async_eigene_aendern(self, kennung: str, symbol: str, name: str) -> None:
        eigene = ar.eigene_aendern(self.eigene, kennung, symbol, name)
        await self._speichern(eigene=eigene)
        self.eigene = eigene

    @_gesperrt
    async def async_eigene_loeschen(self, kennung: str) -> int:
        """Eigene Art löschen: Geräte bekommen wieder die erkannte Art, ihr Schalter unter Warnungen fällt weg.
        Zurück: wie viele Geräte ihr zugeordnet waren."""
        if kennung not in self.eigene:
            raise es.Ungueltig("Diese eigene Art gibt es nicht (mehr)")
        eigene = {k: v for k, v in self.eigene.items() if k != kennung}
        arten = {k: v for k, v in self.arten.items() if v != kennung}
        w = self.warnungen
        warnungen = replace(w, arten={k: v for k, v in w.arten.items() if k != kennung})
        await self._speichern(eigene=eigene, arten=arten, warnungen=warnungen)
        n = len(self.arten) - len(arten)
        self.eigene, self.arten, self.warnungen = eigene, arten, warnungen
        return n

    # ── WU-0010: Warnungen ──
    @_gesperrt
    async def async_warnungen_setzen(
        self, daten: dict[str, Any], dienste: list[str], sprache: str
    ) -> wn.Warneinstellungen:
        """Ziel, Verzögerung, Schalter; `art`/`an` schaltet eine Art. Ungültig → es.Ungueltig."""
        alt = self.warnungen.als_dict()
        if "art" in daten:
            if daten["art"] not in self.art_kennungen:
                raise es.Ungueltig("Diese Art gibt es nicht (mehr)")
            alt["arten"] = {**alt["arten"], daten["art"]: bool(daten.get("an"))}
        werte = {
            k: daten[k] for k in ("ziel", "verzoegerung", "wieder", "neu", "internet") if k in daten
        }
        # ob der Dienst da ist, nur beim Wählen des Ziels prüfen – ein gerade fehlender sperrt sonst alle Schalter
        neu = wn.pruefen(
            {**alt, **werte, "sprache": sprache},
            self.art_kennungen,
            dienste if "ziel" in daten else None,
        )
        await self._speichern(warnungen=neu)
        self.warnungen = neu
        return neu

    @_gesperrt
    async def async_warnung_geraet(self, kennung: str, wert: str) -> None:
        """Ausnahme eines Geräts: immer/nie melden, „gruppe“ = wie seine Art."""
        if wert not in (*wn.AUSNAHMEN, wn.GRUPPE):
            raise es.Ungueltig("Warnen: wie Gruppe, immer oder nie")
        w = self.warnungen
        geraete = {k: v for k, v in w.geraete.items() if k != kennung}
        if wert != wn.GRUPPE:
            geraete[kennung] = wert
        neu = replace(w, geraete=geraete)
        await self._speichern(warnungen=neu)
        self.warnungen = neu

    @_gesperrt
    async def async_serie_merken(self, ergebnis: dict[str, Any]) -> None:
        await self._speichern(letzte_serie=ergebnis)
        self.letzte_serie = ergebnis

    async def _speichern(
        self,
        wert: es.Einstellungen | None = None,
        plan: mp.Messplan | None = None,
        arten: dict[str, str] | None = None,
        letzte_serie: dict[str, Any] | None = None,
        eigene: dict[str, ar.EigeneArt] | None = None,
        warnungen: wn.Warneinstellungen | None = None,
    ) -> None:
        """Alles zusammen speichern; im Speicher übernimmt der Aufrufer erst danach (Speicher == gespeichert)."""
        await self._store.async_save(
            {
                **(wert or self.wert).als_dict(),
                "messplan": (plan or self.plan).als_dict(),
                "arten": self.arten if arten is None else arten,
                "letzte_serie": self.letzte_serie if letzte_serie is None else letzte_serie,
                "eigene_arten": {
                    k: e.als_dict() for k, e in (self.eigene if eigene is None else eigene).items()
                },
                "warnungen": (warnungen or self.warnungen).als_dict(),
            }
        )

    async def async_entfernen(self) -> None:
        await self._store.async_remove()
