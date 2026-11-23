"""Wächter (18.11.2026): Websocket-Befehle, Einspielen auf die Steckdose, Eingriffe ins Journal und als Ereignis,
Stufe 1 (sanft neu starten), und die Steckdose selbst (RPC mit Anmeldung) gegen eine nachgebaute Shelly."""

import json
import time
from dataclasses import replace
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMockResponse

from custom_components.heimnetz import shelly as sh
from custom_components.heimnetz import vorgeschaltet as vg
from custom_components.heimnetz import waechter as wd
from custom_components.heimnetz.const import CONF_MODEM_KENNWORT, CONF_SHELLY_KENNWORT
from custom_components.heimnetz.logik import vorgeschaltet as ve
from custom_components.heimnetz.logik import waechter as wa

DOSE = "192.168.170.41"
KETTE = {
    "art": "internet",
    "glieder": [
        {"typ": "fritzbox", "name": "FRITZ!Box 6860 5G", "adresse": "192.168.170.1", "dose": DOSE}
    ],
}


class Nachbau:
    """Steckdose ohne Netz: merkt sich Skript, Regeln, Befehle und liefert einen Zustand."""

    alle: dict[str, Nachbau] = {}

    def __init__(self, _session, adresse, kennwort, abgelehnt=None):
        self.adresse, self.kennwort = adresse, kennwort
        d = Nachbau.alle.setdefault(adresse, self)
        self.__dict__.update(
            {k: v for k, v in d.__dict__.items() if k not in ("adresse", "kennwort")}
        )
        if d is self:
            self.regeln, self.befehle, self.eingespielt, self.entfernt, self.blinkt = (
                None,
                [],
                0,
                0,
                0,
            )
            self.status = {
                "wv": wa.SKRIPT_VERSION,
                "zustand": "bereit",
                "eingriffe": 0,
                "letzte": [{"t": 1, "was": "start"}],
            }
        Nachbau.alle[adresse] = self

    async def einspielen(self, regeln):
        self.regeln, self.eingespielt = regeln, self.eingespielt + 1
        return 1

    async def regeln_setzen(self, regeln):
        self.regeln = regeln

    async def befehl(self, x, n, **werte):
        self.befehle.append((x, werte))

    async def entfernen(self):
        self.entfernt += 1

    async def stand(self):
        return wa.dosenstand(self.status, 9.5)

    async def blinken(self):
        self.blinkt += 1


@pytest.fixture
def nachbau():
    Nachbau.alle = {}
    with patch.object(wd, "Steckdose", Nachbau):
        yield Nachbau.alle


@pytest.fixture
async def geladen(hass: HomeAssistant, eintrag, box, pi):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    return eintrag


async def _frage(client, **msg):
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def test_speichern_spielt_ein_und_speichert(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    a = await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE)
    assert a["success"], a
    lz = geladen.runtime_data
    assert [w.id for w in lz.einstellungen.waechter] == ["w1"]
    d = nachbau[DOSE]
    assert d.eingespielt == 1
    assert d.regeln["r"] == "kette" and d.regeln["e"] == "192.168.170.1" and d.regeln["s2"] == 12
    # Reiter: Karte mit Zustand der Steckdose nach dem ersten Lesen
    await lz.waechter.lesen()
    a = await _frage(client, type="heimnetz/waechter")
    k = a["result"]["waechter"][0]
    assert k["glieder"][0]["zustand"] == "bereit" and k["glieder"][0]["leistung"] == 9.5
    # gespeichert über einen Neustart der Einstellungen hinweg
    await lz.einstellungen.async_laden()
    assert lz.einstellungen.waechter[0].glieder[0].dose == DOSE


async def test_kennwort_nur_in_den_optionen(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    a = await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE, kennwort="geheim")
    assert a["success"]
    assert geladen.options[CONF_SHELLY_KENNWORT] == "geheim"
    assert nachbau[DOSE].kennwort == "geheim"
    a = await _frage(client, type="heimnetz/waechter")
    assert "geheim" not in json.dumps(a) and a["result"]["kennwort"] is True


