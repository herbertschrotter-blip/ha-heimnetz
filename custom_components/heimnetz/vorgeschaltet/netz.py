"""Gemeinsamer, sicherer Zugriff auf die Weboberfläche eines vorgeschalteten Geräts (WU-0008/WU-0009).

Für alle Bausteine gleich: nur die eine private Adresse (`logik.modem.adresse_erlaubt`, keine Hostnamen), keine
Weiterleitungen, Zeitlimit je Anfrage, Obergrenze für die Antwortgröße, Gesamtzeit; http zuerst, https ohne
Zertifikatsprüfung nur zu genau dieser Adresse (auch, wenn die Startseite per http dorthin weiterleitet). Zwei Wege:
- `Lauf` (aiohttp, im Event-Loop) für die eigenen Bausteine (ZTE goform/ubus, Erkennen),
- `requests_session` (requests, im Executor) für die Bibliotheken huawei-lte-api und tplinkrouterc6u: eigener
  Adapter, der jede Anfrage an eine andere Adresse ablehnt und die Größe begrenzt. Weiterleitungen gibt es dort nur
  innerhalb derselben Adresse (HiLink leitet „/“ auf „/html/index.html“ weiter) – eine auf einen anderen Host lehnt
  der Adapter ab, höchstens drei hintereinander.

`Lauf` sammelt jede Stufe als Eintrag (für 🔬 Diagnose); Rohdaten werden nur geschwärzt abgelegt
(`logik.modem.schwaerzen`). Kennwörter stehen in keinem Eintrag und in keinem Protokoll.
"""

from __future__ import annotations

import ipaddress
import json
import re
import time
from typing import Any
from urllib.parse import urlsplit

import aiohttp
import requests
from requests.adapters import HTTPAdapter

from ..logik import modem as lm
from ..logik.sprache import DE, t

ZEIT_S = 8  # Zeitlimit je Anfrage
SUCHE_ZEIT_S = 4  # beim Suchen kürzer: es sind bis zu fünf Adressen
GESAMT_S = 40  # Gesamtzeit einer Abfrage
GROESSE_MAX = 512 * 1024  # 512 KB je Antwort


def _host(adresse: str) -> str:
    """Adresse für eine URL (IPv6 in Klammern)."""
    ip = ipaddress.ip_address(adresse)
    return f"[{ip}]" if ip.version == 6 else str(ip)


def gleiche_adresse(url: str, adresse: str) -> bool:
    """Geht die URL genau an diese Adresse? (Schutz gegen jede Anfrage an einen anderen Host.)"""
    try:
        host = urlsplit(url).hostname or ""
        return ipaddress.ip_address(host) == ipaddress.ip_address(adresse)
    except ValueError:
        return False


def neue_session(zeitlimit: aiohttp.ClientTimeout) -> aiohttp.ClientSession:
    """Eigene kurzlebige Session mit Cookie-Jar für die Anmeldung (Cookies auch für IP-Adressen: `unsafe=True`)."""
    return aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=zeitlimit)


