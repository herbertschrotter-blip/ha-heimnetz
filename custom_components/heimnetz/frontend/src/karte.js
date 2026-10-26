// Karte „Wo steht der Mast?“ mit Leaflet (WU-0002, Mockup abgenommen 14.10.2026): zoomen (＋/−, Mausrad, zwei Finger),
// ziehen zum Verschieben, ⌖ zeigt wieder alles; oben rechts die Grundlage. Alle Orte und der Rahmen kommen fertig von
// der Integration – hier wird nur gezeichnet. CARTO fällt weg (verlangt seit 2026 einen Schlüssel); die Grundlagen
// basemap.at und OpenStreetMap brauchen keinen. Die Kacheln lädt der Browser; der Anbieter sieht nur den Ausschnitt.
import { LitElement, html, css, unsafeCSS } from 'lit';
import Leaflet from 'leaflet/dist/leaflet.js';  // verkleinerte Fassung: die Seite bleibt klein
import LEAFLET from './leaflet-stil.js';
import { merke, t } from './sprache.js';

// Leaflet setzt beim Laden window.L – zurückgeben, damit ein Leaflet anderer Karten in HA unberührt bleibt
const L = Leaflet.noConflict();

const BASEMAP = (ebene) => `https://mapsneu.wien.gv.at/basemap/${ebene}/normal/google3857/{z}/{y}/{x}.png`;
const QUELLE_BASEMAP = () => `${t('Grundkarte')}: <a href="https://basemap.at" target="_blank" rel="noopener">basemap.at</a>`;
export const GRUNDLAGEN = {
  bmap: { url: BASEMAP('geolandbasemap'), quelle: QUELLE_BASEMAP },
  grau: { url: BASEMAP('bmapgrau'), quelle: QUELLE_BASEMAP },
  osm: {
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    quelle: () => `© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>${t('-Mitwirkende')}`,
  },
}; // Quellenangabe als Funktion: in der Sprache der Seite
export const WAHL = { auto: merke('Automatisch'), bmap: 'basemap.at', grau: merke('basemap.at grau'), osm: 'OpenStreetMap' };
const SPEICHER = 'heimnetz.karte.grundlage';
const SPEICHER_OSM = 'heimnetz.karte.osm';  // Ebene „Masten (OSM)“ an/aus, Vorgabe an
// WU-0006: bis 0.22.0 hieß die Integration „netzwerk“ – gemerkte Wahl von dort gilt weiter, bis neu gewählt wird
const lesen = (schluessel) => localStorage.getItem(schluessel) ?? localStorage.getItem(schluessel.replace(/^heimnetz\./, 'netzwerk.'));
const QUELLE_OSM_MASTEN = () => `${t('Masten')} © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>${t('-Mitwirkende')}`;
const NAH = 15;  // ab dieser Zoomstufe stehen die Zellnamen an der Karte
// Farben aus den Variablen der Seite (wie die Legende); SVG-Attribute von Leaflet kennen keine CSS-Variablen
const FARBEN = { blau: ['--blau', '#64a8ff'], amber: ['--amber', '#ff9f0a'], grau: ['--ink2', '#8e8e93'], ring: ['--ink', '#ffffff'] };

/** Ebene „Masten (OSM)“ an? (für die Legende außerhalb der Karte) */
export function osmGemerkt() {
  try { return lesen(SPEICHER_OSM) !== 'aus'; } catch { return true; }
}

function gemerkt() {
  try { const w = lesen(SPEICHER); return Object.hasOwn(WAHL, w ?? '') ? w : 'auto'; } catch { return 'auto'; }
}
const sicher = (t) => String(t ?? '').replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

/** Welche Kacheln bei welcher Wahl: automatisch hell → basemap.at, dunkel → basemap.at grau, abgedunkelt. */
export function grundlage(wahl, dunkel) {
  if (wahl === 'auto') return { ...GRUNDLAGEN[dunkel ? 'grau' : 'bmap'], abdunkeln: dunkel };
  return { ...(Object.hasOwn(GRUNDLAGEN, wahl) ? GRUNDLAGEN[wahl] : GRUNDLAGEN.bmap), abdunkeln: false };
}

export class HeimnetzKarte extends LitElement {
  // `sprache` nur, damit die Karte bei einem Wechsel der Sprache neu beschriftet
  static properties = { daten: { attribute: false }, dunkel: { type: Boolean }, sprache: { attribute: false }, _wahl: { state: true }, _osm: { state: true }, _voll: { state: true }, _info: { state: true } };

