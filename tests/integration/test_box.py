"""box.py gegen eine nachgebaute FRITZ!Box (fritzconnection ersetzt): Teilausfälle, Abbruch, Fehlertexte."""

from unittest.mock import MagicMock, patch

import pytest
from fritzconnection.core.exceptions import FritzServiceError
from requests.exceptions import ConnectTimeout, HTTPError

from custom_components.heimnetz import box as bx
from tests.logik.daten import GERAETELOG, HOSTLISTE, MESH, WLANLISTE, ZELLEN

ZUGANG = bx.Zugang("192.0.2.1", 49000, "u", "geheim", False)


class Antwort:
    def __init__(self, inhalt: bytes | Exception) -> None:
        self.inhalt = inhalt

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def raise_for_status(self):
        if isinstance(self.inhalt, Exception):
            raise self.inhalt

    @property
    def content(self):
        return self.inhalt


def fake_box(aktionen: dict, dateien: dict, dienste=("X_AVM-DE_WANMobileConnection1",)):
    fc = MagicMock(address="http://192.0.2.1", port=49000, services={d: None for d in dienste})

    def call_action(dienst, aktion, arguments=None):
        wert = aktionen[(dienst, aktion)]
        if isinstance(wert, Exception):
            raise wert
        return wert

    def get(url, timeout=None):
        wert = dateien[url.rsplit(":49000", 1)[1]]
        if isinstance(wert, ConnectTimeout):
            raise wert
        return Antwort(wert)

    fc.call_action.side_effect = call_action
    fc.session.get.side_effect = get
    return fc


AKTIONEN = {
    ("DeviceInfo1", "X_AVM-DE_GetDeviceLogPath"): {"NewDeviceLogPath": "/log"},
    ("DeviceInfo1", "GetDeviceLog"): {"NewDeviceLog": "19.09.26 10:05:00 Text-Protokoll"},
    ("DeviceInfo1", "GetInfo"): {
        "NewModelName": "FRITZ!Box 6860 5G",
        "NewSoftwareVersion": "268.08.03",
        "NewUpTime": "3600",
    },
    ("LANHostConfigManagement1", "GetInfo"): {"NewIPRouters": "192.168.170.1"},
    ("Hosts1", "X_AVM-DE_GetHostListPath"): {"NewX_AVM-DE_HostListPath": "/hosts?sid=abc123"},
    ("Hosts1", "X_AVM-DE_GetMeshListPath"): {"NewX_AVM-DE_MeshListPath": "/mesh?sid=abc123"},
    ("X_AVM-DE_WANMobileConnection1", "GetInfoEx"): {
        "NewCurrentAccessTechnology": "5G-NSA",
        "NewCellList": ZELLEN,
    },
    ("WANCommonIFC1", "GetAddonInfos"): {
        "NewX_AVM_DE_TotalBytesReceived64": "10000000000",
        "NewX_AVM_DE_TotalBytesSent64": "20000000000",
    },
    ("WANCommonInterfaceConfig1", "GetTotalBytesReceived"): {"NewTotalBytesReceived": 5},
    ("WANCommonInterfaceConfig1", "GetTotalBytesSent"): {"NewTotalBytesSent": 6},
}
DATEIEN = {
    "/log": GERAETELOG.encode(),
    "/hosts?sid=abc123": HOSTLISTE.encode(),
    "/mesh?sid=abc123": MESH.encode(),
}


def holen(aktionen=None, dateien=None, langsam=False, **kw):
    b = bx.Box(ZUGANG)
    with patch.object(
        bx,
        "FritzConnection",
        return_value=fake_box(
            {**AKTIONEN, **(aktionen or {})}, {**DATEIEN, **(dateien or {})}, **kw
        ),
    ):
        return b.holen(langsam=langsam, mobil_fragen=True, router="192.0.2.1", sprache="de")


