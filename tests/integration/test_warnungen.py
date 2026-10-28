"""WU-0010: eigene Arten und Warnungen über die WebSocket-Befehle (nur Admins), Versand über einen gemockten
notify-Dienst, Ereignis `heimnetz_warnung`, Journal, Testnachricht, Fehler beim Versand ohne Absturz."""

from dataclasses import replace

import pytest
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import async_capture_events, async_mock_service

from custom_components.heimnetz.logik import geraete as gr
from custom_components.heimnetz.logik.verlauf import geraete_id
from custom_components.heimnetz.warnungen import EREIGNIS
from tests.integration.conftest import box_daten
from tests.logik.daten import HOSTLISTE

PI, FERNSEHER = "00:11:22:33:44:01", "00:11:22:33:44:02"


@pytest.fixture
async def geladen(hass: HomeAssistant, eintrag, box, pi):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    return eintrag


async def _frage(client, **msg):
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def test_nicht_admin_abgelehnt(hass, geladen, hass_ws_client, hass_read_only_access_token):
    gast = await hass_ws_client(hass, hass_read_only_access_token)
    kennung = geraete_id(PI, geladen.runtime_data.salz)
    for msg in (
        {"type": "heimnetz/arten"},
        {"type": "heimnetz/art/neu", "name": "Baustelle"},
        {"type": "heimnetz/art/aendern", "art": "eigen:1", "name": "x"},
        {"type": "heimnetz/art/loeschen", "art": "eigen:1"},
        {"type": "heimnetz/warnungen"},
        {"type": "heimnetz/warnungen/setzen", "verzoegerung": 2},
        {"type": "heimnetz/warnungen/geraet", "geraet": kennung, "wert": "immer"},
        {"type": "heimnetz/warnungen/test"},
    ):
        assert (await _frage(gast, **msg))["error"]["code"] == "unauthorized", msg
    assert geladen.runtime_data.einstellungen.eigene == {}


async def test_eigene_arten_anlegen_zuordnen_umbenennen_loeschen(hass, geladen, hass_ws_client):
    lz = geladen.runtime_data
    client = await hass_ws_client(hass)
    tv = geraete_id(FERNSEHER, lz.salz)
    neu = await _frage(client, type="heimnetz/art/neu", symbol="🏗️", name="Baustelle", geraet=tv)
    assert neu["success"], neu
    k = neu["result"]["neu"]
    assert neu["result"]["eigene"] == [
        {"name": k, "symbol": "🏗️", "titel": "Baustelle", "text": "🏗️ Baustelle", "geraete": 1}
    ]
    doppelt = await _frage(client, type="heimnetz/art/neu", name="baustelle")
    assert (
        doppelt["error"]["code"] == "ungueltig" and "gibt es schon" in doppelt["error"]["message"]
    )
    # gilt wie eine feste Art: Gruppe „nach Art“, Auswahl im Gerätefenster, Warnungen
    d = (await _frage(client, type="heimnetz/geraete"))["result"]
    assert {"name": k, "text": "🏗️ Baustelle", "online": 1, "gesamt": 1} in d["gruppen_art"]
    g = (await _frage(client, type="heimnetz/geraet", geraet=tv))["result"]
    assert (g["kat"], g["art_selbst"]) == (k, True) and g["kategorien"][-1]["name"] == k
    an = await _frage(client, type="heimnetz/warnungen/setzen", art=k, an=True)
    zeile = next(x for x in an["result"]["arten"] if x["name"] == k)
    assert zeile == {"name": k, "text": "🏗️ Baustelle", "an": True, "geraete": 1, "hinweis": None}
    um = await _frage(
        client, type="heimnetz/art/aendern", art=k, symbol="🚧", name="Baustelle Nord"
    )
    assert um["result"]["eigene"][0]["text"] == "🚧 Baustelle Nord"
    # gespeichert: übersteht das Neuladen
    assert await hass.config_entries.async_reload(geladen.entry_id)
    await hass.async_block_till_done()
    lz = geladen.runtime_data
    assert lz.einstellungen.eigene[k].name == "Baustelle Nord" and lz.einstellungen.arten[tv] == k
    assert lz.einstellungen.warnungen.art_an(k)
    weg = await _frage(client, type="heimnetz/art/loeschen", art=k)
    assert weg["result"]["zurueck"] == 1 and weg["result"]["eigene"] == []
    assert tv not in lz.einstellungen.arten and k not in lz.einstellungen.warnungen.arten
    g = (await _frage(client, type="heimnetz/geraet", geraet=tv))["result"]
    assert g["kat"] != k and not g["art_selbst"], "wieder erkannt"
    fehlt = await _frage(client, type="heimnetz/art/loeschen", art=k)
    assert fehlt["error"]["code"] == "ungueltig"
    zuordnen = await _frage(client, type="heimnetz/geraet/art", geraet=tv, art=k)
    assert zuordnen["error"]["code"] == "ungueltig", "gelöschte Art nicht mehr wählbar"


