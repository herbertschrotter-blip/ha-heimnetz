"""Momentaufnahme zu einer Speedtest-Messung (WU-0005): was im Moment der Messung los war.

Flach, mit festen Schlüsseln (KEYS) – so steht sie in der Datenbank (Spalte `kontext`, JSON), als Attribute des
Sensors „Letzte Messung“ (für InfluxDB) und auf der Seite. Fehlende Werte fehlen im Wörterbuch (nicht None).
`quelle` sagt, woher: „messung“ (im Moment der Messung) oder „nachgetragen“ (später aus Verlauf und Journal; nur, was
dort steht).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from .karte import sendeanlage
from .mobil import Mobilfunk

MESSUNG = "messung"
NACHGETRAGEN = "nachgetragen"
NACHTRAG_TAGE = 62  # so weit reicht der Verlauf von Home Assistant (purge_keep_days)

# Ookla: Schlüssel im unique_id des Sensors → Schlüssel hier
OOKLA_ZUSATZ = {
    "jitter": "jitter",
    "jitter during download": "jitter_down",
    "jitter during upload": "jitter_up",
    "bufferbloat_grade": "bufferbloat",
    "isp": "anbieter",
    "result_url": "ergebnis_url",
}

KEYS = (
    "quelle",
    # Messung
    "ausloeser",
    "serie_lauf",
    "serie_n",
    *OOKLA_ZUSATZ.values(),
    # Mobilfunk
    "netz",
    "zelle",
    "anlage",
    "pci",
    "rsrp",
    "rsrq",
    "nr_aktiv",
    "nr_pci",
    "nr_rsrp",
    "nr_rsrq",
    "entfernung_m",
    "nachbarzellen",
    "plmn",
    "tac",
    "verbunden_s",
    "mast_m",
    "mast_richtung",
    # Box
    "box_modell",
    "box_firmware",
    "box_laufzeit_s",
    "baender",
    # Heimnetz
    "online",
    "online_wlan",
    # Umgebung
    "wetter",
    "temperatur",
    "feuchte",
    "wolken",
    "tagesart",
)

PLAN, JETZT, SERIE, OOKLA = "messplan", "jetzt", "serie", "ookla"
AUSLOESER_FENSTER_S = (
    5 * 60
)  # eine Messung bis so lange nach dem Auslösen gehört zu diesem Auslösen


def tagesart(tag: date, feiertag: bool) -> str:
    """„feiertag“, „wochenende“ oder „werktag“."""
    return "feiertag" if feiertag else "wochenende" if tag.weekday() >= 5 else "werktag"


def ausloeser(
    t: float, ausgeloest: float, grund: str | None, serie: Mapping[str, int] | None
) -> str:
    """Wer die Messung gestartet hat: eine laufende Serie, kurz davor der Messplan oder „Jetzt messen“, sonst Ookla
    selbst (eigener Takt oder von Hand in Ookla)."""
    if serie:
        return SERIE
    if ausgeloest and 0 <= t - ausgeloest <= AUSLOESER_FENSTER_S:
        return JETZT if grund == "von Hand" else PLAN
    return OOKLA


def _ohne_leere(d: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and v != ""}


def mobilfunk(m: Mobilfunk | None) -> dict[str, Any]:
    """Mobilfunk-Teil aus dem Stand der Box."""
    if m is None:
        return {}
    h, nr = m.haupt, m.nr
    nachbarn = sum(1 for z in m.zellen if z is not h and z is not nr)
    return _ohne_leere(
        {
            "netz": m.technik,
            "zelle": h.zelle if h else None,
            "anlage": sendeanlage(h) if h else None,
            "pci": h.pci if h else None,
            "rsrp": h.rsrp if h else None,
            "rsrq": h.rsrq if h else None,
            "nr_aktiv": nr is not None,
            "nr_pci": nr.pci if nr else None,
            "nr_rsrp": nr.rsrp if nr else None,
            "nr_rsrq": nr.rsrq if nr else None,
            "entfernung_m": h.entfernung_m if h else None,
            "nachbarzellen": nachbarn if m.zellen else None,
            "plmn": h.plmn if h else None,
            "tac": h.tac if h else None,
            "verbunden_s": m.laufzeit_s,
        }
    )


def zahl(wert: Any) -> float | None:
    try:
        return round(float(wert), 2)
    except TypeError, ValueError:
        return None


def ookla(zustaende: Mapping[str, Any]) -> dict[str, Any]:
    """Zusatzwerte der Ookla-Sensoren (Schlüssel wie OOKLA_ZUSATZ-Werte); Zahlen als Zahl, sonst Text."""
    out: dict[str, Any] = {}
    for k in OOKLA_ZUSATZ.values():
        v = zustaende.get(k)
        if v in (None, "", "unknown", "unavailable"):
            continue
        out[k] = zahl(v) if k.startswith("jitter") else str(v)[:200]
    return out


def wetter(zustand: str | None, attr: Mapping[str, Any]) -> dict[str, Any]:
    if zustand in (None, "", "unknown", "unavailable"):
        return {}
    return _ohne_leere(
        {
            "wetter": zustand,
            "temperatur": zahl(attr.get("temperature")),
            "feuchte": zahl(attr.get("humidity")),
            "wolken": zahl(attr.get("cloud_coverage")),
        }
    )


def momentaufnahme(*teile: Mapping[str, Any], quelle: str = MESSUNG) -> dict[str, Any]:
    """Teile zusammenführen, nur bekannte Schlüssel, in fester Reihenfolge."""
    alles: dict[str, Any] = {}
    for t in teile:
        alles.update(t)
    alles["quelle"] = quelle
    return {k: alles[k] for k in KEYS if k in alles and alles[k] is not None and alles[k] != ""}


# ── Nachtragen aus Verlauf und Journal ──


def wert_bei(verlauf: Sequence[tuple[float, Any]], t: float) -> Any:
    """Zustand zum Zeitpunkt t aus einem nach Zeit sortierten Verlauf (Zeitpunkt der Änderung, Wert): der letzte Wert
    davor. Unbekannt/nicht verfügbar → None."""
    wert = None
    for zeit, v in verlauf:
        if zeit > t:
            break
        wert = v
    return None if wert in ("unknown", "unavailable", "") else wert


OOKLA_NACH_S = (
    5 * 60
)  # die Ookla-Zusatzsensoren bekommen den Wert der Messung erst kurz nach ihrem Zeitpunkt


def wert_nach(verlauf: Sequence[tuple[float, Any]], t: float, fenster: float = OOKLA_NACH_S) -> Any:
    """Erster Wert, der nach t (bis t + fenster) gesetzt wurde – für Werte, die zur Messung erst danach erscheinen
    (Jitter, Anbieter, Link der Ookla-Sensoren). Davor stand noch der der vorigen Messung."""
    for zeit, v in verlauf:
        if t < zeit <= t + fenster:
            return None if v in ("unknown", "unavailable", "") else v
    return None


# Journal-Einträge von mobil.abgleich – in jeder Sprache, in der sie geschrieben wurden
ZELLWECHSEL = re.compile(r"(?:Funkzelle gewechselt|cell changed) (\S+) → (\S+)")


def zelle_bei(journal: Sequence[tuple[float, str]], t: float) -> str | None:
    """Ankerzelle („enb-sektor“) zum Zeitpunkt t aus den Journal-Einträgen „Funkzelle gewechselt A → B“ (sortiert):
    das Ziel des letzten Wechsels davor, sonst die Ausgangszelle des ersten Wechsels danach."""
    vorher = nachher = None
    for zeit, text in journal:
        m = ZELLWECHSEL.search(text)
        if not m:
            continue
        if zeit <= t:
            vorher = m.group(2)
        elif nachher is None:
            nachher = m.group(1)
            break
    kennung = vorher or nachher
    return kennung.split("/")[0] if kennung else None


def nachtrag(
    t: float,
    verlaeufe: Mapping[str, Sequence[tuple[float, Any]]],
    journal: Sequence[tuple[float, str]],
    feiertag: bool,
    tag: date,
) -> dict[str, Any]:
    """Momentaufnahme für eine ältere Messung: Schlüssel von `verlaeufe` sind die Schlüssel hier (netz, rsrp, …,
    jitter, wetter, temperatur …). Ookla-Werte: der erste nach der Messung, alle anderen: der Stand zur Messung."""
    ookla_keys = set(OOKLA_ZUSATZ.values())
    werte: dict[str, Any] = {}
    for k, v in verlaeufe.items():
        w = wert_nach(v, t) if k in ookla_keys else wert_bei(v, t)
        if w is None:
            continue
        werte[k] = (
            zahl(w)
            if k in ("rsrp", "rsrq", "nr_rsrp", "nr_rsrq", "temperatur", "feuchte", "wolken")
            or k.startswith("jitter")
            else w
        )
    for k in ("rsrp", "rsrq", "nr_rsrp", "nr_rsrq"):
        if isinstance(werte.get(k), float):
            werte[k] = round(werte[k])
    if "nr_rsrp" in werte:
        werte["nr_aktiv"] = True
    if z := zelle_bei(journal, t):
        werte["zelle"] = z
        werte["anlage"] = z.split("-")[0].lower() if "-" in z else None
    werte["tagesart"] = tagesart(tag, feiertag)
    return momentaufnahme(werte, quelle=NACHGETRAGEN)
