"""Befunde aus dem aktuellen Stand: Adress-Probleme im Heimnetz, fremde DHCP-Server, Internet vom Pi aus.

Übernommen aus dem Altbestand (`netzdiagnose/fritz_diag.py`, find_problems), dazu der Befund „kein Internet“.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field

from .ereignis import INFO, KRITISCH, STUFEN, WARNUNG, Ereignis
from .geraete import Geraet
from .sprache import DE, merke, t
from .werte import kurz

# Gesamtstand
OK = "ok"
BOX_FEHLT = "box_fehlt"
GESAMTSTAENDE = (OK, WARNUNG, KRITISCH, BOX_FEHLT)


@dataclass(frozen=True)
class Heimnetz:
    """LAN-Einstellungen der Box (LANHostConfigManagement GetInfo)."""

    router: str = ""
    maske: str = ""
    dhcp_von: str = ""
    dhcp_bis: str = ""
    dhcp_an: bool | None = None
    dns: str = ""


@dataclass(frozen=True)
class Angebot:
    """Antwort eines DHCP-Servers auf die Test-Anfrage."""

    server: str
    angebot: str
    router: str = ""
    maske: str = ""
    dns: str = ""
    mac: str = ""


@dataclass(frozen=True)
class DhcpTest:
    """Ergebnis des DHCP-Tests. ok = Test lief (auch ohne Antwort); fehler = warum er nicht lief."""

    ok: bool = False
    server: tuple[Angebot, ...] = ()
    fehler: str = ""


@dataclass(frozen=True)
class PiVerbindung:
    """Was der Pi selbst erreicht. gw_mac_alt = bisher bekannte Hardware-Adresse der Box."""

    box: bool
    internet: bool
    dns: bool
    gw_mac: str = ""
    gw_mac_alt: str = ""


@dataclass(frozen=True)
class Befund:
    key: str
    stufe: str
    titel: str
    text: str = field(compare=False)


def _netz(
    lan: Heimnetz,
) -> tuple[
    ipaddress.IPv4Network | ipaddress.IPv6Network | None,
    ipaddress.IPv4Address | ipaddress.IPv6Address | None,
    ipaddress.IPv4Address | ipaddress.IPv6Address | None,
]:
    try:
        netz = ipaddress.ip_network(f"{lan.router}/{lan.maske}", strict=False)
    except ValueError:
        return None, None, None
    try:
        return netz, ipaddress.ip_address(lan.dhcp_von), ipaddress.ip_address(lan.dhcp_bis)
    except ValueError:
        return netz, None, None


def _im_bereich(
    adresse: ipaddress.IPv4Address | ipaddress.IPv6Address,
    von: ipaddress.IPv4Address | ipaddress.IPv6Address | None,
    bis: ipaddress.IPv4Address | ipaddress.IPv6Address | None,
) -> bool:
    if von is None or bis is None or not adresse.version == von.version == bis.version:
        return False
    return int(von) <= int(adresse) <= int(bis)


# AN-0003: was gerade los ist, wenn das Internet fehlt (Lage aus logik/stoerung.lage)
KEIN_INTERNET = {
    "box": merke("Auch die FRITZ!Box antwortet dem Pi nicht – Heimnetz oder Box prüfen."),
    "neu": merke("Die FRITZ!Box ist erreichbar und wählt sich gerade neu ins Mobilfunknetz ein."),
    "schwach": merke(
        "Die FRITZ!Box ist erreichbar, der Mobilfunk-Empfang ist aber schwach – vermutlich die Funkstrecke."
    ),
    "steht": merke(
        "Die FRITZ!Box ist erreichbar und die Mobilfunk-Verbindung steht (keine Neueinwahl, Empfang "
        "ausreichend) – der Weg ins Internet hakt vermutlich beim Anbieter. Meist ist das nach wenigen Minuten vorbei."
    ),
}
KEIN_INTERNET_SONST = merke("Die FRITZ!Box ist erreichbar, aber der Weg ins Internet nicht.")


def finden(
    geraete: dict[str, Geraet],
    lan: Heimnetz,
    dhcp: DhcpTest | None,
    pi: PiVerbindung,
    lage: str | None = None,
    sprache: str = DE,
) -> list[Befund]:
    """Alle Befunde, schwerste zuerst, Texte in `sprache`."""
    out: list[Befund] = []

    def dazu(key: str, stufe: str, titel: str, text: str) -> None:
        out.append(Befund(key, stufe, titel, kurz(text, 400)))

    def tr(text: str, /, **werte: object) -> str:
        return t(text, sprache, **werte)

    if not pi.internet:
        if not pi.box:
            lage = "box"
        dazu(
            "kein_internet",
            KRITISCH,
            tr("Keine Internetverbindung"),
            tr(KEIN_INTERNET.get(lage or "", KEIN_INTERNET_SONST)),
        )

    netz, von, bis = _netz(lan)
    je_ip: dict[str, list[Geraet]] = {}
    for g in geraete.values():
        if g.ip and not g.vpn:
            je_ip.setdefault(g.ip, []).append(g)
    for ip, gruppe in sorted(je_ip.items()):
        if len(gruppe) < 2:
            continue
        aktiv = [g for g in gruppe if g.aktiv]
        namen = ", ".join(f"{g.kennung} – {'online' if g.aktiv else 'offline'}" for g in gruppe)
        if len(aktiv) >= 2:
            dazu(
                f"doppelt:{ip}",
                KRITISCH,
                tr("IP-Adresse {ip} doppelt in Benutzung", ip=ip),
                tr(
                    "Zwei Geräte sind gleichzeitig mit derselben Adresse online: {namen}. "
                    "Beide verlieren abwechselnd die Verbindung.",
                    namen=namen,
                ),
            )
        elif aktiv:
            dazu(
                f"doppelt:{ip}",
                WARNUNG,
                tr("IP-Adresse {ip} doppelt vergeben", ip=ip),
                tr(
                    "Die Box führt mehrere Geräte unter dieser Adresse: {namen}. "
                    "Kommt das zweite Gerät zurück, gibt es einen Konflikt.",
                    namen=namen,
                ),
            )

    for g in geraete.values():
        if not g.ip or g.vpn or g.gast:
            continue
        try:
            adresse = ipaddress.ip_address(g.ip)
        except ValueError:
            continue
        if g.aktiv and netz is not None and adresse not in netz:
            grund = (
                tr(
                    "Adresse 169.254.x.x heißt: das Gerät hat vom DHCP-Server keine Antwort bekommen."
                )
                if adresse.is_link_local
                else tr(
                    "Das Gerät hat seine Adresse nicht von der FRITZ!Box bekommen – entweder fest falsch "
                    "eingestellt oder ein zweiter DHCP-Server (anderer Router, Repeater im Router-Modus) verteilt "
                    "Adressen."
                )
            )
            dazu(
                f"fremdnetz:{g.mac}",
                KRITISCH,
                tr("{name} hat eine Adresse außerhalb des Heimnetzes", name=g.name),
                tr(
                    "{name} hat {ip}, das Heimnetz ist {netz}. {grund}",
                    name=g.kennung,
                    ip=g.ip,
                    netz=netz,
                    grund=grund,
                ),
            )
        if g.quelle == "Static" and _im_bereich(adresse, von, bis):
            dazu(
                f"fest_im_dhcp:{g.mac}",
                WARNUNG,
                tr("{name}: feste IP im DHCP-Bereich", name=g.name),
                tr(
                    "{name} hat {ip} fest im Gerät eingestellt, die Box verteilt aber {von}–{bis} automatisch. "
                    "Ist das Gerät aus, kann die Box die Adresse einem anderen Gerät geben → Konflikt beim "
                    "Wiederkommen. Abhilfe: im Gerät auf automatisch (DHCP) stellen und in der Box „immer dieselbe "
                    "IP-Adresse zuweisen“ anhaken, oder eine Adresse außerhalb des Bereichs nehmen.",
                    name=g.kennung,
                    ip=g.ip,
                    von=lan.dhcp_von,
                    bis=lan.dhcp_bis,
                ),
            )
        if g.aktiv and (g.gesperrt or g.wan == "denied"):
            dazu(
                f"gesperrt:{g.mac}",
                WARNUNG,
                tr("{name}: Internet durch die FRITZ!Box gesperrt", name=g.name),
                tr(
                    "{name} ist online, aber ein Zugangsprofil (Kindersicherung/Zeitbudget/Sperre) lässt es "
                    "nicht ins Internet.",
                    name=g.kennung,
                ),
            )

    if lan.dhcp_an is False:
        dazu(
            "dhcp_aus",
            INFO,
            tr("DHCP-Server der FRITZ!Box ist ausgeschaltet"),
            tr(
                "Die Box verteilt keine Adressen. Das ist nur richtig, wenn ein anderes Gerät diese Aufgabe "
                "bewusst übernimmt."
            ),
        )

    if dhcp is not None and dhcp.ok:
        fremd = [s for s in dhcp.server if s.server != lan.router] if lan.router else []
        if fremd:
            liste = "; ".join(
                tr(
                    "{server} bietet {angebot} an, Router {router}",
                    server=s.server + (f" [{s.mac}]" if s.mac else ""),
                    angebot=s.angebot,
                    router=s.router or "?",
                )
                for s in fremd
            )
            dazu(
                "dhcp_fremd:" + ",".join(sorted(s.server for s in fremd)),
                KRITISCH,
                tr("Zweiter DHCP-Server im Netz"),
                tr(
                    "Auf die Test-Anfrage antwortet nicht nur die FRITZ!Box: {liste}. Geräte, die ihre Adresse "
                    "von dort bekommen, haben einen falschen Weg ins Internet – genau das Bild „manche Geräte "
                    "gehen, manche nicht“.",
                    liste=liste,
                ),
            )
        elif not dhcp.server:
            dazu(
                "dhcp_stumm",
                WARNUNG,
                tr("Kein DHCP-Server hat geantwortet"),
                tr(
                    "Auf die Test-Anfrage kam keine Antwort. Geräte, die sich neu verbinden, bekommen dann "
                    "keine Adresse."
                ),
            )

    if pi.gw_mac and pi.gw_mac_alt and pi.gw_mac != pi.gw_mac_alt:
        dazu(
            f"gw_mac:{pi.gw_mac}",
            KRITISCH,
            tr("Hardware-Adresse der FRITZ!Box hat gewechselt"),
            tr(
                "Unter {adresse} meldet sich ein anderes Gerät als bisher. Ein anderes Gerät benutzt vermutlich "
                "die Adresse der Box.",
                adresse=lan.router or tr("der Adresse der Box"),
            ),
        )

    return sorted(out, key=lambda b: STUFEN.index(b.stufe))


def gesamtstand(befunde: list[Befund], box_erreichbar: bool) -> str:
    """ok, warnung, kritisch oder box_fehlt (die Box antwortet nicht – dann ist fast nichts prüfbar)."""
    if not box_erreichbar:
        return BOX_FEHLT
    stufen = {b.stufe for b in befunde}
    if KRITISCH in stufen:
        return KRITISCH
    return WARNUNG if WARNUNG in stufen else OK


def abgleich(
    alt: dict[str, str], befunde: list[Befund], sprache: str = DE
) -> tuple[list[Ereignis], dict[str, str]]:
    """Neue und erledigte Befunde als Journalzeilen; dazu die Schlüssel für den nächsten Abgleich. Ein erledigter
    Befund trägt den Titel, unter dem er gemerkt wurde (auch nach einem Wechsel der Sprache)."""
    neu = {b.key: b.titel for b in befunde}
    ereignisse = [
        Ereignis(
            "befund", b.stufe, t("Befund: {titel} – {text}", sprache, titel=b.titel, text=b.text)
        )
        for b in befunde
        if b.key not in alt
    ]
    ereignisse += [
        Ereignis("befund_weg", INFO, t("Befund erledigt: {titel}", sprache, titel=titel))
        for k, titel in alt.items()
        if k not in neu
    ]
    return ereignisse, neu


def dhcp_pruefung(dhcp: DhcpTest | None, router: str, sprache: str = DE) -> tuple[bool | None, str]:
    """Für die Prüfungsliste: in Ordnung nur, wenn genau die Box antwortet. None = nicht gelaufen."""
    if dhcp is None:
        return None, t("noch nicht gelaufen", sprache)
    if not dhcp.ok:
        return None, dhcp.fehler or t("nicht möglich", sprache)
    n = len(dhcp.server)
    text = (
        t("kein Server antwortet", sprache)
        if n == 0
        else t("{n} Server antwortet", sprache, n=n)
        if n == 1
        else t("{n} Server antworten", sprache, n=n)
    )
    return n == 1 and dhcp.server[0].server == router, text