async def test_einstellungen_und_ausnahme(hass, geladen, hass_ws_client):
    lz = geladen.runtime_data
    client = await hass_ws_client(hass)
    w = (await _frage(client, type="heimnetz/warnungen"))["result"]
    assert (w["ziel"], w["verzoegerung"], w["wieder"], w["neu"], w["internet"]) == (
        "keine",
        5,
        True,
        True,
        True,
    )
    an = {x["name"]: x["an"] for x in w["arten"]}
    assert [k for k, v in an.items() if v] == ["netz", "smart", "haushalt", "kamera"]
    assert next(x for x in w["arten"] if x["name"] == "mobil")["hinweis"].startswith("ausgenommen")
    assert w["ziele"][-1]["name"] == "keine" and w["gesamt"] == 5
    falsch = await _frage(client, type="heimnetz/warnungen/setzen", ziel="mobile_app_fehlt")
    assert falsch["error"]["code"] == "ungueltig"
    async_mock_service(hass, "notify", "mobile_app_handy")
    w = (
        await _frage(
            client,
            type="heimnetz/warnungen/setzen",
            ziel="mobile_app_handy",
            verzoegerung=15,
            sprache="en",
        )
    )["result"]
    assert (w["ziel"], w["verzoegerung"]) == ("mobile_app_handy", 15)
    assert [z["name"] for z in w["ziele"]] == ["mobile_app_handy", "alle", "keine"]
    assert lz.einstellungen.warnungen.sprache == "en", "Nachrichten in der Sprache der Seite"
    assert (await _frage(client, type="heimnetz/warnungen/setzen", verzoegerung=3))["error"][
        "code"
    ] == "ungueltig"
    kennung = geraete_id(PI, lz.salz)
    g = (await _frage(client, type="heimnetz/warnungen/geraet", geraet=kennung, wert="nie"))[
        "result"
    ]
    assert g["warnen"]["wert"] == "nie"
    w = (await _frage(client, type="heimnetz/warnungen"))["result"]
    assert w["ausnahmen"] == [{"id": kennung, "name": "Pi", "wert": "nie"}]
    g = (await _frage(client, type="heimnetz/warnungen/geraet", geraet=kennung, wert="gruppe"))[
        "result"
    ]
    assert g["warnen"]["wert"] == "gruppe" and lz.einstellungen.warnungen.geraete == {}
    unbekannt = await _frage(
        client, type="heimnetz/warnungen/geraet", geraet="x" * 16, wert="immer"
    )
    assert unbekannt["error"]["code"] == "not_found"


async def test_testnachricht(hass, geladen, hass_ws_client):
    client = await hass_ws_client(hass)
    ereignisse = async_capture_events(hass, EREIGNIS)
    nur = await _frage(client, type="heimnetz/warnungen/test")
    assert nur["result"] == {"dienste": []}, "keine Nachricht – nur Ereignis"
    aufrufe = async_mock_service(hass, "notify", "mobile_app_handy")
    async_mock_service(hass, "notify", "mobile_app_tablet")
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="alle")
    alle = await _frage(client, type="heimnetz/warnungen/test")
    assert alle["result"] == {"dienste": ["mobile_app_handy", "mobile_app_tablet"]}
    assert aufrufe[0].data == {
        "title": "Heimnetz",
        "message": "Testnachricht von Heimnetz – so kommen Warnungen an.",
    }
    await hass.async_block_till_done()
    assert [e.data["art"] for e in ereignisse] == ["test", "test"]

    async def kaputt(_call: ServiceCall) -> None:
        raise HomeAssistantError("Push-Dienst nicht erreichbar")

    hass.services.async_register("notify", "mobile_app_kaputt", kaputt)
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="mobile_app_kaputt")
    fehler = await _frage(client, type="heimnetz/warnungen/test")
    assert fehler["error"]["code"] == "nicht_zugestellt"
    assert "Push-Dienst nicht erreichbar" in fehler["error"]["message"]


def _weiter(stand, minuten, **aktiv):
    """Stand `minuten` später; aktiv={mac: bool} schaltet Geräte."""
    geraete = {mac: replace(g, aktiv=aktiv.get(mac, g.aktiv)) for mac, g in stand.geraete.items()}
    return replace(stand, zeit=stand.zeit + minuten * 60, geraete=geraete, ereignisse=())


