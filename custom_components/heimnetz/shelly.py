"""Shelly-Steckdosen für den Wächter (Herbert, 18.11.2026): über die lokale Schnittstelle der Steckdose (RPC über HTTP,
Gen 2 und neuer) – ohne Cloud, ohne App.

Heimnetz ändert auf der Steckdose nur sein eigenes Skript „heimnetz-waechter“ und dessen zwei KVS-Schlüssel; dazu auf
Knopfdruck „kurz blinken“ (Shelly.Identify). Andere Skripte und Einstellungen der Steckdose (WLAN, Zeitpläne, Name,
Kennwort) bleiben unberührt. Wie bei vorgeschalteten Geräten: nur private Adressen, keine Weiterleitung, Zeit- und
Größengrenzen; das Kennwort kommt aus den Optionen des Eintrags, wird nur an die Steckdose geschickt und nie
protokolliert; abgelehnt kein zweiter Versuch.
"""

from __future__ import annotations

import json
import logging
import secrets
from dataclasses import dataclass
from importlib import resources
from typing import Any

import aiohttp

from .logik import waechter as wa
from .logik.modem import adresse_erlaubt
from .logik.sprache import merke

LOGGER = logging.getLogger(__package__)
ZEIT_S = 8
GROESSE_MAX = 256 * 1024


class ShellyFehler(Exception):
    """Steckdose nicht erreichbar, falsche Antwort oder abgelehnt (`abgelehnt` = Kennwort)."""

    def __init__(self, text: str, abgelehnt: bool = False) -> None:
        super().__init__(text)
        self.abgelehnt = abgelehnt


@dataclass(frozen=True)
class Info:
    adresse: str
    kennung: str  # shellyplusplugs-e465…
    modell: str  # SNPL-00112EU
    app: str  # PlusPlugS
    gen: int  # 1 = zu alt (keine Skripte)
    kennwort: bool  # auth_en

    @property
    def passt(self) -> bool:
        return self.gen >= 2


# beim Import gelesen (das läuft nicht in der Ereignisschleife), nicht bei jedem Einspielen
_CODE = resources.files(__package__).joinpath("shelly/waechter.js").read_text(encoding="utf-8")


def skript_code() -> str:
    return _CODE


