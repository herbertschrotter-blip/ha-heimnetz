// Seitentest: jeder Reiter rendert mit den Vorlagedaten, Bedienung schickt die richtigen Befehle.
import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { DATEN, QUELLE, machHass, seite, text, warten } from './umgebung.mjs';

await import(`${QUELLE}/heimnetz-panel.js`);
const { REITER } = await import(`${QUELLE}/heimnetz-panel.js`);

after(() => document.body.replaceChildren());

async function reiter(el, name) {
  const knopf = [...el.shadowRoot.querySelectorAll('nav button')].find((b) => b.textContent.trim() === name);
  assert.ok(knopf, `Reiter ${name}`);
  knopf.click();
  await warten(10);
  await el.updateComplete;
}

async function einstellungen(el) {
  const knopf = [...el.shadowRoot.querySelectorAll('.glas-kopf button')].find((b) => b.textContent.trim() === '⚙');
  assert.ok(knopf, '⚙ im Kopf');
  knopf.click();
  await warten(10);
  await el.updateComplete;
  assert.ok(el.shadowRoot.querySelector('.sheet.an'), 'Fenster offen');
}

const blatt = (el) => el.shadowRoot.querySelector('.sheet');

/** Reiter im Fenster Einstellungen wählen (AN-0002). */
async function einTab(el, name) {
  const b = [...el.shadowRoot.querySelectorAll('.sheet .e-reiter button')].find((x) => x.textContent.includes(name));
  assert.ok(b, `Reiter ${name}`);
  b.click();
  await el.updateComplete;
}
const knoepfe = (wurzel) => [...wurzel.querySelectorAll('button')];

test('Übersicht: Kopf, Kacheln, Befunde, Prüfungen', async () => {
  const hass = machHass();
  const el = await seite(hass);
  const t = text(el);
  assert.equal(hass.aufrufe[0].type, 'heimnetz/uebersicht');
  assert.match(t, /Störung|Hinweise|Alles in Ordnung/);
  assert.match(t, /Geräte online/);
  assert.match(t, /Pi → FRITZ!Box/);
  assert.match(t, /Wichtige Ereignisse/);
  assert.equal(el.shadowRoot.querySelectorAll('nav button').length, REITER.length);
  assert.ok(!/undefined|NaN/.test(t), t);
});

test('alle Reiter rendern ohne Fehler und ohne „undefined“', async () => {
  const hass = machHass();
  const el = await seite(hass);
  for (const [, name] of REITER) {
    await reiter(el, name);
    const t = text(el);
    assert.ok(!/undefined|NaN|\[object Object\]/.test(t), `${name}: ${t.slice(0, 400)}`);
    assert.ok(!t.includes('Daten nicht abrufbar'), name);
  }
  const typen = new Set(hass.aufrufe.map((a) => a.type));
  for (const b of ['uebersicht', 'speedtest', 'einstellungen', 'geraete', 'wlan', 'verbrauch', 'protokoll']) {
    assert.ok(typen.has(`heimnetz/${b}`), b);
  }
});

test('Speedtest: Raster 7 × 24, Auswahl schickt die Parameter', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  assert.equal(el.shadowRoot.querySelectorAll('.wr i').length, 7 * 24);
  // leere Zellen nicht mit der Klasse .leer (Hinweistext mit Innenabstand) – sonst sprengt das Raster am Handy die Karte
  assert.equal(el.shadowRoot.querySelectorAll('.wr i.leer').length, 0);
  assert.ok(el.shadowRoot.querySelectorAll('.wr i.ohne').length > 0);
  const vierWochen = [...el.shadowRoot.querySelectorAll('.seg button')].find((b) => b.textContent === '4 Wochen');
  vierWochen.click();
  await warten(10);
  const letzter = hass.aufrufe.filter((a) => a.type === 'heimnetz/speedtest').at(-1);
  assert.equal(letzter.tage, 28);
  assert.equal(letzter.grundlast, 'aus');
});

test('Speedtest: Tagesverlauf für Wochentag und Datum (WU-0004)', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  const w = el.shadowRoot;
  const gezaehlt = DATEN.speedtest.raster.flat().filter((z) => z.anzahl).length;
  assert.equal(w.querySelectorAll('.wr i b').length, gezaehlt, 'Median-Zahl in jeder Kachel mit Messung');
  assert.equal(w.querySelector('.tv svg'), null, 'zu, bis ein Tag gewählt ist');
  assert.match(w.querySelector('.tv').textContent, /Tipp auf einen Wochentag/);
  w.querySelectorAll('.wr button.tag')[0].click();
  await warten(10);
  await el.updateComplete;
  let letzter = hass.aufrufe.filter((x) => x.type === 'heimnetz/speedtest').at(-1);
  assert.equal(letzter.tag, 0);
  assert.equal(letzter.datum, undefined);
  assert.ok(w.querySelector('.wr button.tag.on'));
  assert.ok(w.querySelector('.tv svg'));
  assert.equal(w.querySelectorAll('.tv rect.h').length, 24);
  assert.equal(w.querySelectorAll('.tv polyline.glatt').length, 1, 'geglätteter Mittelwert als eigene Linie');
  assert.equal(w.querySelectorAll('.tv circle.pkt').length, DATEN.speedtest.verlauf.stunden.filter((s) => s.anzahl).length);
  assert.match(w.querySelector('.tv .gruppe').textContent, /alle Montage/);
  assert.match(w.querySelector('.tv .info').textContent, /Beste Stunde 23–24 Uhr .*schwächste 2–3 Uhr/);
  // Tipp auf eine Stunde zeigt die Werte, ohne neu abzufragen
  const vorher = hass.aufrufe.length;
  w.querySelectorAll('.tv rect.h')[2].dispatchEvent(new Event('click'));
  await el.updateComplete;
  assert.equal(hass.aufrufe.length, vorher);
  assert.match(w.querySelector('.tv .info').textContent, /2–3 Uhr: Median 112 Mbit\/s · niedrigste 98 · höchste 123 · 2 Messungen/);
  w.querySelectorAll('.tv rect.h')[20].dispatchEvent(new Event('click'));
  await el.updateComplete;
  assert.match(w.querySelector('.tv .info').textContent, /20–21 Uhr: Median 118 Mbit\/s · 1 Messung · geglättet 118/);
  // Datum: eigener Parameter, der Wochentag fällt weg
  const sel = w.querySelector('.tv select');
  sel.value = DATEN.speedtest.tage_liste[1].datum;
  sel.dispatchEvent(new Event('change'));
  await warten(10);
  letzter = hass.aufrufe.filter((x) => x.type === 'heimnetz/speedtest').at(-1);
  assert.equal(letzter.datum, DATEN.speedtest.tage_liste[1].datum);
  assert.equal(letzter.tag, undefined);
  // ✕ schließt
  [...w.querySelectorAll('.tv button')].find((x) => x.textContent === '✕').click();
  await warten(10);
  await el.updateComplete;
  assert.equal(w.querySelector('.tv svg'), null);
  assert.ok(!/undefined|NaN/.test(text(el)));
});

