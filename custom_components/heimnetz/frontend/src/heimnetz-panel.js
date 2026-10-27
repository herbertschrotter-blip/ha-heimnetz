// Seite „Heimnetz“ in der Seitenleiste (Lit, HA-Grundsatz G-22). Gestaltung nach dem abgenommenen Mockup
// mockups/netzwerk.html. Die Seite rechnet nichts Fachliches: alle Daten kommen fertig über die WebSocket-Befehle
// `heimnetz/*` der Integration; hier wird nur dargestellt und bedient.
import { LitElement, html, nothing } from 'lit';
import { stil } from './stil.js';
import { phase, zeit } from './format.js';
import { merke, sprache, t, waehle } from './sprache.js';
import { uebersicht } from './ansichten/uebersicht.js';
import { speedtest, kachelPopup, messungBlatt } from './ansichten/speedtest.js';
import { geraeteReiter, geraetBlatt } from './ansichten/geraete.js';
import { internet } from './ansichten/internet.js';
import { einstellungenBlatt } from './ansichten/einstellungen.js';
import { verbrauch } from './ansichten/verbrauch.js';
import { protokoll } from './ansichten/protokoll.js';
import { MB_MAX, MB_PX, alsMarkdown, bildBlatt, githubBlatt, meldenBlatt, meldenKnopf, meldungenBlatt } from './ansichten/melden.js';

export const VERSION = typeof __HEIMNETZ_VERSION__ === 'string' ? __HEIMNETZ_VERSION__ : 'entwicklung';
export const REITER = [
  ['uebersicht', merke('Übersicht')],
  ['speedtest', merke('Speedtest')],
  ['geraete', merke('Geräte')],
  ['internet', merke('Internet')], // WU-0009: vorher „Funk“; WLAN steht jetzt unter Geräte
  ['verbrauch', merke('Verbrauch')],
  ['protokoll', merke('Protokoll')],
]; // Namen deutsch (Schlüssel der Übersetzung), angezeigt über t()
const ANSICHT = { uebersicht, speedtest, geraete: geraeteReiter, internet, verbrauch, protokoll };
const NEU_LADEN_MS = 60_000;
const KACHEL_WARTEN_MS = 150; // Überfahren einer Stundenkachel: so lange stehen bleiben, bis das Popup abfragt
const ENTWURF = 'heimnetz-melden-entwurf'; // FE-0001: Entwurf überlebt ein Neuladen der Seite (z. B. nach der Galerie)

/** Felder einer Meldung aus dem Entwurf (für meldung/neu und die GitHub-Vorschau). */
const meldeFelder = (f) => ({ art: f.art, text: f.text.trim(), kontext: f.kontext, version: f.version, geraet: f.geraet });

/** Gewählte Datei als Bild versuchen? Die Android-App liefert Bilder aus der Galerie oft ohne Typ – nur ein anderer
 *  bekannter Typ (Video, PDF …) wird abgelehnt; ob es wirklich ein Bild ist, entscheidet das Laden. */
export function istBildDatei(datei) {
  return !!datei && (!datei.type || datei.type.startsWith('image/'));
}
const TITEL = {
  ok: merke('Alles in Ordnung'),
  warnung: merke('Hinweise'),
  kritisch: merke('Störung'),
  box_fehlt: merke('FRITZ!Box nicht erreichbar'),
};
const PUNKT = { ok: '', warnung: 'amber', kritisch: 'rot', box_fehlt: 'grau' };
/** Stand im Kopf: heute nur die Uhrzeit, sonst Tag und Uhrzeit. */
const standZeit = (s) => zeit(s).replace(new RegExp(`^${t('Heute {uhr}', { uhr: '' })}`), '');

export class HeimnetzPanel extends LitElement {
  static properties = {
    hass: { attribute: false },
    narrow: { type: Boolean },
    panel: { attribute: false },
    _reiter: { state: true },
    _daten: { state: true },
    _opt: { state: true },
    _fehler: { state: true },
    _laedt: { state: true },
    _blatt: { state: true },
    _hinweis: { state: true },
    _hinweisPlan: { state: true },
    _hinweisEinr: { state: true },
    _diag: { state: true },
    _hinweisZugang: { state: true },
    _toast: { state: true },
    _kachel: { state: true },
  };

  static styles = stil;

  constructor() {
    super();
    this._reiter = 'uebersicht';
    this._daten = {};
    this._fehler = '';
    this._hinweis = '';
    this._hinweisPlan = '';
    this._hinweisEinr = '';
    this._diag = { adresse: '192.168.0.1', laeuft: false, antwort: null, fehler: '' }; // WU-0008; Kennwort nie im Zustand
    this._hinweisZugang = ''; // WU-0009: Fehler beim Festlegen des Zugangs
    this._blatt = null;
    this._toast = '';
    this._bilder = new Map(); // Bilder der Tickets für die Liste (id:nr → Data-URL)
    const entwurf = this._entwurfLesen();
    // Reiter und Gerät beschreiben die gemeldete Stelle und bleiben; die Version ist die der Seite jetzt
    if (entwurf) this._blatt = { art: 'melden', form: { ...entwurf, version: VERSION }, vorher: null };
    this._opt = {
      speedtest: { tage: 84, groesse: 'down', grundlast: 'aus', server: '', tag: null, datum: null, stunde: null },
      geraete: { filter: 'alle', suche: '', teil: 'geraete' },
      internet: { sicht: 'haupt' }, // haupt = Zugangsart, ersatz = Ersatzzugang
      mobilfunk: { tage: 1 },
      verbrauch: { tage: 30 },
      protokoll: { art: 'journal', nur_warnungen: false, suche: '' },
    };
  }

