// Fenster „Einstellungen“ (⚙ im Kopf): alles Einstellbare an einem Ort – Speedtest-Auswertung, Messplan, WLAN,
// Meldungen. Seit AN-0002 (Mockup netzwerk.html · Einstellungen gruppiert, Variante B, 13.10.2026) mit Reitern oben,
// darunter nur die gewählte Gruppe in einer Karte. Werte und Zustand kommen von der Integration. WU-0007: fünfter
// Reiter „Einrichtung“ (Mockup netzwerk.html · Einrichtung, 27.10.2026) – was eingerichtet ist, erkennt die Integration
// (heimnetz/einrichtung), die Seite zeigt nur an und öffnet Home Assistant oder HACS an der richtigen Stelle.
// WU-0008: sechster Reiter „Diagnose“ (Mockup netzwerk.html · Diagnose, 27.10.2026) – fragt auf Knopfdruck die
// Rohdaten eines vorgeschalteten Modems ab (heimnetz/modem); Abfragen und Schwärzen macht die Integration, die Seite
// zeigt nur an und speichert/kopiert die geschwärzte Antwort. WU-0009: Reiter „Zugang“ vor „Einrichtung“ (Mockup
// netzwerk.html · Internet und Zugang, 27.10.2026) – Vorschlag der Integration mit Belegen, Wahl des Admins, Adresse und
// Kennwort eines vorgeschalteten Geräts (das Kennwort speichert die Integration, die Seite bekommt nur „hinterlegt“).
import { html, nothing } from 'lit';
import { live } from 'lit/directives/live.js';
import { uhr, zahl, zeit } from '../format.js';
import { merke, t, tl } from '../sprache.js';
import { seg } from './teile.js';
import { meldungenZeile } from './melden.js';

const MODI = [['aus', merke('weglassen')], ['halb', '¼'], ['mit', merke('voll')]];
const TAKTE = [[1, '1 h'], [2, '2 h'], [4, '4 h'], [6, '6 h'], [12, '12 h'], [24, '24 h']];
const VERKEHR = [['warten', merke('verschieben')], ['messen', merke('messen')]];
const SERIE = [[2, '2'], [3, '3'], [4, '4'], [5, '5']];
const SCHWACH = [[30, '30 %'], [40, '40 %'], [50, '50 %']];

export const TEILE = [['speed', '📈 Speedtest'], ['plan', merke('⏱️ Messplan')], ['wlan', merke('📶 WLAN')], ['meld', merke('💬 Meldungen')],
  ['zugang', merke('🌐 Zugang')], ['einr', merke('🧩 Einrichtung')], ['diag', merke('🔬 Diagnose')]];
const WAHL = {
  auto: [merke('Automatisch (empfohlen)'), ''],
  box_mobil: [merke('Mobilfunk über die FRITZ!Box'), merke('eingebautes Modem oder Stick')],
  extern: [merke('Mobilfunk über ein vorgeschaltetes Modem'), merke('ZTE, Huawei, TP-Link … (Beta)')],
  dsl: [merke('DSL über die FRITZ!Box'), merke('ADSL, VDSL, Supervectoring')],
  glasfaser: [merke('Glasfaser'), merke('über die FRITZ!Box oder ein eigenes Glasfaser-Modem')],
  kabel: [merke('Kabel'), merke('über die FRITZ!Box')],
};
const ERSATZ = [['auto', merke('automatisch')], ['kein', merke('keiner')]];
const STUFEN = { muss: merke('Muss'), soll: merke('Soll – empfohlen'), kann: merke('Kann – optional') };
const ZEICHEN = { ok: '✓', fehlt: '!', muss: '✕', aus: '–' };

