/* OUT OF PLUMB: how much of the page's ink is drawn on axis?
 *   node plumb.js <hive.html> [out.json] [--dt 30] [--frames N] [--tol 4]
 *                                [--vw 1440] [--vh 900] [--count N]
 *
 * --vw/--vh/--count matter more than they look. The lattice is sized from the
 * viewport (wantCols/wantRows) and the roster runs to 30, so a template that
 * lays cells on a grid can run out of whole lattice slots on a short page and
 * quietly fall back to the dissection it was meant to replace. One viewport
 * and one roster size cannot see that; this is how the gate looks at both.
 *
 * corners.js counts how many corners a cell has; it cannot tell a rectangle
 * from a trapezoid, because both have four. But a bento READS as a bento
 * because its edges are vertical and horizontal, and a fanned column reads as
 * wrong for exactly the opposite reason — every edge is a degree or two off
 * and no two agree.
 *
 * So this measures ANGLE, weighted by edge LENGTH:
 *
 *   axisShare    the share of a cell's outline length lying within --tol
 *                degrees of horizontal or vertical. 1.0 is a rectangle. A
 *                trapezoid with two axis-aligned sides sits near 0.5.
 *   rectShare    the share of CELLS that are wholly on axis (axisShare >= 0.95
 *                and 4 to 6 corners) — a cell a person would call a card.
 *   tiltMean     for the off-axis length only, the mean angle from the nearer
 *                axis. A page that is 3 degrees out everywhere is a page that
 *                looks skewed; a page with a few genuinely diagonal seams is
 *                not the same thing and this separates them.
 *   edgeTilt     the same, length-weighted over every off-axis edge, split by
 *                whether the edge lies ON the window boundary (which is
 *                exactly on axis by construction and is excluded) or inside.
 *
 * Read at REST — the last frames of a settled scene — because that is when a
 * layout is making its claim about what shape it is. Nested members are not
 * read; a field's own outline is what the page shows.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 30), JIT = +opt('--jitter', 0);
const FRAMES = +opt('--frames', 220);
const TOL = +opt('--tol', 4);        // degrees from an axis that still counts as on it
const PX = +opt('--parkx', -1000), PY = +opt('--parky', -1000);
const VW = +opt('--vw', 1440), VH = +opt('--vh', 900);
const COUNT = +opt('--count', 0);    // 0: leave the page's own default roster
const FULL = +opt('--full', 0);      // 1: read every body's own outline, fields included
const SEATED = 5;                    // frames at the end of a scene counted as settled
const MIN_EDGE = 2;                  // px: shorter than this is a rounding artefact

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({ picture: typeof picture !== 'undefined' ? picture : undefined, W: typeof W !== 'undefined' ? W : undefined, H: typeof H !== 'undefined' ? H : undefined, root: typeof root !== 'undefined' ? root : undefined })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'plumb-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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

const RUN = ({ FRAMES, PX, PY, TOL, SEATED, MIN_EDGE, COUNT, FULL }) => {
  const X = window.__X;
  X.setMouse(PX, PY);
  const W = X.fn('W'), H = X.fn('H');
  const onWindow = (a, b) => {
    const e = 0.75;
    return (Math.abs(a[0]) < e && Math.abs(b[0]) < e) || (Math.abs(a[0] - W) < e && Math.abs(b[0] - W) < e)
        || (Math.abs(a[1]) < e && Math.abs(b[1]) < e) || (Math.abs(a[1] - H) < e && Math.abs(b[1] - H) < e);
  };
  const measure = (l) => {
    let total = 0, onAxis = 0, tiltSum = 0, tiltLen = 0, edges = 0;
    for (const lp of l.loops) {
      for (let i = 0, m = lp.length; i < m; i++) {
        const a = lp[i], b = lp[(i + 1) % m];
        const dx = b[0] - a[0], dy = b[1] - a[1];
        const len = Math.hypot(dx, dy);
        if (len < MIN_EDGE) continue;
        edges++;
        total += len;
        // angle to the NEARER axis, in degrees: 0 is on axis, 45 is diagonal
        let ang = Math.abs(Math.atan2(dy, dx) * 180 / Math.PI) % 90;
        if (ang > 45) ang = 90 - ang;
        if (ang <= TOL) { onAxis += len; continue; }
        if (onWindow(a, b)) { onAxis += len; continue; }   // the crop is on axis by construction
        tiltSum += ang * len; tiltLen += len;
      }
    }
    if (total <= 0) return null;
    return { id: l.body.id, total, axisShare: onAxis / total, tilt: tiltLen ? tiltSum / tiltLen : 0, tiltLen, edges };
  };
  // THE ROSTER. Not an angle at all: the count of bodies that are still
  // bidding, and any rectangle with no area. A template that hands out a
  // zero-area rect drops that body below ACTIVE_MIN and it stops bidding —
  // the page loses a card while every angle on it still reads beautifully.
  // An axis measure cannot see that, so it is counted here beside it.
  const census = () => {
    const root = X.fn('root');
    let bodies = 0, bidding = 0, zeroArea = 0;
    if (root) for (const b of root.bodies) {
      bodies++;
      if (b.claim >= 0.01) bidding++;
      const r = b.rect;
      if (r && !((r[2] - r[0]) > 0 && (r[3] - r[1]) > 0)) zeroArea++;
    }
    return { bodies, bidding, zeroArea };
  };
  const sample = () => {
    const pic = X.fn('picture');
    const cells = [];
    if (FULL) {
      const root = X.fn('root');
      if (root) for (const b of root.bodies) {
        if (b.isVoid || !b.loops || !b.loops.length) continue;
        const c = measure({ loops: b.loops, body: b });
        if (c) cells.push(c);
      }
      return cells;
    }
    if (pic) for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid || !l.loops) continue;
      const c = measure(l);
      if (c) cells.push(c);
    }
    return cells;
  };
  const step = () => { window.__advance(1); };
  if (COUNT) {
    const c = document.getElementById('count');
    c.value = String(COUNT);
    c.dispatchEvent(new Event('input', { bubbles: true }));
  }
  for (let i = 0; i < 120; i++) step();
  const out = {}, roster = {};
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    let seated = [];
    for (let i = 0; i < FRAMES; i++) { step(); if (i >= FRAMES - SEATED) seated = seated.concat(sample()); }
    out[sc] = seated;
    roster[sc] = census();
  }
  return { cells: out, roster };
};

function metrics(payload) {
  const data = payload.cells, roster = payload.roster;
  const by = {};
  for (const sc in data) {
    const cells = data[sc];
    if (!cells.length) { by[sc] = null; continue; }
    const len = cells.reduce((a, c) => a + c.total, 0);
    const onAxis = cells.reduce((a, c) => a + c.axisShare * c.total, 0);
    const tiltLen = cells.reduce((a, c) => a + c.tiltLen, 0);
    const tiltSum = cells.reduce((a, c) => a + c.tilt * c.tiltLen, 0);
    const rect = cells.filter(c => c.axisShare >= 0.95).length;
    const half = cells.filter(c => c.axisShare >= 0.5).length;
    by[sc] = {
      cells: cells.length,
      axisShare: +(onAxis / len).toFixed(4),
      rectShare: +(rect / cells.length).toFixed(4),
      halfShare: +(half / cells.length).toFixed(4),
      tiltMean: +(tiltLen ? tiltSum / tiltLen : 0).toFixed(2),
      offAxisLenShare: +(tiltLen / len).toFixed(4),
    };
  }
  const T = ['hero', 'sidebar', 'frame'].filter(k => by[k]);
  const avg = (k) => T.length ? +(T.reduce((a, s) => a + by[s][k], 0) / T.length).toFixed(4) : 0;
  return {
    clock: { dtMs: DT, jitterMs: JIT }, frames: FRAMES, tolDeg: TOL,
    viewport: { w: VW, h: VH }, count: COUNT || null, full: !!FULL,
    roster,
    // the worst scene on each roster fact, so a gate needs one comparison
    bodiesMin: Math.min(...Object.values(roster).map(r => r.bodies)),
    notBiddingMax: Math.max(...Object.values(roster).map(r => r.bodies - r.bidding)),
    zeroAreaMax: Math.max(...Object.values(roster).map(r => r.zeroArea)),
    withVoid: { axisShare: avg('axisShare'), rectShare: avg('rectShare'), tiltMean: avg('tiltMean') },
    bento: by.bento, byScene: by,
  };
}

(async () => {
  const dst = instrument(SRC);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: VW, height: VH } });
  await p.addInitScript(CLOCK);
  const errs = []; p.on('pageerror', e => errs.push(String(e.message || e)));
  await p.goto('file://' + dst);
  await p.waitForTimeout(300);
  const data = await p.evaluate(RUN, { FRAMES, PX, PY, TOL, SEATED, MIN_EDGE, COUNT, FULL });
  await b.close();
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 2));
  console.log(JSON.stringify(m));
})();
