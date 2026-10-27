"""WebSocket-Befehle der Seite: fertige Daten je Reiter, Einstellungen (Admin, Prüfung, Übernahme aus dem Altbestand)."""

from datetime import date, timedelta

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.heimnetz.logik.messung import Messung
from custom_components.heimnetz.logik.verlauf import geraete_id


@pytest.fixture
async def geladen(hass: HomeAssistant, eintrag, box, pi):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    await geladen_tarif(hass, eintrag)
    return eintrag


async def geladen_tarif(hass, eintrag):
    await eintrag.runtime_data.einstellungen.async_setzen(
        {"tarif_down": 150, "tarif_up": 30, "ab": "2026-09-21"}
    )


async def _frage(hass_ws_client, hass, **msg):
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def test_uebersicht(hass, geladen, hass_ws_client):
    antwort = await _frage(hass_ws_client, hass, type="heimnetz/uebersicht")
    assert antwort["success"], antwort
    d = antwort["result"]
    assert d["gesamt"] == "kritisch" and d["box_erreichbar"]
    assert d["geraete"] == {
        "online": 5,
        "bekannt": 5,
        "neu": 0,
        "wackelt": 0,
    }  # erster Abruf: „Erfassung gestartet“
    assert [p["name"] for p in d["pruefungen"]][:3] == [
        "Pi → FRITZ!Box",
        "Pi → Internet",
        "Namensauflösung (DNS)",
    ]
    assert d["empfang"]["rsrp_anker"] == -100 and d["internet"]["technik"] == "5G-NSA"
    assert all(b["stufe"] in ("kritisch", "warnung", "info") for b in d["befunde"])
    assert "00:11:22" not in str(d)  # keine Hardware-Adressen


async def test_speedtest(hass, geladen, hass_ws_client):
    db = geladen.runtime_data.datenbank
    jetzt = dt_util.utcnow()
    await hass.async_add_executor_job(
        db.messungen_schreiben,
        [
            Messung(
                (jetzt - timedelta(hours=h)).timestamp(),
                100.0 + h,
                30.0,
                20.0,
                "Wien",
                1.0 if h else 40.0,
                0.1,
            )
            for h in range(5)
        ],
    )
    antwort = await _frage(
        hass_ws_client, hass, type="heimnetz/speedtest", tage=7, groesse="down", grundlast="aus"
    )
    d = antwort["result"]
    assert (d["gesamt"], d["belastet"], d["anzahl"], d["tarif"], d["schwelle"]) == (
        5,
        1,
        4,
        150.0,
        15.0,
    )
    assert len(d["raster"]) == 7 and len(d["raster"][0]) == 24
    assert d["messungen"][0]["belastet"] and d["messungen"][0]["gewicht"] == 0
    assert d["server"] == [{"name": "Wien", "anzahl": 5}] and d["einheit"] == "Mbit/s"
    falsch = await _frage(hass_ws_client, hass, type="heimnetz/speedtest", tage=3)
    assert not falsch["success"]
    assert d["verlauf"] is None and d["tage_liste"][0]["anzahl"] >= 1
    # WU-0004: Tagesverlauf für einen Wochentag oder ein Datum
    erster = date.fromisoformat(d["tage_liste"][0]["datum"]).weekday()
    v = (await _frage(hass_ws_client, hass, type="heimnetz/speedtest", tag=erster))["result"][
        "verlauf"
    ]
    assert v["tag"] == erster and len(v["stunden"]) == 24
    assert sum(s["anzahl"] for s in v["stunden"]) >= d["tage_liste"][0]["anzahl"]
    tag = (
        await _frage(
            hass_ws_client, hass, type="heimnetz/speedtest", datum=d["tage_liste"][0]["datum"]
        )
    )["result"]["verlauf"]
    assert tag["datum"] == d["tage_liste"][0]["datum"] and tag["tag"] is None
    # AN-0005: Messungen hinter einer Kachel
    neu = dt_util.as_local(dt_util.utc_from_timestamp(d["letzte"]["t"]))
    k = (
        await _frage(
            hass_ws_client,
            hass,
            type="heimnetz/speedtest/kachel",
            tage=7,
            tag=neu.weekday(),
            stunde=neu.hour,
        )
    )["result"]
    assert k["messungen"][0]["t"] == d["letzte"]["t"] and k["einheit"] == "Mbit/s"
    assert k["anzahl"] == sum(1 for m in k["messungen"] if m["gewicht"] > 0)
    assert not (
        await _frage(hass_ws_client, hass, type="heimnetz/speedtest/kachel", tag=1, stunde=24)
    )["success"]
    for falsch in ({"tag": 7}, {"datum": "kein Datum"}):
        assert not (await _frage(hass_ws_client, hass, type="heimnetz/speedtest", **falsch))[
            "success"
        ]