test('Speedtest: Popup zur Stundenkachel – überfahren zeigt, Klick hält fest (AN-0005)', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  const w = el.shadowRoot;
  const k = w.querySelector('.wr i.kachel');
  const [tag, stunde] = k.dataset.k.split('-').map(Number);
  el.setze('speedtest', { datum: DATEN.speedtest.tage_liste[0].datum }); // ein Datum im Tagesverlauf stört nicht
  await warten(10);
  await el.updateComplete;
  k.dispatchEvent(new Event('mouseenter'));
  await warten(200); // Überfahren wartet kurz
  await el.updateComplete;
  const frage = hass.aufrufe.filter((x) => x.type === 'heimnetz/speedtest/kachel').at(-1);
  assert.deepEqual([frage.tag, frage.stunde, frage.tage, frage.grundlast], [tag, stunde, 84, 'aus']);
  assert.equal(frage.datum, undefined, 'nur die Auswahl des Rasters');
  let pop = w.querySelector('.kpop');
  assert.ok(pop && !pop.classList.contains('fest'));
  assert.match(pop.textContent, /Median 118,0 Mbit\/s · niedrigste 104,0 · höchste 120,0 · 3 gezählt · 1 belastet \(zählt nicht\)/);
  assert.equal(pop.querySelectorAll('tr').length - 1, DATEN['speedtest/kachel'].messungen.length);
  assert.match(pop.textContent, /zählt nicht/);
  k.dispatchEvent(new Event('mouseleave'));
  await el.updateComplete;
  assert.equal(w.querySelector('.kpop'), null, 'Verlassen schließt');
  // Klick (am Handy: Tipp) hält fest; Verlassen schließt dann nicht
  k.click();
  await warten(10);
  await el.updateComplete;
  pop = w.querySelector('.kpop');
  assert.ok(pop.classList.contains('fest') && w.querySelector('.wr i.wahl'));
  k.dispatchEvent(new Event('mouseleave'));
  await el.updateComplete;
  assert.ok(w.querySelector('.kpop'), 'fest bleibt');
  // Überfahren einer anderen Kachel ändert das festgehaltene Popup nicht
  const andere = [...w.querySelectorAll('.wr i.kachel')].find((x) => x !== k);
  const vorher = hass.aufrufe.length;
  andere.dispatchEvent(new Event('mouseenter'));
  await warten(200);
  assert.equal(hass.aufrufe.length, vorher);
  // zweiter Tipp auf dieselbe Kachel schließt
  k.click();
  await el.updateComplete;
  assert.equal(w.querySelector('.kpop'), null);
  // gemerkt: erneutes Öffnen fragt nicht noch einmal
  k.click();
  await warten(10);
  await el.updateComplete;
  assert.equal(hass.aufrufe.length, vorher);
  assert.ok(w.querySelector('.kpop.fest'));
  // Klick daneben schließt
  w.querySelector('.block-kopf').click();
  await el.updateComplete;
  assert.equal(w.querySelector('.kpop'), null);
  // ✕ schließt ebenso
  k.click();
  await warten(10);
  await el.updateComplete;
  w.querySelector('.kpop .zu-k').click();
  await el.updateComplete;
  assert.equal(w.querySelector('.kpop'), null);
  assert.ok(!/undefined|NaN/.test(text(el)));
});

test('Speedtest: Zusatzdaten je Messung – Spalten und alle Werte per Tipp (WU-0005)', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  const w = el.shadowRoot;
  const zeilen = [...w.querySelectorAll('tr.klick')];
  assert.equal(zeilen.length, DATEN.speedtest.messungen.length);
  const voll = zeilen[1].textContent.replace(/\s+/g, ' ');
  assert.match(voll, /5G-NSA/);
  assert.match(voll, /…-64/);
  assert.match(voll, /-93 dBm/);
  assert.match(voll, /6860 5G · 8\.03/);
  assert.match(zeilen[0].textContent, /–/, 'ohne Momentaufnahme: Striche');
  zeilen[1].click();
  await el.updateComplete;
  const s = w.querySelector('.sheet.an');
  assert.ok(s, 'Fenster offen');
  const t = s.textContent.replace(/\s+/g, ' ');
  for (const muster of [/Momentaufnahme im Moment der Messung/, /Note B/, /Messplan/, /Anlage aaaaa/, /PCI 982/, /2,1 km Nordost/,
    /FRITZ!Box 6860 5G · 268\.08\.03/, /9 h 12 min/, /6 Tage 4 h/, /31 · 22/, /teils bewölkt · 12,0 °C · 78 % Feuchte · 60 % Wolken/, /Werktag/]) {
    assert.match(t, muster);
  }
  assert.ok(s.querySelector('a[href^="https://"][rel~="noopener"]'), 'Link zu Ookla');
  assert.ok(!/undefined|NaN|null/.test(t), t);
  s.querySelector('.zu').click();
  await el.updateComplete;
  zeilen.at(-1).click();
  await el.updateComplete;
  assert.match(w.querySelector('.sheet.an').textContent, /nachgetragen aus Verlauf und Journal/);
});

test('Einstellungen: Admin speichert, andere sehen nur', async () => {
  const hass = machHass({ admin: true });
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  assert.equal(el.shadowRoot.querySelector('.seite [name=tarif_down]'), null, 'Reiter ohne Einstellungen');
  await einstellungen(el);
  const feld = blatt(el).querySelector('[name=tarif_down]');
  feld.value = '200';
  knoepfe(blatt(el)).find((b) => b.textContent === 'Speichern').click();
  await warten(10);
  const setzen = hass.aufrufe.find((a) => a.type === 'heimnetz/einstellungen/setzen');
  assert.equal(setzen.tarif_down, '200');
  const gast = await seite(machHass({ admin: false }));
  await einstellungen(gast);
  assert.ok(gast.shadowRoot.querySelector('[name=tarif_down]').disabled);
  assert.ok(![...gast.shadowRoot.querySelectorAll('button')].some((b) => b.textContent === 'Speichern'));
});

test('Geräte: Filter nur in der Anzeige, Tippen öffnet die Einblendung', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Geräte');
  const zeilen = el.shadowRoot.querySelectorAll('.geraet');
  assert.equal(zeilen.length, DATEN.geraete.geraete.length);
  const vorher = hass.aufrufe.length;
  [...el.shadowRoot.querySelectorAll('.seg button')].find((b) => b.textContent === 'Offline').click();
  await el.updateComplete;
  assert.equal(hass.aufrufe.length, vorher); // keine neue Abfrage
  [...el.shadowRoot.querySelectorAll('.seg button')].find((b) => b.textContent === 'Alle').click();
  await el.updateComplete;
  el.shadowRoot.querySelector('.geraet').click();
  await warten(10);
  await el.updateComplete;
  const auf = hass.aufrufe.find((a) => a.type === 'heimnetz/geraet');
  const erste = DATEN.geraete.geraete.find((g) => g.verbindung === DATEN.geraete.gruppen[0].name);
  assert.equal(auf.geraet, erste.id, 'erstes Gerät der ersten Gruppe');
  assert.ok(el.shadowRoot.querySelector('.sheet.an'));
  assert.match(text(el), /Letzte 7 Tage/);
});

test('Protokoll: Suche und Art gehen an die Integration', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Protokoll');
  const suche = el.shadowRoot.querySelector('.suche');
  suche.value = 'getrennt';
  suche.dispatchEvent(new Event('change'));
  await warten(10);
  assert.equal(hass.aufrufe.filter((a) => a.type === 'heimnetz/protokoll').at(-1).suche, 'getrennt');
  [...el.shadowRoot.querySelectorAll('.seg button')].find((b) => b.textContent === 'WLAN').click();
  await warten(10);
  assert.equal(hass.aufrufe.filter((a) => a.type === 'heimnetz/protokoll').at(-1).art, 'wlan');
});

test('Fehler der Integration wird gezeigt statt einer leeren Seite', async () => {
  const hass = machHass();
  hass.callWS = async () => { throw new Error('Die Integration Heimnetz ist nicht geladen.'); };
  const el = await seite(hass);
  assert.match(text(el), /Daten nicht abrufbar: Die Integration Heimnetz ist nicht geladen/);
});

test('hell und dunkel, Hintergrund nach Tageszeit', async () => {
  const hass = machHass({ dunkel: false });
  hass.states['sun.sun'] = { attributes: { elevation: -12, rising: false } };
  const el = await seite(hass);
  assert.ok(el.shadowRoot.querySelector('.wurzel.hell'));
  assert.equal(el.shadowRoot.querySelector('.glas-bg').dataset.phase, 'nacht');
});

