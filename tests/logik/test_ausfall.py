"""Ausfälle des Pi (18.11.2026): Speicher, Systemprotokoll des vorigen Starts, Bericht."""

from __future__ import annotations

from datetime import UTC, datetime

from logik import ausfall as af
from logik.sprache import ENG

BOOT = """\
2026-11-09 08:12:51.818+01:00 homeassistant kernel: Out of memory: Killed process 12 (MainThread) total-vm:12211988kB, anon-rss:11070952kB, file-rss:39216kB
2026-11-09 08:14:45.846+01:00 homeassistant kernel: Free swap  = 0kB
2026-11-10 01:55:55.030+01:00 homeassistant dockerd[691]: level=error msg="[resolver] failed to query external DNS server"
"""
SAUBER = "2026-11-10 17:41:01.584+01:00 homeassistant systemd[1]: Stopping Flush Journal to Persistent Storage...\n"


def ts(s: str) -> float:
    return datetime.fromisoformat(s).timestamp()


def test_meminfo_und_knapp():
    text = "MemTotal:       16384020 kB\nMemAvailable:   11068524 kB\nSwapTotal:       4194300 kB\nSwapFree:        3691316 kB\n"
    assert af.meminfo(text) == (16000, 10809, 4095, 3604)
    gut = af.Speicherstand(0, 16000, 11000, 4096, 3600, {"Home Assistant": 1000})
    assert af.knapp(gut) is None
    assert af.knapp(af.Speicherstand(0, 16000, 1000, 4096, 3600)) == "frei"
    assert af.knapp(af.Speicherstand(0, 16000, 9000, 4096, 500)) == "swap"


def test_speicherstand_rund_und_top():
    s = af.Speicherstand(
        5,
        16000,
        900,
        4096,
        0,
        {"Home Assistant": 10900, "Claude Terminal": 4400, "Samba": 50, "X": 300},
    )
    assert af.Speicherstand.aus_dict(5, s.als_dict()) == s
    assert [n for n, _ in s.top] == ["Home Assistant", "Claude Terminal", "X"]
    assert "Home Assistant 10,6 GB" in af.knapp_text(s)


def test_boot_auswerten():
    b = af.boot_auswerten(BOOT)
    assert b.ende == ts("2026-11-10T01:55:55.030+01:00")
    assert not b.sauber and b.swap_leer
    assert b.oom == ((ts("2026-11-09T08:12:51.818+01:00"), "MainThread", 10811),)
    assert af.boot_auswerten(BOOT + SAUBER).sauber


def test_bericht_nur_bei_unsauberem_ende():
    assert af.bericht(af.Lage(jetzt=100, lebt=50, sauber=60, pi_start=None), UTC) is None
    assert af.bericht(af.Lage(jetzt=100, lebt=None, sauber=None, pi_start=None), UTC) is None


def test_bericht_pi_neu_mit_speicher_und_steckdose():
    lebt, start = ts("2026-11-10T06:26:00+00:00"), ts("2026-11-10T08:20:00+00:00")
    lage = af.Lage(
        jetzt=start + 120,
        lebt=lebt,
        sauber=None,
        pi_start=start,
        boot=af.boot_auswerten(BOOT),
        speicher=af.Speicherstand(
            lebt - 100, 16000, 900, 4096, 0, {"Home Assistant": 10900, "Claude Terminal": 4400}
        ),
        dose=("Steckdose: Pi: Strom 15 s aus …",),
    )
    z = af.bericht(lage, UTC)
    assert (
        z[0] == "Home Assistant lief zuletzt 10.11. 06:26, wieder da 10.11. 08:22 (1 h 56 min weg)"
    )
    assert "Systemprotokoll endet 10.11. 00:55 ohne Herunterfahren" in z[1]
    assert z[2].startswith(
        "Speicher voll: der Kernel hat 1× ein Programm beendet (MainThread, bis 10,6 GB)"
    )
    assert z[3] == "Die Auslagerung war ganz voll"
    assert "am meisten: Home Assistant 10,6 GB, Claude Terminal 4,3 GB" in z[4]
    assert z[5] == "Steckdose: Pi: Strom 15 s aus …"
    assert af.bericht(lage, UTC, ENG)[0].startswith("Home Assistant was last alive")


def test_bericht_nur_home_assistant_neu():
    z = af.bericht(af.Lage(jetzt=7200, lebt=3600, sauber=None, pi_start=10), UTC)
    assert z[1] == "Nur Home Assistant ist neu gestartet, der Pi lief durch"
