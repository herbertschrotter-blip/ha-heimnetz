"""Werte eines vorgeschalteten Geräts aus einer eingerichteten HA-Integration lesen (huawei_lte, netgear_lte,
teltonika) statt das Gerät selbst zu fragen. Nur lesen: Entitätsregister und Zustände, nichts wird gesteuert."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..logik.mobil import Mobilfunk
from ..logik.vorgeschaltet import integrationen as li


def eingerichtet(hass: HomeAssistant, domain: str) -> bool:
    return bool(domain) and bool(hass.config_entries.async_loaded_entries(domain))


def lesen(hass: HomeAssistant, domain: str) -> Mobilfunk | None:
    """Zustände der passenden Sensoren der ersten geladenen Einrichtung → gemeinsames Format."""
    eintraege = hass.config_entries.async_loaded_entries(domain)
    if not eintraege:
        return None
    werte: dict[str, str] = {}
    einheiten: dict[str, str | None] = {}
    for e in er.async_entries_for_config_entry(er.async_get(hass), eintraege[0].entry_id):
        if e.domain != "sensor" or e.platform != domain:
            continue
        if (feld := li.feld(domain, e.unique_id)) and (zustand := hass.states.get(e.entity_id)):
            werte[feld] = zustand.state
            einheiten[feld] = zustand.attributes.get("unit_of_measurement")
    return li.aus_zustaenden(domain, werte, einheiten)
