"""Diagnose-Log: hält fest, wann welches Gerät wo und wie im Netz war, dazu Internet, Box und Modem – ohne Home Assistant.

Zweck: viele Meldungen „offline / wieder online“ einordnen. Die Geräteliste der Box zeigt, ob ein Gerät weg war; die
Zeilen rundherum (Abrufe, Größe der Liste, Protokoll der Box, gesendete Warnungen) zeigen, ob das echt war oder an der
Abfrage lag. Aufgezeichnet wird, was sich ändert, dazu alle 10 Minuten ein Gesamtstand; `Schreiber` hält den Vergleich
nur im Speicher. Die Einträge bleiben 7 Tage lokal. In der Datei stehen keine Namen, Hardware- oder IP-Adressen.
"""

from __future__ import annotations

import ipaddress
import math
import re
from bisect import bisect_left, bisect_right
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, tzinfo
from typing import Any

from .geraete import OHNE_NAMEN, anzeigename, gruppen_text
from .sprache import DE, merke, t
from .warnungen import GESCHRUMPFT, Meldung, dauer_text
from .werte import ohne_mac

TAGE = 7
AUFBEWAHREN_S = TAGE * 86_400
STAND_S = 600  # so oft ein Gesamtstand
LUECKE_S = 180  # Abstand zweier Abrufe, ab dem er als Lücke gilt (Takt: 60 s)
HAEUFUNG_S = 120  # so nah beieinander zählen Geräte als „zugleich weg“
HAEUFUNG_AB = 3  # so viele Geräte
DAUERHAFT = 5  # so viele Abrufe in Folge kleiner: die Liste gilt wieder (aufgeräumt, keine Lücke)
ZEILEN_SEITE = 500  # so viele Einträge bekommt die Seite, die Datei alle
BOX_ZEILEN = (
    "wlan",
    "internet",
)  # andere Gruppen des Box-Protokolls enthalten Rufnummern und Benutzernamen

GERAET, INTERNET, MODEM, BOX, STAND, WARNUNG = (
    "geraet",
    "internet",
    "modem",
    "box",
    "stand",
    "warnung",
)
ANZEIGE = {
    GERAET: merke("Gerät"),
    INTERNET: merke("Internet"),
    MODEM: merke("Modem"),
    BOX: merke("Box"),
    STAND: merke("Stand"),
    WARNUNG: merke("Warnung"),
}
AUFFAELLIG = frozenset(
    {"weg", "raus", "internet_weg", "box_weg", "liste", "luecke", "netz", "warnung"}
)
_IP4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
_IP6 = re.compile(r"(?<![\w:.])[0-9a-fA-F:]*:[0-9a-fA-F:]*:[0-9a-fA-F:]*(?![\w:])")
UNGEFAEHR = ("", "WLAN")  # Verbindung ohne bekanntes Band: kein Wechsel
ZUSTAENDE = ("internet_weg", "internet_da", "box_weg", "box_da")
MELDUNG = {
    "offline": merke("offline"),
    "online": merke("wieder online"),
    "neu": merke("neues Gerät"),
    "internet": merke("Internet oder FRITZ!Box war weg"),
}


@dataclass(frozen=True)
class Geraetstand:
    """Ein Gerät in einem Abruf. `verbindung` = Gruppe (geraete.verbindung), `knoten` = Box oder Repeater (nur bekannt,
    wenn die Mesh-Liste es nennt), `mesh` = das Gerät ist selbst ein Mesh-Gerät."""

    schluessel: str
    name: str
    aktiv: bool
    verbindung: str = ""
    knoten: str = ""
    signal: int | None = None
    mbit: int | None = None
    mesh: bool = False


@dataclass(frozen=True)
class Aufnahme:
    """Ein Abruf, soweit das Log ihn braucht."""

    t: float
    box: bool
    internet: bool
    geraete: tuple[Geraetstand, ...] = ()
    netz: str = ""
    zelle: str = ""
    pegel: int | None = None
    kanaele: str = ""
    warnungen: tuple[tuple[Meldung, bool], ...] = ()  # (Meldung, jetzt verschickt)
    box_zeilen: tuple[tuple[float | None, str, str], ...] = ()  # (Zeit laut Box, Gruppe, Text)