def test_alles_da():
    d = holen()
    assert (
        d.fehler == []
        and len(d.geraete) == 5
        and len(d.protokoll) == 2
        and d.mobil.technik == "5G-NSA"
    )
    assert (d.zaehler.rx, d.zaehler.tx) == (10_000_000_000, 20_000_000_000)  # 64-Bit-Zähler


def test_box_info_nur_im_langsamen_takt():
    """WU-0005: Modell, Firmware und Laufzeit der Box – alle 10 Minuten reicht."""
    assert holen().info is None
    i = holen(langsam=True).info
    assert i is not None and (i.modell, i.firmware, i.laufzeit_s) == (
        "FRITZ!Box 6860 5G",
        "268.08.03",
        3600,
    )


def test_kaputtes_xml_ist_teilausfall():
    d = holen(dateien={"/hosts?sid=abc123": b"<html>Sitzung abgelaufen"})
    assert d.geraete is None and d.protokoll is not None and d.zaehler is not None
    assert d.fehler and d.fehler[0].startswith("Gerätetabelle: ParseError")


def test_protokoll_weicht_bei_http_fehler_auf_text_aus():
    d = holen(dateien={"/log": HTTPError("404")})
    assert [z.text for z in d.protokoll] == ["Text-Protokoll"] and d.fehler == []


def test_32_bit_zaehler_wenn_64_bit_fehlt():
    d = holen(aktionen={("WANCommonIFC1", "GetAddonInfos"): FritzServiceError("unbekannt")})
    assert (d.zaehler.rx, d.zaehler.tx) == (5, 6)


def test_ohne_mobilfunk_dienst():
    d = holen(dienste=())
    assert d.ohne_mobilfunk and d.mobil is None


def test_verbindung_weg_bricht_ab_statt_jeden_teil_abzuwarten():
    d = holen(dateien={"/log": ConnectTimeout("192.0.2.1 timeout")})
    assert d.geraete is None and d.zaehler is None and len(d.fehler) == 1
    assert "192.0.2.1" not in d.fehler[0]


@pytest.mark.parametrize(
    ("fehler", "darf_nicht"),
    [
        (ValueError("http://192.0.2.1:49000/hosts?sid=abc123 kaputt"), ("192.0.2.1", "abc123")),
        (OSError("connect 10.0.0.1 failed sid=deadbeef"), ("10.0.0.1", "deadbeef")),
    ],
)
def test_grund_ohne_adressen_und_sitzung(fehler, darf_nicht):
    text = bx.grund(fehler)
    for x in darf_nicht:
        assert x not in text


def test_nach_schliessen_keine_neue_verbindung():
    b = bx.Box(ZUGANG)
    b.schliessen()
    with patch.object(bx, "FritzConnection") as fc, pytest.raises(bx.NichtErreichbar):
        b.verbinden()
    fc.assert_not_called()


def test_pruefen_meldet_sich_an():
    from fritzconnection.core.exceptions import FritzAuthorizationError

    b = bx.Box(ZUGANG)
    with patch.object(
        bx,
        "FritzConnection",
        return_value=fake_box({("DeviceInfo1", "GetInfo"): FritzAuthorizationError()}, {}),
    ):
        with pytest.raises(bx.AnmeldungAbgelehnt):
            b.pruefen()