class Steckdose:
    """Eine Anfrage-Folge an eine Steckdose (eine aiohttp-Session des Aufrufers)."""

    def __init__(self, session: aiohttp.ClientSession, adresse: str, kennwort: str | None) -> None:
        if not adresse_erlaubt(adresse):
            raise ShellyFehler(merke("Adresse nicht im Heimnetz"))
        self.session, self.adresse, self.kennwort = session, adresse, kennwort or None
        self._nr = 0

    async def _http(
        self, methode: str, pfad: str, daten: dict[str, Any] | None = None
    ) -> tuple[int, Any]:
        try:
            async with self.session.request(
                methode,
                f"http://{self.adresse}{pfad}",
                json=daten,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=ZEIT_S),
            ) as antwort:
                roh = await antwort.content.read(GROESSE_MAX + 1)
                if len(roh) > GROESSE_MAX:
                    raise ShellyFehler(merke("Antwort zu groß"))
                try:
                    return antwort.status, json.loads(roh or b"null")
                except ValueError:
                    return antwort.status, None
        except (aiohttp.ClientError, TimeoutError) as err:
            raise ShellyFehler(merke("nicht erreichbar")) from err

    async def info(self) -> Info:
        """GET /shelly – ohne Anmeldung (Gen 1 meldet keine „gen“)."""
        status, d = await self._http("GET", "/shelly")
        if status != 200 or not isinstance(d, dict):
            raise ShellyFehler(merke("keine Shelly"))
        return Info(
            adresse=self.adresse,
            kennung=str(d.get("id") or d.get("mac") or ""),
            modell=str(d.get("model") or d.get("type") or ""),
            app=str(d.get("app") or d.get("type") or ""),
            gen=int(d.get("gen") or 1),
            kennwort=bool(d.get("auth_en") or d.get("auth")),
        )

    async def rpc(self, methode: str, params: dict[str, Any] | None = None) -> Any:
        self._nr += 1
        anfrage: dict[str, Any] = {"id": self._nr, "method": methode, "params": params or {}}
        status, d = await self._http("POST", "/rpc", anfrage)
        if status == 401:
            if not self.kennwort:
                raise ShellyFehler(merke("Steckdose verlangt ein Kennwort"), abgelehnt=True)
            frage = (d or {}).get("error", {}).get("message") if isinstance(d, dict) else None
            try:
                werte = json.loads(frage) if isinstance(frage, str) else {}
            except ValueError:
                werte = {}
            if not werte.get("nonce"):
                raise ShellyFehler(merke("Anmeldung nicht verstanden"))
            anfrage["auth"] = wa.anmeldung(
                self.kennwort,
                str(werte.get("realm", "")),
                werte["nonce"],
                secrets.token_hex(8),
                int(werte.get("nc", 1)),
            )
            status, d = await self._http("POST", "/rpc", anfrage)
            if status == 401:
                self.kennwort = None  # kein zweiter Versuch mit demselben Kennwort
                raise ShellyFehler(merke("Kennwort der Steckdose abgelehnt"), abgelehnt=True)
        if not isinstance(d, dict):
            raise ShellyFehler(merke("falsche Antwort"))
        if "error" in d:
            raise ShellyFehler(str(d["error"].get("message", "Fehler")))
        return d.get("result")

    # ── Skript ──

    async def skript_id(self) -> int | None:
        liste = await self.rpc("Script.List")
        for s in (liste or {}).get("scripts", []):
            if s.get("name") == wa.SKRIPT_NAME:
                return int(s["id"])
        return None

    async def einspielen(self, regeln: dict[str, Any]) -> int:
        """Skript anlegen oder überschreiben, Regeln schreiben, Autostart an, starten. Zurück: id."""
        sid = await self.skript_id()
        if sid is None:
            sid = int((await self.rpc("Script.Create", {"name": wa.SKRIPT_NAME}))["id"])
        else:
            await self.rpc("Script.Stop", {"id": sid})
        await self.rpc("KVS.Set", {"key": wa.KVS_REGELN, "value": wa.kvs_text(regeln)})
        # Grundlage für Befehle: das Skript führt den ersten gelesenen Befehl nicht aus (er könnte von vor einem Neustart
        # der Steckdose stammen) – so wirkt schon der erste echte Befehl aus Heimnetz
        await self.rpc(
            "KVS.Set", {"key": wa.KVS_BEFEHL, "value": json.dumps({"x": "keiner", "n": 0})}
        )
        for i, stueck in enumerate(wa.stuecke(skript_code())):
            await self.rpc("Script.PutCode", {"id": sid, "code": stueck, "append": i > 0})
        await self.rpc("Script.SetConfig", {"id": sid, "config": {"enable": True}})
        await self.rpc("Script.Start", {"id": sid})
        return sid

    async def regeln_setzen(self, regeln: dict[str, Any]) -> None:
        """Nur die Regeln (das Skript liest sie in jeder Runde)."""
        await self.rpc("KVS.Set", {"key": wa.KVS_REGELN, "value": wa.kvs_text(regeln)})

    async def befehl(self, x: str, n: int, **werte: Any) -> None:
        await self.rpc(
            "KVS.Set", {"key": wa.KVS_BEFEHL, "value": wa.kvs_text({"x": x, "n": n, **werte})}
        )

    async def entfernen(self) -> None:
        sid = await self.skript_id()
        if sid is not None:
            await self.rpc("Script.Stop", {"id": sid})
            await self.rpc("Script.Delete", {"id": sid})
        for key in (wa.KVS_REGELN, wa.KVS_BEFEHL):
            try:
                await self.rpc("KVS.Delete", {"key": key})
            except ShellyFehler:
                continue  # Schlüssel gab es nicht

    async def stand(self) -> wa.Dosenstand:
        """Zustand des Skripts und Leistung; nicht erreichbar → Dosenstand(erreichbar=False)."""
        try:
            leistung = (await self.rpc("Switch.GetStatus", {"id": 0}) or {}).get("apower")
            sid = await self.skript_id()
            if sid is None:
                return wa.dosenstand(None, leistung)
            # über Script.Eval statt GET /script/…/status: so gilt die Anmeldung wie für jede andere Anfrage
            antwort = await self.rpc("Script.Eval", {"id": sid, "code": "status()"})
            try:
                d = json.loads((antwort or {}).get("result") or "null")
            except ValueError:
                d = None
            return wa.dosenstand(d, leistung)
        except ShellyFehler:
            return wa.Dosenstand(erreichbar=False)

    async def leistung(self) -> float | None:
        return (await self.rpc("Switch.GetStatus", {"id": 0}) or {}).get("apower")

    async def blinken(self) -> None:
        await self.rpc("Shelly.Identify")