export function einstellungenBlatt(p) {
  const e = p._daten.einstellungen;
  const teil = p._blatt.teil || 'speed';
  const kopf = html`<div class="griff"></div><button class="zu" @click=${() => p.zu()}>✕</button>
    <h3>${t('Einstellungen')}</h3><div class="leise">${p.istAdmin ? t('gelten für die ganze Seite') : t('nur Admins ändern')}</div>
    <div class="seg e-reiter">${TEILE.map(([k, name]) => html`<button class=${k === teil ? 'on' : ''} @click=${() => { p._blatt = { ...p._blatt, teil: k }; if (k === 'einr') p.einrichtungLaden(); if (k === 'zugang') p.zugangLaden(); }}>${t(name)}${k === 'einr' ? punkt(p) : nothing}</button>`)}</div>`;
  if (teil === 'einr') return html`${kopf}<div class="ek"><div class="ek-inhalt">${einrichtung(p)}</div></div>`;
  if (teil === 'diag') return html`${kopf}<div class="ek"><div class="ek-inhalt">${diagnose(p)}</div></div>`;
  if (teil === 'zugang') return html`${kopf}<div class="ek"><div class="ek-inhalt">${zugang(p)}</div></div>`;
  if (!e) return html`${kopf}<div class="leer">${t('lädt …')}</div>`;
  const inhalt = { speed: auswertung, plan: messplan, wlan, meld: (q) => meldungenZeile(q) }[teil](p, e);
  return html`${kopf}<div class="ek"><div class="ek-inhalt">${inhalt}</div></div>`;
}

/** Eingabe mit Einheit im ruhigen Feld-Stil der Seite. */
function feld(name, wert, einheit, admin, typ = 'number') {
  return html`<label class="ein"><input name=${name} type=${typ} min="0" step="1" .value=${wert ?? ''} ?disabled=${!admin}>${einheit ? html`<small>${einheit}</small>` : nothing}</label>`;
}

function auswertung(p, e) {
  const admin = p.istAdmin;
  const speichern = (ev) => {
    const f = ev.target.closest('.sheet');
    p.einstellungenSpeichern({
      tarif_down: f.querySelector('[name=tarif_down]').value || null,
      tarif_up: f.querySelector('[name=tarif_up]').value || null,
      ab: f.querySelector('[name=ab]').value || null,
    });
  };
  return html`
    <div class="ez"><span>${t('Tarif Download')}</span>${feld('tarif_down', e.tarif_down, 'Mbit/s', admin)}</div>
    <div class="ez"><span>${t('Tarif Upload')}</span>${feld('tarif_up', e.tarif_up, 'Mbit/s', admin)}</div>
    <div class="ez"><span>${t('Auswerten ab')}<small>${t('ältere Messungen zählen nicht')}</small></span>${feld('ab', e.ab, '', admin, 'date')}</div>
    ${admin ? html`<div class="leiste" style="justify-content:flex-end;padding:4px 0"><button class="knopf haupt" @click=${speichern}>${t('Speichern')}</button></div>` : nothing}
    ${p._hinweis ? html`<p class="fein">${p._hinweis}</p>` : nothing}
    <div class="ez"><span>${t('Belastete Messungen')}<small>${t('über {n} Mbit/s Verkehr vor der Messung', { n: zahl(e.schwelle) })}</small></span>${seg(tl(MODI), p._opt.speedtest.grundlast, (v) => p.setze('speedtest', { grundlast: v }, p._reiter === 'speedtest'))}</div>
    <p class="hinweis">${t('Die Auswahl „belastete Messungen“ gilt für das Wochenraster auf diesem Gerät.')}</p>`;
}

