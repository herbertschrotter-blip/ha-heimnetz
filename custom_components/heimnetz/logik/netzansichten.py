"""Weitere Ansichten der Netzkarte (1.10, abgenommen 21.11.2026): Datenfluss und WLAN-Radar.

Beide rechnen aus dem fertigen Ergebnis von `netzkarte.zeichnen` (Geräte mit Anbindung, Band, Rate, Empfang, Zustand);
die Seite zeichnet nur. Datenfluss: Internet → FRITZ!Box → Anbindung → Gerät, Breite = Geschwindigkeit der Verbindung
(die Box nennt keinen Durchsatz je Gerät, nur für den ganzen Anschluss). Radar: Abstand von der Mitte = Empfang,
Winkel wie auf der Karte, das Aufleuchten folgt dem kreisenden Strahl.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

from .sprache import DE, merke, t

# ── Datenfluss ──
F_BREITE = 440.0
F_X = {"internet": 26.0, "box": 112.0, "gruppe": 214.0, "geraet": 300.0}
F_ZEILE = 26.0  # Abstand der Geräte untereinander
F_RAND = 24.0
F_LUECKE = 16.0  # Luft zwischen zwei Gruppen (Platz für den Namen der Gruppe)
F_MIN_HOEHE = 320.0
F_LANGSAM = 20  # Mbit/s: darunter zählt eine Funkverbindung als langsam

# ── Radar ──
R_MITTE = (220.0, 240.0)
R_RADIUS = 190.0
R_UMLAUF = 6.0  # Sekunden für eine Runde des Strahls
R_INNEN = 0.12  # Anteil des Radius für 100 % Empfang (Platz für die Box in der Mitte)

AUFFAELLIG = ("schwach", "wackelt")
# Ringe = Grenzen in % Empfang, je Ring der Name der Zone innen; „mäßig“ endet an der Schwach-Grenze der Einstellungen
RINGE = ((merke("sehr gut"), 80), (merke("gut"), 60), (merke("mäßig"), None), (merke("schwach"), 0))


def _abstand(signal: float) -> float:
    """Anteil des Radius für einen Empfang in %: 100 % innen am Rand der Box, 0 % fast ganz außen."""
    return R_INNEN + (1 - max(0.0, min(100.0, signal)) / 100) * (1 - R_INNEN - 0.02)


def _band_text(band: str, sprache: str) -> str:
    return band if sprache == DE else band.replace(",", ".")


def _faden(mbit: int | None) -> float:
    """Breite eines Bands in px: Wurzel der Geschwindigkeit, damit 6 Mbit/s neben 1 Gbit/s sichtbar bleibt."""
    return round(max(1.6, math.sqrt(mbit) * 0.62), 1) if mbit else 1.6


def _gruppe(g: dict[str, Any]) -> str:
    if g.get("ueber") == "vpn":
        return "vpn"
    if g.get("rep"):
        return f"rep:{g['rep']}"
    if g.get("kabel"):
        return "kabel"
    return f"wlan:{g.get('band') or ''}"


def fluss(
    karte: dict[str, Any],
    down_jetzt: float | None,
    tarif_down: float | None,
    sprache: str = DE,
) -> dict[str, Any]:
    """Datenfluss: Lage der Gruppen (Kabel, je Band, je Repeater, VPN) und Geräte samt Breite der Bänder."""
    geraete = [*karte.get("geraete", []), *((karte.get("vpn") or {}).get("geraete", []))]
    rep_name = {r["id"]: r["name"] for r in karte.get("repeater", [])}
    reihenfolge = ["kabel", "wlan:6", "wlan:5", "wlan:2,4", "wlan:"]
    reihenfolge += [f"rep:{r}" for r in rep_name] + ["vpn"]

    def name(k: str) -> tuple[str, str]:
        if k == "kabel":
            return t("Kabel", sprache), "kabel"
        if k == "vpn":
            return "VPN", "vpn"
        if k.startswith("rep:"):
            return rep_name.get(k[4:], t("Repeater", sprache)), "rep"
        b = k[5:]
        return (f"{_band_text(b, sprache)} GHz" if b else "WLAN"), b or "wlan"

    reihe: list[dict[str, Any]] = []
    gruppen: list[dict[str, Any]] = []
    for k in reihenfolge:
        drin = sorted(
            (g for g in geraete if _gruppe(g) == k),
            key=lambda g: (-(g.get("mbit") or 0), g["name"].lower()),
        )
        if not drin:
            continue
        erste = len(reihe)
        for g in drin:
            reihe.append(
                {
                    "id": g["id"],
                    "name": g["name"],
                    "symbol": g["symbol"],
                    "mbit": g.get("mbit"),
                    "zustand": g["zustand"],
                    "y": F_RAND + len(reihe) * F_ZEILE + len(gruppen) * F_LUECKE + F_ZEILE / 2,
                    "breite": _faden(g.get("mbit")),
                    "gruppe": k,
                    "kabel": bool(g.get("kabel")),
                }
            )
        summe = sum(g.get("mbit") or 0 for g in drin)
        text_, farbe = name(k)
        gruppen.append(
            {
                "id": k,
                "name": text_,
                "farbe": farbe,
                "y": round((reihe[erste]["y"] + reihe[-1]["y"]) / 2, 1),
                "breite": round(min(30.0, _faden(summe) * 1.1), 1),
                "n": len(drin),
            }
        )
    hoehe = max(F_MIN_HOEHE, 2 * F_RAND + len(reihe) * F_ZEILE + len(gruppen) * F_LUECKE)
    funk = [
        g
        for g in reihe
        if g["gruppe"].startswith(("wlan:", "rep:")) and not g["kabel"] and g["mbit"]
    ]
    duennster = min(funk, key=lambda g: g["mbit"], default=None)
    langsam = [
        g for g in reihe if g["zustand"] in AUFFAELLIG or (g in funk and g["mbit"] < F_LANGSAM)
    ]
    gname = {g["id"]: g["name"] for g in gruppen}
    return {
        "breite": F_BREITE,
        "hoehe": hoehe,
        "x": F_X,
        "mitte": hoehe / 2,
        "internet": {
            "down": round(down_jetzt, 1) if down_jetzt is not None else None,
            "tarif": tarif_down,
            "anteil": round(100 * down_jetzt / tarif_down)
            if down_jetzt is not None and tarif_down
            else None,
            "breite": round(min(26.0, max(4.0, math.sqrt(down_jetzt or 0) * 2.2)), 1),
        },
        "gruppen": gruppen,
        "geraete": reihe,
        "langsam": len(langsam),
        "duennster": {
            "name": duennster["name"],
            "mbit": duennster["mbit"],
            "wo": gname[duennster["gruppe"]],
        }
        if duennster
        else None,
    }


def radar(
    karte: dict[str, Any],
    kanaele: Iterable[tuple[str, int | None, bool | None]],
    grenze: int = 40,
    sprache: str = DE,
) -> dict[str, Any]:
    """WLAN-Radar: je Funkgerät mit bekanntem Empfang Lage (Abstand = Empfang, Winkel wie auf der Karte) und Takt."""
    mx, my = karte["mitte"]["x"], karte["mitte"]["y"]
    punkte, ohne = [], 0
    for g in karte.get("geraete", []):
        if g.get("kabel"):
            continue
        if g.get("signal") is None:
            ohne += 1
            continue
        # Winkel wie auf der Karte; Geräte am Repeater nehmen den Winkel des Repeaters
        bx, by = (g["vx"], g["vy"]) if g.get("rep") else (g["x"], g["y"])
        winkel = math.degrees(math.atan2(by - my, bx - mx)) % 360
        r = R_RADIUS * _abstand(g["signal"])
        x = R_MITTE[0] + r * math.cos(math.radians(winkel))
        y = R_MITTE[1] + r * math.sin(math.radians(winkel))
        farbe = "schwach" if g["zustand"] in AUFFAELLIG else (g.get("band") or "wlan")
        punkte.append(
            {
                "id": g["id"],
                "name": g["name"],
                "symbol": g["symbol"],
                "signal": g["signal"],
                "band": g.get("band"),
                "zustand": g["zustand"],
                "farbe": farbe,
                "neu": g["zustand"] == "neu",
                "x": round(x, 1),
                "y": round(y, 1),
                "links": x
                > R_MITTE[0] + R_RADIUS * 0.55,  # Name links vom Punkt, sonst ragt er hinaus
                "takt": round(winkel / 360 * R_UMLAUF - R_UMLAUF, 2),
            }
        )
    je_band: dict[str, int] = {}
    for p in punkte:
        if p["band"]:
            je_band[p["band"]] = je_band.get(p["band"], 0) + 1
    rand = sorted((p for p in punkte if p["signal"] < grenze), key=lambda p: p["signal"])[:2]
    ringe: list[dict[str, Any]] = []
    for n, wert in RINGE:
        if wert and wert <= grenze:
            continue  # Schwach-Grenze liegt über dieser Zone: sie fällt weg
        w = grenze if wert is None else wert
        ringe.append({"r": round(R_RADIUS * _abstand(w), 1), "name": t(n, sprache)})
    return {
        "breite": 440.0,
        "hoehe": 480.0,
        "mitte": {"x": R_MITTE[0], "y": R_MITTE[1]},
        "radius": R_RADIUS,
        "umlauf": R_UMLAUF,
        "ringe": ringe,
        "geraete": punkte,
        "ohne_empfang": ohne,
        "kanaele": [
            {
                "band": f"{_band_text(b, sprache)} GHz",
                "kanal": k,
                "auto": bool(a),
                "n": je_band.get(b, 0),
            }
            for b, k, a in kanaele
        ],
        "rand": [{"name": p["name"], "signal": p["signal"]} for p in rand],
    }
