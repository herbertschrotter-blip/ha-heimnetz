"""Statistik-Abfrage gegen einen echten Recorder (die Schnittstelle ändert sich zwischen HA-Fassungen)."""

from datetime import timedelta

import pytest
from homeassistant.components.recorder.models import StatisticMeanType
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.components.recorder.common import (
    async_wait_recording_done,
)

from custom_components.heimnetz import abfragen as ab


# Der Recorder muss vor Home Assistant aufgesetzt werden; die automatischen Fixtures der übrigen Tests holen hass
# früher – hier braucht es sie nicht.
@pytest.fixture(autouse=True)
def eigene_integration():
    return None


@pytest.fixture(autouse=True)
def eigener_ordner():
    return None


@pytest.fixture(autouse=True)
def deutsch():
    return None


async def test_statistik_mittel(recorder_mock, hass: HomeAssistant) -> None:
    start = dt_util.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(hours=3)
    async_import_statistics(
        hass,
        {
            "source": "recorder",
            "statistic_id": "sensor.beispiel",
            "unit_of_measurement": "Mbit/s",
            "has_sum": False,
            "mean_type": StatisticMeanType.ARITHMETIC,
            "name": None,
            "unit_class": None,
        },
        [
            {"start": start, "mean": 100.0, "min": 90.0, "max": 110.0},
            {"start": start + timedelta(hours=1), "mean": 80.0, "min": 70.0, "max": 90.0},
        ],
    )
    await async_wait_recording_done(hass)
    reihe = await ab.statistik(
        hass, ["sensor.beispiel", None], start, dt_util.utcnow(), "hour", "mean"
    )
    assert reihe["sensor.beispiel"] == [
        (start.timestamp(), 100.0),
        (start.timestamp() + 3600, 80.0),
    ]


async def test_ohne_recorder_leer(hass: HomeAssistant) -> None:
    assert (
        await ab.statistik(hass, ["sensor.x"], dt_util.utcnow(), dt_util.utcnow(), "hour", "mean")
        == {}
    )