async def test_geraete_und_geraet(hass, geladen, hass_ws_client):
    d = (await _frage(hass_ws_client, hass, type="heimnetz/geraete"))["result"]
    assert d["online"] == 5 and all(len(g["streifen"]) == 48 for g in d["geraete"])
    # AN-0001: Gruppen nach Verbindung (Band aus der WLAN-Liste der Box), gezählt von der Integration
    assert sum(gr_["gesamt"] for gr_ in d["gruppen"]) == len(d["geraete"])
    assert {g["verbindung"] for g in d["geraete"]} == {gr_["name"] for gr_ in d["gruppen"]}
    assert any(g["band"] for g in d["geraete"])
    assert "00:11" not in str(d)
    kennung = geraete_id("00:11:22:33:44:01", geladen.runtime_data.salz)
    g = (await _frage(hass_ws_client, hass, type="heimnetz/geraet", geraet=kennung, tage=3))[
        "result"
    ]
    assert g["name"] == "Pi" and len(g["tage"]) == 3 and g["quelle"] == "unbekannt"
    fehlt = await _frage(hass_ws_client, hass, type="heimnetz/geraet", geraet="gibtsnicht")
    assert fehlt["error"]["code"] == "not_found"


async def test_geraete_nach_art(hass, geladen, hass_ws_client, hass_read_only_access_token):
    """AN-0001: Art aus der Geräteliste von HA (nicht aus den Einträgen „Tracked device“), selbst wählbar (nur Admin)."""
    from homeassistant.helpers import device_registry as dr
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    fremd = MockConfigEntry(domain="shelly")
    fremd.add_to_hass(hass)
    reg = dr.async_get(hass)
    mac = dr.CONNECTION_NETWORK_MAC
    reg.async_get_or_create(
        config_entry_id=fremd.entry_id,
        connections={(mac, "00:11:22:33:44:02")},
        manufacturer="Shelly",
        model="Shelly Plug S Gen3",
    )
    reg.async_get_or_create(
        config_entry_id=fremd.entry_id,
        connections={(mac, "00:11:22:33:44:04")},
        manufacturer="FRITZ!",
        model="FRITZ!Box Tracked device",
    )
    d = (await _frage(hass_ws_client, hass, type="heimnetz/geraete"))["result"]
    je_name = {g["name"]: g for g in d["geraete"]}
    assert (je_name["fernseher"]["kat"], je_name["fernseher"]["art_quelle"]) == (
        "smart",
        "Home Assistant: Shelly Shelly Plug S Gen3",
    )
    assert "Tracked" not in je_name["kind"]["art_quelle"]
    assert sum(gr_["gesamt"] for gr_ in d["gruppen_art"]) == len(d["geraete"])
    assert all(gr_["text"] for gr_ in d["gruppen_art"])

    kennung = geraete_id("00:11:22:33:44:02", geladen.runtime_data.salz)
    gast = await hass_ws_client(hass, hass_read_only_access_token)
    await gast.send_json_auto_id(
        {"type": "heimnetz/geraet/art", "geraet": kennung, "art": "medien"}
    )
    assert (await gast.receive_json())["error"]["code"] == "unauthorized"
    g = (
        await _frage(hass_ws_client, hass, type="heimnetz/geraet/art", geraet=kennung, art="medien")
    )["result"]
    assert (g["kat"], g["art_quelle"], g["art_selbst"]) == ("medien", "selbst gewählt", True)
    assert {k["name"] for k in g["kategorien"]} >= {"netz", "smart", "unbekannt"}
    weg = await _frage(
        hass_ws_client, hass, type="heimnetz/geraet/art", geraet="gibtsnicht", art="smart"
    )
    assert weg["error"]["code"] == "not_found"
    assert "gibtsnicht" not in geladen.runtime_data.einstellungen.arten  # nicht gespeichert
    falsch = await _frage(hass_ws_client, hass, type="heimnetz/geraet/art", geraet=kennung, art="x")
    assert falsch["error"]["code"] == "ungueltig"
    # bleibt nach einem Neuladen der Einrichtung
    await hass.config_entries.async_reload(geladen.entry_id)
    await hass.async_block_till_done()
    d = (await _frage(hass_ws_client, hass, type="heimnetz/geraete"))["result"]
    assert next(x for x in d["geraete"] if x["id"] == kennung)["kat"] == "medien"
    g = (await _frage(hass_ws_client, hass, type="heimnetz/geraet/art", geraet=kennung, art=None))[
        "result"
    ]
    assert (g["kat"], g["art_selbst"]) == ("smart", False)


