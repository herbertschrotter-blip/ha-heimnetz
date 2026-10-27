"""Vertrag zwischen Integration und Seite: die Antworten der WebSocket-Befehle haben die Form der Vorlage
tests/seite/daten.json, mit der die Seite getestet wird. Neu schreiben: HEIMNETZ_VORLAGE=1 pytest …"""

import json
import os
from datetime import timedelta
from pathlib import Path

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.heimnetz.box import BoxInfo
from custom_components.heimnetz.logik import leitung as ln
from custom_components.heimnetz.logik import zugang as zg
from custom_components.heimnetz.logik.messung import Messung
from custom_components.heimnetz.logik.verlauf import geraete_id
from tests.integration.conftest import box_daten

VORLAGE = Path(__file__).parents[1] / "seite" / "daten.json"
BEFEHLE = {
    "uebersicht": {},
    "speedtest": {"tage": 84, "groesse": "down", "grundlast": "aus", "tag": 0},
    "geraete": {},
    "mobilfunk": {"tage": 1},
    "wlan": {},
    "verbrauch": {"tage": 30},
    "protokoll": {"art": "journal"},
    "einstellungen": {},
    "einrichtung": {},
    "internet": {"tage": 1},
    "zugang": {},
}
# WU-0009: Reiter „Internet“ je Zugangsart – DSL, Glasfaser und Kabel mit erfundenen Werten in der Form der FRITZ!-Doku
ANDERE_ZUGAENGE = {
    "internet_dsl": {
        "info": BoxInfo("FRITZ!Box 7590 AX", "8.03", 3600, 0.0),
        "zugang": zg.Meldung(
            zugangsart="DSL",
            link="Up",
            art_avm="DSL",
            down_bit=108_396_000,
            up_bit=38_189_000,
            mobil_dienst=True,
            mobil_an=True,
            dsl_dienst=True,
            dsl_status="Up",
            wan_netz="oeffentlich",
        ),
        "dsl": ln.Dsl(
            t=0.0,
            status="Up",
            sync_down=108_396,
            sync_up=38_189,
            max_down=124_620,
            max_up=41_012,
            marge_down=52,
            marge_up=79,
            daempfung_down=140,
            daempfung_up=90,
            modulation="VDSL",
            profil="35b",
            crc=120,
            fec=18_400,
        ),
    },
    "internet_glasfaser": {
        "info": BoxInfo("FRITZ!Box 5590 Fiber", "8.03", 3600, 0.0),
        "zugang": zg.Meldung(
            zugangsart="X_AVM-DE_Fiber",
            link="Up",
            down_bit=1_000_000_000,
            up_bit=500_000_000,
            faser_dienst=True,
            faser_modus="GPON",
        ),
        "faser": ln.Faser(
            t=0.0,
            modus="GPON",
            rx=-19_400,
            rx_min=-28_000,
            rx_max=-8_000,
            tx=2_100,
            tx_min=500,
            tx_max=5_000,
            fehler_rx=0,
            resyncs=1,
            minuten=30_240,
        ),
    },
    "internet_kabel": {
        "info": BoxInfo("FRITZ!Box 6690 Cable", "8.03", 3600, 0.0),
        "zugang": zg.Meldung(
            zugangsart="X_AVM-DE_Cable", link="Up", down_bit=1_000_000_000, up_bit=50_000_000
        ),
    },
}


def form(wert):
    """Form statt Inhalt: Schlüssel von Objekten, Art von Werten (Listen: Form des ersten Elements)."""
    if isinstance(wert, dict):
        return {k: form(v) for k, v in sorted(wert.items())}
    if isinstance(wert, list):
        return [form(wert[0])] if wert else []
    if isinstance(wert, bool) or wert is None:
        return type(wert).__name__
    return "zahl" if isinstance(wert, int | float) else type(wert).__name__


