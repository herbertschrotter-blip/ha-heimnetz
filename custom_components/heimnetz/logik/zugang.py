"""Woher kommt das Internet (WU-0009): Zugangsart aus dem, was die FRITZ!Box meldet, plus die Wahl des Admins.

Ohne Home Assistant und ohne Netz. Gelesen wird die Box nur im gemeinsamen Abruf (box.py, langsamer Takt) über diese
TR-064-Aktionen (AVM/FRITZ!-Doku „TR-064 Support“, fritz.support/resources):

- `WANCommonInterfaceConfig1` · `GetCommonLinkProperties`: `NewWANAccessType` (DSL, Ethernet, X_AVM-DE_Fiber,
  X_AVM-DE_UMTS, X_AVM-DE_Cable, X_AVM-DE_LTE, unknown), `NewPhysicalLinkStatus` (Up, Down, Initializing,
  Unavailable), `NewLayer1Downstream/UpstreamMaxBitRate` (bit/s)
- `WANCommonInterfaceConfig1` · `X_AVM-DE_GetAddonInfos` (erst neuere FRITZ!OS): `NewX_AVM-DE_WANAccessType` (Cable,
  DSL, Ethernet, Fiber, IP-Client, Mobile, Other) – „IP-Client“ heißt: die Box hängt hinter einem anderen Router
- `X_AVM-DE_WANMobileConnection1` · `GetInfo`: `NewEnable` (Mobilfunk an der Box eingeschaltet)
- `WANDSLInterfaceConfig1` · `GetInfo`: `NewStatus`; `X_AVM-DE_WANFiber1` · `GetInfo`: `NewFiberMode`
- `Layer3Forwarding1` · `GetDefaultConnectionService` und dort `GetExternalIPAddress`: nur die Art der Adresse
  (privat, Netz des Anbieters, öffentlich) und daraus ein Vorschlag für die Adresse eines vorgeschalteten Geräts –
  die Adresse selbst bleibt in box.py.

Ein Gateway der WAN-Verbindung meldet TR-064 nicht; abgesucht wird nichts (kein Abfragen fremder Adressen).
Zugangsarten (Kennungen fest): mobilfunk, dsl, glasfaser, kabel, extern (vorgeschaltetes Modem oder Router).
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from .ereignis import INFO, WARNUNG, Ereignis
from .sprache import DE, merke, t

ARTEN = ("mobilfunk", "dsl", "glasfaser", "kabel", "extern")
WAHLEN = ("auto", "box_mobil", "extern", "dsl", "glasfaser", "kabel")
ERSATZ_WAHLEN = ("auto", "kein")
UEBLICHE_ADRESSEN = ("192.168.0.1", "192.168.1.1", "192.168.8.1")
_PRIVAT = tuple(ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
FESTE = (
    "dsl",
    "glasfaser",
    "kabel",
)  # Zugänge, für die ein Mobilfunk-Stick als Ersatz einspringen kann
ERSATZ_VERGESSEN_S = 14 * 86_400  # so lange gilt ein Ausfall des festen Zugangs als „über Ersatz“

# NewWANAccessType → Art
_ZUGANGSART = {
    "DSL": "dsl",
    "X_AVM-DE_Fiber": "glasfaser",
    "X_AVM-DE_Cable": "kabel",
    "X_AVM-DE_LTE": "mobilfunk",
    "X_AVM-DE_UMTS": "mobilfunk",
    "Ethernet": "extern",
}
# NewX_AVM-DE_WANAccessType (X_AVM-DE_GetAddonInfos) → Art
_ART_AVM = {
    "DSL": "dsl",
    "Fiber": "glasfaser",
    "Cable": "kabel",
    "Mobile": "mobilfunk",
    "Ethernet": "extern",
    "IP-Client": "extern",
}
_WAS = {
    "DSL": merke("DSL"),
    "X_AVM-DE_Fiber": merke("Glasfaser"),
    "X_AVM-DE_Cable": merke("Kabel"),
    "X_AVM-DE_LTE": merke("Mobilfunk (LTE/5G)"),
    "X_AVM-DE_UMTS": merke("Mobilfunk (UMTS)"),
    "Ethernet": merke("LAN 1 (externes Modem oder Router)"),
}
_LINK = {
    "Up": merke("verbunden"),
    "Down": merke("nicht verbunden"),
    "Initializing": merke("baut auf"),
    "Unavailable": merke("nicht verfügbar"),
}
DSL_STATUS = {
    "Up": merke("synchron"),
    "Initializing": merke("baut auf"),
    "EstablishingLink": merke("baut auf"),
    "NoSignal": merke("kein Signal"),
    "Error": merke("Fehler"),
    "Disabled": merke("ausgeschaltet"),
}
TITEL = {
    "mobilfunk": merke("Mobilfunk"),
    "dsl": "DSL",
    "glasfaser": merke("Glasfaser"),
    "kabel": merke("Kabel"),
    "extern": merke("ein vorgeschaltetes Gerät"),
    "": merke("unbekannt"),
}


@dataclass(frozen=True)
class Meldung:
    """Was die Box über ihren Zugang meldet; "" / None = nicht gemeldet oder nicht gefragt."""

    zugangsart: str = ""  # NewWANAccessType
    link: str = ""  # NewPhysicalLinkStatus
    art_avm: str = ""  # NewX_AVM-DE_WANAccessType (X_AVM-DE_GetAddonInfos)
    down_bit: int | None = None  # NewLayer1DownstreamMaxBitRate
    up_bit: int | None = None  # NewLayer1UpstreamMaxBitRate
    mobil_dienst: bool = False  # X_AVM-DE_WANMobileConnection1 vorhanden
    mobil_an: bool | None = None  # dort GetInfo NewEnable
    dsl_dienst: bool = False  # WANDSLInterfaceConfig1 vorhanden
    dsl_status: str = ""  # dort GetInfo NewStatus
    faser_dienst: bool = False  # X_AVM-DE_WANFiber1 vorhanden
    faser_modus: str = ""  # dort GetInfo NewFiberMode (AON, GPON, XGSPON …)
    wan_netz: str = ""  # Art der WAN-Adresse der Box: privat, anbieter (CGNAT), oeffentlich
    vorschlag: str = ""  # Adresse für ein vorgeschaltetes Gerät (nur bei privater WAN-Adresse)


def wan_netz(adresse: str) -> tuple[str, str]:
    """Art der WAN-Adresse der Box und Vorschlag für die Adresse des Geräts davor (die .1 desselben /24-Netzes; nur
    bei privater Adresse). Die Adresse selbst wird nicht weitergegeben."""
    try:
        ip = ipaddress.ip_address(adresse.strip())
    except ValueError:
        return "", ""
    if not isinstance(ip, ipaddress.IPv4Address) or ip.is_unspecified:
        return "", ""
    if ip in ipaddress.ip_network("100.64.0.0/10"):
        return "anbieter", ""
    if any(ip in n for n in _PRIVAT):
        a, b, c, _ = str(ip).split(".")
        return "privat", f"{a}.{b}.{c}.1"
    return "oeffentlich", ""


def art_erkennen(m: Meldung, haupt_vorher: str = "") -> tuple[str, bool]:
    """Zugangsart und ob gerade der Ersatz trägt. Meldet die Box Mobilfunk, war vorher aber ein fester Zugang (DSL,
    Glasfaser, Kabel) erkannt und ist dessen Anschluss noch da, ist das der Ersatz bei Ausfall – nicht der Wechsel."""
    art = _ZUGANGSART.get(m.zugangsart) or _ART_AVM.get(m.art_avm, "")
    if m.art_avm == "IP-Client":
        art = (
            "extern"  # Box hinter einem anderen Router, auch wenn die Zugangsart etwas anderes sagt
        )
    if art == "mobilfunk" and haupt_vorher in FESTE:
        noch_da = {"dsl": m.dsl_dienst, "glasfaser": m.faser_dienst, "kabel": True}[haupt_vorher]
        if noch_da:
            return haupt_vorher, True
    return art, False


def ersatz_da(m: Meldung, art: str) -> bool:
    """Mobilfunk an der Box eingeschaltet, Internet kommt aber über einen festen Zugang: springt bei Ausfall ein,
    wenn das in der Box so eingestellt ist (TR-064 meldet die Einstellung selbst nicht)."""
    return art in FESTE and m.mobil_dienst and m.mobil_an is True


def dsl_lesen(m: Meldung, haupt: str = "") -> bool:
    """DSL-Werte lesen: das Internet kommt über DSL, die Leitung steht oder sie ist gerade ausgefallen (Ersatz trägt).
    Eine Box mit ungenutztem DSL-Anschluss bekommt so keine DSL-Werte und keine DSL-Entitäten."""
    return m.dsl_dienst and (m.zugangsart == "DSL" or m.dsl_status == "Up" or haupt == "dsl")


def faser_lesen(m: Meldung, haupt: str = "") -> bool:
    """Glasfaser-Werte lesen: das Internet kommt über Glasfaser oder sie ist gerade ausgefallen."""
    return m.faser_dienst and (
        m.zugangsart == "X_AVM-DE_Fiber" or m.art_avm == "Fiber" or haupt == "glasfaser"
    )


def wirksam(auto: str, wahl: str) -> str:
    """Art nach der Wahl des Admins; „auto“ = erkannt."""
    return (
        {"box_mobil": "mobilfunk", "extern": "extern"}.get(wahl, wahl) if wahl != "auto" else auto
    )


def haupt_merken(
    vorher: str, ersatz_seit: float | None, art: str, ersatz_aktiv: bool, jetzt: float
) -> tuple[str, float | None]:
    """Gedächtnis für art_erkennen: der zuletzt erkannte feste Zugang und seit wann der Ersatz trägt. Trägt er länger
    als ERSATZ_VERGESSEN_S, gilt der Mobilfunk als neuer Zugang (Anschluss gewechselt)."""
    if ersatz_aktiv:
        seit = ersatz_seit or jetzt
        if jetzt - seit >= ERSATZ_VERGESSEN_S:
            return "", None
        return vorher, seit
    if art in FESTE:
        return art, None
    if art:
        return "", None
    return vorher, None  # nichts erkannt: Gedächtnis behalten


@dataclass(frozen=True)
class Internetzugang:
    """Fertig für Seite und Kopf; Texte in der Sprache der Abfrage."""

    art: str  # ARTEN oder "" (unbekannt)
    quelle: str  # "automatisch" oder "festgelegt"
    weg: str  # "eingebaut", "stick", "vorgeschaltet" oder ""
    titel: str  # „Internet über Mobilfunk“
    geraet: str
    weg_text: str
    belege: tuple[str, ...]
    ersatz: str  # "" oder "mobilfunk"
    ersatz_aktiv: bool
    ersatz_text: str
    vorschlag: str  # was automatisch erkannt ist („Mobilfunk über FRITZ!Box 6860 5G“)
    vorschlag_art: str
    abweichung: bool  # festgelegt, aber die Box meldet etwas anderes
    adresse: str  # Adresse des vorgeschalteten Geräts (gewählt oder vorgeschlagen), sonst ""
    adressen: tuple[str, ...]  # Vorschläge für die Adresse (nur private)
    kopf: str  # Zeile im Kopf der Seite


def _mit_stick(modell: str) -> bool:
    """Ohne „LTE“ oder „5G“ im Namen hat die Box kein eingebautes Mobilfunk-Modem – dann ist es ein USB-Stick."""
    m = modell.upper()
    return bool(m) and "LTE" not in m and "5G" not in m


def _weg(art: str, modell: str) -> str:
    if art == "extern":
        return "vorgeschaltet"
    if art == "mobilfunk":
        return "stick" if _mit_stick(modell) else "eingebaut"
    return "eingebaut" if art else ""


def _weg_text(art: str, weg: str, m: Meldung, adresse: str, s: str) -> str:
    if weg == "vorgeschaltet":
        return t("vorgeschaltet über {adresse} · Beta", s, adresse=adresse)
    if art == "mobilfunk":
        return t("Mobilfunk-Stick (USB)" if weg == "stick" else "eingebautes Modem", s)
    if art == "dsl":
        return t("eingebautes DSL-Modem", s)
    if art == "glasfaser":
        return t("eingebautes Glasfaser-Modem", s) + (
            f" ({m.faser_modus})" if m.faser_modus else ""
        )
    if art == "kabel":
        return t("eingebautes Kabelmodem", s)
    return ""


def belege(m: Meldung, art: str, ersatz_aktiv: bool, mobil_technik: str, s: str) -> list[str]:
    """Kurze Sätze, woran die Zugangsart erkannt ist – nur aus dem, was die Box meldet."""
    b: list[str] = []
    if m.zugangsart in _WAS:
        link = _LINK.get(m.link)
        b.append(
            t("FRITZ!Box meldet: Internet über {was}", s, was=_WAS[m.zugangsart])
            + (f", {t(link, s)}" if link else "")
        )
    else:
        b.append(t("FRITZ!Box meldet keine Zugangsart", s))
    if m.art_avm == "IP-Client":
        b.append(t("Betriebsart der Box: IP-Client (hinter einem anderen Router)", s))
    if m.mobil_dienst:
        if mobil_technik and mobil_technik.lower() not in ("unknown", "unkown"):
            b.append(t("Mobilfunk-Modem der Box: {technik}", s, technik=mobil_technik))
        elif m.mobil_an is False:
            b.append(t("Mobilfunk-Modem der Box: ausgeschaltet", s))
        else:
            b.append(t("Mobilfunk-Modem der Box: nicht verbunden", s))
    else:
        b.append(t("Mobilfunk an der Box: meldet die Box nicht", s))
    if m.dsl_dienst:
        b.append(
            t(
                "DSL-Anschluss der Box: {status}",
                s,
                status=DSL_STATUS.get(m.dsl_status, m.dsl_status or "–"),
            )
        )
    elif art == "dsl":
        b.append(t("DSL-Werte: meldet die Box nicht", s))
    if m.faser_dienst:
        b.append(t("Glasfaser-Modul der Box: {modus}", s, modus=m.faser_modus or "–"))
    if art == "extern" or m.zugangsart == "Ethernet":
        if m.wan_netz == "privat":
            b.append(
                t(
                    "Die Box hat im WAN eine private Adresse – davor steht ein Modem oder Router (vermutlich unter {adresse})",
                    s,
                    adresse=m.vorschlag,
                )
            )
        elif m.wan_netz == "anbieter":
            b.append(t("Die Box hat eine Adresse aus dem Netz des Anbieters (CGNAT)", s))
        elif m.wan_netz == "oeffentlich":
            b.append(
                t(
                    "Die Box hat eine öffentliche Adresse – das Gerät davor arbeitet als reines Modem",
                    s,
                )
            )
    if ersatz_aktiv:
        b.append(t("Gerade aktiv: Ersatz über Mobilfunk – der feste Zugang ist ausgefallen", s))
    return b


def _adressen(m: Meldung) -> tuple[str, ...]:
    return tuple(dict.fromkeys(a for a in (m.vorschlag, *UEBLICHE_ADRESSEN) if a))


def beschreiben(
    m: Meldung,
    auto: str,
    ersatz_aktiv: bool,
    wahl: str = "auto",
    adresse: str | None = None,
    ersatz_wahl: str = "auto",
    modell: str = "",
    mobil_technik: str = "",
    s: str = DE,
) -> Internetzugang:
    """Zugang für die Seite: erkannt (`auto`, aus art_erkennen) oder festgelegt (`wahl`), mit Belegen und Ersatz."""
    art = wirksam(auto, wahl)
    weg = _weg(art, modell)
    box = modell or "FRITZ!Box"
    adressen = _adressen(m)
    adr = (adresse or adressen[0]) if art == "extern" else ""
    if art == "extern":
        geraet = t("vorgeschaltetes Modem" if wahl == "extern" else "vorgeschaltetes Gerät", s)
        titel = t(
            "Internet über Mobilfunk"
            if wahl == "extern"
            else "Internet über ein vorgeschaltetes Gerät",
            s,
        )
    elif art:
        geraet = box
        titel = t("Internet über {art}", s, art=TITEL[art])
    else:
        geraet = box
        titel = t("Zugang nicht erkannt", s)
    ersatz = "mobilfunk" if ersatz_wahl != "kein" and (ersatz_aktiv or ersatz_da(m, art)) else ""
    ersatz_text = (
        t("Mobilfunk an der FRITZ!Box – gerade aktiv", s)
        if ersatz and ersatz_aktiv
        else t("Mobilfunk an der FRITZ!Box, springt bei Ausfall ein", s)
        if ersatz
        else ""
    )
    vorschlag = (
        t("{art} über {geraet}", s, art=TITEL[auto], geraet=box)
        if auto and auto != "extern"
        else t("ein vorgeschaltetes Gerät", s)
        if auto == "extern"
        else t("unbekannt", s)
    )
    kurz = t(TITEL[art], s) if art != "extern" else geraet
    zusatz = mobil_technik if art == "mobilfunk" and mobil_technik else ""
    kopf = " · ".join(
        x
        for x in (
            box,
            kurz + (f" {zusatz}" if zusatz else ""),
            t("über Ersatz", s) if ersatz and ersatz_aktiv else "",
        )
        if x
    )
    return Internetzugang(
        art=art,
        quelle="automatisch" if wahl == "auto" else "festgelegt",
        weg=weg,
        titel=titel,
        geraet=geraet,
        weg_text=_weg_text(art, weg, m, adr, s),
        belege=tuple(belege(m, auto, ersatz_aktiv, mobil_technik, s)),
        ersatz=ersatz,
        ersatz_aktiv=bool(ersatz and ersatz_aktiv),
        ersatz_text=ersatz_text,
        vorschlag=vorschlag,
        vorschlag_art=auto,
        abweichung=wahl != "auto" and bool(auto) and art != auto,
        adresse=adr,
        adressen=adressen,
        kopf=kopf,
    )


def abgleich(
    vorher: str, art: str, ersatz_vorher: bool, ersatz: bool, s: str = DE
) -> list[Ereignis]:
    """Journal: anderer Zugang erkannt, Ersatz springt ein oder ist wieder aus. Beim ersten Erkennen nichts."""
    neu: list[Ereignis] = []
    if vorher and art and art != vorher:
        neu.append(
            Ereignis(
                "zugang",
                INFO,
                t(
                    "Internetzugang: jetzt {art} (vorher {vorher})",
                    s,
                    art=TITEL[art],
                    vorher=TITEL[vorher],
                ),
            )
        )
    if ersatz and not ersatz_vorher:
        neu.append(Ereignis("ersatz_an", WARNUNG, t("Ersatz über Mobilfunk springt ein", s)))
    elif ersatz_vorher and not ersatz:
        neu.append(
            Ereignis(
                "ersatz_aus",
                INFO,
                t(
                    "Wieder über den festen Zugang, Ersatz aus"
                    if art in FESTE
                    else "Ersatz beendet – Mobilfunk gilt jetzt als Zugang",
                    s,
                ),
            )
        )
    return neu


def ersatz_zeiten(
    an: list[float], aus: list[float], ab: float, jetzt: float, aktiv: bool
) -> tuple[int, float, float | None]:
    """Umschaltungen auf den Ersatz seit `ab`, wie lange er getragen hat (Sekunden) und wann zuletzt. `an`/`aus` sind
    die Zeitpunkte aus dem Journal; ein Zeitraum ohne Ende läuft bis jetzt, wenn der Ersatz gerade trägt."""
    ereignisse = sorted([(x, True) for x in an] + [(x, False) for x in aus])
    seit: float | None = None
    summe = 0.0
    anzahl = 0
    letzte: float | None = None
    for zeit, ein in ereignisse:
        if ein:
            if seit is None:
                seit = zeit
                if zeit >= ab:
                    anzahl += 1
                letzte = zeit
        elif seit is not None:
            summe += max(0.0, zeit - max(seit, ab))
            seit = None
    if seit is not None and aktiv:
        summe += max(0.0, jetzt - max(seit, ab))
    return anzahl, summe, letzte
