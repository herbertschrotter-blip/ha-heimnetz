"""DHCP-Test: Anfrage und Angebot (Fälle aus dem Altbestand)."""

import struct

from logik import dhcp

XID = b"\x01\x02\x03\x04"


def angebot_roh(xid=XID):
    kopf = (
        struct.pack("!BBBB4sHH", 2, 1, 6, 0, xid, 0, 0x8000)
        + bytes(4)
        + bytes([192, 168, 170, 99])
        + bytes(8)
    )
    kopf += bytes(16) + bytes(192)
    opts = (
        dhcp.MAGIC
        + b"\x35\x01\x02"
        + b"\x36\x04"
        + bytes([192, 168, 170, 1])
        + b"\x03\x04"
        + bytes([192, 168, 170, 1])
        + b"\x06\x08"
        + bytes([192, 168, 170, 1, 1, 1, 1, 1])
        + b"\xff"
    )
    return kopf + opts


def test_anfrage_ist_kein_angebot():
    a = dhcp.anfrage(XID)
    assert len(a) == 300
    assert dhcp.angebot(a, XID) is None


def test_angebot_lesen():
    o = dhcp.angebot(angebot_roh(), XID)
    assert o is not None
    assert (o.server, o.angebot, o.router, o.dns) == (
        "192.168.170.1",
        "192.168.170.99",
        "192.168.170.1",
        "192.168.170.1, 1.1.1.1",
    )
    assert dhcp.angebot(angebot_roh(), b"\x09\x09\x09\x09") is None


def test_pruefsumme():
    kopf = bytes.fromhex("4500003c1c4640004006" + "0000" + "ac100a63ac100a0c")
    assert dhcp.pruefsumme(kopf) == 0xB1E6


def test_rahmen_hin_und_zurueck():
    """Der gesendete Rahmen ist ein gültiger IPv4-Rundruf; ein Angebot im Rahmen wird mit Absender gelesen."""
    r = dhcp.rahmen(bytes.fromhex("aabbccddeeff"), XID)
    assert r[:6] == b"\xff" * 6 and r[12:14] == b"\x08\x00"
    assert dhcp.pruefsumme(r[14:34]) == 0
    payload = angebot_roh()
    udp = struct.pack("!HHHH", 67, 68, 8 + len(payload), 0) + payload
    ip = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0, 64, 17, 0, bytes(4), b"\xff" * 4
    )
    paket = b"\xff" * 6 + bytes.fromhex("112233445566") + b"\x08\x00" + ip + udp
    o = dhcp.aus_rahmen(paket, XID)
    assert o is not None and o.mac == "11:22:33:44:55:66" and o.server == "192.168.170.1"
    assert dhcp.aus_rahmen(r, XID) is None  # eigene Anfrage (UDP 68 → 67)
