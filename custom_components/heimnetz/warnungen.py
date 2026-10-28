"""Warnungen versenden (WU-0010): nach jedem Abruf den Wächter (`logik/warnungen.py`) fortschreiben, für jede Meldung
das Ereignis `heimnetz_warnung` feuern und eine Journalzeile anlegen, die Nachricht über den gewählten notify-Dienst
von Home Assistant schicken.

Zweite Ausnahme von „die Integration liest nur“ (Herbert, 28.10.2026): Nachrichten über notify-Dienste von HA. Die
Companion App stellt sie über den Push-Dienst von Google bzw. Apple zu – der Gerätename verlässt dabei das Heimnetz.
Versendet wird im Hintergrund (der Abruf wartet nicht); ein Fehler kommt ins Protokoll und ins Journal, nie in den
Abruf.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .ansichten import geraete_daten, ha_geraete
from .const import DOMAIN, sprache, sprache_system
from .logik import arten as ar
from .logik import geraete as gr
from .logik import sammeln as sm
from .logik import warnungen as wn
from .logik import wlan as wl
from .logik.ereignis import INFO, WARNUNG, Ereignis
from .logik.sprache import DE, merke, t
from .logik.verlauf import geraete_id

if TYPE_CHECKING:
    from . import Laufzeit

LOGGER = logging.getLogger(__package__)
EREIGNIS = f"{DOMAIN}_warnung"
NOTIFY = "notify"
TITEL = "Heimnetz"
ZEIT_S = 30  # so lange darf ein notify-Dienst für eine Nachricht brauchen
OHNE = (
    "send_message",
)  # notify-Aktion für Entitäten (braucht ein Ziel) – kein Dienst zum Auswählen
BEISPIEL = merke("Kamera Garten")


def dienste(hass: HomeAssistant) -> list[str]:
    """Vorhandene notify-Dienste (ohne `notify.send_message`)."""
    return sorted(d for d in hass.services.async_services_for_domain(NOTIFY) if d not in OHNE)


def _app_namen(hass: HomeAssistant) -> dict[str, str]:
    """notify-Dienst der Companion App → Name des Geräts (wie die App ihn beim Einrichten meldet)."""
    out = {}
    for e in hass.config_entries.async_entries("mobile_app"):
        if name := e.data.get("device_name"):
            out[f"{wn.MOBILE_APP}{slugify(name)}"] = str(name)
    return out


def ziele(hass: HomeAssistant, ziel: str, s: str) -> list[dict[str, str]]:
    """Auswahl „Nachricht an“: Companion Apps, alle Companion Apps, andere notify-Dienste, keine."""
    vorhanden, namen = dienste(hass), _app_namen(hass)
    apps = [d for d in vorhanden if d.startswith(wn.MOBILE_APP)]
    out = [
        {
            "name": d,
            "text": t(
                "Companion App · {name}",
                s,
                name=namen.get(d) or d.removeprefix(wn.MOBILE_APP).replace("_", " "),
            ),
        }
        for d in apps
    ]
    if apps:
        out.append({"name": wn.ALLE, "text": t("alle Companion Apps ({n})", s, n=len(apps))})
    out += [{"name": d, "text": f"notify.{d}"} for d in vorhanden if d not in apps]
    out.append({"name": wn.KEINE, "text": t("keine Nachricht – nur Ereignis", s)})
    if ziel not in {x["name"] for x in out}:
        out.insert(0, {"name": ziel, "text": t("notify.{dienst} – fehlt", s, dienst=ziel)})
    return out


def _fehlt(ziel: str, s: str) -> str:
    """Warum es kein Ziel gibt: keine Companion App eingerichtet bzw. der gewählte Dienst fehlt."""
    if ziel == wn.ALLE:
        return t("keine Companion App eingerichtet", s)
    return t("den Dienst notify.{dienst} gibt es nicht", s, dienst=ziel)


def _verbindungen(stand: sm.Stand, s: str) -> dict[str, str]:
    """Verbindung je Gerät als Text („WLAN 5 GHz“, „LAN“ …) – nur für Geräte, die gerade verbunden sind."""
    w = stand.wlan
    baender = {f.mac: wl.band_von(f, w.baender) for f in w.geraete} if w else {}
    return {
        mac: gr.gruppen_text(gr.verbindung(g.art, g.aktiv, baender.get(mac), g.vpn), s)
        for mac, g in stand.geraete.items()
        if g.aktiv
    }


class Warndienst:
    """Wächter der Warnungen und Versand; eine Instanz je Einrichtung (Laufzeit)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, lz: Laufzeit) -> None:
        self.hass, self.entry, self.lz = hass, entry, lz
        self.waechter = wn.Waechter()
        # Fehler beim Versand ins Journal (der Abruf schreibt sie beim nächsten Mal mit)
        self.journal: Callable[[list[Ereignis]], None] = lambda _e: None
        self._sperre = asyncio.Lock()  # Abrufe nie gleichzeitig durch den Wächter
        self._letzter = 0.0  # Zeit des zuletzt verarbeiteten Abrufs

    async def async_bekannt_laden(self) -> None:
        """Je gesehene Geräte für „neues Gerät“: gemerkte, die der Box (Gedächtnis, auch aus der Übernahme) und alle
        mit Geräteverlauf im Journal – so meldet sich nach dem Einspielen kein altes Gerät als neu."""
        g = self.lz.abruf.gedaechtnis
        try:
            journal = await self.hass.async_add_executor_job(self.lz.datenbank.journal_macs)
        except Exception:  # Datenbank gerade nicht lesbar: ohne den Verlauf weiter
            LOGGER.warning("Heimnetz: Geräteverlauf für Warnungen nicht lesbar")
            journal = []
        bekannt = dict.fromkeys([*journal, *g.bekannt, *(g.geraete or {})])
        self.waechter.bekannt = bekannt
        g.bekannt = list(bekannt)

    # ── nach jedem Abruf ──
    async def abruf(self, stand: sm.Stand) -> list[Ereignis]:
        """Wächter fortschreiben, Ereignisse feuern, Versand anstoßen. Zurück: Journalzeilen zu den Meldungen.
        Blockierendes (Arten bestimmen) im Executor, der Wächter selbst nur hier im Event-Loop und nacheinander."""
        async with self._sperre:
            if stand.zeit <= self._letzter:
                return []  # älterer Abruf, der sich überholt hat
            self._letzter = stand.zeit
            e = self.lz.einstellungen.warnungen
            ueberwacht = await self.hass.async_add_executor_job(
                self._ueberwacht,
                stand,
                e,
                ha_geraete(self.hass),
                dict(self.lz.einstellungen.arten),
                dict(self.lz.einstellungen.eigene),
            )
            verbindung = _verbindungen(stand, e.sprache)
            beobachtet = [
                wn.Beobachtung(
                    mac, g.name, g.ip, g.aktiv, verbindung.get(mac, ""), gr.zufallsadresse(mac)
                )
                for mac, g in stand.geraete.items()
            ]
            w = self.waechter
            ergebnis = w.schritt(
                stand.zeit,
                stand.box_erreichbar,
                stand.pi.internet,
                beobachtet,
                e,
                lambda mac: ueberwacht.get(mac, False),
            )
            if w.bekannt_geaendert:
                self.lz.abruf.gedaechtnis.bekannt = list(w.bekannt)
                w.bekannt_geaendert = False
        tz, s_ha = dt_util.get_default_time_zone(), sprache_system(self.hass)
        journal = []
        for m in ergebnis.neu:
            self.hass.bus.async_fire(EREIGNIS, m.ereignis(e.sprache, tz))
            journal.append(
                Ereignis(
                    "warnung",
                    INFO,
                    t("🔔 Warnung: {text}", s_ha, text=m.text(s_ha, tz)),
                    m.schluessel,
                )
            )
        if ergebnis.senden and e.ziel != wn.KEINE:
            self.entry.async_create_background_task(
                self.hass, self._zustellen(list(ergebnis.senden), e), f"{DOMAIN}_warnung"
            )
        return journal

    def _ueberwacht(
        self,
        stand: sm.Stand,
        e: wn.Warneinstellungen,
        ha: dict[str, tuple[str, str]],
        selbst: dict[str, str],
        eigene: dict[str, ar.EigeneArt],
    ) -> dict[str, bool]:
        """Blockierend (Herstellerliste beim ersten Mal): wird jedes Gerät überwacht? Art + Ausnahme."""
        ar.tabelle_laden()
        out = {}
        for mac, g in stand.geraete.items():
            kennung = geraete_id(mac, self.lz.salz)
            kat = ar.bestimmen(
                g.name,
                mac,
                selbst=selbst.get(kennung),
                ha=ha.get(mac.upper()),
                mesh=stand.mesh.get(mac.upper()),
                sprache=DE,
                eigene=eigene,
            ).kat
            out[mac] = e.ueberwacht(kat, kennung)
        return out

    # ── Versand ──
    async def _zustellen(self, meldungen: list[wn.Meldung], e: wn.Warneinstellungen) -> None:
        ziel = wn.ziel_dienste(e.ziel, dienste(self.hass))
        s_ha = sprache_system(self.hass)
        if not ziel:
            LOGGER.warning("Heimnetz: Warnung nicht zugestellt – notify.%s fehlt", e.ziel)
            self.journal(
                [
                    Ereignis(
                        "warnung_fehler",
                        WARNUNG,
                        t("Warnung nicht zugestellt: {grund}", s_ha, grund=_fehlt(e.ziel, s_ha)),
                    )
                ]
            )
            return
        tz = dt_util.get_default_time_zone()
        fehler = []
        for m in meldungen:
            text = m.text(e.sprache, tz)
            for dienst in ziel:
                if (grund := await self._senden(dienst, text)) is not None:
                    fehler.append(
                        Ereignis(
                            "warnung_fehler",
                            WARNUNG,
                            t(
                                "Warnung nicht zugestellt (notify.{dienst}): {fehler}",
                                s_ha,
                                dienst=dienst,
                                fehler=grund,
                            ),
                            m.schluessel,
                        )
                    )
        if fehler:
            self.journal(fehler)

    async def _senden(self, dienst: str, text: str) -> str | None:
        """Eine Nachricht an einen notify-Dienst; zurück der Fehler als Text, None = angenommen."""
        try:
            async with asyncio.timeout(ZEIT_S):
                await self.hass.services.async_call(
                    NOTIFY, dienst, {"title": TITEL, "message": text}, blocking=True
                )
        except Exception as err:  # jeder Fehler des Dienstes: protokollieren, nie den Abruf stören
            grund = str(err) or type(err).__name__
            LOGGER.warning("Heimnetz: Warnung an notify.%s nicht zugestellt: %s", dienst, grund)
            return grund
        return None

    async def testen(self) -> list[str]:
        """„Testnachricht senden“ (Sprache der Seite): Ereignis immer, Nachricht an das Ziel. Zurück: erreichte
        Dienste; ein Fehler → RuntimeError mit dem Grund."""
        e, s = self.lz.einstellungen.warnungen, sprache(self.hass)
        tz = dt_util.get_default_time_zone()
        m = wn.test(dt_util.utcnow().timestamp())
        self.hass.bus.async_fire(EREIGNIS, m.ereignis(s, tz))
        if e.ziel == wn.KEINE:
            return []
        ziel = wn.ziel_dienste(e.ziel, dienste(self.hass))
        if not ziel:
            raise RuntimeError(_fehlt(e.ziel, s))
        for dienst in ziel:
            if (grund := await self._senden(dienst, m.text(s, tz))) is not None:
                raise RuntimeError(f"notify.{dienst}: {grund}")
        return ziel

    def diagnose(self) -> dict[str, Any]:
        """Zahlen statt Namen; das Ziel nur als Art (ein Dienstname enthält den Gerätenamen)."""
        e = self.lz.einstellungen.warnungen
        art = (
            e.ziel
            if e.ziel in (wn.KEINE, wn.ALLE)
            else "companion_app"
            if e.ziel.startswith(wn.MOBILE_APP)
            else "dienst"
        )
        return {
            "ziel": art,
            "verzoegerung": e.verzoegerung,
            "arten_an": sorted(k for k in ar.TEXT if e.art_an(k)),
            "eigene_arten": len(self.lz.einstellungen.eigene),
            "eigene_an": sum(1 for k in self.lz.einstellungen.eigene if e.art_an(k)),
            "ausnahmen": len(e.geraete),
            "schalter": {"wieder": e.wieder, "neu": e.neu, "internet": e.internet},
            "grundzustand": self.waechter.grundzustand,
            "zustaende": self.waechter.zaehlen(),
            "zurueckgehalten": len(self.waechter.zurueck),
        }