async def test_mobilfunk_verbrauch_protokoll(hass, geladen, hass_ws_client):
    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk", tage=7))["result"]
    assert m["verfuegbar"] and m["strecke"]["rsrp"] == -100 and m["befund"]["titel"]
    v = (await _frage(hass_ws_client, hass, type="heimnetz/verbrauch", tage=7))["result"]
    assert len(v["tage"]) == 7 and not v["verfuegbar"]  # ohne Zähler-Entitäten von FRITZ!Box Tools
    j = (await _frage(hass_ws_client, hass, type="heimnetz/protokoll", art="journal"))["result"]
    assert j["eintraege"][-1]["text"].startswith("Erfassung gestartet")
    w = (
        await _frage(
            hass_ws_client, hass, type="heimnetz/protokoll", art="journal", nur_warnungen=True
        )
    )["result"]
    assert all(z["stufe"] in ("kritisch", "warnung") for z in w["eintraege"])
    i = (
        await _frage(
            hass_ws_client, hass, type="heimnetz/protokoll", art="internet", suche="GETRENNT"
        )
    )["result"]
    assert [z["text"] for z in i["eintraege"]] == ["Internetverbindung wurde getrennt."]


async def test_verbrauch_findet_zaehler_von_fritzbox_tools(hass, geladen, fritz, hass_ws_client):
    reg = er.async_get(hass)
    for k in ("gb_received", "gb_sent"):
        reg.async_get_or_create("sensor", "fritz", f"box-{k}", config_entry=fritz)
    v = (await _frage(hass_ws_client, hass, type="heimnetz/verbrauch", tage=7))["result"]
    assert v["verfuegbar"] and v["kacheln"]["heute"] == {"down": 0, "up": 0, "speedtest": 0}


async def test_einstellungen(hass, eintrag, box, pi, hass_ws_client, hass_read_only_access_token):
    hass.states.async_set(
        "input_number.netz_tarif_download", "150.0"
    )  # alter Helfer zählt nicht mehr
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    e = (await _frage(hass_ws_client, hass, type="heimnetz/einstellungen"))["result"]
    assert (e["tarif_down"], e["tarif_up"], e["ab"]) == (None, None, None)  # leer am Anfang
    neu = await _frage(
        hass_ws_client, hass, type="heimnetz/einstellungen/setzen", tarif_down=200, tarif_up=30
    )
    assert neu["result"]["tarif_down"] == 200.0 and neu["result"]["tarif_up"] == 30.0
    falsch = await _frage(
        hass_ws_client, hass, type="heimnetz/einstellungen/setzen", ab="2999-01-01"
    )
    assert falsch["error"]["code"] == "ungueltig" and "Zukunft" in falsch["error"]["message"]
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "heimnetz/einstellungen/setzen", "tarif_down": 1})
    assert (await client.receive_json())["error"]["code"] == "unauthorized"
    assert eintrag.runtime_data.einstellungen.wert.tarif_down == 200.0
    assert await hass.config_entries.async_reload(eintrag.entry_id)  # bleibt gespeichert
    await hass.async_block_till_done()
    assert eintrag.runtime_data.einstellungen.wert.tarif_down == 200.0


async def test_ohne_einrichtung(hass, hass_ws_client):
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, "heimnetz", {})
    antwort = await _frage(hass_ws_client, hass, type="heimnetz/uebersicht")
    assert antwort["error"]["code"] == "nicht_eingerichtet"


