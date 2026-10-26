"""Umstieg von der alten Integration „netzwerk“ (WU-0006): Übernahme beim ersten Laden, nie beide parallel."""

import sqlite3
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryDisabler, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heimnetz.const import (
    ALT_DOMAIN,
    CONF_ALT_EINTRAG,
    CONF_FRITZ_EINTRAG,
    CONF_OPENCELLID,
    CONF_UEBERNOMMEN,
    DOMAIN,
    ISSUE_ALT_AKTIV,
)
from custom_components.heimnetz.logik.messung import Messung
from custom_components.heimnetz.speicher import Datenbank

MESSUNG = Messung(1_760_000_000.0, 98.5, 22.1, 31.0, "Testserver", 0.4, 0.1)
ALTE_TICKETS = {
    "meldungen": [
        {
            "id": "a1",
            "ticket": "FE-0006",
            "art": "fehler",
            "text": "alt",
            "status": "neu",
            "bilder": ["FE-0006-1.jpg"],
        }
    ],
    "nummern": {"FE": 6, "WU": 2},
}


def _speicher(hass_storage, key: str, daten) -> None:
    hass_storage[key] = {"version": 1, "minor_version": 1, "key": key, "data": daten}


def _alt(hass: HomeAssistant, **kw) -> MockConfigEntry:
    alt = MockConfigEntry(
        domain=ALT_DOMAIN,
        title="Netzwerk",
        data={CONF_FRITZ_EINTRAG: "x"},
        options={CONF_OPENCELLID: "schluessel"},
        **kw,
    )
    alt.add_to_hass(hass)
    return alt


def _altbestand(ordner, hass_storage, alt: MockConfigEntry) -> None:
    """Was die alte Integration hinterlässt: Datenbank mit einer Messung, Bild eines Tickets, Speicher."""
    db = Datenbank(ordner / "netzwerk" / "netzwerk.db")
    db.oeffnen()
    db.messungen_schreiben([MESSUNG])
    db.schliessen()
    (ordner / "netzwerk" / "meldungen").mkdir()
    (ordner / "netzwerk" / "meldungen" / "FE-0006-1.jpg").write_bytes(b"bild")
    _speicher(
        hass_storage,
        f"netzwerk.{alt.entry_id}",
        {"tarif_down": 150, "messplan": {"an": True, "takt_h": 12}},
    )
    _speicher(hass_storage, f"netzwerk.{alt.entry_id}.mast", {"zelle": {"t": 1}})
    _speicher(hass_storage, "netzwerk.meldungen", ALTE_TICKETS)


async def _laden(hass: HomeAssistant, eintrag) -> None:
    await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()


async def test_uebernahme_beim_ersten_laden(
    hass: HomeAssistant, hass_storage, hass_ws_client, fritz, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    _altbestand(eigener_ordner, hass_storage, alt)
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id, CONF_ALT_EINTRAG: alt.entry_id},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED
    lz = eintrag.runtime_data
    # Messungen aus der alten Datenbank, Einstellungen und Messplan aus dem alten Speicher
    assert lz.datenbank.messungen_lesen() == [MESSUNG]
    assert lz.einstellungen.wert.tarif_down == 150
    assert lz.einstellungen.plan.an and lz.einstellungen.plan.takt_h == 12
    assert hass_storage[f"heimnetz.{eintrag.entry_id}.mast"]["data"] == {"zelle": {"t": 1}}
    assert eintrag.data[CONF_UEBERNOMMEN] is True
    # Bild des Tickets liegt jetzt auch unter heimnetz/, die alten Dateien bleiben
    assert (eigener_ordner / "heimnetz" / "meldungen" / "FE-0006-1.jpg").read_bytes() == b"bild"
    assert (eigener_ordner / "netzwerk" / "netzwerk.db").exists()
    assert (eigener_ordner / "netzwerk" / "meldungen" / "FE-0006-1.jpg").exists()
    assert "netzwerk.meldungen" in hass_storage
    # Tickets: übernommen, die Nummern laufen weiter
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/meldungen"})
    assert [m["ticket"] for m in (await client.receive_json())["result"]] == ["FE-0006"]
    await client.send_json_auto_id(
        {"type": "heimnetz/meldung/neu", "meldung": {"art": "fehler", "text": "neu"}}
    )
    assert (await client.receive_json())["result"]["ticket"] == "FE-0007"


async def test_vorhandenes_wird_nie_ueberschrieben(
    hass: HomeAssistant, hass_storage, fritz, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    _altbestand(eigener_ordner, hass_storage, alt)
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    neu = Datenbank(eigener_ordner / "heimnetz" / "heimnetz.db")
    neu.oeffnen()
    neu.schliessen()
    _speicher(hass_storage, f"heimnetz.{eintrag.entry_id}", {"tarif_down": 50})
    await _laden(hass, eintrag)
    lz = eintrag.runtime_data
    assert lz.datenbank.messungen_lesen() == []
    assert lz.einstellungen.wert.tarif_down == 50
    assert not lz.einstellungen.plan.an


async def test_uebernahme_nur_einmal(
    hass: HomeAssistant, hass_storage, fritz, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id, CONF_UEBERNOMMEN: True},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    _altbestand(eigener_ordner, hass_storage, alt)
    await _laden(hass, eintrag)
    assert eintrag.runtime_data.datenbank.messungen_lesen() == []
    assert eintrag.runtime_data.einstellungen.wert.tarif_down is None


async def test_ohne_altbestand(hass: HomeAssistant, eintrag, box, pi, eigener_ordner) -> None:
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED
    assert eintrag.data[CONF_UEBERNOMMEN] is True
    assert not (eigener_ordner / "netzwerk").exists()


async def test_alte_noch_aktiv_heimnetz_startet_nicht(
    hass: HomeAssistant, hass_storage, eintrag, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass)
    _altbestand(eigener_ordner, hass_storage, alt)
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.SETUP_ERROR
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_ALT_AKTIV)
    assert not (eigener_ordner / "heimnetz" / "heimnetz.db").exists()
    assert CONF_UEBERNOMMEN not in eintrag.data
    box.assert_not_called()  # die Box wurde nicht gefragt
    # alte deaktiviert → neu laden: läuft, Hinweis weg, Daten da
    await hass.config_entries.async_set_disabled_by(alt.entry_id, ConfigEntryDisabler.USER)
    await hass.async_block_till_done()
    assert await hass.config_entries.async_reload(eintrag.entry_id)
    await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.LOADED
    assert not ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_ALT_AKTIV)
    assert eintrag.runtime_data.datenbank.messungen_lesen() == [MESSUNG]


