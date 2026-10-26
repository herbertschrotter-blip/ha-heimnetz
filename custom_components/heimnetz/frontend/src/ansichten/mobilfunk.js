// Reiter „Funk“ · Mobilfunk: Befund, Verbindung zur Basisstation (Grafik und alle Zellen), Verbindung, Bänder, Verlauf.
import { html, svg, nothing } from 'lit';
import { farbe, zeit } from '../format.js';
import { kachel, seg } from './teile.js';
import { osmGemerkt } from '../karte.js';
import { merke, sprache, t } from '../sprache.js';

const W = 600;
const H = 170;
const UNTEN = -120;
const OBEN = -75;
const y = (v) => ((OBEN - Math.max(UNTEN, Math.min(OBEN, v))) / (OBEN - UNTEN)) * H;

function linie(punkte, von, bis) {
  if (!punkte.length) return '';
  const x = (t) => ((t - von) / Math.max(1, bis - von)) * W;
  return punkte.map(([t, v], i) => `${i ? 'L' : 'M'}${x(t).toFixed(1)},${y(v).toFixed(1)}`).join('');
}

export function mobilfunk(p, d) {
  if (!d.verfuegbar) return html`<div class="glas-panel block"><div class="leer">${t('Die Box meldet gerade keine Mobilfunkwerte.')}</div></div>`;
  const o = p._opt.mobilfunk;
  const bis = Date.now() / 1000;
  const von = bis - o.tage * 86400;
  return html`
    <details class="glas-panel klapp befund-k">
      <summary><span class="punkt" style="background:${farbe(d.befund.lage)}"></span><b>${d.befund.titel}</b><span class="mehr">ⓘ</span></summary>
      <p class="hinweis">${d.befund.text}</p>
    </details>
    ${d.zellen.length ? html`<div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Verbindung zur Basisstation')}</h3><span class="leise">${[d.technik, d.strecke?.anbieter].filter(Boolean).join(' · ')}</span></div>
      ${d.strecke ? strecke(d.strecke) : nothing}
      <div class="zellen">${d.zellen.map(zelle)}</div>
      <details class="klapp"><summary><span class="leise">ⓘ ${t('Was zeigt die Liste?')}</span></summary>
        <p class="hinweis">${d.zellen.length > 1 ? `${t('Die Box hält gleichzeitig mehrere Zellen: die Ankerzelle trägt die Verbindung, die übrigen bündeln dazu.')} ` : ''}${t('Balken = Signalstärke (RSRP), daneben die Signalqualität (RSRQ).')}</p></details>
    </div>` : nothing}
    ${d.karte && d.karte.rahmen ? karte(p, d.karte, !!(p.hass && p.hass.themes && p.hass.themes.darkMode)) : nothing}
    <div class="glas-raster">
      ${kachel(t('Verbunden seit'), d.laufzeit ?? '–', d.letzter_abbruch ? t('Neueinwahl {zeit}', { zeit: zeit(d.letzter_abbruch) }) : t('ohne Neueinwahl (7 Tage)'))}
      ${kachel(t('Abbrüche'), html`${d.abbrueche_7}`, t('Neueinwahlen, letzte 7 Tage'))}
      ${kachel(t('Bänder'), d.baender ? html`<span style="font-size:15px">${d.baender}</span>` : '–', t('eingeschaltet (in der Box)'))}
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Verlauf Signalstärke')}</h3>${seg([[1, '24 h'], [7, t('{n} Tage', { n: 7 })], [30, t('{n} Tage', { n: 30 })]], o.tage, (v) => p.setze('mobilfunk', { tage: v }))}</div>
      ${d.verlauf.anker.length || d.verlauf.nr.length ? html`<svg class="dia" viewBox="-30 -6 ${W + 36} ${H + 24}">
        ${[-80, -90, -100, -110, -120].map((v) => svg`<line class="gitter" x1="0" x2=${W} y1=${y(v)} y2=${y(v)}></line><text x="-4" y=${y(v) + 3} text-anchor="end">${v}</text>`)}
        ${svg`<rect x="0" y=${y(d.schwach_unter)} width=${W} height=${H - y(d.schwach_unter)} fill="var(--rot)" opacity=".08"></rect>`}
        ${svg`<path d=${linie(d.verlauf.anker, von, bis)} fill="none" stroke="var(--s1)" stroke-width="1.6"></path>`}
        ${svg`<path d=${linie(d.verlauf.nr, von, bis)} fill="none" stroke="var(--s2)" stroke-width="1.6"></path>`}
        ${svg`<text x="0" y=${H + 16}>${o.tage === 1 ? t('vor {n} h', { n: 24 }) : t('vor {n} Tagen', { n: o.tage })}</text><text x=${W} y=${H + 16} text-anchor="end">${t('jetzt')}</text>`}
      </svg>
      <div class="legende"><span><i style="background:var(--s1)"></i>${t('4G-Anker')}</span><span><i style="background:var(--s2)"></i>5G</span><span><i style="background:var(--rot);opacity:.3"></i>${t('schwach (unter {n} dBm)', { n: d.schwach_unter })}</span></div>
      <p class="hinweis">${t('Steigt die Linie nach dem Umstellen der Box um etwa 10 dBm, war der Standort die Bremse.')}</p>`
        : html`<div class="leer">${t('Noch kein Verlauf aufgezeichnet.')}</div>`}
      ${nothing}
    </div>`;
}