async def test_keine_hardware_adressen_an_die_seite(hass, geladen, hass_ws_client):
    db = geladen.runtime_data.datenbank
    from custom_components.heimnetz.logik.ereignis import Ereignis
    from custom_components.heimnetz.speicher import Journalzeile

    alt = Journalzeile(
        dt_util.utcnow().timestamp(),
        Ereignis(
            "neu", "warnung", "Neues Gerät: Pi (33:44:01), 00:11:22:33:44:01", "00:11:22:33:44:01"
        ),
    )
    await hass.async_add_executor_job(db.journal_schreiben, [alt])
    for msg in (
        {"type": "heimnetz/protokoll"},
        {"type": "heimnetz/uebersicht"},
        {"type": "heimnetz/geraete"},
        {"type": "heimnetz/wlan"},
    ):
        antwort = await _frage(hass_ws_client, hass, **msg)
        assert "33:44:01" not in str(antwort["result"]), msg


async def test_suche_findet_auch_aeltere_zeilen(hass, geladen, hass_ws_client):
    from custom_components.heimnetz.logik.ereignis import Ereignis
    from custom_components.heimnetz.speicher import Journalzeile

    db = geladen.runtime_data.datenbank
    t = dt_util.utcnow().timestamp() - 86_400
    zeilen = [Journalzeile(t - 10, Ereignis("x", "info", "Drucker 100% weg"))] + [
        Journalzeile(t + i, Ereignis("x", "info", f"Füllung {i}")) for i in range(50)
    ]
    await hass.async_add_executor_job(db.journal_schreiben, zeilen)
    d = (
        await _frage(
            hass_ws_client, hass, type="heimnetz/protokoll", suche="drucker 100%", grenze=5
        )
    )["result"]
    assert [z["text"] for z in d["eintraege"]] == ["Drucker 100% weg"]
    d = (await _frage(hass_ws_client, hass, type="heimnetz/protokoll", suche="_", grenze=5))[
        "result"
    ]
    assert d["eintraege"] == []  # „_“ ist kein Platzhalter


async def test_tagesgrenzen_ueber_die_zeitumstellung(hass, freezer):
    from custom_components.heimnetz.ansichten import _mitternacht

    await hass.config.async_set_time_zone("Europe/Vienna")
    freezer.move_to("2026-10-26 10:00:00+01:00")  # Tag nach dem Ende der Sommerzeit
    assert _mitternacht(0) - _mitternacht(1) == 25 * 3600
    assert _mitternacht(1) - _mitternacht(2) == 24 * 3600


async def test_wlan_und_mobilfunk_neu(hass, geladen, hass_ws_client):
    w = (await _frage(hass_ws_client, hass, type="heimnetz/wlan"))["result"]
    assert w["verfuegbar"] and w["schwach_unter"] == 40 and w["gast_an"] is False
    assert [(g["name"], g["band"], g["signal"], g["schwach"]) for g in w["geraete"]] == [
        ("Tab", "2,4", 18, True),
        ("kind", "2,4", 55, False),
        ("fernseher", "5", 92, False),
    ]
    assert [(b["band"], b["kanal"], b["geraete"]) for b in w["baender"]] == [
        ("2,4", 6, 2),
        ("5", 44, 1),
    ]
    assert w["befunde"][0]["titel"] == "1 Gerät mit schwachem Empfang"
    assert "00:11" not in str(w) and all(len(g["id"]) < 40 for g in w["geraete"])
    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]
    assert "antennen" not in m and m["laufzeit"] == "1 h 2 min"
    assert m["baender"] == "LTE 1, 3 · 5G n78" and m["abbrueche_7"] == 0
    assert m["herkunft"] == "box" and m["herkunft_text"] == "laut FRITZ!Box"
    assert m["strecke"] == {
        "geraet": "FRITZ!Box",
        "rsrp": -100,
        "lage": 0.5,
        "wort": "mittel",
        "entfernung": "1,4 km",
        "anbieter": "3 AT",
        "masten": ["5G", "4G"],
    }
    assert [(z["art"], z["rolle"], z["anker"], z["kennung"], z["stufen"]) for z in m["zellen"]] == [
        ("5G", "bündelt dazu", False, "PCI 121", 3),
        ("LTE", "Anker", True, "abcde-0b", 2),
    ]
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "heimnetz/einstellungen/setzen", "wlan_schwach": 50})
    assert (await client.receive_json())["result"]["wlan_schwach"] == 50
    await client.send_json_auto_id({"type": "heimnetz/einstellungen/setzen", "wlan_schwach": 45})
    assert (await client.receive_json())["error"]["code"] == "ungueltig"
    w = (await _frage(hass_ws_client, hass, type="heimnetz/wlan"))["result"]
    assert [g["schwach"] for g in w["geraete"]] == [True, False, False] and w["schwach_unter"] == 50


