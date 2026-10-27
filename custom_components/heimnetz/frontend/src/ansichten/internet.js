// Reiter „Internet“ (vorher „Funk“, WU-0009; Mockup netzwerk.html · Internet und Zugang, 27.10.2026): oben woher das
// Internet kommt (erkannt oder in ⚙ › 🌐 Zugang festgelegt), darunter die Werte der Zugangsart – Mobilfunk, DSL,
// Glasfaser, Kabel – und als eigener Umschalter der Ersatzzugang. Erkennen, Bewerten und alle Texte macht die
// Integration (heimnetz/internet); die Seite zeigt nur an. Was die Schnittstelle der Box nicht liefert, steht als „–“.
import { html, svg, nothing } from 'lit';
import { zahl, zeit } from '../format.js';
import { merke, t } from '../sprache.js';
import { seg } from './teile.js';
import { mobilfunk } from './mobilfunk.js';

const SYMBOL = { mobilfunk: '📶', dsl: '☎️', glasfaser: '💡', kabel: '📺', extern: '📶' };
const ABZEICHEN = { gut: 'gruen', knapp: 'amber-b', schlecht: 'rot-b' };
const QUELLE = { automatisch: merke('automatisch erkannt'), festgelegt: merke('festgelegt') };

const lade = () => html`<div class="glas-panel block"><div class="leer">${t('lädt …')}</div></div>`;
const wert = (w, stellen = 1) => (w == null ? '–' : zahl(w, stellen));

/** Kachel ohne Klick (Werte der Leitung). */
function ik(titel, w, unter, cls = '') {
  return html`<div class="glas-k glas-panel ${cls}"><span class="glas-klein">${titel}</span><span class="glas-wert">${w}</span><span class="glas-kwk">${unter}</span></div>`;
}

/** Zeile „Name – Wert“ mit Erklärung darunter. */
function iz(name, w, unter = '') {
  return html`<div class="ez"><span>${name}${unter ? html`<small>${unter}</small>` : nothing}</span><span class="iz-w">${w}</span></div>`;
}

/** Herkunft des Zugangs: „Internet über …“, Gerät und Weg, Abzeichen, „ändern ›“ → ⚙ › 🌐 Zugang. */
export function zugangZeile(p, z) {
  return html`<div class="glas-panel block iq">
    <span class="iq-ic">${SYMBOL[z.art] ?? '🌐'}</span>
    <span><b>${z.titel}</b><small>${[z.geraet, z.weg_text, z.ersatz_text ? t('Ersatz: {text}', { text: z.ersatz_text }) : ''].filter(Boolean).join(' · ')}</small>
      ${z.abweichung ? html`<small class="amber-t">${t('Die FRITZ!Box meldet etwas anderes: {vorschlag}', { vorschlag: z.abweichung })}</small>` : nothing}</span>
    <span class="iq-r"><span class="badge">${t(QUELLE[z.quelle] ?? z.quelle)}</span>
      ${p.istAdmin ? html`<button class="leise blau" @click=${() => p.einstellungenOeffnen('zugang')}>${t('ändern ›')}</button>` : nothing}</span>
  </div>`;
}

export function internet(p, d) {
  if (!d) return lade();
  const z = d.zugang;
  const sicht = p._opt.internet.sicht === 'ersatz' && d.ersatz ? 'ersatz' : 'haupt';
  const knoepfe = [['haupt', `${SYMBOL[z.art] ?? '🌐'} ${art(z)}`], ...(d.ersatz ? [['ersatz', t('📶 Ersatz')]] : [])];
  const inhalt = sicht === 'ersatz' ? ersatz(d.ersatz)
    : z.art === 'dsl' ? dsl(d.dsl)
      : z.art === 'glasfaser' ? glasfaser(d.glasfaser)
        : z.art === 'kabel' ? kabel(d.kabel)
          : z.art === 'extern' ? extern(p)
            : z.art === 'mobilfunk' && d.mobilfunk ? mobilfunk(p, d.mobilfunk)
              : html`<div class="glas-panel block"><div class="leer">${t('Die Box meldet noch nicht, woher das Internet kommt – sie wird alle 10 Minuten gefragt.')}</div></div>`;
  return html`${zugangZeile(p, z)}
    ${knoepfe.length > 1 ? html`<div class="leiste">${seg(knoepfe, sicht, (v) => p.setze('internet', { sicht: v }, false), false)}</div>` : nothing}
    ${inhalt}`;
}

