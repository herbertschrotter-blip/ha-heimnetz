// Reiter „Funk“: Umschalter WLAN / Mobilfunk (sechs Reiter bleiben; Mockup Funk und Einstellungen, 12.10.2026).
import { html } from 'lit';
import { merke, t, tl } from '../sprache.js';
import { seg } from './teile.js';
import { wlan } from './wlan.js';
import { mobilfunk } from './mobilfunk.js';

export const TEILE = [['wlan', merke('WLAN')], ['mobilfunk', merke('Mobilfunk')]];

export function funk(p, d) {
  const teil = p._opt.funk.teil;
  return html`<div class="leiste">${seg(tl(TEILE), teil, (v) => p.setze('funk', { teil: v }), false)}</div>
    ${d ? (teil === 'wlan' ? wlan(p, d) : mobilfunk(p, d)) : html`<div class="glas-panel block"><div class="leer">${t('lädt …')}</div></div>`}`;
}