OPENCELLID = "https://opencellid.org/cell/get"
BEACONDB = "https://api.beacondb.net/v1/geolocate"
OVERPASS = "https://overpass-api.de/api/interpreter"
OCID_ABZUG = "https://opencellid.org/ocid/downloads"


async def _karte(hass, hass_ws_client):
    return (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]["karte"]


def _anfragen(aioclient_mock, url):
    return [c for c in aioclient_mock.mock_calls if str(c[1]).startswith(url)]


async def test_karte_ohne_schluessel_nur_ring(hass, geladen, hass_ws_client, aioclient_mock):
    k = await _karte(hass, hass_ws_client)
    assert k["stand"] == "ohne_schluessel" and k["masten"] == [] and k["punkte"] == []
    assert k["ring"] == "1,4 km" and k["ring_m"] == 1350 and k["gefunden"] == 0 and k["zellen"] == 2
    assert k["wohnung"] == [hass.config.latitude, hass.config.longitude]
    s, w, n, o = k["rahmen"]
    assert s < hass.config.latitude < n and w < hass.config.longitude < o
    assert not _anfragen(aioclient_mock, OPENCELLID)  # ohne Schlüssel nicht zu OpenCellID
    (anfrage,) = _anfragen(
        aioclient_mock, BEACONDB
    )  # BeaconDB nur für die Zelle mit voller Kennung
    zelle = anfrage[2]["cellTowers"][0]
    assert zelle == {
        "radioType": "lte",
        "mobileCountryCode": 232,
        "mobileNetworkCode": 5,
        "locationAreaCode": 0xC0FC,
        "cellId": 0xABCDE * 256 + 0x0B,
    }
    assert anfrage[2]["considerIp"] is False  # der eigene Standort geht nie hinaus
    assert set(anfrage[2]) == {"considerIp", "fallbacks", "cellTowers"}  # nur die Zelle
    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]
    anker = next(z for z in m["zellen"] if z["anker"])
    assert anker["tac"] == "c0fc" and anker["plmn"] == "232 05" and anker["fund"] is None
    assert anker["such"] == "nicht gefunden"
    assert next(z for z in m["zellen"] if not z["anker"])["such"] == "nur PCI – nicht nachschlagbar"
    assert len(_anfragen(aioclient_mock, BEACONDB)) == 1  # „nicht gefunden“ gemerkt: einen Tag Ruhe


async def test_karte_beacondb_findet_den_mast(hass, geladen, hass_ws_client, aioclient_mock):
    lat, lon = hass.config.latitude + 0.008, hass.config.longitude + 0.011
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.post(BEACONDB, json={"location": {"lat": lat, "lng": lon}, "accuracy": 50})
    k = await _karte(hass, hass_ws_client)
    assert k["stand"] == "gefunden" and k["gefunden"] == 1
    (mast,) = k["masten"]
    assert mast["ort"] == [lat, lon]
    assert mast[
        "fuenf_g"
    ]  # die 5G-Zelle bündelt dazu: am Mast der Ankerzelle „4G + 5G (vermutlich)“
    assert {kk: mast[kk] for kk in ("name", "entfernung", "richtung", "genau")} == {
        "name": "abcde",
        "entfernung": "1,4 km",
        "richtung": "Nordost",
        "genau": "50 m",
    }
    (punkt,) = k["punkte"]
    assert punkt == {"ort": [lat, lon], "genau_m": 50, "anker": True, "name": "0b"}
    assert k["rahmen"][2] > lat and k["rahmen"][3] > lon  # Mast im Rahmen
    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]
    assert next(z for z in m["zellen"] if z["anker"])["fund"] == {
        "quelle": "BeaconDB",
        "genau": "50 m",
    }


