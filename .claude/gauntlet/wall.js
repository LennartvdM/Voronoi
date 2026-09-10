/* THE WALL'S OWN SPEEDOMETER.
 *   node wall.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames 330]
 *
 * Every other instrument here measures a CELL: its area (score.js), its shape
 * undone (flicker.js), its painted mask against the last frame (strobe.js).
 * This one measures the WALL BETWEEN TWO CELLS, in pixels, and splits its
 * motion into the two things that can move it.
 *
 * The wall between i and j is where |x-si|² - wi = |x-sj|² - wj. It is
 * perpendicular to the line joining the seeds and it sits offset from their
 * midpoint by (wi - wj) / (2 d), d the seed separation. So the wall moves for
 * exactly two reasons:
 *
 *   TRAVEL. The seeds moved, and the wall came with them. This is honest
 *     motion: the cells went somewhere and their shared edge followed.
 *   DECISION. Nobody moved and the wall slid anyway, because the auction
 *     handed back a different weight difference than it did last frame:
 *     Δ(wi - wj) / (2 d) pixels of slide from a standstill.
 *
 * The second is the strobe. A page where DECISION is larger than TRAVEL is a
 * page whose cells are not travelling anywhere — they are being re-decided in
 * place, every frame, and no still frame will show it.
 *
 * Also reported: REACH. Because the offset divides by d, a pair of seeds that
 * drift close together can put their shared wall arbitrarily far away —
 * |wi - wj| / (2 d) can exceed the page. That is the wedge stretched across
 * the screen. `reachPx` is that offset in pixels; `reachOut` counts the
 * frames where a wall sits further outside its own pair than the page is wide.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0);
// where the pointer sits. Off the canvas (-100,-100) it hovers nothing, and the
// run measures the transitions alone.
const PX = +opt('--parkx', 700), PY = +opt('--parky', 400), FRAMES = +opt('--frames', 330);

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const h = require('crypto').createHash('sha1').update(src + DT + JIT).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'wall-' + h + '.html');
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
    const w = {}, x = {}, y = {}, nb = {};
    if (r.solvedSubs && r.solved) r.solvedSubs.forEach((sb, k) => {
      const id = sb.body.id;
      w[id] = r.solved.weights[k]; x[id] = sb.x; y[id] = sb.y;
      // who this cell actually shares an edge with, from the diagram's own labels
      const c = r.solved.diagram.cells[k], seen = {};
      const scan = (pc) => { if (!pc || !pc.labs) return; for (const l of pc.labs) if (l >= 0 && r.solvedSubs[l]) seen[r.solvedSubs[l].body.id] = 1; };
      scan(c); if (c && c.pieces) for (const pc of c.pieces) scan(pc);
      nb[id] = Object.keys(seen).map(Number);
    });
    L.push({ f: n, w, x, y, nb });
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
  if (!v.length) return { n: 0, mean: 0, med: 0, p90: 0, p99: 0, max: 0 };
  const s = v.slice().sort((a, b) => a - b), q = (p) => +s[Math.min(s.length - 1, Math.floor(s.length * p))].toFixed(1);
  return { n: v.length, mean: +(v.reduce((a, b) => a + b, 0) / v.length).toFixed(2), med: q(0.5), p90: q(0.9), p99: q(0.99), max: q(1) };
};

function metrics({ L, marks }, W) {
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  const all = { dec: [], trav: [], reach: [] }, scenes = {}, worst = [], trackByScene = {};
  let slid = 0, reachOut = 0;
  for (let k = 1; k < L.length; k++) {
    const F = L[k], P = L[k - 1], sc = sceneOf(F.f);
    const S = scenes[sc] = scenes[sc] || { dec: [], trav: [], reach: [], slid: 0, reachOut: 0, pairs: new Set() };
    const track = trackByScene[sc] = trackByScene[sc] || {};
    const done = {};
    for (const id in F.nb) {
      if (!(id in P.w)) continue;
      for (const j of F.nb[id]) {
        if (j == id || !(j in P.w) || !(j in F.w)) continue;
        const key = Math.min(id, j) + '-' + Math.max(id, j);
        if (done[key]) continue; done[key] = 1;
        const d = Math.hypot(F.x[id] - F.x[j], F.y[id] - F.y[j]);
        if (!(d > 1)) continue;
        const lo = Math.min(+id, +j), hi = Math.max(+id, +j), sgn = (+id === lo) ? 1 : -1;
        const oF = sgn * (F.w[id] - F.w[j]) / (2 * d), oP = sgn * (P.w[id] - P.w[j]) / (2 * Math.max(1, Math.hypot(P.x[id] - P.x[j], P.y[id] - P.y[j])));
        (track[key] = track[key] || []).push(oF - oP);
        const dec = Math.abs((F.w[id] - F.w[j]) - (P.w[id] - P.w[j])) / (2 * d);
        const trav = 0.5 * (Math.hypot(F.x[id] - P.x[id], F.y[id] - P.y[id]) + Math.hypot(F.x[j] - P.x[j], F.y[j] - P.y[j]));
        const reach = Math.abs(F.w[id] - F.w[j]) / (2 * d);
        all.dec.push(dec); all.trav.push(trav); all.reach.push(reach);
        S.dec.push(dec); S.trav.push(trav); S.reach.push(reach); S.pairs.add(key);
        if (dec > 40) { slid++; S.slid++; if (worst.length < 4000) worst.push({ f: F.f, scene: sc, pair: key, decidedPx: Math.round(dec), travelPx: +trav.toFixed(1), sepPx: Math.round(d) }); }
        if (reach > W) { reachOut++; S.reachOut++; }
      }
    }
  }
  // IS A WALL CATCHING UP, OR CHANGING ITS MIND? Over a short window a wall
  // that is travelling to somewhere sums its steps: |sum| is close to sum|.|.
  // A wall being re-decided in place goes back and forth and |sum| collapses.
  // `carry` is the share of a wall's motion that got it anywhere; 1 is pure
  // travel, 0 is pure argument. Windowed at 8 frames, which is a fifth of a
  // second at the owner's clock: long enough to contain a real slide, short
  // enough that an honest journey has not turned around inside it.
  const WIN = 8;
  const carryAll = [];
  const carryScene = {};
  for (const sc in trackByScene) {
    const cs = carryScene[sc] = [];
    for (const key in trackByScene[sc]) {
      const v = trackByScene[sc][key];
      for (let a = 0; a + WIN <= v.length; a += WIN) {
        let sum = 0, abs = 0;
        for (let b = a; b < a + WIN; b++) { sum += v[b]; abs += Math.abs(v[b]); }
        if (abs > 4) { const c = Math.abs(sum) / abs; carryAll.push(c); cs.push(c); }
      }
    }
  }
  const mean = (v) => v.length ? +(v.reduce((a, b) => a + b, 0) / v.length).toFixed(3) : null;
  const decS = stat(all.dec), travS = stat(all.trav);
  return {
    clock: { dtMs: +DT.toFixed(3), jitterMs: JIT }, pointer: [PX, PY], pairFrames: decS.n,
    // the headline: the ratio of decision to travel. 1.0 means a page whose
    // walls move as much from being re-decided as from anything moving.
    strobeRatio: +(decS.mean / Math.max(1e-9, travS.mean)).toFixed(2),
    decidedPx: decS, travelPx: travS, reachPx: stat(all.reach),
    slidOver40: slid, reachOffPage: reachOut,
    // 1 = every pixel of wall motion got the wall somewhere; 0 = the wall
    // argued with itself and ended where it started
    carry: mean(carryAll), carryWindows: carryAll.length,
    scenes: Object.fromEntries(Object.entries(scenes).map(([k, v]) => [k, {
      strobeRatio: +(stat(v.dec).mean / Math.max(1e-9, stat(v.trav).mean)).toFixed(2),
      decidedMean: stat(v.dec).mean, decidedP99: stat(v.dec).p99, decidedMax: stat(v.dec).max,
      travelMean: stat(v.trav).mean, slidOver40: v.slid, reachOffPage: v.reachOut,
      // THE SAMPLE. wall.js sees only pairs among the root main auction's live
      // bidders. A change that pushes cells into the hole or shadow path
      // lowers decidedPx by deleting pair-frames, not motion, so every mean
      // above is only comparable against a run with a comparable sample.
      pairFrames: stat(v.dec).n, distinctPairs: v.pairs.size,
      carry: mean(carryScene[k] || []),
    }])),
    worstSlides: worst.sort((a, b) => b.decidedPx - a.decidedPx).slice(0, 12),
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
  const m = metrics(data, 1440); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  const { worstSlides, ...head } = m;
  console.log(JSON.stringify(head, null, 1));
  console.log('worst slides (a wall that moved with nobody moving it):');
  for (const w of worstSlides) console.log('  ' + JSON.stringify(w));
})().catch(e => { console.error(e); process.exit(1); });
