/* WHERE IN TIME THE STROBE IS.
 *   node events.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--parkx -100 --parky -100] [--near 2]
 *
 * Every wall between two free cells is an auction wall, and it slides for
 * two reasons: the pair travelled, or the auction's QUESTION changed. The
 * question changes at EVENTS — a body becoming a hole (it leaves the bidding
 * and its shape is cut from the ground), a hole becoming free (it joins the
 * bidding and its shape is handed back to the ground), a wall melting into a
 * hole, a hole locking into a wall, a seed crossing the bidder gate. Each is
 * a step in the ground and the denominator at once, and every wall in the
 * pocket answers it. This lines the slides up against the events, frame by
 * frame, and asks how much of the top decile falls within NEAR frames of one.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0), FRAMES = +opt('--frames', 330);
const PX = +opt('--parkx', -100), PY = +opt('--parky', -100), NEAR = +opt('--near', 2);

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const h = require('crypto').createHash('sha1').update(src + DT + JIT + PX + PY).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'events-' + h + '.html');
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

const RUN = ({ FRAMES, PX, PY }) => {
  const X = window.__X, r = X.fn('root');
  X.setMouse(PX, PY);
  const L = [], marks = [];
  let n = 0;
  const step = () => {
    window.__advance(1); n++;
    const st = {}, x = {}, y = {};
    for (const bd of r.bodies) { if (bd.isSelf || bd.isVoid) continue; st[bd.id] = bd.wall ? 'W' : bd.hole ? 'H' : 'F'; x[bd.id] = bd.x; y[bd.id] = bd.y; }
    const w = {}, nb = {}; let S = 0;
    if (r.solvedSubs && r.solved) r.solvedSubs.forEach((sb, k) => {
      const id = sb.body.id; w[id] = r.solved.weights[k]; S += sb.claim;
      const c = r.solved.diagram.cells[k], seen = {};
      const scan = (pc) => { if (!pc || !pc.labs) return; for (const l of pc.labs) if (l >= 0 && r.solvedSubs[l]) seen[r.solvedSubs[l].body.id] = 1; };
      scan(c); if (c && c.pieces) for (const pc of c.pieces) scan(pc);
      nb[id] = Object.keys(seen).map(Number);
    });
    L.push({ f: n, st, x, y, w, nb, S, active: Object.keys(w).length });
  };
  for (let i = 0; i < 120; i++) step();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    marks.push({ f: n, scene: sc });
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    for (let i = 0; i < FRAMES; i++) step();
  }
  return { L, marks };
};

function metrics({ L, marks }) {
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  // events per frame
  const ev = [];   // { f, kinds: {WH, HF, FH, HW, in, out}, dS }
  for (let k = 1; k < L.length; k++) {
    const F = L[k], P = L[k - 1], kinds = { WH: 0, HF: 0, FH: 0, HW: 0, in: 0, out: 0 };
    for (const id in F.st) { const a = P.st[id], b = F.st[id]; if (!a || a === b) continue; const key = a + b; if (key in kinds) kinds[key]++; else kinds[key] = (kinds[key] || 0) + 1; }
    for (const id in F.w) if (!(id in P.w)) kinds.in++;
    for (const id in P.w) if (!(id in F.w)) kinds.out++;
    ev.push({ f: F.f, kinds, total: Object.values(kinds).reduce((s, v) => s + v, 0), dS: P.S > 0 ? Math.abs(F.S - P.S) / P.S : 0 });
  }
  const evAt = new Map(ev.map(e => [e.f, e]));
  const nearEvent = (f, kind) => { for (let d = -NEAR; d <= NEAR; d++) { const e = evAt.get(f + d); if (!e) continue; if (kind ? e.kinds[kind] > 0 : e.total > 0) return true; } return false; };
  // slides per pair-frame, transitions only
  const slides = [], perFrame = {};
  for (let k = 1; k < L.length; k++) {
    const F = L[k], P = L[k - 1], sc = sceneOf(F.f);
    if (sc === 'flock0' || sc === 'bento') continue;
    const done = {}; const pf = perFrame[F.f] = { dec: [], sc };
    for (const id in F.nb) for (const j of F.nb[id]) {
      if (j == id || !(id in P.w) || !(j in P.w) || !(j in F.w)) continue;
      const key = Math.min(id, j) + '-' + Math.max(id, j); if (done[key]) continue; done[key] = 1;
      const d = Math.hypot(F.x[id] - F.x[j], F.y[id] - F.y[j]); if (!(d > 1)) continue;
      const dec = Math.abs((F.w[id] - F.w[j]) - (P.w[id] - P.w[j])) / (2 * d);
      slides.push({ f: F.f, dec, sc }); pf.dec.push(dec);
    }
  }
  slides.sort((a, b) => a.dec - b.dec);
  const top = slides.slice(Math.floor(slides.length * 0.9));
  const share = (arr, kind) => arr.length ? arr.filter(s => nearEvent(s.f, kind)).length / arr.length : 0;
  const KINDS = [null, 'WH', 'HF', 'FH', 'HW', 'in', 'out'];
  const enrich = {};
  for (const kd of KINDS) { const a = share(slides, kd), t = share(top, kd); enrich[kd || 'any'] = { allShare: +a.toFixed(3), topShare: +t.toFixed(3), enrichment: a > 0 ? +(t / a).toFixed(2) : null }; }
  // frames: how many transition frames have an event, and the mean slide in event frames vs quiet frames
  let evFrames = 0, quietFrames = 0, evDec = 0, quietDec = 0, evMax = [], quietMax = [];
  for (const f in perFrame) { const pf = perFrame[f]; if (!pf.dec.length) continue; const m = pf.dec.reduce((s, v) => s + v, 0) / pf.dec.length, mx = Math.max(...pf.dec); if (nearEvent(+f, null)) { evFrames++; evDec += m; evMax.push(mx); } else { quietFrames++; quietDec += m; quietMax.push(mx); } }
  const p90 = (v) => { if (!v.length) return null; const s = v.slice().sort((a, b) => a - b); return +s[Math.floor(s.length * 0.9)].toFixed(1); };
  // spearman: per-frame mean slide vs event count, and vs dS
  const fr = Object.keys(perFrame).map(Number).filter(f => perFrame[f].dec.length);
  const rank = (v) => { const idx = v.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]); const r = new Array(v.length); idx.forEach(([, i], k) => r[i] = k); return r; };
  const sp = (a, b) => { const ra = rank(a), rb = rank(b), n = a.length; let s = 0; for (let i = 0; i < n; i++) { const d = ra[i] - rb[i]; s += d * d; } return +(1 - 6 * s / (n * (n * n - 1))).toFixed(3); };
  const meanDec = fr.map(f => perFrame[f].dec.reduce((s, v) => s + v, 0) / perFrame[f].dec.length);
  const evCount = fr.map(f => { let c = 0; for (let d = -NEAR; d <= NEAR; d++) { const e = evAt.get(f + d); if (e) c += e.total; } return c; });
  const dS = fr.map(f => { const e = evAt.get(f); return e ? e.dS : 0; });
  const byKind = {}; for (const e of ev) { if (sceneOf(e.f) === 'flock0' || sceneOf(e.f) === 'bento') continue; for (const k in e.kinds) byKind[k] = (byKind[k] || 0) + e.kinds[k]; }
  return {
    clock: { dtMs: +DT.toFixed(3), jitterMs: JIT }, pointer: [PX, PY], near: NEAR,
    transitionEvents: byKind, pairFrames: slides.length,
    // the test: what share of the top-decile slides sit within NEAR frames of an event, against all slides
    enrichment: enrich,
    frames: { withEvent: evFrames, quiet: quietFrames, meanSlideWithEvent: +(evFrames ? evDec / evFrames : 0).toFixed(2), meanSlideQuiet: +(quietFrames ? quietDec / quietFrames : 0).toFixed(2), p90MaxSlideWithEvent: p90(evMax), p90MaxSlideQuiet: p90(quietMax) },
    spearman: { slideVsEventCount: sp(meanDec, evCount), slideVsDeltaSumClaims: sp(meanDec, dS) },
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
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  console.log(JSON.stringify(m, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
