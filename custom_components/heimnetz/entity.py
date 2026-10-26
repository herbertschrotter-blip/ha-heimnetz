"""Gemeinsame Grundlage der Entitäten: ein Gerät „Heimnetz“ je Einrichtung."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Abruf


class HeimnetzEntitaet(CoordinatorEntity[Abruf]):
    """has_entity_name, feste unique_id aus Eintrag und Schlüssel (G-13)."""

    _attr_has_entity_name = True
    BRAUCHT_BOX = True  # hängt der Wert von der Box ab? Dann bei Ausfall nicht verfügbar (G-21)

    def __init__(self, abruf: Abruf, schluessel: str) -> None:
        super().__init__(abruf)
        entry = abruf.config_entry
        self._attr_translation_key = schluessel
        self._attr_unique_id = f"{entry.entry_id}_{schluessel}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        return super().available and (not self.BRAUCHT_BOX or self.coordinator.data.box_erreichbar)
