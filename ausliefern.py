"""Integration in die Home-Assistant-Konfiguration ausliefern – mit Rückweg.

    python ausliefern.py [--ziel <HA-Konfiguration>] [--ohne-pruefung]  ausliefern
    python ausliefern.py [--ziel <HA-Konfiguration>] --zurueck          jüngste Sicherung wiederherstellen

Kopiert den Ordner der Integration aus custom_components/ in die HA-Konfiguration. Vorher prüft es, ob die gebaute
Seite zu ihren Quellen passt (node frontend/bauen.mjs --pruefen), und bricht sonst ab; --ohne-pruefung übergeht das.
Die dort liegende Fassung wird vorher im Projekt unter .auslieferung/vorher/ mit Zeitstempel gesichert (nicht im Repo,
die letzten drei Stände bleiben); --zurueck stellt den jüngsten Stand wieder her und verbraucht ihn – mehrmals
aufgerufen geht es Stand für Stand zurück. Gab es vor einer Auslieferung keine Fassung, entfernt --zurueck die
Integration wieder. Ohne --ziel gilt der Ordner zwei Ebenen über dem Projekt, wenn dort eine configuration.yaml liegt.
Danach: Konfiguration prüfen und Home Assistant neu starten.
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DOMAIN = "heimnetz"
PROJEKT = Path(__file__).resolve().parent
QUELLE = PROJEKT / "custom_components" / DOMAIN
VORHER = (
    PROJEKT / ".auslieferung" / "vorher"
)  # je Stand <DOMAIN>-<Zeitstempel>, Ordner oder Merker *.keine
KEINE = ".keine"  # Merker: vor dieser Auslieferung gab es keine Fassung
STAENDE = 3  # so viele Sicherungen bleiben
BAUEN = QUELLE / "frontend" / "bauen.mjs"
# Nur ausgeliefert, was HA braucht: Quellen und Werkzeuge der Seite bleiben im Repo
OHNE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "node_modules", "src", "package*.json", "*.mjs"
)


class AuslieferFehler(RuntimeError):
    """Ziel oder Sicherung passt nicht; es wurde nichts geändert."""


def ha_konfiguration(ziel: str | None) -> Path:
    """HA-Konfiguration: --ziel oder zwei Ebenen über dem Projekt, mit configuration.yaml."""
    ordner = Path(ziel).resolve() if ziel else PROJEKT.parents[1]
    if not (ordner / "configuration.yaml").is_file():
        hinweis = "" if ziel else " – mit --ziel den Ordner der HA-Konfiguration angeben"
        raise AuslieferFehler(f"{ordner}: keine configuration.yaml{hinweis}")
    return ordner


def _ersetzen(quelle: Path, ziel: Path) -> None:
    """ziel durch eine Kopie von quelle ersetzen; erst kopieren, dann tauschen."""
    neu = ziel.with_name(f".{ziel.name}.neu")
    shutil.rmtree(neu, ignore_errors=True)
    shutil.copytree(quelle, neu, ignore=OHNE)
    if ziel.exists():
        shutil.rmtree(ziel)
    neu.rename(ziel)


def seite_pruefen() -> None:
    """Die gebaute Seite muss zu ihren Quellen passen (bauen.mjs --pruefen), sonst wird nicht ausgeliefert."""
    if not BAUEN.is_file():
        return
    hinweis = "– mit --ohne-pruefung trotzdem ausliefern"
    try:
        lauf = subprocess.run(
            ["node", str(BAUEN), "--pruefen"],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuslieferFehler(f"Seite nicht prüfbar ({exc}) {hinweis}") from exc
    if lauf.returncode != 0:
        text = (lauf.stderr or lauf.stdout).strip()
        raise AuslieferFehler(f"gebaute Seite passt nicht zur Quelle: {text} {hinweis}")


def _staende() -> list[Path]:
    """Gesicherte Stände, ältester zuerst. Der Stand ohne Zeitstempel (alte Fassung des Skripts) gilt als ältester."""

    def zeit(pfad: Path) -> str:
        return pfad.name.removesuffix(KEINE).removeprefix(DOMAIN).removeprefix("-")

    if not VORHER.is_dir():
        return []
    staende = [
        p
        for p in VORHER.iterdir()
        if p.name.removesuffix(KEINE) == DOMAIN
        or p.name.removesuffix(KEINE).startswith(f"{DOMAIN}-")
    ]
    return sorted(staende, key=zeit)


def _entfernen(pfad: Path) -> None:
    if pfad.is_dir():
        shutil.rmtree(pfad)
    else:
        pfad.unlink(missing_ok=True)


def _neuer_stand() -> Path:
    VORHER.mkdir(parents=True, exist_ok=True)
    zeit = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return VORHER / f"{DOMAIN}-{zeit}"


def ausliefern(konfiguration: Path, *, pruefen: bool = True) -> str:
    ziel = konfiguration / "custom_components" / DOMAIN
    if not (QUELLE / "manifest.json").is_file():
        raise AuslieferFehler(f"{QUELLE}: keine manifest.json")
    if pruefen:
        seite_pruefen()
    ziel.parent.mkdir(exist_ok=True)
    stand = _neuer_stand()
    if ziel.exists():
        _ersetzen(ziel, stand)
        gesichert = f"; vorige Fassung gesichert in {stand.relative_to(PROJEKT)}"
    else:
        stand = stand.with_name(stand.name + KEINE)
        stand.touch()
        gesichert = "; es gab keine vorige Fassung"
    for alt in _staende()[:-STAENDE]:
        _entfernen(alt)
    _ersetzen(QUELLE, ziel)
    return f"ausgeliefert nach {ziel}{gesichert}"


def zurueck(konfiguration: Path) -> str:
    ziel = konfiguration / "custom_components" / DOMAIN
    staende = _staende()
    if not staende:
        raise AuslieferFehler(f"{VORHER}: keine gesicherte Fassung – nichts zurückzunehmen")
    stand = staende[-1]
    if stand.name.endswith(KEINE):
        shutil.rmtree(ziel, ignore_errors=True)
        stand.unlink()
        return f"{ziel} entfernt – vor der Auslieferung gab es keine Fassung"
    if not (stand / "manifest.json").is_file():
        raise AuslieferFehler(f"{stand}: Sicherung ohne manifest.json – nichts geändert")
    _ersetzen(stand, ziel)
    shutil.rmtree(stand)
    return f"Fassung aus {stand.name} wiederhergestellt in {ziel} (noch {len(staende) - 1} ältere Stände)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"{DOMAIN} in die HA-Konfiguration ausliefern")
    parser.add_argument("--ziel", help="Ordner der HA-Konfiguration (mit configuration.yaml)")
    parser.add_argument("--zurueck", action="store_true", help="jüngste Sicherung wiederherstellen")
    parser.add_argument(
        "--ohne-pruefung",
        action="store_true",
        help="nicht prüfen, ob die gebaute Seite zu den Quellen passt",
    )
    args = parser.parse_args(argv)
    try:
        konfiguration = ha_konfiguration(args.ziel)
        meldung = (
            zurueck(konfiguration)
            if args.zurueck
            else ausliefern(konfiguration, pruefen=not args.ohne_pruefung)
        )
    except (AuslieferFehler, OSError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    print(meldung)
    print("Danach: Konfiguration prüfen und Home Assistant neu starten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
