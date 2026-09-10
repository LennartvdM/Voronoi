/* Deterministic scorecard for a hive.html build.
 *   node score.js <path-to-hive.html> [out.json] [--frames N] [--dump frames.json]
 * A fixed-step clock (1/60 s per frame, driven from the probe) replaces
 * requestAnimationFrame and performance.now, so two runs of the same file give
 * the same numbers frame for frame, and two builds differ only by their code.
 * Scenario: pointer parked at (700,400); settle 120 frames in Flock; then
 * Bento, Hero, Sidebar, Frame, Flock, each held N frames (default 330).
 * Everything is read off the frame's PICTURE (the leaves actually drawn).
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || '/home/user/Voronoi/hive.html');
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const FRAMES = +opt('--frames', 330), DUMP = opt('--dump', null);
// where the pointer sits for the whole run. It matters more than it looks:
// parked inside a cell that expands, the hover boost crushes that cell's
// neighbours, and their recovery when the boost is handed back at a scene
// change is counted here as their own jump. Move it to ask what the page
// does with nobody leaning on it.
const PX = +opt('--parkx', 700), PY = +opt('--parky', 400);
// the clock, as in flicker.js: --dt <ms> fixed step (default 1000/60),
// --jitter <ms> a deterministic +-jitter on every step. The owner watches at
// real, uneven frame times; a number quoted at 60 fps is a number at 60 fps.
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0);
const NAMES = ['root', 'buildPicture', 'ringArea', 'picture', 'rasterCheck', 'config', 'W', 'H'];

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({${NAMES.map(n => `${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`).join(', ')}})[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'score-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
  fs.writeFileSync(dst, s.slice(0, i) + exp + s.slice(i));
  return dst;
}

const CLOCK = `(() => {
  let t = 0, seed = 12345; const q = []; const realNow = performance.now.bind(performance);
  const DT = ${DT}, JIT = ${JIT};
  const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
  window.__realNow = realNow;
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => {};
  performance.now = () => t;
  window.__advance = (n) => { for (let i = 0; i < n; i++) { t += DT + (JIT ? (2 * rnd() - 1) * JIT : 0); const cbs = q.splice(0); for (const cb of cbs) cb(t); } };
})();`;

const RUN = ({ FRAMES, PX, PY }) => {
  const X = window.__X, r = X.fn('root'), ra = X.fn('ringArea'), rc = X.fn('rasterCheck');
  X.setMouse(PX, PY);
  const frames = [], marks = [];
  let n = 0;
  const step = () => {
    const t0 = window.__realNow();
    window.__advance(1);
    const ms = window.__realNow() - t0;
    const pic = X.fn('picture'), W = X.fn('W'), H = X.fn('H');
    const rec = { f: n++, ms: +ms.toFixed(2), a: {}, st: {} };
    // a loop's area is the part of it ON THE PAGE: a cell that spills past the
    // edge has not grown by what it spilled. Sutherland-Hodgman against the
    // page box; exact for area whatever the loop's shape.
    const clipBox = (pts) => {
      let poly = pts;
      const edges = [[p => p[0] >= 0, (a, b) => (0 - a[0]) / (b[0] - a[0])], [p => p[0] <= W, (a, b) => (W - a[0]) / (b[0] - a[0])], [p => p[1] >= 0, (a, b) => (0 - a[1]) / (b[1] - a[1])], [p => p[1] <= H, (a, b) => (H - a[1]) / (b[1] - a[1])]];
      for (const [keep, ix] of edges) {
        const out = [];
        for (let k = 0; k < poly.length; k++) { const a = poly[k], b = poly[(k + 1) % poly.length], ka = keep(a), kb = keep(b); if (ka) out.push(a); if (ka !== kb) { const t = ix(a, b); out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]); } }
        poly = out; if (poly.length < 3) return [];
      }
      return poly;
    };
    if (pic) for (const l of pic.leaves) { const rb = l.path[0].body; let a = 0; for (const lp of l.loops) { const c = clipBox(lp); if (c.length >= 3) a += (lp.hole ? -1 : 1) * Math.abs(ra(c)); } rec.a[rb.id] = (rec.a[rb.id] || 0) + a; }
    for (const bd of r.bodies) { if (bd.isSelf) continue; rec.st[bd.id] = { cr: +bd.crystal.toFixed(4), w: !!bd.wall, h: !!bd.hole, v: !!bd.isVoid, lv: !!bd.leaving, ex: bd.holeExtra ? Math.round(bd.holeExtra.reduce((s, pc) => s + Math.abs(ra(pc)), 0)) : 0, core: bd.holeCore && bd.holeCore.core ? Math.round(Math.abs(ra(bd.holeCore.core))) : 0 }; }
    if (pic && n % 6 === 0) { const rr = rc(pic.leaves.flatMap(l => l.loops.map(pts => ({ pts, hole: !!pts.hole }))), W, H); rec.gap = rr.gap; rec.over = rr.over; }
    rec.err = r.solved ? +r.solved.maxRelErr.toExponential(2) : 0;
    frames.push(rec);
  };
  for (let i = 0; i < 120; i++) step();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    marks.push({ f: n, scene: sc });
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    for (let i = 0; i < FRAMES; i++) step();
  }
  return { frames, marks };
};

function metrics({ frames, marks }) {
  const st = (s) => s.w ? 'W' : s.h ? 'H' : 'F';
  const J = [], V = [];
  const vanish = [];
  let gapMax = 0, overMax = 0, errMax = 0;
  const ms = frames.map(f => f.ms).sort((a, b) => a - b);
  const pct = (arr, p) => arr.length ? arr[Math.min(arr.length - 1, Math.floor(p * (arr.length - 1)))] : 0;
  for (let k = 1; k < frames.length; k++) {
    const F = frames[k], P = frames[k - 1];
    if (F.gap !== undefined) { gapMax = Math.max(gapMax, F.gap); overMax = Math.max(overMax, F.over); }
    errMax = Math.max(errMax, F.err || 0);
    let scene = 'flock0', sf = 0; for (const m of marks) if (F.f >= m.f) { scene = m.scene; sf = F.f - m.f; }
    for (const id in F.st) {
      const s = F.st[id], p = P.st[id]; if (!p) continue;
      const a = F.a[id] || 0, q = P.a[id] || 0;
      if (!s.v && !s.lv && a < 1 && q >= 1) vanish.push({ f: F.f, id: +id, scene, sf });
      const d = Math.abs(a - q);
      if (d > 4000 && d / Math.max(a, q) > 0.12) {
        const j = { f: F.f, scene, sf, id: +id, rel: +(d / Math.max(a, q)).toFixed(2), dir: a > q ? '+' : '-', from: Math.round(q), to: Math.round(a), k: st(p) + '>' + st(s), cr: [p.cr, s.cr], core: [p.core, s.core], ex: [p.ex, s.ex] };
        (s.v ? V : J).push(j);
      }
    }
  }
  // kinds
  const kind = (j) => j.k === 'F>H' || (j.k === 'H>H' && j.cr[1] < 0.1 && j.cr[1] >= j.cr[0]) ? 'opening'
    : j.k === 'H>F' || j.k === 'H>W' || j.k === 'W>H' ? 'switch'
    : j.k === 'H>H' && Math.abs(j.ex[1] - j.ex[0]) > 3000 ? 'adoption'
    : j.k === 'H>H' ? 'hole' : j.k === 'F>F' ? 'free' : j.k;
  const kinds = {}; for (const j of J) kinds[kind(j)] = (kinds[kind(j)] || 0) + 1;
  const byScene = {}; for (const j of J) byScene[j.scene] = (byScene[j.scene] || 0) + 1;
  const phase = { start: 0, mid: 0, end: 0 }; for (const j of J) phase[j.sf < 48 ? 'start' : j.sf < 132 ? 'mid' : 'end']++;
  // reversals: same body, opposite direction, within 5 frames
  let rev = 0; const byId = {}; for (const j of J) (byId[j.id] = byId[j.id] || []).push(j);
  for (const id in byId) { const a = byId[id]; for (let i = 1; i < a.length; i++) if (a[i].f - a[i - 1].f <= 5 && a[i].dir !== a[i - 1].dir) rev++; }
  let shock = 0; for (const j of J) shock += Math.abs(j.to - j.from);
  const rels = J.map(j => j.rel).sort((a, b) => a - b);
  // settled at the end of every scene?
  // settled at the end of every scene: nothing still morphing (a liquid scene
  // settles into free cells, a laid-out one into walls)
  const settled = marks.map((m, i) => { const end = (marks[i + 1] ? marks[i + 1].f : frames.length) - 1; const F = frames[end]; let ok = true; for (const id in F.st) { const s = F.st[id]; if (!s.v && !s.lv && (s.h || (s.cr > 0 && s.cr < 1))) ok = false; } return ok; });
  return {
    frames: frames.length,
    jumps: J.length, reversals: rev, shockPx2: Math.round(shock), relP50: pct(rels, 0.5), relP90: pct(rels, 0.9), relMax: pct(rels, 1),
    kinds, phase, byScene,
    voidJumps: V.length,
    vanish: vanish.length,
    gapMax, overMax, errMax,
    settledScenes: settled.filter(Boolean).length + '/' + settled.length,
    msP50: pct(ms, 0.5), msP95: pct(ms, 0.95), msMax: pct(ms, 1),
    worst: J.slice().sort((a, b) => b.rel - a.rel).slice(0, 12),
  };
}

(async () => {
  const dst = instrument(SRC);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.addInitScript(CLOCK);
  const errs = []; p.on('pageerror', e => errs.push(String(e.message || e)));
  await p.goto('file://' + dst);
  await p.waitForTimeout(300);
  const data = await p.evaluate(RUN, { FRAMES, PX, PY });
  await b.close();
  if (DUMP) fs.writeFileSync(DUMP, JSON.stringify(data));
  const m = metrics(data); m.clock = { dtMs: DT, jitterMs: JIT }; m.pageErrors = errs.length; if (errs.length) m.pageErrorSample = errs.slice(0, 3);
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  const { worst, ...head } = m;
  console.log(JSON.stringify(head));
  for (const w of worst) console.log('  ' + JSON.stringify(w));
})().catch(e => { console.error(e); process.exit(1); });