function art(z) {
  return { mobilfunk: t('Mobilfunk'), dsl: 'DSL', glasfaser: t('Glasfaser'), kabel: t('Kabel'), extern: t('Vorgeschaltet') }[z.art] ?? t('Internet');
}

function bewertung(b) {
  const rahmen = b.stufe === 'knapp' ? 'border-color:color-mix(in srgb, var(--amber) 60%, var(--panel-rand))'
    : b.stufe === 'schlecht' ? 'border-color:color-mix(in srgb, var(--rot) 60%, var(--panel-rand))' : '';
  return html`<div class="glas-panel block" style=${rahmen}>
    <div class="block-kopf"><h3>${b.titel}</h3>${b.abzeichen ? html`<span class="badge ${ABZEICHEN[b.stufe] ?? ''}">${b.abzeichen}</span>` : nothing}</div>
    ${b.text ? html`<p class="hinweis" style="font-size:13px">${b.text}</p>` : nothing}</div>`;
}

/** Fehlt ein Wert, weil TR-064 ihn nicht hergibt: „–“ mit kurzem Hinweis. */
const fehlt = (text) => html`<span class="leise" title=${text}>–</span>`;

function dsl(d) {
  if (!d) return html`<div class="glas-panel block"><div class="leer">${t('Die Box meldet gerade keine DSL-Werte.')}</div></div>`;
  const moeglich = (m, tarif) => [m != null ? t('möglich {n}', { n: zahl(m, 1) }) : '', tarif ? t('Tarif {n}', { n: zahl(tarif) }) : ''].filter(Boolean).join(' · ') || t('laut Box');
  return html`${bewertung(d.bewertung)}
    <div class="glas-raster">
      ${ik(t('Synchron Download'), html`${wert(d.sync_down)}<small> Mbit/s</small>`, moeglich(d.max_down, d.tarif_down))}
      ${ik(t('Synchron Upload'), html`${wert(d.sync_up)}<small> Mbit/s</small>`, moeglich(d.max_up, d.tarif_up))}
      ${ik(t('Störabstand ↓ / ↑'), html`${wert(d.marge_down)} / ${wert(d.marge_up)}<small> dB</small>`, t('Marge, gut ab {n} dB', { n: zahl(d.marge_gut) }), ['knapp', 'schlecht'].includes(d.marge_stufe) ? 'amber-k' : '')}
      ${ik(t('Dämpfung ↓ / ↑'), html`${wert(d.daempfung_down)} / ${wert(d.daempfung_up)}<small> dB</small>`, t('laut Box'))}
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t('Leitung')}</h3><span class="leise">${t('laut FRITZ!Box')}</span></div>
      ${iz(t('Status'), d.status)}
      ${iz(t('Verfahren'), d.verfahren ?? fehlt(d.fehlt), t('Vectoring: {text}', { text: d.fehlt }))}
      ${iz(t('Verbunden seit'), d.seit_text ?? '–', d.seit ? t('letzte Neusynchronisierung {zeit}', { zeit: zeit(d.seit) }) : t('seit dem Start von Heimnetz keine Neusynchronisierung gesehen'))}
      ${iz(t('Fehler je Stunde'), d.crc_h == null && d.fec_h == null ? '–' : `CRC ${wert(d.crc_h, 0)} · FEC ${wert(d.fec_h, 0)}`, t('CRC = nicht korrigierbar, FEC = korrigiert'))}
      ${iz(t('Neusynchronisierungen'), t('{n} in 7 Tagen', { n: d.neusync_7 }))}
      ${iz(t('Gegenstelle (DSLAM)'), fehlt(d.fehlt), d.fehlt)}
    </div>
    ${verlauf(t('Verlauf 7 Tage'), t('Synchron-Download und Störabstand'), [
      { punkte: d.verlauf.sync, farbe: 'var(--s1)', name: t('Synchron-Download (Mbit/s)') },
      { punkte: d.verlauf.marge, farbe: 'var(--amber)', name: t('Störabstand Download (dB)') },
    ], d.neusync.map((n) => n.t))}`;
}

