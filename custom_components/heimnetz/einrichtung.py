"""Einrichtung (WU-0007): liest aus Home Assistant, was für Heimnetz eingerichtet ist – geladene Integrationen,
Config-Einträge, heruntergeladene Custom Components, die eigenen Optionen. Bewertet wird in `logik/einrichtung.py`.

Nur lesen: nichts installieren, nichts herunterladen, kein Neustart. Gerätenamen und Adressen bleiben außen vor; von
der Box geht nur das Modell an die Seite, vom OpenCellID-Schlüssel nur „eingetragen ja/nein“.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_custom_components

from .const import CONF_FRITZ_EINTRAG, CONF_OPENCELLID, DOMAIN, FRITZ, HA_MINDEST, sprache
from .logik import einrichtung as ei

LOGGER = logging.getLogger(__package__)


def _recorder_tage(hass: HomeAssistant) -> int | None:
    """Aufbewahrung des Recorders in Tagen – nur, wenn er geladen ist und sie verrät."""
    if ei.RECORDER not in hass.config.components:
        return None
    try:
        from homeassistant.components.recorder import get_instance  # noqa: PLC0415

        tage = get_instance(hass).keep_days
    except KeyError, AttributeError, ImportError:
        return None
    return tage if isinstance(tage, int) else None


async def stand(hass: HomeAssistant) -> ei.Stand:
    """Was gerade eingerichtet ist (Momentaufnahme beim Öffnen des Reiters)."""
    eintraege: dict[str, int] = {}
    geladen_e: dict[str, int] = {}
    for domain in ei.MIT_EINTRAG:
        alle = hass.config_entries.async_entries(domain)
        eintraege[domain] = len(alle)
        geladen_e[domain] = sum(1 for e in alle if e.state is ConfigEntryState.LOADED)
    heimnetz = hass.config_entries.async_entries(DOMAIN)
    opencellid = False
    box_modell = ""
    if heimnetz:
        e = heimnetz[0]
        opencellid = bool((e.options.get(CONF_OPENCELLID) or "").strip())
        # zählt der Eintrag von FRITZ!Box Tools, aus dem Heimnetz den Zugang holt
        eintraege[FRITZ] = int(
            hass.config_entries.async_get_entry(e.data.get(CONF_FRITZ_EINTRAG, "")) is not None
        )
        if e.state is ConfigEntryState.LOADED and (info := e.runtime_data.abruf.box_info):
            box_modell = info.modell
    try:
        eigene = await async_get_custom_components(hass)
    except Exception:  # noqa: BLE001 – Anzeige darf am Lesen der Custom Components nicht scheitern
        LOGGER.debug("Heimnetz: Custom Components nicht lesbar", exc_info=True)
        eigene = {}
    return ei.Stand(
        ha_version=HA_VERSION,
        ha_mindest=HA_MINDEST,
        geladen=frozenset(c for c in hass.config.components if "." not in c),
        eintraege=eintraege,
        eintraege_geladen=geladen_e,
        heruntergeladen=frozenset(d for d in eigene if d in ei.AUS_HACS),
        box_modell=box_modell,
        recorder_tage=_recorder_tage(hass),
        opencellid=opencellid,
    )


async def bewertung(hass: HomeAssistant) -> dict[str, Any]:
    """Antwort für `heimnetz/einrichtung` in der Sprache der Seite."""
    return ei.bewerten(await stand(hass), sprache(hass))