function messplan(p, e) {
  if (!e.messplan) return nothing;
  const m = e.messplan, z = e.plan, o = e.ookla, admin = p.istAdmin;
  const setzen = (werte) => p.messplanSetzen(werte);
  const belastet = e.verkehr_mbit != null && e.verkehr_mbit > e.schwelle;
  const naechste = !m.an ? `– (${t('aus')})`
    : z.misst ? t('misst gerade …')
    : z.wartet ? t('verschoben – neuer Versuch {uhr}', { uhr: uhr(z.neuer_versuch) })
    : z.naechste ? zeit(z.naechste) : '–';
  return html`<p class="hinweis" style="margin:2px 0 4px">${t('Gemessen wird von der Ookla-Integration; dieser Plan sagt ihr, wann.')}</p>
    ${!o.vorhanden ? html`<div class="befund"><span class="punkt rot"></span><div><b>${t('Ookla-Integration fehlt')}</b><p>${t('Ohne sie kann der Plan nicht messen.')}</p></div></div>` : nothing}
    ${o.misst_selbst ? html`<div class="befund"><span class="punkt amber"></span><div><b>${t('Ookla misst zusätzlich nach eigenem Takt')}</b><p>${t('In den Ookla-Einstellungen ist „manuell“ aus – dann misst Ookla neben diesem Plan. Für einen einzigen Plan dort „manuell“ einschalten.')}</p></div></div>` : nothing}
    <div class="ez"><span>${t('Automatisch messen')}</span><button class="sw ${m.an ? 'on' : ''}" role="switch" aria-checked=${m.an ? 'true' : 'false'} ?disabled=${!admin} @click=${() => setzen({ an: !m.an })}><i></i></button></div>
    <div class="ez"><span>${t('Wie oft')}</span>${admin ? seg(TAKTE, m.takt_h, (v) => setzen({ takt_h: v })) : html`<span class="leise">${t('alle {n} h', { n: m.takt_h })}</span>`}</div>
    ${volumen(e.volumen)}
    <div class="ez"><span>${t('Nur zwischen')}</span><span>
      <label class="ein"><input type="time" .value=${live(m.von === '24:00' ? '00:00' : m.von)} ?disabled=${!admin} @change=${(ev) => setzen({ von: ev.target.value || '00:00' })}></label> –
      <label class="ein"><input type="time" .value=${live(m.bis === '24:00' ? '00:00' : m.bis)} ?disabled=${!admin} @change=${(ev) => setzen({ bis: ev.target.value === '00:00' ? '24:00' : ev.target.value || '24:00' })}></label></span></div>
    <div class="ez"><span>${t('Bei Verkehr im Heimnetz')}<small>${t('über {n} Mbit/s', { n: zahl(e.schwelle) })}</small></span>${admin ? seg(tl(VERKEHR), m.verkehr, (v) => setzen({ verkehr: v })) : html`<span class="leise">${m.verkehr === 'warten' ? t('verschieben') : t('trotzdem messen')}</span>`}</div>
    <div class="ez"><span>${t('Serie „{n}× messen“', { n: m.serie })}<small>${t('Durchläufe hintereinander, Ergebnis als Median')}</small></span>${admin ? seg(SERIE, m.serie, (v) => setzen({ serie: v })) : html`<span class="leise">${m.serie}×</span>`}</div>
    <div class="ez"><span>${t('Server der Serie')}<small>${t('alle Ookla-Tests reihum')}${o.server ? ` – ${o.server}` : ''}</small></span><span class="leise">${o.tests ?? 0} ${o.tests === 1 ? 'Test' : 'Tests'}</span></div>
    <div class="ez"><span>${t('Verkehr gerade')}</span><span class=${belastet ? 'rot-t' : 'leise'}>${e.verkehr_mbit == null ? '–' : `${zahl(e.verkehr_mbit, 1)} Mbit/s – ${belastet ? t('belastet') : t('ruhig')}`}</span></div>
    <div class="ez"><span>${t('Nächste Messung')}</span><span class="leise">${naechste}</span></div>
    <div class="ez"><span>${t('Server und „manuell“')}<small>${t('in Ookla eingestellt')}</small></span><button class="blau" @click=${() => { p.zu(); p.oeffne('/config/integrations/integration/ookla_speedtest'); }}>Ookla ›</button></div>
    ${p._hinweisPlan ? html`<p class="fein">${p._hinweisPlan}</p>` : nothing}
    <p class="hinweis">${t('Wird verschoben, versucht es der Plan alle 5 Minuten neu, höchstens 30 Minuten lang; danach misst er trotzdem und die Messung gilt als belastet.')}</p>`;
}

