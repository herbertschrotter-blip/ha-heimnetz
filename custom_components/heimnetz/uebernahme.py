"""Umstieg von der alten Integration „netzwerk“ (WU-0006): Daten beim ersten Laden übernehmen, alte nie anfassen.

Übernommen werden die Datenbank (Journal, Protokoll, Messungen, Gedächtnis – über die Sicherungs-Schnittstelle von
SQLite, damit auch der Inhalt der WAL-Datei mitkommt), die übrigen Dateien aus `<config>/netzwerk/` (Bilder der
Tickets), die Speicher der alten Einrichtung (Einstellungen, Messplan, gemerkte Masten) und die Tickets. Die Speicher
werden über `Store` geladen, nie als Datei aus `.storage/` gelesen. Was der Plan ist, steht in `logik/uebernahme.py`.
Solange eine alte Einrichtung nicht deaktiviert ist, wird weder eingerichtet noch übernommen (nie beide an der Box).
"""

from __future__ import annotations

import logging
import os
import shutil
import sqlite3
from collections.abc import Callable, Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.storage import Store

from .const import ALT_DOMAIN, CONF_ALT_EINTRAG, CONF_UEBERNOMMEN, DATENBANK, DOMAIN
from .logik import uebernahme as ue

LOGGER = logging.getLogger(__package__)
SPEICHER_VERSION = 1  # alle übernommenen Speicher haben Version 1 (Einstellungen, Masten, OSM, OpenCellID, Tickets)
type Regel = Callable[[Mapping[str, Any] | None, Mapping[str, Any] | None], dict[str, Any] | None]


def alte_aktiv(hass: HomeAssistant) -> bool:
    """Gibt es eine Einrichtung der alten Integration, die nicht deaktiviert ist? Ignorierte zählen nicht."""
    return ue.alte_aktiv(
        e.disabled_by is not None
        for e in hass.config_entries.async_entries(ALT_DOMAIN, include_ignore=False)
    )


def alte_einrichtung(hass: HomeAssistant, entry_id: str | None = None) -> ConfigEntry | None:
    """Die alte Einrichtung: die gemerkte, sonst die erste (die alte Integration hatte höchstens eine)."""
    alte = hass.config_entries.async_entries(ALT_DOMAIN, include_ignore=False)
    return next((e for e in alte if e.entry_id == entry_id), None) or next(iter(alte), None)


async def async_uebernehmen(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, int]:
    """Einmal je Einrichtung (vor dem Öffnen der Datenbank): alles übernehmen, was es alt gibt und neu noch nicht.
    Die Tickets übernimmt `tickets.Meldungen` selbst (sie gehören der ganzen Integration, nicht der Einrichtung).

    Gibt zurück, was übernommen wurde (für das Protokoll); merkt sich danach in den Daten der Einrichtung, dass die
    Übernahme gelaufen ist. Ein Schreibfehler (z. B. Speicher voll, auch von SQLite) → später noch einmal
    (ConfigEntryNotReady); eine kaputte alte Datenbank (`ue.datenbank_kaputt`) lässt sich nicht retten: dann weiter
    ohne sie, wie bei einem unlesbaren Gedächtnis – die übrigen Dateien kommen trotzdem mit."""
    alt = alte_einrichtung(hass, entry.data.get(CONF_ALT_EINTRAG))
    try:
        ergebnis = await hass.async_add_executor_job(
            _dateien, hass.config.path(ALT_DOMAIN), hass.config.path(DATENBANK)
        )
    except OSError as err:
        raise ConfigEntryNotReady(f"Daten der alten Integration nicht übernommen: {err}") from err
    ergebnis["speicher"] = 0
    if alt is not None:
        for alt_key, neu_key in ue.speicher_schluessel(
            ALT_DOMAIN, alt.entry_id, DOMAIN, entry.entry_id
        ):
            if await _speicher(hass, alt_key, neu_key, ue.speicher_uebernehmen):
                ergebnis["speicher"] += 1
    hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_UEBERNOMMEN: True})
    if any(ergebnis.values()):
        LOGGER.info("Heimnetz: Daten der alten Integration übernommen (%s)", ergebnis)
    return ergebnis