async def test_ungueltig_und_doppelte_steckdose(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    a = await _frage(
        client,
        type="heimnetz/waechter/speichern",
        waechter={"art": "ha", "glieder": [{"adresse": "192.168.170.60:8123"}]},
    )
    assert (
        not a["success"]
        and a["error"]["code"] == "ungueltig"
        and "Ohne Steckdose" in a["error"]["message"]
    )
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    zweit = {"art": "geraet", "glieder": [{"adresse": "192.168.170.9", "dose": DOSE}]}
    a = await _frage(client, type="heimnetz/waechter/speichern", waechter=zweit)
    assert not a["success"] and "schon ein anderer Wächter" in a["error"]["message"]


async def test_aendern_ruhe_aus_loeschen(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    assert (await _frage(client, type="heimnetz/waechter/aendern", waechter="w1", was="ruhe"))[
        "success"
    ]
    assert nachbau[DOSE].befehle == [("ruhe", {"min": 60})]
    assert (await _frage(client, type="heimnetz/waechter/aendern", waechter="w1", was="aus"))[
        "success"
    ]
    assert nachbau[DOSE].regeln["an"] == 0
    assert (await _frage(client, type="heimnetz/waechter/blinken", adresse=DOSE))["success"]
    assert nachbau[DOSE].blinkt == 1
    assert (await _frage(client, type="heimnetz/waechter/aendern", waechter="w1", was="loeschen"))[
        "success"
    ]
    assert nachbau[DOSE].entfernt == 1 and geladen.runtime_data.einstellungen.waechter == []
    a = await _frage(client, type="heimnetz/waechter/aendern", waechter="w1", was="an")
    assert a["error"]["code"] == "not_found"


async def test_ohne_admin_nichts_aendern(
    hass, geladen, nachbau, hass_ws_client, hass_read_only_access_token
):
    client = await hass_ws_client(hass, hass_read_only_access_token)
    a = await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE)
    assert a["error"]["code"] == "unauthorized"
    assert (await _frage(client, type="heimnetz/waechter"))["success"]


async def test_eingriff_ins_journal_und_als_ereignis(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    lz = geladen.runtime_data
    ereignisse = []
    hass.bus.async_listen("heimnetz_warnung", lambda e: ereignisse.append(e.data))
    await lz.waechter.lesen()  # erstes Lesen: nichts nachmelden
    d = nachbau[DOSE]
    d.status = {
        **d.status,
        "eingriffe": 1,
        "letzte": [*d.status["letzte"], {"t": 50, "was": "strom", "grund": "inet_weg"}],
    }
    await lz.waechter.lesen()
    await hass.async_block_till_done()
    assert [e["art"] for e in ereignisse] == ["waechter"]
    assert (
        ereignisse[0]["nachricht"]
        == "Wächter: FRITZ!Box 6860 5G: Strom 30 s aus und wieder ein – kein Internet"
    )
    await lz.abruf.async_refresh()  # Journal wird mit dem nächsten Abruf geschrieben
    a = await _frage(client, type="heimnetz/waechter")
    assert a["result"]["eingriffe"][0]["text"].startswith("FRITZ!Box 6860 5G: Strom 30 s")


async def test_stufe1_startet_die_box_sanft_neu(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    lz = geladen.runtime_data
    lz.waechter._gelesen = time.time()  # Steckdose hier nicht lesen
    stand = replace(lz.abruf.data, pi=replace(lz.abruf.data.pi, internet=False))
    lz.waechter.sanft["w1"] = wa.Sanft(weg_seit=time.time() - 6 * 60)
    with patch.object(lz.abruf.box, "neustarten", return_value=True) as neu:
        await lz.waechter.abruf(stand)
        await lz.waechter.abruf(stand)
    assert neu.call_count == 1, "je Störung nur einmal"
    # vorher an die Steckdose: so lange anhalten (Herbert, 23.11.2026)
    assert nachbau[DOSE].befehle == [("sanft", {"min": wa.SANFT_HALT_MIN, "grund": "fritzbox"})]


async def test_stufe1_nicht_angenommen_beendet_den_halt(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    lz = geladen.runtime_data
    lz.waechter._gelesen = time.time()
    stand = replace(lz.abruf.data, pi=replace(lz.abruf.data.pi, internet=False))
    lz.waechter.sanft["w1"] = wa.Sanft(weg_seit=time.time() - 6 * 60)
    with patch.object(lz.abruf.box, "neustarten", return_value=False):
        await lz.waechter.abruf(stand)
    assert [w["min"] for _, w in nachbau[DOSE].befehle] == [wa.SANFT_HALT_MIN, 0]


MODEM = "192.168.0.1"


def _kette_mit_modem(lz):
    router = lz.waechter.router()
    return wa.pruefen(
        {
            "art": "internet",
            "glieder": [
                {"typ": "zte_goform", "name": "ZTE", "adresse": MODEM, "dose": "192.168.170.42"},
                {"typ": "fritzbox", "name": "Box", "adresse": router, "dose": DOSE},
            ],
        }
    )


async def test_stufe1_startet_nicht_die_gesunde_box_wenn_das_modem_haengt(hass, geladen, nachbau):
    lz = geladen.runtime_data
    w = _kette_mit_modem(lz)
    stand = replace(lz.abruf.data, pi=replace(lz.abruf.data.pi, internet=False))
    assert stand.box_erreichbar
    gefragt = []

    async def antwortet(adresse):
        gefragt.append(adresse)
        return False

    lz.waechter.sanft[w.id] = wa.Sanft(weg_seit=time.time() - 6 * 60)
    with (
        patch.object(lz.waechter, "_antwortet", antwortet),
        patch.object(lz.abruf.box, "neustarten", return_value=True) as box,
    ):
        await lz.waechter._sanft(w, stand, time.time())
    assert gefragt == [MODEM], "vor Stufe 1 frisch gefragt (der Stand des Modems kann alt sein)"
    assert box.call_count == 0 and nachbau == {}, "nichts neu gestartet, nichts gemeldet"

    # antwortet das Modem doch: zuerst das Modem (sanft), nicht die Box
    neu = []

    async def sanft(g):
        neu.append(g.typ)
        return True

    with (
        patch.object(lz.waechter, "_antwortet", return_value=True),
        patch.object(lz.waechter, "_sanft_neustarten", sanft),
    ):
        await lz.waechter._sanft(w, stand, time.time())
    assert neu == ["zte_goform"]
    assert {a: [x for x, _ in d.befehle] for a, d in nachbau.items()} == {
        "192.168.170.42": ["sanft"],
        DOSE: ["sanft"],
    }, "beide Steckdosen der Kette halten an"


async def test_stufe1_ont_ohne_weboberflaeche_haelt_nicht_auf(hass, geladen, nachbau):
    """Ein Glied ohne Weboberfläche (ONT, Switch) wird nicht per HTTP gefragt und blockiert Stufe 1 nicht."""
    lz = geladen.runtime_data
    router = lz.waechter.router()
    w = wa.pruefen(
        {
            "art": "internet",
            "glieder": [
                {
                    "typ": "geraet",
                    "name": "ONT",
                    "adresse": "192.168.170.9",
                    "dose": "192.168.170.42",
                },
                {"typ": "fritzbox", "name": "Box", "adresse": router, "dose": DOSE},
            ],
        }
    )
    stand = replace(lz.abruf.data, pi=replace(lz.abruf.data.pi, internet=False))
    gefragt = []

    async def antwortet(adresse):
        gefragt.append(adresse)
        return False

    neu = []

    async def sanft(g):
        neu.append(g.typ)
        return True

    lz.waechter.sanft[w.id] = wa.Sanft(weg_seit=time.time() - 6 * 60)
    with (
        patch.object(lz.waechter, "_antwortet", antwortet),
        patch.object(lz.waechter, "_sanft_neustarten", sanft),
    ):
        await lz.waechter._sanft(w, stand, time.time())
        assert gefragt == [], "ONT ohne Weboberfläche nicht gefragt"
        assert neu == ["fritzbox"], "die Box startet sanft neu"
        # Box gemacht, ONT nicht sanft startbar: nichts mehr fällig, keine Probe mehr
        await lz.waechter._sanft(w, stand, time.time() + 600)
    assert neu == ["fritzbox"] and gefragt == []


async def test_stufe1_modem_kennwort_abgelehnt_kein_zweiter_versuch(hass, geladen):
    lz = geladen.runtime_data
    hass.config_entries.async_update_entry(
        geladen, options={**geladen.options, CONF_MODEM_KENNWORT: "Modem-Geheim"}
    )
    await hass.async_block_till_done()
    lz = geladen.runtime_data
    modem = lz.abruf.modem
    modem.adresse, modem.gemerkt = MODEM, ve.Erkennung("zte_goform", "")
    g = wa.Glied("zte_goform", "ZTE", MODEM)
    with patch.object(wd, "baustein_neustarten", return_value="abgelehnt") as neu:
        assert not await lz.waechter._sanft_neustarten(g)
        assert not await lz.waechter._sanft_neustarten(g)
    assert neu.call_count == 1, "abgelehnt: kein weiterer Anmeldeversuch"
    assert modem.kennwort_abgelehnt(MODEM, "Modem-Geheim")
    # an einer anderen Adresse als der, für die das Kennwort gilt, kein Neustart mit Kennwort
    modem._abgelehnt, modem.kennwort_bei = None, "192.168.8.1"  # noqa: SLF001
    with patch.object(wd, "baustein_neustarten", return_value="ok") as neu:
        assert not await lz.waechter._sanft_neustarten(g)
    assert neu.call_count == 0
    modem.kennwort_bei = MODEM
    with patch.object(wd, "baustein_neustarten", return_value="ok") as neu:
        assert await lz.waechter._sanft_neustarten(g)
    assert neu.call_args.args[3] == "Modem-Geheim"
    # fremdes Gerät unter der Adresse oder anderer Baustein: nie
    assert not await lz.waechter._sanft_neustarten(wa.Glied("tplink", "X", MODEM))


async def test_kein_sanfter_neustart_neben_einer_ha_integration(hass):
    with patch.object(vg.integrationen, "eingerichtet", return_value=True):
        ergebnis = await vg.baustein_neustarten(
            hass, None, ve.Erkennung("huawei_hilink", ""), "Kennwort"
        )
    assert ergebnis == "integration", "sonst stört die zweite Anmeldung die Sitzung von huawei_lte"
    assert await vg.baustein_neustarten(hass, None, ve.Erkennung("zte_ubus", ""), "x") == "fehler"


# ── Die Steckdose selbst (RPC über HTTP) gegen eine nachgebaute Shelly ──


async def test_steckdose_rpc_mit_anmeldung(hass, aioclient_mock):
    nonce = 1_700_000_000
    gesehen = []

    async def rpc(method, url, data):
        anfrage = json.loads(data) if isinstance(data, (str, bytes)) else data
        gesehen.append(anfrage)
        if "auth" not in anfrage:
            frage = json.dumps(
                {
                    "auth_type": "digest",
                    "nonce": nonce,
                    "nc": 1,
                    "realm": "shellyplusplugs-a1",
                    "algorithm": "SHA-256",
                }
            )
            return AiohttpClientMockResponse(
                method,
                url,
                status=401,
                json={"id": anfrage["id"], "error": {"code": 401, "message": frage}},
            )
        a = anfrage["auth"]
        erwartet = wa.anmeldung("geheim", "shellyplusplugs-a1", nonce, a["cnonce"])["response"]
        if a["response"] != erwartet:
            return AiohttpClientMockResponse(
                method,
                url,
                status=401,
                json={"id": anfrage["id"], "error": {"code": 401, "message": "{}"}},
            )
        return AiohttpClientMockResponse(
            method, url, json={"id": anfrage["id"], "result": {"scripts": []}}
        )

    aioclient_mock.post(f"http://{DOSE}/rpc", side_effect=rpc)
    dose = sh.Steckdose(async_get_clientsession(hass), DOSE, "geheim")
    assert await dose.skript_id() is None
    assert "auth" in gesehen[-1] and gesehen[-1]["auth"]["username"] == "admin"
    falsch = sh.Steckdose(async_get_clientsession(hass), DOSE, "falsch")
    with pytest.raises(sh.ShellyFehler) as fehler:
        await falsch.skript_id()
    assert fehler.value.abgelehnt and falsch.kennwort is None


async def test_steckdose_nur_im_heimnetz(hass):
    with pytest.raises(sh.ShellyFehler):
        sh.Steckdose(async_get_clientsession(hass), "8.8.8.8", None)


async def test_steckdose_info_gen1_und_gen2(hass, aioclient_mock):
    aioclient_mock.get(
        f"http://{DOSE}/shelly",
        json={
            "id": "shellyplusplugs-a1",
            "model": "SNPL-00112EU",
            "gen": 2,
            "app": "PlusPlugS",
            "auth_en": False,
        },
    )
    aioclient_mock.get(
        "http://192.168.170.44/shelly", json={"type": "SHPLG-S", "mac": "AABB", "auth": False}
    )
    neu = await sh.Steckdose(async_get_clientsession(hass), DOSE, None).info()
    alt = await sh.Steckdose(async_get_clientsession(hass), "192.168.170.44", None).info()
    assert neu.passt and neu.app == "PlusPlugS"
    assert not alt.passt and alt.gen == 1


async def test_einspielen_schickt_code_in_stuecken(hass, aioclient_mock):
    aufrufe = []

    async def rpc(method, url, data):
        anfrage = json.loads(data) if isinstance(data, (str, bytes)) else data
        aufrufe.append(anfrage)
        ergebnis = {"Script.List": {"scripts": []}, "Script.Create": {"id": 3}}.get(
            anfrage["method"], {}
        )
        return AiohttpClientMockResponse(
            method, url, json={"id": anfrage["id"], "result": ergebnis}
        )

    aioclient_mock.post(f"http://{DOSE}/rpc", side_effect=rpc)
    sid = await sh.Steckdose(async_get_clientsession(hass), DOSE, None).einspielen({"v": 1})
    assert sid == 3
    methoden = [a["method"] for a in aufrufe]
    assert methoden[:3] == ["Script.List", "Script.Create", "KVS.Set"]
    assert methoden[-2:] == ["Script.SetConfig", "Script.Start"]
    code = "".join(a["params"]["code"] for a in aufrufe if a["method"] == "Script.PutCode")
    assert code == sh.skript_code()
    assert not any(m.startswith(("Sys.", "Wifi.", "Shelly.Set", "Schedule.")) for m in methoden), (
        "sonst nichts ändern"
    )


async def test_nicht_erreichbar_meldet_alte_eingriffe_nicht_nochmal(
    hass, geladen, nachbau, hass_ws_client
):
    client = await hass_ws_client(hass)
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    lz = geladen.runtime_data
    d = nachbau[DOSE]
    d.status = {
        **d.status,
        "letzte": [{"t": 1, "was": "start"}, {"t": 5, "was": "strom", "grund": "inet_weg"}],
    }
    await lz.waechter.lesen()
    gemeldet = []
    with patch.object(lz.waechter, "_eingriff", lambda *a: gemeldet.append(a)):
        weg = d.status
        d.stand = lambda: _weg()  # einmal nicht erreichbar
        await lz.waechter.lesen()
        d.stand = lambda: _da(weg)
        await lz.waechter.lesen()
    assert gemeldet == []


async def _weg():
    return wa.Dosenstand(erreichbar=False)


async def _da(status):
    return wa.dosenstand(status, 9.5)


async def test_fremde_kette_wird_abgelehnt(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    fremd = {
        "art": "internet",
        "glieder": [{"typ": "zte_goform", "adresse": "192.168.170.50", "dose": DOSE}],
    }
    a = await _frage(client, type="heimnetz/waechter/speichern", waechter=fremd)
    assert not a["success"] and "Kette des Internets hat sich geändert" in a["error"]["message"]
    assert DOSE not in nachbau, "nichts eingespielt"


async def test_diagnose_schwaerzt_das_kennwort_der_steckdosen(
    hass, geladen, nachbau, hass_ws_client
):
    from custom_components.heimnetz.diagnostics import async_get_config_entry_diagnostics

    client = await hass_ws_client(hass)
    assert (
        await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE, kennwort="geheim")
    )["success"]
    d = await async_get_config_entry_diagnostics(hass, geladen)
    assert "geheim" not in json.dumps(d, default=str)
    assert d["laufzeit"]["waechter"] == {"waechter": 1, "arten": ["internet"], "dosen": 1}


async def test_veraltetes_skript_wird_selbst_erneuert(hass, geladen, nachbau, hass_ws_client):
    client = await hass_ws_client(hass)
    assert (await _frage(client, type="heimnetz/waechter/speichern", waechter=KETTE))["success"]
    lz = geladen.runtime_data
    d = nachbau[DOSE]
    d.status = {**d.status, "wv": wa.SKRIPT_VERSION - 1}
    await lz.waechter.lesen()
    d = nachbau[DOSE]
    assert d.eingespielt == 2, "mit den gespeicherten Regeln neu eingespielt"
    assert d.regeln["e"] == "192.168.170.1"
    await lz.waechter.lesen()
    assert nachbau[DOSE].eingespielt == 2, "höchstens einmal je Stunde"
    await lz.abruf.async_refresh()
    texte = await hass.async_add_executor_job(
        lz.datenbank.journal_texte, "waechter", 0, time.time() + 60
    )
    assert any("auf neuen Stand gebracht (Version" in x for _, x in texte)


# ── Steckdose: abgelehnt merken, unerwartete Antworten, Suche ohne Kennwort ──


def _rpc_ablehnend(gesehen):
    async def rpc(method, url, data):
        anfrage = json.loads(data) if isinstance(data, (str, bytes)) else data
        gesehen.append(json.loads(json.dumps(anfrage)))  # Abzug: die Anfrage wird danach ergänzt
        frage = json.dumps({"nonce": 1, "realm": "r", "nc": 1})
        return AiohttpClientMockResponse(
            method, url, status=401, json={"id": anfrage["id"], "error": {"message": frage}}
        )

    return rpc


async def test_abgelehnt_gilt_je_adresse_auch_fuer_die_naechste_anfrage(hass, aioclient_mock):
    gesehen = []
    aioclient_mock.post(f"http://{DOSE}/rpc", side_effect=_rpc_ablehnend(gesehen))
    merker: dict[str, str] = {}
    for _ in range(3):
        dose = sh.Steckdose(async_get_clientsession(hass), DOSE, "falsch", abgelehnt=merker)
        with pytest.raises(sh.ShellyFehler) as fehler:
            await dose.skript_id()
        assert fehler.value.abgelehnt
    assert sum("auth" in a for a in gesehen) == 1, "nur ein Anmeldeversuch"
    # ein anderes Kennwort wird wieder versucht
    dose = sh.Steckdose(async_get_clientsession(hass), DOSE, "anders", abgelehnt=merker)
    with pytest.raises(sh.ShellyFehler):
        await dose.skript_id()
    assert sum("auth" in a for a in gesehen) == 2


@pytest.mark.parametrize(
    ("antwort", "status"),
    [
        ({"id": 1, "error": "kaputt"}, 200),
        ({"id": 1, "result": {"scripts": [{"name": wa.SKRIPT_NAME, "id": "abc"}]}}, 200),
        ({"id": 1, "result": {"scripts": "keine"}}, 200),
        ({"id": 1, "result": ["liste"]}, 200),
        ({"id": 1, "error": {"message": "[1, 2]"}}, 401),
        ({"id": 1, "error": {"message": '{"nonce": 1, "nc": "x"}'}}, 401),
        (["keine", "antwort"], 200),
    ],
)
async def test_unerwartete_antworten_sind_shellyfehler(hass, aioclient_mock, antwort, status):
    aioclient_mock.post(f"http://{DOSE}/rpc", status=status, json=antwort)
    dose = sh.Steckdose(async_get_clientsession(hass), DOSE, "geheim")
    with pytest.raises(sh.ShellyFehler):
        await dose.skript_id()
    assert (await dose.stand()).erreichbar is False


async def test_info_und_leistung_unerwartet(hass, aioclient_mock):
    aioclient_mock.get(f"http://{DOSE}/shelly", json={"gen": "zwei"})
    aioclient_mock.post(f"http://{DOSE}/rpc", json={"id": 1, "result": {"apower": "viel"}})
    dose = sh.Steckdose(async_get_clientsession(hass), DOSE, None)
    with pytest.raises(sh.ShellyFehler):
        await dose.info()
    with pytest.raises(sh.ShellyFehler):
        await dose.leistung()


async def test_suche_fragt_geschuetzte_steckdosen_nicht_mit_kennwort(hass, geladen, aioclient_mock):
    hass.config_entries.async_update_entry(
        geladen, options={**geladen.options, CONF_SHELLY_KENNWORT: "geheim"}
    )
    await hass.async_block_till_done()
    MockConfigEntry(domain="shelly", title="Plug", data={"host": DOSE}).add_to_hass(hass)
    MockConfigEntry(domain="shelly", title="Offen", data={"host": "192.168.170.44"}).add_to_hass(
        hass
    )
    aioclient_mock.get(
        f"http://{DOSE}/shelly", json={"id": "shellyplusplugs-a1", "gen": 2, "auth_en": True}
    )
    aioclient_mock.get(
        "http://192.168.170.44/shelly",
        json={"id": "shellyplusplugs-b2", "gen": 2, "auth_en": False},
    )
    aioclient_mock.post(f"http://{DOSE}/rpc", status=401, json={})
    aioclient_mock.post("http://192.168.170.44/rpc", json={"id": 1, "result": {"apower": 4.5}})
    dosen = await geladen.runtime_data.waechter.kandidaten()
    assert {d["adresse"]: d["leistung"] for d in dosen} == {DOSE: None, "192.168.170.44": 4.5}
    rpc = [str(u) for m, u, *_ in aioclient_mock.mock_calls if m == "POST"]
    assert all(DOSE not in u for u in rpc), "an die geschützte Steckdose keine Anfrage mit Kennwort"


async def test_frisch_fragen_ob_das_modem_antwortet(hass, geladen, aioclient_mock, monkeypatch):
    import asyncio

    import aiohttp

    monkeypatch.setattr(
        wd, "neue_session", lambda _z: aioclient_mock.create_session(asyncio.get_running_loop())
    )
    aioclient_mock.get(f"http://{MODEM}/", text="<html></html>")
    aioclient_mock.get("http://192.168.8.1/", exc=aiohttp.ClientError())
    aioclient_mock.get("https://192.168.8.1/", exc=aiohttp.ClientError())
    w = geladen.runtime_data.waechter
    assert await w._antwortet(MODEM)
    assert not await w._antwortet("192.168.8.1")
    assert not await w._antwortet("8.8.8.8"), "nur im Heimnetz"


async def test_halt_steckdose_weg_haelt_nicht_auf(hass, geladen, nachbau):
    lz = geladen.runtime_data
    w = _kette_mit_modem(lz)

    async def weg(*_a, **_k):
        raise sh.ShellyFehler("nicht erreichbar")

    Nachbau("s", "192.168.170.42", None).befehl = weg
    await lz.waechter._halt(w, 5, "fritzbox")
    assert nachbau[DOSE].befehle == [("sanft", {"min": 5, "grund": "fritzbox"})]