async def test_versand_offline_online_ereignis_journal(hass, geladen, hass_ws_client):
    lz = geladen.runtime_data
    client = await hass_ws_client(hass)
    aufrufe = async_mock_service(hass, "notify", "mobile_app_handy")
    ereignisse = async_capture_events(hass, EREIGNIS)
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="mobile_app_handy", verzoegerung=2)
    await _frage(
        client, type="heimnetz/warnungen/geraet", geraet=geraete_id(PI, lz.salz), wert="immer"
    )
    s0 = lz.abruf.data  # Grundzustand hat der erste Abruf übernommen
    assert lz.warnungen.waechter.grundzustand
    s1 = _weiter(s0, 1, **{PI: False})
    assert await lz.warnungen.abruf(s1) == []
    journal = await lz.warnungen.abruf(_weiter(s1, 3))
    await hass.async_block_till_done()
    assert [e.art for e in journal] == ["warnung"] and journal[0].mac == PI
    assert journal[0].text.startswith("🔔 Warnung: Pi ist seit 3 min offline")
    assert len(aufrufe) == 1 and aufrufe[0].data["title"] == "Heimnetz"
    assert aufrufe[0].data["message"].startswith("Pi ist seit 3 min offline (zuletzt ")
    d = ereignisse[0].data
    assert (d["art"], d["geraet"], d["ip"], d["verbindung"], d["dauer"]) == (
        "offline",
        "Pi",
        "192.168.170.60",
        "LAN",
        180,
    )
    assert "00:11:22" not in str(d)
    await lz.warnungen.abruf(_weiter(s1, 4))  # noch weg: nichts mehr
    await lz.warnungen.abruf(_weiter(s1, 10, **{PI: True}))
    await hass.async_block_till_done()
    assert [e.data["art"] for e in ereignisse] == ["offline", "online"]
    assert ereignisse[1].data["dauer"] == 600 and "war 10 min weg" in aufrufe[1].data["message"]


async def test_box_weg_dann_internet_meldung_und_versandfehler_ins_journal(
    hass, geladen, hass_ws_client
):
    lz = geladen.runtime_data
    client = await hass_ws_client(hass)
    ereignisse = async_capture_events(hass, EREIGNIS)

    async def kaputt(_call: ServiceCall) -> None:
        raise HomeAssistantError("abgelehnt")

    hass.services.async_register("notify", "mobile_app_kaputt", kaputt)
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="mobile_app_kaputt", verzoegerung=2)
    s0 = lz.abruf.data
    weg = replace(
        _weiter(s0, 1), box_erreichbar=False, geraete={}, pi=replace(s0.pi, internet=False)
    )
    for i in range(1, 6):
        assert await lz.warnungen.abruf(replace(weg, zeit=s0.zeit + i * 60)) == []
    journal = await lz.warnungen.abruf(_weiter(s0, 7))
    await hass.async_block_till_done()
    assert [e.data["art"] for e in ereignisse] == ["internet"]
    assert "FRITZ!Box war 6 min nicht erreichbar" in ereignisse[0].data["nachricht"]
    assert journal[0].text.startswith("🔔 Warnung: FRITZ!Box war 6 min")
    fehler = [
        z.ereignis for z in lz.abruf._ausstehend_journal if z.ereignis.art == "warnung_fehler"
    ]
    assert fehler and "notify.mobile_app_kaputt" in fehler[0].text and "abgelehnt" in fehler[0].text


async def test_neues_geraet_im_abruf(hass, geladen, box, hass_ws_client):
    lz = geladen.runtime_data
    aufrufe = async_mock_service(hass, "notify", "mobile_app_handy")
    client = await hass_ws_client(hass)
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="alle")
    ereignisse = async_capture_events(hass, EREIGNIS)
    geraete = gr.aus_hostliste(HOSTLISTE)
    fremd = replace(
        geraete["00:11:22:33:44:04"], mac="00:11:22:33:44:99", name="Fremd", ip="192.168.170.99"
    )
    box.return_value = box_daten(geraete={**geraete, fremd.mac: fremd})
    await lz.abruf.async_refresh()
    await hass.async_block_till_done()
    assert [(e.data["art"], e.data["geraet"]) for e in ereignisse] == [("neu", "Fremd")]
    assert "Neues Gerät im Heimnetz: Fremd, IP 192.168.170.99" in aufrufe[0].data["message"]
    zeilen = await hass.async_add_executor_job(lz.datenbank.journal_lesen, 0.0)
    assert any(z.ereignis.art == "warnung" and z.ereignis.mac == fremd.mac for z in zeilen)
    await lz.abruf.async_refresh()  # noch einmal: keine zweite Meldung
    await hass.async_block_till_done()
    assert len(ereignisse) == 1


