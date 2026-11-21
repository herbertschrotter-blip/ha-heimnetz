// Netzkarte (1.9, abgenommen 20.11.2026, Mockup mockups/seiten/netzkarte.html 0.2): eigene Seite unter Geräte, die Karte
// füllt den Bildschirm, Titel, Filter, Zahlen und Infokarte schweben als Glas darüber. Sternkarte: FRITZ!Box in der Mitte,
// Internet kommt von oben; Ringe = Anbindung, Sektoren = Art, Switch an einer Buchse mit mehreren Geräten, Repeater mit
// seinen Geräten. Lage, Texte und Zahlen liefert die Integration (heimnetz/netzkarte); die Seite zeichnet nur.
// Maus über einem Punkt: Name, IP, Anbindung, Zustand; Tipp: Weg hervorgehoben, Infokarte mit „Verlauf öffnen ›“.
// Dazu zwei Ansichten (1.10, abgenommen 21.11.2026, Mockup mockups/seiten/netz-ideen.html 0.1): „Fluss“ – Internet →
// Box → Anbindung → Gerät als fließende Bänder (Breite = Geschwindigkeit der Verbindung) – und „Radar“ – ein Strahl
// kreist, Geräte leuchten auf; Abstand = Empfang. Lage und Zahlen liefert die Integration (fluss, radar).
import { html, svg, nothing } from 'lit';
import { keyed } from 'lit/directives/keyed.js';
import { unsafeSVG } from 'lit/directives/unsafe-svg.js';
import { zeit } from '../format.js';
import { merke, t, tl } from '../sprache.js';

const FILTER = [['alle', merke('Alle')], ['kabel', merke('Kabel')], ['wlan', 'WLAN'], ['auff', merke('⚠ Auffällig')]];
const ZUSTAND = { an: merke('online'), wackelt: merke('wackelt'), schwach: merke('schwacher Empfang'), neu: merke('neu'), aus: merke('offline') };
const FARBE = { an: 'var(--nk-gruen)', wackelt: 'var(--amber)', schwach: 'var(--amber)', neu: 'var(--blau)' };
const AUFF = ['wackelt', 'schwach', 'neu'];
const ANSICHTEN = [['karte', merke('🗺️ Karte')], ['fluss', merke('〰️ Fluss')], ['radar', merke('📡 Radar')]];
// Farbe je Gruppe bzw. Band (amber bleibt „schwach/wackelt“)
const FB = { kabel: 'var(--nk-gruen)', 5: 'var(--blau)', '2,4': 'var(--s5)', 6: 'var(--s3)', wlan: 'var(--ink2)', rep: 'var(--ink)', vpn: 'var(--ink2)', schwach: 'var(--amber)' };

function passt(g, filter) {
  if (filter === 'kabel') return g.kabel;
  if (filter === 'wlan') return !g.kabel && g.ueber !== 'vpn';
  if (filter === 'auff') return AUFF.includes(g.zustand);
  return true;
}

function tip(g, i, d, an, kennung = i) {
  const b = 140, h = 56;
  const x = g.x < d.breite * 0.66 ? g.x + 16 : g.x - 16 - b;
  const y = Math.max(4, Math.min(d.hoehe - h - 4, g.y - h / 2));
  const z = g.ueber === 'vpn' && g.seit ? t('verbunden seit {zeit}', { zeit: zeit(g.seit) }) : t(ZUSTAND[g.zustand] || g.zustand);
  return svg`<g class="nk-tip ${an ? 'an' : ''}" data-i=${kennung}><rect x=${x} y=${y} width=${b} height=${h} rx="9"></rect>
    <text class="t1" x=${x + 10} y=${y + 15}>${g.symbol} ${g.name}</text><text class="t2" x=${x + 10} y=${y + 27}>${g.ip}</text>
    <text class="t3" x=${x + 10} y=${y + 39}>${g.anbindung}</text>
    <text class="t4" x=${x + 10} y=${y + 50} style="fill:${g.ueber === 'vpn' ? 'var(--s5)' : FARBE[g.zustand] || 'var(--ink2)'}">● ${z}${g.gast ? ` · ${t('Gast')}` : ''}</text></g>`;
}

