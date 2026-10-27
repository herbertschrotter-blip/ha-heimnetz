"""Baustein TP-Link LTE/5G-Router (Archer MR-, NX-Serie, M-Serie): `LTEStatus` der Bibliothek `tplinkrouterc6u`
(AlexandrErohin/TP-Link-Archer-C6U, GPL-3.0; wird nur als Abhängigkeit installiert, kein Code übernommen) in das
gemeinsame Format umrechnen. Ohne Netz.

Die Bibliothek liefert über `get_lte_status()` nur Signalstärke, -qualität und SNR der verbundenen Zelle, die Netzart
(Zahl, Tabelle `LTEStatus.network_types`) und den Anbieter – keine Zellkennung, keine PCI. Ungetestet am Gerät.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..mobil import Mobilfunk, Zelle
from ..werte import ganzzahl, text

# LTEStatus.network_types: 3 „4G LTE“, 7 „4G+ LTE“, 8 „5G NR“; 1/2/4/5/6 2G/3G
_TECHNIK = {3: "LTE", 7: "LTE", 8: "5G"}


def aus_lte_status(d: Mapping[str, Any]) -> Mobilfunk | None:
    """`dataclasses.asdict(LTEStatus)` → gemeinsames Format; None ohne Signalwert oder ohne Verbindung."""
    rsrp = ganzzahl(d.get("rsrp"))
    if rsrp is None or rsrp == 0:
        return None
    netz = _TECHNIK.get(ganzzahl(d.get("network_type")) or -1, "")
    art = "5G" if netz == "5G" else "LTE"
    snr = d.get("snr")
    z = Zelle(
        rolle="primary",
        art=art,
        anbieter=text(d.get("isp_name")),
        pci=None,
        zelle="",
        rsrp=rsrp,
        rsrq=ganzzahl(d.get("rsrq")),
        sinr=float(snr) if isinstance(snr, int | float) else None,
    )
    return Mobilfunk(
        technik="5G-SA" if art == "5G" else netz or "LTE",
        roaming=False,
        haupt=z,
        nr=z if art == "5G" else None,
        zellen=(z,),
    )
