"""Ein gemeinsamer Abruf je Minute: Box lesen, vom Pi aus prüfen, auswerten (logik.sammeln), speichern.

Antwortet die Box nicht, scheitert der Abruf nicht: der Stand heißt dann „box_fehlt“, und die Entitäten, die von der
Box abhängen, werden nicht verfügbar (G-21). Nur eine abgelehnte Anmeldung ist ein Reparatur-Hinweis.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import time
from collections.abc import Awaitable, Callable
from dataclasses import replace
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SSL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import pi
from .box import AnmeldungAbgelehnt, Box, BoxDaten, BoxInfo, Zugang
from .const import (
    CONF_MODEM_KENNWORT,
    DOMAIN,
    INTERVALL,
    ISSUE_ANMELDUNG,
    ISSUE_FRITZ_FEHLT,
)
from .const import sprache_system as sprache_von
from .einstellungen import Einstellungsdienst
from .logik import auswertung as aw
from .logik import messplan as mp
from .logik import messung as ms
from .logik import sammeln as sm
from .logik import serie as sr
from .logik import sprache as sp
from .logik import vorgeschaltet as ve
from .logik import zugang as zg
from .logik.messung import Messung
from .logik.protokoll import Protokolleintrag
from .speedtest import OOKLA, Speedtest, alle_finden, async_messen, lauf, zeitpunkt
from .speicher import Datenbank, Journalzeile
from .vorgeschaltet import Dienst

AUFRAEUMEN_S = 86_400
AUSSTEHEND_HOECHSTENS = (
    10_000  # so viele ungeschriebene Zeilen hält der Abruf, wenn die Datenbank klemmt
)
SCHREIBFEHLER = (sqlite3.Error, OSError, RuntimeError)

LOGGER = logging.getLogger(__package__)
ZUGANG_SUCHEN_S = 30  # „Erneut suchen“ höchstens so oft (WU-0009)
SERIE_TAKT_S = 5  # so oft schaut die Serie nach dem Ergebnis eines Durchlaufs


def zugang_aus_fritz(hass: HomeAssistant, entry_id: str) -> Zugang | None:
    """Zugang aus dem Eintrag von FRITZ!Box Tools – nicht noch einmal eingeben, nirgends speichern."""
    fritz = hass.config_entries.async_get_entry(entry_id)
    if fritz is None or not fritz.data.get(CONF_HOST):
        return None
    d = fritz.data
    tls = bool(d.get(CONF_SSL))
    return Zugang(
        host=d[CONF_HOST],
        port=int(d.get(CONF_PORT) or (49443 if tls else 49000)),
        benutzer=d.get(CONF_USERNAME) or "",
        kennwort=d.get(CONF_PASSWORD) or "",
        tls=tls,
    )


class Abruf(DataUpdateCoordinator[sm.Stand]):
    """Holt die Daten im Takt INTERVALL und merkt sich, was der nächste Abruf braucht."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        box: Box,
        fritz_eintrag: str,
        datenbank: Datenbank,
        gedaechtnis: sm.Gedaechtnis,
        letzte_messung: float,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=INTERVALL,
            always_update=False,
        )
        self.box = box
        self.fritz_eintrag = fritz_eintrag
        self.datenbank = datenbank
        self.gedaechtnis = gedaechtnis
        # Gedächtnis ohne Zähler-Ring beim letzten Speichern: nur Änderungen schreiben
        self._gespeichert = ""
        self._ausstehend_journal: list[Journalzeile] = []
        self._ausstehend_protokoll: list[Protokolleintrag] = []
        self._schreibvorgaenge: set[asyncio.Task[None]] = set()
        self._aufgeraeumt = 0.0
        self.letzte_messung = letzte_messung
        self.gestartet = (
            time.time()
        )  # Messungen davor: keine Momentaufnahme vom Stand von jetzt (WU-0005)
        self.letzte: Messung | None = (
            None  # zuletzt eingetragene Messung (Sensor „Letzte Messung“, WU-0005)
        )
        self.einstellungen: Einstellungsdienst | None = None  # nach dem Laden gesetzt
        self.ausgeloest = 0.0  # letztes Auslösen einer Messung (Messplan oder von Hand)
        self.ausloese_grund: str | None = (
            None  # Grund des letzten Auslösens („von Hand“ oder der des Messplans)
        )
        self.box_info: BoxInfo | None = None  # Modell/Firmware/Laufzeit, langsam gelesen (WU-0005)
        self.zugang_neu = False  # WU-0009: „Erneut suchen“ – Zugang im nächsten Abruf mitlesen
        self._zugang_gesucht = -ZUGANG_SUCHEN_S
        # WU-0005: Momentaufnahme zu einer neuen Messung (gesetzt in __init__, braucht die Laufzeit)
        self.kontext_holen: Callable[[Messung], Awaitable[dict[str, Any]]] | None = None
        self.plan_status: mp.Entscheidung | None = None
        self.serie_status: dict[str, int] | None = None  # WU-0001: laufende Serie {n, lauf}
        self._serie_aufgabe: asyncio.Task[None] | None = None
        self.speedtest = Speedtest(
            hass, lambda: self.gedaechtnis.ring, lambda: self.letzte_messung, self._messung
        )
        # WU-0009 Stufe 2: vorgeschaltetes Gerät – eigener langsamer Takt, getrennt von der Sperre der Box
        self.modem = Dienst(hass)
        if (v := gedaechtnis.vorgeschaltet) is not None:
            self.modem.gemerkt = ve.Erkennung(v["baustein"], v.get("modell", ""))
            self.modem.adresse = v["adresse"]

    async def _async_update_data(self) -> sm.Stand:
        g, jetzt = self.gedaechtnis, time.time()
        sprache = sprache_von(self.hass)  # WU-0006: Texte für Seite und Journal, Sprache von HA
        langsam = g.langsam_faellig(jetzt)
        router = g.lan.router or self.box.zugang.host
        daten = await self._box_lesen(langsam, router, sprache)
        if daten.info is not None:
            self.box_info = daten.info
        verbindung = await pi.verbindung(router)
        dhcp = (
            await self.hass.async_add_executor_job(pi.dhcp_test, pi.DHCP_WARTEN_S, sprache)
            if langsam
            else None
        )

        modem = self._modem(daten.zugang, router, jetzt, sprache)
        roh = sm.Rohdaten(
            jetzt=jetzt,
            pi=verbindung,
            dhcp=dhcp,
            fehler=tuple(daten.fehler),
            protokoll=daten.protokoll,
            lan=daten.lan,
            geraete=daten.geraete,
            quellen=daten.quellen,
            mobil=daten.mobil,
            ohne_mobilfunk=daten.ohne_mobilfunk,
            zaehler=daten.zaehler,
            mobil_baender=daten.mobil_baender,
            wlan_baender=daten.wlan_baender,
            wlan_gast=daten.wlan_gast,
            wlan_geraete=daten.wlan_geraete,
            mesh=daten.mesh,
            zugang=daten.zugang,
            dsl=daten.dsl,
            faser=daten.faser,
            modem=modem,
            sprache=sprache,
        )
        stand = sm.auswerten(g, roh)
        await self._speichern(stand)
        self.speedtest.verbinden()
        await self._messplan(stand)
        if stand.fehler:
            LOGGER.debug("Abruf mit Lücken: %s", "; ".join(stand.fehler))
        return stand

    @property
    def letzte_ausloesung(self) -> float | None:
        """Letzte Messung oder letztes Auslösen – ab hier zählt der Takt des Messplans."""
        return max(self.letzte_messung, self.ausgeloest) or None

    async def _messplan(self, stand: sm.Stand) -> None:
        """Messplan: fällige Messung bei Ookla starten oder wegen Verkehr verschieben (logik.messplan). Ein Fehler
        hier darf den Abruf der Box nicht ungültig machen – er wird nur protokolliert."""
        if self.einstellungen is None or self.serie_status is not None:
            return  # während einer Serie misst der Plan nicht dazwischen
        try:
            self.plan_status = mp.entscheiden(
                self.einstellungen.plan,
                self.letzte_ausloesung,
                stand.zeit,
                dt_util.get_default_time_zone(),
                stand.rate.down if stand.rate else None,
                aw.schwelle(self.einstellungen.wert.tarif_down),
                self.plan_status,
            )
            if self.plan_status.aktion == mp.MESSEN:
                await self.messen(self.plan_status.grund, stand.zeit)
        except Exception:
            LOGGER.exception("Heimnetz: Messplan fehlgeschlagen")
            self.plan_status = None

    async def zugang_suchen(self) -> bool:
        """WU-0009: „Erneut suchen“ – den Zugang gleich im gemeinsamen Abruf lesen (keine eigene Verbindung), bei
        einem vorgeschalteten Gerät dazu dieses an den wenigen Adressen suchen (Stufe 2). Öfter als alle
        ZUGANG_SUCHEN_S geht das nicht (mehrfaches Tippen)."""
        jetzt = time.monotonic()
        if jetzt - self._zugang_gesucht < ZUGANG_SUCHEN_S:
            return False
        self._zugang_gesucht = jetzt
        self.zugang_neu = True
        await self.async_refresh()
        if await self.modem_jetzt(suchen=True):
            await self.async_refresh()
        return True

    # ── WU-0009 Stufe 2: vorgeschaltetes Gerät ──
    def modem_aktiv(self, meldung: zg.Meldung | None = None) -> bool:
        """Kommt das Internet über ein vorgeschaltetes Gerät (festgelegt oder erkannt)? Nur dann wird es gefragt."""
        wahl = self.einstellungen.wert.zugang_wahl if self.einstellungen else "auto"
        if wahl != "auto":
            return zg.wirksam("", wahl) == "extern"
        g = self.gedaechtnis
        art = zg.art_erkennen(meldung, g.zugang_haupt)[0] if meldung else g.zugang_art
        return art == "extern"

    def _modem_parameter(
        self, meldung: zg.Meldung | None, router: str
    ) -> tuple[tuple[str, ...], str | None, str | None]:
        """Kandidaten der Suche, Kennwort (aus den Optionen) und gespeicherte Adresse."""
        gespeichert = self.einstellungen.wert.zugang_adresse if self.einstellungen else None
        meldung = meldung or self.gedaechtnis.zugang
        kandidaten = ve.kandidaten(gespeichert, meldung.vorschlag if meldung else None, router)
        kennwort = self.config_entry.options.get(CONF_MODEM_KENNWORT) or None
        return kandidaten, kennwort, gespeichert

    def _modem(
        self, meldung: zg.Meldung | None, router: str, jetzt: float, sprache: str
    ) -> ve.Modemstand | None:
        """Im langsamen Takt Arbeit im Hintergrund anstoßen; zurück kommt der zuletzt gelesene Stand (Werte nur,
        solange sie frisch sind)."""
        if not self.modem_aktiv(meldung):
            self._modem_hinweise(None)
            return None
        if self.modem.faellig(jetzt):
            kandidaten, kennwort, gespeichert = self._modem_parameter(meldung, router)
            # als Hintergrund-Aufgabe des Eintrags: beim Entladen abgebrochen
            self.modem.aufgabe = self.config_entry.async_create_background_task(
                self.hass,
                self._modem_arbeiten(kandidaten, kennwort, sprache, gespeichert),
                f"{DOMAIN}_modem",
            )
        stand = self.modem.stand
        if stand is not None and not stand.frisch(jetzt):
            return replace(stand, mobil=None)
        return stand

    async def _modem_arbeiten(
        self,
        kandidaten: tuple[str, ...],
        kennwort: str | None,
        sprache: str,
        gespeichert: str | None,
    ) -> None:
        """Suchen/lesen; ein Fehler hier macht den Abruf der Box nie ungültig."""
        try:
            await self.modem.arbeiten(kandidaten, kennwort, sprache, gespeichert)
        except Exception:
            LOGGER.exception("Heimnetz: Lesen des vorgeschalteten Geräts fehlgeschlagen")
            self.modem.stand = ve.Modemstand(
                self.modem.adresse, self.modem.gemerkt, None, "fehler", time.time()
            )
        g = self.modem.gemerkt
        self.gedaechtnis.vorgeschaltet = (
            {"adresse": self.modem.adresse, "baustein": g.baustein, "modell": g.modell}
            if g
            else None
        )
        self._modem_hinweise(self.modem.stand)

    async def modem_jetzt(self, *, suchen: bool = False) -> bool:
        """Gleich suchen bzw. lesen (⚙ › Zugang: neue Wahl, Adresse, Kennwort, „↻ Erneut suchen“). False, wenn das
        Internet nicht über ein vorgeschaltetes Gerät kommt."""
        meldung = self.data.zugang if self.data else None
        if not self.modem_aktiv(meldung):
            self._modem_hinweise(None)
            return False
        self.modem.anstossen(suchen=suchen)
        if (laufend := self.modem.aufgabe) is not None and not laufend.done():
            await asyncio.wait(
                {laufend}
            )  # die laufende zuerst fertig werden lassen – kein Weg an ihr vorbei
        router = self.gedaechtnis.lan.router or self.box.zugang.host
        kandidaten, kennwort, gespeichert = self._modem_parameter(meldung, router)
        # als Hintergrund-Aufgabe des Eintrags (beim Entladen abgebrochen); arbeiten() prüft unter der Sperre selbst,
        # ob noch etwas fällig ist
        aufgabe = self.config_entry.async_create_background_task(
            self.hass,
            self._modem_arbeiten(kandidaten, kennwort, sprache_von(self.hass), gespeichert),
            f"{DOMAIN}_modem_jetzt",
        )
        self.modem.aufgabe = aufgabe
        await asyncio.wait({aufgabe})
        return True

    def _modem_hinweise(self, stand: ve.Modemstand | None) -> None:
        """Reparatur-Hinweise: Kennwort abgelehnt (gleich), Gerät nicht erreichbar (erst nach zwei Takten)."""
        befund = stand.befund if stand else None
        self._hinweis(ve.REPARATUR["anmeldung_abgelehnt"], befund == "anmeldung_abgelehnt")
        self._hinweis(
            ve.REPARATUR["nicht_erreichbar"],
            befund == "nicht_erreichbar" and self.modem.nicht_erreichbar_lange,
        )

    async def messen(self, grund: str, jetzt: float | None = None) -> bool:
        """Messung bei Ookla starten (Messplan oder „Jetzt messen“); als ausgelöst gilt sie ab jetzt."""
        if not await async_messen(self.hass, self.speedtest.sensoren):
            return False
        self.ausgeloest = jetzt or time.time()
        self.ausloese_grund = grund
        LOGGER.debug("Heimnetz: Ookla-Messung ausgelöst (%s)", grund)
        return True

    def serie_starten(self) -> bool:
        """WU-0001: n Durchläufe hintereinander (Anzahl aus dem Messplan), alle Ookla-Tests reihum. False, wenn
        schon eine Serie läuft oder es Ookla nicht gibt."""
        if self.serie_status is not None or self.einstellungen is None:
            return False
        tests = alle_finden(self.hass)
        if not tests or not self.hass.services.has_service(OOKLA, "run_speedtest"):
            return False
        n = self.einstellungen.plan.serie
        self.serie_status = {"n": n, "lauf": 0}
        self._serie_aufgabe = self.hass.async_create_background_task(
            self._serie(tests, n), f"{DOMAIN}_serie"
        )
        return True

    async def _serie(self, tests: list, n: int) -> None:
        laeufe: list[sr.Lauf] = []
        try:
            for i in range(n):
                s = tests[i % len(tests)]
                self.serie_status = {"n": n, "lauf": i + 1}
                vorher = zeitpunkt(self.hass.states.get(s.last_test)) or 0.0
                await self.hass.services.async_call(
                    OOKLA, "run_speedtest", {"entity_id": s.last_test}, blocking=False
                )
                self.ausgeloest = time.time()
                if (neu := await self._warten_auf(s, vorher)) is not None:
                    laeufe.append(neu)
                else:
                    LOGGER.warning("Heimnetz: Durchlauf %s der Serie ohne Ergebnis", i + 1)
        finally:
            self.serie_status = None
        if laeufe:
            # AN-0007: während der Serie gelöschte Durchläufe zählen nicht
            try:
                weg = [
                    x.t
                    for x in laeufe
                    if await self.hass.async_add_executor_job(self.datenbank.ist_geloescht, x.t)
                ]
            except SCHREIBFEHLER:
                weg = []
            laeufe = [x for x in laeufe if not ms.ist_geloescht(x.t, weg)]
        if laeufe and self.einstellungen is not None:
            await self.einstellungen.async_serie_merken(
                sr.ergebnis(laeufe, self.einstellungen.wert.tarif_down, n)
            )

    async def _warten_auf(self, s, vorher: float) -> sr.Lauf | None:
        """Bis der Sensor „letzter Test“ einen neueren Zeitpunkt zeigt; dann kurz warten, bis alle Werte da sind."""
        frist = time.monotonic() + sr.WARTEN_S
        while time.monotonic() < frist:
            await asyncio.sleep(SERIE_TAKT_S)
            t = zeitpunkt(self.hass.states.get(s.last_test))
            if t is not None and t > vorher:
                await asyncio.sleep(SERIE_TAKT_S)
                return lauf(self.hass, s)
        return None

    async def _speichern(self, stand: sm.Stand) -> None:
        """Ergebnis in die Datenbank. Ein Fehler beim Schreiben macht den Abruf nicht ungültig (die Box wurde ja
        gelesen); die Zeilen bleiben ausstehend und gehen beim nächsten Mal mit."""
        self._ausstehend_journal += [Journalzeile(stand.zeit, e) for e in stand.ereignisse]
        self._ausstehend_protokoll += stand.protokoll
        del self._ausstehend_journal[:-AUSSTEHEND_HOECHSTENS]
        del self._ausstehend_protokoll[:-AUSSTEHEND_HOECHSTENS]
        aufraeumen = stand.zeit - self._aufgeraeumt >= AUFRAEUMEN_S
        try:
            vergleich, aufgeraeumt = await self.hass.async_add_executor_job(
                self._schreiben, stand.zeit, aufraeumen
            )
        except SCHREIBFEHLER as err:
            LOGGER.warning(
                "Heimnetz: Schreiben in die Datenbank fehlgeschlagen (%s), nächster Versuch in einer Minute",
                err,
            )
            return
        self._ausstehend_journal.clear()
        self._ausstehend_protokoll.clear()
        self._gespeichert = vergleich
        if aufgeraeumt:
            self._aufgeraeumt = stand.zeit

    def _schreiben(self, jetzt: float, aufraeumen: bool) -> tuple[str, bool]:
        """Blockierend. Das Gedächtnis wird nur geschrieben, wenn sich mehr als der Zähler-Ring geändert hat –
        der ändert sich jede Minute, ist aber nach einem Neustart ohnehin schnell wieder voll."""
        daten = sm.gedaechtnis_als_dict(self.gedaechtnis)
        vergleich = json.dumps({**daten, "ring": None}, ensure_ascii=False, sort_keys=True)
        gedaechtnis = (
            json.dumps(daten, ensure_ascii=False) if vergleich != self._gespeichert else None
        )
        self.datenbank.abruf_schreiben(
            self._ausstehend_journal, self._ausstehend_protokoll, gedaechtnis, jetzt
        )
        aufgeraeumt = aufraeumen and self.datenbank.aufraeumen(jetzt) is not None
        return vergleich, aufgeraeumt

    def _messung(self, messung: Messung) -> None:
        """Neue Ookla-Messung (im Event-Loop gemeldet): im Executor schreiben; als eingetragen gilt sie erst danach."""
        aufgabe = self.hass.async_create_task(self._messung_schreiben(messung))
        self._schreibvorgaenge.add(aufgabe)
        aufgabe.add_done_callback(self._schreibvorgaenge.discard)

    async def _messung_schreiben(self, messung: Messung) -> None:
        try:
            geloescht = await self.hass.async_add_executor_job(
                self.datenbank.ist_geloescht, messung.t
            )
        except SCHREIBFEHLER as err:
            LOGGER.warning("Heimnetz: Speedtest-Messung nicht geprüft (%s), wird nachgeholt", err)
            return
        if geloescht:
            # AN-0007: gelöscht – Ookla zeigt sie weiter als letzten Test; nicht wieder eintragen, nicht mehr lesen
            self.letzte_messung = max(self.letzte_messung, messung.t)
            return
        if self.kontext_holen is not None:
            try:
                messung = replace(messung, kontext=await self.kontext_holen(messung))
            except Exception:  # die Messung zählt auch ohne Momentaufnahme
                LOGGER.exception("Heimnetz: Momentaufnahme zur Messung fehlgeschlagen")
        try:
            n = await self.hass.async_add_executor_job(
                self.datenbank.messungen_schreiben, [messung]
            )
            # AN-0007: inzwischen gelöscht (während der Momentaufnahme) – nicht als letzte Messung zeigen
            weg = not n and await self.hass.async_add_executor_job(
                self.datenbank.ist_geloescht, messung.t
            )
        except SCHREIBFEHLER as err:
            LOGGER.warning(
                "Heimnetz: Speedtest-Messung nicht gespeichert (%s), wird nachgeholt", err
            )
            return
        self.letzte_messung = max(self.letzte_messung, messung.t)
        if weg:
            return
        if self.letzte is None or messung.t >= self.letzte.t:
            self.letzte = messung
            self.async_update_listeners()

    async def messung_loeschen(self, kennung: float) -> float | None:
        """AN-0007: Messung in der eigenen Datenbank löschen (Recorder-Verlauf der Ookla-Entitäten bleibt), samt
        Momentaufnahme, Durchlauf der gemerkten Serie und Journalzeile. Zeitpunkt der gelöschten Messung, None =
        unbekannte Kennung. `letzte_messung` bleibt: gemessen wurde ja, der Messplan zählt ab dann weiter."""
        tz, sprache = dt_util.get_default_time_zone(), sprache_von(self.hass)
        t = await self.hass.async_add_executor_job(
            self.datenbank.messung_loeschen,
            kennung,
            time.time(),
            lambda x: ms.geloescht_ereignis(x, tz, sprache),
        )
        if t is None:
            return None
        e = self.einstellungen
        if e is not None and e.letzte_serie:
            rest = sr.ohne_lauf(e.letzte_serie, lambda x: ms.gleich(x, t), e.wert.tarif_down)
            if rest is not None:
                await e.async_serie_merken(rest)
        if self.letzte is not None and ms.gleich(self.letzte.t, t):
            # Sensor „Letzte Messung“: zurück auf die Messung davor (oder keine)
            self.letzte = await self.hass.async_add_executor_job(self.datenbank.letzte_lesen)
            self.async_update_listeners()
        return t

    async def async_schliessen(self) -> None:
        """Beim Entladen: Speedtest lösen, laufende Schreibvorgänge abwarten – danach darf die Datenbank zu."""
        self.speedtest.trennen()
        if self.modem.aufgabe is not None and not self.modem.aufgabe.done():
            self.modem.aufgabe.cancel()
        if self._serie_aufgabe is not None and not self._serie_aufgabe.done():
            self._serie_aufgabe.cancel()
        if self._schreibvorgaenge:
            await asyncio.gather(*self._schreibvorgaenge, return_exceptions=True)

    async def _box_lesen(self, langsam: bool, router: str, sprache: str) -> BoxDaten:
        """Zugang jedes Mal frisch aus FRITZ!Box Tools: ein neues Kennwort dort gilt ab dem nächsten Abruf."""
        zugang = zugang_aus_fritz(self.hass, self.fritz_eintrag)
        self._hinweis(ISSUE_FRITZ_FEHLT, zugang is None)
        if zugang is None:
            return BoxDaten(fehler=[sp.t("FRITZ!Box Tools: Eintrag fehlt", sprache)])
        if zugang != self.box.zugang:
            await self.hass.async_add_executor_job(self.box.neuer_zugang, zugang)
        mobil_fragen = self.gedaechtnis.mobil_dienst is not False
        zugang_fragen, self.zugang_neu = self.zugang_neu, False
        try:
            daten: BoxDaten = await self.hass.async_add_executor_job(
                self.box.holen,
                langsam,
                mobil_fragen,
                router,
                sprache,
                zugang_fragen,
                self.gedaechtnis.zugang_haupt,
            )
        except AnmeldungAbgelehnt:
            await self.hass.async_add_executor_job(self.box.trennen)
            self._hinweis(ISSUE_ANMELDUNG, True)
            return BoxDaten(fehler=[sp.t("FRITZ!Box: Anmeldung abgelehnt", sprache)])
        self._hinweis(ISSUE_ANMELDUNG, False)
        if daten.geraete is None:
            await self.hass.async_add_executor_job(
                self.box.trennen
            )  # nächstes Mal neu verbinden (Neustart der Box)
        return daten

    def _hinweis(self, schluessel: str, an: bool) -> None:
        """Reparatur-Hinweis nur für Probleme, die der Benutzer lösen kann (G-21)."""
        if an:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                schluessel,
                is_fixable=False,
                severity=ir.IssueSeverity.ERROR,
                translation_key=schluessel,
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, schluessel)