async def test_karte_mit_mast_und_merken(hass, geladen, hass_ws_client, aioclient_mock):
    lat, lon = hass.config.latitude + 0.008, hass.config.longitude + 0.011
    aioclient_mock.get(OPENCELLID, json={"lat": lat, "lon": lon, "range": 350})
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "geheim-123"})
    k = await _karte(hass, hass_ws_client)
    assert k["stand"] == "gefunden"
    assert {kk: k["masten"][0][kk] for kk in ("entfernung", "richtung", "genau")} == {
        "entfernung": "1,4 km",
        "richtung": "Nordost",
        "genau": "350 m",
    }
    (_, url, _, _) = _anfragen(aioclient_mock, OPENCELLID)[0]
    assert (
        url.query["mcc"] == "232"
        and url.query["lac"] == str(0xC0FC)
        and url.query["radio"] == "LTE"
    )
    assert url.query["cellid"] == str(0xABCDE * 256 + 0x0B)
    assert not {"lat", "lon"} & set(url.query)  # der eigene Standort geht nie hinaus
    await _karte(hass, hass_ws_client)
    assert len(_anfragen(aioclient_mock, OPENCELLID)) == 1  # gemerkt, nicht noch einmal gefragt
    assert "geheim-123" not in str(k)


async def test_karte_genauerer_fund_zaehlt(hass, geladen, hass_ws_client, aioclient_mock):
    lat, lon = hass.config.latitude + 0.008, hass.config.longitude + 0.011
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.get(OPENCELLID, json={"lat": lat + 0.01, "lon": lon, "range": 2000})
    aioclient_mock.post(BEACONDB, json={"location": {"lat": lat, "lng": lon}, "accuracy": 80})
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "a"})
    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]
    assert next(z for z in m["zellen"] if z["anker"])["fund"] == {
        "quelle": "BeaconDB",
        "genau": "80 m",
    }
    assert m["karte"]["masten"][0]["entfernung"] == "1,4 km"


async def test_karte_mast_unbekannt_und_fehler(hass, geladen, hass_ws_client, aioclient_mock):
    aioclient_mock.get(OPENCELLID, json={"error": "Cell not found", "code": 1})
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "a"})
    k = await _karte(hass, hass_ws_client)
    assert k["stand"] == "nicht_gefunden" and k["masten"] == [] and k["rahmen"]
    await _karte(hass, hass_ws_client)
    assert len(_anfragen(aioclient_mock, OPENCELLID)) == 1  # ein Tag Pause
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.get(OPENCELLID, exc=TimeoutError())
    aioclient_mock.post(BEACONDB, exc=TimeoutError())
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "b"})
    # neuer Schlüssel: OpenCellID gleich neu gefragt (nicht erreichbar); BeaconDB merkt sich „nicht gefunden“ noch
    # einen Tag – „unbekannt“ ist damit nicht sicher, also „nicht erreichbar“
    assert (await _karte(hass, hass_ws_client))["stand"] == "fehler"
    assert len(_anfragen(aioclient_mock, OPENCELLID)) == 1 and not _anfragen(
        aioclient_mock, BEACONDB
    )


async def test_karte_beide_nicht_erreichbar(hass, geladen, hass_ws_client, aioclient_mock):
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.get(OPENCELLID, exc=TimeoutError())
    aioclient_mock.post(BEACONDB, status=503, json={})
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "a"})
    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]
    assert m["karte"]["stand"] == "fehler"
    assert (
        next(z for z in m["zellen"] if z["anker"])["such"]
        == "Dienste nicht erreichbar – später neu"
    )


async def test_karte_schluessel_abgelehnt(hass, geladen, hass_ws_client, aioclient_mock):
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.get(OPENCELLID, status=401, json={"error": "Invalid token", "code": 2})
    aioclient_mock.post(BEACONDB, json={"location": {"lat": 48.21, "lng": 16.38}, "accuracy": 500})
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "falsch"})
    k = await _karte(hass, hass_ws_client)
    assert (
        k["stand"] == "schluessel_ungueltig" and k["gefunden"] == 1
    )  # Hinweis bleibt, BeaconDB zeigt trotzdem