function karte(p, d, u, o) {
  const m = d.mitte;
  const wahl = o.wahl;
  const dimm = !!wahl || o.filter !== 'alle';
  const hebt = (g) => (wahl ? g.id === wahl || g.switch === wahl : passt(g, o.filter));
  const weg = !d.box_erreichbar;
  const inet = u && u.leitung ? u.leitung.knoten : null;
  const zg = inet ? inet[2] : null;
  const netzOk = inet ? inet[3].zustand === 'gut' : false;
  const s = u && u.speedtest;
  const r = d.dot;
  const auswaehlen = (id) => p.setze('geraete', { karte: { ...o, wahl: id === wahl ? null : id } }, false);
  const vpn = d.vpn ? d.vpn.geraete : [];
  const hover = [...d.geraete.map((_, i) => `${i}`), ...vpn.map((_, i) => `v${i}`)]
    .map((k) => `svg:has(.nk-g[data-i="${k}"]:hover) .nk-tip[data-i="${k}"]{opacity:1}`).join('');
  return html`<svg viewBox="0 0 ${d.breite} ${d.hoehe}" preserveAspectRatio="xMidYMid meet" role="img" aria-label=${t('Netzkarte')}
      class="nk-svg ${dimm ? 'dimm' : ''} ${o.namen ? 'namen' : ''} ${weg ? 'grau' : ''}">${svg`
    ${d.ringe.map((x, i) => svg`<circle class="nk-ring ${i ? 'gestr' : ''}" cx=${m.x} cy=${m.y} r=${x.r}></circle>
      <text class="nk-ringname" x=${m.x - 9} y=${m.y - x.r + 11} text-anchor="end">${x.name}</text>`)}
    ${d.sektoren.map((x) => svg`<text class="nk-sektor" x=${x.x} y=${x.y} text-anchor="middle" dominant-baseline="central">${x.name}</text>`)}
    ${netzOk && !weg
      ? svg`<line class="nk-uplink" x1=${m.x} y1=${m.y - 30} x2=${m.x} y2="38"></line><line class="nk-uplink-fluss" x1=${m.x} y1=${m.y - 30} x2=${m.x} y2="38"></line>`
      : svg`<line class="nk-ring gestr" x1=${m.x} y1=${m.y - 30} x2=${m.x} y2="38"></line>`}
    ${zg ? svg`<g class="nk-klick" @click=${() => p.geh('internet')}><circle class="nk-knoten ${zg.zustand}" cx=${m.x} cy="74" r="13"></circle>
      <text class="nk-sym" x=${m.x} y="74.5" style="font-size:13px">${zg.symbol}</text>
      <text class="nk-kb" x=${m.x + 20} y="72">${zg.name}</text><text class="nk-kt" x=${m.x + 20} y="84">${zg.text}</text></g>` : nothing}
    <g class="nk-klick" @click=${() => p.geh('speedtest')}><circle class="nk-knoten ${netzOk ? 'gut' : 'weg'}" cx=${m.x} cy="24" r="14"></circle>
      <text class="nk-sym" x=${m.x} y="24.5" style="font-size:14px">🌐</text>
      <text class="nk-kb" x=${m.x + 21} y="22">Internet</text>
      <text class="nk-kt" x=${m.x + 21} y="34">${s && s.down != null ? `↓ ${Math.round(s.down)} · ↑ ${Math.round(s.up)} Mbit/s · ${Math.round(s.ping)} ms` : inet ? inet[3].text : ''}</text></g>
    ${d.repeater.map((x) => svg`<g class="nk-klick">
      <line class="nk-rep-draht ${x.kabel ? 'kabel' : ''}" x1=${m.x} y1=${m.y} x2=${x.x} y2=${x.y}></line><line class="nk-fluss" x1=${m.x} y1=${m.y} x2=${x.x} y2=${x.y}></line>
      <circle class="nk-rep-halo" cx=${x.x} cy=${x.y} r="46"></circle><circle class="nk-rep" cx=${x.x} cy=${x.y} r="16"></circle>
      <text class="nk-sym" x=${x.x} y=${x.y + 0.5} style="font-size:14px">📶</text>
      <text class="nk-name an" x=${x.x} y=${x.y + 28}>${x.name}</text><title>${x.name} · ${x.text}</title></g>`)}
    <g>${d.geraete.map((g) => svg`<g class="nk-draht z-${g.zustand} ${hebt(g) ? 'gew' : ''}">
      <line class=${g.kabel ? 'nk-lan' : 'nk-wlan'} x1=${g.vx} y1=${g.vy} x2=${g.x} y2=${g.y}></line>
      <line class="nk-fluss ${g.kabel ? '' : 'wlan'}" x1=${g.vx} y1=${g.vy} x2=${g.x} y2=${g.y} style="opacity:${(0.35 + Math.min(1, (g.mbit || 50) / 600) * 0.6).toFixed(2)}"></line></g>`)}</g>
    ${d.switche.map((x) => svg`<g class="nk-sw nk-klick ${wahl === x.id ? 'gew' : ''}" @click=${() => auswaehlen(x.id)}>
      <line class="nk-sw-draht" x1=${m.x} y1=${m.y} x2=${x.x} y2=${x.y}></line><line class="nk-fluss" x1=${m.x} y1=${m.y} x2=${x.x} y2=${x.y}></line>
      <rect class="nk-sw-kern" x=${x.x - 13} y=${x.y - 10} width="26" height="20" rx="5"></rect>
      <text class="nk-sym" x=${x.x} y=${x.y - 2} style="font-size:8px">⇄</text><text class="nk-sw-name" x=${x.x} y=${x.y + 6}>LAN ${x.port}</text></g>`)}
    ${d.geraete.filter((g) => g.px != null).map((g) => svg`<g class="nk-draht ${hebt(g) ? 'gew' : ''}"><rect class="nk-port-bg" x=${g.px - 11} y=${g.py - 5.5} width="22" height="11" rx="5.5"></rect>
      <text class="nk-port" x=${g.px} y=${g.py + 0.5}>LAN ${g.port}</text></g>`)}
    ${d.aus.map((x) => svg`<circle class="nk-aus" cx=${x.x} cy=${x.y} r="4.5"><title>${x.name} · ${t('offline')}</title></circle>`)}
    <g class=${weg ? 'nk-weg' : ''} @click=${() => p.geh('internet')}>
      <circle class="nk-box-halo" cx=${m.x} cy=${m.y} r="30">${weg ? nothing : svg`<animate attributeName="r" values="30;54" dur="2.6s" repeatCount="indefinite"></animate><animate attributeName="opacity" values=".22;0" dur="2.6s" repeatCount="indefinite"></animate>`}</circle>
      <circle class="nk-box-halo" cx=${m.x} cy=${m.y} r="34" style="opacity:.1"></circle>
      <circle class="nk-box" cx=${m.x} cy=${m.y} r="27"></circle><text class="nk-sym" style="font-size:20px" x=${m.x} y=${m.y - 4}>🛜</text>
      <text class="nk-name an" x=${m.x} y=${m.y + 15} style="font-weight:700">FRITZ!Box</text></g>
    <g>${d.geraete.map((g, i) => {
      const gr = wahl === g.id ? r + 4 : r;
      const puls = g.zustand === 'schwach' || g.zustand === 'neu'
        ? svg`<circle cx=${g.x} cy=${g.y} r=${gr} fill="none" stroke=${g.zustand === 'neu' ? 'var(--blau)' : 'var(--amber)'} stroke-width="1.5"><animate attributeName="r" values="${gr};${gr + 9}" dur="1.8s" repeatCount="indefinite"></animate><animate attributeName="opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"></animate></circle>`
        : nothing;
      return svg`<g class="nk-g z-${g.zustand} ${hebt(g) ? 'gew' : ''}" data-i=${i} @click=${() => auswaehlen(g.id)}>${puls}
        <circle class="nk-dot" cx=${g.x} cy=${g.y} r=${gr}></circle><text class="nk-sym" x=${g.x} y=${g.y + 0.5} style="font-size:${gr}px">${g.symbol}</text>
        <text class="nk-name" x=${g.x} y=${g.y + gr + 10}>${g.name}</text></g>`;
    })}</g>
    ${d.vpn ? svg`<g class="nk-klick"><line class="nk-vpn-draht" x1=${m.x - 14} y1="28" x2=${d.vpn.x + 14} y2=${d.vpn.y - 6}></line>
      <line class="nk-vpn-fluss" x1=${m.x - 14} y1="28" x2=${d.vpn.x + 14} y2=${d.vpn.y - 6}></line>
      <circle class="nk-vpn-halo" cx=${d.vpn.x} cy=${d.vpn.y} r="40"></circle><circle class="nk-vpn" cx=${d.vpn.x} cy=${d.vpn.y} r="15"></circle>
      <text class="nk-sym" style="font-size:13px" x=${d.vpn.x} y=${d.vpn.y + 0.5}>🔐</text>
      <text class="nk-name an" style="font-weight:700" x=${d.vpn.x} y=${d.vpn.y - 21}>VPN · WireGuard</text></g>
      ${vpn.map((g, i) => svg`<g class="nk-g z-vpn ${hebt(g) ? 'gew' : ''}" data-i="v${i}" @click=${() => auswaehlen(g.id)}>
        <line class="nk-vpn-draht duenn" x1=${g.vx} y1=${g.vy} x2=${g.x} y2=${g.y}></line>
        <circle class="nk-dot" cx=${g.x} cy=${g.y} r=${wahl === g.id ? r + 4 : r}></circle><text class="nk-sym" x=${g.x} y=${g.y + 0.5} style="font-size:${r}px">${g.symbol}</text>
        <text class="nk-name" x=${g.x} y=${g.y + r + 10}>${g.name}</text></g>`)}` : nothing}
    ${d.geraete.map((g, i) => tip(g, i, d, false))}
    ${vpn.map((g, i) => tip(g, i, d, false, `v${i}`))}
    ${unsafeSVG(`<style>${hover}</style>`)}`}
  </svg>`;
}

