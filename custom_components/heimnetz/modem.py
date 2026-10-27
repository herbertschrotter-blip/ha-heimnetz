"""Rohdaten eines vorgeschalteten Modems abfragen (WU-0008): dünner HA-Teil über das Netz, nur lesend.

Kommt das Internet über ein eigenes 5G/LTE-Modem vor der FRITZ!Box (z. B. ein ZTE von Drei Österreich), kennt die Box
das Funknetz nicht. Dieses Werkzeug fragt auf Knopfdruck die Weboberfläche des Modems im eigenen Heimnetz ab und gibt
die Rohdaten geschwärzt zurück, damit der Entwickler die Unterstützung bauen kann – es wertet nichts aus.

Nur lesen: abgefragt werden ausschließlich lesende Schnittstellen (ZTE `goform_get_cmd_process`) plus die Anmeldung
und Abmeldung mit dem Kennwort, das der Besitzer selbst eingibt. `goform_set_cmd_process` wird NUR mit `goformId=LOGIN`
bzw. `LOGOUT` aufgerufen, nie mit einem anderen set-Befehl. Es werden keine Einstellungen des Modems geändert.

Sicherheit: nur private Adressen im eigenen Heimnetz (`logik.modem.adresse_erlaubt`), keine Hostnamen; Weiterleitungen
werden nicht verfolgt; je Anfrage ein kurzes Zeitlimit und eine Obergrenze für die Antwortgröße, dazu ein Gesamtlimit.
Das Kennwort wird nur für diese Abfrage verwendet, nie gespeichert, nie protokolliert und steht in keiner Antwort.
Vor der Rückgabe wird alles Vertrauliche geschwärzt (`logik.modem.schwaerzen`).
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant

from .logik import modem as lm
from .logik.sprache import DE, merke, t

LOGGER = logging.getLogger(__package__)

VORGABE_ADRESSE = "192.168.0.1"
ZEIT_S = 8  # Zeitlimit je Anfrage
GESAMT_S = 40  # Gesamtzeit aller Anfragen
GROESSE_MAX = 512 * 1024  # 512 KB je Antwort

# Breite Liste lesender Werte (ZTE goform). Was das Gerät nicht kennt, kommt leer zurück – auch das ist ein Ergebnis.
_CMD = (
    "modem_main_state,modem_model,hardware_version,wa_inner_version,cr_version,web_version,"
    "network_type,network_provider,rmcc,rmnc,signalbar,rssi,"
    "lte_rsrp,lte_rsrq,lte_rssi,lte_snr,lte_band,lte_ca_pcell_band,lte_ca_scell_band,lte_pci,"
    "lte_ca_pcell_freq,lte_ca_scell_freq,cell_id,lte_cell_id,enodeb_id,tac,lac,plmn,"
    "nr5g_action_band,nr5g_pci,nr5g_cell_id,nr5g_action_channel,nr5g_rsrp,nr5g_rsrq,nr5g_snr,"
    "Z5g_rsrp,Z5g_snr,Z5g_SINR,Z5g_CELL_ID,wan_active_band,wan_active_channel,ngbr_cell_info"
)

# goform_set_cmd_process ausschließlich hiermit – nie ein anderer set-Befehl.
_LOGIN = "LOGIN"
_LOGOUT = "LOGOUT"

# Namen der Stufen (übersetzt beim Anzeigen); merke(), damit der Sprachtest die englischen Zeilen findet.
_N_STARTSEITE = merke("Startseite")
_N_OHNE = merke("Werte ohne Anmeldung")
_N_ANMELDUNG = merke("Anmeldung")
_N_NACH = merke("Werte nach Anmeldung")
_N_UBUS = merke("zweite Schnittstelle (ubus)")


class _Lauf:
    """Sammelt die Stufen einer Abfrage; achtet auf die Gesamtzeit."""

    def __init__(self, session: aiohttp.ClientSession, sprache: str) -> None:
        self.session = session
        self.sprache = sprache
        self.start = time.monotonic()
        self.abfragen: list[dict[str, Any]] = []
        self.daten: dict[str, Any] = {}
        self.geschwaerzt = 0
        self.basis = ""

    def zeit_uebrig(self) -> bool:
        return (time.monotonic() - self.start) < GESAMT_S

    def eintrag(self, schluessel: str, name: str, status: str, angabe: str) -> None:
        self.abfragen.append({"name": t(name, self.sprache), "status": status, "angabe": angabe})

    def ablegen(self, schluessel: str, rohdaten: Any) -> int:
        """Rohdaten geschwärzt ablegen; gibt die Anzahl der Werte zurück."""
        rein, anzahl = lm.schwaerzen(rohdaten)
        self.daten[schluessel] = rein
        self.geschwaerzt += anzahl
        return lm.werte_zaehlen(rein)

    async def lesen(
        self, url: str, *, methode: str = "GET", daten: Any = None, referer: str | None = None
    ) -> tuple[int, str]:
        """Eine Anfrage; keine Weiterleitung, Zeitlimit, Antwortgröße begrenzt. (Status, Text)."""
        kopf = {"Referer": referer} if referer else None
        ssl = False if url.startswith("https:") else None
        async with self.session.request(
            methode,
            url,
            data=daten,
            headers=kopf,
            allow_redirects=False,
            ssl=ssl,
            timeout=aiohttp.ClientTimeout(total=ZEIT_S),
        ) as antwort:
            roh = await antwort.content.read(GROESSE_MAX + 1)
            return antwort.status, roh[:GROESSE_MAX].decode("utf-8", "replace")


def _neue_session(zeitlimit: aiohttp.ClientTimeout) -> aiohttp.ClientSession:
    """Eigene kurzlebige Session mit Cookie-Jar für die Anmeldung (Cookies auch für IP-Adressen: `unsafe=True`)."""
    return aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=zeitlimit)


def _json(text: str) -> dict[str, Any] | None:
    try:
        wert = json.loads(text)
    except ValueError:
        return None
    return wert if isinstance(wert, dict) else None


def _gekuerzt(text: str, grenze: int = 2000) -> str:
    """Rohantwort gekürzt, damit der Entwickler eine gescheiterte Stufe nachbessern kann."""
    knapp = text.strip()
    return knapp if len(knapp) <= grenze else knapp[:grenze] + " …"


async def abfragen(
    hass: HomeAssistant, adresse: str, kennwort: str | None, sprache: str = DE
) -> dict[str, Any]:
    """Startseite, goform ohne und mit Anmeldung, zweite Schnittstelle – jede Stufe als eigener Eintrag."""
    adresse = (adresse or "").strip()
    if not lm.adresse_erlaubt(adresse):
        return _antwort([], {}, 0, befund="adresse_nicht_erlaubt", modell="", sprache=sprache)

    zeitlimit = aiohttp.ClientTimeout(total=GESAMT_S)
    async with _neue_session(zeitlimit) as session:
        lauf = _Lauf(session, sprache)
        try:
            return await asyncio.wait_for(_ablauf(lauf, adresse, kennwort), timeout=GESAMT_S)
        except TimeoutError:
            if not lauf.abfragen:
                return _antwort([], {}, 0, befund="nicht_erreichbar", modell="", sprache=sprache)
            return _antwort(lauf.abfragen, lauf.daten, lauf.geschwaerzt, modell="", sprache=sprache)


async def _ablauf(lauf: _Lauf, adresse: str, kennwort: str | None) -> dict[str, Any]:
    # Stufe 1: Startseite, http zuerst, https (ohne Zertifikatsprüfung) nur, wenn http nicht antwortet.
    startseite = ""
    for schema in ("http", "https"):
        basis = f"{schema}://{adresse}"
        try:
            _, text = await lauf.lesen(f"{basis}/")
        except aiohttp.ClientError, TimeoutError:
            continue
        lauf.basis = basis
        startseite = text
        break
    if not lauf.basis:
        lauf.eintrag("startseite", _N_STARTSEITE, "fehler", "")
        return _antwort(
            lauf.abfragen,
            lauf.daten,
            lauf.geschwaerzt,
            befund="nicht_erreichbar",
            modell="",
            sprache=lauf.sprache,
        )

    zte, modell = lm.erkennen(startseite)
    lauf.ablegen(
        "startseite", {"titel": _titel(startseite), "rohdaten": _gekuerzt(startseite, 1200)}
    )
    lauf.eintrag(
        "startseite",
        _N_STARTSEITE,
        "ok" if zte else "fehler",
        t("{modell} erkannt", lauf.sprache, modell=modell)
        if modell
        else (t("ZTE erkannt", lauf.sprache) if zte else t("kein ZTE-Modem", lauf.sprache)),
    )
    if not zte:
        return _antwort(
            lauf.abfragen,
            lauf.daten,
            lauf.geschwaerzt,
            befund="kein_zte",
            modell=modell or "",
            sprache=lauf.sprache,
        )

    referer = f"{lauf.basis}/index.html"

    # Stufe 2: goform ohne Anmeldung.
    await _goform(lauf, referer, "ohne_anmeldung", _N_OHNE)

    # Stufe 3 + 4: Anmeldung nur mit dem Kennwort, das der Besitzer eingibt – ein einziger Versuch.
    befund = None
    if kennwort:
        angemeldet = await _anmelden(lauf, referer, kennwort)
        if angemeldet:
            await _goform(lauf, referer, "nach_anmeldung", _N_NACH)
            await _abmelden(lauf, referer)
        else:
            befund = "anmeldung_abgelehnt"

    # Stufe 5: zweite, nur lesende Schnittstelle (ubus) – höchstens eine Abfrage, sonst „nicht vorhanden“.
    await _ubus(lauf)

    return _antwort(
        lauf.abfragen,
        lauf.daten,
        lauf.geschwaerzt,
        befund=befund,
        modell=modell or "",
        sprache=lauf.sprache,
    )


async def _goform(lauf: _Lauf, referer: str, schluessel: str, name: str) -> dict[str, Any] | None:
    """Lesende ZTE-Abfrage; Erfolg mit „n Werte“, sonst HTTP-Code bzw. Fehler (Rohantwort gekürzt + geschwärzt)."""
    url = f"{lauf.basis}/goform/goform_get_cmd_process?isTest=false&multi_data=1&cmd={_CMD}"
    try:
        status, text = await lauf.lesen(url, referer=referer)
    except (aiohttp.ClientError, TimeoutError) as err:
        lauf.eintrag(schluessel, name, "fehler", type(err).__name__)
        return None
    werte = _json(text)
    if werte is None:
        lauf.ablegen(schluessel, {"rohdaten": _gekuerzt(text)})
        lauf.eintrag(schluessel, name, "fehler", f"HTTP {status}")
        return None
    anzahl = lauf.ablegen(schluessel, werte)
    lauf.eintrag(schluessel, name, "ok", t("{n} Werte", lauf.sprache, n=anzahl))
    return werte


async def _anmelden(lauf: _Lauf, referer: str, kennwort: str) -> bool:
    """Normales Web-Login des ZTE-Modems (LD-Wert holen, Hash bilden, goformId=LOGIN) – ein Versuch."""
    url = f"{lauf.basis}/goform/goform_get_cmd_process?isTest=false&cmd=LD"
    try:
        _, text = await lauf.lesen(url, referer=referer)
        ld = (_json(text) or {}).get("LD", "")
        kennwort_feld = lm.anmelde_hash(kennwort, ld) if ld else kennwort
        status, antwort = await lauf.lesen(
            f"{lauf.basis}/goform/goform_set_cmd_process",
            methode="POST",
            daten={"isTest": "false", "goformId": _LOGIN, "password": kennwort_feld},
            referer=referer,
        )
    except (aiohttp.ClientError, TimeoutError) as err:
        lauf.eintrag("anmeldung", _N_ANMELDUNG, "fehler", type(err).__name__)
        return False
    ergebnis = str((_json(antwort) or {}).get("result", ""))
    ok = ergebnis == "0"
    lauf.eintrag(
        "anmeldung",
        _N_ANMELDUNG,
        "ok" if ok else "fehler",
        t("angenommen", lauf.sprache) if ok else t("abgelehnt", lauf.sprache),
    )
    return ok


async def _abmelden(lauf: _Lauf, referer: str) -> None:
    """Abmelden, wenn das Gerät es anbietet (goformId=LOGOUT) – still, kein eigener Eintrag."""
    try:
        await lauf.lesen(
            f"{lauf.basis}/goform/goform_set_cmd_process",
            methode="POST",
            daten={"isTest": "false", "goformId": _LOGOUT},
            referer=referer,
        )
    except aiohttp.ClientError, TimeoutError:
        LOGGER.debug("Heimnetz: Modem-Abmeldung nicht möglich")


async def _ubus(lauf: _Lauf) -> None:
    """Eine einzige lesende Abfrage einer zweiten Schnittstelle; sonst „nicht vorhanden“."""
    if not lauf.zeit_uebrig():
        lauf.eintrag("ubus", _N_UBUS, "aus", t("nicht vorhanden", lauf.sprache))
        return
    try:
        status, text = await lauf.lesen(f"{lauf.basis}/ubus/")
    except aiohttp.ClientError, TimeoutError:
        lauf.eintrag("ubus", _N_UBUS, "aus", t("nicht vorhanden", lauf.sprache))
        return
    werte = _json(text)
    if status == 200 and werte is not None:
        anzahl = lauf.ablegen("ubus", werte)
        lauf.eintrag("ubus", _N_UBUS, "ok", t("{n} Werte", lauf.sprache, n=anzahl))
    else:
        lauf.eintrag("ubus", _N_UBUS, "aus", t("nicht vorhanden", lauf.sprache))


def _titel(startseite: str) -> str:
    treffer = re.search(r"<title>(.*?)</title>", startseite, re.IGNORECASE | re.DOTALL)
    return treffer.group(1).strip()[:120] if treffer else ""


def _antwort(
    abfragen_: list[dict[str, Any]],
    daten: dict[str, Any],
    geschwaerzt: int,
    *,
    befund: str | None = None,
    modell: str = "",
    sprache: str = DE,
) -> dict[str, Any]:
    ok = sum(1 for a in abfragen_ if a["status"] == "ok")
    werte = lm.werte_zaehlen(daten)
    return {
        "modell": modell,
        "abfragen": abfragen_,
        "summen": {"ok": ok, "gesamt": len(abfragen_), "werte": werte, "geschwaerzt": geschwaerzt},
        "befund": befund,
        "daten": daten,
    }
