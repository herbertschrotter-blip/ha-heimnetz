// Reiter „Übersicht“: Kacheln, Befunde, Prüfungen, wichtige Ereignisse.
import { html, nothing } from 'lit';
import { zahl, zeit, vor, punkt } from '../format.js';
import { t } from '../sprache.js';
import { kachel } from './teile.js';

export function uebersicht(p, u) {
  const aus = !u.box_erreichbar;
  const g = u.geraete || {};
  const e = u.empfang;
  const s = u.speedtest;
  const h = u.verbrauch_heute;
  const kacheln = [
    kachel('Internet', html`<span class=${u.internet.ok ? 'ok' : 'rot-t'}>${u.internet.ok ? t('verbunden') : t('getrennt')}</span>`,
      u.internet.technik || '', () => p.geh('protokoll')),
    kachel(t('Geräte online'), aus ? '–' : html`${g.online}<small> / ${g.bekannt}</small>`,
      aus ? t('nicht verfügbar') : [g.neu ? t('{n} neu', { n: g.neu }) : '', g.wackelt ? t('{n} wackelt', { n: g.wackelt }) : ''].filter(Boolean).join(' · ') || t('alles ruhig'),
      () => p.geh('geraete')),
    kachel(t('Empfang'), e ? html`${e.rsrp_anker ?? '–'}<small> dBm</small>` : '–',
      e ? `${e.wort ?? ''}${e.rsrp_5g != null ? ` · 5G ${e.rsrp_5g} dBm` : ''}` : t('nicht verfügbar'), () => { p.setze('internet', { sicht: 'haupt' }, false); p.geh('internet'); }),
    kachel('Speedtest', s && s.down != null ? html`${zahl(s.down)}<small> Mbit/s</small>` : '–',
      s ? `↑ ${zahl(s.up)} · ${zahl(s.ping)} ms · ${vor(s.t)}` : t('noch keine Messung'), () => p.geh('speedtest')),
    kachel(t('Heute'), h ? html`${zahl(h.down + h.up, 1)}<small> GB</small>` : '–',
      h ? `↓ ${zahl(h.down, 1)} · ↑ ${zahl(h.up, 1)} · ${t('Speedtests {gb}', { gb: zahl(h.speedtest, 1) })}` : t('keine Zählerdaten'), () => p.geh('verbrauch')),
    kachel(t('Befunde'), html`${(u.befunde || []).length}`, t('offen'), () => {}),
  ];
  return html`
    <div class="glas-raster">${kacheln}</div>
    <div class="raster2">
      <div class="glas-panel block">
        <div class="block-kopf"><h3>${t('Befunde')}</h3><span class="leise">${t('{n} offen', { n: (u.befunde || []).length })}</span></div>
        ${(u.befunde || []).length
          ? u.befunde.map((b) => html`<div class="befund"><span class="punkt ${punkt(b.stufe)}"></span><div><b>${b.titel}</b><p>${b.text}</p></div></div>`)
          : html`<div class="leer">${t('Im Moment nichts Auffälliges.')}</div>`}
        ${(u.fehler || []).length ? html`<p class="fein">${t('Abfrage unvollständig: {fehler}', { fehler: u.fehler.join(' · ') })}</p>` : nothing}
      </div>
      <div class="glas-panel block">
        <div class="block-kopf"><h3>${t('Prüfungen')}</h3><span class="leise">${t('jede Minute')}</span></div>
        ${u.pruefungen.map((x) => html`<div class="zeile">
          <span style="display:flex;gap:10px;align-items:center"><span class="punkt ${x.ok === true ? '' : x.ok === false ? 'rot' : 'grau'}"></span>${x.name}</span>
          <span class="leise" style="text-align:right">${x.wert}</span></div>`)}
      </div>
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Wichtige Ereignisse')}</h3><button class="leise blau" @click=${() => p.geh('protokoll')}>${t('ganzes Journal ›')}</button></div>
      ${(u.wichtig || []).length
        ? u.wichtig.map((z) => html`<div class="ereig"><span class="punkt ${punkt(z.stufe)}"></span><time>${zeit(z.t)}</time><span>${z.text}</span></div>`)
        : html`<div class="leer">${t('Noch keine.')}</div>`}
    </div>`;
}
