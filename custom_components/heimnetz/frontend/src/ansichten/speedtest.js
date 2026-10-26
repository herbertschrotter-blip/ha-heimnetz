// Reiter „Speedtest“: letzte Messung, Wochenraster mit Tagesverlauf, Messplan in einer Zeile, letzte Messungen.
// Eingestellt wird im Fenster ⚙ (ansichten/einstellungen.js).
import { html, svg, nothing } from 'lit';
import { datum, uhr, wochentage, zahl, zeit, farbe } from '../format.js';
import { merke, t, tl } from '../sprache.js';
import { kachel, seg } from './teile.js';

const GROESSEN = [['down', '↓ Download'], ['up', '↑ Upload'], ['ping', 'Ping']];
const ZEITRAEUME = [[7, merke('7 Tage')], [28, merke('4 Wochen')], [84, merke('12 Wochen')]];
const BELASTET = { aus: merke('weggelassen'), halb: merke('¼ gezählt'), mit: merke('voll gezählt') };
const prozent = (a) => (a == null ? '' : t('{n} % vom Tarif', { n: zahl(a * 100) }));
/** Name des Zeitraums (7 Tage, 4 Wochen, 12 Wochen). */
const zeitraum = (tage) => t(ZEITRAEUME.find(([x]) => x === tage)?.[1] ?? '');
/** „2–3 Uhr“ bzw. „2–3 h“. */
const stunden = (h) => t('{von}–{bis} Uhr', { von: h, bis: h + 1 });

