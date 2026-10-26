"""Einrichtung: FRITZ!Box aus FRITZ!Box Tools wählen, Verbindung prüfen, jede Box nur einmal."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.heimnetz.box import AnmeldungAbgelehnt, NichtErreichbar
from custom_components.heimnetz.const import CONF_FRITZ_EINTRAG, DOMAIN

PRUEFEN = f"custom_components.{DOMAIN}.box.Box.pruefen"


async def _dialog(hass: HomeAssistant, eintrag: str):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_FRITZ_EINTRAG: eintrag}
    )


async def test_ohne_fritzbox_tools(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "keine_fritzbox"


async def test_eintrag_wird_angelegt_ohne_kennwort(hass: HomeAssistant, fritz, box, pi) -> None:
    with patch(PRUEFEN):
        result = await _dialog(hass, fritz.entry_id)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_FRITZ_EINTRAG: fritz.entry_id}
    assert "geheim" not in str(result)


async def test_nur_eine_einrichtung(hass: HomeAssistant, fritz, box, pi) -> None:
    with patch(PRUEFEN):
        await _dialog(hass, fritz.entry_id)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "single_instance_allowed"


@pytest.mark.parametrize(
    ("fehler", "grund"), [(NichtErreichbar, "cannot_connect"), (AnmeldungAbgelehnt, "invalid_auth")]
)
async def test_fehler(hass: HomeAssistant, fritz, fehler, grund) -> None:
    with patch(PRUEFEN, side_effect=fehler):
        result = await _dialog(hass, fritz.entry_id)
    assert result["type"] is FlowResultType.FORM and result["errors"] == {"base": grund}


async def test_optionen_schluessel_opencellid(hass: HomeAssistant, eintrag, box, pi) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    result = await hass.config_entries.options.async_init(eintrag.entry_id)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"opencellid_schluessel": "  abc  "}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert eintrag.options == {"opencellid_schluessel": "abc"}
    result = await hass.config_entries.options.async_init(eintrag.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert eintrag.options == {}  # leer = ohne Karte zum Mast
