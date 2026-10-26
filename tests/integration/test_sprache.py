"""WU-0006: Die Integration liefert ihre Texte in der Sprache von Home Assistant (Deutsch oder Englisch); was im
Journal steht, bleibt in der Sprache, in der es geschrieben wurde."""

from homeassistant.core import HomeAssistant


async def _frage(hass_ws_client, hass, **msg):
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def _laden(hass: HomeAssistant, eintrag) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()


async def test_texte_der_seite_auf_englisch(hass, eintrag, box, pi, hass_ws_client):
    hass.config.language = "en"
    await _laden(hass, eintrag)
    d = (await _frage(hass_ws_client, hass, type="heimnetz/uebersicht"))["result"]
    assert [p["name"] for p in d["pruefungen"]] == [
        "Pi → FRITZ!Box",
        "Pi → Internet",
        "Name resolution (DNS)",
        "Home network",
        "DHCP hands out",
        "DHCP test",
    ]
    assert d["pruefungen"][-1]["wert"] == "no server answers"
    assert d["empfang"]["wort"] == "fair"

    w = (await _frage(hass_ws_client, hass, type="heimnetz/wlan"))["result"]
    assert w["befunde"][0]["titel"] == "1 device with weak reception"
    assert [g["band"] for g in w["geraete"]][:1] == ["2.4"] and w["baender"][0]["band"] == "2.4"

    m = (await _frage(hass_ws_client, hass, type="heimnetz/mobilfunk"))["result"]
    assert (m["strecke"]["wort"], m["strecke"]["entfernung"]) == ("fair", "1.4 km")
    assert [(z["rolle"], z["rolle_art"]) for z in m["zellen"]] == [
        ("aggregated", "dazu"),
        ("anchor", "anker"),
    ]
    assert m["befund"]["titel"].startswith("Fair reception")

    g = (await _frage(hass_ws_client, hass, type="heimnetz/geraete"))["result"]
    texte = {x["name"]: x["text"] for x in g["gruppen"]}
    assert texte.get("WLAN 2,4 GHz") == "WLAN 2.4 GHz"  # Kennung bleibt, Text englisch
    assert all(not x["text"].startswith("❓ Unbekannt") for x in g["gruppen_art"])

    j = (await _frage(hass_ws_client, hass, type="heimnetz/protokoll", art="journal"))["result"]
    assert any(z["text"].startswith("Recording started:") for z in j["eintraege"])


async def test_fehlertexte_der_befehle_auf_englisch(hass, eintrag, box, pi, hass_ws_client):
    await _laden(hass, eintrag)
    hass.config.language = "en-GB"
    a = await _frage(hass_ws_client, hass, type="heimnetz/einstellungen/setzen", wlan_schwach=45)
    assert a["error"] == {"code": "ungueltig", "message": "Weak reception: 30, 40, 50 percent"}
    a = await _frage(hass_ws_client, hass, type="heimnetz/geraet", geraet="gibt-es-nicht")
    assert a["error"]["message"] == "Device not found"
    hass.config.language = "de"
    a = await _frage(hass_ws_client, hass, type="heimnetz/geraet", geraet="gibt-es-nicht")
    assert a["error"]["message"] == "Gerät nicht gefunden"


async def test_journal_bleibt_in_seiner_sprache(hass, eintrag, box, pi, hass_ws_client):
    await _laden(hass, eintrag)  # Deutsch: „Erfassung gestartet …“
    hass.config.language = "en"
    j = (await _frage(hass_ws_client, hass, type="heimnetz/protokoll", art="journal"))["result"]
    assert any(z["text"].startswith("Erfassung gestartet:") for z in j["eintraege"])
    d = (await _frage(hass_ws_client, hass, type="heimnetz/uebersicht"))["result"]
    assert d["pruefungen"][2]["name"] == "Name resolution (DNS)"  # was neu entsteht, ist englisch


async def test_tickets_auf_englisch(hass, eintrag, box, pi, hass_ws_client):
    await _laden(hass, eintrag)
    hass.config.language = "en"
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "heimnetz/meldung/neu", "meldung": {"art": "wunsch", "text": "Bitte mehr Farbe"}}
    )
    assert (await client.receive_json())["success"]
    await client.send_json_auto_id({"type": "heimnetz/meldung/neu", "meldung": {"art": "wunsch"}})
    assert (await client.receive_json())["error"]["message"] == "text: please describe briefly"
    await client.send_json_auto_id({"type": "heimnetz/meldungen"})
    m = (await client.receive_json())["result"][0]
    assert (m["art_text"], m["status_text"]) == ("Wish", "new")


async def test_sprache_der_seite_vor_der_sprache_von_ha(hass, eintrag, box, pi, hass_ws_client):
    """Die Seite schickt die Sprache aus dem Profil des Nutzers mit; sie gilt nur für diese Antwort."""
    hass.config.language = "de"
    await _laden(hass, eintrag)
    a = await _frage(hass_ws_client, hass, type="heimnetz/geraet", geraet="x", sprache="en")
    assert a["error"]["message"] == "Device not found"
    v = await _frage(
        hass_ws_client,
        hass,
        type="heimnetz/meldung/github",
        meldung={"art": "fehler", "text": "Karte bleibt grau"},
        sprache="en-GB",
    )
    assert v["result"]["titel"] == "[Bug] Karte bleibt grau"
    # Befehl ohne eigene Felder nimmt das Feld ebenso an
    d = await _frage(hass_ws_client, hass, type="heimnetz/uebersicht", sprache="en")
    assert d["success"] and d["result"]["pruefungen"][2]["name"] == "Name resolution (DNS)"
    # ohne Feld: Sprache von Home Assistant (nichts bleibt hängen)
    a = await _frage(hass_ws_client, hass, type="heimnetz/geraet", geraet="x")
    assert a["error"]["message"] == "Gerät nicht gefunden"
    d = await _frage(hass_ws_client, hass, type="heimnetz/uebersicht")
    assert d["result"]["pruefungen"][2]["name"] == "Namensauflösung (DNS)"
