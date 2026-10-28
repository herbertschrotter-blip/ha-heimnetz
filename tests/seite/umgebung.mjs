// Browser-Umgebung für die Seitentests (happy-dom) und ein nachgebautes hass, dessen callWS die Vorlage
// tests/seite/daten.json liefert – dieselbe Form, die die Integration sendet (tests/integration/test_vertrag_seite.py).
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const hier = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(hier, '../../custom_components/heimnetz/frontend/package.json'));
const { Window } = require('happy-dom');

const fenster = new Window({ url: 'http://localhost:8123/heimnetz' });
for (const name of ['window', 'document', 'Document', 'customElements', 'HTMLElement', 'HTMLTemplateElement', 'HTMLStyleElement', 'Element', 'Node', 'Event', 'CustomEvent',
  'ShadowRoot', 'CSSStyleSheet', 'sessionStorage', 'localStorage', 'MutationObserver', 'DocumentFragment', 'Text', 'Comment', 'TreeWalker', 'NodeFilter']) {
  globalThis[name] = fenster[name];
}
globalThis.requestAnimationFrame = (f) => setTimeout(f, 0);
globalThis.getComputedStyle = (el) => fenster.getComputedStyle(el);  // Farben der Karte aus den Variablen der Seite

export const DATEN = JSON.parse(readFileSync(join(hier, 'daten.json'), 'utf8'));
export const QUELLE = join(hier, '../../custom_components/heimnetz/frontend/src');

