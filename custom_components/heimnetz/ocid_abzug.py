"""OpenCellID-Datenabzug für Österreich holen – im Hintergrund, einmal im Monat, nur mit eigenem Schlüssel (WU-0002).

Geladen wird die Datei des ganzen Landes (MCC 232) in Stücken in eine temporäre Datei im Ordner der Integration (nicht in
den Speicher); entpackt und ausgewertet wird Zeile für Zeile, behalten werden nur die Zellen im Ausschnitt der OSM-Masten
(logik/osm.rahmen). Hinaus geht nur der Schlüssel, kein Standort.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import itertools
import os
import tempfile
from pathlib import Path
from typing import IO, Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_OPENCELLID, DOMAIN
from .gemerkt import GemerkterAbruf
from .logik import karte as ka
from .logik import ocid as lc
from .logik import osm as lo

URL = "https://opencellid.org/ocid/downloads"
LAND = "232"  # Österreich
ZEIT_S = 300
# Österreich gepackt: einige MB (2026); mehr lädt die Integration nicht – reichlich Luft, schützt aber die Speicherkarte
GROESSTE = 64 * 1024 * 1024
SCHUB = 1 << 22  # so viel sammelt der Download, bevor er (im Executor) in die Datei schreibt


class OcidAbzug(GemerkterAbruf):
    NAME = "OpenCellID-Abzug"
    SPEICHER = "ocid"
    FELD = "zellen"
    GUELTIG_S = lc.GUELTIG_S
    NOCHMAL_S = lc.NOCHMAL_S

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self._zellen: tuple[Any, list[lc.OcidZelle]] = (None, [])
        self._infos: tuple[Any, list[lc.MastInfo | None]] = (None, [])

    async def infos(self, wohnung: ka.Ort, masten: list[ka.Ort]) -> list[lc.MastInfo | None]:
        """Anbieter und Technik je Mast; gerechnet nur, wenn sich Abzug oder Masten geändert haben."""
        schluessel = (self.entry.options.get(CONF_OPENCELLID) or "").strip()
        if not schluessel or not masten:
            return [None] * len(masten)
        r = lo.rahmen(wohnung)
        # Ausschnitt und Schlüssel zusammen: neuer Schlüssel = neuer Versuch
        kennung = (
            ",".join(f"{x:.1f}" for x in r)
            + "|"
            + hashlib.sha256(schluessel.encode()).hexdigest()[:8]
        )
        liste = await self._gemerkt(kennung, schluessel, r)
        if self._zellen[0] != self.stand:
            self._zellen = (
                self.stand,
                [lc.OcidZelle(t, mnc, ka.Ort(la, lo_)) for t, mnc, la, lo_ in liste],
            )
        zellen = self._zellen[1]
        if not zellen:
            return [None] * len(masten)
        schl = (self.stand, tuple((m.lat, m.lon) for m in masten))
        if self._infos[0] != schl:
            self._infos = (schl, await self.hass.async_add_executor_job(lc.je_mast, masten, zellen))
        return self._infos[1]

    async def _abrufen(self, *args: Any) -> list[Any]:
        schluessel, r = args
        datei = await self.hass.async_add_executor_job(_temp_oeffnen, self.hass.config.path(DOMAIN))
        try:
            await self._laden(schluessel, datei)
            zellen = await self.hass.async_add_executor_job(_auswerten, Path(datei.name), r)
        finally:
            await self.hass.async_add_executor_job(_temp_weg, datei)
        return [[z.technik, z.mnc, z.ort.lat, z.ort.lon] for z in zellen]

    async def _laden(self, schluessel: str, datei: IO[bytes]) -> None:
        """Download in Schüben in die Datei – im Speicher liegen höchstens SCHUB Bytes."""
        puffer, gesamt = bytearray(), 0
        async with async_get_clientsession(self.hass).get(
            URL,
            params={"token": schluessel, "type": "mcc", "file": f"{LAND}.csv.gz"},
            timeout=aiohttp.ClientTimeout(total=ZEIT_S),
        ) as antwort:
            antwort.raise_for_status()
            async for stueck in antwort.content.iter_chunked(1 << 16):
                puffer += stueck
                gesamt += len(stueck)
                if gesamt > GROESSTE:
                    raise ValueError("Abzug größer als erwartet")
                if len(puffer) >= SCHUB:
                    await self.hass.async_add_executor_job(datei.write, bytes(puffer))
                    puffer.clear()
        if puffer:
            await self.hass.async_add_executor_job(datei.write, bytes(puffer))
        await self.hass.async_add_executor_job(datei.flush)


def _temp_oeffnen(ordner: str) -> IO[bytes]:
    """Blockierend: temporäre Datei im Ordner der Integration (auf der Platte, nicht im RAM wie oft /tmp). Was ein
    früherer Abzug liegen ließ (Absturz, Stromausfall), kommt vorher weg – nur `.ocid-*.tmp` in diesem Ordner."""
    os.makedirs(ordner, exist_ok=True)
    _reste_weg(ordner)
    return tempfile.NamedTemporaryFile(dir=ordner, prefix=".ocid-", suffix=".tmp", delete=False)  # noqa: SIM115


def _reste_weg(ordner: str) -> None:
    for alt in Path(ordner).glob(".ocid-*.tmp"):
        if alt.is_file() or alt.is_symlink():
            try:
                alt.unlink()
            except OSError:
                pass


def _temp_weg(datei: IO[bytes]) -> None:
    datei.close()
    try:
        os.remove(datei.name)
    except FileNotFoundError:
        pass


def _auswerten(daten: bytes | Path, r: tuple[float, float, float, float]) -> list[lc.OcidZelle]:
    """Blockierend: Zeile für Zeile entpacken und filtern (wenig Speicher, auch bei großer Datei)."""
    if isinstance(daten, Path):
        with daten.open("rb") as f:
            return _auswerten_strom(f, r)
    return _auswerten_strom(io.BytesIO(daten), r)


def _auswerten_strom(roh: IO[bytes], r: tuple[float, float, float, float]) -> list[lc.OcidZelle]:
    kopf_bytes = roh.read(2)
    roh.seek(0)
    strom: IO[bytes] = gzip.GzipFile(fileobj=roh) if kopf_bytes == b"\x1f\x8b" else roh
    text = io.TextIOWrapper(strom, encoding="utf-8", errors="replace", newline="")
    kopf = text.readline()
    if not lc.ist_csv(kopf.encode()):
        # OpenCellID schickt bei Tageslimit oder falschem Schlüssel einen kurzen Text statt der Datei; der Text kommt
        # nicht ins Protokoll (er könnte den Schlüssel enthalten)
        raise ValueError("keine CSV")
    return lc.zellen_aus(itertools.chain([kopf], text), r)
