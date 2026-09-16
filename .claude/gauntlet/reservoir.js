/* WHOSE SPILLOVER IS IT? — is the margin a buffer the page uses together, or
 * an escape hatch one crushed cell reaches for?
 *   node reservoir.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N]
 *
 * spill.js answers HOW MUCH ink is outside the window and FOR HOW LONG, which
 * is enough to catch a permanent bleed. It cannot tell the two things apart
 * that the owner distinguished by eye:
 *
 *   "I see single cells resorting to it if they feel squeezed, but I don't
 *    see it being used holistically. It sadly is a private escape hatch
 *    rather than what it should be: a spillover buffer the hivemind can use
 *    to accommodate coordinated and choreographed motions."
 *
 * One cell hanging a long way off one edge and the whole page breathing a
 * little way off all four can carry the SAME outside area for the SAME number
 * of frames. What separates them is how the spill is shared out:
 *
 *   users        how many bodies have ink outside the window in a frame. 1 is
 *                an escape hatch; most of the roster is a page breathing.
 *   concentration the largest single spiller's share of that frame's outside
 *                ink. 1.0 means one body is the whole of it. LOW IS THE
 *                COLLECTIVE CASE.
 *   edges        how many of the four window edges carry ink in one frame. A
 *                cell escaping goes over one; a page making room goes over
 *                all of them.
 *   worstShare   the largest share of the outside ink any one body held, in
 *                any frame of the scene. This is the escape hatch at its most
 *                private, and no averaging can hide it.
 *
 * And the gate every one of those is worthless without:
 *
 *   restingPx2   outside ink once the scene has settled. Must be zero. A
 *                reservoir with anything in it at rest is not a reservoir,
 *                it is a bigger page.
 *
 * Areas are computed by clipping each raw outline against the window and
 * against each of the four outside half-planes — exact, not rastered, so a
 * cell one pixel over the edge is counted as one pixel. Nested members are
 * not read: a member spills with its field or not at all.
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
const SEATED = 5;      // frames at the end of a scene counted as settled
const EPS_PX2 = 25;    // px² of outside ink below which a body is not spilling

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({ picture: typeof picture !== 'undefined' ? picture : undefined, W: typeof W !== 'undefined' ? W : undefined, H: typeof H !== 'undefined' ? H : undefined })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'reservoir-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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

const RUN = ({ FRAMES, PX, PY, EPS_PX2, SEATED }) => {
  const X = window.__X;
  X.setMouse(PX, PY);
  const W = X.fn('W'), H = X.fn('H');
  const shoelace = (p) => { let a = 0; for (let i = 0, m = p.length; i < m; i++) { const q = p[(i + 1) % m]; a += p[i][0] * q[1] - q[0] * p[i][1]; } return a / 2; };
  // Sutherland-Hodgman against one half-plane, given as keep(p) and the
  // intersection of the segment with the boundary
  const clipHalf = (poly, keep, cut) => {
    const out = [];
    for (let i = 0, m = poly.length; i < m; i++) {
      const a = poly[i], b = poly[(i + 1) % m], ka = keep(a), kb = keep(b);
      if (ka) out.push(a);
      if (ka !== kb) out.push(cut(a, b));
    }
    return out;
  };
  const AX = (lo, hi, axis) => (poly) => {
    let p = poly;
    p = clipHalf(p, (q) => q[axis] >= lo, (a, b) => { const t = (lo - a[axis]) / (b[axis] - a[axis]); return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; });
    if (!p.length) return p;
    p = clipHalf(p, (q) => q[axis] <= hi, (a, b) => { const t = (hi - a[axis]) / (b[axis] - a[axis]); return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; });
    return p;
  };
  const BIG = 1e5;
  const clipBox = (poly, x0, y0, x1, y1) => {
    let p = AX(x0, x1, 0)(poly);
    if (!p.length) return p;
    return AX(y0, y1, 1)(p);
  };
  const areaIn = (loops, x0, y0, x1, y1) => {
    let a = 0;
    for (const lp of loops) { const c = clipBox(lp, x0, y0, x1, y1); if (c.length > 2) a += shoelace(c); }
    return a;
  };
  const scenes = [];
  const step = () => {
    window.__advance(1);
    const pic = X.fn('picture');
    const rows = [];
    if (pic) for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid) continue;
      const loops = l.loops.map(lp => lp.map(p => [p[0], p[1]]));
      const tot = Math.abs(loops.reduce((a, lp) => a + shoelace(lp), 0));
      const ins = Math.abs(areaIn(loops, 0, 0, W, H));
      const outside = Math.max(0, tot - ins);
      if (outside <= EPS_PX2) continue;
      rows.push({
        id: l.body.id, outside,
        e: [
          Math.abs(areaIn(loops, -BIG, -BIG, 0, BIG)),      // left of the window
          Math.abs(areaIn(loops, W, -BIG, BIG, BIG)),       // right
          Math.abs(areaIn(loops, -BIG, -BIG, BIG, 0)),      // above
          Math.abs(areaIn(loops, -BIG, H, BIG, BIG)),       // below
        ],
      });
    }
    return rows;
  };
  for (let i = 0; i < 120; i++) step();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    const frames = [];
    for (let i = 0; i < FRAMES; i++) frames.push(step());
    scenes.push({ scene: sc, frames });
  }
  return { W, H, scenes };
};

function metrics(data) {
  const by = {};
  for (const s of data.scenes) {
    const n = s.frames.length;
    let spillFrames = 0, usersSum = 0, usersMax = 0, concSum = 0, edgesMax = 0, edgesSum = 0;
    let outMax = 0, outSum = 0, worstShare = 0, restPx2 = 0;
    for (let i = 0; i < n; i++) {
      const rows = s.frames[i];
      const total = rows.reduce((a, r) => a + r.outside, 0);
      if (i >= n - SEATED) restPx2 = Math.max(restPx2, total);
      if (!rows.length) continue;
      spillFrames++;
      usersSum += rows.length; usersMax = Math.max(usersMax, rows.length);
      const top = Math.max(...rows.map(r => r.outside));
      const share = total > 0 ? top / total : 0;
      concSum += share; worstShare = Math.max(worstShare, share);
      const edges = [0, 1, 2, 3].filter(k => rows.reduce((a, r) => a + r.e[k], 0) > 25).length;
      edgesMax = Math.max(edgesMax, edges); edgesSum += edges;
      outMax = Math.max(outMax, total); outSum += total;
    }
    const d = (x) => +x.toFixed(3);
    by[s.scene] = {
      frames: n, spillFrames,
      spillShare: d(spillFrames / n),
      usersMax, usersMean: spillFrames ? d(usersSum / spillFrames) : 0,
      concentration: spillFrames ? d(concSum / spillFrames) : 0,
      worstShare: d(worstShare),
      edgesMax, edgesMean: spillFrames ? d(edgesSum / spillFrames) : 0,
      outsideMaxPx2: Math.round(outMax),
      outsideMeanPx2: spillFrames ? Math.round(outSum / spillFrames) : 0,
      restingPx2: Math.round(restPx2),
    };
  }
  const T = ['hero', 'sidebar', 'frame'].filter(k => by[k]);
  // WEIGHTED BY THE FRAMES THAT ACTUALLY SPILL. A plain mean over scenes
  // counts a scene that never touched the margin as a scene whose spill was
  // perfectly shared, which flatters exactly the page this probe exists to
  // catch: Tide reaches the ring in one of its three transitions, and
  // averaging its 0.573 concentration with two zeros reported 0.191 — better
  // than a page that genuinely shares it. Scenes that never spill are counted
  // by scenesUsed instead, where their silence means what it says.
  const wsum = T.reduce((a, s) => a + by[s].spillFrames, 0);
  const wavg = (k) => wsum ? +(T.reduce((a, s) => a + by[s][k] * by[s].spillFrames, 0) / wsum).toFixed(3) : 0;
  const avg = (k) => T.length ? +(T.reduce((a, s) => a + by[s][k], 0) / T.length).toFixed(3) : 0;
  const worst = (k) => T.length ? Math.max(...T.map(s => by[s][k])) : 0;
  return {
    clock: { dtMs: DT, jitterMs: JIT }, frames: FRAMES,
    transition: {
      scenesUsed: T.filter(s => by[s].spillFrames > 0).length, scenes: T.length,
      usersMean: wavg('usersMean'), usersMax: worst('usersMax'),
      concentration: wavg('concentration'), worstShare: worst('worstShare'),
      edgesMean: wavg('edgesMean'), edgesMax: worst('edgesMax'),
      spillShare: avg('spillShare'), outsideMaxPx2: worst('outsideMaxPx2'),
    },
    restingPx2: Math.max(...Object.values(by).map(v => v.restingPx2)),
    byScene: by,
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
  const data = await p.evaluate(RUN, { FRAMES, PX, PY, EPS_PX2, SEATED });
  await b.close();
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 2));
  console.log(JSON.stringify(m));
})();
