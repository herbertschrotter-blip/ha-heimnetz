// Reiter „Verbrauch“: Kacheln und Balken je Tag (Download, Upload, davon Speedtests).
import { html, svg, nothing } from 'lit';
import { datum, zahl } from '../format.js';
import { t } from '../sprache.js';
import { kachel, seg } from './teile.js';

const W = 600;
const H = 160;

export function verbrauch(p, d) {
  const o = p._opt.verbrauch;
  if (!d.verfuegbar) {
    return html`<div class="glas-panel block"><div class="leer">${t('Keine Zähler von FRITZ!Box Tools gefunden („GB empfangen/gesendet“).')}</div></div>`;
  }
  const k = d.kacheln;
  const tage = d.tage;
  const max = Math.max(0.1, ...tage.map((x) => x.down + x.up)) * 1.1;
  const bw = W / Math.max(1, tage.length);
  const balken = tage.map((x, i) => {
    const h1 = (x.down / max) * H, h2 = (x.up / max) * H, h3 = (x.speedtest / max) * H;
    const d0 = new Date(`${x.tag}T12:00`);
    return svg`<g><title>${datum(d0)}: ↓ ${zahl(x.down, 1)} GB, ↑ ${zahl(x.up, 1)} GB, ${t('davon Speedtests {gb} GB', { gb: zahl(x.speedtest, 2) })}</title>
      <rect x=${i * bw + 1} y=${H - h1} width=${Math.max(1, bw - 2)} height=${h1} rx="2" fill="var(--s1)"></rect>
      <rect x=${i * bw + 1} y=${H - h1 - h2} width=${Math.max(1, bw - 2)} height=${h2} rx="2" fill="var(--s2)"></rect>
      <rect x=${i * bw + 1} y=${H - h3} width=${Math.max(1, bw - 2)} height=${h3} fill="var(--s4)" opacity=".9"></rect></g>`;
  });
  return html`
    ${k ? html`<div class="glas-raster">
      ${kachel(t('Heute'), html`${zahl(k.heute.down + k.heute.up, 1)}<small> GB</small>`, `↓ ${zahl(k.heute.down, 1)} · ↑ ${zahl(k.heute.up, 1)}`)}
      ${kachel(t('Diese Woche'), html`${zahl(k.woche, 1)}<small> GB</small>`, t('seit Montag'))}
      ${kachel(t('Dieser Monat'), html`${zahl(k.monat, 1)}<small> GB</small>`, t('seit dem 1.'))}
      ${kachel(t('Ø je Tag'), html`${zahl(k.schnitt, 1)}<small> GB</small>`, t('letzte {n} Tage', { n: o.tage }))}
      ${kachel(t('Davon Speedtests'), html`${zahl(k.speedtest, 1)}<small> GB</small>`, t('geschätzt'))}
    </div>` : nothing}
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Datenverbrauch der ganzen Box')}</h3>${seg([[7, t('{n} Tage', { n: 7 })], [30, t('{n} Tage', { n: 30 })]], o.tage, (v) => p.setze('verbrauch', { tage: v }))}</div>
      <svg class="dia" viewBox="-30 -6 ${W + 36} ${H + 24}">
        ${[0, 0.25, 0.5, 0.75, 1].map((f) => svg`<line class="gitter" x1="0" x2=${W} y1=${H - f * H} y2=${H - f * H}></line><text x="-4" y=${H - f * H + 3} text-anchor="end">${zahl(f * max)}</text>`)}
        ${balken}
        ${svg`<text x="0" y=${H + 16}>${t('vor {n} Tagen', { n: tage.length - 1 })}</text><text x=${W} y=${H + 16} text-anchor="end">${t('heute')}</text>`}
      </svg>
      <div class="legende"><span><i style="background:var(--s1)"></i>Download</span><span><i style="background:var(--s2)"></i>Upload</span><span><i style="background:var(--s4)"></i>${t('davon Speedtests')}</span><span>${t('GB je Tag')}</span></div>
      <p class="hinweis">${t('Die FRITZ!Box zählt nur gesamt, nicht je Gerät.')}</p>
    </div>`;
}
