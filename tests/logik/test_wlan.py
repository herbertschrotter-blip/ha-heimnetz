"""WLAN der Box: Bänder, Geräteliste, Kanalwechsel, Befunde."""

from logik import wlan as wl

LISTE = """<?xml version="1.0" encoding="UTF-8"?>
<List><TotalAssociations>4</TotalAssociations>
<Item><AssociatedDeviceIndex>1</AssociatedDeviceIndex><AssociatedDeviceMACAddress>aa:00:00:00:00:01</AssociatedDeviceMACAddress>
<X_AVM-DE_Speed>866</X_AVM-DE_Speed><X_AVM-DE_SignalStrength>92</X_AVM-DE_SignalStrength>
<AssociatedDeviceChannel>44</AssociatedDeviceChannel><AssociatedDeviceGuest>0</AssociatedDeviceGuest></Item>
<Item><AssociatedDeviceMACAddress>aa:00:00:00:00:02</AssociatedDeviceMACAddress>
<X_AVM-DE_Speed>6</X_AVM-DE_Speed><X_AVM-DE_SignalStrength>18</X_AVM-DE_SignalStrength>
<AssociatedDeviceChannel>6</AssociatedDeviceChannel><AssociatedDeviceGuest>0</AssociatedDeviceGuest></Item>
<Item><AssociatedDeviceMACAddress>aa:00:00:00:00:03</AssociatedDeviceMACAddress>
<X_AVM-DE_Speed>72</X_AVM-DE_Speed><X_AVM-DE_SignalStrength>25</X_AVM-DE_SignalStrength>
<AssociatedDeviceChannel>6</AssociatedDeviceChannel><AssociatedDeviceGuest>1</AssociatedDeviceGuest></Item>
<Item><AssociatedDeviceMACAddress></AssociatedDeviceMACAddress></Item>
</List>"""

B24 = wl.Band("2,4", True, 6, True, "ax")
B5 = wl.Band("5", True, 44, True, "ax")


def test_band_aus_antwort():
    info = {
        "NewEnable": True,
        "NewStatus": "Up",
        "NewStandard": "ax",
        "NewX_AVM-DE_FrequencyBand": "5000",
        "NewSSID": "geheim",
    }
    b = wl.band_aus(info, {"NewChannel": 44, "NewX_AVM-DEAuto_ChannelEnabled": "1"})
    assert b == wl.Band("5", True, 44, True, "ax")
    assert "geheim" not in repr(b)
    assert wl.band_aus({"NewX_AVM-DE_FrequencyBand": "unknown"}, {}) is None
    aus = wl.band_aus(
        {"NewEnable": "0", "NewStatus": "Disabled", "NewX_AVM-DE_FrequencyBand": "2400"}, {}
    )
    assert aus is not None and (aus.an, aus.kanal, aus.auto) == (False, None, None)
    assert wl.ist_gast({"NewX_AVM-DE_APType": "guest"}) and not wl.ist_gast({})


def test_geraeteliste():
    g = wl.geraete_aus(LISTE)
    assert [(x.mac, x.kanal, x.signal, x.mbit, x.gast) for x in g] == [
        ("AA:00:00:00:00:01", 44, 92, 866, False),
        ("AA:00:00:00:00:02", 6, 18, 6, False),
        ("AA:00:00:00:00:03", 6, 25, 72, True),
    ]
    assert [wl.band_von(x, (B24, B5)) for x in g] == ["5", "2,4", "2,4"]
    assert (
        wl.band_von(wl.Funkgeraet("X", 100, 50, 1, False), ()) == "5"
    )  # ohne Bänder: nach Kanalnummer
    assert wl.band_von(wl.Funkgeraet("X", None, 50, 1, False), ()) is None
    b6 = wl.Band(
        "6", True, 37, True, "be"
    )  # Box mit 6 GHz: Kanal 5 ist ohne passendes Band nicht eindeutig
    assert wl.band_von(wl.Funkgeraet("X", 5, 50, 1, False), (B24, B5, b6)) is None


def test_kanalwechsel():
    e, neu = wl.abgleich({}, (B24, B5))
    assert e == [] and neu == {"2,4": 6, "5": 44}
    e, neu = wl.abgleich(neu, (B24, wl.Band("5", True, 36, True, "ax")))
    assert [x.text for x in e] == ["WLAN 5 GHz: Kanal 44 → 36"] and neu["5"] == 36
    zwei5 = (
        B24,
        B5,
        wl.Band("5", True, 100, True, "ax"),
    )  # zwei Funknetze auf 5 GHz: kein Schein-Wechsel
    _, neu = wl.abgleich({}, zwei5)
    e, neu = wl.abgleich(neu, zwei5)
    assert e == [] and neu == {"2,4": 6, "5": 44, "5#2": 100}


def test_befunde():
    w = wl.Wlan((B24, B5), False, wl.geraete_aus(LISTE))
    schnell = wl.schnell_gesehen(["AA:00:00:00:00:02"], w)
    assert schnell == ["AA:00:00:00:00:01", "AA:00:00:00:00:02"]
    assert wl.schnell_gesehen(["ALT"], w, ["AA:00:00:00:00:01"]) == [
        "AA:00:00:00:00:01"
    ]  # Unbekanntes fällt heraus
    b = wl.befunde(w, schnell, 40)
    assert b.schwach == ("AA:00:00:00:00:02",)  # Gast mit 25 % zählt nicht
    assert b.auf_24 == ("AA:00:00:00:00:02",)
    nur24 = wl.Wlan((B24,), None, w.geraete)  # ohne 5-GHz-Netz kein Hinweis „hängt auf 2,4 GHz“
    assert wl.befunde(nur24, schnell, 40).auf_24 == ()
    assert wl.lage_signal(None) is None and wl.lage_signal(10) == 0 and wl.lage_signal(95) == 1
