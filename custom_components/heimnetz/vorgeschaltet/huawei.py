"""Baustein Huawei HiLink über die Bibliothek huawei-lte-api (dieselbe wie die Integration huawei_lte von Home
Assistant). Läuft im Executor (die Bibliothek arbeitet mit requests).

Nur lesend: `device/basic_information`, `device/signal`, `net/current-plmn`, `monitoring/traffic-statistics`; dazu
Anmelden/Abmelden (`user/login`, `user/logout`) mit dem Kennwort des Besitzers, höchstens ein Versuch. Die Bibliothek
bekommt eine eigene requests-Session (`netz.requests_session`): nur diese Adresse, keine Weiterleitung, Größe begrenzt.

Ist die Integration huawei_lte in Home Assistant eingerichtet, fragt Heimnetz das Gerät nicht selbst (sonst stört die
zweite Anmeldung deren Sitzung) – dann gelten deren Entitäten (`integrationen.py`).

Die Bibliothek schreibt im Debug-Protokoll das Kennwort mit („Password: …“ in Connection, Anmeldedaten in Session) –
der Filter unten verwirft diese Zeilen, egal welche Protokollstufe eingestellt ist.
"""

from __future__ import annotations

import logging
from typing import Any

from ..logik.sprache import merke, t
from ..logik.vorgeschaltet import huawei as lh
from .netz import ZEIT_S, Lauf, basis_url, requests_session
from .zte import Lesung

_N_BASIS = merke("Huawei: Gerät")
_N_ANMELDUNG = merke("Anmeldung")
_N_SIGNAL = merke("Huawei: Signal")
_N_NETZ = merke("Huawei: Netz")
_N_VERKEHR = merke("Huawei: Verbindung")


class _OhneKennwort(logging.Filter):
    """Verwirft Protokollzeilen der Bibliothek, die Anmeldedaten enthalten könnten."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            text = record.getMessage().lower()
        except Exception:  # lieber verwerfen als etwas Falsches schreiben
            return False
        return not any(
            w in text
            for w in ("password", "user/login", "user/challenge", "user/authentication", "username")
        )


_FILTER = _OhneKennwort()
for _name in (
    "huawei_lte_api",
    "huawei_lte_api.Connection",
    "huawei_lte_api.Session",
    "huawei_lte_api.api.User",
):
    logging.getLogger(_name).addFilter(_FILTER)


def _als_dict(wert: Any) -> dict[str, Any]:
    return dict(wert) if isinstance(wert, dict) else {}


def lesen(lauf: Lauf, kennwort: str | None) -> Lesung:
    """Blockierend (Executor). Stufen landen in `lauf` (für 🔬 Diagnose). Läuft nach dem Zeitlimit des Aufrufers
    womöglich weiter (ein Thread lässt sich nicht abbrechen); die Zeitlimits je Anfrage (ZEIT_S) begrenzen das."""
    from huawei_lte_api.Client import Client  # noqa: PLC0415 – erst hier, die Bibliothek ist nur dafür nötig
    from huawei_lte_api.Connection import Connection  # noqa: PLC0415
    from huawei_lte_api.exceptions import (  # noqa: PLC0415
        LoginErrorInvalidCredentialsException,
        LoginErrorUsernamePasswordOverrunException,
        ResponseErrorException,
        ResponseErrorLoginRequiredException,
    )
    from requests import RequestException  # noqa: PLC0415

    lesung = Lesung()
    session = requests_session(lauf.adresse)
    try:
        conn = Connection(basis_url(lauf.adresse), timeout=ZEIT_S, requests_session=session)
    except Exception as err:  # keine HiLink-Antwort (auch unlesbares XML) – wie nicht erreichbar
        lauf.eintrag(_N_BASIS, "fehler", type(err).__name__)
        session.close()
        lesung.befund = "nicht_erreichbar"
        return lesung
    client = Client(conn)
    try:
        try:
            basis = _als_dict(client.device.basic_information())
            lauf.ablegen("huawei_basis", basis)
            lauf.eintrag(_N_BASIS, "ok", lh.modell(basis) or t("gelesen", lauf.sprache))
        except Exception as err:  # Netz, Fehlercode des Geräts, unlesbares XML
            lauf.eintrag(_N_BASIS, "fehler", type(err).__name__)
        if kennwort:
            try:
                client.user.login("admin", kennwort, force_new_login=True)
            except LoginErrorUsernamePasswordOverrunException:
                lauf.eintrag(_N_ANMELDUNG, "aus", t("gesperrt", lauf.sprache))
                lesung.befund = "gesperrt"
            except LoginErrorInvalidCredentialsException:
                lauf.eintrag(_N_ANMELDUNG, "fehler", t("abgelehnt", lauf.sprache))
                lesung.befund = "anmeldung_abgelehnt"
            except (RequestException, ResponseErrorException) as err:
                lauf.eintrag(_N_ANMELDUNG, "fehler", type(err).__name__)
            else:
                lesung.angemeldet = True
                lauf.eintrag(_N_ANMELDUNG, "ok", t("angenommen", lauf.sprache))
        teile: dict[str, dict[str, Any]] = {}
        for schluessel, name, abfrage in (
            ("signal", _N_SIGNAL, client.device.signal),
            ("plmn", _N_NETZ, client.net.current_plmn),
            ("verkehr", _N_VERKEHR, client.monitoring.traffic_statistics),
        ):
            try:
                teile[schluessel] = _als_dict(abfrage())
            except ResponseErrorLoginRequiredException:
                lauf.eintrag(name, "aus", t("nur mit Anmeldung", lauf.sprache))
                continue
            except Exception as err:  # Netz, Fehlercode des Geräts, unlesbares XML
                lauf.eintrag(name, "fehler", type(err).__name__)
                continue
            n = lauf.ablegen(f"huawei_{schluessel}", teile[schluessel])
            lauf.eintrag(name, "ok", t("{n} Werte", lauf.sprache, n=n))
        if "signal" in teile:
            lesung.mobil = lh.aus_hilink(teile["signal"], teile.get("plmn"), teile.get("verkehr"))
        if lesung.angemeldet:
            try:
                client.user.logout()
            except RequestException, ResponseErrorException:
                pass
    finally:
        conn.close()
        session.close()
    if lesung.befund is None and lesung.mobil is None:
        lesung.befund = "keine_werte" if kennwort else "ohne_kennwort"
    return lesung


def probe(lauf: Lauf) -> str | None:
    """Blockierend: Modell aus `device/basic_information` (ohne Anmeldung); None, wenn es keine HiLink-Antwort ist."""
    session = requests_session(lauf.adresse)
    try:
        from huawei_lte_api.Client import Client  # noqa: PLC0415
        from huawei_lte_api.Connection import Connection  # noqa: PLC0415

        with Connection(basis_url(lauf.adresse), timeout=ZEIT_S, requests_session=session) as conn:
            return lh.modell(_als_dict(Client(conn).device.basic_information()))
    except Exception:  # alles, was keine HiLink-Antwort ist (auch: Bibliothek fehlt)
        return None
    finally:
        session.close()
