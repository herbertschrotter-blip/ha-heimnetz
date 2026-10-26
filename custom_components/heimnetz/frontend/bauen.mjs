// Baut die Seite „Heimnetz“: src/heimnetz-panel.js → heimnetz-panel.js (wie ha-baustelle).
// Aufruf: node custom_components/heimnetz/frontend/bauen.mjs [--pruefen]
//   ohne Schalter: schreibt heimnetz-panel.js neu
//   --pruefen:     baut im Speicher und vergleicht mit der eingecheckten Datei (schreibt nichts)
// Die Version kommt aus manifest.json und wird über esbuild `define` eingesetzt.
import { build } from 'esbuild';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const hier = dirname(fileURLToPath(import.meta.url));
const ziel = join(hier, 'heimnetz-panel.js');
const pruefen = process.argv.includes('--pruefen');
const { version } = JSON.parse(readFileSync(join(hier, '..', 'manifest.json'), 'utf8'));

const ergebnis = await build({
  entryPoints: [join(hier, 'src', 'heimnetz-panel.js')],
  bundle: true,
  format: 'esm',
  platform: 'browser',
  target: ['es2022'],
  minify: false, // lesbar für die Fehlersuche
  legalComments: 'inline',
  charset: 'utf8',
  write: false,
  absWorkingDir: hier,
  define: { __HEIMNETZ_VERSION__: JSON.stringify(version) },
  banner: { js: '// Seite „Heimnetz“ – gebaut mit esbuild aus custom_components/heimnetz/frontend/src (nicht von Hand ändern)' },
  logLevel: 'warning',
});
const neu = ergebnis.outputFiles[0].text;

if (pruefen) {
  let alt = '';
  try { alt = readFileSync(ziel, 'utf8'); } catch { /* fehlt */ }
  if (alt !== neu) {
    console.error('heimnetz-panel.js passt nicht zur Quelle – node custom_components/heimnetz/frontend/bauen.mjs ausführen');
    process.exit(1);
  }
  console.log(`heimnetz-panel.js aktuell (Version ${version}, ${Math.round(neu.length / 1024)} KB)`);
} else {
  writeFileSync(ziel, neu);
  console.log(`heimnetz-panel.js gebaut (Version ${version}, ${Math.round(neu.length / 1024)} KB)`);
}
