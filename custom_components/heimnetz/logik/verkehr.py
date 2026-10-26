"""Verkehr über die Box aus den Byte-Zählern (WANCommonInterfaceConfig) und die Grundlast vor einer Messung."""

from __future__ import annotations

from dataclasses import dataclass

MERKEN = 20  # so viele Zählerstände (einer je Minute) merkt sich der Abruf
GRUNDLAST_VON_S = 450  # Grundlast = Verkehr im Fenster von 7½ bis 1½ Minuten vor der Messung –
GRUNDLAST_BIS_S = 90  # die Messung selbst (läuft ~40 s, das Ergebnis kommt am Ende) bleibt draußen
MINDEST_S = 120  # weniger Abdeckung → keine Aussage


@dataclass(frozen=True)
class Zaehlerstand:
    t: float  # Sekunden seit 1970
    rx: int
    tx: int


@dataclass(frozen=True)
class Rate:
    """Mbit/s; `sek` = abgedeckte Zeit."""

    down: float
    up: float
    sek: int


def fortschreiben(ring: list[Zaehlerstand], neu: Zaehlerstand) -> list[Zaehlerstand]:
    return (ring + [neu])[-MERKEN:]


def _gueltig(a: Zaehlerstand, b: Zaehlerstand) -> bool:
    """Ein Rücksprung des Zählers (Neustart der Box) oder gleiche Zeit ergibt keinen Abschnitt."""
    return b.t > a.t and b.rx >= a.rx and b.tx >= a.tx


def letzte_rate(ring: list[Zaehlerstand]) -> Rate | None:
    """Verkehr zwischen den letzten beiden Zählerständen."""
    if len(ring) < 2 or not _gueltig(ring[-2], ring[-1]):
        return None
    a, b = ring[-2], ring[-1]
    sek = b.t - a.t
    return Rate(
        round((b.rx - a.rx) * 8 / sek / 1e6, 1), round((b.tx - a.tx) * 8 / sek / 1e6, 1), int(sek)
    )


def grundlast(
    ring: list[Zaehlerstand],
    jetzt: float,
    von_s: int = GRUNDLAST_VON_S,
    bis_s: int = GRUNDLAST_BIS_S,
) -> Rate | None:
    """Verkehr VOR einer Messung: nur Abschnitte, die ganz im Fenster [jetzt − von_s, jetzt − bis_s] liegen."""
    sek = rx = tx = 0.0
    for a, b in zip(ring, ring[1:], strict=False):
        if a.t < jetzt - von_s or b.t > jetzt - bis_s or not _gueltig(a, b):
            continue
        sek += b.t - a.t
        rx += b.rx - a.rx
        tx += b.tx - a.tx
    if sek < MINDEST_S:
        return None
    return Rate(round(rx * 8 / sek / 1e6, 1), round(tx * 8 / sek / 1e6, 1), int(sek))
