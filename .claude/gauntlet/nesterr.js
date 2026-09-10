/* WHAT THE FIELDS INSIDE A CELL ARE PAYING.
 *   node nesterr.js <hive.html> [out.json] [--dt 30] [--jitter 12]
 *
 * A cell of this page can hold a hive of its own, and that hive runs its own
 * auction on its own ground. Nothing else in this harness looks at one:
 * score.js reads the root diagram's areas, wall.js reads the root main
 * auction's pairs, and strobe.js counts a nested leaf's reach but not what it
 * was promised. So a change can starve every nested auction on the page and
 * score clean everywhere — which has already happened once: a build took the
 * worst nested residual from 0.4% to 6,180% with no instrument noticing.
 *
 * This walks the whole tree every frame and asks each hive the one question
 * the auction exists to answer: did every bidder get the area its claim was
 * promised. `relErr` is the auction's own residual, `missP99` is the share by
 * which a body's painted cell differs from what it was asked for.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0), FRAMES = +opt('--frames', 330);

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const h = require('crypto').createHash('sha1').update(src + DT + JIT).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'nesterr-' + h + '.html');
  fs.writeFileSync(dst, s.slice(0, i) + `\n window.__X = { fn: (n) => ({ root, ringArea })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n` + s.slice(i));
  return dst;
}

const CLOCK = `(() => {
  let t = 0, seed = 12345; const q = []; const DT = ${DT}, JIT = ${JIT};
  const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => {};
  performance.now = () => t;
  window.__advance = (n) => { for (let i = 0; i < n; i++) { t += DT + (JIT ? (2 * rnd() - 1) * JIT : 0); const cbs = q.splice(0); for (const cb of cbs) cb(t); } };
})();`;

const RUN = (FRAMES) => {
  const X = window.__X, r = X.fn('root'), ra = X.fn('ringArea');
  X.setMouse(700, 400);
  const L = [], marks = [];
  let n = 0;
  const walk = (h, depth, out) => {
    if (!h || h.dormant) return;
    if (h.solved && h.solvedSubs && h.solvedSubs.length) {
      let gA = 0; for (const pc of (h.ground || [])) gA += Math.abs(ra(pc));
      if (!gA) gA = h.W * h.H;
      let S = 0; for (const s of h.solvedSubs) S += s.claim;
      let worst = 0; const miss = [];
      for (let k = 0; k < h.solvedSubs.length; k++) {
        const tgt = h.solvedSubs[k].claim * gA / S;
        if (!(tgt > 1)) continue;
        const m = Math.abs(h.solved.diagram.areas[k] - tgt) / tgt;
        miss.push(m); if (m > worst) worst = m;
      }
      out.push({ depth, n: h.solvedSubs.length, relErr: h.solved.maxRelErr, conv: !!h.solved.converged, iters: h.solved.iterations | 0, worstMiss: worst, miss });
    }
    for (const b of h.bodies) if (b.hive) walk(b.hive, depth + 1, out);
  };
  const step = () => {
    window.__advance(1); n++;
    const out = []; walk(r, 0, out);
    L.push({ f: n, h: out });
  };
  for (let i = 0; i < 120; i++) step();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    marks.push({ f: n, scene: sc });
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    for (let i = 0; i < FRAMES; i++) step();
  }
  return { L, marks };
};

const stat = (v) => {
  if (!v.length) return { n: 0 };
  const s = v.slice().sort((a, b) => a - b), q = (p) => +s[Math.min(s.length - 1, Math.floor(s.length * p))].toPrecision(3);
  return { n: v.length, med: q(0.5), p90: q(0.9), p99: q(0.99), max: q(1) };
};

(async () => {
  const dst = instrument(SRC);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.addInitScript(CLOCK);
  const errs = []; p.on('pageerror', e => errs.push(String(e.message || e)));
  await p.goto('file://' + dst);
  await p.waitForTimeout(300);
  const { L, marks } = await p.evaluate(RUN, FRAMES);
  await b.close();
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  const byDepth = {}, byScene = {}, worst = [];
  for (const F of L) {
    const sc = sceneOf(F.f);
    for (const h of F.h) {
      const D = byDepth[h.depth] = byDepth[h.depth] || { err: [], miss: [], unconv: 0, hiveFrames: 0 };
      D.hiveFrames++; D.err.push(h.relErr); if (!h.conv) D.unconv++;
      for (const m of h.miss) D.miss.push(m);
      if (h.depth > 0) {
        const S = byScene[sc] = byScene[sc] || { err: [], unconv: 0, hiveFrames: 0 };
        S.hiveFrames++; S.err.push(h.relErr); if (!h.conv) S.unconv++;
        if (h.relErr > 0.05) worst.push({ f: F.f, scene: sc, depth: h.depth, n: h.n, relErr: +h.relErr.toPrecision(3), worstMiss: +h.worstMiss.toPrecision(3), conv: h.conv });
      }
    }
  }
  const m = {
    file: SRC, clock: { dtMs: +DT.toFixed(3), jitterMs: JIT }, pageErrors: errs.length,
    byDepth: Object.fromEntries(Object.entries(byDepth).map(([d, v]) => [d, {
      hiveFrames: v.hiveFrames, unconverged: v.unconv,
      relErr: stat(v.err), bodyMiss: stat(v.miss),
    }])),
    nestedByScene: Object.fromEntries(Object.entries(byScene).map(([s, v]) => [s, { hiveFrames: v.hiveFrames, unconverged: v.unconv, relErrP99: stat(v.err).p99, relErrMax: stat(v.err).max }])),
    nestedOver5pct: worst.length,
    worst: worst.sort((a, b) => b.relErr - a.relErr).slice(0, 10),
  };
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  console.log(JSON.stringify(m, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
