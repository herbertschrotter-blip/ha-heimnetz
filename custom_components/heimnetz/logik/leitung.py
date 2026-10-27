"""Werte der Leitung je Zugangsart (WU-0009): DSL und Glasfaser aus TR-064, bewertet; Kabel liefert TR-064 nicht.

Ohne Home Assistant und ohne Netz. Gelesen wird im gemeinsamen Abruf (box.py, langsamer Takt), nur wenn die Box den
Dienst hat. Quellen: AVM/FRITZ!-Doku „TR-064 Support“ (fritz.support/resources) und für die Einheiten die TR-064-Norm
des Broadband Forum (DSL-Raten in kbit/s, Störabstandsmarge und Dämpfung in 0,1 dB – so rechnet auch fritzconnection,
`format_dB` teilt durch 10):

- DSL: `WANDSLInterfaceConfig1` · `GetInfo` (`NewStatus`, `NewDownstream/UpstreamCurrRate`, `…MaxRate`,
  `…NoiseMargin`, `…Attenuation`), `X_AVM-DE_GetDSLInfo` (`NewModulationType`, `NewCurrentProfile`) und
  `GetStatisticsTotal` (`NewCRCErrors`, `NewFECErrors` der Box, `NewATUCCRCErrors`, `NewATUCFECErrors` der Gegenstelle).
  Den Hersteller der Gegenstelle (DSLAM), Vectoring und die Zeit seit der Synchronisierung meldet TR-064 nicht.
- Glasfaser: `X_AVM-DE_WANFiber1` · `GetInfo` (`NewOpticalSignalLevel`, `NewTransmitOpticalLevel` und die Schwellen
  der Box `NewLower/UpperOpticalThreshold`, `NewLower/UpperTransmitPowerThreshold`, alle in dBm/1000; `NewFiberMode`)
  und `GetStatistics` (`NewPacketErrorsReceived/Sent`, `NewResyncs`, `NewMinutesInShowtime`). Seriennummern und
  Kennungen (SFP, GPON) werden nicht übernommen; Status O1–O7 und Temperatur meldet TR-064 nicht.
- Kabel: TR-064 hat keinen Dienst für DOCSIS – Kanäle, Pegel, MER und Fehler meldet die Schnittstelle nicht; es bleibt
  die Rate der Verbindung aus `GetCommonLinkProperties` (logik/zugang.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from .sprache import DE, t, zahl

STUNDE_S = 3600
NEUSYNC_TAGE = 7
MARGE_GUT_DB = 6.0  # Störabstandsmarge: darunter wenig Reserve
MARGE_KRITISCH_DB = 3.0
CRC_ERHOEHT_H = 10  # nicht korrigierbare Fehler je Stunde
CRC_HOCH_H = 100
NEUSYNC_EINIGE = 2
NEUSYNC_VIELE = 5
LICHT_KNAPP_DB = 2.0  # so nah an der unteren Schwelle der Box gilt das Licht als knapp


@dataclass(frozen=True)
class Dsl:
    """Was die Box über die DSL-Leitung meldet; None = nicht gemeldet."""

    t: float
    status: str = ""
    sync_down: int | None = None  # kbit/s
    sync_up: int | None = None
    max_down: int | None = None
    max_up: int | None = None
    marge_down: int | None = None  # 0,1 dB
    marge_up: int | None = None
    daempfung_down: int | None = None  # 0,1 dB
    daempfung_up: int | None = None
    modulation: str = ""  # X_AVM-DE_GetDSLInfo: VDSL, ADSL …
    profil: str = ""  # z. B. 17a, 35b
    crc: int | None = None  # GetStatisticsTotal, seit der Synchronisierung
    fec: int | None = None
    crc_gegen: int | None = None
    fec_gegen: int | None = None


@dataclass(frozen=True)
class Faser:
    """Was die Box über den Glasfaser-Anschluss meldet; Pegel in dBm/1000."""

    t: float
    modus: str = ""
    rx: int | None = None
    rx_min: int | None = None
    rx_max: int | None = None
    tx: int | None = None
    tx_min: int | None = None
    tx_max: int | None = None
    fehler_rx: int | None = None  # PacketErrorsReceived
    fehler_tx: int | None = None
    resyncs: int | None = None
    minuten: int | None = None  # MinutesInShowtime: so lange verbunden


@dataclass(frozen=True)
class Bewertung:
    stufe: str  # gut, knapp, schlecht – „“ = ohne Bewertung
    titel: str
    text: str
    abzeichen: str


def db(zehntel: int | None) -> float | None:
    """0,1 dB → dB."""
    return None if zehntel is None else round(zehntel / 10, 1)


def dbm(tausendstel: int | None) -> float | None:
    """dBm/1000 → dBm."""
    return None if tausendstel is None else round(tausendstel / 1000, 1)


def mbit(kbit: int | None) -> float | None:
    return None if kbit is None else round(kbit / 1000, 1)


def _je_stunde(vorher: int | None, jetzt: int | None, sekunden: float) -> float | None:
    if vorher is None or jetzt is None or sekunden < 60 or jetzt < vorher:
        return None
    return round((jetzt - vorher) * STUNDE_S / sekunden, 1)


def dsl_neu_synchron(vorher: Dsl | None, jetzt: Dsl) -> bool:
    """Neusynchronisierung seit dem letzten Lesen: Status wieder „Up“ oder die Fehlerzähler fingen neu an."""
    if vorher is None or jetzt.status != "Up":
        return False
    if vorher.status != "Up":
        return True
    return any(
        a is not None and b is not None and b < a
        for a, b in ((vorher.crc, jetzt.crc), (vorher.fec, jetzt.fec))
    )


def dsl_fehler_je_stunde(vorher: Dsl | None, jetzt: Dsl) -> tuple[float | None, float | None]:
    """CRC (nicht korrigierbar) und FEC (korrigiert) je Stunde seit dem letzten Lesen; None nach einem Neustart der
    Zähler oder ohne vorigen Wert."""
    if vorher is None:
        return None, None
    s = jetzt.t - vorher.t
    return _je_stunde(vorher.crc, jetzt.crc, s), _je_stunde(vorher.fec, jetzt.fec, s)


def neusync_fortschreiben(liste: list[float], neu: bool, jetzt: float) -> list[float]:
    """Zeitpunkte der Neusynchronisierungen, nur die letzten NEUSYNC_TAGE."""
    grenze = jetzt - NEUSYNC_TAGE * 86_400
    return [x for x in liste if x >= grenze] + ([jetzt] if neu else [])


def anteil(sync: int | None, moeglich: int | None) -> int | None:
    """Synchronrate in Prozent der möglichen."""
    if not sync or not moeglich:
        return None
    return round(100 * sync / moeglich)


def _marge_stufe(marge_db: float | None) -> str:
    if marge_db is None:
        return ""
    return (
        "schlecht"
        if marge_db < MARGE_KRITISCH_DB
        else "knapp"
        if marge_db < MARGE_GUT_DB
        else "gut"
    )


_RANG = {"": 0, "gut": 1, "knapp": 2, "schlecht": 3}


def _schlechter(*stufen: str) -> str:
    return max(stufen, key=lambda x: _RANG[x])


def marge_stufe(d: Dsl) -> str:
    """Schlechtere Störabstandsmarge der beiden Richtungen: gut, knapp, schlecht oder „“ ohne Wert."""
    return _schlechter(_marge_stufe(db(d.marge_down)), _marge_stufe(db(d.marge_up)))


def dsl_bewerten(d: Dsl, crc_h: float | None, neusync: int, s: str = DE) -> Bewertung:
    """Bewertung der Leitung: Störabstandsmarge (gut ab 6 dB, unter 3 dB kritisch), nicht korrigierbare Fehler je
    Stunde (über 10 erhöht, über 100 hoch) und Neusynchronisierungen in 7 Tagen (ab 2 auffällig, ab 5 instabil)."""
    if d.status and d.status != "Up":
        return Bewertung(
            "schlecht",
            t("DSL nicht synchron", s),
            t(
                "Die Box meldet für die DSL-Leitung: {status}. Kabel zur Telefondose prüfen; hält es an, beim Anbieter melden.",
                s,
                status=d.status,
            ),
            t("getrennt", s),
        )
    m_down, m_up = db(d.marge_down), db(d.marge_up)
    marge = marge_stufe(d)
    fehler = (
        ""
        if crc_h is None
        else "schlecht"
        if crc_h > CRC_HOCH_H
        else "knapp"
        if crc_h > CRC_ERHOEHT_H
        else "gut"
    )
    sync = (
        "schlecht" if neusync >= NEUSYNC_VIELE else "knapp" if neusync >= NEUSYNC_EINIGE else "gut"
    )
    stufe = _schlechter(marge, fehler, sync)
    saetze: list[str] = []
    schwach = min((x for x in (m_down, m_up) if x is not None), default=None)
    if schwach is not None:
        richtung = t("Download" if schwach == m_down else "Upload", s)
        saetze.append(
            t(
                "Die Störabstandsmarge im {richtung} liegt bei {db} dB (gut ab {gut} dB).",
                s,
                richtung=richtung,
                db=zahl(schwach, 1, s),
                gut=zahl(MARGE_GUT_DB, 0, s),
            )
        )
    p = anteil(d.sync_down, d.max_down)
    if p is not None:
        saetze.append(t("Die Leitung läuft mit {p} % der möglichen Geschwindigkeit.", s, p=p))
    if crc_h is not None:
        saetze.append(t("{n} nicht korrigierbare Fehler je Stunde.", s, n=zahl(crc_h, 0, s)))
    saetze.append(
        t(
            "{n} Neusynchronisierung in 7 Tagen."
            if neusync == 1
            else "{n} Neusynchronisierungen in 7 Tagen.",
            s,
            n=neusync,
        )
    )
    if stufe in ("knapp", "schlecht"):
        saetze.append(t("Häufige Ursache: Verkabelung im Haus (Telefondose, Verlängerung).", s))
    if stufe == "schlecht":
        titel, abzeichen = t("Leitung instabil", s), t("instabil", s)
    elif stufe == "knapp" and marge == "knapp":
        titel, abzeichen = t("Leitung stabil, aber wenig Reserve", s), t("Reserve knapp", s)
    elif stufe == "knapp":
        titel, abzeichen = t("Leitung mit Auffälligkeiten", s), t("auffällig", s)
    elif stufe == "gut":
        titel, abzeichen = t("Leitung in Ordnung", s), t("gut", s)
    else:
        titel, abzeichen = t("DSL verbunden", s), ""
    return Bewertung(stufe, titel, " ".join(saetze), abzeichen)


def faser_fehler_je_stunde(vorher: Faser | None, jetzt: Faser) -> float | None:
    """Empfangene fehlerhafte Pakete je Stunde seit dem letzten Lesen."""
    if vorher is None:
        return None
    return _je_stunde(vorher.fehler_rx, jetzt.fehler_rx, jetzt.t - vorher.t)


def _schwellen(lo: int | None, hi: int | None) -> tuple[int, int] | None:
    """Schwellen der Box; 0/0 oder vertauscht = nicht gemeldet."""
    if lo is None or hi is None or lo == hi:
        return None
    return (min(lo, hi), max(lo, hi))


def licht_bereich(f: Faser) -> tuple[float, float] | None:
    """Guter Bereich der empfangenen Lichtleistung laut Box (dBm, von unten nach oben)."""
    b = _schwellen(f.rx_min, f.rx_max)
    return None if b is None else (b[0] / 1000, b[1] / 1000)


def sende_bereich(f: Faser) -> tuple[float, float] | None:
    b = _schwellen(f.tx_min, f.tx_max)
    return None if b is None else (b[0] / 1000, b[1] / 1000)


def faser_bewerten(f: Faser, s: str = DE) -> Bewertung:
    """Bewertung nach den Schwellen, die die Box selbst meldet: außerhalb = schlecht, bis 2 dB über der unteren
    Schwelle = knapp. Ohne Schwellen keine Bewertung."""
    rx, bereich = dbm(f.rx), licht_bereich(f)
    saetze: list[str] = []
    stufe = ""
    if rx is not None and bereich is not None:
        lo, hi = bereich
        stufe = "schlecht" if not lo <= rx <= hi else "knapp" if rx - lo < LICHT_KNAPP_DB else "gut"
        saetze.append(
            t(
                "Das Licht kommt mit {rx} dBm an (gut zwischen {hi} und {lo} dBm laut Box).",
                s,
                rx=zahl(rx, 1, s),
                hi=zahl(hi, 1, s),
                lo=zahl(lo, 1, s),
            )
        )
    elif rx is not None:
        saetze.append(t("Das Licht kommt mit {rx} dBm an.", s, rx=zahl(rx, 1, s)))
    if f.minuten:
        saetze.append(t("Seit {dauer} ohne Unterbrechung.", s, dauer=dauer(f.minuten * 60, s)))
    if stufe == "schlecht":
        saetze.append(
            t(
                "Stecker und Glasfaserkabel prüfen (nicht knicken); hält es an, beim Anbieter melden.",
                s,
            )
        )
    titel, abzeichen = {
        "gut": (t("Glasfaser in Ordnung", s), t("gut", s)),
        "knapp": (t("Glasfaser: Licht knapp", s), t("knapp", s)),
        "schlecht": (t("Glasfaser: Licht außerhalb des guten Bereichs", s), t("prüfen", s)),
        "": (t("Glasfaser verbunden", s), ""),
    }[stufe]
    return Bewertung(stufe, titel, " ".join(saetze), abzeichen)


def dauer(sekunden: float, s: str = DE) -> str:
    """Grobe Dauer: Tage und Stunden, Stunden und Minuten oder Minuten."""
    m = int(sekunden // 60)
    tage, rest = divmod(m, 1440)
    h, mi = divmod(rest, 60)
    if tage:
        return t("{t} Tage {h} h" if tage != 1 else "{t} Tag {h} h", s, t=tage, h=h)
    if h:
        return t("{h} h {m} min", s, h=h, m=mi)
    return t("{m} min", s, m=mi)
