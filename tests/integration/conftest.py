"""Tests gegen Home Assistant (pytest-homeassistant-custom-component), ohne FRITZ!Box und ohne Netz.

Jeder Test bekommt ein eigenes Home Assistant; kein Test beeinflusst einen anderen. Box, Prüfungen des Pi und
DHCP-Test werden ersetzt; die Beispieldaten sind dieselben wie in den Tests der Fachlogik.
"""

from unittest.mock import patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SSL, CONF_USERNAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heimnetz.box import BoxDaten
from custom_components.heimnetz.const import CONF_FRITZ_EINTRAG, DOMAIN, FRITZ
from custom_components.heimnetz.logik import befunde as bf
from custom_components.heimnetz.logik import geraete as gr
from custom_components.heimnetz.logik import messplan as mp
from custom_components.heimnetz.logik import mobil as mb
from custom_components.heimnetz.logik import protokoll as pr
from custom_components.heimnetz.logik import wlan as wl
from custom_components.heimnetz.logik import zugang as zg
from tests.logik.daten import GERAETELOG, HOSTLISTE, WLANLISTE, ZELLEN

pytest_plugins = ["pytest_homeassistant_custom_component"]

LAN = bf.Heimnetz("192.168.170.1", "255.255.255.0", "192.168.170.20", "192.168.170.200", True)
PI_OK = bf.PiVerbindung(box=True, internet=True, dns=True, gw_mac="AA")


@pytest.fixture(autouse=True)
def eigene_integration(enable_custom_integrations):
    """Die Integration aus custom_components/ laden lassen."""
    return


BEACONDB = "https://api.beacondb.net/v1/geolocate"
OVERPASS = "https://overpass-api.de/api/interpreter"


@pytest.fixture(autouse=True)
def beacondb_kennt_nichts(aioclient_mock):
    """Kein Test fragt das echte Internet: BeaconDB kennt nichts, Overpass meldet keine Masten – außer ein Test sagt es anders."""
    aioclient_mock.post(BEACONDB, status=404, json={"error": {"code": 404, "message": "Not found"}})
    aioclient_mock.post(OVERPASS, json={"elements": []})


@pytest.fixture(autouse=True)
def eigener_ordner(hass, tmp_path):
    """Jeder Test hat seine eigene HA-Konfiguration – Datenbank und Altdaten liegen nur dort."""
    hass.config.config_dir = str(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def deutsch(hass):
    """WU-0006: Die Texte der Integration folgen der Sprache von HA – die Tests prüfen Deutsch, außer ein Test stellt
    `hass.config.language` auf Englisch."""
    hass.config.language = "de"


@pytest.fixture(autouse=True)
def plan_aus():
    """WU-0006: Eine neue Installation misst von sich aus (messplan.NEU). Die Tests rechnen mit einem Plan, der aus
    ist, bis sie ihn einschalten; die Vorgabe selbst prüft test_vorgaben.py (überschreibt diese Fixture)."""
    with patch(f"custom_components.{DOMAIN}.logik.messplan.NEU", mp.Messplan()):
        yield


def box_daten(**kw) -> BoxDaten:
    werte = {
        "protokoll": pr.aus_xml(GERAETELOG),
        "lan": LAN,
        "geraete": gr.aus_hostliste(HOSTLISTE),
        "quellen": {},
        "mobil": mb.aus_antwort(
            {
                "NewCurrentAccessTechnology": "5G-NSA",
                "NewCellList": ZELLEN,
                "NewSignalRSRP0": -99,
                "NewSignalRSRP1": -104,
                "NewUptime": 3720,
            }
        ),
        "mobil_baender": "LTE 1, 3 · 5G n78",
        "wlan_baender": (wl.Band("2,4", True, 6, True, "ax"), wl.Band("5", True, 44, True, "ax")),
        "wlan_gast": False,
        "wlan_geraete": wl.geraete_aus(WLANLISTE),
        # WU-0009: Mobilfunk über das eingebaute Modem wie bei der FRITZ!Box 6860 5G
        "zugang": zg.Meldung(
            zugangsart="X_AVM-DE_LTE",
            link="Up",
            down_bit=1_000_000_000,
            up_bit=150_000_000,
            mobil_dienst=True,
            mobil_an=True,
        ),
    }
    werte.update(kw)
    return BoxDaten(**werte)


@pytest.fixture
def box():
    """Box.holen ersetzen; `box.return_value` / `box.side_effect` stellen den Fall ein."""
    with patch(f"custom_components.{DOMAIN}.box.Box.holen", return_value=box_daten()) as holen:
        yield holen


@pytest.fixture
def pi():
    with (
        patch(f"custom_components.{DOMAIN}.pi.verbindung", return_value=PI_OK) as verbindung,
        patch(f"custom_components.{DOMAIN}.pi.dhcp_test", return_value=bf.DhcpTest(True, ())),
    ):
        yield verbindung


@pytest.fixture
def fritz(hass):
    """Eintrag von FRITZ!Box Tools (nur die Daten, die Integration selbst wird nicht geladen)."""
    entry = MockConfigEntry(
        domain=FRITZ,
        title="FRITZ!Box Test",
        data={
            CONF_HOST: "192.0.2.1",
            CONF_PORT: 49000,
            CONF_USERNAME: "u",
            CONF_PASSWORD: "geheim",
            CONF_SSL: False,
        },
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def eintrag(hass, fritz):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id},
        unique_id=fritz.entry_id,
    )
    entry.add_to_hass(hass)
    return entry