const kurve = (x1, y1, x2, y2) => `M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`;
function zug(d, w, farbe, dauer, an = true) {
  return svg`<path class="ni-band" d=${d} stroke=${farbe} stroke-width=${w}></path>${an ? svg`<path class="ni-funke" d=${d} stroke-width=${Math.min(3.2, w * 0.5)} style="animation-duration:${dauer}s"></path>` : nothing}`;
}

/** 1.10 A Datenfluss: Internet → FRITZ!Box → Gruppe → Gerät. */
function fluss(p, d, u, o) {
  const f = d.fluss;
  const { x } = f;
  const y0 = f.mitte;
  const weg = !d.box_erreichbar;
  const farbe = Object.fromEntries(f.gruppen.map((g) => [g.id, FB[g.farbe] || 'var(--ink2)']));
  const gy = Object.fromEntries(f.gruppen.map((g) => [g.id, g.y]));
  const auswaehlen = (id) => p.setze('geraete', { karte: { ...o, wahl: id === o.wahl ? null : id } }, false);
  const zg = u && u.leitung ? u.leitung.knoten[2] : null;
  const i = f.internet;
  return html`<svg viewBox="0 0 ${f.breite} ${f.hoehe}" preserveAspectRatio="xMidYMid meet" role="img" aria-label=${t('Datenfluss')}
      class="ni-svg ${o.wahl ? 'dimm' : ''} ${weg ? 'grau' : ''}">${svg`
    <g class="ni-zug">${zug(kurve(x.internet + 14, y0, x.box - 22, y0), i.breite, 'var(--ink)', 0.9, !weg && i.down > 0)}</g>
    ${f.gruppen.map((g) => svg`<g class="ni-zug">${zug(kurve(x.box + 22, y0, x.gruppe - 14, g.y), g.breite, farbe[g.id], 1.2, !weg)}</g>`)}
    ${f.geraete.map((g) => svg`<g class="ni-zug ${o.wahl === g.id ? 'gew' : ''}">${zug(kurve(x.gruppe + 14, gy[g.gruppe], x.geraet - 9, g.y), g.breite,
      AUFF.slice(0, 2).includes(g.zustand) ? 'var(--amber)' : farbe[g.gruppe], (2.6 - Math.min(1.6, (g.mbit || 0) / 600)).toFixed(2), !weg)}</g>`)}
    <circle class="ni-knoten" cx=${x.internet} cy=${y0} r="15" stroke="var(--ink)"></circle><text class="nk-sym" x=${x.internet} y=${y0 + 0.5} style="font-size:14px">🌐</text>
    <text class="ni-tb" x=${x.internet - 12} y=${y0 - 46}>Internet</text>
    <text class="ni-t2" x=${x.internet - 12} y=${y0 - 34}>${i.down != null ? `↓ ${Math.round(i.down)}${i.tarif ? ` ${t('von')} ${Math.round(i.tarif)}` : ''} Mbit/s` : ''}</text>
    <text class="ni-t2" x=${x.internet - 12} y=${y0 - 24}>${zg ? zg.name : ''}</text>
    <g @click=${() => p.geh('internet')} class="nk-klick"><rect class="ni-knoten" x=${x.box - 22} y=${y0 - 24} width="44" height="48" rx="12" stroke=${weg ? 'var(--rot)' : 'var(--nk-gruen)'}></rect>
      <text class="nk-sym" x=${x.box} y=${y0 - 4} style="font-size:17px">🛜</text><text class="ni-t" x=${x.box} y=${y0 + 14} text-anchor="middle" font-weight="700">FRITZ!Box</text></g>
    ${f.gruppen.map((g) => svg`<circle class="ni-knoten" cx=${x.gruppe} cy=${g.y} r="13" stroke=${farbe[g.id]}></circle>
      <text class="nk-sym" x=${x.gruppe} y=${g.y + 0.5} style="font-size:11px">${g.farbe === 'kabel' ? '⇄' : g.farbe === 'vpn' ? '🔐' : g.farbe === 'rep' ? '📶' : '📡'}</text>
      <text class="ni-t" x=${x.gruppe} y=${g.y - 18} text-anchor="middle" font-weight="700">${g.name}</text>`)}
    ${f.geraete.map((g) => {
      const auff = AUFF.slice(0, 2).includes(g.zustand);
      return svg`<g class="nk-g ${o.wahl === g.id ? 'gew' : ''}" @click=${() => auswaehlen(g.id)}>
        <circle class="ni-knoten" cx=${x.geraet} cy=${g.y} r="8" stroke=${auff ? 'var(--amber)' : farbe[g.gruppe]}></circle><text class="nk-sym" x=${x.geraet} y=${g.y + 0.5} style="font-size:8px">${g.symbol}</text>
        <text class="ni-t" x=${x.geraet + 14} y=${g.y - 1}>${g.name}</text>
        <text class="ni-t2" x=${x.geraet + 14} y=${g.y + 9}>${g.mbit ? `${g.mbit} Mbit/s` : '–'}${auff ? ` · ${t(ZUSTAND[g.zustand])}` : ''}</text></g>`;
    })}`}
  </svg>`;
}

