"""Robustheit der HA-Anbindung: Journal beim Schreiben, Entladen während eines Abrufs, gescheitertes Setup,
beschädigte Datenbank, Sicherung ohne Ende, Gedächtnis-Schreiblast, doppelte Speedtest-Messung."""

import asyncio
import json
import sqlite3
import time
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from custom_components.heimnetz import speicher as sp
from custom_components.heimnetz.const import DOMAIN
from custom_components.heimnetz.logik.ereignis import INFO, Ereignis
from custom_components.heimnetz.speedtest import OoklaSensoren, Speedtest


async def _laden(hass: HomeAssistant, eintrag):
    assert await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    return eintrag.runtime_data


def _journal(db) -> list[str]:
    return [z.ereignis.text for z in reversed(db.journal_lesen(0, grenze=1000))]  # älteste zuerst


async def test_zeilen_waehrend_des_schreibens_gehen_nicht_verloren(
    hass: HomeAssistant, eintrag, box, pi
):
    """Befund 1: was während des Schreibens dazukommt (Wächter, Ausfall, Zustellfehler), geht beim nächsten Mal mit;
    scheitert das Schreiben, bleiben die Zeilen in ihrer Reihenfolge ausstehend."""
    lz = await _laden(hass, eintrag)
    abruf, db = lz.abruf, lz.datenbank
    original = db.abruf_schreiben

    def schreiben_und_dabei_merken(*args):
        original(*args)
        abruf.journal_merken([Ereignis("waechter", INFO, "während des Schreibens")])

    with patch.object(db, "abruf_schreiben", side_effect=schreiben_und_dabei_merken):
        await abruf.async_refresh()
    await abruf.async_refresh()
    assert "während des Schreibens" in await hass.async_add_executor_job(_journal, db)

    abruf.journal_merken([Ereignis("waechter", INFO, "erste")])
    with patch.object(db, "abruf_schreiben", side_effect=sqlite3.OperationalError("locked")):
        await abruf.async_refresh()
    abruf.journal_merken([Ereignis("waechter", INFO, "zweite")])
    assert [z.ereignis.text for z in abruf._ausstehend_journal][:1] == ["erste"]  # noqa: SLF001
    await abruf.async_refresh()
    texte = await hass.async_add_executor_job(_journal, db)
    assert "erste" in texte and "zweite" in texte
    assert not abruf._ausstehend_journal  # noqa: SLF001


async def test_entladen_waehrend_abruf(hass: HomeAssistant, eintrag, box, pi, caplog):
    """Befund 2/14: wird während eines Abrufs entladen, hört er nach dem nächsten await auf – schreibt nicht in die
    geschlossene Datenbank und meldet den Speedtest nicht wieder an. Hintergrund-Aufgaben des Eintrags enden vor dem
    Schließen der Datenbank."""
    lz = await _laden(hass, eintrag)
    abruf = lz.abruf
    weiter = asyncio.Event()
    gestartet = asyncio.Event()
    alt = pi.return_value

    async def langsam(_router):
        gestartet.set()
        await weiter.wait()
        return alt

    nachtrag_lief = asyncio.Event()

    async def haengt():
        nachtrag_lief.set()
        await asyncio.sleep(3600)

    eintrag.async_create_background_task(hass, haengt(), "heimnetz_test_haengt")
    pi.side_effect = langsam
    with patch.object(abruf.speedtest, "verbinden") as verbinden:
        aufgabe = hass.async_create_task(abruf.async_refresh())
        await gestartet.wait()
        await nachtrag_lief.wait()
        assert await hass.config_entries.async_unload(eintrag.entry_id)
        assert not any(
            not a.done()
            for a in eintrag._background_tasks  # noqa: SLF001
        ), "Hintergrund-Aufgaben vor dem Schließen beendet"
        weiter.set()
        await aufgabe
        await hass.async_block_till_done()
    verbinden.assert_not_called()
    assert "Datenbank nicht geöffnet" not in caplog.text
    assert "Schreiben in die Datenbank fehlgeschlagen" not in caplog.text


async def test_speedtest_nach_dem_schliessen_nicht_wieder_verbunden(hass: HomeAssistant):
    st = Speedtest(hass, list, lambda: 0.0, lambda _m: None)
    st.schliessen()
    with patch("custom_components.heimnetz.speedtest.finden") as finden:
        st.verbinden()
    finden.assert_not_called()


async def test_dieselbe_messung_nur_einmal(hass: HomeAssistant):
    """Befund 11: solange eine Messung eingetragen wird, meldet der Speedtest sie nicht noch einmal; scheitert das
    Eintragen, holt der nächste Abruf sie nach."""
    gemeldet = []
    st = Speedtest(hass, list, lambda: 0.0, gemeldet.append)
    st.sensoren = OoklaSensoren("o", "sensor.letzter_test", None, None, None, None)
    t = dt_util.utcnow()
    hass.states.async_set("sensor.letzter_test", t.isoformat())
    st._lesen()  # noqa: SLF001
    st.nachholen()
    st._lesen()  # noqa: SLF001
    assert len(gemeldet) == 1
    st.erledigt(gemeldet[0].t)  # fertig, aber nicht eingetragen (letzte bleibt 0): nachholen
    st.nachholen()
    assert len(gemeldet) == 2


async def test_gescheitertes_setup_vermerkt_sauberes_ende(
    hass: HomeAssistant, eintrag, box, pi, eigener_ordner
):
    """Befund 6: scheitert das Setup nach dem Start des Herzschlags, meldet der nächste Start keinen Ausfall."""
    with patch("custom_components.heimnetz.async_anmelden", side_effect=RuntimeError("kaputt")):
        await hass.config_entries.async_setup(eintrag.entry_id)
        await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.SETUP_ERROR
    d = json.loads((eigener_ordner / "heimnetz" / "lauf.json").read_text(encoding="utf-8"))
    assert d["sauber"] is not None and d["sauber"] >= d["lebt"]


