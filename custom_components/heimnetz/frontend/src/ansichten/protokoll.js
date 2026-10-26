// Reiter „Protokoll“: Journal oder Protokoll der Box (Internet, WLAN, System), nach Tagen; Suche in der Datenbank.
import { html, nothing } from 'lit';
import { zeit, tag, punkt } from '../format.js';
import { merke, t, tl } from '../sprache.js';
import { seg } from './teile.js';

const ARTEN = [['journal', merke('Journal')], ['internet', 'Internet'], ['wlan', merke('WLAN')], ['system', 'System']];

export function protokoll(p, d) {
  const o = p._opt.protokoll;
  const gruppen = [];
  for (const z of d.eintraege) {
    const ueber = z.t == null ? t('ohne Zeit') : tag(z.t);
    if (!gruppen.length || gruppen[gruppen.length - 1][0] !== ueber) gruppen.push([ueber, []]);
    gruppen[gruppen.length - 1][1].push(z);
  }
  const journal = o.art === 'journal';
  return html`<div class="glas-panel block">
    <div class="block-kopf"><h3>${journal ? t('Journal – was hat sich geändert?') : t('Protokoll der FRITZ!Box')}</h3>
      <span class="leise">${journal ? t('aus den Prüfungen dieser Seite') : t('Ereignisse der Box')}</span></div>
    <div class="leiste">${seg(tl(ARTEN), o.art, (v) => p.setze('protokoll', { art: v }), false)}</div>
    <div class="leiste">
      <input class="suche" placeholder=${t('Suchen (Enter)')} .value=${o.suche} @change=${(e) => p.setze('protokoll', { suche: e.target.value })}>
      ${journal ? html`<label class="leise" style="display:flex;gap:6px;align-items:center"><input type="checkbox" .checked=${o.nur_warnungen}
        @change=${(e) => p.setze('protokoll', { nur_warnungen: e.target.checked })}> ${t('nur Warnungen')}</label>` : nothing}
    </div>
    ${gruppen.length ? gruppen.map(([ueber, zeilen]) => html`<div class="gruppe">${ueber}</div>
      ${zeilen.map((z) => html`<div class="ereig"><span class="punkt ${journal ? punkt(z.stufe) : 'grau'}"></span>
        <time>${z.t == null ? z.roh_zeit : zeit(z.t).split(' ').slice(-1)[0]}</time><span>${z.text}</span></div>`)}`)
      : html`<div class="leer">${t('Keine Einträge.')}</div>`}
  </div>`;
}
