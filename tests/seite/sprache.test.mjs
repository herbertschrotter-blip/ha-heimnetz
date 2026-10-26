// Sprache der Seite (WU-0006): Deutsch oder Englisch nach der Sprache des Nutzers in HA, Zahlen- und Datumsformat
// dazu; jeder Text der Seite hat eine englische Zeile. Texte der Integration (Befunde, Prüfungen …) bleiben hier außen
// vor – die liefert die Integration selbst in der Sprache des Nutzers.
import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { DATEN, QUELLE, machHass, seite, text, warten } from './umgebung.mjs';

const { EN, t, waehle, sprache } = await import(`${QUELLE}/sprache.js`);
const f = await import(`${QUELLE}/format.js`);
const { REITER } = await import(`${QUELLE}/heimnetz-panel.js`);

after(() => document.body.replaceChildren());

/** Alle Quellen der Seite außer sprache.js. */
function quellen(ordner = QUELLE) {
  return readdirSync(ordner, { withFileTypes: true }).flatMap((e) => {
    const pfad = join(ordner, e.name);
    if (e.isDirectory()) return quellen(pfad);
    return e.name.endsWith('.js') && e.name !== 'sprache.js' && e.name !== 'leaflet-stil.js' ? [pfad] : [];
  });
}

/** Texte, die über t() oder merke() laufen – auch beide Zweige von t(n === 1 ? '…' : '…'). */
function schluessel() {
  const gefunden = new Map();
  const merken = (k, datei) => { if (!gefunden.has(k)) gefunden.set(k, datei); };
  for (const datei of quellen()) {
    const s = readFileSync(datei, 'utf8');
    for (const m of s.matchAll(/\b(?:t|merke)\(\s*'((?:[^'\\]|\\.)*)'/g)) merken(m[1], datei);
    for (const m of s.matchAll(/\bt\(\s*[^'(),]*\?\s*'((?:[^'\\]|\\.)*)'\s*:\s*'((?:[^'\\]|\\.)*)'/g)) { merken(m[1], datei); merken(m[2], datei); }
  }
  return gefunden;
}
const platzhalter = (s) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',');

test('jeder Text der Seite hat eine englische Zeile mit denselben Platzhaltern', () => {
  const k = schluessel();
  assert.ok(k.size > 300, `nur ${k.size} Texte gefunden – Suche kaputt?`);
  const fehlt = [...k].filter(([x]) => !(x in EN)).map(([x, datei]) => `${datei.split('/src/')[1]}: ${x}`);
  assert.deepEqual(fehlt, [], `ohne englische Zeile:\n${fehlt.join('\n')}`);
  for (const [x] of k) assert.equal(platzhalter(EN[x]), platzhalter(x), `Platzhalter: ${x}`);
});

test('keine englische Zeile ohne Text in der Seite', () => {
  const k = schluessel();
  const uebrig = Object.keys(EN).filter((x) => !k.has(x));
  assert.deepEqual(uebrig, [], `nicht mehr benutzt:\n${uebrig.join('\n')}`);
});

test('Sprache nach HA: de und Varianten Deutsch, alles andere Englisch', () => {
  assert.equal(waehle({ language: 'de' }), 'de');
  assert.equal(waehle({ language: 'de-CH' }), 'de');
  assert.equal(waehle({ locale: { language: 'de' }, language: 'en' }), 'de', 'Profil (locale) vor language');
  assert.equal(waehle({ language: 'en' }), 'en');
  assert.equal(waehle({ language: 'en-GB' }), 'en');
  assert.equal(waehle({ language: 'fr' }), 'en');
  assert.equal(waehle({ language: 'dE' }), 'de');
  assert.equal(waehle({ language: 'dsb' }), 'en', 'Niedersorbisch ist kein Deutsch');
  assert.equal(waehle(undefined), 'en');
  assert.equal(waehle({}), 'en');
  assert.equal(sprache(), 'en');
});

test('Platzhalter werden gefüllt, unbekannte bleiben stehen', () => {
  waehle({ language: 'de' });
  assert.equal(t('vor {n} min', { n: 5 }), 'vor 5 min');
  waehle({ language: 'en' });
  assert.equal(t('vor {n} min', { n: 5 }), '5 min ago');
  assert.equal(t('{n} offen · {erledigt} erledigt', { n: 2 }), '2 open · {erledigt} done');
  assert.equal(t('nicht übersetzt'), 'nicht übersetzt', 'fehlt die Zeile, bleibt der Text');
});

test('Zahlen und Zeiten: Deutsch 1.234,5 und „Sa 10.10.“, Englisch 1,234.5 und „Sat 10 Oct“', () => {
  const jetzt = new Date(2026, 9, 12, 15, 0).getTime();
  const s = (d) => d.getTime() / 1000;
  waehle({ language: 'de' });
  assert.equal(f.zahl(1234.5, 1), '1.234,5');
  assert.equal(f.zeit(s(new Date(2026, 9, 10, 9, 0)), jetzt), 'Sa 10.10. 09:00');
  assert.deepEqual(f.wochentage(true).slice(0, 2), ['Mo', 'Di']);
  waehle({ language: 'en' });
  assert.equal(f.zahl(1234.5, 1), '1,234.5');
  assert.equal(f.zahl(null), '–');
  assert.equal(f.zeit(s(new Date(2026, 9, 12, 14, 5)), jetzt), 'Today 14:05');
  assert.equal(f.zeit(s(new Date(2026, 9, 11, 22, 31)), jetzt), 'Yesterday 22:31');
  assert.equal(f.zeit(s(new Date(2026, 9, 10, 9, 0)), jetzt), 'Sat 10 Oct 09:00');
  assert.equal(f.tag(s(new Date(2026, 9, 10, 9, 0)), jetzt), 'Sat 10 Oct');
  assert.equal(f.tag(s(new Date(2026, 9, 12, 9, 0)), jetzt), 'Today');
  assert.equal(f.vor(jetzt / 1000 - 32 * 60, jetzt), '32 min ago');
  assert.equal(f.vor(jetzt / 1000 - 3 * 86400, jetzt), '3 days ago');
  assert.equal(f.vor(jetzt / 1000 - 10, jetzt), 'just now');
  assert.equal(f.uhr(s(new Date(2026, 9, 10, 9, 7))), '09:07');
  assert.deepEqual(f.wochentage(true).slice(0, 2), ['Mon', 'Tue']);
  assert.deepEqual(f.wochentage().slice(0, 2), ['Sun', 'Mon']);
});

async function klick(el, knopf) {
  knopf.click();
  await warten(10);
  await el.updateComplete;
}

/** Deutsche Texte der Seite, die auf Englisch anders lauten (lang genug, um nicht zufällig in Daten zu stehen). */
const DEUTSCH = Object.entries(EN).filter(([de, en]) => de !== en && de.length >= 12 && !de.includes('{')).map(([de]) => de);
const durchsuchen = (wo, t0) => DEUTSCH.filter((de) => t0.includes(de)).map((de) => `${wo}: ${de}`);

test('englische Seite: Reiter, Kopf und alle Ansichten ohne deutsche Texte der Seite', async () => {
  const hass = machHass({ sprache: 'en' });
  const el = await seite(hass);
  const w = el.shadowRoot;
  assert.equal(w.querySelector('.wurzel').getAttribute('lang'), 'en');
  const namen = [...w.querySelectorAll('nav button')].map((b) => b.textContent.trim());
  assert.deepEqual(namen, ['Overview', 'Speedtest', 'Devices', 'Wireless', 'Usage', 'Log']);
  const funde = [];
  for (const [k] of REITER) {
    await klick(el, [...w.querySelectorAll('nav button')][REITER.findIndex(([x]) => x === k)]);
    if (k === 'funk') {
      funde.push(...durchsuchen('Funk · WLAN', text(el)));
      await klick(el, [...w.querySelectorAll('.leiste .seg button')].find((b) => b.textContent === 'Mobile'));
    }
    const t0 = text(el);
    assert.ok(!/undefined|NaN|\[object Object\]|\{\w+\}/.test(t0), `${k}: ${t0.slice(0, 300)}`);
    funde.push(...durchsuchen(k, t0));
  }
  assert.deepEqual(funde, []);
  // Übersicht und Speedtest mit englischen Wörtern
  await klick(el, w.querySelectorAll('nav button')[0]);
  assert.match(text(el), /Devices online/);
  assert.match(text(el), /Important events/);
  await klick(el, w.querySelectorAll('nav button')[1]);
  assert.match(text(el), /When is the internet fast\?/);
  assert.match(text(el), /Recent measurements/);
  assert.ok([...w.querySelectorAll('.wr button.tag')].map((b) => b.textContent).join(' ').startsWith('Mon Tue Wed'));
});

test('englische Seite: Tagesverlauf, Einstellungen, Melden und Meldungen', async () => {
  const hass = machHass({ sprache: 'en' });
  const el = await seite(hass);
  const w = el.shadowRoot;
  await klick(el, w.querySelectorAll('nav button')[1]);
  w.querySelectorAll('.wr button.tag')[0].click();
  await warten(10);
  await el.updateComplete;
  assert.match(w.querySelector('.tv .gruppe').textContent, /all Mondays/);
  assert.match(w.querySelector('.tv .info').textContent, /Best hour 23–24 h .*weakest 2–3 h/);
  // Messung im Detail
  w.querySelector('table.t tr.klick').click();
  await el.updateComplete;
  assert.match(w.querySelector('.sheet').textContent, /Measurement/);
  assert.deepEqual(durchsuchen('Messung', w.querySelector('.sheet').textContent), []);
  el.zu();
  // Einstellungen, alle Reiter
  await klick(el, [...w.querySelectorAll('.glas-kopf button')].find((b) => b.textContent.trim() === '⚙'));
  const sheet = w.querySelector('.sheet');
  assert.match(sheet.textContent, /Settings/);
  for (const b of [...sheet.querySelectorAll('.e-reiter button')]) {
    await klick(el, b);
    assert.deepEqual(durchsuchen(b.textContent, w.querySelector('.sheet').textContent), []);
  }
  await klick(el, [...w.querySelectorAll('.sheet .e-reiter button')].find((b) => b.textContent.includes('Schedule')));
  assert.match(w.querySelector('.sheet').textContent, /Measure automatically/);
  // Meldungen (Liste) und Melden
  await klick(el, [...w.querySelectorAll('.sheet .e-reiter button')].find((b) => b.textContent.includes('Reports')));
  await klick(el, [...w.querySelectorAll('.sheet button.blau')].at(-1));
  assert.match(w.querySelector('.sheet').textContent, /Every report is a ticket/);
  assert.deepEqual(durchsuchen('Meldungen', w.querySelector('.sheet').textContent), []);
  el.zu();
  await el.updateComplete;
  assert.equal(w.querySelector('.melden-knopf').getAttribute('aria-label'), 'Report');
  await klick(el, w.querySelector('.melden-knopf'));
  const m = w.querySelector('.sheet');
  assert.match(m.textContent, /What happened, what did you expect\?/);
  assert.deepEqual(durchsuchen('Melden', m.textContent), []);
  // Senden ohne Text: Hinweis auf Englisch
  await klick(el, m.querySelector('.ml-senden'));
  assert.match(w.querySelector('.sheet').textContent, /Please describe briefly/);
  // WU-0006: öffentlich auf GitHub melden
  el._blatt.form.text = 'Map grey';
  el._blatt.form.bilder.push({ url: 'data:image/jpeg;base64,AAAA', b: 1, h: 1, kb: 1 }, { url: 'data:image/jpeg;base64,AAAA', b: 1, h: 1, kb: 1 });
  await klick(el, w.querySelector('.ml-github'));
  await warten(10);
  await el.updateComplete;
  el.githubZelle(true);
  await warten(10);
  await el.updateComplete;
  const g = w.querySelector('.sheet');
  assert.match(g.textContent, /Report publicly on GitHub/);
  assert.match(g.textContent, /GitHub cannot take your 2 images over the link/);
  assert.match(w.querySelector('.gh-warn').textContent, /Caution: Cell ID and distance reveal roughly where you live/);
  // Vorschau ist Text der Integration (aus der Vorlage deutsch) – nur der Rest der Seite muss englisch sein
  assert.deepEqual(durchsuchen('GitHub', g.textContent.replace(w.querySelector('.gh-vorschau').textContent, '')), []);
  el.meldenZu();
});

test('Sprache wechselt mit dem Profil in HA, ohne die Seite neu zu laden', async () => {
  const hass = machHass({ sprache: 'de' });
  const el = await seite(hass);
  assert.equal(el.shadowRoot.querySelector('nav button').textContent.trim(), 'Übersicht');
  assert.ok(hass.aufrufe.every((a) => a.sprache === 'de'), 'jede Abfrage nennt die Sprache der Seite');
  const vorher = hass.aufrufe.length;
  el.hass = { ...hass, language: 'en', locale: { ...hass.locale, language: 'en' } };
  await el.updateComplete;
  assert.equal(el.shadowRoot.querySelector('nav button').textContent.trim(), 'Overview');
  // fertige Texte der Integration in der neuen Sprache neu holen
  assert.ok(hass.aufrufe.slice(vorher).some((a) => a.type === 'heimnetz/uebersicht' && a.sprache === 'en'));
  assert.match(text(el), /Devices online/);
  el.hass = hass;
  await el.updateComplete;
  assert.equal(el.shadowRoot.querySelector('nav button').textContent.trim(), 'Übersicht');
});

test('englische Karte: Beschriftung und Quellenangabe', async () => {
  const hass = machHass({ sprache: 'en' });
  const el = await seite(hass);
  const w = el.shadowRoot;
  await klick(el, w.querySelectorAll('nav button')[3]);
  await klick(el, [...w.querySelectorAll('.leiste .seg button')].find((b) => b.textContent === 'Mobile'));
  const karte = w.querySelector('heimnetz-karte');
  assert.ok(karte, 'Karte da');
  await karte.updateComplete;
  const k = karte.shadowRoot;
  assert.equal(k.querySelector('.k-zoom button').getAttribute('title'), 'Zoom in');
  assert.match(k.querySelector('select.k-lage').textContent, /Automatic/);
  assert.ok(DATEN.mobilfunk.karte, 'Vorlage mit Karte');
  assert.match(text(el), /Where is the mast\?/);
});
