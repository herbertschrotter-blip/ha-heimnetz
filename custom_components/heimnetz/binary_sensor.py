"""Prüfungen vom Pi aus: FRITZ!Box, Internet, Namensauflösung. Hängen nicht davon ab, ob die Box TR-064 beantwortet."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import EintragMitLaufzeit
from .coordinator import Abruf
from .entity import HeimnetzEntitaet

PRUEFUNGEN = (("pi_fritzbox", "box"), ("pi_internet", "internet"), ("pi_dns", "dns"))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EintragMitLaufzeit,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    abruf = entry.runtime_data.abruf
    async_add_entities(PiPruefung(abruf, schluessel, feld) for schluessel, feld in PRUEFUNGEN)


class PiPruefung(HeimnetzEntitaet, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    BRAUCHT_BOX = False

    def __init__(self, abruf: Abruf, schluessel: str, feld: str) -> None:
        super().__init__(abruf, schluessel)
        self._feld = feld

    @property
    def is_on(self) -> bool:
        return bool(getattr(self.coordinator.data.pi, self._feld))