/** 1.10 C WLAN-Radar: Abstand = Empfang, der Strahl kreist; ein Gerät leuchtet auf, wenn er es trifft. */
function radar(p, d, o) {
  const r = d.radar;
  const m = r.mitte;
  const R = r.radius;
  const auswaehlen = (id) => p.setze('geraete', { karte: { ...o, wahl: id === o.wahl ? null : id } }, false);
  const hinten = { x: m.x + R * Math.cos(-0.7), y: m.y + R * Math.sin(-0.7) };
  const strahlen = Array.from({ length: 12 }, (_, i) => i * 30);
  return html`<svg viewBox="0 0 ${r.breite} ${r.hoehe}" preserveAspectRatio="xMidYMid meet" role="img" aria-label=${t('WLAN-Radar')}
      class="ni-svg ${o.wahl ? 'dimm' : ''} ${d.box_erreichbar ? '' : 'grau'}">${svg`
    <defs><radialGradient id="ni-grund"><stop offset="0" stop-color="var(--nk-gruen)" stop-opacity=".16"></stop><stop offset="1" stop-color="var(--nk-gruen)" stop-opacity="0"></stop></radialGradient>
      <linearGradient id="ni-keil" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="var(--nk-gruen)" stop-opacity="0"></stop><stop offset="1" stop-color="var(--nk-gruen)" stop-opacity=".55"></stop></linearGradient></defs>
    <circle cx=${m.x} cy=${m.y} r=${R} fill="url(#ni-grund)"></circle>
    ${r.ringe.map((x) => svg`<circle class="ni-ring" cx=${m.x} cy=${m.y} r=${x.r}></circle><text class="ni-ringname" x=${m.x + 4} y=${m.y - x.r + 10}>${x.name}</text>`)}
    ${strahlen.map((a) => svg`<line class="ni-kreuz" x1=${m.x} y1=${m.y} x2=${(m.x + R * Math.cos((a * Math.PI) / 180)).toFixed(1)} y2=${(m.y + R * Math.sin((a * Math.PI) / 180)).toFixed(1)}></line>`)}
    <g class="ni-strahl" style="transform-origin:${m.x}px ${m.y}px;animation-duration:${r.umlauf}s">
      <path d="M${m.x},${m.y} L${hinten.x.toFixed(1)},${hinten.y.toFixed(1)} A${R},${R} 0 0 1 ${m.x + R},${m.y} Z" fill="url(#ni-keil)" opacity=".55"></path>
      <line class="ni-kante" x1=${m.x} y1=${m.y} x2=${m.x + R} y2=${m.y}></line></g>
    ${r.geraete.map((g) => {
      const c = FB[g.farbe] || 'var(--ink2)';
      const gr = o.wahl === g.id ? 7 : 4.6;
      const takt = `animation-delay:${g.takt}s;animation-duration:${r.umlauf}s`;
      return svg`<g class="nk-g ${o.wahl === g.id ? 'gew' : ''}" @click=${() => auswaehlen(g.id)}>
        <circle class="ni-blip-hof" cx=${g.x} cy=${g.y} r="6" fill="none" stroke=${c} style=${takt}></circle>
        <circle class="ni-blip" cx=${g.x} cy=${g.y} r=${gr} fill=${c} style="${takt};filter:drop-shadow(0 0 5px ${c})"></circle>
        ${g.neu ? svg`<circle class="ni-neu" cx=${g.x} cy=${g.y} r=${gr + 4}></circle>` : nothing}
        <circle cx=${g.x} cy=${g.y} r="12" fill="transparent"></circle>
        <text class="ni-t" x=${g.links ? g.x - 8 : g.x + 8} y=${g.y + 3} text-anchor=${g.links ? 'end' : 'start'}>${g.name} <tspan class="ni-t2">${g.signal} %</tspan></text></g>`;
    })}
    <circle class="ni-knoten" cx=${m.x} cy=${m.y} r="17" stroke="var(--nk-gruen)"></circle><text class="nk-sym" x=${m.x} y=${m.y + 0.5} style="font-size:15px">🛜</text>`}
  </svg>`;
}

