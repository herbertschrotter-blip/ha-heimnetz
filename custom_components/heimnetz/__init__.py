"""Integration einrichten und entladen."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from homeassistant.config_entries import SIGNAL_CONFIG_ENTRY_CHANGED, ConfigEntry, ConfigEntryChange
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.typing import ConfigType

from . import kontext, uebernahme
from .box import Box
from .const import (
    ALT_DOMAIN,
    CONF_ALT_EINTRAG,
    CONF_FRITZ_EINTRAG,
    CONF_UEBERNOMMEN,
    DATENBANK,
    DOMAIN,
    ISSUE_ALT_AKTIV,
    ISSUE_FRITZ_FEHLT,
)
from .coordinator import Abruf, zugang_aus_fritz
from .einstellungen import Einstellungsdienst
from .logik import sammeln as sm
from .mast import Mastsuche
from .ocid_abzug import OcidAbzug
from .osm_masten import OsmMasten
from .panel import abmelden, async_anmelden
from .speicher import Datenbank, SchemaZuNeu
from .tickets import meldungen
from .tickets import registrieren as tickets_registrieren
from .websocket import registrieren

LOGGER = logging.getLogger(__package__)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATTFORMEN = [Platform.BINARY_SENSOR, Platform.SENSOR]


@dataclass
class Laufzeit:
    """Was die Integration zur Laufzeit braucht (entry.runtime_data)."""

    abruf: Abruf
    datenbank: Datenbank
    einstellungen: Einstellungsdienst
    salz: str  # für die Geräte-Kennungen der Seite
    mastsuche: Mastsuche
    osm: OsmMasten
    ocid: OcidAbzug

    def diagnose(self) -> dict[str, Any]:
        """Zahlen statt Inhalte: keine Gerätenamen, Hardware-Adressen oder Meldungstexte."""
        s = self.abruf.data
        return {
            "letzter_abruf_ok": self.abruf.last_update_success,
            "gesamt": s.gesamt,
            "box_erreichbar": s.box_erreichbar,
            "befunde": [b.key.split(":")[0] for b in s.befunde],
            "geraete": len(s.geraete),
            "online": s.online,
            "mobilfunk": s.mobil is not None,
            "dhcp_test": None
            if s.dhcp is None
            else {"ok": s.dhcp.ok, "server": len(s.dhcp.server)},
            "pi": {"box": s.pi.box, "internet": s.pi.internet, "dns": s.pi.dns},
            "fehler": list(s.fehler),
            "speedtest": self.abruf.speedtest.sensoren is not None,
        }


type EintragMitLaufzeit = ConfigEntry[Laufzeit]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """WebSocket-Befehle der Seite und Tickets (Melden-Knopf, Dienst heimnetz.ticket) einmal je HA-Start anmelden."""
    registrieren(hass)
    tickets_registrieren(hass)
    hass.async_create_task(
        meldungen(hass).async_laden(), f"{DOMAIN}_meldungen_laden"
    )  # lesbare Kopie beim Start
    return True


async def async_setup_entry(hass: HomeAssistant, entry: EintragMitLaufzeit) -> bool:
    if uebernahme.alte_aktiv(hass):
        # WU-0006: nie beide zugleich an der Box und im Speedtest-Protokoll
        ir.async_create_issue(
            hass,
            DOMAIN,
            ISSUE_ALT_AKTIV,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key=ISSUE_ALT_AKTIV,
        )
        raise ConfigEntryError(translation_domain=DOMAIN, translation_key=ISSUE_ALT_AKTIV)
    ir.async_delete_issue(hass, DOMAIN, ISSUE_ALT_AKTIV)
    if not entry.data.get(CONF_UEBERNOMMEN):
        await uebernahme.async_uebernehmen(hass, entry)
    await meldungen(hass).async_nachholen()

    zugang = zugang_aus_fritz(hass, entry.data[CONF_FRITZ_EINTRAG])
    if zugang is None:
        ir.async_create_issue(
            hass,
            DOMAIN,
            ISSUE_FRITZ_FEHLT,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key=ISSUE_FRITZ_FEHLT,
        )
        raise ConfigEntryError(translation_domain=DOMAIN, translation_key=ISSUE_FRITZ_FEHLT)
    ir.async_delete_issue(hass, DOMAIN, ISSUE_FRITZ_FEHLT)

    datenbank = Datenbank(Path(hass.config.path(DATENBANK)))
    try:
        await hass.async_add_executor_job(datenbank.oeffnen)
    except SchemaZuNeu as err:
        raise ConfigEntryError(str(err)) from err
    try:
        gedaechtnis, letzte, salz = await hass.async_add_executor_job(_vorbereiten, datenbank)
        abruf = Abruf(
            hass, entry, Box(zugang), entry.data[CONF_FRITZ_EINTRAG], datenbank, gedaechtnis, letzte
        )
        if letzte:
            abruf.letzte = (await hass.async_add_executor_job(datenbank.messungen_lesen, letzte))[
                -1
            ]
        # WU-0006: Vorgabe-Messplan nur für eine neue Installation, nicht beim Umstieg von der alten Integration
        einstellungen = Einstellungsdienst(
            hass, entry.entry_id, neu=not entry.data.get(CONF_ALT_EINTRAG)
        )
        await einstellungen.async_laden()
        abruf.einstellungen = einstellungen
        entry.runtime_data = Laufzeit(
            abruf=abruf,
            datenbank=datenbank,
            einstellungen=einstellungen,
            salz=salz,
            mastsuche=Mastsuche(hass, entry),
            osm=OsmMasten(hass, entry),
            ocid=OcidAbzug(hass, entry),
        )
        lz = entry.runtime_data
        abruf.kontext_holen = lambda m: kontext.momentaufnahme(hass, lz, m)  # WU-0005
        entry.async_on_unload(abruf.speedtest.trennen)
        await abruf.async_config_entry_first_refresh()
        await async_anmelden(hass)
        entry.async_on_unload(lambda: abmelden(hass))
    except BaseException:
        await hass.async_add_executor_job(datenbank.schliessen)
        raise
    await hass.config_entries.async_forward_entry_setups(entry, PLATTFORMEN)

    @callback
    def _nachtrag_starten(_hass: HomeAssistant) -> None:
        entry.async_create_background_task(hass, _nachtragen(hass, lz), f"{DOMAIN}_nachtrag")

    entry.async_on_unload(async_at_started(hass, _nachtrag_starten))

    @callback
    def _alt_geaendert(_aenderung: ConfigEntryChange, geaendert: ConfigEntry) -> None:
        """WU-0006: wird die alte Integration wieder aktiv, hört Heimnetz sofort auf – neu laden bricht mit Hinweis ab."""
        if geaendert.domain == ALT_DOMAIN and uebernahme.alte_aktiv(hass):
            hass.config_entries.async_schedule_reload(entry.entry_id)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_CONFIG_ENTRY_CHANGED, _alt_geaendert)
    )
    return True


async def _nachtragen(hass: HomeAssistant, lz: Laufzeit) -> None:
    """WU-0005: ältere Messungen ohne Momentaufnahme aus Verlauf und Journal ergänzen – Fehler nur protokollieren."""
    try:
        n = await kontext.nachtragen(hass, lz)
    except Exception:
        LOGGER.exception("Heimnetz: Nachtragen der Momentaufnahmen fehlgeschlagen")
        return
    if n:
        LOGGER.info("Heimnetz: %s ältere Messungen mit Momentaufnahme ergänzt", n)
        # die beim Start geladene letzte Messung kann jetzt ihre Momentaufnahme haben (Sensor „Letzte Messung“)
        abruf = lz.abruf
        if abruf.letzte is not None and not abruf.letzte.kontext:
            neu = await hass.async_add_executor_job(lz.datenbank.messungen_lesen, abruf.letzte.t)
            if neu and neu[-1].t == abruf.letzte.t:
                abruf.letzte = neu[-1]
                abruf.async_update_listeners()


def _vorbereiten(datenbank: Datenbank) -> tuple[sm.Gedaechtnis, float, str]:
    """Blockierend: Gedächtnis, letzte Messung und Salz laden."""
    gedaechtnis = sm.Gedaechtnis()
    try:
        gespeichert = datenbank.gedaechtnis_laden()
        if gespeichert:
            gedaechtnis = sm.gedaechtnis_aus_dict(gespeichert)
    except (ValueError, TypeError, KeyError, AttributeError) as err:
        # unlesbares Gedächtnis: neu anfangen statt bei jedem Start zu scheitern
        LOGGER.warning(
            "Heimnetz: gespeichertes Gedächtnis unlesbar (%s), neu angefangen", type(err).__name__
        )
    return gedaechtnis, datenbank.letzte_messung(), datenbank.salz()


async def async_unload_entry(hass: HomeAssistant, entry: EintragMitLaufzeit) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATTFORMEN)
    if ok:
        laufzeit = entry.runtime_data
        await laufzeit.abruf.async_schliessen()
        await hass.async_add_executor_job(laufzeit.abruf.box.schliessen)
        await hass.async_add_executor_job(laufzeit.datenbank.schliessen)
    return ok


async def async_remove_entry(hass: HomeAssistant, entry: EintragMitLaufzeit) -> None:
    """Einrichtung gelöscht: Einstellungen, gemerkte Masten und OSM-Masten weg. Die Datenbank bleibt (Verlauf), bis Herbert sie selbst löscht."""
    await Einstellungsdienst(hass, entry.entry_id).async_entfernen()
    await Mastsuche(hass, entry).async_entfernen()
    await OsmMasten(hass, entry).async_entfernen()
    await OcidAbzug(hass, entry).async_entfernen()
