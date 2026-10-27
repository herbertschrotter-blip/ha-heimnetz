"""WU-0009: Reiter „Internet“, ⚙ › Zugang und die Entitäten je Zugangsart gegen Home Assistant (Box ersetzt)."""

import json
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.heimnetz.const import CONF_MODEM_KENNWORT, CONF_OPENCELLID, DOMAIN
from custom_components.heimnetz.diagnostics import async_get_config_entry_diagnostics
from custom_components.heimnetz.logik import leitung as ln
from custom_components.heimnetz.logik import zugang as zg
from tests.integration.conftest import box_daten

KENNWORT = "Modem-Geheim-123"
DSL_BOX = {
    "zugang": zg.Meldung(
        zugangsart="DSL",
        link="Up",
        mobil_dienst=True,
        mobil_an=True,
        dsl_dienst=True,
        dsl_status="Up",
    ),
    "dsl": ln.Dsl(
        t=0.0, status="Up", sync_down=108_396, sync_up=38_189, marge_down=52, marge_up=79
    ),
}


def _zustand(hass, eintrag, schluessel):
    eid = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{eintrag.entry_id}_{schluessel}"
    )
    return hass.states.get(eid).state if eid else None


async def _laden(hass, eintrag):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()


async def _frage(client, **msg):
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def test_internet_mobilfunk_und_wechsel_auf_dsl(
    hass: HomeAssistant, eintrag, box, pi, hass_ws_client
):
    await _laden(hass, eintrag)
    assert _zustand(hass, eintrag, "zugang") == "mobilfunk"
    assert _zustand(hass, eintrag, "dsl_sync_down") is None, "ohne DSL keine DSL-Entitäten"
    client = await hass_ws_client(hass)
    d = (await _frage(client, type="heimnetz/internet"))["result"]
    assert d["zugang"]["titel"] == "Internet über Mobilfunk" and d["mobilfunk"]["verfuegbar"]
    assert d["dsl"] is None and d["ersatz"] is None
    u = (await _frage(client, type="heimnetz/uebersicht"))["result"]
    assert u["zugang"]["kopf"] == "FRITZ!Box · Mobilfunk 5G-NSA"

    box.return_value = box_daten(**DSL_BOX)
    await eintrag.runtime_data.abruf.async_refresh()
    await hass.async_block_till_done()
    assert _zustand(hass, eintrag, "zugang") == "dsl"
    assert _zustand(hass, eintrag, "dsl_sync_down") == "108.4"
    assert _zustand(hass, eintrag, "dsl_snr_down") == "5.2"
    d = (await _frage(client, type="heimnetz/internet", tage=7))["result"]
    assert d["dsl"]["bewertung"]["abzeichen"] == "Reserve knapp"
    assert d["ersatz"]["text"] == "Mobilfunk an der FRITZ!Box, springt bei Ausfall ein"
    journal = eintrag.runtime_data.datenbank.journal_lesen(0, art="zugang")
    assert [z.ereignis.text for z in journal] == ["Internetzugang: jetzt DSL (vorher Mobilfunk)"]

    # DSL fällt weg (andere Box): Entitäten bleiben registriert, sind aber nicht verfügbar
    box.return_value = box_daten()
    await eintrag.runtime_data.abruf.async_refresh()
    await hass.async_block_till_done()
    assert _zustand(hass, eintrag, "dsl_sync_down") == "unavailable"


async def test_zugang_nur_fuer_admins(
    hass: HomeAssistant, eintrag, box, pi, hass_ws_client, hass_read_only_access_token
):
    await _laden(hass, eintrag)
    gast = await hass_ws_client(hass, hass_read_only_access_token)
    for msg in (
        {"type": "heimnetz/zugang"},
        {"type": "heimnetz/zugang/setzen", "wahl": "dsl"},
        {"type": "heimnetz/zugang/suchen"},
    ):
        assert (await _frage(gast, **msg))["error"]["code"] == "unauthorized", msg
    assert (await _frage(gast, type="heimnetz/internet"))["success"], "lesen darf jeder"
    assert eintrag.runtime_data.einstellungen.wert.zugang_wahl == "auto"


