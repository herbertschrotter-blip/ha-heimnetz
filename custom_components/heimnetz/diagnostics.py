"""Diagnose-Download: Einstellungen, Laufzeit und grober Stand – alles Vertrauliche geschwärzt (WU-0006).

Die Datei soll sich gefahrlos an ein öffentliches Issue hängen lassen. Darum gehen nur Zahlen und grobe Angaben mit
(Box-Modell, FRITZ!OS, Netztechnik, Ookla ja/nein, Messplan), und `logik.diagnose.schwaerzen` ersetzt zum Schluss
alles, was nicht öffentlich sein soll – auch in Fehlermeldungen.
"""

from __future__ import annotations

from typing import Any

from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from . import EintragMitLaufzeit
from .const import DOMAIN, sprache
from .logik import diagnose as dg
from .logik import github as gh
from .speedtest import ookla_einstellung


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: EintragMitLaufzeit
) -> dict[str, Any]:
    """Was beim Fehlersuchen hilft, ohne Zugangsdaten und ohne Persönliches; die Datenbank wird im Executor gezählt."""
    lz = entry.runtime_data
    abruf = lz.abruf
    db = lz.datenbank
    datenbank = await hass.async_add_executor_job(lambda: {"zeilen": db.anzahl()})
    stand = abruf.data
    info = abruf.box_info
    # Gerätenamen – kommen sie in einem Text vor, werden sie geschwärzt (Box und Geräte-Tracker in HA)
    namen = [g.name for g in stand.geraete.values()] if stand else []
    namen += [s.name for s in hass.states.async_all("device_tracker")]
    namen += gh.zell_kennungen(stand.mobil if stand else None)  # Zellkennungen auch in Texten
    roh = {
        "version": {
            "heimnetz": str((await async_get_integration(hass, DOMAIN)).version or ""),
            "home_assistant": HA_VERSION,
            "sprache": sprache(hass),
        },
        "eintrag": dict(entry.data),
        "optionen": dict(entry.options),
        "laufzeit": lz.diagnose(),
        "box": {
            "modell": info.modell if info else None,
            "firmware": info.firmware if info else None,
            "netztechnik": stand.mobil.technik if stand and stand.mobil else None,
        },
        "speedtest": {
            "ookla": ookla_einstellung(hass) is not None,
            "messplan": lz.einstellungen.plan.als_dict(),
        },
        "datenbank": datenbank,
    }
    ergebnis: dict[str, Any] = dg.schwaerzen(roh, namen)
    return ergebnis
