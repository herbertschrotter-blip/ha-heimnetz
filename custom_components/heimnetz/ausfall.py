"""Ausfälle des Pi verstehen (Herbert, 18.11.2026) – dünner HA-Teil zu `logik/ausfall.py`.

- Herzschlag jede Minute und Marke beim Beenden in `heimnetz/lauf.json` (nicht in der Datenbank: deren Schreiben
  wartet während einer Sicherung).
- Alle 5 Minuten Speicher je Programm über den Supervisor (Home Assistant, Supervisor, jedes laufende Add-on) und
  /proc/meminfo; knapp → Warnung (höchstens einmal je Stunde).
- Beim Start: endete der vorige Lauf nicht sauber, nach 3 Minuten (dann hat der Wächter seine Steckdosen gelesen) ein
  Ausfallbericht ins Journal (Art „waechter“, erscheint im Reiter Wächter) und als Warnung.

Nur lesend gegenüber dem Supervisor (Statistik, Liste der Add-ons, Systemprotokoll des vorigen Starts). Ohne
Supervisor (Home Assistant Container) bleibt es beim Herzschlag und dem Speicher aus /proc/meminfo.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .const import sprache_system
from .logik import ausfall as af
from .logik import waechter as wa
from .logik.ereignis import WARNUNG, Ereignis
from .logik.sprache import t

if TYPE_CHECKING:
    from . import Laufzeit

LOGGER = logging.getLogger(__package__)
BERICHT_NACH_S = 180
ZEIT_S = 15
MEMINFO = "/proc/meminfo"
LAUF = "heimnetz/lauf.json"  # Herzschlag und Marke für ein sauberes Ende


class Supervisor:
    """Lesender Zugang zum Supervisor (nur unter Home Assistant OS / Supervised)."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.adresse = os.environ.get("SUPERVISOR")
        self.token = os.environ.get("SUPERVISOR_TOKEN")

    @property
    def da(self) -> bool:
        return bool(self.adresse and self.token)

    async def _get(self, pfad: str, text: bool = False) -> Any:
        async with async_get_clientsession(self.hass).get(
            f"http://{self.adresse}{pfad}",
            headers={
                "Authorization": f"Bearer {self.token}",
                **({"Accept": "text/plain"} if text else {}),
            },
            timeout=aiohttp.ClientTimeout(total=ZEIT_S),
        ) as antwort:
            antwort.raise_for_status()
            return await antwort.text() if text else (await antwort.json()).get("data")

    async def _mb(self, pfad: str) -> int | None:
        """Belegt in MB laut einer Statistik; nicht lesbar → None (ein fehlendes Add-on kostet nicht den Rest)."""
        try:
            return int((await self._get(pfad))["memory_usage"]) // (1024 * 1024)
        except aiohttp.ClientError, TimeoutError, KeyError, TypeError, ValueError:
            return None

    async def speicher(self) -> dict[str, int]:
        """Belegter Speicher in MB je Programm (gleichzeitig gefragt)."""
        namen = [af.HA, af.SUPERVISOR]
        pfade = ["/core/stats", "/supervisor/stats"]
        try:
            addons = (await self._get("/addons")).get("addons", [])
        except aiohttp.ClientError, TimeoutError, KeyError, TypeError, ValueError:
            addons = []
        for a in addons:
            if a.get("state") == "started":
                namen.append(str(a.get("name") or a["slug"]))
                pfade.append(f"/addons/{a['slug']}/stats")
        werte = await asyncio.gather(*(self._mb(p) for p in pfade))
        return {n: w for n, w in zip(namen, werte, strict=True) if w is not None}

    async def pi_start(self) -> float | None:
        info = await self._get("/host/info")
        us = info.get("boot_timestamp")
        return us / 1_000_000 if us else None

    async def voriger_boot(self) -> str:
        return str(await self._get("/host/logs/boots/-1?lines=20000", text=True))


