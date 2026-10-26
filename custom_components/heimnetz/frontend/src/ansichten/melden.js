// Melden-Knopf, Melde-Dialog und Liste der Tickets (Mockup netzwerk.html · Melden, abgenommen 13.10.2026; Muster aus
// dem Baustrommanager). Der Entwurf (Art, Text, Bilder, „Stand mitschicken“) liegt in p._blatt.form; Nummern, Status
// und Ablage macht die Integration (heimnetz/meldung/*). Bilder gehen nach der Meldung einzeln hinüber, damit jedes
// bestätigt wird und keines still verloren geht.
import { html, nothing } from 'lit';
import { live } from 'lit/directives/live.js';
import { unsafeSVG } from 'lit/directives/unsafe-svg.js';
import { zeit as zeitS } from '../format.js';
import { merke, t, tl } from '../sprache.js';
import { seg } from './teile.js';

export const MB_MAX = 3, MB_PX = 1600;
export const ICON_MELDEN = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M4 5h16v11H9l-5 4z"/><path stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M12 8v3.5M12 13.6v.2"/></svg>';
const ARTEN = [['fehler', merke('Fehler')], ['wunsch', merke('Wunsch')], ['anregung', merke('Anregung')]];
// nur Farben; Texte, Status und offen/erledigt liefert die Integration (heimnetz/meldungen)
const ART_FARBE = { fehler: 'rot-b', wunsch: 'blau-b', anregung: 'amber-b' };
const STATUS_FARBE = { neu: 'amber-b', angenommen: 'blau-b', in_arbeit: 'blau-b', geloest: 'gruen' };
const zeit = (iso) => { const ms = Date.parse(iso || ''); return Number.isNaN(ms) ? '–' : zeitS(ms / 1000); };
const FRAGE = { fehler: merke('Was ist passiert, was hättest du erwartet?'), wunsch: merke('Was wünschst du dir?'), anregung: merke('Deine Idee') };

export const offen = (m) => !!m.offen;

export function meldenKnopf(p, imBlatt = false) {
  return html`<button class="melden-knopf glas-panel ${imBlatt ? 'im-sheet' : ''}" title=${t('Fehler, Wunsch oder Anregung melden')} aria-label=${t('Melden')} @click=${() => p.meldenAuf()}>${unsafeSVG(ICON_MELDEN)}</button>`;
}

// FE-0001: ein Bild je Auswahl – mit „multiple“ liefert die Galerie die Auswahl so, dass die Android-App von Home
// Assistant sie nicht an die Seite weitergibt (kein Bild, kein Ereignis). Mehr Bilder: einfach noch einmal wählen.
function bilderBox(p, f) {
  const B = f.bilder, pc = !p.narrow;
  const auf = pc && typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia;
  const gewaehlt = (e) => {
    const dateien = [...(e.target.files || [])];
    if (!dateien.length) p.toast(t('Kein Bild gewählt'));
    dateien.forEach((x) => p.bildDatei(x, merke('Bild gewählt')));
    e.target.value = '';
  };
  return html`<div class="mb-box"><div class="mb-kopf"><b>📷 Screenshot</b><span class="leise">${t('{n} von {gesamt}', { n: B.length, gesamt: MB_MAX })}</span></div>
    ${B.length >= MB_MAX ? nothing : html`<div class="mb-knoepfe"><label>📎 ${t('Bild wählen')}<input type="file" accept="image/*" @change=${gewaehlt}></label>${auf ? html`<button @click=${() => p.fensterAufnehmen()}>🖥 ${t('Fenster aufnehmen')}</button>` : nothing}</div>`}
    <div class="leise">${pc ? html`${t('oder einen Screenshot mit')} <b>${t('Strg+V')}</b> ${t('einfügen (z. B. nach Win+Shift+S)')}` : t('Screenshot mit den Handy-Tasten machen, dann „Bild wählen“ – der neueste steht in der Galerie vorne')} · ${t('wird auf höchstens {n} px verkleinert', { n: MB_PX })}</div>
    ${B.length ? html`<div class="mb-bilder">${B.map((x, i) => html`<div class="mb-bild"><img src=${x.url} alt=${t('Bild {n}', { n: i + 1 })}><button class="x" aria-label=${t('Bild entfernen')} @click=${() => { B.splice(i, 1); p.requestUpdate(); p.entwurfMerken(); }}>✕</button><small>${x.b}×${x.h} · ${x.kb} KB</small></div>`)}</div>` : nothing}</div>`;
}