export function speedtest(p, d) {
  const o = p._opt.speedtest;
  const l = d.letzte;
  const la = d.letzte_anteil || {};
  const tagWahl = o.datum ? null : o.tag;
  const TAGE = wochentage(true);
  const raster = d.raster.map((reihe, wd) => html`<button class="tag ${tagWahl === wd ? 'on' : ''}" title=${t('Tagesverlauf {tag}', { tag: TAGE[wd] })}
    @click=${() => p.setze('speedtest', { tag: wd, datum: null, stunde: null })}>${TAGE[wd]}</button>${reihe.map((z, h) => z.anzahl
    ? html`<i class="kachel ${p._kachel && p._kachel.fest && p._kachel.tag === wd && p._kachel.stunde === h ? 'wahl' : ''}" data-k="${wd}-${h}"
      style="background:${farbe(z.lage)}" aria-label=${`${TAGE[wd]} ${stunden(h)}: ${t('Median {wert} ({n} Messungen)', { wert: `${zahl(z.median, 1)} ${d.einheit}`, n: z.anzahl })}`}
      @mouseenter=${() => p.kachelZeigen(wd, h, false)} @mouseleave=${() => p.kachelWeg(false)}
      @click=${() => p.kachelZeigen(wd, h, true)}><b>${zahl(z.median)}</b></i>`
    : html`<i class="ohne" title=${`${TAGE[wd]} ${stunden(h)}: ${t('keine Messung')}`}></i>`)}`);
  return html`
    <div class="glas-raster">
      ${kachel(t('Download zuletzt'), l ? html`${zahl(l.down)}<small> Mbit/s</small>` : '–', l ? `${prozent(la.down)} · ${zeit(l.t)}` : t('noch keine Messung'))}
      ${kachel(t('Upload zuletzt'), l ? html`${zahl(l.up)}<small> Mbit/s</small>` : '–', prozent(la.up))}
      ${kachel(t('Ping zuletzt'), l ? html`${zahl(l.ping)}<small> ms</small>` : '–', l && l.server ? `Server ${l.server}` : '')}
      ${kachel(t('Typisch (Median)'), d.median != null ? html`${zahl(d.median, 1)}<small> ${d.einheit}</small>` : '–', d.anteil != null ? prozent(d.anteil) : t('{n} Messungen gezählt', { n: d.anzahl }))}
      ${kachel(t('Messungen'), html`${d.gesamt}`, t('{n} belastet · {fehl} Fehlmessungen', { n: d.belastet, fehl: d.fehl }))}
      ${kachel(t('Volumen Speedtests'), html`${zahl(d.volumen_monat_mb / 1000, 1)}<small> GB</small>`, t('diesen Monat (geschätzt)'))}
    </div>
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Wann ist das Internet schnell?')}</h3><span class="leise">${t('Median je Wochentag und Stunde')}</span></div>
      <div class="leiste">
        ${seg(tl(ZEITRAEUME), o.tage, (v) => p.setze('speedtest', { tage: v, datum: null, stunde: null }))}
        ${seg(GROESSEN, o.groesse, (v) => p.setze('speedtest', { groesse: v, stunde: null }))}
        <select style="font-size:12px;padding:5px 8px" @change=${(e) => p.setze('speedtest', { server: e.target.value, stunde: null })}>
          <option value="" ?selected=${!o.server}>${t('alle Server')}</option>
          ${d.server.map((s) => html`<option value=${s.name} ?selected=${o.server === s.name}>${s.name} (${s.anzahl})</option>`)}
          ${o.server && !d.server.some((s) => s.name === o.server)
            ? html`<option value=${o.server} selected>${o.server} (${t('keine Messungen im Zeitraum')})</option>` : nothing}
        </select>
      </div>
      ${d.gesamt ? html`<div class="wr"><span></span>${Array.from({ length: 24 }, (_, h) => html`<span>${h % 3 ? '' : h}</span>`)}${raster}</div>
        <div class="leiste" style="justify-content:space-between"><div class="skala">${d.groesse === 'ping' ? t('langsam') : '0 %'}<i></i>${d.groesse === 'ping' ? t('schnell') : d.tarif ? t('{n} % vom Tarif', { n: 100 }) : t('typisch')}</div>
        <span class="leise">${t('grau = keine Messung · Zahl = Median der Stunde · Tipp auf einen Tag zeigt den Verlauf · belastete Messungen {wie} (⚙) · {n} ohne Grundlast', { wie: t(BELASTET[o.grundlast]), n: d.ungeprueft })}</span></div>`
        : html`<div class="leer">${t('Im gewählten Zeitraum keine Messungen.')}</div>`}
      ${d.gesamt ? tagesverlauf(p, d) : nothing}
      ${d.auffaellig ? html`<p class="hinweis"><b>${t('Auffällig:')}</b> ${d.auffaellig}</p>` : nothing}
    </div>
    ${planStatus(p, p._daten.einstellungen)}
    ${serieKarte(p._daten.einstellungen)}
    <div class="glas-panel block"><div class="block-kopf"><h3>${t('Letzte Messungen')}</h3><span class="leise">${t('mit Grundlast')}</span></div>
        ${d.messungen.length ? html`<div class="tab-scroll"><table class="t">
          <tr><th>${t('Zeit')}</th><th>Server</th><th class="r">↓</th><th class="r">↑</th><th class="r">Ping</th><th>${t('Netz')}</th><th>${t('Zelle')}</th><th class="r">Signal</th><th>Box</th><th class="r">${t('Grundlast')}</th><th></th></tr>
          ${d.messungen.map((m) => { const k = m.kontext || {}; return html`<tr class="klick ${m.gewicht ? '' : 'belastet'}" @click=${() => p.messungOeffnen(m)}>
            <td>${zeit(m.t)}</td><td>${m.server ?? '–'}</td><td class="r">${zahl(m.down)}</td><td class="r">${zahl(m.up)}</td>
            <td class="r">${zahl(m.ping)}</td><td>${k.netz ? html`<span class="badge ${k.netz.startsWith('5G') ? 'blau-b' : ''}">${k.netz}</span>` : '–'}</td>
            <td>${k.zelle ? kurzZelle(k.zelle) : '–'}</td><td class="r">${k.rsrp != null ? `${zahl(k.rsrp)} dBm` : '–'}</td>
            <td>${k.box_modell ? boxKurz(k) : html`<span class="leise">–</span>`}</td><td class="r">${zahl(m.last, 1)}</td>
            <td>${m.serie ? html`<span class="badge blau-b">${t('Serie')}</span> ` : nothing}${m.belastet ? html`<span class="badge amber-b">${m.gewicht === 0 ? t('zählt nicht') : m.gewicht < 1 ? t('zählt ¼') : t('belastet')}</span>` : nothing}</td></tr>`; })}
        </table></div><p class="hinweis">${t('Mbit/s. Grundlast = Verkehr über die Box in den Minuten vor der Messung; belastet = über {n} Mbit/s. Netz, Zelle (Ankerzelle), Signal (RSRP der Ankerzelle) und Box (Modell · Firmware) zum Zeitpunkt der Messung – ältere Messungen aus Verlauf und Journal nachgetragen, ohne Box („–“). Tippen auf eine Zeile zeigt alle Werte der Messung.', { n: zahl(d.schwelle, 1) })}</p>`
        : html`<div class="leer">${t('Noch keine eigenen Messungen. Gemessen wird von der Ookla-Integration.')}</div>`}
    </div>`;
}