  connectedCallback() {
    super.connectedCallback();
    // AN-0005: festgehaltenes Kachel-Popup schließt bei einem Klick daneben
    this._klickDaneben = (e) => {
      if (!this._kachel || !this._kachel.fest) return;
      const pfad = e.composedPath();
      if (!pfad.some((x) => x.classList && (x.classList.contains('kpop') || x.classList.contains('kachel')))) this.kachelWeg(true);
    };
    this.addEventListener('click', this._klickDaneben);
    this._takt = setInterval(() => this.laden(), NEU_LADEN_MS);
    // Screenshot mit Strg+V ins offene Melde-Fenster
    this._einfuegen = (e) => {
      if (!this._blatt || this._blatt.art !== 'melden') return;
      const teile = [...((e.clipboardData && e.clipboardData.items) || [])];
      const it = teile.find((i) => i.type && i.type.startsWith('image/'));
      if (!it || teile.some((i) => i.type === 'text/plain')) return; // Text (auch mit Bild, z. B. aus Word) bleibt Text
      e.preventDefault();
      this.bildDatei(it.getAsFile(), merke('Bild eingefügt'));
    };
    window.addEventListener('paste', this._einfuegen);
    // Erstes Laden über updated() (sobald hass da ist); hier nur beim Wiederanhängen eines schon gezeigten Panels
    if (this.hasUpdated && this.hass) this.laden();
  }

  disconnectedCallback() {
    clearTimeout(this._kachelTakt);
    this.removeEventListener('click', this._klickDaneben);
    clearInterval(this._takt);
    window.removeEventListener('paste', this._einfuegen);
    clearTimeout(this._toastZeit);
    clearTimeout(this._serieTakt);
    this._serieTakt = null;
    super.disconnectedCallback();
  }

  /** Sprache der Seite nach der Sprache des Nutzers in HA, bevor gezeichnet wird. */
  willUpdate(geaendert) {
    if (!geaendert.has('hass')) return;
    const vorher = sprache();
    // Sprache im Profil gewechselt: die fertigen Texte der Integration neu holen (sie kommen in der Sprache der Abfrage)
    if (waehle(this.hass) !== vorher && geaendert.get('hass')) this._sprachWechsel = true;
  }

  updated(geaendert) {
    if (this._kachel && (geaendert.has('_kachel') || geaendert.has('_daten'))) this._kachelLage();
    if (geaendert.has('hass') && !geaendert.get('hass') && this.hass) this.laden();
    else if (this._sprachWechsel) { this._sprachWechsel = false; this.laden(); }
    // laufende Serie: alle 10 s neu laden, damit Fortschritt und Ergebnis zügig erscheinen
    const serie = this._daten.einstellungen && this._daten.einstellungen.serie;
    if (serie && !this._serieTakt) this._serieTakt = setTimeout(() => { this._serieTakt = null; this.laden(); }, 10_000);
  }

  ws(typ, parameter = {}) {
    // Sprache der Seite mitschicken: Texte, die die Integration fertig liefert, folgen dem Profil des Nutzers (WU-0006)
    return this.hass.callWS({ type: `heimnetz/${typ}`, ...parameter, sprache: sprache() });
  }

  /** Übersicht (für den Kopf) und den gewählten Reiter laden. Nur die Antwort der neuesten Abfrage zählt –
   *  eine langsamere ältere (z. B. vor dem Wechsel des Zeitraums) darf nichts überschreiben. */
  async laden() {
    if (!this.hass) return;
    const nummer = (this._abfrage = (this._abfrage || 0) + 1);
    const reiter = this._datenReiter;
    const auftraege = { uebersicht: this.ws('uebersicht') };
    if (reiter !== 'uebersicht') auftraege[reiter] = this.ws(reiter, this._parameter(reiter));
    if (reiter === 'speedtest' || (this._blatt && this._blatt.art === 'einstellungen')) auftraege.einstellungen = this.ws('einstellungen');
    this._laedt = true;
    try {
      const werte = await Promise.all(Object.values(auftraege));
      if (nummer !== this._abfrage) return;
      const neu = { ...this._daten };
      Object.keys(auftraege).forEach((k, i) => { neu[k] = werte[i]; });
      this._daten = neu;
      this._fehler = '';
      // neue Messungen: gemerkte Kachel-Listen verwerfen, ein offenes Popup frisch holen
      this._kachelSpeicher = new Map();
      if (this._kachel && this._kachel.daten && reiter === 'speedtest') this._kachelHolen(this._kachel.tag, this._kachel.stunde, this._kachel.fest, true);
    } catch (err) {
      if (nummer === this._abfrage) this._fehler = (err && err.message) || String(err);
    } finally {
      if (nummer === this._abfrage) this._laedt = false;
    }
  }