test('ältere, langsamere Antwort überschreibt die neuere nicht', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  const langsam = { ...DATEN.speedtest, tage: 7, median: 1 };
  let freigeben;
  hass.callWS = async (msg) => {
    if (msg.type === 'heimnetz/speedtest' && msg.tage === 7) {
      await new Promise((r) => { freigeben = r; });
      return langsam;
    }
    return msg.type === 'heimnetz/speedtest' ? { ...DATEN.speedtest, tage: 84, median: 99 } : DATEN[msg.type.replace('heimnetz/', '')];
  };
  el.setze('speedtest', { tage: 7 });
  await warten(5);
  el.setze('speedtest', { tage: 84 });
  await warten(10);
  freigeben();
  await warten(10);
  assert.equal(el._daten.speedtest.median, 99);
  assert.equal(el._laedt, false);
});

test('geschlossene Einblendung bleibt zu, wenn die Antwort später kommt', async () => {
  const hass = machHass();
  const el = await seite(hass);
  let freigeben;
  hass.callWS = async (msg) => {
    if (msg.type === 'heimnetz/geraet') await new Promise((r) => { freigeben = r; });
    return DATEN[msg.type.replace('heimnetz/', '')];
  };
  el.geraetOeffnen('x');
  await warten(5);
  el.zu();
  freigeben();
  await warten(10);
  assert.equal(el._blatt, null);
});

test('beim Öffnen wird nur einmal geladen', async () => {
  const hass = machHass();
  await seite(hass);
  assert.equal(hass.aufrufe.filter((a) => a.type === 'heimnetz/uebersicht').length, 1);
});

test('gewählter Server bleibt sichtbar, auch ohne Messungen im Zeitraum', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  el.setze('speedtest', { server: 'Graz – X' });
  await warten(10);
  await el.updateComplete;
  const gewaehlt = el.shadowRoot.querySelector('select option[selected]');
  assert.match(gewaehlt.textContent, /Graz – X \(keine Messungen im Zeitraum\)/);
});

test('Messplan: Admin ändert den Takt und misst jetzt', async () => {
  const hass = machHass({ admin: true });
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  assert.match(text(el), /Messplan/);
  await einstellungen(el);
  await einTab(el, 'Messplan');
  [...blatt(el).querySelectorAll('.seg button')].find((b) => b.textContent === '12 h').click();
  await warten(10);
  const setzen = hass.aufrufe.find((a) => a.type === 'heimnetz/messplan/setzen');
  assert.equal(setzen.takt_h, 12);
  [...el.shadowRoot.querySelectorAll('button')].find((b) => b.textContent.includes('Jetzt messen')).click();
  await warten(10);
  await el.updateComplete;
  assert.ok(hass.aufrufe.some((a) => a.type === 'heimnetz/messen'));
  assert.match(text(el), /⏳ misst …/);
});

test('Messplan: ohne Admin nur Anzeige', async () => {
  const el = await seite(machHass({ admin: false }));
  await reiter(el, 'Speedtest');
  assert.ok(![...el.shadowRoot.querySelectorAll('button')].some((b) => b.textContent.includes('Jetzt messen')));
  assert.match(text(el), /alle 4 h/);
});

test('Messplan: Warnung, wenn Ookla selbst misst; Verschieben wird angezeigt', async () => {
  const hass = machHass();
  const e = DATEN.einstellungen;
  const daten = { ...e, ookla: { ...e.ookla, misst_selbst: true }, verkehr_mbit: 38.4,
    plan: { ...e.plan, wartet: true, neuer_versuch: Date.now() / 1000 + 300 } };
  const alt = hass.callWS;
  hass.callWS = async (msg) => (msg.type === 'heimnetz/einstellungen' ? daten : alt(msg));
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  const t = text(el);
  assert.match(t, /Ookla misst zusätzlich nach eigenem Takt/);
  assert.match(t, /verschoben wegen Verkehr – neuer Versuch \d\d:\d\d/);
  await einstellungen(el);
  await einTab(el, 'Messplan');
  assert.match(blatt(el).textContent.replace(/\s+/g, ' '), /38,4 Mbit\/s – belastet/);
});

test('WU-0006: ohne Ookla zeigt der Speedtest-Reiter den Hinweis mit Link, alles andere läuft', async () => {
  const hass = machHass();
  const e = DATEN.einstellungen;
  const leer = { ...DATEN.speedtest, gesamt: 0, letzte: null, messungen: [], raster: DATEN.speedtest.raster.map((r) => r.map((z) => ({ ...z, anzahl: 0 }))) };
  const daten = { ...e, ookla: { ...e.ookla, vorhanden: false, sensoren: false, tests: 0, eintrag: null, takt_min: null },
    volumen: { tests_tag: 4, je_test_mb: null, tag_mb: null, monat_gb: null } };
  const alt = hass.callWS;
  hass.callWS = async (msg) => (msg.type === 'heimnetz/einstellungen' ? daten : msg.type === 'heimnetz/speedtest' ? leer : alt(msg));
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  const t = text(el);
  assert.match(t, /Ookla Speedtest ist nicht eingerichtet/);
  assert.match(t, /Heimnetz läuft auch ohne/);
  const link = el.shadowRoot.querySelector('.ohne-ookla a');
  assert.equal(link.getAttribute('href'), 'https://github.com/soulripper13/hass-speedtest-ookla');
  assert.equal(link.getAttribute('target'), '_blank');
  assert.ok(knoepfe(el.shadowRoot).filter((b) => /Jetzt messen|× messen/.test(b.textContent)).every((b) => b.disabled));
  assert.ok(!/undefined|NaN/.test(t), t);
  await einstellungen(el);
  await einTab(el, 'Messplan');
  assert.match(blatt(el).textContent.replace(/\s+/g, ' '), /bei schnellen Anschlüssen einige hundert MB/);
});

test('WU-0006: Datenvolumen je Messung im Messplan', async () => {
  const el = await seite(machHass());
  await einstellungen(el);
  await einTab(el, 'Messplan');
  const t = blatt(el).textContent.replace(/\s+/g, ' ');
  assert.match(t, /Jede Messung kostet etwa 270 MB Datenvolumen; mit diesem Plan 6 Messungen am Tag, rund 1\.620 MB am Tag und 48,6 GB im Monat/);
});

test('Messplan: abgelehnter Wert springt auf den gespeicherten zurück', async () => {
  const hass = machHass();
  const alt = hass.callWS;
  hass.callWS = async (msg) => {
    if (msg.type === 'heimnetz/messplan/setzen') throw new Error('Nur zwischen: von und bis sind gleich');
    return alt(msg);
  };
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Messplan');
  const von = el.shadowRoot.querySelectorAll('input[type=time]')[0];
  von.value = '06:00';
  von.dispatchEvent(new Event('change'));
  await warten(10);
  await el.updateComplete;
  assert.match(text(el), /von und bis sind gleich/);
  assert.equal(el.shadowRoot.querySelectorAll('input[type=time]')[0].value, DATEN.einstellungen.messplan.von);
});