  static styles = [unsafeCSS(LEAFLET), css`
    :host { display: block; }
    .rahmen { position: relative; border-radius: 16px; overflow: hidden; }
    #karte { width: 100%; aspect-ratio: 15 / 8; min-height: 240px; background: rgba(127,127,127,.15); }
    .kachel-dunkel { filter: invert(1) hue-rotate(180deg) brightness(.9) contrast(.9); }
    .k-zoom { position: absolute; left: 10px; top: 10px; z-index: 500; display: flex; flex-direction: column; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
    /* deckend: auf heller wie dunkler Grundlage gut lesbar */
    .k-zoom button { width: 34px; height: 34px; border: 0; font: inherit; font-size: 18px; cursor: pointer; background: rgba(28,28,30,.88); color: #fff; }
    .k-zoom button + button { border-top: 1px solid rgba(255,255,255,.18); }
    /* Vollbild: über die ganze Seite (Fullscreen-API, sonst fest über dem Fenster) */
    .rahmen.voll, .rahmen:fullscreen { position: fixed; inset: 0; z-index: 9999; border-radius: 0; background: #111; }
    .rahmen.voll #karte, .rahmen:fullscreen #karte { aspect-ratio: auto; height: 100%; min-height: 0; }
    .k-voll-zu { position: absolute; left: 50%; transform: translateX(-50%); top: 10px; z-index: 600; font: inherit; font-size: 14px; padding: 6px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(28,28,30,.88); color: #fff; cursor: pointer; }
    .k-info { position: absolute; left: 10px; right: 10px; bottom: 26px; z-index: 600; display: flex; flex-direction: column; gap: 3px; padding: 10px 36px 10px 12px; border-radius: 12px; background: rgba(28,28,30,.92); color: #fff; font-size: 13px; }
    .k-info .leise { color: rgba(255,255,255,.65); } .k-info .passt { color: var(--amber, #ff9f0a); }
    .k-info-zu { position: absolute; right: 6px; top: 4px; background: none; border: 0; color: #fff; font-size: 16px; cursor: pointer; }
    .osm-dreieck { cursor: pointer; }
    .k-osm { position: absolute; right: 10px; top: 48px; z-index: 500; font: inherit; font-size: 13px; padding: 6px 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(28,28,30,.88); color: rgba(255,255,255,.6); cursor: pointer; }
    .k-osm.an { color: #fff; border-color: var(--amber, #ff9f0a); }
    .osm-dreieck { position: relative; width: 16px; height: 15px; background: #8e8e93; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
    .osm-dreieck.passt { width: 22px; height: 20px; background: var(--amber, #ff9f0a); }
    .osm-dreieck.passt::after { content: ''; position: absolute; inset: 4px 4px 2px; background: #8e8e93; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
    .k-lage { position: absolute; right: 10px; top: 10px; z-index: 500; font: inherit; font-size: 13px; padding: 6px 8px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(28,28,30,.88); color: #fff; }
    /* Beschriftungen als Tooltips: Leaflet legt sie selbst links oder rechts, je nachdem wo Platz ist */
    .leaflet-tooltip.k-name { background: none; border: 0; box-shadow: none; padding: 0 14px; font-size: 13px; font-weight: 600; color: #fff; white-space: nowrap; text-shadow: 0 0 3px rgba(0,0,0,.9), 0 0 2px rgba(0,0,0,.9); }
    .leaflet-tooltip.k-name::before { display: none; }
    .leaflet-tooltip.k-name.klein { font-size: 11px; font-weight: 500; padding: 0 8px; }
    /* Zellnamen erst beim Hineinzoomen – weiter weg liegen sie aufeinander */
    .leaflet-container:not(.nah) .leaflet-tooltip.klein { display: none; }
    .leaflet-container { font: inherit; }
    .leaflet-control-attribution { font-size: 10px; }
  `];

  constructor() {
    super();
    this._wahl = gemerkt();
    this._osm = osmGemerkt();
    this._voll = false;
    this._info = null;
    this._karte = null;
    this._gezeigt = false;
  }

