/* Flicker scorecard: how much of a transition's motion is FIGHTING.
 *   node flicker.js <path-to-hive.html> [out.json] [--frames N] [--dump frames.json]
 * Same fixed-step clock and scenario as score.js (deterministic: two runs of
 * one file agree frame for frame). Where score.js counts jumps above 12% of a
 * cell in one frame, this measures the motion BELOW that threshold: the
 * frame-by-frame reversals, the motion that is undone, the seeds that fight
 * their own path, the auction's residual pressure, and how long a scene takes
 * to go quiet after its last switch.
 *
 * Per body per frame it records: painted area, painted centroid, seed
 * position, seed velocity, the carrot on its path (where the journey says it
 * should be), crystal and state. From those:
 *   waste      1 - |net displacement over a window| / sum of per-frame steps,
 *              averaged over bodies and 6-frame windows, for the painted
 *              centroid (wasteC) and the painted area (wasteA). 0 = every step
 *              in one direction, 1 = pure oscillation.
 *   reversals  body-frames where a step is opposite in sign to the previous
 *              step (area, and centroid along its own previous step), as a
 *              share of moving body-frames.
 *   fight      the seed's velocity against the carrot's direction: share of
 *              moving body-frames where the seed moves away from its carrot,
 *              and the mean distance seed-to-carrot while travelling.
 *   pressure   the auction's residual: mean and p95 of maxRelErr over frames
 *              with a solve, and the share of frames above 1%.
 *   settle     frames from a scene's last state switch (wall/hole/free change)
 *              to the frame after which no body moves more than 0.5 px or 0.5%
 *              of area; per scene and summed.
 * Voids are excluded from waste/reversals/fight (they are crushed by design)
 * but counted separately.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const FRAMES = +opt('--frames', 330), DUMP = opt('--dump', null);
// the clock: --dt <ms> fixed step (default 1000/60); --jitter <ms> adds a
// deterministic pseudo-random +-jitter to every step (an LCG, so two runs still
// agree), because the page is watched at real, uneven frame times and a fight
// can hide at a steady 60 fps
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0);
const NAMES = ['root', 'ringArea', 'picture', 'W', 'H'];

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({${NAMES.map(n => `${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`).join(', ')}})[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'flicker-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
  fs.writeFileSync(dst, s.slice(0, i) + exp + s.slice(i));
  return dst;
}

const CLOCK = `(() => {
  let t = 0, seed = 12345; const q = []; const realNow = performance.now.bind(performance);
  const DT = ${DT}, JIT = ${JIT};
  const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
  window.__realNow = realNow;
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => {};
  performance.now = () => t;
  window.__advance = (n) => { for (let i = 0; i < n; i++) { t += DT + (JIT ? (2 * rnd() - 1) * JIT : 0); const cbs = q.splice(0); for (const cb of cbs) cb(t); } };
})();`;

const RUN = (FRAMES) => {
  const X = window.__X, r = X.fn('root'), ra = X.fn('ringArea');
  X.setMouse(700, 400);
  const frames = [], marks = [];
  let n = 0;
  const cen = (lp) => { let x = 0, y = 0, a = 0; const m = lp.length; for (let k = 0; k < m; k++) { const p = lp[k], q = lp[(k + 1) % m]; const c = p[0] * q[1] - q[0] * p[1]; x += (p[0] + q[0]) * c; y += (p[1] + q[1]) * c; a += c; } return a ? [x / (3 * a), y / (3 * a), a / 2] : [lp[0][0], lp[0][1], 0]; };
  // the shape itself, on a 4 px raster: a mask per body per frame, kept for
  // three frames, so a shape that flips and flips back is caught even when
  // its area and centroid never move. sd = px² changed since last frame;
  // back = px² that changed and changed back across three frames.
  const CELL = 4, GW = Math.ceil(X.fn('W') / CELL), GH = Math.ceil(X.fn('H') / CELL);
  const masks = {};   // id -> [m(t-2), m(t-1), m(t)] as Uint8Array
  const fillLoop = (m, lp, val) => {
    let y0 = Infinity, y1 = -Infinity; for (const q of lp) { y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }
    const r0 = Math.max(0, Math.floor(y0 / CELL)), r1 = Math.min(GH - 1, Math.floor(y1 / CELL));
    const L = lp.length;
    for (let row = r0; row <= r1; row++) {
      const sy = (row + 0.5) * CELL; const xs = [];
      for (let k = 0; k < L; k++) { const a = lp[k], b = lp[(k + 1) % L]; if ((a[1] <= sy) !== (b[1] <= sy)) xs.push(a[0] + (sy - a[1]) * (b[0] - a[0]) / (b[1] - a[1])); }
      xs.sort((u, v) => u - v);
      for (let k = 0; k + 1 < xs.length; k += 2) { const c0 = Math.max(0, Math.round(xs[k] / CELL)), c1 = Math.min(GW, Math.round(xs[k + 1] / CELL)); for (let c = c0; c < c1; c++) m[row * GW + c] = val; }
    }
  };
  const step = () => {
    window.__advance(1);
    const pic = X.fn('picture');
    const rec = { f: n++, b: {}, err: r.solved ? +r.solved.maxRelErr.toExponential(3) : null, sh: r.shadowOn ? 1 : 0 };
    const acc = {};
    const loopsOf = {};
    if (pic) for (const l of pic.leaves) {
      const rb = l.path[0].body; const A = acc[rb.id] = acc[rb.id] || { a: 0, mx: 0, my: 0 };
      (loopsOf[rb.id] = loopsOf[rb.id] || []).push(...l.loops);
      for (const lp of l.loops) { const [cx, cy, sa] = cen(lp); const w = (lp.hole ? -1 : 1) * Math.abs(sa); A.a += w; A.mx += cx * w; A.my += cy * w; }
    }
    const shape = {};
    for (const id in loopsOf) {
      const m = new Uint8Array(GW * GH);
      for (const lp of loopsOf[id]) if (!lp.hole) fillLoop(m, lp, 1);
      for (const lp of loopsOf[id]) if (lp.hole) fillLoop(m, lp, 0);
      const hist = masks[id] = (masks[id] || []).concat([m]).slice(-3);
      let sd = 0, back = 0;
      if (hist.length >= 2) { const p = hist[hist.length - 2]; for (let i = 0; i < m.length; i++) if (m[i] !== p[i]) sd++; }
      if (hist.length === 3) { const pp = hist[0], p = hist[1]; for (let i = 0; i < m.length; i++) if (p[i] !== pp[i] && m[i] === pp[i]) back++; }
      shape[id] = [sd * CELL * CELL, back * CELL * CELL];
    }
    for (const bd of r.bodies) {
      if (bd.isSelf) continue;
      const A = acc[bd.id];
      let car = null;
      if (bd.path && bd.progress !== undefined) { const e = bd.progress, m = 1 - e, p = bd.path; car = [+(m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex).toFixed(2), +(m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey).toFixed(2)]; }
      const sh = shape[bd.id] || [0, 0];
      // sliver: perimeter² / (4π area) of the painted shape, 1 for a disc,
      // far above 1 for a cell squeezed thin between crowded seeds
      let per = 0, ar = 0; if (loopsOf[bd.id]) for (const lp of loopsOf[bd.id]) { if (lp.hole) continue; for (let k = 0; k < lp.length; k++) { const p0 = lp[k], p1 = lp[(k + 1) % lp.length]; per += Math.hypot(p1[0] - p0[0], p1[1] - p0[1]); } ar += Math.abs(ra(lp)); }
      const sliver = ar > 100 ? +(per * per / (4 * Math.PI * ar)).toFixed(2) : null;
      rec.b[bd.id] = { sd: sh[0], back: sh[1], sliver, a: A ? Math.round(A.a) : 0, cx: A && A.a ? +(A.mx / A.a).toFixed(2) : null, cy: A && A.a ? +(A.my / A.a).toFixed(2) : null,
        x: +bd.x.toFixed(2), y: +bd.y.toFixed(2), vx: +(bd.vx || 0).toFixed(2), vy: +(bd.vy || 0).toFixed(2), car,
        cr: +bd.crystal.toFixed(4), st: bd.wall ? 'W' : bd.hole ? 'H' : 'F', v: !!bd.isVoid, lv: !!bd.leaving, j: !!bd.journey };
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
  const ids = new Set(); for (const F of frames) for (const id in F.b) ids.add(id);
  const sceneOf = (f) => { let s = 'flock0', i = -1; marks.forEach((m, k) => { if (f >= m.f) { s = m.scene; i = k; } }); return [s, i]; };
  const W = 6;
  let wasteC = 0, wasteA = 0, wn = 0, revA = 0, revC = 0, moving = 0, fightN = 0, fightSum = 0, travel = 0, seedRev = 0;
  const perScene = {};
  const touch = (s) => perScene[s] = perScene[s] || { wasteC: 0, wasteA: 0, wn: 0, revA: 0, revC: 0, moving: 0, fight: 0, travel: 0, settle: null };
  for (const id of ids) {
    let pdx = 0, pdy = 0, pda = 0, pvx = 0, pvy = 0;
    for (let k = 1; k < frames.length; k++) {
      const b = frames[k].b[id], p = frames[k - 1].b[id];
      if (!b || !p || b.v || b.lv || b.cx === null || p.cx === null) { pdx = pdy = pda = 0; continue; }
      const [sc] = sceneOf(frames[k].f); const S = touch(sc);
      const dx = b.cx - p.cx, dy = b.cy - p.cy, da = b.a - p.a;
      const stepL = Math.hypot(dx, dy);
      const isMoving = stepL > 0.25 || Math.abs(da) > 0.002 * Math.max(1, p.a);
      if (isMoving) {
        moving++; S.moving++;
        if (da * pda < 0 && Math.abs(da) > 0.002 * p.a && Math.abs(pda) > 0.002 * p.a) { revA++; S.revA++; }
        if ((dx * pdx + dy * pdy) < 0 && stepL > 0.25 && Math.hypot(pdx, pdy) > 0.25) { revC++; S.revC++; }
      }
      // seed against its carrot
      if (b.j && b.car && p.car) {
        const tx = b.car[0] - b.x, ty = b.car[1] - b.y, tl = Math.hypot(tx, ty);
        const sv = Math.hypot(b.vx, b.vy);
        if (sv > 5 && tl > 1) { travel++; S.travel++; fightSum += tl; if ((b.vx * tx + b.vy * ty) / (sv * tl) < -0.2) { fightN++; S.fight++; } }
        if ((b.vx * pvx + b.vy * pvy) < 0 && sv > 5 && Math.hypot(pvx, pvy) > 5) seedRev++;
      }
      pdx = dx; pdy = dy; pda = da; pvx = b.vx; pvy = b.vy;
      // windowed waste
      if (k >= W && k % 3 === 0) {
        let sumC = 0, sumA = 0, ok = true;
        for (let j = k - W + 1; j <= k; j++) { const q = frames[j].b[id], o = frames[j - 1].b[id]; if (!q || !o || q.cx === null || o.cx === null || q.v) { ok = false; break; } sumC += Math.hypot(q.cx - o.cx, q.cy - o.cy); sumA += Math.abs(q.a - o.a); }
        if (!ok) continue;
        const q0 = frames[k - W].b[id], q1 = frames[k].b[id];
        const netC = Math.hypot(q1.cx - q0.cx, q1.cy - q0.cy), netA = Math.abs(q1.a - q0.a);
        if (sumC > 1.5) { wasteC += 1 - netC / sumC; S.wasteC += 1 - netC / sumC; }
        if (sumA > 0.01 * q0.a) { wasteA += 1 - netA / sumA; S.wasteA += 1 - netA / sumA; }
        if (sumC > 1.5 || sumA > 0.01 * q0.a) { wn++; S.wn++; }
      }
    }
  }
  // shape: motion undone. back(t) is what changed at t-1 and changed back at
  // t, so it is counted against the motion of frame t-1; the share of all
  // shape motion that was a flip is the number to watch.
  let sdSum = 0, backSum = 0; const byBody = {}, sceneShape = {};
  for (let k = 1; k < frames.length; k++) {
    const [sc] = sceneOf(frames[k].f); const S = sceneShape[sc] = sceneShape[sc] || { sd: 0, back: 0, flips: 0 };
    for (const id in frames[k].b) { const b = frames[k].b[id]; if (b.v || b.lv) continue; sdSum += b.sd; backSum += b.back; S.sd += b.sd; S.back += b.back; const B = byBody[id] = byBody[id] || { sd: 0, back: 0, flips: 0 }; B.sd += b.sd; B.back += b.back; const prev = frames[k - 1].b[id]; if (prev && b.back > 64 && b.back > 0.5 * prev.sd) { B.flips++; S.flips++; } }
  }
  const worstBodies = Object.entries(byBody).sort((u, v) => v[1].back - u[1].back).slice(0, 5).map(([id, B]) => ({ id: +id, back: Math.round(B.back), sd: Math.round(B.sd), flips: B.flips }));
  // sliver: over non-void bodies while anything moves
  const sl = []; for (let k = 1; k < frames.length; k++) for (const id in frames[k].b) { const b = frames[k].b[id]; if (b.v || b.lv || b.sliver === null || b.st === 'W') continue; sl.push(b.sliver); }
  sl.sort((a, b) => a - b);
  // pressure
  const errs = frames.map(f => f.err).filter(e => e !== null && isFinite(e)).sort((a, b) => a - b);
  const pct = (arr, p) => arr.length ? arr[Math.min(arr.length - 1, Math.floor(p * (arr.length - 1)))] : 0;
  const errMean = errs.length ? errs.reduce((s, e) => s + e, 0) / errs.length : 0;
  // settle per scene: last state switch -> first frame after which nothing moves
  marks.forEach((m, i) => {
    const end = (marks[i + 1] ? marks[i + 1].f : frames.length) - 1;
    let lastSwitch = m.f;
    for (let k = m.f + 1; k <= end; k++) for (const id in frames[k].b) { const b = frames[k].b[id], p = frames[k - 1].b[id]; if (p && b.st !== p.st) lastSwitch = k; }
    let quiet = end + 1;
    for (let k = end; k > lastSwitch; k--) {
      let movesHere = false;
      for (const id in frames[k].b) { const b = frames[k].b[id], p = frames[k - 1].b[id]; if (!p || b.v || b.cx === null || p.cx === null) continue; if (Math.hypot(b.cx - p.cx, b.cy - p.cy) > 0.5 || Math.abs(b.a - p.a) > 0.005 * Math.max(1, p.a)) { movesHere = true; break; } }
      if (movesHere) { quiet = k + 1; break; }
      if (k === lastSwitch + 1) quiet = lastSwitch + 1;
    }
    touch(m.scene).settle = quiet - lastSwitch;
    touch(m.scene).lastSwitch = lastSwitch - m.f;
  });
  const out = {
    frames: frames.length,
    shapeMotionPx2: Math.round(sdSum), shapeBackPx2: Math.round(backSum), shapeBackShare: +(sdSum ? backSum / sdSum : 0).toFixed(3),
    flipFrames: Object.values(byBody).reduce((s, B) => s + B.flips, 0), worstBodies,
    sliverMean: +(sl.length ? sl.reduce((a, b) => a + b, 0) / sl.length : 0).toFixed(2), sliverP95: sl.length ? sl[Math.floor(0.95 * (sl.length - 1))] : 0,
    clock: { dtMs: DT, jitterMs: JIT },
    wasteC: +(wn ? wasteC / wn : 0).toFixed(3), wasteA: +(wn ? wasteA / wn : 0).toFixed(3), windows: wn,
    revA: +(moving ? revA / moving : 0).toFixed(3), revC: +(moving ? revC / moving : 0).toFixed(3), movingBodyFrames: moving,
    fight: +(travel ? fightN / travel : 0).toFixed(3), lag: +(travel ? fightSum / travel : 0).toFixed(1), travelBodyFrames: travel, seedReversals: seedRev,
    pressureMean: +errMean.toExponential(2), pressureP95: +pct(errs, 0.95).toExponential(2), pressureOver1pct: +(errs.length ? errs.filter(e => e > 0.01).length / errs.length : 0).toFixed(3),
    settleTotal: Object.values(perScene).reduce((s, S) => s + (S.settle || 0), 0),
    scenes: {},
  };
  for (const s in perScene) { const S = perScene[s]; const SS = sceneShape[s] || { sd: 0, back: 0, flips: 0 }; out.scenes[s] = { shapeBackShare: +(SS.sd ? SS.back / SS.sd : 0).toFixed(3), shapeBackPx2: Math.round(SS.back), flipFrames: SS.flips, wasteC: +(S.wn ? S.wasteC / S.wn : 0).toFixed(3), wasteA: +(S.wn ? S.wasteA / S.wn : 0).toFixed(3), revA: +(S.moving ? S.revA / S.moving : 0).toFixed(3), revC: +(S.moving ? S.revC / S.moving : 0).toFixed(3), fight: +(S.travel ? S.fight / S.travel : 0).toFixed(3), lastSwitch: S.lastSwitch, settle: S.settle }; }
  return out;
}

(async () => {
  const dst = instrument(SRC);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.addInitScript(CLOCK);
  const errs = []; p.on('pageerror', e => errs.push(String(e.message || e)));
  await p.goto('file://' + dst);
  await p.waitForTimeout(300);
  const data = await p.evaluate(RUN, FRAMES);
  await b.close();
  if (DUMP) fs.writeFileSync(DUMP, JSON.stringify(data));
  const m = metrics(data); m.pageErrors = errs.length; if (errs.length) m.pageErrorSample = errs.slice(0, 3);
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  console.log(JSON.stringify(m));
})().catch(e => { console.error(e); process.exit(1); });
