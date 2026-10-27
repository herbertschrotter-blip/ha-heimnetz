"""Bausteine ZTE goform und ZTE ubus über das Netz (dünn; Anfragen bauen und Antworten lesen: `logik.vorgeschaltet.zte`).

Nur lesen: goform `goform_get_cmd_process`; `goform_set_cmd_process` ausschließlich mit `goformId=LOGIN`/`LOGOUT`.
ubus nur mit den Methoden aus `UBUS_ERLAUBT` (Anmelden, Abmelden, Lesen). Höchstens ein Anmeldeversuch je Abruf,
nur mit dem Kennwort des Besitzers; abgelehnt → Befund, der Aufrufer versucht es nicht wieder.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import aiohttp

from ..logik import modem as lm
from ..logik.mobil import Mobilfunk
from ..logik.sprache import merke, t
from ..logik.vorgeschaltet import zte as lz
from .netz import Lauf, gekuerzt

# Breite Liste lesender Werte für die Diagnose (was das Gerät nicht kennt, kommt leer zurück)
DIAGNOSE_FELDER = (
    "modem_main_state,modem_model,hardware_version,wa_inner_version,cr_version,web_version,"
    "network_type,network_provider,rmcc,rmnc,signalbar,rssi,ppp_status,realtime_time,"
    "lte_rsrp,lte_rsrq,lte_rssi,lte_snr,lte_band,lte_ca_pcell_band,lte_ca_scell_band,lte_pci,"
    "lte_ca_pcell_freq,lte_ca_scell_freq,cell_id,lte_cell_id,enodeb_id,tac,lac,plmn,"
    "nr5g_action_band,nr5g_pci,nr5g_cell_id,nr5g_action_channel,nr5g_rsrp,nr5g_rsrq,nr5g_snr,"
    "Z5g_rsrp,Z5g_rsrq,Z5g_snr,Z5g_SINR,Z5g_CELL_ID,wan_active_band,wan_active_channel,ngbr_cell_info"
)
_LOGIN, _LOGOUT = "LOGIN", "LOGOUT"  # goform_set_cmd_process nur hiermit

_N_OHNE = merke("Werte ohne Anmeldung")
_N_ANMELDUNG = merke("Anmeldung")
_N_NACH = merke("Werte nach Anmeldung")
_N_UBUS_INFO = merke("ubus: Anmeldedaten")
_N_UBUS_ANMELDUNG = merke("ubus: Anmeldung")
_N_UBUS_WERTE = merke("ubus: Funkwerte")
_N_UBUS_VERBINDUNG = merke("ubus: Verbindung")


@dataclass
class Lesung:
    """Ergebnis eines Bausteins: Werte im gemeinsamen Format, Befund (Kennung) oder None, angemeldet?"""

    mobil: Mobilfunk | None = None
    befund: str | None = None
    angemeldet: bool = False


def _befund_ohne(mobil: Mobilfunk | None, kennwort: str | None) -> str | None:
    if mobil is not None:
        return None
    return "keine_werte" if kennwort else "ohne_kennwort"


# ── goform ──
async def goform_probe(lauf: Lauf) -> str | None:
    """Antwortet goform ohne Anmeldung mit JSON? Modell ("" wenn nicht genannt) oder None."""
    try:
        _, text = await lauf.lesen(
            "/goform/goform_get_cmd_process?isTest=false&multi_data=1&cmd=modem_model",
            referer=f"{lauf.basis}/index.html",
        )
    except aiohttp.ClientError, TimeoutError:
        return None
    return lz.goform_modell(lz.json_objekt(text))


async def _goform_werte(
    lauf: Lauf, felder: str, schluessel: str, name: str
) -> dict[str, Any] | None:
    try:
        status, text = await lauf.lesen(
            f"/goform/goform_get_cmd_process?isTest=false&multi_data=1&cmd={felder}",
            referer=f"{lauf.basis}/index.html",
        )
    except (aiohttp.ClientError, TimeoutError) as err:
        lauf.eintrag(name, "fehler", type(err).__name__)
        return None
    werte = lz.json_objekt(text)
    if werte is None:
        lauf.ablegen(schluessel, {"rohdaten": gekuerzt(text)})
        lauf.eintrag(name, "fehler", f"HTTP {status}")
        return None
    anzahl = lauf.ablegen(schluessel, werte)
    lauf.eintrag(name, "ok", t("{n} Werte", lauf.sprache, n=anzahl))
    return werte


async def _goform_anmelden(lauf: Lauf, kennwort: str) -> str:
    """Normales Web-Login (LD-Wert holen, Hash bilden, goformId=LOGIN) – genau ein Versuch. „ok“, „abgelehnt“ oder
    „fehler“ (Netz, keine lesbare Antwort – kein Urteil über das Kennwort)."""
    referer = f"{lauf.basis}/index.html"
    try:
        _, text = await lauf.lesen(
            "/goform/goform_get_cmd_process?isTest=false&cmd=LD", referer=referer
        )
        ld = str((lz.json_objekt(text) or {}).get("LD", ""))
        feld = lm.anmelde_hash(kennwort, ld) if ld else kennwort
        _, antwort = await lauf.lesen(
            "/goform/goform_set_cmd_process",
            methode="POST",
            daten={"isTest": "false", "goformId": _LOGIN, "password": feld},
            referer=referer,
        )
    except (aiohttp.ClientError, TimeoutError) as err:
        lauf.eintrag(_N_ANMELDUNG, "fehler", type(err).__name__)
        return "fehler"
    ergebnis = lz.json_objekt(antwort)
    if ergebnis is None or "result" not in ergebnis:
        lauf.eintrag(_N_ANMELDUNG, "fehler", t("keine Antwort", lauf.sprache))
        return "fehler"
    ok = lz.goform_angemeldet(ergebnis)
    lauf.eintrag(
        _N_ANMELDUNG, "ok" if ok else "fehler", t("angenommen" if ok else "abgelehnt", lauf.sprache)
    )
    return "ok" if ok else "abgelehnt"


async def _goform_abmelden(lauf: Lauf) -> None:
    try:
        await lauf.lesen(
            "/goform/goform_set_cmd_process",
            methode="POST",
            daten={"isTest": "false", "goformId": _LOGOUT},
            referer=f"{lauf.basis}/index.html",
        )
    except aiohttp.ClientError, TimeoutError:
        pass  # Abmelden ist eine Höflichkeit; die Sitzung läuft am Gerät ohnehin ab


async def goform_lesen(lauf: Lauf, kennwort: str | None, diagnose: bool = False) -> Lesung:
    """Werte ohne Anmeldung, mit Kennwort einmal anmelden, Werte nach Anmeldung, abmelden."""
    felder = DIAGNOSE_FELDER if diagnose else lz.GOFORM_FELDER
    ohne = await _goform_werte(lauf, felder, "ohne_anmeldung", _N_OHNE)
    lesung = Lesung(mobil=lz.aus_werten(ohne) if ohne else None)
    if kennwort and lauf.zeit_uebrig():
        anmeldung = await _goform_anmelden(lauf, kennwort)
        if anmeldung == "ok":
            lesung.angemeldet = True
            nach = await _goform_werte(lauf, felder, "nach_anmeldung", _N_NACH)
            await _goform_abmelden(lauf)
            if nach:
                lesung.mobil = lz.aus_werten(nach) or lesung.mobil
        else:
            lesung.befund = "anmeldung_abgelehnt" if anmeldung == "abgelehnt" else "fehler"
    lesung.befund = lesung.befund or _befund_ohne(lesung.mobil, kennwort)
    return lesung


# ── ubus ──
class _Ubus:
    def __init__(self, lauf: Lauf) -> None:
        self.lauf = lauf
        self.sitzung = lz.NULL_SITZUNG
        self.nr = 1

    async def rufen(
        self, objekt: str, methode: str, argumente: dict[str, Any]
    ) -> tuple[int | None, dict[str, Any], str]:
        """Ein erlaubter Aufruf (sonst ValueError aus `ubus_anfrage`); (Code, Daten, Rohtext)."""
        koerper = lz.ubus_anfrage(self.sitzung, objekt, methode, argumente, self.nr)
        self.nr += 1
        _, text = await self.lauf.lesen(
            f"/ubus/?t={int(time.time() * 1000)}",
            methode="POST",
            json_=koerper,
            referer=f"{self.lauf.basis}/",
        )
        code, daten = lz.ubus_ergebnis(text)
        return code, daten, text


async def ubus_probe(lauf: Lauf) -> bool:
    """Antwortet ubus auf `zwrt_web.web_login_info` (ohne Sitzung, liest nur)? Dann ist es ein ZTE mit ubus."""
    try:
        code, daten, _ = await _Ubus(lauf).rufen("zwrt_web", "web_login_info", {})
    except aiohttp.ClientError, TimeoutError:
        return False
    return code == 0 and "zte_web_sault" in daten


async def ubus_lesen(lauf: Lauf, kennwort: str | None) -> Lesung:
    """Anmeldedaten lesen; mit Kennwort einmal anmelden (nicht, wenn das Gerät gesperrt ist); Funkwerte und
    Verbindung lesen; abmelden."""
    u = _Ubus(lauf)
    lesung = Lesung()
    try:
        code, info, text = await u.rufen("zwrt_web", "web_login_info", {})
    except (aiohttp.ClientError, TimeoutError) as err:
        lauf.eintrag(_N_UBUS_INFO, "fehler", type(err).__name__)
        lesung.befund = "nicht_erreichbar"
        return lesung
    if code != 0:
        lauf.ablegen("ubus_info", {"rohdaten": gekuerzt(text)})
        lauf.eintrag(_N_UBUS_INFO, "aus", t("nicht vorhanden", lauf.sprache))
        lesung.befund = "keine_werte"
        return lesung
    salz, rest = lz.ubus_login_info(info)
    lauf.ablegen("ubus_info", {"login_fail_num": rest})  # das Salz ist kein Wert für den Entwickler
    lauf.eintrag(
        _N_UBUS_INFO,
        "ok",
        t("{n} Versuche frei", lauf.sprache, n=rest)
        if rest is not None
        else t("gelesen", lauf.sprache),
    )
    if kennwort and lauf.zeit_uebrig():
        if rest is not None and rest <= 0:
            lauf.eintrag(_N_UBUS_ANMELDUNG, "aus", t("gesperrt", lauf.sprache))
            lesung.befund = "gesperrt"
        else:
            try:
                code, antwort, _ = await u.rufen(
                    "zwrt_web", "web_login", {"password": lz.ubus_hash(kennwort, salz)}
                )
            except (aiohttp.ClientError, TimeoutError) as err:
                lauf.eintrag(_N_UBUS_ANMELDUNG, "fehler", type(err).__name__)
            else:
                if code != 0:  # Fehler der Schnittstelle, kein Urteil über das Kennwort
                    lauf.eintrag(
                        _N_UBUS_ANMELDUNG, "fehler", t("Code {code}", lauf.sprache, code=code)
                    )
                    lesung.befund = "fehler"
                else:
                    sitzung = lz.ubus_sitzung(antwort)
                    lauf.eintrag(
                        _N_UBUS_ANMELDUNG,
                        "ok" if sitzung else "fehler",
                        t("angenommen" if sitzung else "abgelehnt", lauf.sprache),
                    )
                    if sitzung:
                        u.sitzung, lesung.angemeldet = sitzung, True
                    else:
                        lesung.befund = "anmeldung_abgelehnt"
    werte: dict[str, dict[str, Any]] = {}
    for objekt, methode, argumente in lz.UBUS_LESEN:
        name = _N_UBUS_WERTE if objekt == "zte_nwinfo_api" else _N_UBUS_VERBINDUNG
        if not lauf.zeit_uebrig():
            break
        try:
            code, daten, text = await u.rufen(objekt, methode, argumente)
        except (aiohttp.ClientError, TimeoutError) as err:
            lauf.eintrag(name, "fehler", type(err).__name__)
            continue
        if code == 0:
            werte[methode] = daten
            n = lauf.ablegen(f"ubus_{methode}", daten)
            lauf.eintrag(name, "ok", t("{n} Werte", lauf.sprache, n=n))
        else:
            lauf.ablegen(f"ubus_{methode}", {"rohdaten": gekuerzt(text)})
            lauf.eintrag(name, "fehler", t("Code {code}", lauf.sprache, code=code))
    if lesung.angemeldet:
        try:
            await u.rufen("zwrt_web", "web_logout", {})
        except aiohttp.ClientError, TimeoutError:
            pass
    netinfo = werte.get("nwinfo_get_netinfo")
    lesung.mobil = lz.aus_ubus(netinfo, werte.get("get_wwaniface")) if netinfo else None
    lesung.befund = lesung.befund or _befund_ohne(lesung.mobil, kennwort)
    return lesung
