"""Art eines Geräts im Heimnetz (AN-0001): selbst gewählt, sonst erkannt – in dieser Reihenfolge aus der Geräteliste
von Home Assistant (Hersteller/Modell eigener Integrationen), dem Mesh der FRITZ!Box (Repeater, Powerline), dem
Hersteller der Hardware-Adresse (offline, `hersteller.txt`) und dem Namen. Alles nur gelesen.

WU-0010: Neben den festen Arten legt der Admin eigene an (Symbol + Name, Kennung `eigen:<n>`). Sie gelten wie die
festen (Gruppe „nach Art“, Warnungen), werden aber nie erkannt – nur selbst zugeordnet. Ihre Namen sind Daten des
Nutzers: sie liegen nur im Integrations-Speicher, nie im Repo oder unter /local.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from .geraete import zufallsadresse
from .sprache import DE, Ungueltig, merke, t

KATEGORIEN = (
    ("netz", merke("🛜 Netzwerk")),
    ("smart", merke("🔌 Smart Home")),
    ("haushalt", merke("🤖 Haushalt & Roboter")),
    ("computer", merke("💻 Computer")),
    ("drucker", merke("🖨️ Drucker")),  # AN-0004
    ("mobil", merke("📱 Handy & Tablet")),
    ("medien", merke("📺 Fernseher & Musik")),
    ("kamera", merke("📷 Kameras")),
    ("unbekannt", merke("❓ Unbekannt")),
)
TEXT = dict(KATEGORIEN)
UNBEKANNT = "unbekannt"

# Hersteller (kurzer Name aus hersteller.txt bzw. Text aus HA) → Art; fehlt er, sagt der Hersteller allein nichts –
# auch bewusst bei Herstellern mit sehr verschiedenen Geräten (TP-Link, LG, HP, Apple, Samsung, Google, Amazon …)
HERSTELLER_ART = {
    "avm": "netz",
    "fritz": "netz",
    "ubiquiti": "netz",
    "netgear": "netz",
    "shelly": "smart",
    "espressif": "smart",
    "tuya": "smart",
    "philips hue": "smart",
    "signify": "smart",
    "sonos": "medien",
    "bose": "medien",
    "denon": "medien",
    "yamaha": "medien",
    "sony playstation": "medien",
    "nintendo": "medien",
    "raspberry pi": "computer",
    "intel": "computer",
    "dell": "computer",
    "lenovo": "computer",
    "microsoft": "computer",
    "synology": "computer",
    "qnap": "computer",
    "canon": "drucker",
    "epson": "drucker",
    "brother": "drucker",
    "asus": "computer",
    "hikvision": "kamera",
    "reolink": "kamera",
    "dreame": "haushalt",
    "dreametech": "haushalt",
    "roborock": "haushalt",
    "irobot": "haushalt",
    "ecovacs": "haushalt",
    "mammotion": "haushalt",
    "miele": "haushalt",
    "bosch/siemens": "haushalt",
    "oneplus": "mobil",
    "motorola": "mobil",
    "fairphone": "mobil",
    "garmin": "mobil",
}
# Stichwörter in Modell oder Name → Art (Reihenfolge zählt: das erste passende gewinnt)
WOERTER = (
    (
        "smart",
        r"shelly|esphome|\besp[_-]|tasmota|steckdose|stecker|plug|lampe|licht|thermostat|\btrv\b|sensor",
    ),
    (
        "haushalt",
        r"roboter|vacuum|sauger|mäher|maeher|mower|luba|dreame|roborock|waschmaschine|trockner|spülmaschine",
    ),
    ("kamera", r"kamera|camera|\bcam\b|reolink|hikvision|doorbell|klingel"),
    (
        "medien",
        r"\btv\b|fernseher|sonos|echo|chromecast|fire ?tv|playstation|\bps[45]\b|xbox|nintendo|receiver|lautsprecher|speaker",
    ),
    # Netzwerk erst nach den Geräten, die „switch“ oder „mesh“ im Namen tragen können (Nintendo Switch, Shelly Switch)
    ("netz", r"repeater|powerline|access ?point|\bap\b|mesh|\bswitch\b|router|fritz!?box"),
    # Drucker vor Computer: „HP LaserJet“ ist kein PC (HP baut beides, der Hersteller allein sagt nichts)
    (
        "drucker",
        r"drucker|printer|laserjet|officejet|deskjet|pixma|ecotank|workforce|\bmfc-|\bdcp-|\bhl-l",
    ),
    ("mobil", r"iphone|ipad|galaxy|android|pixel|handy|tablet|\btab\b|watch|uhr"),
    (
        "computer",
        r"macbook|laptop|notebook|\bpc\b|desktop|raspberry|homeassistant|home assistant|nas\b",
    ),
)


@dataclass(frozen=True)
class Art:
    kat: str
    quelle: str  # woran erkannt, für die Anzeige („Home Assistant: Shelly Plug S“)

    @property
    def text(self) -> str:
        return TEXT.get(self.kat, TEXT[UNBEKANNT])


def kategorien(
    sprache: str = DE, eigene: Mapping[str, EigeneArt] | None = None
) -> list[dict[str, str]]:
    """Auswahl der Arten für die Seite: Kennung und Text in `sprache`; eigene Arten nach den festen."""
    return [{"name": k, "text": text} for k, text in alle(sprache, eigene)]


def alle(sprache: str = DE, eigene: Mapping[str, EigeneArt] | None = None) -> list[tuple[str, str]]:
    """(Kennung, Text) aller Arten in fester Reihenfolge: erst die festen, dann die eigenen (wie angelegt)."""
    return [(k, t(text, sprache)) for k, text in KATEGORIEN] + [
        (k, e.text) for k, e in (eigene or {}).items()
    ]


# ── WU-0010: eigene Arten ──
EIGEN = "eigen:"
EIGENE_HOECHSTENS = 30
NAME_HOECHSTENS = 30  # Zeichen
SYMBOL_HOECHSTENS = 8  # Codepunkte – ein Emoji kann aus mehreren bestehen (🏳️‍🌈)
SYMBOL_VORGABE = "🏷️"


@dataclass(frozen=True)
class EigeneArt:
    symbol: str
    name: str

    @property
    def text(self) -> str:
        return f"{self.symbol} {self.name}"

    def als_dict(self) -> dict[str, str]:
        return {"symbol": self.symbol, "name": self.name}


def ist_eigen(kat: str) -> bool:
    return kat.startswith(EIGEN)


def _symbol(roh: object) -> str:
    s = str(roh or "").strip() or SYMBOL_VORGABE
    if len(s) > SYMBOL_HOECHSTENS or any(c.isspace() for c in s):
        raise Ungueltig("Symbol: ein Zeichen oder Emoji")
    # Steuerzeichen und unsichtbare Formatzeichen (z. B. Richtungswechsel) nicht – nur der Verbinder von Emojis (ZWJ)
    if any(unicodedata.category(c) in ("Cc", "Cf") and c != "\u200d" for c in s):
        raise Ungueltig("Symbol: ein Zeichen oder Emoji")
    return s


def _name(roh: object) -> str:
    n = " ".join(str(roh or "").split())
    if not n:
        raise Ungueltig("Name der Art fehlt")
    if len(n) > NAME_HOECHSTENS:
        raise Ungueltig("Name der Art: höchstens {n} Zeichen", n=NAME_HOECHSTENS)
    if any(unicodedata.category(c) in ("Cc", "Cf") and c != "\u200d" for c in n):
        raise Ungueltig("Name der Art: unerlaubtes Zeichen")
    return n


def eigene_pruefen(
    eigene: Mapping[str, EigeneArt], symbol: object, name: object, ausser: str | None = None
) -> EigeneArt:
    """Symbol und Name einer eigenen Art prüfen; derselbe Name (ohne Groß/klein) zweimal ist nicht erlaubt."""
    art = EigeneArt(_symbol(symbol), _name(name))
    if any(k != ausser and e.name.casefold() == art.name.casefold() for k, e in eigene.items()):
        raise Ungueltig("Eine eigene Art „{name}“ gibt es schon", name=art.name)
    return art


def eigene_neu(
    eigene: Mapping[str, EigeneArt], symbol: object, name: object
) -> tuple[dict[str, EigeneArt], str]:
    """Neue eigene Art → (alle eigenen, Kennung). Die Kennung zählt hoch und hängt nicht am Namen (umbenennen)."""
    if len(eigene) >= EIGENE_HOECHSTENS:
        raise Ungueltig("Höchstens {n} eigene Arten", n=EIGENE_HOECHSTENS)
    art = eigene_pruefen(eigene, symbol, name)
    nummern = [int(k[len(EIGEN) :]) for k in eigene if k[len(EIGEN) :].isdigit()]
    kennung = f"{EIGEN}{max(nummern, default=0) + 1}"
    return {**eigene, kennung: art}, kennung


def eigene_aendern(
    eigene: Mapping[str, EigeneArt], kennung: str, symbol: object, name: object
) -> dict[str, EigeneArt]:
    if kennung not in eigene:
        raise Ungueltig("Diese eigene Art gibt es nicht (mehr)")
    return {**eigene, kennung: eigene_pruefen(eigene, symbol, name, ausser=kennung)}


def eigene_aus(roh: object) -> dict[str, EigeneArt]:
    """Gespeicherte eigene Arten lesen; Unlesbares fällt weg (der Rest bleibt)."""
    out: dict[str, EigeneArt] = {}
    if not isinstance(roh, dict):
        return out
    for k, v in roh.items():
        if not (isinstance(k, str) and ist_eigen(k) and isinstance(v, dict)):
            continue
        try:
            out[k] = eigene_pruefen(out, v.get("symbol"), v.get("name"))
        except Ungueltig:
            continue
    return out


@cache
def _tabelle() -> dict[str, str]:
    """hersteller.txt → {Adressblock: Hersteller} (einmal gelesen, blockierend)."""
    pfad = Path(__file__).with_name("hersteller.txt")
    out = {}
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        if zeile and not zeile.startswith("#"):
            block, _, name = zeile.partition(" ")
            out[block] = name
    return out


def hersteller(mac: str, tabelle: Mapping[str, str] | None = None) -> str | None:
    if zufallsadresse(mac):  # private Adresse von Handy/Tablet: kein Hersteller bestimmbar
        return None
    return (tabelle if tabelle is not None else _tabelle()).get(mac.replace(":", "").upper()[:6])


def _nach_wort(text: str) -> str | None:
    t = text.lower()
    return next((kat for kat, muster in WOERTER if re.search(muster, t)), None)


def _nach_hersteller(name: str) -> str | None:
    n = name.lower().replace("™", "").strip()
    return next((kat for h, kat in HERSTELLER_ART.items() if n == h or n.startswith(h + " ")), None)


def aus_ha(hersteller_: str, modell: str) -> str | None:
    """Art aus Hersteller/Modell eines Geräts in Home Assistant; das Modell zählt vor dem Hersteller."""
    return _nach_wort(modell) or _nach_hersteller(hersteller_) or _nach_wort(hersteller_)


MESH_GERAET = merke("Mesh-Gerät")  # Mesh-Gerät ohne Modell und Namen (übersetzt erst `bestimmen`)


def mesh_aus(roh: str | bytes) -> dict[str, str]:
    """Mesh-Liste der Box (X_AVM-DE_GetMeshListPath, JSON) → {MAC: Modell} der Mesh-Geräte (Repeater, Powerline …).

    Jede Schnittstelle eines Mesh-Geräts zählt, weil die Gerätetabelle oft eine andere MAC desselben Geräts nennt."""
    try:
        daten = json.loads(roh)
    except ValueError, TypeError:
        return {}
    out: dict[str, str] = {}
    knoten_liste = daten.get("nodes") if isinstance(daten, dict) else None
    for knoten in knoten_liste if isinstance(knoten_liste, list) else []:
        if not isinstance(knoten, dict) or not knoten.get("is_meshed"):
            continue
        if knoten.get("mesh_role") not in ("master", "slave"):
            continue
        modell = str(knoten.get("device_model") or knoten.get("device_name") or MESH_GERAET)
        macs = [knoten.get("device_mac_address")]
        macs += [
            i.get("mac_address") for i in knoten.get("node_interfaces") or [] if isinstance(i, dict)
        ]
        for mac in macs:
            if isinstance(mac, str) and mac:
                out[mac.upper()] = modell
    return out


def bestimmen(
    name: str,
    mac: str,
    *,
    selbst: str | None = None,
    ha: tuple[str, str] | None = None,
    mesh: str | None = None,
    tabelle: Mapping[str, str] | None = None,
    sprache: str = DE,
    eigene: Mapping[str, EigeneArt] | None = None,
) -> Art:
    """Selbst gewählt > Home Assistant > Mesh der Box > Hersteller > Name; sonst unbekannt. `quelle` in `sprache`.
    Eine eigene Art (WU-0010) gilt nur, solange es sie gibt – gelöscht, wird wieder erkannt."""
    if selbst is not None and (selbst in TEXT or selbst in (eigene or {})):
        return Art(selbst, t("selbst gewählt", sprache))
    if ha is not None and (kat := aus_ha(*ha)):
        return Art(kat, f"Home Assistant: {' '.join(x for x in ha if x)}".strip())
    if mesh:
        modell = t(mesh, sprache) if mesh == MESH_GERAET else mesh
        return Art("netz", t("Mesh der FRITZ!Box: {modell}", sprache, modell=modell))
    her = hersteller(mac, tabelle)
    if her and (kat := _nach_hersteller(her)):
        return Art(kat, t("Hersteller ({name})", sprache, name=her))
    if kat := _nach_wort(name):
        return Art(kat, t("Name", sprache))
    return Art(
        UNBEKANNT,
        t("Hersteller ({name})", sprache, name=her) if her else t("nicht erkannt", sprache),
    )


def gruppen(
    eintraege: Iterable[tuple[str, bool]],
    sprache: str = DE,
    eigene: Mapping[str, EigeneArt] | None = None,
) -> list[dict[str, Any]]:
    """(Art, online) je Gerät → Gruppen in fester Reihenfolge (feste, dann eigene) mit Text und „online von gesamt“."""
    liste = list(eintraege)
    out = []
    for kat, text in alle(sprache, eigene):
        drin = [online for k, online in liste if k == kat]
        if drin:
            out.append({"name": kat, "text": text, "online": sum(drin), "gesamt": len(drin)})
    return out


def tabelle_laden() -> None:
    """Herstellerliste einmal lesen (blockierend, im Executor) – danach ist `bestimmen` ohne Datei-Zugriff."""
    _tabelle()