/** Vier Balken wie an der Box; Anzahl und Farbe kommen von der Integration. */
function stufen(n, lage) {
  return html`<span class="stufen">${[1, 2, 3, 4].map((i) => html`<i style="height:${i * 25}%;${i <= n ? `background:${farbe(lage)}` : ''}"></i>`)}</span>`;
}

function zelle(z) {
  const titel = z.anker && z.rolle_art === 'anker' ? t('4G-Anker') : t('{art}-Zelle', { art: z.art });
  const kennung = [z.tac ? `TAC ${z.tac}` : '', z.plmn ? `PLMN ${z.plmn}` : ''].filter(Boolean).join(' · ');
  const wo = z.fund ? html`<span class="z-wo">📍 ${z.fund.quelle}${z.fund.genau ? ` · ±${z.fund.genau}` : ''}</span>` : z.such ? html`<span class="z-wo">${z.such}</span>` : nothing;
  return html`<div class="zelle"><span class="badge ${z.anker ? 'blau-b' : ''}">${z.art}</span>
    <span class="z-name"><b>${titel}</b><span class="leise">${z.kennung ? `${t('Zelle {kennung}', { kennung: z.kennung })} · ` : ''}${z.rolle}</span>
      <span class="leise">${kennung}${kennung && (z.fund || z.such) ? ' · ' : ''}${wo}</span></span>
    ${stufen(z.stufen, z.lage)}<span class="z-wert">${z.rsrp ?? '–'}<small> dBm</small><span class="leise">${z.rsrq ?? '–'} dB</span></span></div>`;
}

