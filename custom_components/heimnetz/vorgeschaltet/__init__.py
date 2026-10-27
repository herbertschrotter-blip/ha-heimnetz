"""Vorgeschaltetes Gerät (WU-0009 Stufe 2): erkennen und laufend lesen – dünner HA-Teil über das Netz.

Je Hersteller/Schnittstelle ein Baustein (`zte.py`, `huawei.py`, `tplink.py`, `integrationen.py`); Erkennen und
Umrechnen ohne HA in `logik/vorgeschaltet/`. Der `Dienst` hält, was der Abruf braucht: das erkannte Gerät, den letzten
Stand und ob ein Kennwort abgelehnt wurde. Er wird vom gemeinsamen Abruf (coordinator.py) im langsamen Takt angestoßen,
läuft im Hintergrund (eine Suche kann bis zu einer Minute dauern) und nie zweimal zugleich – auch nicht neben der
🔬 Diagnose, die dieselbe Sperre nimmt.

Sicherheit wie in `netz.py`: nur private Adressen, keine Weiterleitung, Zeit- und Größengrenzen. Das Kennwort kommt
aus den Optionen des Eintrags, wird nur an das Gerät geschickt und nie protokolliert; abgelehnt merkt sich der Dienst
nur seinen Hash im Speicher und meldet sich damit nicht wieder an, bis ein anderes Kennwort eingetragen ist.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field

import aiohttp
from homeassistant.core import HomeAssistant

from ..logik import vorgeschaltet as ve
from ..logik.sprache import DE
from . import huawei, integrationen, netz, tplink, zte
from .netz import GESAMT_S, SUCHE_ZEIT_S, Lauf

LOGGER = logging.getLogger(__package__)
SUCHE_GESAMT_S = 60  # alle Adressen zusammen


def _kennwort_marke(adresse: str, kennwort: str) -> str:
    return hashlib.sha256(f"{adresse}\0{kennwort}".encode()).hexdigest()


async def erkennen_an(lauf: Lauf, hass: HomeAssistant) -> tuple[bool, ve.Erkennung | None]:
    """Startseite lesen und erkennen. (antwortet, Erkennung)."""
    startseite = await lauf.startseite()
    if startseite is None:
        return False, None
    return True, await erkennen_aus(lauf, hass, startseite)


async def erkennen_aus(lauf: Lauf, hass: HomeAssistant, startseite: str) -> ve.Erkennung | None:
    """Aus der Startseite erkennen; bei ZTE (oder unbekannt) die Schnittstelle mit lesenden Proben bestimmen, bei
    Huawei (oder noch unbekannt) das Modell aus `device/basic_information`."""
    erkennung = ve.erkennen(startseite, lauf.kopf)
    if erkennung is None or erkennung.baustein == "zte":
        modell = erkennung.modell if erkennung else ""
        goform = await zte.goform_probe(lauf)
        ubus = False if goform is not None else await zte.ubus_probe(lauf)
        erkennung = ve.zte_schnittstelle(goform, ubus, modell) or erkennung
    if erkennung is None and lauf.zeit_uebrig():
        # Executor: läuft nach einem Zeitlimit womöglich weiter (Zeitlimit je Anfrage ZEIT_S)
        modell = await hass.async_add_executor_job(huawei.probe, lauf)
        if modell is not None:
            erkennung = ve.Erkennung("huawei_hilink", modell)
    elif erkennung is not None and erkennung.baustein == "huawei_hilink" and not erkennung.modell:
        modell = await hass.async_add_executor_job(huawei.probe, lauf)
        erkennung = ve.Erkennung("huawei_hilink", modell or "")
    return erkennung


async def baustein_lesen(
    hass: HomeAssistant,
    lauf: Lauf,
    erkennung: ve.Erkennung,
    kennwort: str | None,
    diagnose: bool = False,
) -> tuple[zte.Lesung, str]:
    """Werte über den Baustein des erkannten Geräts. (Lesung, Quelle „geraet“/„integration“)."""
    b = erkennung.b
    if b.integration and integrationen.eingerichtet(hass, b.integration) and not diagnose:
        mobil = integrationen.lesen(hass, b.integration)
        return zte.Lesung(mobil=mobil, befund=None if mobil else "keine_werte"), "integration"
    if b.art == "glasfaser":
        return zte.Lesung(befund="glasfaser"), "geraet"
    if erkennung.baustein == "zte_goform":
        return await zte.goform_lesen(lauf, kennwort, diagnose), "geraet"
    if erkennung.baustein == "zte_ubus":
        return await zte.ubus_lesen(lauf, kennwort), "geraet"
    # Die Bibliotheken laufen im Executor. Läuft das Zeitlimit des Aufrufers (asyncio.wait_for) ab, arbeitet der Thread
    # womöglich weiter – abbrechen lässt er sich nicht; begrenzt wird das durch die Zeitlimits je Anfrage (ZEIT_S).
    try:
        if erkennung.baustein == "huawei_hilink":
            return await hass.async_add_executor_job(huawei.lesen, lauf, kennwort), "geraet"
        if erkennung.baustein == "tplink":
            return await hass.async_add_executor_job(tplink.lesen, lauf, kennwort), "geraet"
    except ImportError:  # Bibliothek fehlt (Home Assistant installiert sie aus manifest.json)
        LOGGER.warning("Heimnetz: Bibliothek für %s fehlt", b.hersteller)
        return zte.Lesung(befund="fehler"), "geraet"
    if b.integration:
        return zte.Lesung(befund="integration_fehlt"), "geraet"
    return zte.Lesung(befund="nicht_unterstuetzt"), "geraet"


@dataclass
class Dienst:
    """Erkanntes Gerät und letzter Stand des vorgeschalteten Geräts für den Abruf."""

    hass: HomeAssistant
    sperre: asyncio.Lock = field(default_factory=asyncio.Lock)
    gemerkt: ve.Erkennung | None = None
    adresse: str = ""
    stand: ve.Modemstand | None = None
    treffer: tuple[ve.Treffer, ...] = ()
    gesucht: float | None = None  # Zeitpunkt der letzten Suche
    gelesen: float = 0.0  # letzter Versuch, Werte zu lesen
    suchen_noetig: bool = False  # „↻ Erneut suchen“, neue Adresse
    lesen_noetig: bool = False  # neue Wahl oder neues Kennwort: gleich lesen
    aufgabe: asyncio.Task[None] | None = None
    _abgelehnt: str | None = None  # Hash von Adresse und abgelehntem Kennwort (nur im Speicher)
    _fehlt_seit: int = 0  # so viele Takte hintereinander nicht erreichbar

    def faellig(self, jetzt: float) -> bool:
        """Ist Arbeit fällig (suchen oder lesen)? Läuft schon eine, nie eine zweite."""
        if self.aufgabe is not None and not self.aufgabe.done():
            return False
        return (
            self.suchen_noetig
            or self.lesen_noetig
            or self.gemerkt is None
            and (self.gesucht is None or jetzt - self.gesucht >= ve.TAKT_S)
            or self.gemerkt is not None
            and jetzt - self.gelesen >= ve.TAKT_S
        )

    def kennwort_abgelehnt(self, adresse: str, kennwort: str | None) -> bool:
        """Wurde genau dieses Kennwort an dieser Adresse schon abgelehnt? (für die 🔬 Diagnose)"""
        return bool(kennwort) and _kennwort_marke(adresse, kennwort or "") == self._abgelehnt

    def anstossen(self, *, suchen: bool = False) -> None:
        self.lesen_noetig = True
        self.suchen_noetig = self.suchen_noetig or suchen

    async def suchen(
        self, kandidaten: tuple[str, ...], sprache: str = DE
    ) -> tuple[ve.Treffer, ...]:
        """Nacheinander an den Kandidaten fragen, bis ein Gerät erkannt ist (nicht die Box); das wird gemerkt."""
        gefunden: list[ve.Treffer] = []
        start = time.monotonic()
        try:
            async with netz.neue_session(aiohttp.ClientTimeout(total=SUCHE_GESAMT_S)) as session:
                for adresse in kandidaten:
                    if time.monotonic() - start >= SUCHE_GESAMT_S:
                        break
                    lauf = Lauf(
                        session, adresse, sprache, zeit_s=SUCHE_ZEIT_S, gesamt_s=12, roh=False
                    )
                    try:
                        antwortet, erkennung = await asyncio.wait_for(
                            erkennen_an(lauf, self.hass), 15
                        )
                    except TimeoutError, aiohttp.ClientError:
                        antwortet, erkennung = False, None
                    gefunden.append(ve.Treffer(adresse, antwortet, erkennung))
                    if gefunden[-1].brauchbar:
                        break  # gefunden – die übrigen Adressen werden nicht mehr gefragt
        finally:
            # auch nach einem Fehler: nicht gleich wieder suchen (sonst jede Minute)
            self.treffer = tuple(gefunden)
            self.gesucht = time.time()
            self.suchen_noetig = False
        if (b := ve.bester(self.treffer)) is not None and b.erkennung is not None:
            self.gemerkt, self.adresse = b.erkennung, b.adresse
        return self.treffer

    async def arbeiten(
        self,
        kandidaten: tuple[str, ...],
        kennwort: str | None,
        sprache: str = DE,
        gespeichert: str | None = None,
    ) -> ve.Modemstand:
        """Suchen (wenn nötig) und lesen – ein Durchgang, höchstens eine Anmeldung. Eine neu gespeicherte Adresse
        (anders als die gemerkte) löst eine neue Suche aus."""
        async with self.sperre:
            jetzt = time.time()
            neu_gespeichert = bool(gespeichert) and gespeichert != self.adresse
            suchen = (
                self.suchen_noetig
                or neu_gespeichert
                or (
                    self.gemerkt is None
                    and (self.gesucht is None or jetzt - self.gesucht >= ve.TAKT_S)
                )
            )
            lesen = self.lesen_noetig or jetzt - self.gelesen >= ve.TAKT_S
            if not suchen and not lesen and self.stand is not None:
                return (
                    self.stand
                )  # eben erst gelesen (z. B. zwei Anstöße hintereinander) – kein zweiter Zugriff
            # gelesen gilt ab jetzt – auch nach einem Fehler erst im nächsten Takt wieder
            self.gelesen, self.lesen_noetig = jetzt, False
            if suchen:
                await self.suchen(kandidaten, sprache)
            if self.gemerkt is None:
                befund = "nicht_gefunden" if self.treffer else "nicht_gesucht"
                self.stand = ve.Modemstand("", None, None, befund, jetzt)
                return self.stand
            self.stand = await self._lesen(self.adresse, self.gemerkt, kennwort, sprache, jetzt)
            return self.stand

    async def _lesen(
        self,
        adresse: str,
        erkennung: ve.Erkennung,
        kennwort: str | None,
        sprache: str,
        jetzt: float,
    ) -> ve.Modemstand:
        marke = _kennwort_marke(adresse, kennwort) if kennwort else None
        abgelehnt = marke is not None and marke == self._abgelehnt
        async with netz.neue_session(aiohttp.ClientTimeout(total=GESAMT_S)) as session:
            lauf = Lauf(session, adresse, sprache, roh=False)
            try:
                lesung, quelle = await asyncio.wait_for(
                    self._mit_startseite(lauf, erkennung, None if abgelehnt else kennwort), GESAMT_S
                )
            except TimeoutError:
                lesung, quelle = zte.Lesung(befund="nicht_erreichbar"), "geraet"
        if quelle != "geraet":
            self._abgelehnt = (
                None  # Werte aus einer HA-Integration: kein eigenes Anmelden, kein Merker
            )
        elif lesung.befund == "anmeldung_abgelehnt" and marke:
            self._abgelehnt = marke
        elif abgelehnt and lesung.befund in (None, "ohne_kennwort", "keine_werte"):
            # bleibt, bis ein anderes Kennwort eingetragen ist
            lesung.befund = "anmeldung_abgelehnt"
        elif lesung.angemeldet:
            self._abgelehnt = None
        self._fehlt_seit = self._fehlt_seit + 1 if lesung.befund == "nicht_erreichbar" else 0
        return ve.Modemstand(
            adresse, erkennung, lesung.mobil, lesung.befund, jetzt, quelle, lesung.angemeldet
        )

    async def _mit_startseite(
        self, lauf: Lauf, erkennung: ve.Erkennung, kennwort: str | None
    ) -> tuple[zte.Lesung, str]:
        b = erkennung.b
        if b.integration and integrationen.eingerichtet(self.hass, b.integration):
            return await baustein_lesen(self.hass, lauf, erkennung, kennwort)
        if await lauf.startseite() is None:
            return zte.Lesung(befund="nicht_erreichbar"), "geraet"
        return await baustein_lesen(self.hass, lauf, erkennung, kennwort)

    @property
    def nicht_erreichbar_lange(self) -> bool:
        """Zwei Takte hintereinander nicht erreichbar – erst dann ein Reparatur-Hinweis (kein Flattern)."""
        return self._fehlt_seit >= 2