function glasfaser(g) {
  if (!g) return html`<div class="glas-panel block"><div class="leer">${t('Die Box meldet gerade keine Glasfaser-Werte.')}</div></div>`;
  // empfangen wie an der Box von oben nach unten (−8 … −28), gesendet von unten nach oben (0,5 … 5)
  const bereich = (b, abwaerts) => (b ? t('gut {von} … {bis}', { von: zahl(b[abwaerts ? 1 : 0], 1), bis: zahl(b[abwaerts ? 0 : 1], 1) }) : t('Bereich meldet die Box nicht'));
  return html`${bewertung(g.bewertung)}
    <div class="glas-raster">
      ${ik(t('Empfangene Lichtleistung'), html`${wert(g.rx)}<small> dBm</small>`, bereich(g.rx_bereich, true), g.bewertung.stufe === 'knapp' || g.bewertung.stufe === 'schlecht' ? 'amber-k' : '')}
      ${ik(t('Gesendete Lichtleistung'), html`${wert(g.tx)}<small> dBm</small>`, bereich(g.tx_bereich, false))}
      ${ik(t('Verbindung'), g.modus ?? '–', g.down_mbit ? `${zahl(g.down_mbit)} / ${zahl(g.up_mbit)} Mbit/s` : t('laut Box'))}
      ${ik(t('Status'), '–', g.fehlt)}
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t('Glasfaser-Anschluss')}</h3><span class="leise">${t('laut FRITZ!Box')}</span></div>
      ${iz(t('Verbunden seit'), g.seit_text ?? '–', g.resyncs != null ? t('{n} Neusynchronisierungen laut Box', { n: g.resyncs }) : '')}
      ${iz(t('Fehler je Stunde'), g.fehler_h == null ? '–' : wert(g.fehler_h, 0), t('fehlerhaft empfangene Pakete'))}
      ${iz(t('Temperatur Modul'), fehlt(g.fehlt), g.fehlt)}
      ${iz(t('Anschluss-Kennung'), html`<span class="amber-t">${t('⟨nur in der Box⟩')}</span>`, t('Seriennummer und Kennung zeigt die Seite nicht'))}
    </div>
    ${verlauf(t('Verlauf 7 Tage'), t('Lichtleistung'), [{ punkte: g.verlauf.rx, farbe: 'var(--s1)', name: t('empfangene Lichtleistung (dBm)') }], [], g.rx_bereich)}
    <p class="hinweis">${t('Mit einem eigenen Glasfaser-Modem (ONT) vor der FRITZ!Box kommen diese Werte vom ONT – das folgt in einer späteren Fassung.')}</p>`;
}

function kabel(k) {
  if (!k) return lade();
  return html`<div class="glas-panel block"><div class="block-kopf"><h3>${k.verbunden === false ? t('Kabelanschluss getrennt') : t('Kabelanschluss verbunden')}</h3>
      <span class="badge ${k.verbunden === false ? 'rot-b' : 'gruen'}">${k.verbunden === false ? t('getrennt') : t('verbunden')}</span></div>
    <p class="hinweis" style="font-size:13px">${t('Kanäle, Pegel und Fehler des Kabelmodems gibt die Schnittstelle der FRITZ!Box (TR-064) nicht heraus – nur die Geschwindigkeit der Verbindung.')}</p></div>
    <div class="glas-raster">
      ${ik(t('Verbindung'), k.down_mbit ? html`${zahl(k.down_mbit)}<small> / ${zahl(k.up_mbit)} Mbit/s</small>` : '–', t('laut Box'))}
      ${ik(t('Empfangskanäle'), '–', k.fehlt)}
      ${ik(t('Empfangspegel'), '–', k.fehlt)}
      ${ik(t('Signal/Rausch (MER)'), '–', k.fehlt)}
    </div>
    <div class="glas-panel block"><div class="block-kopf"><h3>${t('Kanäle')}</h3><span class="leise">${t('laut FRITZ!Box')}</span></div>
      ${iz(t('Sendepegel'), '–', k.fehlt)}
      ${iz(t('Fehler korrigiert / nicht korrigierbar'), '–', k.fehlt)}
      ${iz(t('Kanalliste'), '–', k.fehlt)}
    </div>`;
}

