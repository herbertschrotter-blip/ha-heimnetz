// heimnetz-waechter: runs on a Shelly plug (Gen 2+) and power-cycles the device behind it when it hangs.
// Installed by the Heimnetz integration; the rules live in KVS "heimnetz-waechter" (JSON), the code is the same on every
// plug. Checks run on the plug itself, so it also works when Home Assistant hangs or the WLAN is gone with the router.
// It only switches its own relay, always with toggle_after (comes back on by itself). Commands from Heimnetz arrive in
// KVS "heimnetz-waechter-befehl" (protected like the plug). State: status() via Script.Eval (protected like the plug),
// also GET http://<plug>/script/<id>/status (codes, no text).
// Roles: "kette" = device in the internet chain (pos 0 = front, e.g. modem; last = router), "ha" = Home Assistant,
// "geraet" = any other device.
// Keep this file ASCII only and mJS-safe: no const, no arrow functions, no template strings, no let inside blocks.

let WV = 1;
let KEY = 'heimnetz-waechter';
let KEY_BEFEHL = 'heimnetz-waechter-befehl';
// check pages on the internet (fixed here: a KVS value holds at most 255 characters)
let ZIELE = ['http://connectivitycheck.gstatic.com/generate_204', 'http://detectportal.firefox.com/success.txt',
  'http://www.msftconnecttest.com/connecttest.txt'];

// rules in KVS use short keys and bare addresses; expand them to the names used below
function url(h) { if (!h) return null; return 'http://' + h; }
function ausklappen(k) {
  let z = [];
  if (k.i) z = ZIELE;
  return { v: k.v, an: k.an !== 0, pruef_s: k.p, stufe2_min: k.s2, aus_s: k.a, abstand_min: k.ab, pause_nach: k.pn,
    pause_h: k.ph, eigen: url(k.e), rolle: k.r, pos: k.po, anzahl: k.n, nach: url(k.na), vor: url(k.vo), partner: k.pa,
    netz: url(k.ne), ziele: z };
}

let cfg = null;
let st = {
  zustand: 'start',
  grund: '',
  stoer_seit: null,
  letzter: null,
  fehl: 0,
  pause_bis: null,
  eingriffe: 0,
  befehl_n: null,
  nach_eingriff: false,
  pruef: {},
  letzte: []
};
let laeuft = false;

function uptime() { return Shelly.getComponentStatus('sys').uptime; }
function unixzeit() { return Shelly.getComponentStatus('sys').unixtime; }

function merke(was, grund) {
  st.letzte.push({ t: unixzeit(), was: was, grund: grund || '' });
  if (st.letzte.length > 10) st.letzte.splice(0, 1);
}

// reachable = the host answers at all (401/404 count); only timeouts and connection errors do not
function erreichbar(url, fertig) {
  if (!url) { fertig(null); return; }
  Shelly.call('HTTP.GET', { url: url, timeout: 6 }, function (res, fehler) {
    fertig(fehler === 0 && res !== null && res !== undefined);
  });
}

function irgendeins(urls, i, fertig) {
  if (!urls || urls.length === 0) { fertig(null); return; }
  if (i >= urls.length) { fertig(false); return; }
  erreichbar(urls[i], function (ok) {
    if (ok) { fertig(true); } else { irgendeins(urls, i + 1, fertig); }
  });
}

function lies(fertig) {
  Shelly.call('KVS.GetMany', { match: KEY + '*' }, function (res, fehler) {
    let werte = {};
    let items = null;
    let i = 0;
    let k = null;
    if (fehler !== 0 || !res) { fertig(); return; }
    items = res.items;
    if (items && items.length !== undefined) {
      for (i = 0; i < items.length; i++) { werte[items[i].key] = items[i].value; }
    } else if (items) {
      for (k in items) { werte[k] = items[k].value; }
    }
    if (werte[KEY]) {
      try { cfg = ausklappen(JSON.parse(werte[KEY])); if (st.grund === 'regeln_kaputt') st.grund = ''; } catch (e) { cfg = null; st.grund = 'regeln_kaputt'; }
    }
    if (werte[KEY_BEFEHL]) {
      try { befehl(JSON.parse(werte[KEY_BEFEHL])); } catch (e2) { }
    }
    fertig();
  });
}

function befehl(b) {
  let neu = false;
  let min = 30;
  if (!b || b.n === st.befehl_n) return;
  neu = st.befehl_n !== null;
  st.befehl_n = b.n;
  if (!neu) return;
  if (b.x === 'ruhe') {
    if (b.min) min = b.min;
    st.pause_bis = uptime() + min * 60;
    st.stoer_seit = null;
    merke('ruhe', '' + min);
  }
  if (b.x === 'weiter') { st.pause_bis = null; st.fehl = 0; merke('weiter', ''); }
  if (b.x === 'sanft') { merke('sanft', b.grund || ''); }
}

// fault per role; null = all good, else { grund, faktor } (faktor 2 = give the device in front its turn first)
function fehlerbild(p) {
  let letzte = false;
  let faktor = 1;
  if (cfg.rolle === 'kette') {
    letzte = cfg.pos === cfg.anzahl - 1;
    if (letzte) {
      if (p.eigen === false) return { grund: 'router_weg', faktor: 1 };
      if (p.inet === false) {
        if (cfg.anzahl > 1 && p.vor === false) return null;
        if (cfg.anzahl > 1) faktor = 2;
        return { grund: 'inet_weg', faktor: faktor };
      }
      return null;
    }
    if (p.nach === false) return null;
    if (p.eigen === false) return { grund: 'modem_weg', faktor: 1 };
    if (p.inet === false) return { grund: 'inet_weg', faktor: 1 };
    return null;
  }
  if (p.netz === false) return null;
  if (p.eigen === false) return { grund: cfg.rolle + '_weg', faktor: 1 };
  return null;
}