/** WU-0006: Ookla ist empfohlen, nicht Pflicht – ohne zeigt der Reiter, woher die Messungen kämen. */
const OOKLA_LINK = 'https://github.com/soulripper13/hass-speedtest-ookla';

/** Messplan in einer Zeile mit „Jetzt messen“; eingestellt wird im Fenster ⚙ (Mockup: Funk und Einstellungen). */
function planStatus(p, e) {
  if (!e || !e.messplan) return nothing;
  const m = e.messplan, z = e.plan, o = e.ookla, admin = p.istAdmin;
  const stand = !o.vorhanden ? t('Ookla-Integration fehlt')
    : z.misst ? t('misst gerade …')
    : !m.an ? t('automatisch aus')
    : z.wartet ? t('verschoben wegen Verkehr – neuer Versuch {uhr}', { uhr: uhr(z.neuer_versuch) })
    : t('alle {n} h · nächste {zeit}', { n: m.takt_h, zeit: z.naechste ? zeit(z.naechste) : '–' });
  return html`<div class="glas-panel block">
    ${!o.vorhanden ? html`<div class="befund ohne-ookla"><span class="punkt grau"></span><div><b>${t('Ookla Speedtest ist nicht eingerichtet')}</b>
      <p>${t('Heimnetz läuft auch ohne – nur Messungen gibt es dann keine. Für Speedtests die HACS-Integration „Ookla Speedtest“ installieren und einrichten; den Rest erledigt dieser Plan.')}
      <a class="blau" href=${OOKLA_LINK} target="_blank" rel="noopener noreferrer">${t('Ookla Speedtest auf GitHub ↗')}</a></p></div></div>` : nothing}
    ${o.misst_selbst ? html`<div class="befund"><span class="punkt amber"></span><div><b>${t('Ookla misst zusätzlich nach eigenem Takt')}</b><p>${t('In den Ookla-Einstellungen „manuell“ einschalten, damit nur dieser Plan misst.')}</p></div></div>` : nothing}
    <div class="zeile" style="padding:2px 0"><span style="display:flex;gap:10px;align-items:center"><span class="punkt ${m.an && o.vorhanden ? '' : 'grau'}"></span>
      <span><b style="font-weight:600">${t('Messplan')}</b> <span class="leise">${stand}</span></span></span>
      ${admin ? html`<span class="chips"><button class="chip glas-panel" style="font-weight:600" ?disabled=${z.misst || !!e.serie || !o.vorhanden} @click=${() => p.jetztMessen()}>${z.misst && !e.serie ? `⏳ ${t('misst …')}` : `▶ ${t('Jetzt messen')}`}</button>
        <button class="chip glas-panel serie-knopf" style="font-weight:600" ?disabled=${!!e.serie || z.misst || !o.vorhanden} @click=${() => p.serieStarten()}>${e.serie ? `⏳ ${t('Serie {lauf} von {n} …', { lauf: e.serie.lauf, n: e.serie.n })}` : `▶ ${t('{n}× messen', { n: m.serie })}`}</button></span>` : nothing}</div>
    ${e.serie ? html`<p class="hinweis">${t('Misst {n}× hintereinander – der nächste Durchlauf startet, sobald das Ergebnis des vorigen da ist.', { n: e.serie.n })}</p>` : nothing}
    ${p._hinweisPlan ? html`<p class="fein">${p._hinweisPlan}</p>` : nothing}
  </div>`;
}

/** WU-0001 (Mockup netzwerk.html · Speedtest-Serie): Ergebnis der letzten Serie – Median und Spanne rechnet die
 *  Integration. */
