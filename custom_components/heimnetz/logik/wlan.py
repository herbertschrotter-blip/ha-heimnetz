"""WLAN der Box (TR-064 WLANConfiguration, nur lesend): Bänder, Geräte im WLAN, Kanalwechsel, Befunde.

Felder laut AVM „TR-064 WLAN Configuration“ (Version 49, 2026-03-10): GetInfo (Enable, Status, Standard,
X_AVM-DE_FrequencyBand), GetChannelInfo (Channel, X_AVM-DE_AutoChannelEnabled), X_AVM-DE_GetWLANExtInfo
(X_AVM-DE_APType) und die Geräteliste aus X_AVM-DE_GetWLANDeviceListPath. Den Empfang meldet die Box je Gerät als
X_AVM-DE_SignalStrength in Prozent (0…100), nicht in dBm. SSID und Kennwort werden nicht übernommen.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .ereignis import INFO, Ereignis
from .sprache import DE, t
from .werte import ganzzahl, ja, text

BAENDER = {"2400": "2,4", "5000": "5", "6000": "6"}
SCHNELL = ("5", "6")


def band_text(band: str, sprache: str = DE) -> str:
    """Band zum Anzeigen: intern „2,4“, auf Englisch „2.4“."""
    return band if sprache == DE else band.replace(",", ".")


@dataclass(frozen=True)
class Band:
    """Ein Funknetz der Box (ohne Gastnetz). `band`: "2,4", "5" oder "6" (GHz)."""

    band: str
    an: bool
    kanal: int | None
    auto: bool | None
    standard: str


@dataclass(frozen=True)
class Funkgeraet:
    """Ein Gerät im WLAN der Box. `signal` in Prozent, `mbit` aktuelle Geschwindigkeit."""

    mac: str
    kanal: int | None
    signal: int | None
    mbit: int | None
    gast: bool


@dataclass(frozen=True)
class Wlan:
    baender: tuple[Band, ...] = ()
    gast_an: bool | None = None
    geraete: tuple[Funkgeraet, ...] = ()


def band_aus(info: Mapping[str, Any], kanal_info: Mapping[str, Any]) -> Band | None:
    """GetInfo + GetChannelInfo eines WLANConfiguration-Dienstes → Band; None = Band unbekannt."""
    band = BAENDER.get(text(info.get("NewX_AVM-DE_FrequencyBand")))
    if band is None:
        return None
    # die Doku nennt das Argument einmal „NewX_AVM-DEAuto_ChannelEnabled“ – beide Schreibweisen annehmen
    auto = kanal_info.get(
        "NewX_AVM-DE_AutoChannelEnabled", kanal_info.get("NewX_AVM-DEAuto_ChannelEnabled")
    )
    return Band(
        band=band,
        an=ja(info.get("NewEnable")) and text(info.get("NewStatus")) == "Up",
        kanal=ganzzahl(kanal_info.get("NewChannel", info.get("NewChannel"))) or None,
        auto=None if auto is None else ja(auto),
        standard=text(info.get("NewStandard")),
    )


def ist_gast(ext: Mapping[str, Any]) -> bool:
    return text(ext.get("NewX_AVM-DE_APType")) == "guest"


def geraete_aus(roh: str | bytes) -> tuple[Funkgeraet, ...]:
    """XML der Geräteliste (X_AVM-DE_GetWLANDeviceListPath)."""
    out = []
    for item in ET.fromstring(roh):
        if item.tag != "Item":
            continue
        d = {c.tag: text(c.text) for c in item}
        mac = d.get("AssociatedDeviceMACAddress", "").upper()
        if not mac:
            continue
        out.append(
            Funkgeraet(
                mac=mac,
                kanal=ganzzahl(d.get("AssociatedDeviceChannel")) or None,
                signal=ganzzahl(d.get("X_AVM-DE_SignalStrength")),
                mbit=ganzzahl(d.get("X_AVM-DE_Speed")),
                gast=d.get("AssociatedDeviceGuest") == "1",
            )
        )
    return tuple(out)


def band_von(g: Funkgeraet, baender: Iterable[Band]) -> str | None:
    """Band eines Geräts: das Band der Box auf demselben Kanal; sonst nach der Kanalnummer (bis 14 = 2,4 GHz)."""
    if g.kanal is None:
        return None
    baender = tuple(baender)
    for b in baender:
        if b.kanal == g.kanal:
            return b.band
    if any(b.band == "6" for b in baender):
        return None  # 6-GHz-Kanäle überschneiden sich mit den Nummern der anderen Bänder
    return "2,4" if g.kanal <= 14 else "5"


def abgleich(
    alt: Mapping[str, int], baender: Iterable[Band], sprache: str = DE
) -> tuple[list[Ereignis], dict[str, int]]:
    """Kanalwechsel je Funknetz seit dem letzten Lesen → Journal; dazu die Kanäle fürs Gedächtnis. Hat die Box zwei
    Funknetze auf einem Band (z. B. zweimal 5 GHz), heißt das zweite intern „5#2“."""
    neu = dict(alt)
    ereignisse = []
    gezaehlt: dict[str, int] = {}
    for b in baender:
        gezaehlt[b.band] = n = gezaehlt.get(b.band, 0) + 1
        if b.kanal is None:
            continue
        schluessel = b.band if n == 1 else f"{b.band}#{n}"
        vorher = alt.get(schluessel)
        if vorher is not None and vorher != b.kanal:
            ereignisse.append(
                Ereignis(
                    "wlan_kanal",
                    INFO,
                    t(
                        "WLAN {band} GHz: Kanal {vorher} → {kanal}",
                        sprache,
                        band=band_text(b.band, sprache),
                        vorher=vorher,
                        kanal=b.kanal,
                    ),
                )
            )
        neu[schluessel] = b.kanal
    return ereignisse, neu


def schnell_gesehen(alt: Iterable[str], w: Wlan, bekannt: Iterable[str] | None = None) -> list[str]:
    """Geräte, die schon auf 5 oder 6 GHz verbunden waren (für den Befund „hängt auf 2,4 GHz“). `bekannt`: MACs der
    Gerätetabelle – was die Box nicht mehr kennt (z. B. alte Zufallsadressen), fällt heraus."""
    behalten = set(bekannt) if bekannt is not None else None
    out = {m for m in alt if behalten is None or m in behalten}
    for g in w.geraete:
        if band_von(g, w.baender) in SCHNELL:
            out.add(g.mac)
    return sorted(out)


@dataclass(frozen=True)
class Befunde:
    schwach: tuple[str, ...]  # MAC
    auf_24: tuple[str, ...]  # MAC: jetzt auf 2,4 GHz, war schon auf 5 oder 6 GHz


def befunde(w: Wlan, schnell: Iterable[str], grenze: int) -> Befunde:
    """Geräte des Heimnetzes (ohne Gäste) mit schwachem Empfang und solche, die unnötig auf 2,4 GHz hängen."""
    schnell_ = set(schnell)
    hat_schnell = any(b.band in SCHNELL and b.an for b in w.baender)
    eigene = [g for g in w.geraete if not g.gast]
    return Befunde(
        schwach=tuple(g.mac for g in eigene if g.signal is not None and g.signal < grenze),
        auf_24=tuple(
            g.mac
            for g in eigene
            if hat_schnell and g.mac in schnell_ and band_von(g, w.baender) == "2,4"
        ),
    )


def lage_signal(v: int | None) -> float | None:
    """Empfang 0…100 % → 0…1 auf der Farbskala (bis 20 % rot, ab 70 % grün)."""
    return None if v is None else max(0.0, min(1.0, (v - 20) / 50))
