"""HA-Sicherung: vorher die eigene Datenbank abschließen, danach weiter schreiben (wie ha-baustelle, G-14)."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .const import DOMAIN


def _datenbanken(hass: HomeAssistant) -> list:  # type: ignore[type-arg]
    return [
        e.runtime_data.datenbank
        for e in hass.config_entries.async_loaded_entries(DOMAIN)
        if getattr(e, "runtime_data", None) is not None
    ]


async def async_pre_backup(hass: HomeAssistant) -> None:
    """WAL in die Datei, Schreiben anhalten – die Sicherung kopiert eine stimmige Datei."""
    for db in _datenbanken(hass):
        await hass.async_add_executor_job(db.anhalten)


async def async_post_backup(hass: HomeAssistant) -> None:
    """Schreiben wieder freigeben; was in der Zwischenzeit anfiel, wird jetzt geschrieben."""
    for db in _datenbanken(hass):
        await hass.async_add_executor_job(db.fortsetzen)
