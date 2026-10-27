"""Einrichtung (WU-0007): `heimnetz/einrichtung` liest aus Home Assistant, was eingerichtet ist (nur Admins, nur
lesen), und der Reparatur-Hinweis, wenn der Recorder fehlt."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heimnetz import speedtest
from custom_components.heimnetz.box import BoxInfo
from custom_components.heimnetz.const import (
    CONF_FRITZ_EINTRAG,
    CONF_OPENCELLID,
    DOMAIN,
    FRITZ,
    HA_MINDEST,
    ISSUE_RECORDER_FEHLT,
)
from custom_components.heimnetz.logik import einrichtung as ei

HACS_JSON = Path(__file__).parents[2] / "hacs.json"


async def _frage(hass, hass_ws_client, token=None, **msg):
    client = await (hass_ws_client(hass, token) if token else hass_ws_client(hass))
    await client.send_json_auto_id({"type": "heimnetz/einrichtung", **msg})
    return await client.receive_json()


def _teile(antwort) -> dict[str, dict]:
    return {x["schluessel"]: x for s in antwort["stufen"] for x in s["teile"]}


def _geladen(hass, domain, **kw):
    e = MockConfigEntry(domain=domain, **kw)
    e.add_to_hass(hass)
    e.mock_state(hass, ConfigEntryState.LOADED)
    return e


def test_konstanten_wie_in_der_integration():
    """Die Fachlogik kennt die Domains selbst (ohne HA-Import) – sie müssen zu denen der Integration passen."""
    assert ei.OOKLA == speedtest.OOKLA
    assert ei.FRITZ == FRITZ
    assert ei.HEIMNETZ == DOMAIN
    assert json.loads(HACS_JSON.read_text(encoding="utf-8"))["homeassistant"] == HA_MINDEST


async def test_stand_nach_dem_einrichten(hass, eintrag, box, pi, hass_ws_client):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    eintrag.runtime_data.abruf.box_info = BoxInfo("FRITZ!Box 6860 5G", "8.20", 3600, 0.0)
    _geladen(hass, speedtest.OOKLA)
    met = _geladen(hass, "met", title="Home")
    antwort = await _frage(hass, hass_ws_client)
    met.mock_state(
        hass, ConfigEntryState.NOT_LOADED
    )  # Met.no ist nur nachgestellt – nicht entladen lassen
    assert antwort["success"], antwort
    d = antwort["result"]
    t = _teile(d)
    assert [s["stufe"] for s in d["stufen"]] == ["muss", "soll", "kann"]
    assert (
        t["fritz"]["status"] == "ok" and t["fritz"]["stand"] == "eingerichtet · FRITZ!Box 6860 5G"
    )
    assert t["ookla"]["status"] == "ok" and t["met"]["status"] == "ok"
    assert t["holiday"]["status"] == "fehlt"
    assert t["holiday"]["aktionen"][0]["ziel"] == "/_my_redirect/config_flow_start?domain=holiday"
    # in der Testumgebung laufen weder Recorder noch HACS
    assert t["recorder"]["status"] == "muss" and t["hacs"]["status"] == "muss"
    assert t["ookla"]["status"] == "ok"
    assert t["archiv"]["hinweis"] == "erst HACS installieren"
    assert d["punkt"] == "rot" and d["muss_fehlt"] == 2 and d["soll_fehlt"] == 1
    # keine Gerätenamen, Adressen oder Zugangsdaten
    assert "192.0.2.1" not in str(d) and "geheim" not in str(d) and "FRITZ!Box Test" not in str(d)
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_RECORDER_FEHLT)


async def test_nur_fuer_admins(hass, eintrag, box, pi, hass_ws_client, hass_read_only_access_token):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    antwort = await _frage(hass, hass_ws_client, hass_read_only_access_token)
    assert not antwort["success"] and antwort["error"]["code"] == "unauthorized"


async def test_ohne_geladene_einrichtung(hass, hass_ws_client):
    """Auch ohne Heimnetz-Eintrag antwortet der Befehl (nur lesen) – dann fehlt FRITZ!Box Tools."""
    assert await async_setup_component(hass, DOMAIN, {})
    antwort = await _frage(hass, hass_ws_client)
    assert antwort["success"], antwort
    assert _teile(antwort["result"])["fritz"]["status"] == "muss"


async def test_heruntergeladen_und_hacs(hass, eintrag, box, pi, hass_ws_client):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    _geladen(hass, "hacs")
    eigene = {"ookla_speedtest": object(), "heimnetz": object(), "anderes": object()}
    with patch(
        "custom_components.heimnetz.einrichtung.async_get_custom_components", return_value=eigene
    ):
        t = _teile((await _frage(hass, hass_ws_client))["result"])
    assert t["hacs"]["status"] == "ok"
    assert t["ookla"]["hinweis"] == "heruntergeladen – nach einem Neustart einrichten"
    assert t["ookla"]["aktionen"][0]["ziel"].endswith("domain=ookla_speedtest")
    assert t["archiv"]["aktionen"][0]["ziel"] == (
        "/_my_redirect/hacs_repository?owner=jonathan-gtd&repository=scribe&category=integration"
    )


async def test_opencellid_nur_ja_nein_und_englisch(hass, eintrag, box, pi, hass_ws_client):
    hass.config_entries.async_update_entry(eintrag, options={CONF_OPENCELLID: "pk.geheim123"})
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    antwort = await _frage(hass, hass_ws_client, sprache="en")
    d = antwort["result"]
    t = _teile(d)
    assert t["opencellid"]["status"] == "ok" and t["opencellid"]["stand"] == "entered"
    assert "pk.geheim123" not in json.dumps(d)
    assert t["fritz"]["wofuer"] == "access to the box"


async def test_fritz_eintrag_entfernt(hass, fritz, hass_ws_client):
    """Heimnetz nutzt genau den Eintrag von FRITZ!Box Tools, aus dem es den Zugang holt – ist der weg, fehlt er,
    auch wenn es noch einen anderen gibt."""
    MockConfigEntry(domain=DOMAIN, data={CONF_FRITZ_EINTRAG: "weg"}).add_to_hass(hass)
    assert await async_setup_component(hass, DOMAIN, {})
    t = _teile((await _frage(hass, hass_ws_client))["result"])
    assert t["fritz"]["status"] == "muss"


async def test_recorder_da_kein_hinweis(hass, eintrag, box, pi, hass_ws_client):
    """Recorder geladen (nachgestellt – der echte braucht eine eigene Testumgebung): kein Hinweis, Aufbewahrung."""
    hass.config.components.add("recorder")
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_RECORDER_FEHLT) is None
    with patch(
        "homeassistant.components.recorder.get_instance", return_value=SimpleNamespace(keep_days=10)
    ):
        t = _teile((await _frage(hass, hass_ws_client))["result"])
    assert t["recorder"]["status"] == "ok" and t["recorder"]["stand"] == "aktiv · 10 Tage"