/** hass mit callWS aus der Vorlage; `aufrufe` sammelt jede Nachricht. `sprache` = Sprache des Nutzers in HA. */
export function machHass({ admin = true, dunkel = true, sprache = 'de' } = {}) {
  const aufrufe = [];
  let bilder = 0;
  let zugang = null; // WU-0009: zuletzt gespeicherter Zugang (wie in der Integration)
  let arten = DATEN.arten, warnungen = DATEN.warnungen; // WU-0010: Stand nach dem letzten Speichern
  return {
    aufrufe,
    language: sprache,
    locale: { language: sprache, number_format: 'language', time_format: 'language' },
    user: { is_admin: admin },
    themes: { darkMode: dunkel },
    states: { 'sun.sun': { state: 'above_horizon', attributes: { elevation: 30, rising: true } } },
    async callWS(msg) {
      aufrufe.push(msg);
      const befehl = msg.type.replace('heimnetz/', '');
      if (befehl === 'einstellungen/setzen') return { ...DATEN.einstellungen, ...msg, type: undefined };
      if (befehl === 'messplan/setzen') return { ...DATEN.einstellungen, messplan: { ...DATEN.einstellungen.messplan, ...msg, type: undefined, id: undefined } };
      if (befehl === 'messen') return { ...DATEN.einstellungen, plan: { ...DATEN.einstellungen.plan, misst: true } };
      if (befehl === 'meldungen') return MELDUNGEN;
      if (befehl === 'serie') return { ...DATEN.einstellungen, serie: { n: DATEN.einstellungen.messplan.serie, lauf: 1 } };
      if (befehl === 'geraet/art') return { ...DATEN.geraet, kat: msg.art || DATEN.geraet.kat, art_selbst: !!msg.art, art_quelle: msg.art ? 'selbst gewählt' : DATEN.geraet.art_quelle };
      if (befehl === 'meldung/neu') return { id: 'm1', ticket: msg.meldung.art === 'wunsch' ? 'WU-0001' : 'FE-0003' };
      if (befehl === 'meldung/github') return githubVorschau('FE-0003', msg.zelle);
      if (befehl === 'meldung/bild') { if (msg.bild.includes('kaputt')) throw new Error('bild: nur JPEG, PNG oder WebP'); return { ticket: 'FE-0003', bilder: ++bilder }; }
      if (befehl === 'meldung/bild_zeigen') return { url: 'data:image/jpeg;base64,AAAA' };
      if (befehl === 'meldung/status') return { ...MELDUNGEN[0], status: msg.status, offen: msg.status !== 'geschlossen' };
      if (befehl === 'meldung/loeschen') return { ok: true };
      if (befehl === 'modem') return MODEM_ANTWORT(msg);
      if (befehl === 'zugang/setzen') {
        // WU-0009: wie die Integration – das Kennwort kommt nie zurück, nur „hinterlegt“
        const z = zugang ?? DATEN.zugang;
        zugang = { ...z, wahl: msg.wahl ?? z.wahl, adresse: 'adresse' in msg ? msg.adresse : z.adresse, ersatz_wahl: msg.ersatz ?? z.ersatz_wahl,
          kennwort: msg.kennwort_loeschen ? false : !!msg.kennwort || z.kennwort, quelle: (msg.wahl ?? z.wahl) === 'auto' ? 'automatisch' : 'festgelegt' };
        return zugang;
      }
      if (befehl === 'zugang/suchen') return { ...(zugang ?? DATEN.zugang), gesucht: true };
      if (befehl === 'zugang' && zugang) return zugang;
      // WU-0010: eigene Arten und Warnungen wie die Integration (tests/integration/test_warnungen.py)
      if (befehl === 'arten') return arten;
      if (befehl === 'art/neu') {
        if (!msg.name.trim()) throw new Error('Name der Art fehlt');
        const symbol = msg.symbol || '🏷️', name = `eigen:${arten.eigene.length + 2}`;
        arten = { ...arten, eigene: [...arten.eigene, { name, symbol, titel: msg.name, text: `${symbol} ${msg.name}`, geraete: msg.geraet ? 1 : 0 }] };
        return { ...arten, neu: name };
      }
      if (befehl === 'art/aendern') {
        arten = { ...arten, eigene: arten.eigene.map((x) => (x.name === msg.art ? { ...x, symbol: msg.symbol, titel: msg.name, text: `${msg.symbol} ${msg.name}` } : x)) };
        return arten;
      }
      if (befehl === 'art/loeschen') {
        const weg = arten.eigene.find((x) => x.name === msg.art);
        arten = { ...arten, eigene: arten.eigene.filter((x) => x !== weg) };
        return { ...arten, zurueck: weg ? weg.geraete : 0 };
      }
      if (befehl === 'warnungen') return warnungen;
      if (befehl === 'warnungen/setzen') {
        if (msg.verzoegerung != null && !warnungen.verzoegerungen.includes(msg.verzoegerung)) throw new Error('Offline melden nach: 2, 5, 15, 60 Minuten');
        const { type, id, sprache: _s, art, an, ...rest } = msg;
        warnungen = { ...warnungen, ...rest, arten: art ? warnungen.arten.map((a) => (a.name === art ? { ...a, an } : a)) : warnungen.arten };
        return warnungen;
      }
      if (befehl === 'warnungen/geraet') {
        warnungen = { ...warnungen, ausnahmen: msg.wert === 'gruppe' ? warnungen.ausnahmen.filter((x) => x.id !== msg.geraet) : warnungen.ausnahmen };
        return { ...DATEN.geraet, warnen: { ...DATEN.geraet.warnen, wert: msg.wert } };
      }
      if (befehl === 'warnungen/test') return { dienste: warnungen.ziel === 'keine' ? [] : warnungen.ziel === 'alle' ? ['mobile_app_handy'] : [warnungen.ziel] };
      if (!(befehl in DATEN)) throw new Error(`unbekannt: ${msg.type}`);
      return DATEN[befehl];
    },
  };
}

/** Antwort von heimnetz/modem (WU-0008; tests/integration/test_modem.py prüft dieselbe Form). Seit WU-0009 Stufe 2
 *  mit erkanntem Gerät (`erkannt`), Befund fertig formuliert (`hinweis`) und umgerechneten Werten. */
