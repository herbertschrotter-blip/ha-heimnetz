// Wächter-Skript der Shelly-Steckdose (custom_components/heimnetz/shelly/waechter.js) mit einer nachgebauten Steckdose:
// Zeit, Erreichbarkeit der Adressen, KVS und Schalter sind von Hand gesteuert.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const ALLE_WEG = { 'connectivitycheck.gstatic.com': false, 'detectportal.firefox.com': false, 'www.msftconnecttest.com': false };
const QUELLE = join(dirname(fileURLToPath(import.meta.url)), '../../custom_components/heimnetz/shelly/waechter.js');
const CODE = readFileSync(QUELLE, 'utf8');

// Regeln wie logik/waechter.py:kvs – kurze Schlüssel, Adressen ohne http://
const ohne = (u) => (u ? u.replace('http://', '') : undefined);
function kurz(c) {
  const k = { v: c.v, an: c.an === false ? 0 : 1, p: c.pruef_s, s2: c.stufe2_min, a: c.aus_s, ab: c.abstand_min, pn: c.pause_nach,
    ph: c.pause_h, e: ohne(c.eigen), r: c.rolle, po: c.pos, n: c.anzahl, na: ohne(c.nach), vo: ohne(c.vor), pa: c.partner, ne: ohne(c.netz), ho: ohne(c.host),
    i: c.ziele && c.ziele.length ? 1 : undefined };
  const s = JSON.stringify(k);
  assert.ok(s.length <= 254, s);
  return s;
}

function steckdose(regeln, netz = {}) {
  const d = { uptime: 0, kvs: { 'heimnetz-waechter': kurz(regeln) }, netz, schaltungen: [], output: true, partner: true, timer: [], endpunkte: {} };
  const call = (methode, p, cb) => {
    if (methode === 'HTTP.GET') {
      if (p.url.includes('/rpc/Switch.GetStatus')) return cb({ code: 200, body: JSON.stringify({ output: d.partner }) }, 0);
      const host = p.url.replace('http://', '').split('/')[0];
      return d.netz[host] === false ? cb(null, -104, 'timeout') : cb({ code: 200 }, 0);
    }
    if (methode === 'KVS.GetMany') return cb({ items: Object.entries(d.kvs).map(([key, value]) => ({ key, value })) }, 0);
    if (methode === 'Switch.Set') { d.schaltungen.push(JSON.parse(JSON.stringify(p))); d.output = p.on; return cb({}, 0); }
    throw new Error(methode);
  };
  const ctx = {
    Shelly: { call, getComponentStatus: (k) => (k === 'sys' ? { uptime: d.uptime, unixtime: 1_800_000_000 + d.uptime } : { output: d.output, aenergy: { by_minute: [131, 132, 132] } }) },
    Timer: { set: (ms, wiederholt, fn) => d.timer.push({ ms, wiederholt, fn }) },
    HTTPServer: { registerEndpoint: (n, fn) => { d.endpunkte[n] = fn; } },
    JSON, Math,
  };
  vm.createContext(ctx);
  vm.runInContext(CODE, ctx);
  d.runde = d.timer.find((t) => !t.wiederholt).fn;
  d.minuten = (n) => { for (let i = 0; i < n; i++) { d.uptime += 60; d.runde(); } };
  d.status = () => { const res = { send() {} }; d.endpunkte.status({}, res); return JSON.parse(res.body); };
  d.eval = (code) => JSON.parse(vm.runInContext(code, ctx));
  d.befehl = (x, n, extra = {}) => { d.kvs['heimnetz-waechter-befehl'] = JSON.stringify({ x, n, ...extra }); };
  return d;
}

const BOX = { v: 1, rolle: 'kette', pos: 0, anzahl: 1, eigen: 'http://192.168.178.1', ziele: ['fest'], stufe2_min: 12, aus_s: 30, abstand_min: 60, pause_nach: 3, pause_h: 6 };

test('alles gut: bereit, kein Schalten', () => {
  const d = steckdose(BOX);
  d.minuten(30);
  assert.equal(d.status().zustand, 'bereit');
  assert.equal(d.schaltungen.length, 0);
  assert.equal(d.status().wv, 2);
});

test('Internet weg: erst nach 12 min Strom aus mit von selbst wieder ein', () => {
  const d = steckdose(BOX, { ...ALLE_WEG });
  d.minuten(12);
  assert.equal(d.schaltungen.length, 0, 'nicht vor Ablauf');
  assert.equal(d.status().zustand, 'stoerung');
  d.minuten(1);
  assert.deepEqual(d.schaltungen, [{ id: 0, on: false, toggle_after: 30 }]);
});

