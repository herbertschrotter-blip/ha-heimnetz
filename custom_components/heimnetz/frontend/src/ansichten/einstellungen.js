// Fenster „Einstellungen“ (⚙ im Kopf): alles Einstellbare an einem Ort – Speedtest-Auswertung, Messplan, WLAN,
// Meldungen. Seit AN-0002 (Mockup netzwerk.html · Einstellungen gruppiert, Variante B, 13.10.2026) mit Reitern oben,
// darunter nur die gewählte Gruppe in einer Karte. Werte und Zustand kommen von der Integration.
import { html, nothing } from 'lit';
import { live } from 'lit/directives/live.js';
import { uhr, zahl, zeit } from '../format.js';
import { merke, t, tl } from '../sprache.js';
import { seg } from './teile.js';
import { meldungenZeile } from './melden.js';

const MODI = [['aus', merke('weglassen')], ['halb', '¼'], ['mit', merke('voll')]];
const TAKTE = [[1, '1 h'], [2, '2 h'], [4, '4 h'], [6, '6 h'], [12, '12 h'], [24, '24 h']];
const VERKEHR = [['warten', merke('verschieben')], ['messen', merke('messen')]];
const SERIE = [[2, '2'], [3, '3'], [4, '4'], [5, '5']];
const SCHWACH = [[30, '30 %'], [40, '40 %'], [50, '50 %']];

export const TEILE = [['speed', '📈 Speedtest'], ['plan', merke('⏱️ Messplan')], ['wlan', merke('📶 WLAN')], ['meld', merke('💬 Meldungen')]];

export function einstellungenBlatt(p) {
  const e = p._daten.einstellungen;
  const teil = p._blatt.teil || 'speed';
  const kopf = html`<div class="griff"></div><button class="zu" @click=${() => p.zu()}>✕</button>
    <h3>${t('Einstellungen')}</h3><div class="leise">${p.istAdmin ? t('gelten für die ganze Seite') : t('nur Admins ändern')}</div>
    <div class="seg e-reiter">${TEILE.map(([k, name]) => html`<button class=${k === teil ? 'on' : ''} @click=${() => { p._blatt = { ...p._blatt, teil: k }; }}>${t(name)}</button>`)}</div>`;
  if (!e) return html`${kopf}<div class="leer">${t('lädt …')}</div>`;
  const inhalt = { speed: auswertung, plan: messplan, wlan, meld: (q) => meldungenZeile(q) }[teil](p, e);
  return html`${kopf}<div class="ek"><div class="ek-inhalt">${inhalt}</div></div>`;
}

/** Eingabe mit Einheit im ruhigen Feld-Stil der Seite. */
function feld(name, wert, einheit, admin, typ = 'number') {
  return html`<label class="ein"><input name=${name} type=${typ} min="0" step="1" .value=${wert ?? ''} ?disabled=${!admin}>${einheit ? html`<small>${einheit}</small>` : nothing}</label>`;
}

function auswertung(p, e) {
  const admin = p.istAdmin;
  const speichern = (ev) => {
    const f = ev.target.closest('.sheet');
    p.einstellungenSpeichern({
      tarif_down: f.querySelector('[name=tarif_down]').value || null,
      tarif_up: f.querySelector('[name=tarif_up]').value || null,
      ab: f.querySelector('[name=ab]').value || null,
    });
  };
  return html`
    <div class="ez"><span>${t('Tarif Download')}</span>${feld('tarif_down', e.tarif_down, 'Mbit/s', admin)}</div>
    <div class="ez"><span>${t('Tarif Upload')}</span>${feld('tarif_up', e.tarif_up, 'Mbit/s', admin)}</div>
    <div class="ez"><span>${t('Auswerten ab')}<small>${t('ältere Messungen zählen nicht')}</small></span>${feld('ab', e.ab, '', admin, 'date')}</div>
    ${admin ? html`<div class="leiste" style="justify-content:flex-end;padding:4px 0"><button class="knopf haupt" @click=${speichern}>${t('Speichern')}</button></div>` : nothing}
    ${p._hinweis ? html`<p class="fein">${p._hinweis}</p>` : nothing}
    <div class="ez"><span>${t('Belastete Messungen')}<small>${t('über {n} Mbit/s Verkehr vor der Messung', { n: zahl(e.schwelle) })}</small></span>${seg(tl(MODI), p._opt.speedtest.grundlast, (v) => p.setze('speedtest', { grundlast: v }, p._reiter === 'speedtest'))}</div>
    <p class="hinweis">${t('Die Auswahl „belastete Messungen“ gilt für das Wochenraster auf diesem Gerät.')}</p>`;
}