test('Funk: WLAN mit Befund, Bändern und Geräten; Umschalten lädt Mobilfunk', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Funk');
  let t = text(el);
  assert.match(t, /Geräte im WLAN/);
  assert.match(t, /mit schwachem Empfang/);
  assert.match(t, /Kanal 44/);
  assert.equal(el.shadowRoot.querySelectorAll('.t tr.klick').length, DATEN.wlan.geraete.length);
  el.shadowRoot.querySelector('.t tr.klick').click();
  await warten(10);
  assert.ok(hass.aufrufe.some((a) => a.type === 'heimnetz/geraet' && a.geraet === DATEN.wlan.geraete[0].id));
  el.zu();
  knoepfe(el.shadowRoot.querySelector('.seite')).find((b) => b.textContent === 'Mobilfunk').click();
  await warten(10);
  await el.updateComplete;
  t = text(el);
  assert.ok(hass.aufrufe.some((a) => a.type === 'heimnetz/mobilfunk'));
  assert.match(t, /Verbindung zur Basisstation/);
  assert.match(t, new RegExp(`↔ ${DATEN.mobilfunk.strecke.entfernung}`));
  assert.equal(el.shadowRoot.querySelectorAll('.zelle').length, DATEN.mobilfunk.zellen.length);
  assert.equal(el.shadowRoot.querySelectorAll('.strecke circle').length, DATEN.mobilfunk.strecke.masten.length);
  assert.ok(!/Antenne 1/.test(t));
  const k = DATEN.mobilfunk.karte;
  assert.match(t, /Wo steht der Mast\?/);
  const kk = el.shadowRoot.querySelector('heimnetz-karte');
  assert.ok(kk && kk.shadowRoot.querySelector('.leaflet-container'), 'Leaflet-Karte angelegt');
  assert.deepEqual([...kk.shadowRoot.querySelectorAll('.k-lage option')].map((o) => o.value), ['auto', 'bmap', 'grau', 'osm']);
  assert.equal(kk.shadowRoot.querySelectorAll('.k-zoom button').length, 4);  // ＋ − ⌖ ⛶
  assert.ok(!kk.shadowRoot.innerHTML.includes('cartocdn'));  // CARTO verlangt einen Schlüssel – nicht mehr benutzt
  assert.match(t, /opencellid\.org/);  // ohne Schlüssel: Hinweis, wie es zum Mast kommt
  assert.match(t, new RegExp(`${k.ring} laut Box`));
  const befund = el.shadowRoot.querySelector('details.befund-k');
  assert.ok(befund && !befund.open, 'Befund zugeklappt');
  assert.equal(befund.querySelector('summary b').textContent, DATEN.mobilfunk.befund.titel);
  assert.match(t, /Verbunden seit/);
  assert.ok(!/undefined|NaN/.test(t), t.slice(0, 400));
});

test('Funk · Mobilfunk: Zellen mit Fundstelle, Mast je Sendeanlage auf der Karte (WU-0002)', async () => {
  const alt = DATEN.mobilfunk;
  const anker = alt.zellen.find((z) => z.anker);
  DATEN.mobilfunk = {
    ...alt,
    zellen: alt.zellen.map((z) => (z.anker ? { ...z, fund: { quelle: 'BeaconDB', genau: '50 m' }, such: null } : z)),
    karte: { ...alt.karte, stand: 'gefunden', gefunden: 1,
      masten: [{ name: 'abcde', ort: [48.21, 16.38], entfernung: '1,4 km', richtung: 'Nordost', genau: '50 m', fuenf_g: true }],
      punkte: [{ ort: [48.21, 16.38], genau_m: 50, anker: true, name: '0b' }],
      osm: [{ ort: [48.19, 16.37], betreiber: null, passt: true, entfernung: '1,3 km', richtung: 'Süd', anbieter: ['Drei'], technik: ['LTE', '5G'], zellen: 4 },
        { ort: [48.25, 16.40], betreiber: 'A1', passt: false, entfernung: '5,6 km', richtung: 'Nord', anbieter: null, technik: null, zellen: 0 }] },
  };
  try {
    const hass = machHass();
    const el = await seite(hass);
    await reiter(el, 'Funk');
    knoepfe(el.shadowRoot.querySelector('.seite')).find((b) => b.textContent === 'Mobilfunk').click();
    await warten(10);
    await el.updateComplete;
    const t = text(el);
    assert.match(t, new RegExp(`TAC ${anker.tac} · PLMN ${anker.plmn} · 📍 BeaconDB · ±50 m`));
    assert.match(t, /nur PCI – nicht nachschlagbar/);
    assert.match(t, /geschätzt · 1 von 2 Zellen gefunden/);
    assert.match(t, /Mast abcde \(geschätzt\) · 4G \+ 5G \(vermutlich\) · 1,4 km Nordost \(± 50 m\)/);
    const kk = el.shadowRoot.querySelector('heimnetz-karte');
    assert.equal(kk.shadowRoot.querySelectorAll('.k-name').length, 0);  // ohne Größe zeichnet Leaflet noch nicht
    const ziel = kk.shadowRoot.querySelector('#karte');  // die Testumgebung kennt keine Größen: so tun als ob
    Object.defineProperty(ziel, 'clientWidth', { value: 600 });
    Object.defineProperty(ziel, 'clientHeight', { value: 320 });
    kk._erstesMal();
    assert.ok(kk._gezeigt, 'Rahmen der Integration gezeigt');
    assert.deepEqual([...kk.shadowRoot.querySelectorAll('.k-name')].map((n) => n.textContent), ['Funkmast (OSM) · 1,3 km Süd · passt', '0b', 'Mast abcde · 4G + 5G? · 1,4 km', 'Wohnung']);
    // Antippen eines Masts: Infofeld mit Anbieter und Technik laut OpenCellID; anderer Mast: „unbekannt“
    const symbol = (n) => kk.shadowRoot.querySelectorAll('.leaflet-marker-icon')[[...kk.shadowRoot.querySelectorAll('.leaflet-marker-icon')].findIndex((m) => m.querySelector('.osm-dreieck')) + n];
    symbol(0).dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    await kk.updateComplete;
    let feld = kk.shadowRoot.querySelector('.k-info');
    assert.ok(feld, 'Infofeld offen');
    assert.match(feld.textContent, /passt zur Entfernung laut Box/);
    assert.match(feld.textContent, /📶 Drei · LTE · 5G/);
    assert.match(feld.textContent, /laut OpenCellID: 4 Zellen in höchstens 500 m/);
    symbol(1).dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    await kk.updateComplete;
    feld = kk.shadowRoot.querySelector('.k-info');
    assert.match(feld.textContent, /A1/);
    assert.match(feld.textContent, /5,6 km Nord/);
    assert.match(feld.textContent, /Anbieter und Technik unbekannt/);
    feld.querySelector('.k-info-zu').click();
    await kk.updateComplete;
    assert.ok(!kk.shadowRoot.querySelector('.k-info'));
    // ⛶ Vollbild (die Testumgebung kennt keine Fullscreen-API: fest über dem Fenster), ✕ schließt
    [...kk.shadowRoot.querySelectorAll('.k-zoom button')].find((b) => b.textContent === '⛶').click();
    await warten(5);
    await kk.updateComplete;
    assert.ok(kk.shadowRoot.querySelector('.rahmen.voll'));
    kk.shadowRoot.querySelector('.k-voll-zu').click();
    await warten(5);
    await kk.updateComplete;
    assert.ok(!kk.shadowRoot.querySelector('.rahmen.voll'));
    // Ebene „Masten (OSM)“: zwei Dreiecke, das passende hervorgehoben; Knopf schaltet aus und merkt es sich
    assert.equal(kk.shadowRoot.querySelectorAll('.osm-dreieck').length, 2);
    assert.equal(kk.shadowRoot.querySelectorAll('.osm-dreieck.passt').length, 1);
    assert.match(t, /Funkmast laut OpenStreetMap \(orange umrandet: passt am besten\)/);
    const osm = kk.shadowRoot.querySelector('.k-osm');
    assert.ok(osm.classList.contains('an'));
    osm.click();
    await kk.updateComplete;
    assert.equal(kk.shadowRoot.querySelectorAll('.osm-dreieck').length, 0);
    assert.equal(localStorage.getItem('heimnetz.karte.osm'), 'aus');
    await el.updateComplete;
    assert.ok(!/Funkmast laut OpenStreetMap/.test(text(el)), 'Legende folgt dem Knopf');
    localStorage.removeItem('heimnetz.karte.osm');
    assert.ok(!/opencellid\.org|undefined|NaN/.test(t));  // gefunden: kein Hinweis auf den Schlüssel
  } finally {
    DATEN.mobilfunk = alt;
  }
});