  /** Welche Daten der gewählte Reiter braucht; „Geräte“ lädt nur den gewählten Teil (Geräte oder WLAN). */
  get _datenReiter() {
    return this._reiter === 'geraete' && this._opt.geraete.teil === 'wlan' ? 'wlan' : this._reiter;
  }

  _parameter(reiter) {
    const o = this._opt[reiter];
    switch (reiter) {
      case 'speedtest':
        return {
          tage: o.tage, groesse: o.groesse, grundlast: o.grundlast, ...(o.server ? { server: o.server } : {}),
          ...(o.datum ? { datum: o.datum } : o.tag != null ? { tag: o.tag } : {}),
        };
      case 'internet':
        return { tage: this._opt.mobilfunk.tage }; // Zeitraum des Mobilfunk-Verlaufs
      case 'mobilfunk':
      case 'verbrauch':
        return { tage: o.tage };
      case 'protokoll':
        return { art: o.art, nur_warnungen: o.nur_warnungen, suche: o.suche };
      default:
        return {};
    }
  }

  geh(reiter) {
    this._reiter = reiter;
    this.kachelWeg(true);
    const scroll = this.shadowRoot && this.shadowRoot.querySelector('.scroll');
    if (scroll) scroll.scrollTop = 0;
    this.laden();
  }

  /** Auswahl eines Reiters ändern; `laden` = neu abfragen (Filter, die nur die Anzeige betreffen, nicht). */
  setze(reiter, werte, laden = true) {
    if (reiter === 'speedtest' && laden) this._kachel = null;
    this._opt = { ...this._opt, [reiter]: { ...this._opt[reiter], ...werte } };
    if (laden) this.laden();
  }

  /** AN-0005: Popup zur Stundenkachel. Desktop beim Überfahren (`fest` = false), Klick oder Tipp hält es fest. Die
   *  Messungen holt die Integration nur für diese Kachel; die Antwort zählt nur, wenn noch dieselbe Kachel gezeigt wird. */
  kachelZeigen(tag, stunde, fest) {
    clearTimeout(this._kachelTakt);
    const gleich = this._kachel && this._kachel.tag === tag && this._kachel.stunde === stunde;
    if (fest) {
      // zweiter Klick/Tipp auf die festgehaltene Kachel schließt
      if (gleich && this._kachel.fest) { this._kachel = null; return; }
      if (gleich) { this._kachel = { ...this._kachel, fest }; return; }
      this._kachelHolen(tag, stunde, true);
      return;
    }
    if (gleich || (this._kachel && this._kachel.fest)) return;
    // Überfahren: kurz warten, damit ein Wischen über das Raster nicht für jede Kachel abfragt
    this._kachelTakt = setTimeout(() => this._kachelHolen(tag, stunde, false), KACHEL_WARTEN_MS);
  }

  /** Messungen der Kachel holen – gemerkt je Auswahl, bis zum nächsten Laden des Reiters. */
  async _kachelHolen(tag, stunde, fest, neu = false) {
    const o = this._opt.speedtest;
    const parameter = { tage: o.tage, groesse: o.groesse, grundlast: o.grundlast, ...(o.server ? { server: o.server } : {}), tag, stunde };
    const schluessel = JSON.stringify(parameter);
    this._kachelSpeicher = this._kachelSpeicher || new Map();
    const gemerkt = !neu && this._kachelSpeicher.get(schluessel);
    if (!neu) this._kachel = { tag, stunde, fest, daten: gemerkt || null };
    if (gemerkt) return;
    let ergebnis;
    try {
      const daten = await this.ws('speedtest/kachel', parameter);
      this._kachelSpeicher.set(schluessel, daten);
      ergebnis = { daten };
    } catch (err) {
      ergebnis = { fehler: (err && err.message) || String(err) };
    }
    const k = this._kachel;
    if (k && k.tag === tag && k.stunde === stunde) this._kachel = { tag, stunde, fest: k.fest, daten: null, ...ergebnis };
  }

  /** WU-0005: alle Werte einer Messung (Zeile in „Letzte Messungen“). */
  messungOeffnen(m) {
    this.kachelWeg(true);
    this._blatt = { art: 'messung', m };
  }

  kachelWeg(fest) {
    clearTimeout(this._kachelTakt);
    if (!this._kachel || (this._kachel.fest && !fest)) return;
    this._kachel = null;
  }

  /** Popup unter die Kachel setzen, bei zu wenig Platz darüber; seitlich innerhalb der Seite. */
  _kachelLage() {
    const w = this.shadowRoot;
    const pop = w && w.querySelector('.kpop');
    const el = w && w.querySelector(`.wr i[data-k="${this._kachel.tag}-${this._kachel.stunde}"]`);
    const app = w && w.querySelector('.app');
    if (!pop || !el || !app) return;
    const a = app.getBoundingClientRect(), r = el.getBoundingClientRect();
    const x = Math.min(Math.max(8, r.left - a.left + r.width / 2 - pop.offsetWidth / 2), a.width - pop.offsetWidth - 8);
    const unten = r.bottom - a.top + 6, oben = r.top - a.top - pop.offsetHeight - 6;
    pop.style.left = `${Math.max(8, x)}px`;
    pop.style.top = `${unten + pop.offsetHeight < a.height - 8 || oben < 8 ? unten : oben}px`;
  }