/** Eigene Zeichnung: Box – Funkstrecke – Masten; Linie in der Farbe der Signalstärke der Ankerzelle. */
function strecke(s) {
  const f = farbe(s.lage);
  const masten = s.masten.length ? s.masten : ['4G'];
  const mitte = 530 - (masten.length - 1) * 30;
  const mast = (x, t) => svg`<g transform="translate(${x},0)">
    <path d="M0,46 L-17,104 M0,46 L17,104 M-11,82 L11,82 M-14,94 L14,94 M-8,70 L8,70" stroke="var(--ink2)" stroke-width="2" fill="none" stroke-linecap="round"></path>
    <path d="M-10,36 a14,14 0 0 1 0,-20 M10,36 a14,14 0 0 0 0,-20 M-17,42 a24,24 0 0 1 0,-32 M17,42 a24,24 0 0 0 0,-32" stroke="var(--ink2)" stroke-width="1.6" fill="none" opacity=".7"></path>
    <circle cx="0" cy="62" r="13" fill="var(--sheet)" stroke="var(--panel-rand)"></circle><text x="0" y="66" text-anchor="middle" class="m-t">${t}</text></g>`;
  return html`<svg class="strecke" viewBox="0 0 600 132" role="img" aria-label=${t('Verbindung der FRITZ!Box zur Basisstation')}>
    <rect x="30" y="22" width="44" height="74" rx="9" fill="var(--panel)" stroke="var(--ink2)" stroke-width="2"></rect>
    <rect x="30" y="84" width="44" height="12" rx="4" fill="var(--s2)"></rect>
    <line x1="58" y1="44" x2="66" y2="44" stroke="var(--ink2)" stroke-width="2"></line><line x1="58" y1="50" x2="66" y2="50" stroke="var(--ink2)" stroke-width="2"></line>
    <text x="52" y="122" text-anchor="middle" class="m-t">FRITZ!Box</text>
    <line x1="96" y1="62" x2=${mitte - 60} y2="62" stroke=${f} stroke-width="5" stroke-linecap="round"></line>
    <line class="fluss" x1="96" y1="62" x2=${mitte - 60} y2="62" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 22" opacity=".45"></line>
    ${s.entfernung ? svg`<text x=${(36 + mitte) / 2} y="48" text-anchor="middle" class="m-w">↔ ${s.entfernung}</text>` : nothing}
    ${s.rsrp != null ? svg`<text x=${(36 + mitte) / 2} y="86" text-anchor="middle" class="m-t">${t('Signal {wort} · {n} dBm', { wort: s.wort, n: s.rsrp })}</text>` : nothing}
    ${masten.map((t, i) => mast(mitte + i * 60, t))}
    <text x=${mitte + (masten.length - 1) * 30} y="122" text-anchor="middle" class="m-t">${t('Basisstation')}</text></svg>`;
}

const STAND = {
  ohne_schluessel: merke('BeaconDB kennt diese Zellen nicht. Mit einem Schlüssel von opencellid.org (Einstellungen → Geräte & Dienste → Heimnetz → Konfigurieren) fragt die Integration zusätzlich OpenCellID.'),
  nicht_gefunden: merke('Weder OpenCellID noch BeaconDB kennen diese Zellen – die Karte zeigt nur die Entfernung laut Box.'),
  fehler: merke('Der Dienst für den Standort der Zellen war nicht erreichbar; neuer Versuch in einer Stunde.'),
  schluessel_ungueltig: merke('OpenCellID lehnt den Schlüssel ab – unter Geräte & Dienste → Heimnetz → Konfigurieren prüfen.'),
  ohne_kennung: merke('Die Box nennt für keine Zelle eine vollständige Kennung – die Karte zeigt nur die Entfernung.'),
};

/** Karte: Orte und Rahmen kommen fertig von der Integration; gezeichnet wird mit Leaflet (src/karte.js). */
function karte(p, k, dunkel) {
  return html`<div class="glas-panel block">
    <div class="block-kopf"><h3>${t('Wo steht der Mast?')}</h3><span class="leise">${k.gefunden ? t('geschätzt · {n} von {gesamt} Zellen gefunden', { n: k.gefunden, gesamt: k.zellen }) : t('Entfernung laut Box')}</span></div>
    <heimnetz-karte .daten=${k} ?dunkel=${dunkel} .sprache=${sprache()} @osm-umgeschaltet=${() => p.requestUpdate()}></heimnetz-karte>
    <div class="legende"><span><i style="background:var(--blau)"></i>${t('Wohnung')}</span>
      ${k.masten.map((m) => html`<span><i style="background:var(--amber)"></i>${t('Mast {name} (geschätzt)', { name: m.name })}${m.fuenf_g ? ` · ${t('4G + 5G (vermutlich)')}` : ''} · ${m.entfernung} ${m.richtung}${m.genau ? ` (± ${m.genau})` : ''}</span>`)}
      ${k.punkte.length ? html`<span><i class="punkt-l" style="background:var(--blau)"></i>${t('Ankerzelle')}</span><span><i class="punkt-l" style="background:var(--ink2)"></i>${t('weitere Zellen')}</span><span><i class="genau-l"></i>${t('Genauigkeit')}</span>` : nothing}
      ${k.osm?.length && osmGemerkt() ? html`<span><i class="osm-l"></i>${t('Funkmast laut OpenStreetMap')}${k.osm.some((o) => o.passt) ? ` ${t('(orange umrandet: passt am besten)')}` : ''}</span>` : nothing}
      ${k.ring ? html`<span><i class="ring"></i>${t('{ring} laut Box', { ring: k.ring })}</span>` : nothing}</div>
    ${STAND[k.stand] ? html`<p class="hinweis">${t(STAND[k.stand])}</p>` : nothing}
    <details class="klapp"><summary><span class="leise">ⓘ ${t('Woher kommt das?')}</span></summary>
      <p class="hinweis">${t(WOHER)}</p></details>
  </div>`;
}

