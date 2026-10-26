"""Eigene Seite „Heimnetz“ in der Seitenleiste: JavaScript ausliefern (einmal je HA-Start), Seite anmelden solange die
Einrichtung geladen ist. Ist die Adresse schon von etwas anderem belegt, bleibt das unangetastet."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

URL_PANEL = "heimnetz"
URL_STATISCH = "/heimnetz_static"
WEBCOMPONENT = "heimnetz-panel"
DATEI = "heimnetz-panel.js"
ORDNER = Path(__file__).parent / "frontend"
DATA_STATISCH = f"{DOMAIN}_statisch"
DATA_EIGEN = f"{DOMAIN}_panel"  # die Seite unter URL_PANEL ist die eigene
LOGGER = logging.getLogger(__package__)


async def async_anmelden(hass: HomeAssistant) -> None:
    """Statischen Pfad nur einmal je HA-Start (geht nicht zweimal), die Seite bei jedem Laden der Einrichtung."""
    version = str((await async_get_integration(hass, DOMAIN)).version)
    if not hass.data.get(DATA_STATISCH):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_STATISCH, str(ORDNER), cache_headers=False)]
        )
        hass.data[DATA_STATISCH] = True
    if URL_PANEL in hass.data.get(frontend.DATA_PANELS, {}):
        if not hass.data.get(DATA_EIGEN):
            LOGGER.warning(
                "Heimnetz: die Adresse /%s ist schon belegt – die Seite wird nicht angemeldet",
                URL_PANEL,
            )
        return
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=URL_PANEL,
        webcomponent_name=WEBCOMPONENT,
        sidebar_title="Heimnetz",
        sidebar_icon="mdi:router-network",  # anders als das alte Dashboard, solange beide da sind
        module_url=f"{URL_STATISCH}/{DATEI}?v={version}",
        require_admin=False,
        config={"version": version},
    )
    hass.data[DATA_EIGEN] = True


def abmelden(hass: HomeAssistant) -> None:
    """Nur die eigene Seite entfernen."""
    if hass.data.pop(DATA_EIGEN, False):
        frontend.async_remove_panel(hass, URL_PANEL, warn_if_unknown=False)
