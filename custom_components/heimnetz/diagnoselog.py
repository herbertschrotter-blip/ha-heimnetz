"""Diagnose-Log (⚙ › Diagnose): nach jedem Abruf aufzeichnen, wenn der Schalter an ist. Fachlogik in `logik/diagnoselog.py`;
ein Fehler hier stört den Abruf nie. Die Einträge bleiben in der eigenen Datenbank, gesendet wird nichts."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import sprache
from .logik import diagnoselog as dl
from .logik import geraete as gr
from .logik import sammeln as sm
from .logik import warnungen as wn
from .logik import wlan as wl

if TYPE_CHECKING:
    from . import Laufzeit

LOGGER = logging.getLogger(__package__)
SEIT = "diagnoselog_seit"
AUSSTEHEND_HOECHSTENS = 2000


def aufnahme(stand: sm.Stand, warnungen: tuple[tuple[wn.Meldung, bool], ...]) -> dl.Aufnahme:
    """Stand eines Abrufs → Aufnahme (ohne IP-Adressen)."""
    w = stand.wlan
    funk = {f.mac: f for f in w.geraete} if w else {}
    baender = w.baender if w else ()
    geraete = []
    for mac, g in stand.geraete.items():
        f = funk.get(mac)
        band = wl.band_von(f, baender) if f else None
        geraete.append(
            dl.Geraetstand(
                mac,
                g.name,
                g.aktiv,
                gr.verbindung(g.art, g.aktiv, band, g.vpn),
                stand.anbindung.get(mac.upper(), ""),
                f.signal if f else None,
                f.mbit if f else None,
                mac.upper() in stand.mesh,
            )
        )
    m = stand.mobil
    zelle = (m.nr if m.technik == "5G-SA" and m.nr else m.haupt) if m else None
    return dl.Aufnahme(
        stand.zeit,
        stand.box_erreichbar,
        stand.pi.internet,
        tuple(geraete),
        m.technik if m else "",
        f"PCI {zelle.pci}" if zelle and zelle.pci is not None else "",
        zelle.rsrp if zelle else None,
        ", ".join(f"{b.band} GHz {b.kanal}" for b in baender if b.kanal),
        warnungen,
        tuple(
            (e.zeitpunkt.timestamp() if e.zeitpunkt else None, e.kategorie, e.text)
            for e in stand.protokoll
        ),
    )


class Diagnoselog:
    """Eine Instanz je Einrichtung (Laufzeit)."""

    def __init__(self, hass: HomeAssistant, lz: Laufzeit) -> None:
        self.hass, self.lz = hass, lz
        self.schreiber: dl.Schreiber | None = None
        self._ausstehend: list[dl.Eintrag] = []  # noch nicht geschrieben (Datenbank nicht bereit)

    async def abruf(self, stand: sm.Stand) -> None:
        if not self.lz.einstellungen.wert.diagnoselog:
            self.schreiber = None
            return
        try:
            self.schreiber = self.schreiber or dl.Schreiber()
            warnungen = self.lz.warnungen.letzte if self.lz.warnungen else ()
            self._ausstehend += self.schreiber.schritt(aufnahme(stand, warnungen))
            del self._ausstehend[:-AUSSTEHEND_HOECHSTENS]
            await self.hass.async_add_executor_job(
                self.lz.datenbank.diagnoselog_schreiben, list(self._ausstehend)
            )
            self._ausstehend.clear()
        except Exception:
            LOGGER.exception("Heimnetz: Diagnose-Log fehlgeschlagen")

    def _lesen(self) -> list[dl.Eintrag]:
        jetzt = dt_util.utcnow().timestamp()
        return self.lz.datenbank.diagnoselog_lesen(jetzt - dl.AUFBEWAHREN_S)

    def _ansicht(self, s: str) -> dict[str, Any]:
        seit = self.lz.datenbank.meta(SEIT)
        return {
            "an": self.lz.einstellungen.wert.diagnoselog,
            "seit": float(seit) if seit else None,
            "tage": dl.TAGE,
            **dl.anzeigen(self._lesen(), s),
        }

    async def ansicht(self) -> dict[str, Any]:
        return await self.hass.async_add_executor_job(self._ansicht, sprache(self.hass))

    async def setzen(self, an: bool) -> dict[str, Any]:
        await self.lz.einstellungen.async_setzen({"diagnoselog": an})
        if an:
            jetzt = dt_util.utcnow().timestamp()
            await self.hass.async_add_executor_job(self.lz.datenbank.meta_setzen, SEIT, str(jetzt))
        return await self.ansicht()

    async def loeschen(self) -> dict[str, Any]:
        await self.hass.async_add_executor_job(self.lz.datenbank.diagnoselog_loeschen)
        self._ausstehend.clear()
        self.schreiber = None  # nächster Eintrag beginnt mit „Aufzeichnung beginnt“
        return await self.ansicht()

    def _datei(self, s: str) -> dict[str, Any]:
        namen = [g.name for g in self.lz.abruf.data.geraete.values()]
        return dl.datei(self._lesen(), namen, dt_util.get_default_time_zone(), s)

    async def datei(self) -> dict[str, Any]:
        return await self.hass.async_add_executor_job(self._datei, sprache(self.hass))
