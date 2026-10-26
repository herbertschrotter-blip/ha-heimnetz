"""Ereignisprotokoll der FRITZ!Box: lesen, einordnen, neue Zeilen erkennen.

Die Box hält nur einige hundert Zeilen und überschreibt alte; die Integration merkt sich, welche Zeilen sie schon
gesehen hat, und übernimmt nur neue (Abgleich über Datum, Zeit und Text).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime

from .werte import text

# Gruppen im Ereignisprotokoll (wie der Filter in der Oberfläche der Box)
GRUPPEN = {
    "1": "system",
    "2": "internet",
    "3": "telefon",
    "4": "wlan",
    "5": "usb",
    "sys": "system",
    "net": "internet",
    "fon": "telefon",
    "wlan": "wlan",
    "usb": "usb",
}
WORTE = (
    ("wlan", ("wlan", "wi-fi", "funknetz")),
    (
        "internet",
        (
            "internet",
            "dsl",
            "mobilfunk",
            "pppoe",
            "ip-adresse",
            "ipv6",
            "dns",
            "anbieter",
            "lte",
            "5g",
        ),
    ),
    ("telefon", ("telefon", "anruf", "rufnummer", "dect")),
)
GESEHEN_MERKEN = 1500  # so viele Schlüssel merkt sich der Abgleich (die Box hält ~400 Zeilen)
_ZUSAMMENGEFASST = re.compile(r"\s*\[\d+ Meldungen seit [^\]]+\]")


@dataclass(frozen=True)
class BoxZeile:
    """Eine Zeile, wie die Box sie liefert."""

    datum: str
    zeit: str
    gruppe: str
    id: str
    text: str


@dataclass(frozen=True)
class Protokolleintrag:
    """Eine neue Zeile für das dauerhafte Protokoll."""

    zeitpunkt: datetime | None
    roh_zeit: str
    kategorie: str
    text: str
    schluessel: str  # gleiche Zeile der Box = gleicher Schlüssel (auch nach einem Neustart von HA)


def kategorie(gruppe: str, meldung: str) -> str:
    """system, internet, telefon, wlan oder usb – nach Gruppe der Box, sonst nach Stichworten."""
    g = GRUPPEN.get(gruppe.strip().lower())
    if g:
        return g
    klein = meldung.lower()
    for name, worte in WORTE:
        if any(w in klein for w in worte):
            return name
    return "system"


def zeitpunkt(z: BoxZeile) -> datetime | None:
    for muster in ("%d.%m.%y %H:%M:%S", "%d.%m.%Y %H:%M:%S"):
        try:
            return datetime.strptime(f"{z.datum} {z.zeit}", muster)
        except ValueError:
            pass
    return None


def _aelteste_zuerst(zeilen: list[BoxZeile]) -> list[BoxZeile]:
    """Die Box liefert neueste zuerst; gedreht wird nur, wenn das stimmt (gleiche Sekunden bleiben in Reihenfolge)."""
    if len(zeilen) > 1:
        a, b = zeitpunkt(zeilen[0]), zeitpunkt(zeilen[-1])
        if a and b and a > b:
            zeilen.reverse()
    return zeilen


def aus_xml(roh: str | bytes) -> list[BoxZeile]:
    """XML aus X_AVM-DE_GetDeviceLogPath → Zeilen, älteste zuerst."""
    out = []
    for ev in ET.fromstring(roh):
        d = {c.tag.lower(): text(c.text) for c in ev}
        meldung = d.get("msg") or d.get("message") or d.get("text") or ""
        if meldung:
            out.append(
                BoxZeile(
                    d.get("date", ""),
                    d.get("time", ""),
                    d.get("group", ""),
                    d.get("id", ""),
                    meldung,
                )
            )
    return _aelteste_zuerst(out)


def aus_text(roh: str) -> list[BoxZeile]:
    """Textform aus GetDeviceLog: je Zeile „TT.MM.JJ HH:MM:SS Meldung“."""
    out = []
    for zeile in roh.splitlines():
        m = re.match(r"^(\d{2}\.\d{2}\.\d{2,4}) (\d{2}:\d{2}:\d{2}) (.+)$", zeile.strip())
        if m:
            out.append(BoxZeile(m.group(1), m.group(2), "", "", m.group(3)))
    return _aelteste_zuerst(out)


def schluessel(z: BoxZeile) -> str:
    return schluessel_aus(f"{z.datum} {z.zeit}", z.text)


def schluessel_aus(roh_zeit: str, meldung: str) -> str:
    """Wiederholte Meldungen fasst die Box zusammen („[3 Meldungen seit …]“) – der Zusatz zählt nicht."""
    return f"{roh_zeit} {_ZUSAMMENGEFASST.sub('', meldung)}"


def neue_zeilen(zeilen: list[BoxZeile], gesehen: list[str]) -> list[Protokolleintrag]:
    """Noch nicht gesehene Zeilen → Einträge; `gesehen` wird fortgeschrieben und gekürzt."""
    bekannt, neu = set(gesehen), []
    for z in zeilen:
        k = schluessel(z)
        if k in bekannt:
            continue
        bekannt.add(k)
        gesehen.append(k)
        neu.append(
            Protokolleintrag(
                zeitpunkt(z), f"{z.datum} {z.zeit}", kategorie(z.gruppe, z.text), z.text, k
            )
        )
    del gesehen[:-GESEHEN_MERKEN]
    return neu
