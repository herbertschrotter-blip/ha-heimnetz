"""Vorgeschaltetes Gerät (WU-0009 Stufe 2): erkennen, welches Modem vor der FRITZ!Box steht, und seine Werte in das
gemeinsame Format bringen, das die Mobilfunk-Ansicht schon versteht (`mobil.Mobilfunk` mit `mobil.Zelle`).

Ohne Home Assistant und ohne Netz. Je Hersteller bzw. Schnittstelle ein Baustein mit demselben Muster:
(a) erkennen aus Startseite und Antwortkopf (hier, `erkennen`), (b) nur lesende Abfragen und (c) die Anmeldung mit dem
Kennwort des Besitzers macht der dünne HA-Teil (`vorgeschaltet/` neben `logik/`), (d) umrechnen steht im Modul des
Bausteins (`zte.py`, `huawei.py`, `tplink.py`, `integrationen.py`). Was ein Gerät nicht liefert, bleibt leer.

Gesucht wird nur an wenigen Adressen (`kandidaten`): der gespeicherten, dem Vorschlag aus der FRITZ!Box und den
üblichen Modem-Adressen – kein Absuchen des Heimnetzes.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from ..mobil import Mobilfunk
from ..modem import adresse_erlaubt
from ..sprache import DE, merke, t

# Übliche Adressen von Mobilfunk- und Glasfaser-Modems (ZTE, Huawei, TP-Link, Netgear, Nokia …)
UEBLICHE_ADRESSEN = ("192.168.0.1", "192.168.1.1", "192.168.8.1", "192.168.18.1", "192.168.100.1")
TAKT_S = 600  # Werte vom Gerät im langsamen Takt – wie Zugang und Bänder der Box, nicht öfter
FRISCH_S = (
    2 * TAKT_S + 120
)  # so lange gelten die zuletzt gelesenen Werte, bis der nächste Abruf sie ersetzt


@dataclass(frozen=True)
class Baustein:
    """Was ein Baustein kann. `werte`: liest laufende Werte selbst; `integration`: Domain einer HA-Integration, deren
    Entitäten Heimnetz liest, wenn sie eingerichtet ist (dann fragt Heimnetz das Gerät nicht selbst)."""

    kennung: str
    hersteller: str
    name: str  # Schnittstelle, wie sie angezeigt wird („goform“, „ubus“, „HiLink“)
    art: str  # mobilfunk, glasfaser, router, box
    werte: bool
    integration: str = ""


BAUSTEINE = {
    b.kennung: b
    for b in (
        Baustein("zte_goform", "ZTE", "goform", "mobilfunk", True),
        Baustein("zte_ubus", "ZTE", "ubus", "mobilfunk", True),
        Baustein("zte", "ZTE", "", "mobilfunk", False),  # erkannt, Schnittstelle noch offen
        Baustein("huawei_hilink", "Huawei", "HiLink", "mobilfunk", True, "huawei_lte"),
        Baustein("tplink", "TP-Link", "", "mobilfunk", True),
        Baustein("netgear_lte", "Netgear", "", "mobilfunk", False, "netgear_lte"),
        Baustein("teltonika", "Teltonika", "", "mobilfunk", False, "teltonika"),
        Baustein("mikrotik", "MikroTik", "RouterOS", "router", False),
        Baustein("sagemcom", "Sagemcom", "", "router", False),
        Baustein("nokia_5g", "Nokia", "FastMile", "mobilfunk", False),
        Baustein("zyxel_5g", "Zyxel", "", "mobilfunk", False),
        Baustein("ont_nokia", "Nokia", "ONT", "glasfaser", False),
        Baustein("ont_huawei", "Huawei", "ONT", "glasfaser", False),
        Baustein("ont_zyxel", "Zyxel", "ONT", "glasfaser", False),
        Baustein("fritzbox", "AVM", "FRITZ!Box", "box", False),
    )
}


@dataclass(frozen=True)
class Erkennung:
    """Ergebnis des Erkennens an einer Adresse."""

    baustein: str  # Schlüssel in BAUSTEINE
    modell: str = ""

    @property
    def b(self) -> Baustein:
        return BAUSTEINE[self.baustein]

    @property
    def name(self) -> str:
        """„ZTE G5TC (ubus)“ – Modell (oder Hersteller) und Schnittstelle."""
        b = self.b
        geraet = self.modell or b.hersteller
        return f"{geraet} ({b.name})" if b.name and b.name not in geraet else geraet


# Erkennen: Reihenfolge zählt (ONT vor Router desselben Herstellers, FRITZ!Box zuerst).
_ZTE_MODELL = re.compile(r"ZTE[\s_-]*([A-Z]{1,3}\d{1,4}[A-Z0-9]*)", re.IGNORECASE)
_ZTE_MODELL_KURZ = re.compile(r"\b(G5T[A-Z]|MC\d{3,4}[A-Z]?|MF\d{3,4}[A-Z]?)\b")
_HUAWEI_MODELL = re.compile(
    r"\b((?:B|E|H)\d{3,4}[A-Z]?(?:-\d{2,3}[a-z]?)?|5G CPE (?:Pro|Max|Win)\s*\d?)\b"
)
_TPLINK_MODELL = re.compile(
    r"\b(Archer\s+(?:MR|NX)\d{3,4}[A-Z]?|(?:MR|NX)\d{3,4}[A-Z]?|M\d{4}[A-Z]?|Deco\s+X\d+-(?:4G|5G))\b"
)
_TELTONIKA_MODELL = re.compile(r"\b(RUT[XM]?\d{2,3}|TRB\d{3})\b")
_NETGEAR_MODELL = re.compile(r"\b((?:LB|LM|MR|LAX|NBR)\d{4}|M[1-6]|Nighthawk\s+M\d)\b")


def _kopftext(kopf: Mapping[str, str] | None) -> str:
    if not kopf:
        return ""
    return " ".join(f"{k}: {v}" for k, v in kopf.items() if k.lower() in ("server", "location"))


def _treffer(muster: re.Pattern[str], text: str) -> str:
    m = muster.search(text)
    return m.group(1).strip() if m else ""


def erkennen(startseite: str, kopf: Mapping[str, str] | None = None) -> Erkennung | None:
    """Aus Startseite und Antwortkopf (Server, Location einer Weiterleitung – der nicht gefolgt wird) erkennen, was
    für ein Gerät antwortet. None: antwortet, aber nicht erkannt."""
    text = f"{startseite}\n{_kopftext(kopf)}"
    tief = text.lower()
    if "fritz!box" in tief or "fritz!os" in tief:
        return Erkennung("fritzbox", "FRITZ!Box")
    if "echolife" in tief or "optixstar" in tief or re.search(r"\bhg8\d{3}", tief):
        return Erkennung("ont_huawei", _treffer(re.compile(r"\b(HG8\d{3}[A-Z0-9]*)", re.I), text))
    if "fastmile" in tief:
        return Erkennung("nokia_5g", "Nokia FastMile")
    if "nokia" in tief or "alcl" in tief:
        return Erkennung("ont_nokia", _treffer(re.compile(r"\b(G-\d{3}[A-Z]-[A-Z])\b"), text))
    if "zyxel" in tief:
        mobil = _treffer(re.compile(r"\b((?:NR|LTE)\d{4}[A-Z0-9-]*)\b"), text)
        if mobil:
            return Erkennung("zyxel_5g", f"Zyxel {mobil}")
        return Erkennung(
            "ont_zyxel", _treffer(re.compile(r"\b((?:PMG|PM|AX)\d{4}[A-Z0-9-]*)\b"), text)
        )
    if "zte" in tief or "goform" in tief or "zwrt" in tief:
        modell = _treffer(_ZTE_MODELL, text)
        modell = modell or _treffer(_ZTE_MODELL_KURZ, text)
        return Erkennung("zte", f"ZTE {modell.upper()}" if modell else "")
    if "huawei" in tief or "hilink" in tief or "sestokinfo" in tief or "/html/index.html" in tief:
        modell = _treffer(_HUAWEI_MODELL, text)
        return Erkennung("huawei_hilink", f"Huawei {modell}" if modell else "")
    if "tp-link" in tief or "tplink" in tief or "archer" in tief:
        modell = _treffer(_TPLINK_MODELL, text)
        return Erkennung("tplink", f"TP-Link {modell}" if modell else "")
    if "netgear" in tief or "nighthawk" in tief:
        modell = _treffer(_NETGEAR_MODELL, text)
        return Erkennung("netgear_lte", f"Netgear {modell}" if modell else "")
    if "teltonika" in tief or _TELTONIKA_MODELL.search(text):
        return Erkennung("teltonika", _treffer(_TELTONIKA_MODELL, text))
    if "mikrotik" in tief or "routeros" in tief:
        return Erkennung("mikrotik", "MikroTik")
    if "sagemcom" in tief:
        return Erkennung("sagemcom", "Sagemcom")
    return None


def zte_schnittstelle(goform: str | None, ubus: bool, modell: str = "") -> Erkennung | None:
    """Welche Schnittstelle ein ZTE-Gerät spricht – aus den beiden lesenden Proben: goform (Modell aus
    `modem_model`, "" = antwortet ohne Modell, None = keine goform-Antwort) und ubus (`web_login_info` antwortet)."""
    if goform is not None:
        return Erkennung("zte_goform", modell or (f"ZTE {goform}" if goform else ""))
    if ubus:
        return Erkennung("zte_ubus", modell)
    return None


def kandidaten(
    gespeichert: str | None, vorschlag: str | None, box: str | None = None
) -> tuple[str, ...]:
    """Adressen für die Suche, in dieser Reihenfolge: gespeichert, Vorschlag aus der Box, übliche – nur private,
    ohne die Adresse der FRITZ!Box selbst, jede einmal."""
    out: list[str] = []
    for a in (gespeichert, vorschlag, *UEBLICHE_ADRESSEN):
        a = (a or "").strip()
        if a and a != box and adresse_erlaubt(a) and a not in out:
            out.append(a)
    return tuple(out)


@dataclass(frozen=True)
class Treffer:
    """Ergebnis der Suche an einer Adresse: antwortet sie, und was ist es."""

    adresse: str
    antwortet: bool
    erkennung: Erkennung | None = None

    @property
    def brauchbar(self) -> bool:
        return self.erkennung is not None and self.erkennung.b.art != "box"


def bester(treffer: Iterable[Treffer]) -> Treffer | None:
    """Erste Adresse mit einem erkannten Gerät, das nicht die FRITZ!Box selbst ist."""
    return next((x for x in treffer if x.brauchbar), None)


def beleg(x: Treffer, s: str = DE) -> str:
    """„192.168.0.1 antwortet: ZTE G5TC (ubus)“ – Beleg in ⚙ › Zugang."""
    if not x.antwortet:
        return t("{adresse} antwortet nicht", s, adresse=x.adresse)
    if x.erkennung is None:
        return t("{adresse} antwortet, Gerät nicht erkannt", s, adresse=x.adresse)
    if x.erkennung.b.art == "box":
        return t("{adresse} ist die FRITZ!Box selbst", s, adresse=x.adresse)
    return t("{adresse} antwortet: {geraet}", s, adresse=x.adresse, geraet=x.erkennung.name)


# Werte, die nur ein vorgeschaltetes Modem liefert – je eine Entität, angelegt erst, wenn genau dieser Wert einmal da war
ZUSATZWERTE = ("sinr_anker", "sinr_5g", "mobil_band")


def zusatzwerte(m: Mobilfunk) -> list[str]:
    """Welche der ZUSATZWERTE dieser Stand enthält."""
    da = []
    if m.haupt is not None and m.haupt.art != "5G" and m.haupt.sinr is not None:
        da.append("sinr_anker")
    if m.nr is not None and m.nr.sinr is not None:
        da.append("sinr_5g")
    if any(z.band for z in m.zellen):
        da.append("mobil_band")
    return da


@dataclass(frozen=True)
class Modemstand:
    """Was der Abruf zuletzt vom vorgeschalteten Gerät weiß. `befund` (Kennung aus BEFUNDE) ist None, wenn alles
    gelesen wurde; `quelle` „geraet“ (selbst gefragt) oder „integration“ (Entitäten einer HA-Integration)."""

    adresse: str
    erkennung: Erkennung | None
    mobil: Mobilfunk | None
    befund: str | None
    zeit: float
    quelle: str = "geraet"
    angemeldet: bool = False

    def frisch(self, jetzt: float) -> bool:
        return jetzt - self.zeit < FRISCH_S


# Befunde (Kennung → Lage, Titel, Text); Lage: grau (Hinweis), amber (Aufgabe), rot (Störung)
BEFUNDE = {
    "nicht_gesucht": (
        "grau",
        merke("Noch kein Gerät gesucht"),
        merke(
            "Heimnetz sucht das vorgeschaltete Gerät beim nächsten Abruf – oder sofort über ⚙ › 🌐 Zugang › ↻ Erneut suchen."
        ),
    ),
    "nicht_gefunden": (
        "amber",
        merke("Kein vorgeschaltetes Gerät gefunden"),
        merke(
            "An der gespeicherten Adresse, am Vorschlag der FRITZ!Box und an den üblichen Adressen hat sich kein bekanntes Gerät gemeldet. Adresse unter ⚙ › 🌐 Zugang eintragen – sie steht in den Einstellungen des Modems oder auf einem Aufkleber."
        ),
    ),
    "nicht_erreichbar": (
        "rot",
        merke("Vorgeschaltetes Gerät antwortet nicht"),
        merke(
            "Unter dieser Adresse antwortet nichts. Ist das Gerät an und die Adresse richtig? Sie steht in den Einstellungen des Modems oder auf einem Aufkleber. Der laufende Abruf versucht es im nächsten Takt wieder."
        ),
    ),
    "nicht_erkannt": (
        "amber",
        merke("Gerät nicht erkannt"),
        merke(
            "Unter dieser Adresse antwortet etwas, aber kein Gerät, das Heimnetz kennt. Die Rohdaten der Startseite helfen dem Entwickler, es zu unterstützen."
        ),
    ),
    "fritzbox": (
        "grau",
        merke("Das ist die FRITZ!Box selbst"),
        merke(
            "Unter dieser Adresse antwortet die FRITZ!Box. Das vorgeschaltete Gerät hat eine andere Adresse – meist die, die die Box als Vorschlag nennt."
        ),
    ),
    "adresse_nicht_erlaubt": (
        "amber",
        merke("Adresse nicht erlaubt"),
        merke(
            "Die Adresse liegt nicht im eigenen Heimnetz. Abgefragt werden nur private Adressen (192.168.x.x, 10.x.x.x, 172.16–31.x.x)."
        ),
    ),
    "nicht_unterstuetzt": (
        "amber",
        merke("Gerät erkannt, Werte noch nicht unterstützt"),
        merke(
            "Dieses Gerät kann Heimnetz noch nicht auslesen. Rohdaten über ⚙ › 🔬 Diagnose abfragen und an den Entwickler schicken – dann kann er es unterstützen."
        ),
    ),
    "integration_fehlt": (
        "amber",
        merke("Werte über die Integration von Home Assistant"),
        merke(
            "Für dieses Gerät gibt es eine eigene Integration in Home Assistant. Ist sie eingerichtet, liest Heimnetz deren Werte – Heimnetz fragt das Gerät dann nicht selbst."
        ),
    ),
    "integration_eingerichtet": (
        "grau",
        merke("Werte kommen aus der Integration in Home Assistant"),
        merke(
            "Für dieses Gerät ist eine eigene Integration eingerichtet; ihre Werte liest Heimnetz laufend. Die Diagnose meldet sich deshalb nicht selbst am Gerät an – das würde deren Sitzung stören. Oben steht nur die Startseite."
        ),
    ),
    "ohne_kennwort": (
        "amber",
        merke("Kennwort fehlt"),
        merke(
            "Ohne Anmeldung gibt das Gerät seine Signalwerte nicht heraus. Kennwort der Weboberfläche unter ⚙ › 🌐 Zugang hinterlegen."
        ),
    ),
    "anmeldung_abgelehnt": (
        "rot",
        merke("Anmeldung abgelehnt"),
        merke(
            "Das Gerät lehnt das Kennwort ab; ohne Anmeldung fehlen die Signalwerte. Der laufende Abruf versucht es nicht noch einmal, bis unter ⚙ › 🌐 Zugang ein anderes Kennwort eingetragen ist – sonst sperrt das Gerät womöglich die Anmeldung."
        ),
    ),
    "gesperrt": (
        "rot",
        merke("Anmeldung am Gerät gesperrt"),
        merke(
            "Das Gerät nimmt nach zu vielen Fehlversuchen gerade keine Anmeldung an. Später wieder versuchen; Heimnetz meldet sich bis dahin nicht an."
        ),
    ),
    "keine_werte": (
        "amber",
        merke("Gerät meldet keine Funkwerte"),
        merke(
            "Das Gerät antwortet, nennt aber keine Werte zum Mobilfunk – vielleicht ohne Netz oder eine andere Firmware. Rohdaten über ⚙ › 🔬 Diagnose abfragen."
        ),
    ),
    "fehler": (
        "rot",
        merke("Lesen fehlgeschlagen"),
        merke(
            "Beim Lesen des vorgeschalteten Geräts ist ein Fehler aufgetreten; Heimnetz versucht es im nächsten Takt wieder."
        ),
    ),
    "glasfaser": (
        "grau",
        merke("Glasfaser-Modem erkannt"),
        merke(
            "Werte eines Glasfaser-Modems (ONT) liest Heimnetz noch nicht – dafür fehlt eine echte Antwort eines Geräts. Rohdaten über ⚙ › 🔬 Diagnose abfragen. Ein ONT am Internet-Anschluss der FRITZ!Box ist vom Heimnetz aus oft gar nicht erreichbar."
        ),
    ),
}
# Befunde, die einen Reparatur-Hinweis in Home Assistant bekommen (der Nutzer kann sie lösen)
REPARATUR = {"anmeldung_abgelehnt": "modem_anmeldung", "nicht_erreichbar": "modem_fehlt"}


def befund_daten(kennung: str | None, s: str = DE) -> dict[str, str] | None:
    """Befund für die Seite: Kennung, Lage, Titel und Text in der Sprache der Abfrage."""
    if kennung is None or kennung not in BEFUNDE:
        return None
    lage, titel, text = BEFUNDE[kennung]
    return {"kennung": kennung, "lage": lage, "titel": t(titel, s), "text": t(text, s)}
