"""Karte zum Mast: Kennungen der Zellen für OpenCellID und BeaconDB, Antworten lesen, Mast schätzen, Kartenrahmen.

Die Box nennt je Zelle PLMN (MCC+MNC), TAC (hexadezimal) und die Zellkennung als „eNodeB-Sektor“ (beides
hexadezimal, z. B. „03584-03“; AVM „TR-064 WAN Mobile Connection“ V7, CellList). OpenCellID erwartet für LTE die
Kennung der Zelle (ECI = eNodeB · 256 + Sektor) und den TAC als Zahl, BeaconDB dieselben Teile. Beide liefern nicht
den Mast selbst, sondern einen geschätzten Ort der Zelle mit Genauigkeit; eine Senderichtung kennen sie nicht. Zellen
derselben Sendeanlage (eNodeB) hängen am selben Mast: Sein Ort ist das Mittel ihrer Orte, genauere zählen mehr.
Gezeichnet wird mit Leaflet auf der Seite; hier entsteht nur der Rahmen, den die Karte beim Öffnen zeigt.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .mobil import Zelle, entfernung
from .sprache import DE, merke, t

ERDE_M = 6_371_000.0
GUELTIG_S = 30 * 86_400  # gefundener Mast: einen Monat merken
NOCHMAL_S = 86_400  # nicht gefunden oder Schlüssel abgelehnt: frühestens morgen wieder fragen
FEHLER_S = 3600  # nicht erreichbar: in einer Stunde noch einmal
FERN_M = 5000  # Zellen und Masten weiter weg (und über dem Dreifachen des Rings) vergrößern die Karte nicht

# Stand des Nachschlagens (je Zelle und für die Karte)
GEFUNDEN = "gefunden"
NICHT_GEFUNDEN = "nicht_gefunden"
FEHLER = "fehler"
UNGUELTIG = "schluessel_ungueltig"
OHNE_SCHLUESSEL = "ohne_schluessel"
OHNE_KENNUNG = "ohne_kennung"
OPENCELLID = "OpenCellID"
BEACONDB = "BeaconDB"
RICHTUNGEN = (
    merke("Nord"),
    merke("Nordost"),
    merke("Ost"),
    merke("Südost"),
    merke("Süd"),
    merke("Südwest"),
    merke("West"),
    merke("Nordwest"),
)


@dataclass(frozen=True)
class Kennung:
    mcc: int
    mnc: int
    lac: int
    cellid: int
    radio: str = "LTE"

    @property
    def schluessel(self) -> str:
        return f"{self.mcc}-{self.mnc}-{self.lac}-{self.cellid}"


def sendeanlage(z: Zelle) -> str | None:
    """eNodeB einer LTE-Zelle („aaaaa“ aus „aaaaa-64“); None, wenn die Box nur die PCI nennt."""
    enb, strich, sektor = z.zelle.partition("-")
    return enb.lower() if z.art == "LTE" and strich and enb and sektor else None


def kennteile(z: Zelle, haupt: Zelle | None = None) -> tuple[str, str]:
    """PLMN und TAC, mit denen eine Zelle nachgeschlagen wird: ihre eigenen, sonst die der Hauptzelle, wenn beide zur
    selben Sendeanlage gehören – eine Sendeanlage liegt in einem Gebiet und gehört einem Anbieter."""
    gleich = (
        haupt is not None
        and sendeanlage(haupt) is not None
        and sendeanlage(haupt) == sendeanlage(z)
    )
    return z.plmn or (haupt.plmn if gleich and haupt else ""), z.tac or (
        haupt.tac if gleich and haupt else ""
    )


def kennung(z: Zelle | None, haupt: Zelle | None = None) -> Kennung | None:
    """Kennung einer LTE-Zelle zum Nachschlagen; None, wenn die Box nicht alle Teile nennt."""
    if z is None or z.art != "LTE":
        return None
    plmn, tac = kennteile(z, haupt)
    if len(plmn) not in (5, 6) or not plmn.isdigit():
        return None
    enb, _, sektor = z.zelle.partition("-")
    try:
        lac = int(tac, 16)
        cellid = int(enb, 16) * 256 + int(sektor, 16)
    except ValueError:
        return None
    if not lac or not cellid:
        return None
    return Kennung(int(plmn[:3]), int(plmn[3:]), lac, cellid)


def plmn_text(plmn: str) -> str | None:
    """„23205“ → „232 05“ (Land und Netz getrennt, wie man sie nachschlägt)."""
    return f"{plmn[:3]} {plmn[3:]}" if len(plmn) in (5, 6) and plmn.isdigit() else None


@dataclass(frozen=True)
class Ort:
    lat: float
    lon: float


@dataclass(frozen=True)
class Mast:
    ort: Ort
    genau_m: int | None  # „range“ von OpenCellID: wie weit die Schätzung danebenliegen kann


def mast_aus(antwort: Mapping[str, Any]) -> Mast | None:
    """Antwort von OpenCellID (cell/get, format=json); Fehlerantwort oder Unsinn → None."""
    if antwort.get("error"):
        return None
    try:
        lat, lon = float(antwort["lat"]), float(antwort["lon"])
    except KeyError, TypeError, ValueError:
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
        return None
    try:
        genau = int(float(antwort.get("range") or 0)) or None
    except TypeError, ValueError, OverflowError:
        genau = None
    return Mast(Ort(lat, lon), genau)


def beacondb_aus(antwort: Mapping[str, Any]) -> Mast | None:
    """Antwort von BeaconDB (geolocate, wie die Geolocation-API von Mozilla); nicht gefunden oder Unsinn → None."""
    ort = antwort.get("location")
    if not isinstance(ort, Mapping):
        return None
    return mast_aus(
        {"lat": ort.get("lat"), "lon": ort.get("lng"), "range": antwort.get("accuracy")}
    )


def schaetzen(orte: Sequence[Mast]) -> Mast | None:
    """Mast einer Sendeanlage aus den Orten ihrer Zellen: Mittel, gewichtet mit 1/Genauigkeit² (ohne Angabe 1 km).

    Die Genauigkeit ist die der genauesten Zelle – das Mittel ist nicht genauer als der beste Einzelwert."""
    if not orte:
        return None
    gewicht = [1 / max(o.genau_m or 1000, 10) ** 2 for o in orte]
    summe = sum(gewicht)
    lat = sum(o.ort.lat * g for o, g in zip(orte, gewicht, strict=True)) / summe
    lon = sum(o.ort.lon * g for o, g in zip(orte, gewicht, strict=True)) / summe
    genau = [o.genau_m for o in orte if o.genau_m]
    return Mast(Ort(lat, lon), min(genau) if genau else None)


@dataclass(frozen=True)
class Fund:
    """Ergebnis für eine Zelle: genauester Ort aus beiden Diensten, sonst warum nicht."""

    stand: str
    mast: Mast | None = None
    quelle: str | None = None
    schluessel_ungueltig: bool = False


def _gemerkt(eintrag: Mapping[str, Any] | None) -> Mast | None:
    if not eintrag or eintrag.get("lat") is None:
        return None
    return Mast(Ort(eintrag["lat"], eintrag["lon"]), eintrag.get("genau"))


def fund(
    opencellid: Mapping[str, Any] | None, beacondb: Mapping[str, Any] | None, mit_schluessel: bool
) -> Fund:
    """Gemerkte Antworten beider Dienste zu einem Ergebnis: der genauere Ort (ohne Angabe gilt jeder andere als
    genauer); sonst „nicht erreichbar“, sobald ein Dienst nicht antwortete – dann ist „unbekannt“ nicht sicher."""
    ungueltig = bool(opencellid and opencellid.get("stand") == UNGUELTIG)
    orte = [
        (q, m) for q, e in ((OPENCELLID, opencellid), (BEACONDB, beacondb)) if (m := _gemerkt(e))
    ]
    if orte:
        quelle, mast = min(orte, key=lambda o: o[1].genau_m or 10**9)
        return Fund(GEFUNDEN, mast, quelle, ungueltig)
    staende = [e.get("stand", FEHLER) for e in (opencellid, beacondb) if e]
    if ungueltig:
        stand = UNGUELTIG
    elif FEHLER in staende:
        stand = FEHLER
    else:
        stand = NICHT_GEFUNDEN if mit_schluessel else OHNE_SCHLUESSEL
    return Fund(stand, schluessel_ungueltig=ungueltig)


def gesamtstand(funde: Sequence[Fund]) -> str:
    """Stand für die Karte. Ein abgelehnter Schlüssel zählt immer (Hinweis auch, wenn BeaconDB etwas fand)."""
    if any(f.schluessel_ungueltig for f in funde):
        return UNGUELTIG
    if any(f.mast for f in funde):
        return GEFUNDEN
    if not funde:
        return OHNE_KENNUNG
    staende = {f.stand for f in funde}
    for stand in (FEHLER, OHNE_SCHLUESSEL):
        if stand in staende:
            return stand
    return NICHT_GEFUNDEN


def such_text(z: Zelle, f: Fund | None, sprache: str = DE) -> str | None:
    """Was die Zellenliste sagt, wenn eine Zelle keinen Ort hat; None, wenn sie einen hat."""
    if f is None:
        if z.art != "LTE":
            if z.zelle:
                return t("{art} – nicht nachschlagbar", sprache, art=z.art)
            return t("nur PCI – nicht nachschlagbar", sprache)
        return t(
            "nur PCI – nicht nachschlagbar" if sendeanlage(z) is None else "Kennung unvollständig",
            sprache,
        )
    if f.mast:
        return None
    return t(
        "Dienste nicht erreichbar – später neu" if f.stand == FEHLER else "nicht gefunden", sprache
    )


def gemerkte_anlagen(merk: Mapping[str, Any]) -> dict[tuple[int, str], list[Mast]]:
    """Früher gefundene Zellen je Sendeanlage (Netz, eNodeB hex) aus dem Merkspeicher der Mastsuche – je Zelle der
    genauere Fund. Schlüssel dort: „mcc-mnc-lac-cellid“ (OpenCellID) bzw. „beacondb:…“."""
    je_zelle: dict[str, Mast] = {}
    for schluessel, eintrag in merk.items():
        mast = _gemerkt(eintrag) if isinstance(eintrag, Mapping) else None
        if mast is None:
            continue
        zelle = schluessel.removeprefix("beacondb:")
        alt = je_zelle.get(zelle)
        if alt is None or (mast.genau_m or 10**9) < (alt.genau_m or 10**9):
            je_zelle[zelle] = mast
    out: dict[tuple[int, str], list[Mast]] = {}
    for zelle, mast in je_zelle.items():
        teile = zelle.split("-")
        if len(teile) != 4 or not all(t.isdigit() for t in teile):
            continue
        out.setdefault((int(teile[1]), f"{int(teile[3]) // 256:x}"), []).append(mast)
    return out


def masten_je_anlage(
    zellen: Sequence[tuple[Zelle, Mast]],
    gemerkt: Mapping[tuple[int, str], Sequence[Mast]] | None = None,
    haupt: Zelle | None = None,
    alle: Sequence[Zelle] = (),
) -> list[tuple[str, Mast]]:
    """Geschätzter Mast je Sendeanlage; die Sendeanlage der Hauptzelle zuerst. Mit `gemerkt` zählen auch früher
    gefundene Zellen der Sendeanlagen, an denen die Box gerade hängt (`alle`) – so bleibt der Mast sichtbar, wenn die
    Box an einem Sektor hängt, den keine Datenbank kennt."""
    anlagen: dict[str, list[Mast]] = {}
    for z, ort in sorted(zellen, key=lambda zo: zo[0].rolle != "primary"):
        anlagen.setdefault(sendeanlage(z) or "", []).append(ort)
    frueher = gemerkt or {}
    for z in sorted(alle, key=lambda z: z.rolle != "primary") if frueher else ():
        enb = sendeanlage(z)
        plmn, _ = kennteile(z, haupt)
        if enb is None or not plmn.isdigit() or len(plmn) not in (5, 6):
            continue
        liste = anlagen.setdefault(enb, [])
        liste.extend(m for m in frueher.get((int(plmn[3:]), enb), []) if m not in liste)
    erst = sendeanlage(haupt) if haupt else None
    if (
        erst in anlagen
    ):  # Sendeanlage der Hauptzelle zuerst, auch wenn sie nur aus gemerkten Zellen besteht
        anlagen = {erst: anlagen[erst], **{k: v for k, v in anlagen.items() if k != erst}}
    return [(enb, mast) for enb, liste in anlagen.items() if liste and (mast := schaetzen(liste))]


def fuenf_g_dabei(zellen: Sequence[Zelle]) -> bool:
    """Läuft gerade 5G mit (Anker oder dazugebündelt)? Die Box nennt für 5G nur die PCI, nachschlagen geht nicht;
    bei 5G-NSA hängt die 5G-Zelle aber meist am selben Mast wie die LTE-Ankerzelle – daher nur „vermutlich“."""
    return any(z.art == "5G" and z.rolle in ("primary", "secondary") for z in zellen)


def stand_aus(antwort: Mapping[str, Any]) -> str:
    """Fehlerantwort von OpenCellID: Code 1 = Zelle unbekannt, 2 = Schlüssel ungültig, sonst (z. B. Tageslimit) Fehler."""
    code = antwort.get("code")
    return NICHT_GEFUNDEN if code == 1 else UNGUELTIG if code == 2 else FEHLER


def aufraeumen(merk: Mapping[str, Mapping[str, Any]], jetzt: float) -> dict[str, Any]:
    """Gemerktes ohne Wert mehr (älter als einen Monat) fällt heraus, damit der Speicher nicht wächst."""
    return {k: v for k, v in merk.items() if jetzt - float(v.get("t", 0)) < GUELTIG_S}


def faellig(eintrag: Mapping[str, Any] | None, jetzt: float, schluessel_id: str) -> bool:
    """Neu nachschlagen? Gefunden: nach einem Monat; nicht erreichbar: nach einer Stunde; sonst nach einem Tag –
    oder sofort, wenn ein neuer Schlüssel eingetragen ist."""
    if not eintrag:
        return True
    alter = jetzt - float(eintrag.get("t", 0))
    if eintrag.get("lat") is not None:
        return alter >= GUELTIG_S
    if eintrag.get("schluessel") != schluessel_id:
        return True
    return alter >= (FEHLER_S if eintrag.get("stand") == "fehler" else NOCHMAL_S)


def entfernung_m(a: Ort, b: Ort) -> float:
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp, dl = p2 - p1, math.radians(b.lon - a.lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * ERDE_M * math.asin(math.sqrt(h))


def peilung(von: Ort, nach: Ort) -> float:
    """Richtung in Grad (0 = Nord, 90 = Ost)."""
    p1, p2 = math.radians(von.lat), math.radians(nach.lat)
    dl = math.radians(nach.lon - von.lon)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def richtung(von: Ort, nach: Ort, sprache: str = DE) -> str:
    """Himmelsrichtung in acht Stufen."""
    return t(RICHTUNGEN[round(peilung(von, nach) / 45) % 8], sprache)


def strecke(m: float, sprache: str = DE) -> str:
    """„850 m“, „1,2 km“ (wie die Entfernung laut Box)."""
    return entfernung(round(m), sprache) or "0 m"


def rahmen(
    wohnung: Ort, ring_m: float | None, masten: Sequence[Ort] = (), punkte: Sequence[Mast] = ()
) -> tuple[float, float, float, float] | None:
    """Was die Karte beim Öffnen (und mit ⌖) zeigt: Süd, West, Nord, Ost um die Wohnung, groß genug für Ring, Masten
    und Zellen; None, wenn es nichts zu zeigen gibt. Der erste Mast (Sendeanlage der Hauptzelle) zählt immer, ferne
    Nachbarn und Zellen (weiter als FERN_M bzw. das Dreifache des Rings) zoomen nicht heraus."""
    grenze = max(FERN_M, 3 * (ring_m or 0))
    abstaende = [entfernung_m(wohnung, o) for o in [*masten[1:], *(p.ort for p in punkte)]]
    erster = entfernung_m(wohnung, masten[0]) if masten else 0
    weit = max([ring_m or 0, erster, *(d for d in abstaende if d <= grenze)]) or min(
        abstaende, default=0
    )
    if weit <= 0:
        return None
    weit *= 1.15  # etwas Rand, damit Beschriftungen nicht am Kartenrand kleben
    dlat = math.degrees(weit / ERDE_M)
    dlon = math.degrees(weit / (ERDE_M * max(math.cos(math.radians(wohnung.lat)), 0.01)))
    return (wohnung.lat - dlat, wohnung.lon - dlon, wohnung.lat + dlat, wohnung.lon + dlon)
