"""Mobilfunk der Box (X_AVM-DE_WANMobileConnection GetInfoEx): Technik und Empfang je Funkzelle.

Seriennummer und IMSI der Antwort werden bewusst nicht übernommen.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .ereignis import INFO, WARNUNG, Ereignis
from .sprache import DE, merke, t, zahl
from .werte import ganzzahl, ja, text


@dataclass(frozen=True)
class Zelle:
    rolle: str
    art: str
    anbieter: str
    pci: int | None
    zelle: str
    rsrp: int | None
    rsrq: int | None
    entfernung_m: int | None = None  # Distance; 0 = die Box kennt sie nicht
    plmn: str = ""  # Netzkennung, z. B. „23205“ (MCC 232, MNC 05)
    tac: str = ""  # Tracking Area Code, hexadezimal
    # WU-0009: nur von einem vorgeschalteten Modem – die Box meldet beides über TR-064 nicht
    sinr: float | None = None  # Signal zu Störung und Rauschen in dB
    band: str = ""  # „B3“, „n78“


@dataclass(frozen=True)
class Mobilfunk:
    """haupt = verbundene Hauptzelle (bei 5G-NSA die LTE-Ankerzelle), nr = erste 5G-Zelle."""

    technik: str
    roaming: bool
    haupt: Zelle | None
    nr: Zelle | None
    antennen: tuple[int | None, int | None] = (None, None)  # SignalRSRP0/1 in dBm (Hauptverbindung)
    laufzeit_s: int | None = None  # Uptime: seit wann die Mobilfunkverbindung steht
    zellen: tuple[Zelle, ...] = ()  # alle Zellen der Zellliste, in der Reihenfolge der Box

    @property
    def zellkennung(self) -> str:
        return f"{self.haupt.zelle}/{self.haupt.pci}" if self.haupt else ""


def aus_antwort(info: Mapping[str, Any]) -> Mobilfunk:
    zellen: list[Zelle] = []
    try:
        for c in ET.fromstring(text(info.get("NewCellList")) or "<CellList/>"):
            d = {x.tag.lower(): text(x.text) for x in c}
            art = d.get("celltype", "")
            zellen.append(
                Zelle(
                    rolle=d.get("connected", ""),
                    art={"lte": "LTE", "nr5g": "5G"}.get(art, art),
                    anbieter=d.get("provider", ""),
                    pci=ganzzahl(d.get("physicalid")),
                    zelle=d.get("cellid", ""),
                    rsrp=ganzzahl(d.get("rsrp")),
                    rsrq=ganzzahl(d.get("rsrq")),
                    entfernung_m=ganzzahl(d.get("distance")) or None,
                    plmn=d.get("plmn", ""),
                    tac=d.get("tac", ""),
                )
            )
    except ET.ParseError:
        pass
    haupt = next((z for z in zellen if z.rolle == "primary"), zellen[0] if zellen else None)
    return Mobilfunk(
        technik=text(info.get("NewCurrentAccessTechnology")),
        roaming=ja(info.get("NewRoaming")),
        haupt=haupt,
        nr=next((z for z in zellen if z.art == "5G"), None),
        antennen=(_dbm(info.get("NewSignalRSRP0")), _dbm(info.get("NewSignalRSRP1"))),
        laufzeit_s=ganzzahl(info.get("NewUptime")),
        zellen=tuple(zellen),
    )


def _dbm(wert: Any) -> int | None:
    """RSRP der Antenne; 0 ist die Vorgabe der Box für „kein Wert“."""
    v = ganzzahl(wert)
    return v if v else None


def neu_eingewaehlt(alt_s: int | None, neu: Mobilfunk, sprache: str = DE) -> Ereignis | None:
    """Die Verbindungsdauer ist kleiner als beim letzten Abruf: die Box hat sich neu eingewählt. Das zählt auch nach einem
    Neustart der Box – das Internet war dann ebenfalls weg."""
    if alt_s is None or neu.laufzeit_s is None or neu.laufzeit_s >= alt_s:
        return None
    return Ereignis(
        "mobil_neu",
        WARNUNG,
        t(
            "Mobilfunk neu eingewählt (die Verbindung davor lief {dauer})",
            sprache,
            dauer=dauer(alt_s, sprache),
        ),
    )


def dauer(s: int, sprache: str = DE) -> str:
    """Sekunden lesbar: „3 Tage 4 h“, „5 h 12 min“, „7 min“."""
    tage, rest = divmod(max(0, s), 86_400)
    h, rest = divmod(rest, 3600)
    m = rest // 60
    if tage:
        return t("{n} Tag {h} h" if tage == 1 else "{n} Tage {h} h", sprache, n=tage, h=h)
    return f"{h} h {m} min" if h else f"{m} min"


def baender(info: Mapping[str, Any], sprache: str = DE) -> str:
    """GetEnabledBandCapabilities → „LTE 1, 3, 20 · 5G n78“; „0“ heißt automatisch (alle Bänder des Moduls)."""

    def liste(wert: Any, vor: str) -> str:
        roh = text(wert)
        if not roh or roh == "unknown":
            return ""
        if roh == "0":
            return t("automatisch", sprache)
        return ", ".join(f"{vor}{b.strip().lstrip('nNbB')}" for b in roh.split(",") if b.strip())

    teile = []
    if lte := liste(info.get("NewBandCapabilitiesLTE"), ""):
        teile.append(f"LTE {lte}")
    nr = liste(info.get("NewBandCapabilities5GNSA"), "n") or liste(
        info.get("NewBandCapabilities5GSA"), "n"
    )
    if nr:
        teile.append(f"5G {nr}")
    return " · ".join(teile)


# Rolle einer Zelle: Kennung (für die Seite, z. B. „4G-Anker“ als Titel) → Text
ROLLEN = {
    "anker": merke("Anker"),
    "verbunden": merke("verbunden"),
    "dazu": merke("bündelt dazu"),
    "reichweite": merke("in Reichweite"),
}


def rolle_art(z: Zelle, technik: str) -> str:
    """„anker“ trägt die Verbindung (bei reinem LTE/5G-SA „verbunden“), „dazu“ = zusätzliche Zelle (Carrier
    Aggregation bzw. 5G bei NSA); was die Box sonst listet, ist nur in Reichweite („reichweite“)."""
    if z.rolle == "primary":
        return "verbunden" if not technik.endswith("NSA") else "anker"
    return "dazu" if z.rolle == "secondary" else "reichweite"


def rolle(z: Zelle, technik: str, sprache: str = DE) -> str:
    """Rolle als Text: „Anker“, „verbunden“, „bündelt dazu“, „in Reichweite“."""
    return t(ROLLEN[rolle_art(z, technik)], sprache)


def zellen_sortiert(m: Mobilfunk) -> list[Zelle]:
    """Erst 5G, dann die Ankerzelle, dann die übrigen in der Reihenfolge der Box (wie die Übersicht der Box)."""
    return sorted(m.zellen, key=lambda z: (z.art != "5G", z.rolle != "primary"))


def entfernung(m: int | None, sprache: str = DE) -> str | None:
    """Entfernung zur Basisstation: „850 m“, „1,2 km“ (Englisch „1.2 km“)."""
    if not m:
        return None
    return f"{m} m" if m < 1000 else f"{zahl(m / 1000, 1, sprache)} km"


def stufen(v: float | None) -> int:
    """Signalstärke als Balken 0…4 wie an der Box, Grenzen wie `wort_rsrp`; 0 = kein Wert."""
    if v is None:
        return 0
    return 4 if v >= -85 else 3 if v >= -95 else 2 if v >= -105 else 1


def abgleich(alt_technik: str, alt_zelle: str, neu: Mobilfunk, sprache: str = DE) -> list[Ereignis]:
    """Wechsel von Technik oder Funkzelle; der Wechsel weg von 5G ist eine Warnung."""
    out = []
    if alt_technik and neu.technik and alt_technik != neu.technik:
        weg_von_5g = alt_technik.startswith("5G") and not neu.technik.startswith("5G")
        out.append(
            Ereignis(
                "mobil_technik",
                WARNUNG if weg_von_5g else INFO,
                t(
                    "Mobilfunk: Technik gewechselt {alt} → {neu}",
                    sprache,
                    alt=alt_technik,
                    neu=neu.technik,
                ),
            )
        )
    if alt_zelle and neu.haupt and alt_zelle != neu.zellkennung:
        out.append(
            Ereignis(
                "mobil_zelle",
                INFO,
                # das Muster liest kontext.ZELLWECHSEL beim Nachtragen wieder aus dem Journal
                t(
                    "Mobilfunk: Funkzelle gewechselt {alt} → {neu} (Empfang RSRP {rsrp} dBm)",
                    sprache,
                    alt=alt_zelle,
                    neu=neu.zellkennung,
                    rsrp=neu.haupt.rsrp,
                ),
            )
        )
    return out


# Einstufung (übliche Richtwerte für LTE/5G, wie die Mobilfunk-Karte des Altbestands)
def lage_rsrp(v: float | None) -> float | None:
    """Signalstärke −120 … −80 dBm → 0 … 1."""
    return None if v is None else max(0.0, min(1.0, (v + 120) / 40))


def lage_rsrq(v: float | None) -> float | None:
    """Signalqualität −20 … −8 dB → 0 … 1."""
    return None if v is None else max(0.0, min(1.0, (v + 20) / 12))


def wort_rsrp(v: float, sprache: str = DE) -> str:
    return t(
        "sehr gut"
        if v >= -85
        else "gut"
        if v >= -95
        else "mittel"
        if v >= -105
        else "schwach"
        if v >= -115
        else "sehr schwach",
        sprache,
    )


def wort_rsrq(v: float, sprache: str = DE) -> str:
    return t(
        "gut" if v >= -10 else "mittel" if v >= -15 else "schwach" if v >= -20 else "sehr schwach",
        sprache,
    )


@dataclass(frozen=True)
class Befund:
    lage: float | None
    titel: str
    text: str


def befund(
    technik: str,
    anker: int | None,
    nr: int | None,
    download: float | None,
    tarif: float | None,
    sprache: str = DE,
) -> Befund:
    """Befund in einem Satz aus Empfang (dBm), typischem Download der letzten 7 Tage und Tarif (aus dem Altbestand)."""

    def tr(text: str, /, **werte: object) -> str:
        return t(text, sprache, **werte)

    werte_ = [v for v in (anker, nr) if v is not None]
    if not werte_:
        return Befund(
            None,
            tr("Noch keine Empfangswerte"),
            tr("Die FRITZ!Box hat noch keine Werte geliefert."),
        )
    schwaechste = min(werte_)
    anteil = round(download / tarif * 100) if download is not None and tarif else None
    tempo = (
        ""
        if download is None
        else " "
        + (
            tr(
                "Der Download der letzten 7 Tage liegt typisch bei {mbit} Mbit/s.",
                mbit=zahl(download, 1, sprache),
            )
            if anteil is None
            else tr(
                "Der Download der letzten 7 Tage liegt typisch bei {mbit} Mbit/s = {anteil} % vom Tarif.",
                mbit=zahl(download, 1, sprache),
                anteil=anteil,
            )
        )
    )
    nur4g = (
        " " + tr("Im Moment läuft die Verbindung nur über {technik}.", technik=technik)
        if technik and not technik.startswith("5G")
        else ""
    )
    if anker is not None and nr is not None:
        werte = tr("Signalstärke {anker} dBm (4G-Anker) und {nr} dBm (5G).", anker=anker, nr=nr)
    elif anker is not None:
        werte = tr("Signalstärke {anker} dBm (4G-Anker).", anker=anker)
    else:
        werte = tr("Signalstärke {nr} dBm (5G).", nr=nr)
    if schwaechste < -105:
        return Befund(
            lage_rsrp(schwaechste),
            tr("Empfang schwach – zuerst den Standort der Box verbessern"),
            f"{werte}{tempo}{nur4g} "
            + tr(
                "Bei so schwachem Empfang bremst vor allem die Funkstrecke: Box ans Fenster Richtung Sender, "
                "höher stellen oder außen montieren. Erst wenn der Empfang besser ist, sagt die Geschwindigkeit "
                "etwas über den Anbieter."
            ),
        )
    if schwaechste < -95:
        return Befund(
            lage_rsrp(schwaechste),
            tr("Empfang mittelmäßig – Standort der Box lohnt einen Versuch"),
            f"{werte}{tempo}{nur4g} "
            + tr(
                "Bei mittlerem Empfang kann beides bremsen: die Funkstrecke und eine volle Zelle. Test: die Box "
                "an ein anderes Fenster oder höher stellen – steigt die Signalstärke um etwa 10 dBm und der "
                "Download nicht, liegt es an der Zelle (Anbieter)."
            ),
        )
    if anteil is not None and anteil < 60:
        return Befund(
            0.35,
            tr(
                "Empfang gut, Geschwindigkeit trotzdem niedrig – spricht für eine ausgelastete Zelle"
            ),
            f"{werte}{tempo}{nur4g} "
            + tr(
                "An der Funkstrecke liegt es kaum. Das ist Sache des Anbieters – dafür lohnt die zertifizierte "
                "Messung (RTR-Netztest) in den schlechten Stunden aus dem Wochen-Raster."
            ),
        )
    return Befund(lage_rsrp(schwaechste), tr("Empfang gut"), f"{werte}{tempo}{nur4g}")


def schwaechster(m: Mobilfunk | None) -> int | None:
    """Schwächste Signalstärke von Anker- und 5G-Zelle (entscheidet über den Befund)."""
    if m is None:
        return None
    werte = [z.rsrp for z in (m.haupt, m.nr) if z is not None and z.rsrp is not None]
    return min(werte) if werte else None