test('Karte: Grundlage automatisch nach Design, Wahl bleibt im Browser', async () => {
  const { grundlage, GRUNDLAGEN } = await import(`${QUELLE}/karte.js`);
  assert.deepEqual(grundlage('auto', true), { ...GRUNDLAGEN.grau, abdunkeln: true });
  assert.deepEqual(grundlage('auto', false), { ...GRUNDLAGEN.bmap, abdunkeln: false });
  assert.match(grundlage('osm', true).url, /^https:\/\/tile\.openstreetmap\.org\//);
  assert.match(grundlage('grau', false).url, /mapsneu\.wien\.gv\.at\/basemap\/bmapgrau\//);
  assert.equal(grundlage('kaputt', false).url, GRUNDLAGEN.bmap.url);
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Funk');
  knoepfe(el.shadowRoot.querySelector('.seite')).find((b) => b.textContent === 'Mobilfunk').click();
  await warten(10);
  await el.updateComplete;
  const kk = el.shadowRoot.querySelector('heimnetz-karte');
  const wahl = kk.shadowRoot.querySelector('.k-lage');
  wahl.value = 'osm';
  wahl.dispatchEvent(new Event('change'));
  await kk.updateComplete;
  assert.equal(localStorage.getItem('heimnetz.karte.grundlage'), 'osm');
  assert.match(kk._kacheln._url, /^https:\/\/tile\.openstreetmap\.org\//);  // Kachel-Ebene gewechselt (ohne Größe lädt Leaflet keine Bilder)
  localStorage.removeItem('heimnetz.karte.grundlage');
});

test('Übersicht: Kachel Empfang springt zu Funk · Mobilfunk', async () => {
  const hass = machHass();
  const el = await seite(hass);
  [...el.shadowRoot.querySelectorAll('.glas-k')].find((k) => k.textContent.includes('Empfang')).click();
  await warten(10);
  await el.updateComplete;
  assert.equal(el._reiter, 'funk');
  assert.equal(el._opt.funk.teil, 'mobilfunk');
  assert.ok(hass.aufrufe.some((a) => a.type === 'heimnetz/mobilfunk'));
});

test('Einstellungen: Grenze für schwachen WLAN-Empfang', async () => {
  const hass = machHass({ admin: true });
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'WLAN');
  [...blatt(el).querySelectorAll('.seg button')].find((b) => b.textContent === '50 %').click();
  await warten(10);
  const setzen = hass.aufrufe.find((a) => a.type === 'heimnetz/einstellungen/setzen');
  assert.equal(setzen.wlan_schwach, 50);
});

test('Melden: Knopf öffnet den Dialog, Senden schickt Meldung und Bilder einzeln, Rückmeldung nennt die Bilder', async () => {
  const hass = machHass({ admin: false });
  const el = await seite(hass);
  const knopf = el.shadowRoot.querySelector('.melden-knopf');
  assert.ok(knopf, 'Melden-Knopf');
  knopf.click();
  await el.updateComplete;
  assert.match(text(el), /Melden.*Was ist passiert/);
  assert.match(text(el), /Reiter Übersicht/);
  // leer senden geht nicht
  el.shadowRoot.querySelector('.ml-senden').click();
  await el.updateComplete;
  assert.match(text(el), /Bitte kurz beschreiben/);
  assert.ok(!hass.aufrufe.some((a) => a.type === 'heimnetz/meldung/neu'));
  const f = el._blatt.form;
  f.text = 'Karte grau';
  f.bilder.push({ url: 'data:image/jpeg;base64,AAAA', b: 720, h: 1600, kb: 1 }, { url: 'data:image/jpeg;base64,kaputt', b: 1, h: 1, kb: 1 });
  el.requestUpdate();
  await el.updateComplete;
  assert.equal(el.shadowRoot.querySelectorAll('.mb-bild img').length, 2, 'Vorschau im Dialog');
  el.shadowRoot.querySelector('.ml-senden').click();
  await warten(10);
  await el.updateComplete;
  const typen = hass.aufrufe.map((a) => a.type);
  assert.deepEqual(typen.filter((t) => t.startsWith('heimnetz/meldung/')), ['heimnetz/meldung/neu', 'heimnetz/meldung/bild', 'heimnetz/meldung/bild']);
  const neu = hass.aufrufe.find((a) => a.type === 'heimnetz/meldung/neu').meldung;
  assert.equal(neu.art, 'fehler');
  assert.deepEqual(neu.seite, { reiter: 'uebersicht', funk: 'wlan', dialog: null });
  assert.ok(!('bilder' in neu), 'Bilder nicht in der Meldung selbst');
  assert.equal(el._blatt, null, 'Dialog zu');
  assert.match(el.shadowRoot.querySelector('.toast').textContent, /gemeldet als FE-0003 mit 1 Bild · 1 Bild kam nicht an \(bild: nur JPEG/);
});

test('WU-0006: öffentlich auf GitHub melden – Vorschau, Schalter mit Warnung, Bilder-Hinweis, speichern und öffnen', async () => {
  const hass = machHass({ admin: false });
  const el = await seite(hass);
  el.meldenAuf();
  await el.updateComplete;
  const gh = () => el.shadowRoot.querySelector('.ml-github');
  assert.match(gh().textContent, /Senden \+ öffentlich auf GitHub ↗/);
  assert.match(text(el), /mit deinem eigenen GitHub-Konto/);
  // ohne Text geht es nicht weiter
  gh().click();
  await el.updateComplete;
  assert.equal(el._blatt.art, 'melden');
  assert.match(text(el), /Bitte kurz beschreiben/);
  assert.ok(!hass.aufrufe.some((a) => a.type === 'heimnetz/meldung/github'));

  const f = el._blatt.form;
  f.text = 'Karte grau';
  f.bilder.push({ url: 'data:image/jpeg;base64,AAAA', b: 720, h: 1600, kb: 1 });
  gh().click();
  await warten(10);
  await el.updateComplete;
  assert.equal(el._blatt.art, 'github');
  let t = blatt(el).textContent.replace(/\s+/g, ' ');
  assert.match(t, /Öffentlich auf GitHub melden/);
  assert.match(el.shadowRoot.querySelector('.gh-vorschau').textContent, /\[Fehler\] Karte grau\s+Karte grau\s+### Umgebung/);
  assert.match(t, /Nie dabei: Gerätenamen, Hardware-Adressen, IP-Adressen, Standort von Home Assistant, Kennwörter\./);
  assert.match(t, /Dein Bild kann GitHub nicht über den Link übernehmen/);
  assert.ok(!el.shadowRoot.querySelector('.gh-warn'), 'Warnung erst mit Schalter');
  assert.ok(!el.shadowRoot.querySelector('.melden-knopf.im-sheet'), 'kein zweiter Melden-Knopf');
  const vorschau = hass.aufrufe.filter((a) => a.type === 'heimnetz/meldung/github');
  assert.deepEqual(vorschau, [{ type: 'heimnetz/meldung/github', meldung: { art: 'fehler', text: 'Karte grau', kontext: 'Übersicht', version: f.version, geraet: 'Desktop' }, zelle: false, sprache: 'de' }]);

  // Schalter: neue Vorschau mit Zelldaten und gelbe Warnung
  blatt(el).querySelector('.sw').click();
  await warten(10);
  await el.updateComplete;
  assert.equal(hass.aufrufe.filter((a) => a.type === 'heimnetz/meldung/github').at(-1).zelle, true);
  assert.match(el.shadowRoot.querySelector('.gh-vorschau').textContent, /Zell- und Signaldaten/);
  assert.match(el.shadowRoot.querySelector('.gh-warn').textContent, /lässt sich ungefähr bestimmen, wo du wohnst/);

  // Zurück: Melde-Dialog mit dem Entwurf; wieder vor
  knoepfe(blatt(el)).find((b) => b.textContent.trim() === 'Zurück').click();
  await el.updateComplete;
  assert.equal(el._blatt.art, 'melden');
  assert.equal(el._blatt.form.text, 'Karte grau');
  gh().click();
  await warten(10);
  await el.updateComplete;

  // Speichern und weiter: Fenster mit dem gezeigten Link noch im Klick öffnen (vor jeder Antwort), lokal melden, Bilder
  const geoeffnet = [];
  const echt = window.open;
  window.open = (...a) => { geoeffnet.push([...a, hass.aufrufe.filter((x) => x.type === 'heimnetz/meldung/neu').length]); return null; };
  try {
    el.shadowRoot.querySelector('.gh-senden').click();
    assert.equal(geoeffnet.length, 1, 'gleich im Klick geöffnet');
    await warten(10);
    await el.updateComplete;
  } finally {
    window.open = echt;
  }
  const neu = hass.aufrufe.find((a) => a.type === 'heimnetz/meldung/neu');
  assert.ok(!('github' in neu));
  assert.equal(neu.meldung.text, 'Karte grau');
  assert.deepEqual(neu.meldung.seite, { reiter: 'uebersicht', funk: 'wlan', dialog: null });
  assert.equal(geoeffnet.length, 1);
  assert.match(geoeffnet[0][0], /^https:\/\/github\.com\/x\/ha-heimnetz\/issues\/new\?title=.*Lokales%20Ticket%3A%20FE-0003/);
  assert.deepEqual(geoeffnet[0].slice(1), ['_blank', 'noopener', 0], 'vor dem Speichern, ohne Zugriff auf die Seite');
  assert.match(decodeURIComponent(geoeffnet[0][0]), /Zell- und Signaldaten/, 'genau die gezeigte Vorschau');
  assert.deepEqual(hass.aufrufe.filter((a) => a.type.startsWith('heimnetz/meldung/')).map((a) => a.type).slice(-2), ['heimnetz/meldung/neu', 'heimnetz/meldung/bild']);
  assert.equal(el._blatt, null, 'Dialog zu');
  assert.match(el.shadowRoot.querySelector('.toast').textContent, /Gemeldet als FE-0003 – GitHub öffnet sich in einem neuen Fenster mit 1 Bild/);
  assert.equal(sessionStorage.getItem('heimnetz-melden-entwurf'), null, 'Entwurf weg');
});

test('WU-0006: Fehler bei Vorschau und beim Speichern bleiben im Dialog; andere Nummer wird gemeldet', async () => {
  const hass = machHass();
  const el = await seite(hass);
  const echtWS = hass.callWS;
  hass.callWS = async (msg) => { if (msg.type === 'heimnetz/meldung/github') throw new Error('kaputt'); return echtWS.call(hass, msg); };
  el.meldenAuf();
  el._blatt.form.text = 'x';
  el.githubAuf();
  await warten(10);
  await el.updateComplete;
  assert.match(blatt(el).textContent, /Vorschau nicht abrufbar: kaputt/);
  assert.ok(el.shadowRoot.querySelector('.gh-senden').disabled, 'ohne Vorschau nicht senden');
  let geoeffnet = 0;
  const echt = window.open;
  window.open = () => { geoeffnet++; return null; };
  try {
    await el.meldungSenden(true);
    assert.equal(geoeffnet, 0, 'ohne Vorschau kein Fenster');
    // Speichern scheitert: Dialog bleibt mit Fehler, Schalter und Zurück gesperrt nur während des Sendens
    let weiter;
    hass.callWS = async (msg) => {
      if (msg.type === 'heimnetz/meldung/neu') { await new Promise((r) => { weiter = r; }); throw new Error('voll'); }
      return echtWS.call(hass, msg);
    };
    el.githubZelle(false);
    await warten(10);
    await el.updateComplete;
    el.shadowRoot.querySelector('.gh-senden').click();
    await el.updateComplete;
    assert.ok(blatt(el).querySelector('.sw').disabled && knoepfe(blatt(el)).find((b) => b.textContent.trim() === 'Zurück').disabled);
    el.githubZelle(true);
    assert.equal(el._blatt.vorher.form.zelle, false, 'während des Sendens bleibt der Schalter');
    weiter();
    await warten(10);
    await el.updateComplete;
    assert.equal(el._blatt.art, 'github');
    assert.match(blatt(el).textContent, /Nicht gesendet: voll/);
    // inzwischen hat jemand anderer gemeldet: die Nummer im Issue stimmt nicht mehr – die Rückmeldung sagt es
    hass.callWS = async (msg) => (msg.type === 'heimnetz/meldung/neu' ? { id: 'm9', ticket: 'FE-0004' } : echtWS.call(hass, msg));
    el.shadowRoot.querySelector('.gh-senden').click();
    await warten(10);
    await el.updateComplete;
  } finally {
    window.open = echt;
  }
  assert.equal(geoeffnet, 2);
  assert.equal(el._blatt, null);
  assert.match(el.shadowRoot.querySelector('.toast').textContent, /Gemeldet als FE-0004 – im Issue auf GitHub steht FE-0003, bitte dort ändern/);
  el.remove();
});

test('Meldungen: ⚙ zeigt die Zeile, Liste filtert, Admin schließt', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await einstellungen(el);
  await warten(10);
  await einTab(el, 'Meldungen');
  assert.match(text(el), /Tickets aus dem Melden-Knopf.*1 offen · 1 erledigt/);
  knoepfe(blatt(el)).find((b) => b.textContent.includes('1 offen · 1 erledigt')).click();
  await warten(10);
  await el.updateComplete;
  let t = text(el);
  assert.match(t, /FE-0002.*Karte bleibt grau/);
  assert.ok(!t.includes('Tablet offline'), 'nur offene');
  assert.ok(!/undefined|NaN|\[object Object\]/.test(t), t);
  knoepfe(blatt(el)).find((b) => b.textContent.startsWith('alle')).click();
  await el.updateComplete;
  t = text(el);
  assert.match(t, /Tablet offline.*Claude · v0\.7\.1 · Commit 3f2a9c1 · Abgleich korrigiert/);
  assert.ok(el.shadowRoot.querySelector('.ml-bilder img'), 'Bild des Tickets');
  knoepfe(blatt(el)).find((b) => b.textContent.includes('Schließen')).click();
  await warten(10);
  assert.deepEqual(hass.aufrufe.find((a) => a.type === 'heimnetz/meldung/status'), { type: 'heimnetz/meldung/status', meldung_id: 'a1', status: 'geschlossen', sprache: 'de' });
});

test('Meldungen: ohne Admin keine Knöpfe zum Schließen und Löschen', async () => {
  const hass = machHass({ admin: false });
  const el = await seite(hass);
  el.meldungenOeffnen();
  await warten(10);
  await el.updateComplete;
  assert.match(text(el), /Karte bleibt grau/);
  assert.ok(!knoepfe(blatt(el)).some((b) => /Schließen|Löschen/.test(b.textContent)));
  assert.match(text(el), /nur Admins/);
});

test('FE-0001: Bild aus der Galerie ohne Typ wird geladen und gemeldet', async () => {
  const { istBildDatei } = await import(`${QUELLE}/heimnetz-panel.js`);
  assert.equal(istBildDatei({ type: '' }), true, 'Android-App: ohne Typ');
  assert.equal(istBildDatei({ type: 'image/png' }), true);
  assert.equal(istBildDatei({ type: 'video/mp4' }), false);
  const hass = machHass();
  const el = await seite(hass);
  el.meldenAuf();
  await el.updateComplete;
  const wahl = el.shadowRoot.querySelector('.mb-knoepfe input[type=file]');
  assert.ok(wahl && !wahl.multiple && !wahl.hasAttribute('multiple'), 'ein Bild je Auswahl (Android-App)');
  // Bild laden nachstellen: Objekt-Adresse und Image wie im Browser
  const echtesImage = globalThis.Image, echtesURL = globalThis.URL;
  const genommen = [];
  globalThis.URL = { createObjectURL: () => 'blob:x', revokeObjectURL: () => {} };
  globalThis.Image = class { set src(_) { this.naturalWidth = 1080; this.naturalHeight = 2400; setTimeout(() => this.onload(), 0); } };
  el.bildAus = (_q, b, h, wie) => genommen.push([b, h, wie]);
  try {
    el.bildDatei({ type: '', name: 'Screenshot_1.png' }, 'gewählt');
    assert.match(el.shadowRoot.querySelector('.toast').textContent || el._toast, /Bild wird geladen/);
    await warten(5);
    assert.deepEqual(genommen, [[1080, 2400, 'gewählt']]);
    el.bildDatei({ type: 'application/pdf', name: 'x.pdf' }, 'gewählt');
    assert.match(el._toast, /Kein Bild/);
  } finally {
    globalThis.Image = echtesImage; globalThis.URL = echtesURL;
    el.meldenZu();
    el.remove();
  }
});

test('FE-0001: Entwurf übersteht ein Neuladen der Seite', async () => {
  sessionStorage.clear();
  const hass = machHass();
  const el = await seite(hass);
  el.meldenAuf();
  await el.updateComplete;
  const ta = el.shadowRoot.querySelector('textarea[name=ml-text]');
  ta.value = 'Karte grau';
  ta.dispatchEvent(new Event('input'));
  el._blatt.form.bilder.push({ url: 'data:image/jpeg;base64,AAAA', b: 720, h: 1600, kb: 1 });
  el.entwurfMerken();
  el.remove();
  const neu = await seite(machHass());
  assert.equal(neu._blatt && neu._blatt.art, 'melden', 'Dialog wieder offen');
  assert.equal(neu._blatt.form.text, 'Karte grau');
  assert.equal(neu.shadowRoot.querySelectorAll('.mb-bild img').length, 1, 'Bild wieder da');
  neu.meldenZu();
  assert.equal(sessionStorage.getItem('heimnetz-melden-entwurf'), null, 'Abbrechen löscht den Entwurf');
  neu.remove();
});

test('AN-0001: Geräte nach Verbindung gruppiert, eine Zeile je Gerät, Gruppe zuklappbar', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Geräte');
  const kopf = [...el.shadowRoot.querySelectorAll('.ggr summary')].map((s) => [...s.querySelectorAll('span')].map((x) => x.textContent.trim()));
  assert.deepEqual(kopf.map((k) => k[0]), DATEN.geraete.gruppen.map((g) => g.name));
  assert.match(kopf[0][1], new RegExp(`${DATEN.geraete.gruppen[0].online} von ${DATEN.geraete.gruppen[0].gesamt} online`));
  assert.equal(el.shadowRoot.querySelectorAll('.geraet.gk').length, DATEN.geraete.geraete.length);
  assert.equal(el.shadowRoot.querySelectorAll('.geraet .badge').length, 0, 'Punkt statt Abzeichen');
  const fuenf = DATEN.geraete.geraete.find((g) => g.band === '5 GHz');
  assert.ok(text(el).includes(`${fuenf.name}${fuenf.ip} · 5 GHz`), 'volle IP und Band');
  // erste Gruppe zuklappen: ihre Geräte verschwinden, ohne neue Abfrage
  const vorher = hass.aufrufe.length, n = DATEN.geraete.gruppen[0].gesamt;
  el.shadowRoot.querySelector('.ggr summary').click();
  await el.updateComplete;
  assert.equal(el.shadowRoot.querySelectorAll('.geraet.gk').length, DATEN.geraete.geraete.length - n);
  assert.equal(hass.aufrufe.length, vorher);
});

test('AN-0001: volle IP, Umschalter nach Art, Art im Verlauf wählbar', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await reiter(el, 'Geräte');
  const g0 = DATEN.geraete.geraete.find((g) => g.ip);
  assert.ok(text(el).includes(g0.ip), 'volle IP-Adresse');
  knoepfe(el.shadowRoot).find((b) => b.textContent === 'nach Art').click();
  await el.updateComplete;
  const kopf = [...el.shadowRoot.querySelectorAll('.ggr summary span:first-child')].map((s) => s.textContent);
  assert.deepEqual(kopf, DATEN.geraete.gruppen_art.map((g) => g.text));
  assert.equal(el.shadowRoot.querySelectorAll('.geraet.gk').length, DATEN.geraete.geraete.length);
  // Verlauf: Art mit Quelle, Admin wählt
  el.shadowRoot.querySelector('.geraet').click();
  await warten(10);
  await el.updateComplete;
  assert.match(text(el), new RegExp(`Art · ${DATEN.geraet.art_quelle.replace(/[()]/g, '.')}`));
  const wahl = el.shadowRoot.querySelector('select.ga-wahl');
  wahl.value = 'medien';
  wahl.dispatchEvent(new Event('change'));
  await warten(10);
  assert.deepEqual(hass.aufrufe.find((a) => a.type === 'heimnetz/geraet/art'), { type: 'heimnetz/geraet/art', geraet: DATEN.geraet.id, art: 'medien', sprache: 'de' });
});

test('AN-0001: ohne Admin keine Auswahl der Art', async () => {
  const el = await seite(machHass({ admin: false }));
  await el.geraetOeffnen(DATEN.geraet.id);
  await el.updateComplete;
  assert.ok(!el.shadowRoot.querySelector('select.ga-wahl'));
  assert.match(text(el), /Art · /);
});

test('AN-0002: Einstellungen mit Reitern, je eine Gruppe, Schalter statt Checkbox', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await einstellungen(el);
  await warten(10);
  await el.updateComplete;
  const reiter = [...blatt(el).querySelectorAll('.e-reiter button')].map((b) => b.textContent.trim());
  assert.deepEqual(reiter, ['📈 Speedtest', '⏱️ Messplan', '📶 WLAN', '💬 Meldungen', '🧩 Einrichtung', '🔬 Diagnose']);
  assert.ok(blatt(el).querySelector('[name=tarif_down]'), 'Speedtest zuerst');
  assert.ok(!blatt(el).querySelector('input[type=time]'), 'Messplan nicht gleichzeitig');
  const vorher = hass.aufrufe.length;
  await einTab(el, 'Messplan');
  assert.equal(hass.aufrufe.length, vorher, 'Reiterwechsel ohne Abfrage');
  assert.ok(!blatt(el).querySelector('input[type=checkbox]'));
  blatt(el).querySelector('.sw').click();
  await warten(10);
  assert.equal(hass.aufrufe.find((a) => a.type === 'heimnetz/messplan/setzen').an, !DATEN.einstellungen.messplan.an);
  await einTab(el, 'WLAN');
  assert.match(text(el), /Schwacher Empfang unter/);
  assert.ok(!/undefined|NaN/.test(text(el)));
});

