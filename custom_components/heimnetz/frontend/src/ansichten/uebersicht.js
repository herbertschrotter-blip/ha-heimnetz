// Reiter „Übersicht“ – Lagebild (1.1, abgenommen 20.11.2026, Mockup mockups/seiten/uebersicht.html 0.3): schlanke
// Kopfzeile, Leitung Pi → FRITZ!Box → Zugang → Internet, Punktfeld der Geräte mit „🗺️ Netzkarte ›“, Mini-Kacheln Heute
// und Wächter, Meldezeile; Befunde, Prüfungen und wichtige Ereignisse im Fenster „Befunde und Ereignisse“.
// Zustände, Texte und die wichtigste Meldung liefert die Integration (heimnetz/uebersicht → kopf, leitung, meldung,
// waechter); die Seite zeichnet nur.
import { html, nothing } from 'lit';
import { zahl, zeit, vor, punkt } from '../format.js';
import { t } from '../sprache.js';

const standZeit = (s) => zeit(s).replace(new RegExp(`^${t('Heute {uhr}', { uhr: '' })}`), '');

const ZIEL = { pi: 'geraete', box: 'geraete', zugang: 'internet', internet: 'protokoll' };
const SYMBOL = { pi: '🍓', box: '🛜', internet: '🌐' };

/** Zu einem Reiter; Geräte immer mit der Liste (die Karte bleibt sonst als gewählter Teil stehen). */
function gehe(p, reiter) {
  if (reiter === 'geraete') p.setze('geraete', { teil: 'geraete' }, false);
  p.geh(reiter);
}

const balken = (n) => html`<span class="lb-balken">${[1, 2, 3, 4].map((i) => html`<i class=${i <= n ? 'an' : ''}></i>`)}</span>`;

function leitung(p, u) {
  const l = u.leitung;
  if (!l) return nothing;
  const s = u.speedtest;
  const inetWeg = l.knoten[3].zustand === 'weg';
  return html`<div class="glas-panel lb-leitung">
    <div class="lb-draht">${l.draehte.map((d) => html`<i class=${d}></i>`)}</div>
    <div class="lb-reihe">${l.knoten.map((k) => html`
      <button class="lb-knoten ${k.zustand}" @click=${() => gehe(p, ZIEL[k.teil])}>
        <span class="rund">${k.symbol || SYMBOL[k.teil]}</span><b>${k.name}</b><small>${k.text}${k.balken != null ? balken(k.balken) : nothing}</small>
      </button>`)}</div>
    ${inetWeg
      ? html`<div class="lb-tempo"><span class="rot-t">${t('Die FRITZ!Box antwortet, das Internet nicht.')}</span></div>`
      : s && s.down != null
        ? html`<button class="lb-tempo" @click=${() => p.geh('speedtest')}><span>↓ <b>${zahl(s.down)}</b> Mbit/s</span><span>↑ <b>${zahl(s.up)}</b></span><span><b>${zahl(s.ping)}</b> ms</span><span class="leise">${vor(s.t)}</span></button>`
        : nothing}
  </div>`;
}

function punktfeld(p, u) {
  const g = u.geraete || {};
  const aus = !u.box_erreichbar;
  const online = aus ? 0 : g.online || 0;
  const neu = aus ? 0 : g.neu || 0;
  const wackelt = aus ? 0 : g.wackelt || 0;
  const punkte = [];
  for (let i = 0; i < (g.bekannt || 0); i++) punkte.push(i < online - wackelt - neu ? 'an' : i < online - neu ? 'wa' : i < online ? 'neu' : '');
  return html`<div class="glas-panel lb-punktfeld" @click=${() => gehe(p, 'geraete')}>
    <div class="lb-pf-kopf"><span class="lb-pf-zahl">${aus ? '–' : online}<small> / ${t('{n} Geräte online', { n: g.bekannt || 0 })}</small></span>
      <span class="leise">${wackelt ? html`<span class="amber">● ${t('{n} wackelt', { n: wackelt })}</span>` : t('alles ruhig')}${neu ? html` · <span class="blau">● ${t('{n} neu', { n: neu })}</span>` : nothing}</span></div>
    <div class="lb-pf-punkte">${punkte.map((c) => html`<i class=${c}></i>`)}</div>
    <div class="lb-pf-fuss"><span class="leise">${t('Tippen: Geräteliste')}</span>
      <button class="chip glas-panel" @click=${(e) => { e.stopPropagation(); p.setze('geraete', { teil: 'karte' }, false); p.geh('geraete'); }}>🗺️ ${t('Netzkarte ›')}</button></div>
  </div>`;
}