function schalten(grund) {
  let aus = 30;
  if (cfg.aus_s) aus = cfg.aus_s;
  Shelly.call('Switch.Set', { id: 0, on: false, toggle_after: aus }, function (res, fehler) {
    let pn = 3;
    let ph = 6;
    if (fehler !== 0) { merke('schalten_fehler', grund); return; }
    st.eingriffe++;
    st.letzter = uptime();
    st.fehl++;
    st.zustand = 'schaltet';
    st.nach_eingriff = true;
    st.stoer_seit = null;
    merke('strom', grund);
    if (cfg.pause_nach) pn = cfg.pause_nach;
    if (cfg.pause_h) ph = cfg.pause_h;
    if (st.fehl >= pn) {
      st.pause_bis = uptime() + ph * 3600;
      merke('pause', '' + st.fehl);
    }
  });
}

function partnerFrei(fertig) {
  if (!cfg.partner) { fertig(true); return; }
  Shelly.call('HTTP.GET', { url: 'http://' + cfg.partner + '/rpc/Switch.GetStatus?id=0', timeout: 5 }, function (res, fehler) {
    let s = null;
    if (fehler !== 0 || !res || res.code !== 200) { fertig(true); return; }
    try { s = JSON.parse(res.body); } catch (e) { s = null; }
    fertig(!s || s.output !== false);
  });
}

function urteile(p) {
  let jetzt = uptime();
  let sw = Shelly.getComponentStatus('switch:0');
  let f = null;
  let warte = 0;
  let abstand = 60;
  st.pruef = p;
  if (sw && sw.output === false) { st.zustand = 'aus'; return; }
  if (st.pause_bis !== null && jetzt < st.pause_bis) { st.zustand = 'pause'; return; }
  if (st.pause_bis !== null) { st.pause_bis = null; st.fehl = 0; merke('pause_vorbei', ''); }
  f = fehlerbild(p);
  if (!f) {
    if (st.stoer_seit !== null || st.nach_eingriff) merke('ok', '');
    st.nach_eingriff = false;
    st.stoer_seit = null;
    st.fehl = 0;
    st.zustand = 'bereit';
    st.grund = '';
    return;
  }
  if (st.stoer_seit === null) st.stoer_seit = jetzt;
  st.zustand = 'stoerung';
  st.grund = f.grund;
  warte = 12;
  if (cfg.stufe2_min) warte = cfg.stufe2_min;
  warte = warte * 60 * f.faktor;
  if (cfg.abstand_min) abstand = cfg.abstand_min;
  if (jetzt - st.stoer_seit < warte) return;
  if (st.letzter !== null && jetzt - st.letzter < abstand * 60) return;
  partnerFrei(function (frei) { if (frei) schalten(f.grund); });
}

function pruefe() {
  let p = {};
  erreichbar(cfg.eigen, function (a) {
    p.eigen = a;
    erreichbar(cfg.nach || cfg.netz, function (b) {
      if (cfg.nach) { p.nach = b; } else { p.netz = b; }
      erreichbar(cfg.vor, function (c) {
        p.vor = c;
        irgendeins(cfg.ziele, 0, function (d) {
          p.inet = d;
          urteile(p);
          laeuft = false;
        });
      });
    });
  });
}

function runde() {
  if (laeuft) return;
  laeuft = true;
  lies(function () {
    if (!cfg || cfg.v !== 1) {
      st.zustand = 'fehler';
      if (!cfg && st.grund !== 'regeln_kaputt') st.grund = 'keine_regeln';
      laeuft = false;
      return;
    }
    if (cfg.an === false) { st.zustand = 'aus_regel'; laeuft = false; return; }
    pruefe();
  });
}

function status() {
  let jetzt = uptime();
  let o = { wv: WV, zustand: st.zustand, grund: st.grund, rolle: null, stoer_s: null, pause_s: null,
    seit_eingriff_s: null, eingriffe: st.eingriffe, fehl: st.fehl, pruef: st.pruef, letzte: st.letzte, jetzt: unixzeit() };
  if (cfg) o.rolle = cfg.rolle;
  if (st.stoer_seit !== null) o.stoer_s = jetzt - st.stoer_seit;
  if (st.pause_bis !== null) o.pause_s = Math.max(0, st.pause_bis - jetzt);
  if (st.letzter !== null) o.seit_eingriff_s = jetzt - st.letzter;
  return JSON.stringify(o);
}

HTTPServer.registerEndpoint('status', function (req, res) {
  res.code = 200;
  res.headers = [['Content-Type', 'application/json']];
  res.body = status();
  res.send();
});

function takt() {
  let s = 60;
  if (cfg && cfg.pruef_s) s = cfg.pruef_s;
  return s;
}

let zaehler = 0;
merke('start', '');
Timer.set(15000, false, runde);
// one 30 s tick; a round runs every pruef_s (30, 60 or 120)
Timer.set(30000, true, function () {
  zaehler++;
  if ((zaehler * 30) % takt() === 0) runde();
});