async def async_meldungen_uebernehmen(hass: HomeAssistant) -> bool:
    """Tickets (Speicher `netzwerk.meldungen`, eine Liste für die ganze Integration) mit ihren Nummern; True, wenn
    übernommen wurde. Nur wenn die alte Integration nicht mehr läuft – sonst schriebe sie danach weiter in ihre."""
    if alte_aktiv(hass):
        return False
    return await _speicher(
        hass, f"{ALT_DOMAIN}.meldungen", f"{DOMAIN}.meldungen", ue.meldungen_uebernehmen
    )


async def _speicher(hass: HomeAssistant, alt_key: str, neu_key: str, regel: Regel) -> bool:
    neu: Store[dict[str, Any]] = Store(hass, SPEICHER_VERSION, neu_key)
    alt: Store[dict[str, Any]] = Store(hass, SPEICHER_VERSION, alt_key)
    inhalt = regel(await neu.async_load(), await alt.async_load())
    if inhalt is None:
        return False
    await neu.async_save(inhalt)
    return True


def _dateien(alt_ordner: str, neu_db: str) -> dict[str, int]:
    """Blockierend: Datenbank und übrige Dateien vom alten in den Ordner der neuen Datenbank kopieren (nur was fehlt).
    Jede Datei erst unter einem Zwischennamen, dann umbenannt: nie eine halbe Kopie, die als „schon da“ gälte."""
    ergebnis = {"datenbank": 0, "dateien": 0}
    if not os.path.isdir(alt_ordner):
        return ergebnis
    alt_db = os.path.join(alt_ordner, ue.ALT_DATENBANK)
    neu_ordner = os.path.dirname(neu_db)
    os.makedirs(neu_ordner, exist_ok=True)
    if ue.datenbank_planen(os.path.isfile(alt_db), os.path.exists(neu_db)):
        try:
            _datenbank_kopieren(alt_db, neu_db)
            ergebnis["datenbank"] = 1
        except sqlite3.DatabaseError as err:
            name = getattr(err, "sqlite_errorname", None)
            if not ue.datenbank_kaputt(name):
                # Platte voll, Ein-/Ausgabe, gesperrt …: vorübergehend → ConfigEntryNotReady, später noch einmal
                raise OSError(f"{name or type(err).__name__}: {err}") from err
            # nicht zu retten: weiter ohne sie (die Bilder der Tickets kommen trotzdem mit)
            LOGGER.error(
                "Heimnetz: alte Datenbank nicht übernommen (%s: %s), weiter ohne", name, err
            )
    for quelle, ziel in ue.dateien_planen(_liste(alt_ordner), _liste(neu_ordner)):
        pfad = os.path.join(neu_ordner, ziel)
        os.makedirs(os.path.dirname(pfad), exist_ok=True)
        zwischen = f"{pfad}.uebernahme"
        shutil.copy2(os.path.join(alt_ordner, quelle), zwischen)
        os.replace(zwischen, pfad)
        ergebnis["dateien"] += 1
    return ergebnis


def _liste(ordner: str) -> list[str]:
    """Alle Dateien unter `ordner`, relativ und mit „/“."""
    pfade = []
    for wurzel, _, dateien in os.walk(ordner):
        for name in dateien:
            pfade.append(os.path.relpath(os.path.join(wurzel, name), ordner).replace(os.sep, "/"))
    return pfade


def _datenbank_kopieren(quelle: str, ziel: str) -> None:
    """Die alte Datei (mit ihrer WAL-Datei) erst daneben unter Zwischennamen kopieren und nur die Kopie öffnen – SQLite
    legt beim Öffnen sonst -wal/-shm neben die alte. Über die Sicherungs-Schnittstelle in eine Zwischendatei, dann
    umbenennen: nie eine halbe Datenbank."""
    kopie = f"{ziel}.quelle"
    zwischen = f"{ziel}.uebernahme"
    weg = [kopie + e for e in ("", *ue.DATENBANK_BEGLEITER)]
    for pfad in (*weg, zwischen):
        if os.path.exists(pfad):
            os.remove(pfad)
    try:
        shutil.copy2(quelle, kopie)
        if os.path.isfile(quelle + "-wal"):
            shutil.copy2(quelle + "-wal", kopie + "-wal")
        alt = sqlite3.connect(kopie)
        try:
            neu = sqlite3.connect(zwischen)
            try:
                alt.backup(neu)
            finally:
                neu.close()
        finally:
            alt.close()
        os.replace(zwischen, ziel)
    finally:
        for pfad in (*weg, zwischen):
            if os.path.exists(pfad):
                os.remove(pfad)
