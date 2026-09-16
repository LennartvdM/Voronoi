/* THE SPILL: does the page use the ground past its window, visibly?
 *   node spill.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N] [--parkx X --parky Y]
 *
 * The owner has let the layout spill into a margin around the screen for
 * five marks, and each one either kept every cell inside the viewport or
 * computed outside geometry and then drew its cells bordered along the
 * crop. This probe reads, per frame, on every root content leaf's raw
 * outline (page px, the window being [0,W]x[0,H]):
 *
 *   OUTSIDE AREA   px² of the outline beyond the window (the outline
 *                  clipped to the window, subtracted from the whole);
 *   STRADDLERS     bodies with any outline both inside and outside;
 *   CROP BORDERS   a straddler's outline edge that runs ALONG a window edge
 *                  the same outline crosses (both ends within 0.5 px of it,
 *                  longer than 4 px): the signature of geometry cut at the
 *                  crop rather than continuing past it — a picture that
 *                  says it spills but draws a frame. A cell that truly
 *                  crosses has vertices outside and no such edge; a tile
 *                  seated on the lattice's edge has an edge on the window's
 *                  edge, but does not cross it there.
 *
 * Summed per scene (transition frames), with the peak frame's outside area
 * and the bodies out there. A build whose domain is the window reads 0
 * everywhere; a build whose domain is wider should read outside area on
 * the transitions, straddlers, and no crop borders.
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
  const dst = path.join(os.tmpdir(), 'spill-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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
  const X = window.__X;
  X.setMouse(PX, PY);
  const frames = [], marks = [];
  let n = 0;
  const ringArea = (pts) => { let a = 0; for (let i = 0, m = pts.length; i < m; i++) { const p = pts[i], q = pts[(i + 1) % m]; a += p[0] * q[1] - q[0] * p[1]; } return Math.abs(a) / 2; };
  const clipHalf = (pts, ax, ay, b) => {   // keep ax*x + ay*y <= b
    const out = []; const m = pts.length;
    for (let i = 0; i < m; i++) {
      const A = pts[i], B = pts[(i + 1) % m];
      const av = ax * A[0] + ay * A[1] - b, bv = ax * B[0] + ay * B[1] - b;
      if (av <= 0) out.push(A);
      if ((av < 0) !== (bv < 0) && av !== bv) { const t = av / (av - bv); out.push([A[0] + t * (B[0] - A[0]), A[1] + t * (B[1] - A[1])]); }
    }
    return out;
  };
  const inLoop = (x, y, pts) => { let inside = false; for (let i = 0, m = pts.length, j = m - 1; i < m; j = i++) { const a = pts[i], b = pts[j]; if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) inside = !inside; } return inside; };
  const step = () => {
    window.__advance(1);
    const pic = X.fn('picture'), W = X.fn('W'), H = X.fn('H');
    const rec = { f: n++, out: 0, straddlers: 0, cropBorders: 0, bodies: [] };
    // THE INK PAST THE EDGE, whoever's it is: a cell's own edge lying along a
    // window edge it crosses is only a crop — a page computed wide and painted
    // narrow — if the picture stops there. Where the cell beside it carries the
    // ink on past the crop, the two cells simply meet on a line that happens to
    // run along the window's edge, and nothing is cut short.
    const painted = pic ? pic.leaves.filter(l => !l.isVoid).flatMap(l => l.loops.filter(lp => !lp.hole && lp.length >= 3)) : [];
    const inkAt = (x, y) => { for (const lp of painted) if (inLoop(x, y, lp)) return true; return false; };
    if (pic) for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid) continue;
      let outside = 0, inside = 0, borders = 0;
      for (const lp of l.loops) {
        if (lp.hole || lp.length < 3) continue;
        const whole = ringArea(lp);
        let c = clipHalf(lp, -1, 0, 0); if (c.length >= 3) c = clipHalf(c, 1, 0, W); if (c.length >= 3) c = clipHalf(c, 0, -1, 0); if (c.length >= 3) c = clipHalf(c, 0, 1, H);
        const inArea = c.length >= 3 ? ringArea(c) : 0;
        inside += inArea; outside += Math.max(0, whole - inArea);
        // the window's edges this loop crosses (vertices on both sides), and an
        // edge of the loop lying along one of THOSE: a lattice-edge tile sits
        // exactly on the window's left edge and that is not a crop
        const m = lp.length;
        const crossed = [[1, 0, 0], [1, 0, W], [0, 1, 0], [0, 1, H]].filter(([ax, ay, b]) => lp.some(p => ax * p[0] + ay * p[1] < b - 0.5) && lp.some(p => ax * p[0] + ay * p[1] > b + 0.5));
        for (let k = 0; k < m && crossed.length; k++) {
          const p = lp[k], q = lp[(k + 1) % m];
          if (Math.hypot(q[0] - p[0], q[1] - p[1]) < 4) continue;
          for (const [ax, ay, b] of crossed) {
            if (!(Math.abs(ax * p[0] + ay * p[1] - b) < 0.5 && Math.abs(ax * q[0] + ay * q[1] - b) < 0.5)) continue;
            // the far side of the line, a pixel out from the middle of this edge
            const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2, out = b > 0 ? 1 : -1;
            if (inkAt(mx + ax * out, my + ay * out)) break;   // the ink runs on: the cells meet here, the crop does not cut
            borders++; break;
          }
        }
      }
      if (outside > 1) {
        rec.out += outside;
        if (inside > 1) { rec.straddlers++; rec.cropBorders += borders; }
        rec.bodies.push({ id: l.body.id, out: Math.round(outside), in: Math.round(inside), borders });
      }
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
  const sceneOf = (f) => { let s = 'flock0', sf = f; for (const m of marks) if (f >= m.f) { s = m.scene; sf = f - m.f; } return [s, sf]; };
  const byScene = {};
  for (const F of frames) {
    const [sc, sf] = sceneOf(F.f);
    const o = byScene[sc] = byScene[sc] || { frames: 0, framesOutside: 0, outsideSum: 0, outsideMax: 0, peakFrame: -1, peakBodies: [], straddlerFrames: 0, cropBorders: 0, bodiesOutside: new Set() };
    o.frames++;
    if (F.out > 1) { o.framesOutside++; o.outsideSum += F.out; if (F.out > o.outsideMax) { o.outsideMax = F.out; o.peakFrame = sf; o.peakBodies = F.bodies; } for (const b of F.bodies) o.bodiesOutside.add(b.id); }
    if (F.straddlers) o.straddlerFrames++;
    o.cropBorders += F.cropBorders;
  }
  const out = {};
  for (const sc in byScene) { const o = byScene[sc]; out[sc] = { frames: o.frames, framesOutside: o.framesOutside, outsideMaxPx2: Math.round(o.outsideMax), outsideMeanPx2: Math.round(o.outsideSum / Math.max(1, o.frames)), peakFrame: o.peakFrame, peakBodies: o.peakBodies, straddlerFrames: o.straddlerFrames, cropBorders: o.cropBorders, bodiesOutside: [...o.bodiesOutside] }; }
  const sum = (k) => ['hero', 'sidebar', 'frame'].reduce((a, sc) => a + (byScene[sc] ? byScene[sc][k] : 0), 0);
  return { frames: frames.length, clock: { dtMs: DT, jitterMs: JIT }, pointer: [PX, PY], transition: { framesOutside: sum('framesOutside'), outsideMaxPx2: Math.round(['hero', 'sidebar', 'frame'].reduce((a, sc) => Math.max(a, byScene[sc] ? byScene[sc].outsideMax : 0), 0)), straddlerFrames: sum('straddlerFrames'), cropBorders: sum('cropBorders') }, byScene: out };
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