/** Melde-Dialog; p._blatt = { art: 'melden', form, vorher } */
export function meldenBlatt(p) {
  const f = p._blatt.form;
  const setze = (k, v) => { f[k] = v; p.requestUpdate(); p.entwurfMerken(); };
  return html`<div class="griff"></div><button class="zu" @click=${() => p.meldenZu()}>✕</button>
    <h3>${t('Melden')}</h3><div class="leise">${t('Fehler, Wunsch oder Anregung – wird ein lokales Ticket; öffentlich über GitHub erreicht es den Entwickler.')}</div>
    ${seg(tl(ARTEN), f.art, (v) => setze('art', v), false)}
    <label class="feld">${t(FRAGE[f.art])}<textarea rows="4" name="ml-text" placeholder=${t('kurz beschreiben')} .value=${live(f.text)} @input=${(e) => { f.text = e.target.value; p.entwurfMerken(); }}></textarea></label>
    <div class="ml-kontext"><div><span class="leise">${t('Reiter')}</span> ${f.kontext}</div><div><span class="leise">Version</span> ${f.version} · ${f.geraet}</div></div>
    ${bilderBox(p, f)}
    <div class="zeile"><div><b>${t('Stand der Seite mitschicken')}</b><div class="leise">${t('Reiter, Filter und offener Dialog – hilft beim Nachstellen, ohne Zugangsdaten')}</div></div>
      <button class="sw ${f.stand ? 'on' : ''}" role="switch" aria-checked=${f.stand ? 'true' : 'false'} @click=${() => setze('stand', !f.stand)}><i></i></button></div>
    ${f.fehler ? html`<p class="fein">${f.fehler}</p>` : nothing}
    <button class="knopf breit amber ml-senden" ?disabled=${f.sendet} @click=${() => p.meldungSenden()}>${f.sendet ? t('sendet …') : t('Senden')}</button>
    <button class="knopf breit ml-github" ?disabled=${f.sendet} @click=${() => p.githubAuf()}>${t('Senden + öffentlich auf GitHub')} ↗</button>
    <div class="leise mitte">${t('GitHub: für den Entwickler sichtbar, auch wenn er dein Heimnetz nicht kennt – mit deinem eigenen GitHub-Konto')}</div>
    <button class="knopf breit leise-k" @click=${() => p.meldenZu()}>${t('Abbrechen')}</button>`;
}

/** WU-0006 (Mockup netzwerk.html · githubMelden): Vorschau des öffentlichen Issues; p._blatt = { art: 'github',
 *  vorher: <Melde-Dialog>, vorschau, fehler }. Titel, Text und Link baut die Integration (heimnetz/meldung/github);
 *  gespeichert wird lokal wie bisher, GitHub öffnet sich vorausgefüllt in einem neuen Fenster. */
export function githubBlatt(p) {
  const b = p._blatt, f = b.vorher.form, v = b.vorschau, n = f.bilder.length;
  return html`<div class="griff"></div><button class="zu" @click=${() => p.meldenZu()}>✕</button>
    <h3>${t('Öffentlich auf GitHub melden')}</h3><div class="leise">${t('Das Issue ist für alle sichtbar. Du siehst hier genau, was mitgeht; auf GitHub kannst du es vor dem Absenden noch ändern.')}</div>
    ${v ? html`<div class="gh-vorschau"><b>${v.titel}</b>

${v.text}</div>` : html`<div class="leer">${b.fehler || t('lädt …')}</div>`}
    ${v && v.gekuerzt ? html`<div class="leise">${t('Der Text ist für den Link zu lang und wurde gekürzt – ganz steht er im lokalen Ticket.')}</div>` : nothing}
    <div class="zeile"><div><b>${t('Zell- und Signaldaten mitsenden')}</b><div class="leise">${v && !v.zelle_da ? t('Im Moment keine Zelldaten von der Box') : t('Zellkennung, Signal, Entfernung zum Mast – hilft bei Fehlern im Mobilfunk-Reiter')}</div></div>
      <button class="sw ${f.zelle ? 'on' : ''}" role="switch" aria-checked=${f.zelle ? 'true' : 'false'} ?disabled=${f.sendet} @click=${() => p.githubZelle(!f.zelle)}><i></i></button></div>
    ${f.zelle ? html`<div class="gh-warn"><b>${t('Achtung:')}</b> ${t('Aus Zellkennung und Entfernung lässt sich ungefähr bestimmen, wo du wohnst. Nur mitsenden, wenn es für den Fehler nötig ist.')}</div>` : nothing}
    <div class="leise">${t('Nie dabei: Gerätenamen, Hardware-Adressen, IP-Adressen, Standort von Home Assistant, Kennwörter.')}${n ? ` · ${t(n === 1 ? 'Dein Bild kann GitHub nicht über den Link übernehmen – nach dem Öffnen ins Issue ziehen.' : 'Deine {n} Bilder kann GitHub nicht über den Link übernehmen – nach dem Öffnen ins Issue ziehen.', { n })}` : ''}</div>
    ${f.fehler ? html`<p class="fein">${f.fehler}</p>` : nothing}
    <button class="knopf breit amber gh-senden" ?disabled=${f.sendet || !v} @click=${() => p.meldungSenden(true)}>${f.sendet ? t('sendet …') : html`${t('Speichern und weiter zu GitHub')} ↗`}</button>
    <button class="knopf breit leise-k" ?disabled=${f.sendet} @click=${() => p.githubZurueck()}>${t('Zurück')}</button>`;
}