function mini(p, u) {
  const h = u.verbrauch_heute;
  const w = u.waechter || {};
  return html`<div class="lb-mini">
    <button class="glas-k glas-panel" @click=${() => p.geh('verbrauch')}><span class="glas-klein">${t('Heute')}</span>
      <span class="glas-wert">${h ? html`${zahl(h.down + h.up, 1)}<small> GB</small>` : '–'}</span>
      <span class="glas-kwk">${h ? `↓ ${zahl(h.down, 1)} · ↑ ${zahl(h.up, 1)}` : t('keine Zählerdaten')}</span></button>
    <button class="glas-k glas-panel" @click=${() => p.geh('waechter')}><span class="glas-klein">🛡️ ${t('Wächter')}</span>
      <span class="glas-wert lb-wort"><span class="punkt ${w.punkt === 'ok' ? '' : w.punkt || 'grau'}"></span>${w.wort || '–'}</span>
      <span class="glas-kwk">${w.text || ''}${w.t ? ` ${vor(w.t)}` : ''}</span></button>
  </div>`;
}

function meldezeile(p, u) {
  const m = u.meldung;
  if (!m) return nothing;
  return html`<button class="glas-panel lb-meldezeile" @click=${() => p.befundeOeffnen()}>
    <span class="anzahl ${m.art}">${m.n}</span>
    <span class="text"><b>${m.titel}</b><span>${m.t ? `${t('zuletzt:')} ${m.text} · ${zeit(m.t)}` : m.text}</span></span>
    <span class="leise">›</span></button>`;
}

export function uebersicht(p, u) {
  const k = u.kopf || { punkt: 'grau', titel: '' };
  return html`<div class="lb">
    <div class="lb-kopf"><span class="lb-titel"><span class="punkt ${k.punkt}"></span>${k.titel}</span>
      <span class="lb-stand">${t('Stand {zeit}', { zeit: standZeit(u.stand) })}
        <button class="chip glas-panel" title=${t('Einstellungen')} @click=${() => p.einstellungenOeffnen()}>⚙</button></span></div>
    ${(u.fehler || []).length ? html`<p class="fein">${t('Abfrage unvollständig: {fehler}', { fehler: u.fehler.join(' · ') })}</p>` : nothing}
    ${leitung(p, u)}${punktfeld(p, u)}${mini(p, u)}${meldezeile(p, u)}
  </div>`;
}

/** Fenster „Befunde und Ereignisse“ (Tipp auf die Meldezeile). */
export function befundeBlatt(p) {
  const u = p._daten.uebersicht || {};
  const befunde = u.befunde || [];
  return html`<div class="griff"></div><button class="zu" @click=${() => p.zu()}>✕</button>
    <h3>${t('Befunde und Ereignisse')}</h3><div class="leise">${t('{n} offen', { n: befunde.length })} · ${t('aus den Prüfungen jede Minute')}</div>
    <div class="gruppe">${t('Befunde')}</div>
    ${befunde.length
      ? befunde.map((b) => html`<div class="befund"><span class="punkt ${punkt(b.stufe)}"></span><div><b>${b.titel}</b><p>${b.text}</p></div></div>`)
      : html`<div class="leer">${t('Im Moment nichts Auffälliges.')}</div>`}
    <div class="gruppe">${t('Prüfungen')}</div>
    ${(u.pruefungen || []).map((x) => html`<div class="zeile">
      <span style="display:flex;gap:10px;align-items:center"><span class="punkt ${x.ok === true ? '' : x.ok === false ? 'rot' : 'grau'}"></span>${x.name}</span>
      <span class="leise" style="text-align:right">${x.wert}</span></div>`)}
    <div class="gruppe">${t('Wichtige Ereignisse')}</div>
    ${(u.wichtig || []).length
      ? u.wichtig.map((z) => html`<div class="ereig"><span class="punkt ${punkt(z.stufe)}"></span><time>${zeit(z.t)}</time><span>${z.text}</span></div>`)
      : html`<div class="leer">${t('Noch keine.')}</div>`}
    <div class="leiste" style="margin-top:6px"><button class="knopf" @click=${() => { p.zu(); p.geh('protokoll'); }}>${t('ganzes Journal ›')}</button></div>`;
}
