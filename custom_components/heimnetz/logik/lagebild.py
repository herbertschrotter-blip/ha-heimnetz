"""Übersicht „Lagebild“ (1.1, Herbert 20.11.2026) – ohne Home Assistant.

Was die Übersicht auf einen Blick zeigt, fertig für die Seite: Kopfzeile (Gesamtstand in einem Satz), Leitung
Pi → FRITZ!Box → Zugang → Internet mit dem Zustand je Knoten und Draht, die Meldezeile (wichtigste Meldung) und der
Wächter in einer Zeile.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from .sprache import DE, t

GUT, WARN, WEG, UNKLAR = "gut", "warn", "weg", ""
_RANG = {"kritisch": 0, "warnung": 1, "info": 2}
ZUGANG_SYMBOL = {"mobilfunk": "📡", "dsl": "☎️", "glasfaser": "💡", "kabel": "📺"}


def kopf(
    box: bool, internet: bool | None, befunde: Sequence[str], sprache: str = DE
) -> dict[str, Any]:
    """Gesamtstand für den Kopf aller Reiter – ein Wortlaut aus einer Quelle. `befunde`: Stufen der offenen Befunde.

    `titel` = Satz der Übersicht („2 Störungen · 1 Hinweis“), `wort` = großes Wort im Kopf der anderen Reiter
    („Störung“), `chips` = Zahlen als Knöpfe daneben (kritisch rot, Warnung amber), `punkt` = Farbe.
    """
    stoerungen = sum(1 for b in befunde if b == "kritisch")
    hinweise = sum(1 for b in befunde if b == "warnung")
    chips = []
    if stoerungen:
        chips.append(
            {
                "art": "rot",
                "text": t(
                    "1 Störung" if stoerungen == 1 else "{n} Störungen", sprache, n=stoerungen
                ),
            }
        )
    if hinweise:
        chips.append(
            {
                "art": "amber",
                "text": t("1 Hinweis" if hinweise == 1 else "{n} Hinweise", sprache, n=hinweise),
            }
        )
    if not box:
        satz = t("FRITZ!Box nicht erreichbar", sprache)
        return {"punkt": "grau", "titel": satz, "wort": satz, "chips": chips}
    if internet is False:
        satz = t("Kein Internet", sprache)
        return {"punkt": "rot", "titel": satz, "wort": satz, "chips": chips}
    if not chips:
        satz = t("Alles in Ordnung", sprache)
        return {"punkt": "", "titel": satz, "wort": satz, "chips": []}
    return {
        "punkt": "rot" if stoerungen else "amber",
        "titel": " · ".join(c["text"] for c in chips),
        "wort": t("Störung", sprache) if stoerungen else t("Hinweise", sprache),
        "chips": chips,
    }


def balken(lage: float | None) -> int:
    """Empfang 0 … 1 → 0 … 4 Balken."""
    return 0 if lage is None else max(0, min(4, round(lage * 4)))


@dataclass(frozen=True)
class Zugang:
    art: str  # mobilfunk | dsl | glasfaser | kabel | …
    name: str  # „5G-NSA“, „DSL“ …
    verbunden: bool | None  # Verbindung des Zugangs selbst (Mobilfunknetz, Synchronisation …)
    lage: float | None = None  # Empfang 0 … 1 (nur Mobilfunk)
    wert: str = ""  # „−88 dBm“


def leitung(
    box: bool,
    pi_box: bool | None,
    internet: bool | None,
    zugang: Zugang | None,
    modell: str,
    sprache: str = DE,
) -> dict[str, Any]:
    """Vier Knoten (Pi, Box, Zugang, Internet) mit Zustand und drei Drähte dazwischen („weg“ = gestrichelt rot)."""
    box_ok = box and pi_box is not False
    zg_zustand = UNKLAR
    if box_ok and zugang is not None:
        if zugang.verbunden is False:
            zg_zustand = WEG
        elif zugang.lage is not None:
            zg_zustand = GUT if zugang.lage >= 0.5 else WARN
        elif zugang.verbunden or internet:
            zg_zustand = GUT
    inet = UNKLAR if not box_ok else GUT if internet else WEG if internet is False else UNKLAR
    zg_weg = zg_zustand == WEG
    return {
        "knoten": [
            {"teil": "pi", "zustand": GUT, "name": "Pi", "text": "Home Assistant"},
            {
                "teil": "box",
                "zustand": GUT if box_ok else WEG,
                "name": "FRITZ!Box",
                "text": modell.replace("FRITZ!Box", "").strip(),
            },
            {
                "teil": "zugang",
                "zustand": zg_zustand,
                "symbol": ZUGANG_SYMBOL.get(zugang.art, "🔗") if zugang else "🔗",
                "name": zugang.name if zugang else t("Zugang", sprache),
                "text": (zugang.wert if zugang and zugang.wert else "")
                if not zg_weg
                else t("kein Netz", sprache),
                "balken": balken(zugang.lage) if zugang and zugang.lage is not None else None,
            },
            {
                "teil": "internet",
                "zustand": inet,
                "name": "Internet",
                "text": t("erreichbar", sprache)
                if inet == GUT
                else t("getrennt", sprache)
                if inet == WEG
                else t("unbekannt", sprache),
            },
        ],
        "draehte": [
            "" if box_ok else WEG,
            WEG if box_ok and zg_weg else "",
            WEG if box_ok and inet == WEG else "",
        ],
    }


def meldung(
    befunde: Sequence[dict[str, Any]], letztes: dict[str, Any] | None, sprache: str = DE
) -> dict[str, Any]:
    """Meldezeile: Anzahl, Farbe, wichtigste Meldung; ohne Befund das letzte wichtige Ereignis (Zeit: `t`)."""
    liste = sorted(befunde, key=lambda b: _RANG.get(str(b.get("stufe")), 3))
    if not liste:
        return {
            "n": 0,
            "art": "ok",
            "titel": t("Nichts Auffälliges", sprache),
            "text": letztes["text"] if letztes else "",
            "t": letztes["t"] if letztes else None,
        }
    erst = liste[0]
    art = "rot" if erst.get("stufe") == "kritisch" else "amber"
    text = (
        t("+{n} weitere: {titel}", sprache, n=len(liste) - 1, titel=liste[1]["titel"])
        if len(liste) > 1
        else str(erst.get("text") or "")
    )
    return {"n": len(liste), "art": art, "titel": erst["titel"], "text": text, "t": None}


@dataclass(frozen=True)
class Waechterzustand:
    an: bool
    punkt: str  # ok | amber | rot | grau
    weg_seit: float | None  # Ausfall läuft (sanfte Stufe wartet oder greift)
    eingriffe: Iterable[float]  # Zeiten der Eingriffe (Strom aus/an)


def waechter(liste: Sequence[Waechterzustand], jetzt: float, sprache: str = DE) -> dict[str, Any]:
    """Wächter in einer Zeile für die Mini-Kachel."""
    if not liste:
        return {
            "wort": t("keiner", sprache),
            "text": t("einrichten ›", sprache),
            "punkt": "grau",
            "t": None,
        }
    an = [w for w in liste if w.an]
    if not an:
        return {
            "wort": t("aus", sprache),
            "text": t("{n} eingerichtet", sprache, n=len(liste)),
            "punkt": "grau",
            "t": None,
        }
    letzter = max((z for w in an for z in w.eingriffe), default=None)
    greift = any(w.weg_seit is not None for w in an)  # nur solange ein Ausfall läuft
    punkt = (
        "rot"
        if any(w.punkt == "rot" for w in an)
        else "amber"
        if greift or any(w.punkt == "amber" for w in an)
        else "grau"
        if all(w.punkt == "grau" for w in an)  # noch keine Steckdose gelesen
        else "ok"
    )
    return {
        "wort": t("greift ein", sprache) if greift else t("bereit", sprache),
        "text": t("{n} an", sprache, n=len(an))
        + " · "
        + (t("letzter Eingriff", sprache) if letzter is not None else t("kein Eingriff", sprache)),
        "punkt": punkt,
        "t": letzter,
    }
