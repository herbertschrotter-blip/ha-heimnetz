"""Vorgeschaltetes Mobilfunk-Modem (WU-0008): reine Logik ohne Home-Assistant-Code.

Kommt das Internet über ein eigenes 5G/LTE-Modem vor der FRITZ!Box (z. B. ein ZTE von Drei Österreich), kennt die Box
das Funknetz nicht. Diese Version liefert nur das Werkzeug, die Rohdaten des Modems abzufragen und geschwärzt
auszugeben, damit der Entwickler die Unterstützung später bauen kann – keine Auswertung.

Hier steht, was ohne Netz prüfbar ist und darum eigene Tests hat:
- `adresse_erlaubt`: nur private IPv4/IPv6-Adressen, keine Hostnamen, kein Loopback/Link-Local/unspezifiziert.
- `erkennen`: aus der Startseite lesen, ob es ein ZTE-Modem ist und welches Modell.
- `schwaerzen`: alles Vertrauliche aus den Rohdaten entfernen (nach Schlüssel und nach Wert), die Zellkennung bleibt.
- `werte_zaehlen`: wie viele Einzelwerte in der Antwort stehen.

Die Anmeldung und das Abfragen über das Netz macht der dünne HA-Teil `modem.py`; das Rechnen am Kennwort (der
Anmelde-Hash der ZTE-Weboberfläche) steht hier, weil es ohne Netz prüfbar ist.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from collections.abc import Mapping
from typing import Any

ERSATZ = "⟨geschwärzt⟩"

# Schlüssel (Teilzeichenfolge, ohne Groß-/Kleinschreibung): Wert wird geschwärzt. BEHALTEN hat Vorrang.
_SCHWAERZEN_TEIL = (
    "imei", "imsi", "iccid", "msisdn", "phone", "number", "bssid", "ssid", "wpa", "psk",
    "secret", "token", "stok", "cookie", "session", "serial", "sms",
    "username", "apn_user", "ipaddr", "ipv6", "wan_ip", "dns", "gps", "latitude", "longitude",
    "passw", "pass_", "pwd", "puk",
)  # fmt: skip
# Schlüssel als ganzes Wort (zwischen Trennern): schwärzen. Fängt „sn“, „mac“, „key“, „pin“, „lat“, „lon“, „pass“
# ohne längere Wörter wie „latency“, „macro“, „monkey“ zu treffen.
_SCHWAERZEN_WORT = frozenset(
    {"sn", "mac", "key", "pin", "lat", "lon", "pass", "puk", "imei", "imsi", "iccid", "psk"}
)
# Diese Schlüssel bleiben, auch wenn sie an einen der Begriffe oben erinnern (Zellkennung, Signal, Technik, Modell).
_BEHALTEN_TEIL = (
    "cell_id", "cellid", "eci", "enb", "gnb", "nci", "pci", "tac", "lac", "plmn", "mcc", "mnc",
    "band", "earfcn", "arfcn", "rsrp", "rsrq", "sinr", "snr", "rssi",
    "network_type", "provider", "model", "modell", "firmware", "version",
)  # fmt: skip

_TRENNER = re.compile(r"[^a-z0-9]+")

# Werte, die unabhängig vom Schlüssel geschwärzt werden (auch in freien Texten).
_MAC = re.compile(
    r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])"
)
_IMEI = re.compile(r"(?<!\d)\d{15}(?!\d)")
_ICCID = re.compile(r"(?<!\d)\d{18,22}(?!\d)")
_MAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_TEL = re.compile(r"(?<![\d+])\+43[\d /-]{6,}\d")
_IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
_IPV6 = re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}(?![\w:])")


def adresse_erlaubt(adresse: str) -> bool:
    """Nur private IPv4/IPv6-Adressen im eigenen Heimnetz; keine Hostnamen, kein Loopback/Link-Local/unspezifiziert."""
    try:
        ip = ipaddress.ip_address(adresse.strip())
    except ValueError:
        return False
    return ip.is_private and not (
        ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_reserved or ip.is_multicast
    )


def _ist_private(text: str) -> bool:
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified


def _schluessel_schwaerzen(schluessel: str) -> bool:
    lk = str(schluessel).lower()
    if any(b in lk for b in _BEHALTEN_TEIL):
        return False
    if any(s in lk for s in _SCHWAERZEN_TEIL):
        return True
    worte = {w for w in _TRENNER.split(lk) if w}
    return bool(worte & _SCHWAERZEN_WORT)


def schwaerzen(daten: Any) -> tuple[Any, int]:
    """Tief schwärzen (dict, list, Text, eingebettetes JSON); gibt (Kopie, Anzahl geschwärzter Werte) zurück.

    Nach Schlüssel: IMEI, IMSI, ICCID, Rufnummer, MAC, WLAN-Name/-Kennwort, Schlüssel, Sitzung, Seriennummer,
    Benutzer, WAN-/IPv6-/DNS-Adresse, Koordinaten. Nach Wert zusätzlich IMEI-/ICCID-Ziffernfolgen, MAC-Muster,
    öffentliche IP, E-Mail, Telefonnummer (+43…). Zellkennung, Signal, Band, Technik, Modell und Firmware bleiben.
    """
    zaehler = [0]
    return _tief(daten, zaehler), zaehler[0]


def _tief(wert: Any, zaehler: list[int]) -> Any:
    if isinstance(wert, Mapping):
        aus: dict[Any, Any] = {}
        for k, v in wert.items():
            if _schluessel_schwaerzen(k) and v not in (None, ""):
                aus[k] = ERSATZ
                zaehler[0] += 1
            else:
                aus[k] = _tief(v, zaehler)
        return aus
    if isinstance(wert, list | tuple):
        return [_tief(x, zaehler) for x in wert]
    if isinstance(wert, str):
        return _text_schwaerzen(wert, zaehler)
    return wert


def _text_schwaerzen(text: str, zaehler: list[int]) -> str:
    """Freien Text schwärzen; sieht er nach eingebettetem JSON aus, erst dieses rekursiv schwärzen."""
    knapp = text.strip()
    if knapp[:1] in "{[":
        try:
            geladen = json.loads(knapp)
        except ValueError:
            pass
        else:
            return json.dumps(_tief(geladen, zaehler), ensure_ascii=False)
    aus = text
    for muster in (_MAC, _MAIL, _TEL, _ICCID, _IMEI, _IPV6):
        aus, n = muster.subn(ERSATZ, aus)
        zaehler[0] += n

    def _ip(treffer: re.Match[str]) -> str:
        # öffentliche IP schwärzen, private (eigene Modem-/Heimnetz-Adresse) stehen lassen – nur die zählen
        if _ist_private(treffer.group(0)):
            return treffer.group(0)
        zaehler[0] += 1
        return ERSATZ

    return _IPV4.sub(_ip, aus)


def werte_zaehlen(daten: Any) -> int:
    """Einzelwerte (Blätter) in der Antwort – ohne leere Strings und None (für „n Werte“)."""
    if isinstance(daten, Mapping):
        return sum(werte_zaehlen(v) for v in daten.values())
    if isinstance(daten, list | tuple):
        return sum(werte_zaehlen(x) for x in daten)
    return 0 if daten is None or daten == "" else 1


_MODELL = re.compile(r"ZTE[\s_-]*([A-Z]{1,3}\d{1,4}[A-Z0-9]*)", re.IGNORECASE)


def erkennen(startseite: str) -> tuple[bool, str | None]:
    """Aus der Startseite lesen: ist es ein ZTE-Modem (Text „ZTE“, goform, ubus) und welches Modell."""
    tief = startseite.lower()
    zte = "zte" in tief or "goform" in tief or "ubus" in tief
    treffer = _MODELL.search(startseite)
    modell = f"ZTE {treffer.group(1).upper()}" if treffer else None
    return zte, modell


def anmelde_hash(kennwort: str, ld: str) -> str:
    """Anmelde-Hash der ZTE-Weboberfläche: SHA-256(SHA-256(Kennwort)·groß + LD·groß)·groß. Der LD-Wert kommt
    vorher vom Gerät (`cmd=LD`). Öffentlich dokumentiert (z. B. teixeluis/zte-lte-modem)."""
    erst = hashlib.sha256(kennwort.encode("utf-8")).hexdigest().upper()
    return hashlib.sha256((erst + ld.upper()).encode("utf-8")).hexdigest().upper()