test('WU-0001: Serie starten, Fortschritt, Ergebnis mit Median und Spanne', async () => {
  const hass = machHass();
  const e = DATEN.einstellungen;
  const serie = { t: Date.now() / 1000 - 60, geplant: 3, server: ['Wien – Magenta'], anteil: 79,
    down: { median: 118, min: 60, max: 121 }, up: { median: 40, min: 39, max: 41 }, ping: { median: 23, min: 22, max: 27 },
    laeufe: [1, 2, 3].map((i) => ({ t: Date.now() / 1000 - 60 + i * 60, server: 'Wien – Magenta', down: 100 + i, up: 40, ping: 23 })) };
  const alt = hass.callWS;
  hass.callWS = async (msg) => (msg.type === 'heimnetz/einstellungen' ? { ...e, letzte_serie: serie } : alt(msg));
  const el = await seite(hass);
  await reiter(el, 'Speedtest');
  let t = text(el);
  assert.match(t, new RegExp(`▶ ${e.messplan.serie}× messen`));
  assert.match(t, /Letzte Serie.*3 Durchläufe · Wien – Magenta/);
  assert.match(t, /Download \(Median\)\s*118/);
  assert.match(t, /Spanne 60–121 · 79 % vom Tarif/);
  el.shadowRoot.querySelector('.serie-knopf').click();
  await warten(10);
  await el.updateComplete;
  assert.ok(hass.aufrufe.some((a) => a.type === 'heimnetz/serie'));
  assert.match(text(el), new RegExp(`⏳ Serie 1 von ${e.messplan.serie}`));
  el.remove();
});