@dataclass(frozen=True)
class Eintrag:
    t: float
    art: str
    schluessel: str
    daten: dict[str, Any]


@dataclass
class Schreiber:
    """Vergleicht jeden Abruf mit dem vorigen. Nach einem Neustart beginnt er mit „Aufzeichnung beginnt“."""

    alt: dict[str, Geraetstand] = field(default_factory=dict)
    weg_seit: dict[str, float] = field(default_factory=dict)
    zuletzt: Aufnahme | None = None
    stand_t: float = 0.0
    voll: int = 0
    unbrauchbar: int = 0  # Abrufe in Folge mit unbrauchbarer Liste

    def schritt(self, a: Aufnahme) -> list[Eintrag]:
        v = self.zuletzt
        out: list[Eintrag] = []

        def dazu(art: str, ereignis: str, schluessel: str = "", **daten: Any) -> None:
            out.append(Eintrag(a.t, art, schluessel, {"ereignis": ereignis, **daten}))

        def box_zeile(t_: float | None, gruppe: str, text_: str) -> None:
            daten = {"ereignis": "zeile", "gruppe": gruppe, "text": text_}
            out.append(Eintrag(a.t if t_ is None else t_, BOX, "", daten))

        if v is None:
            dazu(BOX, "start")
        else:
            if a.t - v.t > LUECKE_S:
                dazu(BOX, "luecke", dauer_s=a.t - v.t)
            if a.box != v.box:
                dazu(BOX, "box_da" if a.box else "box_weg")
            if a.internet != v.internet:
                dazu(INTERNET, "internet_da" if a.internet else "internet_weg")
            if a.netz and v.netz and a.netz != v.netz:
                dazu(MODEM, "netz", von=v.netz, nach=a.netz)
            if a.zelle and v.zelle and a.zelle != v.zelle:
                dazu(MODEM, "zelle", von=v.zelle, nach=a.zelle)
        liste = {g.schluessel: g for g in a.geraete}
        brauchbar = bool(liste) and not (self.voll and len(liste) < self.voll * GESCHRUMPFT)
        if a.box and liste and not brauchbar and self.unbrauchbar + 1 >= DAUERHAFT:
            brauchbar, self.voll = True, 0  # dauerhaft kleiner: die Liste wurde aufgeräumt
        if a.box and not brauchbar and not self.unbrauchbar:
            dazu(BOX, "liste", n=len(liste), voll=self.voll)
        self.unbrauchbar = self.unbrauchbar + 1 if a.box and not brauchbar else 0
        if a.box and brauchbar:
            if self.alt:
                self._geraete(a.t, liste, dazu)
            self.alt, self.voll = liste, len(liste)
        for m, verschickt in a.warnungen:
            dazu(
                WARNUNG,
                "warnung",
                m.schluessel,
                name=m.name,
                meldung=m.art,
                dauer_s=m.dauer_s,
                verschickt=verschickt,
            )
        for zeit_, gruppe, text_ in a.box_zeilen:
            if gruppe in BOX_ZEILEN:
                box_zeile(zeit_, gruppe, text_)
        if a.t - self.stand_t >= STAND_S:
            self.stand_t = a.t
            dazu(
                STAND,
                "stand",
                internet=a.internet,
                box=a.box,
                online=sum(1 for g in a.geraete if g.aktiv),
                gesamt=len(a.geraete),
                netz=a.netz,
                pegel=a.pegel,
                kanaele=a.kanaele,
            )
        self.zuletzt = a
        return out

    def _geraete(self, jetzt: float, liste: dict[str, Geraetstand], dazu: Any) -> None:
        for k, g in liste.items():
            a = self.alt.get(k)
            if a is None:
                dazu(GERAET, "neu", k, name=g.name, verbindung=g.verbindung, mesh=g.mesh)
            elif a.aktiv and not g.aktiv:
                self.weg_seit[k] = jetzt
                dazu(
                    GERAET,
                    "weg",
                    k,
                    name=g.name,
                    verbindung=a.verbindung,
                    knoten=a.knoten,
                    signal=a.signal,
                    mbit=a.mbit,
                    mesh=g.mesh,
                )
            elif g.aktiv and not a.aktiv:
                seit = self.weg_seit.pop(k, None)
                dazu(
                    GERAET,
                    "da",
                    k,
                    name=g.name,
                    verbindung=g.verbindung,
                    knoten=g.knoten,
                    dauer_s=None if seit is None else jetzt - seit,
                    mesh=g.mesh,
                )
            elif g.aktiv and a.aktiv:
                # unbekannt ist kein Wechsel: Band fehlt bei einem Lesefehler, der Knoten bis zum nächsten Mesh-Abruf
                band = (
                    a.verbindung != g.verbindung
                    and a.verbindung not in UNGEFAEHR
                    and g.verbindung not in UNGEFAEHR
                )
                knoten = bool(a.knoten and g.knoten and a.knoten != g.knoten)
                if band or knoten:
                    dazu(
                        GERAET,
                        "wechsel",
                        k,
                        name=g.name,
                        von=a.verbindung if band else "",
                        nach=g.verbindung if band else "",
                        knoten_von=a.knoten if knoten else "",
                        knoten_nach=g.knoten if knoten else "",
                        mesh=g.mesh,
                    )
        for k, a in self.alt.items():
            if k not in liste:
                dazu(GERAET, "raus", k, name=a.name, mesh=a.mesh)


