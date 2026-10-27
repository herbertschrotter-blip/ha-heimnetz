"""Öffentlich auf GitHub melden (WU-0006, Mockup netzwerk.html · githubMelden, abgenommen 25.10.2026).

Aus einem Ticket des Melden-Knopfs wird ein vorausgefülltes Issue: Titel `[Art] Text…`, Text der Meldung und ein
grober Stand (Version von Heimnetz und Home Assistant, Reiter und Gerät, Box-Modell und FRITZ!OS, Netztechnik, Ookla
ja/nein, lokale Ticketnummer). Zell- und Signaldaten nur, wenn der Nutzer es einschaltet – daraus lässt sich der
Wohnort eingrenzen. Nie dabei: Gerätenamen, Hardware-Adressen, IP-Adressen, Standort von Home Assistant, Kennwörter.
Was der Nutzer selbst schreibt, wird darauf geprüft und geschwärzt (`schwaerzen`), bevor es in die Vorschau geht –
auch Zellkennungen, TAC und PCI, die er selbst in den Text schreibt.

Abgeschickt wird auf GitHub mit dem eigenen Konto; die Integration hat keinen Token. Der Link
`…/issues/new?title=…&body=…` bleibt unter URL_MAX Zeichen (Grenze der Browser und von GitHub), sonst wird der Text
der Meldung gekürzt – der ganze Text steht im lokalen Ticket.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from urllib.parse import quote

from . import mobil as mb
from .sprache import DE, t
from .tickets import art_text

URL_MAX = 7000  # ganzer Link; GitHub und Browser schneiden längere ab
TITEL_TEXT_MAX = 60  # Zeichen der Meldung im Titel
NAME_MIN = 3  # kürzere Gerätenamen („TV“) würden in jedem Satz Wörter schwärzen

_MAC = re.compile(
    r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])"
)
_IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
_IPV6 = re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![\w:])")
# Koordinaten: zwei Zahlen mit mindestens vier Nachkommastellen nebeneinander („47.0707, 15.4395“, „47,0707; 15,4395“)
_ORT = re.compile(
    r"-?\d{1,3}\.\d{4,}\s*[,;/ ]\s*-?\d{1,3}\.\d{4,}|-?\d{1,3},\d{4,}\s*[;/ ]\s*-?\d{1,3},\d{4,}"
)
# Koordinaten als einzelne Werte mit Schlüssel, etwa in Kartenlinks („?mlat=47.07071&mlon=15.43952“, „lat: 47.0707“)
_ORT_WERT = re.compile(r"(?i)\b(m?lat|m?lon|lng|latitude|longitude)(\s*[=:]\s*)-?\d{1,3}\.\d{3,}")
# Zellkennung, wie die Box sie zeigt: Sendeanlage (eNodeB, hex) und Sektor („4f2a1-17“); dazu Werte hinter TAC, PCI,
# ECI, NCI, eNB, Cell-ID – daraus lässt sich der Wohnort eingrenzen, auch wenn der Nutzer sie selbst in den Text schreibt.
# Bis 16 Stellen (ECI/NCI dezimal sind 9–11 Stellen, FE-0006); mindestens eine Ziffer, damit „PCI face“ stehen bleibt
_ZELLE = re.compile(r"(?<![0-9A-Za-z])[0-9A-Fa-f]{5,6}-[0-9A-Fa-f]{2}(?![0-9A-Za-z])")
_ZELL_WERT = re.compile(
    r"(?i)\b(tac|pci|eci|nci|enb|enodeb|gnb|cell[-_ ]?id|cid)(\s*[:=]?\s*)(?:0x)?(?=[0-9a-f]*\d)[0-9a-f]{1,16}(?![0-9A-Za-z])"
)
# Gerät zur Meldung: nur die Werte, die die eigene Seite schickt (Handy/Phone, Desktop) – alles andere fällt weg
GERAETE = ("Handy", "Phone", "Desktop")
# Kennwörter: „Kennwort: …“, „pw=…“, „Passwort lautet …“ – geschwärzt bis zum Zeilenende, Komma oder Semikolon
# (lieber zu viel; die Vorschau zeigt es). „ist/lautet“ nur bei eindeutigen Wörtern – „der Schlüssel ist eingetragen“
# bleibt stehen.
_KENNWORT = re.compile(
    r"(?i)\b(passwort|kennwort|password|passwd|pw|pin|token|api[-_ ]?key|schlüssel|key)(\s*[:=]\s*)[^\n,;]+"
    r"|\b(passwort|kennwort|password|passwd)(\s+(?:ist|is|lautet)\b\s*[:=]?\s*)[^\n,;]+"
)


@dataclass(frozen=True)
class Umgebung:
    """Grober Stand fürs Issue; leere Werte fallen weg."""

    heimnetz: str
    ha: str
    kontext: str = ""  # Reiter (und Dialog) zur Meldung
    geraet: str = ""  # Handy / Desktop
    box_modell: str = ""
    box_firmware: str = ""
    netz: str = ""  # Netztechnik der Box, z. B. „LTE“, „5G-NSA“
    ookla: bool | None = None  # Ookla Speedtest eingerichtet? None = unbekannt
    ticket: str = ""  # lokale Ticketnummer


@dataclass(frozen=True)
class Zelldaten:
    kennung: str
    pci: int | None
    tac: str
    plmn: str
    rsrp: int | None
    rsrq: int | None
    nr_rsrp: int | None  # 5G (NR); None = keine 5G-Zelle
    entfernung: str | None


def zelldaten(m: mb.Mobilfunk | None, sprache: str = DE) -> Zelldaten | None:
    """Ankerzelle mit Signal und Entfernung; None ohne Mobilfunk oder Ankerzelle."""
    if m is None or m.haupt is None:
        return None
    z = m.haupt
    return Zelldaten(
        kennung=z.zelle,
        pci=z.pci,
        tac=z.tac.upper(),
        plmn=z.plmn,
        rsrp=z.rsrp,
        rsrq=z.rsrq,
        nr_rsrp=m.nr.rsrp if m.nr else None,
        entfernung=mb.entfernung(z.entfernung_m, sprache),
    )


def _ipv6(m: re.Match[str]) -> bool:
    # Uhrzeiten (14:05:33) haben zwei Doppelpunkte, eine IPv6-Adresse „::“ oder mindestens fünf
    s = m.group(0)
    return any(c not in ":" for c in s) and ("::" in s or s.count(":") >= 5)


def zell_kennungen(m: mb.Mobilfunk | None) -> list[str]:
    """Kennungen der Zellen, die die Box gerade sieht (Zelle, Sendeanlage, TAC) – zum Schwärzen wie Gerätenamen."""
    if m is None:
        return []
    kennungen = []
    for z in (m.haupt, m.nr, *m.zellen):
        if z is not None:
            kennungen += [z.zelle, z.zelle.split("-", 1)[0], z.tac]
    return [k for k in dict.fromkeys(kennungen) if k]


def schwaerzen(text: str, namen: Iterable[str] = (), sprache: str = DE) -> str:
    """Hardware- und IP-Adressen, Koordinaten, Zellkennungen (auch TAC/PCI …), Kennwörter („Kennwort: …“) und
    bekannte Namen (Geräte, Kennungen der aktuellen Zellen: `zell_kennungen`) ersetzen."""
    weg = t("[entfernt]", sprache)
    text = _MAC.sub(weg, text)
    text = _IPV4.sub(weg, text)  # vor IPv6: in „::ffff:192.0.2.1“ zuerst den IPv4-Teil
    text = _IPV6.sub(lambda m: weg if _ipv6(m) else m.group(0), text)
    text = _ORT.sub(weg, text)
    text = _ORT_WERT.sub(lambda m: m.group(1) + m.group(2) + weg, text)
    text = _ZELLE.sub(weg, text)
    text = _ZELL_WERT.sub(lambda m: m.group(1) + m.group(2) + weg, text)
    text = _KENNWORT.sub(
        lambda m: (m.group(1) or m.group(3)) + (m.group(2) or m.group(4)) + weg, text
    )
    # längere Namen zuerst („Wohnzimmer TV“ vor „Wohnzimmer“)
    for name in sorted(
        {n.strip() for n in namen if len(n.strip()) >= NAME_MIN}, key=len, reverse=True
    ):
        text = re.sub(rf"(?<!\w){re.escape(name)}(?!\w)", weg, text, flags=re.IGNORECASE)
    return text


def titel(art: str, text: str, sprache: str = DE) -> str:
    """„[Fehler] Die Karte zum Mast bleibt grau, obwohl der Schlüssel …“ – erste Zeile, gekürzt am Wort."""
    zeile = " ".join(text.strip().splitlines()[0].split()) if text.strip() else ""
    if len(zeile) > TITEL_TEXT_MAX:
        kurz = zeile[:TITEL_TEXT_MAX]
        zeile = (kurz.rsplit(" ", 1)[0] if " " in kurz else kurz) + " …"
    return f"[{art_text(art, sprache)}] {zeile}".strip()


def _zeile(*teile: str | None, trenner: str = " · ") -> str:
    return trenner.join(x for x in teile if x)


def _umgebung(u: Umgebung, sprache: str) -> list[str]:
    ookla = None if u.ookla is None else t("ja" if u.ookla else "nein", sprache)
    box = _zeile(u.box_modell or None, f"FRITZ!OS {u.box_firmware}" if u.box_firmware else None)
    netz = _zeile(
        t("Netz: {technik}", sprache, technik=u.netz) if u.netz else None,
        t("Ookla Speedtest: {wert}", sprache, wert=ookla) if ookla else None,
    )
    zeilen = [
        _zeile(f"Heimnetz {u.heimnetz}", f"Home Assistant {u.ha}"),
        t("Reiter: {reiter}", sprache, reiter=_zeile(u.kontext, u.geraet))
        if u.kontext or u.geraet
        else "",
        box,
        netz,
        t("Lokales Ticket: {ticket}", sprache, ticket=u.ticket) if u.ticket else "",
    ]
    return [f"- {z}" for z in zeilen if z]


def _zelle(z: Zelldaten, sprache: str) -> list[str]:
    anker = _zeile(
        z.kennung or None,
        f"PCI {z.pci}" if z.pci is not None else None,
        f"TAC {z.tac}" if z.tac else None,
        f"PLMN {z.plmn}" if z.plmn else None,
    )
    signal = _zeile(
        f"RSRP {z.rsrp} dBm" if z.rsrp is not None else None,
        f"RSRQ {z.rsrq} dB" if z.rsrq is not None else None,
        "5G: " + (f"RSRP {z.nr_rsrp} dBm" if z.nr_rsrp is not None else t("aus", sprache)),
    )
    zeilen = [
        t("Ankerzelle: {zelle}", sprache, zelle=anker) if anker else "",
        signal,
        t("Entfernung laut Box: {entfernung}", sprache, entfernung=z.entfernung)
        if z.entfernung
        else "",
    ]
    return [f"### {t('Zell- und Signaldaten', sprache)}"] + [f"- {x}" for x in zeilen if x]


def _text(meldung: str, u: Umgebung, z: Zelldaten | None, sprache: str) -> str:
    teile = [meldung.strip(), "", f"### {t('Umgebung', sprache)}", *_umgebung(u, sprache)]
    if z is not None:
        teile += ["", *_zelle(z, sprache)]
    return "\n".join(teile)


def url(basis: str, titel_: str, text: str) -> str:
    """Link auf das vorausgefüllte Issue (basis = …/issues/new)."""
    return f"{basis}?title={quote(titel_, safe='')}&body={quote(text, safe='')}"


@dataclass(frozen=True)
class Issue:
    titel: str
    text: str
    url: str
    gekuerzt: bool  # Text der Meldung gekürzt, damit der Link passt


def issue(
    basis: str,
    art: str,
    meldung: str,
    u: Umgebung,
    z: Zelldaten | None = None,
    namen: Iterable[str] = (),
    sprache: str = DE,
) -> Issue:
    """Titel, Text und Link; der Text der Meldung ist geschwärzt und so weit gekürzt, dass der Link passt."""
    namen = tuple(namen)
    meldung = schwaerzen(meldung.strip(), namen, sprache)
    # Reiter und Gerät kommen frei von der Seite: den Reiter schwärzen, beim Gerät nur die bekannten Werte
    u = replace(
        u,
        kontext=schwaerzen(u.kontext, namen, sprache),
        geraet=u.geraet if u.geraet in GERAETE else "",
    )
    titel_ = titel(art, meldung, sprache)
    text = _text(meldung, u, z, sprache)
    link = url(basis, titel_, text)
    if len(link) <= URL_MAX:
        return Issue(titel_, text, link, False)
    hinweis = "\n\n" + t(
        "… (gekürzt – der ganze Text steht im lokalen Ticket {ticket})",
        sprache,
        ticket=u.ticket or "–",
    )
    # längsten Anfang der Meldung suchen, mit dem der Link passt (der Rest ist begrenzt: Reiter höchstens 200 Zeichen,
    # die übrigen Felder kurz – ohne Meldung passt er immer)
    unten, oben = 0, len(meldung)
    while unten < oben:
        mitte = (unten + oben + 1) // 2
        if (
            len(url(basis, titel_, _text(meldung[:mitte].rstrip() + hinweis, u, z, sprache)))
            <= URL_MAX
        ):
            unten = mitte
        else:
            oben = mitte - 1
    text = _text(meldung[:unten].rstrip() + hinweis, u, z, sprache)
    return Issue(titel_, text, url(basis, titel_, text), True)