class Ausfalldienst:
    def __init__(self, hass: HomeAssistant, lz: Laufzeit) -> None:
        self.hass, self.lz = hass, lz
        self.sv = Supervisor(hass)
        self._herz = 0.0
        self._speicher = 0.0
        self._gewarnt = 0.0
        self.letzter: af.Speicherstand | None = None
        self._vorher: tuple[float | None, float | None] = (None, None)
        self._gestoppt = False
        # eigene kleine Datei statt der Datenbank: unabhängig von deren Sperre während einer Sicherung
        self.datei = Path(hass.config.path(LAUF))

    def _lauf_lesen(self) -> tuple[float | None, float | None]:
        try:
            d = json.loads(self.datei.read_text(encoding="utf-8"))
            return (_zahl(d.get("lebt")), _zahl(d.get("sauber")))
        except OSError, ValueError, AttributeError:
            return (None, None)

    def _lauf_schreiben(self, lebt: float, sauber: float | None) -> None:
        self.datei.parent.mkdir(parents=True, exist_ok=True)
        neu = self.datei.with_suffix(".neu")
        neu.write_text(json.dumps({"lebt": lebt, "sauber": sauber}), encoding="utf-8")
        neu.replace(self.datei)

    async def start(self) -> None:
        """Vor dem ersten Abruf: Stand des vorigen Laufs merken, Herzschlag beginnen, Bericht planen."""
        self._vorher = await self.hass.async_add_executor_job(self._lauf_lesen)
        self.lz.abruf.config_entry.async_on_unload(
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._beendet)
        )
        if af.Lage(time.time(), *self._vorher, pi_start=None).unsauber:
            self.lz.abruf.config_entry.async_create_background_task(
                self.hass, self._bericht_spaeter(), "heimnetz_ausfallbericht"
            )
        self._herz = time.time()
        await self.hass.async_add_executor_job(self._lauf_schreiben, self._herz, None)

    def beenden(self) -> None:
        """Sauberes Ende (Home Assistant hält an, Integration wird entladen): kein Herzschlag mehr, Marke setzen.
        Blockierend – im Executor oder beim Entladen vor dem Schließen der Datenbank."""
        if self._gestoppt:
            return
        self._gestoppt = True
        try:
            self._lauf_schreiben(self._herz, time.time())
        except OSError as err:
            LOGGER.warning("Heimnetz: Marke für sauberes Ende nicht geschrieben: %s", err)

    async def _beendet(self, _event: Event) -> None:
        await self.hass.async_add_executor_job(self.beenden)

    # ── im Takt des Abrufs ──

    async def abruf(self) -> None:
        if self._gestoppt:
            return  # nach dem Anhalten kein Herzschlag mehr (ein noch laufender Abruf darf „lebt“ nicht erneuern)
        jetzt = time.time()
        if jetzt - self._herz >= af.HERZSCHLAG_S:
            self._herz = jetzt
            await self.hass.async_add_executor_job(self._lauf_schreiben, jetzt, None)
        if jetzt - self._speicher >= af.SPEICHER_TAKT_S:
            self._speicher = jetzt
            self.lz.abruf.config_entry.async_create_background_task(
                self.hass, self._speicher_lesen(jetzt), "heimnetz_speicher"
            )

    async def _speicher_lesen(self, jetzt: float) -> None:
        try:
            text = await self.hass.async_add_executor_job(_lesen, MEMINFO)
            gesamt, frei, swap, swap_frei = af.meminfo(text)
            wer = await self.sv.speicher() if self.sv.da else {}
        except (OSError, aiohttp.ClientError, TimeoutError, KeyError, ValueError) as err:
            LOGGER.debug("Heimnetz: Speicher nicht lesbar: %s", err)
            return
        s = af.Speicherstand(jetzt, gesamt, frei, swap, swap_frei, wer)
        self.letzter = s
        try:
            await self.hass.async_add_executor_job(self.lz.datenbank.speicherstand_schreiben, s)
        except (
            sqlite3.Error,
            OSError,
            RuntimeError,
        ) as err:  # Datenbank klemmt oder ist schon zu (Entladen)
            LOGGER.debug("Heimnetz: Speicherstand nicht geschrieben: %s", err)
        if af.knapp(s) and jetzt - self._gewarnt >= af.WARN_ABSTAND_S:
            self._gewarnt = jetzt
            sp = sprache_system(self.hass)
            self.lz.abruf.journal_merken([Ereignis(wa_art(), WARNUNG, af.knapp_text(s, sp))])
            if self.lz.warnungen is not None:
                await self.lz.warnungen.waechter_melden(lambda s_: af.knapp_text(s, s_), af.HA)

    # ── Bericht ──

    async def _bericht_spaeter(self) -> None:
        await asyncio.sleep(BERICHT_NACH_S)
        try:
            await self.bericht()
        except Exception:  # ein Bericht darf nie die Integration stören
            LOGGER.exception("Heimnetz: Ausfallbericht")

    async def bericht(self) -> list[str] | None:
        lebt, sauber = self._vorher
        jetzt = time.time()
        pi_start = boot = None
        if self.sv.da:
            try:
                pi_start = await self.sv.pi_start()
                if pi_start is not None and lebt is not None and pi_start > lebt:
                    # bis 20 000 Zeilen: im Executor auswerten, nicht im Event-Loop
                    roh = await self.sv.voriger_boot()
                    boot = await self.hass.async_add_executor_job(af.boot_auswerten, roh)
            except (aiohttp.ClientError, TimeoutError, KeyError, ValueError) as err:
                LOGGER.debug("Heimnetz: Supervisor für den Ausfallbericht nicht lesbar: %s", err)
        speicher = (
            await self.hass.async_add_executor_job(self.lz.datenbank.speicherstand_vor, lebt)
            if lebt is not None
            else None
        )
        sp = sprache_system(self.hass)
        lage = af.Lage(jetzt, lebt, sauber, pi_start, boot, speicher, tuple(self._dose(lebt, sp)))
        zeilen = af.bericht(lage, dt_util.get_default_time_zone(), sp)
        if not zeilen:
            return None
        text = t("Ausfall: {text}", sp, text=" · ".join(zeilen))
        self.lz.abruf.journal_merken([Ereignis(wa_art(), WARNUNG, text)])
        if self.lz.warnungen is not None:
            tz = dt_util.get_default_time_zone()
            await self.lz.warnungen.waechter_melden(
                lambda s_: t(
                    "Ausfall: {text}", s_, text=" · ".join(af.bericht(lage, tz, s_) or [])
                ),
                af.HA,
            )
        return zeilen

    def _dose(self, lebt: float | None, sprache: str) -> list[str]:
        """Was die Steckdosen der Wächter für Home Assistant seit kurz vor dem Ausfall festhielten."""
        if lebt is None or self.lz.waechter is None:
            return []
        aus = []
        for w in self.lz.waechter.liste:
            if w.art != "ha":
                continue
            for i, _ in w.dosen:
                stand = self.lz.waechter.staende.get((w.id, i))
                for e in stand.letzte if stand else ():
                    if e.get("was") in ("strom", "pause") and float(e.get("t") or 0) >= lebt - 3600:
                        aus.append(
                            t(
                                "Steckdose: {text}",
                                sprache,
                                text=wa.eingriff_text(e, w.glieder[i], w, sprache),
                            )
                        )
        return aus


def wa_art() -> str:
    return "waechter"


def _lesen(pfad: str) -> str:
    with open(pfad, encoding="utf-8") as f:
        return f.read()


def _zahl(wert: Any) -> float | None:
    return float(wert) if isinstance(wert, int | float) else None