  render() {
    const info = this._osm && this._info !== null ? this.daten?.osm?.[this._info] : null;
    return html`<div class="rahmen ${this._voll ? 'voll' : ''}">
      ${this._voll ? html`<button class="k-voll-zu" title=${t('Vollbild schließen')} @click=${() => this._vollbild(false)}>✕</button>` : ''}
      <div id="karte" role="img" aria-label=${t('Karte: Wohnung, Zellen und geschätzter Mast')}></div>
      <div class="k-zoom">
        <button title=${t('Näher')} aria-label=${t('Näher')} @click=${() => this._karte?.zoomIn()}>＋</button>
        <button title=${t('Weiter weg')} aria-label=${t('Weiter weg')} @click=${() => this._karte?.zoomOut()}>−</button>
        <button title=${t('Alles zeigen')} aria-label=${t('Alles zeigen')} @click=${() => this._alles()}>⌖</button>
        <button title=${this._voll ? t('Vollbild schließen') : t('Vollbild')} aria-label=${t('Vollbild')} @click=${() => this._vollbild(!this._voll)}>⛶</button>
      </div>
      ${this.daten?.osm?.length ? html`<button class="k-osm ${this._osm ? 'an' : ''}" title=${t('Funkmasten aus OpenStreetMap ein/aus')} aria-pressed=${this._osm ? 'true' : 'false'} @click=${() => this._osmUmschalten()}>📡 ${t('Masten (OSM)')}</button>` : ''}
      ${info ? this._infofeld(info) : ''}
      <select class="k-lage" title=${t('Kartengrundlage')} @change=${(e) => this._waehlen(e.target.value)}>
        ${Object.entries(WAHL).map(([k, name]) => html`<option value=${k} ?selected=${k === this._wahl}>🗺️ ${t(name)}</option>`)}
      </select>
    </div>`;
  }

  willUpdate(geaendert) {
    // andere Mastliste: der gemerkte Index zeigte sonst auf einen anderen Mast
    if (geaendert.has('daten') && JSON.stringify(this.daten?.osm || []) !== this._osmText) this._info = null;
  }

  updated(geaendert) {
    const neu = !this._karte && this._anlegen();
    if (!this._karte) return;
    const sprache = geaendert.has('sprache') && geaendert.get('sprache') !== undefined;  // Wechsel, nicht das erste Setzen
    if (neu || sprache || geaendert.has('_wahl') || geaendert.has('dunkel')) this._grundlage();
    if (neu || sprache || geaendert.has('daten') || geaendert.has('dunkel')) this._zeichnen();
    const osmText = JSON.stringify(this.daten?.osm || []);  // die Masten ändern sich selten: nur dann neu zeichnen
    if (neu || sprache || geaendert.has('_osm') || geaendert.has('_wahl') || osmText !== this._osmText) {
      this._osmText = osmText;
      this._osmZeichnen();
    }
    this._erstesMal();
  }

  /** Den Rahmen der Integration zeigen, sobald Daten da sind und die Karte eine Größe hat (sonst zeigt Leaflet die
   *  ganze Welt); danach bleibt die Ansicht des Nutzers, bis er ⌖ drückt. */
  _erstesMal() {
    const ziel = this.renderRoot.querySelector('#karte');
    if (this._gezeigt || !this.daten || !ziel || !ziel.clientWidth) return;
    this._karte.invalidateSize();
    this._alles();
    this._gezeigt = true;
  }

  disconnectedCallback() {  // HA hängt die Seite aus, wenn die App im Hintergrund ist
    super.disconnectedCallback();
    document.removeEventListener('fullscreenchange', this._vollAus);
    document.removeEventListener('keydown', this._esc);
    if (document.fullscreenElement && this.renderRoot.contains(document.fullscreenElement)) document.exitFullscreen?.().catch(() => {});
    this._voll = false;
    this._info = null;
    this._beobachter?.disconnect();
    this._karte?.remove();
    this._karte = this._kacheln = this._ebene = this._osmEbene = this._osmText = this._osmQuelle = null;
    this._gezeigt = false;
  }

  connectedCallback() {
    super.connectedCallback();
    // Vollbild mit Zurück-Taste oder Esc verlassen: Zustand mitziehen
    this._vollAus ??= () => { if (!document.fullscreenElement && this._voll) { this._voll = false; this.updateComplete.then(() => this._karte?.invalidateSize()); } };
    document.addEventListener('fullscreenchange', this._vollAus);
    // Vollbild ohne Fullscreen-API (fest über dem Fenster): Esc schließt
    this._esc ??= (e) => { if (e.key === 'Escape' && this._voll) this._vollbild(false); };
    document.addEventListener('keydown', this._esc);
    if (this.hasUpdated) this.requestUpdate();  // wieder eingehängt: Karte neu anlegen
  }

