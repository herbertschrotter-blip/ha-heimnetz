// WU-0010 (Mockup netzwerk.html · Warnungen und Eigene Arten, abgenommen 28.10.2026): zwei Reiter im Fenster ⚙
// Einstellungen, nur für Admins. „🏷️ Arten“: eigene Arten anlegen, umbenennen, löschen, darunter die festen.
// „🔔 Warnungen“: Ziel (notify-Dienst), Verzögerung, Testnachricht, Schalter je Art, Ausnahmen je Gerät, außerdem
// melden. Wer überwacht wird, die Zählungen und das Beispiel kommen fertig von der Integration (heimnetz/arten,
// heimnetz/warnungen); die Seite zeigt nur an und schickt die Wahl.
import { html, nothing } from 'lit';
import { live } from 'lit/directives/live.js';
import { t } from '../sprache.js';
import { seg } from './teile.js';

const anzahl = (n) => t(n === 1 ? '{n} Gerät' : '{n} Geräte', { n });
const schalter = (an, klick) => html`<button class="sw ${an ? 'on' : ''}" role="switch" aria-checked=${an ? 'true' : 'false'} @click=${klick}><i></i></button>`;
const nurAdmin = (text) => html`<p class="hinweis" style="padding-top:8px">${text}</p>`;

/** Felder Symbol und Name einer eigenen Art; `los(symbol, name)` beim Anlegen/Speichern. */
export function artFormular({ symbol = '🏷️', name = '', platz, knopf, los, weg }) {
  const werte = (ev) => {
    const z = ev.target.closest('.art-form');
    return [z.querySelector('[name=art-ic]').value, z.querySelector('[name=art-name]').value];
  };
  return html`<div class="ez art-form"><input name="art-ic" class="art-ic" maxlength="8" .value=${symbol} title=${t('Symbol')} aria-label=${t('Symbol')}>
    <input name="art-name" class="art-name" maxlength="30" .value=${name} placeholder=${platz}>
    <button class="knopf haupt" @click=${(ev) => los(...werte(ev))}>${knopf}</button><button class="leise" title=${t('Abbrechen')} @click=${weg}>✕</button></div>`;
}

export function artenTeil(p) {
  if (!p.istAdmin) return nurAdmin(t('Eigene Arten legen nur Admins an.'));
  const a = p._daten.arten, b = p._blatt;
  if (!a) return p._hinweisArten ? html`<p class="fein">${p._hinweisArten}</p>` : html`<div class="leer">${t('lädt …')}</div>`;
  const stelle = (werte) => { p._blatt = { ...p._blatt, artBearb: null, artLoe: null, artNeu: false, ...werte }; };
  const eigen = a.eigene.map((x) => (b.artBearb === x.name
    ? artFormular({ symbol: x.symbol, name: x.titel, knopf: t('Speichern'), los: (s, n) => p.artAendern(x.name, s, n), weg: () => stelle({}) })
    : html`<div class="ez" data-art=${x.name}><span>${x.text}<small>${t('eigene · {anzahl}', { anzahl: anzahl(x.geraete) })}</small></span>
        <span class="art-k"><button class="leise blau" @click=${() => stelle({ artBearb: x.name })}>${t('✎ ändern')}</button><button class="leise rot-t" title=${t('löschen')} @click=${() => stelle({ artLoe: x.name })}>🗑</button></span></div>
      ${b.artLoe === x.name ? html`<div class="mg-frage" style="margin:4px 0 8px"><b>${t('„{text}“ löschen?', { text: x.text })}</b><br>${t(x.geraete === 1 ? '{n} Gerät bekommt wieder die automatisch erkannte Art; Warnungen für diese Art fallen weg.' : '{n} Geräte bekommen wieder die automatisch erkannte Art; Warnungen für diese Art fallen weg.', { n: x.geraete })}
        <div class="dg-knoepfe" style="margin-top:8px"><button class="rot" @click=${() => p.artLoeschen(x.name)}>${t('Löschen')}</button><button @click=${() => stelle({})}>${t('Abbrechen')}</button></div></div>` : nothing}`));
  const neu = b.artNeu
    ? artFormular({ platz: t('Name, z. B. Werkstatt'), knopf: t('Anlegen'), los: (s, n) => p.artNeu(s, n), weg: () => stelle({}) })
    : html`<div class="dg-knoepfe" style="margin-top:4px"><button class="art-neu" ?disabled=${a.eigene.length >= a.hoechstens} @click=${() => stelle({ artNeu: true })}>${t('＋ Neue Art')}</button></div>`;
  return html`<div class="vs-stufe"><span>${t('Eigene Arten')}</span><span>${a.eigene.length}</span></div>
    ${a.eigene.length ? eigen : html`<p class="hinweis">${t('noch keine')}</p>`}${neu}
    ${p._hinweisArten ? html`<p class="fein">${p._hinweisArten}</p>` : nothing}
    <p class="hinweis" style="margin-top:6px">${t('Zuordnen im Fenster eines Geräts (Reiter Geräte → Gerät antippen → Art). Eigene Arten gelten wie die festen: unter Geräte › nach Art und in ⚙ › 🔔 Warnungen.')}</p>
    <div class="vs-stufe"><span>${t('Feste Arten')}</span><span>${a.feste.length}</span></div>
    ${a.feste.map((x) => html`<div class="ez"><span>${x.text}<small>${t('fest · {anzahl}', { anzahl: anzahl(x.geraete) })}</small></span><span class="leise">${t('automatisch erkannt')}</span></div>`)}`;
}

