// Reiter „Wächter“ und Fenster „Wächter einrichten“ (Mockup 1.8 und 3.8, Herbert 18.11.2026). Alles Fachliche (welches
// Gerät hängt, wann geschaltet wird) machen die Integration und das Skript auf der Steckdose; hier nur Anzeige und
// Bedienung.
import { html, nothing } from 'lit';
import { zeit, zahl } from '../format.js';
import { merke, t } from '../sprache.js';
import { seg } from './teile.js';

const ARTEN = [
  ['internet', merke('Internet'), merke('die Geräte, über die das Internet kommt – neu gestartet wird nur das, das hängt')],
  ['ha', merke('Home Assistant (dieser Pi)'), merke('nur Strom aus/ein – prüft die Steckdose selbst')],
  ['geraet', merke('Anderes Gerät im Heimnetz'), merke('Repeater, Switch, Kamera … – Strom aus/ein, wenn es nicht mehr antwortet')],
];
const SANFT_TABELLE = [
  ['AVM FRITZ!Box', merke('sanft (TR-064) + Strom'), true],
  ['ZTE (goform: MC801A, MC888, MF289 …)', merke('sanft (Weboberfläche, Beta) + Strom'), true],
  ['Huawei (HiLink: B535, B818, 5G CPE …)', merke('sanft (Weboberfläche, Beta) + Strom'), true],
  ['TP-Link (Archer MR/NX)', merke('sanft (Weboberfläche, Beta) + Strom'), true],
  [merke('andere'), merke('nur Strom aus/ein'), false],
];
const PUNKT = { ok: '', amber: 'amber', rot: 'rot', grau: 'grau' };

const marke = (text, ok) => html`<span class="leise wa-marke"><span class="vs-st ${ok ? 'ok' : 'aus'}">${ok ? '✓' : '–'}</span>${text}</span>`;

function glied(g) {
  return html`<div class="zeile wa-glied">
    <span class="wa-links"><span class="punkt ${PUNKT[g.punkt] ?? 'grau'}"></span>
      <span>${g.symbol} ${g.name}<small class="leise wa-klein">${g.adresse} · ${g.zustand}${g.veraltet ? ` · ${t('Skript veraltet – neu einspielen')}` : ''}</small></span></span>
    <span class="leise wa-rechts">${g.dose ? html`🔌 ${g.dose}${g.leistung != null ? ` · ${zahl(g.leistung, 1)} W` : ''}` : t('keine Steckdose')}
      <small>${g.sanft ? t('sanft: {weg}', { weg: g.sanft }) : t('nur Strom aus/ein')}</small></span>
  </div>`;
}

function karte(p, w) {
  const admin = p.istAdmin;
  const r = w.regeln;
  const regel = w.art === 'internet'
    ? t('sanft nach {a} min · Strom {s} s aus nach {b} min · höchstens alle {c} min', { a: r.stufe1_min, b: r.stufe2_min, s: r.aus_s, c: r.abstand_min })
    : t('Strom {s} s aus nach {b} min · höchstens alle {c} min', { b: r.stufe2_min, s: r.aus_s, c: r.abstand_min });
  const pause = w.glieder.some((g) => g.punkt === 'rot' && g.dose);
  return html`<div class="glas-panel block wa-karte">
    <div class="block-kopf"><h3>${w.symbol} ${w.name}</h3>
      <span class="leise"><span class="punkt ${PUNKT[w.punkt] ?? 'grau'}" style="margin:0 6px 0 0"></span>${w.an ? t('an') : t('aus')}</span></div>
    <div class="leise wa-regel">${regel}</div>
    ${w.glieder.map((g, i) => html`${i ? html`<div class="leise wa-pfeil">↓</div>` : nothing}${glied(g)}`)}
    ${w.weg_seit ? html`<div class="vs-kopf" style="margin-top:8px"><b>${t('Kein Internet seit {zeit}', { zeit: zeit(w.weg_seit) })}</b></div>` : nothing}
    ${admin ? html`<div class="leiste" style="margin-top:8px">
      <span class="leise">${t('{n} Eingriffe', { n: w.eingriffe })}</span><span style="flex:1"></span>
      ${seg([['an', t('an')], ['aus', t('aus')]], w.an ? 'an' : 'aus', (v) => p.waechterAendern(w.id, v))}
      ${w.weg_seit || w.punkt === 'amber' ? html`<button class="knopf amber" @click=${() => p.waechterAendern(w.id, 'ruhe')}>${t('Eingriff abbrechen')}</button>` : nothing}
      ${pause ? html`<button class="knopf" @click=${() => p.waechterAendern(w.id, 'weiter')}>${t('Pause beenden')}</button>` : nothing}
      <button class="knopf" @click=${() => p.waechterEinrichten(w.roh)}>${t('Bearbeiten')}</button>
    </div>` : nothing}
  </div>`;
}

