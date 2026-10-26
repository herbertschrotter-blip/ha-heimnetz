"""Verbindung zur FRITZ!Box über fritzconnection (dieselbe Bibliothek wie FRITZ!Box Tools) – nur lesend.

Alles hier ist blockierend und läuft im Executor. Ein Teil darf ausfallen, der Rest läuft weiter; der Grund steht
dann in `fehler`. Ist die Verbindung selbst weg, bricht der Abruf nach dem ersten Teil ab, statt jeden Teil in die
Zeitüberschreitung laufen zu lassen. Kennwort, Adressen und Sitzungskennungen stehen nie in Fehlertexten.
"""

from __future__ import annotations

import logging
import re
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from fritzconnection import FritzConnection
from fritzconnection.core.exceptions import FritzAuthorizationError, FritzConnectionException
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, RequestException, Timeout

from .logik import arten as ar
from .logik import befunde as bf
from .logik import geraete as gr
from .logik import mobil as mb
from .logik import protokoll as pr
from .logik import verkehr as vk
from .logik import wlan as wl
from .logik.sprache import merke, t
from .logik.werte import ganzzahl, ja, text

LOGGER = logging.getLogger(__package__)
TIMEOUT = 10.0
MOBIL = "X_AVM-DE_WANMobileConnection1"
FEHLER = (FritzConnectionException, RequestException, OSError, KeyError, ValueError, ET.ParseError)
VERBINDUNG_WEG = (RequestsConnectionError, Timeout)


class AnmeldungAbgelehnt(Exception):
    """Die Box lehnt Benutzer oder Kennwort ab – lösbar in FRITZ!Box Tools."""


class NichtErreichbar(Exception):
    """Die Box antwortet nicht."""


class _Abbruch(Exception):
    """Verbindung weg: die übrigen Teile dieses Abrufs auslassen."""


WEITERREICHEN = (AnmeldungAbgelehnt, *VERBINDUNG_WEG)  # nie als Teilausfall schlucken


@dataclass(frozen=True)
class Zugang:
    host: str
    port: int
    benutzer: str
    kennwort: str = field(repr=False)
    tls: bool


@dataclass(frozen=True)
class BoxInfo:
    """Modell, Firmware und Laufzeit der Box (DeviceInfo, WU-0005); `t` = Zeitpunkt des Lesens."""

    modell: str
    firmware: str
    laufzeit_s: int | None
    t: float


@dataclass
class BoxDaten:
    """Teilergebnis für logik.sammeln.Rohdaten; None = fehlgeschlagen oder nicht gefragt."""

    protokoll: list[pr.BoxZeile] | None = None
    lan: bf.Heimnetz | None = None
    geraete: dict[str, gr.Geraet] | None = None
    quellen: dict[str, str] | None = None
    mobil: mb.Mobilfunk | None = None
    ohne_mobilfunk: bool = False
    mobil_baender: str | None = None
    zaehler: vk.Zaehlerstand | None = None
    wlan_baender: tuple[wl.Band, ...] | None = None
    wlan_gast: bool | None = None
    wlan_geraete: tuple[wl.Funkgeraet, ...] | None = None
    mesh: dict[str, str] | None = None  # MAC → Modell der Mesh-Geräte (langsam, AN-0001)
    info: BoxInfo | None = None  # langsam (WU-0005)
    fehler: list[str] = field(default_factory=list)