# ── Lesen ──
def _name(d: dict[str, Any], s: str) -> str:
    return anzeigename(str(d.get("name") or ""), s)


def _verbindung(wert: Any, s: str) -> str:
    return gruppen_text(str(wert), s) if wert else ""


def _kette(*teile: Any) -> str:
    return " · ".join(str(x) for x in teile if x)


def _pfeil(von: str, nach: str) -> str:
    return f"{von or '–'} → {nach or '–'}" if von != nach else ""


def _prozent(wert: Any) -> str:
    return f"{wert} %" if wert is not None else ""


def _mbit(wert: Any) -> str:
    return f"{wert} Mbit/s" if wert is not None else ""


def _ja_nein(wert: Any, s: str) -> str:
    return t("ok", s) if wert else t("gestört", s)


def _geraet_text(d: dict[str, Any], s: str) -> tuple[str, str]:
    e = d["ereignis"]
    mesh = "Repeater" if d.get("mesh") else ""
    if e == "weg":
        war = _kette(
            _verbindung(d.get("verbindung"), s),
            d.get("knoten"),
            _prozent(d.get("signal")),
            _mbit(d.get("mbit")),
        )
        return t("weg", s), _kette(mesh, t("war {wo}", s, wo=war) if war else "")
    if e == "da":
        dauer = d.get("dauer_s")
        return t("wieder da", s), _kette(
            mesh,
            _verbindung(d.get("verbindung"), s),
            d.get("knoten"),
            None if dauer is None else t("nach {dauer}", s, dauer=dauer_text(dauer, s)),
        )
    if e == "wechsel":
        return t("wechselt", s), _kette(
            mesh,
            _pfeil(_verbindung(d.get("von"), s), _verbindung(d.get("nach"), s)),
            _pfeil(str(d.get("knoten_von") or ""), str(d.get("knoten_nach") or "")),
        )
    if e == "neu":
        return t("neu in der Geräteliste", s), _kette(mesh, _verbindung(d.get("verbindung"), s))
    return t("aus der Geräteliste verschwunden", s), mesh


