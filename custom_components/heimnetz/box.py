"""Verbindung zur FRITZ!Box über fritzconnection (dieselbe Bibliothek wie FRITZ!Box Tools) – nur lesend.

Alles hier ist blockierend und läuft im Executor. Ein Teil darf ausfallen, der Rest läuft weiter; der Grund steht
dann in `fehler`. Ist die Verbindung selbst weg, bricht der Abruf nach dem ersten Teil ab, statt jeden Teil in die
Zeitüberschreitung laufen zu lassen. Kennwort, Adressen und Sitzungskennungen stehen nie in Fehlertexten.
"""

from __future__ import annotations

import logging
import re
import threading
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
from .logik import leitung as ln
from .logik import mobil as mb
from .logik import protokoll as pr
from .logik import verkehr as vk
from .logik import wlan as wl
from .logik import zugang as zg
from .logik.sprache import merke, t
from .logik.werte import ganzzahl, ja, text

LOGGER = logging.getLogger(__package__)
TIMEOUT = 10.0
MOBIL = "X_AVM-DE_WANMobileConnection1"
WAN = "WANCommonInterfaceConfig1"
DSL = "WANDSLInterfaceConfig1"
FASER = "X_AVM-DE_WANFiber1"
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
    zugang: zg.Meldung | None = None  # langsam (WU-0009)
    dsl: ln.Dsl | None = None  # langsam, nur mit DSL-Dienst
    faser: ln.Faser | None = None  # langsam, nur mit Glasfaser-Dienst
    fehler: list[str] = field(default_factory=list)


