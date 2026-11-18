"""Ausfälle des Pi verstehen (Herbert, 18.11.2026) – ohne Home Assistant.

Zwei Ausfälle (10.11., 16.11.) ließen sich hinterher nur zum Teil erklären: das Systemprotokoll des Pi endete ohne
Herunterfahren, wer den Speicher gefüllt hatte, schrieb niemand mit. Deshalb:

- **Speicher mitschreiben:** alle 5 Minuten, wie viel Home Assistant, der Supervisor und jedes Add-on belegen, dazu
  freier Speicher und Auslagerung des Pi. Wird es knapp, eine Warnung (höchstens einmal je Stunde).
- **Ausfallbericht:** Beim Start sieht Heimnetz nach, ob der letzte Lauf sauber geendet hat (Herzschlag jede Minute,
  Marke beim Beenden). Wenn nicht: wann Home Assistant zuletzt lebte, ob der Pi selbst neu gestartet ist, wann sein
  Systemprotokoll endete, ob der Speicher voll war (vom Kernel beendete Programme, leere Auslagerung), wer zuletzt am
  meisten Speicher hatte und was die Steckdose des Wächters gesehen und getan hat.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .sprache import DE, t, zahl

SPEICHER_TAKT_S = 300
SPEICHER_AUFBEWAHREN_S = 8 * 86_400
HERZSCHLAG_S = 60
WARN_FREI_ANTEIL = 0.10  # weniger frei als 10 % des Speichers …
WARN_SWAP_ANTEIL = 0.80  # … oder Auslagerung zu mehr als 80 % belegt
WARN_ABSTAND_S = 3600
HA = "Home Assistant"
SUPERVISOR = "Supervisor"


# ── Speicher ──


@dataclass(frozen=True)
class Speicherstand:
    t: float
    gesamt_mb: int
    frei_mb: int  # MemAvailable
    swap_mb: int
    swap_frei_mb: int
    wer: dict[str, int] = field(default_factory=dict)  # Name → belegt in MB

    def als_dict(self) -> dict[str, Any]:
        return {
            "g": self.gesamt_mb,
            "f": self.frei_mb,
            "s": self.swap_mb,
            "sf": self.swap_frei_mb,
            "w": self.wer,
        }

    @classmethod
    def aus_dict(cls, t: float, d: dict[str, Any]) -> Speicherstand:
        return cls(
            t,
            int(d["g"]),
            int(d["f"]),
            int(d["s"]),
            int(d["sf"]),
            {str(k): int(v) for k, v in d["w"].items()},
        )

    @property
    def top(self) -> list[tuple[str, int]]:
        return sorted(self.wer.items(), key=lambda x: -x[1])[:3]


def meminfo(text: str) -> tuple[int, int, int, int]:
    """(gesamt, verfügbar, Auslagerung gesamt, Auslagerung frei) in MB aus /proc/meminfo."""
    werte = {}
    for zeile in text.splitlines():
        name, _, rest = zeile.partition(":")
        if name in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree") and rest.strip():
            werte[name] = int(rest.split()[0]) // 1024
    return (
        werte.get("MemTotal", 0),
        werte.get("MemAvailable", 0),
        werte.get("SwapTotal", 0),
        werte.get("SwapFree", 0),
    )


def knapp(s: Speicherstand) -> str | None:
    """Grund, wenn der Speicher knapp wird, sonst None."""
    if s.gesamt_mb and s.frei_mb < s.gesamt_mb * WARN_FREI_ANTEIL:
        return "frei"
    if s.swap_mb and (s.swap_mb - s.swap_frei_mb) > s.swap_mb * WARN_SWAP_ANTEIL:
        return "swap"
    return None


def gb(mb: int, sprache: str = DE) -> str:
    return f"{zahl(mb / 1024, 1, sprache)} GB"


def wer_text(s: Speicherstand, sprache: str = DE) -> str:
    return ", ".join(f"{n} {gb(mb, sprache)}" for n, mb in s.top)


def knapp_text(s: Speicherstand, sprache: str = DE) -> str:
    return t(
        "Speicher knapp: frei {frei} von {gesamt}, Auslagerung {swap} belegt – am meisten: {wer}",
        sprache,
        frei=gb(s.frei_mb, sprache),
        gesamt=gb(s.gesamt_mb, sprache),
        swap=gb(s.swap_mb - s.swap_frei_mb, sprache),
        wer=wer_text(s, sprache),
    )


# ── Systemprotokoll des vorigen Starts ──

_ZEIT = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{2}:\d{2})")
_OOM = re.compile(r"Out of memory: Killed process \d+ \(([^)]*)\).*?anon-rss:(\d+)kB")
_SWAP_LEER = re.compile(r"Free swap\s*=\s*0kB")
_SAUBER = re.compile(
    r"(Reached target .*(Shutdown|Reboot|Power-Off)|systemd-shutdown|Stopping Flush Journal)"
)


@dataclass(frozen=True)
class Bootbefund:
    ende: float | None  # letzte Zeile mit Zeit
    sauber: bool  # herunterfahren steht im Protokoll
    oom: tuple[tuple[float, str, int], ...]  # (Zeit, Programm, belegt in MB)
    swap_leer: bool


def _zeit(zeile: str) -> float | None:
    if m := _ZEIT.match(zeile):
        try:
            return datetime.fromisoformat(m.group(1)).timestamp()
        except ValueError:
            return None
    return None


def boot_auswerten(text: str) -> Bootbefund:
    ende = None
    oom = []
    swap_leer = sauber = False
    for zeile in text.splitlines():
        z = _zeit(zeile)
        if z is not None:
            ende = z
        if m := _OOM.search(zeile):
            oom.append((z or 0.0, m.group(1), int(m.group(2)) // 1024))
        if _SWAP_LEER.search(zeile):
            swap_leer = True
        if _SAUBER.search(zeile):
            sauber = True
    return Bootbefund(ende, sauber, tuple(oom), swap_leer)


# ── Bericht ──


@dataclass(frozen=True)
class Lage:
    """Was Heimnetz beim Start weiß. Zeiten in Sekunden (Unix)."""

    jetzt: float
    lebt: float | None  # letzter Herzschlag des vorigen Laufs
    sauber: float | None  # Marke beim Beenden des vorigen Laufs
    pi_start: float | None  # Start des Pi (Supervisor)
    boot: Bootbefund | None = (
        None  # Systemprotokoll des vorigen Starts (nur wenn der Pi neu gestartet ist)
    )
    speicher: Speicherstand | None = None  # letzter Speicherstand vor dem Ausfall
    dose: tuple[
        str, ...
    ] = ()  # was die Steckdose des Wächters in der Zeit festhielt (fertige Texte)

    @property
    def unsauber(self) -> bool:
        return self.lebt is not None and (self.sauber is None or self.sauber < self.lebt)

    @property
    def pi_neu(self) -> bool:
        return self.pi_start is not None and self.lebt is not None and self.pi_start > self.lebt


def _uhr(ts: float, tz: Any) -> str:
    return datetime.fromtimestamp(ts, tz).strftime("%d.%m. %H:%M")


def _dauer(s: float, sprache: str) -> str:
    m = int(s // 60)
    return (
        t("{h} h {m} min", sprache, h=m // 60, m=m % 60) if m >= 60 else t("{m} min", sprache, m=m)
    )


def bericht(lage: Lage, tz: Any, sprache: str = DE) -> list[str] | None:
    """Zeilen des Ausfallberichts, None, wenn der vorige Lauf sauber endete (oder es keinen gab)."""
    if not lage.unsauber or lage.lebt is None:
        return None
    zeilen = [
        t(
            "Home Assistant lief zuletzt {zeit}, wieder da {jetzt} ({dauer} weg)",
            sprache,
            zeit=_uhr(lage.lebt, tz),
            jetzt=_uhr(lage.jetzt, tz),
            dauer=_dauer(lage.jetzt - lage.lebt, sprache),
        )
    ]
    if lage.pi_neu:
        b = lage.boot
        if b is not None and b.ende is not None:
            zeilen.append(
                t(
                    "Der Pi ist neu gestartet ({start}); sein Systemprotokoll endet {ende} {wie}",
                    sprache,
                    start=_uhr(lage.pi_start or 0, tz),
                    ende=_uhr(b.ende, tz),
                    wie=t("mit Herunterfahren", sprache)
                    if b.sauber
                    else t("ohne Herunterfahren", sprache),
                )
            )
        else:
            zeilen.append(
                t("Der Pi ist neu gestartet ({start})", sprache, start=_uhr(lage.pi_start or 0, tz))
            )
        if b is not None and b.oom:
            namen = sorted({n for _, n, _ in b.oom})
            groesste = max(mb for _, _, mb in b.oom)
            zeilen.append(
                t(
                    "Speicher voll: der Kernel hat {n}× ein Programm beendet ({namen}, bis {gb}), zuletzt {zeit}",
                    sprache,
                    n=len(b.oom),
                    namen=", ".join(namen),
                    gb=gb(groesste, sprache),
                    zeit=_uhr(b.oom[-1][0], tz),
                )
            )
        if b is not None and b.swap_leer:
            zeilen.append(t("Die Auslagerung war ganz voll", sprache))
    else:
        zeilen.append(t("Nur Home Assistant ist neu gestartet, der Pi lief durch", sprache))
    if (s := lage.speicher) is not None:
        zeilen.append(
            t(
                "Speicher zuletzt ({zeit}): frei {frei} von {gesamt}, Auslagerung {swap} belegt – am meisten: {wer}",
                sprache,
                zeit=_uhr(s.t, tz),
                frei=gb(s.frei_mb, sprache),
                gesamt=gb(s.gesamt_mb, sprache),
                swap=gb(s.swap_mb - s.swap_frei_mb, sprache),
                wer=wer_text(s, sprache),
            )
        )
    zeilen += list(lage.dose)
    return zeilen