function ticket(p, m) {
  const auf = offen(m);
  const letzte = (m.verlauf || []).filter((v) => v.notiz || v.version || v.commit).at(-1);
  return html`<div class="ml ${auf ? '' : 'erledigt'}"><div class="ml-kopf"><span><b>${m.ticket}</b> <span class="badge ${ART_FARBE[m.art] || ''}">${m.art_text}</span> <span class="badge ${STATUS_FARBE[m.status] || ''}">${m.status_text}</span></span>
      <span class="leise">${zeit(m.zeit)} · ${m.geraet || '–'} · v${m.version || '–'}</span></div>
    <div class="ml-text">${m.text}</div>${m.kontext ? html`<div class="leise">${m.kontext}</div>` : nothing}
    ${(m.bilder || []).length ? html`<div class="ml-bilder">${m.bilder.map((_, i) => { const u = p.meldungBild(m, i); return u ? html`<img src=${u} alt=${t('Bild {n}', { n: i + 1 })} @click=${() => p.bildGross(m, i)}>` : html`<i></i>`; })}</div>` : nothing}
    ${letzte ? html`<div class="ml-notiz">${[letzte.von, letzte.version && `v${letzte.version}`, letzte.commit && `Commit ${letzte.commit}`, letzte.notiz].filter(Boolean).join(' · ')}</div>` : nothing}
    ${p.istAdmin ? html`<div class="ml-k"><button class="chip glas-panel" @click=${() => p.meldungStatus(m, auf ? 'geschlossen' : 'neu')}>${auf ? `✓ ${t('Schließen')}` : `↺ ${t('wieder öffnen')}`}</button><button class="chip glas-panel" @click=${() => p.meldungLoeschen(m)}>${t('Löschen')}</button></div>` : nothing}</div>`;
}

/** Liste der Tickets (⚙ › Meldungen); p._blatt = { art: 'meldungen', filter } */
export function meldungenBlatt(p) {
  const alle = p._daten.meldungen, f = p._blatt.filter || 'offen';
  const anzahl = (k) => !alle ? '' : k === 'alle' ? alle.length : alle.filter((m) => (k === 'offen') === offen(m)).length;
  const liste = (alle || []).filter((m) => f === 'alle' || (f === 'offen') === offen(m));
  return html`<div class="griff"></div><button class="zu" @click=${() => p.zu()}>✕</button>
    <h3>${t('Meldungen')}</h3><div class="leise">${t('Jede Meldung ist ein Ticket: FE Fehler, WU Wunsch, AN Anregung')}</div>
    ${seg([['offen', `${t('offen')} ${anzahl('offen')}`], ['erledigt', `${t('erledigt')} ${anzahl('erledigt')}`], ['alle', `${t('alle')} ${anzahl('alle')}`]], f, (v) => { p._blatt = { ...p._blatt, filter: v }; })}
    ${!alle ? html`<div class="leer">${t('lädt …')}</div>` : liste.length ? liste.map((m) => ticket(p, m)) : html`<div class="leer">${t('Keine Meldungen')}</div>`}
    ${alle && alle.length ? html`<div class="ml-k"><button class="chip glas-panel" @click=${() => p.meldungenKopieren()}>${t('Als Markdown kopieren')}</button></div>` : nothing}
    <p class="hinweis">${t('Die Tickets bleiben lokal in Home Assistant und liegen lesbar unter heimnetz/meldungen.md. Ist eines erledigt, wird es geschlossen; passt es nicht, hier wieder öffnen.')}${p.istAdmin ? '' : ` ${t('Schließen und löschen dürfen nur Admins.')}`}</p>`;
}

export function bildBlatt(p) {
  const { m, i } = p._blatt, u = p.meldungBild(m, i);
  return html`<div class="griff"></div><button class="zu" @click=${() => p.meldungenOeffnen()}>✕</button>
    <h3>${m.ticket} · ${t('Bild {n}', { n: i + 1 })}</h3>${u ? html`<img class="mb-gross" src=${u} alt=${t('Bild {n}', { n: i + 1 })}>` : html`<div class="leer">${t('lädt …')}</div>`}`;
}

/** Zeile im Fenster Einstellungen */
export function meldungenZeile(p) {
  const alle = p._daten.meldungen, n = alle ? alle.filter(offen).length : null;
  return html`<div class="ez"><span>${t('Tickets aus dem Melden-Knopf')}<small>${t('Fehler, Wünsche, Anregungen – lokal gespeichert')}</small></span>
    <button class="blau" @click=${() => p.meldungenOeffnen()}>${alle ? t('{n} offen · {erledigt} erledigt', { n, erledigt: alle.length - n }) : '–'} ›</button></div>`;
}

export function alsMarkdown(liste) {
  return liste.map((m) => `- [${offen(m) ? ' ' : 'x'}] **${m.ticket} ${m.art_text}** (${m.status_text}, ${zeit(m.zeit)}, v${m.version || '–'}, ${m.geraet || '–'}, ${m.kontext || '–'}): ${m.text}`).join('\n');
}