function zahlenFluss(f) {
  const i = f.internet;
  return html`<div class="glas-panel ni-zahlen"><div><b>${i.down != null ? Math.round(i.down) : '–'}</b><small>${t('MBIT/S JETZT')}</small></div>
    <div><b>${i.anteil != null ? `${i.anteil} %` : '–'}</b><small>${t('VOM TARIF')}</small></div>
    <div><b class="amber">${f.langsam}</b><small>${t('LANGSAM')}</small></div></div>
    <div class="glas-panel ni-karte"><b>${t('Wo es eng wird')}</b><span>${f.duennster
      ? t('{name} hängt mit {n} Mbit/s an {wo} – der dünnste Faden im Bild.', { name: f.duennster.name, n: f.duennster.mbit, wo: f.duennster.wo })
      : t('Keine Funkverbindung mit bekannter Geschwindigkeit.')}</span></div>
    <div class="nk-legende nk-nur-breit">${t('Breite = Geschwindigkeit der Verbindung. Wie viel ein einzelnes Gerät gerade lädt, meldet die FRITZ!Box nicht – nur der ganze Anschluss (oben links).')}</div>`;
}

function zahlenRadar(r) {
  const rand = r.rand.map((x) => `${x.name} (${x.signal} %)`).join(` ${t('und')} `);
  return html`<div class="glas-panel ni-zahlen" style="grid-template-columns:repeat(${1 + r.kanaele.length},minmax(0,1fr))"><div><b>${r.geraete.length}</b><small>${t('IM FUNK')}</small></div>
    ${r.kanaele.map((k) => html`<div><b>${t('Kanal')} ${k.kanal ?? (k.auto ? 'auto' : '–')}</b><small>${k.band} · ${k.n}</small></div>`)}</div>
    <div class="glas-panel ni-karte"><b>${t('Am Rand des Radars')}</b><span>${rand
      ? t('{liste}: am weitesten draußen – dort lohnt ein Repeater. Je näher an der Mitte, desto besser der Empfang.', { liste: rand })
      : t('Kein Gerät im WLAN mit Empfangswert.')}${r.ohne_empfang ? ` ${t('{n} ohne Empfangswert (z. B. am Repeater) – nicht auf dem Radar.', { n: r.ohne_empfang })}` : ''}</span></div>`;
}

