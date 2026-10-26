// Darstellung: Zahlen, Zeiten, Farben der Skala. Nichts Fachliches – Lagen (0…1) und Texte kommen von der Integration.
// Zahlen- und Datumsformat folgen der Sprache der Seite (sprache.js): Deutsch 1.234,5 · „Sa 10.10.“, Englisch
// 1,234.5 · „Sat 10 Oct“; die Uhrzeit bleibt in beiden Sprachen 24-stündig (14:05).
import { sprache, t } from './sprache.js';

const TAGE = { de: ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'], en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] };
const MONATE = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const zwei = (n) => String(n).padStart(2, '0');

/** Kurze Wochentage ab Sonntag (wie Date.getDay()) oder ab Montag (Wochenraster der Integration). */
export function wochentage(abMontag = false) {
  const l = TAGE[sprache()] || TAGE.en;
  return abMontag ? [...l.slice(1), l[0]] : l;
}

/** Datum ohne Jahr: „Sa 10.10.“ bzw. „Sat 10 Oct“; `mitTag` = Wochentag davor. */
export function datum(d, mitTag = true) {
  const tagName = mitTag ? `${wochentage()[d.getDay()]} ` : '';
  return sprache() === 'de'
    ? `${tagName}${zwei(d.getDate())}.${zwei(d.getMonth() + 1)}.`
    : `${tagName}${d.getDate()} ${MONATE[d.getMonth()]}`;
}

/** Zahl mit `stellen` Nachkommastellen; null → „–“. */
export function zahl(v, stellen = 0) {
  if (v == null || Number.isNaN(v)) return '–';
  return Number(v).toLocaleString(sprache(), { minimumFractionDigits: stellen, maximumFractionDigits: stellen });
}

/** Sekunden seit 1970 → „Heute 14:05“, „Gestern 22:31“ oder „Sa 10.10. 09:00“. */
export function zeit(s, jetzt = Date.now()) {
  if (s == null) return '–';
  const d = new Date(s * 1000), h = new Date(jetzt);
  const uhr = `${zwei(d.getHours())}:${zwei(d.getMinutes())}`;
  const tagBeginn = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const abstand = Math.round((tagBeginn(h) - tagBeginn(d)) / 864e5);
  if (abstand === 0) return t('Heute {uhr}', { uhr });
  if (abstand === 1) return t('Gestern {uhr}', { uhr });
  return `${datum(d)} ${uhr}`;
}

/** Nur die Uhrzeit (14:05); null → „–“. */
export function uhr(s) {
  if (s == null) return '–';
  const d = new Date(s * 1000);
  return `${zwei(d.getHours())}:${zwei(d.getMinutes())}`;
}

/** Tag als Überschrift („Heute“, „Gestern“, „Sa 10.10.“). */
export function tag(s, jetzt = Date.now()) {
  return zeit(s, jetzt).replace(/ \d\d:\d\d$/, '');
}

/** „vor 32 min“, „vor 3 h“, „vor 2 Tagen“. */
export function vor(s, jetzt = Date.now()) {
  if (s == null) return '';
  const x = Math.max(0, jetzt / 1000 - s);
  if (x < 90) return t('gerade eben');
  if (x < 5400) return t('vor {n} min', { n: Math.round(x / 60) });
  if (x < 172800) return t('vor {n} h', { n: Math.round(x / 3600) });
  return t('vor {n} Tagen', { n: Math.round(x / 86400) });
}

/** Lage 0…1 → Farbe rot → gelb → grün (nur Variablen der Seite); null → blass. */
export function farbe(lage) {
  if (lage == null) return 'rgba(127,127,127,.12)';
  const x = Math.max(0, Math.min(1, lage));
  return x < 0.5
    ? `color-mix(in srgb, var(--amber) ${Math.round(x * 200)}%, var(--rot))`
    : `color-mix(in srgb, var(--s3) ${Math.round((x - 0.5) * 200)}%, var(--amber))`;
}

/** Punkt-Klasse zur Stufe. */
export function punkt(stufe) {
  return { kritisch: 'rot', warnung: 'amber', info: 'grau', ok: '' }[stufe] ?? 'grau';
}

/** Tageszeit für den Hintergrund aus sun.sun (Höhe und ob sie steigt). */
export function phase(sonne) {
  const a = sonne && sonne.attributes;
  if (!a || a.elevation == null) return 'tag';
  if (a.elevation < -6) return 'nacht';
  if (a.elevation < 6) return a.rising ? 'morgen' : 'abend';
  return 'tag';
}