  _anlegen() {
    const ziel = this.renderRoot.querySelector('#karte');
    if (!ziel) return false;
    this._karte = L.map(ziel, { zoomControl: false, attributionControl: true });
    this._karte.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');
    L.control.scale({ imperial: false, position: 'bottomleft' }).addTo(this._karte);
    // eigene Ebene unter Zellen, Mast und Wohnung (die liegen als Kreise in der overlayPane, zIndex 400)
    this._karte.createPane('osm').style.zIndex = 350;
    this._osmEbene = L.layerGroup().addTo(this._karte);
    this._ebene = L.layerGroup().addTo(this._karte);
    this._karte.on('zoomend', () => this._nah());
    if (typeof ResizeObserver !== 'undefined') {
      this._beobachter = new ResizeObserver(() => { this._karte?.invalidateSize(); this._erstesMal(); });
      this._beobachter.observe(ziel);
    }
    return true;
  }

  _grundlage() {
    const g = grundlage(this._wahl, this.dunkel);
    this._kacheln?.remove();
    this._kacheln = L.tileLayer(g.url, { maxZoom: 19, attribution: g.quelle(), className: g.abdunkeln ? 'kachel-dunkel' : '' }).addTo(this._karte);
  }

  _waehlen(wahl) {
    this._wahl = wahl;
    try { localStorage.setItem(SPEICHER, wahl); } catch { /* privates Fenster: nur für jetzt */ }
  }

  /** Infofeld zu einem angetippten Mast (Werte kommen fertig von der Integration). */
  _infofeld(o) {
    const zu = () => { this._info = null; };
    return html`<div class="k-info" role="dialog" aria-label=${t('Funkmast')}>
      <button class="k-info-zu" title=${t('Schließen')} aria-label=${t('Schließen')} @click=${zu}>✕</button>
      <b>${t('Funkmast')} (OpenStreetMap)${o.betreiber ? ` · ${o.betreiber}` : ''}${o.passt ? html` · <span class="passt">${o.warum === 'lage' ? t('am nächsten am geschätzten Mast') : t('passt zur Entfernung laut Box')}</span>` : ''}</b>
      <span class="leise">${t('{entfernung} {richtung} von der Wohnung', { entfernung: o.entfernung, richtung: o.richtung })}</span>
      ${o.anbieter
        ? html`<span>📶 ${o.anbieter.join(' · ')}${o.technik?.length ? ` · ${o.technik.join(' · ')}` : ''}</span>
          <span class="leise">${t(o.zellen === 1 ? 'laut OpenCellID: {n} Zelle in höchstens 500 m – geschätzt, nicht amtlich' : 'laut OpenCellID: {n} Zellen in höchstens 500 m – geschätzt, nicht amtlich', { n: o.zellen })}</span>`
        : html`<span class="leise">${t('Anbieter und Technik unbekannt – OpenCellID kennt hier keine Zellen (oder es ist kein Schlüssel eingetragen). Im Senderkataster nachsehen.')}</span>`}
    </div>`;
  }

  /** Vollbild über die Fullscreen-API; wo sie fehlt (z. B. iPhone), fest über dem Fenster. */
  async _vollbild(an) {
    const rahmen = this.renderRoot.querySelector('.rahmen');
    this._voll = an;
    try {
      if (an && rahmen?.requestFullscreen && !document.fullscreenElement) await rahmen.requestFullscreen();
      else if (!an && document.fullscreenElement) await document.exitFullscreen();
    } catch { /* nicht erlaubt: bleibt beim festen Rahmen */ }
    await this.updateComplete;
    this._karte?.invalidateSize();
  }

  _osmUmschalten() {
    this._osm = !this._osm;
    if (!this._osm) this._info = null;
    try { localStorage.setItem(SPEICHER_OSM, this._osm ? 'an' : 'aus'); } catch { /* privates Fenster: nur für jetzt */ }
    // die Legende steht außerhalb der Karte: Bescheid geben, damit sie mitzieht
    this.dispatchEvent(new CustomEvent('osm-umgeschaltet', { detail: this._osm, bubbles: true, composed: true }));
  }

