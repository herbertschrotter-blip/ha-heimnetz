"""Baustein TP-Link LTE/5G-Router über die Bibliothek tplinkrouterc6u (AlexandrErohin/TP-Link-Archer-C6U, GPL-3.0;
nur als Abhängigkeit installiert). Executor, requests.

Die Gerätefamilie wird nur mit Abfragen OHNE Anmeldung bestimmt – mit den Schlüssel-Abfragen der Bibliothek, die vor
jeder Anmeldung laufen (`cgi/getParm`, `cgi/getGDPRParm`): MR600 (ECC-Schlüssel als JSON), EX (`getGDPRParm`), MR
(`getParm` mit `seq`), MR200 (`getParm` ohne `seq`). Nicht `supports()` und nicht `TplinkRouterProvider.get_client()`:
die melden sich bei mehreren Clients (EX-, MR-GCM) in Wahrheit an und probieren so mehrere Kennwörter-Versuche.
Danach genau ein `authorize()` je Abruf, nur mit Kennwort; dann `get_lte_status()` und `logout()`.

Die Verschlüsselungs-Variante einer Familie (CBC, GCM, GCM mit OAEP) lässt sich ohne Anmeldung nicht unterscheiden;
genommen wird je Familie die der neueren Firmware (GCM) – passt sie nicht, meldet das Gerät „abgelehnt“ (am Gerät
prüfen). Wiederholungen der Bibliothek bei HTTP 500/406 sind auf eine Anfrage begrenzt (`REQUEST_RETRIES = 1`).
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from requests import RequestException

from ..logik.sprache import merke, t
from ..logik.vorgeschaltet import tplink as lt
from .netz import ZEIT_S, Lauf, requests_session
from .zte import Lesung

_N_ART = merke("TP-Link: Gerätefamilie")
_N_ANMELDUNG = merke("Anmeldung")
_N_LTE = merke("TP-Link: Mobilfunk")


def _familien() -> list[tuple[str, type[Any], str]]:
    """(Familie, Client für die Anmeldung, Schlüssel-Abfrage ohne Anmeldung) – Reihenfolge der Proben."""
    from tplinkrouterc6u.client.ex import TPLinkEXClientGCM  # noqa: PLC0415
    from tplinkrouterc6u.client.mr import TPLinkMR600Client, TPLinkMRClientGCM  # noqa: PLC0415
    from tplinkrouterc6u.client.mr200 import TPLinkMR200Client  # noqa: PLC0415

    return [
        ("MR600", TPLinkMR600Client, "_req_ecc_key"),
        ("EX", TPLinkEXClientGCM, "_req_rsa_key"),
        ("MR", TPLinkMRClientGCM, "_req_rsa_key"),
        ("MR200", TPLinkMR200Client, "_get_params"),
    ]


def _client(klasse: type[Any], adresse: str, kennwort: str, session: Any) -> Any:
    c = klasse(f"http://{adresse}", kennwort, logger=None, verify_ssl=False, timeout=ZEIT_S)
    c.req = session  # nur diese Adresse (netz.requests_session)
    c.REQUEST_RETRIES = 1
    return c


def familie(adresse: str, session: Any) -> tuple[str, Any] | None:
    """Blockierend: Gerätefamilie nur über Schlüssel-Abfragen ohne Anmeldung – (Familie, Client-Klasse) oder None."""
    for name, klasse, probe in _familien():
        try:
            getattr(_client(klasse, adresse, "", session), probe)()
        except Exception:  # passt nicht – nächste Familie (keine Anmeldung dabei)
            continue
        return name, klasse
    return None


def abgelehnt(err: Exception) -> bool:
    """Lehnt das Gerät das Kennwort ab? AuthorizeError, oder die Bibliothek nennt Login/Kennwort im Fehler."""
    text = str(err).lower()
    return type(err).__name__ == "AuthorizeError" or "login failed" in text or "password" in text


def lesen(lauf: Lauf, kennwort: str | None) -> Lesung:
    """Blockierend (Executor). Läuft nach dem Zeitlimit des Aufrufers womöglich noch weiter (ein Thread lässt sich
    nicht abbrechen) – die Zeitlimits je Anfrage (ZEIT_S) begrenzen das."""
    session = requests_session(lauf.adresse)
    lesung = Lesung()
    try:
        gefunden = familie(lauf.adresse, session)
        if gefunden is None:
            lauf.eintrag(_N_ART, "aus", t("nicht erkannt", lauf.sprache))
            lesung.befund = "nicht_unterstuetzt"
            return lesung
        name, klasse = gefunden
        lauf.eintrag(_N_ART, "ok", name)
        if not kennwort:
            lesung.befund = "ohne_kennwort"  # ohne Kennwort keine Anmeldung, auch keine mit leerem
            return lesung
        router = _client(klasse, lauf.adresse, kennwort, session)
        try:
            router.authorize()  # genau ein Versuch
        except RequestException as err:  # Netz weg – kein Urteil über das Kennwort
            lauf.eintrag(_N_ANMELDUNG, "fehler", type(err).__name__)
            lesung.befund = "nicht_erreichbar"
            return lesung
        except Exception as err:  # die Bibliothek meldet Ablehnung und Netzfehler gleichermaßen als ClientException
            if abgelehnt(err):
                lauf.eintrag(_N_ANMELDUNG, "fehler", t("abgelehnt", lauf.sprache))
                lesung.befund = "anmeldung_abgelehnt"
            else:  # kein Urteil über das Kennwort – kein Merker, nächster Takt versucht es wieder
                lauf.eintrag(_N_ANMELDUNG, "fehler", type(err).__name__)
                lesung.befund = "fehler"
            return lesung
        lesung.angemeldet = True
        lauf.eintrag(_N_ANMELDUNG, "ok", t("angenommen", lauf.sprache))
        try:
            status = router.get_lte_status()
            d = asdict(status) if is_dataclass(status) and not isinstance(status, type) else {}
            n = lauf.ablegen("tplink_lte", d)
            lauf.eintrag(_N_LTE, "ok", t("{n} Werte", lauf.sprache, n=n))
            lesung.mobil = lt.aus_lte_status(d)
        except Exception as err:  # Gerät ohne Mobilfunk-Teil oder andere Firmware
            lauf.eintrag(_N_LTE, "fehler", type(err).__name__)
        try:
            router.logout()
        except Exception:  # Abmelden ist eine Höflichkeit
            pass
    finally:
        session.close()
    if lesung.befund is None and lesung.mobil is None:
        lesung.befund = "keine_werte"
    return lesung