/** WU-0006: Datenvolumen der Messungen – geschätzt rechnet die Integration (letzte Messung, sonst Tarif), hier nur
 *  der Satz dazu. Ohne Werte der allgemeine Hinweis. */
function volumen(v) {
  if (!v) return nothing;
  const text = v.je_test_mb == null
    ? t('Jede Messung kostet Datenvolumen – bei schnellen Anschlüssen einige hundert MB. Bei Mobilfunk mit Datenlimit lieber selten messen.')
    : v.tests_tag
      ? t('Jede Messung kostet etwa {mb} MB Datenvolumen; mit diesem Plan {n} Messungen am Tag, rund {tag} MB am Tag und {monat} GB im Monat. Bei Mobilfunk mit Datenlimit lieber selten messen.',
        { mb: zahl(v.je_test_mb), n: v.tests_tag, tag: zahl(v.tag_mb), monat: zahl(v.monat_gb, 1) })
      : t('Jede Messung kostet etwa {mb} MB Datenvolumen.', { mb: zahl(v.je_test_mb) });
  return html`<p class="hinweis volumen" style="margin:0 0 4px">${text}</p>`;
}

function wlan(p, e) {
  const admin = p.istAdmin;
  return html`
    <div class="ez"><span>${t('Schwacher Empfang unter')}<small>${t('so meldet die Box den Empfang je Gerät')}</small></span>${admin
      ? seg(SCHWACH, e.wlan_schwach, (v) => p.einstellungenSpeichern({ wlan_schwach: v }))
      : html`<span class="leise">${e.wlan_schwach} %</span>`}</div>
    <p class="hinweis">${t('Kanal, Gast-WLAN und Bänder stellst du in der FRITZ!Box ein – die Seite ändert dort nichts.')}</p>`;
}

