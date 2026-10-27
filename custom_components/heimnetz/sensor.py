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
    UnitOfDataRate,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import EintragMitLaufzeit
from .coordinator import Abruf
from .entity import HeimnetzEntitaet
from .logik import leitung as ln
from .logik import zugang as zg
from .logik.befunde import GESAMTSTAENDE
from .logik.mobil import Mobilfunk, Zelle
from .logik.sammeln import Stand


@dataclass(frozen=True, kw_only=True)
class Beschreibung(SensorEntityDescription):
    wert: Callable[[Stand], str | int | float | None]
    braucht_box: bool = True
    da: Callable[[Stand], bool] | None = (
        None  # nur verfügbar, wenn das zutrifft (z. B. DSL-Werte gelesen)
    )


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
# WU-0009 Stufe 2: was nur ein vorgeschaltetes Modem liefert (die Box über TR-064 nicht) – erst, wenn es Werte hatte
_SINR = {
    "native_unit_of_measurement": SIGNAL_STRENGTH_DECIBELS,
    "state_class": SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 1,
}
MODEM = (
    Beschreibung(key="sinr_anker", wert=_zelle("haupt", "sinr"), **_SINR),
    Beschreibung(key="sinr_5g", wert=_zelle("nr", "sinr"), **_SINR),
    Beschreibung(
        key="mobil_band",
        wert=lambda s: (
            " · ".join(dict.fromkeys(z.band for z in s.mobil.zellen if z.band)) or None
            if s.mobil
            else None
        ),
    ),
)


# WU-0009: Werte der Leitung – Entitäten nur, wenn die Box diesen Anschluss hat (kommen mit dem ersten Lesen dazu)
def _dsl(f: Callable[[ln.Dsl], int | float | None]) -> Callable[[Stand], int | float | None]:
    return lambda s: f(s.dsl) if s.dsl else None


def _faser(f: Callable[[ln.Faser], int | float | None]) -> Callable[[Stand], int | float | None]:
    return lambda s: f(s.faser) if s.faser else None


_MBIT = {
    "device_class": SensorDeviceClass.DATA_RATE,
    "native_unit_of_measurement": UnitOfDataRate.MEGABITS_PER_SECOND,
    "state_class": SensorStateClass.MEASUREMENT,
}
_DB = {"native_unit_of_measurement": "dB", "state_class": SensorStateClass.MEASUREMENT}
_DBM = {
    "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
    "native_unit_of_measurement": SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    "state_class": SensorStateClass.MEASUREMENT,
}


def _hat_dsl(s: Stand) -> bool:
    return s.dsl is not None


def _hat_faser(s: Stand) -> bool:
    return s.faser is not None


DSL = (
    Beschreibung(
        key="dsl_sync_down", wert=_dsl(lambda d: ln.mbit(d.sync_down)), da=_hat_dsl, **_MBIT
    ),
    Beschreibung(key="dsl_sync_up", wert=_dsl(lambda d: ln.mbit(d.sync_up)), da=_hat_dsl, **_MBIT),
    Beschreibung(key="dsl_snr_down", wert=_dsl(lambda d: ln.db(d.marge_down)), da=_hat_dsl, **_DB),
    Beschreibung(key="dsl_snr_up", wert=_dsl(lambda d: ln.db(d.marge_up)), da=_hat_dsl, **_DB),
    Beschreibung(
        key="dsl_daempfung_down", wert=_dsl(lambda d: ln.db(d.daempfung_down)), da=_hat_dsl, **_DB
    ),
    Beschreibung(
        key="dsl_daempfung_up", wert=_dsl(lambda d: ln.db(d.daempfung_up)), da=_hat_dsl, **_DB
    ),
    Beschreibung(
        key="dsl_crc_stunde",
        native_unit_of_measurement="1/h",
        state_class=SensorStateClass.MEASUREMENT,
        wert=lambda s: s.dsl_crc_h,
        da=_hat_dsl,
    ),
)
GLASFASER = (
    Beschreibung(key="glasfaser_rx", wert=_faser(lambda f: ln.dbm(f.rx)), da=_hat_faser, **_DBM),
    Beschreibung(key="glasfaser_tx", wert=_faser(lambda f: ln.dbm(f.tx)), da=_hat_faser, **_DBM),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EintragMitLaufzeit,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    abruf = entry.runtime_data.abruf
    async_add_entities(HeimnetzSensor(abruf, b) for b in ALLGEMEIN)
    async_add_entities([LetzteMessung(abruf), Zugangsart(abruf)])

    # WU-0009: DSL- und Glasfaser-Werte erst, wenn die Box sie gemeldet hat (auch später, nach einem Wechsel)
    angelegt: set[str] = set()

    def leitung_pruefen() -> None:
        s = abruf.data
        for name, da, liste in (("dsl", _hat_dsl, DSL), ("glasfaser", _hat_faser, GLASFASER)):
            if name not in angelegt and s is not None and da(s):
                angelegt.add(name)
                async_add_entities(HeimnetzSensor(abruf, b) for b in liste)

    leitung_pruefen()
    entry.async_on_unload(abruf.async_add_listener(leitung_pruefen))

    # Empfangssensoren erst, wenn die Box ein Mobilfunk-Modem gemeldet hat oder ein vorgeschaltetes Modem Funkwerte
    # geliefert hat (WU-0009 Stufe 2) – war die Box beim Start nicht erreichbar, kommen sie mit dem ersten gelungenen
    # Abruf dazu; eine Box ohne Modem und ohne Gerät davor bekommt keine.
    def funk_pruefen() -> None:
        g = abruf.gedaechtnis
        if "mobil" not in angelegt and (g.mobil_dienst or g.modem_mobil):
            angelegt.add("mobil")
            async_add_entities(HeimnetzSensor(abruf, b) for b in MOBILFUNK)
        # je Zusatzwert erst, wenn genau dieser Wert einmal da war
        neu = [b for b in MODEM if b.key in g.modem_werte and b.key not in angelegt]
        if neu:
            angelegt.update(b.key for b in neu)
            async_add_entities(HeimnetzSensor(abruf, b) for b in neu)

    funk_pruefen()
    entry.async_on_unload(abruf.async_add_listener(funk_pruefen))


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
        da = self.entity_description.da
        if da is not None and not da(self.coordinator.data):
            return False
        mobil: Mobilfunk | None = self.coordinator.data.mobil
        return mobil is not None or (
            self.entity_description not in MOBILFUNK and self.entity_description not in MODEM
        )

    @property
    def native_value(self) -> str | int | float | None:
        return self.entity_description.wert(self.coordinator.data)


class Zugangsart(HeimnetzEntitaet, SensorEntity):
    """WU-0009: woher das Internet kommt – erkannt oder in ⚙ › Zugang festgelegt."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(zg.ARTEN)

    def __init__(self, abruf: Abruf) -> None:
        super().__init__(abruf, "zugang")

    @property
    def native_value(self) -> str | None:
        e = self.coordinator.einstellungen
        wahl = e.wert.zugang_wahl if e else "auto"
        return zg.wirksam(self.coordinator.data.zugang_art, wahl) or None


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
