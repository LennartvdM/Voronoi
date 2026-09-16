/* THE CORNER BUDGET: a cell should be organic, not rigid, and not flubber.
 *   node corners.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N] [--parkx X --parky Y]
 *
 * shape.js names what a cell IS (rectangle / notched / voronoi / cut /
 * fractured). That taxonomy cannot tell a page of floating rectangles from a
 * page of living cells, because both score clean. This probe counts CORNERS,
 * which is the thing the owner can actually see:
 *
 *   3..9 corners   the organic middle: a Voronoi cell with a handful of
 *                  neighbours. This is the band the page should live in
 *                  while anything is moving.
 *   4 corners      a rectangle. Legitimate as a DESTINATION — a template
 *                  that asks for a bento slot should land one — but a high
 *                  share while bodies are in transit means the cells are not
 *                  alive, they are sliding rectangles.
 *   >=10 corners   flubber: a cell with so many corners it reads as a blob
 *                  or a tooth-ridden membrane.
 *
 * Reported over all frames, over transition frames only (the cold settle
 * excluded) and over SEATED frames only (the last few frames of each settled
 * scene), because the three answer different questions: transit wants the
 * middle band, seated wants whatever the template asked for.
 *
 * Also measured, on the same pass: the RESTING INSET, the distance from each
 * window edge to the nearest content ink once a scene has settled. Positive
 * is a gutter — the neat 100% page. Negative means ink sits permanently off
 * the crop, which is a bleed being spent at rest instead of held in reserve
 * for a gridlock.
 *
 * Outlines are read raw (before the garment rounds them), with near-duplicate
 * and collinear vertices removed, so a corner is a real change of direction.
 * Nested members are not read.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0);
const FRAMES = +opt('--frames', 220);
const PX = +opt('--parkx', -1000), PY = +opt('--parky', -1000);
const SEATED = 5;   // frames at the end of a scene counted as settled
const SLIVER = Math.PI * 4 / 25;   // 0.5027: the isoperimetric quotient of a 1:4 box

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({ root: typeof root !== 'undefined' ? root : undefined, picture: typeof picture !== 'undefined' ? picture : undefined, W: typeof W !== 'undefined' ? W : undefined, H: typeof H !== 'undefined' ? H : undefined })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'corners-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
  fs.writeFileSync(dst, s.slice(0, i) + exp + s.slice(i));
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

const RUN = ({ FRAMES, PX, PY, SEATED, SLIVER }) => {
  const X = window.__X;
  X.setMouse(PX, PY);
  // a loop with its collinear and near-duplicate vertices removed: a corner
  // is a real change of direction, not a seam in the outline
  const clean = (lp) => {
    let a = [];
    for (const p of lp) { const q = a[a.length - 1]; if (!q || Math.hypot(p[0] - q[0], p[1] - q[1]) > 0.5) a.push(p); }
    while (a.length > 1 && Math.hypot(a[0][0] - a[a.length - 1][0], a[0][1] - a[a.length - 1][1]) <= 0.5) a.pop();
    if (a.length < 3) return a;
    const out = [];
    for (let i = 0; i < a.length; i++) {
      const p = a[(i + a.length - 1) % a.length], c = a[i], q = a[(i + 1) % a.length];
      const ux = c[0] - p[0], uy = c[1] - p[1], vx = q[0] - c[0], vy = q[1] - c[1];
      const lu = Math.hypot(ux, uy), lv = Math.hypot(vx, vy);
      if (Math.abs(ux * vy - uy * vx) / (lu * lv) > 1e-3) out.push(c);
    }
    return out.length >= 3 ? out : a;
  };
  const frames = [], marks = [], inset = {};
  let n = 0, cur = 'flock0';
  const step = (seated) => {
    window.__advance(1);
    const pic = X.fn('picture'), W = X.fn('W'), H = X.fn('H');
    const rec = { f: n++, k: {}, seated: !!seated, n: 0, iqSum: 0, sliver: 0, iqMin: 1 };
    if (!pic) { frames.push(rec); return; }
    let L = Infinity, R = Infinity, T = Infinity, B = Infinity;
    for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid) continue;
      for (const lp0 of l.loops) {
        if (lp0.hole) continue;
        const lp = clean(lp0);
        if (lp.length < 3) continue;
        rec.k[lp.length] = (rec.k[lp.length] || 0) + 1;
        // HOW FAT THE CELL IS. A corner count alone cannot tell a cell from a
        // splinter: a five-cornered wedge scores exactly like a five-cornered
        // cell. The isoperimetric quotient 4*pi*A / P^2 is 1 for a disc; for a
        // 1:r box it is pi*r / (1 + r)^2, so 0.785 for a square, 0.698 for 1:2,
        // 0.589 for 1:3 and 0.503 for 1:4. Below SLIVER a card is thinner than
        // a 1:4 box and reads as a shard. (An earlier cut of this probe used
        // 0.40, which is 1:5.68 — it let every 1:4 to 1:5.7 wedge through as
        // fat, which is exactly the shape the gate exists to catch.)
        let A2 = 0, P = 0;
        for (let i = 0, m = lp.length; i < m; i++) {
          const p = lp[i], q = lp[(i + 1) % m];
          A2 += p[0] * q[1] - q[0] * p[1];
          P += Math.hypot(q[0] - p[0], q[1] - p[1]);
        }
        const A = Math.abs(A2) / 2;
        const iq = P > 0 ? Math.min(1, 4 * Math.PI * A / (P * P)) : 0;
        rec.n++; rec.iqSum += iq; rec.iqMin = Math.min(rec.iqMin, iq);
        if (iq < SLIVER) rec.sliver++;
        for (const p of lp) {
          L = Math.min(L, p[0]); R = Math.min(R, W - p[0]);
          T = Math.min(T, p[1]); B = Math.min(B, H - p[1]);
        }
      }
    }
    if (seated && Number.isFinite(L)) inset[cur] = { left: +L.toFixed(1), right: +R.toFixed(1), top: +T.toFixed(1), bottom: +B.toFixed(1) };
    frames.push(rec);
  };
  for (let i = 0; i < 120; i++) step(false);
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    cur = sc; marks.push({ f: n, scene: sc });
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    for (let i = 0; i < FRAMES; i++) step(i >= FRAMES - SEATED);
  }
  return { frames, marks, inset };
};

function tally(frames) {
  const hist = {};
  let total = 0;
  for (const F of frames) for (const k in F.k) { hist[k] = (hist[k] || 0) + F.k[k]; total += F.k[k]; }
  const share = (pred) => {
    let s = 0;
    for (const k in hist) if (pred(+k)) s += hist[k];
    return total ? +(s / total).toFixed(4) : 0;
  };
  let vertsMax = 0;
  for (const k in hist) vertsMax = Math.max(vertsMax, +k);
  let n = 0, iqSum = 0, sliver = 0, iqMin = 1;
  for (const F of frames) { n += F.n || 0; iqSum += F.iqSum || 0; sliver += F.sliver || 0; if (F.n) iqMin = Math.min(iqMin, F.iqMin); }
  return {
    bodyFrames: total, hist, vertsMax,
    // a cell that is not a splinter: mean fatness, and the share thinner
    // than a 1:4 box. A high organicShare with a high sliverShare is not the
    // middle the page wants — it is shards.
    iqMean: n ? +(iqSum / n).toFixed(3) : 0,
    iqMin: +iqMin.toFixed(3),
    sliverShare: n ? +(sliver / n).toFixed(4) : 0,
    budgetShare: share(k => k >= 3 && k <= 9),      // the organic middle
    rigidShare: share(k => k === 4),                 // rectangles
    organicShare: share(k => k >= 5 && k <= 9),      // the band that must dominate in transit
    overBudget: share(k => k >= 10),                 // flubber
  };
}

function metrics({ frames, marks, inset }) {
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  const transition = frames.filter(F => ['hero', 'sidebar', 'frame'].includes(sceneOf(F.f)) && !F.seated);
  const seated = frames.filter(F => F.seated);
  const byScene = {};
  for (const sc of ['flock0', 'bento', 'hero', 'sidebar', 'frame', 'flock']) {
    const fs_ = frames.filter(F => sceneOf(F.f) === sc);
    if (fs_.length) byScene[sc] = tally(fs_);
  }
  const insets = Object.values(inset);
  const worstInset = insets.length ? Math.min(...insets.flatMap(o => [o.left, o.right, o.top, o.bottom])) : null;
  return {
    clock: { dtMs: DT, jitterMs: JIT }, pointer: [PX, PY], frames: frames.length,
    all: tally(frames), transition: tally(transition), seated: tally(seated),
    byScene,
    restingInset: inset,
    // the single number that says whether the page rests at 100%: the
    // smallest gutter over every settled scene and every edge. Negative is
    // ink off the crop at rest, which is a permanent bleed.
    worstRestingInset: worstInset,
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
  const data = await p.evaluate(RUN, { FRAMES, PX, PY, SEATED, SLIVER });
  await b.close();
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 2));
  console.log(JSON.stringify(m));
})();