class Box:
    """Eine Verbindung je Einrichtung; das Laden der Beschreibung der Box ist teuer und geschieht nur einmal."""

    def __init__(self, zugang: Zugang) -> None:
        self.zugang = zugang
        self._fc: FritzConnection | None = None
        self._geschlossen = False

    def verbinden(self) -> FritzConnection:
        if self._geschlossen:
            raise NichtErreichbar("Verbindung geschlossen")
        if self._fc is None:
            z = self.zugang
            try:
                self._fc = FritzConnection(
                    address=z.host,
                    port=z.port,
                    user=z.benutzer,
                    password=z.kennwort,
                    use_tls=z.tls,
                    timeout=TIMEOUT,
                    redact_debug_log=True,
                )
            except FritzAuthorizationError as err:
                raise AnmeldungAbgelehnt from err
            except FEHLER as err:
                raise NichtErreichbar(grund(err)) from err
        return self._fc

    def pruefen(self) -> None:
        """Verbinden und anmelden: das Laden der Beschreibung allein prüft das Kennwort nicht."""
        try:
            self._aktion("DeviceInfo1", "GetInfo")
        except FEHLER as err:
            raise NichtErreichbar(grund(err)) from err
        finally:
            self.trennen()

    def neuer_zugang(self, zugang: Zugang) -> None:
        """Zugang in FRITZ!Box Tools geändert: beim nächsten Abruf neu verbinden."""
        if zugang != self.zugang:
            self.trennen()
            self.zugang = zugang

    def trennen(self) -> None:
        if self._fc is not None:
            self._fc.session.close()
            self._fc = None

    def schliessen(self) -> None:
        """Beim Entladen: ein noch laufender Abruf verbindet sich danach nicht wieder."""
        self._geschlossen = True
        self.trennen()

    def _aktion(self, dienst: str, aktion: str, **args: Any) -> dict[str, Any]:
        try:
            return dict(self.verbinden().call_action(dienst, aktion, arguments=args or None))
        except FritzAuthorizationError as err:
            raise AnmeldungAbgelehnt from err

    def _datei(self, pfad: str) -> bytes:
        fc = self.verbinden()
        with fc.session.get(f"{fc.address}:{fc.port}{pfad}", timeout=TIMEOUT) as antwort:
            antwort.raise_for_status()
            return bytes(antwort.content)

    def holen(self, langsam: bool, mobil_fragen: bool, router: str, sprache: str) -> BoxDaten:
        """Alles für einen Abruf. `langsam`: auch Heimnetz und Adressquelle je Gerät (alle 10 min). Die Namen der
        Teile in `fehler` (für die Übersicht) und die Bänder („automatisch“) in `sprache`."""
        d = BoxDaten()
        try:
            fc = self.verbinden()
        except NichtErreichbar as err:
            d.fehler.append(f"FRITZ!Box: {err}")
            return d

        def teil(name_: str, fn: Callable[[], None]) -> None:
            name = t(name_, sprache)
            try:
                fn()
            except AnmeldungAbgelehnt:
                raise
            except VERBINDUNG_WEG as err:
                d.fehler.append(f"{name}: {grund(err)}")
                raise _Abbruch from err
            except FEHLER as err:
                d.fehler.append(f"{name}: {grund(err)}")

        def protokoll() -> None:
            try:
                pfad = text(
                    self._aktion("DeviceInfo1", "X_AVM-DE_GetDeviceLogPath")["NewDeviceLogPath"]
                )
                d.protokoll = pr.aus_xml(self._datei(pfad))
            except WEITERREICHEN:
                raise
            except FEHLER:
                d.protokoll = pr.aus_text(
                    text(self._aktion("DeviceInfo1", "GetDeviceLog").get("NewDeviceLog"))
                )

        def heimnetz() -> None:
            i = self._aktion("LANHostConfigManagement1", "GetInfo")
            d.lan = bf.Heimnetz(
                router=(text(i.get("NewIPRouters")) or router).split(",")[0].strip(),
                maske=text(i.get("NewSubnetMask")),
                dhcp_von=text(i.get("NewMinAddress")),
                dhcp_bis=text(i.get("NewMaxAddress")),
                dhcp_an=ja(i.get("NewDHCPServerEnable")),
                dns=text(i.get("NewDNSServers")),
            )

        def geraete() -> None:
            pfad = text(
                self._aktion("Hosts1", "X_AVM-DE_GetHostListPath")["NewX_AVM-DE_HostListPath"]
            )
            d.geraete = gr.aus_hostliste(self._datei(pfad))
            if langsam:
                quellen = {}
                for mac, g in d.geraete.items():
                    if g.aktiv and g.ip:
                        try:
                            antwort = self._aktion(
                                "Hosts1", "GetSpecificHostEntry", NewMACAddress=mac
                            )
                            quellen[mac] = text(antwort.get("NewAddressSource"))
                        except WEITERREICHEN:
                            raise
                        except FEHLER:
                            pass  # einzelnes Gerät: beim nächsten Mal wieder
                d.quellen = quellen

        def mobil() -> None:
            if MOBIL not in fc.services:
                d.ohne_mobilfunk = True
                return
            d.mobil = mb.aus_antwort(self._aktion(MOBIL, "GetInfoEx"))
            if langsam:
                try:
                    d.mobil_baender = mb.baender(
                        self._aktion(MOBIL, "GetEnabledBandCapabilities"), sprache
                    )
                except WEITERREICHEN:
                    raise
                except FEHLER:
                    pass  # ältere FRITZ!OS ohne diese Aktion: Bänder bleiben leer

        def wlan() -> None:
            dienste = sorted(n for n in fc.services if n.startswith("WLANConfiguration"))
            if not dienste:
                return
            if langsam:
                baender, gast = [], None
                for n in dienste:
                    try:
                        ext = self._aktion(n, "X_AVM-DE_GetWLANExtInfo")
                    except WEITERREICHEN:
                        raise
                    except FEHLER:
                        ext = {}  # ältere FRITZ!OS ohne diese Aktion: als normales Funknetz lesen
                    try:
                        info = self._aktion(n, "GetInfo")
                        if wl.ist_gast(ext):
                            gast = ja(info.get("NewEnable"))
                            continue
                        band = wl.band_aus(info, self._aktion(n, "GetChannelInfo"))
                    except WEITERREICHEN:
                        raise
                    except FEHLER:
                        continue  # nur dieses Funknetz fehlt diesmal; die anderen und die Geräte gelten
                    if band is not None:
                        baender.append(band)
                d.wlan_baender, d.wlan_gast = tuple(baender), gast
            pfad = text(
                self._aktion(dienste[0], "X_AVM-DE_GetWLANDeviceListPath")[
                    "NewX_AVM-DE_WLANDeviceListPath"
                ]
            )
            d.wlan_geraete = wl.geraete_aus(self._datei(pfad))

        def zaehler() -> None:
            # 64-Bit-Zähler (die 32-Bit-Zähler laufen bei Dauerlast alle paar Minuten über); ältere FRITZ!OS ohne
            # diese Werte: die 32-Bit-Zähler
            try:
                a = self._aktion("WANCommonIFC1", "GetAddonInfos")
                rx = ganzzahl(a["NewX_AVM_DE_TotalBytesReceived64"])
                tx = ganzzahl(a["NewX_AVM_DE_TotalBytesSent64"])
            except KeyError, FritzConnectionException:
                w = "WANCommonInterfaceConfig1"
                rx = ganzzahl(self._aktion(w, "GetTotalBytesReceived")["NewTotalBytesReceived"])
                tx = ganzzahl(self._aktion(w, "GetTotalBytesSent")["NewTotalBytesSent"])
            if rx is not None and tx is not None:
                d.zaehler = vk.Zaehlerstand(round(time.time(), 1), rx, tx)

        def info() -> None:
            i = self._aktion("DeviceInfo1", "GetInfo")
            d.info = BoxInfo(
                text(i.get("NewModelName")),
                text(i.get("NewSoftwareVersion")),
                ganzzahl(i.get("NewUpTime")),
                round(time.time(), 1),
            )

        def mesh() -> None:
            pfad = text(
                self._aktion("Hosts1", "X_AVM-DE_GetMeshListPath")["NewX_AVM-DE_MeshListPath"]
            )
            d.mesh = ar.mesh_aus(self._datei(pfad))

        try:
            teil(merke("Ereignisprotokoll"), protokoll)
            if langsam:
                teil(merke("Heimnetz"), heimnetz)
            teil(merke("Gerätetabelle"), geraete)
            if mobil_fragen:
                teil(merke("Mobilfunk"), mobil)
            teil("WLAN", wlan)
            teil(merke("Verkehr"), zaehler)
            if langsam:
                teil("Mesh", mesh)
                teil(merke("Gerät"), info)
        except _Abbruch:
            pass
        return d


_SID = re.compile(r"sid=[0-9a-fA-F]+")
_ADRESSE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|https?://\S+")


def grund(err: BaseException) -> str:
    """Kurzer Grund ohne Adressen, URLs und Sitzungskennungen (landet in der Diagnose)."""
    if isinstance(err, HTTPError) and err.response is not None:
        return f"HTTP {err.response.status_code}"
    if isinstance(err, RequestException):
        return type(err).__name__
    zeile = str(err).split("\n")[0][:200]
    zeile = _ADRESSE.sub("…", _SID.sub("sid=…", zeile))
    return f"{type(err).__name__}: {zeile}" if zeile else type(err).__name__
