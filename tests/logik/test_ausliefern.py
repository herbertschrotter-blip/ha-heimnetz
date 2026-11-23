"""Auslieferung mit Rückweg – ohne Home Assistant, in einer nachgebauten Konfiguration."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SKRIPT = Path(__file__).resolve().parents[2] / "ausliefern.py"
DOMAIN = "heimnetz"


@pytest.fixture
def ha(tmp_path):
    """HA-Konfiguration mit dem Projekt unter projekte/, wie auf dem HA-Rechner."""
    (tmp_path / "configuration.yaml").write_text("homeassistant:\n", encoding="utf-8")
    projekt = tmp_path / "projekte" / "projekt"
    integration = projekt / "custom_components" / DOMAIN
    integration.mkdir(parents=True)
    (integration / "manifest.json").write_text('{"version": "2"}', encoding="utf-8")
    (integration / "__pycache__").mkdir()
    shutil.copy(SKRIPT, projekt / "ausliefern.py")
    return tmp_path


def lauf(ha, *args):
    return subprocess.run(
        [sys.executable, str(ha / "projekte" / "projekt" / "ausliefern.py"), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def ausgeliefert(ha):
    return (ha / "custom_components" / DOMAIN / "manifest.json").read_text(encoding="utf-8")


def test_erste_auslieferung(ha):
    r = lauf(ha)
    assert r.returncode == 0, r.stderr
    assert ausgeliefert(ha) == '{"version": "2"}'
    assert not (ha / "custom_components" / DOMAIN / "__pycache__").exists()
    assert "neu starten" in r.stdout


def test_vorige_fassung_sichern_und_zurueck(ha):
    alt = ha / "custom_components" / DOMAIN
    alt.mkdir(parents=True)
    (alt / "manifest.json").write_text('{"version": "1"}', encoding="utf-8")
    assert lauf(ha).returncode == 0
    assert ausgeliefert(ha) == '{"version": "2"}'
    r = lauf(ha, "--zurueck")
    assert r.returncode == 0, r.stderr
    assert ausgeliefert(ha) == '{"version": "1"}'


def test_zurueck_nach_erster_auslieferung_entfernt(ha):
    assert lauf(ha).returncode == 0
    r = lauf(ha, "--zurueck")
    assert r.returncode == 0, r.stderr
    assert not (ha / "custom_components" / DOMAIN).exists()
    assert lauf(ha, "--zurueck").returncode == 1


def test_zurueck_ohne_sicherung(ha):
    r = lauf(ha, "--zurueck")
    assert r.returncode == 1
    assert "keine gesicherte Fassung" in r.stderr


def test_ziel_ohne_configuration_yaml(ha, tmp_path_factory):
    leer = tmp_path_factory.mktemp("kein_ha")
    r = lauf(ha, "--ziel", str(leer))
    assert r.returncode == 1
    assert not (leer / "custom_components").exists()


def test_nur_die_gebaute_seite_wird_ausgeliefert(ha):
    """Quellen und Werkzeuge der Seite bleiben im Repo; ausgeliefert wird nur die gebaute Datei."""
    frontend = ha / "projekte" / "projekt" / "custom_components" / DOMAIN / "frontend"
    for pfad in (
        "node_modules/lit/index.js",
        "src/heimnetz-panel.js",
        "package.json",
        "bauen.mjs",
        "heimnetz-panel.js",
    ):
        (frontend / pfad).parent.mkdir(parents=True, exist_ok=True)
        (frontend / pfad).write_text("//", encoding="utf-8")
    assert lauf(ha, "--ohne-pruefung").returncode == 0
    ziel = ha / "custom_components" / DOMAIN / "frontend"
    assert sorted(p.name for p in ziel.iterdir()) == ["heimnetz-panel.js"]


def ausliefern_version(ha, version):
    manifest = ha / "projekte" / "projekt" / "custom_components" / DOMAIN / "manifest.json"
    manifest.write_text(f'{{"version": "{version}"}}', encoding="utf-8")
    r = lauf(ha)
    assert r.returncode == 0, r.stderr


def staende(ha):
    return sorted(
        p.name for p in (ha / "projekte" / "projekt" / ".auslieferung" / "vorher").iterdir()
    )


def test_mehrere_staende_und_schrittweise_zurueck(ha):
    """Zweimal ausliefern überschreibt die letzte gute Fassung nicht; --zurueck geht Stand für Stand zurück."""
    for version in ("1", "2", "3"):
        ausliefern_version(ha, version)
    assert ausgeliefert(ha) == '{"version": "3"}'
    assert lauf(ha, "--zurueck").returncode == 0
    assert ausgeliefert(ha) == '{"version": "2"}'
    assert lauf(ha, "--zurueck").returncode == 0
    assert ausgeliefert(ha) == '{"version": "1"}'
    r = lauf(ha, "--zurueck")
    assert r.returncode == 0, r.stderr
    assert not (ha / "custom_components" / DOMAIN).exists()


def test_nur_die_letzten_drei_staende_bleiben(ha):
    for version in ("1", "2", "3", "4", "5"):
        ausliefern_version(ha, version)
    namen = staende(ha)
    assert len(namen) == 3
    assert all(n.startswith(f"{DOMAIN}-") and not n.endswith(".keine") for n in namen)
    for erwartet in ("4", "3", "2"):
        assert lauf(ha, "--zurueck").returncode == 0
        assert ausgeliefert(ha) == f'{{"version": "{erwartet}"}}'
    assert lauf(ha, "--zurueck").returncode == 1


def test_alter_stand_ohne_zeitstempel_gilt_als_aeltester(ha):
    """Sicherung der früheren Fassung des Skripts (…/vorher/heimnetz) wird übernommen, fremde Ordner bleiben."""
    vorher = ha / "projekte" / "projekt" / ".auslieferung" / "vorher"
    (vorher / DOMAIN).mkdir(parents=True)
    (vorher / DOMAIN / "manifest.json").write_text('{"version": "0"}', encoding="utf-8")
    (vorher / "netzwerk").mkdir()
    ausliefern_version(ha, "1")
    ausliefern_version(ha, "2")
    assert lauf(ha, "--zurueck").returncode == 0
    assert ausgeliefert(ha) == '{"version": "1"}'
    assert lauf(ha, "--zurueck").returncode == 0
    assert not (ha / "custom_components" / DOMAIN).exists()
    assert lauf(ha, "--zurueck").returncode == 0
    assert ausgeliefert(ha) == '{"version": "0"}'
    assert (vorher / "netzwerk").is_dir()


def bauen_mit_ergebnis(ha, code):
    bauen = ha / "projekte" / "projekt" / "custom_components" / DOMAIN / "frontend" / "bauen.mjs"
    bauen.parent.mkdir(parents=True, exist_ok=True)
    bauen.write_text(
        f"if (!process.argv.includes('--pruefen')) process.exit(9);\n"
        f"console.error('passt nicht');\nprocess.exit({code});\n",
        encoding="utf-8",
    )


@pytest.mark.skipif(shutil.which("node") is None, reason="node fehlt")
def test_veraltete_seite_bricht_ab(ha):
    bauen_mit_ergebnis(ha, 1)
    r = lauf(ha)
    assert r.returncode == 1
    assert "passt nicht" in r.stderr
    assert "--ohne-pruefung" in r.stderr
    assert not (ha / "custom_components" / DOMAIN).exists()
    r = lauf(ha, "--ohne-pruefung")
    assert r.returncode == 0, r.stderr
    assert ausgeliefert(ha) == '{"version": "2"}'


@pytest.mark.skipif(shutil.which("node") is None, reason="node fehlt")
def test_aktuelle_seite_wird_ausgeliefert(ha):
    bauen_mit_ergebnis(ha, 0)
    r = lauf(ha)
    assert r.returncode == 0, r.stderr
    assert ausgeliefert(ha) == '{"version": "2"}'
