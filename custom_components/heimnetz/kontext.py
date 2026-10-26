"""Momentaufnahme zu einer Speedtest-Messung einsammeln und ältere Messungen nachtragen (WU-0005).

Im Moment der Messung: Stand der Box (Mobilfunk, Geräte, Bänder), Modell/Firmware/Laufzeit der Box, Auslöser,
Zusatzwerte der Ookla-Sensoren, Wetter-Entität, Feiertags-Kalender, geschätzter Mast. Nachtragen: aus dem Verlauf von
Home Assistant (Recorder) und dem Journal, einmal je Messung. Nur lesen – nichts davon ändert etwas.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from . import abfragen as ab
from . import ansichten
from .logik import kontext as kx
from .logik.messung import Messung
from .speedtest import OOKLA

if TYPE_CHECKING:
    from . import Laufzeit

LOGGER = logging.getLogger(__package__)
MAST_WARTEN_S = (
    10  # der Mast ist eine Zugabe: länger wartet die Messung nicht auf BeaconDB/OpenCellID
)
BOX_INFO_MAX_S = (
    15 * 60
)  # Laufzeit der Box nur, wenn sie zuletzt höchstens so lange vor der Messung gelesen wurde
STAND_MAX_S = 5 * 60  # „verbunden seit“ nur, wenn der Abruf höchstens so lange vor der Messung war
WETTER_PLATTFORMEN = ("met",)  # bevorzugt die Wetter-Entität des Standorts (Met.no „Home“)
FEIERTAGE = "holiday"

# Eigene Sensoren (Schlüssel) für den Nachtrag → Schlüssel der Momentaufnahme
EIGENE = {
    "mobil_technik": "netz",
    "rsrp_anker": "rsrp",
    "rsrq_anker": "rsrq",
    "rsrp_5g": "nr_rsrp",
    "rsrq_5g": "nr_rsrq",
}
WETTER_ATTR = {"temperatur": "temperature", "feuchte": "humidity", "wolken": "cloud_coverage"}


def _ookla_ids(hass: HomeAssistant, eintrag: str | None) -> dict[str, str]:
    """Schlüssel der Momentaufnahme → Entität der Ookla-Zusatzsensoren desselben Ookla-Eintrags."""
    if not eintrag:
        return {}
    reg = er.async_get(hass)
    out = {}
    for schluessel, k in kx.OOKLA_ZUSATZ.items():
        if eid := reg.async_get_entity_id("sensor", OOKLA, f"{eintrag}_{schluessel}"):
            out[k] = eid
    return out


def _plattform(hass: HomeAssistant, domain: str, plattformen: Sequence[str]) -> list[str]:
    return sorted(
        e.entity_id
        for e in er.async_get(hass).entities.values()
        if e.domain == domain and e.platform in plattformen and not e.disabled
    )


def _wetter_id(hass: HomeAssistant) -> str | None:
    """Wetter-Entität: die von Met.no zuerst (Standort von Home Assistant), sonst die erste vorhandene."""
    bevorzugt = _plattform(hass, "weather", WETTER_PLATTFORMEN)
    if bevorzugt:
        return bevorzugt[0]
    alle = sorted(s.entity_id for s in hass.states.async_all("weather"))
    return alle[0] if alle else None


def _zustand(s: State | None) -> str | None:
    return None if s is None else s.state


def _tag(t: float) -> Any:
    return dt_util.as_local(dt_util.utc_from_timestamp(t)).date()


async def momentaufnahme(hass: HomeAssistant, lz: Laufzeit, messung: Messung) -> dict[str, Any]:
    """Alles, was im Moment der Messung los war. Leer für eine Messung von vor dem Start der Integration (etwa nach
    einem Neustart nachgeholt) – deren Stand kennt nur der Verlauf, sie wird nachgetragen."""
    abruf = lz.abruf
    if messung.t < abruf.gestartet:
        return {}
    stand = abruf.data
    teile: list[Mapping[str, Any]] = []
    if stand is not None:
        mobil = kx.mobilfunk(stand.mobil)
        abstand = messung.t - stand.zeit
        if "verbunden_s" in mobil:
            if -60 <= abstand <= STAND_MAX_S:
                mobil["verbunden_s"] = max(0, round(mobil["verbunden_s"] + abstand))
            else:
                del mobil["verbunden_s"]
        teile.append(mobil)
        teile.append(
            {
                "online": stand.online,
                "online_wlan": len(stand.wlan.geraete) if stand.wlan else None,
                "baender": stand.mobil_baender or None,
            }
        )
    if (i := abruf.box_info) is not None:
        alter = messung.t - i.t
        teile.append(
            {
                "box_modell": i.modell or None,
                "box_firmware": i.firmware or None,
                "box_laufzeit_s": round(i.laufzeit_s + alter)
                if i.laufzeit_s is not None and -60 <= alter <= BOX_INFO_MAX_S
                else None,
            }
        )
    serie = abruf.serie_status
    teile.append(
        {
            "ausloeser": kx.ausloeser(messung.t, abruf.ausgeloest, abruf.ausloese_grund, serie),
            "serie_lauf": serie["lauf"] if serie else None,
            "serie_n": serie["n"] if serie else None,
        }
    )
    sensoren = abruf.speedtest.sensoren
    ids = _ookla_ids(hass, sensoren.eintrag if sensoren else None)
    teile.append(kx.ookla({k: _zustand(hass.states.get(e)) for k, e in ids.items()}))
    if (wid := _wetter_id(hass)) and (w := hass.states.get(wid)):
        teile.append(kx.wetter(w.state, w.attributes))
    feiertag = any(
        _zustand(hass.states.get(c)) == "on" for c in _plattform(hass, "calendar", (FEIERTAGE,))
    )
    teile.append({"tagesart": kx.tagesart(_tag(messung.t), feiertag)})
    try:
        mast = await asyncio.wait_for(ansichten.mast_zur_ankerzelle(hass, lz), MAST_WARTEN_S)
        if mast:
            teile.append({"mast_m": mast[0], "mast_richtung": mast[1]})
    except Exception:  # der Mast ist eine Zugabe – fehlt er (Zeit um, Fehler), gilt der Rest
        LOGGER.debug("Heimnetz: Mast für die Momentaufnahme nicht ermittelt", exc_info=True)
    return kx.momentaufnahme(*teile)


# ── Nachtragen (einmal je Messung ohne Momentaufnahme, höchstens NACHTRAG_TAGE zurück) ──


def _verlaeufe_je_messung(
    hass: HomeAssistant, ids: Mapping[str, str], kalender: Sequence[str], zeiten: Sequence[float]
) -> dict[float, tuple[dict[str, list[tuple[float, Any]]], bool]]:
    """Im Executor des Recorders: je Messung ein kleines Fenster (Stand zum Zeitpunkt der Messung und die Änderungen
    der nächsten Minuten für die Ookla-Werte) – statt des ganzen Verlaufs von Wochen auf einmal."""
    from homeassistant.components.recorder import history  # nur wenn der Recorder läuft

    alle = sorted(set(ids.values()) | set(kalender))
    out: dict[float, tuple[dict[str, list[tuple[float, Any]]], bool]] = {}
    for t in zeiten:
        roh = history.get_significant_states(
            hass,
            dt_util.utc_from_timestamp(t),
            dt_util.utc_from_timestamp(t + kx.OOKLA_NACH_S),
            alle,
            significant_changes_only=False,
            minimal_response=False,
            include_start_time_state=True,
        )
        verlaeufe: dict[str, list[tuple[float, Any]]] = {}
        for schluessel, eid in ids.items():
            attr = WETTER_ATTR.get(schluessel)
            verlaeufe[schluessel] = [
                (s.last_updated.timestamp(), s.attributes.get(attr) if attr else s.state)
                for s in roh.get(eid, [])
                if isinstance(s, State)
            ]
        feiertag = any(
            kx.wert_bei(
                [
                    (s.last_updated.timestamp(), s.state)
                    for s in roh.get(k, [])
                    if isinstance(s, State)
                ],
                t,
            )
            == "on"
            for k in kalender
        )
        out[t] = (verlaeufe, feiertag)
    return out


async def nachtragen(hass: HomeAssistant, lz: Laufzeit) -> int:
    """Ältere Messungen ohne Momentaufnahme aus Verlauf und Journal ergänzen; Anzahl der ergänzten Messungen."""
    db = lz.datenbank
    offen = await hass.async_add_executor_job(
        db.ohne_kontext, time.time() - kx.NACHTRAG_TAGE * 86_400
    )
    if not offen:
        return 0
    try:
        from homeassistant.components.recorder import get_instance

        recorder = get_instance(hass)
    except KeyError, ImportError:
        return 0  # ohne Recorder kein Verlauf
    eintrag = lz.abruf.config_entry.entry_id
    ids = {
        k: eid for schluessel, k in EIGENE.items() if (eid := ab.eigene(hass, eintrag, schluessel))
    }
    sensoren = lz.abruf.speedtest.sensoren
    ids.update(_ookla_ids(hass, sensoren.eintrag if sensoren else None))
    if wid := _wetter_id(hass):
        ids.update({"wetter": wid, **dict.fromkeys(WETTER_ATTR, wid)})
    kalender = _plattform(hass, "calendar", (FEIERTAGE,))
    je_messung = await recorder.async_add_executor_job(
        _verlaeufe_je_messung, hass, ids, kalender, offen
    )
    journal = await hass.async_add_executor_job(
        db.journal_texte, "mobil_zelle", offen[0] - 30 * 86_400, offen[-1] + 30 * 86_400
    )
    kontexte = {
        t: kx.nachtrag(t, verlaeufe, journal, feiertag, _tag(t))
        for t, (verlaeufe, feiertag) in je_messung.items()
    }
    return await hass.async_add_executor_job(db.kontext_nachtragen, kontexte)