export function waechter(p, d) {
  const liste = d.waechter || [];
  const admin = p.istAdmin;
  return html`
    ${liste.length ? html`<div class="raster2">${liste.map((w) => karte(p, w))}</div>` : html`<div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Was ist ein Wächter?')}</h3></div>
      <p class="hinweis">${t('Ein Wächter schaut laufend, ob das Internet noch geht oder Home Assistant noch antwortet. Hängt etwas, findet er das Gerät, das schuld ist, und startet es neu: zuerst sanft über seine Schnittstelle (FRITZ!Box, ZTE, Huawei, TP-Link), dann mit einer Shelly-Steckdose Strom aus und wieder ein.')}</p>
      <p class="hinweis">${t('Gebraucht wird je Gerät eine Shelly-Steckdose der Generation 2 oder neuer (z. B. Plus Plug S, Plug S Gen3). Sie bekommt ein kleines Skript und arbeitet damit selbstständig weiter, auch wenn Home Assistant hängt.')}</p>
    </div>`}
    ${admin ? html`<div class="leiste"><button class="knopf haupt" @click=${() => p.waechterEinrichten()}>＋ ${t('Wächter einrichten')}</button></div>` : nothing}
    <div class="glas-panel block">
      <div class="block-kopf"><h3>${t('Eingriffe')}</h3><span class="leise">${t('letzte 30 Tage')}</span></div>
      ${(d.eingriffe || []).length
        ? d.eingriffe.map((e) => html`<div class="ereig"><span class="punkt amber"></span><time>${zeit(e.t)}</time><span>${e.text}</span></div>`)
        : html`<div class="leer">${t('Noch kein Eingriff.')}</div>`}
    </div>
    <p class="hinweis" style="padding:0 4px">${t('Der Wächter sucht zuerst, welches Gerät hängt, und startet nur dieses neu – erst sanft, dann Strom aus und von selbst wieder ein, nie zwei zugleich. Bremse: höchstens einmal je Abstand, nach mehreren Eingriffen ohne Erfolg eine Pause (dann liegt es meist am Anbieter). Strom aus/ein macht die Steckdose selbst, auch wenn Home Assistant hängt.')}</p>`;
}

// ── Fenster „Wächter einrichten“ ──

function schritte(p, b) {
  return html`<div class="seg e-reiter">${[merke('1 Gerät'), merke('2 Steckdose'), merke('3 Regeln')].map((name, i) =>
    html`<button class=${b.schritt === i + 1 ? 'on' : ''} @click=${() => i + 1 < b.schritt && p.waechterSetze({ schritt: i + 1, fehler: '' })}>${i + 1 < b.schritt ? '✓ ' : ''}${t(name)}</button>`)}</div>`;
}

function schritt1(p, b) {
  const f = b.form, v = b.vorschlag;
  return html`
    <div class="vs-stufe"><span>${t('Überwachen')}</span><span></span></div>
    ${ARTEN.map(([k, name, text]) => html`<button class="zg" @click=${() => p.waechterArt(k)}><span class="zg-r ${f.art === k ? 'on' : ''}"></span><span>${t(name)}<small>${t(text)}</small></span></button>`)}
    ${f.art === 'internet' ? html`
      <div class="vs-stufe"><span>${t('Kette des Internets')}</span><span class="leise">${t('aus ⚙ → Zugang')}</span></div>
      ${f.glieder.length ? f.glieder.map((g, i) => html`${i ? html`<div class="leise wa-pfeil">↓</div>` : nothing}<div class="zeile"><span>${g.typ === 'fritzbox' ? '🛜' : '📡'} ${g.name}<small class="leise wa-klein">${g.adresse}</small></span>${marke(g.sanft ? t('sanft möglich') : t('nur Strom aus/ein'), g.sanft)}</div>`)
        : html`<div class="leer">${t('Keine Kette gefunden – erst ⚙ → Zugang prüfen.')}</div>`}
      <p class="hinweis">${t('Stimmt die Kette nicht, ist sie in ⚙ → Zugang zu ändern. Ohne vorgeschaltetes Modem (DSL, Glasfaser, Kabel in der FRITZ!Box) besteht sie nur aus der Box.')}</p>
      <div class="glas-panel block" style="margin-top:10px;padding:10px 12px">
        <div class="block-kopf"><h3 style="font-size:14px">${t('Welche Geräte gehen wie?')}</h3></div>
        ${SANFT_TABELLE.map(([name, text, ok]) => html`<div class="zeile"><span>${t(name)}</span>${marke(t(text), ok)}</div>`)}
        <p class="hinweis">${t('Sanft heißt: Neustart über die Schnittstelle des Geräts, mit dem dort hinterlegten Kennwort (FRITZ!Box aus FRITZ!Box Tools, Modem aus ⚙ → Zugang). Die Einstellungen des Geräts ändert Heimnetz nie. Geht das nicht, bleibt der Strom-Neustart über die Steckdose.')}</p>
      </div>` : nothing}
    ${f.art === 'ha' ? html`<div class="zeile"><span>🏠 Home Assistant<small class="leise wa-klein">${f.glieder[0]?.adresse || t('Adresse nicht gefunden')}</small></span>${marke(t('nur Strom aus/ein'), false)}</div>` : nothing}
    ${f.art === 'geraet' ? html`
      <label class="feld"><span>${t('Name')}</span><input .value=${f.glieder[0]?.name || ''} @input=${(e) => p.waechterGlied(0, { name: e.target.value })}></label>
      <label class="feld"><span>${t('Adresse im Heimnetz')}</span><input .value=${f.glieder[0]?.adresse || ''} placeholder="192.168.178.20" @input=${(e) => p.waechterGlied(0, { adresse: e.target.value.trim() })}></label>` : nothing}
    ${v ? nothing : html`<div class="leer">${t('sucht Steckdosen …')}</div>`}`;
}

