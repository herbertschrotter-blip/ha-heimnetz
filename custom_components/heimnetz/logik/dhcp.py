"""DHCP-Test: Anfrage bauen und Antworten lesen (das Senden über den Netzwerk-Anschluss macht `pi.py`).

Gesendet wird nur ein DHCPDISCOVER mit einer erfundenen Adresse; es wird keine Adresse angenommen (kein REQUEST).
"""

from __future__ import annotations

import socket
import struct

from .befunde import Angebot

PROBE_MAC = "02:4e:45:54:5a:44"  # erfunden, lokal verwaltet („NETZD“)
MAGIC = b"\x63\x82\x53\x63"


def anfrage(xid: bytes, mac: str = PROBE_MAC) -> bytes:
    """DHCPDISCOVER (BOOTP-Kopf + Optionen), auf 300 Bytes aufgefüllt."""
    chaddr = bytes.fromhex(mac.replace(":", ""))
    kopf = (
        struct.pack("!BBBB4sHH", 1, 1, 6, 0, xid, 0, 0x8000) + b"\x00" * 16 + chaddr + b"\x00" * 202
    )
    optionen = (
        MAGIC
        + b"\x35\x01\x01"  # DHCPDISCOVER
        + b"\x3d\x07\x01"
        + chaddr  # Client-ID
        + b"\x0c\x08netzdiag"  # Hostname
        + b"\x37\x05\x01\x03\x06\x33\x36"  # gewünschte Angaben
        + b"\xff"
    )
    return (kopf + optionen).ljust(300, b"\x00")


def _ip(b: bytes | None) -> str:
    return socket.inet_ntoa(b[:4]) if b and len(b) >= 4 else ""


def angebot(daten: bytes, xid: bytes) -> Angebot | None:
    """DHCPOFFER zur Anfrage `xid` → Angebot, sonst None."""
    if len(daten) < 240 or daten[0] != 2 or daten[4:8] != xid or daten[236:240] != MAGIC:
        return None
    opts: dict[int, bytes] = {}
    i = 240
    while i < len(daten) and daten[i] != 255:
        if daten[i] == 0:
            i += 1
            continue
        if i + 1 >= len(daten):
            break
        n = daten[i + 1]
        opts[daten[i]] = daten[i + 2 : i + 2 + n]
        i += 2 + n
    if opts.get(53) != b"\x02":
        return None
    dns = opts.get(6, b"")
    return Angebot(
        server=_ip(opts.get(54)) or _ip(daten[20:24]),
        angebot=_ip(daten[16:20]),
        router=_ip(opts.get(3)),
        maske=_ip(opts.get(1)),
        dns=", ".join(_ip(dns[j : j + 4]) for j in range(0, len(dns) - 3, 4)),
    )


def pruefsumme(b: bytes) -> int:
    """IPv4-Kopf-Prüfsumme."""
    s = sum(int(x) for x in struct.unpack(f"!{len(b) // 2}H", b))
    s = (s >> 16) + (s & 0xFFFF)
    return int(~(s + (s >> 16)) & 0xFFFF)


def rahmen(quelle_mac: bytes, xid: bytes) -> bytes:
    """Ganzer Ethernet-Rahmen als Rundruf: Ethernet → IPv4 (0.0.0.0 → 255.255.255.255) → UDP 68 → 67."""
    dhcp = anfrage(xid)
    udp = struct.pack("!HHHH", 68, 67, 8 + len(dhcp), 0) + dhcp
    ip = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0, 64, 17, 0, b"\x00" * 4, b"\xff" * 4
    )
    ip = ip[:10] + struct.pack("!H", pruefsumme(ip)) + ip[12:]
    return b"\xff" * 6 + quelle_mac + b"\x08\x00" + ip + udp


def aus_rahmen(paket: bytes, xid: bytes) -> Angebot | None:
    """Empfangener Ethernet-Rahmen → Angebot (mit Hardware-Adresse des Absenders), sonst None."""
    if len(paket) < 42 or paket[12:14] != b"\x08\x00" or paket[23] != 17:
        return None
    u = 14 + (paket[14] & 0x0F) * 4
    if paket[u : u + 4] != b"\x00\x43\x00\x44":  # UDP 67 → 68
        return None
    a = angebot(paket[u + 8 :], xid)
    if a is None:
        return None
    mac = ":".join(f"{b:02X}" for b in paket[6:12])
    return Angebot(a.server, a.angebot, a.router, a.maske, a.dns, mac)
