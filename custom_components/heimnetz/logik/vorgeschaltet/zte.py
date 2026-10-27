"""Bausteine ZTE goform (ältere Geräte wie MC801A, MF289F) und ZTE ubus (neuere wie G5TS/G5TC): Anfragen bauen,
Antworten lesen und in das gemeinsame Format umrechnen. Ohne Netz.

Protokoll nach öffentlichen Quellen, nicht übernommen, sondern nachgebaut:
- goform: `goform/goform_get_cmd_process?isTest=false&multi_data=1&cmd=…` (lesen), Anmeldung über
  `goform_set_cmd_process` mit `goformId=LOGIN` und dem Hash aus `logik.modem.anmelde_hash` (z. B. teixeluis/zte-lte-modem).
- ubus: JSON-RPC 2.0 an `/ubus/?t=<zeit>`, `params = [sitzung, objekt, methode, argumente]`, Antwort
  `result = [code, daten]`; Anmeldung `zwrt_web.web_login_info` (Salz `zte_web_sault`, verbleibende Versuche
  `login_fail_num`) und `zwrt_web.web_login` mit SHA-256(SHA-256(Kennwort)·groß + Salz)·groß; Werte aus
  `zte_nwinfo_api.nwinfo_get_netinfo`. Quelle: chennest/zte-cpe-go (GPL-3.0, Go) – nur das öffentliche Protokoll, kein
  Code übernommen.

Die Feldnamen der Funkwerte sind bei beiden Schnittstellen dieselben (ZTE-Firmware); welche ein Gerät wirklich liefert,
ist ungetestet am Gerät – was fehlt, bleibt leer.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from ..mobil import Mobilfunk, Zelle
from ..werte import text

# Lesende goform-Werte für den laufenden Abruf (die Diagnose fragt eine breitere Liste)
GOFORM_FELDER = (
    "modem_model,network_type,network_provider,rmcc,rmnc,ppp_status,realtime_time,"
    "lte_rsrp,lte_rsrq,lte_snr,lte_band,lte_pci,cell_id,tac,lac,"
    "nr5g_action_band,nr5g_pci,nr5g_cell_id,nr5g_rsrp,nr5g_rsrq,nr5g_snr,"
    "Z5g_rsrp,Z5g_rsrq,Z5g_SINR,Z5g_CELL_ID,wan_active_band"
)

NULL_SITZUNG = "0" * 32
# ubus: nur diese Objekte/Methoden – Anmelden, Abmelden, Lesen. Nie eine set-Methode.
UBUS_ERLAUBT = frozenset(
    {
        ("zwrt_web", "web_login_info"),
        ("zwrt_web", "web_login"),
        ("zwrt_web", "web_logout"),
        ("zte_nwinfo_api", "nwinfo_get_netinfo"),
        ("zwrt_data", "get_wwaniface"),
    }
)
UBUS_LESEN: tuple[tuple[str, str, dict[str, Any]], ...] = (
    ("zte_nwinfo_api", "nwinfo_get_netinfo", {}),
    ("zwrt_data", "get_wwaniface", {"source_module": "web", "cid": 1}),
)


def json_objekt(roh: str) -> dict[str, Any] | None:
    try:
        wert = json.loads(roh)
    except ValueError:
        return None
    return wert if isinstance(wert, dict) else None


# ── goform ──
def goform_modell(antwort: Mapping[str, Any] | None) -> str | None:
    """Probe ohne Anmeldung: antwortet goform mit JSON, ist es ein goform-Gerät. Modell aus `modem_model` ("" wenn das
    Gerät es ohne Anmeldung nicht nennt); None = keine goform-Antwort."""
    if antwort is None:
        return None
    return text(antwort.get("modem_model")).removeprefix("ZTE").strip()


def goform_angemeldet(antwort: Mapping[str, Any] | None) -> bool:
    """`goformId=LOGIN`: „0“ heißt angenommen; alles andere (1, 3, „failure“) abgelehnt."""
    return antwort is not None and text(antwort.get("result")) == "0"


# ── ubus ──
def ubus_anfrage(
    sitzung: str, objekt: str, methode: str, argumente: Mapping[str, Any], nr: int
) -> list[dict[str, Any]]:
    """JSON-RPC-Körper für einen ubus-Aufruf. Nur erlaubte Objekte/Methoden – sonst ValueError (nie ein set-Befehl)."""
    if (objekt, methode) not in UBUS_ERLAUBT:
        raise ValueError(f"ubus {objekt}.{methode} ist nicht erlaubt")
    return [
        {
            "jsonrpc": "2.0",
            "id": nr,
            "method": "call",
            "params": [sitzung, objekt, methode, dict(argumente)],
        }
    ]


def ubus_ergebnis(roh: str) -> tuple[int | None, dict[str, Any]]:
    """Antwort auf einen ubus-Aufruf: (Code, Daten). Code None = keine ubus-Antwort; 0 = in Ordnung."""
    try:
        wert = json.loads(roh)
    except ValueError:
        return None, {}
    if isinstance(wert, list):
        wert = wert[0] if wert else None
    if not isinstance(wert, dict):
        return None, {}
    if "error" in wert:
        fehler = wert["error"]
        try:
            return (int(fehler.get("code", -1)) if isinstance(fehler, dict) else -1), {}
        except TypeError, ValueError:
            return -1, {}
    ergebnis = wert.get("result")
    if not isinstance(ergebnis, list) or not ergebnis:
        return None, {}
    try:
        code = int(ergebnis[0])
    except TypeError, ValueError:
        return None, {}
    daten = ergebnis[1] if len(ergebnis) > 1 and isinstance(ergebnis[1], dict) else {}
    return code, daten


def ubus_login_info(daten: Mapping[str, Any]) -> tuple[str, int | None]:
    """Salz und verbleibende Versuche aus `web_login_info`."""
    versuche = daten.get("login_fail_num")
    try:
        rest = int(versuche) if versuche is not None else None
    except TypeError, ValueError:
        rest = None
    return text(daten.get("zte_web_sault")), rest


def ubus_hash(kennwort: str, salz: str) -> str:
    """SHA-256(SHA-256(Kennwort)·groß + Salz)·groß – wie die Weboberfläche selbst."""
    erst = hashlib.sha256(kennwort.encode("utf-8")).hexdigest().upper()
    return hashlib.sha256((erst + salz).encode("utf-8")).hexdigest().upper()


def ubus_sitzung(daten: Mapping[str, Any]) -> str | None:
    """`web_login`: Sitzung bei result 0, sonst None (abgelehnt; 3 = jemand anderer ist angemeldet)."""
    if text(daten.get("result")) != "0":
        return None
    return text(daten.get("ubus_rpc_session")) or None


# ── umrechnen (beide Schnittstellen) ──
def _zahl(wert: Any) -> float | None:
    roh = text(wert).replace(",", ".")
    for einheit in ("dBm", "dB"):
        roh = roh.removesuffix(einheit).strip()
    try:
        v = float(roh)
    except ValueError:
        return None
    return v


def _ganz(wert: Any) -> int | None:
    v = _zahl(wert)
    return round(v) if v is not None else None


def _hex(wert: Any) -> int | None:
    """ZTE nennt PCI und Zellkennung hexadezimal (so zeigt sie auch die Weboberfläche)."""
    roh = text(wert).lower().removeprefix("0x")
    try:
        return int(roh, 16) if roh else None
    except ValueError:
        return None


def _band(wert: Any, vor: str) -> str:
    roh = text(wert)
    if not roh:
        return ""
    roh = roh.split(",")[0].strip().upper().lstrip("BN").removeprefix("AND").strip()
    roh = roh.removeprefix("LTE").removeprefix("NR").strip().lstrip("BN")
    return f"{vor}{roh}" if roh.isdigit() else ""


def _plmn(mcc: Any, mnc: Any) -> str:
    a, b = text(mcc), text(mnc)
    if not (a.isdigit() and b.isdigit()) or len(a) != 3:
        return ""
    return a + b.zfill(2)


def technik(netz: str, lte: bool, nr: bool) -> str:
    """ZTE network_type (LTE, ENDC, LTE-NSA, SA, NR5G_SA …) in die Schreibweise der Box: LTE, 5G-NSA, 5G-SA."""
    n = netz.upper().replace("_", "-")
    if (
        "SA" in n.split("-")
        or n in ("SA", "NR5G-SA", "NR-SA", "5G-SA")
        or (nr and not lte and "NR" in n)
    ):
        return "5G-SA"
    if "ENDC" in n or "NSA" in n or (lte and nr):
        return "5G-NSA"
    if lte or "LTE" in n:
        return "LTE"
    return netz


def zelle_lte(eci: int | None) -> str:
    """E-UTRAN-Zellkennung (28 Bit) wie die Box: eNodeB und Sektor hexadezimal („1a2b3-c4“)."""
    if not eci:
        return ""
    return f"{eci >> 8:x}-{eci & 0xFF:02x}"


def _pci(wert: Any, hex_: bool) -> int | None:
    """goform nennt die PCI hexadezimal. Bei ubus ist das offen: nur Ziffern → dezimal, mit a–f → hexadezimal
    (am Gerät prüfen, sobald echte Rohdaten vorliegen)."""
    roh = text(wert)
    if not hex_ and roh.isdigit():
        return int(roh)
    return _hex(roh)


def aus_werten(w: Mapping[str, Any], pci_hex: bool = True) -> Mobilfunk | None:
    """goform- oder ubus-netinfo-Werte → gemeinsames Format. None, wenn das Gerät keinen Funkwert nennt."""
    anbieter = text(w.get("network_provider"))
    plmn = _plmn(w.get("rmcc"), w.get("rmnc"))
    rsrp = _ganz(w.get("lte_rsrp"))
    lte: Zelle | None = None
    if rsrp is not None or text(w.get("cell_id")):
        lte = Zelle(
            rolle="primary",
            art="LTE",
            anbieter=anbieter,
            pci=_pci(w.get("lte_pci"), pci_hex),
            zelle=zelle_lte(_hex(w.get("cell_id"))),
            rsrp=rsrp,
            rsrq=_ganz(w.get("lte_rsrq")),
            plmn=plmn,
            tac=text(w.get("tac")).lower().removeprefix("0x"),
            sinr=_zahl(w.get("lte_snr")),
            band=_band(w.get("lte_band") or w.get("lte_ca_pcell_band"), "B"),
        )
    nr_rsrp = _ganz(w.get("nr5g_rsrp") if text(w.get("nr5g_rsrp")) else w.get("Z5g_rsrp"))
    nr: Zelle | None = None
    if nr_rsrp is not None:
        nr = Zelle(
            rolle="secondary" if lte else "primary",
            art="5G",
            anbieter=anbieter,
            pci=_pci(w.get("nr5g_pci"), pci_hex),
            zelle="",  # 5G-Zellkennung lässt sich nicht nachschlagen – wie bei der Box nur die PCI
            rsrp=nr_rsrp,
            rsrq=_ganz(w.get("nr5g_rsrq") if text(w.get("nr5g_rsrq")) else w.get("Z5g_rsrq")),
            plmn=plmn,
            sinr=_zahl(w.get("nr5g_snr") if text(w.get("nr5g_snr")) else w.get("Z5g_SINR")),
            band=_band(w.get("nr5g_action_band"), "n"),
        )
    if lte is None and nr is None:
        return None
    zellen = tuple(z for z in (lte, nr) if z is not None)
    laufzeit = _ganz(w.get("realtime_time") or w.get("connect_time"))
    return Mobilfunk(
        technik=technik(text(w.get("network_type")), lte is not None, nr is not None),
        roaming=False,
        haupt=lte or nr,
        nr=nr,
        laufzeit_s=laufzeit if laufzeit is not None and laufzeit >= 0 else None,
        zellen=zellen,
    )


def aus_ubus(netinfo: Mapping[str, Any], wwan: Mapping[str, Any] | None = None) -> Mobilfunk | None:
    """ubus: Funkwerte aus `nwinfo_get_netinfo`, die Verbindungsdauer – falls genannt – aus `get_wwaniface`."""
    werte = dict(netinfo)
    if wwan:
        for k in ("realtime_time", "connect_time"):
            if k in wwan and k not in werte:
                werte[k] = wwan[k]
    return aus_werten(werte, pci_hex=False)