function extern(p) {
  return html`<div class="glas-panel block"><div class="befund"><span class="punkt grau"></span><div><b>${t('Werte vom vorgeschalteten Gerät folgen')}</b>
    <p>${t('Die FRITZ!Box hängt hinter einem eigenen Modem oder Router und kennt dessen Leitung nicht. Heimnetz liest die Werte dieses Geräts in einer späteren Fassung; die Rohdaten gibt es schon über 🔬 Diagnose.')}</p></div></div>
    ${p.istAdmin ? html`<div class="dg-knoepfe"><button @click=${() => p.einstellungenOeffnen('diag')}>${t('🔬 Rohdaten abfragen ›')}</button></div>` : nothing}</div>`;
}

function ersatz(e) {
  return html`<div class="glas-panel block"><div class="block-kopf"><h3>${t('Ersatzzugang Mobilfunk')}</h3>
      <span class="badge ${e.aktiv ? 'amber-b' : ''}">${e.aktiv ? t('aktiv') : t('bereit · nicht aktiv')}</span></div>
    <p class="hinweis" style="font-size:13px">${e.text}${e.letzte ? ` · ${t('zuletzt aktiv {zeit}', { zeit: zeit(e.letzte) })}` : ''}${e.rsrp != null ? ` · ${t('Signal gerade {n} dBm', { n: e.rsrp })}${e.technik ? ` (${e.technik})` : ''}` : ''}</p></div>
    <div class="glas-raster">
      ${ik(t('Umschaltungen'), html`${e.umschaltungen_30}`, t('letzte 30 Tage'))}
      ${ik(t('Über Ersatz'), e.dauer_30 ?? '–', t('letzte 30 Tage'))}
      ${ik(t('Datenmenge'), '–', t('über Ersatz: meldet die Box nicht getrennt'))}
    </div>`;
}

/** Verlauf aus der Aufzeichnung (Mittel je Stunde): eine oder zwei Linien, je mit eigener Skala; Punkte = Neusync. */
function verlauf(titel, unter, linien, marken = [], band = null) {
  const W = 600, H = 150;
  const bis = Date.now() / 1000, von = bis - 7 * 86400;
  const x = (z) => ((z - von) / (bis - von)) * W;
  const da = linien.some((l) => l.punkte.length);
  const pfad = (l) => {
    const v = l.punkte.map((q) => q[1]).concat(band ? band : []);
    const lo = Math.min(...v), hi = Math.max(...v), spanne = hi - lo || 1;
    const y = (w) => H - ((w - lo) / spanne) * (H - 10) - 5;
    return { d: l.punkte.map(([z, w], i) => `${i ? 'L' : 'M'}${x(z).toFixed(1)},${y(w).toFixed(1)}`).join(''), y };
  };
  const erste = da ? pfad(linien[0]) : null;
  return html`<div class="glas-panel block"><div class="block-kopf"><h3>${titel}</h3><span class="leise">${unter}</span></div>
    ${da ? html`<svg class="dia" viewBox="0 -6 ${W} ${H + 24}">
        ${band && erste ? svg`<rect x="0" y=${Math.min(erste.y(band[0]), erste.y(band[1]))} width=${W} height=${Math.abs(erste.y(band[0]) - erste.y(band[1]))} fill="var(--s3)" opacity=".1"></rect>` : nothing}
        ${linien.map((l) => svg`<path d=${pfad(l).d} fill="none" stroke=${l.farbe} stroke-width="1.6"></path>`)}
        ${marken.map((m) => svg`<circle cx=${x(m)} cy=${H - 4} r="4" fill="var(--rot)"></circle>`)}
        ${svg`<text x="0" y=${H + 16}>${t('vor {n} Tagen', { n: 7 })}</text><text x=${W} y=${H + 16} text-anchor="end">${t('jetzt')}</text>`}
      </svg>
      <div class="legende">${linien.map((l) => html`<span><i style="background:${l.farbe}"></i>${l.name}</span>`)}${marken.length ? html`<span><i style="background:var(--rot)"></i>${t('Neusynchronisierung')}</span>` : nothing}</div>`
      : html`<div class="leer">${t('Noch kein Verlauf aufgezeichnet.')}</div>`}
  </div>`;
}