async def test_karte_osm_masten_im_hintergrund(hass, geladen, hass_ws_client, aioclient_mock):
    la, lo_ = hass.config.latitude, hass.config.longitude
    aioclient_mock.clear_requests()
    aioclient_mock.post(BEACONDB, status=404, json={})
    aioclient_mock.post(
        OVERPASS,
        json={
            "elements": [
                {
                    "type": "node",
                    "lat": la - 0.0122,
                    "lon": lo_,
                    "tags": {"tower:type": "communication"},
                },
                {"type": "node", "lat": la + 0.05, "lon": lo_, "tags": {"operator": "A1"}},
            ]
        },
    )
    await _karte(hass, hass_ws_client)  # erstes Öffnen: Masten werden im Hintergrund geholt
    await hass.async_block_till_done()
    k = await _karte(hass, hass_ws_client)
    passt, fern = k["osm"]
    assert passt["passt"] and passt["entfernung"] == "1,4 km" and passt["richtung"] == "Süd"
    assert not fern["passt"] and fern["betreiber"] == "A1" and fern["entfernung"] == "5,6 km"
    (anfrage,) = _anfragen(aioclient_mock, OVERPASS)  # einmal, dann gemerkt
    text = str(anfrage[2])
    assert (
        f"{la:.4f}" not in text and f"{lo_:.4f}" not in text
    )  # nur der Raster-Ausschnitt, nie die Wohnung


async def test_osm_abbruch_wird_nicht_gemerkt(hass, geladen, hass_ws_client, aioclient_mock):
    aioclient_mock.clear_requests()
    aioclient_mock.post(BEACONDB, status=404, json={})
    aioclient_mock.post(OVERPASS, json={"remark": "runtime error: Query timed out", "elements": []})
    await _karte(hass, hass_ws_client)
    await hass.async_block_till_done()
    await _karte(hass, hass_ws_client)
    await hass.async_block_till_done()
    assert (
        len(_anfragen(aioclient_mock, OVERPASS)) == 1
    )  # Abbruch: Fehler gemerkt, in sechs Stunden neu – keine Schleife
    merk = geladen.runtime_data.osm._merk
    assert merk["fehler_t"] and merk["masten"] == []


async def test_karte_anbieter_aus_opencellid_abzug(hass, geladen, hass_ws_client, aioclient_mock):
    import gzip

    la, lo_ = hass.config.latitude, hass.config.longitude
    csv = (
        "radio,mcc,net,area,cell,unit,lon,lat,range,samples,changeable,created,updated,averageSignal\n"
        f"LTE,232,5,1,1,0,{lo_},{la - 0.012},500,3,1,0,0,0\n"
        f"NR,232,5,1,2,0,{lo_ + 0.001},{la - 0.0125},500,1,1,0,0,0\n"
    )
    aioclient_mock.clear_requests()
    aioclient_mock.post(BEACONDB, status=404, json={})
    aioclient_mock.get(OPENCELLID, json={"error": "Cell not found", "code": 1})
    aioclient_mock.get(OCID_ABZUG, content=gzip.compress(csv.encode()))
    aioclient_mock.post(
        OVERPASS,
        json={"elements": [{"type": "node", "lat": la - 0.0122, "lon": lo_, "tags": {}}]},
    )
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "geheim-9"})
    for _ in range(3):  # Masten, dann Abzug (erst wenn Masten da sind), dann Anzeige
        await _karte(hass, hass_ws_client)
        await hass.async_block_till_done()
    (mast,) = (await _karte(hass, hass_ws_client))["osm"]
    assert mast["anbieter"] == ["Drei"] and mast["technik"] == ["LTE", "5G"] and mast["zellen"] == 2
    assert mast["entfernung"] == "1,4 km" and mast["richtung"] == "Süd"
    (abruf,) = _anfragen(aioclient_mock, OCID_ABZUG)  # einmal, dann gemerkt
    assert abruf[1].query["type"] == "mcc" and abruf[1].query["file"] == "232.csv.gz"