async def test_diagnose_ohne_namen(hass, geladen, hass_ws_client):
    from custom_components.heimnetz.diagnostics import async_get_config_entry_diagnostics

    lz = geladen.runtime_data
    async_mock_service(hass, "notify", "mobile_app_handy_von_herbert")
    client = await hass_ws_client(hass)
    await _frage(client, type="heimnetz/art/neu", symbol="🏗️", name="Geheimprojekt")
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="mobile_app_handy_von_herbert")
    d = await async_get_config_entry_diagnostics(hass, geladen)
    w = d["laufzeit"]["warnungen"]
    assert (w["ziel"], w["eigene_arten"], w["grundzustand"]) == ("companion_app", 1, True)
    assert "Geheimprojekt" not in str(d) and "herbert" not in str(d)
    assert lz.warnungen is not None


async def test_fehlender_dienst_sperrt_die_schalter_nicht(hass, geladen, hass_ws_client):
    """Verschwindet der gewählte notify-Dienst (App entfernt), lassen sich die anderen Werte weiter ändern."""
    client = await hass_ws_client(hass)
    async_mock_service(hass, "notify", "mobile_app_handy")
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="mobile_app_handy")
    hass.services.async_remove("notify", "mobile_app_handy")
    w = await _frage(client, type="heimnetz/warnungen/setzen", verzoegerung=15)
    assert w["success"], w
    assert w["result"]["ziel_fehlt"] and w["result"]["ziele"][0]["text"].endswith("fehlt")
    await _frage(client, type="heimnetz/warnungen/setzen", ziel="alle")
    keine = await _frage(client, type="heimnetz/warnungen/test")
    assert "keine Companion App eingerichtet" in keine["error"]["message"]


async def test_bekannt_aus_journal_und_gedaechtnis(hass, geladen, box):
    """Geräte mit Verlauf im Journal (auch ohne Eintrag im Gedächtnis) gelten nach dem Neuladen nicht als neu; die
    Menge der bekannten wird im Gedächtnis gespeichert."""
    from custom_components.heimnetz.logik.ereignis import INFO, Ereignis
    from custom_components.heimnetz.speicher import Journalzeile

    lz = geladen.runtime_data
    alt = "00:11:22:33:44:77"
    await hass.async_add_executor_job(
        lz.datenbank.abruf_schreiben,
        [Journalzeile(1.0, Ereignis("offline", INFO, "Alt ist offline", alt))],
        [],
        None,
        1.0,
    )
    assert set(gr.aus_hostliste(HOSTLISTE)) <= set(lz.abruf.gedaechtnis.bekannt)
    assert await hass.config_entries.async_reload(geladen.entry_id)
    await hass.async_block_till_done()
    lz = geladen.runtime_data
    assert alt in lz.warnungen.waechter.bekannt
    ereignisse = async_capture_events(hass, EREIGNIS)
    geraete = gr.aus_hostliste(HOSTLISTE)
    wieder = replace(geraete["00:11:22:33:44:04"], mac=alt, name="Alt")
    box.return_value = box_daten(geraete={**geraete, alt: wieder})
    await lz.abruf.async_refresh()
    await hass.async_block_till_done()
    assert ereignisse == [], "aus dem Journal bekannt: nicht neu"


async def test_ueberlappende_abrufe_und_gleichzeitiges_speichern(hass, geladen):
    import asyncio

    lz = geladen.runtime_data
    stand = _weiter(lz.abruf.data, 1)
    await asyncio.gather(lz.warnungen.abruf(stand), lz.warnungen.abruf(stand))
    assert lz.warnungen._letzter == stand.zeit
    assert await lz.warnungen.abruf(_weiter(lz.abruf.data, 0)) == [], "älterer Abruf: kein Schritt"
    a, b = geraete_id(PI, lz.salz), geraete_id(FERNSEHER, lz.salz)
    await asyncio.gather(
        lz.einstellungen.async_warnung_geraet(a, "immer"),
        lz.einstellungen.async_warnung_geraet(b, "nie"),
    )
    assert lz.einstellungen.warnungen.geraete == {a: "immer", b: "nie"}, (
        "keine Änderung geht verloren"
    )


async def test_ausnahme_fuer_unbekanntes_geraet_zuruecksetzen(hass, geladen, hass_ws_client):
    lz = geladen.runtime_data
    weg = "f" * 16
    await lz.einstellungen.async_warnung_geraet(weg, "nie")
    client = await hass_ws_client(hass)
    antwort = await _frage(client, type="heimnetz/warnungen/geraet", geraet=weg, wert="gruppe")
    assert antwort["success"] and antwort["result"] is None
    assert lz.einstellungen.warnungen.geraete == {}