test('WU-0001: Anzahl der Serie im Messplan wählbar', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Messplan');
  assert.match(text(el), /Server der Serie/);
  [...blatt(el).querySelectorAll('.seg button')].find((b) => b.textContent === '5').click();
  await warten(10);
  assert.equal(hass.aufrufe.find((a) => a.type === 'heimnetz/messplan/setzen').serie, 5);
});

test('WU-0007: Reiter Einrichtung – Stufen, Punkt, Knöpfe; geprüft beim Öffnen', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await einstellungen(el);
  await warten(10);
  await el.updateComplete;
  const fragen = () => hass.aufrufe.filter((a) => a.type === 'heimnetz/einrichtung').length;
  assert.equal(fragen(), 1, 'beim Öffnen von ⚙ geprüft (Punkt am Reiter)');
  const tab = [...blatt(el).querySelectorAll('.e-reiter button')].find((b) => b.textContent.includes('Einrichtung'));
  assert.ok(tab.querySelector('.e-punkt') && !tab.querySelector('.e-punkt.rot'), 'oranger Punkt: Empfohlenes fehlt');
  await einTab(el, 'Einrichtung');
  await warten(10);
  await el.updateComplete;
  assert.equal(fragen(), 2, 'beim Öffnen des Reiters neu geprüft');
  const t = text(el);
  assert.match(t, /2 empfohlen/);
  assert.match(t, /Muss/); assert.match(t, /4 von 4/); assert.match(t, /Soll – empfohlen/); assert.match(t, /Kann – optional/);
  assert.match(t, /eingerichtet · FRITZ!Box 6860 5G/);
  assert.match(t, /Heimnetz installiert nichts selbst/);
  assert.ok(!/undefined|NaN|\[object Object\]/.test(t), t);
  assert.equal(blatt(el).querySelectorAll('.vs').length, 9);
  const zeile = (k) => blatt(el).querySelector(`.vs[data-teil=${k}]`);
  assert.ok(zeile('ookla').querySelector('.vs-st.fehlt'));
  assert.match(zeile('ookla').textContent, /heruntergeladen – nach einem Neustart einrichten/);
  assert.ok(zeile('opencellid').querySelector('.vs-st.aus'));
  // Knöpfe: in Home Assistant navigieren bzw. extern im neuen Fenster
  const ziele = [];
  el.oeffne = (z) => ziele.push(z);
  knoepfe(zeile('ookla')).find((b) => b.textContent.includes('Einrichten')).click();
  await el.updateComplete;
  assert.deepEqual(ziele, ['/_my_redirect/config_flow_start?domain=ookla_speedtest']);
  assert.ok(!el.shadowRoot.querySelector('.sheet.an'), 'Fenster zu vor dem Wechsel');
  await einstellungen(el);
  await einTab(el, 'Einrichtung');
  await warten(10);
  await el.updateComplete;
  const geoeffnet = [];
  const echt = window.open;
  window.open = (...a) => { geoeffnet.push(a); return null; };
  try {
    knoepfe(zeile('opencellid')).find((b) => b.textContent.includes('Schlüssel holen')).click();
    knoepfe(zeile('archiv')).find((b) => b.textContent.includes('In HACS öffnen')).click();
  } finally {
    window.open = echt;
  }
  assert.deepEqual(geoeffnet, [['https://opencellid.org', '_blank', 'noopener']]);
  assert.equal(ziele[1], '/_my_redirect/hacs_repository?owner=jonathan-gtd&repository=scribe&category=integration');
});