function info(p, d, o) {
  const g = [...d.geraete, ...(d.vpn ? d.vpn.geraete : [])].find((x) => x.id === o.wahl);
  const sw = d.switche.find((x) => x.id === o.wahl);
  const zu = () => p.setze('geraete', { karte: { ...o, wahl: null } }, false);
  if (sw) {
    const dran = d.geraete.filter((x) => x.switch === sw.id);
    return html`<div class="glas-panel nk-info">
      <div class="nk-info-kopf"><span class="gross" style="border-color:var(--s1)">⇄</span><div><b>${sw.text}</b><small>${t('erkannt: mehrere Geräte an derselben Buchse')}</small></div><button class="nk-zu" title=${t('Schließen')} @click=${zu}>✕</button></div>
      <div class="nk-werte"><div><b>${sw.n}</b><small>${t('Geräte')}</small></div><div><b>${dran.map((x) => x.name).join(', ') || '–'}</b><small>${t('online')}</small></div><div><b>${sw.mbit ? (sw.mbit >= 1000 ? `${sw.mbit / 1000} Gbit/s` : `${sw.mbit} Mbit/s`) : '–'}</b><small>${t('Buchse')}</small></div></div>
      <p>${t('Die FRITZ!Box sieht einen einfachen Switch selbst nicht – nur, dass mehrere Geräte an derselben Buchse hängen.')}</p></div>`;
  }
  if (!g) return nothing;
  const rand = FARBE[g.zustand] || 'var(--ink2)';
  return html`<div class="glas-panel nk-info">
    <div class="nk-info-kopf"><span class="gross" style="border-color:${rand}">${g.symbol}</span><div><b>${g.name}</b><small>${g.ip} · ${g.anbindung}</small></div><button class="nk-zu" title=${t('Schließen')} @click=${zu}>✕</button></div>
    <div class="nk-werte">${g.ueber === 'vpn'
      ? html`<div><b>🔐</b><small>WireGuard</small></div><div><b>${g.seit ? zeit(g.seit) : '–'}</b><small>${t('verbunden seit')}</small></div>`
      : html`<div><b style="color:${rand}">${g.signal != null ? `${g.signal} %` : '–'}</b><small>${t('Empfang')}</small></div>`}
      ${g.ueber === 'vpn' ? nothing : html`<div><b>${g.mbit ?? '–'}</b><small>Mbit/s</small></div>`}<div><b style="color:${rand}">${t(ZUSTAND[g.zustand] || g.zustand)}</b><small>${t('Zustand')}</small></div></div>
    <button class="chip glas-panel" @click=${() => p.geraetOeffnen(g.id)}>${t('Verlauf öffnen ›')}</button></div>`;
}

