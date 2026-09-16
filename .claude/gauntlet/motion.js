/* THE COILED SPRING: is the page MOVING, or arriving?
 *   node motion.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N]
 *
 * Every other probe here asks what the page looks like in a frame. None asks
 * how a change is distributed over TIME, which is what the owner is describing
 * with "barely any motion at all, everything just jumps into its position like
 * a tightly coiled spring". A page can score perfectly on shape, corners,
 * fatness and coverage and still read as arriving rather than travelling.
 *
 * Per root content leaf, per frame: the centroid, and how far it moved since
 * the last frame. Per body per scene change:
 *
 *   pathLen     total distance the centroid travelled, in px
 *   netDisp     straight-line distance from where it started to where it
 *               ended. pathLen / netDisp is how indirect the route was; 1.0 is
 *               a straight line.
 *   moveFrames  frames in which it moved more than MOVE_EPS
 *   f80         frames it needed to cover 80% of its pathLen
 *   burst       f80 as a share of the frames the whole change took. LOW IS THE
 *               COMPLAINT: 0.1 means four fifths of the journey happened in a
 *               tenth of the time and the rest was sitting still.
 *   peakRatio   its fastest frame over its mean moving frame. HIGH IS THE
 *               COMPLAINT: a spring uncoiling, not a body travelling.
 *
 * And per scene: settleFrames, how long until the page stopped moving at all.
 * A change that settles in a fifth of the time the clock allows it has not
 * been given a chance to be watched.
 *
 * Centroids come from the raw outlines, before the garment rounds them.
 * Nested members are not read.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 30), JIT = +opt('--jitter', 0);
const FRAMES = +opt('--frames', 220);
const PX = +opt('--parkx', -1000), PY = +opt('--parky', -1000);
const MOVE_EPS = 0.5;     // px in one frame: below this a body is standing still
const STILL_RUN = 6;      // consecutive still frames that count as settled

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({ picture: typeof picture !== 'undefined' ? picture : undefined, W: typeof W !== 'undefined' ? W : undefined, H: typeof H !== 'undefined' ? H : undefined })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'motion-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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

const RUN = ({ FRAMES, PX, PY, MOVE_EPS }) => {
  const X = window.__X;
  X.setMouse(PX, PY);
  const centroid = (loops) => {
    let A2 = 0, cx = 0, cy = 0;
    for (const lp of loops) {
      if (lp.hole) continue;
      for (let i = 0, m = lp.length; i < m; i++) {
        const p = lp[i], q = lp[(i + 1) % m];
        const f = p[0] * q[1] - q[0] * p[1];
        A2 += f; cx += (p[0] + q[0]) * f; cy += (p[1] + q[1]) * f;
      }
    }
    if (Math.abs(A2) < 1e-9) return null;
    return [cx / (3 * A2), cy / (3 * A2)];
  };
  const scenes = [];
  const step = (rec) => {
    window.__advance(1);
    const pic = X.fn('picture');
    const here = new Map();
    if (pic) for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid) continue;
      const c = centroid(l.loops);
      if (c) here.set(l.body.id, c);
    }
    if (rec) {
      const step = new Map();
      for (const [id, c] of here) {
        const prev = rec.last.get(id);
        if (prev) step.set(id, Math.hypot(c[0] - prev[0], c[1] - prev[1]));
        if (!rec.first.has(id)) rec.first.set(id, c);
        rec.end.set(id, c);
      }
      rec.steps.push(step);
    }
    return here;
  };
  let last = new Map();
  for (let i = 0; i < 120; i++) last = step(null);
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    const rec = { scene: sc, steps: [], first: new Map(), end: new Map(), last };
    for (let i = 0; i < FRAMES; i++) { rec.last = step(rec); }
    // serialise: per body, the per-frame displacements
    const perBody = {};
    for (const [id] of rec.end) {
      perBody[id] = {
        d: rec.steps.map(s => +(s.get(id) || 0).toFixed(3)),
        first: rec.first.get(id), end: rec.end.get(id),
      };
    }
    scenes.push({ scene: sc, frames: rec.steps.length, perBody });
    last = rec.last;
  }
  return scenes;
};

function metrics(scenes) {
  const out = {};
  for (const s of scenes) {
    const rows = [];
    let settle = 0;
    // settleFrames: the last frame in which ANY body moved, plus the still run
    const anyMove = new Array(s.frames).fill(0);
    for (const id in s.perBody) {
      const d = s.perBody[id].d;
      for (let i = 0; i < d.length; i++) if (d[i] > MOVE_EPS) anyMove[i] = 1;
    }
    // the LAST frame anything moved, not the first lull: a staggered change has
    // quiet gaps in the middle, and breaking on one of those reported a scene
    // far shorter than it was, which made burst exceed 1 — impossible for a
    // share, and the tell that this was wrong.
    for (let i = 0; i < anyMove.length; i++) if (anyMove[i]) settle = i + 1;
    for (const id in s.perBody) {
      const b = s.perBody[id], d = b.d;
      const pathLen = d.reduce((a, x) => a + x, 0);
      if (pathLen < 2) continue;                      // never really moved
      const netDisp = b.first && b.end ? Math.hypot(b.end[0] - b.first[0], b.end[1] - b.first[1]) : 0;
      const moving = d.filter(x => x > MOVE_EPS);
      let acc = 0, f80 = d.length;
      for (let i = 0; i < d.length; i++) { acc += d[i]; if (acc >= 0.8 * pathLen) { f80 = i + 1; break; } }
      rows.push({
        pathLen, netDisp,
        wander: netDisp > 1 ? pathLen / netDisp : 1,
        moveFrames: moving.length,
        f80,
        burst: f80 / Math.max(1, settle),
        peakRatio: moving.length ? Math.max(...moving) / (moving.reduce((a, x) => a + x, 0) / moving.length) : 0,
      });
    }
    const mean = (k) => rows.length ? +(rows.reduce((a, r) => a + r[k], 0) / rows.length).toFixed(3) : 0;
    out[s.scene] = {
      bodies: rows.length, frames: s.frames, settleFrames: settle,
      settleShare: +(settle / s.frames).toFixed(3),
      pathLen: mean('pathLen'), netDisp: mean('netDisp'), wander: mean('wander'),
      moveFrames: mean('moveFrames'), f80: mean('f80'),
      burst: mean('burst'), peakRatio: mean('peakRatio'),
    };
  }
  const T = ['hero', 'sidebar', 'frame'].filter(k => out[k]);
  const avg = (k) => T.length ? +(T.reduce((a, s) => a + out[s][k], 0) / T.length).toFixed(3) : 0;
  return {
    clock: { dtMs: DT, jitterMs: JIT }, frames: FRAMES,
    transition: {
      settleShare: avg('settleShare'), pathLen: avg('pathLen'), netDisp: avg('netDisp'),
      wander: avg('wander'), moveFrames: avg('moveFrames'), burst: avg('burst'), peakRatio: avg('peakRatio'),
    },
    byScene: out,
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
  const data = await p.evaluate(RUN, { FRAMES, PX, PY, MOVE_EPS });
  await b.close();
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 2));
  console.log(JSON.stringify(m));
})();
