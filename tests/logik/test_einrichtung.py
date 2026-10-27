"""Einrichtung (WU-0007): welche Voraussetzungen eingerichtet sind und was fehlt – Stufen wie im README, Status je
Zeile, Knöpfe mit dem richtigen Ziel, Zusammenfassung und Punkt am Reiter."""

from urllib.parse import parse_qs, urlsplit

from logik import einrichtung as ei
from logik.sprache import ENG

ALLE_E = {d: 1 for d in ei.MIT_EINTRAG}


def stand(**kw) -> ei.Stand:
    """Alles eingerichtet; `kw` stellt den Fall ein."""
    werte = {
        "ha_version": "2026.10.2",
        "ha_mindest": "2026.10.1",
        "geladen": frozenset(
            {"recorder", "hacs", "met", "holiday", "fritz", "ookla_speedtest", "scribe"}
        ),
        "eintraege": ALLE_E,
        "eintraege_geladen": ALLE_E,
        "box_modell": "FRITZ!Box 6860 5G",
        "recorder_tage": 10,
        "opencellid": True,
    }
    werte.update(kw)
    return ei.Stand(**werte)


def ohne(*domains: str) -> dict[str, int]:
    return {d: 0 if d in domains else 1 for d in ei.MIT_EINTRAG}


def teil(s: ei.Stand, schluessel: str, sp: str = "de") -> ei.Teil:
    return next(x for x in ei.teile(s, sp) if x.schluessel == schluessel)


def test_reihenfolge_und_stufen_wie_im_readme():
    t = ei.teile(stand())
    assert [(x.stufe, x.schluessel) for x in t] == [
        ("muss", "homeassistant"),
        ("muss", "fritz"),
        ("muss", "recorder"),
        ("muss", "hacs"),
        ("soll", "ookla"),
        ("soll", "met"),
        ("soll", "holiday"),
        ("kann", "opencellid"),
        ("kann", "archiv"),
    ]
    assert all(x.status == "ok" and not x.aktionen for x in t)


def test_alles_eingerichtet_ohne_punkt():
    b = ei.bewerten(stand())
    assert (b["muss_fehlt"], b["soll_fehlt"], b["punkt"]) == (0, 0, None)
    assert [(s["stufe"], s["ok"], s["von"]) for s in b["stufen"]] == [
        ("muss", 4, 4),
        ("soll", 3, 3),
        ("kann", 2, 2),
    ]


def test_stand_bei_eingerichtet():
    s = stand()
    assert teil(s, "homeassistant").stand == "2026.10.2"
    assert teil(s, "homeassistant").wofuer == "ab 2026.10.1"
    assert teil(s, "fritz").stand == "eingerichtet · FRITZ!Box 6860 5G"
    assert teil(s, "recorder").stand == "aktiv · 10 Tage"
    assert teil(stand(recorder_tage=None), "recorder").stand == "aktiv"
    assert teil(s, "hacs").stand == "installiert"
    assert teil(s, "opencellid").stand == "eingetragen"
    assert teil(s, "archiv").stand == "Scribe eingerichtet"
    assert teil(stand(box_modell=""), "fritz").stand == "eingerichtet"


def test_ha_zu_alt_ist_muss():
    x = teil(stand(ha_version="2026.9.4"), "homeassistant")
    assert x.status == "muss" and x.hinweis == "2026.9.4 ist zu alt"
    assert [a.ziel for a in x.aktionen] == ["/config/updates"]
    assert teil(stand(ha_version="2026.11.0b1"), "homeassistant").status == "ok"
    assert teil(stand(ha_version="2026.10.1"), "homeassistant").status == "ok"
    assert ei.version_tupel("2026.10.0.dev20261001") == (2026, 10, 0)
    assert ei.version_tupel("2027.1") == (2027, 1, 0)


def test_fritz_fehlt_ist_muss_mit_einrichten():
    b = ei.bewerten(stand(eintraege=ohne("fritz"), eintraege_geladen=ohne("fritz")))
    assert b["punkt"] == "rot" and b["muss_fehlt"] == 1
    x = teil(stand(eintraege=ohne("fritz")), "fritz")
    assert x.status == "muss"
    assert [a.ziel for a in x.aktionen] == ["/_my_redirect/config_flow_start?domain=fritz"]


def test_fritz_vorhanden_reicht_auch_nicht_geladen():
    """Heimnetz liest nur den Zugang aus dem Eintrag – geladen muss FRITZ!Box Tools dafür nicht sein."""
    assert teil(stand(eintraege_geladen=ohne("fritz")), "fritz").status == "ok"


def test_recorder_fehlt():
    x = teil(stand(geladen=frozenset({"hacs"})), "recorder")
    assert x.status == "muss" and x.hinweis == "nicht geladen"
    assert x.aktionen[0].extern


def test_ohne_hacs_anleitung_und_bei_hacs_teilen_erst_hacs():
    s = stand(
        eintraege=ohne("hacs", "ookla_speedtest", "scribe"),
        eintraege_geladen=ohne("hacs", "ookla_speedtest", "scribe"),
    )
    h = teil(s, "hacs")
    assert h.status == "muss" and h.wofuer == "ohne HACS kommen keine Updates"
    assert [(a.ziel, a.extern) for a in h.aktionen] == [("https://hacs.xyz/docs/use/", True)]
    for k in ("ookla", "archiv"):
        x = teil(s, k)
        assert x.hinweis == "erst HACS installieren" and not x.aktionen, k
    assert teil(s, "ookla").status == "fehlt" and teil(s, "archiv").status == "aus"