WLAN = {
    ("LANHostConfigManagement1", "GetInfo"): {
        "NewIPRouters": "192.0.2.1",
        "NewSubnetMask": "255.255.255.0",
    },
    ("Hosts1", "GetSpecificHostEntry"): {"NewAddressSource": "DHCP"},
    ("WLANConfiguration1", "X_AVM-DE_GetWLANExtInfo"): {"NewX_AVM-DE_APType": "normal"},
    ("WLANConfiguration1", "GetInfo"): {
        "NewEnable": "1",
        "NewStatus": "Up",
        "NewStandard": "ax",
        "NewX_AVM-DE_FrequencyBand": "2400",
    },
    ("WLANConfiguration1", "GetChannelInfo"): {
        "NewChannel": "6",
        "NewX_AVM-DE_AutoChannelEnabled": "1",
    },
    ("WLANConfiguration1", "X_AVM-DE_GetWLANDeviceListPath"): {
        "NewX_AVM-DE_WLANDeviceListPath": "/wlan?sid=abc"
    },
    ("WLANConfiguration2", "X_AVM-DE_GetWLANExtInfo"): FritzServiceError(
        "unbekannt"
    ),  # älteres FRITZ!OS
    ("WLANConfiguration2", "GetInfo"): {
        "NewEnable": "1",
        "NewStatus": "Up",
        "NewStandard": "ax",
        "NewX_AVM-DE_FrequencyBand": "5000",
    },
    ("WLANConfiguration2", "GetChannelInfo"): {
        "NewChannel": "44",
        "NewX_AVM-DE_AutoChannelEnabled": "0",
    },
    ("WLANConfiguration3", "X_AVM-DE_GetWLANExtInfo"): {"NewX_AVM-DE_APType": "guest"},
    ("WLANConfiguration3", "GetInfo"): {"NewEnable": "0", "NewStatus": "Disabled"},
    ("X_AVM-DE_WANMobileConnection1", "GetEnabledBandCapabilities"): {
        "NewBandCapabilitiesLTE": "1,3",
        "NewBandCapabilities5GNSA": "78",
    },
}
DIENSTE = (
    "X_AVM-DE_WANMobileConnection1",
    "WLANConfiguration1",
    "WLANConfiguration2",
    "WLANConfiguration3",
)


def test_wlan_langsam_mit_baendern_und_gast():
    d = holen(WLAN, {"/wlan?sid=abc": WLANLISTE.encode()}, langsam=True, dienste=DIENSTE)
    assert d.fehler == []
    assert [(b.band, b.kanal, b.auto) for b in d.wlan_baender] == [
        ("2,4", 6, True),
        ("5", 44, False),
    ]
    assert (
        d.wlan_gast is False and len(d.wlan_geraete) == 3 and d.mobil_baender == "LTE 1, 3 · 5G n78"
    )


def test_wlan_jede_minute_nur_die_geraete():
    d = holen(WLAN, {"/wlan?sid=abc": WLANLISTE.encode()}, dienste=DIENSTE)
    assert d.wlan_baender is None and len(d.wlan_geraete) == 3 and d.mobil_baender is None


def test_ein_funknetz_mit_fehler_nimmt_die_anderen_nicht_mit():
    kaputt = {
        **WLAN,
        ("WLANConfiguration2", "GetChannelInfo"): FritzServiceError("x"),
        ("WLANConfiguration3", "GetInfo"): FritzServiceError("x"),
    }
    d = holen(kaputt, {"/wlan?sid=abc": WLANLISTE.encode()}, langsam=True, dienste=DIENSTE)
    assert (
        [b.band for b in d.wlan_baender] == ["2,4"] and len(d.wlan_geraete) == 3 and d.fehler == []
    )


def test_ohne_wlan_dienst_und_ohne_baender_aktion():
    d = holen(
        {
            **WLAN,
            ("X_AVM-DE_WANMobileConnection1", "GetEnabledBandCapabilities"): FritzServiceError("x"),
        },
        langsam=True,
    )
    assert (
        d.wlan_geraete is None
        and d.mobil is not None
        and d.mobil_baender is None
        and d.fehler == []
    )


def test_mesh_nur_im_langsamen_abruf():
    assert holen().mesh is None
    assert holen(langsam=True).mesh["00:11:22:33:44:04"] == "FRITZ!Repeater 3000"