  /** Einblendung öffnen; die Antwort zählt nur, wenn noch dieselbe Einblendung offen ist (nicht geschlossen,
   *  kein anderes Gerät angetippt). */
  async geraetOeffnen(kennung) {
    const blatt = { art: 'geraet', kennung, laedt: true };
    this._blatt = blatt;
    let neu;
    try {
      neu = { art: 'geraet', kennung, daten: await this.ws('geraet', { geraet: kennung, tage: 7 }) };
    } catch (err) {
      neu = { art: 'geraet', kennung, fehler: (err && err.message) || String(err) };
    }
    if (this._blatt === blatt) this._blatt = neu;
  }

  zu() {
    this._blatt = null;
  }

  /** Art eines Geräts selbst wählen oder wieder automatisch (AN-0001, nur Admins). */
  async geraetArt(kennung, art) {
    try {
      const daten = await this.ws('geraet/art', { geraet: kennung, art });
      if (this._blatt && this._blatt.kennung === kennung) this._blatt = { art: 'geraet', kennung, daten };
      this.laden();
    } catch (err) {
      this.toast(t('Art nicht gespeichert: {fehler}', { fehler: (err && err.message) || err }));
      this.requestUpdate(); // Auswahl zurück auf den gespeicherten Stand (live-Bindung)
    }
  }

  /** Fenster „Einstellungen“ (⚙ im Kopf); `teil` öffnet gleich einen Reiter (z. B. „zugang“ aus dem Reiter Internet). */
  einstellungenOeffnen(teil) {
    this._blatt = { art: 'einstellungen', ...(teil ? { teil } : {}) };
    const z = (this._daten.internet && this._daten.internet.zugang) || this._daten.zugang;
    if (teil === 'diag' && z && z.adresse) this._diag = { ...this._diag, adresse: z.adresse };
    this.laden();
    this.meldungenLaden();
    this.einrichtungLaden(); // WU-0007: für den Punkt am Reiter „Einrichtung“
    if (teil === 'zugang') this.zugangLaden();
  }

  /* ---- WU-0009: ⚙ › 🌐 Zugang (nur Admins; erkennen und prüfen macht die Integration) ---- */
  async zugangLaden() {
    if (!this.istAdmin) return;
    try {
      this._daten = { ...this._daten, zugang: await this.ws('zugang') };
      this._hinweisZugang = '';
    } catch (err) {
      this._hinweisZugang = t('Zugang nicht abrufbar: {fehler}', { fehler: (err && err.message) || err });
    }
  }

  /** Wahl, Adresse, Ersatz oder Kennwort speichern. Das Kennwort geht nur mit diesem Befehl mit, wird nie im
   *  Zustand behalten und danach im Feld gelöscht; zurück kommt nur „hinterlegt ja/nein“. */
  async zugangSetzen(werte, feld = null) {
    try {
      this._daten = { ...this._daten, zugang: await this.ws('zugang/setzen', werte) };
      this._hinweisZugang = '';
      if (feld) feld.value = ''; // gespeichert: Kennwort im Feld löschen (abgelehnt: zum Korrigieren stehen lassen)
      this.laden();
    } catch (err) {
      this._hinweisZugang = (err && err.message) || String(err);
      this.requestUpdate(); // Auswahl zurück auf den gespeicherten Stand (live-Bindung)
    }
  }

  async zugangSuchen() {
    try {
      const { gesucht, ...zugang } = await this.ws('zugang/suchen');
      this._daten = { ...this._daten, zugang };
      this._hinweisZugang = '';
      this.toast(!gesucht ? t('Eben erst gesucht – in einer halben Minute wieder') : zugang.vorgeschaltet ? t('Gesucht: FRITZ!Box und vorgeschaltetes Gerät neu gefragt') : t('Gesucht: FRITZ!Box neu gefragt'));
      this.laden();
    } catch (err) {
      this._hinweisZugang = (err && err.message) || String(err);
    }
  }

  /** „🔬 Rohdaten abfragen ›“: in den Reiter Diagnose, die Adresse des vorgeschalteten Geräts übernehmen. */
  zuDiagnose(adresse) {
    if (adresse) this._diag = { ...this._diag, adresse };
    this._blatt = { ...this._blatt, teil: 'diag' };
  }

  /** WU-0007: was eingerichtet ist und was fehlt – geprüft beim Öffnen (nur Admins; die Integration erkennt). */
  async einrichtungLaden() {
    if (!this.istAdmin) return;
    try {
      const d = await this.ws('einrichtung');
      this._daten = { ...this._daten, einrichtung: d };
      this._hinweisEinr = '';
    } catch (err) {
      this._hinweisEinr = t('Einrichtung nicht abrufbar: {fehler}', { fehler: (err && err.message) || err });
    }
  }

  /** WU-0007: Knopf einer Voraussetzung – extern im neuen Fenster, sonst Home Assistant an der Stelle öffnen. */
  einrichtungAktion(a) {
    if (a.extern) { window.open(a.ziel, '_blank', 'noopener'); return; }
    this.zu();
    this.oeffne(a.ziel);
  }

