// Reiter „Funk“ · WLAN (Mockup netzwerk.html · Funk und Einstellungen): Befunde, Bänder, Geräte schwächstes zuerst,
// Kanalwechsel. Lagen (0…1) und Befundtexte kommen fertig von der Integration.
import { html, nothing } from 'lit';
import { farbe, punkt, zeit } from '../format.js';
import { t } from '../sprache.js';
import { kachel } from './teile.js';

export function wlan(p, d) {
  if (!d.verfuegbar) return html`<div class="glas-panel block"><div class="leer">${t('Die Box meldet gerade keine WLAN-Werte.')}</div></div>`;
  const band = (b) => kachel(`${b.band} GHz`, b.an ? t('Kanal {k}', { k: b.kanal ?? '–' }) : t('aus'),
    b.an ? `${b.auto ? t('automatisch') : t('fest')}${b.standard ? ` · Wi-Fi ${standard(b.standard)}` : ''} · ${t(b.geraete === 1 ? '{n} Gerät' : '{n} Geräte', { n: b.geraete })}` : t('abgeschaltet'));
  return html`
    ${d.befunde.length ? html`<div class="glas-panel block">${d.befunde.map((b) => html`<div class="befund"><span class="punkt ${punkt(b.stufe)}"></span>
      <div><b>${b.titel}</b><p>${b.text}</p></div></div>`)}</div>` : nothing}
    <div class="glas-raster">
      ${d.baender.map(band)}
      ${kachel(t('Gast-WLAN'), d.gast_an == null ? '–' : d.gast_an ? t('an') : t('aus'), t('nur lesen'))}
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Geräte im WLAN')}</h3><span class="leise">${t('{n} verbunden · schwächstes zuerst', { n: d.geraete.length })}</span></div>
      ${d.geraete.length ? html`<div class="tab-scroll"><table class="t">
        <tr><th>${t('Gerät')}</th><th>Band</th><th>${t('Empfang')}</th><th class="r">%</th><th class="r">Mbit/s</th></tr>
        ${d.geraete.map((g) => html`<tr class="klick" @click=${() => p.geraetOeffnen(g.id)}>
          <td>${g.name} ${g.schwach ? html`<span class="badge amber-b">${t('schwach')}</span>` : nothing}${g.gast ? html` <span class="badge">${t('Gast')}</span>` : nothing}</td>
          <td>${g.band ? `${g.band} GHz` : '–'}</td>
          <td><span class="sig"><i style="width:${Math.round((g.lage ?? 0) * 100)}%;background:${farbe(g.lage)}"></i></span></td>
          <td class="r">${g.signal ?? '–'}</td><td class="r">${g.mbit ?? '–'}</td></tr>`)}
      </table></div>` : html`<div class="leer">${t('Kein Gerät im WLAN.')}</div>`}
      <p class="hinweis">${t('Empfang und Geschwindigkeit meldet die FRITZ!Box je Gerät; schwach = unter {n} % (⚙). Tippen öffnet den Verlauf des Geräts.', { n: d.schwach_unter })}</p>
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t('Kanalwechsel')}</h3><span class="leise">${t('letzte 7 Tage · die Box wählt selbst')}</span></div>
      ${d.kanalwechsel.length ? d.kanalwechsel.map((k) => html`<div class="ereig"><span class="punkt grau"></span><time>${zeit(k.t)}</time><span>${k.text}</span></div>`)
        : html`<div class="leer">${t('Kein Wechsel in den letzten 7 Tagen.')}</div>`}
    </div>`;
}

function standard(s) {
  return { be: '7', ax: '6', ac: '5', n: '4' }[s] ?? s;
}