async def test_beschaedigte_datenbank_reparatur_hinweis(
    hass: HomeAssistant, eintrag, box, pi, eigener_ordner
):
    """Befund 7: eine beschädigte Datei → Fehler mit Übersetzung und Hinweis unter Reparaturen."""
    (eigener_ordner / "heimnetz").mkdir(exist_ok=True)
    (eigener_ordner / "heimnetz" / "heimnetz.db").write_bytes(b"kein SQLite" * 1000)
    await hass.config_entries.async_setup(eintrag.entry_id)
    await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.SETUP_ERROR
    hinweis = ir.async_get(hass).async_get_issue(DOMAIN, "datenbank_kaputt")
    assert hinweis is not None and hinweis.translation_key == "datenbank_kaputt"
    assert hinweis.translation_placeholders == {"datei": "heimnetz/heimnetz.db"}
    for sprache in ("de", "en"):
        tr = json.loads(
            (
                __import__("pathlib").Path(sp.__file__).parent / "translations" / f"{sprache}.json"
            ).read_text(encoding="utf-8")
        )
        assert "{datei}" in tr["issues"]["datenbank_kaputt"]["description"]
        assert tr["exceptions"]["datenbank_kaputt"]["message"]
        assert "{grund}" in tr["exceptions"]["schema_zu_neu"]["message"]


async def test_beschaedigte_datenbank_beim_ersten_lesen_reparatur_hinweis(
    hass: HomeAssistant, eintrag, box, pi, eigener_ordner
):
    """Öffnen gelingt, das erste Lesen (Gedächtnis, letzte Messung) scheitert an einer beschädigten Datei: derselbe
    Reparatur-Hinweis wie beim Öffnen, die Datenbank wird geschlossen."""
    geschlossen = []
    echt = sp.Datenbank.schliessen

    def schliessen(self):
        geschlossen.append(True)
        echt(self)

    with (
        patch(
            "custom_components.heimnetz._vorbereiten",
            side_effect=sqlite3.DatabaseError("database disk image is malformed"),
        ),
        patch.object(sp.Datenbank, "schliessen", schliessen),
    ):
        await hass.config_entries.async_setup(eintrag.entry_id)
        await hass.async_block_till_done()
    assert eintrag.state is ConfigEntryState.SETUP_ERROR
    hinweis = ir.async_get(hass).async_get_issue(DOMAIN, "datenbank_kaputt")
    assert hinweis is not None and hinweis.translation_placeholders == {
        "datei": "heimnetz/heimnetz.db"
    }
    assert geschlossen, "Datenbank nach dem Fehler geschlossen"


def test_sicherung_ohne_ende_schreibt_nach_hoechstdauer_weiter(tmp_path):
    """Befund 8: backup/start ohne backup/end hält das Schreiben nicht für immer an; die Warteschlange ist gedeckelt."""
    db = sp.Datenbank(tmp_path / "h.db")
    db.oeffnen()
    jetzt = [1000.0]
    with patch.object(sp.time, "monotonic", side_effect=lambda: jetzt[0]):
        db.anhalten()
        for i in range(sp.WARTESCHLANGE_HOECHSTENS + 5):
            db.meta_setzen("x", str(i))
        assert len(db._warteschlange) == sp.WARTESCHLANGE_HOECHSTENS  # noqa: SLF001
        assert db.meta("x") is None
        jetzt[0] += 3 * 3600  # große Recorder-Datenbank: nach 3 h noch angehalten
        db.meta_setzen("z", "1")
        assert db._angehalten and db.meta("z") is None  # noqa: SLF001
        jetzt[0] += sp.ANHALTEN_HOECHSTENS_S - 3 * 3600
        db.meta_setzen("y", "1")  # zu lange angehalten: selbst fortsetzen, Wartendes zuerst
    assert not db._angehalten and not db._warteschlange  # noqa: SLF001
    zeilen = dict(db._verbindung.execute("SELECT schluessel, wert FROM meta").fetchall())  # noqa: SLF001
    assert zeilen["x"] == str(sp.WARTESCHLANGE_HOECHSTENS + 4) and zeilen["y"] == "1"
    db.schliessen()


async def test_gedaechtnis_nicht_neu_wenn_sich_nur_die_merkliste_aendert(
    hass: HomeAssistant, eintrag, box, pi
):
    """Befund 4: eine neue Protokollzeile allein schreibt das Gedächtnis nicht jedes Mal neu (die Tabelle protokoll
    verhindert Dubletten); höchstens alle GESEHEN_SPEICHERN_S geht die Merkliste mit."""
    lz = await _laden(hass, eintrag)
    abruf = lz.abruf
    geschrieben = []
    with patch.object(
        lz.datenbank, "abruf_schreiben", side_effect=lambda *a: geschrieben.append(a[2])
    ):
        abruf.gedaechtnis.gesehen.append("0123456789abcdef")
        abruf._schreiben([], [], time.time(), False, False)  # noqa: SLF001
        assert geschrieben[-1] is None
        abruf._schreiben([], [], time.time(), False, True)  # noqa: SLF001
        assert geschrieben[-1] is not None and "0123456789abcdef" in geschrieben[-1]
        abruf._schreiben([], [], time.time(), False, True)  # noqa: SLF001
        assert geschrieben[-1] is None, "unverändert: nichts zu schreiben"
        abruf.gedaechtnis.quellen["x"] = "dhcp"  # anderes geändert: gleich schreiben
        abruf._schreiben([], [], time.time(), False, False)  # noqa: SLF001
        assert geschrieben[-1] is not None