# ── ⚙ › 🔔 Warnungen ──
async def ansicht(hass: HomeAssistant, lz: Laufzeit) -> dict[str, Any]:
    """Alles für den Reiter: Ziel und Auswahl, Verzögerung, je Art Schalter mit Anzahl, Ausnahmen, Schalter, Beispiel.
    Wer überwacht wird und die Zählungen rechnet die Integration, die Seite zeigt nur an."""
    s, e = sprache(hass), lz.einstellungen.warnungen
    jetzt = dt_util.utcnow().timestamp()
    liste = (await hass.async_add_executor_job(geraete_daten, lz, jetzt, ha_geraete(hass), s))[
        "geraete"
    ]
    zahl: dict[str, int] = {}
    for x in liste:
        zahl[x["kat"]] = zahl.get(x["kat"], 0) + 1
    ueberwacht = [x for x in liste if e.ueberwacht(x["kat"], x["id"])]
    namen = {x["id"]: x["name"] for x in liste}
    for (
        mac,
        g,
    ) in (
        lz.abruf.data.geraete.items()
    ):  # Ausnahmen für Geräte, die gerade nicht in der Liste stehen
        namen.setdefault(geraete_id(mac, lz.salz), gr.anzeigename(g.name, s))
    vorbild = next((x for x in ueberwacht if x["aktiv"]), None)
    beispiel = wn.beispiel(
        jetzt,
        vorbild["name"] if vorbild else t(BEISPIEL, s),
        gr.gruppen_text(vorbild["verbindung"] if vorbild else "WLAN 2,4 GHz", s),
        e.verzoegerung,
    )
    return {
        "ziel": e.ziel,
        "ziele": ziele(hass, e.ziel, s),
        "ziel_fehlt": e.ziel != wn.KEINE and not wn.ziel_dienste(e.ziel, dienste(hass)),
        "verzoegerung": e.verzoegerung,
        "verzoegerungen": list(wn.VERZOEGERUNGEN),
        "arten": [
            {
                "name": k,
                "text": text,
                "an": e.art_an(k),
                "geraete": zahl.get(k, 0),
                "hinweis": t(wn.AUSGENOMMEN[k], s) if k in wn.AUSGENOMMEN else None,
            }
            for k, text in ar.alle(s, lz.einstellungen.eigene)
        ],
        "ueberwacht": len(ueberwacht),
        "gesamt": len(liste),
        "ausnahmen": [
            {"id": k, "name": namen.get(k) or t("Gerät nicht mehr bekannt", s), "wert": v}
            for k, v in e.geraete.items()
        ],
        "wieder": e.wieder,
        "neu": e.neu,
        "internet": e.internet,
        "beispiel": beispiel.text(s, dt_util.get_default_time_zone()),
    }