async def test_opencellid_abzug_fehlertext(hass, geladen, hass_ws_client, aioclient_mock):
    aioclient_mock.clear_requests()
    aioclient_mock.post(BEACONDB, status=404, json={})
    aioclient_mock.get(OPENCELLID, json={"error": "Cell not found", "code": 1})
    aioclient_mock.get(OCID_ABZUG, content=b"RATE_LIMITED")
    la, lo_ = hass.config.latitude, hass.config.longitude
    aioclient_mock.post(
        OVERPASS, json={"elements": [{"type": "node", "lat": la - 0.0122, "lon": lo_}]}
    )
    hass.config_entries.async_update_entry(geladen, options={"opencellid_schluessel": "k"})
    for _ in range(3):
        await _karte(hass, hass_ws_client)
        await hass.async_block_till_done()
    (mast,) = (await _karte(hass, hass_ws_client))["osm"]
    assert mast["anbieter"] is None and mast["zellen"] == 0
    assert len(_anfragen(aioclient_mock, OCID_ABZUG)) == 1  # Fehler gemerkt: erst morgen wieder
    assert geladen.runtime_data.ocid._merk["fehler_t"]


def test_ocid_abzug_zeilenweise_entpackt():
    import gzip

    from custom_components.heimnetz.ocid_abzug import _auswerten

    kopf = "radio,mcc,net,area,cell,unit,lon,lat,range,samples,changeable,created,updated,averageSignal\n"
    zeilen = "".join(f"LTE,232,1,1,{i},0,16.3,48.2,1,1,1,0,0,0\n" for i in range(20_000))
    r = (48.1, 16.1, 48.5, 16.5)
    assert len(_auswerten(gzip.compress((kopf + zeilen).encode()), r)) == 20_000
    assert len(_auswerten((kopf + zeilen).encode(), r)) == 20_000  # auch ungepackt
    try:
        _auswerten(b"Invalid token geheim", r)
    except ValueError as err:
        assert "geheim" not in str(err)  # Antworttext kommt nie in die Meldung
    else:
        raise AssertionError("keine CSV muss als Fehler gelten")


async def test_karte_mast_aus_gemerkten_zellen(hass, geladen, hass_ws_client, aioclient_mock):
    """Einmal gefunden, dann wechselt die Box auf einen unbekannten Sektor: der Mast bleibt."""
    lat, lon = hass.config.latitude + 0.008, hass.config.longitude + 0.011
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.post(BEACONDB, json={"location": {"lat": lat, "lng": lon}, "accuracy": 50})
    assert (await _karte(hass, hass_ws_client))["masten"][0]["name"] == "abcde"
    aioclient_mock.clear_requests()
    aioclient_mock.post(OVERPASS, json={"elements": []})
    aioclient_mock.post(BEACONDB, status=404, json={})
    from dataclasses import replace

    abruf = geladen.runtime_data.abruf
    m = abruf.data.mobil
    neu = tuple(replace(z, zelle="abcde-0c") if z.rolle == "primary" else z for z in m.zellen)
    haupt = next(z for z in neu if z.rolle == "primary")
    abruf.async_set_updated_data(replace(abruf.data, mobil=replace(m, zellen=neu, haupt=haupt)))
    k = await _karte(hass, hass_ws_client)
    assert k["gefunden"] == 0 and k["punkte"] == []  # der neue Sektor ist unbekannt …
    assert [x["name"] for x in k["masten"]] == ["abcde"]  # … der Mast der Sendeanlage bleibt


async def test_geraete_vpn_gruppe(hass, geladen, hass_ws_client):
    """WU-0003: ein per WireGuard eingewähltes Gerät steht in der Gruppe „🔐 VPN (WireGuard)“."""
    from dataclasses import replace

    from custom_components.heimnetz.logik import geraete as gr

    abruf = geladen.runtime_data.abruf
    mac, g = next(iter(abruf.data.geraete.items()))
    abruf.async_set_updated_data(
        replace(abruf.data, geraete={**abruf.data.geraete, mac: replace(g, vpn=True)})
    )
    d = (await _frage(hass_ws_client, hass, type="heimnetz/geraete"))["result"]
    assert d["gruppen"][0]["name"] == gr.VPN and d["gruppen"][0]["gesamt"] == 1
    assert sum(x["verbindung"] == gr.VPN for x in d["geraete"]) == 1
