"""Internet-Störung zusammenfassen (AN-0003): mehrere kurze Ausfälle kurz hintereinander werden ein Journal-Eintrag,
sobald das Internet RUHE_S lang ohne Unterbrechung da war – mit Zahl der Unterbrechungen, Dauer und Ursache in Worten.

Lage während eines Ausfalls (von sammeln bestimmt): „box“ = auch die FRITZ!Box antwortet nicht, „neu“ = die Box wählt
sich neu ins Mobilfunknetz ein, „schwach“ = Mobilfunk-Empfang schwach, „steht“ = Mobilfunk steht ohne Neueinwahl,
None = keine Mobilfunk-Box oder unbekannt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .ereignis import WARNUNG, Ereignis
from .mobil import dauer
from .sprache import DE, merke, t

RUHE_S = 600  # so lange ohne Ausfall, dann gilt die Störung als vorbei
NEU_S = 300  # Mobilfunk-Verbindung jünger als 5 min: gerade neu eingewählt
SCHWACH_DBM = -110
LAGEN = ("box", "neu", "schwach", "steht")  # Reihenfolge = Gewicht für die Ursache

URSACHE = {
    "box": merke("die FRITZ!Box war vom Pi aus nicht erreichbar"),
    "neu": merke("die Box hat sich neu ins Mobilfunknetz eingewählt"),
    "schwach": merke("der Mobilfunk-Empfang war schwach – vermutlich die Funkstrecke"),
    "steht": merke("Mobilfunk stand (keine Neueinwahl), vermutlich beim Anbieter"),
}


@dataclass
class Stoerung:
    von: float
    weg_seit: float | None  # None = gerade wieder da
    bis: float | None = None  # Ende der letzten Unterbrechung
    anzahl: int = 1
    weg_s: float = 0.0
    lagen: list[str] = field(default_factory=list)

    def als_dict(self) -> dict[str, Any]:
        return asdict(self)


def aus_dict(d: dict[str, Any] | None) -> Stoerung | None:
    if not d:
        return None
    try:
        return Stoerung(
            von=float(d["von"]),
            weg_seit=None if d.get("weg_seit") is None else float(d["weg_seit"]),
            bis=None if d.get("bis") is None else float(d["bis"]),
            anzahl=int(d.get("anzahl", 1)),
            weg_s=float(d.get("weg_s", 0.0)),
            lagen=[str(x) for x in d.get("lagen") or [] if x in LAGEN],
        )
    except KeyError, TypeError, ValueError:
        return None


def lage(
    box_ok: bool,
    mobil_laufzeit_s: int | None,
    schwaechster_dbm: int | None,
    neu_eingewaehlt: bool,
    mobil: bool,
) -> str | None:
    """Was gerade los ist, wenn das Internet fehlt."""
    if not box_ok:
        return "box"
    if not mobil:
        return None
    if neu_eingewaehlt or (mobil_laufzeit_s is not None and mobil_laufzeit_s < NEU_S):
        return "neu"
    if schwaechster_dbm is not None and schwaechster_dbm < SCHWACH_DBM:
        return "schwach"
    return "steht"


def fortschreiben(
    st: Stoerung | None, internet_ok: bool, jetzt: float, lage_: str | None, sprache: str = DE
) -> tuple[Stoerung | None, Ereignis | None]:
    """Einen Abruf einrechnen; liefert die offene Störung und ggf. den Abschluss-Eintrag."""
    if not internet_ok:
        if st is None:
            st = Stoerung(von=jetzt, weg_seit=jetzt)
        elif st.weg_seit is None:
            st.anzahl += 1
            st.weg_seit = jetzt
        if lage_ and lage_ not in st.lagen:
            st.lagen.append(lage_)
        return st, None
    if st is None:
        return None, None
    if st.weg_seit is not None:
        st.weg_s += max(0.0, jetzt - st.weg_seit)
        st.weg_seit = None
        st.bis = jetzt
        return st, None
    if st.bis is not None and jetzt - st.bis >= RUHE_S:
        return None, Ereignis("internet_stoerung", WARNUNG, text(st, sprache))
    return st, None


def text(st: Stoerung, sprache: str = DE) -> str:
    weg = dauer(round(st.weg_s), sprache)
    if st.anzahl == 1:
        teil = t("1 Unterbrechung, {weg} weg", sprache, weg=weg)
    else:
        teil = t(
            "{n} Unterbrechungen in {dauer}, zusammen {weg} weg",
            sprache,
            n=st.anzahl,
            dauer=dauer(round((st.bis or st.von) - st.von), sprache),
            weg=weg,
        )
    ursache = next((t(URSACHE[x], sprache) for x in LAGEN if x in st.lagen), "")
    return t("Internet-Störung vorbei: {teil}", sprache, teil=teil) + (
        f" – {ursache}" if ursache else ""
    )