function serieKarte(e) {
  const s = e && e.letzte_serie;
  if (!s || !s.laeufe || !s.laeufe.length) return nothing;
  const k = (titel, w, einheit, zusatz) => html`<div class="glas-k glas-panel"><span class="glas-klein">${titel} (Median)</span>
    <span class="glas-wert">${w ? zahl(w.median) : '–'}<small> ${einheit}</small></span>
    <span class="glas-kwk">${w ? t('Spanne {min}–{max}', { min: zahl(w.min), max: zahl(w.max) }) : t('kein Wert')}${zusatz || ''}</span></div>`;
  const laeufe = s.laeufe.length < s.geplant ? t('{n} von {geplant} Durchläufe', { n: s.laeufe.length, geplant: s.geplant }) : t('{n} Durchläufe', { n: s.laeufe.length });
  return html`<div class="glas-panel block">
    <div class="block-kopf"><h3>${t('Letzte Serie')}</h3><span class="leise">${zeit(s.t)} · ${laeufe} · ${s.server.join(', ') || '–'}</span></div>
    <div class="glas-raster" style="grid-template-columns:repeat(3,1fr)">
      ${k('Download', s.down, 'Mbit/s', s.anteil != null ? ` · ${t('{n} % vom Tarif', { n: s.anteil })}` : '')}${k('Upload', s.up, 'Mbit/s')}${k('Ping', s.ping, 'ms')}</div>
    <div class="tab-scroll"><table class="t" style="margin-top:8px"><tr><th>${t('Durchlauf')}</th><th>Server</th><th class="r">↓</th><th class="r">↑</th><th class="r">Ping</th></tr>
      ${s.laeufe.map((x, i) => html`<tr><td>${i + 1} · ${zeit(x.t)}</td><td>${x.server ?? '–'}</td><td class="r">${zahl(x.down)}</td><td class="r">${zahl(x.up)}</td><td class="r">${zahl(x.ping)}</td></tr>`)}</table></div>
    <p class="hinweis">${t('Median statt Mittelwert: ein Ausreißer verzieht ihn nicht. Die einzelnen Messungen zählen in Wochenraster und Auswertung normal mit (markiert als „Serie“). Für verschiedene Server in Ookla weitere Tests anlegen – die Serie wechselt dann reihum.')}</p></div>`;
}

/** „aaaaa-64“ → „…-64“ (die Sendeanlage steht im Detail), ohne Strich unverändert. */
const kurzZelle = (z) => (z.includes('-') ? `…-${z.split('-').pop()}` : z);
/** „FRITZ!Box 6860 5G“ + „268.08.03“ → „6860 5G · 8.03“ (FRITZ!OS-Version ohne Hardware-Kennung davor). */
function boxKurz(k) {
  const modell = k.box_modell.replace(/^FRITZ!Box\s*/, '');
  const teile = (k.box_firmware || '').split('.');
  const fw = teile.length >= 3 ? `${Number(teile[1])}.${teile[2]}` : k.box_firmware || '';
  return fw ? `${modell} · ${fw}` : modell;
}
const AUSLOESER = { messplan: merke('Messplan'), jetzt: merke('„Jetzt messen“'), serie: merke('Serie'), ookla: merke('Ookla (eigener Takt oder von Hand)') };
const TAGESART = { werktag: merke('Werktag'), wochenende: merke('Wochenende'), feiertag: merke('Feiertag') };
const WETTER = {
  'clear-night': merke('klar'), cloudy: merke('bewölkt'), exceptional: merke('außergewöhnlich'), fog: merke('Nebel'), hail: merke('Hagel'),
  lightning: merke('Gewitter'), 'lightning-rainy': merke('Gewitter mit Regen'), partlycloudy: merke('teils bewölkt'), pouring: merke('Starkregen'),
  rainy: merke('Regen'), snowy: merke('Schnee'), 'snowy-rainy': merke('Schneeregen'), sunny: merke('sonnig'), windy: merke('windig'),
  'windy-variant': merke('windig, bewölkt'),
};
function dauer(s) {
  if (s == null) return null;
  const tg = Math.floor(s / 86_400), h = Math.floor((s % 86_400) / 3600), m = Math.floor((s % 3600) / 60);
  return tg ? `${t(tg === 1 ? '{n} Tag' : '{n} Tage', { n: tg })} ${h} h` : h ? `${h} h ${m} min` : `${m} min`;
}

/** WU-0005 (Mockup netzwerk.html · Zusatzdaten je Messung): alle Werte einer Messung. Die Werte hält die
 *  Integration im Moment der Messung fest (bzw. trägt sie nach); hier wird nur beschriftet und formatiert. */
