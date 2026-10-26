"""WU-0006: Öffentlich auf GitHub melden – Vorschau zum Entwurf (speichert nichts), Melden mit Link zum Issue,
grober Stand aus der Einrichtung, Zelldaten nur mit Schalter, nie Gerätenamen oder Adressen. Geht auch ohne geladene
Einrichtung."""

from urllib.parse import parse_qs, urlsplit

from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.heimnetz.box import BoxInfo
from custom_components.heimnetz.const import GITHUB_ISSUE_NEU

from .conftest import box_daten

ENTWURF = {
    "art": "fehler",
    "text": "fernseher (00:11:22:33:44:02) verliert das WLAN",
    "kontext": "Funk · Mobilfunk",
    "geraet": "Desktop",
    "version": "0.23.0",
}


async def _ws(client, **msg):
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def _laden(hass: HomeAssistant, eintrag) -> None:
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()


def _body(url: str) -> str:
    return parse_qs(urlsplit(url).query)["body"][0]


async def test_vorschau_mit_stand_der_einrichtung(hass, eintrag, box, pi, hass_ws_client):
    box.return_value = box_daten(info=BoxInfo("FRITZ!Box 6860 5G", "8.03", 3600, 0.0))
    await _laden(hass, eintrag)
    client = await hass_ws_client(hass)

    v = await _ws(client, type="heimnetz/meldung/github", meldung=ENTWURF)
    assert v["success"], v
    r = v["result"]
    assert r["titel"] == "[Fehler] [entfernt] ([entfernt]) verliert das WLAN"
    assert r["url"].startswith(GITHUB_ISSUE_NEU + "?title=")
    assert _body(r["url"]) == r["text"]
    assert f"- Heimnetz 0.23.0 · Home Assistant {HA_VERSION}" in r["text"]
    assert "- Reiter: Funk · Mobilfunk · Desktop" in r["text"]
    assert "- FRITZ!Box 6860 5G · FRITZ!OS 8.03" in r["text"]
    assert "- Netz: 5G-NSA · Ookla Speedtest: nein" in r["text"]
    assert "- Lokales Ticket: FE-0001" in r["text"]
    assert (r["zelle"], r["zelle_da"], r["gekuerzt"]) == (False, True, False)
    for nie in (
        "fernseher",
        "00:11:22",
        "192.168.",
        "abcde-0b",
        "C0FC",
        "geheim",
        str(hass.config.latitude),
    ):
        assert nie not in r["text"] + r["titel"], nie

    mit = (await _ws(client, type="heimnetz/meldung/github", meldung=ENTWURF, zelle=True))["result"]
    assert mit["zelle"] is True
    assert "### Zell- und Signaldaten" in mit["text"]
    assert "- Ankerzelle: abcde-0b · PCI 443 · TAC C0FC · PLMN 23205" in mit["text"]
    assert "- RSRP -100 dBm · RSRQ -11 dB · 5G: RSRP -94 dBm" in mit["text"]
    assert "- Entfernung laut Box: 1,4 km" in mit["text"]

    # die Vorschau speichert nichts
    assert (await _ws(client, type="heimnetz/meldungen"))["result"] == []


async def test_vorschau_sagt_die_nummer_voraus_und_speichert_nichts(hass, hass_ws_client):
    """Ohne Einrichtung: nur Versionen, Reiter, Ookla und Ticketnummer; Zelldaten gibt es dann keine."""
    assert await async_setup_component(hass, "heimnetz", {})
    await hass.async_block_till_done()
    client = await hass_ws_client(hass)
    erst = await _ws(client, type="heimnetz/meldung/neu", meldung={**ENTWURF, "text": "erste"})
    assert erst["result"]["ticket"] == "FE-0001"

    v = (await _ws(client, type="heimnetz/meldung/github", meldung=ENTWURF, zelle=True))["result"]
    assert "- Lokales Ticket: FE-0002" in v["text"], "vorausgesagte Nummer"
    assert (v["zelle"], v["zelle_da"]) == (False, False)
    assert "FRITZ!OS" not in v["text"] and "Netz:" not in v["text"]

    assert v["ticket"] == "FE-0002"
    neu = await _ws(client, type="heimnetz/meldung/neu", meldung=ENTWURF)
    assert neu["result"]["ticket"] == v["ticket"], "die vorausgesagte Nummer bekommt das Ticket"
    liste = (await _ws(client, type="heimnetz/meldungen"))["result"]
    assert [m["ticket"] for m in liste] == ["FE-0002", "FE-0001"]
    assert liste[0]["text"] == ENTWURF["text"], "lokal bleibt der Text, wie er gemeldet wurde"


async def test_vorschau_englisch_und_fehler(hass, hass_ws_client):
    assert await async_setup_component(hass, "heimnetz", {})
    await hass.async_block_till_done()
    hass.config.language = "en"
    # Namen der Geräte-Tracker (FRITZ!Box Tools) gelten auch ohne Einrichtung
    hass.states.async_set("device_tracker.laptop", "home", {"friendly_name": "Laptop-Wohnzimmer"})
    client = await hass_ws_client(hass)
    v = (
        await _ws(
            client,
            type="heimnetz/meldung/github",
            meldung={
                **ENTWURF,
                "art": "wunsch",
                "text": ENTWURF["text"] + ", auch laptop-wohnzimmer",
            },
        )
    )["result"]
    assert v["text"].startswith("fernseher ([removed]) verliert das WLAN, auch [removed]\n")
    # ohne Einrichtung kennt Heimnetz keine Gerätenamen – Adressen fallen trotzdem weg
    assert v["titel"] == "[Wish] fernseher ([removed]) verliert das WLAN, auch [removed]"
    assert "### Environment" in v["text"] and "- Local ticket: WU-0001" in v["text"]
    leer = await _ws(client, type="heimnetz/meldung/github", meldung={**ENTWURF, "text": " "})
    assert leer["error"]["code"] == "ungueltig"


async def test_vorschau_ohne_mobilfunk_und_ohne_ookla(hass, eintrag, box, pi, hass_ws_client):
    """Eine Box ohne Mobilfunk und keine Ookla-Integration: Melden geht trotzdem, Zelldaten fallen still weg."""
    box.return_value = box_daten(mobil=None, ohne_mobilfunk=True)
    await _laden(hass, eintrag)
    client = await hass_ws_client(hass)
    v = (await _ws(client, type="heimnetz/meldung/github", meldung=ENTWURF, zelle=True))["result"]
    assert v["zelle"] is False and v["zelle_da"] is False
    assert "Ookla Speedtest: nein" in v["text"] and "Netz:" not in v["text"]
    assert "Zell- und Signaldaten" not in v["text"]
    r = await _ws(client, type="heimnetz/meldung/neu", meldung=ENTWURF)
    assert r["success"], r