# WU-0009: Zugang und Werte der Leitung – Antworten in der Form der FRITZ!-Doku (TR-064 Support), erfunden
ZUGANG_MOBIL = {
    ("WANCommonInterfaceConfig1", "GetCommonLinkProperties"): {
        "NewWANAccessType": "X_AVM-DE_LTE",
        "NewLayer1UpstreamMaxBitRate": 150_000_000,
        "NewLayer1DownstreamMaxBitRate": 1_000_000_000,
        "NewPhysicalLinkStatus": "Up",
    },
    ("X_AVM-DE_WANMobileConnection1", "GetInfo"): {
        "NewEnable": True,
        "NewStatus": "PIN successful",
    },
    ("Layer3Forwarding1", "GetDefaultConnectionService"): {
        "NewDefaultConnectionService": "1.WANIPConnection.1"
    },
    ("WANIPConnection1", "GetExternalIPAddress"): {"NewExternalIPAddress": "10.120.7.88"},
}
DIENSTE_MOBIL = ("X_AVM-DE_WANMobileConnection1", "WANCommonInterfaceConfig1", "Layer3Forwarding1")
DSL_ANTWORTEN = {
    ("WANCommonInterfaceConfig1", "GetCommonLinkProperties"): {
        "NewWANAccessType": "DSL",
        "NewLayer1UpstreamMaxBitRate": 38_189_000,
        "NewLayer1DownstreamMaxBitRate": 108_396_000,
        "NewPhysicalLinkStatus": "Up",
    },
    ("WANCommonInterfaceConfig1", "X_AVM-DE_GetAddonInfos"): {"NewX_AVM-DE_WANAccessType": "DSL"},
    ("WANDSLInterfaceConfig1", "GetInfo"): {
        "NewEnable": True,
        "NewStatus": "Up",
        "NewDataPath": "Interleaved",
        "NewUpstreamCurrRate": 38_189,
        "NewDownstreamCurrRate": 108_396,
        "NewUpstreamMaxRate": 41_012,
        "NewDownstreamMaxRate": 124_620,
        "NewUpstreamNoiseMargin": 79,
        "NewDownstreamNoiseMargin": 52,
        "NewUpstreamAttenuation": 90,
        "NewDownstreamAttenuation": 140,
        "NewATURVendor": "41564d00",
        "NewATURCountry": "0",
        "NewUpstreamPower": 0,
        "NewDownstreamPower": 0,
    },
    ("WANDSLInterfaceConfig1", "X_AVM-DE_GetDSLInfo"): {
        "NewModulationType": "VDSL",
        "NewCurrentProfile": "35b",
    },
    ("WANDSLInterfaceConfig1", "GetStatisticsTotal"): {
        "NewCRCErrors": 120,
        "NewFECErrors": 18_400,
        "NewATUCCRCErrors": 3,
        "NewATUCFECErrors": 200,
    },
    ("Layer3Forwarding1", "GetDefaultConnectionService"): {
        "NewDefaultConnectionService": "1.WANPPPConnection.1"
    },
    ("WANPPPConnection1", "GetExternalIPAddress"): {"NewExternalIPAddress": "84.115.20.7"},
}
FASER_ANTWORTEN = {
    ("WANCommonInterfaceConfig1", "GetCommonLinkProperties"): {
        "NewWANAccessType": "X_AVM-DE_Fiber",
        "NewPhysicalLinkStatus": "Up",
    },
    ("X_AVM-DE_WANFiber1", "GetInfo"): {
        "NewOpticalSignalLevel": -19_400,
        "NewLowerOpticalThreshold": -28_000,
        "NewUpperOpticalThreshold": -8_000,
        "NewTransmitOpticalLevel": 2_100,
        "NewLowerTransmitPowerThreshold": 500,
        "NewUpperTransmitPowerThreshold": 5_000,
        "NewSFPVendor": "Erfunden",
        "NewSFPPartNumber": "X1",
        "NewSFPSerialNumber": "SN-NIE-ZEIGEN",
        "NewSFPType": 1,
        "NewTXWaveLength": 1310,
        "NewFiberMode": "GPON",
    },
    ("X_AVM-DE_WANFiber1", "GetStatistics"): {
        "NewPacketErrorsReceived": 0,
        "NewPacketErrorsSent": 0,
        "NewResyncs": 1,
        "NewMinutesInShowtime": 30_240,
    },
}