export function messungBlatt(p) {
  const m = p._blatt.m, k = m.kontext || {}, nach = k.quelle === 'nachgetragen', leer = !k.quelle;
  const z = (titel, wert) => html`<div class="zeile"><span class="leise">${titel}</span><span style="text-align:right">${wert ?? html`<span class="leise">–</span>`}</span></div>`;
  const mit = (...w) => (w.some((x) => x == null) ? null : w.join(' · '));
  const dbm = (v, e = 'dBm') => (v == null ? null : `${zahl(v)} ${e}`);
  return html`<div class="griff"></div><button class="zu" @click=${() => p.zu()}>✕</button>
    <h3>${t('Messung {zeit}', { zeit: zeit(m.t) })}</h3>
    <div class="leise">${leer ? t('ohne Momentaufnahme (älter als der Verlauf von Home Assistant)') : nach ? t('nachgetragen aus Verlauf und Journal – Box, Heimnetz und Teile des Mobilfunks nicht bekannt') : t('Momentaufnahme im Moment der Messung')}</div>
    <div class="gruppe">${t('Messung')}</div>
    ${z('Download · Upload · Ping', `${zahl(m.down)} · ${zahl(m.up)} Mbit/s · ${zahl(m.ping)} ms`)}
    ${z(t('Jitter (gesamt · ↓ · ↑)'), k.jitter != null ? `${[k.jitter, k.jitter_down, k.jitter_up].map((x) => (x == null ? '–' : zahl(x, 1))).join(' · ')} ms` : null)}
    ${z('Bufferbloat', k.bufferbloat ? t('Note {note}', { note: k.bufferbloat }) : null)}
    ${z(t('Server · Anbieter'), [m.server, k.anbieter].filter(Boolean).join(' · ') || null)}
    ${z(t('Ergebnis bei Ookla'), k.ergebnis_url && /^https:\/\//.test(k.ergebnis_url) ? html`<a class="blau" href=${k.ergebnis_url} target="_blank" rel="noopener noreferrer">${t('öffnen ›')}</a>` : null)}
    ${z(t('Auslöser'), k.ausloeser ? `${AUSLOESER[k.ausloeser] ? t(AUSLOESER[k.ausloeser]) : k.ausloeser}${k.serie_n ? `, ${t('Durchlauf {lauf} von {n}', { lauf: k.serie_lauf, n: k.serie_n })}` : ''}` : null)}
    ${z(t('Grundlast'), m.last != null ? `${zahl(m.last, 1)} Mbit/s${m.belastet ? ` · ${t('belastet')}` : ''}` : null)}
    <div class="gruppe">${t('Mobilfunk')}</div>
    ${z(t('Netz'), k.netz ? html`<span class="badge ${k.netz.startsWith('5G') ? 'blau-b' : ''}">${k.netz}</span>` : null)}
    ${z(t('Ankerzelle · Sendeanlage'), k.zelle ? [k.zelle, k.anlage && t('Anlage {anlage}', { anlage: k.anlage })].filter(Boolean).join(' · ') : null)}
    ${z(t('RSRP · RSRQ Anker'), k.rsrp != null ? [dbm(k.rsrp), dbm(k.rsrq, 'dB')].filter(Boolean).join(' · ') : null)}
    ${z('5G', k.nr_aktiv === false ? t('aus') : k.nr_aktiv ? [t('aktiv'), k.nr_pci != null && `PCI ${k.nr_pci}`, dbm(k.nr_rsrp), dbm(k.nr_rsrq, 'dB')].filter(Boolean).join(' · ') : null)}
    ${z(t('Entfernung laut Box'), k.entfernung_m ? `${zahl(k.entfernung_m / 1000, 1)} km` : null)}
    ${z(t('Nachbarzellen'), k.nachbarzellen)}
    ${z(t('Netz · Gebiet'), mit(k.plmn, k.tac && `TAC ${k.tac}`))}
    ${z(t('Verbunden seit'), dauer(k.verbunden_s))}
    ${z(t('Geschätzter Mast'), k.mast_m ? `${zahl(k.mast_m / 1000, 1)} km ${k.mast_richtung || ''}`.trim() : null)}
    <div class="gruppe">Box</div>
    ${z(t('Modell · Firmware'), k.box_modell ? [k.box_modell, k.box_firmware].filter(Boolean).join(' · ') : null)}
    ${z(t('Läuft seit'), dauer(k.box_laufzeit_s))}
    ${z(t('Eingeschaltete Bänder'), k.baender)}
    <div class="gruppe">Heimnetz</div>
    ${z(t('Geräte online · davon WLAN'), k.online != null ? `${k.online}${k.online_wlan != null ? ` · ${k.online_wlan}` : ''}` : null)}
    <div class="gruppe">${t('Umgebung')}</div>
    ${z(t('Wetter'), k.wetter ? [WETTER[k.wetter] ? t(WETTER[k.wetter]) : k.wetter, k.temperatur != null && `${zahl(k.temperatur, 1)} °C`, k.feuchte != null && t('{n} % Feuchte', { n: zahl(k.feuchte) }), k.wolken != null && t('{n} % Wolken', { n: zahl(k.wolken) })].filter(Boolean).join(' · ') : null)}
    ${z(t('Tag'), TAGESART[k.tagesart] && t(TAGESART[k.tagesart]))}
    <p class="hinweis" style="margin-top:10px">${t('Nicht verfügbar über die Schnittstelle der Box: genutztes Band, SINR, Bandbreite, MIMO, Carrier Aggregation.')}</p>`;
}