/** WU-0009: Zugang – Vorschlag mit Belegen, Auswahl, vorgeschaltetes Gerät, Ersatz. Nur Admins. */
function zugang(p) {
  if (!p.istAdmin) return html`<p class="hinweis" style="padding-top:8px">${t('Den Zugang legen nur Admins fest.')}</p>`;
  const z = p._daten.zugang;
  if (!z) return p._hinweisZugang ? html`<p class="fein">${p._hinweisZugang}</p>` : html`<div class="leer">${t('lädt …')}</div>`;
  const vorgeschaltet = z.wahl === 'extern' || (z.wahl === 'auto' && z.vorschlag_art === 'extern');
  const adresseFeld = (ev) => ev.target.closest('.sheet').querySelector('input[name=zg-adresse]');
  const kennwortFeld = (ev) => ev.target.closest('.sheet').querySelector('input[name=zg-kennwort]');
  const speichern = (ev) => {
    const kw = kennwortFeld(ev);
    const werte = { adresse: adresseFeld(ev).value.trim() || null };
    if (kw && kw.value) werte.kennwort = kw.value;
    p.zugangSetzen(werte, kw);
  };
  return html`
    <div class="vs-kopf"><b>${t('Vorschlag: {text}', { text: z.vorschlag })}</b><br><span class="leise">${z.belege.map((b, i) => html`${i ? html`<br>` : nothing}✓ ${b}`)}</span></div>
    <div class="vs-stufe"><span>${t('Internet kommt über')}</span><span></span></div>
    ${z.wahlen.map((k) => {
      const [name, unter] = WAHL[k] || [k, ''];
      const text = k === 'auto' ? t('jetzt: {text}', { text: z.vorschlag }) : t(unter);
      return html`<button class="zg" data-wahl=${k} @click=${() => z.wahl !== k && p.zugangSetzen({ wahl: k })}><span class="zg-r ${z.wahl === k ? 'on' : ''}"></span><span>${t(name)}<small>${text}</small></span></button>`;
    })}
    ${vorgeschaltet ? html`<div class="vs-stufe"><span>${t('Vorgeschaltetes Gerät')}</span><span></span></div>
      <label class="dg-feld">${t('Adresse')}<input name="zg-adresse" inputmode="decimal" list="zg-adressen" .value=${live(z.adresse || z.adresse_jetzt || z.adressen[0] || '')}>
        <small>${t('vorgeschlagen: {liste} – nur Adressen im eigenen Heimnetz', { liste: z.adressen.join(', ') })}</small></label>
      <datalist id="zg-adressen">${z.adressen.map((a) => html`<option value=${a}></option>`)}</datalist>
      <label class="dg-feld">${t('Kennwort der Weboberfläche')}<input name="zg-kennwort" type="password" autocomplete="off" placeholder=${z.kennwort ? t('hinterlegt – zum Ändern neu eingeben') : t('wie beim Anmelden im Browser')}>
        <small>${t('wird in Home Assistant gespeichert (wie bei anderen Integrationen), nie angezeigt')}</small></label>
      <div class="dg-knoepfe"><button class="amber" @click=${speichern}>${t('Speichern')}</button>${z.kennwort ? html`<button @click=${() => p.zugangSetzen({ kennwort_loeschen: true })}>${t('Kennwort entfernen')}</button>` : nothing}</div>
      <p class="hinweis" style="margin-top:6px">${t('Laufende Werte vom vorgeschalteten Gerät folgen in einer späteren Fassung; bis dahin zeigt 🔬 Diagnose die Rohdaten.')}</p>` : nothing}
    <div class="vs-stufe"><span>${t('Ersatzzugang bei Ausfall')}</span><span></span></div>
    <div class="ez"><span>${t('Ersatz')}<small>${t('z. B. Mobilfunk-Stick an der FRITZ!Box, wenn DSL ausfällt')}</small></span>${seg(tl(ERSATZ), z.ersatz_wahl, (v) => p.zugangSetzen({ ersatz: v }))}</div>
    ${p._hinweisZugang ? html`<p class="fein">${p._hinweisZugang}</p>` : nothing}
    <div class="dg-knoepfe" style="margin-top:8px"><button @click=${() => p.zugangSuchen()}>${t('↻ Erneut suchen')}</button>
      <button @click=${() => p.zuDiagnose(vorgeschaltet ? z.adresse || z.adresse_jetzt || z.adressen[0] : null)}>${t('🔬 Rohdaten abfragen ›')}</button></div>
    <p class="hinweis" style="margin-top:8px">${t('Gefragt wird nur die FRITZ!Box – kein Absuchen des Heimnetzes. Vorgeschlagen werden die Adresse vor der Box und übliche Modem-Adressen (192.168.0.1, 192.168.1.1, 192.168.8.1). Heimnetz liest nur.')}</p>`;
}

/** WU-0007: Punkt am Reiter – rot, wenn Nötiges fehlt, orange, wenn Empfohlenes fehlt (Farbe von der Integration). */
function punkt(p) {
  const d = p.istAdmin && p._daten.einrichtung;
  if (!d || !d.punkt) return nothing;
  return html`<span class="e-punkt ${d.punkt === 'rot' ? 'rot' : ''}"></span>`;
}