  /** Funkmasten aus OpenStreetMap: graue Dreiecke, der passende orange umrandet und beschriftet. */
  _osmZeichnen() {
    const e = this._osmEbene, liste = this.daten?.osm || [];
    if (!e) return;
    e.clearLayers();
    if (this._osmQuelle) this._karte.attributionControl.removeAttribution(this._osmQuelle);
    this._osmQuelle = null;
    if (!this._osm || !liste.length) return;
    // bei der Grundlage OpenStreetMap steht die Quelle schon da
    if (grundlage(this._wahl, this.dunkel).url !== GRUNDLAGEN.osm.url) {
      this._osmQuelle = QUELLE_OSM_MASTEN();  // genau dieser Text wird beim nächsten Zeichnen wieder entfernt
      this._karte.attributionControl.addAttribution(this._osmQuelle);
    }
    for (const [i, o] of liste.entries()) {
      const gross = o.passt ? [22, 20] : [16, 15];
      const m = L.marker(o.ort, {
        keyboard: false, zIndexOffset: o.passt ? 100 : 0, pane: 'osm', title: t('Funkmast – antippen für Infos'),
        icon: L.divIcon({ className: '', html: `<div class="osm-dreieck${o.passt ? ' passt' : ''}"></div>`, iconSize: gross, iconAnchor: [gross[0] / 2, gross[1] / 2] }),
      }).addTo(e);
      m.on('click', () => { this._info = this._info === i ? null : i; });
      if (o.passt) {
        m.bindTooltip(sicher(`${t('Funkmast')} (OSM) · ${o.entfernung} ${o.richtung} · ${t('passt')}`), {
          permanent: true, direction: 'auto', className: 'k-name', interactive: false,
        });
      }
    }
  }

  /** ⌖ und beim ersten Öffnen: der Rahmen der Integration (Ring, Masten, nahe Zellen). */
  _alles() {
    const d = this.daten;
    if (!this._karte || !d?.rahmen) return;
    const [s, w, n, o] = d.rahmen;
    this._karte.fitBounds([[s, w], [n, o]]);
  }

  /** Zellnamen erst ab Zoomstufe NAH (sonst liegen sie aufeinander). */
  _nah() {
    this._karte?.getContainer().classList.toggle('nah', this._karte.getZoom() >= NAH);
  }

  _zeichnen() {
    const d = this.daten, e = this._ebene;
    if (!e) return;
    e.clearLayers();
    if (!d || !d.wohnung) return;
    const stil = getComputedStyle(this);
    const f = Object.fromEntries(Object.entries(FARBEN).map(([k, [v, ersatz]]) => [k, stil.getPropertyValue(v).trim() || ersatz]));
    // Beschriftung an einem Punkt; „auto“: Leaflet legt sie auf die Seite, auf der in der Karte Platz ist
    const name = (lage, text, klein, richtung = 'auto') => lage.bindTooltip(sicher(text), {
      permanent: true, direction: richtung, offset: [0, richtung === 'top' ? -10 : 0],  // Abstand zur Seite: Rand im CSS (Leaflet zieht den Versatz links ab)
      className: `k-name${klein ? ' klein' : ''}`, interactive: false,
    });
    if (d.ring_m) L.circle(d.wohnung, { radius: d.ring_m, color: f.ring, weight: 1.5, opacity: .7, dashArray: '6 6', fill: false, interactive: false }).addTo(e);
    for (const p of d.punkte) {
      const c = p.anker ? f.blau : f.grau;
      if (p.genau_m) L.circle(p.ort, { radius: p.genau_m, color: c, weight: 1, opacity: .6, dashArray: '3 4', fillColor: c, fillOpacity: .08, interactive: false }).addTo(e);
      name(L.circleMarker(p.ort, { radius: 5, color: '#fff', weight: 1.5, fillColor: c, fillOpacity: 1, interactive: false }).addTo(e), p.name, true);
    }
    for (const m of d.masten) {
      L.polyline([d.wohnung, m.ort], { color: f.amber, weight: 3, interactive: false }).addTo(e);
      name(L.circleMarker(m.ort, { radius: 10, color: '#fff', weight: 2, fillColor: f.amber, fillOpacity: 1, interactive: false }).addTo(e),
        `${t('Mast {name}', { name: m.name })}${m.fuenf_g ? ' · 4G + 5G?' : ''} · ${m.entfernung}`, false);
    }
    name(L.circleMarker(d.wohnung, { radius: 9, color: '#fff', weight: 2, fillColor: f.blau, fillOpacity: 1, interactive: false }).addTo(e), t('Wohnung'), false, 'top');
    this._nah();
  }
}

if (!customElements.get('heimnetz-karte')) customElements.define('heimnetz-karte', HeimnetzKarte);
