/* THE SKIP: does the page ever move in one frame in a way it cannot explain?
 *   node jolt.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N]
 *
 * motion.js asks how a change is spread over time and answers with averages:
 * a page can score well on every one of them and still contain two frames that
 * read as a jolt, because two frames out of two hundred move no average very
 * far. This probe looks for the opposite thing — the WORST single frame — and
 * says where in the change it happened.
 *
 * A cell has two properties that should never step:
 *
 *   its AREA, which is set by its claim, and its claim is eased along the same
 *   progress curve as its position. A cell whose area changes by a tenth in
 *   one frame was not eased into it by anything; something about the GROUND
 *   changed under it.
 *
 *   its CENTROID, which is carried by a spring with a 0.148 s response. A
 *   spring cannot move a body a long way in one frame.
 *
 * Reported per scene:
 *
 *   areaStepMax     the largest one-frame change in a cell's area, as a share
 *                   of that cell's area. HIGH IS THE COMPLAINT.
 *   areaStepP99     the 99th percentile of the same, so one outlier cannot be
 *                   mistaken for a page that steps constantly.
 *   spike           the worst frame's displacement over the MEDIAN OF ITS
 *                   NEIGHBOURS — the frames either side of it, itself
 *                   excluded. A skip is a discontinuity, not a global
 *                   outlier, so the comparison has to be local: measured
 *                   against the whole scene, the frame in which Murmur's
 *                   reservoir slams shut is only 4.5x the average, because
 *                   the average is taken over a page that is moving. Against
 *                   the four frames on either side of it, which move 3-5 px,
 *                   its 173 px is FORTY times its neighbours, and that is
 *                   what the eye is reporting.
 *   spikeFrames     how many frames exceed SPIKE_RATIO by that measure.
 *   worst           the three worst frames: index, when in the scene they fall
 *                   (0 = the first frame of the change, 1 = the last frame
 *                   anything moved), and what made them.
 *
 * The position in the scene is the point. A jolt at 0.00 and another at ~1.0
 * is a thing that switches on when the change starts and off when it ends; a
 * jolt in the middle is a collision. Nested members are not read.
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
const SPIKE_RATIO = 4;    // x the median of a frame's NEIGHBOURS before it is a spike
const SPIKE_WIN = 4;      // frames either side that count as the neighbourhood
const SPIKE_FLOOR = 3;    // px: a neighbourhood quieter than this cannot make a ratio
const AREA_FLOOR = 400;   // px2: a cell smaller than this is a transient, not a cell

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({ picture: typeof picture !== 'undefined' ? picture : undefined, W: typeof W !== 'undefined' ? W : undefined, H: typeof H !== 'undefined' ? H : undefined })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'jolt-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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
  const measure = (loops) => {
    let A2 = 0, cx = 0, cy = 0;
    for (const lp of loops) {
      for (let i = 0, m = lp.length; i < m; i++) {
        const p = lp[i], q = lp[(i + 1) % m];
        const f = p[0] * q[1] - q[0] * p[1];
        A2 += f; cx += (p[0] + q[0]) * f; cy += (p[1] + q[1]) * f;
      }
    }
    if (Math.abs(A2) < 1e-9) return null;
    return { a: Math.abs(A2 / 2), c: [cx / (3 * A2), cy / (3 * A2)] };
  };
  const snap = () => {
    window.__advance(1);
    const pic = X.fn('picture');
    const m = new Map();
    if (pic) for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid) continue;
      const v = measure(l.loops);
      if (v) m.set(l.body.id, v);
    }
    return m;
  };
  for (let i = 0; i < 120; i++) snap();
  const scenes = [];
  // THE FIRST FRAME OF A CHANGE IS THE ONE THAT MATTERS MOST, so `prev` is
  // carried across the click: frame 0's displacement is the step from the
  // page AS IT RESTED into the first frame of the change. Resetting it to
  // null per scene, as this probe first did, silently discarded exactly the
  // frame in which anything that switches on at the start of a change would
  // show — and in Murmur that frame moves 33 px against neighbours of 1.4.
  let prev = snap();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    const frames = [];
    for (let i = 0; i < FRAMES; i++) {
      const now = snap();
      const row = { move: 0, areaStep: 0, areaStepId: null, moveMax: 0 };
      if (prev) for (const [id, v] of now) {
        const p = prev.get(id);
        if (!p) continue;
        const d = Math.hypot(v.c[0] - p.c[0], v.c[1] - p.c[1]);
        row.move += d;
        if (d > row.moveMax) row.moveMax = d;
        const base = Math.max(p.a, v.a);
        if (base > 400) {
          const s = Math.abs(v.a - p.a) / base;
          if (s > row.areaStep) { row.areaStep = s; row.areaStepId = id; }
        }
      }
      frames.push(row);
      prev = now;
    }
    scenes.push({ scene: sc, frames });
  }
  return scenes;
};

function metrics(scenes) {
  const by = {};
  for (const s of scenes) {
    const F = s.frames;
    // the change ends at the LAST frame in which anything moved
    let settle = 0;
    for (let i = 0; i < F.length; i++) if (F[i].moveMax > MOVE_EPS) settle = i + 1;
    const moving = F.slice(0, Math.max(1, settle)).map(f => f.move).filter(x => x > MOVE_EPS);
    const sorted = moving.slice().sort((a, b) => a - b);
    const median = sorted.length ? sorted[sorted.length >> 1] : 0;
    const areas = F.slice(0, Math.max(1, settle)).map(f => f.areaStep).sort((a, b) => a - b);
    const p = (q) => areas.length ? areas[Math.min(areas.length - 1, Math.floor(q * areas.length))] : 0;
    // THE LOCAL COMPARISON. A frame's neighbours are the SPIKE_WIN frames on
    // either side of it, itself excluded; a frame is a spike when it moves
    // SPIKE_RATIO times their median. The neighbourhood is floored at
    // SPIKE_FLOOR px so that a page which is merely still does not make every
    // ordinary frame look like a leap.
    const span = Math.max(1, settle);
    const mv = F.slice(0, span).map(f => f.move);
    const local = (i) => {
      const n = [];
      for (let k = Math.max(0, i - SPIKE_WIN); k <= Math.min(span - 1, i + SPIKE_WIN); k++) if (k !== i) n.push(mv[k]);
      if (!n.length) return SPIKE_FLOOR;
      n.sort((a, b) => a - b);
      return Math.max(SPIKE_FLOOR, n[n.length >> 1]);
    };
    const rows = F.slice(0, span).map((f, i) => ({
      i, at: settle > 1 ? +(i / (settle - 1)).toFixed(3) : 0,
      move: +f.move.toFixed(1),
      spike: +(f.move / local(i)).toFixed(2),
      ratio: median > 0 ? +(f.move / median).toFixed(2) : 0,
      areaStep: +f.areaStep.toFixed(4),
    }));
    const spikeFrames = rows.filter(r => r.spike >= SPIKE_RATIO).length;
    const worstMove = rows.slice().sort((a, b) => b.spike - a.spike).slice(0, 3);
    const worstArea = rows.slice().sort((a, b) => b.areaStep - a.areaStep).slice(0, 3);
    by[s.scene] = {
      settleFrames: settle, medianMove: +median.toFixed(1),
      areaStepMax: +p(0.999).toFixed(4), areaStepP99: +p(0.99).toFixed(4), areaStepP50: +p(0.5).toFixed(4),
      spikeFrames, spikeMax: worstMove.length ? worstMove[0].spike : 0,
      joltFrames: rows.filter(r => r.ratio >= SPIKE_RATIO).length,
      worstByMove: worstMove, worstByArea: worstArea,
    };
  }
  const T = ['hero', 'sidebar', 'frame'].filter(k => by[k]);
  const avg = (k) => T.length ? +(T.reduce((a, s) => a + by[s][k], 0) / T.length).toFixed(4) : 0;
  const worst = (k) => T.length ? Math.max(...T.map(s => by[s][k])) : 0;
  return {
    clock: { dtMs: DT, jitterMs: JIT }, frames: FRAMES,
    transition: {
      areaStepMax: worst('areaStepMax'), areaStepP99: avg('areaStepP99'),
      spikeMax: worst('spikeMax'), spikeFrames: worst('spikeFrames'),
      joltFrames: worst('joltFrames'),
    },
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
  const data = await p.evaluate(RUN, { FRAMES, PX, PY });
  await b.close();
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 2));
  console.log(JSON.stringify(m));
})();
