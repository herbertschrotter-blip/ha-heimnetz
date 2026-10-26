// Formatierung der Seite (nur Darstellung).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { QUELLE } from './umgebung.mjs';

const f = await import(`${QUELLE}/format.js`);
const { waehle } = await import(`${QUELLE}/sprache.js`);
waehle({ language: 'de' });

test('Zahlen deutsch, null als Strich', () => {
  assert.equal(f.zahl(1234.5, 1), '1.234,5');
  assert.equal(f.zahl(null), '–');
});

test('Zeiten relativ zu heute', () => {
  const jetzt = new Date(2026, 9, 12, 15, 0).getTime();
  assert.equal(f.zeit(new Date(2026, 9, 12, 14, 5).getTime() / 1000, jetzt), 'Heute 14:05');
  assert.equal(f.zeit(new Date(2026, 9, 11, 22, 31).getTime() / 1000, jetzt), 'Gestern 22:31');
  assert.equal(f.zeit(new Date(2026, 9, 10, 9, 0).getTime() / 1000, jetzt), 'Sa 10.10. 09:00');
  assert.equal(f.vor(jetzt / 1000 - 32 * 60, jetzt), 'vor 32 min');
});

test('Farbe aus der Lage, Tageszeit aus der Sonne', () => {
  assert.match(f.farbe(0), /var\(--amber\) 0%, var\(--rot\)/);
  assert.match(f.farbe(1), /var\(--s3\) 100%/);
  assert.equal(f.farbe(null), 'rgba(127,127,127,.12)');
  assert.equal(f.phase({ attributes: { elevation: 2, rising: true } }), 'morgen');
  assert.equal(f.phase({ attributes: { elevation: 2, rising: false } }), 'abend');
  assert.equal(f.phase(undefined), 'tag');
});

test('FE-0003: Kacheln schweben nicht dauernd (nur Einblenden)', async () => {
  const { readFileSync } = await import('node:fs');
  const stil = readFileSync(`${QUELLE}/stil.js`, 'utf8');
  const regel = stil.match(/\.glas-k \{[^}]*\}/)[0];
  assert.match(regel, /animation: rein /);
  assert.ok(!/infinite/.test(regel), regel);
  assert.ok(!/schweben2/.test(stil));
});