  /** WU-0008: Rohdaten eines vorgeschalteten Modems abfragen (nur Admins). Das Kennwort geht nur mit dieser Abfrage
      mit, wird nie im Zustand behalten und nach der Abfrage im Feld gelöscht. */
  async modemAbfragen() {
    const blatt = this.shadowRoot.querySelector('.sheet');
    const feld = blatt && blatt.querySelector('input[name=kennwort]');
    const adresse = ((blatt && blatt.querySelector('input[name=adresse]').value) || '').trim();
    const kennwort = (feld && feld.value) || null;
    this._diag = { ...this._diag, adresse, laeuft: true, fehler: '' };
    try {
      const antwort = await this.ws('modem', { adresse, kennwort });
      this._diag = { ...this._diag, adresse, laeuft: false, antwort, fehler: '' };
    } catch (err) {
      this._diag = { ...this._diag, laeuft: false, fehler: t('Abfrage nicht möglich: {fehler}', { fehler: (err && err.message) || err }) };
    } finally {
      if (feld) feld.value = ''; // Kennwort im Feld löschen, nicht behalten
    }
  }

  /** WU-0008: geschwärzte Antwort als Datei – Inhalt = Antwort des WS-Befehls plus Heimnetz-Version und Zeitpunkt. */
  _modemDatei() {
    return JSON.stringify({ heimnetz: VERSION, zeit: new Date().toISOString(), antwort: this._diag.antwort }, null, 2);
  }

