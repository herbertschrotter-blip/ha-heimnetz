"""Netzkarte (1.9, Herbert 20.11.2026) – ohne Home Assistant.

Aus der Mesh-Liste der FRITZ!Box (X_AVM-DE_GetMeshListPath, JSON) je Gerät, wo und wie es hängt: an der Box oder an
einem Repeater, über Kabel (Buchse LAN 1–4 der Box, Geschwindigkeit), WLAN (2,4 / 5 / 6 GHz, Rate) oder Powerline.
Einen einfachen Switch sieht die Box nicht – hängen mehrere Geräte an derselben Buchse, steht dort einer.

Dazu die Lage der Punkte für die Sternkarte (die Seite zeichnet nur): FRITZ!Box in der Mitte, Ringe nach Anbindung
(Kabel innen, dann die WLAN-Bänder; schwächerer Empfang = weiter draußen; offline ganz außen), Sektoren nach Art des
Geräts, Switch zwischen Box und seinen Geräten, Repeater als eigener Knoten mit seinen Geräten rundherum.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .sprache import DE, t

BOX = "box"
BREITE, HOEHE = 440, 462
MITTE = (220.0, 252.0)
R_KABEL = 62.0
R_WLAN = (108.0, 150.0)  # innerster und äußerster WLAN-Ring
R_AUS = 178.0
R_SEKTOR = 200.0
R_SWITCH = 48.0
R_HINTER_SWITCH = 86.0
R_UM_REPEATER = 38.0
VPN = (84.0, 56.0)  # Tunnel-Knoten oben links, neben der Leitung ins Internet
WINKEL = (-62.0, 242.0)  # oben (−90°) bleibt frei für die Leitung ins Internet
LUECKE = 4.0
STREUUNG = 22.0  # so viel weiter draußen bei 0 % Empfang
_LAN = re.compile(r"LAN\s*:?\s*(\d+)", re.I)
_BAND = re.compile(r"(2G|5G|6G|2[,.]4|\b5\b|\b6\b)", re.I)


# ── Mesh-Liste lesen ──


@dataclass(frozen=True)
class Anschluss:
    an: str = BOX  # „box“ oder Kennung eines Repeaters („r1“ …)
    art: str = "lan"  # lan | wlan | plc
    port: int | None = None  # Buchse am Gerät, an dem es hängt
    band: str | None = None  # „2,4“, „5“, „6“
    mbit: int | None = None
    gast: bool = False


@dataclass(frozen=True)
class Repeater:
    id: str
    name: str  # Modell, gleiche Modelle nummeriert
    macs: tuple[str, ...]
    uplink: (
        Anschluss | None
    )  # wie er selbst angebunden ist (an der Box oder an einem anderen Repeater)


@dataclass(frozen=True)
class Netz:
    geraete: dict[str, Anschluss] = field(default_factory=dict)  # MAC (groß) → Anschluss
    repeater: tuple[Repeater, ...] = ()
    schnittstellen: tuple[
        str, ...
    ] = ()  # Namen der Schnittstellen von Box und Repeatern (für die Diagnose)


def _art(typ: object) -> str:
    s = str(typ or "").upper()
    return "wlan" if "WLAN" in s or "WIFI" in s else "plc" if "PLC" in s else "lan"


def _band(name: object, kanal: object) -> str | None:
    if m := _BAND.search(str(name or "")):
        b = m.group(1).upper().replace(".", ",")
        return {"2G": "2,4", "5G": "5", "6G": "6"}.get(b, b)
    if isinstance(kanal, int) and kanal > 0:
        return "2,4" if kanal <= 14 else "5"
    return None


def _mbit(link: Mapping[str, Any]) -> int | None:
    """Rate einer Verbindung in Mbit/s (die Box nennt kbit/s): die aktuelle, sonst die mögliche."""
    for a, b in (
        ("cur_data_rate_rx", "cur_data_rate_tx"),
        ("max_data_rate_rx", "max_data_rate_tx"),
    ):
        werte = [v for v in (link.get(a), link.get(b)) if isinstance(v, int | float) and v > 0]
        if werte:
            return round(max(werte) / 1000)
    return None


def mesh_lesen(roh: str | bytes) -> Netz:
    """Mesh-Liste → Anschluss je Gerät und die Repeater. Unlesbares ergibt ein leeres Netz."""
    try:
        daten = json.loads(roh)
    except ValueError, TypeError:
        return Netz()
    knoten = [
        k
        for k in (daten.get("nodes") if isinstance(daten, dict) else None) or []
        if isinstance(k, dict)
    ]
    rollen: dict[str, str] = {}  # uid → „box“ oder Kennung des Repeaters
    namen: dict[str, str] = {}
    gezaehlt: dict[str, int] = {}
    for k in knoten:
        if not k.get("is_meshed"):
            continue
        if k.get("mesh_role") == "master":
            rollen[str(k.get("uid"))] = BOX
        elif k.get("mesh_role") == "slave":
            modell = str(k.get("device_model") or "Repeater")
            gezaehlt[modell] = gezaehlt.get(modell, 0) + 1
            n = gezaehlt[modell]
            rid = f"r{len(namen) + 1}"
            rollen[str(k.get("uid"))] = rid
            namen[rid] = modell if n == 1 else f"{modell} {n}"
    schnitt: dict[
        str, tuple[str, dict[str, Any]]
    ] = {}  # uid der Schnittstelle → (uid des Knotens, Schnittstelle)
    for k in knoten:
        for i in k.get("node_interfaces") or []:
            if isinstance(i, dict):
                schnitt[str(i.get("uid"))] = (str(k.get("uid")), i)

    def anschluss(k: dict[str, Any]) -> Anschluss | None:
        """Beste bestehende Verbindung von Knoten k zu einem Mesh-Knoten (Box zuerst, dann höchste Rate)."""
        uid = str(k.get("uid"))
        beste: tuple[tuple[int, int], Anschluss] | None = None
        for i in k.get("node_interfaces") or []:
            if not isinstance(i, dict):
                continue
            for link in i.get("node_links") or []:
                if not isinstance(link, dict) or link.get("state") != "CONNECTED":
                    continue
                eins, zwei = str(link.get("node_1_uid")), str(link.get("node_2_uid"))
                gegen = zwei if eins == uid else eins
                if gegen == uid or gegen not in rollen:
                    continue
                gs_uid = str(
                    link.get("node_interface_2_uid" if eins == uid else "node_interface_1_uid")
                )
                gs = schnitt.get(gs_uid, ("", {}))[1]
                art = _art(gs.get("type") or i.get("type"))
                port = None
                if art == "lan" and (m := _LAN.search(str(gs.get("name") or ""))):
                    port = int(m.group(1))
                a = Anschluss(
                    an=rollen[gegen],
                    art=art,
                    port=port,
                    band=_band(gs.get("name"), gs.get("current_channel"))
                    if art == "wlan"
                    else None,
                    mbit=_mbit(link),
                    gast=str(gs.get("op_mode") or "").upper() == "AP_GUEST",
                )
                rang = (0 if rollen[gegen] == BOX else 1, -(a.mbit or 0))
                if beste is None or rang < beste[0]:
                    beste = (rang, a)
        return beste[1] if beste else None

    geraete: dict[str, Anschluss] = {}
    repeater: list[Repeater] = []
    for k in knoten:
        uid = str(k.get("uid"))
        macs = [k.get("device_mac_address")] + [
            i.get("mac_address") for i in k.get("node_interfaces") or [] if isinstance(i, dict)
        ]
        macs_ = tuple(dict.fromkeys(m.upper() for m in macs if isinstance(m, str) and m))
        rolle = rollen.get(uid)
        if rolle == BOX:
            continue
        if rolle is not None:
            repeater.append(Repeater(rolle, namen[rolle], macs_, anschluss(k)))
            continue
        a = anschluss(k)
        if a is not None:
            for mac in macs_:
                geraete[mac] = a
    namen_if = sorted(
        {
            str(i.get("name"))
            for k in knoten
            if str(k.get("uid")) in rollen
            for i in k.get("node_interfaces") or []
            if isinstance(i, dict) and i.get("name")
        }
    )
    return Netz(geraete, tuple(repeater), tuple(namen_if))


def diagnose(netz: Netz) -> dict[str, Any]:
    """Für den Diagnose-Download: nur Zählungen und Namen der Schnittstellen, keine Adressen."""
    zaehl: dict[str, int] = {}
    for a in netz.geraete.values():
        k = f"{a.an}:{a.art}:{a.port if a.port is not None else a.band or '-'}"
        zaehl[k] = zaehl.get(k, 0) + 1
    return {
        "anschluesse": dict(sorted(zaehl.items())),
        "repeater": [
            {
                "name": r.name,
                "uplink": f"{r.uplink.art}:{r.uplink.band or r.uplink.port or '-'}"
                if r.uplink
                else None,
            }
            for r in netz.repeater
        ],
        "schnittstellen": list(netz.schnittstellen),
    }


# ── Lage auf der Karte ──


@dataclass(frozen=True)
class Punkt:
    """Ein Gerät für die Karte (aus Gerätetabelle, WLAN-Tabelle und Art)."""

    id: str
    mac: str
    name: str
    symbol: str
    kat: str
    ip: str
    aktiv: bool
    zustand: str  # an | wackelt | neu | aus (Einstufung)
    art: str = ""  # aus der Gerätetabelle: LAN, WLAN, Powerline …
    band: str | None = None  # aus der WLAN-Tabelle
    signal: int | None = None
    mbit: int | None = None
    schwach: bool = False
    seit: float | None = None  # zuletzt online gegangen (VPN-Geräte)


def _p(r: float, w: float, um: tuple[float, float] = MITTE) -> tuple[float, float]:
    return (
        round(um[0] + r * math.cos(math.radians(w)), 1),
        round(um[1] + r * math.sin(math.radians(w)), 1),
    )


def _rate(mbit: int | None, sprache: str) -> str:
    if not mbit:
        return ""
    return t("{n} Gbit/s", sprache, n=f"{mbit / 1000:g}") if mbit >= 1000 else f"{mbit} Mbit/s"


def _band_text(band: str, sprache: str) -> str:
    return band if sprache == DE else band.replace(",", ".")


def _baender(punkte: Iterable[Punkt], netz: Netz) -> list[str]:
    da = {p.band for p in punkte if p.band}
    da |= {a.band for a in netz.geraete.values() if a.band}
    return [b for b in ("6", "5", "2,4") if b in da] or ["5", "2,4"]


ZEICHEN_SEKTOR = (
    7.6  # Breite eines Großbuchstabens der Sektor-Schrift samt Sperrung (8,5 px, 1,8 px Abstand)
)


def _im_bild(x: float, name: str) -> float:
    """Mitte einer Sektor-Beschriftung so schieben, dass der Text ganz in der Karte bleibt (am Handy nichts abgeschnitten)."""
    halb = len(name) * ZEICHEN_SEKTOR / 2 + 4
    if 2 * halb >= BREITE:  # breiter als die Karte: mittig
        return BREITE / 2
    return round(min(max(x, halb), BREITE - halb), 1)


def zeichnen(
    punkte: list[Punkt],
    netz: Netz,
    kategorien: list[tuple[str, str]],
    sprache: str = DE,
    vpn: Iterable[Punkt] = (),
) -> dict[str, Any]:
    """Lage aller Punkte, Ringe, Sektoren, Switches und Repeater in einem Feld von BREITE × HOEHE."""
    rep_macs = {m: r.id for r in netz.repeater for m in r.macs}
    rep_ids = {r.id for r in netz.repeater}
    liste = [p for p in punkte if p.mac.upper() not in rep_macs]

    def anschluss(p: Punkt) -> Anschluss | None:
        return netz.geraete.get(p.mac.upper()) if p.aktiv else None

    def am_repeater(p: Punkt) -> str | None:
        a = anschluss(p)
        return a.an if a and a.an in rep_ids else None

    def kabel(p: Punkt) -> bool:
        a = anschluss(p)
        if a is not None:
            return a.art in ("lan", "plc")
        return p.art.split(" ")[0] in ("LAN", "Powerline")

    def band(p: Punkt) -> str | None:
        a = anschluss(p)
        return (a.band if a and a.band else None) or p.band

    baender = _baender(liste, netz)
    schritt = (R_WLAN[1] - R_WLAN[0]) / max(1, len(baender) - 1)
    r_band = {b: R_WLAN[0] + i * schritt for i, b in enumerate(baender)}

    # Sektoren: Geräte an der Box (und offline) nach Art, Breite nach Anzahl
    an_box = [p for p in liste if not am_repeater(p)]
    reihe = [k for k, _ in kategorien]
    kats = sorted(
        {p.kat for p in an_box}, key=lambda k: (reihe.index(k) if k in reihe else len(reihe), k)
    )
    if netz.repeater and "netz" not in kats:
        kats = sorted([*kats, "netz"], key=lambda k: reihe.index(k) if k in reihe else len(reihe))
    gewicht = {k: sum(1 for p in an_box if p.kat == k) + 0.6 for k in kats}
    frei = WINKEL[1] - WINKEL[0] - LUECKE * len(kats)
    summe = sum(gewicht.values()) or 1
    sektoren: list[dict[str, Any]] = []
    winkel: dict[str, float] = {}
    start = WINKEL[0]
    text = dict(kategorien)
    for k in kats:
        breite = frei * gewicht[k] / summe
        drin = sorted((p for p in an_box if p.kat == k), key=lambda p: (kabel(p), p.name.lower()))
        for i, p in enumerate(drin):
            winkel[p.id] = start + (i + 0.5) * breite / len(drin)
        mitte = start + breite / 2
        x, y = _p(R_SEKTOR, mitte)
        name = text.get(k, k)
        sektoren.append({"kat": k, "name": name, "x": _im_bild(x, name), "y": y, "w": mitte})
        start += breite + LUECKE

    n_online = sum(1 for p in liste if p.aktiv)
    dot = 11 if n_online <= 24 else 9 if n_online <= 40 else 7
    geraete, aus, switche, repeater = [], [], [], []

    def eintrag(
        p: Punkt, x: float, y: float, von: tuple[float, float], ueber: str, text_: str
    ) -> dict[str, Any]:
        a = anschluss(p)
        return {
            "id": p.id,
            "name": p.name,
            "symbol": p.symbol,
            "ip": p.ip,
            "kat": p.kat,
            "x": x,
            "y": y,
            "vx": von[0],
            "vy": von[1],
            "kabel": kabel(p),
            "ueber": ueber,
            "zustand": "schwach" if p.schwach and p.zustand == "an" else p.zustand,
            "anbindung": text_,
            "signal": p.signal,
            "mbit": (a.mbit if a and a.mbit else None) or p.mbit,
            "gast": bool(a and a.gast),
        }

    def wlan_text(p: Punkt, am_rep: bool) -> str:
        b = band(p)
        teile = [f"WLAN {_band_text(b, sprache)} GHz" if b else "WLAN"]
        if p.signal is not None:
            teile.append(f"{p.signal} %")
        a = anschluss(p)
        if r := _rate((a.mbit if a and a.mbit else None) or p.mbit, sprache):
            teile.append(r)
        if am_rep:
            teile.append(t("Repeater", sprache))
        return " · ".join(teile)

    # Kabel: je Buchse der Box; mehrere Geräte an einer Buchse → Switch
    buchsen: dict[int, list[Punkt]] = {}
    for p in an_box:
        a = anschluss(p)
        if p.aktiv and kabel(p) and a is not None and a.an == BOX and a.port is not None:
            buchsen.setdefault(a.port, []).append(p)
    hinter_switch = {p.id for g in buchsen.values() if len(g) > 1 for p in g}
    for port, gruppe in sorted(buchsen.items()):
        if len(gruppe) < 2:
            continue
        w = sum(winkel[p.id] for p in gruppe) / len(gruppe)
        sx, sy = _p(R_SWITCH, w)
        mbit = max((getattr(anschluss(p), "mbit", None) or 0) for p in gruppe) or None
        switche.append(
            {
                "id": f"s{port}",
                "port": port,
                "x": sx,
                "y": sy,
                "n": len(gruppe),
                "mbit": mbit,
                "text": t("Switch an LAN {port}", sprache, port=port),
            }
        )
        for i, p in enumerate(sorted(gruppe, key=lambda p: winkel[p.id])):
            wi = w + (i - (len(gruppe) - 1) / 2) * min(30.0, 150.0 / len(gruppe))
            x, y = _p(R_HINTER_SWITCH, wi)
            geraete.append(
                {"switch": f"s{port}"}
                | eintrag(
                    p,
                    x,
                    y,
                    (sx, sy),
                    "switch",
                    " · ".join(
                        x_
                        for x_ in (
                            t("Switch an LAN {port}", sprache, port=port),
                            _rate(getattr(anschluss(p), "mbit", None), sprache),
                        )
                        if x_
                    ),
                )
            )

    for p in an_box:
        w = winkel[p.id]
        if not p.aktiv:
            x, y = _p(R_AUS, w)
            aus.append({"id": p.id, "name": p.name, "ip": p.ip, "x": x, "y": y})
            continue
        if p.id in hinter_switch:
            continue
        if kabel(p):
            a = anschluss(p)
            x, y = _p(R_KABEL, w)
            buchse = f"LAN {a.port}" if a and a.port is not None else t("Kabel", sprache)
            e = eintrag(
                p,
                x,
                y,
                MITTE,
                "box",
                " · ".join(s for s in (buchse, _rate(a.mbit if a else None, sprache)) if s),
            )
            if a and a.port is not None:
                e["port"] = a.port
                e["px"], e["py"] = _p(36.0, w)
            geraete.append(e)
            continue
        b = band(p)
        r = r_band.get(b or "", r_band[baender[0]]) + (
            (100 - p.signal) / 100 * STREUUNG if p.signal is not None else 0
        )
        x, y = _p(r, w)
        geraete.append(eintrag(p, x, y, MITTE, "box", wlan_text(p, False)))

    # Repeater: im Sektor „netz“ auf dem Ring seiner Anbindung, seine Geräte rundherum
    netz_w = next((s["w"] for s in sektoren if s["kat"] == "netz"), 170.0)
    for j, rep in enumerate(netz.repeater):
        w = netz_w + (j - (len(netz.repeater) - 1) / 2) * 24
        u = rep.uplink
        r = (
            R_KABEL + 10
            if u and u.art in ("lan", "plc")
            else r_band.get((u.band if u else None) or "5", R_WLAN[0])
        )
        rx, ry = _p(min(r, R_WLAN[0] + 10), w)
        kinder = [p for p in liste if am_repeater(p) == rep.id]
        anb = (
            (f"WLAN {_band_text(u.band, sprache)} GHz" if u.band else "WLAN")
            if u and u.art == "wlan"
            else (t("Kabel", sprache) if u and u.art == "lan" else "Powerline" if u else "")
        )
        repeater.append(
            {
                "id": rep.id,
                "name": rep.name,
                "x": rx,
                "y": ry,
                "n": len(kinder),
                "kabel": bool(u and u.art != "wlan"),
                "mbit": u.mbit if u else None,
                "text": " · ".join(s for s in (anb, _rate(u.mbit if u else None, sprache)) if s),
            }
        )
        for i, p in enumerate(sorted(kinder, key=lambda p: p.name.lower())):
            reihe_, pos = divmod(i, 7)
            n_reihe = min(7, len(kinder) - reihe_ * 7)
            wi = w + (pos - (n_reihe - 1) / 2) * 34
            x, y = _p(R_UM_REPEATER + reihe_ * 22, wi, (rx, ry))
            text_ = (
                " · ".join((t("Kabel", sprache), t("Repeater", sprache)))
                if kabel(p)
                else wlan_text(p, True)
            )
            geraete.append(eintrag(p, x, y, (rx, ry), "repeater", text_))

    # VPN (WireGuard): eigener Tunnel-Knoten oben links, die Geräte rundherum (nur die verbundenen)
    tunnel = sorted((p for p in vpn if p.aktiv), key=lambda p: p.name.lower())
    vpn_geraete = []
    for i, p in enumerate(tunnel):
        reihe_, pos = divmod(i, 5)
        n_reihe = min(5, len(tunnel) - reihe_ * 5)
        wi = 150 + (pos - (n_reihe - 1) / 2) * (55 if n_reihe < 3 else 110 / (n_reihe - 1))
        x, y = _p(R_UM_REPEATER + reihe_ * 22, wi, VPN)
        vpn_geraete.append(
            {
                "id": p.id,
                "name": p.name,
                "symbol": p.symbol,
                "ip": p.ip,
                "kat": p.kat,
                "x": x,
                "y": y,
                "vx": VPN[0],
                "vy": VPN[1],
                "kabel": False,
                "ueber": "vpn",
                "zustand": p.zustand,
                "anbindung": t("VPN (WireGuard) · über das Internet", sprache),
                "signal": None,
                "mbit": None,
                "gast": False,
                "seit": p.seit,
            }
        )

    ringe = [{"r": R_KABEL, "name": t("Kabel", sprache)}]
    ringe += [{"r": round(r_band[b], 1), "name": f"{_band_text(b, sprache)} GHz"} for b in baender]
    ringe.append({"r": R_AUS, "name": t("offline", sprache)})
    auff = sum(1 for g in geraete if g["zustand"] in ("wackelt", "schwach"))
    return {
        "breite": BREITE,
        "hoehe": HOEHE,
        "mitte": {"x": MITTE[0], "y": MITTE[1]},
        "dot": dot,
        "ringe": ringe,
        "sektoren": [{k: s[k] for k in ("name", "x", "y")} for s in sektoren],
        "switche": switche,
        "repeater": repeater,
        "geraete": geraete,
        "aus": aus,
        "vpn": {"x": VPN[0], "y": VPN[1], "geraete": vpn_geraete} if vpn_geraete else None,
        "zahlen": {
            "online": len(geraete),
            "offline": len(aus),
            "auffaellig": auff,
            "neu": sum(1 for g in geraete if g["zustand"] == "neu"),
            "vpn": len(vpn_geraete),
        },
    }