class Box:
    """Eine Verbindung je Einrichtung; das Laden der Beschreibung der Box ist teuer und geschieht nur einmal."""

    def __init__(self, zugang: Zugang) -> None:
        self.zugang = zugang
        self._fc: FritzConnection | None = None
        self._geschlossen = False
        # nie zwei Abrufe gleichzeitig an der Box (z. B. „Erneut suchen“ während des Takts, WU-0009)
        self._sperre = threading.Lock()

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

    def _wan_adresse(self) -> str:
        """Adresse der Box im WAN über die Standardverbindung (Layer3Forwarding); nur für logik.zugang.wan_netz, sie
        verlässt box.py nicht. Fehlt etwas, bleibt sie leer."""
        try:
            dienst = text(
                self._aktion("Layer3Forwarding1", "GetDefaultConnectionService")[
                    "NewDefaultConnectionService"
                ]
            )
            teile = dienst.split(".")
            if len(teile) < 2 or not teile[1].startswith(("WANIPConnection", "WANPPPConnection")):
                return ""
            name = teile[1] + (teile[2] if len(teile) > 2 and teile[2].isdigit() else "1")
            return text(self._aktion(name, "GetExternalIPAddress").get("NewExternalIPAddress"))
        except WEITERREICHEN:
            raise
        except FEHLER:
            return ""

    def holen(
        self,
        langsam: bool,
        mobil_fragen: bool,
        router: str,
        sprache: str,
        zugang_fragen: bool = False,
        haupt: str = "",
    ) -> BoxDaten:
        """Alles für einen Abruf. `langsam`: auch Heimnetz und Adressquelle je Gerät (alle 10 min) und der Zugang;
        `zugang_fragen`: den Zugang auch diesmal (⚙ › Zugang „Erneut suchen“). Die Namen der Teile in `fehler` (für
        die Übersicht) und die Bänder („automatisch“) in `sprache`. `haupt`: zuletzt erkannter fester Zugang – dessen
        Werte werden auch während eines Ausfalls gelesen (logik.zugang.dsl_lesen)."""
        with self._sperre:
            return self._holen(langsam, mobil_fragen, router, sprache, zugang_fragen, haupt)

    def _holen(
        self,
        langsam: bool,
        mobil_fragen: bool,
        router: str,
        sprache: str,
        zugang_fragen: bool,
        haupt: str,
    ) -> BoxDaten:
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

        def optional(dienst: str, aktion: str) -> dict[str, Any]:
            """Aktion, die ältere FRITZ!OS nicht kennen: fehlt sie, bleibt es leer."""
            try:
                return self._aktion(dienst, aktion)
            except WEITERREICHEN:
                raise
            except FEHLER:
                return {}

        def zugang() -> None:
            # WU-0009: woher kommt das Internet – nur lesen, im langsamen Takt (logik/zugang.py)
            link = self._aktion(WAN, "GetCommonLinkProperties")
            avm = optional(WAN, "X_AVM-DE_GetAddonInfos")
            mobil_an = None
            if MOBIL in fc.services:
                info_mobil = optional(MOBIL, "GetInfo")
                mobil_an = ja(info_mobil["NewEnable"]) if "NewEnable" in info_mobil else None
            dsl_status = (
                text(optional(DSL, "GetInfo").get("NewStatus")) if DSL in fc.services else ""
            )
            modus = (
                text(optional(FASER, "GetInfo").get("NewFiberMode")) if FASER in fc.services else ""
            )
            netz, vorschlag = zg.wan_netz(self._wan_adresse())
            d.zugang = zg.Meldung(
                zugangsart=text(link.get("NewWANAccessType")),
                link=text(link.get("NewPhysicalLinkStatus")),
                art_avm=text(avm.get("NewX_AVM-DE_WANAccessType")),
                down_bit=ganzzahl(link.get("NewLayer1DownstreamMaxBitRate")),
                up_bit=ganzzahl(link.get("NewLayer1UpstreamMaxBitRate")),
                mobil_dienst=MOBIL in fc.services,
                mobil_an=mobil_an,
                dsl_dienst=DSL in fc.services,
                dsl_status=dsl_status,
                faser_dienst=FASER in fc.services,
                faser_modus=modus,
                wan_netz=netz,
                vorschlag=vorschlag,
            )

        def dsl() -> None:
            # WU-0009: Werte der DSL-Leitung (logik/leitung.py); X_AVM-DE_GetDSLInfo erst ab neueren FRITZ!OS
            i = self._aktion(DSL, "GetInfo")
            x = optional(DSL, "X_AVM-DE_GetDSLInfo")
            st = optional(DSL, "GetStatisticsTotal")
            d.dsl = ln.Dsl(
                t=round(time.time(), 1),
                status=text(i.get("NewStatus")),
                sync_down=ganzzahl(i.get("NewDownstreamCurrRate")),
                sync_up=ganzzahl(i.get("NewUpstreamCurrRate")),
                max_down=ganzzahl(i.get("NewDownstreamMaxRate")),
                max_up=ganzzahl(i.get("NewUpstreamMaxRate")),
                marge_down=ganzzahl(i.get("NewDownstreamNoiseMargin")),
                marge_up=ganzzahl(i.get("NewUpstreamNoiseMargin")),
                daempfung_down=ganzzahl(i.get("NewDownstreamAttenuation")),
                daempfung_up=ganzzahl(i.get("NewUpstreamAttenuation")),
                modulation=text(x.get("NewModulationType")),
                profil=text(x.get("NewCurrentProfile")),
                crc=ganzzahl(st.get("NewCRCErrors")),
                fec=ganzzahl(st.get("NewFECErrors")),
                crc_gegen=ganzzahl(st.get("NewATUCCRCErrors")),
                fec_gegen=ganzzahl(st.get("NewATUCFECErrors")),
            )

        def faser() -> None:
            # WU-0009: Glasfaser-Modul (logik/leitung.py); Seriennummern und Kennungen werden nicht übernommen
            i = self._aktion(FASER, "GetInfo")
            st = optional(FASER, "GetStatistics")
            d.faser = ln.Faser(
                t=round(time.time(), 1),
                modus=text(i.get("NewFiberMode")),
                rx=ganzzahl(i.get("NewOpticalSignalLevel")),
                rx_min=ganzzahl(i.get("NewLowerOpticalThreshold")),
                rx_max=ganzzahl(i.get("NewUpperOpticalThreshold")),
                tx=ganzzahl(i.get("NewTransmitOpticalLevel")),
                tx_min=ganzzahl(i.get("NewLowerTransmitPowerThreshold")),
                tx_max=ganzzahl(i.get("NewUpperTransmitPowerThreshold")),
                fehler_rx=ganzzahl(st.get("NewPacketErrorsReceived")),
                fehler_tx=ganzzahl(st.get("NewPacketErrorsSent")),
                resyncs=ganzzahl(st.get("NewResyncs")),
                minuten=ganzzahl(st.get("NewMinutesInShowtime")),
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
            if langsam or zugang_fragen:
                if WAN in fc.services:
                    teil(merke("Zugang"), zugang)
                z = d.zugang
                # Werte der Leitung nur, wenn das Internet darüber kommt (auch während eines Ausfalls) – eine Box
                # mit ungenutztem Anschluss bekommt so keine DSL- oder Glasfaser-Entitäten (WU-0009)
                if z is not None and zg.dsl_lesen(z, haupt):
                    teil("DSL", dsl)
                if z is not None and zg.faser_lesen(z, haupt):
                    teil(merke("Glasfaser"), faser)
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
