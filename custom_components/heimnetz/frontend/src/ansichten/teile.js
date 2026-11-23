// Kleine Bausteine, die mehrere Reiter brauchen.
import { html } from 'lit';
import { farbe } from '../format.js';

/** Umschalter; `liste` = [[wert, text], …]. */
export function seg(liste, wert, wahl, klein = true) {
  return html`<div class="seg ${klein ? 'klein' : ''}" role="group">
    ${liste.map(([k, t]) => html`<button class=${k === wert ? 'on' : ''} aria-pressed=${k === wert ? 'true' : 'false'} @click=${() => wahl(k)}>${t}</button>`)}
  </div>`;
}

/** Kachel der Kopfzeile eines Reiters; ein Knopf nur, wenn sie etwas tut. */
export function kachel(titel, wert, unter, klick) {
  const inhalt = html`<span class="glas-klein">${titel}</span><span class="glas-wert">${wert}</span><span class="glas-kwk">${unter}</span>`;
  return klick ? html`<button class="glas-k glas-panel" @click=${klick}>${inhalt}</button>` : html`<div class="glas-k glas-panel">${inhalt}</div>`;
}

/** Tastatur für Klickflächen, die kein Knopf sind (role="button", tabindex="0"): Enter und Leertaste lösen `los` aus.
 *  Nur auf der Fläche selbst – ein Knopf darin bedient sich selbst. */
export const taste = (los) => (e) => {
  if ((e.key === 'Enter' || e.key === ' ') && e.target === e.currentTarget) {
    e.preventDefault();
    los(e);
  }
};

/** Streifen online/offline (Felder an/aus/luecke). */
export function streifen(felder) {
  const breite = 100 / Math.max(1, felder.length);
  return html`<span class="streifen">${felder.map((f) => html`<i class=${f} style="width:${breite}%"></i>`)}</span>`;
}

/** Pegel mit Marke auf einer Bahn rot → grün; `lage` 0…1 von der Integration. */
export function pegel(titel, wert, einheit, lage) {
  return html`<div class="pegel">
    <div class="mw"><span class="leise">${titel}</span><span class="glas-wert">${wert ?? '–'}<small> ${einheit}</small></span></div>
    <div class="pegel-bahn">${lage == null ? '' : html`<b style="left:${Math.round(lage * 100)}%"></b>`}</div>
  </div>`;
}

export { farbe };
