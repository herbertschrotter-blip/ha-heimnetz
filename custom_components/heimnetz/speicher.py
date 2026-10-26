"""Eigene kleine Datenbank (SQLite) der Integration: Journal, Protokoll der Box, Speedtest-Messungen, Gedächtnis.

Ohne Home Assistant, blockierend – Aufrufe laufen im Executor. Schema-Version in `PRAGMA user_version`, Schritte in
SCHRITTE (G-14). Während einer HA-Sicherung ist das Schreiben angehalten (backup.py): was dann anfällt, wartet in
einer Warteschlange. Die Datei liegt in der HA-Konfiguration (nicht unter /local), weil sie Gerätenamen und
Hardware-Adressen enthält.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .logik.ereignis import Ereignis
from .logik.messung import Messung
from .logik.protokoll import Protokolleintrag

SCHEMA_VERSION = 1
AUFBEWAHREN_S = 400 * 86_400  # Journal und Protokoll; Messungen bleiben

SCHRITTE: dict[int, tuple[str, ...]] = {
    1: (
        "CREATE TABLE meta (schluessel TEXT PRIMARY KEY, wert TEXT NOT NULL)",
        """CREATE TABLE journal (
            id INTEGER PRIMARY KEY, t REAL NOT NULL, art TEXT NOT NULL, stufe TEXT NOT NULL,
            text TEXT NOT NULL, mac TEXT NOT NULL DEFAULT '')""",
        "CREATE INDEX journal_t ON journal (t)",
        "CREATE INDEX journal_mac ON journal (mac, t)",
        """CREATE TABLE protokoll (
            id INTEGER PRIMARY KEY, t REAL, roh_zeit TEXT NOT NULL, kategorie TEXT NOT NULL,
            text TEXT NOT NULL, schluessel TEXT NOT NULL UNIQUE, eingetragen REAL NOT NULL)""",
        "CREATE INDEX protokoll_t ON protokoll (kategorie, t)",
        """CREATE TABLE messung (
            t REAL PRIMARY KEY, down REAL, up REAL, ping REAL, server TEXT NOT NULL DEFAULT '',
            last_down REAL, last_up REAL)""",
    ),
}
# WU-0005: Momentaufnahme je Messung (JSON, logik.kontext) in einer eigenen Tabelle, ohne Versionssprung: eine ältere
# Fassung der Integration (Rückweg `ausliefern.py --zurueck`) kennt die Tabelle nicht und lässt sie einfach liegen.
ZUSATZ = ("CREATE TABLE IF NOT EXISTS messung_kontext (t REAL PRIMARY KEY, kontext TEXT NOT NULL)",)

JOURNAL = "INSERT INTO journal (t, art, stufe, text, mac) VALUES (?, ?, ?, ?, ?)"
PROTOKOLL = (
    "INSERT OR IGNORE INTO protokoll (t, roh_zeit, kategorie, text, schluessel, eingetragen) "
    "VALUES (?, ?, ?, ?, ?, ?)"
)
MESSUNG = "INSERT OR IGNORE INTO messung VALUES (?, ?, ?, ?, ?, ?, ?)"
KONTEXT = "INSERT OR IGNORE INTO messung_kontext VALUES (?, ?)"
META = "INSERT OR REPLACE INTO meta VALUES (?, ?)"
META_WENN_NEU = "INSERT OR IGNORE INTO meta VALUES (?, ?)"

type Schritt = tuple[str, list[tuple[Any, ...]]]


class SchemaZuNeu(Exception):
    """Die Datei stammt von einer neueren Fassung der Integration – nicht anfassen."""


@dataclass(frozen=True)
class Journalzeile:
    t: float
    ereignis: Ereignis


def _muster(suche: str) -> str:
    """Teiltext für LIKE (Groß/Klein egal bei ASCII); %, _ und \\ gelten wörtlich."""
    zeichen = suche.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{zeichen}%"


def _journal(zeilen: Iterable[Journalzeile]) -> Schritt:
    return JOURNAL, [
        (z.t, z.ereignis.art, z.ereignis.stufe, z.ereignis.text, z.ereignis.mac) for z in zeilen
    ]


def _protokoll(eintraege: Iterable[Protokolleintrag], jetzt: float) -> Schritt:
    return PROTOKOLL, [
        (
            e.zeitpunkt.timestamp() if e.zeitpunkt else None,
            e.roh_zeit,
            e.kategorie,
            e.text,
            e.schluessel,
            jetzt,
        )
        for e in eintraege
    ]


def _messungen(messungen: Iterable[Messung]) -> Schritt:
    return MESSUNG, [
        (m.t, m.down, m.up, m.ping, m.server, m.last_down, m.last_up) for m in messungen
    ]


def _kontexte(kontexte: Iterable[tuple[float, dict[str, Any]]]) -> Schritt:
    return KONTEXT, [(t, json.dumps(k, ensure_ascii=False)) for t, k in kontexte if k]


def _kontext(roh: str | None) -> dict[str, Any]:
    if not roh:
        return {}
    try:
        wert = json.loads(roh)
    except ValueError:
        return {}
    return wert if isinstance(wert, dict) else {}


class Datenbank:
    def __init__(self, pfad: Path) -> None:
        self.pfad = pfad
        self._db: sqlite3.Connection | None = None
        self._sperre = threading.Lock()
        self._angehalten = False
        self._warteschlange: list[list[Schritt]] = []

    # ── Lebenszyklus ──
    def oeffnen(self) -> None:
        self.pfad.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.pfad, check_same_thread=False, isolation_level=None)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=NORMAL")
            self._migrieren(db)
            for befehl in ZUSATZ:
                db.execute(befehl)
        except Exception:
            db.close()
            raise
        with self._sperre:
            self._db = db

    def _migrieren(self, db: sqlite3.Connection) -> None:
        stand = int(db.execute("PRAGMA user_version").fetchone()[0])
        if stand > SCHEMA_VERSION:
            raise SchemaZuNeu(f"Schema {stand}, diese Fassung kennt {SCHEMA_VERSION}")
        for version in range(stand + 1, SCHEMA_VERSION + 1):
            with db:
                db.execute("BEGIN")
                for befehl in SCHRITTE[version]:
                    db.execute(befehl)
                db.execute(f"PRAGMA user_version = {version}")

    def schliessen(self) -> None:
        """Wartet auf einen laufenden Schreibvorgang; was danach kommt, schlägt mit RuntimeError fehl."""
        with self._sperre:
            if self._db is not None:
                self._db.close()
                self._db = None

    def anhalten(self) -> None:
        """Vor einer Sicherung: alles in die Hauptdatei; was danach anfällt, wartet bis `fortsetzen`."""
        with self._sperre:
            self._angehalten = True
            if self._db is not None:
                self._db.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    def fortsetzen(self) -> None:
        with self._sperre:
            self._angehalten = False
            wartend, self._warteschlange = self._warteschlange, []
            if self._db is not None:
                for schritte in wartend:
                    self._ausfuehren(schritte)

    @property
    def _verbindung(self) -> sqlite3.Connection:
        if self._db is None:
            raise RuntimeError("Datenbank nicht geöffnet")
        return self._db

    def _schreiben(self, *schritte: Schritt) -> int:
        """Alle Schritte in einer Transaktion – ganz oder gar nicht."""
        liste = [s for s in schritte if s[1]]
        if not liste:
            return 0
        with self._sperre:
            if self._angehalten:
                self._warteschlange.append(liste)
                return 0
            return self._ausfuehren(liste)

    def _ausfuehren(self, schritte: list[Schritt]) -> int:
        db = self._verbindung
        with db:
            db.execute("BEGIN")
            return sum(db.executemany(befehl, zeilen).rowcount for befehl, zeilen in schritte)

    # ── Schreiben ──
    def meta_setzen(self, schluessel: str, wert: str) -> None:
        self._schreiben((META, [(schluessel, wert)]))

    def gedaechtnis_speichern(self, daten: dict[str, Any] | str) -> None:
        text = daten if isinstance(daten, str) else json.dumps(daten, ensure_ascii=False)
        self.meta_setzen("gedaechtnis", text)

    def journal_schreiben(self, zeilen: Iterable[Journalzeile]) -> int:
        return self._schreiben(_journal(zeilen))

    def protokoll_schreiben(
        self, eintraege: Iterable[Protokolleintrag], jetzt: float | None = None
    ) -> int:
        """Neue Zeilen der Box; eine schon vorhandene (gleicher Schlüssel) wird nicht doppelt eingetragen."""
        return self._schreiben(_protokoll(eintraege, time.time() if jetzt is None else jetzt))

    def messungen_schreiben(self, messungen: Iterable[Messung]) -> int:
        """Neue Messungen samt Momentaufnahme in einer Transaktion; Anzahl der geschriebenen Zeilen."""
        liste = list(messungen)
        return self._schreiben(_messungen(liste), _kontexte((m.t, m.kontext) for m in liste))

    def abruf_schreiben(
        self,
        journal: Iterable[Journalzeile],
        protokoll: Iterable[Protokolleintrag],
        gedaechtnis: str | None,
        jetzt: float,
    ) -> None:
        """Ergebnis eines Abrufs in einer Transaktion: neue Ereignisse, neue Protokollzeilen, Gedächtnis."""
        self._schreiben(
            _journal(journal),
            _protokoll(protokoll, jetzt),
            (META, [("gedaechtnis", gedaechtnis)] if gedaechtnis is not None else []),
        )

    def aufraeumen(self, jetzt: float) -> int | None:
        """Alte Journal- und Protokollzeilen löschen (Protokoll ohne lesbare Zeit nach der Eintragezeit).
        None = während einer Sicherung ausgelassen."""
        grenze = jetzt - AUFBEWAHREN_S
        with self._sperre:
            if self._angehalten:
                return None
            db = self._verbindung
            with db:
                db.execute("BEGIN")
                n = db.execute("DELETE FROM journal WHERE t < ?", (grenze,)).rowcount
                n += db.execute(
                    "DELETE FROM protokoll WHERE COALESCE(t, eingetragen) < ?", (grenze,)
                ).rowcount
            return n

    # ── Lesen ──
    def _lesen(self, befehl: str, werte: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
        with self._sperre:
            return list(self._verbindung.execute(befehl, werte).fetchall())

    def meta(self, schluessel: str) -> str | None:
        zeilen = self._lesen("SELECT wert FROM meta WHERE schluessel = ?", (schluessel,))
        return None if not zeilen else str(zeilen[0][0])

    def gedaechtnis_laden(self) -> dict[str, Any] | None:
        wert = self.meta("gedaechtnis")
        return None if wert is None else dict(json.loads(wert))

    def salz(self) -> str:
        """Zufälliges Salz dieser Installation für die Geräte-Kennungen (einmal erzeugt, dann gleich)."""
        if self.meta("salz") is None:
            self._schreiben((META_WENN_NEU, [("salz", secrets.token_hex(16))]))
        return str(self.meta("salz"))

    def journal_lesen(
        self,
        ab: float = 0,
        nur_wichtig: bool = False,
        grenze: int = 200,
        suche: str = "",
        art: str = "",
    ) -> list[Journalzeile]:
        """Neueste zuerst. nur_wichtig = Warnungen und Kritisches; suche = Teiltext; art = nur diese Art (beides in der
        Datenbank gefiltert)."""
        filter_ = "AND stufe IN ('kritisch', 'warnung')" if nur_wichtig else ""
        mitte: tuple[Any, ...] = ()
        if suche:
            filter_ += " AND text LIKE ? ESCAPE '\\'"
            mitte += (_muster(suche),)
        if art:
            filter_ += " AND art = ?"
            mitte += (art,)
        werte: tuple[Any, ...] = (ab, *mitte, grenze)
        zeilen = self._lesen(
            f"SELECT t, art, stufe, text, mac FROM journal WHERE t >= ? {filter_} ORDER BY t DESC, id DESC LIMIT ?",
            werte,
        )
        return [
            Journalzeile(t, Ereignis(art, stufe, text, mac)) for t, art, stufe, text, mac in zeilen
        ]

    def geraet_lesen(self, mac: str, ab: float) -> list[Journalzeile]:
        """Ereignisse eines Geräts ab `ab`, älteste zuerst (Verlauf je Gerät)."""
        zeilen = self._lesen(
            "SELECT t, art, stufe, text, mac FROM journal WHERE mac = ? AND t >= ? ORDER BY t, id",
            (mac, ab),
        )
        return [Journalzeile(t, Ereignis(art, stufe, text, m)) for t, art, stufe, text, m in zeilen]

    def letzter_zustand(self, mac: str, vor: float) -> str | None:
        """Letztes online/offline/neu eines Geräts vor `vor` – Zustand am Anfang eines Verlaufs."""
        zeilen = self._lesen(
            "SELECT art FROM journal WHERE mac = ? AND t < ? AND art IN ('online', 'offline', 'neu') "
            "ORDER BY t DESC, id DESC LIMIT 1",
            (mac, vor),
        )
        return None if not zeilen else str(zeilen[0][0])

    def protokoll_lesen(
        self, kategorien: tuple[str, ...], grenze: int = 200, suche: str = ""
    ) -> list[Protokolleintrag]:
        """Neueste zuerst; Zeilen ohne lesbare Zeit stehen am Ende. suche = Teiltext (in der Datenbank gesucht)."""
        platz = ", ".join("?" * len(kategorien))
        filter_, such = (" AND text LIKE ? ESCAPE '\\'", (_muster(suche),)) if suche else ("", ())
        zeilen = self._lesen(
            f"SELECT t, roh_zeit, kategorie, text, schluessel FROM protokoll WHERE kategorie IN ({platz}){filter_} "
            "ORDER BY t IS NULL, t DESC, id DESC LIMIT ?",
            (*kategorien, *such, grenze),
        )
        return [
            Protokolleintrag(
                datetime.fromtimestamp(t) if t is not None else None, roh, kat, text, k
            )
            for t, roh, kat, text, k in zeilen
        ]

    def geraete_zaehlen(self, ab: float) -> dict[str, tuple[int, bool]]:
        """Je Gerät seit `ab`: (Abbrüche, neu?) – für die Übersicht, ohne den ganzen Verlauf zu lesen."""
        zeilen = self._lesen(
            "SELECT mac, SUM(art = 'offline'), MAX(art = 'neu') FROM journal WHERE t >= ? AND mac != '' GROUP BY mac",
            (ab,),
        )
        return {mac: (int(n or 0), bool(neu)) for mac, n, neu in zeilen}

    def erstes(self, mac: str) -> float | None:
        wert = self._lesen("SELECT MIN(t) FROM journal WHERE mac = ?", (mac,))[0][0]
        return None if wert is None else float(wert)

    def messungen_lesen(self, ab: float = 0) -> list[Messung]:
        """Älteste zuerst."""
        return [
            Messung(*z[:7], kontext=_kontext(z[7]))
            for z in self._lesen(
                "SELECT m.t, m.down, m.up, m.ping, m.server, m.last_down, m.last_up, k.kontext "
                "FROM messung m LEFT JOIN messung_kontext k ON k.t = m.t WHERE m.t >= ? ORDER BY m.t",
                (ab,),
            )
        ]

    def journal_texte(self, art: str, von: float, bis: float) -> list[tuple[float, str]]:
        """Zeit und Text der Journal-Einträge einer Art (z. B. „mobil_zelle“), älteste zuerst."""
        return [
            (float(z[0]), str(z[1]))
            for z in self._lesen(
                "SELECT t, text FROM journal WHERE art = ? AND t >= ? AND t <= ? ORDER BY t",
                (art, von, bis),
            )
        ]

    def ohne_kontext(self, ab: float) -> list[float]:
        """Zeitpunkte der Messungen ab `ab` ohne Momentaufnahme (zum Nachtragen, WU-0005)."""
        return [
            float(z[0])
            for z in self._lesen(
                "SELECT t FROM messung WHERE t >= ? AND t NOT IN (SELECT t FROM messung_kontext) "
                "ORDER BY t",
                (ab,),
            )
        ]

    def kontext_nachtragen(self, kontexte: dict[float, dict[str, Any]]) -> int:
        """Momentaufnahmen zu bestehenden Messungen setzen – nur, wo noch keine steht."""
        return self._schreiben(_kontexte(kontexte.items()))

    def letzte_messung(self) -> float:
        wert = self._lesen("SELECT MAX(t) FROM messung")[0][0]
        return 0.0 if wert is None else float(wert)

    def anzahl(self) -> dict[str, int]:
        return {
            tabelle: int(self._lesen(f"SELECT COUNT(*) FROM {tabelle}")[0][0])
            for tabelle in ("journal", "protokoll", "messung")
        }
