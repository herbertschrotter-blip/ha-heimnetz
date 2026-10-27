"""Fertige Daten je Reiter der Seite (über websocket.py). Die Seite rechnet nichts Fachliches: Zahlen, Lagen auf der
Farbskala (0…1), Texte und Streifen kommen von hier; die Regeln dahinter stehen in `logik/`. Datenbank-Zugriffe
laufen im Executor.

Sprache (WU-0006): Texte entstehen in der Sprache von Home Assistant (`hass.config.language`, Deutsch oder Englisch,
`logik/sprache.py`); Journalzeilen bleiben in der Sprache, in der sie geschrieben wurden.

Datenschutz: Geräte tragen statt der Hardware-Adresse eine gesalzene Kennung (`verlauf.geraete_id`), und aus allen
Texten an die Seite werden Hardware-Adressen entfernt (`werte.ohne_mac`).
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util

from . import abfragen as ab
from .const import CONF_MODEM_KENNWORT, sprache
from .logik import arten as ar
from .logik import auswertung as aw
from .logik import befunde as bf
from .logik import geraete as gr
from .logik import karte as ka
from .logik import leitung as ln
from .logik import messplan as mp
from .logik import mobil as mb
from .logik import ocid as lc
from .logik import osm as lo
from .logik import verbrauch as vb
from .logik import verlauf as vl
from .logik import vorgeschaltet as ve
from .logik import wlan as wl
from .logik import zugang as zg
from .logik.ereignis import Ereignis
from .logik.sprache import merke, t
from .logik.werte import ohne_mac
from .speedtest import _mbit, _wert, alle_finden, ookla_einstellung

if TYPE_CHECKING:
    from . import Laufzeit

TAG_S = 86_400
PROTOKOLL_ARTEN = {
    "internet": ("internet",),
    "wlan": ("wlan",),
    "system": ("system", "telefon", "usb"),
}


def _jetzt() -> float:
    return dt_util.utcnow().timestamp()


def _dt(t: float) -> datetime:
    return datetime.fromtimestamp(t, dt_util.UTC)


def _mitternacht(tage_zurueck: int) -> float:
    """Lokale Mitternacht vor `tage_zurueck` Tagen – stimmt auch über eine Zeitumstellung hinweg."""
    return dt_util.start_of_local_day(
        dt_util.now().date() - timedelta(days=tage_zurueck)
    ).timestamp()


# ── Speedtest ──
async def _punkte(hass: HomeAssistant, lz: Laufzeit, jetzt: float, tage: int) -> list[aw.Punkt]:
    """Speedtest-Protokoll der letzten `tage`."""
    messungen = await hass.async_add_executor_job(
        lz.datenbank.messungen_lesen, jetzt - tage * TAG_S
    )
    return aw.aus_messungen(messungen)


def _ab_datum(lz: Laufzeit) -> float:
    ab_ = lz.einstellungen.wert.ab
    return dt_util.start_of_local_day(ab_).timestamp() if ab_ else 0.0


def _tarif(lz: Laufzeit, groesse: str) -> float | None:
    e = lz.einstellungen.wert
    return {"down": e.tarif_down, "up": e.tarif_up}.get(groesse)


def _punkt(p: aw.Punkt | None) -> dict[str, Any] | None:
    return None if p is None else asdict(p)


def _anteile(p: aw.Punkt | None, lz: Laufzeit) -> dict[str, float | None]:
    """Anteil einer Messung am Tarif je Richtung (None ohne Tarif oder Wert)."""
    e = lz.einstellungen.wert
    return {
        "down": aw.anteil(p.down if p else None, e.tarif_down),
        "up": aw.anteil(p.up if p else None, e.tarif_up),
    }


async def speedtest(
    hass: HomeAssistant,
    lz: Laufzeit,
    tage: int,
    groesse: str,
    grundlast: str,
    server: str | None,
    tag: int | None = None,
    datum: date | None = None,
) -> dict[str, Any]:
    jetzt = _jetzt()
    monat = dt_util.start_of_local_day(dt_util.now().date().replace(day=1)).timestamp()
    punkte = await _punkte(hass, lz, jetzt, max(tage, int((jetzt - monat) // TAG_S) + 1))
    tarif_down = lz.einstellungen.wert.tarif_down
    a = aw.auswerten(
        punkte,
        jetzt,
        _ab_datum(lz),
        tage,
        groesse,
        grundlast,
        server,
        _tarif(lz, groesse),
        tarif_down,
        dt_util.get_default_time_zone(),
        tag,
        datum,
        sprache(hass),
    )
    grenze = aw.schwelle(tarif_down)
    heute = dt_util.now().date()
    letzte = [p for p in punkte if p.quelle == "p"][-20:]
    serie = lz.einstellungen.letzte_serie or {}
    in_serie = {round(x["t"]) for x in serie.get("laeufe") or []}
    return {
        **{
            k: v
            for k, v in asdict(a).items()
            if k not in ("raster", "letzte", "server", "tage_liste")
        },
        "tage_liste": [
            {"datum": d, "anzahl": n, "vor_tagen": (heute - date.fromisoformat(d)).days}
            for d, n in a.tage_liste
        ],
        "einheit": aw.GROESSEN[groesse].einheit,
        "raster": [[asdict(z) for z in reihe] for reihe in a.raster],
        "server": [{"name": n, "anzahl": k} for n, k in a.server],
        "letzte": _punkt(a.letzte),
        "letzte_anteil": _anteile(a.letzte, lz),
        "schwelle": grenze,
        "volumen_monat_mb": round(sum(aw.volumen_mb(p) for p in punkte if p.t >= monat), 1),
        "messungen": [
            {
                **asdict(p),
                "belastet": p.last is not None and p.last > grenze,
                "gewicht": aw.gewicht(p, grundlast, None, grenze),
                "serie": round(p.t) in in_serie,
            }
            for p in reversed(letzte)
        ],
        "tarif_down": tarif_down,
        "tarif_up": lz.einstellungen.wert.tarif_up,
    }


async def speedtest_kachel(
    hass: HomeAssistant,
    lz: Laufzeit,
    tage: int,
    groesse: str,
    grundlast: str,
    server: str | None,
    tag: int,
    stunde: int,
) -> dict[str, Any]:
    """AN-0005: Messungen hinter einer Stundenkachel, nur auf Anfrage (Popup)."""
    jetzt = _jetzt()
    k = aw.kachel(
        await _punkte(hass, lz, jetzt, tage),
        jetzt,
        _ab_datum(lz),
        tage,
        groesse,
        grundlast,
        server,
        lz.einstellungen.wert.tarif_down,
        dt_util.get_default_time_zone(),
        tag,
        stunde,
    )
    return {**asdict(k), "einheit": aw.GROESSEN[groesse].einheit, "groesse": groesse, "tage": tage}


# ── Geräte ──
def _ha_geraete(hass: HomeAssistant) -> dict[str, tuple[str, str]]:
    """Hersteller/Modell der Geräte in Home Assistant je Hardware-Adresse (AN-0001). Die Einträge, die FRITZ!Box Tools
    für jedes Gerät im Heimnetz anlegt („Tracked device“), sagen über die Art nichts und bleiben weg."""
    out: dict[str, tuple[str, str]] = {}
    for d in dr.async_get(hass).devices:  # Iteration liefert die Einträge (.values() ist veraltet)
        modell = d.model or ""
        if "tracked device" in modell.lower():
            continue
        for art, wert in d.connections:
            if art != dr.CONNECTION_NETWORK_MAC:
                continue
            mac = wert.upper()
            # mehrere Geräte mit derselben Adresse: eines, das eine Art ergibt, gewinnt
            if mac not in out or ar.aus_ha(*out[mac]) is None:
                out[mac] = (d.manufacturer or "", modell)
    return out


def _art(
    lz: Laufzeit, g: gr.Geraet, kennung: str, ha: dict[str, tuple[str, str]], sprache_: str
) -> ar.Art:
    """Blockierend (Herstellerliste wird beim ersten Mal gelesen)."""
    return ar.bestimmen(
        g.name,
        g.mac,
        selbst=lz.einstellungen.arten.get(kennung),
        ha=ha.get(g.mac.upper()),
        mesh=lz.abruf.data.mesh.get(g.mac.upper()),
        sprache=sprache_,
    )


def _geraete_daten(
    lz: Laufzeit, jetzt: float, ha: dict[str, tuple[str, str]], sprache_: str
) -> dict[str, Any]:
    """Blockierend: Geräte mit Ereignissen der letzten 24 h, Streifen und Einstufung."""
    stand = lz.abruf.data
    ab_ = jetzt - TAG_S
    w = stand.wlan
    baender = {f.mac: wl.band_von(f, w.baender) for f in w.geraete} if w else {}
    je_mac: dict[str, list[tuple[float, Ereignis]]] = {}
    for z in reversed(lz.datenbank.journal_lesen(ab_, grenze=20_000)):
        if z.ereignis.mac:
            je_mac.setdefault(z.ereignis.mac, []).append((z.t, z.ereignis))
    liste = []
    for mac, g in stand.geraete.items():
        ev = je_mac.get(mac, [])
        if not g.aktiv and not ev:
            continue
        arten = [(t, e.art) for t, e in ev]
        start = vl.vorher(
            lz.datenbank.letzter_zustand(mac, ab_),
            next((a for _, a in arten if a in vl.WECHSEL), None),
            g.aktiv,
        )
        abbrueche = sum(1 for _, a in arten if a == "offline")
        kennung = vl.geraete_id(mac, lz.salz)
        art = _art(lz, g, kennung, ha, sprache_)
        liste.append(
            {
                "id": kennung,
                "name": ohne_mac(gr.anzeigename(g.name, sprache_)),
                "ip": g.ip,
                "art": g.art,
                "aktiv": g.aktiv,
                "einstufung": vl.einstufung(g.aktiv, abbrueche, any(a == "neu" for _, a in arten)),
                "abbrueche": abbrueche,
                "streifen": vl.streifen(vl.abschnitte(start, arten, ab_, jetzt), ab_, jetzt),
                "verbindung": gr.verbindung(g.art, g.aktiv, baender.get(mac), g.vpn),
                "band": f"{wl.band_text(b, sprache_)} GHz" if (b := baender.get(mac)) else "",
                "kat": art.kat,
                "art_quelle": art.quelle,
            }
        )
    liste.sort(
        key=lambda x: (x["einstufung"] not in ("neu", "wackelt"), not x["aktiv"], x["name"].lower())
    )
    return {
        "ab": ab_,
        "jetzt": jetzt,
        "online": stand.online,
        "bekannt": len(stand.geraete),
        "box_erreichbar": stand.box_erreichbar,
        "geraete": liste,
        "gruppen": gr.gruppen([(x["verbindung"], x["aktiv"]) for x in liste], sprache_),
        "gruppen_art": ar.gruppen(((x["kat"], x["aktiv"]) for x in liste), sprache_),
    }


async def geraete(hass: HomeAssistant, lz: Laufzeit) -> dict[str, Any]:
    return await hass.async_add_executor_job(
        _geraete_daten, lz, _jetzt(), _ha_geraete(hass), sprache(hass)
    )


ADRESSQUELLE = {"Static": merke("fest im Gerät eingestellt"), "DHCP": "FRITZ!Box (DHCP)"}


def _geraet_daten(
    lz: Laufzeit,
    g: gr.Geraet,
    kennung: str,
    grenzen: list[tuple[float, float]],
    jetzt: float,
    sprache_: str,
) -> dict[str, Any]:
    """Blockierend: nur das Fenster aus der Datenbank und der Zustand davor – nicht der ganze Verlauf."""
    von = grenzen[0][0]
    ereignisse = lz.datenbank.geraet_lesen(g.mac, von)
    arten = [(z.t, z.ereignis.art) for z in ereignisse]
    start = vl.vorher(
        lz.datenbank.letzter_zustand(g.mac, von),
        next((a for _, a in arten if a in vl.WECHSEL), None),
        g.aktiv,
    )
    tage = vl.tage(start, arten, grenzen, jetzt)
    return {
        "id": kennung,
        "name": ohne_mac(gr.anzeigename(g.name, sprache_)),
        "ip": g.ip,
        "art": g.art,
        "aktiv": g.aktiv,
        "quelle": t(ADRESSQUELLE.get(g.quelle, merke("unbekannt")), sprache_),
        "zufallsadresse": gr.zufallsadresse(g.mac),
        "zuerst": lz.datenbank.erstes(g.mac),
        "tage": [
            {"tag": t.von, "streifen": list(t.streifen), "online_s": t.online_s}
            for t in reversed(tage)
        ],
        "abbrueche": sum(1 for _, a in arten if a == "offline"),
        "online_anteil": vl.online_anteil(tage),
        "ereignisse": [
            {
                "t": z.t,
                "art": z.ereignis.art,
                "stufe": z.ereignis.stufe,
                "text": ohne_mac(z.ereignis.text),
            }
            for z in reversed(ereignisse)
        ][:100],
    }


def geraet_bekannt(lz: Laufzeit, kennung: str) -> bool:
    return any(vl.geraete_id(x.mac, lz.salz) == kennung for x in lz.abruf.data.geraete.values())


async def geraet(
    hass: HomeAssistant, lz: Laufzeit, kennung: str, tage: int
) -> dict[str, Any] | None:
    g = next(
        (x for x in lz.abruf.data.geraete.values() if vl.geraete_id(x.mac, lz.salz) == kennung),
        None,
    )
    if g is None:
        return None
    grenzen = [(_mitternacht(i), _mitternacht(i - 1)) for i in range(tage - 1, -1, -1)]
    ha, s = _ha_geraete(hass), sprache(hass)

    def blockierend() -> tuple[dict[str, Any], ar.Art]:
        return _geraet_daten(lz, g, kennung, grenzen, _jetzt(), s), _art(lz, g, kennung, ha, s)

    daten, art = await hass.async_add_executor_job(blockierend)
    return {
        **daten,
        "kat": art.kat,
        "art_quelle": art.quelle,
        "art_selbst": kennung in lz.einstellungen.arten,
        "kategorien": ar.kategorien(s),
    }


# ── Mobilfunk ──
async def mobilfunk(hass: HomeAssistant, lz: Laufzeit, tage: int) -> dict[str, Any]:
    jetzt, s = _jetzt(), sprache(hass)
    m = lz.abruf.data.mobil
    tarif_down = lz.einstellungen.wert.tarif_down
    typisch = aw.auswerten(
        await _punkte(hass, lz, jetzt, 7),
        jetzt,
        _ab_datum(lz),
        7,
        "down",
        "aus",
        None,
        None,
        tarif_down,
        dt_util.get_default_time_zone(),
    ).median
    eintrag = lz.abruf.config_entry.entry_id
    ids = {
        "anker": ab.eigene(hass, eintrag, "rsrp_anker"),
        "nr": ab.eigene(hass, eintrag, "rsrp_5g"),
    }
    stat = await ab.statistik(
        hass,
        ids.values(),
        _dt(jetzt - tage * TAG_S),
        _dt(jetzt),
        "5minute" if tage <= 1 else "hour",
        "mean",
    )
    verlauf = {
        k: [[t, v] for t, v in stat.get(sid or "", []) if v is not None] for k, sid in ids.items()
    }

    anker = m.haupt.rsrp if m and m.haupt else None
    nr = m.nr.rsrp if m and m.nr else None
    neu = await hass.async_add_executor_job(_journal_art, lz, "mobil_neu", jetzt - 7 * TAG_S)
    funde = await _funde(lz, m)
    wohnung = _wohnung(hass)
    osm = (
        lo.in_der_naehe(wohnung, await lz.osm.masten(wohnung)) if wohnung and m and m.haupt else []
    )
    # Anbieter und Technik je Mast aus dem OpenCellID-Abzug (nur mit Schlüssel; gemerkt, bis sich etwas ändert)
    infos = await lz.ocid.infos(wohnung, [o.ort for o in osm]) if osm and wohnung else []
    gemerkt = await lz.mastsuche.gemerkte_anlagen()
    vom_modem = lz.abruf.data.mobil_quelle == "modem"
    return {
        "verfuegbar": m is not None,
        # WU-0009 Stufe 2: Herkunft der Werte – die Box selbst oder das vorgeschaltete Modem
        "herkunft": "modem" if vom_modem else "box",
        "herkunft_text": t("vom vorgeschalteten Modem" if vom_modem else "laut FRITZ!Box", s),
        "technik": m.technik if m else None,
        "befund": asdict(mb.befund(m.technik if m else "", anker, nr, typisch, tarif_down, s)),
        "verlauf": verlauf,
        "schwach_unter": -105,
        "laufzeit_s": m.laufzeit_s if m else None,
        "laufzeit": mb.dauer(m.laufzeit_s, s) if m and m.laufzeit_s is not None else None,
        "abbrueche_7": len(neu),
        "letzter_abbruch": neu[0]["t"] if neu else None,
        "baender": _baender(m) if vom_modem else lz.abruf.data.mobil_baender or None,
        "baender_unter": t(
            "genutzt (laut Modem)" if vom_modem else "eingeschaltet (in der Box)", s
        ),
        "strecke": _strecke(m, s, t("Modem", s) if vom_modem else "FRITZ!Box"),
        "zellen": [_zelle(z, m, funde.get(z), s) for z in mb.zellen_sortiert(m)] if m else [],
        "karte": _karte(wohnung, m, funde, osm, infos, gemerkt, s),
    }


async def _funde(lz: Laufzeit, m: mb.Mobilfunk | None) -> dict[mb.Zelle, ka.Fund | None]:
    """Je Zelle der Fund bei OpenCellID/BeaconDB; None = keine vollständige Kennung (nur PCI, 5G) – nicht gefragt."""
    if m is None:
        return {}
    kennungen = {z: ka.kennung(z, m.haupt) for z in m.zellen}
    gesucht = await lz.mastsuche.suchen([k for k in kennungen.values() if k])
    return {z: gesucht[k.schluessel] if k else None for z, k in kennungen.items()}


async def mast_zur_ankerzelle(hass: HomeAssistant, lz: Laufzeit) -> tuple[int, str] | None:
    """WU-0005: Entfernung (m) und Richtung zum geschätzten Mast der Sendeanlage der Ankerzelle – wie die Karte. Ist
    eine Zelle noch nicht (oder nicht mehr frisch) gemerkt, fragt die Mastsuche wie bei der Karte nach (nur die
    Zellkennung, einmal im Monat je Zelle)."""
    m, wohnung = lz.abruf.data.mobil if lz.abruf.data else None, _wohnung(hass)
    if m is None or m.haupt is None or wohnung is None:
        return None
    funde = await _funde(lz, m)
    zellen = [(z, f.mast) for z in mb.zellen_sortiert(m) if (f := funde.get(z)) and f.mast]
    masten = ka.masten_je_anlage(zellen, await lz.mastsuche.gemerkte_anlagen(), m.haupt, m.zellen)
    mast = next((mast for enb, mast in masten if enb == ka.sendeanlage(m.haupt)), None)
    if mast is None:
        return None
    return round(ka.entfernung_m(wohnung, mast.ort)), ka.richtung(wohnung, mast.ort, sprache(hass))


def _wohnung(hass: HomeAssistant) -> ka.Ort | None:
    """Standort aus Home Assistant; None, wenn keiner eingetragen ist."""
    if not (hass.config.latitude or hass.config.longitude):
        return None
    return ka.Ort(hass.config.latitude, hass.config.longitude)


def _karte(
    wohnung: ka.Ort | None,
    m: mb.Mobilfunk | None,
    funde: dict[mb.Zelle, ka.Fund | None],
    osm: list[lo.OsmMast],
    infos: list[lc.MastInfo | None],
    gemerkt: dict[tuple[int, str], list[ka.Mast]] | None,
    sprache_: str,
) -> dict[str, Any] | None:
    """Karte (Leaflet auf der Seite): Wohnung (Standort aus Home Assistant), Ring laut Box, jede gefundene Zelle mit
    Genauigkeit, je Sendeanlage der geschätzte Mast und der Rahmen, den die Karte beim Öffnen zeigt."""
    if m is None or m.haupt is None or wohnung is None:
        return None
    zellen = [(z, f.mast) for z in mb.zellen_sortiert(m) if (f := funde.get(z)) and f.mast]
    masten = ka.masten_je_anlage(zellen, gemerkt, m.haupt, m.zellen)
    ziel = next((mast.ort for enb, mast in masten if enb == ka.sendeanlage(m.haupt)), None)
    treffer = lo.passend(wohnung, osm, m.haupt.entfernung_m, ziel)
    passt, warum = treffer if treffer else (None, None)
    r = ka.rahmen(
        wohnung, m.haupt.entfernung_m, [mast.ort for _, mast in masten], [ort for _, ort in zellen]
    )
    return {
        "stand": ka.gesamtstand([f for f in funde.values() if f]),
        "gefunden": len(zellen),
        "zellen": len(m.zellen),
        "rahmen": list(r) if r else None,
        "wohnung": [wohnung.lat, wohnung.lon],
        "ring_m": m.haupt.entfernung_m or None,
        "ring": mb.entfernung(m.haupt.entfernung_m, sprache_),
        "masten": [
            {
                "name": enb,
                "ort": [mast.ort.lat, mast.ort.lon],
                "entfernung": ka.strecke(ka.entfernung_m(wohnung, mast.ort), sprache_),
                "richtung": ka.richtung(wohnung, mast.ort, sprache_),
                "genau": ka.strecke(mast.genau_m, sprache_) if mast.genau_m else None,
                # nur an der Sendeanlage der Ankerzelle: dort hängt 5G bei NSA meist mit dran
                "fuenf_g": enb == ka.sendeanlage(m.haupt) and ka.fuenf_g_dabei(m.zellen),
            }
            for enb, mast in masten
        ],
        "punkte": [
            {
                "ort": [ort.ort.lat, ort.ort.lon],
                "genau_m": ort.genau_m,
                "anker": z.rolle == "primary",
                "name": z.zelle.partition("-")[2],
            }
            for z, ort in zellen
        ],
        "osm": [
            {
                "ort": [o.ort.lat, o.ort.lon],
                "betreiber": o.betreiber,
                "passt": i == passt,
                "warum": warum
                if i == passt
                else None,  # lage: nahe am geschätzten Mast; entfernung: laut Box
                "entfernung": ka.strecke(ka.entfernung_m(wohnung, o.ort), sprache_),
                "richtung": ka.richtung(wohnung, o.ort, sprache_),
                # laut OpenCellID-Abzug: Zellen in höchstens 500 m (None = dort keine bekannt)
                "anbieter": list(info.anbieter) if info else None,
                "technik": list(info.technik) if info else None,
                "zellen": info.zellen if info else 0,
            }
            for i, (o, info) in enumerate(zip(osm, infos, strict=True))
        ],
    }


def _baender(m: mb.Mobilfunk | None) -> str | None:
    """Genutzte Bänder laut vorgeschaltetem Modem („B3 · n78“) – die Box nennt stattdessen die eingeschalteten."""
    if m is None:
        return None
    return " · ".join(dict.fromkeys(z.band for z in m.zellen if z.band)) or None


def _strecke(
    m: mb.Mobilfunk | None, sprache_: str, geraet: str = "FRITZ!Box"
) -> dict[str, Any] | None:
    """Grafik Gerät → Basisstation: Empfang der Ankerzelle, Entfernung, Anbieter, welche Masten (5G/4G)."""
    if m is None or m.haupt is None:
        return None
    z = m.haupt
    return {
        "geraet": geraet,
        "rsrp": z.rsrp,
        "lage": mb.lage_rsrp(z.rsrp),
        "wort": mb.wort_rsrp(z.rsrp, sprache_) if z.rsrp is not None else None,
        "entfernung": mb.entfernung(z.entfernung_m, sprache_),
        "anbieter": z.anbieter or None,
        "masten": [
            t for art, t in (("5G", "5G"), ("LTE", "4G")) if any(c.art == art for c in m.zellen)
        ],
    }


def _zelle(z: mb.Zelle, m: mb.Mobilfunk, fund: ka.Fund | None, sprache_: str) -> dict[str, Any]:
    plmn, tac = ka.kennteile(z, m.haupt)  # so, wie nachgeschlagen wird
    return {
        "art": z.art,
        "rolle": mb.rolle(z, m.technik, sprache_),
        "rolle_art": mb.rolle_art(z, m.technik),  # anker, verbunden, dazu, reichweite
        "anker": z.rolle == "primary",
        "kennung": z.zelle or (f"PCI {z.pci}" if z.pci is not None else None),
        "rsrp": z.rsrp,
        "rsrq": z.rsrq,
        "sinr": z.sinr,  # nur vom vorgeschalteten Modem
        "band": z.band or None,
        "stufen": mb.stufen(z.rsrp),
        "lage": mb.lage_rsrp(z.rsrp),
        "tac": tac.lower() if z.art == "LTE" and tac else None,
        "plmn": ka.plmn_text(plmn) if z.art == "LTE" else None,
        "fund": {
            "quelle": fund.quelle,
            "genau": ka.strecke(fund.mast.genau_m, sprache_) if fund.mast.genau_m else None,
        }
        if fund and fund.mast
        else None,
        "such": ka.such_text(z, fund, sprache_),
    }


def _journal_art(lz: Laufzeit, art: str, ab_: float) -> list[dict[str, Any]]:
    """Blockierend: Journalzeilen einer Art seit `ab_`, neueste zuerst."""
    return [
        {"t": z.t, "text": ohne_mac(z.ereignis.text)}
        for z in lz.datenbank.journal_lesen(ab_, grenze=500, art=art)
    ]


# ── Internet: Zugang und Werte je Zugangsart (WU-0009) ──
FEHLT = merke("liefert die Schnittstelle der Box nicht")


def zugang_jetzt(lz: Laufzeit, s: str) -> zg.Internetzugang:
    """Zugang aus dem zuletzt Gelesenen und der Wahl des Admins (⚙ › Zugang)."""
    st, w = lz.abruf.data, lz.einstellungen.wert
    info = lz.abruf.box_info
    dienst = lz.abruf.modem
    erkannt = dienst.gemerkt if lz.abruf.modem_aktiv(st.zugang) else None
    return zg.beschreiben(
        st.zugang or zg.Meldung(),
        st.zugang_art,
        st.ersatz_aktiv,
        w.zugang_wahl,
        w.zugang_adresse,
        w.zugang_ersatz,
        info.modell if info else "",
        st.mobil.technik if st.mobil else "",
        s,
        erkannt=erkannt.name if erkannt else "",
        erkannt_art=erkannt.b.art if erkannt else "",
        such_belege=tuple(ve.beleg(x, s) for x in dienst.treffer),
        erkannt_adresse=dienst.adresse if erkannt else "",
    )


def _zugang_kurz(z: zg.Internetzugang) -> dict[str, Any]:
    return {
        "art": z.art,
        "quelle": z.quelle,
        "weg": z.weg,
        "titel": z.titel,
        "geraet": z.geraet,
        "weg_text": z.weg_text,
        "ersatz": z.ersatz or None,
        "ersatz_aktiv": z.ersatz_aktiv,
        "ersatz_text": z.ersatz_text or None,
        "abweichung": z.vorschlag if z.abweichung else None,
        "adresse": z.adresse or None,  # nur bei vorgeschaltetem Gerät, nur privat (für 🔬 Diagnose)
        "kopf": z.kopf,
    }


async def _verlauf(
    hass: HomeAssistant, lz: Laufzeit, schluessel: dict[str, str], tage: int
) -> dict[str, list[list[float]]]:
    """Verlauf eigener Sensoren aus der Aufzeichnung (Mittel je Stunde) – wie beim Mobilfunk."""
    jetzt = _jetzt()
    eintrag = lz.abruf.config_entry.entry_id
    ids = {k: ab.eigene(hass, eintrag, v) for k, v in schluessel.items()}
    stat = await ab.statistik(
        hass, ids.values(), _dt(jetzt - tage * TAG_S), _dt(jetzt), "hour", "mean"
    )
    return {
        k: [[t_, v] for t_, v in stat.get(sid or "", []) if v is not None] for k, sid in ids.items()
    }


async def _dsl_daten(hass: HomeAssistant, lz: Laufzeit, s: str) -> dict[str, Any] | None:
    st = lz.abruf.data
    d = st.dsl
    if d is None:
        return None
    b = ln.dsl_bewerten(d, st.dsl_crc_h, st.dsl_neusync, s)
    neusync = await hass.async_add_executor_job(_journal_art, lz, "dsl_sync", _jetzt() - 7 * TAG_S)
    w = lz.einstellungen.wert
    verfahren = " · ".join(
        x for x in (d.modulation, t("Profil {p}", s, p=d.profil) if d.profil else "") if x
    )
    return {
        "bewertung": asdict(b),
        "status": t(zg.DSL_STATUS.get(d.status, d.status or "–"), s),
        "sync_down": ln.mbit(d.sync_down),
        "sync_up": ln.mbit(d.sync_up),
        "max_down": ln.mbit(d.max_down),
        "max_up": ln.mbit(d.max_up),
        "tarif_down": w.tarif_down,
        "tarif_up": w.tarif_up,
        "anteil_down": ln.anteil(d.sync_down, d.max_down),
        "marge_down": ln.db(d.marge_down),
        "marge_up": ln.db(d.marge_up),
        "marge_gut": ln.MARGE_GUT_DB,
        "marge_stufe": ln.marge_stufe(d) or None,
        "daempfung_down": ln.db(d.daempfung_down),
        "daempfung_up": ln.db(d.daempfung_up),
        "verfahren": verfahren or None,
        "seit": st.dsl_seit,
        "seit_text": ln.dauer(_jetzt() - st.dsl_seit, s) if st.dsl_seit else None,
        "crc_h": st.dsl_crc_h,
        "fec_h": st.dsl_fec_h,
        "neusync_7": st.dsl_neusync,
        "neusync": neusync,
        "gegenstelle": None,
        "fehlt": t(FEHLT, s),
        "verlauf": await _verlauf(hass, lz, {"sync": "dsl_sync_down", "marge": "dsl_snr_down"}, 7),
    }


async def _faser_daten(hass: HomeAssistant, lz: Laufzeit, s: str) -> dict[str, Any] | None:
    st = lz.abruf.data
    f = st.faser
    if f is None:
        return None
    rx_b, tx_b = ln.licht_bereich(f), ln.sende_bereich(f)
    z = st.zugang
    return {
        "bewertung": asdict(ln.faser_bewerten(f, s)),
        "rx": ln.dbm(f.rx),
        "tx": ln.dbm(f.tx),
        "rx_bereich": list(rx_b) if rx_b else None,
        "tx_bereich": list(tx_b) if tx_b else None,
        "modus": f.modus or None,
        "down_mbit": round(z.down_bit / 1e6) if z and z.down_bit else None,
        "up_mbit": round(z.up_bit / 1e6) if z and z.up_bit else None,
        "seit_text": ln.dauer(f.minuten * 60, s) if f.minuten else None,
        "fehler_h": st.faser_fehler_h,
        "resyncs": f.resyncs,
        "fehlt": t(FEHLT, s),
        "verlauf": await _verlauf(hass, lz, {"rx": "glasfaser_rx"}, 7),
    }


def _kabel_daten(lz: Laufzeit, s: str) -> dict[str, Any]:
    z = lz.abruf.data.zugang
    return {
        "down_mbit": round(z.down_bit / 1e6) if z and z.down_bit else None,
        "up_mbit": round(z.up_bit / 1e6) if z and z.up_bit else None,
        "verbunden": z.link == "Up" if z and z.link else None,
        "fehlt": t(FEHLT, s),
    }


async def _ersatz_daten(
    hass: HomeAssistant, lz: Laufzeit, z: zg.Internetzugang, s: str
) -> dict[str, Any] | None:
    if not z.ersatz:
        return None
    jetzt = _jetzt()
    ab_ = jetzt - 30 * TAG_S
    an = await hass.async_add_executor_job(_journal_art, lz, "ersatz_an", ab_ - 30 * TAG_S)
    aus = await hass.async_add_executor_job(_journal_art, lz, "ersatz_aus", ab_ - 30 * TAG_S)
    n, sek, letzte = zg.ersatz_zeiten(
        [x["t"] for x in an], [x["t"] for x in aus], ab_, jetzt, z.ersatz_aktiv
    )
    m = lz.abruf.data.mobil
    return {
        "aktiv": z.ersatz_aktiv,
        "text": z.ersatz_text,
        "umschaltungen_30": n,
        "dauer_30": ln.dauer(sek, s) if sek else None,
        "letzte": letzte,
        "rsrp": m.haupt.rsrp if m and m.haupt else None,
        "technik": m.technik if m else None,
    }


def _vorgeschaltet(lz: Laufzeit, s: str) -> dict[str, Any]:
    """WU-0009 Stufe 2: was Heimnetz vom vorgeschalteten Gerät weiß – erkannt, Herkunft der Werte, Befund."""
    dienst = lz.abruf.modem
    stand, e = dienst.stand, dienst.gemerkt
    befund = stand.befund if stand else ("nicht_gesucht" if e is None else None)
    if stand is not None and stand.mobil is None and befund is None:
        befund = "keine_werte"
    return {
        "geraet": e.name if e else None,
        "hersteller": e.b.hersteller if e else None,
        "adresse": dienst.adresse or None,
        "art": e.b.art if e else None,  # mobilfunk, glasfaser, router
        "quelle": stand.quelle if stand else None,  # geraet / integration
        "integration": e.b.integration or None if e else None,
        "gelesen": stand.zeit if stand else None,
        "werte": lz.abruf.data.mobil_quelle == "modem",
        "befund": ve.befund_daten(befund, s),
    }


async def internet(hass: HomeAssistant, lz: Laufzeit, tage: int) -> dict[str, Any]:
    """Reiter „Internet“: Herkunft des Zugangs und die Werte der gewählten Zugangsart."""
    s = sprache(hass)
    z = zugang_jetzt(lz, s)
    vom_modem = z.art == "extern" and lz.abruf.data.mobil_quelle == "modem"
    return {
        "zugang": _zugang_kurz(z),
        # die Ansicht Ersatz braucht nur Signal und Technik (in „ersatz“) – nicht die ganze Mobilfunk-Ansicht
        "mobilfunk": await mobilfunk(hass, lz, tage) if z.art == "mobilfunk" or vom_modem else None,
        "vorgeschaltet": _vorgeschaltet(lz, s) if z.art == "extern" else None,
        "dsl": await _dsl_daten(hass, lz, s) if z.art == "dsl" else None,
        "glasfaser": await _faser_daten(hass, lz, s) if z.art == "glasfaser" else None,
        "kabel": _kabel_daten(lz, s) if z.art == "kabel" else None,
        "ersatz": await _ersatz_daten(hass, lz, z, s),
    }


def zugang(hass: HomeAssistant, lz: Laufzeit) -> dict[str, Any]:
    """⚙ › Zugang: Vorschlag mit Belegen, Wahl, Adresse; vom Kennwort nur, ob eines hinterlegt ist."""
    s = sprache(hass)
    z = zugang_jetzt(lz, s)
    w = lz.einstellungen.wert
    return {
        **_zugang_kurz(z),
        "vorschlag": z.vorschlag,
        "vorschlag_art": z.vorschlag_art or None,
        "belege": list(z.belege),
        "wahl": w.zugang_wahl,
        "wahlen": list(zg.WAHLEN),
        "ersatz_wahl": w.zugang_ersatz,
        "adresse": w.zugang_adresse,
        "adresse_jetzt": z.adresse or None,
        "adressen": list(z.adressen),
        "kennwort": bool(lz.abruf.config_entry.options.get(CONF_MODEM_KENNWORT)),
        "gelesen": lz.abruf.data.zugang is not None,
        # WU-0009 Stufe 2: gefundenes Gerät (✓ … antwortet: …) und wann zuletzt gesucht
        "vorgeschaltet": _vorgeschaltet(lz, s) if z.art == "extern" else None,
        "gesucht_zeit": lz.abruf.modem.gesucht,
    }


# ── WLAN ──
async def wlan(hass: HomeAssistant, lz: Laufzeit) -> dict[str, Any]:
    """Bänder, Geräte im WLAN (schwächstes zuerst), Befunde und Kanalwechsel der letzten 7 Tage."""
    stand = lz.abruf.data
    w = stand.wlan
    jetzt, s = _jetzt(), sprache(hass)
    wechsel = await hass.async_add_executor_job(_journal_art, lz, "wlan_kanal", jetzt - 7 * TAG_S)
    grenze = lz.einstellungen.wert.wlan_schwach
    if w is None:
        return {"verfuegbar": False, "kanalwechsel": wechsel, "schwach_unter": grenze}

    def name(mac: str) -> str:
        g = stand.geraete.get(mac)
        return ohne_mac(gr.anzeigename(g.name, s)) if g else gr.anzeigename(gr.OHNE_NAMEN, s)

    b = wl.befunde(w, lz.abruf.gedaechtnis.wlan_schnell, grenze)
    befunde = []
    if b.schwach:
        befunde.append(
            {
                "stufe": "warnung",
                "titel": t(
                    "{n} Gerät mit schwachem Empfang"
                    if len(b.schwach) == 1
                    else "{n} Geräte mit schwachem Empfang",
                    s,
                    n=len(b.schwach),
                ),
                "text": t(
                    "{namen} – unter {grenze} %. Näher an die Box oder einen Repeater stellen; bei schwachem "
                    "Empfang bricht die Verbindung leichter ab.",
                    s,
                    namen=", ".join(name(m) for m in b.schwach),
                    grenze=grenze,
                ),
            }
        )
    if b.auf_24:
        namen = ", ".join(name(m) for m in b.auf_24)
        befunde.append(
            {
                "stufe": "info",
                "titel": t(
                    "{namen} hängt auf 2,4 GHz"
                    if len(b.auf_24) == 1
                    else "{namen} hängen auf 2,4 GHz",
                    s,
                    namen=namen,
                ),
                "text": t(
                    "War schon auf 5 GHz verbunden – dort wäre es schneller. Meist wechselt das Gerät von "
                    "selbst, wenn es näher an der Box ist.",
                    s,
                ),
            }
        )
    geraete = []
    for g in w.geraete:
        band = wl.band_von(g, w.baender)
        geraete.append(
            {
                "id": vl.geraete_id(g.mac, lz.salz),
                "name": name(g.mac),
                "band": wl.band_text(band, s) if band else band,
                "signal": g.signal,
                "lage": wl.lage_signal(g.signal),
                "mbit": g.mbit,
                "gast": g.gast,
                "schwach": g.mac in b.schwach,
            }
        )
    geraete.sort(key=lambda x: (x["signal"] is None, x["signal"] or 0))
    return {
        "verfuegbar": True,
        "befunde": befunde,
        "baender": [
            {
                **asdict(x),
                "band": wl.band_text(x.band, s) if x.band else x.band,
                "geraete": sum(1 for g in w.geraete if g.kanal == x.kanal),
            }
            for x in w.baender
        ],
        "gast_an": w.gast_an,
        "geraete": geraete,
        "kanalwechsel": wechsel,
        "schwach_unter": grenze,
    }


# ── Verbrauch ──
async def verbrauch(
    hass: HomeAssistant, lz: Laufzeit, tage: int, ganzer_monat: bool = True
) -> dict[str, Any]:
    """`ganzer_monat`: so weit zurück lesen, dass Woche und Monat stimmen (die Übersicht braucht nur heute)."""
    jetzt = _jetzt()
    anzahl = max(tage, dt_util.now().day) if ganzer_monat else tage
    ids = ab.fritz_zaehler(hass, lz.abruf.fritz_eintrag)
    start = dt_util.start_of_local_day() - timedelta(days=anzahl - 1)
    stat = await ab.statistik(hass, ids.values(), start, dt_util.utcnow(), "day", "change")
    messungen = await hass.async_add_executor_job(lz.datenbank.messungen_lesen, start.timestamp())
    alle = vb.tage(
        stat.get(ids.get("down", ""), []),
        stat.get(ids.get("up", ""), []),
        aw.aus_messungen(messungen),
        jetzt,
        anzahl,
        dt_util.get_default_time_zone(),
    )
    k = vb.kacheln(alle, tage)
    return {
        "verfuegbar": bool(ids),
        "tage": [
            {"tag": t.tag.isoformat(), "down": t.down, "up": t.up, "speedtest": t.speedtest}
            for t in alle[-tage:]
        ],
        "kacheln": None
        if k is None
        else {
            "heute": {"down": k.heute.down, "up": k.heute.up, "speedtest": k.heute.speedtest},
            "woche": k.woche if ganzer_monat else None,
            "monat": k.monat if ganzer_monat else None,
            "schnitt": k.schnitt,
            "speedtest": k.speedtest,
        },
    }


# ── Protokoll ──
def _protokoll_daten(
    lz: Laufzeit, art: str, nur_warnungen: bool, suche: str, grenze: int
) -> dict[str, Any]:
    suche = suche.strip()
    if art == "journal":
        zeilen = [
            {
                "t": z.t,
                "stufe": z.ereignis.stufe,
                "art": z.ereignis.art,
                "text": ohne_mac(z.ereignis.text),
            }
            for z in lz.datenbank.journal_lesen(
                0, nur_wichtig=nur_warnungen, grenze=grenze, suche=suche
            )
        ]
    else:
        zeilen = [
            {
                "t": e.zeitpunkt.timestamp() if e.zeitpunkt else None,
                "roh_zeit": e.roh_zeit,
                "stufe": "",
                "text": ohne_mac(e.text),
            }
            for e in lz.datenbank.protokoll_lesen(PROTOKOLL_ARTEN[art], grenze=grenze, suche=suche)
        ]
    return {"art": art, "eintraege": zeilen}


async def protokoll(
    hass: HomeAssistant, lz: Laufzeit, art: str, nur_warnungen: bool, suche: str, grenze: int
) -> dict[str, Any]:
    return await hass.async_add_executor_job(
        _protokoll_daten, lz, art, nur_warnungen, suche, grenze
    )


# ── Übersicht ──
def _uebersicht_db(
    lz: Laufzeit, jetzt: float
) -> tuple[list[Any], dict[str, tuple[int, bool]], list[Any]]:
    db = lz.datenbank
    return (
        db.journal_lesen(0, nur_wichtig=True, grenze=10),
        db.geraete_zaehlen(jetzt - TAG_S),
        db.messungen_lesen(jetzt - 30 * TAG_S),
    )


async def uebersicht(hass: HomeAssistant, lz: Laufzeit) -> dict[str, Any]:
    s, sp_ = lz.abruf.data, sprache(hass)
    jetzt = _jetzt()
    wichtig, zaehlung, messungen = await hass.async_add_executor_job(_uebersicht_db, lz, jetzt)
    heute = (await verbrauch(hass, lz, 1, ganzer_monat=False))["kacheln"]
    stufen = [
        vl.einstufung(g.aktiv, *zaehlung.get(mac, (0, False))) for mac, g in s.geraete.items()
    ]
    m = s.mobil
    dhcp_ok, dhcp_text = bf.dhcp_pruefung(s.dhcp, s.lan.router, sp_)
    schwaechster = mb.schwaechster(m)
    pruefungen = [
        {"name": "Pi → FRITZ!Box", "ok": s.pi.box, "wert": ""},
        {"name": "Pi → Internet", "ok": s.pi.internet, "wert": ""},
        {"name": t("Namensauflösung (DNS)", sp_), "ok": s.pi.dns, "wert": ""},
        {
            "name": t("Heimnetz", sp_),
            "ok": True if s.lan.router else None,
            "wert": f"Box {s.lan.router} · {s.lan.maske}" if s.lan.router else "",
        },
        {
            "name": t("DHCP verteilt", sp_),
            "ok": s.lan.dhcp_an,
            "wert": f"{s.lan.dhcp_von} – {s.lan.dhcp_bis}"
            if s.lan.dhcp_an
            else (t("ausgeschaltet", sp_) if s.lan.dhcp_an is False else ""),
        },
        {"name": t("DHCP-Test", sp_), "ok": dhcp_ok, "wert": dhcp_text},
    ]
    return {
        "stand": s.zeit,
        "gesamt": s.gesamt,
        "box_erreichbar": s.box_erreichbar,
        "fehler": [ohne_mac(f) for f in s.fehler],
        "befunde": [
            {
                "key": b.key.split(":")[0],
                "stufe": b.stufe,
                "titel": ohne_mac(b.titel),
                "text": ohne_mac(b.text),
            }
            for b in s.befunde
        ],
        "pruefungen": pruefungen,
        "internet": {"ok": s.pi.internet, "technik": m.technik if m else None},
        "zugang": _zugang_kurz(zugang_jetzt(lz, sp_)),
        "geraete": {
            "online": s.online,
            "bekannt": len(s.geraete),
            "neu": stufen.count("neu"),
            "wackelt": stufen.count("wackelt"),
        },
        "empfang": None
        if schwaechster is None or m is None or m.haupt is None
        else {
            "rsrp_anker": m.haupt.rsrp,
            "rsrp_5g": m.nr.rsrp if m.nr else None,
            "lage": mb.lage_rsrp(schwaechster),
            "wort": mb.wort_rsrp(schwaechster, sp_),
        },
        "speedtest": asdict(aw.aus_messungen(messungen[-1:])[0]) if messungen else None,
        "verbrauch_heute": None if heute is None else heute["heute"],
        "wichtig": [
            {"t": z.t, "stufe": z.ereignis.stufe, "text": ohne_mac(z.ereignis.text)}
            for z in wichtig
        ],
    }


def einstellungen(hass: HomeAssistant, lz: Laufzeit) -> dict[str, Any]:
    """Tarif, Auswerten ab und Messplan samt Zustand (nächste Messung, Verkehr, Ookla)."""
    abruf = lz.abruf
    plan = lz.einstellungen.plan
    stand = abruf.data
    jetzt = _jetzt()
    status = abruf.plan_status
    letzte = abruf.letzte_ausloesung
    sensoren = abruf.speedtest.sensoren
    ookla = ookla_einstellung(hass, sensoren.eintrag if sensoren else None)
    server = _wert(hass.states.get(sensoren.server)) if sensoren and sensoren.server else None
    # WU-0006: Datenvolumen je Messung – aus den letzten Werten von Ookla, sonst aus dem Tarif
    get = hass.states.get
    down = _mbit(get(sensoren.download)) if sensoren and sensoren.download else None
    up = _mbit(get(sensoren.upload)) if sensoren and sensoren.upload else None
    if down is None and up is None:
        down, up = lz.einstellungen.wert.tarif_down, lz.einstellungen.wert.tarif_up
    return {
        **lz.einstellungen.wert.als_dict(),
        "messplan": plan.als_dict(),
        "plan": {
            "naechste": mp.naechste(plan, letzte, jetzt, dt_util.get_default_time_zone()),
            "wartet": bool(status and status.aktion == mp.WARTEN),
            "grund": t(status.grund, sprache(hass)) if status else None,
            "neuer_versuch": status.neuer_versuch if status else None,
            "ausgeloest": abruf.ausgeloest or None,
            "misst": bool(
                abruf.ausgeloest
                and abruf.ausgeloest > abruf.letzte_messung
                and jetzt - abruf.ausgeloest < 300
            ),
        },
        "serie": abruf.serie_status,
        "letzte_serie": lz.einstellungen.letzte_serie,
        "verkehr_mbit": stand.rate.down if stand.rate else None,
        "schwelle": aw.schwelle(lz.einstellungen.wert.tarif_down),
        "volumen": mp.volumen(plan, down, up),
        "ookla": {
            "vorhanden": ookla is not None,
            "sensoren": abruf.speedtest.sensoren is not None,
            "misst_selbst": bool(ookla and ookla.misst_selbst),
            "startzeit": ookla.startzeit if ookla else None,
            "takt_min": ookla.takt_min if ookla else None,
            "server": server,
            "eintrag": ookla.eintrag if ookla else None,
            "tests": len(alle_finden(hass)),
        },
    }
