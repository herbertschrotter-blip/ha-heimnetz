"""Wächter (Herbert, 18.11.2026) – dünner HA-Teil: Steckdosen finden, Skript einspielen und entfernen, Zustand der
Steckdosen lesen (alle 2 min, im Hintergrund), neue Eingriffe ins Journal und als Warnung, Stufe 1 (sanft neu starten)
nach jedem Abruf. Fachliches in `logik/waechter.py`, die Steckdose in `shelly.py`.

Was Heimnetz hier auslöst, ist bewusst eng: Neustart der FRITZ!Box über TR-064, Neustart eines vorgeschalteten Geräts
über seine Weboberfläche (nur ZTE goform, Huawei HiLink, TP-Link; mit dem Kennwort aus ⚙ → Zugang) und das eigene
Skript samt Regeln auf den gewählten Steckdosen. Nie eine Einstellung eines Geräts.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable
from dataclasses import replace
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_MODEM_KENNWORT, CONF_SHELLY_KENNWORT, sprache_system
from .logik import sammeln as sm
from .logik import waechter as wa
from .logik.ereignis import INFO, WARNUNG, Ereignis
from .logik.modem import adresse_erlaubt
from .logik.sprache import Ungueltig, t
from .shelly import Info, ShellyFehler, Steckdose
from .vorgeschaltet import baustein_neustarten
from .vorgeschaltet.netz import Lauf, neue_session

if TYPE_CHECKING:
    from . import Laufzeit

LOGGER = logging.getLogger(__package__)
ABFRAGE_S = 120  # Zustand der Steckdosen so oft lesen
SUCHE_HOECHSTENS = 24  # so viele Adressen fragt die Suche nach Steckdosen höchstens
ART = "waechter"  # Journal
# Beobachter des Supervisors (Port 4357) gibt es nur unter Home Assistant OS / Supervised
BEOBACHTER = bool(os.environ.get("SUPERVISOR"))


class Waechterdienst:
    def __init__(self, hass: HomeAssistant, lz: Laufzeit) -> None:
        self.hass, self.lz = hass, lz
        self.staende: dict[tuple[str, int], wa.Dosenstand] = {}
        self.sanft: dict[str, wa.Sanft] = {}
        self._gelesen = 0.0
        self._aufgabe: asyncio.Task[None] | None = None
        self._sperre = asyncio.Lock()
        self._befehl_n = int(time.time())

    @property
    def liste(self) -> list[wa.Waechter]:
        return self.lz.einstellungen.waechter

    def _kennwort(self) -> str | None:
        return self.lz.abruf.config_entry.options.get(CONF_SHELLY_KENNWORT) or None

    def _dose(self, adresse: str) -> Steckdose:
        return Steckdose(async_get_clientsession(self.hass), adresse, self._kennwort())

    def journal(self, ereignisse: list[Ereignis]) -> None:
        self.lz.abruf.journal_merken(ereignisse)

    # ── Was es zu überwachen gibt ──

    def router(self) -> str | None:
        r = self.lz.abruf.gedaechtnis.lan.router or self.lz.abruf.box.zugang.host
        return r if r and adresse_erlaubt(r) else None

    def kette(self) -> list[wa.Glied]:
        """Kette des Internets aus ⚙ → Zugang: vorgeschaltetes Gerät (wenn aktiv), dann die FRITZ!Box."""
        abruf, aus = self.lz.abruf, []
        if abruf.modem_aktiv(abruf.data.zugang if abruf.data else None) and abruf.modem.adresse:
            e = abruf.modem.gemerkt
            aus.append(
                wa.Glied(
                    e.baustein if e else "andere", e.name if e else "Modem", abruf.modem.adresse
                )
            )
        if (r := self.router()) is not None:
            info = abruf.box_info
            aus.append(
                wa.Glied("fritzbox", info.modell if info and info.modell else "FRITZ!Box", r)
            )
        return aus

    async def ha_glied(self) -> wa.Glied | None:
        from homeassistant.components.network import async_get_source_ip  # noqa: PLC0415

        try:
            ip = await async_get_source_ip(self.hass)
        except Exception:  # kein Netz-Helfer
            return None
        port = getattr(getattr(self.hass, "http", None), "server_port", None) or wa.HA_PORT
        return wa.Glied("ha", "Home Assistant", f"{ip}:{port}") if adresse_erlaubt(ip) else None

    async def kandidaten(self) -> list[dict[str, Any]]:
        """Shelly-Steckdosen im Heimnetz: aus der Shelly-Integration von HA und aus der Geräteliste der Box (Name
        beginnt mit „shelly“). Jede wird einmal ohne Anmeldung gefragt (GET /shelly), passende auch nach der
        Leistung."""
        adressen: dict[str, str] = {}
        for e in self.hass.config_entries.async_entries("shelly"):
            if (h := str(e.data.get("host") or "")) and adresse_erlaubt(h):
                adressen.setdefault(h, e.title)
        for g in (self.lz.abruf.data.geraete if self.lz.abruf.data else {}).values():
            if g.aktiv and g.name.lower().startswith("shelly") and adresse_erlaubt(g.ip):
                adressen.setdefault(g.ip, g.name)
        belegt = {d: w.id for w in self.liste for _, d in w.dosen}

        async def fragen(adresse: str, name: str) -> dict[str, Any] | None:
            dose = self._dose(adresse)
            try:
                info: Info = await dose.info()
            except ShellyFehler:
                return None
            leistung = None
            if info.passt:
                try:
                    leistung = await dose.leistung()
                except ShellyFehler:
                    leistung = None
            return {
                "adresse": adresse,
                "name": name,
                "kennung": info.kennung,
                "modell": info.app or info.modell,
                "gen": info.gen,
                "passt": info.passt,
                "kennwort": info.kennwort,
                "leistung": leistung,
                "belegt": belegt.get(adresse),
            }

        liste = list(adressen.items())[:SUCHE_HOECHSTENS]
        ergebnis = await asyncio.gather(*(fragen(a, n) for a, n in liste))
        return sorted((e for e in ergebnis if e), key=lambda e: (not e["passt"], e["adresse"]))

    # ── Ändern ──

    async def _einspielen(self, w: wa.Waechter, kennwort: str | None) -> None:
        router = self.router()
        for i, adresse in w.dosen:
            dose = Steckdose(async_get_clientsession(self.hass), adresse, kennwort)
            await dose.einspielen(wa.kvs(w, i, router, BEOBACHTER))

    def _kette_pruefen(self, w: wa.Waechter) -> None:
        """Typ und Adresse der Geräte kommen von der Seite: ein sanfter Neustart (mit dem Kennwort des Modems) nur an
        Geräten, die Heimnetz selbst als Kette kennt."""
        if w.art != "internet":
            return
        bekannt = {(g.typ, g.adresse) for g in self.kette()}
        if any((g.typ, g.adresse) not in bekannt for g in w.glieder):
            raise Ungueltig("Die Kette des Internets hat sich geändert – Wächter neu einrichten")

    async def speichern(self, daten: dict[str, Any], kennwort: str | None = None) -> wa.Waechter:
        """Prüfen, auf die Steckdosen spielen, speichern. Ungültig → Ungueltig; Steckdose → ShellyFehler. `kennwort`:
        neu eingetipptes Kennwort der Steckdosen (sonst das hinterlegte)."""
        async with self._sperre:
            liste = self.liste
            neu = wa.pruefen({**daten, "id": daten.get("id") or wa.neue_id(liste)})
            self._kette_pruefen(neu)
            alt = next((w for w in liste if w.id == neu.id), None)
            if alt is None and len(liste) >= wa.HOECHSTENS:
                raise Ungueltig("Höchstens {n} Wächter", n=wa.HOECHSTENS)
            if (d := wa.doppelte_dose(neu, liste)) is not None:
                raise Ungueltig("Die Steckdose {d} benutzt schon ein anderer Wächter", d=d)
            await self._einspielen(neu, kennwort or self._kennwort())
            weg = {d for _, d in alt.dosen} - {d for _, d in neu.dosen} if alt else set()
            for d in weg:
                await self._entfernen_von(d)
            await self.lz.einstellungen.async_waechter_setzen(
                [neu if w.id == neu.id else w for w in liste] + ([] if alt else [neu])
            )
            self.sanft.pop(neu.id, None)
            self._gelesen = 0.0
            self.journal(
                [
                    Ereignis(
                        ART,
                        INFO,
                        t(
                            "Wächter {name} eingerichtet",
                            sprache_system(self.hass),
                            name=_name(neu),
                        ),
                    )
                ]
            )
            return neu

    async def _entfernen_von(self, adresse: str) -> None:
        try:
            await self._dose(adresse).entfernen()
        except ShellyFehler as err:
            LOGGER.warning("Heimnetz: Wächter-Skript auf %s nicht entfernt: %s", adresse, err)

    async def entfernen(self, wid: str) -> None:
        async with self._sperre:
            w = self._finden(wid)
            for _, d in w.dosen:
                await self._entfernen_von(d)
            await self.lz.einstellungen.async_waechter_setzen(
                [x for x in self.liste if x.id != wid]
            )
            for i, _ in w.dosen:
                self.staende.pop((wid, i), None)
            self.sanft.pop(wid, None)

    async def schalten(self, wid: str, an: bool) -> None:
        async with self._sperre:
            w = self._finden(wid)
            neu = wa.pruefen({**w.als_dict(), "an": an})
            router = self.router()
            for i, d in neu.dosen:
                await self._dose(d).regeln_setzen(wa.kvs(neu, i, router, BEOBACHTER))
            await self.lz.einstellungen.async_waechter_setzen(
                [neu if x.id == wid else x for x in self.liste]
            )
            self._gelesen = 0.0

    async def befehl(self, wid: str, x: str) -> None:
        """„ruhe“ (Eingriff abbrechen: 60 min Ruhe) oder „weiter“ (Pause beenden) an alle Steckdosen des Wächters."""
        w = self._finden(wid)
        self._befehl_n += 1
        for _, d in w.dosen:
            await self._dose(d).befehl(x, self._befehl_n, **({"min": 60} if x == "ruhe" else {}))
        alt = self.sanft.get(wid, wa.Sanft())
        self.sanft[wid] = wa.Sanft(
            zuletzt=alt.zuletzt, ruhe_bis=time.time() + 3600 if x == "ruhe" else None
        )
        self._gelesen = 0.0

    async def blinken(self, adresse: str) -> None:
        await self._dose(adresse).blinken()

    def _finden(self, wid: str) -> wa.Waechter:
        for w in self.liste:
            if w.id == wid:
                return w
        raise KeyError(wid)

    # ── Im Takt des Abrufs ──

    async def abruf(self, stand: sm.Stand) -> None:
        """Nach jedem Abruf: Stufe 1 entscheiden; alle ABFRAGE_S die Steckdosen lesen (im Hintergrund)."""
        if not self.liste:
            return
        jetzt = time.time()
        for w in self.liste:
            await self._sanft(w, stand, jetzt)
        if jetzt - self._gelesen >= ABFRAGE_S and (self._aufgabe is None or self._aufgabe.done()):
            self._gelesen = jetzt
            self._aufgabe = self.lz.abruf.config_entry.async_create_background_task(
                self.hass, self.lesen(), "heimnetz_waechter_lesen"
            )

    async def _sanft(self, w: wa.Waechter, stand: sm.Stand, jetzt: float) -> None:
        if w.art != "internet":
            return
        erreichbar: dict[int, bool | None] = {}
        for i, g in enumerate(w.glieder):
            if g.typ == "fritzbox":
                erreichbar[i] = stand.box_erreichbar
            elif stand.modem is not None and stand.modem.adresse == g.adresse:
                erreichbar[i] = stand.modem.befund != "nicht_erreichbar"
        internet = stand.pi.internet if stand.pi is not None else None
        s, i = wa.sanft_entscheiden(
            w, self.sanft.get(w.id, wa.Sanft()), jetzt, internet, erreichbar
        )
        self.sanft[w.id] = s
        if i is None:
            return
        g = w.glieder[i]
        ok = await self._sanft_neustarten(g)
        sp = sprache_system(self.hass)
        text = (
            t("{geraet}: kein Internet – sanft neu gestartet", sp, geraet=g.name)
            if ok
            else t("{geraet}: kein Internet – sanfter Neustart nicht angenommen", sp, geraet=g.name)
        )
        # nur ins Journal: ohne Internet käme eine Push-Nachricht ohnehin nicht an
        self.journal([Ereignis(ART, WARNUNG, text)])

    async def _sanft_neustarten(self, g: wa.Glied) -> bool:
        """Nur an Geräten, die Heimnetz selbst kennt: die Box unter der Adresse des Routers, das vorgeschaltete Gerät
        unter seiner erkannten Adresse und mit seinem erkannten Baustein."""
        modem = self.lz.abruf.modem
        if g.typ == "fritzbox":
            if g.adresse != self.router():
                return False
            return await self.hass.async_add_executor_job(self.lz.abruf.box.neustarten)
        if g.adresse != modem.adresse or modem.gemerkt is None or modem.gemerkt.baustein != g.typ:
            return False
        kennwort = self.lz.abruf.config_entry.options.get(CONF_MODEM_KENNWORT) or None
        async with neue_session(aiohttp.ClientTimeout(total=30)) as session:
            lauf = Lauf(session, g.adresse, roh=False)
            return await baustein_neustarten(self.hass, lauf, g.typ, kennwort)

    async def lesen(self) -> None:
        """Zustand aller Steckdosen; neue Eingriffe ins Journal und als Warnung."""
        for w in list(self.liste):
            for i, d in w.dosen:
                neu = await self._dose(d).stand()
                alt = self.staende.get((w.id, i))
                if not neu.letzte and alt is not None:
                    # nicht erreichbar oder ohne Skript: die zuletzt gelesenen Eingriffe bleiben die Grundlage
                    neu = replace(neu, letzte=alt.letzte)
                self.staende[(w.id, i)] = neu
                if alt is None or not alt.letzte or not neu.erreichbar or neu.fehlt:
                    continue  # erstes Lesen (nach dem Start) oder nichts Neues lesbar: nichts nachmelden
                for e in wa.neue_eingriffe(alt.letzte, neu.letzte):
                    self._eingriff(w, w.glieder[i], e)

    def _eingriff(self, w: wa.Waechter, g: wa.Glied, e: dict[str, Any]) -> None:
        sp = sprache_system(self.hass)
        stufe = INFO if e.get("was") == "ok" else WARNUNG
        self.journal([Ereignis(ART, stufe, wa.eingriff_text(e, g, w, sp))])
        if w.regeln.melden and e.get("was") != "ok" and self.lz.warnungen is not None:
            text: Callable[[str], str] = lambda s_: wa.eingriff_text(e, g, w, s_)  # noqa: E731
            # im Hintergrund: ein langsamer notify-Dienst hält das Lesen der Steckdosen nicht auf
            self.lz.abruf.config_entry.async_create_background_task(
                self.hass,
                self.lz.warnungen.waechter_melden(text, g.name),
                "heimnetz_waechter_melden",
            )

    # ── Für die Seite ──

    async def ansicht(self, sprache: str) -> dict[str, Any]:
        jetzt = time.time()
        eingriffe = await self.hass.async_add_executor_job(
            self.lz.datenbank.journal_texte, ART, jetzt - 30 * 86_400, jetzt
        )
        karten = []
        for w in self.liste:
            glieder = [
                wa.glied_karte(g, self.staende.get((w.id, i)), sprache)
                for i, g in enumerate(w.glieder)
            ]
            punkte = [k["punkt"] for k in glieder if k["dose"]]
            punkt = (
                "grau"
                if not w.an
                else "rot"
                if "rot" in punkte
                else "amber"
                if "amber" in punkte
                else "ok"
            )
            s = self.sanft.get(w.id)
            karten.append(
                {
                    "id": w.id,
                    "art": w.art,
                    "symbol": wa.ART_SYMBOL[w.art],
                    "name": t(wa.ART_TEXT[w.art], sprache),
                    "an": w.an,
                    "punkt": punkt,
                    "glieder": glieder,
                    "regeln": w.regeln.als_dict(),
                    "weg_seit": s.weg_seit if s else None,
                    "eingriffe": sum(k["eingriffe"] for k in glieder),
                    "roh": w.als_dict(),
                }
            )
        return {
            "waechter": karten,
            "eingriffe": [{"t": z, "text": x} for z, x in reversed(eingriffe[-50:])],
            "gelesen": self._gelesen or None,
            "kennwort": bool(self._kennwort()),
        }

    async def vorschlag(self) -> dict[str, Any]:
        """Für „Wächter einrichten“: Kette, Home Assistant, Steckdosen."""
        ha = await self.ha_glied()
        return {
            "kette": [{**g.als_dict(), "sanft": g.sanft} for g in self.kette()],
            "ha": ha.als_dict() if ha else None,
            "router": self.router(),
            "dosen": await self.kandidaten(),
            "vorgabe": wa.VORGABE,
        }

    def diagnose(self) -> dict[str, Any]:
        """Zahlen statt Adressen."""
        return {
            "waechter": len(self.liste),
            "arten": sorted({w.art for w in self.liste}),
            "dosen": sum(len(w.dosen) for w in self.liste),
        }


def _name(w: wa.Waechter) -> str:
    return " → ".join(g.name for g in w.glieder) or w.art