def test_hacs_heruntergeladen_aber_nicht_geladen():
    s = stand(
        eintraege=ohne("hacs"), eintraege_geladen=ohne("hacs"), heruntergeladen=frozenset({"hacs"})
    )
    h = teil(s, "hacs")
    assert h.status == "muss" and h.hinweis == "heruntergeladen – nach einem Neustart einrichten"
    assert [a.ziel for a in h.aktionen] == ["/_my_redirect/config_flow_start?domain=hacs"]


def test_ookla_aus_hacs_holen():
    s = stand(eintraege=ohne("ookla_speedtest"), eintraege_geladen=ohne("ookla_speedtest"))
    x = teil(s, "ookla")
    assert x.status == "fehlt" and x.hinweis is None
    (a,) = x.aktionen
    assert a.text == "In HACS öffnen ↗" and not a.extern
    u = urlsplit(a.ziel)
    assert u.path == "/_my_redirect/hacs_repository"
    assert parse_qs(u.query) == {
        "owner": ["soulripper13"],
        "repository": ["hass-speedtest-ookla"],
        "category": ["integration"],
    }
    b = ei.bewerten(s)
    assert b["punkt"] == "orange" and b["soll_fehlt"] == 1 and b["muss_fehlt"] == 0


def test_ookla_heruntergeladen_nach_dem_neustart():
    s = stand(
        eintraege=ohne("ookla_speedtest"),
        eintraege_geladen=ohne("ookla_speedtest"),
        heruntergeladen=frozenset({"ookla_speedtest"}),
    )
    x = teil(s, "ookla")
    assert x.hinweis == "heruntergeladen – nach einem Neustart einrichten"
    assert [a.ziel for a in x.aktionen] == [
        "/_my_redirect/config_flow_start?domain=ookla_speedtest"
    ]


def test_eingerichtet_aber_nicht_geladen():
    x = teil(stand(eintraege_geladen=ohne("met")), "met")
    assert x.status == "fehlt" and x.hinweis == "eingerichtet, aber nicht geladen"
    assert [a.ziel for a in x.aktionen] == ["/config/integrations/integration/met"]


def test_met_und_holiday_einrichten():
    s = stand(eintraege=ohne("met", "holiday"), eintraege_geladen=ohne("met", "holiday"))
    for k in ("met", "holiday"):
        x = teil(s, k)
        assert x.status == "fehlt"
        assert [a.ziel for a in x.aktionen] == [f"/_my_redirect/config_flow_start?domain={k}"]
    assert ei.bewerten(s)["soll_fehlt"] == 2


def test_opencellid_ohne_schluessel():
    x = teil(stand(opencellid=False), "opencellid")
    assert x.status == "aus"
    assert [(a.ziel, a.extern) for a in x.aktionen] == [
        ("https://opencellid.org", True),
        ("/config/integrations/integration/heimnetz", False),
    ]
    # Kann fehlt: kein Punkt am Reiter
    assert ei.bewerten(stand(opencellid=False))["punkt"] is None


def test_langzeitarchiv_scribe_oder_influxdb():
    ohne_s = ohne("scribe")
    x = teil(stand(eintraege=ohne_s, eintraege_geladen=ohne_s), "archiv")
    assert x.status == "aus"
    assert "repository=scribe" in x.aktionen[0].ziel and "owner=jonathan-gtd" in x.aktionen[0].ziel
    influx = stand(
        eintraege=ohne_s, eintraege_geladen=ohne_s, geladen=frozenset({"recorder", "influxdb"})
    )
    y = teil(influx, "archiv")
    assert y.status == "ok" and y.stand == "InfluxDB aktiv"


def test_muss_vor_soll_beim_punkt():
    s = stand(geladen=frozenset(), eintraege=ohne("met"), eintraege_geladen=ohne("met"))
    b = ei.bewerten(s)
    assert (b["muss_fehlt"], b["soll_fehlt"], b["punkt"]) == (1, 1, "rot")


def test_englisch():
    s = stand(
        eintraege=ohne("ookla_speedtest"),
        eintraege_geladen=ohne("ookla_speedtest"),
        opencellid=False,
    )
    assert teil(s, "ookla", ENG).aktionen[0].text == "Open in HACS ↗"
    assert teil(s, "fritz", ENG).stand == "set up · FRITZ!Box 6860 5G"
    assert teil(s, "homeassistant", ENG).wofuer == "2026.10.1 or newer"
    assert teil(s, "opencellid", ENG).name == "OpenCellID key"


def test_jede_zeile_hat_dieselben_felder():
    """Vertrag mit der Seite: jede Zeile hat alle Felder (leer = None), der OpenCellID-Schlüssel ist nie dabei."""
    b = ei.bewerten(stand(opencellid=False))
    zeilen = [x for s in b["stufen"] for x in s["teile"]]
    assert {tuple(sorted(x)) for x in zeilen} == {
        ("aktionen", "hinweis", "name", "schluessel", "stand", "status", "stufe", "wofuer")
    }
