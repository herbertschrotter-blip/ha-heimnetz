"""🔬 Diagnose (WU-0008, seit WU-0009 Stufe 2 mit den Bausteinen): Rohdaten eines vorgeschalteten Geräts abfragen –
dünner HA-Teil, nur lesend.

Ablauf: Startseite lesen und erkennen (`logik.vorgeschaltet.erkennen`, bei ZTE die Schnittstelle über lesende Proben),
dann der Baustein des erkannten Geräts (`vorgeschaltet/`) – dieselben Abfragen wie im laufenden Abruf, hier aber mit
allen Rohdaten (geschwärzt) und jeder Stufe als eigener Eintrag. Bei ZTE kommt die jeweils andere Schnittstelle als
Probe dazu. Geräte, die Heimnetz nur erkennt (Glasfaser-Modem, MikroTik …), liefern die Startseite.

Sicherheit wie in `vorgeschaltet/netz.py` (nur private Adressen, keine Weiterleitung, Zeit- und Größengrenzen). Das
Kennwort wird nur für diese Abfrage verwendet, nie gespeichert, nie protokolliert und steht in keiner Antwort.
Abgefragt wird nie gleichzeitig mit dem laufenden Abruf (gemeinsame Sperre).
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant

from .logik import kontext as kx
from .logik import modem as lm
from .logik import vorgeschaltet as ve
from .logik.sprache import DE, merke, t
from .vorgeschaltet import baustein_lesen, erkennen_aus, integrationen, netz, zte
from .vorgeschaltet.netz import GESAMT_S, Lauf, gekuerzt, titel

VORGABE_ADRESSE = "192.168.0.1"

_N_STARTSEITE = merke("Startseite")
_N_UBUS = merke("zweite Schnittstelle (ubus)")
_N_GOFORM = merke("zweite Schnittstelle (goform)")


@dataclass
class _Leer:
    """Ergebnis ohne Abfrage (Adresse nicht erlaubt)."""

    sprache: str
    abfragen: list[dict[str, Any]] = field(default_factory=list)
    daten: dict[str, Any] = field(default_factory=dict)
    geschwaerzt: int = 0


async def abfragen(
    hass: HomeAssistant,
    adresse: str,
    kennwort: str | None,
    sprache: str = DE,
    sperre: asyncio.Lock | None = None,
) -> dict[str, Any]:
    """Erkennen und alle passenden Schnittstellen abfragen – jede Stufe als eigener Eintrag."""
    adresse = (adresse or "").strip()
    if not lm.adresse_erlaubt(adresse):
        return _antwort(_Leer(sprache), befund="adresse_nicht_erlaubt")
    async with sperre or contextlib.nullcontext():
        async with netz.neue_session(aiohttp.ClientTimeout(total=GESAMT_S)) as session:
            lauf = Lauf(session, adresse, sprache)
            try:
                return await asyncio.wait_for(_ablauf(hass, lauf, kennwort), timeout=GESAMT_S)
            except TimeoutError:
                return _antwort(lauf, befund=None if lauf.abfragen else "nicht_erreichbar")


async def _ablauf(hass: HomeAssistant, lauf: Lauf, kennwort: str | None) -> dict[str, Any]:
    startseite = await lauf.startseite()
    if startseite is None:
        lauf.eintrag(_N_STARTSEITE, "fehler", "")
        return _antwort(lauf, befund="nicht_erreichbar")
    lauf.ablegen(
        "startseite",
        {
            "titel": titel(startseite),
            "kopf": dict(lauf.kopf),
            "rohdaten": gekuerzt(startseite, 1200),
        },
    )
    erkennung = await erkennen_aus(lauf, hass, startseite)
    lauf.abfragen.insert(
        0,
        {
            "name": t(_N_STARTSEITE, lauf.sprache),
            "status": "ok" if erkennung else "fehler",
            "angabe": t("{name} erkannt", lauf.sprache, name=erkennung.name)
            if erkennung
            else t("Gerät nicht erkannt", lauf.sprache),
        },
    )
    if erkennung is None:
        return _antwort(lauf, befund="nicht_erkannt")
    if erkennung.b.art == "box":
        return _antwort(lauf, erkennung, befund="fritzbox")
    if erkennung.b.integration and integrationen.eingerichtet(hass, erkennung.b.integration):
        # die HA-Integration hat eine Sitzung am Gerät – eine eigene Anmeldung würde sie stören
        return _antwort(lauf, erkennung, befund="integration_eingerichtet")
    lesung, _ = await baustein_lesen(hass, lauf, erkennung, kennwort, diagnose=True)
    # ZTE: die jeweils andere Schnittstelle als Probe (eine lesende Abfrage, keine Anmeldung)
    if erkennung.baustein == "zte_goform" and lauf.zeit_uebrig():
        da = await zte.ubus_probe(lauf)
        lauf.eintrag(
            _N_UBUS,
            "ok" if da else "aus",
            t("vorhanden" if da else "nicht vorhanden", lauf.sprache),
        )
    elif erkennung.baustein == "zte_ubus" and lauf.zeit_uebrig():
        da = await zte.goform_probe(lauf) is not None
        lauf.eintrag(
            _N_GOFORM,
            "ok" if da else "aus",
            t("vorhanden" if da else "nicht vorhanden", lauf.sprache),
        )
    # ohne Kennwort ist kein Befund – die Diagnose geht auch ohne Anmeldung
    befund = None if lesung.befund == "ohne_kennwort" else lesung.befund
    return _antwort(lauf, erkennung, befund=befund, umgerechnet=kx.mobilfunk(lesung.mobil))


def _antwort(
    lauf: Lauf | _Leer,
    erkennung: ve.Erkennung | None = None,
    *,
    befund: str | None = None,
    umgerechnet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ok = sum(1 for a in lauf.abfragen if a["status"] == "ok")
    b = erkennung.b if erkennung else None
    return {
        "modell": erkennung.modell if erkennung else "",
        "erkannt": {
            "name": erkennung.name,
            "hersteller": b.hersteller,
            "schnittstelle": b.name or None,
            "baustein": erkennung.baustein,
            "werte": b.werte or bool(b.integration),
        }
        if erkennung and b
        else None,
        "abfragen": lauf.abfragen,
        "summen": {
            "ok": ok,
            "gesamt": len(lauf.abfragen),
            "werte": lm.werte_zaehlen(lauf.daten),
            "geschwaerzt": lauf.geschwaerzt,
        },
        "befund": befund,
        "hinweis": ve.befund_daten(befund, lauf.sprache),
        "umgerechnet": umgerechnet or None,
        "daten": lauf.daten,
    }