export function warnungenTeil(p) {
  if (!p.istAdmin) return nurAdmin(t('Warnungen stellen nur Admins ein.'));
  const w = p._daten.warnungen;
  if (!w) return p._hinweisWarn ? html`<p class="fein">${p._hinweisWarn}</p>` : html`<div class="leer">${t('lädt …')}</div>`;
  const setzen = (werte) => p.warnungenSetzen(werte);
  const letzte = w.verzoegerungen.length - 1;
  return html`
    <div class="ez"><span>${t('Nachricht an')}<small>${t('notify-Dienst von Home Assistant')}</small></span>
      <select class="ga-wahl w-ziel" .value=${live(w.ziel)} @change=${(e) => setzen({ ziel: e.target.value })}>
        ${w.ziele.map((z) => html`<option value=${z.name} ?selected=${z.name === w.ziel}>${z.text}</option>`)}</select></div>
    ${w.ziel_fehlt ? html`<div class="befund"><span class="punkt amber"></span><div><b>${t('Dienst fehlt')}</b><p>${t('Den gewählten notify-Dienst gibt es gerade nicht – Warnungen kommen nur als Ereignis und ins Journal.')}</p></div></div>` : nothing}
    <div class="ez"><span>${t('Offline melden nach')}<small>${t('so lange muss ein Gerät weg sein')}</small></span>${seg(w.verzoegerungen.map((m, i) => [m, i === letzte ? `${m} min` : String(m)]), w.verzoegerung, (v) => setzen({ verzoegerung: v }))}</div>
    <div class="dg-knoepfe" style="margin:2px 0 4px"><button class="w-test" @click=${() => p.testnachricht()}>${t('🔔 Testnachricht senden')}</button></div>
    ${p._hinweisWarn ? html`<p class="fein">${p._hinweisWarn}</p>` : nothing}
    <div class="vs-stufe"><span>${t('Überwachen nach Art')}</span><span>${t('{n} von {gesamt} Geräten', { n: w.ueberwacht, gesamt: w.gesamt })}</span></div>
    ${w.arten.map((a) => html`<div class="ez" data-art=${a.name}><span>${a.text}<small>${a.hinweis || anzahl(a.geraete)}</small></span>${schalter(a.an, () => setzen({ art: a.name, an: !a.an }))}</div>`)}
    <div class="vs-stufe"><span>${t('Einzeln abweichend')}</span><span>${w.ausnahmen.length}</span></div>
    ${w.ausnahmen.length ? w.ausnahmen.map((x) => html`<div class="ez" data-ausnahme=${x.id}><span>${x.name}<small>${x.wert === 'immer' ? t('wird immer gemeldet – abweichend von der Gruppe') : t('wird nie gemeldet – abweichend von der Gruppe')}</small></span>
      <button class="leise blau" title=${t('zurücksetzen')} @click=${() => p.warnungGeraet(x.id, 'gruppe')}>✕</button></div>`) : html`<p class="hinweis">${t('keine')}</p>`}
    <p class="hinweis">${t('Einzelne Geräte stellst du im Fenster des Geräts um (Reiter Geräte → Gerät antippen).')}</p>
    <div class="vs-stufe"><span>${t('Außerdem melden')}</span><span></span></div>
    <div class="ez" data-schalter="wieder"><span>${t('Wieder online')}<small>${t('mit Dauer, nur wenn vorher gemeldet')}</small></span>${schalter(w.wieder, () => setzen({ wieder: !w.wieder }))}</div>
    <div class="ez" data-schalter="neu"><span>${t('Neues unbekanntes Gerät')}<small>${t('sobald sich ein noch nie gesehenes Gerät verbindet')}</small></span>${schalter(w.neu, () => setzen({ neu: !w.neu }))}</div>
    <div class="ez" data-schalter="internet"><span>${t('Internet oder FRITZ!Box weg')}<small>${t('kommt an, sobald es wieder geht – mit Dauer des Ausfalls')}</small></span>${schalter(w.internet, () => setzen({ internet: !w.internet }))}</div>
    <div class="vs-kopf" style="margin-top:8px"><span class="leise">${t('Beispiel')}</span><br><b>Heimnetz</b> · ${w.beispiel}</div>
    <p class="hinweis" style="margin-top:6px">${t('Nachrichten an die Companion App laufen über den Push-Dienst von Google bzw. Apple – der Gerätename verlässt dabei das Heimnetz. Für jede Meldung gibt es zusätzlich das Ereignis „heimnetz_warnung“ für eigene Automationen.')}</p>`;
}
