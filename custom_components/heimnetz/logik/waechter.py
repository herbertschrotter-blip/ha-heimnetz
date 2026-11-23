"""Wächter (Herbert, 18.11.2026): ein Gerät, das hängt, neu starten – zuerst sanft über seine Schnittstelle (Stufe 1,
macht Heimnetz), dann mit einer Shelly-Steckdose Strom aus und von selbst wieder ein (Stufe 2, macht das Skript auf der
Steckdose selbst, auch wenn Home Assistant hängt).

Ein Wächter überwacht eins von drei Dingen:

- `internet`: die Kette der Geräte, über die das Internet kommt (aus ⚙ → Zugang: vorgeschaltetes Modem → FRITZ!Box,
  oder nur die Box). Je Gerät eine Steckdose (oder keine); neu gestartet wird nur das Gerät, das hängt.
- `ha`: Home Assistant selbst (dieser Pi) – nur Stufe 2.
- `geraet`: ein anderes Gerät im Heimnetz – nur Stufe 2.

Hier ohne Home Assistant: Regeln prüfen, die Regeln je Steckdose (KVS) bauen, den Code in Stücke teilen, die Anmeldung
an der Steckdose (Digest wie von Shelly beschrieben), den Zustand der Steckdose lesen, neue Eingriffe als Text, und wann
Heimnetz sanft neu startet (Stufe 1).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from typing import Any

from .modem import adresse_erlaubt
from .sprache import DE, Ungueltig, Wort, merke, t

SKRIPT_NAME = "heimnetz-waechter"
KVS_REGELN = "heimnetz-waechter"
KVS_BEFEHL = "heimnetz-waechter-befehl"
# WV im Skript (shelly/waechter.js). Bei jeder Änderung des Skripts beide hochzählen und die Prüfsumme neu eintragen –
# der Test vergleicht sie; Heimnetz bringt Steckdosen mit älterer Version selbst auf den neuen Stand.
SKRIPT_VERSION = 3
SKRIPT_PRUEFSUMME = "212995ec4c18b8b6"  # sha256 des Skripts, erste 16 Zeichen
STUECK_BYTES = 1024  # Script.PutCode: Stücke an Zeilengrenzen, höchstens so viele Bytes

ARTEN = ("internet", "ha", "geraet")
ART_TEXT = {
    "internet": merke("Internet"),
    "ha": merke("Home Assistant"),
    "geraet": merke("Gerät"),
}
ART_SYMBOL = {"internet": "🌐", "ha": "🏠", "geraet": "🔌"}

# Gerätetyp → wie es sanft neu startet (Stufe 1). Fehlt der Typ hier: nur Strom aus/ein.
SANFT = {
    "fritzbox": merke("TR-064"),
    "zte_goform": merke("Weboberfläche (Beta)"),
    "huawei_hilink": merke("Weboberfläche (Beta)"),
    "tplink": merke("Weboberfläche (Beta)"),
}
TYP_SYMBOL = {"fritzbox": "🛜", "ha": "🏠", "geraet": "🔌"}  # sonst Modem 📡

# Prüfadressen im Internet: die Prüfseiten der Betriebssysteme. 1.1.1.1 und 9.9.9.9 auf Port 80 antworten nicht
# überall (an Herberts Anschluss nicht) – Name auflösen gehört zum Test dazu.
ZIELE = (
    "http://connectivitycheck.gstatic.com/generate_204",
    "http://detectportal.firefox.com/success.txt",
    "http://www.msftconnecttest.com/connecttest.txt",
)
PRUEF_S = (30, 60, 120)

# Grenzen der Regeln: (kleinster, größter Wert)
GRENZEN = {
    "stufe1_min": (2, 60),
    "stufe2_min": (5, 240),
    "aus_s": (5, 300),
    "abstand_min": (15, 24 * 60),
    "pause_nach": (1, 10),
    "pause_h": (1, 48),
}
VORGABE = {
    "internet": {"pruef_s": 60, "stufe1_min": 5, "stufe2_min": 12, "aus_s": 30, "abstand_min": 60},
    "ha": {"pruef_s": 120, "stufe1_min": 5, "stufe2_min": 20, "aus_s": 15, "abstand_min": 120},
    "geraet": {"pruef_s": 60, "stufe1_min": 5, "stufe2_min": 10, "aus_s": 15, "abstand_min": 60},
}
HOECHSTENS = 10  # Wächter
# Stufe 1 meldet jeden sanften Neustart an alle Steckdosen der Kette (Herbert, 23.11.2026: „Pause + nur hängendes
# Gerät“). So lange schaltet keine Steckdose und ein Gerät, das gerade neu startet, gilt nicht als Störung oder als
# „wieder in Ordnung“: eine FRITZ!Box braucht für den Neustart etwa 3–4 min, Modems (ZTE, Huawei, TP-Link) 2–3 min.
SANFT_HALT_MIN = 5
HA_PORT = 8123
BEOBACHTER_PORT = 4357  # Observer des Supervisors – läuft getrennt von Home Assistant


@dataclass(frozen=True)
class Regeln:
    pruef_s: int = 60
    stufe1_min: int = 5  # sanft neu starten nach (nur internet, nur wo es geht)
    stufe2_min: int = 12  # Strom aus/ein nach
    aus_s: int = 30
    abstand_min: int = 60  # höchstens alle … je Gerät
    pause_nach: int = 3  # Eingriffe ohne Erfolg …
    pause_h: int = 6  # … dann so lange Pause
    melden: bool = True

    def als_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


@dataclass(frozen=True)
class Glied:
    """Ein Gerät, das der Wächter neu starten kann: Typ (Baustein-Kennung, „fritzbox“, „ha“, „geraet“), Name zum
    Anzeigen, Adresse zum Prüfen und die Steckdose davor (Adresse) oder keine."""

    typ: str
    name: str
    adresse: str
    dose: str | None = None

    def als_dict(self) -> dict[str, Any]:
        return {"typ": self.typ, "name": self.name, "adresse": self.adresse, "dose": self.dose}

    @property
    def sanft(self) -> bool:
        return self.typ in SANFT


@dataclass(frozen=True)
class Waechter:
    id: str
    art: str
    glieder: tuple[Glied, ...]
    regeln: Regeln = field(default_factory=Regeln)
    an: bool = True

    def als_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "art": self.art,
            "an": self.an,
            "glieder": [g.als_dict() for g in self.glieder],
            "regeln": self.regeln.als_dict(),
        }

    @property
    def dosen(self) -> list[tuple[int, str]]:
        """(Index des Glieds, Adresse der Steckdose) – Glieder ohne Steckdose fehlen."""
        return [(i, g.dose) for i, g in enumerate(self.glieder) if g.dose]


# ── Prüfen ──


def _ganz(wert: Any, name: str, grenzen: tuple[int, int]) -> int:
    try:
        v = int(wert)
    except (TypeError, ValueError) as err:
        raise Ungueltig("{name}: keine ganze Zahl", name=name) from err
    if not grenzen[0] <= v <= grenzen[1]:
        raise Ungueltig("{name}: zwischen {a} und {b}", name=name, a=grenzen[0], b=grenzen[1])
    return v


def _adresse(wert: Any, name: str, port: bool = False) -> str:
    text = str(wert or "").strip()
    host, _, p = text.partition(":") if port and text.count(":") == 1 else (text, "", "")
    if not adresse_erlaubt(host) or (p and not p.isdigit()):
        raise Ungueltig("{name}: nur eine private Adresse im Heimnetz", name=name)
    return text


def regeln_pruefen(daten: dict[str, Any] | None, art: str) -> Regeln:
    d = {**VORGABE[art], **(daten or {})}
    pruef = _ganz(d.get("pruef_s"), "pruef_s", (min(PRUEF_S), max(PRUEF_S)))
    if pruef not in PRUEF_S:
        raise Ungueltig("pruef_s: 30, 60 oder 120")
    werte = {k: _ganz(d.get(k, getattr(Regeln, k)), k, g) for k, g in GRENZEN.items()}
    if art == "internet" and werte["stufe2_min"] <= werte["stufe1_min"]:
        raise Ungueltig("Strom aus/ein erst nach dem sanften Neustart")
    return Regeln(pruef_s=pruef, melden=bool(d.get("melden", True)), **werte)


def pruefen(daten: dict[str, Any]) -> Waechter:
    """Einen Wächter aus Eingaben (Seite) oder dem Speicher; ungültig → Ungueltig mit verständlichem Text."""
    art = daten.get("art")
    if art not in ARTEN:
        raise Ungueltig("Art des Wächters: internet, ha oder geraet")
    roh = daten.get("glieder") or []
    if not isinstance(roh, list) or not 1 <= len(roh) <= 3 or (art != "internet" and len(roh) != 1):
        raise Ungueltig("Geräte des Wächters fehlen")
    glieder = []
    for g in roh:
        dose = g.get("dose") or None
        glieder.append(
            Glied(
                typ=str(g.get("typ") or "geraet"),
                name=str(g.get("name") or "")[:60],
                adresse=_adresse(g.get("adresse"), "adresse", port=art == "ha"),
                dose=_adresse(dose, "Steckdose") if dose else None,
            )
        )
    dosen = [g.dose for g in glieder if g.dose]
    if not dosen and art != "internet":
        raise Ungueltig("Ohne Steckdose kann dieser Wächter nichts tun")
    if not dosen and not any(g.sanft for g in glieder):
        raise Ungueltig("Ohne Steckdose kann dieser Wächter nichts tun")
    if len(set(dosen)) != len(dosen):
        raise Ungueltig("Eine Steckdose kann nur ein Gerät versorgen")
    return Waechter(
        id=str(daten.get("id") or "")[:20] or "w1",
        art=art,
        glieder=tuple(glieder),
        regeln=regeln_pruefen(daten.get("regeln"), art),
        an=bool(daten.get("an", True)),
    )


def alle_pruefen(liste: list[dict[str, Any]] | None) -> list[Waechter]:
    """Gespeicherte Liste – Ungültiges fällt weg (der Aufrufer meldet es)."""
    aus = []
    for d in liste or []:
        try:
            aus.append(pruefen(d))
        except Ungueltig:
            continue
    return aus[:HOECHSTENS]


def neue_id(vorhanden: list[Waechter]) -> str:
    belegt = {w.id for w in vorhanden}
    return next(f"w{n}" for n in range(1, HOECHSTENS + 2) if f"w{n}" not in belegt)


def doppelte_dose(neu: Waechter, andere: list[Waechter]) -> str | None:
    """Steckdose, die schon ein anderer Wächter benutzt – je Steckdose gibt es nur ein Skript."""
    fremd = {d for w in andere if w.id != neu.id for _, d in w.dosen}
    return next((d for _, d in neu.dosen if d in fremd), None)


# ── Regeln je Steckdose ──


KVS_MAX = (
    254  # ein KVS-Wert der Shelly hat höchstens 255 Zeichen („length should be less than 255“)
)


def kvs(w: Waechter, i: int, router: str | None, beobachter: bool = False) -> dict[str, Any]:
    """Regeln für die Steckdose vor Glied `i` (KVS „heimnetz-waechter“), mit kurzen Schlüsseln – ein KVS-Wert darf
    nicht länger als KVS_MAX sein. Das Skript klappt sie aus (`ausklappen` in shelly/waechter.js); die Prüfseiten im
    Internet stehen dort fest (`i: 1`). Adressen ohne „http://“. `router`: Adresse der FRITZ!Box – daran erkennt die
    Steckdose, ob das Heimnetz selbst geht (ha, geraet)."""
    r, g = w.regeln, w.glieder[i]
    d: dict[str, Any] = {
        "v": 1,
        "an": int(w.an),
        "p": r.pruef_s,
        "s2": r.stufe2_min,
        "a": r.aus_s,
        "ab": r.abstand_min,
        "pn": r.pause_nach,
        "ph": r.pause_h,
        "e": g.adresse,
    }
    if w.art == "internet":
        d.update(r="kette", po=i, n=len(w.glieder), i=1)
        if i + 1 < len(w.glieder):
            d["na"] = w.glieder[i + 1].adresse
        if i > 0:
            d["vo"] = w.glieder[i - 1].adresse
            # vorne in der Kette schaltet die andere Steckdose: nie beide zugleich
            if partner := w.glieder[i - 1].dose:
                d["pa"] = partner
    else:
        d["r"] = w.art
        if router:
            d["ne"] = router
        if w.art == "ha" and beobachter:
            # Beobachter des Supervisors (nur Home Assistant OS / Supervised): lebt der Pi selbst noch?
            d["ho"] = f"{g.adresse.partition(':')[0]}:{BEOBACHTER_PORT}"
    return d


def kvs_text(d: dict[str, Any]) -> str:
    """Regeln als kurzes JSON für KVS.Set; zu lang → Ungueltig (statt einer Fehlermeldung der Steckdose)."""
    text = json.dumps(d, separators=(",", ":"))
    if len(text) > KVS_MAX:
        raise Ungueltig("Regeln zu lang für die Steckdose")
    return text


def stuecke(code: str, n: int = STUECK_BYTES) -> list[str]:
    """Script.PutCode: an Zeilengrenzen, je Stück höchstens n Bytes (die Steckdose verschluckt sich an mitten
    geteilten Zeilen)."""
    aus: list[str] = []
    jetzt = ""
    for zeile in code.splitlines(keepends=True):
        if len((jetzt + zeile).encode()) > n and jetzt:
            aus.append(jetzt)
            jetzt = ""
        jetzt += zeile
    if jetzt:
        aus.append(jetzt)
    return aus


def skript_version(code: str) -> int | None:
    """WV aus dem Code des Skripts (`let WV = 1;`)."""
    for zeile in code.splitlines():
        if zeile.startswith("let WV = "):
            return int(zeile.removeprefix("let WV = ").rstrip(";").strip())
    return None


# ── Anmeldung an der Steckdose (Shelly Gen 2: Digest mit SHA-256, Antwort im Feld „auth“) ──


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def anmeldung(
    kennwort: str, realm: str, nonce: int | str, cnonce: str, nc: int = 1
) -> dict[str, Any]:
    """Feld „auth“ für eine RPC-Anfrage nach einer 401 mit realm/nonce."""
    ha1 = _sha(f"admin:{realm}:{kennwort}")
    ha2 = _sha("dummy_method:dummy_uri")
    return {
        "realm": realm,
        "username": "admin",
        "nonce": nonce,
        "cnonce": cnonce,
        "response": _sha(f"{ha1}:{nonce}:{nc}:{cnonce}:auth:{ha2}"),
        "algorithm": "SHA-256",
    }


# ── Zustand der Steckdose ──

ZUSTAND = {
    "bereit": ("ok", merke("bereit")),
    "stoerung": ("amber", merke("Störung erkannt")),
    "schaltet": ("amber", merke("Strom aus – schaltet gleich wieder ein")),
    "aus": ("amber", merke("Steckdose aus")),
    "sanft": ("amber", merke("wartet auf den sanften Neustart")),
    "pause": ("rot", merke("Pause nach Eingriffen ohne Erfolg")),
    "aus_regel": ("grau", merke("ausgeschaltet")),
    "fehler": ("rot", merke("Skript ohne gültige Regeln")),
    "start": ("grau", merke("startet")),
}
GRUND = {
    "router_weg": merke("Router antwortet nicht"),
    "modem_weg": merke("Modem antwortet nicht"),
    "inet_weg": merke("kein Internet"),
    "ha_weg": merke("Home Assistant antwortet nicht"),
    "ha_weg_pi_lebt": merke("Home Assistant antwortet nicht, der Pi selbst schon"),
    "pi_weg": merke("weder Home Assistant noch der Pi antworten"),
    "geraet_weg": merke("Gerät antwortet nicht"),
    "keine_regeln": merke("keine Regeln"),
    "regeln_kaputt": merke("Regeln nicht lesbar"),
}


@dataclass(frozen=True)
class Dosenstand:
    """Was die Steckdose über ihr Skript meldet (oder dass sie nicht antwortet)."""

    erreichbar: bool
    zustand: str = ""
    grund: str = ""
    version: int | None = None
    stoer_s: int | None = None
    pause_s: int | None = None
    eingriffe: int = 0
    letzte: tuple[dict[str, Any], ...] = ()
    leistung: float | None = None  # W, aus Switch.GetStatus
    fehlt: bool = False  # erreichbar, aber kein Skript darauf

    @property
    def veraltet(self) -> bool:
        return self.erreichbar and not self.fehlt and self.version != SKRIPT_VERSION


def _liste(wert: Any) -> list[Any]:
    return wert if isinstance(wert, list) else []


def dosenstand(status: dict[str, Any] | None, leistung: float | None = None) -> Dosenstand:
    if not isinstance(status, dict):
        return Dosenstand(erreichbar=True, fehlt=True, leistung=leistung)
    letzte = tuple(e for e in _liste(status.get("letzte")) if isinstance(e, dict))
    try:
        eingriffe = int(status.get("eingriffe") or 0)
    except TypeError, ValueError:
        eingriffe = 0
    return Dosenstand(
        erreichbar=True,
        zustand=str(status.get("zustand") or ""),
        grund=str(status.get("grund") or ""),
        version=status.get("wv"),
        stoer_s=status.get("stoer_s"),
        pause_s=status.get("pause_s"),
        eingriffe=eingriffe,
        letzte=letzte,
        leistung=leistung,
    )


EREIGNIS = {
    "strom": merke("{geraet}: Strom {s} s aus und wieder ein – {grund}"),
    "pause": merke("{geraet}: {n} Eingriffe ohne Erfolg – Wächter macht Pause"),
    "ok": merke("{geraet}: wieder in Ordnung"),
    "schalten_fehler": merke("{geraet}: Steckdose konnte nicht schalten"),
}


def neue_eingriffe(
    alt: tuple[dict[str, Any], ...], neu: tuple[dict[str, Any], ...]
) -> list[dict[str, Any]]:
    """Einträge aus `neu`, die in `alt` noch nicht waren (Vergleich über Zeit und Art)."""
    gesehen = {(e.get("t"), e.get("was")) for e in alt}
    return [
        e for e in neu if (e.get("t"), e.get("was")) not in gesehen and e.get("was") in EREIGNIS
    ]


def eingriff_text(e: dict[str, Any], g: Glied, w: Waechter, sprache: str = DE) -> str:
    was = str(e.get("was"))
    grund = GRUND.get(str(e.get("grund")), Wort(str(e.get("grund") or "")))
    text = t(
        EREIGNIS[was],
        sprache,
        geraet=g.name or t(ART_TEXT[w.art], sprache),
        s=w.regeln.aus_s,
        grund=grund,
        n=e.get("grund") or "",
    )
    if was == "strom" and isinstance(b := e.get("b"), dict):
        text += befund_text(b, sprache)
    return text


def befund_text(b: dict[str, Any], sprache: str = DE) -> str:
    """Was die Steckdose vor dem Schalten sah: seit wann keine Antwort, Leistung des Geräts (viel = rechnet sich fest,
    wenig = steht)."""
    teile = []
    if isinstance(b.get("ok"), int | float):
        teile.append(t("letzte Antwort vor {n} min", sprache, n=int(b["ok"])))
    if isinstance(b.get("w"), int | float):
        teile.append(t("{w} W", sprache, w=str(b["w"]).replace(".", "," if sprache == DE else ".")))
    return f" ({', '.join(teile)})" if teile else ""


# ── Stufe 1: sanft neu starten (Heimnetz) ──


@dataclass
class Sanft:
    """Zustand der Stufe 1 je Wächter: seit wann das Internet weg ist und welche Geräte in dieser Störung schon sanft
    neu gestartet wurden (jedes höchstens einmal je Störung)."""

    weg_seit: float | None = None
    gemacht: dict[int, float] = field(default_factory=dict)
    zuletzt: dict[int, float] = field(
        default_factory=dict
    )  # letzter sanfter Neustart je Glied, über Störungen hinweg
    ruhe_bis: float | None = None  # „Eingriff abbrechen“: so lange nichts tun


def _sanft_frei(w: Waechter, s: Sanft, jetzt: float, internet: bool | None) -> bool:
    return (
        w.art == "internet"
        and w.an
        and internet is False
        and not (s.ruhe_bis is not None and jetzt < s.ruhe_bis)
    )


def _sanft_kandidat(w: Waechter, s: Sanft, jetzt: float) -> int | None:
    """Erstes Glied, das in dieser Störung noch sanft neu starten darf: sanft startbar, noch nicht gemacht, Bremse
    `abstand_min` (auch über Störungen hinweg) vorbei."""
    for i, g in enumerate(w.glieder):
        if i in s.gemacht or not g.sanft:
            continue
        if jetzt - s.zuletzt.get(i, -1e12) < w.regeln.abstand_min * 60:
            continue  # Bremse wie bei der Steckdose: höchstens einmal je Abstand
        return i
    return None


def sanft_faellig(w: Waechter, s: Sanft, jetzt: float, internet: bool | None) -> bool:
    """Könnte `sanft_entscheiden` jetzt ein Gerät neu starten? Dann lohnt es, vorher frisch zu fragen, welche Geräte
    der Kette antworten (der Stand des Modems ist bis zu 10 min alt). Kommt kein Glied mehr infrage (alle gemacht,
    keines sanft startbar, Bremse), ist nichts fällig – sonst liefe bei langem Ausfall jede Minute eine Probe."""
    if not _sanft_frei(w, s, jetzt, internet) or s.weg_seit is None:
        return False
    letzter = max(s.gemacht.values(), default=s.weg_seit)
    if jetzt - letzter < w.regeln.stufe1_min * 60:
        return False
    return _sanft_kandidat(w, s, jetzt) is not None


def sanft_entscheiden(
    w: Waechter,
    s: Sanft,
    jetzt: float,
    internet: bool | None,
    erreichbar: dict[int, bool | None],
) -> tuple[Sanft, int | None]:
    """Welches Glied jetzt sanft neu starten (Index) oder keines. Nur für den Wächter „internet“.

    Nur das Gerät, das hängt (Herbert, 23.11.2026): antwortet ein Gerät der Kette nicht, ist es das hängende – sanft
    lässt es sich dann nicht neu starten, das macht seine Steckdose; die übrigen sind gesund und bleiben in Ruhe (nie
    die Box, wenn nur das Modem nicht antwortet). Antworten alle und das Internet fehlt trotzdem: vorne zuerst (Modem),
    danach das nächste, jeweils `stufe1_min` nach dem Ausfall bzw. nach dem vorigen Neustart. Bremse je Glied
    `abstand_min` auch über Störungen hinweg; „Eingriff abbrechen“ (`ruhe_bis`) hält an. `internet` None = unbekannt
    (nichts tun); `erreichbar` je Glied, None = unbekannt (z. B. ein Glied ohne Weboberfläche – es hält Stufe 1 nicht
    auf)."""
    if w.art != "internet" or not w.an or internet is None:
        return s, None
    if s.ruhe_bis is not None and jetzt < s.ruhe_bis:
        return replace(s, weg_seit=None, gemacht={}), None
    if internet:
        return Sanft(zuletzt=s.zuletzt), None
    if s.weg_seit is None:
        return replace(s, weg_seit=jetzt, gemacht={}, ruhe_bis=None), None
    if not sanft_faellig(w, s, jetzt, internet):
        return s, None
    if any(erreichbar.get(i) is False for i in range(len(w.glieder))):
        return s, None  # ein Gerät hängt ganz: das ist Sache seiner Steckdose
    i = _sanft_kandidat(w, s, jetzt)
    if i is None:
        return s, None
    return replace(s, gemacht={**s.gemacht, i: jetzt}, zuletzt={**s.zuletzt, i: jetzt}), i


# ── Für die Seite ──


def glied_karte(g: Glied, d: Dosenstand | None, sprache: str = DE) -> dict[str, Any]:
    symbol = TYP_SYMBOL.get(g.typ, "📡")
    punkt, text = "grau", t("keine Steckdose", sprache)
    if g.dose and d is not None:
        if not d.erreichbar:
            punkt, text = "rot", t("Steckdose antwortet nicht", sprache)
        elif d.fehlt:
            punkt, text = "rot", t("Skript fehlt auf der Steckdose", sprache)
        else:
            punkt, wort = ZUSTAND.get(d.zustand, ("grau", Wort(d.zustand)))
            text = t(wort, sprache)
            if d.grund in GRUND and d.zustand in ("stoerung", "fehler"):
                text = f"{text} · {t(GRUND[d.grund], sprache)}"
    return {
        "symbol": symbol,
        "name": g.name,
        "adresse": g.adresse,
        "dose": g.dose,
        "punkt": punkt,
        "zustand": text,
        "leistung": d.leistung if d else None,
        "sanft": t(SANFT[g.typ], sprache) if g.sanft else None,
        "veraltet": bool(d and d.veraltet),
        "eingriffe": d.eingriffe if d else 0,
    }
