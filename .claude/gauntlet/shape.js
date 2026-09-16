/* THE SHAPE: every cell on the page is a rectangle or a Voronoi cell, or it is not.
 *   node shape.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N] [--parkx X --parky Y]
 *
 * The owner's rule for a page of cards: a cell is EITHER an axis-aligned
 * rectangle OR a convex Voronoi cell of a point site, cut straight where it
 * meets a rectangle or the page's edge; fracturing an edge beyond what
 * fitting requires is a last resort. ripple.js counts teeth; this probe
 * names what every root content leaf IS, frame by frame, on its raw outline
 * (before the garment rounds it):
 *
 *   RECTANGLE   the outline is its own bounding box (every vertex on the
 *               box's boundary, area within 0.5% of the box's).
 *   NOTCHED     axis-aligned throughout, but not its box: a rectangle less
 *               one or more rectangles — a tile another tile lies across,
 *               the last-resort cut, counted apart because it is one.
 *   VORONOI     convex (every turn the same way, within 1e-3 of straight),
 *               at most 16 vertices, no edge shorter than 2 px.
 *   CUT         convex except at reflex vertices that stand on a rigid
 *               neighbour's boundary (a wall or a hole: a rectangle, or the
 *               reference's convex blend) or the page's edge, within 1 px:
 *               a Voronoi cell cut by what it wraps around, which is what
 *               fitting requires.
 *   FRACTURED   anything else: a tooth, a step, a wedge, a concavity no
 *               rectangle explains.
 *
 * Counted per body-frame and summed per scene, transition frames only (the
 * cold settle excluded); the worst frames are the ones with the most
 * fractured bodies. Same deterministic clock and scenario as the rest of the
 * harness; nested members are not read.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0);
const FRAMES = +opt('--frames', 330);
const PX = +opt('--parkx', -1000), PY = +opt('--parky', -1000);
const NAMES = ['root', 'ringArea', 'picture', 'W', 'H'];

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({${NAMES.map(n => `${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`).join(', ')}})[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'shape-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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

const RUN = ({ FRAMES, PX, PY }) => {
  const X = window.__X, r = X.fn('root');
  X.setMouse(PX, PY);
  const frames = [], marks = [];
  let n = 0;
  const ringArea = (pts) => { let a = 0; for (let i = 0, m = pts.length; i < m; i++) { const p = pts[i], q = pts[(i + 1) % m]; a += p[0] * q[1] - q[0] * p[1]; } return a / 2; };
  // a loop with its collinear and near-duplicate vertices removed
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
  const step = () => {
    window.__advance(1);
    const pic = X.fn('picture');
    const W = X.fn('W'), H = X.fn('H');
    const rec = { f: n++, b: {} };
    if (!pic) { frames.push(rec); return; }
    // the rigid shapes of this frame: every wall and hole (a rectangle, or the
    // reference's convex blend of a cell and its rectangle), whose edges
    // explain a concavity in a cell that wraps around them
    const rigidLoops = [];
    for (const l of pic.leaves) if (l.path.length === 1 && (l.body.wall || l.body.hole)) for (const lp of l.loops) if (!lp.hole && lp.length >= 3) rigidLoops.push(lp);
    // a FIELD (a body with a nested hive) has no root leaf of its own — its
    // members are the leaves — so its wall or hole is read from the engine's
    // state, which every build keeps: root.walls (rectangles) and root.holes
    // (convex pieces); a free cell wrapping a field is cut by it, not fractured
    for (const b of r.walls) { const q = b.wall; if (q) rigidLoops.push([[q[0], q[1]], [q[2], q[1]], [q[2], q[3]], [q[0], q[3]]]); }
    for (const b of r.holes) if (b.hole && b.hole.pieces) for (const pc of b.hole.pieces) if (pc.length >= 3) rigidLoops.push(pc);
    const rectsOf = [];
    const leaves = pic.leaves.filter(l => l.path.length === 1 && !l.isVoid);
    const classes = new Map();
    for (const l of leaves) {
      for (const lp0 of l.loops) {
        if (lp0.hole) continue;
        const lp = clean(lp0);
        if (lp.length < 3) continue;
        let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
        for (const p of lp) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); }
        const onBox = lp.every(p => Math.abs(p[0] - x0) < 0.5 || Math.abs(p[0] - x1) < 0.5 || Math.abs(p[1] - y0) < 0.5 || Math.abs(p[1] - y1) < 0.5);
        const area = Math.abs(ringArea(lp)), box = (x1 - x0) * (y1 - y0);
        const axisAll = lp.every((p, i) => { const q = lp[(i + 1) % lp.length]; return Math.abs(p[0] - q[0]) < 0.5 || Math.abs(p[1] - q[1]) < 0.5; });
        if (onBox && axisAll && area >= 0.995 * box) { rectsOf.push([x0, y0, x1, y1]); classes.set(lp0, { cls: 'rectangle', lp }); continue; }
        classes.set(lp0, { cls: axisAll ? 'notched' : null, lp, x0, y0, x1, y1 });
      }
    }
    const segDist = (p, a, b) => { const ex = b[0] - a[0], ey = b[1] - a[1], L2 = ex * ex + ey * ey || 1e-9; let t = ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / L2; t = Math.max(0, Math.min(1, t)); return Math.hypot(a[0] + t * ex - p[0], a[1] + t * ey - p[1]); };
    const nearRectEdge = (p) => {
      if (Math.abs(p[0]) < 1 || Math.abs(p[0] - W) < 1 || Math.abs(p[1]) < 1 || Math.abs(p[1] - H) < 1) return true;
      for (const r of rectsOf) {
        const inX = p[0] > r[0] - 1 && p[0] < r[2] + 1, inY = p[1] > r[1] - 1 && p[1] < r[3] + 1;
        if ((Math.abs(p[0] - r[0]) < 1 || Math.abs(p[0] - r[2]) < 1) && inY) return true;
        if ((Math.abs(p[1] - r[1]) < 1 || Math.abs(p[1] - r[3]) < 1) && inX) return true;
      }
      for (const lp of rigidLoops) for (let k = 0; k < lp.length; k++) if (segDist(p, lp[k], lp[(k + 1) % lp.length]) < 1) return true;
      return false;
    };
    for (const l of leaves) {
      const id = l.body.id;
      const b = { rectangle: 0, notched: 0, voronoi: 0, cut: 0, fractured: 0, verts: 0, shortEdges: 0, reflex: 0, unexplained: 0, bite: 0 };
      for (const lp0 of l.loops) {
        const c = classes.get(lp0);
        if (!c) continue;
        const lp = c.lp;
        b.verts = Math.max(b.verts, lp.length);
        if (c.cls === 'rectangle') { b.rectangle++; continue; }
        // HOW DEEP THE LAST RESORT GOES. A notch is a rectangle less a
        // rectangle; the bite is what is missing from the rectangle it would
        // otherwise be, as a share. Counting notched frames alone lets one
        // deep bite hide among many shallow ones.
        if (c.cls === 'notched') {
          let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
          for (const p of lp) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); }
          const box = Math.max(1, (x1 - x0) * (y1 - y0));
          b.notched++; b.bite = Math.max(b.bite, 1 - Math.abs(ringArea(lp)) / box);
          continue;
        }
        // turns and edge lengths
        const m = lp.length, sgn = Math.sign(ringArea(lp)) || 1;
        let reflex = 0, unexplained = 0, shortEdges = 0;
        for (let k = 0; k < m; k++) {
          const p = lp[(k + m - 1) % m], cpt = lp[k], q = lp[(k + 1) % m];
          const ux = cpt[0] - p[0], uy = cpt[1] - p[1], vx = q[0] - cpt[0], vy = q[1] - cpt[1];
          const cr = (ux * vy - uy * vx) / (Math.hypot(ux, uy) * Math.hypot(vx, vy) || 1);
          if (Math.hypot(vx, vy) < 2) shortEdges++;
          if (cr * sgn < -1e-3) { reflex++; if (!nearRectEdge(cpt)) unexplained++; }
        }
        b.reflex += reflex; b.unexplained += unexplained; b.shortEdges += shortEdges;
        if (!reflex && m <= 16 && !shortEdges) b.voronoi++;
        else if (reflex && !unexplained && !shortEdges && m <= 24) b.cut++;
        else b.fractured++;
      }
      rec.b[id] = b;
    }
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
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  const byScene = {};
  const worst = [];
  const keys = ['rectangle', 'notched', 'voronoi', 'cut', 'fractured'];
  for (const F of frames) {
    const sc = sceneOf(F.f);
    const o = byScene[sc] = byScene[sc] || { bodyFrames: 0, rectangle: 0, notched: 0, voronoi: 0, cut: 0, fractured: 0, fracturedFrames: 0, vertsMax: 0, biteMax: 0, biteSum: 0, notchFrames: 0 };
    let fr = 0;
    for (const id in F.b) {
      const b = F.b[id];
      o.bodyFrames++;
      for (const k of keys) o[k] += b[k];
      o.vertsMax = Math.max(o.vertsMax, b.verts);
      if (b.notched) { o.notchFrames++; o.biteMax = Math.max(o.biteMax, b.bite); o.biteSum += b.bite; }
      if (b.fractured) { fr++; worst.push({ f: F.f, scene: sc, id: +id, verts: b.verts, reflex: b.reflex, unexplained: b.unexplained, shortEdges: b.shortEdges }); }
    }
    if (fr) o.fracturedFrames++;
  }
  const out = {};
  for (const sc in byScene) { const o = byScene[sc]; out[sc] = { ...o, fracturedShare: +(o.fractured / Math.max(1, o.bodyFrames)).toFixed(4), rectangleShare: +(o.rectangle / Math.max(1, o.bodyFrames)).toFixed(3), biteMax: +o.biteMax.toFixed(3), biteMean: +(o.biteSum / Math.max(1, o.notchFrames)).toFixed(3) }; }
  const sum = (k) => ['hero', 'sidebar', 'frame'].reduce((a, sc) => a + (byScene[sc] ? byScene[sc][k] : 0), 0);
  return { frames: frames.length, clock: { dtMs: DT, jitterMs: JIT }, pointer: [PX, PY],
    transition: { bodyFrames: sum('bodyFrames'), rectangle: sum('rectangle'), notched: sum('notched'), voronoi: sum('voronoi'), cut: sum('cut'), fractured: sum('fractured'), fracturedFrames: sum('fracturedFrames'),
      notchFrames: sum('notchFrames'), biteMax: +['hero', 'sidebar', 'frame'].reduce((a, sc) => Math.max(a, byScene[sc] ? byScene[sc].biteMax : 0), 0).toFixed(3),
      biteMean: +(sum('biteSum') / Math.max(1, sum('notchFrames'))).toFixed(3) },
    byScene: out, worst: worst.sort((a, b) => b.unexplained - a.unexplained || b.verts - a.verts).slice(0, 12) };
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
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 2));
  console.log(JSON.stringify(m));
})();
