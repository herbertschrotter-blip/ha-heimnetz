// Kleine Bausteine, die mehrere Reiter brauchen.
import { html } from 'lit';
import { farbe } from '../format.js';

/** Umschalter; `liste` = [[wert, text], …]. */
export function seg(liste, wert, wahl, klein = true) {
  return html`<div class="seg ${klein ? 'klein' : ''}">
    ${liste.map(([k, t]) => html`<button class=${k === wert ? 'on' : ''} @click=${() => wahl(k)}>${t}</button>`)}
  </div>`;
}

/** Kachel der Kopfzeile eines Reiters. */
export function kachel(titel, wert, unter, klick) {
  return html`<button class="glas-k glas-panel" @click=${klick || (() => {})}>
    <span class="glas-klein">${titel}</span><span class="glas-wert">${wert}</span><span class="glas-kwk">${unter}</span>
  </button>`;
}

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
