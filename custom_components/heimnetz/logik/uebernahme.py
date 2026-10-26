"""Umstieg von der alten Integration „netzwerk“ auf „heimnetz“ (WU-0006): was übernommen wird und wann.

Übernommen wird nur in eine leere Heimnetz-Ablage und nur, solange die alte Integration nicht mehr läuft (nie beide
zugleich an der Box). Die alten Daten bleiben liegen; gelöscht wird nichts. Ohne Home Assistant, ohne Dateizugriff:
`uebernahme.py` der Integration liest Ordner und Speicher und schreibt nach diesem Plan.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

ALT_DATENBANK = "netzwerk.db"
# Begleitdateien von SQLite: die Datenbank kommt über die Sicherungs-Schnittstelle, nie als Datei-Kopie
DATENBANK_BEGLEITER = ("-wal", "-shm", "-journal")
# Speicher je Einrichtung: Einstellungen (Tarif, Messplan, Arten), gemerkte Masten, OSM-Masten, OpenCellID-Abzug
SPEICHER_ENDUNGEN = ("", ".mast", ".osm", ".ocid")
# Lesbare Ablage der Tickets: schreibt Heimnetz aus dem übernommenen Speicher selbst neu – die alte nie darüber kopieren
# (sie verwiese auf Bilder unter netzwerk/ und könnte eine frische Ablage ersetzen)
EIGENE_ABLAGE = ("meldungen.json", "meldungen.md")
# Fehler von SQLite, nach denen die alte Datenbank nicht zu retten ist; alle anderen (Platte voll, Ein-/Ausgabe,
# gesperrt …) sind vorübergehend: dann später noch einmal
DATENBANK_KAPUTT = ("SQLITE_CORRUPT", "SQLITE_NOTADB")


def alte_aktiv(deaktiviert: Iterable[bool]) -> bool:
    """Läuft die alte Integration noch (oder startet sie beim nächsten Mal)? Jede nicht deaktivierte Einrichtung
    zählt – auch eine, die gerade nicht geladen ist, denn sie lädt beim nächsten Start wieder."""
    return any(not d for d in deaktiviert)


def speicher_schluessel(
    alt_domain: str, alt_id: str, neu_domain: str, neu_id: str
) -> list[tuple[str, str]]:
    """Paare (alter Schlüssel, neuer Schlüssel) der Speicher je Einrichtung."""
    return [(f"{alt_domain}.{alt_id}{e}", f"{neu_domain}.{neu_id}{e}") for e in SPEICHER_ENDUNGEN]


def speicher_uebernehmen(
    neu: Mapping[str, Any] | None, alt: Mapping[str, Any] | None
) -> dict[str, Any] | None:
    """Was in den neuen Speicher kommt: der alte Inhalt, wenn der neue leer ist und der alte etwas hat; sonst None
    (nichts schreiben – Vorhandenes wird nie überschrieben)."""
    if neu or not alt:
        return None
    return dict(alt)


def meldungen_uebernehmen(
    neu: Mapping[str, Any] | None, alt: Mapping[str, Any] | None
) -> dict[str, Any] | None:
    """Tickets: nur wenn Heimnetz noch keine hat (weder Meldungen noch vergebene Nummern). Die Nummern kommen mit,
    damit die Zählung je Art weiterläuft (FE-0007 nach FE-0006, nie eine Nummer doppelt)."""
    if neu and (neu.get("meldungen") or neu.get("nummern")):
        return None
    if not alt or not (alt.get("meldungen") or alt.get("nummern")):
        return None
    return {
        "meldungen": list(alt.get("meldungen") or []),
        "nummern": {str(k): int(v) for k, v in (alt.get("nummern") or {}).items()},
    }


def dateien_planen(alt: Iterable[str], neu_vorhanden: Iterable[str]) -> list[tuple[str, str]]:
    """Paare (Quelle, Ziel) relativ zum alten bzw. neuen Ordner, ohne die Datenbank (siehe `datenbank_planen`).

    Kopiert wird nur, was im neuen Ordner noch fehlt; Begleitdateien der Datenbank und die lesbare Ablage der Tickets
    (oberste Ebene, `EIGENE_ABLAGE`) nie. Pfade mit „/“, sortiert."""
    vorhanden = set(neu_vorhanden)
    paare = []
    for pfad in sorted(set(alt)):
        name = pfad.rsplit("/", 1)[-1]
        if name == ALT_DATENBANK or (
            name.startswith(ALT_DATENBANK) and name[len(ALT_DATENBANK) :] in DATENBANK_BEGLEITER
        ):
            continue
        if pfad in EIGENE_ABLAGE:
            continue
        if pfad not in vorhanden:
            paare.append((pfad, pfad))
    return paare


def datenbank_planen(alt_da: bool, neu_da: bool) -> bool:
    """Datenbank übernehmen? Nur wenn die alte da ist und Heimnetz noch keine hat."""
    return alt_da and not neu_da


def datenbank_kaputt(fehlername: str | None) -> bool:
    """Ist die alte Datenbank nach diesem Fehler von SQLite (`sqlite_errorname`, z. B. „SQLITE_CORRUPT_INDEX“)
    dauerhaft unlesbar? Dann weiter ohne sie; sonst (unbekannt eingeschlossen) später noch einmal versuchen."""
    if not fehlername:
        return False
    return any(fehlername == k or fehlername.startswith(k + "_") for k in DATENBANK_KAPUTT)


def optionen_uebernehmen(
    alt: Mapping[str, Any] | None, schluessel: Iterable[str]
) -> dict[str, Any]:
    """Optionen der alten Einrichtung (z. B. OpenCellID-Schlüssel), nur die bekannten und nur mit Wert."""
    if not alt:
        return {}
    return {k: alt[k] for k in schluessel if alt.get(k)}
