"""Momentaufnahme zur Speedtest-Messung (WU-0005): beim Messen einsammeln, Sensor „Letzte Messung“, Nachtragen."""

from datetime import timedelta
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.heimnetz.box import BoxInfo
from custom_components.heimnetz.logik.ereignis import Ereignis
from custom_components.heimnetz.logik.messung import Messung
from custom_components.heimnetz.speedtest import OOKLA, WARTEN_S
from custom_components.heimnetz.speicher import Journalzeile

from .conftest import box_daten

ZUSATZ = {
    "jitter": "3.1",
    "isp": "Drei",
    "result_url": "https://example.invalid/r/1",
    "bufferbloat_grade": "B",
}


def _ookla(hass: HomeAssistant) -> dict[str, str]:
    ookla = MockConfigEntry(domain=OOKLA)
    ookla.add_to_hass(hass)
    reg = er.async_get(hass)
    return {
        k: reg.async_get_or_create(
            "sensor", OOKLA, f"{ookla.entry_id}_{k}", config_entry=ookla
        ).entity_id
        for k in ("last_test", "download", "upload", "ping", "server", *ZUSATZ)
    }


def _umgebung(hass: HomeAssistant, wetter: str = "rainy") -> str:
    reg = er.async_get(hass)
    wid = reg.async_get_or_create("weather", "met", "home").entity_id
    hass.states.async_set(wid, wetter, {"temperature": 11.5, "humidity": 80, "cloud_coverage": 90})
    kid = reg.async_get_or_create("calendar", "holiday", "feiertage").entity_id
    hass.states.async_set(kid, "off")
    return wid


async def test_momentaufnahme_beim_messen_und_sensor(hass: HomeAssistant, eintrag, box, pi) -> None:
    box.return_value = box_daten(
        info=BoxInfo("FRITZ!Box 6860 5G", "268.08.03", 3600, dt_util.utcnow().timestamp())
    )
    ids = _ookla(hass)
    _umgebung(hass)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    jetzt = dt_util.utcnow()
    for k, v in ZUSATZ.items():
        hass.states.async_set(ids[k], v)
    hass.states.async_set(ids["download"], "120", {"unit_of_measurement": "Mbit/s"})
    hass.states.async_set(ids["upload"], "30", {"unit_of_measurement": "Mbit/s"})
    hass.states.async_set(ids["ping"], "21")
    hass.states.async_set(ids["server"], "Wien – A1")
    hass.states.async_set(ids["last_test"], jetzt.isoformat())
    with patch(
        "custom_components.heimnetz.ansichten.mast_zur_ankerzelle", return_value=(2100, "Nordost")
    ):
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=WARTEN_S + 1))
        await hass.async_block_till_done()

    db = eintrag.runtime_data.datenbank
    k = (await hass.async_add_executor_job(db.messungen_lesen))[-1].kontext
    assert k["quelle"] == "messung" and k["ausloeser"] == "ookla"
    assert (k["netz"], k["zelle"], k["rsrp"], k["nr_aktiv"]) == ("5G-NSA", "abcde-0b", -100, True)
    assert (k["box_modell"], k["box_firmware"]) == ("FRITZ!Box 6860 5G", "268.08.03")
    assert k["box_laufzeit_s"] >= 3600 and k["baender"] == "LTE 1, 3 · 5G n78"
    assert (k["jitter"], k["anbieter"], k["bufferbloat"]) == (3.1, "Drei", "B")
    assert (k["wetter"], k["temperatur"], k["feuchte"]) == ("rainy", 11.5, 80.0)
    assert k["tagesart"] in ("werktag", "wochenende") and k["online"] >= 1

    sensor = next(
        e.entity_id
        for e in er.async_get(hass).entities.values()
        if e.unique_id == f"{eintrag.entry_id}_letzte_messung"
    )
    s = hass.states.get(sensor)
    assert s is not None and s.state != "unknown"
    assert s.attributes["download"] == 120.0 and s.attributes["netz"] == "5G-NSA"
    assert s.attributes["anbieter"] == "Drei"
    # Mast gespeichert (Seite), aber nicht als Attribut: daraus ließe sich die Wohnung bestimmen
    assert (k["mast_m"], k["mast_richtung"]) == (2100, "Nordost")
    assert "mast_m" not in s.attributes and "mast_richtung" not in s.attributes


async def test_alte_messung_bekommt_keine_momentaufnahme_von_jetzt(
    hass: HomeAssistant, eintrag, box, pi
) -> None:
    ids = _ookla(hass)
    hass.states.async_set(ids["download"], "80", {"unit_of_measurement": "Mbit/s"})
    hass.states.async_set(ids["last_test"], (dt_util.utcnow() - timedelta(days=1)).isoformat())
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    db = eintrag.runtime_data.datenbank
    m = (await hass.async_add_executor_job(db.messungen_lesen))[-1]
    assert m.kontext.get("quelle") != "messung"  # leer oder nachgetragen, nie der Stand von jetzt


