// Reiter „Geräte“: Liste mit 24-h-Streifen, Filter und Suche (nur Anzeige); Einblendung je Gerät mit 7 Tagen.
// WU-0009: WLAN steht hier als Umschalter „Geräte | WLAN“ (vorher unter „Funk“).
// WU-0010: im Fenster eines Geräts eigene Arten in der Auswahl samt „＋ eigene Art …“ und die Zeile „🔔 Bei offline
// warnen“ (wie Gruppe · immer · nie) – was die Gruppe sagt, liefert die Integration (heimnetz/geraet → warnen).
import { html, nothing } from 'lit';
import { live } from 'lit/directives/live.js';
import { zahl, zeit, tag, punkt } from '../format.js';
import { merke, t, tl } from '../sprache.js';
import { seg, streifen } from './teile.js';
import { wlan } from './wlan.js';
import { artFormular } from './warnungen.js';

export const TEILE = [['geraete', merke('Geräte')], ['wlan', merke('WLAN')]];

/** Reiter „Geräte“ mit Umschalter; geladen wird nur der gewählte Teil (heimnetz/geraete oder heimnetz/wlan). */
export function geraeteReiter(p, d) {
  const teil = p._opt.geraete.teil;
  return html`<div class="leiste">${seg(tl(TEILE), teil, (v) => p.setze('geraete', { teil: v }), false)}</div>
    ${!d ? html`<div class="glas-panel block"><div class="leer">${t('lädt …')}</div></div>` : teil === 'wlan' ? wlan(p, d) : geraete(p, d)}`;
}

const FILTER = [['alle', merke('Alle')], ['online', 'Online'], ['offline', 'Offline'], ['auff', merke('Auffällig')]];
// AN-0001 (Mockup netzwerk.html · Geräte kompakt, Variante D): eine Zeile je Gerät, Punkt statt Abzeichen
const PUNKT = { an: ['', 'online'], aus: ['grau', 'offline'], neu: ['blau', merke('neu')], wackelt: ['amber', merke('wackelt')] };
const ZU = 'WLAN, nicht verbunden'; // anfangs zugeklappt: feste Kennung der Gruppe (name); angezeigt wird ihr text
const NACH = [['verb', merke('nach Verbindung')], ['art', merke('nach Art')]];
const SYMBOL = { LAN: '🔌', WLAN: '📶', Powerline: '⚡' };
const WARNEN = [['gruppe', merke('wie Gruppe')], ['immer', merke('immer')], ['nie', merke('nie')]];
const NEU = 'neu'; // Wert „＋ eigene Art …“ in der Auswahl (keine Art)

function passt(g, filter, suche) {
  if (filter === 'online' && !g.aktiv) return false;
  if (filter === 'offline' && g.aktiv) return false;
  if (filter === 'auff' && !['neu', 'wackelt'].includes(g.einstufung)) return false;
  return !suche || `${g.name} ${g.ip}`.toLowerCase().includes(suche.toLowerCase());
}

export function geraete(p, d) {
  const o = p._opt.geraete;
  const liste = d.geraete.filter((g) => passt(g, o.filter, o.suche));
  const nachArt = o.nach === 'art';
  return html`<div class="glas-panel block">
    <div class="block-kopf"><h3>${t('Geräte im Heimnetz')}</h3><span class="leise">${t('{n} von {gesamt} online · letzte 24 h', { n: d.online, gesamt: d.bekannt })}</span></div>
    <div class="leiste">${seg(tl(NACH), o.nach || 'verb', (v) => p.setze('geraete', { nach: v }, false))}</div>
    <div class="leiste">${seg(tl(FILTER), o.filter, (v) => p.setze('geraete', { filter: v }, false))}
      <input class="suche" placeholder=${t('Suchen (Name oder IP)')} .value=${o.suche} @input=${(e) => p.setze('geraete', { suche: e.target.value }, false)}></div>
    ${!d.box_erreichbar ? html`<p class="fein">${t('Die FRITZ!Box antwortet nicht – die Liste zeigt den letzten bekannten Stand.')}</p>` : nothing}
    ${liste.length ? (nachArt ? d.gruppen_art || [] : d.gruppen || []).map((gr) => gruppe(p, gr, liste.filter((g) => (nachArt ? g.kat : g.verbindung) === gr.name), nachArt))
      : html`<div class="leer">${t('Kein Gerät passt.')}</div>`}
    <div class="gk-achse"><span></span><div class="achse"><span>${t('vor {n} h', { n: 24 })}</span><span>${t('jetzt')}</span></div></div>
    <p class="hinweis">${t('Punkt: grün online, grau offline, amber wackelt, blau neu. Streifen: grün = im Heimnetz, schraffiert = keine Aufzeichnung. Das WLAN-Band kennt die Box nur bei verbundenen Geräten. „🔐 VPN (WireGuard)“ sind Geräte, die sich von unterwegs über VPN mit deiner Box verbinden. Tippen öffnet den Verlauf.')}</p>
  </div>`;
}

function gruppe(p, gr, geraete, nachArt) {
  if (!geraete.length) return nothing;
  const zu = p._opt.geraete.zu || [ZU];
  const offen = !zu.includes(gr.name);
  const umschalten = (e) => {
    e.preventDefault();
    p.setze('geraete', { zu: offen ? [...zu, gr.name] : zu.filter((n) => n !== gr.name) }, false);
  };
  return html`<details class="ggr" ?open=${offen}><summary @click=${umschalten}><span>${gr.text || gr.name}</span><span>${t('{n} von {gesamt} online', { n: gr.online, gesamt: gr.gesamt })} ${offen ? '▾' : '▸'}</span></summary>
    ${offen ? geraete.map((g) => zeile(p, g, nachArt)) : nothing}</details>`;
}