  modemSpeichern() {
    if (!this._diag.antwort) return;
    const name = `heimnetz-modem-${new Date().toISOString().slice(0, 10)}.json`;
    const blob = new Blob([this._modemDatei()], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    this.toast(t('Gespeichert: {name}', { name }));
  }

  modemKopieren() {
    if (!this._diag.antwort) return;
    if (navigator.clipboard) navigator.clipboard.writeText(this._modemDatei()).catch(() => {});
    this.toast(t('Kopiert – {n} Werte', { n: this._diag.antwort.summen.werte }));
  }

  /* ---- Melden (Tickets) ---- */
  toast(text) {
    this._toast = text;
    clearTimeout(this._toastZeit);
    this._toastZeit = setTimeout(() => { this._toast = ''; }, 3500);
  }

  meldenAuf() {
    const reiter = t((REITER.find(([k]) => k === this._reiter) || [, this._reiter])[1]);
    const kontext = [reiter, this._teilText(),
      this._blatt ? t('Dialog „{art}“', { art: this._blatt.art }) : ''].filter(Boolean).join(' · ');
    const form = { art: 'fehler', text: '', kontext, version: VERSION, geraet: this.narrow ? t('Handy') : 'Desktop', stand: true, zelle: false, bilder: [] };
    this._blatt = { art: 'melden', form, vorher: this._blatt };
    this.entwurfMerken();
  }

  /** Gewählter Teil des Reiters in Worten (für den Kontext einer Meldung). */
  _teilText() {
    if (this._reiter === 'geraete' && this._opt.geraete.teil === 'wlan') return t('WLAN');
    if (this._reiter !== 'internet') return '';
    if (this._opt.internet.sicht === 'ersatz') return t('Ersatz');
    const z = this._daten.internet && this._daten.internet.zugang;
    return z ? z.titel : '';
  }

  /** Teil des Reiters als Kennung (Stand der Seite einer Meldung). */
  get _teil() {
    return this._reiter === 'geraete' ? this._opt.geraete.teil : this._reiter === 'internet' ? this._opt.internet.sicht : null;
  }

  meldenZu() {
    const b = this._blatt && this._blatt.art === 'github' ? this._blatt.vorher : this._blatt;
    this._blatt = (b && b.vorher) || null;
    this._entwurfWeg();
  }

  /* ---- WU-0006: öffentlich auf GitHub melden ---- */
  /** Vom Melde-Dialog zur Vorschau des Issues; ohne Text geht es nicht weiter (wie „Senden“). */
  githubAuf() {
    const melden = this._blatt, f = melden.form;
    if (!f.text.trim()) { f.fehler = t('Bitte kurz beschreiben'); this.requestUpdate(); return; }
    f.fehler = '';
    this._blatt = { art: 'github', vorher: melden, vorschau: null };
    this._githubVorschau();
  }

  githubZurueck() {
    if (this._blatt && this._blatt.art === 'github') this._blatt = this._blatt.vorher;
  }

  githubZelle(an) {
    const b = this._blatt;
    if (b.vorher.form.sendet) return;
    b.vorher.form.zelle = an;
    this._blatt = { ...b, vorschau: null }; // alte Vorschau weg, bis die neue da ist – nie eine falsche zeigen
    this.entwurfMerken();
    this._githubVorschau();
  }

  /** Titel, Text und Link baut die Integration; die Antwort zählt nur, solange noch dieselbe Vorschau offen ist. */
  async _githubVorschau() {
    const b = this._blatt, melden = b.vorher;
    let neu;
    try {
      neu = { ...b, vorschau: await this.ws('meldung/github', { meldung: meldeFelder(melden.form), zelle: !!melden.form.zelle }), fehler: '' };
    } catch (err) {
      neu = { ...b, fehler: t('Vorschau nicht abrufbar: {fehler}', { fehler: (err && err.message) || err }) };
    }
    if (this._blatt === b) this._blatt = neu;
  }

  /** Entwurf (Art, Text, Bilder …) im Browser merken; Speicher voll oder gesperrt → ohne Sicherung weiter. */
  entwurfMerken() {
    const b = this._blatt && this._blatt.art === 'github' ? this._blatt.vorher : this._blatt;
    if (!b || b.art !== 'melden') return;
    const { sendet, fehler, ...form } = b.form;
    try {
      sessionStorage.setItem(ENTWURF, JSON.stringify(form));
    } catch {
      // Speicher voll (Bilder): wenigstens Art und Text sichern, nie einen älteren Stand stehen lassen
      try { sessionStorage.setItem(ENTWURF, JSON.stringify({ ...form, bilder: [] })); } catch { this._entwurfWeg(); }
    }
  }

  _entwurfLesen() {
    try {
      const f = JSON.parse(sessionStorage.getItem(ENTWURF) || 'null');
      return f && typeof f.text === 'string' && Array.isArray(f.bilder) ? f : null;
    } catch {
      return null;
    }
  }

  _entwurfWeg() {
    try { sessionStorage.removeItem(ENTWURF); } catch { /* nichts gemerkt */ }
  }

  /** Meldung senden, danach jedes Bild einzeln; die Rückmeldung sagt, wie viele Bilder angekommen sind.
   *  `github` (WU-0006): aus der Vorschau – das vorausgefüllte Issue, genau wie gezeigt, in einem neuen Fenster öffnen
   *  (noopener: GitHub bekommt keinen Zugriff auf diese Seite) und lokal speichern wie bisher. Geöffnet wird noch im
   *  Klick, vor jeder Antwort – danach sperren Safari und die App von Home Assistant das Fenster. */
  async meldungSenden(github = false) {
    const b = this._blatt, melden = b.art === 'github' ? b.vorher : b, f = melden.form;
    if (!f.text.trim()) { f.fehler = t('Bitte kurz beschreiben'); this.requestUpdate(); return; }
    const vorschau = github ? b.vorschau : null;
    if (github && !vorschau) return;
    if (vorschau) window.open(vorschau.url, '_blank', 'noopener');
    const seite = f.stand ? { reiter: this._reiter, teil: this._teil, dialog: melden.vorher ? melden.vorher.art : null } : null;
    f.sendet = true; f.fehler = ''; this.requestUpdate();
    let neu;
    try {
      neu = await this.ws('meldung/neu', { meldung: { ...meldeFelder(f), seite } });
    } catch (err) {
      f.sendet = false; f.fehler = t('Nicht gesendet: {fehler}', { fehler: (err && err.message) || err }); this.requestUpdate();
      return;
    }
    let angekommen = 0, fehler = '';
    for (const bild of f.bilder) {
      try {
        angekommen = (await this.ws('meldung/bild', { meldung_id: neu.id, bild: bild.url })).bilder;
      } catch (err) {
        fehler = (err && err.message) || String(err);
      }
    }
    if (this._blatt === b) this._blatt = melden.vorher || null;
    this._entwurfWeg();
    delete this._daten.meldungen;
    const mit = angekommen ? t(angekommen === 1 ? ' mit {n} Bild' : ' mit {n} Bildern', { n: angekommen }) : '';
    const fehlt = f.bilder.length - angekommen;
    const verloren = fehlt ? t(fehlt === 1 ? ' · {n} Bild kam nicht an' : ' · {n} Bilder kamen nicht an', { n: fehlt }) + (fehler ? ` (${fehler})` : '') : '';
    // Nummer im Issue vorausgesagt: hat inzwischen jemand anderer gemeldet, steht dort eine andere – das sagen
    const gemeldet = !vorschau ? t('Danke – gemeldet als {ticket}', { ticket: neu.ticket })
      : vorschau.ticket === neu.ticket ? t('Gemeldet als {ticket} – GitHub öffnet sich in einem neuen Fenster', { ticket: neu.ticket })
        : t('Gemeldet als {ticket} – im Issue auf GitHub steht {vorher}, bitte dort ändern', { ticket: neu.ticket, vorher: vorschau.ticket });
    this.toast(gemeldet + mit + verloren);
  }

  /** Bild/Video → verkleinertes JPEG in das offene Melde-Fenster. */
  bildAus(quelle, b, h, wie) {
    const blatt = this._blatt;
    if (!blatt || blatt.art !== 'melden') return;
    const B = blatt.form.bilder;
    if (B.length >= MB_MAX) { this.toast(t('Höchstens {n} Bilder', { n: MB_MAX })); return; }
    const k = Math.min(1, MB_PX / Math.max(b, h)), c = document.createElement('canvas');
    c.width = Math.round(b * k); c.height = Math.round(h * k);
    c.getContext('2d').drawImage(quelle, 0, 0, c.width, c.height);
    const url = c.toDataURL('image/jpeg', 0.82);
    B.push({ url, b: c.width, h: c.height, kb: Math.round((url.length * 0.75) / 1024) });
    this.requestUpdate();
    this.entwurfMerken();
    this.toast(t(wie));
  }

  /** FE-0001: jede Datei versuchen, die kein anderer bekannter Typ ist; geladen über eine Objekt-Adresse (der Browser
   *  erkennt das Bild am Inhalt, auch ohne Typ). Jeder Schritt meldet sich – nie mehr stilles „0 von 3“. */
  bildDatei(datei, wie) {
    if (!datei) return;
    if (!istBildDatei(datei)) { this.toast(t('Kein Bild ({typ}) – bitte ein Bild wählen', { typ: datei.type })); return; }
    this.toast(t('Bild wird geladen …'));
    let adresse;
    try {
      adresse = URL.createObjectURL(datei);
    } catch {
      this.toast(t('Bild nicht lesbar'));
      return;
    }
    const img = new Image();
    const fertig = () => URL.revokeObjectURL(adresse);
    img.onload = () => {
      try {
        this.bildAus(img, img.naturalWidth || img.width, img.naturalHeight || img.height, wie);
      } catch (err) {
        this.toast(t('Bild nicht übernommen: {fehler}', { fehler: (err && err.message) || err }));
      } finally {
        fertig();
      }
    };
    img.onerror = () => { fertig(); this.toast(t('Bild nicht lesbar – bitte ein anderes wählen')); };
    img.src = adresse;
  }

  async fensterAufnehmen() {
    let strom;
    try {
      strom = await navigator.mediaDevices.getDisplayMedia({ video: { displaySurface: 'browser' }, preferCurrentTab: true });
      const v = document.createElement('video');
      v.srcObject = strom; v.muted = true;
      await v.play();
      await new Promise((r) => setTimeout(r, 300));
      if (!v.videoWidth || !v.videoHeight) throw new Error('leer');
      this.bildAus(v, v.videoWidth, v.videoHeight, merke('Bild aufgenommen'));
    } catch {
      this.toast(t('Aufnahme abgebrochen'));
    } finally {
      if (strom) strom.getTracks().forEach((t) => t.stop());
    }
  }

  async meldungenLaden() {
    try {
      this._daten = { ...this._daten, meldungen: await this.ws('meldungen') };
    } catch (err) {
      this.toast(t('Meldungen nicht abrufbar: {fehler}', { fehler: (err && err.message) || err }));
    }
  }

  meldungenOeffnen() {
    this._blatt = { art: 'meldungen', filter: (this._blatt && this._blatt.filter) || 'offen' };
    this.meldungenLaden();
  }

  /** Bild eines Tickets für die Liste; lädt beim ersten Zeigen nach (nur über die Verbindung). */
  meldungBild(m, i) {
    const k = `${m.id}:${i}`;
    if (!this._bilder.has(k)) {
      this._bilder.set(k, null);
      this.ws('meldung/bild_zeigen', { meldung_id: m.id, nr: i })
        .then((r) => { this._bilder.set(k, r.url); this.requestUpdate(); })
        .catch(() => { this._bilder.delete(k); }); // beim nächsten Zeichnen neu versuchen
    }
    return this._bilder.get(k);
  }

  bildGross(m, i) {
    this._blatt = { art: 'bild', m, i, filter: this._blatt && this._blatt.filter };
  }

  async meldungStatus(m, status) {
    try {
      await this.ws('meldung/status', { meldung_id: m.id, status });
      await this.meldungenLaden();
    } catch (err) {
      this.toast(t('Nicht geändert: {fehler}', { fehler: (err && err.message) || err }));
    }
  }

  async meldungLoeschen(m) {
    try {
      await this.ws('meldung/loeschen', { meldung_id: m.id });
      this.toast(t('{ticket} gelöscht', { ticket: m.ticket }));
      await this.meldungenLaden();
    } catch (err) {
      this.toast(t('Nicht gelöscht: {fehler}', { fehler: (err && err.message) || err }));
    }
  }

  meldungenKopieren() {
    const liste = this._daten.meldungen || [];
    if (navigator.clipboard) navigator.clipboard.writeText(alsMarkdown(liste)).catch(() => {});
    this.toast(t('{n} Meldungen als Markdown kopiert', { n: liste.length }));
  }

  async einstellungenSpeichern(werte) {
    try {
      const neu = await this.ws('einstellungen/setzen', werte);
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweis = '';
      this.laden();
    } catch (err) {
      this._hinweis = (err && err.message) || String(err);
    }
  }

  async messplanSetzen(werte) {
    try {
      const neu = await this.ws('messplan/setzen', werte);
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweisPlan = '';
    } catch (err) {
      this._hinweisPlan = (err && err.message) || String(err);
      this.requestUpdate(); // Felder wieder auf den gespeicherten Plan stellen (live-Bindung)
    }
  }

  /** WU-0001: Serie „n× messen“ starten; während sie läuft, öfter nachsehen. */
  async serieStarten() {
    try {
      const neu = await this.ws('serie');
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweisPlan = '';
    } catch (err) {
      this._hinweisPlan = (err && err.message) || String(err);
    }
  }

  async jetztMessen() {
    try {
      const neu = await this.ws('messen');
      this._daten = { ...this._daten, einstellungen: neu };
      this._hinweisPlan = '';
    } catch (err) {
      this._hinweisPlan = (err && err.message) || String(err);
    }
  }

  /** Andere Seite von Home Assistant öffnen (z. B. Ookla-Einstellungen). */
  oeffne(pfad) {
    history.pushState(null, '', pfad);
    window.dispatchEvent(new CustomEvent('location-changed', { detail: { replace: false } }));
  }

  get istAdmin() {
    return !!(this.hass && this.hass.user && this.hass.user.is_admin);
  }

  _kopf(u) {
    if (!u) return html`<div class="glas-panel glas-kopf"><div class="glas-klein">Heimnetz</div><div class="leise">${t('lädt …')}</div></div>`;
    const befunde = u.befunde || [];
    const kritisch = befunde.filter((b) => b.stufe === 'kritisch').length;
    const warnung = befunde.filter((b) => b.stufe === 'warnung').length;
    const unter = !u.box_erreichbar
      ? t('Die Box antwortet nicht · Home Assistant versucht es jede Minute')
      : [u.zugang ? u.zugang.kopf : u.internet && u.internet.technik, u.internet && u.internet.ok ? t('Internet erreichbar') : t('kein Internet')]
        .filter(Boolean).join(' · ');
    return html`
      <div class="glas-panel glas-kopf">
        <div>
          <div class="glas-klein">Heimnetz · ${t('Stand {zeit}', { zeit: standZeit(u.stand) })}</div>
          <div class="kopf-titel" style="margin-top:6px">
            <span class="punkt ${PUNKT[u.gesamt] ?? 'grau'}"></span>
            <span class="glas-kw" style="font-size:30px">${TITEL[u.gesamt] ? t(TITEL[u.gesamt]) : u.gesamt}</span>
          </div>
          <div class="leise" style="margin-top:6px">${unter}</div>
        </div>
        <div class="chips">
          ${kritisch ? html`<button class="chip glas-panel rot" @click=${() => this.geh('uebersicht')}>● ${t(kritisch > 1 ? '{n} Störungen' : '{n} Störung', { n: kritisch })}</button>` : nothing}
          ${warnung ? html`<button class="chip glas-panel amber" @click=${() => this.geh('uebersicht')}>⚠ ${t(warnung > 1 ? '{n} Hinweise' : '{n} Hinweis', { n: warnung })}</button>` : nothing}
          <button class="chip glas-panel" title=${t('Einstellungen')} @click=${() => this.einstellungenOeffnen()}>⚙</button>
        </div>
      </div>`;
  }

  _blattInhalt() {
    const b = this._blatt;
    if (!b) return nothing;
    const art = { einstellungen: einstellungenBlatt, melden: meldenBlatt, github: githubBlatt, meldungen: meldungenBlatt, bild: bildBlatt, messung: messungBlatt }[b.art];
    return art ? art(this) : geraetBlatt(this, b);
  }

  render() {
    const hell = !(this.hass && this.hass.themes && this.hass.themes.darkMode);
    const u = this._daten.uebersicht;
    const ansicht = ANSICHT[this._reiter];
    const daten = this._reiter === 'uebersicht' ? u : this._daten[this._datenReiter];
    return html`
      <div class="wurzel ${hell ? 'hell' : ''}" lang=${sprache()}>
        <div class="ui"><div class="app">
          <div class="glas-bg" data-phase=${phase(this.hass && this.hass.states['sun.sun'])}>
            <i class="k1"></i><i class="k2"></i><i class="k3"></i>
          </div>
          ${this.narrow
            ? html`<button class="menue-knopf glas-panel" title=${t('Menü')} @click=${() => this.dispatchEvent(new Event('hass-toggle-menu', { bubbles: true, composed: true }))}>☰</button>`
            : nothing}
          <nav class="glas-nav glas-panel sechs">
            ${REITER.map(([k, name]) => html`<button class=${k === this._reiter ? 'on' : ''} @click=${() => this.geh(k)}>${t(name)}</button>`)}
          </nav>
          <div class="scroll" @scroll=${() => this.kachelWeg(true)}><div class="seite ${this._laedt ? 'laden' : ''}">
            ${this._kopf(u)}
            ${this._fehler ? html`<div class="glas-panel fehler-band">${t('Daten nicht abrufbar: {fehler}', { fehler: this._fehler })}</div>` : nothing}
            ${daten || this._reiter === 'geraete' ? ansicht(this, daten) : html`<div class="glas-panel block"><div class="leer">${t('lädt …')}</div></div>`}
            <div class="leise" style="text-align:center;padding:8px">Heimnetz ${VERSION}</div>
          </div></div>
          <div class="schleier ${this._blatt ? 'an' : ''}" @click=${() => this.zu()}></div>
          <div class="sheet glas-panel ${this._blatt ? 'an' : ''}">${this._blatt && !['melden', 'github'].includes(this._blatt.art) ? meldenKnopf(this, true) : nothing}${this._blattInhalt()}</div>
          ${this._blatt ? nothing : meldenKnopf(this)}
          <div class="toast glas-panel ${this._toast ? 'an' : ''}" role="status">${this._toast}</div>
          ${this._kachel && this._reiter === 'speedtest' ? kachelPopup(this) : nothing}
        </div></div>
      </div>`;
  }
}

if (!customElements.get('heimnetz-panel')) customElements.define('heimnetz-panel', HeimnetzPanel);
