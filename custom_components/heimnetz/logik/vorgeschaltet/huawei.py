"""Baustein Huawei HiLink (B535, B818, E5xxx, 5G CPE …): Antworten der Bibliothek `huawei-lte-api` (dieselbe, die
Home Assistant für die Integration huawei_lte nutzt) in das gemeinsame Format umrechnen. Ohne Netz.

Die Bibliothek liefert die XML-Antworten des Geräts als Wörterbuch mit Texten wie „-95dBm“, „-11.0dB“, „12dB“
(`device/signal`), dazu `net/current-plmn` (FullName, Numeric) und `monitoring/traffic-statistics`
(CurrentConnectTime in Sekunden). Felder laut huawei-lte-api (Salamek/huawei-lte-api, LGPL-3.0) und der Integration
huawei_lte von Home Assistant; ungetestet am Gerät.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ..mobil import Mobilfunk, Zelle
from ..werte import text
from .zte import zelle_lte

_ZAHL = re.compile(r"-?\d+(?:[.,]\d+)?")


def zahl(wert: Any) -> float | None:
    """„-95dBm“, „&gt;=-44dBm“, „12dB“ → Zahl; leer oder unlesbar → None."""
    m = _ZAHL.search(text(wert).replace("&gt;", "").replace("&lt;", ""))
    return float(m.group(0).replace(",", ".")) if m else None


def _ganz(wert: Any) -> int | None:
    v = zahl(wert)
    return round(v) if v is not None else None


def _dezimal(wert: Any) -> int | None:
    roh = text(wert)
    if roh.isdigit():
        return int(roh)
    try:
        return int(roh, 16) if roh else None
    except ValueError:
        return None


def _tac(wert: Any) -> str:
    """TAC hexadezimal wie die Box; Huawei nennt ihn meist dezimal."""
    v = _dezimal(wert)
    return f"{v:x}" if v else ""


def _band(wert: Any, vor: str) -> str:
    roh = text(wert).upper().lstrip("BN")
    return f"{vor}{roh}" if roh.isdigit() else ""


def modell(basis: Mapping[str, Any]) -> str:
    """`device/basic_information` (ohne Anmeldung): devicename, z. B. „B535-232“."""
    name = text(basis.get("devicename") or basis.get("DeviceName"))
    return f"Huawei {name}" if name else ""


def aus_hilink(
    signal: Mapping[str, Any],
    plmn: Mapping[str, Any] | None = None,
    verkehr: Mapping[str, Any] | None = None,
) -> Mobilfunk | None:
    """`device/signal` (+ `net/current-plmn`, `monitoring/traffic-statistics`) → gemeinsames Format."""
    plmn = plmn or {}
    anbieter = text(plmn.get("FullName") or plmn.get("ShortName"))
    netz = text(plmn.get("Numeric"))
    netz = netz if netz.isdigit() and len(netz) in (5, 6) else ""
    rsrp = _ganz(signal.get("rsrp"))
    lte: Zelle | None = None
    if rsrp is not None:
        lte = Zelle(
            rolle="primary",
            art="LTE",
            anbieter=anbieter,
            pci=_dezimal(signal.get("pci")),
            zelle=zelle_lte(_dezimal(signal.get("cell_id"))),
            rsrp=rsrp,
            rsrq=_ganz(signal.get("rsrq")),
            plmn=netz,
            tac=_tac(signal.get("tac")),
            sinr=zahl(signal.get("sinr")),
            band=_band(signal.get("band"), "B"),
        )
    nr_rsrp = _ganz(signal.get("nrrsrp"))
    nr: Zelle | None = None
    if nr_rsrp is not None:
        nr = Zelle(
            rolle="secondary" if lte else "primary",
            art="5G",
            anbieter=anbieter,
            pci=_dezimal(signal.get("nrpci")),
            zelle="",
            rsrp=nr_rsrp,
            rsrq=_ganz(signal.get("nrrsrq")),
            plmn=netz,
            sinr=zahl(signal.get("nrsinr")),
            band=_band(signal.get("nrband"), "n"),
        )
    if lte is None and nr is None:
        return None
    laufzeit = _ganz((verkehr or {}).get("CurrentConnectTime"))
    return Mobilfunk(
        technik="5G-NSA" if lte and nr else "5G-SA" if nr else "LTE",
        roaming=False,
        haupt=lte or nr,
        nr=nr,
        laufzeit_s=laufzeit,
        zellen=tuple(z for z in (lte, nr) if z is not None),
    )
