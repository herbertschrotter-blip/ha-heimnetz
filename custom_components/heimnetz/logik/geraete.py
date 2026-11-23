"""Gerätetabelle der FRITZ!Box: lesen und mit dem vorigen Abruf vergleichen."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from typing import Any

from .ereignis import INFO, WARNUNG, Ereignis
from .sprache import DE, merke, t
from .werte import text

ANSCHLUSS = {"Ethernet": "LAN", "802.11": "WLAN", "HomePlug": "Powerline"}
UNBEKANNT = "–"
OHNE_NAMEN = merke("Gerät ohne Namen")


@dataclass(frozen=True)
class Geraet:
    """Ein Gerät, wie die Box es kennt. `quelle`: Adressquelle (DHCP oder Static), "" = noch nicht gefragt."""

    mac: str
    ip: str
    aktiv: bool
    name: str
    art: str
    gast: bool = False
    vpn: bool = False
    gesperrt: bool = False
    wan: str = ""
    quelle: str = ""

    @property
    def kennung(self) -> str:
        """Name für Texte – ohne Hardware-Adresse (die Texte gehen an die Seite und ins Journal)."""
        return self.name


VPN_SCHLUESSEL = (
    "VPN:"  # Schlüssel statt MAC für Geräte im WireGuard-Tunnel (die Box nennt keine MAC)
)


def hostliste_zahlen(roh: str | bytes) -> dict[str, Any]:
    """Diagnose ohne Namen und Adressen: wie viele Einträge, mit/ohne MAC, mit VPN-Kennung, je Anschlussart.
    `vpn_ohne_ip`: VPN-Geräte ohne Tunnel-Adresse – ihr Schlüssel kommt dann aus dem Namen (siehe `aus_hostliste`)."""
    z: dict[str, Any] = {
        "eintraege": 0,
        "ohne_mac": 0,
        "vpn": 0,
        "vpn_aktiv": 0,
        "vpn_ohne_mac": 0,
        "vpn_ohne_ip": 0,
        "arten": {},
    }
    for item in ET.fromstring(roh):
        d = {c.tag: text(c.text) for c in item}
        vpn = d.get("X_AVM-DE_VPN") == "1"
        ohne = not d.get("MACAddress")
        z["eintraege"] += 1
        z["ohne_mac"] += ohne
        z["vpn"] += vpn
        z["vpn_aktiv"] += vpn and d.get("Active") == "1"
        z["vpn_ohne_mac"] += vpn and ohne
        z["vpn_ohne_ip"] += vpn and ohne and not d.get("IPAddress")
        art = d.get("InterfaceType") or "-"
        z["arten"][art] = z["arten"].get(art, 0) + 1
    return z


def aus_hostliste(roh: str | bytes) -> dict[str, Geraet]:
    """XML aus X_AVM-DE_GetHostListPath → {mac: Geraet}. Ein Gerät ohne Namen heißt OHNE_NAMEN – ein gemerkter Text:
    in Journal und Befunden übersetzt t() ihn mit, für die Seite `anzeigename`."""
    geraete = {}
    for item in ET.fromstring(roh):
        d = {c.tag: text(c.text) for c in item}
        mac = d.get("MACAddress", "").upper()
        vpn = d.get("X_AVM-DE_VPN") == "1"
        if not mac and vpn:
            # WireGuard hat keine MAC und die Hostliste sonst keine feste Kennung (Index wechselt, MAC-Liste leer):
            # Schlüssel aus der Tunnel-Adresse – sie steht fest in der WireGuard-Verbindung der Box –, ohne sie aus dem
            # Namen. Ob die Box die Adresse auch offline nennt, zählt die Diagnose (`vpn_ohne_ip`).
            mac = VPN_SCHLUESSEL + (
                d.get("IPAddress") or d.get("X_AVM-DE_FriendlyName") or d.get("HostName") or ""
            )
        if not mac or mac == VPN_SCHLUESSEL:
            continue
        art = d.get("InterfaceType", "")
        geraete[mac] = Geraet(
            mac=mac,
            ip=d.get("IPAddress", ""),
            aktiv=d.get("Active") == "1",
            name=d.get("X_AVM-DE_FriendlyName") or d.get("HostName") or OHNE_NAMEN,
            art=ANSCHLUSS.get(art, art or UNBEKANNT),
            gast=d.get("X_AVM-DE_Guest") == "1",
            vpn=vpn,
            gesperrt=d.get("X_AVM-DE_Disallow") == "1",
            wan=d.get("X_AVM-DE_WANAccess", ""),
        )
    return geraete


def anzeigename(name: str, sprache: str = DE) -> str:
    """Name eines Geräts zum Anzeigen: „Gerät ohne Namen“ in `sprache`, sonst der Name, wie er ist."""
    return t(OHNE_NAMEN, sprache) if name == OHNE_NAMEN else name


def ergaenzen(
    neu: dict[str, Geraet], alt: dict[str, Geraet], quellen: dict[str, str]
) -> dict[str, Geraet]:
    """Adressquelle eintragen; offline nennt die Box keinen Anschluss – dann den letzten bekannten behalten."""
    out = {}
    for mac, g in neu.items():
        art = g.art
        if art == UNBEKANNT and mac in alt and alt[mac].art != UNBEKANNT:
            art = alt[mac].art
        out[mac] = replace(g, art=art, quelle=quellen.get(mac, ""))
    return out


def zufallsadresse(mac: str) -> bool:
    """„Private WLAN-Adresse“ von Handy/Tablet: Bit „lokal verwaltet“ im ersten Byte."""
    try:
        return bool(int(mac[:2], 16) & 2)
    except ValueError:
        return False


def abgleich(alt: dict[str, Geraet], neu: dict[str, Geraet], sprache: str = DE) -> list[Ereignis]:
    """Änderungen zwischen zwei Abrufen: neues Gerät, IP-Wechsel, online/offline, Anschluss gewechselt."""
    out = []
    for mac, g in neu.items():
        a = alt.get(mac)
        if a is None:
            text_ = t(
                "Neues Gerät: {name}, IP {ip}, {art}",
                sprache,
                name=g.kennung,
                ip=g.ip or "–",
                art=g.art,
            )
            if zufallsadresse(mac):
                text_ += " – " + t(
                    "Zufalls-Adresse, evtl. ein bekanntes Handy/Tablet mit neuer „privater WLAN-Adresse“",
                    sprache,
                )
            out.append(Ereignis("neu", INFO, text_, mac))
            continue
        if a.ip and g.ip and a.ip != g.ip:
            out.append(
                Ereignis(
                    "ip_wechsel",
                    WARNUNG,
                    t(
                        "{name}: IP-Adresse gewechselt {alt} → {neu}",
                        sprache,
                        name=g.kennung,
                        alt=a.ip,
                        neu=g.ip,
                    ),
                    mac,
                )
            )
        if a.aktiv != g.aktiv:
            out.append(
                Ereignis(
                    "online" if g.aktiv else "offline",
                    INFO,
                    t(
                        "{name} ist wieder online ({ip}, {art})"
                        if g.aktiv
                        else "{name} ist offline ({ip}, {art})",
                        sprache,
                        name=g.kennung,
                        ip=g.ip or "–",
                        art=g.art,
                    ),
                    mac,
                )
            )
        if g.aktiv and a.aktiv and a.art != g.art:
            out.append(
                Ereignis(
                    "anschluss",
                    INFO,
                    t(
                        "{name}: Anschluss gewechselt {alt} → {neu}",
                        sprache,
                        name=g.kennung,
                        alt=a.art,
                        neu=g.art,
                    ),
                    mac,
                )
            )
    return out


# AN-0001: Geräteliste nach Verbindung. Das WLAN-Band kennt die Box nur bei verbundenen Geräten. Der Name einer
# Gruppe ist ihre feste Kennung (die Seite erkennt daran z. B. „WLAN, nicht verbunden“); angezeigt wird `text`.
NICHT_VERBUNDEN = merke("WLAN, nicht verbunden")
VPN = "🔐 VPN (WireGuard)"  # WU-0003: von unterwegs eingewählt (die Box meldet X_AVM-DE_VPN)
GRUPPEN = (
    VPN,
    "LAN",
    "WLAN 6 GHz",
    "WLAN 5 GHz",
    "WLAN 2,4 GHz",
    "WLAN",
    NICHT_VERBUNDEN,
    "Powerline",
    merke("Sonstige"),
)


def verbindung(art: str, aktiv: bool, band: str | None, vpn: bool = False) -> str:
    """Gruppe eines Geräts: VPN, LAN, WLAN mit Band (2,4, 5 oder 6 GHz), WLAN ohne bekanntes Band, nicht verbunden …"""
    if vpn:
        return VPN
    art = art.split(" ")[0]
    if art in ("LAN", "Powerline"):
        return art
    if art == "WLAN":
        if not aktiv:
            return NICHT_VERBUNDEN
        return f"WLAN {band} GHz" if band else "WLAN"
    return "Sonstige"


def gruppen_text(name: str, sprache: str = DE) -> str:
    """Anzeige einer Gruppe: „WLAN 2,4 GHz“ (Englisch „WLAN 2.4 GHz“), „Sonstige“ …"""
    text_ = t(name, sprache)
    return text_ if sprache == DE else text_.replace("2,4", "2.4")


def gruppen(eintraege: list[tuple[str, bool]], sprache: str = DE) -> list[dict[str, object]]:
    """(Gruppe, online) je Gerät → Gruppen in fester Reihenfolge mit Text und „online von gesamt“, leere weggelassen."""
    out = []
    unbekannt = [g for g, _ in eintraege if g not in GRUPPEN]  # nie ein Gerät still verlieren
    for name in (*GRUPPEN, *dict.fromkeys(unbekannt)):
        drin = [online for g, online in eintraege if g == name]
        if drin:
            out.append(
                {
                    "name": name,
                    "text": gruppen_text(name, sprache),
                    "online": sum(drin),
                    "gesamt": len(drin),
                }
            )
    return out
