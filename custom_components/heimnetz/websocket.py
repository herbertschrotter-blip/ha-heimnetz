"""WebSocket-Befehle der Seite (G-11): je Reiter ein Lesebefehl mit fertigen Daten, dazu Einstellungen setzen (nur
Admin). Gibt es keine geladene Einrichtung, antwortet jeder Befehl mit dem Fehler „nicht_eingerichtet“."""

from __future__ import annotations

import functools
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import messages
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from . import ansichten, einrichtung, modem
from .const import CONF_MODEM_KENNWORT, DOMAIN, SEITEN_SPRACHE
from .logik import auswertung as aw
from .logik import vorgeschaltet as ve
from .logik import zugang as zg
from .logik.einstellungen import Ungueltig
from .logik.sprache import t
from .speicher import Angehalten


def _tr(hass: HomeAssistant, text: str) -> str:
    """Fehlertext für die Seite in der Sprache von Home Assistant."""
    return t(text, ansichten.sprache(hass))


def _laufzeit(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> Any:
    eintraege = hass.config_entries.async_loaded_entries(DOMAIN)
    if not eintraege:
        connection.send_error(
            msg["id"],
            "nicht_eingerichtet",
            _tr(hass, "Die Integration Heimnetz ist nicht geladen."),
        )
        return None
    return eintraege[0].runtime_data


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/uebersicht"})
@websocket_api.async_response
async def _uebersicht(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], await ansichten.uebersicht(hass, lz))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/speedtest",
        vol.Optional("tage", default=84): vol.In(aw.ZEITRAEUME),
        vol.Optional("groesse", default="down"): vol.In(tuple(aw.GROESSEN)),
        vol.Optional("grundlast", default="aus"): vol.In(aw.MODI),
        vol.Optional("server"): vol.Any(None, str),
        vol.Optional("tag"): vol.Any(None, vol.All(int, vol.Range(min=0, max=6))),
        vol.Optional("datum"): vol.Any(None, cv.date),
    }
)
@websocket_api.async_response
async def _speedtest(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        daten = await ansichten.speedtest(
            hass,
            lz,
            msg["tage"],
            msg["groesse"],
            msg["grundlast"],
            msg.get("server"),
            msg.get("tag"),
            msg.get("datum"),
        )
        connection.send_result(msg["id"], daten)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/speedtest/kachel",
        vol.Optional("tage", default=84): vol.In(aw.ZEITRAEUME),
        vol.Optional("groesse", default="down"): vol.In(tuple(aw.GROESSEN)),
        vol.Optional("grundlast", default="aus"): vol.In(aw.MODI),
        vol.Optional("server"): vol.Any(None, str),
        vol.Required("tag"): vol.All(int, vol.Range(min=0, max=6)),
        vol.Required("stunde"): vol.All(int, vol.Range(min=0, max=23)),
    }
)
@websocket_api.async_response
async def _speedtest_kachel(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        daten = await ansichten.speedtest_kachel(
            hass,
            lz,
            msg["tage"],
            msg["groesse"],
            msg["grundlast"],
            msg.get("server"),
            msg["tag"],
            msg["stunde"],
        )
        connection.send_result(msg["id"], daten)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/messung/loeschen",
        vol.Required("t"): vol.Coerce(float),  # Kennung = Zeitpunkt, wie in heimnetz/speedtest
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def _messung_loeschen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """AN-0007: eine Messung in Heimnetz löschen (nur Admins); der Verlauf der Ookla-Entitäten bleibt."""
    if lz := _laufzeit(hass, connection, msg):
        try:
            t = await lz.abruf.messung_loeschen(msg["t"])
        except Angehalten:
            connection.send_error(
                msg["id"],
                "sicherung",
                _tr(hass, "Gerade läuft eine Sicherung – bitte gleich noch einmal."),
            )
            return
        if t is None:
            connection.send_error(
                msg["id"], websocket_api.ERR_NOT_FOUND, _tr(hass, "Messung nicht gefunden")
            )
        else:
            connection.send_result(msg["id"], {"t": t})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/geraete"})
@websocket_api.async_response
async def _geraete(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], await ansichten.geraete(hass, lz))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/geraet",
        vol.Required("geraet"): vol.All(
            str, vol.Length(min=1, max=40)
        ),  # Kennung, nicht die Hardware-Adresse
        vol.Optional("tage", default=7): vol.All(int, vol.Range(min=1, max=31)),
    }
)
@websocket_api.async_response
async def _geraet(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        daten = await ansichten.geraet(hass, lz, msg["geraet"], msg["tage"])
        if daten is None:
            connection.send_error(
                msg["id"], websocket_api.ERR_NOT_FOUND, _tr(hass, "Gerät nicht gefunden")
            )
        else:
            connection.send_result(msg["id"], daten)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/geraet/art",
        vol.Required("geraet"): vol.All(str, vol.Length(min=1, max=40)),
        vol.Required("art"): vol.Any(None, str),  # None = wieder automatisch
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def _geraet_art(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Art eines Geräts selbst festlegen (AN-0001, nur Admins); Antwort wie heimnetz/geraet."""
    if lz := _laufzeit(hass, connection, msg):
        if not ansichten.geraet_bekannt(lz, msg["geraet"]):
            connection.send_error(
                msg["id"], websocket_api.ERR_NOT_FOUND, _tr(hass, "Gerät nicht gefunden")
            )
            return
        try:
            await lz.einstellungen.async_art_setzen(msg["geraet"], msg["art"])
        except Ungueltig as err:
            connection.send_error(msg["id"], "ungueltig", err.text(ansichten.sprache(hass)))
            return
        daten = await ansichten.geraet(hass, lz, msg["geraet"], 7)
        if daten is None:
            connection.send_error(
                msg["id"], websocket_api.ERR_NOT_FOUND, _tr(hass, "Gerät nicht gefunden")
            )
        else:
            connection.send_result(msg["id"], daten)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/mobilfunk",
        vol.Optional("tage", default=1): vol.In((1, 7, 30)),
    }
)
@websocket_api.async_response
async def _mobilfunk(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], await ansichten.mobilfunk(hass, lz, msg["tage"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/internet",
        vol.Optional("tage", default=1): vol.In((1, 7, 30)),
    }
)
@websocket_api.async_response
async def _internet(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0009: Reiter „Internet“ – Herkunft des Zugangs und die Werte der Zugangsart."""
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], await ansichten.internet(hass, lz, msg["tage"]))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/zugang"})
@websocket_api.require_admin
@callback
def _zugang(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0009: ⚙ › Zugang (nur Admins) – vom Kennwort nur, ob eines hinterlegt ist."""
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], ansichten.zugang(hass, lz))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/zugang/setzen",
        vol.Optional("wahl"): vol.In(zg.WAHLEN),
        vol.Optional("adresse"): vol.Any(None, vol.All(str, vol.Length(max=60))),
        vol.Optional("ersatz"): vol.In(zg.ERSATZ_WAHLEN),
        vol.Optional("kennwort"): vol.All(str, vol.Length(min=1, max=200)),
        vol.Optional("kennwort_loeschen", default=False): bool,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def _zugang_setzen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0009: Zugang festlegen (nur Admins). Wahl und Adresse über den Einstellungsdienst; das Kennwort nur in den
    Optionen des Eintrags – es steht in keiner Antwort und in keinem Protokoll."""
    if lz := _laufzeit(hass, connection, msg):
        daten = {f"zugang_{k}": msg[k] for k in ("wahl", "adresse", "ersatz") if k in msg}
        try:
            if daten:
                await lz.einstellungen.async_setzen(daten)
        except Ungueltig as err:
            connection.send_error(msg["id"], "ungueltig", err.text(ansichten.sprache(hass)))
            return
        entry = lz.abruf.config_entry
        if "kennwort" in msg or msg["kennwort_loeschen"]:
            optionen = {k: v for k, v in entry.options.items() if k != CONF_MODEM_KENNWORT}
            if "kennwort" in msg and not msg["kennwort_loeschen"]:
                optionen[CONF_MODEM_KENNWORT] = msg["kennwort"]
            hass.config_entries.async_update_entry(entry, options=optionen)
        lz.abruf.async_update_listeners()  # Sensor „Internetzugang“ folgt der Wahl gleich
        if daten or "kennwort" in msg:
            # WU-0009 Stufe 2: neue Wahl, Adresse oder neues Kennwort – das Gerät gleich (im Hintergrund) suchen/lesen
            entry.async_create_background_task(
                hass,
                _modem_neu(lz, suchen="zugang_wahl" in daten or "zugang_adresse" in daten),
                f"{DOMAIN}_modem_neu",
            )
        connection.send_result(msg["id"], ansichten.zugang(hass, lz))


async def _modem_neu(lz: Any, *, suchen: bool) -> None:
    if await lz.abruf.modem_jetzt(suchen=suchen):
        await lz.abruf.async_request_refresh()


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/zugang/suchen"})
@websocket_api.require_admin
@websocket_api.async_response
async def _zugang_suchen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0009: „Erneut suchen“ – den Zugang im gemeinsamen Abruf neu lesen (nur die Box, nichts absuchen)."""
    if lz := _laufzeit(hass, connection, msg):
        gesucht = await lz.abruf.zugang_suchen()
        connection.send_result(msg["id"], {**ansichten.zugang(hass, lz), "gesucht": gesucht})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/wlan"})
@websocket_api.async_response
async def _wlan(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], await ansichten.wlan(hass, lz))


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/verbrauch", vol.Optional("tage", default=30): vol.In((7, 30))}
)
@websocket_api.async_response
async def _verbrauch(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], await ansichten.verbrauch(hass, lz, msg["tage"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/protokoll",
        vol.Optional("art", default="journal"): vol.In(("journal", *ansichten.PROTOKOLL_ARTEN)),
        vol.Optional("nur_warnungen", default=False): bool,
        vol.Optional("suche", default=""): vol.All(str, vol.Length(max=100)),
        vol.Optional("grenze", default=200): vol.All(int, vol.Range(min=1, max=1000)),
    }
)
@websocket_api.async_response
async def _protokoll(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        daten = await ansichten.protokoll(
            hass, lz, msg["art"], msg["nur_warnungen"], msg["suche"], msg["grenze"]
        )
        connection.send_result(msg["id"], daten)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/einstellungen"})
@callback
def _einstellungen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        connection.send_result(msg["id"], ansichten.einstellungen(hass, lz))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/einstellungen/setzen",
        vol.Optional("tarif_down"): vol.Any(None, vol.Coerce(float)),
        vol.Optional("tarif_up"): vol.Any(None, vol.Coerce(float)),
        vol.Optional("ab"): vol.Any(None, str),
        vol.Optional("wlan_schwach"): vol.Coerce(int),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def _einstellungen_setzen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        daten = {k: msg[k] for k in ("tarif_down", "tarif_up", "ab", "wlan_schwach") if k in msg}
        try:
            await lz.einstellungen.async_setzen(daten)
        except Ungueltig as err:
            connection.send_error(msg["id"], "ungueltig", err.text(ansichten.sprache(hass)))
            return
        connection.send_result(msg["id"], ansichten.einstellungen(hass, lz))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/messplan/setzen",
        vol.Optional("an"): bool,
        vol.Optional("takt_h"): vol.Coerce(int),
        vol.Optional("von"): str,
        vol.Optional("bis"): str,
        vol.Optional("verkehr"): str,
        vol.Optional("serie"): vol.Coerce(int),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def _messplan_setzen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    if lz := _laufzeit(hass, connection, msg):
        daten = {k: msg[k] for k in ("an", "takt_h", "von", "bis", "verkehr", "serie") if k in msg}
        try:
            await lz.einstellungen.async_plan_setzen(daten)
        except Ungueltig as err:
            connection.send_error(msg["id"], "ungueltig", err.text(ansichten.sprache(hass)))
            return
        lz.abruf.plan_status = None  # neuer Plan: nicht weiter auf den alten warten
        connection.send_result(msg["id"], ansichten.einstellungen(hass, lz))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/messen"})
@websocket_api.require_admin
@websocket_api.async_response
async def _messen(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """„Jetzt messen“: startet eine Messung der Ookla-Integration (nur Admins)."""
    if lz := _laufzeit(hass, connection, msg):
        if not await lz.abruf.messen("von Hand"):
            connection.send_error(
                msg["id"], "ookla_fehlt", _tr(hass, "Die Ookla-Integration ist nicht eingerichtet.")
            )
            return
        connection.send_result(msg["id"], ansichten.einstellungen(hass, lz))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/serie"})
@websocket_api.require_admin
@websocket_api.async_response
async def _serie(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0001: Serie „n× messen“ starten (nur Admins); Antwort wie heimnetz/einstellungen."""
    if lz := _laufzeit(hass, connection, msg):
        if not lz.abruf.serie_starten():
            connection.send_error(
                msg["id"],
                "nicht_moeglich",
                _tr(hass, "Es läuft schon eine Serie oder Ookla fehlt."),
            )
            return
        connection.send_result(msg["id"], ansichten.einstellungen(hass, lz))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/einrichtung"})
@websocket_api.require_admin
@websocket_api.async_response
async def _einrichtung(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0007: was eingerichtet ist und was fehlt (nur Admins; nur lesen, auch ohne geladene Einrichtung)."""
    connection.send_result(msg["id"], await einrichtung.bewertung(hass))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/modem",
        vol.Required("adresse"): vol.All(str, vol.Length(max=60)),
        vol.Optional("kennwort"): vol.Any(None, str),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def _modem(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """WU-0008: Rohdaten eines vorgeschalteten Modems abfragen (nur Admins; nur lesen). Das Kennwort wird nur für
    diese Abfrage verwendet, nie gespeichert und steht in keiner Antwort; die Rohdaten kommen geschwärzt zurück."""
    kennwort = msg.get("kennwort")
    sperre = None
    hinterlegt_abgelehnt = False
    adresse = msg["adresse"].strip()
    for e in hass.config_entries.async_loaded_entries(DOMAIN):
        dienst = e.runtime_data.abruf.modem
        sperre = dienst.sperre  # nie zugleich mit dem laufenden Abruf am Gerät
        if not kennwort and adresse == _hinterlegt_fuer(e.runtime_data):
            # WU-0009: ohne eingetipptes Kennwort das in ⚙ › Zugang hinterlegte – nur für genau diese Adresse und
            # nicht, wenn das Gerät genau dieses schon abgelehnt hat (nur ein frisch eingetipptes wird versucht)
            hinterlegt = e.options.get(CONF_MODEM_KENNWORT) or None
            if dienst.kennwort_abgelehnt(adresse, hinterlegt):
                hinterlegt_abgelehnt = True
            else:
                kennwort = hinterlegt
    s = ansichten.sprache(hass)
    antwort = await modem.abfragen(hass, msg["adresse"], kennwort, s, sperre)
    if hinterlegt_abgelehnt and antwort.get("befund") is None:
        antwort = {
            **antwort,
            "befund": "anmeldung_abgelehnt",
            "hinweis": ve.befund_daten("anmeldung_abgelehnt", s),
        }
    connection.send_result(msg["id"], antwort)


def _hinterlegt_fuer(lz: Any) -> str:
    """Adresse, für die das hinterlegte Kennwort gilt: die gespeicherte, sonst die des gefundenen Geräts."""
    return lz.einstellungen.wert.zugang_adresse or lz.abruf.modem.adresse or ""


BEFEHLE = (
    _uebersicht,
    _speedtest,
    _speedtest_kachel,
    _messung_loeschen,
    _geraete,
    _geraet,
    _geraet_art,
    _mobilfunk,
    _internet,
    _zugang,
    _zugang_setzen,
    _zugang_suchen,
    _wlan,
    _verbrauch,
    _protokoll,
    _einstellungen,
    _einstellungen_setzen,
    _messplan_setzen,
    _messen,
    _serie,
    _einrichtung,
    _modem,
)


def mit_sprache_registrieren(hass: HomeAssistant, befehl: Any) -> None:
    """Befehl registrieren, der zusätzlich das Feld `sprache` der Seite annimmt (WU-0006): Texte der Antwort folgen
    dann der Sprache im Profil des Nutzers statt der von Home Assistant. Gesetzt wird sie nur für diesen Aufruf –
    die Aufgabe, die `async_response` startet, übernimmt sie beim Anlegen."""
    befehl_typ = befehl._ws_command  # noqa: SLF001
    schema = befehl._ws_schema  # noqa: SLF001
    feld = {vol.Optional("sprache"): vol.All(str, vol.Length(max=20))}
    if schema is False:  # Befehl ohne eigene Felder
        schema = messages.BASE_COMMAND_MESSAGE_SCHEMA.extend(
            {vol.Required("type"): befehl_typ, **feld}
        )
    else:
        schema = schema.extend(feld)

    @callback
    @functools.wraps(befehl)
    def mit_sprache(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        marke = SEITEN_SPRACHE.set(msg.get("sprache"))
        try:
            befehl(hass, connection, msg)
        finally:
            SEITEN_SPRACHE.reset(marke)

    websocket_api.async_register_command(hass, befehl_typ, mit_sprache, schema)


@callback
def registrieren(hass: HomeAssistant) -> None:
    for befehl in BEFEHLE:
        mit_sprache_registrieren(hass, befehl)
