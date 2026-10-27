"""Einstellungen prüfen."""

from datetime import date

import pytest
from logik import einstellungen as es

HEUTE = date(2026, 10, 12)


def test_gueltig_und_leer():
    e = es.pruefen({"tarif_down": "150", "tarif_up": 30, "ab": "2026-09-21"}, HEUTE)
    assert e == es.Einstellungen(150.0, 30.0, date(2026, 9, 21))
    assert e.als_dict() == {
        "tarif_down": 150.0,
        "tarif_up": 30.0,
        "ab": "2026-09-21",
        "wlan_schwach": 40,
        "zugang_wahl": "auto",
        "zugang_adresse": None,
        "zugang_ersatz": "auto",
    }
    assert es.pruefen({"wlan_schwach": "50"}, HEUTE).wlan_schwach == 50
    assert es.pruefen({"tarif_down": 0, "ab": ""}, HEUTE) == es.Einstellungen()
    assert es.pruefen({"ab": "1970-01-01 00:00:00"}, HEUTE).ab is None  # alter Helfer „ohne Grenze“
    assert es.pruefen(e.als_dict(), HEUTE) == e


@pytest.mark.parametrize(
    "daten",
    [
        {"tarif_down": "viel"},
        {"tarif_up": -5},
        {"tarif_down": 20000},
        {"ab": "morgen"},
        {"ab": "2026-10-13"},
        {"wlan_schwach": 35},
        {"wlan_schwach": "wenig"},
        {"wlan_schwach": 0},
        {"wlan_schwach": 40.5},
        {"zugang_wahl": "satellit"},
        {"zugang_ersatz": "immer"},
        {"zugang_adresse": "8.8.8.8"},  # WU-0009: nur private Adressen
        {"zugang_adresse": "modem.local"},
        {"zugang_adresse": "127.0.0.1"},
    ],
)
def test_ungueltig(daten):
    with pytest.raises(es.Ungueltig):
        es.pruefen(daten, HEUTE)


def test_null_heisst_kein_tarif():
    assert es.pruefen({"tarif_up": "0.0"}, HEUTE).tarif_up is None


def test_zugang_wahl_und_adresse():
    """WU-0009: Wahl des Zugangs, Adresse eines vorgeschalteten Geräts (nur private) und Ersatz."""
    e = es.pruefen(
        {"zugang_wahl": "extern", "zugang_adresse": " 192.168.8.1 ", "zugang_ersatz": "kein"}, HEUTE
    )
    assert (e.zugang_wahl, e.zugang_adresse, e.zugang_ersatz) == ("extern", "192.168.8.1", "kein")
    assert es.pruefen(e.als_dict(), HEUTE) == e
    assert es.pruefen({"zugang_adresse": ""}, HEUTE).zugang_adresse is None
    assert es.pruefen({}, HEUTE).zugang_wahl == "auto"
