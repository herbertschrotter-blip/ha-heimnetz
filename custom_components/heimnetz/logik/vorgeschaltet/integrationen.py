"""Werte aus einer HA-Integration des vorgeschalteten Geräts statt eigener Abfrage (Huawei LTE, NETGEAR LTE,
Teltonika): Zustände ihrer Sensoren in das gemeinsame Format umrechnen. Ohne Home Assistant.

Gefunden werden die Sensoren über das Entitätsregister am Ende ihrer `unique_id` (so legen die Integrationen sie an,
siehe homeassistant/components/<domain>/sensor.py): huawei_lte `<seriennummer>-<gruppe>.<feld>`, netgear_lte
`<feld>_<seriennummer>`, teltonika `<eintrag>_<modem>_<feld>`. Hier steht nur die Zuordnung Feld → Wert.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..mobil import Mobilfunk, Zelle
from .huawei import aus_hilink, zahl

# je Domain: Feld der Integration → unser Feld (so heißen sie in der unique_id)
FELDER: dict[str, dict[str, str]] = {
    "huawei_lte": {
        "device_signal.rsrp": "rsrp",
        "device_signal.rsrq": "rsrq",
        "device_signal.sinr": "sinr",
        "device_signal.pci": "pci",
        "device_signal.cell_id": "cell_id",
        "device_signal.tac": "tac",
        "device_signal.band": "band",
        "device_signal.nrrsrp": "nrrsrp",
        "device_signal.nrrsrq": "nrrsrq",
        "device_signal.nrsinr": "nrsinr",
        "net_current_plmn.FullName": "FullName",
        "net_current_plmn.Numeric": "Numeric",
        "monitoring_traffic_statistics.CurrentConnectTime": "CurrentConnectTime",
    },
    "netgear_lte": {
        "rx_level": "rsrp",  # NETGEAR nennt die Empfangsstärke rx_level (dBm)
        "current_band": "band",
        "cell_id": "cell_id",
        "register_network_display": "anbieter",
        "current_ps_service_type": "netz",
    },
    "teltonika": {
        "rsrp": "rsrp",
        "rsrq": "rsrq",
        "sinr": "sinr",
        "band": "band",
        "operator": "anbieter",
        "connection_type": "netz",
    },
}
UNBRAUCHBAR = ("", "unknown", "unavailable", "none")


def feld(domain: str, unique_id: str) -> str | None:
    """Welches unserer Felder ein Sensor der Integration trägt (am Ende bzw. Anfang seiner unique_id)."""
    for ihr, unser in FELDER.get(domain, {}).items():
        if domain == "huawei_lte" and unique_id.endswith(f"-{ihr}"):
            return unser
        if domain == "netgear_lte" and unique_id.startswith(f"{ihr}_"):
            return unser
        if domain == "teltonika" and unique_id.endswith(f"_{ihr}"):
            return unser
    return None


# Einheit einer Dauer (unit_of_measurement der Entität) → Sekunden
_SEKUNDEN = {"s": 1, "min": 60, "h": 3600, "d": 86_400}


def sekunden(wert: str, einheit: str | None) -> str:
    """Dauer in Sekunden – die Integration zeigt sie womöglich in einer anderen Einheit (z. B. h)."""
    v = zahl(wert)
    faktor = _SEKUNDEN.get((einheit or "s").strip(), 1)
    return str(round(v * faktor)) if v is not None else wert


def aus_zustaenden(
    domain: str, werte: Mapping[str, str], einheiten: Mapping[str, str | None] | None = None
) -> Mobilfunk | None:
    """Zustände der Sensoren (unser Feld → Zustand, dazu deren Einheit) → gemeinsames Format; None ohne Signalwert."""
    w = {k: v for k, v in werte.items() if str(v).strip().lower() not in UNBRAUCHBAR}
    if "CurrentConnectTime" in w:
        w["CurrentConnectTime"] = sekunden(
            w["CurrentConnectTime"], (einheiten or {}).get("CurrentConnectTime")
        )
    if domain == "huawei_lte":
        return aus_hilink(w, w, w)
    rsrp = zahl(w.get("rsrp"))
    if rsrp is None:
        return None
    netz = str(w.get("netz", "")).upper()
    art = "5G" if "5G" in netz or "NR" in netz else "LTE"
    band = str(w.get("band", "")).upper().replace("BAND", "").strip().lstrip("BN")
    z = Zelle(
        rolle="primary",
        art=art,
        anbieter=str(w.get("anbieter", "")),
        pci=None,
        zelle="",
        rsrp=round(rsrp),
        rsrq=round(v) if (v := zahl(w.get("rsrq"))) is not None else None,
        sinr=zahl(w.get("sinr")),
        band=f"{'n' if art == '5G' else 'B'}{band}" if band.isdigit() else "",
    )
    return Mobilfunk(
        technik="5G-SA" if art == "5G" else "LTE",
        roaming=False,
        haupt=z,
        nr=z if art == "5G" else None,
        zellen=(z,),
    )
