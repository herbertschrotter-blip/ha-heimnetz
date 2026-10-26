"""Lesen aus der Langzeit-Statistik von Home Assistant (Recorder): Zähler von FRITZ!Box Tools, Mobilfunk-Empfang. Ohne Recorder (oder ohne Werte) kommen leere Listen – die Seite zeigt dann „keine Daten“.

Entitäten werden über das Register gefunden (Plattform und unique_id), nicht über Namen.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any, Literal

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, FRITZ

type Reihe = list[tuple[float, float | None]]
type Periode = Literal["5minute", "hour", "day"]


def fritz_zaehler(hass: HomeAssistant, fritz_eintrag: str) -> dict[str, str]:
    """Entitäten „GB empfangen/gesendet“ der FRITZ!Box Tools-Einrichtung → {"down": …, "up": …}."""
    out = {}
    for e in er.async_entries_for_config_entry(er.async_get(hass), fritz_eintrag):
        if e.platform != FRITZ or e.domain != "sensor":
            continue
        if e.unique_id.endswith("-gb_received"):
            out["down"] = e.entity_id
        elif e.unique_id.endswith("-gb_sent"):
            out["up"] = e.entity_id
    return out


def eigene(hass: HomeAssistant, entry_id: str, schluessel: str) -> str | None:
    return er.async_get(hass).async_get_entity_id("sensor", DOMAIN, f"{entry_id}_{schluessel}")


async def statistik(
    hass: HomeAssistant,
    ids: Iterable[str | None],
    start: datetime,
    ende: datetime,
    periode: Periode,
    art: Literal["mean", "change"],
) -> dict[str, Reihe]:
    """{statistic_id: [(start in s, Wert), …]} – leer, wenn der Recorder fehlt oder die Abfrage scheitert."""
    gesucht = {i for i in ids if i}
    if not gesucht or "recorder" not in hass.config.components:
        return {}
    from homeassistant.components.recorder import get_instance  # noqa: PLC0415 – nur mit Recorder
    from homeassistant.components.recorder.statistics import statistics_during_period  # noqa: PLC0415

    zeilen: dict[str, list[Any]] = await get_instance(hass).async_add_executor_job(
        statistics_during_period, hass, start, ende, gesucht, periode, None, {art}
    )
    return {sid: [(float(z["start"]), z.get(art)) for z in reihe] for sid, reihe in zeilen.items()}
