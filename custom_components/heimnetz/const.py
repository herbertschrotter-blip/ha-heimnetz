"""Konstanten der Integration."""

from __future__ import annotations

from contextvars import ContextVar
from datetime import timedelta
from typing import TYPE_CHECKING

from .logik.sprache import waehle

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

DOMAIN = "heimnetz"
FRITZ = "fritz"  # Domäne von FRITZ!Box Tools: daher kommt der Zugang zur Box
CONF_FRITZ_EINTRAG = "fritz_eintrag"
INTERVALL = timedelta(seconds=60)
DATENBANK = "heimnetz/heimnetz.db"  # relativ zur HA-Konfiguration
ISSUE_FRITZ_FEHLT = "fritz_fehlt"
ISSUE_ANMELDUNG = "anmeldung"
CONF_OPENCELLID = "opencellid_schluessel"  # Optionen: Schlüssel für OpenCellID (Standort des Masts)
# WU-0006: Umstieg von der alten Integration „netzwerk“ (Daten übernehmen, nie beide zugleich an der Box)
ALT_DOMAIN = "netzwerk"
CONF_ALT_EINTRAG = "alt_eintrag"  # Einrichtung der alten Integration, deren Daten übernommen werden
CONF_UEBERNOMMEN = "uebernommen"  # Übernahme ist gelaufen (nur einmal je Einrichtung)
ISSUE_ALT_AKTIV = "alt_aktiv"
# WU-0006: öffentlich melden – vorausgefülltes Issue, abgeschickt mit dem eigenen GitHub-Konto (kein Token hier)
GITHUB_REPO = "herbertschrotter-blip/ha-heimnetz"
GITHUB_ISSUE_NEU = f"https://github.com/{GITHUB_REPO}/issues/new"


# Sprache, die die Seite beim WebSocket-Befehl mitschickt (Profil des Nutzers); gilt nur in der Aufgabe dieses Befehls
SEITEN_SPRACHE: ContextVar[str | None] = ContextVar("heimnetz_seiten_sprache", default=None)


def sprache(hass: HomeAssistant) -> str:
    """WU-0006: Sprache der Texte, die die Integration erzeugt – „de“ oder „en“. Für die Seite (Antworten auf
    WebSocket-Befehle) die Sprache aus dem Profil des Nutzers, die sie mitschickt; sonst die von Home Assistant."""
    return waehle(SEITEN_SPRACHE.get() or hass.config.language)


def sprache_system(hass: HomeAssistant) -> str:
    """Sprache von Home Assistant – für alles, was gespeichert wird (Journal, Befunde des Abrufs), nie die eines
    einzelnen Nutzers."""
    return waehle(hass.config.language)