/** WU-0007: Voraussetzungen in den Stufen Muss / Soll / Kann wie im README. */
function einrichtung(p) {
  if (!p.istAdmin) return html`<p class="hinweis" style="padding-top:8px">${t('Was eingerichtet ist, sehen nur Admins.')}</p>`;
  const d = p._daten.einrichtung;
  if (p._hinweisEinr) return html`<p class="fein">${p._hinweisEinr}</p>`;
  if (!d) return html`<div class="leer">${t('lädt …')}</div>`;
  const kopf = d.muss_fehlt
    ? html`<div class="vs-kopf"><b class="rot-t">${t(d.muss_fehlt === 1 ? '{n} Voraussetzung fehlt' : '{n} Voraussetzungen fehlen', { n: d.muss_fehlt })}</b> – ${t('was dann fehlt, steht in der Zeile. Fehlen FRITZ!Box Tools oder Recorder, auch unter Einstellungen › System › Reparaturen.')}</div>`
    : d.soll_fehlt
      ? html`<div class="vs-kopf"><b class="amber-t">${t('{n} empfohlen', { n: d.soll_fehlt })}</b> – ${t(d.soll_fehlt === 1 ? 'Heimnetz läuft, mit diesem Teil zeigt es mehr.' : 'Heimnetz läuft, mit diesen Teilen zeigt es mehr.')}</div>`
      : html`<div class="vs-kopf"><b class="ok">${t('Alles Nötige ist eingerichtet.')}</b></div>`;
  return html`${kopf}
    ${d.stufen.map((s) => html`<div class="vs-stufe"><span>${t(STUFEN[s.stufe] || s.stufe)}</span><span>${t('{ok} von {von}', { ok: s.ok, von: s.von })}</span></div>
      ${s.teile.map((x) => html`<div class="vs" data-teil=${x.schluessel}><span class="vs-st ${x.status}">${ZEICHEN[x.status] || ''}</span><span>${x.name}<small>${x.wofuer}</small></span>
        <span class="vs-r">${x.stand ? html`<span class="leise">${x.stand}</span>` : nothing}${x.hinweis ? html`<span class="leise">${x.hinweis}</span>` : nothing}${x.aktionen.map((a) => html`<button class=${a.blau ? 'blau' : ''} @click=${() => p.einrichtungAktion(a)}>${a.text}</button>`)}</span></div>`)}`)}
    <p class="hinweis" style="margin-top:8px">${t('Heimnetz installiert nichts selbst: die Knöpfe öffnen Home Assistant oder HACS an der richtigen Stelle. Nach einem Download aus HACS Home Assistant neu starten, dann einrichten. Geprüft wird beim Öffnen dieses Reiters.')}</p>`;
}

/** WU-0008: Diagnose – Rohdaten eines vorgeschalteten Modems. Nur Admins; Abfragen und Schwärzen macht die Integration. */
const ROH = '⟨geschwärzt⟩';
const BEFUND = {
  adresse_nicht_erlaubt: ['amber', merke('Adresse nicht erlaubt'), merke('Die Adresse liegt nicht im eigenen Heimnetz. Abgefragt werden nur private Adressen (192.168.x.x, 10.x.x.x, 172.16–31.x.x).')],
  nicht_erreichbar: ['rot', merke('Modem nicht erreichbar'), merke('Unter dieser Adresse antwortet nichts. Adresse prüfen – sie steht in den Einstellungen des Modems oder auf einem Aufkleber.')],
  kein_zte: ['amber', merke('Kein ZTE-Modem erkannt'), merke('Unter dieser Adresse antwortet etwas, aber kein ZTE-Modem. Diese Version unterstützt vorerst nur ZTE-Modems.')],
  anmeldung_abgelehnt: ['rot', merke('Anmeldung abgelehnt'), merke('Das Modem lehnt das Kennwort ab. Ohne Anmeldung fehlen die Signalwerte. Kennwort prüfen und noch einmal abfragen.')],
};