function zeile(p, g, nachArt) {
  const [farbe, schluessel] = PUNKT[g.einstufung] ?? ['grau', g.einstufung];
  const wort = t(schluessel);
  // volle IP; nach Art zusätzlich die Verbindung, nach Verbindung nur das Band
  const zusatz = nachArt ? g.band || g.art : g.band;
  return html`<div class="geraet gk" @click=${() => p.geraetOeffnen(g.id)}>
    <span>${SYMBOL[g.art.split(' ')[0]] ?? '•'}</span>
    <span class="n">${g.name}<small>${g.ip || '–'}${zusatz ? ` · ${zusatz}` : ''}</small></span>
    ${streifen(g.streifen)}<span class="punkt ${farbe}" title=${wort} aria-label=${wort}></span></div>`;
}

export function geraetBlatt(p, b) {
  const kopf = html`<div class="griff"></div><button class="zu" @click=${() => p.zu()}>✕</button>`;
  if (b.laedt) return html`${kopf}<div class="leer">${t('lädt …')}</div>`;
  if (b.fehler) return html`${kopf}<p class="fein">${b.fehler}</p>`;
  const g = b.daten;
  return html`${kopf}
    <h3>${g.name}</h3>
    <div class="leise">${g.ip || '–'} · ${g.art} · ${t('Adresse {quelle}', { quelle: g.quelle })}${g.zufallsadresse ? ` · ${t('Zufalls-Adresse')}` : ''}${g.zuerst ? ` · ${t('zuerst gesehen {tag}', { tag: tag(g.zuerst) })}` : ''}</div>
    ${g.kategorien ? html`<div class="zeile ga-zeile"><span>${t('Art')} <span class="leise">· ${g.art_quelle}</span></span>${p.istAdmin
      ? html`<select class="ga-wahl" .value=${live(g.art_selbst ? g.kat : 'auto')} @change=${(e) => {
          if (e.target.value !== NEU) { p.geraetArt(g.id, e.target.value === 'auto' ? null : e.target.value); return; }
          p._blatt = { ...b, eigenNeu: true }; // Auswahl springt beim Zeichnen zurück (live)
        }}>
          <option value="auto">${t('automatisch')}</option>
          ${g.kategorien.map((k) => html`<option value=${k.name}>${k.text}</option>`)}
          <option value=${NEU}>${t('＋ eigene Art …')}</option></select>`
      : html`<span class="leise">${(g.kategorien.find((k) => k.name === g.kat) || {}).text || g.kat}</span>`}</div>` : nothing}
    ${b.eigenNeu && p.istAdmin ? html`${artFormular({ platz: t('Name der Art, z. B. Baustelle'), knopf: t('Anlegen'), los: (s, n) => p.artNeu(s, n, g.id), weg: () => { p._blatt = { ...b, eigenNeu: false }; } })}
      <p class="hinweis">${t('Eigene Arten erscheinen unter Geräte › nach Art und in ⚙ › Warnungen; umbenennen und löschen unter ⚙ › 🏷️ Arten.')}</p>` : nothing}
    ${g.warnen ? warnZeile(p, g) : nothing}
    <div class="glas-raster" style="grid-template-columns:repeat(3,1fr)">
      <div class="glas-panel block" style="padding:10px"><span class="glas-klein">${t('online 7 Tage')}</span><span class="glas-wert">${g.online_anteil == null ? '–' : zahl(g.online_anteil * 100)}<small> %</small></span></div>
      <div class="glas-panel block" style="padding:10px"><span class="glas-klein">${t('Abbrüche')}</span><span class="glas-wert">${g.abbrueche}</span></div>
      <div class="glas-panel block" style="padding:10px"><span class="glas-klein">${t('jetzt')}</span><span class="glas-wert" style="font-size:18px">${g.aktiv ? 'online' : 'offline'}</span></div>
    </div>
    <div class="gruppe">${t('Letzte 7 Tage')}</div>
    ${g.tage.map((x) => html`<div style="display:flex;gap:10px;align-items:center;font-size:12px"><span class="leise" style="width:66px">${tag(x.tag)}</span>${streifen(x.streifen)}</div>`)}
    <div class="achse" style="padding-left:76px"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>
    <div class="gruppe">${t('Ereignisse')}</div>
    ${g.ereignisse.length ? g.ereignisse.map((e) => html`<div class="ereig"><span class="punkt ${punkt(e.stufe)}"></span><time>${zeit(e.t)}</time><span>${e.text}</span></div>`)
      : html`<div class="leer">${t('Keine Ereignisse in den letzten 7 Tagen.')}</div>`}`;
}

/** WU-0010: „🔔 Bei offline warnen“ – Ausnahme des Geräts; ohne Ausnahme gilt der Schalter seiner Art. */
function warnZeile(p, g) {
  const w = g.warnen;
  const unter = w.wert !== 'gruppe' ? t('eigene Einstellung') : w.gruppe ? t('wie Gruppe (an)') : t('wie Gruppe (aus)');
  const wort = { gruppe: w.gruppe ? t('wie Gruppe (an)') : t('wie Gruppe (aus)'), immer: t('immer'), nie: t('nie') }[w.wert];
  return html`<div class="zeile ga-zeile ga-warnen"><span>${t('🔔 Bei offline warnen')} <span class="leise">· ${unter}</span></span>${p.istAdmin
    ? seg(tl(WARNEN), w.wert, (v) => v !== w.wert && p.warnungGeraet(g.id, v))
    : html`<span class="leise">${wort}</span>`}</div>`;
}