def _texte(e: Eintrag, s: str) -> tuple[str, str]:
    d, art = e.daten, e.art
    ereignis = d.get("ereignis")
    if art == GERAET:
        return _geraet_text(d, s)
    if art == WARNUNG:
        dauer = d.get("dauer_s")
        art_ = str(d.get("meldung") or "")
        kopf = t("🔔 Warnung: {art}", s, art=t(MELDUNG[art_], s) if art_ in MELDUNG else art_)
        return kopf, _kette(
            None if dauer is None else dauer_text(dauer, s),
            t("verschickt", s) if d.get("verschickt") else t("nicht verschickt", s),
        )
    if art == STAND:
        kopf = t(
            "Internet {internet} · {online} von {gesamt} Geräten online",
            s,
            internet=_ja_nein(d.get("internet"), s),
            online=d.get("online", 0),
            gesamt=d.get("gesamt", 0),
        )
        modem = _kette(d.get("netz"), f"{d['pegel']} dBm" if d.get("pegel") is not None else "")
        return kopf, _kette(
            t("Box {zustand}", s, zustand=_ja_nein(d.get("box"), s)),
            t("Modem {werte}", s, werte=modem) if modem else "",
            d.get("kanaele"),
        )
    if art == MODEM:
        kopf = t("Zelle gewechselt", s) if ereignis == "zelle" else t("Netz gewechselt", s)
        return kopf, _pfeil(str(d.get("von") or ""), str(d.get("nach") or ""))
    if ereignis == "internet_weg":
        return t("Internet weg", s), ""
    if ereignis == "internet_da":
        return t("Internet wieder da", s), ""
    if ereignis == "box_weg":
        return t("FRITZ!Box nicht erreichbar", s), ""
    if ereignis == "box_da":
        return t("FRITZ!Box wieder erreichbar", s), ""
    if ereignis == "start":
        return t("Aufzeichnung beginnt", s), t("eingeschaltet oder Home Assistant neu gestartet", s)
    if ereignis == "luecke":
        return t("Lücke im Abruf", s), dauer_text(d.get("dauer_s") or 0, s)
    if ereignis == "liste":
        return t("Geräteliste unbrauchbar", s), t(
            "{n} statt {voll} Geräte, zählt nicht als weg",
            s,
            n=d.get("n", 0),
            voll=d.get("voll", 0),
        )
    return t("Protokoll der Box", s), str(d.get("text") or "")


def _kat(e: Eintrag) -> str:
    """Filter der Seite: Warnungen stehen bei dem, was sie betreffen."""
    if e.art == WARNUNG:
        return GERAET if e.schluessel else INTERNET
    return e.art


def zeile(e: Eintrag, s: str = DE, name: str | None = None) -> dict[str, Any]:
    """Ein Eintrag zum Anzeigen. `name` ersetzt den Gerätenamen (Datei)."""
    text_, detail = _texte(e, s)
    return {
        "t": e.t,
        "art": e.art,
        "kat": _kat(e),
        "badge": t(ANZEIGE[e.art], s),
        "auffaellig": e.daten.get("ereignis") in AUFFAELLIG,
        "name": name if name is not None else _name(e.daten, s) if e.daten.get("name") else "",
        "text": text_,
        "detail": detail,
    }


def _im_fenster(liste: Sequence[Eintrag], von: float, bis: float) -> list[Eintrag]:
    """`liste` nach Zeit sortiert."""
    zeiten = [e.t for e in liste]
    return list(liste[bisect_left(zeiten, von) : bisect_right(zeiten, bis)])


def _stoerung(zustaende: Sequence[Eintrag], von: float, bis: float, weg: str, da: str) -> bool:
    """Weg im Fenster: entweder ein Wechsel darin oder schon davor weg und noch nicht zurück."""
    if any(e.daten["ereignis"] in (weg, da) for e in _im_fenster(zustaende, von, bis)):
        return True
    for e in reversed(zustaende):
        if e.t < von and e.daten["ereignis"] in (weg, da):
            return bool(e.daten["ereignis"] == weg)
    return False


def _haeufung(
    gruppe: list[Eintrag], zustaende: Sequence[Eintrag], modem: Sequence[Eintrag], s: str
) -> dict[str, Any]:
    von, bis = gruppe[0].t, gruppe[-1].t
    n = len({e.schluessel for e in gruppe})
    teile = [t("{n} Geräte in {m} min weg", s, n=n, m=max(1, math.ceil((bis - von) / 60)))]
    orte = Counter(str(e.daten["knoten"]) for e in gruppe if e.daten.get("knoten"))
    orte = orte or Counter(
        gruppen_text(str(e.daten["verbindung"]), s) for e in gruppe if e.daten.get("verbindung")
    )
    if orte:
        ort, k = orte.most_common(1)[0]
        if k * 2 >= n:
            teile.append(t("{k} davon auf {ort}", s, k=k, ort=ort))
    if any(e.daten.get("mesh") for e in gruppe):
        teile.append(t("darunter ein Repeater", s))
    fenster = von - HAEUFUNG_S, bis + HAEUFUNG_S
    if _stoerung(zustaende, *fenster, "internet_weg", "internet_da"):
        rest = t("Zur selben Zeit war das Internet gestört.", s)
    elif _stoerung(zustaende, *fenster, "box_weg", "box_da"):
        rest = t("Zur selben Zeit war die FRITZ!Box nicht erreichbar.", s)
    elif _im_fenster(modem, *fenster):
        rest = t("Internet ohne Störung, das Modem hat aber gewechselt.", s)
    else:
        rest = t("Zur selben Zeit keine Störung bei Internet oder Modem.", s)
    return {"t": von, "text": f"{', '.join(teile)}. {rest}"}


