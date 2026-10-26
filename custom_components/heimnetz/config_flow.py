"""Einrichtung: FRITZ!Box aus FRITZ!Box Tools wählen, Verbindung vor dem Anlegen prüfen.

Der Zugang wird nicht eingegeben und nicht gespeichert; gespeichert wird nur, welcher Eintrag gemeint ist.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from . import uebernahme, zugang_aus_fritz
from .box import AnmeldungAbgelehnt, Box, NichtErreichbar
from .const import CONF_ALT_EINTRAG, CONF_FRITZ_EINTRAG, CONF_OPENCELLID, DOMAIN, FRITZ
from .logik import uebernahme as ue


class EinrichtungsDialog(ConfigFlow, domain=DOMAIN):
    """Eine Einrichtung je FRITZ!Box."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return Optionen()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if uebernahme.alte_aktiv(self.hass):
            return self.async_abort(reason="alt_aktiv")  # WU-0006: nie beide zugleich an der Box
        boxen = {e.entry_id: e.title for e in self.hass.config_entries.async_entries(FRITZ)}
        if not boxen:
            return self.async_abort(reason="keine_fritzbox")
        fehler: dict[str, str] = {}
        if user_input is not None:
            eintrag = user_input[CONF_FRITZ_EINTRAG]
            await self.async_set_unique_id(eintrag)
            self._abort_if_unique_id_configured()
            zugang = zugang_aus_fritz(self.hass, eintrag)
            try:
                if zugang is None:
                    raise NichtErreichbar
                await self.hass.async_add_executor_job(Box(zugang).pruefen)
            except AnmeldungAbgelehnt:
                fehler["base"] = "invalid_auth"
            except NichtErreichbar:
                fehler["base"] = "cannot_connect"
            else:
                return self._anlegen(eintrag)
        schema = vol.Schema(
            {vol.Required(CONF_FRITZ_EINTRAG, default=next(iter(boxen))): vol.In(boxen)}
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=fehler)

    def _anlegen(self, eintrag: str) -> ConfigFlowResult:
        """WU-0006: gibt es eine (deaktivierte) Einrichtung der alten Integration, kommen ihre Optionen mit, und die
        Einrichtung merkt sich, von wem sie beim ersten Laden die Daten übernimmt."""
        daten: dict[str, Any] = {CONF_FRITZ_EINTRAG: eintrag}
        optionen: dict[str, Any] = {}
        if (alt := uebernahme.alte_einrichtung(self.hass)) is not None:
            daten[CONF_ALT_EINTRAG] = alt.entry_id
            optionen = ue.optionen_uebernehmen(alt.options, (CONF_OPENCELLID,))
        return self.async_create_entry(title="Heimnetz", data=daten, options=optionen)


class Optionen(OptionsFlow):
    """Schlüssel für OpenCellID (Standort des Masts auf der Seite); leer = ohne Karte zum Mast."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            wert = (user_input.get(CONF_OPENCELLID) or "").strip()
            return self.async_create_entry(data={CONF_OPENCELLID: wert} if wert else {})
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_OPENCELLID,
                    description={"suggested_value": self.config_entry.options.get(CONF_OPENCELLID)},
                ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
