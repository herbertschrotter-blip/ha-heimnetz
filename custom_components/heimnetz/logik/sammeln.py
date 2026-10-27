"""Ein Abruf: aus den Rohdaten der Box und den Prüfungen des Pi den neuen Stand rechnen.

Ohne Home Assistant und ohne Netz – die Rohdaten holt der Abruf (coordinator.py), hier wird nur ausgewertet.
Was zwischen zwei Abrufen erhalten bleiben muss, steht im `Gedaechtnis`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from . import befunde as bf
from . import geraete as gr
from . import leitung as ln
from . import mobil as mb
from . import protokoll as pr
from . import stoerung as sg
from . import verkehr as vk
from . import wlan as wl
from . import zugang as zg
from .ereignis import INFO, KRITISCH, Ereignis
from .sprache import DE, merke, t

LANGSAM_S = 600  # DHCP-Test, Adressquelle je Gerät, Heimnetz: alle 10 min
GW_STABIL_S = 86_400  # eine neue Hardware-Adresse der Box gilt erst nach 24 h als die bekannte
PI_PRUEFUNGEN = (
    ("box", merke("FRITZ!Box vom Pi aus")),
    ("internet", merke("Internet vom Pi aus")),
    ("dns", merke("Namensauflösung am Pi")),
)


@dataclass
class Gedaechtnis:
    """Was der nächste Abruf vom vorigen wissen muss."""

    geraete: dict[str, gr.Geraet] | None = None  # None = noch kein Abruf gelungen
    quellen: dict[str, str] = field(default_factory=dict)
    gesehen: list[str] = field(default_factory=list)
    lan: bf.Heimnetz = field(default_factory=bf.Heimnetz)
    befunde: dict[str, str] = field(default_factory=dict)
    ring: list[vk.Zaehlerstand] = field(default_factory=list)
    mobil_dienst: bool | None = (
        None  # None: noch unbekannt; False: Box ohne Mobilfunk-Modem, nicht mehr fragen
    )
    mobil_technik: str = ""
    mobil_zelle: str = ""
    mobil_laufzeit: int | None = None
    mobil_baender: str = ""
    wlan_baender: tuple[
        wl.Band, ...
    ] = ()  # nur im Speicher: wird nach einem Neustart sofort neu gelesen
    wlan_gast: bool | None = None
    wlan_kanaele: dict[str, int] = field(default_factory=dict)
    wlan_schnell: list[str] = field(default_factory=list)  # MAC: schon auf 5 oder 6 GHz gesehen
    mesh: dict[str, str] = field(
        default_factory=dict
    )  # MAC → Modell der Mesh-Geräte der Box (AN-0001)
    stoerung: sg.Stoerung | None = None  # offene Internet-Störung (AN-0003)
    pi: bf.PiVerbindung | None = None
    gw_mac_bekannt: str = ""
    gw_wechsel_seit: float | None = None
    dhcp: bf.DhcpTest | None = None
    langsam_t: float = 0.0
    # WU-0009: Zugang (langsam gelesen) und Werte der Leitung
    zugang: zg.Meldung | None = None
    zugang_art: str = ""  # zuletzt erkannte Art (ohne Wahl des Admins)
    zugang_haupt: str = (
        ""  # zuletzt erkannter fester Zugang (DSL, Glasfaser, Kabel): Mobilfunk danach = Ersatz
    )
    ersatz_seit: float | None = None
    dsl: ln.Dsl | None = None
    dsl_neusync: list[float] = field(default_factory=list)
    dsl_crc_h: float | None = None
    dsl_fec_h: float | None = None
    faser: ln.Faser | None = None
    faser_fehler_h: float | None = None
    dsl_seit: float | None = None  # letzte erkannte Neusynchronisierung (bleibt auch nach 7 Tagen)

    def langsam_faellig(self, jetzt: float) -> bool:
        return jetzt - self.langsam_t >= LANGSAM_S


@dataclass(frozen=True)
class Rohdaten:
    """Was ein Abruf geholt hat; None = nicht abgefragt oder fehlgeschlagen (Grund in `fehler`)."""

    jetzt: float
    pi: bf.PiVerbindung
    protokoll: list[pr.BoxZeile] | None = None
    lan: bf.Heimnetz | None = None
    geraete: dict[str, gr.Geraet] | None = None
    quellen: dict[str, str] | None = None
    mobil: mb.Mobilfunk | None = None
    ohne_mobilfunk: bool = False  # die Box hat den Dienst nicht
    zaehler: vk.Zaehlerstand | None = None
    dhcp: bf.DhcpTest | None = None
    mobil_baender: str | None = None  # eingeschaltete Bänder (langsam)
    wlan_baender: tuple[wl.Band, ...] | None = None  # Funknetze der Box (langsam)
    wlan_gast: bool | None = None
    wlan_geraete: tuple[wl.Funkgeraet, ...] | None = None
    mesh: dict[str, str] | None = None  # Mesh-Geräte (langsam)
    zugang: zg.Meldung | None = None  # WU-0009: Zugang (langsam)
    dsl: ln.Dsl | None = None  # nur mit DSL-Dienst (langsam)
    faser: ln.Faser | None = None  # nur mit Glasfaser-Dienst (langsam)
    fehler: tuple[str, ...] = ()
    sprache: str = DE  # Sprache der Texte (Befunde, Journal), nach Home Assistant


@dataclass(frozen=True)
class Stand:
    """Ergebnis eines Abrufs – daraus lesen Entitäten und Schnittstelle."""

    zeit: float
    box_erreichbar: bool
    gesamt: str
    befunde: tuple[bf.Befund, ...]
    geraete: dict[str, gr.Geraet]
    lan: bf.Heimnetz
    pi: bf.PiVerbindung
    dhcp: bf.DhcpTest | None
    mobil: mb.Mobilfunk | None
    rate: vk.Rate | None
    ereignisse: tuple[Ereignis, ...]
    protokoll: tuple[pr.Protokolleintrag, ...]
    fehler: tuple[str, ...]
    wlan: wl.Wlan | None = None  # None = Box ohne WLAN-Dienst oder nicht gelesen
    mobil_baender: str = ""
    mesh: dict[str, str] = field(default_factory=dict)
    # WU-0009: Zugang (zuletzt gelesen) und Werte der Leitung; None = noch nicht gelesen oder nicht vorhanden
    zugang: zg.Meldung | None = None
    zugang_art: str = ""  # erkannt, ohne Wahl des Admins
    ersatz_aktiv: bool = False
    dsl: ln.Dsl | None = None
    dsl_crc_h: float | None = None
    dsl_fec_h: float | None = None
    dsl_neusync: int = 0  # in 7 Tagen
    dsl_seit: float | None = None  # letzte erkannte Neusynchronisierung
    faser: ln.Faser | None = None
    faser_fehler_h: float | None = None

    @property
    def online(self) -> int:
        return sum(1 for g in self.geraete.values() if g.aktiv)


def _gw_bekannt(g: Gedaechtnis, gw_mac: str, jetzt: float) -> str:
    """Bekannte Hardware-Adresse der Box. Meldet sich eine andere, bleibt der Befund stehen, bis sie 24 h stabil ist."""
    if not g.gw_mac_bekannt:
        g.gw_mac_bekannt = gw_mac
    if gw_mac and gw_mac != g.gw_mac_bekannt:
        if g.gw_wechsel_seit is None:
            g.gw_wechsel_seit = jetzt
        elif jetzt - g.gw_wechsel_seit >= GW_STABIL_S:
            g.gw_mac_bekannt, g.gw_wechsel_seit = gw_mac, None
    else:
        g.gw_wechsel_seit = None
    return g.gw_mac_bekannt


def auswerten(g: Gedaechtnis, roh: Rohdaten) -> Stand:
    """Neuen Stand rechnen und das Gedächtnis fortschreiben."""
    ereignisse: list[Ereignis] = []
    sprache = roh.sprache

    protokoll = pr.neue_zeilen(roh.protokoll, g.gesehen) if roh.protokoll is not None else []

    if roh.lan is not None:
        g.lan = roh.lan
    if roh.quellen is not None:
        g.quellen.update(roh.quellen)

    geraete: dict[str, gr.Geraet] = {}
    if roh.geraete is not None:
        geraete = gr.ergaenzen(roh.geraete, g.geraete or {}, g.quellen)
        if g.geraete is None:
            online = sum(1 for x in geraete.values() if x.aktiv)
            ereignisse.append(
                Ereignis(
                    "start",
                    INFO,
                    t(
                        "Erfassung gestartet: {n} Geräte bekannt, {online} online",
                        sprache,
                        n=len(geraete),
                        online=online,
                    ),
                )
            )
        else:
            ereignisse += gr.abgleich(g.geraete, geraete, sprache)
        g.geraete = geraete
    box_erreichbar = roh.geraete is not None

    if roh.ohne_mobilfunk:
        g.mobil_dienst = False
    neu_mobil: Ereignis | None = None
    if roh.mobil is not None:
        g.mobil_dienst = True
        ereignisse += mb.abgleich(g.mobil_technik, g.mobil_zelle, roh.mobil, sprache)
        if roh.mobil.technik:
            g.mobil_technik = roh.mobil.technik
            g.mobil_zelle = roh.mobil.zellkennung or g.mobil_zelle
        neu_mobil = mb.neu_eingewaehlt(g.mobil_laufzeit, roh.mobil, sprache)
        if neu_mobil is not None:
            ereignisse.append(neu_mobil)
        if roh.mobil.laufzeit_s is not None:
            g.mobil_laufzeit = roh.mobil.laufzeit_s
    if roh.mobil_baender is not None:
        g.mobil_baender = roh.mobil_baender
    if roh.mesh is not None:
        g.mesh = roh.mesh

    if roh.wlan_baender is not None:
        neu_kanal, g.wlan_kanaele = wl.abgleich(g.wlan_kanaele, roh.wlan_baender, sprache)
        ereignisse += neu_kanal
        g.wlan_baender, g.wlan_gast = roh.wlan_baender, roh.wlan_gast
    wlan = None
    if roh.wlan_geraete is not None:
        wlan = wl.Wlan(g.wlan_baender, g.wlan_gast, roh.wlan_geraete)
        g.wlan_schnell = wl.schnell_gesehen(g.wlan_schnell, wlan, g.geraete)

    if roh.zaehler is not None:
        g.ring = vk.fortschreiben(g.ring, roh.zaehler)

    ereignisse += _zugang(g, roh, sprache)

    alt = g.pi
    gw_mac = roh.pi.gw_mac or (
        alt.gw_mac if alt else ""
    )  # gerade kein ARP-Eintrag: alten Wert behalten
    pi = bf.PiVerbindung(
        roh.pi.box, roh.pi.internet, roh.pi.dns, gw_mac, _gw_bekannt(g, gw_mac, roh.jetzt)
    )
    if alt is not None:
        for feld, name in PI_PRUEFUNGEN:
            jetzt_ok, vorher_ok = getattr(pi, feld), getattr(alt, feld)
            if jetzt_ok != vorher_ok:
                ereignisse.append(
                    Ereignis(
                        f"pi_{feld}",
                        INFO if jetzt_ok else KRITISCH,
                        t(
                            "{name}: wieder erreichbar" if jetzt_ok else "{name}: NICHT erreichbar",
                            sprache,
                            name=name,
                        ),
                    )
                )
    g.pi = pi

    if roh.dhcp is not None:
        g.dhcp = roh.dhcp
    if roh.quellen is not None or roh.dhcp is not None:
        g.langsam_t = roh.jetzt

    lage = sg.lage(
        pi.box,
        roh.mobil.laufzeit_s if roh.mobil else None,
        mb.schwaechster(roh.mobil),
        neu_mobil is not None,
        roh.mobil is not None,
    )
    g.stoerung, abschluss = sg.fortschreiben(g.stoerung, pi.internet, roh.jetzt, lage, sprache)
    if abschluss is not None:
        ereignisse.append(abschluss)
    liste = (
        bf.finden(geraete, g.lan, g.dhcp, pi, lage, sprache)
        if box_erreichbar
        else bf.finden({}, bf.Heimnetz(), None, pi, lage, sprache)
    )
    if box_erreichbar:  # ohne Gerätetabelle bleibt offen, ob alte Befunde erledigt sind
        neu, g.befunde = bf.abgleich(g.befunde, liste, sprache)
        ereignisse += neu

    return Stand(
        zeit=roh.jetzt,
        box_erreichbar=box_erreichbar,
        gesamt=bf.gesamtstand(liste, box_erreichbar),
        befunde=tuple(liste),
        geraete=geraete,
        lan=g.lan,
        pi=pi,
        dhcp=g.dhcp,
        mobil=roh.mobil,
        rate=vk.letzte_rate(g.ring) if roh.zaehler is not None else None,
        ereignisse=tuple(ereignisse),
        protokoll=tuple(protokoll),
        fehler=roh.fehler,
        wlan=wlan,
        mobil_baender=g.mobil_baender,
        mesh=dict(g.mesh),
        zugang=g.zugang,
        zugang_art=g.zugang_art,
        ersatz_aktiv=g.ersatz_seit is not None,
        dsl=g.dsl,
        dsl_crc_h=g.dsl_crc_h,
        dsl_fec_h=g.dsl_fec_h,
        dsl_neusync=len(ln.neusync_fortschreiben(g.dsl_neusync, False, roh.jetzt)),
        dsl_seit=g.dsl_seit,
        faser=g.faser,
        faser_fehler_h=g.faser_fehler_h,
    )


def _zugang(g: Gedaechtnis, roh: Rohdaten, sprache: str) -> list[Ereignis]:
    """WU-0009: Zugang erkennen (mit Gedächtnis für den Ersatz) und die Werte der Leitung fortschreiben."""
    ereignisse: list[Ereignis] = []
    haupt = g.zugang_haupt  # wie im Abruf (box.py liest DSL/Glasfaser auch während des Ersatzes)
    if roh.zugang is not None:
        art, ersatz = zg.art_erkennen(roh.zugang, g.zugang_haupt)
        ereignisse += zg.abgleich(
            g.zugang_art if g.zugang is not None else "",
            art,
            g.ersatz_seit is not None,
            ersatz,
            sprache,
        )
        g.zugang, g.zugang_art = roh.zugang, art
        g.zugang_haupt, g.ersatz_seit = zg.haupt_merken(
            g.zugang_haupt, g.ersatz_seit, art, ersatz, roh.jetzt
        )
    if roh.dsl is not None:
        neu = ln.dsl_neu_synchron(g.dsl, roh.dsl)
        if neu:
            ereignisse.append(Ereignis("dsl_sync", INFO, t("DSL neu synchronisiert", sprache)))
        g.dsl_crc_h, g.dsl_fec_h = ln.dsl_fehler_je_stunde(g.dsl, roh.dsl)
        g.dsl_neusync = ln.neusync_fortschreiben(g.dsl_neusync, neu, roh.jetzt)
        if neu:
            g.dsl_seit = roh.jetzt
        g.dsl = roh.dsl
    elif roh.zugang is not None and not zg.dsl_lesen(roh.zugang, haupt):
        # kein oder ungenutzter Anschluss; ein einzelner Lesefehler lässt den letzten Stand stehen
        g.dsl, g.dsl_crc_h, g.dsl_fec_h, g.dsl_seit = None, None, None, None
    if roh.faser is not None:
        g.faser_fehler_h = ln.faser_fehler_je_stunde(g.faser, roh.faser)
        g.faser = roh.faser
    elif roh.zugang is not None and not zg.faser_lesen(roh.zugang, haupt):
        g.faser, g.faser_fehler_h = None, None
    return ereignisse


GEDAECHTNIS_VERSION = 1


def gedaechtnis_als_dict(g: Gedaechtnis) -> dict[str, Any]:
    """Für die Datenbank (JSON): was nach einem Neustart von HA weiter gelten soll."""
    return {
        "version": GEDAECHTNIS_VERSION,
        "geraete": None if g.geraete is None else [asdict(x) for x in g.geraete.values()],
        "quellen": g.quellen,
        "gesehen": g.gesehen,
        "lan": asdict(g.lan),
        "befunde": g.befunde,
        "ring": [asdict(z) for z in g.ring],
        "mobil_dienst": g.mobil_dienst,
        "mobil_technik": g.mobil_technik,
        "mobil_zelle": g.mobil_zelle,
        "mobil_laufzeit": g.mobil_laufzeit,
        "mobil_baender": g.mobil_baender,
        "wlan_kanaele": g.wlan_kanaele,
        "wlan_schnell": g.wlan_schnell,
        "mesh": g.mesh,
        "stoerung": g.stoerung.als_dict() if g.stoerung else None,
        "gw_mac_bekannt": g.gw_mac_bekannt,
        "gw_wechsel_seit": g.gw_wechsel_seit,
        "zugang": asdict(g.zugang) if g.zugang else None,
        "zugang_art": g.zugang_art,
        "zugang_haupt": g.zugang_haupt,
        "ersatz_seit": g.ersatz_seit,
        "dsl": asdict(g.dsl) if g.dsl else None,
        "dsl_neusync": g.dsl_neusync,
        "dsl_seit": g.dsl_seit,
        "faser": asdict(g.faser) if g.faser else None,
    }


def gedaechtnis_aus_dict(d: dict[str, Any]) -> Gedaechtnis:
    """Gegenstück zu gedaechtnis_als_dict; eine andere Version ergibt ein leeres Gedächtnis."""
    g = Gedaechtnis()
    if d.get("version") != GEDAECHTNIS_VERSION:
        return g
    if d.get("geraete") is not None:
        g.geraete = {x["mac"]: gr.Geraet(**x) for x in d["geraete"]}
    g.quellen = dict(d.get("quellen") or {})
    g.gesehen = list(d.get("gesehen") or [])
    g.lan = bf.Heimnetz(**(d.get("lan") or {}))
    g.befunde = dict(d.get("befunde") or {})
    g.ring = [vk.Zaehlerstand(**z) for z in d.get("ring") or []]
    g.mobil_dienst = d.get("mobil_dienst")
    g.mobil_technik = d.get("mobil_technik") or ""
    g.mobil_zelle = d.get("mobil_zelle") or ""
    g.mobil_laufzeit = d.get("mobil_laufzeit")
    g.mobil_baender = d.get("mobil_baender") or ""
    g.wlan_kanaele = {str(k): int(v) for k, v in (d.get("wlan_kanaele") or {}).items()}
    g.wlan_schnell = list(d.get("wlan_schnell") or [])
    g.mesh = {str(k): str(v) for k, v in (d.get("mesh") or {}).items()}
    g.stoerung = sg.aus_dict(d.get("stoerung"))
    g.gw_mac_bekannt = d.get("gw_mac_bekannt") or ""
    g.gw_wechsel_seit = d.get("gw_wechsel_seit")
    g.zugang = zg.Meldung(**d["zugang"]) if d.get("zugang") else None
    g.zugang_art = d.get("zugang_art") or ""
    g.zugang_haupt = d.get("zugang_haupt") or ""
    g.ersatz_seit = d.get("ersatz_seit")
    g.dsl = ln.Dsl(**d["dsl"]) if d.get("dsl") else None
    g.dsl_neusync = [float(x) for x in d.get("dsl_neusync") or []]
    g.dsl_seit = d.get("dsl_seit")
    g.faser = ln.Faser(**d["faser"]) if d.get("faser") else None
    return g