def haeufungen(eintraege: Sequence[Eintrag], s: str = DE) -> list[dict[str, Any]]:
    """Mehrere Geräte kurz nacheinander weg, neueste zuerst. `eintraege`: älteste zuerst."""
    weg = [e for e in eintraege if e.art == GERAET and e.daten.get("ereignis") == "weg"]
    zustaende = [e for e in eintraege if e.daten.get("ereignis") in ZUSTAENDE]
    modem = [e for e in eintraege if e.art == MODEM]
    zeiten = [e.t for e in weg]
    out, i = [], 0
    while i < len(weg):
        gruppe = weg[i : bisect_right(zeiten, weg[i].t + HAEUFUNG_S)]
        if len({e.schluessel for e in gruppe}) >= HAEUFUNG_AB:
            out.append(_haeufung(gruppe, zustaende, modem, s))
            i += len(gruppe)
        else:
            i += 1
    return out[::-1]


def anzeigen(eintraege: Sequence[Eintrag], s: str = DE) -> dict[str, Any]:
    """Für die Seite; `eintraege`: älteste zuerst."""
    return {
        "eintraege": len(eintraege),
        "haeufungen": haeufungen(eintraege, s),
        "zeilen": [zeile(e, s) for e in reversed(eintraege[-ZEILEN_SEITE:])],
    }


# ── Datei ──
def _ip6(treffer: re.Match[str]) -> str:
    """Nur echte Adressen: Uhrzeiten wie 12:34:56 bleiben."""
    try:
        ipaddress.IPv6Address(treffer[0])
    except ValueError:
        return treffer[0]
    return "⟨IP⟩"


def schwaerzen(text_: str, namen: Iterable[str]) -> str:
    """Zeile der Box für die Datei: Hardware- und IP-Adressen und bekannte Gerätenamen heraus."""
    out = _IP6.sub(_ip6, _IP4.sub("⟨IP⟩", ohne_mac(text_)))
    for name in sorted(set(namen), key=len, reverse=True):
        if name and name != OHNE_NAMEN:
            out = re.sub(rf"(?<!\w){re.escape(name)}(?!\w)", "⟨Gerät⟩", out, flags=re.IGNORECASE)
    return out


def datei(
    eintraege: Sequence[Eintrag], namen: Iterable[str], tz: tzinfo, s: str = DE
) -> dict[str, Any]:
    """Inhalt der Datei: Geräte als „Gerät 1, 2 …“, ohne MAC- und IP-Adressen. `namen`: alle bekannten Gerätenamen."""
    bekannt = {str(e.daten["name"]) for e in eintraege if e.daten.get("name")} | set(namen)
    nummern: dict[str, int] = {}
    zeilen = []
    for e in eintraege:
        name = None
        if e.schluessel:
            nr = nummern.setdefault(e.schluessel, len(nummern) + 1)
            name = t("Gerät {n}", s, n=nr)
        z = zeile(e, s, name)
        z["detail"] = schwaerzen(z["detail"], bekannt)
        zeilen.append(
            {
                "zeit": datetime.fromtimestamp(e.t, tz).strftime("%Y-%m-%d %H:%M:%S"),
                **{k: z[k] for k in ("art", "auffaellig", "name", "text", "detail")},
            }
        )
    return {
        "eintraege": len(zeilen),
        "geraete": len(nummern),
        "haeufungen": [
            {
                "zeit": datetime.fromtimestamp(h["t"], tz).strftime("%Y-%m-%d %H:%M:%S"),
                "text": h["text"],
            }
            for h in haeufungen(eintraege, s)
        ],
        "zeilen": zeilen,
    }