const BELASTET_KURZ = { aus: merke('zählt nicht'), halb: merke('zählt ¼'), mit: merke('belastet') };

/** AN-0005 (Mockup netzwerk.html · Popup zur Stundenkachel): Kennzahlen und Messungen hinter einer Kachel. Was zählt
 *  und wie, rechnet die Integration (gleiche Auswahl wie das Raster); hier wird nur angezeigt. */
export function kachelPopup(p) {
  const k = p._kachel, o = p._opt.speedtest, d = k.daten, TAGE = wochentage(true);
  const kopf = html`<div class="kp-kopf"><b>${TAGE[k.tag]} ${stunden(k.stunde)} · ${GROESSE_NAME[o.groesse]}</b>
    ${k.fest ? html`<button class="zu-k" title=${t('Schließen')} @click=${() => p.kachelWeg(true)}>✕</button>` : html`<span class="leise">${zeitraum(o.tage)}</span>`}</div>`;
  const inhalt = k.fehler ? html`<div class="kp-werte">${t('Nicht abrufbar: {fehler}', { fehler: k.fehler })}</div>`
    : !d ? html`<div class="kp-werte">${t('lädt …')}</div>`
    : html`<div class="kp-werte">Median <b>${zahl(d.median, 1)} ${d.einheit}</b> · ${t('niedrigste {min} · höchste {max}', { min: zahl(d.min, 1), max: zahl(d.max, 1) })} · ${t('{n} gezählt', { n: d.anzahl })}${d.belastet ? ` · ${t('{n} belastet', { n: d.belastet })} (${t(BELASTET_KURZ[o.grundlast])})` : ''}</div>
      <div class="kp-liste"><table class="t"><tr><th>${t('Wann')}</th><th>Server</th><th class="r">${d.einheit}</th><th>${t('Netz')}</th><th class="r">Signal</th><th class="r">${t('Grundlast')}</th><th></th></tr>
        ${d.messungen.map((m) => html`<tr class=${m.gewicht ? '' : 'belastet'}><td>${zeit(m.t)}</td><td>${m.server ?? '–'}</td><td class="r">${zahl(m.wert)}</td>
          <td>${m.netz ?? '–'}</td><td class="r">${m.rsrp != null ? zahl(m.rsrp) : '–'}</td>
          <td class="r">${zahl(m.last, 1)}</td><td>${m.belastet ? html`<span class="badge amber-b">${t(BELASTET_KURZ[o.grundlast])}</span>` : nothing}</td></tr>`)}
      </table></div>${d.weitere ? html`<div class="leise">${t('… und {n} ältere', { n: d.weitere })}</div>` : nothing}`;
  return html`<div class="kpop glas-panel ${k.fest ? 'fest' : ''}" role="dialog" aria-label=${`${t('Messungen')} ${TAGE[k.tag]} ${stunden(k.stunde)}`}>${kopf}${inhalt}</div>`;
}

const WOCHENTAGE = [merke('alle Montage'), merke('alle Dienstage'), merke('alle Mittwoche'), merke('alle Donnerstage'), merke('alle Freitage'),
  merke('alle Samstage'), merke('alle Sonntage')];
const GROESSE_NAME = { down: 'Download', up: 'Upload', ping: 'Ping' };

/** „2026-10-22“ → „Do 22.10.“, dazu „(heute)“/„(gestern)“ nach `vor_tagen` der Integration (Zeitzone von HA). */
function datumText(iso, vorTagen) {
  const d = new Date(`${iso}T12:00`);
  return `${datum(d)}${vorTagen === 0 ? ` (${t('heute')})` : vorTagen === 1 ? ` (${t('gestern')})` : ''}`;
}

/** WU-0004 (Mockup netzwerk.html · Tagesverlauf): Median je Stunde, Band niedrigste bis höchste Messung, Tarif.
 *  Median, Spanne, beste und schwächste Stunde rechnet die Integration; hier wird nur gezeichnet. */