async def test_tickets_warten_solange_die_alte_aktiv_ist(
    hass: HomeAssistant, hass_storage, hass_ws_client, eigener_ordner
) -> None:
    _alt(hass)
    _speicher(hass_storage, "netzwerk.meldungen", ALTE_TICKETS)
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/meldungen"})
    assert (await client.receive_json())["result"] == []
    assert "heimnetz.meldungen" not in hass_storage


async def test_einrichtung_bricht_ab_solange_die_alte_aktiv_ist(hass: HomeAssistant, fritz) -> None:
    _alt(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "alt_aktiv"


async def test_einrichtung_uebernimmt_optionen_der_alten(
    hass: HomeAssistant, fritz, box, pi
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    with patch(f"custom_components.{DOMAIN}.box.Box.pruefen"):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_FRITZ_EINTRAG: fritz.entry_id}
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Heimnetz"
    assert result["data"] == {CONF_FRITZ_EINTRAG: fritz.entry_id, CONF_ALT_EINTRAG: alt.entry_id}
    assert result["options"] == {CONF_OPENCELLID: "schluessel"}


async def test_alte_wieder_aktiv_heimnetz_haelt_an(
    hass: HomeAssistant, hass_storage, fritz, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED
    await hass.config_entries.async_set_disabled_by(alt.entry_id, None)
    alt.mock_state(
        hass, ConfigEntryState.LOADED
    )  # die alte Integration gibt es im Test nicht: lädt „wie echt“
    await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.SETUP_ERROR
    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_ALT_AKTIV)


async def test_ignorierte_alte_sperrt_nicht(hass: HomeAssistant, eintrag, box, pi) -> None:
    _alt(hass, source=config_entries.SOURCE_IGNORE)
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED


async def test_kaputte_alte_datenbank_weiter_ohne(
    hass: HomeAssistant, hass_storage, fritz, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    (eigener_ordner / "netzwerk").mkdir()
    (eigener_ordner / "netzwerk" / "netzwerk.db").write_bytes(b"keine Datenbank" * 100)
    (eigener_ordner / "netzwerk" / "meldungen").mkdir()
    (eigener_ordner / "netzwerk" / "meldungen" / "FE-0006-1.jpg").write_bytes(b"bild")
    _speicher(hass_storage, f"netzwerk.{alt.entry_id}", {"tarif_down": 150})
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id, CONF_ALT_EINTRAG: alt.entry_id},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.LOADED
    assert eintrag.runtime_data.datenbank.messungen_lesen() == []
    assert eintrag.runtime_data.einstellungen.wert.tarif_down == 150
    assert (eigener_ordner / "netzwerk" / "netzwerk.db").read_bytes() == b"keine Datenbank" * 100
    # die Bilder der Tickets kommen trotzdem mit
    assert (eigener_ordner / "heimnetz" / "meldungen" / "FE-0006-1.jpg").read_bytes() == b"bild"


async def test_platte_voll_beim_kopieren_der_datenbank_spaeter_noch_einmal(
    hass: HomeAssistant, hass_storage, fritz, box, pi, eigener_ordner
) -> None:
    """Ein vorübergehender Fehler von SQLite (Platte voll) zählt nicht als kaputte Datenbank: neuer Versuch."""
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    _altbestand(eigener_ordner, hass_storage, alt)
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id, CONF_ALT_EINTRAG: alt.entry_id},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    voll = sqlite3.OperationalError("database or disk is full")
    voll.sqlite_errorname = "SQLITE_FULL"
    with patch("custom_components.heimnetz.uebernahme._datenbank_kopieren", side_effect=voll):
        await _laden(hass, eintrag)
    assert eintrag.state is ConfigEntryState.SETUP_RETRY
    assert CONF_UEBERNOMMEN not in eintrag.data
    assert not (eigener_ordner / "heimnetz" / "heimnetz.db").exists()


async def test_alte_datenbank_bleibt_unveraendert(
    hass: HomeAssistant, hass_storage, fritz, box, pi, eigener_ordner
) -> None:
    alt = _alt(hass, disabled_by=ConfigEntryDisabler.USER)
    _altbestand(eigener_ordner, hass_storage, alt)
    vorher = {
        p.name: p.read_bytes() for p in (eigener_ordner / "netzwerk").iterdir() if p.is_file()
    }
    eintrag = MockConfigEntry(
        domain=DOMAIN,
        title="Heimnetz",
        data={CONF_FRITZ_EINTRAG: fritz.entry_id},
        unique_id=fritz.entry_id,
    )
    eintrag.add_to_hass(hass)
    await _laden(hass, eintrag)
    nachher = {
        p.name: p.read_bytes() for p in (eigener_ordner / "netzwerk").iterdir() if p.is_file()
    }
    assert nachher == vorher
    assert not list((eigener_ordner / "heimnetz").rglob("*.uebernahme"))