def test_zugang_mobilfunk_nur_im_langsamen_takt():
    assert holen(ZUGANG_MOBIL, dienste=DIENSTE_MOBIL).zugang is None
    d = holen(ZUGANG_MOBIL, langsam=True, dienste=DIENSTE_MOBIL)
    z = d.zugang
    assert d.fehler == [] and z is not None
    assert (z.zugangsart, z.link, z.mobil_dienst, z.mobil_an) == ("X_AVM-DE_LTE", "Up", True, True)
    assert (z.dsl_dienst, z.faser_dienst, z.down_bit) == (False, False, 1_000_000_000)
    assert (z.wan_netz, z.vorschlag) == ("privat", "10.120.7.1")
    assert "10.120.7.88" not in repr(d), "die WAN-Adresse selbst bleibt in box.py"
    assert d.dsl is None and d.faser is None
    # „Erneut suchen“: auch außerhalb des langsamen Takts
    b = bx.Box(ZUGANG)
    with patch.object(
        bx,
        "FritzConnection",
        return_value=fake_box({**AKTIONEN, **ZUGANG_MOBIL}, DATEIEN, DIENSTE_MOBIL),
    ):
        assert b.holen(False, True, "192.0.2.1", "de", zugang_fragen=True).zugang is not None


def test_zugang_dsl_mit_werten():
    dienste = (*DIENSTE_MOBIL, "WANDSLInterfaceConfig1")
    d = holen(DSL_ANTWORTEN, langsam=True, dienste=dienste)
    assert d.fehler == []
    assert (
        d.zugang.zugangsart == "DSL" and d.zugang.art_avm == "DSL" and d.zugang.dsl_status == "Up"
    )
    assert d.zugang.wan_netz == "oeffentlich" and d.zugang.vorschlag == ""
    x = d.dsl
    assert (x.sync_down, x.max_down, x.marge_down, x.daempfung_down) == (108_396, 124_620, 52, 140)
    assert (x.modulation, x.profil, x.crc, x.fec, x.crc_gegen) == ("VDSL", "35b", 120, 18_400, 3)


def test_dsl_ohne_neuere_aktionen_und_ausgeschaltet():
    """Ältere FRITZ!OS ohne X_AVM-DE_GetDSLInfo/X_AVM-DE_GetAddonInfos: der Rest gilt; ausgeschaltet: keine Werte."""
    dienste = (*DIENSTE_MOBIL, "WANDSLInterfaceConfig1")
    alt = {k: v for k, v in DSL_ANTWORTEN.items() if "X_AVM-DE" not in k[1]}
    d = holen(alt, langsam=True, dienste=dienste)
    assert d.fehler == [] and d.dsl.profil == "" and d.dsl.sync_down == 108_396
    assert d.zugang.art_avm == ""
    aus = {**DSL_ANTWORTEN, ("WANDSLInterfaceConfig1", "GetInfo"): {"NewStatus": "Disabled"}}
    d = holen(aus, langsam=True, dienste=dienste)
    assert d.zugang.dsl_status == "Disabled" and d.dsl is not None, (
        "Internet über DSL: Werte auch so"
    )
    # Mobilfunk-Box mit ungenutztem DSL-Anschluss: keine DSL-Werte (und damit keine DSL-Entitäten)
    ungenutzt = {**ZUGANG_MOBIL, ("WANDSLInterfaceConfig1", "GetInfo"): {"NewStatus": "NoSignal"}}
    d = holen(ungenutzt, langsam=True, dienste=dienste)
    assert d.zugang.dsl_status == "NoSignal" and d.dsl is None and d.fehler == []


def test_zugang_glasfaser_ohne_seriennummer():
    dienste = ("WANCommonInterfaceConfig1", "X_AVM-DE_WANFiber1")
    d = holen(FASER_ANTWORTEN, langsam=True, dienste=dienste)
    assert d.zugang.faser_modus == "GPON" and d.zugang.wan_netz == ""
    f = d.faser
    assert (f.rx, f.rx_min, f.rx_max, f.tx, f.minuten) == (-19_400, -28_000, -8_000, 2_100, 30_240)
    assert "SN-NIE-ZEIGEN" not in repr(d)
