// Stile der Seite: Glas-Stil wie ha-baustelle, übernommen aus dem abgenommenen Mockup mockups/netzwerk.html
// (ohne Vorführ-Leiste). Farben nur als Variablen; neue Werte zuerst im Mockup.
import { css, unsafeCSS } from 'lit';

const GLAS = `
:host { display: block; height: 100%; }
.menue-knopf { position: absolute; top: 10px; left: 14px; z-index: 6; width: 36px; height: 36px; border-radius: 50% !important; display: grid; place-items: center; font-size: 17px; color: var(--ink2); }
.fehler-band { padding: 10px 16px; border-color: var(--rot); color: var(--ink); font-size: 13px; }
.laden { opacity: .6; transition: opacity .2s; }
.leer { padding: 18px 0; text-align: center; color: var(--ink2); font-size: 13px; }
.knopf { padding: 7px 14px; border-radius: 12px; background: rgba(127,127,127,.2); font-size: 13px; }
.knopf.haupt { background: color-mix(in srgb, var(--blau) 30%, transparent); color: var(--ink); font-weight: 600; }
.knopf[disabled] { opacity: .45; cursor: not-allowed; }
.fein { color: var(--rot); font-size: 12px; }
/* ── ab hier: Glas-Stil wie ha-baustelle (frontend/src/alt.js, GLAS_CSS) ── */
.wurzel { position: relative; height: 100vh; height: 100dvh; font-family: -apple-system, "SF Pro Text", system-ui, "Segoe UI", Roboto, sans-serif; background: #0b0b0b; color: #fff; font-size: 14px; }
.wurzel.hell { background: #d9dee5; color: #111; }
.ui { position: absolute; inset: 0; }
.app { --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #008300;
  --ink: #fff; --ink2: rgba(255,255,255,.66); --gridc: rgba(255,255,255,.14); --axisc: rgba(255,255,255,.55); --amber: #ff9f0a; --rot: #ff6961; --blau: #64a8ff;
  --panel: rgba(255,255,255,.05); --panel-rand: rgba(255,255,255,.2); --sheet: rgba(28,32,44,.82);
  position: relative; height: 100%; overflow: hidden; color: var(--ink); container-type: inline-size; }
.hell .app { --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; --s6: #008300;
  --ink: #111; --ink2: rgba(0,0,0,.6); --gridc: rgba(0,0,0,.1); --axisc: rgba(0,0,0,.5); --amber: #d97800; --rot: #d7372b; --blau: #0a64d6;
  --panel: rgba(255,255,255,.2); --panel-rand: rgba(255,255,255,.65); --sheet: rgba(250,250,252,.86); }
:where(.app button) { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-align: inherit; }
.app input, .app select { font: inherit; color: var(--ink); background: rgba(127,127,127,.16); border: 1px solid var(--panel-rand); border-radius: 10px; padding: 7px 10px; }
.app select option { color: #111; }
.glas-bg { position: absolute; inset: 0; overflow: hidden; background: linear-gradient(165deg, var(--g1) 0%, var(--g2) 50%, var(--g3) 100%); }
.glas-bg[data-phase=morgen] { --g1: #2e2748; --g2: #4a3150; --g3: #6b4040; --f1: #ff8a5c; --f2: #6a7bd6; --f3: #d07ab8; }
.glas-bg[data-phase=tag]    { --g1: #1c3552; --g2: #1f4a70; --g3: #2a5575; --f1: #ffc766; --f2: #3aa0ff; --f3: #7fd0ff; }
.glas-bg[data-phase=abend]  { --g1: #2a1a36; --g2: #45203d; --g3: #5a2a2c; --f1: #ff7a2e; --f2: #d0457a; --f3: #7a4bd0; }
.glas-bg[data-phase=nacht]  { --g1: #070d1c; --g2: #0c1528; --g3: #131a33; --f1: #2c3e8a; --f2: #1b4a7a; --f3: #4b3a8a; }
.hell .glas-bg[data-phase=morgen] { --g1: #ffd9c7; --g2: #f5e0f0; --g3: #cfdcff; --f1: #ff9a6a; --f2: #9fb4ff; --f3: #f0a0c8; }
.hell .glas-bg[data-phase=tag]    { --g1: #cfe6ff; --g2: #e3f1ff; --g3: #fff3d6; --f1: #ffd060; --f2: #6ab8ff; --f3: #a8e0ff; }
.hell .glas-bg[data-phase=abend]  { --g1: #ffd2b0; --g2: #f7c6d8; --g3: #d9ccff; --f1: #ff8a3a; --f2: #ff6f9a; --f3: #a58aff; }
.hell .glas-bg[data-phase=nacht]  { --g1: #b9c4e0; --g2: #c9cde6; --g3: #d8d0ec; --f1: #6d80c8; --f2: #7fa3dc; --f3: #9a88d2; }
.glas-bg > i { position: absolute; border-radius: 50%; filter: blur(40px) saturate(1); opacity: .7; animation: schweben 14s ease-in-out infinite; }
.glas-bg .k1 { width: 260px; height: 260px; background: var(--f1); top: -60px; left: -60px; }
.glas-bg .k2 { width: 240px; height: 240px; background: var(--f2); top: 300px; right: -80px; animation-delay: -5s; }
.glas-bg .k3 { width: 200px; height: 200px; background: var(--f3); bottom: -40px; left: 40px; animation-delay: -9s; }
.glas-bg[data-phase=nacht] > i { opacity: .45; }
.scroll { position: absolute; inset: 0; overflow-y: auto; }
.seite { padding: 56px 14px 120px; display: flex; flex-direction: column; gap: 12px; max-width: 1100px; margin: 0 auto; animation: seite .28s cubic-bezier(.2,.7,.2,1) backwards; }
.glas-panel { background: var(--panel); border: 1px solid var(--panel-rand); backdrop-filter: blur(12px) saturate(1.4); -webkit-backdrop-filter: blur(12px) saturate(1.4);
  border-radius: 24px; box-shadow: 0 8px 32px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.22); }
.glas-kopf { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 16px 18px; flex-wrap: wrap; }
.glas-klein { font-size: 11px; letter-spacing: 1.2px; color: var(--ink2); text-transform: uppercase; }
.glas-kw { font-size: 38px; font-weight: 300; letter-spacing: -.5px; display: flex; align-items: baseline; gap: 4px; white-space: nowrap; line-height: 1; }
.glas-kw small, .glas-wert small { font-size: .5em; opacity: .7; }
.chip { display: inline-flex; align-items: center; gap: 5px; font-size: 13px; padding: 6px 12px; border-radius: 18px !important; transition: transform .15s; }
.chip:active { transform: scale(.96); } .chip.rot { color: var(--rot); } .chip.amber { color: var(--amber); }
.glas-raster { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.glas-k { padding: 12px; display: flex; flex-direction: column; gap: 3px; animation: rein .5s ease-out backwards;  /* FE-0003: kein Dauer-Schweben mehr, nur Einblenden */ transition: transform .2s cubic-bezier(.2,.7,.2,1), box-shadow .2s; }
.glas-k:hover { box-shadow: 0 14px 40px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.3); } .glas-k:active { transform: scale(.97); }
.glas-wert { font-size: 26px; font-weight: 300; } .glas-kwk { font-size: 12px; color: var(--ink2); }
.glas-nav { position: absolute; left: 14px; right: 14px; bottom: 22px; display: flex; justify-content: space-around; padding: 6px; z-index: 5; }
.glas-nav button { flex: 1; text-align: center; padding: 8px 2px; border-radius: 16px; font-size: 13px; color: var(--ink2); transition: background .2s, color .2s; }
.glas-nav button.on { color: var(--ink); font-weight: 700; background: rgba(255,255,255,.16); }
.hell .glas-nav button.on { background: rgba(255,255,255,.7); }
.glas-nav.sechs button { font-size: 12px; padding-left: 1px; padding-right: 1px; }
.block { padding: 14px 16px; display: flex; flex-direction: column; gap: 8px; }
.block-kopf { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.block-kopf h3 { margin: 0; font-size: 16px; font-weight: 600; }
.leise { color: var(--ink2); font-size: 12px; } .rot-t { color: var(--rot); } .blau { color: var(--blau); } .ok { color: #30d158; }
.zeile { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px; width: 100%; box-sizing: border-box; min-height: 44px; }
.block .zeile { padding: 8px 0; }
.block .zeile + .zeile { border-top: 1px solid var(--gridc); }
.gruppe { font-size: 11px; letter-spacing: 1.2px; text-transform: uppercase; color: var(--ink2); padding: 10px 0 2px; }
.g-ic { width: 32px; height: 32px; border-radius: 10px; display: grid; place-items: center; background: rgba(142,142,147,.22); flex: none; }
.seg { display: flex; padding: 3px; border-radius: 14px; background: rgba(120,120,128,.2); gap: 2px; }
.seg button { flex: 1; text-align: center; padding: 7px 6px; border-radius: 11px; font-size: 13px; color: var(--ink2); transition: background .2s, color .2s; white-space: nowrap; }
.seg button.on { background: rgba(255,255,255,.2); color: var(--ink); font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,.15); }
.hell .seg button.on { background: #fff; }
.seg.klein button { padding: 5px 10px; font-size: 12px; flex: none; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: rgba(142,142,147,.25); color: var(--ink2); white-space: nowrap; }
.badge.gruen { background: rgba(48,209,88,.22); color: #30d158; }
.badge.rot-b { background: rgba(255,69,58,.2); color: var(--rot); }
.badge.amber-b { background: color-mix(in srgb, var(--amber) 22%, transparent); color: var(--amber); }
.badge.blau-b { background: color-mix(in srgb, var(--blau) 22%, transparent); color: var(--blau); }
.schleier { position: absolute; inset: 0; background: rgba(0,0,0,.35); opacity: 0; pointer-events: none; transition: opacity .25s; z-index: 20; }
.schleier.an { opacity: 1; pointer-events: auto; }
.sheet { position: absolute; left: 8px; right: 8px; bottom: 8px; max-height: 82%; overflow-y: auto; z-index: 21; padding: 8px 18px 18px; background: var(--sheet);
  transform: translateY(110%); transition: transform .32s cubic-bezier(.2,.8,.2,1); border-radius: 28px; display: flex; flex-direction: column; gap: 10px; }
.sheet.an { transform: none; } .sheet > * { flex-shrink: 0; }
.sheet h3 { margin: 4px 0 0; font-size: 20px; }
.griff { width: 40px; height: 5px; border-radius: 3px; background: var(--ink2); opacity: .5; margin: 0 auto 4px; }
.sheet .zeile { padding: 8px 0; } .sheet .zeile + .zeile { border-top: 1px solid var(--gridc); }
.zu { position: absolute; top: 14px; right: 16px; font-size: 18px; color: var(--ink2); }
@keyframes schweben { 50% { transform: translate(30px, 40px) scale(1.15); } }
@keyframes seite { from { opacity: 0; transform: translateY(10px); } }
@keyframes rein { from { opacity: 0; transform: translateY(8px); } }
@media (prefers-reduced-motion: reduce) { .glas-k, .glas-bg > i, .seite, .strecke .fluss { animation: none !important; } }
@container (min-width: 700px) {
  .seite { padding: 84px 28px 40px; }
  .glas-nav { top: 16px; bottom: auto; left: 50%; right: auto; transform: translateX(-50%); width: 620px; }
  .glas-raster { grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); }
  .sheet { left: 50%; right: auto; width: 520px; bottom: auto; top: 50%; transform: translate(-50%, -40%) scale(.96); opacity: 0; pointer-events: none;
    transition: transform .25s cubic-bezier(.2,.8,.2,1), opacity .2s; }
  .sheet.an { transform: translate(-50%, -50%); opacity: 1; pointer-events: auto; }
  .griff { display: none; }
  .raster2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }
}

/* ── eigene Bausteine der Heimnetz-Seite, nur mit den Variablen oben ── */
.raster2 > * + * { margin-top: 0; } .raster2 > * { min-width: 0; } .raster2 { display: grid; gap: 12px; }
.punkt { width: 9px; height: 9px; border-radius: 50%; flex: none; display: inline-block; background: #30d158; }
.punkt.amber { background: var(--amber); } .punkt.rot { background: var(--rot); } .punkt.grau { background: var(--ink2); opacity: .5; }
.kopf-titel { display: flex; align-items: center; gap: 10px; } .kopf-titel .punkt { width: 14px; height: 14px; box-shadow: 0 0 12px currentColor; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.befund { display: flex; gap: 10px; align-items: flex-start; padding: 10px 0; } .befund + .befund { border-top: 1px solid var(--gridc); }
.befund .punkt { margin-top: 5px; } .befund b { display: block; margin-bottom: 2px; } .befund p { margin: 0; color: var(--ink2); font-size: 13px; line-height: 1.45; }
.ereig { display: grid; grid-template-columns: 12px 92px 1fr; gap: 10px; align-items: baseline; padding: 7px 0; font-size: 13px; }
.ereig + .ereig { border-top: 1px solid var(--gridc); } .ereig .punkt { align-self: center; } .ereig time { color: var(--ink2); font-variant-numeric: tabular-nums; }
.leiste { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; }
.leiste .seg { flex: none; }
.wr { display: grid; grid-template-columns: 26px repeat(24, minmax(0, 1fr)); gap: 2px; font-size: 10px; color: var(--ink2); }
.wr i { aspect-ratio: 1.3; border-radius: 3px; display: block; cursor: default; }
.wr i.ohne { background: rgba(127,127,127,.12); }
.sig { display: inline-block; width: 70px; height: 8px; border-radius: 4px; background: rgba(127,127,127,.18); overflow: hidden; vertical-align: middle; }
.sig i { display: block; height: 100%; border-radius: 4px; }
.t tr.klick { cursor: pointer; }
.wr span { text-align: center; } .wr span.tag { text-align: left; align-self: center; }
/* WU-0004: Wochentag antippbar, Median-Zahl in der Kachel nur auf breitem Schirm, Tagesverlauf */
.wr button.tag { text-align: left; align-self: center; color: var(--blau); font-size: inherit; }
.wr button.tag.on { color: var(--ink); font-weight: 700; }
.wr i b { display: none; }
@container (min-width: 760px) { .wr i b { display: grid; place-items: center; height: 100%; font-size: 9.5px; font-weight: 600; font-style: normal; color: rgba(0,0,0,.72); font-variant-numeric: tabular-nums; } }
.tv { display: flex; flex-direction: column; gap: 8px; }
.tv svg { width: 100%; height: auto; display: block; touch-action: manipulation; }
/* Textfarbe statt Akzentblau: der Glas-Hintergrund ist oft selbst blau (WU-0004, Herbert 23.10.2026) */
.tv .band { fill: var(--ink); opacity: .26; } .tv .med { fill: none; stroke: var(--ink); stroke-width: 2.6; stroke-linejoin: round; }
.tv .med.luecke { stroke-width: 1.4; stroke-dasharray: 3 4; opacity: .55; } .tv .pkt { fill: var(--ink); }
.tv .glatt { fill: none; stroke: var(--amber); stroke-width: 2.6; stroke-linejoin: round; stroke-linecap: round; }
.tv .tarif { stroke: var(--ink2); stroke-dasharray: 4 4; stroke-width: 1; }
.tv .gitter { stroke: var(--gridc); stroke-width: 1; } .tv text { fill: var(--ink2); font-size: 11px; }
.tv .wahl { fill: rgba(127,127,127,.16); } .tv rect.h { fill: transparent; cursor: pointer; }
.tv .info { font-size: 13px; min-height: 20px; } .tv .info b { font-weight: 600; }
/* AN-0005: Popup zur Stundenkachel */
.wr i.kachel { cursor: pointer; } .wr i.wahl { outline: 2px solid var(--ink); outline-offset: 1px; }
.kpop { position: absolute; z-index: 15; width: 400px; max-width: calc(100% - 16px); box-sizing: border-box; padding: 10px 12px 8px;
  background: var(--sheet); border-radius: 16px; font-size: 12px; pointer-events: none; left: 8px; top: 8px; }
.kpop.fest { pointer-events: auto; }
.kpop .kp-kopf { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; } .kpop .kp-kopf b { font-size: 13px; }
.kpop .kp-werte { color: var(--ink2); margin: 3px 0 6px; line-height: 1.4; } .kpop .kp-werte b { color: var(--ink); font-weight: 600; }
.kpop table.t { font-size: 12px; } .kpop .t td { padding: 4px 6px 4px 0; } .kpop .t th { padding: 2px 6px 4px 0; }
.kpop .kp-liste { max-height: 220px; overflow-y: auto; } .kpop .zu-k { font-size: 14px; padding: 0 2px; color: var(--ink2); }
.legende i.l-med { background: var(--ink); height: 3px; } .legende i.l-glatt { background: var(--amber); height: 3px; } .legende i.l-band { background: var(--ink); opacity: .3; }
.legende i.l-luecke { background: none; border-top: 1px dashed var(--ink); height: 0; } .legende i.l-tarif { background: none; border-top: 1px dashed var(--ink2); height: 0; }
.skala { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--ink2); }
.skala i { width: 120px; height: 8px; border-radius: 4px; background: linear-gradient(90deg, var(--rot), var(--amber), var(--s3)); }
table.t { width: 100%; border-collapse: collapse; font-size: 13px; } .t th { text-align: left; font-weight: 500; color: var(--ink2); font-size: 11px; padding: 6px 8px 6px 0; }
.t td { padding: 7px 8px 7px 0; border-top: 1px solid var(--gridc); font-variant-numeric: tabular-nums; white-space: nowrap; } .t td.r, .t th.r { text-align: right; }
.t tr.belastet td { color: var(--ink2); }
.tab-scroll { overflow-x: auto; }
.streifen { display: flex; height: 14px; border-radius: 5px; overflow: hidden; background: rgba(127,127,127,.12); flex: 1; min-width: 120px; }
.streifen i { display: block; height: 100%; } .streifen i.an { background: var(--s3); } .streifen i.aus { background: transparent; } .streifen i.luecke { background: repeating-linear-gradient(45deg, transparent 0 3px, var(--gridc) 3px 6px); }
.geraet { display: grid; grid-template-columns: 32px minmax(0, 1.2fr) minmax(120px, 2fr) auto; gap: 12px; align-items: center; padding: 9px 0; cursor: pointer; }
.geraet + .geraet { border-top: 1px solid var(--gridc); } .geraet .n { display: flex; flex-direction: column; min-width: 0; } .geraet .n b { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.achse { display: flex; justify-content: space-between; font-size: 10px; color: var(--ink2); }
.pegel { display: flex; flex-direction: column; gap: 4px; } .pegel-bahn { position: relative; height: 10px; border-radius: 5px; background: linear-gradient(90deg, var(--rot) 0 30%, var(--amber) 30% 55%, var(--s3) 55%); opacity: .85; }
.pegel-bahn b { position: absolute; top: -4px; width: 4px; height: 18px; border-radius: 2px; background: var(--ink); box-shadow: 0 0 0 2px rgba(0,0,0,.35); transform: translateX(-2px); }
.mw { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; } .mw .glas-wert { font-size: 22px; }
svg.dia { width: 100%; height: auto; display: block; overflow: visible; } .dia text { fill: var(--axisc); font-size: 10px; } .dia .gitter { stroke: var(--gridc); }
.legende { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: var(--ink2); } .legende i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }
.neu { font-size: 10px; font-weight: 700; letter-spacing: .5px; padding: 1px 6px; border-radius: 6px; background: color-mix(in srgb, var(--blau) 25%, transparent); color: var(--blau); vertical-align: 2px; margin-left: 6px; }
.strecke { width: 100%; height: auto; display: block; }
.strecke .m-t { font-size: 12px; fill: var(--ink2); } .strecke .m-w { font-size: 15px; fill: var(--ink); font-weight: 600; }
.strecke .fluss { animation: fluss 1.6s linear infinite; } @keyframes fluss { to { stroke-dashoffset: -24; } }
.zellen { display: flex; flex-direction: column; }
.zelle { display: grid; grid-template-columns: 40px minmax(0, 1fr) auto auto; gap: 10px; align-items: center; padding: 8px 0; }
.zelle + .zelle { border-top: 1px solid var(--gridc); } .zelle .badge { text-align: center; }
.z-name { display: flex; flex-direction: column; min-width: 0; } .z-name b { font-weight: 600; font-size: 14px; }
.z-name .leise { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.z-wert { white-space: nowrap; min-width: 64px; display: flex; flex-direction: column; align-items: flex-end; font-variant-numeric: tabular-nums; } .z-wert small { opacity: .7; }
.stufen { display: inline-flex; align-items: flex-end; gap: 3px; height: 20px; } .stufen i { width: 5px; border-radius: 2px; background: rgba(127,127,127,.25); }
.klapp summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; }
.klapp summary::-webkit-details-marker { display: none; }
.klapp[open] > .hinweis { margin-top: 8px; }
.befund-k { padding: 12px 16px; } .befund-k b { flex: 1; font-weight: 600; font-size: 14px; line-height: 1.35; }
.befund-k .mehr { color: var(--ink2); font-size: 16px; } .befund-k[open] .mehr { color: var(--ink); }
.legende i.ring { border: 1px dashed var(--ink2); background: none; }
.legende i.osm-l { background: #8e8e93; border-radius: 0; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
.legende i.punkt-l { border-radius: 50%; } .legende i.genau-l { border: 1px dashed var(--ink2); background: none; border-radius: 50%; }
.hinweis { font-size: 12px; color: var(--ink2); line-height: 1.45; margin: 0; }
.aus-box .glas-wert, .aus-box .glas-kw { color: var(--ink2); }
.suche { flex: 1 1 160px; min-width: 0; }
/* Geräte kompakt nach Verbindung (AN-0001, Mockup netzwerk.html · Geräte kompakt, Variante D) */
.geraet.gk { grid-template-columns: 22px minmax(0, 1fr) 84px 10px; gap: 8px; padding: 5px 0; font-size: 13px; }
.gk .n { min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; } .gk .n small { color: var(--ink2); margin-left: 6px; font-size: 11px; }
.gk .streifen { height: 8px; min-width: 0; } .punkt.blau { background: var(--blau); }
.ggr summary { display: flex; justify-content: space-between; padding: 8px 0 4px; font-size: 12px; letter-spacing: .8px; text-transform: uppercase; color: var(--ink2); cursor: pointer; list-style: none; }
.ggr summary::-webkit-details-marker { display: none; }
.gk-achse { display: grid; grid-template-columns: minmax(0, 1fr) 84px 10px; gap: 8px; } .gk-achse .achse { font-size: 10px; }
select.ga-wahl { font: inherit; font-size: 13px; color: var(--ink); background: rgba(120,120,128,.18); border: 1px solid var(--panel-rand); border-radius: 10px; padding: 5px 8px; }
.ga-zeile { padding: 6px 0 !important; }
/* Einstellungen mit Reitern (AN-0002, Mockup netzwerk.html · Einstellungen gruppiert, Variante B) */
.e-reiter { margin: 4px 0 8px; } .e-reiter.seg button { font-size: 12px; padding: 7px 4px; }
.ek { border: 1px solid var(--gridc); border-radius: 18px; background: rgba(127,127,127,.06); overflow: hidden; }
.ek-inhalt { padding: 4px 14px 12px; display: flex; flex-direction: column; }
.ez { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 9px 0; min-height: 40px; font-size: 14px; }
.ez + .ez { border-top: 1px solid var(--gridc); } .ez > span:first-child small { display: block; color: var(--ink2); font-size: 11px; }
.ein { display: inline-flex; align-items: center; gap: 6px; background: rgba(127,127,127,.16); border: 1px solid var(--gridc); border-radius: 10px; padding: 5px 10px; font-size: 14px; }
.ein input { width: 64px; border: 0; background: none; color: var(--ink); font: inherit; text-align: right; padding: 0; }
.ein input[type=time], .ein input[type=date] { width: auto; text-align: left; color-scheme: dark; } .hell .ein input { color-scheme: light; }
.ein small { color: var(--ink2); } .sw[disabled] { opacity: .5; cursor: not-allowed; }
/* WU-0007: Einrichtung – was eingerichtet ist und was fehlt (Mockup netzwerk.html · Einrichtung) */
.amber-t { color: var(--amber); }
.e-punkt { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--amber); margin-left: 4px; vertical-align: 2px; }
.e-punkt.rot { background: var(--rot); }
.vs-stufe { font-size: 11px; letter-spacing: .8px; text-transform: uppercase; color: var(--ink2); padding: 10px 0 2px; display: flex; justify-content: space-between; }
.vs { display: grid; grid-template-columns: 22px minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 9px 0; min-height: 40px; font-size: 14px; }
.vs + .vs { border-top: 1px solid var(--gridc); }
.vs-st { width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center; font-size: 12px; font-weight: 700; }
.vs-st.ok { background: color-mix(in srgb, #30d158 22%, transparent); color: #30d158; }
.vs-st.fehlt { background: color-mix(in srgb, var(--amber) 22%, transparent); color: var(--amber); }
.vs-st.muss { background: color-mix(in srgb, var(--rot) 22%, transparent); color: var(--rot); }
.vs-st.aus { background: rgba(127,127,127,.18); color: var(--ink2); }
.vs > span:nth-child(2) { min-width: 0; } .vs small { display: block; color: var(--ink2); font-size: 11px; }
.vs-r { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; align-items: center; font-size: 13px; }
.vs-r .leise { font-size: 12px; }
.vs-r button { font-size: 13px; padding: 5px 10px; border-radius: 12px; background: rgba(120,120,128,.2); white-space: nowrap; }
.vs-r button.blau { background: color-mix(in srgb, var(--blau) 22%, transparent); }
.vs-kopf { border-radius: 12px; padding: 8px 12px; font-size: 13px; line-height: 1.4; background: rgba(127,127,127,.1); margin: 6px 0 2px; }
@container (max-width: 520px) { .vs { grid-template-columns: 22px minmax(0, 1fr); } .vs-r { grid-column: 2; justify-content: flex-start; } }
/* Melden (Tickets wie im Baustrommanager; Mockup netzwerk.html · Melden, 13.10.2026) */
.melden-knopf { position: absolute; right: 16px; bottom: 96px; z-index: 6; width: 40px; height: 40px; border-radius: 50% !important; display: grid; place-items: center; color: var(--ink2); opacity: .85; }
.melden-knopf:hover { opacity: 1; color: var(--ink); }
.melden-knopf.im-sheet { position: absolute; top: 10px; right: 48px; bottom: auto; width: 30px; height: 30px; z-index: 2; background: rgba(120,120,128,.18); }
.feld { display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: var(--ink2); }
.feld textarea { font: inherit; font-size: 14px; color: var(--ink); background: rgba(120,120,128,.14); border: 1px solid var(--panel-rand); border-radius: 14px; padding: 10px 12px; resize: vertical; }
.ml-kontext { font-size: 12px; display: flex; flex-direction: column; gap: 2px; }
/* WU-0006: öffentlich auf GitHub melden (Mockup githubMelden) */
.leise.mitte { text-align: center; }
.gh-vorschau { font: 12px/1.45 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre-wrap; overflow-wrap: anywhere; border: 1px solid var(--panel-rand); border-radius: 12px; padding: 10px 12px; max-height: 240px; overflow: auto; color: var(--ink); }
.gh-warn { border-radius: 12px; padding: 8px 12px; font-size: 12px; line-height: 1.45; background: color-mix(in srgb, var(--amber) 16%, transparent); color: var(--ink); }
.gh-warn b { color: var(--amber); }
.mb-box { border: 1px dashed var(--panel-rand); border-radius: 16px; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }
.mb-kopf { display: flex; justify-content: space-between; align-items: baseline; } .mb-knoepfe { display: flex; gap: 8px; flex-wrap: wrap; }
.mb-knoepfe button, .mb-knoepfe label { font-size: 13px; padding: 6px 12px; border-radius: 14px; background: rgba(120,120,128,.2); cursor: pointer; }
.mb-knoepfe input[type=file] { display: none; }
.mb-bilder, .ml-bilder { display: flex; gap: 8px; flex-wrap: wrap; }
.mb-bild { position: relative; width: 96px; display: flex; flex-direction: column; gap: 2px; } .mb-bild img { width: 96px; height: 62px; object-fit: cover; border-radius: 10px; }
.mb-bild .x { position: absolute; top: 3px; right: 3px; width: 22px; height: 22px; border-radius: 50%; background: rgba(0,0,0,.55); color: #fff; font-size: 12px; }
.mb-bild small { font-size: 10px; color: var(--ink2); }
.ml-bilder img, .ml-bilder i { width: 80px; height: 62px; object-fit: cover; border-radius: 10px; cursor: zoom-in; display: block; background: rgba(120,120,128,.2); }
.mb-gross { width: 100%; height: auto; border-radius: 12px; }
.sw { width: 46px; height: 28px; border-radius: 14px; background: rgba(120,120,128,.3); position: relative; flex: none; } .sw i { position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; border-radius: 50%; background: #fff; transition: left .2s; }
.sw.on { background: #30d158; } .sw.on i { left: 21px; }
.knopf.breit { width: 100%; padding: 12px; border-radius: 16px; font-size: 15px; font-weight: 600; } .knopf.amber { background: var(--amber); color: #1c1c1e; }
.knopf.leise-k { background: none; color: var(--ink2); font-weight: 500; }
.ml { padding: 10px 0; display: flex; flex-direction: column; gap: 6px; } .ml + .ml { border-top: 1px solid var(--gridc); } .ml.erledigt { opacity: .7; }
.ml-kopf { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; align-items: baseline; } .ml-text { font-size: 14px; line-height: 1.4; white-space: pre-wrap; }
.ml-notiz { font-size: 12px; color: var(--ink2); border-left: 2px solid var(--blau); padding-left: 8px; } .ml-k { display: flex; gap: 8px; flex-wrap: wrap; }
.toast { position: absolute; left: 50%; bottom: 100px; transform: translate(-50%, 20px); opacity: 0; z-index: 30; padding: 10px 16px; border-radius: 16px; font-size: 13px; transition: opacity .2s, transform .2s; pointer-events: none; max-width: 90%; text-align: center; }
.toast.an { opacity: 1; transform: translate(-50%, 0); }
@container (min-width: 700px) { .melden-knopf { bottom: 24px; right: 24px; } .toast { bottom: 40px; } }
@container (max-width: 520px) {
  .geraet { grid-template-columns: 32px minmax(0, 1fr) auto; } .geraet .streifen { grid-column: 2 / 4; }
  .geraet.gk { grid-template-columns: 22px minmax(0, 1fr) 70px 10px; } .geraet.gk .streifen { grid-column: auto; } .gk-achse { grid-template-columns: minmax(0, 1fr) 70px 10px; }
  .ereig { grid-template-columns: 12px 70px 1fr; }
  .wr { grid-template-columns: 22px repeat(24, minmax(0, 1fr)); gap: 1px; font-size: 9px; }
}
`;

export const stil = css`${unsafeCSS(GLAS)}`;