test('ein Ziel reicht: kein Eingriff, wenn eines antwortet', () => {
  const d = steckdose(BOX, { 'connectivitycheck.gstatic.com': false });
  d.minuten(30);
  assert.equal(d.schaltungen.length, 0);
});

test('Bremse: höchstens 1× pro Stunde, nach 3 Fehlschlägen Pause', () => {
  const d = steckdose(BOX, { ...ALLE_WEG });
  d.minuten(13);
  d.output = true; // Steckdose hat sich von selbst wieder eingeschaltet
  d.minuten(30);
  assert.equal(d.schaltungen.length, 1, 'innerhalb der Stunde kein zweites Mal');
  d.minuten(40); d.output = true; d.minuten(70); d.output = true; d.minuten(70); d.output = true;
  assert.equal(d.schaltungen.length, 3);
  assert.equal(d.status().zustand, 'pause');
  d.minuten(120); d.output = true;
  assert.equal(d.schaltungen.length, 3, 'in der Pause nichts');
});

test('Erholung setzt die Fehlschläge zurück', () => {
  const d = steckdose(BOX, { ...ALLE_WEG });
  d.minuten(13); d.output = true;
  d.netz['connectivitycheck.gstatic.com'] = true;
  d.minuten(2);
  const s = d.status();
  assert.equal(s.zustand, 'bereit');
  assert.equal(s.fehl, 0);
  assert.ok(s.letzte.some((e) => e.was === 'ok'));
});

test('Kette Modem → Router: Modem-Steckdose urteilt nur, wenn der Router antwortet', () => {
  const modem = { ...BOX, pos: 0, anzahl: 2, eigen: 'http://192.168.0.1', nach: 'http://192.168.178.1' };
  const d = steckdose(modem, { '192.168.178.1': false, '192.168.0.1': false, ...ALLE_WEG });
  d.minuten(30);
  assert.equal(d.schaltungen.length, 0, 'Router weg: dessen Steckdose ist dran');
  d.netz['192.168.178.1'] = true;
  d.minuten(13);
  assert.equal(d.schaltungen.length, 1, 'Router da, Modem weg: Modem neu');
});

test('Kette: Router-Steckdose lässt dem Modem den Vortritt (doppelte Wartezeit) und wartet, solange der Partner schaltet', () => {
  const router = { ...BOX, pos: 1, anzahl: 2, vor: 'http://192.168.0.1', partner: '192.168.170.41' };
  const d = steckdose(router, { ...ALLE_WEG });
  d.minuten(20);
  assert.equal(d.schaltungen.length, 0);
  d.partner = false; // Modem-Steckdose ist gerade aus
  d.minuten(10);
  assert.equal(d.schaltungen.length, 0, 'Partner schaltet: warten');
  d.partner = true;
  d.minuten(1);
  assert.equal(d.schaltungen.length, 1);
});

test('Kette: Router antwortet nicht → Router-Steckdose schaltet nach der einfachen Zeit', () => {
  const router = { ...BOX, pos: 1, anzahl: 2, vor: 'http://192.168.0.1' };
  const d = steckdose(router, { '192.168.178.1': false, ...ALLE_WEG, '192.168.0.1': false });
  d.minuten(13);
  assert.equal(d.schaltungen.length, 1);
});

test('Home Assistant: nur wenn der Router antwortet (sonst ist das WLAN schuld)', () => {
  const ha = { ...BOX, rolle: 'ha', eigen: 'http://192.168.178.60:8123', netz: 'http://192.168.178.1', ziele: [], stufe2_min: 20, aus_s: 15, abstand_min: 120 };
  const d = steckdose(ha, { '192.168.178.60:8123': false, '192.168.178.1': false });
  d.minuten(40);
  assert.equal(d.schaltungen.length, 0);
  d.netz['192.168.178.1'] = true;
  d.minuten(21);
  assert.deepEqual(d.schaltungen, [{ id: 0, on: false, toggle_after: 15 }]);
});

test('Befehle aus Heimnetz: Ruhe und Weiter; der Befehl von vor dem Start zählt nicht', () => {
  const d = steckdose(BOX, { ...ALLE_WEG });
  d.befehl('ruhe', 1, { min: 30 });
  d.minuten(13);
  assert.equal(d.schaltungen.length, 1, 'alter Befehl wirkt nicht');
  d.output = true;
  d.befehl('ruhe', 2, { min: 600 });
  d.minuten(100);
  assert.equal(d.status().zustand, 'pause');
  assert.equal(d.schaltungen.length, 1);
  d.befehl('weiter', 3);
  d.minuten(14);
  assert.equal(d.schaltungen.length, 2);
});

