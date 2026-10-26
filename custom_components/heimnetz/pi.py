"""Prüfungen vom Pi aus: erreicht er die Box, das Internet, die Namensauflösung? Dazu der DHCP-Test.

Der DHCP-Test schickt ein DHCPDISCOVER über einen Rohdaten-Socket (Linux, braucht root – im HA-Container gegeben) und
sammelt alle Angebote ein; es wird keine Adresse angenommen.
"""

from __future__ import annotations

import asyncio
import os
import socket
import time

from .logik import befunde as bf
from .logik import dhcp
from .logik.sprache import t

TCP_TIMEOUT = 3.0
INTERNET = (("1.1.1.1", 443), ("8.8.8.8", 443))
DNS_NAME = "avm.de"
DHCP_WARTEN_S = 3.0


async def _tcp(host: str, port: int) -> bool:
    try:
        _, schreiber = await asyncio.wait_for(asyncio.open_connection(host, port), TCP_TIMEOUT)
    except OSError, TimeoutError:
        return False
    schreiber.close()
    return True


async def _eine(*ziele: tuple[str, int]) -> bool:
    return any(await asyncio.gather(*(_tcp(h, p) for h, p in ziele)))


async def _dns() -> bool:
    try:
        await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo(DNS_NAME, 443), TCP_TIMEOUT)
    except OSError, TimeoutError:
        return False
    return True


def arp_adresse(ip: str) -> str:
    """Hardware-Adresse zu `ip` aus der ARP-Tabelle des Pi (blockierend)."""
    try:
        with open("/proc/net/arp", encoding="ascii") as f:
            for zeile in f.readlines()[1:]:
                p = zeile.split()
                if len(p) >= 4 and p[0] == ip and p[3] != "00:00:00:00:00:00":
                    return p[3].upper()
    except OSError:
        pass
    return ""


async def verbindung(router: str) -> bf.PiVerbindung:
    box, internet, dns = await asyncio.gather(
        _eine((router, 80), (router, 443)), _eine(*INTERNET), _dns()
    )
    gw_mac = await asyncio.get_running_loop().run_in_executor(None, arp_adresse, router)
    return bf.PiVerbindung(box=box, internet=internet, dns=dns, gw_mac=gw_mac)


def _anschluss() -> str:
    """Netzwerk-Anschluss mit der Standardroute."""
    try:
        with open("/proc/net/route", encoding="ascii") as f:
            for zeile in f.readlines()[1:]:
                p = zeile.split()
                if len(p) > 1 and p[1] == "00000000":
                    return p[0]
    except OSError:
        pass
    return ""


def dhcp_test(warten: float, sprache: str) -> bf.DhcpTest:
    """Blockierend (im Executor): Anfrage als Rundruf senden, `warten` Sekunden Angebote sammeln. Der Grund, warum
    der Test nicht lief, steht in `sprache` (er geht an die Seite)."""
    if not hasattr(socket, "AF_PACKET"):
        return bf.DhcpTest(fehler=t("nur unter Linux", sprache))
    anschluss = _anschluss()
    if not anschluss:
        return bf.DhcpTest(fehler=t("kein Netzwerk-Anschluss gefunden", sprache))
    xid = os.urandom(4)
    try:
        with open(f"/sys/class/net/{anschluss}/address", encoding="ascii") as f:
            eigene = bytes.fromhex(f.read().strip().replace(":", ""))
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
    except (OSError, ValueError) as err:
        return bf.DhcpTest(fehler=t("DHCP-Test nicht möglich: {fehler}", sprache, fehler=err))
    server: dict[str, bf.Angebot] = {}
    try:
        s.bind((anschluss, 0))
        s.send(dhcp.rahmen(eigene, xid))
        ende = time.monotonic() + warten
        while time.monotonic() < ende:
            s.settimeout(max(0.05, ende - time.monotonic()))
            try:
                paket = s.recv(2048)
            except TimeoutError:
                break
            angebot = dhcp.aus_rahmen(paket, xid)
            if angebot:
                server[angebot.server + angebot.mac] = angebot
    except OSError as err:
        return bf.DhcpTest(fehler=t("DHCP-Test abgebrochen: {fehler}", sprache, fehler=err))
    finally:
        s.close()
    return bf.DhcpTest(ok=True, server=tuple(sorted(server.values(), key=lambda a: a.server)))