/** Ganze Seite (statt der Liste unter Geräte). `d` = heimnetz/netzkarte, `u` = Übersicht (Leitung, Speedtest). */
export function netzkarte(p, d, u, fehler = '') {
  const o = { ansicht: 'karte', filter: 'alle', namen: false, wahl: null, ...(p._opt.geraete.karte || {}) };
  const ans = d && d[o.ansicht] ? o.ansicht : 'karte';
  const setz = (w) => p.setze('geraete', { karte: { ...o, ...w } }, false);
  const z = d ? d.zahlen : null;
  const name = { karte: t('Netzkarte'), fluss: t('Datenfluss'), radar: t('WLAN-Radar') }[ans];
  const titel = !d ? t('Netzkarte') : !d.box_erreichbar ? t('FRITZ!Box antwortet nicht') : name;
  const zeile = !d ? (fehler ? '' : t('lädt …')) : [t('Stand {zeit}', { zeit: zeit(d.stand) }), u && u.zugang ? u.zugang.kopf : ''].filter(Boolean).join(' · ');
  const legende = html`<div class="nk-legende"><span><i class="lg-lan"></i>${t('Kabel')}</span><span><i class="lg-wlan"></i>WLAN</span><span><i class="lg-sw"></i>Switch</span>
    <span><i class="lg-p" style="border-color:var(--nk-gruen)"></i>${t('gut')}</span><span><i class="lg-p" style="border-color:var(--amber)"></i>${t('schwach')}</span>
    <span><i class="lg-p" style="border-color:var(--blau)"></i>${t('neu')}</span><span><i class="lg-p" style="border-color:var(--ink2);opacity:.6"></i>${t('offline')}</span></div>`;
  const bild = !d ? nothing : ans === 'fluss' ? fluss(p, d, u, o) : ans === 'radar' ? keyed(`${d.stand}|${d.box_erreichbar}`, radar(p, d, o)) : karte(p, d, u, o);
  return html`<div class="nk-buehne ${ans === 'karte' ? 'zwei' : 'hoch'}">${bild}</div>
    <div class="nk-oben">
      <div class="glas-panel nk-leiste"><button class="nk-zurueck" title=${t('Zurück zu Geräte')} @click=${() => p.setze('geraete', { teil: 'geraete' })}>‹</button>
        <div class="nk-titel"><b><span class="punkt ${d && !d.box_erreichbar ? 'rot' : ''}"></span>${titel}</b><small>${zeile}</small></div></div>
      ${fehler ? html`<div class="glas-panel fehler-band">${t('Daten nicht abrufbar: {fehler}', { fehler })}</div>` : nothing}
      <div class="nk-filter nk-ansicht">${tl(ANSICHTEN).map(([k, n]) => html`<button class="chip glas-panel ${ans === k ? 'on' : ''}" @click=${() => setz({ ansicht: k, wahl: null })}>${n}</button>`)}</div>
      ${ans !== 'karte' ? nothing : html`<div class="nk-filter">${tl(FILTER).map(([k, n]) => html`<button class="chip glas-panel ${o.filter === k ? 'on' : ''}" @click=${() => setz({ filter: k, wahl: null })}>${n}</button>`)}
        <button class="chip glas-panel ${o.namen ? 'on' : ''}" @click=${() => setz({ namen: !o.namen })}>Aa ${t('Namen')}</button></div>`}
    </div>
    <div class="nk-unten">
      ${o.wahl && d ? info(p, d, o) : d && ans === 'fluss' ? zahlenFluss(d.fluss) : d && ans === 'radar' ? zahlenRadar(d.radar) : z
        ? html`<div class="glas-panel nk-zahlen"><div><b>${z.online}</b><small>${t('ONLINE')}</small></div><div><b>${z.offline}</b><small>${t('OFFLINE')}</small></div>
          <div><b class="amber">${z.auffaellig}</b><small>${t('AUFFÄLLIG')}</small></div><div><b class="blau">${z.neu}</b><small>${t('NEU')}</small></div></div>${legende}
          ${z && z.vpn ? html`<div class="nk-legende">🔐 ${t('{n} über VPN verbunden (oben links)', { n: z.vpn })}</div>` : nothing}
          ${d && !d.mesh ? html`<div class="nk-legende">${t('Die Box hat noch keine Mesh-Liste geliefert – Buchsen, Switch und Repeater folgen (alle 10 Minuten).')}</div>` : nothing}
          ${d && !d.box_erreichbar ? html`<div class="nk-legende">${t('Die Karte zeigt den letzten bekannten Stand.')}</div>` : nothing}
          <div class="nk-legende nk-nur-breit">${t('Maus über einen Punkt: Name, IP, Anbindung · Tippen hebt den Weg hervor · Kreise = Anbindung, weiter draußen = schwächerer Empfang · Sektor = Art')}</div>`
        : nothing}
    </div>`;
}