def json_wert(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return None


def gekuerzt(text: str, grenze: int = 2000) -> str:
    """Rohantwort gekürzt, damit der Entwickler eine gescheiterte Stufe nachbessern kann."""
    knapp = text.strip()
    return knapp if len(knapp) <= grenze else knapp[:grenze] + " …"


def titel(startseite: str) -> str:
    treffer = re.search(r"<title>(.*?)</title>", startseite, re.IGNORECASE | re.DOTALL)
    return treffer.group(1).strip()[:120] if treffer else ""


class Lauf:
    """Eine Abfrage an genau einer Adresse: sammelt die Stufen, achtet auf die Gesamtzeit."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        adresse: str,
        sprache: str = DE,
        *,
        zeit_s: float = ZEIT_S,
        gesamt_s: float = GESAMT_S,
        roh: bool = True,
    ) -> None:
        self.session = session
        self.adresse = adresse
        self.sprache = sprache
        self.zeit_s = zeit_s
        self.gesamt_s = gesamt_s
        self.roh = roh  # Rohdaten ablegen (Diagnose); beim laufenden Abruf nur zählen
        self.start = time.monotonic()
        self.abfragen: list[dict[str, Any]] = []
        self.daten: dict[str, Any] = {}
        self.geschwaerzt = 0
        self.basis = ""
        self.kopf: dict[str, str] = {}

    def zeit_uebrig(self) -> bool:
        return (time.monotonic() - self.start) < self.gesamt_s

    def eintrag(self, name: str, status: str, angabe: str) -> None:
        self.abfragen.append({"name": t(name, self.sprache), "status": status, "angabe": angabe})

    def ablegen(self, schluessel: str, rohdaten: Any) -> int:
        """Rohdaten geschwärzt ablegen; gibt die Anzahl der Werte zurück."""
        rein, anzahl = lm.schwaerzen(rohdaten)
        if self.roh:
            self.daten[schluessel] = rein
            self.geschwaerzt += anzahl
        return lm.werte_zaehlen(rein)

    async def lesen(
        self,
        pfad: str,
        *,
        methode: str = "GET",
        daten: Any = None,
        json_: Any = None,
        referer: str | None = None,
        zusatz: dict[str, str] | None = None,
    ) -> tuple[int, str]:
        """Eine Anfrage an `basis + pfad`; keine Weiterleitung, Zeitlimit, Antwortgröße begrenzt. (Status, Text).
        `zusatz`: weitere Kopfzeilen der Anfrage."""
        url = f"{self.basis}{pfad}"
        if not gleiche_adresse(url, self.adresse):
            raise aiohttp.InvalidURL(url)
        kopf = {**({"Referer": referer} if referer else {}), **(zusatz or {})} or None
        async with self.session.request(
            methode,
            url,
            data=daten,
            json=json_,
            headers=kopf,
            allow_redirects=False,
            ssl=False if url.startswith("https:") else None,
            timeout=aiohttp.ClientTimeout(total=self.zeit_s),
        ) as antwort:
            roh = await antwort.content.read(GROESSE_MAX + 1)
            self.kopf = {
                k: v for k, v in antwort.headers.items() if k.lower() in ("server", "location")
            }
            return antwort.status, roh[:GROESSE_MAX].decode("utf-8", "replace")

    async def startseite(self) -> str | None:
        """Startseite: http zuerst, https (ohne Zertifikatsprüfung) nur, wenn http nicht antwortet oder auf https an
        genau diese Adresse weiterleitet (ZTE G5TC, GitHub #2). Setzt `basis`."""
        host = _host(self.adresse)
        for schema in ("http", "https"):
            self.basis = f"{schema}://{host}"
            try:
                status, text = await self.lesen("/")
            except aiohttp.ClientError, TimeoutError, ValueError:
                continue
            if schema == "http" and (ziel := self._auf_https(status)):
                self.basis, pfad = ziel
                try:
                    _, text = await self.lesen(pfad)
                except aiohttp.ClientError, TimeoutError, ValueError:
                    self.basis = f"http://{host}"
            return text
        self.basis = ""
        return None

    def _auf_https(self, status: int) -> tuple[str, str] | None:
        """Leitet die Antwort auf https an genau diese Adresse weiter? (Basis, Pfad) – sonst None."""
        ziel = self.kopf.get("Location") or self.kopf.get("location") or ""
        if not 300 <= status < 400 or not ziel.lower().startswith("https://"):
            return None
        teile = urlsplit(ziel)
        if teile.username or teile.password or not gleiche_adresse(ziel, self.adresse):
            return None
        try:
            port = teile.port
        except ValueError:
            return None
        basis = f"https://{_host(self.adresse)}" + (f":{port}" if port else "")
        return basis, (teile.path or "/") + (f"?{teile.query}" if teile.query else "")


# ── requests (für die Bibliotheken, im Executor) ──
class _NurDieseAdresse(HTTPAdapter):
    """HTTP-Adapter: nur Anfragen an `adresse`, Antwort höchstens GROESSE_MAX, Zeitlimit ZEIT_S, keine Proxys."""

    def __init__(self, adresse: str) -> None:
        super().__init__(max_retries=0)
        self._adresse = adresse

    def send(  # type: ignore[override]
        self,
        request: requests.PreparedRequest,
        stream: bool = False,
        timeout: Any = None,
        verify: Any = True,
        cert: Any = None,
        proxies: Any = None,
    ) -> requests.Response:
        if not gleiche_adresse(request.url or "", self._adresse):
            raise requests.ConnectionError("Heimnetz: Anfrage an eine andere Adresse abgelehnt")
        antwort = super().send(
            request, stream=True, timeout=ZEIT_S, verify=False, cert=cert, proxies={}
        )
        roh = antwort.raw.read(GROESSE_MAX + 1, decode_content=True)
        if len(roh) > GROESSE_MAX:
            antwort.close()
            raise requests.ConnectionError("Heimnetz: Antwort zu groß")
        antwort._content = roh  # noqa: SLF001 – gelesen ist gelesen, die Bibliothek nimmt .text/.content
        antwort._content_consumed = True  # noqa: SLF001
        return antwort


def requests_session(adresse: str) -> requests.Session:
    """requests-Session für eine Bibliothek: nur diese Adresse (auch nach einer Weiterleitung), keine Proxys."""
    s = requests.Session()
    s.max_redirects = 3  # nur innerhalb der Adresse – jede Anfrage geht durch den Adapter, der fremde Hosts ablehnt
    s.trust_env = False
    s.verify = False
    adapter = _NurDieseAdresse(adresse)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


def basis_url(adresse: str) -> str:
    return f"http://{_host(adresse)}/"
