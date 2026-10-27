"""Einrichtung (WU-0007): welche Voraussetzungen eingerichtet sind und was fehlt – wie im README, Abschnitt
„Voraussetzungen“, in drei Stufen Muss / Soll / Kann.

Reine Bewertung ohne Home Assistant: Eingabe ist, was der dünne HA-Teil (`einrichtung.py`) gelesen hat (geladene
Integrationen, Config-Einträge, heruntergeladene Custom Components, Optionen, Versionen); Ausgabe je Teil Stufe,
Status, Stand oder Hinweis und die Knöpfe mit ihrem Ziel. Die Seite zeigt nur an. Heimnetz installiert nichts selbst:
die Knöpfe öffnen Home Assistant oder HACS an der richtigen Stelle.

Status je Zeile: `ok` (eingerichtet), `fehlt` (Soll fehlt), `muss` (Muss fehlt), `aus` (Kann fehlt).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

from .sprache import DE, t

# Domains der Integrationen, die geprüft werden. Ookla wie `speedtest.OOKLA`, FRITZ!Box Tools wie `const.FRITZ` (ein
# Integrationstest prüft, dass sie gleich bleiben – die Fachlogik darf die HA-Module nicht laden).
FRITZ = "fritz"
OOKLA = "ookla_speedtest"
HACS = "hacs"
RECORDER = "recorder"
MET = "met"
HOLIDAY = "holiday"
SCRIBE = "scribe"
INFLUXDB = "influxdb"
HEIMNETZ = "heimnetz"
# Integrationen mit Config-Eintrag: eingerichtet heißt „mindestens ein Eintrag geladen“
MIT_EINTRAG = (FRITZ, OOKLA, HACS, MET, HOLIDAY, SCRIBE)
# Custom Components, die als „heruntergeladen“ zählen können
AUS_HACS = (HACS, OOKLA, SCRIBE)

# Repositories in HACS (README-Links). Scribe: jonathan-gtd/scribe (geprüft 27.10.2026 – das in Notizen genannte
# jeradM/scribe gibt es auf GitHub nicht; Scribe mit TimescaleDB, Domain `scribe`, mit Einrichtungsdialog).
OOKLA_REPO = ("soulripper13", "hass-speedtest-ookla")
SCRIBE_REPO = ("jonathan-gtd", "scribe")
HACS_ANLEITUNG = "https://hacs.xyz/docs/use/"
OPENCELLID = "https://opencellid.org"
RECORDER_ANLEITUNG = "https://www.home-assistant.io/integrations/recorder/"

STUFEN = ("muss", "soll", "kann")
_FEHLT = {"muss": "muss", "soll": "fehlt", "kann": "aus"}


@dataclass(frozen=True)
class Stand:
    """Was Home Assistant gerade meldet (vom HA-Teil gelesen, nichts davon geändert)."""

    ha_version: str
    ha_mindest: str
    geladen: frozenset[str] = (
        frozenset()
    )  # geladene Integrationen (hass.config.components ohne Plattformen)
    eintraege: Mapping[str, int] = field(default_factory=dict)  # Domain → Anzahl Config-Einträge
    eintraege_geladen: Mapping[str, int] = field(default_factory=dict)  # Domain → davon geladen
    heruntergeladen: frozenset[str] = frozenset()  # vorhandene Custom Components (z. B. aus HACS)
    box_modell: str = ""  # nur das Modell der Box, nie Gerätenamen oder Adressen
    recorder_tage: int | None = None  # Aufbewahrung des Recorders, falls lesbar
    opencellid: bool = (
        False  # Schlüssel in den Optionen von Heimnetz eingetragen (der Schlüssel selbst nie)
    )


@dataclass(frozen=True)
class Aktion:
    text: str
    ziel: str  # Pfad in Home Assistant oder (extern) Adresse im Netz
    extern: bool = False  # neues Fenster statt Navigation in Home Assistant
    blau: bool = True

    def als_dict(self) -> dict[str, Any]:
        return {"text": self.text, "ziel": self.ziel, "extern": self.extern, "blau": self.blau}


@dataclass(frozen=True)
class Teil:
    schluessel: str
    stufe: str
    status: str
    name: str
    wofuer: str
    stand: str | None = None  # eingerichtet: was dort steht (leise rechts)
    hinweis: str | None = None  # nicht eingerichtet: kurzer Satz vor den Knöpfen
    aktionen: tuple[Aktion, ...] = ()

    def als_dict(self) -> dict[str, Any]:
        return {
            "schluessel": self.schluessel,
            "stufe": self.stufe,
            "status": self.status,
            "name": self.name,
            "wofuer": self.wofuer,
            "stand": self.stand,
            "hinweis": self.hinweis,
            "aktionen": [a.als_dict() for a in self.aktionen],
        }


def version_tupel(v: str) -> tuple[int, int, int]:
    """„2026.10.2“ → (2026, 10, 2); Vorabfassungen („2026.11.0b1“, „….dev…“) zählen mit ihrer Nummer."""
    z = [int(m.group(0)) if (m := re.match(r"\d+", x)) else 0 for x in v.split(".")[:3]]
    z += [0] * (3 - len(z))
    return z[0], z[1], z[2]


def einrichten_ziel(domain: str) -> str:
    """Einrichtungsdialog der Integration in Home Assistant (My-Home-Assistant-Weiterleitung im eigenen Haus)."""
    return f"/_my_redirect/config_flow_start?{urlencode({'domain': domain})}"


def hacs_ziel(repo: tuple[str, str]) -> str:
    """Repository in HACS öffnen (Herunterladen macht der Nutzer selbst)."""
    owner, repository = repo
    abfrage = urlencode({"owner": owner, "repository": repository, "category": "integration"})
    return f"/_my_redirect/hacs_repository?{abfrage}"


def integration_ziel(domain: str) -> str:
    """Seite der Integration unter Geräte & Dienste."""
    return f"/config/integrations/integration/{domain}"


def _eingerichtet(s: Stand, domain: str) -> bool:
    return s.eintraege_geladen.get(domain, 0) > 0


def _einrichten(sp: str, domain: str) -> Aktion:
    return Aktion(t("Einrichten ›", sp), einrichten_ziel(domain))


def _integration(
    s: Stand,
    sp: str,
    schluessel: str,
    stufe: str,
    name: str,
    wofuer: str,
    domain: str,
    repo: tuple[str, str] | None = None,
    stand: str | None = None,
) -> Teil:
    """Teil mit Config-Eintrag: eingerichtet, eingerichtet aber nicht geladen, heruntergeladen (Custom Component vor
    dem Einrichten bzw. Neustart), aus HACS zu holen oder – für alles in HA Enthaltene – einzurichten."""
    if _eingerichtet(s, domain):
        return Teil(schluessel, stufe, "ok", name, wofuer, stand or t("eingerichtet", sp))
    fehlt = _FEHLT[stufe]
    if s.eintraege.get(domain, 0):
        return Teil(
            schluessel,
            stufe,
            fehlt,
            name,
            wofuer,
            hinweis=t("eingerichtet, aber nicht geladen", sp),
            aktionen=(Aktion(t("Öffnen ›", sp), integration_ziel(domain)),),
        )
    if repo is None:  # in Home Assistant enthalten
        return Teil(schluessel, stufe, fehlt, name, wofuer, aktionen=(_einrichten(sp, domain),))
    if domain in s.heruntergeladen:
        return Teil(
            schluessel,
            stufe,
            fehlt,
            name,
            wofuer,
            hinweis=t("heruntergeladen – nach einem Neustart einrichten", sp),
            aktionen=(_einrichten(sp, domain),),
        )
    if not _eingerichtet(s, HACS):
        return Teil(schluessel, stufe, fehlt, name, wofuer, hinweis=t("erst HACS installieren", sp))
    return Teil(
        schluessel,
        stufe,
        fehlt,
        name,
        wofuer,
        aktionen=(Aktion(t("In HACS öffnen ↗", sp), hacs_ziel(repo)),),
    )


def teile(s: Stand, sp: str = DE) -> list[Teil]:
    """Alle Voraussetzungen in der Reihenfolge des README."""
    neu_genug = version_tupel(s.ha_version) >= version_tupel(s.ha_mindest)
    ha = Teil(
        "homeassistant",
        "muss",
        "ok" if neu_genug else "muss",
        "Home Assistant",
        t("ab {version}", sp, version=s.ha_mindest),
        s.ha_version if neu_genug else None,
        None if neu_genug else t("{version} ist zu alt", sp, version=s.ha_version),
        () if neu_genug else (Aktion(t("Aktualisieren ›", sp), "/config/updates"),),
    )
    # Heimnetz liest nur den Zugang aus dem Eintrag von FRITZ!Box Tools – vorhanden reicht, geladen muss er nicht sein
    if s.eintraege.get(FRITZ, 0):
        fritz = Teil(
            "fritz",
            "muss",
            "ok",
            "FRITZ!Box Tools",
            t("Zugang zur Box", sp),
            t("eingerichtet · {modell}", sp, modell=s.box_modell)
            if s.box_modell
            else t("eingerichtet", sp),
        )
    else:
        fritz = Teil(
            "fritz",
            "muss",
            "muss",
            "FRITZ!Box Tools",
            t("Zugang zur Box", sp),
            aktionen=(_einrichten(sp, FRITZ),),
        )
    if RECORDER in s.geladen:
        recorder = Teil(
            "recorder",
            "muss",
            "ok",
            "Recorder",
            t("Verlauf, Verbrauch je Tag", sp),
            t("aktiv · {n} Tage", sp, n=s.recorder_tage)
            if s.recorder_tage is not None
            else t("aktiv", sp),
        )
    else:
        recorder = Teil(
            "recorder",
            "muss",
            "muss",
            "Recorder",
            t("Verlauf, Verbrauch je Tag", sp),
            hinweis=t("nicht geladen", sp),
            aktionen=(Aktion(t("Anleitung ↗", sp), RECORDER_ANLEITUNG, extern=True),),
        )
    if _eingerichtet(s, HACS):
        hacs = Teil(
            "hacs",
            "muss",
            "ok",
            "HACS",
            t("installieren und aktualisieren", sp),
            t("installiert", sp),
        )
    elif HACS in s.heruntergeladen:
        hacs = Teil(
            "hacs",
            "muss",
            "muss",
            "HACS",
            t("installieren und aktualisieren", sp),
            hinweis=t("heruntergeladen – nach einem Neustart einrichten", sp),
            aktionen=(_einrichten(sp, HACS),),
        )
    else:
        hacs = Teil(
            "hacs",
            "muss",
            "muss",
            "HACS",
            t("ohne HACS kommen keine Updates", sp),
            aktionen=(Aktion(t("Anleitung ↗", sp), HACS_ANLEITUNG, extern=True),),
        )
    ookla = _integration(
        s,
        sp,
        "ookla",
        "soll",
        "Ookla Speedtest",
        t("misst die Geschwindigkeit (aus HACS)", sp),
        OOKLA,
        OOKLA_REPO,
    )
    met = _integration(s, sp, "met", "soll", "Met.no", t("Wetter zur Messung", sp), MET)
    holiday = _integration(
        s, sp, "holiday", "soll", "Holiday", t("Feiertage zur Messung", sp), HOLIDAY
    )
    if s.opencellid:
        ocid = Teil(
            "opencellid",
            "kann",
            "ok",
            t("OpenCellID-Schlüssel", sp),
            t("genauere Karte zum Mast", sp),
            t("eingetragen", sp),
        )
    else:
        ocid = Teil(
            "opencellid",
            "kann",
            "aus",
            t("OpenCellID-Schlüssel", sp),
            t("genauere Karte zum Mast", sp),
            aktionen=(
                Aktion(t("Schlüssel holen ↗", sp), OPENCELLID, extern=True, blau=False),
                Aktion(t("Eintragen ›", sp), integration_ziel(HEIMNETZ)),
            ),
        )
    wofuer_archiv = t("Werte über Jahre (Scribe, InfluxDB)", sp)
    if INFLUXDB in s.geladen and not _eingerichtet(s, SCRIBE):
        archiv = Teil(
            "archiv", "kann", "ok", t("Langzeitarchiv", sp), wofuer_archiv, t("InfluxDB aktiv", sp)
        )
    else:
        archiv = _integration(
            s,
            sp,
            "archiv",
            "kann",
            t("Langzeitarchiv", sp),
            wofuer_archiv,
            SCRIBE,
            SCRIBE_REPO,
            stand=t("Scribe eingerichtet", sp),
        )
    return [ha, fritz, recorder, hacs, ookla, met, holiday, ocid, archiv]


def bewerten(s: Stand, sp: str = DE) -> dict[str, Any]:
    """Antwort für die Seite: Zusammenfassung (wie viel fehlt, Farbe des Punkts am Reiter) und die Stufen."""
    alle = teile(s, sp)
    muss = sum(1 for x in alle if x.stufe == "muss" and x.status != "ok")
    soll = sum(1 for x in alle if x.stufe == "soll" and x.status != "ok")
    return {
        "muss_fehlt": muss,
        "soll_fehlt": soll,
        "punkt": "rot" if muss else "orange" if soll else None,
        "stufen": [
            {
                "stufe": st,
                "ok": sum(1 for x in alle if x.stufe == st and x.status == "ok"),
                "von": sum(1 for x in alle if x.stufe == st),
                "teile": [x.als_dict() for x in alle if x.stufe == st],
            }
            for st in STUFEN
        ],
    }