async def test_nachtragen_aus_verlauf_und_journal(hass: HomeAssistant, eintrag, box, pi) -> None:
    """Verlauf aus dem Recorder (hier nachgebildet) und Zellwechsel aus dem Journal; nur Messungen ohne Momentaufnahme."""
    from pathlib import Path

    from custom_components.heimnetz.speicher import Datenbank

    wid = _umgebung(hass)
    jetzt = dt_util.utcnow().timestamp()
    t_alt, t_mit = jetzt - 2 * 86_400, jetzt - 86_400
    db = Datenbank(Path(hass.config.path("heimnetz/heimnetz.db")))
    await hass.async_add_executor_job(db.oeffnen)
    await hass.async_add_executor_job(
        db.messungen_schreiben,
        [
            Messung(t_alt, 90, 30, 20, "Wien", None, None),
            Messung(t_mit, 90, 30, 20, "Wien", None, None, {"quelle": "messung", "netz": "LTE"}),
        ],
    )
    text = "Mobilfunk: Funkzelle gewechselt x-01/1 → aaaaa-64/2 (Empfang RSRP -90 dBm)"
    await hass.async_add_executor_job(
        db.journal_schreiben, [Journalzeile(t_alt - 600, Ereignis("mobil_zelle", "info", text))]
    )
    await hass.async_add_executor_job(db.schliessen)

    abfragen = []

    def verlauf(_hass, ids, kalender, zeiten):
        abfragen.append((dict(ids), list(kalender), list(zeiten)))
        return {
            z: ({"wetter": [(z - 3600, "rainy")], "temperatur": [(z - 3600, 11.5)]}, False)
            for z in zeiten
        }

    recorder = type(
        "R", (), {"async_add_executor_job": staticmethod(hass.async_add_executor_job)}
    )()
    with (
        patch("homeassistant.components.recorder.get_instance", return_value=recorder),
        patch("custom_components.heimnetz.kontext._verlaeufe_je_messung", side_effect=verlauf),
    ):
        assert await hass.config_entries.async_setup(eintrag.entry_id)
        # der Nachtrag läuft im Hintergrund
        await hass.async_block_till_done(wait_background_tasks=True)
    ids, kalender, zeiten = abfragen[0]
    kid = er.async_get(hass).async_get_entity_id("calendar", "holiday", "feiertage")
    assert ids["wetter"] == wid and kalender == [kid]
    assert zeiten == [t_alt]  # nur die Messung ohne Momentaufnahme
    messungen = {
        m.t: m.kontext
        for m in await hass.async_add_executor_job(eintrag.runtime_data.datenbank.messungen_lesen)
    }
    k = messungen[t_alt]
    assert k["quelle"] == "nachgetragen" and (k["wetter"], k["temperatur"]) == ("rainy", 11.5)
    assert (k["zelle"], k["anlage"]) == ("aaaaa-64", "aaaaa")
    assert messungen[t_mit] == {"quelle": "messung", "netz": "LTE"}  # vorhandene bleibt
    # die letzte Messung hatte schon eine Momentaufnahme – der Sensor zeigt sie
    s = next(
        e.entity_id
        for e in er.async_get(hass).entities.values()
        if e.unique_id == f"{eintrag.entry_id}_letzte_messung"
    )
    assert hass.states.get(s).attributes["netz"] == "LTE"


async def test_sensor_frischt_nach_dem_nachtrag_auf(hass: HomeAssistant, eintrag, box, pi) -> None:
    """Die neueste Messung bekommt ihre Momentaufnahme erst durch den Nachtrag: der Sensor zeigt sie danach."""
    from pathlib import Path

    from custom_components.heimnetz.speicher import Datenbank

    _umgebung(hass)
    t = dt_util.utcnow().timestamp() - 86_400
    db = Datenbank(Path(hass.config.path("heimnetz/heimnetz.db")))
    await hass.async_add_executor_job(db.oeffnen)
    await hass.async_add_executor_job(
        db.messungen_schreiben, [Messung(t, 90, 30, 20, "Wien", None, None)]
    )
    await hass.async_add_executor_job(db.schliessen)
    recorder = type(
        "R", (), {"async_add_executor_job": staticmethod(hass.async_add_executor_job)}
    )()
    with (
        patch("homeassistant.components.recorder.get_instance", return_value=recorder),
        patch(
            "custom_components.heimnetz.kontext._verlaeufe_je_messung",
            side_effect=lambda _h, _i, _k, zeiten: {
                z: ({"wetter": [(z - 60, "rainy")]}, False) for z in zeiten
            },
        ),
    ):
        assert await hass.config_entries.async_setup(eintrag.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        await hass.async_block_till_done()
    s = next(
        e.entity_id
        for e in er.async_get(hass).entities.values()
        if e.unique_id == f"{eintrag.entry_id}_letzte_messung"
    )
    assert hass.states.get(s).attributes["quelle"] == "nachgetragen"
    assert hass.states.get(s).attributes["wetter"] == "rainy"