function messplan(p, e) {
  if (!e.messplan) return nothing;
  const m = e.messplan, z = e.plan, o = e.ookla, admin = p.istAdmin;
  const setzen = (werte) => p.messplanSetzen(werte);
  const belastet = e.verkehr_mbit != null && e.verkehr_mbit > e.schwelle;
  const naechste = !m.an ? `– (${t('aus')})`
    : z.misst ? t('misst gerade …')
    : z.wartet ? t('verschoben – neuer Versuch {uhr}', { uhr: uhr(z.neuer_versuch) })
    : z.naechste ? zeit(z.naechste) : '–';
  return html`<p class="hinweis" style="margin:2px 0 4px">${t('Gemessen wird von der Ookla-Integration; dieser Plan sagt ihr, wann.')}</p>
    ${!o.vorhanden ? html`<div class="befund"><span class="punkt rot"></span><div><b>${t('Ookla-Integration fehlt')}</b><p>${t('Ohne sie kann der Plan nicht messen.')}</p></div></div>` : nothing}
    ${o.misst_selbst ? html`<div class="befund"><span class="punkt amber"></span><div><b>${t('Ookla misst zusätzlich nach eigenem Takt')}</b><p>${t('In den Ookla-Einstellungen ist „manuell“ aus – dann misst Ookla neben diesem Plan. Für einen einzigen Plan dort „manuell“ einschalten.')}</p></div></div>` : nothing}
    <div class="ez"><span>${t('Automatisch messen')}</span><button class="sw ${m.an ? 'on' : ''}" role="switch" aria-checked=${m.an ? 'true' : 'false'} ?disabled=${!admin} @click=${() => setzen({ an: !m.an })}><i></i></button></div>
    <div class="ez"><span>${t('Wie oft')}</span>${admin ? seg(TAKTE, m.takt_h, (v) => setzen({ takt_h: v })) : html`<span class="leise">${t('alle {n} h', { n: m.takt_h })}</span>`}</div>
    ${volumen(e.volumen)}
    <div class="ez"><span>${t('Nur zwischen')}</span><span>
      <label class="ein"><input type="time" .value=${live(m.von === '24:00' ? '00:00' : m.von)} ?disabled=${!admin} @change=${(ev) => setzen({ von: ev.target.value || '00:00' })}></label> –
      <label class="ein"><input type="time" .value=${live(m.bis === '24:00' ? '00:00' : m.bis)} ?disabled=${!admin} @change=${(ev) => setzen({ bis: ev.target.value === '00:00' ? '24:00' : ev.target.value || '24:00' })}></label></span></div>
    <div class="ez"><span>${t('Bei Verkehr im Heimnetz')}<small>${t('über {n} Mbit/s', { n: zahl(e.schwelle) })}</small></span>${admin ? seg(tl(VERKEHR), m.verkehr, (v) => setzen({ verkehr: v })) : html`<span class="leise">${m.verkehr === 'warten' ? t('verschieben') : t('trotzdem messen')}</span>`}</div>
    <div class="ez"><span>${t('Serie „{n}× messen“', { n: m.serie })}<small>${t('Durchläufe hintereinander, Ergebnis als Median')}</small></span>${admin ? seg(SERIE, m.serie, (v) => setzen({ serie: v })) : html`<span class="leise">${m.serie}×</span>`}</div>
    <div class="ez"><span>${t('Server der Serie')}<small>${t('alle Ookla-Tests reihum')}${o.server ? ` – ${o.server}` : ''}</small></span><span class="leise">${o.tests ?? 0} ${o.tests === 1 ? 'Test' : 'Tests'}</span></div>
    <div class="ez"><span>${t('Verkehr gerade')}</span><span class=${belastet ? 'rot-t' : 'leise'}>${e.verkehr_mbit == null ? '–' : `${zahl(e.verkehr_mbit, 1)} Mbit/s – ${belastet ? t('belastet') : t('ruhig')}`}</span></div>
    <div class="ez"><span>${t('Nächste Messung')}</span><span class="leise">${naechste}</span></div>
    <div class="ez"><span>${t('Server und „manuell“')}<small>${t('in Ookla eingestellt')}</small></span><button class="blau" @click=${() => { p.zu(); p.oeffne('/config/integrations/integration/ookla_speedtest'); }}>Ookla ›</button></div>
    ${p._hinweisPlan ? html`<p class="fein">${p._hinweisPlan}</p>` : nothing}
    <p class="hinweis">${t('Wird verschoben, versucht es der Plan alle 5 Minuten neu, höchstens 30 Minuten lang; danach misst er trotzdem und die Messung gilt als belastet.')}</p>`;
}

/** WU-0006: Datenvolumen der Messungen – geschätzt rechnet die Integration (letzte Messung, sonst Tarif), hier nur
 *  der Satz dazu. Ohne Werte der allgemeine Hinweis. */
function volumen(v) {
  if (!v) return nothing;
  const text = v.je_test_mb == null
    ? t('Jede Messung kostet Datenvolumen – bei schnellen Anschlüssen einige hundert MB. Bei Mobilfunk mit Datenlimit lieber selten messen.')
    : v.tests_tag
      ? t('Jede Messung kostet etwa {mb} MB Datenvolumen; mit diesem Plan {n} Messungen am Tag, rund {tag} MB am Tag und {monat} GB im Monat. Bei Mobilfunk mit Datenlimit lieber selten messen.',
        { mb: zahl(v.je_test_mb), n: v.tests_tag, tag: zahl(v.tag_mb), monat: zahl(v.monat_gb, 1) })
      : t('Jede Messung kostet etwa {mb} MB Datenvolumen.', { mb: zahl(v.je_test_mb) });
  return html`<p class="hinweis volumen" style="margin:0 0 4px">${text}</p>`;
}

function wlan(p, e) {
  const admin = p.istAdmin;
  return html`
    <div class="ez"><span>${t('Schwacher Empfang unter')}<small>${t('so meldet die Box den Empfang je Gerät')}</small></span>${admin
      ? seg(SCHWACH, e.wlan_schwach, (v) => p.einstellungenSpeichern({ wlan_schwach: v }))
      : html`<span class="leise">${e.wlan_schwach} %</span>`}</div>
    <p class="hinweis">${t('Kanal, Gast-WLAN und Bänder stellst du in der FRITZ!Box ein – die Seite ändert dort nichts.')}</p>`;
}
