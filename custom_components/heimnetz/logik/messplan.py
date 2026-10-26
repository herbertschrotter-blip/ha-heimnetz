"""Messplan: wann die Integration eine Ookla-Messung startet (Herbert, 12.10.2026; Mockup netzwerk.html).

Der Plan gehört der Integration; gemessen wird von Ookla. Fällig ist eine Messung, wenn der Plan eingeschaltet ist,
die Zeit im Zeitfenster liegt und seit der letzten Messung (oder dem letzten Auslösen) der Takt vergangen ist. Bei
Verkehr über der Schwelle wird – wenn so eingestellt – verschoben: alle 5 Minuten neu, höchstens 30 Minuten; danach
wird trotzdem gemessen (die Messung zählt dann als belastet).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, tzinfo
from typing import Any

from .auswertung import MESS_S
from .einstellungen import Ungueltig
from .sprache import merke

TAKTE_H = (1, 2, 4, 6, 12, 24)
VERKEHR = ("warten", "messen")  # bei Verkehr: verschieben, bis es ruhig ist / trotzdem messen
NEU_VERSUCH_S = 300
HOECHSTENS_S = 1800
TAG_MIN = 1440
SERIE_N = (2, 3, 4, 5)

MESSEN, WARTEN, NICHTS = "messen", "warten", "nichts"


@dataclass(frozen=True)
class Messplan:
    an: bool = False
    takt_h: int = 4
    von_min: int = 0  # Minuten seit Mitternacht
    bis_min: int = TAG_MIN  # 1440 = 24:00; bis < von heißt über Mitternacht
    verkehr: str = "warten"
    serie: int = 3  # WU-0001: Durchläufe bei „n× messen“

    def als_dict(self) -> dict[str, Any]:
        return {
            "an": self.an,
            "takt_h": self.takt_h,
            "von": _uhrzeit(self.von_min),
            "bis": _uhrzeit(self.bis_min),
            "verkehr": self.verkehr,
            "serie": self.serie,
        }


# WU-0006: Vorgabe für eine neue Installation – zurückhaltend 4 Messungen am Tag (jede kostet Datenvolumen). Ohne
# gespeicherten Plan (alte Fassung, übernommene Einstellungen ohne Plan) bleibt es bei `Messplan()`, also aus.
NEU = Messplan(an=True, takt_h=6)


def tests_am_tag(plan: Messplan) -> int:
    """Wie viele Messungen der Plan höchstens an einem Tag startet (Zeitfenster / Takt, aufgerundet); 0 = aus."""
    if not plan.an:
        return 0
    von, bis = plan.von_min, plan.bis_min
    if von == bis or (von == 0 and bis == TAG_MIN):
        fenster = TAG_MIN
    else:
        fenster = bis - von if von < bis else TAG_MIN - von + bis
    takt = plan.takt_h * 60
    return min(-(-fenster // takt), TAG_MIN // takt)


def volumen(plan: Messplan, down: float | None, up: float | None) -> dict[str, Any]:
    """Geschätztes Datenvolumen je Messung und am Tag nach dem Plan (MB): (Download + Upload) in Mbit/s × Dauer je
    Richtung / 8 – dieselbe Schätzung wie im Speedtest-Protokoll. Ohne Werte (keine Messung, kein Tarif) nur die Zahl
    der Messungen; die Seite zeigt dann den allgemeinen Hinweis."""
    n = tests_am_tag(plan)
    je_test = round(((down or 0) + (up or 0)) * MESS_S / 8) if down or up else None
    return {
        "tests_tag": n,
        "je_test_mb": je_test,
        "tag_mb": je_test * n if je_test is not None else None,
        "monat_gb": round(je_test * n * 30 / 1000, 1) if je_test is not None else None,
    }


def _uhrzeit(minuten: int) -> str:
    return f"{minuten // 60:02d}:{minuten % 60:02d}"


def _minuten(wert: Any, name: str) -> int:
    try:
        h, m = (int(x) for x in str(wert).strip()[:5].split(":"))
    except ValueError as err:
        raise Ungueltig("{name}: Uhrzeit wie 06:30", name=name) from err
    if not (0 <= h <= 24 and 0 <= m < 60) or (h == 24 and m):
        raise Ungueltig("{name}: Uhrzeit zwischen 00:00 und 24:00", name=name)
    return h * 60 + m


def pruefen(daten: dict[str, Any] | None) -> Messplan:
    """Aus Eingaben der Seite oder gespeichertem dict; fehlende Felder = Vorgabe."""
    d = daten or {}
    v = Messplan()
    try:
        takt = int(d.get("takt_h", v.takt_h))
    except (TypeError, ValueError) as err:
        raise Ungueltig("Wie oft: keine Zahl") from err
    if takt not in TAKTE_H:
        raise Ungueltig("Wie oft: {werte} Stunden", werte=", ".join(str(t) for t in TAKTE_H))
    verkehr = str(d.get("verkehr", v.verkehr))
    if verkehr not in VERKEHR:
        raise Ungueltig("Bei Verkehr: verschieben oder trotzdem messen")
    von = (
        _minuten(d.get("von", "00:00"), merke("Nur zwischen (von)")) % TAG_MIN
    )  # 24:00 als Beginn = 00:00
    bis = _minuten(d.get("bis", "24:00"), merke("Nur zwischen (bis)"))
    if von == bis and von not in (0, TAG_MIN):
        raise Ungueltig("Nur zwischen: von und bis sind gleich")
    try:
        serie = int(d.get("serie", v.serie))
    except (TypeError, ValueError) as err:
        raise Ungueltig("Serie: keine Zahl") from err
    if serie not in SERIE_N:
        raise Ungueltig("Serie: {von} bis {bis} Durchläufe", von=SERIE_N[0], bis=SERIE_N[-1])
    return Messplan(bool(d.get("an", v.an)), takt, von, bis, verkehr, serie)


def im_fenster(plan: Messplan, t: datetime) -> bool:
    m = t.hour * 60 + t.minute
    von, bis = plan.von_min, plan.bis_min
    if von == bis or (von == 0 and bis == TAG_MIN):
        return True  # ganzer Tag
    if von < bis:
        return von <= m < bis
    return m >= von or m < bis  # über Mitternacht


def naechste(plan: Messplan, letzte: float | None, jetzt: float, tz: tzinfo) -> float | None:
    """Frühester Zeitpunkt ≥ jetzt, an dem der Plan misst (ohne Verschieben wegen Verkehr); None = Plan aus."""
    if not plan.an:
        return None
    kandidat = max(jetzt, (letzte or 0.0) + plan.takt_h * 3600)
    dt = datetime.fromtimestamp(kandidat, tz)
    if im_fenster(plan, dt):
        return kandidat
    start = dt.replace(hour=plan.von_min // 60, minute=plan.von_min % 60, second=0, microsecond=0)
    if start <= dt:
        start = (start + timedelta(days=1)).replace(
            hour=plan.von_min // 60, minute=plan.von_min % 60
        )
    return start.timestamp()


@dataclass(frozen=True)
class Entscheidung:
    aktion: str  # messen, warten, nichts
    grund: str  # deutscher Text, zugleich Kennung; die Seite bekommt ihn übersetzt (sprache.t)
    wartet_seit: float | None = None  # seit wann wegen Verkehr verschoben wird
    geprueft: float | None = None  # letzte Prüfung des Verkehrs beim Warten
    neuer_versuch: float | None = None


def entscheiden(
    plan: Messplan,
    letzte: float | None,
    jetzt: float,
    tz: tzinfo,
    verkehr_mbit: float | None,
    schwelle: float,
    vorher: Entscheidung | None = None,
) -> Entscheidung:
    """Was der Plan in diesem Augenblick tut. `letzte` = letzte Messung oder letztes Auslösen; `vorher` = die
    Entscheidung des vorigen Abrufs (für das Warten: alle 5 Minuten neu prüfen, höchstens 30 Minuten)."""
    faellig = naechste(plan, letzte, jetzt, tz)
    if faellig is None or faellig > jetzt:
        return Entscheidung(NICHTS, merke("nicht fällig"))
    wartet = vorher is not None and vorher.aktion == WARTEN and vorher.wartet_seit is not None
    seit = vorher.wartet_seit if wartet and vorher else None
    if seit is not None and jetzt - seit >= HOECHSTENS_S:
        return Entscheidung(MESSEN, merke("Verkehr seit 30 Minuten – trotzdem gemessen"))
    if (
        seit is not None
        and vorher
        and vorher.geprueft is not None
        and jetzt - vorher.geprueft < NEU_VERSUCH_S
    ):
        return vorher  # zwischen zwei Versuchen nicht neu prüfen
    belastet = verkehr_mbit is not None and verkehr_mbit > schwelle
    if not belastet:
        return Entscheidung(
            MESSEN, merke("ruhig") if verkehr_mbit is not None else merke("Verkehr unbekannt")
        )
    if plan.verkehr == "messen":
        return Entscheidung(MESSEN, merke("Verkehr, trotzdem messen (eingestellt)"))
    start = seit if seit is not None else jetzt
    return Entscheidung(
        WARTEN,
        merke("Verkehr im Heimnetz"),
        start,
        jetzt,
        min(jetzt + NEU_VERSUCH_S, start + HOECHSTENS_S),
    )