async def test_zugang_festlegen_kennwort_nie_zurueck(
    hass: HomeAssistant, eintrag, box, pi, hass_ws_client, caplog
):
    caplog.set_level(logging.DEBUG)
    await _laden(hass, eintrag)
    client = await hass_ws_client(hass)
    z = (await _frage(client, type="heimnetz/zugang"))["result"]
    assert z["wahl"] == "auto" and z["belege"] and z["kennwort"] is False
    assert z["adressen"] == ["192.168.0.1", "192.168.1.1", "192.168.8.1"]

    antwort = await _frage(
        client,
        type="heimnetz/zugang/setzen",
        wahl="extern",
        adresse="192.168.8.1",
        kennwort=KENNWORT,
    )
    assert antwort["success"], antwort
    z = antwort["result"]
    assert (z["wahl"], z["adresse"], z["kennwort"], z["quelle"]) == (
        "extern",
        "192.168.8.1",
        True,
        "festgelegt",
    )
    assert z["titel"] == "Internet über Mobilfunk" and z["abweichung"] == "Mobilfunk über FRITZ!Box"
    assert KENNWORT not in json.dumps(antwort)
    assert eintrag.options[CONF_MODEM_KENNWORT] == KENNWORT
    assert _zustand(hass, eintrag, "zugang") == "extern", "Sensor folgt der Wahl gleich"
    d = (await _frage(client, type="heimnetz/internet"))["result"]
    assert (
        d["zugang"]["weg_text"] == "vorgeschaltet über 192.168.8.1 · Beta"
        and d["mobilfunk"] is None
    )

    diagnose = await async_get_config_entry_diagnostics(hass, eintrag)
    assert (
        KENNWORT not in str(diagnose)
        and diagnose["optionen"][CONF_MODEM_KENNWORT] == "**REDACTED**"
    )
    assert diagnose["zugang"]["wahl"] == "extern"
    eigene = [
        r.getMessage() for r in caplog.records if r.name.startswith("custom_components.heimnetz")
    ]
    assert not any(KENNWORT in m for m in eigene), "Heimnetz protokolliert das Kennwort nie"

    # Optionen von Heimnetz (OpenCellID-Schlüssel) ändern: das Kennwort bleibt
    flow = await hass.config_entries.options.async_init(eintrag.entry_id)
    await hass.config_entries.options.async_configure(flow["flow_id"], {CONF_OPENCELLID: "pk.x"})
    assert (
        eintrag.options[CONF_MODEM_KENNWORT] == KENNWORT
        and eintrag.options[CONF_OPENCELLID] == "pk.x"
    )

    falsch = await _frage(client, type="heimnetz/zugang/setzen", adresse="8.8.8.8")
    assert falsch["error"]["code"] == "ungueltig"
    assert eintrag.runtime_data.einstellungen.wert.zugang_adresse == "192.168.8.1"

    weg = await _frage(client, type="heimnetz/zugang/setzen", wahl="auto", kennwort_loeschen=True)
    assert weg["result"]["kennwort"] is False and CONF_MODEM_KENNWORT not in eintrag.options
    assert eintrag.options[CONF_OPENCELLID] == "pk.x"
    assert _zustand(hass, eintrag, "zugang") == "mobilfunk"


async def test_erneut_suchen_liest_im_gemeinsamen_abruf(
    hass: HomeAssistant, eintrag, box, pi, hass_ws_client
):
    await _laden(hass, eintrag)
    vorher = box.call_count
    client = await hass_ws_client(hass)
    antwort = await _frage(client, type="heimnetz/zugang/suchen")
    assert antwort["success"] and antwort["result"]["gelesen"]
    assert box.call_count == vorher + 1
    assert box.call_args.args[4] is True, "Zugang diesmal mitlesen"
    assert eintrag.runtime_data.abruf.zugang_neu is False
    await _frage(
        client, type="heimnetz/zugang/suchen"
    )  # gleich noch einmal: die Box nicht erneut fragen
    assert box.call_count == vorher + 1


async def test_diagnose_nimmt_das_hinterlegte_kennwort(
    hass: HomeAssistant, eintrag, box, pi, hass_ws_client
):
    """🔬 Diagnose ohne eingetipptes Kennwort: das unter 🌐 Zugang hinterlegte, nur für genau diese Adresse."""
    from unittest.mock import patch

    await _laden(hass, eintrag)
    client = await hass_ws_client(hass)
    await _frage(
        client,
        type="heimnetz/zugang/setzen",
        wahl="extern",
        adresse="192.168.8.1",
        kennwort=KENNWORT,
    )
    leer = {"modell": "", "abfragen": [], "summen": {}, "befund": None, "daten": {}}
    with patch("custom_components.heimnetz.modem.abfragen", return_value=leer) as abfragen:
        await _frage(client, type="heimnetz/modem", adresse="192.168.8.1")
        assert abfragen.call_args.args[2] == KENNWORT
        await _frage(client, type="heimnetz/modem", adresse="192.168.0.1")
        assert abfragen.call_args.args[2] is None, "andere Adresse: nichts mitschicken"
        await _frage(client, type="heimnetz/modem", adresse="192.168.8.1", kennwort="anders")
        assert abfragen.call_args.args[2] == "anders"