const ZTE = { name: 'ZTE G5TC (goform)', hersteller: 'ZTE', schnittstelle: 'goform', baustein: 'zte_goform', werte: true };
export function MODEM_ANTWORT(msg) {
  if (!/^(192\.168|10\.|172\.(1[6-9]|2\d|3[01]))/.test((msg.adresse || '').trim())) {
    return {
      modell: '', erkannt: null, abfragen: [], summen: { ok: 0, gesamt: 0, werte: 0, geschwaerzt: 0 }, befund: 'adresse_nicht_erlaubt',
      hinweis: { kennung: 'adresse_nicht_erlaubt', lage: 'amber', titel: 'Adresse nicht erlaubt', text: 'Die Adresse liegt nicht im eigenen Heimnetz.' },
      umgerechnet: null, daten: {},
    };
  }
  if (msg.kennwort === 'falsch') {
    return {
      modell: 'ZTE G5TC',
      abfragen: [{ name: 'Startseite', status: 'ok', angabe: 'ZTE G5TC erkannt' }, { name: 'Werte ohne Anmeldung', status: 'ok', angabe: '12 Werte' }, { name: 'Anmeldung', status: 'fehler', angabe: 'abgelehnt' }],
      summen: { ok: 2, gesamt: 3, werte: 12, geschwaerzt: 2 }, befund: 'anmeldung_abgelehnt', erkannt: ZTE, umgerechnet: null,
      hinweis: { kennung: 'anmeldung_abgelehnt', lage: 'rot', titel: 'Anmeldung abgelehnt', text: 'Das Gerät lehnt das Kennwort ab.' },
      daten: { ohne_anmeldung: { modem_model: 'ZTE G5TC', imei: '⟨geschwärzt⟩' } },
    };
  }
  return {
    modell: 'ZTE G5TC',
    abfragen: [
      { name: 'Startseite', status: 'ok', angabe: 'ZTE G5TC erkannt' },
      { name: 'Werte ohne Anmeldung', status: 'ok', angabe: '12 Werte' },
      { name: 'Anmeldung', status: 'ok', angabe: 'angenommen' },
      { name: 'Werte nach Anmeldung', status: 'ok', angabe: '186 Werte' },
      { name: 'zweite Schnittstelle (ubus)', status: 'aus', angabe: 'nicht vorhanden' },
    ],
    summen: { ok: 4, gesamt: 5, werte: 198, geschwaerzt: 11 }, befund: null, hinweis: null, erkannt: ZTE,
    umgerechnet: { netz: '5G-NSA', rsrp: -97, sinr: 8 },
    daten: { nach_anmeldung: { modem_model: 'ZTE G5TC', cell_id: '1A2B3C4', lte_pci: '301', imei: '⟨geschwärzt⟩', iccid: '⟨geschwärzt⟩' } },
  };
}

/** Vorschau in der Form von heimnetz/meldung/github (tests/integration/test_github.py prüft dieselbe Form). */
export function githubVorschau(ticket, zelle = false) {
  const text = `Karte grau\n\n### Umgebung\n- Heimnetz 0.23.0 · Home Assistant 2026.10.2\n- Lokales Ticket: ${ticket}${zelle ? '\n\n### Zell- und Signaldaten\n- Ankerzelle: abcde-0b' : ''}`;
  return { ticket, titel: '[Fehler] Karte grau', text, url: `https://github.com/x/ha-heimnetz/issues/new?title=t&body=${encodeURIComponent(text)}`, gekuerzt: false, zelle: !!zelle, zelle_da: true };
}

/** Tickets in der Form von heimnetz/meldungen (tests/integration/test_tickets.py prüft dieselbe Form). */
export const MELDUNGEN = [
  { id: 'a1', ticket: 'FE-0002', art: 'fehler', status: 'neu', zeit: '2026-10-13T19:42:00+02:00', text: 'Karte bleibt grau', kontext: 'Funk · Mobilfunk',
    geraet: 'Handy', version: '0.9.0', bilder: ['FE-0002-1.jpg'], verlauf: [], seite: { reiter: 'funk' }, stand: null, offen: true, art_text: 'Fehler', status_text: 'neu' },
  { id: 'b2', ticket: 'FE-0001', art: 'fehler', status: 'geschlossen', zeit: '2026-10-12T21:10:00+02:00', text: 'Tablet offline', kontext: 'Geräte',
    geraet: 'Desktop', version: '0.7.0', bilder: [], verlauf: [{ zeit: '2026-10-13T08:00:00+02:00', von: 'Claude', status: 'geschlossen', version: '0.7.1', commit: '3f2a9c1', notiz: 'Abgleich korrigiert' }], stand: '2026-10-13T08:00:00+02:00', offen: false, art_text: 'Fehler', status_text: 'geschlossen' },
];

export const warten = (ms = 0) => new Promise((r) => setTimeout(r, ms));

export async function seite(hass) {
  const el = document.createElement('heimnetz-panel');
  el.hass = hass;
  el.narrow = false;
  document.body.appendChild(el);
  await warten(10);
  await el.updateComplete;
  return el;
}

export const text = (el) => el.shadowRoot.textContent.replace(/\s+/g, ' ');
