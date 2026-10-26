"""Sensoren: Gesamtstand, offene Befunde, Geräte online, Mobilfunk-Empfang, letzte Speedtest-Messung mit
Momentaufnahme (WU-0005; die Werte als Attribute, damit InfluxDB & Co. sie mitschreiben).

Was FRITZ!Box Tools schon liefert (Verbindung, Durchsatz, Datenmenge, Betriebszeit), gibt es hier nicht noch einmal.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import EintragMitLaufzeit
from .coordinator import Abruf
from .entity import HeimnetzEntitaet
from .logik.befunde import GESAMTSTAENDE
from .logik.mobil import Mobilfunk, Zelle
from .logik.sammeln import Stand


@dataclass(frozen=True, kw_only=True)
class Beschreibung(SensorEntityDescription):
    wert: Callable[[Stand], str | int | None]
    braucht_box: bool = True


def _zelle(welche: str, groesse: str) -> Callable[[Stand], int | None]:
    def wert(s: Stand) -> int | None:
        z: Zelle | None = getattr(s.mobil, welche) if s.mobil else None
        return getattr(z, groesse) if z else None  # Box antwortet, Wert fehlt → unbekannt

    return wert


ALLGEMEIN = (
    Beschreibung(
        key="gesamtstand",
        device_class=SensorDeviceClass.ENUM,
        options=list(GESAMTSTAENDE),
        wert=lambda s: s.gesamt,
        braucht_box=False,
    ),
    Beschreibung(
        key="befunde",
        state_class=SensorStateClass.MEASUREMENT,
        wert=lambda s: len(s.befunde),
        braucht_box=False,
    ),
    Beschreibung(
        key="geraete_online", state_class=SensorStateClass.MEASUREMENT, wert=lambda s: s.online
    ),
)
MOBILFUNK = (
    Beschreibung(key="mobil_technik", wert=lambda s: s.mobil.technik or None if s.mobil else None),
    Beschreibung(
        key="rsrp_anker",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        wert=_zelle("haupt", "rsrp"),
    ),
    Beschreibung(
        key="rsrq_anker",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        wert=_zelle("haupt", "rsrq"),
    ),
    Beschreibung(
        key="rsrp_5g",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        wert=_zelle("nr", "rsrp"),
    ),
    Beschreibung(
        key="rsrq_5g",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        wert=_zelle("nr", "rsrq"),
    ),
    # WU-0002: was die Box sonst noch meldet – als Entitäten, damit das Langzeitarchiv (Scribe) es mitschreibt
    Beschreibung(
        key="mobil_zelle",
        wert=lambda s: s.mobil.haupt.zelle or None if s.mobil and s.mobil.haupt else None,
    ),
    Beschreibung(
        key="mobil_entfernung",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        wert=_zelle("haupt", "entfernung_m"),
    ),
    Beschreibung(
        key="mobil_nachbarzellen",
        state_class=SensorStateClass.MEASUREMENT,
        wert=lambda s: (
            sum(1 for z in s.mobil.zellen if z is not s.mobil.haupt and z is not s.mobil.nr)
            if s.mobil and s.mobil.zellen
            else None
        ),
    ),
    Beschreibung(key="pci_5g", wert=_zelle("nr", "pci")),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EintragMitLaufzeit,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    abruf = entry.runtime_data.abruf
    async_add_entities(HeimnetzSensor(abruf, b) for b in ALLGEMEIN)
    async_add_entities([LetzteMessung(abruf)])

    # Empfangssensoren erst, wenn die Box ein Mobilfunk-Modem gemeldet hat – war sie beim Start nicht erreichbar,
    # kommen sie mit dem ersten gelungenen Abruf dazu; eine Box ohne Modem bekommt keine.
    def mobilfunk_pruefen() -> bool:
        if abruf.gedaechtnis.mobil_dienst is None:
            return False
        if abruf.gedaechtnis.mobil_dienst:
            async_add_entities(HeimnetzSensor(abruf, b) for b in MOBILFUNK)
        return True

    if not mobilfunk_pruefen():
        abmelden: Callable[[], None] | None = None

        def nach_abruf() -> None:
            nonlocal abmelden
            if abmelden is not None and mobilfunk_pruefen():
                abmelden()
                abmelden = None

        abmelden = abruf.async_add_listener(nach_abruf)
        entry.async_on_unload(lambda: abmelden() if abmelden else None)


class HeimnetzSensor(HeimnetzEntitaet, SensorEntity):
    entity_description: Beschreibung

    def __init__(self, abruf: Abruf, beschreibung: Beschreibung) -> None:
        super().__init__(abruf, beschreibung.key)
        self.entity_description = beschreibung
        self.BRAUCHT_BOX = beschreibung.braucht_box

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        mobil: Mobilfunk | None = self.coordinator.data.mobil
        return mobil is not None or self.entity_description not in MOBILFUNK

    @property
    def native_value(self) -> str | int | None:
        return self.entity_description.wert(self.coordinator.data)


# Aus Mast-Entfernung und -Richtung ließe sich mit dem öffentlichen Standort des Masts die Wohnung bestimmen – nicht in
# die Attribute (die gehen über InfluxDB & Co. womöglich nach außen); auf der Seite bleiben sie.
NICHT_ALS_ATTRIBUT = ("mast_m", "mast_richtung")


class LetzteMessung(HeimnetzEntitaet, SensorEntity):
    """Zeitpunkt der letzten Speedtest-Messung; Messwerte und Momentaufnahme als Attribute (WU-0005)."""

    BRAUCHT_BOX = False
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, abruf: Abruf) -> None:
        super().__init__(abruf, "letzte_messung")

    @property
    def native_value(self) -> datetime | None:
        m = self.coordinator.letzte
        return dt_util.utc_from_timestamp(m.t) if m else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        m = self.coordinator.letzte
        if m is None:
            return None
        return {
            # Momentaufnahme zuerst: die echten Messwerte danach gewinnen bei gleichem Namen
            **{k: v for k, v in m.kontext.items() if k not in NICHT_ALS_ATTRIBUT},
            "download": m.down,
            "upload": m.up,
            "ping": m.ping,
            "server": m.server or None,
            "grundlast_down": m.last_down,
            "grundlast_up": m.last_up,
        }
