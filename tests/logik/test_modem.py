"""Reine Logik des Modem-Werkzeugs (WU-0008): erlaubte Adressen, Schwärzen, Erkennen, Anmelde-Hash – ohne Netz."""

import hashlib

import pytest
from logik import modem as lm


@pytest.mark.parametrize(
    "adresse",
    [
        "192.168.0.1",
        "192.168.178.1",
        "10.0.0.138",
        "172.16.5.4",
        "172.31.255.1",
        "fd00::1",
        " 192.168.0.1 ",
    ],
)
def test_private_adressen_erlaubt(adresse):
    assert lm.adresse_erlaubt(adresse)


@pytest.mark.parametrize(
    "adresse",
    [
        "8.8.8.8",  # öffentlich
        "1.1.1.1",
        "172.32.0.1",  # knapp außerhalb des privaten Bereichs
        "127.0.0.1",  # Loopback
        "::1",
        "169.254.1.1",  # Link-Local
        "0.0.0.0",  # unspezifiziert
        "224.0.0.1",  # Multicast
        "fritz.box",  # Hostname
        "modem.local",
        "",
        "nicht-ip",
        "192.168.0.999",
    ],
)
def test_fremde_und_hostnamen_abgelehnt(adresse):
    assert not lm.adresse_erlaubt(adresse)


def test_schwaerzen_nach_schluessel():
    roh = {
        "imei": "356938035643809",
        "imsi": "232030000000000",
        "iccid": "8943000000000000000",
        "msisdn": "+436601234567",
        "mac_addr": "AA:BB:CC:DD:EE:FF",
        "wan_ipaddr": "203.0.113.7",
        "SSID1": "MeinWLAN",
        "WPAPSK1": "geheimespasswort",
        "loginfo_password": "abc",
        "sn": "ZTE1234567",
        "stok": "deadbeef",
        "apn_user": "drei",
    }
    rein, anzahl = lm.schwaerzen(roh)
    assert all(rein[k] == lm.ERSATZ for k in roh), rein
    assert anzahl == len(roh)


def test_zellkennung_und_signal_bleiben():
    roh = {
        "cell_id": "1A2B3C4",
        "lte_cell_id": "12345",
        "enodeb_id": "4711",
        "tac": "4E21",
        "lac": "1234",
        "plmn": "23205",
        "lte_pci": "301",
        "nr5g_pci": "512",
        "lte_band": "B3",
        "nr5g_action_band": "n78",
        "lte_rsrp": "-97",
        "lte_rsrq": "-11",
        "lte_snr": "9",
        "nr5g_rsrp": "-104",
        "Z5g_SINR": "6",
        "rssi": "-70",
        "network_type": "ENDC",
        "network_provider": "3 AT",
        "modem_model": "ZTE G5TC",
        "wa_inner_version": "BD_G5TCV1.0.0B05",
        "earfcn": "1650",
        "signalbar_num": "4",
    }
    rein, anzahl = lm.schwaerzen(roh)
    assert anzahl == 0
    assert rein == roh


def test_schwaerzen_nach_wert_in_freiem_text():
    roh = {
        "meldung": "IMEI 356938035643809, Mail a@b.de, Tel +43 660 1234567, MAC AA:BB:CC:DD:EE:FF, WAN 93.184.216.34"
    }
    rein, anzahl = lm.schwaerzen(roh)
    assert "356938035643809" not in rein["meldung"]
    assert "a@b.de" not in rein["meldung"]
    assert "93.184.216.34" not in rein["meldung"]
    assert "AA:BB:CC:DD:EE:FF" not in rein["meldung"]
    assert anzahl >= 5


def test_mac_mit_bindestrich():
    rein, anzahl = lm.schwaerzen({"info": "Gerät aa-bb-cc-dd-ee-ff"})
    assert "aa-bb-cc-dd-ee-ff" not in rein["info"] and anzahl == 1


def test_private_ip_im_text_bleibt():
    rein, anzahl = lm.schwaerzen({"hinweis": "Modem unter 192.168.0.1 erreichbar"})
    assert "192.168.0.1" in rein["hinweis"]
    assert anzahl == 0


def test_rekursiv_und_eingebettetes_json():
    roh = {
        "liste": [{"imei": "356938035643809"}, {"tac": "4E21"}],
        "rohtext": '{"iccid": "8943000000000000000", "lte_pci": "7"}',
    }
    rein, anzahl = lm.schwaerzen(roh)
    assert rein["liste"][0]["imei"] == lm.ERSATZ
    assert rein["liste"][1]["tac"] == "4E21"
    assert lm.ERSATZ in rein["rohtext"] and '"lte_pci": "7"' in rein["rohtext"]
    assert anzahl == 2


def test_zaehler_nur_nichtleere_werte():
    assert lm.werte_zaehlen({"a": "x", "b": "", "c": None, "d": 0, "e": [1, 2]}) == 4


@pytest.mark.parametrize(
    "html,zte,modell",
    [
        ("<title>ZTE G5TC</title>", True, "ZTE G5TC"),
        ("<html>login via goform_get_cmd_process</html>", True, None),
        ("<p>powered by ubus</p>", True, None),
        ("<title>FRITZ!Box 6860</title>", False, None),
        ("ZTE MC801A HyperBox", True, "ZTE MC801A"),
    ],
)
def test_erkennen(html, zte, modell):
    assert lm.erkennen(html) == (zte, modell)


def test_anmelde_hash_passt_zur_oeffentlichen_formel():
    kennwort, ld = "geheim", "ABCDEF0123456789"
    erst = hashlib.sha256(kennwort.encode()).hexdigest().upper()
    erwartet = hashlib.sha256((erst + ld).encode()).hexdigest().upper()
    assert lm.anmelde_hash(kennwort, ld) == erwartet
    assert lm.anmelde_hash(kennwort, ld.lower()) == erwartet  # LD wird großgeschrieben
    assert lm.anmelde_hash(kennwort, ld).isupper()