function tagesverlauf(p, d) {
  const o = p._opt.speedtest, v = d.verlauf, ein = d.einheit;
  const offen = o.datum || o.tag != null;
  const wahl = html`<div class="leiste">
    ${seg(wochentage(true).map((x, i) => [i, x]), o.datum ? null : o.tag, (i) => p.setze('speedtest', { tag: i, datum: null, stunde: null }))}
    <select style="font-size:12px;padding:5px 8px" @change=${(e) => p.setze('speedtest', { datum: e.target.value || null, tag: null, stunde: null })}>
      <option value="" ?selected=${!o.datum}>${t('oder Datum …')}</option>
      ${d.tage_liste.map((x) => html`<option value=${x.datum} ?selected=${o.datum === x.datum}>${datumText(x.datum, x.vor_tagen)} · ${t(x.anzahl === 1 ? '{n} Messung' : '{n} Messungen', { n: x.anzahl })}</option>`)}
      ${o.datum && !d.tage_liste.some((x) => x.datum === o.datum) ? html`<option value=${o.datum} selected>${datumText(o.datum)} · ${t('keine Messung')}</option>` : nothing}
    </select>
    ${offen ? html`<button class="chip glas-panel" title=${t('Verlauf schließen')} @click=${() => p.setze('speedtest', { tag: null, datum: null, stunde: null })}>✕</button>` : nothing}
  </div>`;
  if (!offen) {
    return html`<div class="tv"><div class="gruppe">${t('Tagesverlauf')}</div>${wahl}
      <p class="hinweis">${t('Tipp auf einen Wochentag (auch links im Raster) oder wähle ein Datum: Median je Stunde, dazu die niedrigste und höchste Messung.')}</p></div>`;
  }
  // Antwort zur Auswahl noch unterwegs (oder passt nicht mehr): nur die Auswahl zeigen
  if (!v || (o.datum ? v.datum !== o.datum : v.tag !== o.tag)) {
    return html`<div class="tv"><div class="gruppe">${t('Tagesverlauf')}</div>${wahl}<div class="leer">${p._laedt ? t('lädt …') : t('Verlauf nicht geladen.')}</div></div>`;
  }
  const s = v.stunden, mit = s.map((x, h) => [h, x]).filter(([, x]) => x.anzahl);
  const titel = o.datum ? datumText(o.datum, d.tage_liste.find((x) => x.datum === o.datum)?.vor_tagen) : `${t(WOCHENTAGE[o.tag])} · ${zeitraum(o.tage)}`;
  const kopf = html`<div class="gruppe">${t('Tagesverlauf')} · ${GROESSE_NAME[d.groesse]} · ${titel}</div>`;
  if (!mit.length) return html`<div class="tv">${kopf}${wahl}<div class="leer">${t('An diesem Tag keine gezählte Messung.')}</div></div>`;
  const W = 720, H = 230, L = 40, R = 10, O = 14, U = 26, B = W - L - R, HH = H - O - U, sw = B / 24;
  const tarif = d.groesse !== 'ping' ? d.tarif : null;
  const ymax = Math.ceil((Math.max(tarif || 0, ...mit.map(([, x]) => x.max)) * 1.08) / 10) * 10 || 10;
  const x = (h) => L + (h + 0.5) * sw, y = (w) => O + HH - (w / ymax) * HH;
  const stuecke = (ok) => {
    const out = [];
    let cur = [];
    s.forEach((w, h) => { if (w.anzahl && ok(w)) cur.push(h); else { if (cur.length) out.push(cur); cur = []; } });
    if (cur.length) out.push(cur);
    return out;
  };
  // Band: bei einer einzelnen Stunde ein schmaler Balken, sonst die Fläche zwischen niedrigster und höchster Messung
  const band = stuecke((w) => w.max > w.min).map((st) => {
    const b = st.length === 1 ? 5 : 0;
    const oben = st.map((h, i) => `${x(h) - (i === 0 ? b : 0)},${y(s[h].max)}${st.length === 1 ? ` ${x(h) + b},${y(s[h].max)}` : ''}`);
    const unten = [...st].reverse().map((h, i) => `${x(h) + (i === 0 ? b : 0)},${y(s[h].min)}${st.length === 1 ? ` ${x(h) - b},${y(s[h].min)}` : ''}`);
    return svg`<path class="band" d=${`M${[...oben, ...unten].join(' L')} Z`}></path>`;
  });
  const alle = mit.map(([h, w]) => `${x(h)},${y(w.median)}`).join(' ');
  // geglätteter Mittelwert (Integration, ±1 Stunde): durchgehend, wo er einen Wert hat
  const glatt = [];
  let lauf = [];
  s.forEach((w, h) => { if (w.glatt != null) lauf.push(`${x(h)},${y(w.glatt)}`); else { if (lauf.length > 1) glatt.push(lauf); lauf = []; } });
  if (lauf.length > 1) glatt.push(lauf);
  const linien = stuecke(() => true).filter((st) => st.length > 1).map((st) => svg`<polyline class="med" points=${st.map((h) => `${x(h)},${y(s[h].median)}`).join(' ')}></polyline>`);
  const st = o.stunde, gew = st != null ? s[st] : null;
  const anzahl = (n) => t(n === 1 ? '{n} Messung' : '{n} Messungen', { n });
  const info = st != null
    ? gew.anzahl
      ? html`<b>${stunden(st)}:</b> Median <b>${zahl(gew.median)} ${ein}</b>${gew.anzahl > 1 ? ` · ${t('niedrigste {min} · höchste {max}', { min: zahl(gew.min), max: zahl(gew.max) })}` : ''} · ${anzahl(gew.anzahl)}${gew.glatt != null ? ` · ${t('geglättet {wert}', { wert: zahl(gew.glatt) })}` : ''}`
      : html`<b>${stunden(st)}:</b> ${t('keine Messung')}`
    : html`<span class="leise">${v.beste != null ? `${t('Beste Stunde {stunde} ({wert})', { stunde: stunden(v.beste), wert: `${zahl(s[v.beste].median)} ${ein}` })} · ${t('schwächste {stunde} ({wert})', { stunde: stunden(v.schwaechste), wert: `${zahl(s[v.schwaechste].median)} ${ein}` })} · ` : ''}${t('Tipp auf eine Stunde zeigt die Werte')}</span>`;
  return html`<div class="tv">${kopf}${wahl}
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label=${`${t('Tagesverlauf')} ${GROESSE_NAME[d.groesse]}`}>
      ${[0, 0.25, 0.5, 0.75, 1].map((f) => svg`<line class="gitter" x1=${L} x2=${W - R} y1=${y(ymax * f)} y2=${y(ymax * f)}></line><text x=${L - 6} y=${y(ymax * f) + 4} text-anchor="end">${zahl(ymax * f)}</text>`)}
      ${tarif ? svg`<line class="tarif" x1=${L} x2=${W - R} y1=${y(tarif)} y2=${y(tarif)}></line><text x=${W - R - 4} y=${y(tarif) - 5} text-anchor="end">${t('Tarif {wert}', { wert: zahl(tarif) })}</text>` : nothing}
      ${st != null ? svg`<rect class="wahl" x=${L + st * sw} y=${O} width=${sw} height=${HH} rx="3"></rect>` : nothing}
      ${band}
      ${mit.length > 1 ? svg`<polyline class="med luecke" points=${alle}></polyline>` : nothing}
      ${linien}
      ${glatt.map((l) => svg`<polyline class="glatt" points=${l.join(' ')}></polyline>`)}
      ${mit.map(([h, w]) => svg`<circle class="pkt" cx=${x(h)} cy=${y(w.median)} r=${st === h ? 5 : 3}></circle>`)}
      ${[0, 3, 6, 9, 12, 15, 18, 21].map((h) => svg`<text x=${L + h * sw} y=${H - 8} text-anchor="middle">${h}</text>`)}
      ${svg`<text x=${W - R} y=${H - 8} text-anchor="end">${t('{n} Uhr', { n: 24 })}</text>`}
      ${s.map((w, h) => svg`<rect class="h" x=${L + h * sw} y=${O} width=${sw} height=${HH} @click=${() => p.setze('speedtest', { stunde: st === h ? null : h }, false)}><title>${stunden(h)}: ${w.anzahl ? `Median ${zahl(w.median)} ${ein} · ${zahl(w.min)}–${zahl(w.max)} · ${anzahl(w.anzahl)}` : t('keine Messung')}</title></rect>`)}
    </svg>
    <div class="info">${info}</div>
    <div class="legende"><span><i class="l-med"></i>${t('Median je Stunde')}</span><span><i class="l-glatt"></i>${t('Mittelwert geglättet (3 h)')}</span><span><i class="l-band"></i>${t('niedrigste bis höchste Messung')}</span><span><i class="l-luecke"></i>${t('Stunden ohne Messung überbrückt')}</span>${tarif ? html`<span><i class="l-tarif"></i>${t('Tarif')}</span>` : nothing}<span>${ein}</span></div>
    ${o.datum ? html`<p class="hinweis">${t('Ein einzelner Tag hat meist nur wenige Messungen (Messplan) – Stunden ohne Messung bleiben leer, bei einer Messung gibt es kein Band.')}</p>` : nothing}
  </div>`;
}

