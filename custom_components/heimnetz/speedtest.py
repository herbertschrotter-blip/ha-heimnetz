"""Speedtest-Protokoll: liest die Sensoren der Ookla-Integration und trägt jede neue Messung mit Grundlast ein.

Gemessen wird nur von Ookla (eigene Messungen macht diese Integration nicht). Die Sensoren werden über das
Entitätsregister gefunden (Plattform `ookla_speedtest`, unique_id `<Eintrag>_<schlüssel>`), nicht über Namen.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, UnitOfDataRate
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import DataRateConverter

from .logik import messung as ms
from .logik import serie as sr
from .logik.verkehr import Zaehlerstand

LOGGER = logging.getLogger(__package__)
OOKLA = "ookla_speedtest"
SCHLUESSEL = ("last_test", "download", "upload", "ping", "server")
WARTEN_S = (
    5  # Ookla schreibt seine Sensoren nacheinander – kurz warten, bis alle den neuen Wert haben
)


@dataclass(frozen=True)
class OoklaSensoren:
    eintrag: str  # Config Entry der Ookla-Integration, zu dem die Sensoren gehören
    last_test: str
    download: str | None
    upload: str | None
    ping: str | None
    server: str | None


def finden(hass: HomeAssistant) -> OoklaSensoren | None:
    """Erster Eintrag der Ookla-Integration mit einem Sensor „letzter Test“."""
    alle = alle_finden(hass)
    return alle[0] if alle else None


def alle_finden(hass: HomeAssistant) -> list[OoklaSensoren]:
    """Alle Einträge der Ookla-Integration (je Test ein Server) mit einem Sensor „letzter Test“ (WU-0001)."""
    je_eintrag: dict[str, dict[str, str]] = {}
    for e in er.async_get(hass).entities.values():
        if e.platform != OOKLA or e.domain != "sensor" or not e.config_entry_id:
            continue
        for k in SCHLUESSEL:
            if e.unique_id == f"{e.config_entry_id}_{k}":
                je_eintrag.setdefault(e.config_entry_id, {})[k] = e.entity_id
    return [
        OoklaSensoren(
            eintrag,
            ids["last_test"],
            ids.get("download"),
            ids.get("upload"),
            ids.get("ping"),
            ids.get("server"),
        )
        for eintrag, ids in je_eintrag.items()
        if "last_test" in ids
    ]


@dataclass(frozen=True)
class OoklaEinstellung:
    """Was Ookla selbst eingestellt hat (nur gelesen – die Einstellungen gehören Ookla)."""

    eintrag: str
    manuell: bool
    startzeit: str | None
    takt_min: float | None

    @property
    def misst_selbst(self) -> bool:
        """Ookla plant selbst: „manuell“ aus oder eine Startzeit gesetzt (dann plant Ookla auch bei „manuell“)."""
        return not self.manuell or bool(self.startzeit)


def ookla_einstellung(hass: HomeAssistant, eintrag: str | None = None) -> OoklaEinstellung | None:
    """Geladener Eintrag der Ookla-Integration (bevorzugt `eintrag`, der zu den gelesenen Sensoren gehört)."""
    geladen = [
        e for e in hass.config_entries.async_entries(OOKLA) if e.state is ConfigEntryState.LOADED
    ]
    for e in sorted(geladen, key=lambda x: x.entry_id != eintrag):
        werte = {**e.data, **e.options}
        takt = werte.get("scan_interval")
        start = werte.get("start_time")
        return OoklaEinstellung(
            e.entry_id,
            bool(werte.get("manual", True)),
            str(start) if start else None,
            float(takt) if isinstance(takt, int | float) else None,
        )
    return None


async def async_messen(hass: HomeAssistant, sensoren: OoklaSensoren | None) -> bool:
    """Eine Messung der Ookla-Integration starten (deren Aktion), gezielt für den Eintrag der gelesenen Sensoren –
    sonst würden alle Ookla-Einträge messen. False, wenn es die Aktion oder die Sensoren nicht gibt."""
    if sensoren is None or not hass.services.has_service(OOKLA, "run_speedtest"):
        return False
    await hass.services.async_call(
        OOKLA, "run_speedtest", {"entity_id": sensoren.last_test}, blocking=False
    )
    return True


def _wert(state: State | None) -> str | None:
    return (
        None if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else state.state
    )


def _mbit(state: State | None) -> float | None:
    wert = ms.zahl(_wert(state))
    if wert is None or state is None:
        return None
    einheit = state.attributes.get("unit_of_measurement") or UnitOfDataRate.MEGABITS_PER_SECOND
    try:
        return round(
            DataRateConverter.convert(wert, einheit, UnitOfDataRate.MEGABITS_PER_SECOND), 2
        )
    except Exception:  # noqa: BLE001 – unbekannte Einheit: Wert nicht raten
        return None


def zeitpunkt(state: State | None) -> float | None:
    wert = _wert(state)
    dt: datetime | None = dt_util.parse_datetime(wert) if wert else None
    return dt.timestamp() if dt else None


class Speedtest:
    """Hängt sich an den Sensor „letzter Test“; neue Messungen gehen an `eintragen` (schreibt in die Datenbank).

    Was nicht eingetragen werden konnte (Fehler beim Schreiben, HA neu gestartet), holt `nachholen` beim nächsten
    Abruf nach: maßgeblich ist immer die letzte Messung in der Datenbank.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        ring: Callable[[], list[Zaehlerstand]],
        letzte: Callable[[], float],
        eintragen: Callable[[ms.Messung], None],
    ) -> None:
        self.hass = hass
        self._ring = ring
        self._letzte = letzte  # Zeitpunkt der letzten eingetragenen Messung
        self._eintragen = eintragen
        self.sensoren: OoklaSensoren | None = None
        self._abmelden: Callable[[], None] | None = None
        self._timer: Callable[[], None] | None = None

    @callback
    def verbinden(self) -> None:
        """Ookla suchen (auch später nachinstalliert); eine Messung aus der Zeit davor wird nachgetragen."""
        if self.sensoren is None:
            self.sensoren = finden(self.hass)
            if self.sensoren is None:
                return
            self._abmelden = async_track_state_change_event(
                self.hass, [self.sensoren.last_test], self._geaendert
            )
        self.nachholen()

    @callback
    def nachholen(self) -> None:
        if self._timer is None:  # sonst steht das Lesen nach einer Änderung gerade an
            self._lesen()

    @callback
    def trennen(self) -> None:
        if self._timer is not None:
            self._timer()
            self._timer = None
        if self._abmelden is not None:
            self._abmelden()
            self._abmelden = None
        self.sensoren = None

    @callback
    def _geaendert(self, event: Event[EventStateChangedData]) -> None:
        if self._timer is not None:
            self._timer()
        self._timer = async_call_later(self.hass, WARTEN_S, self._spaeter)

    @callback
    def _spaeter(self, _jetzt: datetime) -> None:
        self._timer = None
        self._lesen()

    @callback
    def _lesen(self) -> None:
        s = self.sensoren
        if s is None:
            return
        t = zeitpunkt(self.hass.states.get(s.last_test))
        if t is None or t <= self._letzte():
            return
        get = self.hass.states.get
        messung = ms.eintragen(
            t,
            _mbit(get(s.download) if s.download else None),
            _mbit(get(s.upload) if s.upload else None),
            _wert(get(s.ping) if s.ping else None),
            _wert(get(s.server) if s.server else None),
            self._ring(),
        )
        LOGGER.debug("Neue Messung %s", messung)
        self._eintragen(messung)


def lauf(hass: HomeAssistant, s: OoklaSensoren) -> sr.Lauf | None:
    """Ergebnis des letzten Tests eines Ookla-Eintrags für eine Serie; None ohne Zeitpunkt."""
    get = hass.states.get
    t = zeitpunkt(get(s.last_test))
    if t is None:
        return None
    return sr.Lauf(
        t,
        _wert(get(s.server)) if s.server else None,
        _mbit(get(s.download)) if s.download else None,
        _mbit(get(s.upload)) if s.upload else None,
        ms.zahl(_wert(get(s.ping))) if s.ping else None,
    )
