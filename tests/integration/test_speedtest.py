"""Ookla-Messungen ins Protokoll: Sensoren über das Register finden, neue Messung mit Grundlast eintragen."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.heimnetz.logik.verkehr import Zaehlerstand
from custom_components.heimnetz.speedtest import OOKLA, WARTEN_S


def _ookla(hass: HomeAssistant) -> dict[str, str]:
    ookla = MockConfigEntry(domain=OOKLA)
    ookla.add_to_hass(hass)
    reg = er.async_get(hass)
    return {
        k: reg.async_get_or_create(
            "sensor", OOKLA, f"{ookla.entry_id}_{k}", config_entry=ookla
        ).entity_id
        for k in ("last_test", "download", "upload", "ping", "server")
    }


def _messen(hass, ids, zeit, down="86.47", einheit="Mbit/s"):
    hass.states.async_set(ids["download"], down, {"unit_of_measurement": einheit})
    hass.states.async_set(ids["upload"], "20.41", {"unit_of_measurement": "Mbit/s"})
    hass.states.async_set(ids["ping"], "21")
    hass.states.async_set(ids["server"], "Wien – A1")
    hass.states.async_set(ids["last_test"], zeit.isoformat())


async def test_neue_messung_mit_grundlast(hass: HomeAssistant, eintrag, box, pi) -> None:
    ids = _ookla(hass)
    jetzt = dt_util.utcnow()
    _messen(hass, ids, jetzt - timedelta(days=1))  # Messung von vor dem Start wird nachgetragen
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    abruf = eintrag.runtime_data.abruf
    db = eintrag.runtime_data.datenbank
    assert abruf.speedtest.sensoren is not None
    await hass.async_block_till_done()
    assert len(await hass.async_add_executor_job(db.messungen_lesen)) == 1

    t = jetzt.timestamp()
    abruf.gedaechtnis.ring = [
        Zaehlerstand(t - 480 + 60 * i, int(i * 37.5e6), int(i * 3.75e6)) for i in range(9)
    ]
    _messen(hass, ids, jetzt, down="900", einheit="kbit/s")
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=WARTEN_S + 1))
    await hass.async_block_till_done()
    messungen = await hass.async_add_executor_job(db.messungen_lesen)
    neu = messungen[-1]
    assert len(messungen) == 2
    assert (neu.down, neu.up, neu.ping, neu.server) == (
        0.9,
        20.41,
        21.0,
        "Wien – A1",
    )  # kbit/s umgerechnet
    assert neu.last_down == 5.0 and neu.last_up == 0.5

    hass.states.async_set(
        ids["last_test"], jetzt.isoformat(), {"x": 1}
    )  # gleiche Zeit: nichts Neues
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=2 * WARTEN_S + 2))
    await hass.async_block_till_done()
    assert len(await hass.async_add_executor_job(db.messungen_lesen)) == 2


async def test_ohne_ookla(hass: HomeAssistant, eintrag, box, pi) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    assert eintrag.runtime_data.abruf.speedtest.sensoren is None


async def test_fehlgeschlagene_messung_wird_nachgeholt(
    hass: HomeAssistant, eintrag, box, pi
) -> None:
    import sqlite3
    from unittest.mock import patch

    ids = _ookla(hass)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    db = eintrag.runtime_data.datenbank
    jetzt = dt_util.utcnow()
    with patch.object(
        type(db), "messungen_schreiben", side_effect=sqlite3.OperationalError("gesperrt")
    ):
        _messen(hass, ids, jetzt)
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=WARTEN_S + 1))
        await hass.async_block_till_done()
    assert await hass.async_add_executor_job(db.messungen_lesen) == []
    await eintrag.runtime_data.abruf.async_refresh()  # nächster Abruf holt nach
    await hass.async_block_till_done()
    assert len(await hass.async_add_executor_job(db.messungen_lesen)) == 1


async def test_viele_aenderungen_ein_timer(hass: HomeAssistant, eintrag, box, pi) -> None:
    ids = _ookla(hass)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    sp = eintrag.runtime_data.abruf.speedtest
    jetzt = dt_util.utcnow()
    for i in range(5):
        _messen(hass, ids, jetzt + timedelta(seconds=i))
    assert sp._timer is not None
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=WARTEN_S + 1))
    await hass.async_block_till_done()
    assert sp._timer is None
    assert (
        len(await hass.async_add_executor_job(eintrag.runtime_data.datenbank.messungen_lesen)) == 1
    )


async def test_entladen_wartet_auf_schreiben(hass: HomeAssistant, eintrag, box, pi) -> None:
    ids = _ookla(hass)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    _messen(hass, ids, dt_util.utcnow())
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=WARTEN_S + 1))
    assert await hass.config_entries.async_unload(
        eintrag.entry_id
    )  # kein „Datenbank nicht geöffnet“
    await hass.async_block_till_done()