def _zusammenfuehren(a, b):
    """Felder, die mal None und mal ein Wert sind, gelten als gleich (optional)."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_zusammenfuehren(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return not a or not b or _zusammenfuehren(a[0], b[0])
    return a == b or "NoneType" in (a, b)


async def test_antworten_haben_die_form_der_vorlage(
    hass: HomeAssistant, eintrag, box, pi, fritz, hass_ws_client
):
    for k in ("gb_received", "gb_sent"):
        er.async_get(hass).async_get_or_create("sensor", "fritz", f"box-{k}", config_entry=fritz)
    ookla = MockConfigEntry(domain="ookla_speedtest", data={"manual": True, "scan_interval": 240})
    ookla.add_to_hass(hass)
    ookla.mock_state(hass, ConfigEntryState.LOADED)
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    await eintrag.runtime_data.einstellungen.async_setzen({"tarif_down": 150, "tarif_up": 30})
    db = eintrag.runtime_data.datenbank
    jetzt = dt_util.utcnow()
    await hass.async_add_executor_job(
        db.messungen_schreiben,
        [
            Messung(
                (jetzt - timedelta(hours=3 * h)).timestamp(),
                120.0 - h,
                30.0,
                21.0,
                "Wien – A1",
                2.0 + h,
                0.2,
            )
            for h in range(12)
        ],
    )
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/messplan/setzen", "an": True, "takt_h": 4})
    assert (await client.receive_json())["success"]
    antworten = {}
    for befehl, parameter in BEFEHLE.items():
        await client.send_json_auto_id({"type": f"heimnetz/{befehl}", **parameter})
        antwort = await client.receive_json()
        assert antwort["success"], (befehl, antwort)
        antworten[befehl] = antwort["result"]
    await client.send_json_auto_id(
        {
            "type": "heimnetz/geraet",
            "geraet": geraete_id("00:11:22:33:44:01", eintrag.runtime_data.salz),
            "tage": 7,
        }
    )
    antworten["geraet"] = (await client.receive_json())["result"]
    jetzt_ort = dt_util.now()  # die neueste Messung liegt in dieser Stunde
    await client.send_json_auto_id(
        {
            "type": "heimnetz/speedtest/kachel",
            "tage": 84,
            "tag": jetzt_ort.weekday(),
            "stunde": jetzt_ort.hour,
        }
    )
    antworten["speedtest/kachel"] = (await client.receive_json())["result"]
    assert antworten["speedtest/kachel"]["messungen"], "Vorlage braucht mindestens eine Messung"
    assert (
        antworten["internet"]["zugang"]["art"] == "mobilfunk" and antworten["internet"]["mobilfunk"]
    )
    for name, teile in ANDERE_ZUGAENGE.items():
        box.return_value = box_daten(
            mobil=None if name != "internet_dsl" else box_daten().mobil,
            **{k: v for k, v in teile.items()},
        )
        await eintrag.runtime_data.abruf.async_refresh()
        await hass.async_block_till_done()
        await client.send_json_auto_id({"type": "heimnetz/internet", "tage": 1})
        antwort = await client.receive_json()
        assert antwort["success"], (name, antwort)
        antworten[name] = antwort["result"]
    assert antworten["internet_dsl"]["dsl"]["bewertung"]["abzeichen"] == "Reserve knapp"
    assert antworten["internet_dsl"]["ersatz"]["text"]
    assert antworten["internet_glasfaser"]["glasfaser"]["rx"] == -19.4
    assert antworten["internet_kabel"]["kabel"]["down_mbit"] == 1000
    if os.environ.get("HEIMNETZ_VORLAGE"):
        VORLAGE.write_text(
            json.dumps(antworten, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    vorlage = json.loads(VORLAGE.read_text(encoding="utf-8"))
    assert vorlage.keys() == antworten.keys()
    for befehl in antworten:
        assert _zusammenfuehren(form(vorlage[befehl]), form(antworten[befehl])), befehl