function schritt2(p, b) {
  const f = b.form, dosen = (b.vorschlag && b.vorschlag.dosen) || [];
  const eigene = new Set(f.glieder.map((g) => g.dose).filter(Boolean));
  return html`
    <div class="vs-stufe"><span>${t('Je Gerät eine Steckdose')}</span><span class="leise">${t('{n} Shellys gefunden', { n: dosen.length })}</span></div>
    ${f.glieder.map((g, i) => {
      const d = dosen.find((x) => x.adresse === g.dose);
      return html`<div class="zeile wa-dose"><span>${g.typ === 'fritzbox' ? '🛜' : g.typ === 'ha' ? '🏠' : '📡'} ${g.name || g.adresse}
          <small class="leise wa-klein">${d ? (d.leistung != null ? t('misst jetzt {w} W', { w: zahl(d.leistung, 1) }) : d.modell) : t('keine Steckdose – nur sanfter Neustart')}</small></span>
        <span class="wa-wahl"><select @change=${(e) => p.waechterGlied(i, { dose: e.target.value || null })}>
          <option value="" ?selected=${!g.dose}>${t('keine')}</option>
          ${dosen.map((x) => html`<option value=${x.adresse} ?selected=${x.adresse === g.dose}
            ?disabled=${!x.passt || (x.belegt && x.belegt !== f.id) || (eigene.has(x.adresse) && x.adresse !== g.dose)}>${x.name} · ${x.adresse}${x.passt ? (x.leistung != null ? ` (${zahl(x.leistung, 1)} W)` : '') : ` – ${t('Gen 1, zu alt')}`}${x.belegt && x.belegt !== f.id ? ` – ${t('schon belegt')}` : ''}</option>`)}
        </select>${g.dose ? html`<button class="knopf" title=${t('LED der Steckdose kurz blinken lassen – der Strom bleibt an')} @click=${() => p.waechterBlinken(g.dose)}>💡</button>` : nothing}</span>
      </div>`;
    })}
    <p class="hinweis">${t('Die gemessene Leistung hilft beim Zuordnen (ein Router braucht meist 6–15 W, ein Pi 3–8 W). 💡 lässt die LED der Steckdose kurz blinken – der Strom bleibt an.')}</p>
    <div class="vs-stufe" style="margin-top:10px"><span>${t('Zugang zu den Steckdosen')}</span><span></span></div>
    <label class="feld"><span>${t('Kennwort der Steckdosen')} <span class="leise">· ${b.kennwort_da ? t('hinterlegt – leer lassen, um es zu behalten') : t('nur wenn dort eines gesetzt ist')}</span></span>
      <input type="password" autocomplete="off" .value=${b.kennwort || ''} @input=${(e) => p.waechterSetze({ kennwort: e.target.value })}></label>
    <p class="hinweis">${t('Jede Steckdose bekommt ein kleines Skript von Heimnetz. Es läuft auf der Steckdose und prüft selbst – so wird ein Gerät auch wieder eingeschaltet, wenn mit dem Router das WLAN weg ist. In einer Kette warten die Steckdosen aufeinander. Andere Skripte und Einstellungen der Steckdose bleiben unberührt. Kennwort und feste Adresse (in der FRITZ!Box) sind empfohlen.')}</p>`;
}

function zahlFeld(p, f, k, name, einheit, klein) {
  return html`<div class="zeile"><span>${t(name)}<small class="leise wa-klein">${t(klein)}</small></span>
    <span class="wa-zahl"><input type="number" .value=${String(f.regeln[k] ?? '')} @change=${(e) => p.waechterRegel(k, Number(e.target.value))}><span class="leise">${einheit}</span></span></div>`;
}

