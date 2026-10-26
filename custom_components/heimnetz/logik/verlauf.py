"""Verlauf je Gerät aus dem Journal: online/offline-Abschnitte, Streifen für die Geräteliste, Einstufung.

Übernommen aus Sammler (build_verlauf) und Geräte-Karte (abschnitte) des Altbestands. Das Journal enthält je Gerät die
Ereignisse neu, online, offline, ip_wechsel, anschluss.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

WECHSEL = ("online", "offline", "neu")
WACKELT_AB = 3  # so viele Abbrüche in 24 h machen ein Gerät „auffällig“
AN, AUS, LUECKE = "an", "aus", "luecke"


def geraete_id(mac: str, salz: str) -> str:
    """Kennung für die Oberfläche statt der Hardware-Adresse. Mit einem zufälligen Salz je Installation – ohne
    ließe sie sich durch Durchprobieren aller Adressen zurückrechnen."""
    return hashlib.sha256(f"{salz}:{mac.upper()}".encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Abschnitt:
    von: float
    bis: float
    an: bool


def vorher(letzter_davor: str | None, erstes_im_fenster: str | None, aktiv: bool) -> bool | None:
    """Zustand am Anfang des Fensters. None = keine Aufzeichnung davor (z. B. neues Gerät)."""
    if letzter_davor is not None:
        return letzter_davor != "offline"
    if erstes_im_fenster is not None:
        return {"offline": True, "online": False}.get(erstes_im_fenster)
    return aktiv


def abschnitte(
    start: bool | None, ereignisse: Sequence[tuple[float, str]], ab: float, jetzt: float
) -> list[Abschnitt]:
    """Ereignisse (älteste zuerst) → online/offline-Abschnitte von `ab` bis `jetzt`; ohne Aufzeichnung bleibt eine Lücke."""
    out, t, z = [], ab, start
    for et, art in ereignisse:
        if art not in WECHSEL:
            continue
        et = max(ab, et)
        if z is not None and et > t:
            out.append(Abschnitt(t, et, z))
        t, z = et, art != "offline"
    if z is not None and jetzt > t:
        out.append(Abschnitt(t, jetzt, z))
    return out


def online_s(teile: Sequence[Abschnitt], von: float, bis: float) -> float:
    return sum(max(0.0, min(a.bis, bis) - max(a.von, von)) for a in teile if a.an)


def streifen(teile: Sequence[Abschnitt], ab: float, jetzt: float, felder: int = 48) -> list[str]:
    """Fenster in `felder` gleiche Stücke: an (mindestens halb online), aus, lücke (keine Aufzeichnung)."""
    breite = (jetzt - ab) / felder
    out = []
    for i in range(felder):
        von, bis = ab + i * breite, ab + (i + 1) * breite
        bekannt = sum(max(0.0, min(a.bis, bis) - max(a.von, von)) for a in teile)
        if bekannt < breite / 2:
            out.append(LUECKE)
        else:
            out.append(AN if online_s(teile, von, bis) >= bekannt / 2 else AUS)
    return out


def einstufung(aktiv: bool, abbrueche_24h: int, neu_24h: bool) -> str:
    """neu, wackelt, an oder aus – für Abzeichen und Filter „Auffällig“."""
    if neu_24h:
        return "neu"
    if abbrueche_24h >= WACKELT_AB:
        return "wackelt"
    return AN if aktiv else AUS


@dataclass(frozen=True)
class Tag:
    von: float
    bis: float
    streifen: tuple[str, ...]
    online_s: float
    bekannt_s: float = 0.0  # aufgezeichnete Zeit (ohne Lücken)


def tage(
    start: bool | None,
    ereignisse: Sequence[tuple[float, str]],
    grenzen: Sequence[tuple[float, float]],
    jetzt: float,
    felder: int = 48,
) -> list[Tag]:
    """Je Tag (von, bis = lokale Mitternacht, älteste zuerst) Streifen und Online-Zeit. Der Zustand am Ende eines Tages
    ist der Anfang des nächsten; `start` gilt vor dem ersten Tag. Der heutige Tag endet bei `jetzt`, der Rest bleibt
    Lücke."""
    out, zustand = [], start
    for von, bis in grenzen:
        im = [(t, a) for t, a in ereignisse if von <= t < bis]
        ende = min(bis, jetzt)
        teile = abschnitte(zustand, im, von, ende) if ende > von else []
        out.append(
            Tag(
                von,
                bis,
                tuple(streifen(teile, von, bis, felder)),
                online_s(teile, von, ende),
                sum(a.bis - a.von for a in teile),
            )
        )
        for _, art in im:
            if art in WECHSEL:
                zustand = art != "offline"
    return out


def online_anteil(tage_: Sequence[Tag]) -> float | None:
    """Anteil online an der aufgezeichneten Zeit – Lücken (noch kein Eintrag, z. B. neues Gerät) zählen nicht."""
    dauer = sum(t.bekannt_s for t in tage_)
    return sum(t.online_s for t in tage_) / dauer if dauer else None