test('ausgeschaltet oder ohne Regeln: nichts tun', () => {
  const d = steckdose({ ...BOX, an: false }, { ...ALLE_WEG });
  d.minuten(30);
  assert.equal(d.schaltungen.length, 0);
  assert.equal(d.status().zustand, 'aus_regel');
});

test('Skript bleibt mJS und ASCII: kein const, keine Pfeile, keine Vorlagen-Strings, keine Umlaute', () => {
  assert.ok(/^[\x00-\x7f]*$/.test(CODE), 'nur ASCII – der Interpreter der Shelly verschluckt sich an UTF-8');
  const ohneKommentar = CODE.replace(/\/\/.*$/gm, '');
  assert.ok(!/\bconst\b/.test(ohneKommentar));
  assert.ok(!/=>/.test(ohneKommentar));
  assert.ok(!/`/.test(ohneKommentar));
});

test('„wieder in Ordnung“ auch, wenn eine Runde in die Aus-Zeit fällt', () => {
  const d = steckdose({ ...BOX, aus_s: 60 }, { ...ALLE_WEG });
  d.minuten(13);
  assert.equal(d.schaltungen.length, 1);
  d.minuten(1); // Steckdose noch aus
  assert.equal(d.status().zustand, 'aus');
  d.output = true;
  d.netz['connectivitycheck.gstatic.com'] = true;
  d.minuten(1);
  assert.ok(d.status().letzte.some((e) => e.was === 'ok'));
});

test('kaputte Regeln bleiben als Grund stehen; status() über Script.Eval wie der Endpunkt', () => {
  const d = steckdose(BOX);
  d.kvs['heimnetz-waechter'] = '{kaputt';
  d.minuten(2);
  assert.equal(d.status().grund, 'regeln_kaputt');
  assert.deepEqual(d.eval('status()'), d.status());
});

test('Grundlage aus dem Einspielen: der erste echte Befehl wirkt', () => {
  const d = steckdose(BOX, { ...ALLE_WEG });
  d.befehl('keiner', 0);
  d.minuten(1);
  d.befehl('ruhe', 1, { min: 120 });
  d.minuten(20);
  assert.equal(d.schaltungen.length, 0);
  assert.equal(d.status().zustand, 'pause');
});

test('Home Assistant: lebt der Pi (Beobachter antwortet), erst nach dreifacher Zeit; sonst nach der einfachen – mit Befund', () => {
  const ha = { ...BOX, rolle: 'ha', eigen: 'http://192.168.178.60:8123', netz: 'http://192.168.178.1', host: 'http://192.168.178.60:4357', ziele: [], stufe2_min: 20, aus_s: 15, abstand_min: 120 };
  const d = steckdose(ha, { '192.168.178.60:8123': false });
  d.minuten(21);
  assert.equal(d.schaltungen.length, 0, 'Pi lebt: der Supervisor startet Home Assistant selbst neu');
  assert.equal(d.status().grund, 'ha_weg_pi_lebt');
  d.minuten(40);
  assert.equal(d.schaltungen.length, 1, 'nach 60 min doch');
  const e = d.status().letzte.find((x) => x.was === 'strom');
  assert.equal(e.grund, 'ha_weg_pi_lebt');
  assert.equal(e.b.h, true);
  assert.equal(e.b.e, false);
  const tot = steckdose(ha, { '192.168.178.60:8123': false, '192.168.178.60:4357': false });
  tot.minuten(21);
  assert.equal(tot.schaltungen.length, 1);
  assert.equal(tot.status().letzte.find((x) => x.was === 'strom').grund, 'pi_weg');
});

test('Home Assistant: ein einzelner Aussetzer des Beobachters kürzt die Wartezeit nicht', () => {
  const ha = { ...BOX, rolle: 'ha', eigen: 'http://192.168.178.60:8123', netz: 'http://192.168.178.1', host: 'http://192.168.178.60:4357', ziele: [], stufe2_min: 20, aus_s: 15, abstand_min: 120 };
  const d = steckdose(ha, { '192.168.178.60:8123': false });
  d.minuten(25);
  d.netz['192.168.178.60:4357'] = false;
  d.minuten(1);
  d.netz['192.168.178.60:4357'] = true;
  d.minuten(10);
  assert.equal(d.schaltungen.length, 0, 'Pi lebt weiter – noch 60 min abwarten');
  d.netz['192.168.178.60:4357'] = false;
  d.minuten(3);
  assert.equal(d.schaltungen.length, 1, 'drei Runden ohne Beobachter: der Pi ist weg');
});
