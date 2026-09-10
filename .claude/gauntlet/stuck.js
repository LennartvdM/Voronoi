/* THE GRIDLOCK. A body that is not where it is going and is not getting
 * there, and what happens to the walls around it when it finally comes free.
 *   node stuck.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--parkx -100 --parky -100]
 *
 * The owner's thesis: the strobe is not the auction reshuffling, it is
 * gridlocks breaking — a travelling cell is boxed in by cells that have
 * already landed, sits pressed against them for a while, and when something
 * gives it is handed its new place in a few frames instead of travelling
 * there. This asks the file exactly that:
 *
 *   STUCK.  A body on a journey whose seed is more than LAG px from its own
 *           carrot and moving slower than SLOW px/s, for at least MIN frames
 *           in a row. Recorded with where it is: how far from the page edge,
 *           how far from the nearest landed wall, and whether the thing
 *           between it and its carrot is a wall, a hole, a free body, or the
 *           edge of the page.
 *   RELEASE. The WIN frames after a stuck run ends. The body's own area
 *           change, and the largest slide of any wall it shares, in px.
 *   THE TEST. Of every wall slide in the top decile, what share falls inside
 *           a release window, against the share of all pair-frames that do.
 *           A ratio near 1 says releases are nothing special; a ratio well
 *           above 1 says the strobe lives where the gridlocks break.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0), FRAMES = +opt('--frames', 330);
const PX = +opt('--parkx', -100), PY = +opt('--parky', -100);
const LAG = +opt('--lag', 30), SLOW = +opt('--slow', 40), MIN = +opt('--min', 3), WIN = +opt('--win', 5);

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const h = require('crypto').createHash('sha1').update(src + DT + JIT + PX + PY).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'stuck-' + h + '.html');
  fs.writeFileSync(dst, s.slice(0, i) + `\n window.__X = { fn: (n) => ({ root, ringArea, picture, W, H })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n` + s.slice(i));
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
  const X = window.__X, r = X.fn('root'), ra = X.fn('ringArea');
  X.setMouse(PX, PY);
  const W = X.fn('W'), H = X.fn('H');
  const L = [], marks = [];
  let n = 0;
  const step = () => {
    window.__advance(1); n++;
    const pic = X.fn('picture');
    const area = {};
    if (pic) for (const l of pic.leaves) { const id = l.path[0].body.id; let a = 0; for (const lp of l.loops) a += (lp.hole ? -1 : 1) * Math.abs(ra(lp)); area[id] = (area[id] || 0) + a; }
    const walls = r.walls.map(b => ({ id: b.id, r: b.wall.slice() }));
    const holes = r.holes.map(b => { let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; for (const pc of b.hole.pieces) for (const p of pc) { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); } return { id: b.id, r: [x0, y0, x1, y1] }; });
    const b = {};
    for (const bd of r.bodies) {
      if (bd.isSelf) continue;
      let cx = null, cy = null;
      if (bd.path && bd.journey) { const e = bd.progress, m = 1 - e, p = bd.path; cx = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex; cy = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey; }
      b[bd.id] = { x: bd.x, y: bd.y, vx: bd.vx, vy: bd.vy, cx, cy, cr: +bd.crystal.toFixed(4), w: !!bd.wall, h: !!bd.hole, v: !!bd.isVoid, lv: !!bd.leaving, j: !!bd.journey, a: area[bd.id] || 0 };
    }
    // the pairs and weights, for the walls between cells
    const w = {}, nb = {};
    if (r.solvedSubs && r.solved) r.solvedSubs.forEach((sb, k) => {
      const id = sb.body.id; w[id] = r.solved.weights[k];
      const c = r.solved.diagram.cells[k], seen = {};
      const scan = (pc) => { if (!pc || !pc.labs) return; for (const l of pc.labs) if (l >= 0 && r.solvedSubs[l]) seen[r.solvedSubs[l].body.id] = 1; };
      scan(c); if (c && c.pieces) for (const pc of c.pieces) scan(pc);
      nb[id] = Object.keys(seen).map(Number);
    });
    L.push({ f: n, b, w, nb, walls, holes });
  };
  for (let i = 0; i < 120; i++) step();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    marks.push({ f: n, scene: sc });
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    for (let i = 0; i < FRAMES; i++) step();
  }
  return { L, marks, W, H };
};

function metrics({ L, marks, W, H }) {
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  const dtS = DT / 1000;
  const rectDist = (x, y, r) => { const dx = Math.max(r[0] - x, 0, x - r[2]), dy = Math.max(r[1] - y, 0, y - r[3]); return Math.hypot(dx, dy); };
  // what stands between a point and its carrot: walk the segment and report the first thing it enters
  const blocker = (F, x, y, cx, cy, self) => {
    const n = 20;
    for (let k = 1; k <= n; k++) {
      const t = k / n, px = x + (cx - x) * t, py = y + (cy - y) * t;
      if (px < 0 || px > W || py < 0 || py > H) return 'edge';
      for (const wl of F.walls) if (wl.id !== self && px >= wl.r[0] && px <= wl.r[2] && py >= wl.r[1] && py <= wl.r[3]) return 'wall';
      for (const hl of F.holes) if (hl.id !== self && px >= hl.r[0] && px <= hl.r[2] && py >= hl.r[1] && py <= hl.r[3]) return 'hole';
    }
    // nothing landed in the way: a free body within 40 px of the line is the blocker
    for (const id in F.b) { if (+id === self) continue; const q = F.b[id]; if (q.w || q.h || q.v) continue;
      const ex = cx - x, ey = cy - y, L2 = ex * ex + ey * ey || 1; let t = ((q.x - x) * ex + (q.y - y) * ey) / L2; t = Math.max(0, Math.min(1, t));
      if (Math.hypot(q.x - (x + ex * t), q.y - (y + ey * t)) < 40) return 'free'; }
    return 'none';
  };
  // --- stuck runs
  const runs = [];
  const ids = new Set(); for (const F of L) for (const id in F.b) ids.add(+id);
  for (const id of ids) {
    let run = null;
    for (let k = 0; k < L.length; k++) {
      const F = L[k], b = F.b[id];
      const travelling = b && b.j && b.cx !== null && !b.v && !b.lv && b.cr < 0.999;
      const lag = travelling ? Math.hypot(b.cx - b.x, b.cy - b.y) : 0;
      const speed = b ? Math.hypot(b.vx, b.vy) : 0;
      const stuck = travelling && lag > LAG && speed < SLOW;
      if (stuck) {
        if (!run) run = { id, f0: F.f, frames: 0, lagSum: 0, x: b.x, y: b.y, scene: sceneOf(F.f), edge: Math.min(b.x, b.y, W - b.x, H - b.y), wallD: Infinity, blocker: blocker(F, b.x, b.y, b.cx, b.cy, id), cr: b.cr, a0: b.a };
        run.frames++; run.lagSum += lag;
        for (const wl of F.walls) if (wl.id !== id) run.wallD = Math.min(run.wallD, rectDist(b.x, b.y, wl.r));
      } else if (run) {
        if (run.frames >= MIN) { run.f1 = L[k - 1].f; run.lag = +(run.lagSum / run.frames).toFixed(1); delete run.lagSum; runs.push(run); }
        run = null;
      }
    }
    if (run && run.frames >= MIN) { run.f1 = L[L.length - 1].f; run.lag = +(run.lagSum / run.frames).toFixed(1); delete run.lagSum; runs.push(run); }
  }
  // --- releases: the WIN frames after each run, and the release windows by frame
  const windows = new Set(); // 'f:id'
  for (const run of runs) {
    const k1 = L.findIndex(F => F.f === run.f1);
    let maxDa = 0, maxSlide = 0;
    for (let k = k1 + 1; k <= Math.min(L.length - 1, k1 + WIN); k++) {
      const F = L[k], P = L[k - 1], b = F.b[run.id], p = P.b[run.id];
      windows.add(F.f + ':' + run.id);
      if (b && p && p.a > 2000) maxDa = Math.max(maxDa, Math.abs(b.a - p.a) / p.a);
      if (F.nb[run.id]) for (const j of F.nb[run.id]) {
        if (!(run.id in P.w) || !(j in P.w) || !(j in F.w)) continue;
        const d = Math.hypot(F.b[run.id].x - F.b[j].x, F.b[run.id].y - F.b[j].y); if (!(d > 1)) continue;
        maxSlide = Math.max(maxSlide, Math.abs((F.w[run.id] - F.w[j]) - (P.w[run.id] - P.w[j])) / (2 * d));
      }
    }
    run.releaseDa = +maxDa.toFixed(3); run.releaseSlidePx = +maxSlide.toFixed(1);
    run.wallD = run.wallD === Infinity ? null : +run.wallD.toFixed(1); run.edge = +run.edge.toFixed(1);
    run.x = Math.round(run.x); run.y = Math.round(run.y);
  }
  // --- the test: top-decile wall slides vs release windows, transitions only
  const slides = [];
  for (let k = 1; k < L.length; k++) {
    const F = L[k], P = L[k - 1], sc = sceneOf(F.f);
    if (sc === 'flock0' || sc === 'bento') continue;
    const done = {};
    for (const id in F.nb) for (const j of F.nb[id]) {
      if (j == id || !(id in P.w) || !(j in P.w) || !(j in F.w)) continue;
      const key = Math.min(id, j) + '-' + Math.max(id, j); if (done[key]) continue; done[key] = 1;
      const d = Math.hypot(F.b[id].x - F.b[j].x, F.b[id].y - F.b[j].y); if (!(d > 1)) continue;
      const dec = Math.abs((F.w[id] - F.w[j]) - (P.w[id] - P.w[j])) / (2 * d);
      const inWin = windows.has(F.f + ':' + id) || windows.has(F.f + ':' + j);
      // also: is either member stuck RIGHT NOW (a wall moving while its owner is boxed in)
      slides.push({ dec, inWin, scene: sc });
    }
  }
  slides.sort((a, b) => a.dec - b.dec);
  const top = slides.slice(Math.floor(slides.length * 0.9));
  const share = (arr) => arr.length ? arr.filter(s => s.inWin).length / arr.length : 0;
  const byScene = {};
  for (const run of runs) { const S = byScene[run.scene] = byScene[run.scene] || { runs: 0, frames: 0, blockers: {}, atEdge: 0, atWall: 0 }; S.runs++; S.frames += run.frames; S.blockers[run.blocker] = (S.blockers[run.blocker] || 0) + 1; if (run.edge < 25) S.atEdge++; if (run.wallD !== null && run.wallD < 8) S.atWall++; }
  const blockers = {}; for (const run of runs) blockers[run.blocker] = (blockers[run.blocker] || 0) + 1;
  return {
    clock: { dtMs: +DT.toFixed(3), jitterMs: JIT }, pointer: [PX, PY], thresholds: { lagPx: LAG, slowPxPerS: SLOW, minFrames: MIN, releaseWin: WIN },
    stuckRuns: runs.length, stuckBodyFrames: runs.reduce((s, r) => s + r.frames, 0),
    blockers,
    pressedAgainstWall: runs.filter(r => r.wallD !== null && r.wallD < 8).length,
    withinEdge25: runs.filter(r => r.edge < 25).length,
    // THE TEST
    topDecileSlidesInRelease: +share(top).toFixed(3), allSlidesInRelease: +share(slides).toFixed(3),
    releaseEnrichment: share(slides) > 0 ? +(share(top) / share(slides)).toFixed(2) : null,
    meanReleaseSlidePx: +(runs.length ? runs.reduce((s, r) => s + r.releaseSlidePx, 0) / runs.length : 0).toFixed(1),
    meanReleaseDa: +(runs.length ? runs.reduce((s, r) => s + r.releaseDa, 0) / runs.length : 0).toFixed(3),
    byScene,
    worstRuns: runs.slice().sort((a, b) => b.releaseSlidePx - a.releaseSlidePx).slice(0, 14),
    longestRuns: runs.slice().sort((a, b) => b.frames - a.frames).slice(0, 8),
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
  const { worstRuns, longestRuns, ...head } = m;
  console.log(JSON.stringify(head, null, 1));
  console.log('worst releases (the wall that slid furthest when a stuck body came free):');
  for (const r of worstRuns) console.log('  ' + JSON.stringify(r));
  console.log('longest runs:');
  for (const r of longestRuns) console.log('  ' + JSON.stringify(r));
})().catch(e => { console.error(e); process.exit(1); });