function diagnose(p) {
  if (!p.istAdmin) return html`<p class="hinweis" style="padding-top:8px">${t('Diese Abfrage können nur Admins starten.')}</p>`;
  const d = p._diag;
  const kopf = html`
    <p class="hinweis" style="margin:4px 0 6px">${t('Kommt das Internet über ein eigenes 5G/LTE-Modem vor der FRITZ!Box (z. B. ZTE), kennt die Box das Funknetz nicht – Internet › Mobilfunk bleibt leer. Hier liest Heimnetz die Rohdaten des Modems aus, damit der Entwickler es unterstützen kann.')} <span class="neu">BETA</span></p>
    <label class="dg-feld">${t('Adresse des Modems')}<input name="adresse" inputmode="decimal" .value=${live(d.adresse)} ?disabled=${d.laeuft} @input=${(ev) => { p._diag = { ...p._diag, adresse: ev.target.value }; }}></label>
    <label class="dg-feld">${t('Kennwort der Weboberfläche (optional)')}<input name="kennwort" type="password" autocomplete="off" placeholder=${t('wie beim Anmelden im Browser')} ?disabled=${d.laeuft}><small>${t('wird nur für diese Abfrage verwendet und nicht gespeichert – leer: das unter 🌐 Zugang für diese Adresse hinterlegte')}</small></label>
    <div class="dg-knoepfe"><button class="amber" ?disabled=${d.laeuft} @click=${() => p.modemAbfragen()}>${d.laeuft ? t('⏳ fragt ab …') : t('▶ Abfragen')}</button></div>
    ${d.fehler ? html`<p class="fein">${d.fehler}</p>` : nothing}`;
  if (!d.antwort) return html`${kopf}<p class="hinweis" style="margin-top:8px">${t('Nur Adressen im eigenen Heimnetz (z. B. 192.168.x.x). Heimnetz liest nur und ändert am Modem nichts.')}</p>`;
  return html`${kopf}${ergebnis(p, d.antwort)}`;
}

function befundBlock(befund) {
  const b = BEFUND[befund];
  if (!b) return nothing;
  return html`<div class="befund" style="margin-top:8px"><span class="punkt ${b[0]}"></span><div><b>${t(b[1])}</b><p>${t(b[2])}</p></div></div>`;
}

function rohAnzeige(daten) {
  const text = JSON.stringify(daten, null, 2);
  return text.split(ROH).flatMap((s, i) => (i === 0 ? [s] : [html`<i>${ROH}</i>`, s]));
}

function ergebnis(p, a) {
  if (!a.abfragen.length) {
    return html`${befundBlock(a.befund)}${a.befund === 'anmeldung_abgelehnt'
      ? html`<div class="dg-knoepfe"><button @click=${() => p.modemSpeichern()}>${t('⬇ Trotzdem als Datei speichern')}</button></div>`
      : nothing}`;
  }
  const s = a.summen;
  return html`${befundBlock(a.befund)}
    <div class="vs-stufe" style="margin-top:6px"><span>${t('Ergebnis')}</span><span>${t('{ok} von {gesamt} Abfragen · {werte} Werte · {geschwaerzt} geschwärzt', { ok: s.ok, gesamt: s.gesamt, werte: s.werte, geschwaerzt: s.geschwaerzt })}</span></div>
    ${a.abfragen.map((ab) => html`<div class="dg-ab"><span class="vs-st ${ab.status === 'ok' ? 'ok' : 'aus'}" style="width:18px;height:18px;font-size:10px">${ab.status === 'ok' ? '✓' : '–'}</span><span>${ab.name}</span><code>${ab.angabe}</code></div>`)}
    <div class="dg-roh">${rohAnzeige(a.daten)}</div>
    <div class="gh-warn"><b>${t('Geschwärzt:')}</b> ${t('IMEI, IMSI, ICCID, Rufnummer, Seriennummer, MAC- und öffentliche IP-Adressen, WLAN-Namen und -Kennwörter. Die Zellkennung bleibt drin – daraus lässt sich ungefähr bestimmen, wo das Modem steht.')}</div>
    <div class="dg-knoepfe"><button class="amber" @click=${() => p.modemSpeichern()}>${t('⬇ Als Datei speichern')}</button><button @click=${() => p.modemKopieren()}>${t('⧉ Kopieren')}</button></div>
    <p class="hinweis" style="margin-top:8px">${t('Datei an den Entwickler schicken – per Mail oder als Anhang an ein GitHub-Issue. Heimnetz sendet selbst nichts.')}</p>`;
}