// Erklärung zur Karte (lang; ein Absatz)
const WOHER = merke('Die Box meldet nur die Entfernung (Ring), nicht die Richtung. Jede Zelle mit voller Kennung schlägt die Integration bei BeaconDB (ohne Schlüssel) und – mit eigenem Schlüssel – bei OpenCellID nach und merkt sich das Ergebnis; es zählt der genauere Fund. Hinaus geht nur die Kennung der Zelle, nie dein Standort. Beide Dienste kennen nicht den Mast selbst, sondern die Orte, an denen Nutzer die Zelle empfangen haben – daher der Kreis für die Genauigkeit. Zellen derselben Sendeanlage (Kennung vor dem Bindestrich) hängen am selben Mast; sein Standort ist das Mittel ihrer Punkte, genauere zählen mehr. Zellen, von denen die Box nur die PCI nennt, lassen sich nicht nachschlagen – auch 5G nicht: Die Box nennt für 5G nur diese Nummer. Bei 5G-NSA hängt die 5G-Zelle aber meist am selben Mast wie die LTE-Ankerzelle, deshalb steht dort „4G + 5G (vermutlich)“, solange 5G mitläuft. Die Namen der Zellen erscheinen beim Hineinzoomen. Zoomen mit ＋/−, Mausrad oder zwei Fingern, ziehen zum Verschieben, ⌖ zeigt wieder alles. Die Kartenkacheln lädt dein Browser von basemap.at (Server der Stadt Wien) oder OpenStreetMap; der Anbieter sieht dabei den Kartenausschnitt, nicht mehr. Die gewählte Grundlage merkt sich dein Browser. „📡 Masten (OSM)“ zeigt Funkmasten, die in OpenStreetMap eingetragen sind – echte Bauwerke, aber meist ohne Betreiber. Orange umrandet ist der Mast, der am nächsten am geschätzten Mast der Zellen steht (höchstens 1,5 km daneben); ist der nicht bekannt, der Mast, dessen Entfernung am besten zur Entfernung laut Box passt – die schwankt je Zelle aber stark. Ein Hinweis, kein Beweis. Zellen einer Sendeanlage, die einmal gefunden wurden, zählen einen Monat lang mit – auch wenn die Box gerade an einem Sektor hängt, den keine Datenbank kennt. Antippen eines Masts zeigt Entfernung und Richtung und – mit OpenCellID-Schlüssel – Anbieter und Technik der Zellen, die OpenCellID in höchstens 500 m Abstand kennt (aus dem Datenabzug für ganz Österreich, einmal im Monat geladen und hier ausgewertet). ⛶ öffnet die Karte über die ganze Seite. Die Integration fragt dafür einmal im Monat einen großen Ausschnitt auf festem Raster bei OpenStreetMap ab; daraus lässt sich deine Wohnung nur auf etwa 22 × 15 km eingrenzen.');