test('WU-0007: roter Punkt, wenn Nötiges fehlt', async () => {
  const hass = machHass();
  const e = DATEN.einrichtung;
  const muss = { ...e, muss_fehlt: 1, punkt: 'rot', stufen: e.stufen.map((s) => s.stufe !== 'muss' ? s : { ...s, ok: 3,
    teile: s.teile.map((x) => x.schluessel !== 'hacs' ? x : { ...x, status: 'muss', stand: null, wofuer: 'ohne HACS kommen keine Updates',
      aktionen: [{ text: 'Anleitung ↗', ziel: 'https://hacs.xyz/docs/use/', extern: true, blau: true }] }) }) };
  const alt = hass.callWS.bind(hass);
  hass.callWS = async (msg) => (msg.type === 'heimnetz/einrichtung' ? muss : alt(msg));
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Einrichtung');
  await warten(10);
  await el.updateComplete;
  assert.ok(blatt(el).querySelector('.e-reiter .e-punkt.rot'));
  assert.match(text(el), /1 Voraussetzung fehlt/);
  assert.match(text(el), /3 von 4/);
  assert.ok(blatt(el).querySelector('.vs[data-teil=hacs] .vs-st.muss'));
});

test('WU-0007: ohne Admin keine Prüfung und kein Punkt', async () => {
  const hass = machHass({ admin: false });
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Einrichtung');
  await warten(10);
  await el.updateComplete;
  assert.ok(!hass.aufrufe.some((a) => a.type === 'heimnetz/einrichtung'));
  assert.ok(!blatt(el).querySelector('.e-punkt'));
  assert.match(text(el), /sehen nur Admins/);
});

test('WU-0007: Reiter auf Englisch', async () => {
  const hass = machHass({ sprache: 'en' });
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Setup');
  await warten(10);
  await el.updateComplete;
  assert.match(text(el), /Should – recommended/);
  assert.match(text(el), /Heimnetz installs nothing itself/);
});

test('WU-0008: Diagnose – Abfrage sendet Adresse und Kennwort, Ergebnis geschwärzt, Kennwort nicht behalten', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Diagnose');
  await el.updateComplete;
  const b = blatt(el);
  assert.match(text(el), /BETA/);
  b.querySelector('input[name=adresse]').value = '192.168.0.1';
  b.querySelector('input[name=kennwort]').value = 'geheim';
  knoepfe(b).find((x) => x.textContent.includes('Abfragen')).click();
  await warten(10);
  await el.updateComplete;
  const ruf = hass.aufrufe.find((a) => a.type === 'heimnetz/modem');
  assert.ok(ruf && ruf.adresse === '192.168.0.1' && ruf.kennwort === 'geheim');
  const t = text(el);
  assert.match(t, /4 von 5 Abfragen · 198 Werte · 11 geschwärzt/);
  assert.match(t, /ZTE G5TC/);
  assert.match(t, /⟨geschwärzt⟩/);
  assert.ok(!/undefined|NaN|\[object Object\]/.test(t), t);
  // Kennwort nach der Abfrage gelöscht und nie im Zustand
  assert.equal(blatt(el).querySelector('input[name=kennwort]').value, '');
  assert.ok(!JSON.stringify(el._diag).includes('geheim'));
  assert.ok(knoepfe(blatt(el)).some((x) => x.textContent.includes('Als Datei speichern')));
  assert.ok(knoepfe(blatt(el)).some((x) => x.textContent.includes('Kopieren')));
});

test('WU-0008: Adresse außerhalb des Heimnetzes → Befund „Adresse nicht erlaubt“', async () => {
  const hass = machHass();
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Diagnose');
  await el.updateComplete;
  const b = blatt(el);
  b.querySelector('input[name=adresse]').value = '8.8.8.8';
  knoepfe(b).find((x) => x.textContent.includes('Abfragen')).click();
  await warten(10);
  await el.updateComplete;
  assert.match(text(el), /Adresse nicht erlaubt/);
});

test('WU-0008: ohne Admin kein Diagnose-Formular', async () => {
  const hass = machHass({ admin: false });
  const el = await seite(hass);
  await einstellungen(el);
  await einTab(el, 'Diagnose');
  await el.updateComplete;
  assert.match(text(el), /nur Admins/);
  assert.ok(!blatt(el).querySelector('input[name=adresse]'));
});