function schritt3(p, b) {
  const f = b.form;
  return html`
    <div class="vs-stufe"><span>${t('Prüfen')}</span><span></span></div>
    <div class="zeile"><span>${t('alle')}<small class="leise wa-klein">${f.art === 'internet' ? t('drei Prüfseiten im Internet und die Geräte der Kette') : t('ob das Gerät antwortet (und der Router, sonst ist das WLAN schuld)')}</small></span>
      ${seg([[30, '30 s'], [60, '60 s'], [120, '120 s']], f.regeln.pruef_s, (v) => p.waechterRegel('pruef_s', v))}</div>
    <div class="vs-stufe"><span>${t('Eingreifen')}</span><span class="leise">${f.art === 'internet' ? t('nur beim Gerät, das hängt') : ''}</span></div>
    ${f.art === 'internet' ? zahlFeld(p, f, 'stufe1_min', merke('1 · sanft neu starten nach'), 'min', merke('über die Schnittstelle des Geräts · nur wenn Home Assistant läuft')) : nothing}
    ${zahlFeld(p, f, 'stufe2_min', merke('2 · Strom aus/ein nach'), 'min', merke('macht die Steckdose selbst'))}
    ${zahlFeld(p, f, 'aus_s', merke('Strom aus für'), 's', merke('danach schaltet die Steckdose von selbst wieder ein'))}
    <div class="vs-stufe"><span>${t('Bremse')}</span><span></span></div>
    ${zahlFeld(p, f, 'abstand_min', merke('höchstens alle'), 'min', merke('je Gerät · kein Dauer-Neustart'))}
    ${zahlFeld(p, f, 'pause_nach', merke('Pause nach Fehlschlägen'), '×', merke('Eingriffe ohne Erfolg in Folge'))}
    ${zahlFeld(p, f, 'pause_h', merke('Pause dauert'), 'h', merke('z. B. bei einer Störung beim Anbieter'))}
    <div class="zeile"><span>🔔 ${t('Bei Eingriff melden')}<small class="leise wa-klein">${t('über das Ziel aus ⚙ → Warnungen')}</small></span>
      ${seg([[true, t('ja')], [false, t('nein')]], f.regeln.melden !== false, (v) => p.waechterRegel('melden', v))}</div>
    <div class="vs-kopf" style="margin-top:10px"><b>${t('Auf die Steckdosen spielen')}</b><br><span class="leise">${t('Heimnetz legt das Skript „heimnetz-waechter“ auf den gewählten Steckdosen an und startet es. Auf den Steckdosen wird sonst nichts geändert; Löschen nimmt es wieder herunter.')}</span></div>`;
}

export function waechterBlatt(p) {
  const b = p._blatt;
  const neu = !b.form.id;
  const weiterOk = b.schritt === 1
    ? b.form.glieder.length > 0 && b.form.glieder.every((g) => g.adresse)
    : b.schritt === 2 ? b.form.glieder.some((g) => g.dose) || (b.form.art === 'internet' && b.form.glieder.some((g) => g.sanft)) : true;
  return html`<button class="zu" @click=${() => p.zu()}>✕</button>
    <h3>${neu ? t('Wächter einrichten') : t('Wächter bearbeiten')}</h3>
    <div class="leise">${b.schritt === 1 ? t('Was soll überwacht und bei Ausfall neu gestartet werden?') : b.form.glieder.map((g) => g.name || g.adresse).join(' → ')}</div>
    ${schritte(p, b)}
    <div class="ek"><div class="ek-inhalt">
      ${b.schritt === 1 ? schritt1(p, b) : b.schritt === 2 ? schritt2(p, b) : schritt3(p, b)}
      ${b.fehler ? html`<div class="fehler-band glas-panel" style="margin-top:8px">${b.fehler}</div>` : nothing}
      <div class="dg-knoepfe wa-knoepfe">
        ${b.schritt > 1 ? html`<button class="knopf leise-k" @click=${() => p.waechterSetze({ schritt: b.schritt - 1, fehler: '' })}>‹ ${t('Zurück')}</button>`
          : neu ? html`<button class="knopf leise-k" @click=${() => p.zu()}>${t('Abbrechen')}</button>`
            : html`<button class="knopf leise-k" @click=${() => p.waechterLoeschen()}>${b.frage ? t('Wirklich löschen?') : t('Löschen')}</button>`}
        ${b.schritt < 3
          ? html`<button class="knopf haupt" ?disabled=${!weiterOk} @click=${() => p.waechterSetze({ schritt: b.schritt + 1, fehler: '' })}>${t('Weiter')}</button>`
          : html`<button class="knopf haupt" ?disabled=${b.laeuft} @click=${() => p.waechterSpeichern()}>${b.laeuft ? t('spielt ein …') : t('Einspielen und starten')}</button>`}
      </div>
    </div></div>`;
}
