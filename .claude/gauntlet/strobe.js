/* THE STROBE: a cell that arrives somewhere without travelling there, and a
 * cell that reaches somewhere it has no business being.
 *   node strobe.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--dump f.json]
 *
 * The existing harness measures AREA per frame (score.js: a cell that changes
 * more than 12% of itself) and MOTION UNDONE (flicker.js: shape that changed
 * and changed back). Neither catches the two things the owner is describing:
 *
 *   TELEPORT. A cell whose painted shape is somewhere else this frame while
 *     its own seed barely moved. Its area can be identical, its centroid can
 *     even be identical, and every single frame looks correct — but the cell
 *     did not travel, it was re-decided. Measured as the symmetric difference
 *     between this frame's painted mask and last frame's, as a fraction of the
 *     cell, AGAINST what the seed's own motion could account for. A cell whose
 *     seed moved 2 px has no honest way to repaint 40% of itself.
 *   REACH. A cell with a piece far from its own seed: the wedge stretched
 *     across the page like chewing gum. Measured as the farthest painted point
 *     from the seed, in units of the cell's own equivalent radius, so a disc
 *     is 1 and a cell reaching four times its own size is 4. Reported with
 *     WHERE that far piece came from — the body's own cell, its hole's cut
 *     pieces, or ground it ADOPTED (holeExtra), which is the one that can be
 *     anywhere on the page.
 *
 * Same deterministic clock and scenario as the rest of the harness.
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
const PX = +opt('--parkx', 700), PY = +opt('--parky', 400);
const FRAMES = +opt('--frames', 330), DUMP = opt('--dump', null);
const NAMES = ['root', 'ringArea', 'picture', 'W', 'H'];

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({${NAMES.map(n => `${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`).join(', ')}})[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const h = require('crypto').createHash('sha1').update(src).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'strobe-' + h + '.html');
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
  const X = window.__X, r = X.fn('root'), ra = X.fn('ringArea');
  X.setMouse(PX, PY);
  const W = X.fn('W'), H = X.fn('H');
  const CELL = 4, GW = Math.ceil(W / CELL), GH = Math.ceil(H / CELL);
  const masks = {};
  const fillLoop = (m, lp, val) => {
    let y0 = Infinity, y1 = -Infinity; for (const q of lp) { y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }
    const r0 = Math.max(0, Math.floor(y0 / CELL)), r1 = Math.min(GH - 1, Math.floor(y1 / CELL)), L = lp.length;
    for (let row = r0; row <= r1; row++) {
      const sy = (row + 0.5) * CELL, xs = [];
      for (let k = 0; k < L; k++) { const a = lp[k], b = lp[(k + 1) % L]; if ((a[1] <= sy) !== (b[1] <= sy)) xs.push(a[0] + (sy - a[1]) * (b[0] - a[0]) / (b[1] - a[1])); }
      xs.sort((u, v) => u - v);
      for (let k = 0; k + 1 < xs.length; k += 2) { const c0 = Math.max(0, Math.round(xs[k] / CELL)), c1 = Math.min(GW, Math.round(xs[k + 1] / CELL)); for (let c = c0; c < c1; c++) m[row * GW + c] = val; }
    }
  };
  const frames = [], marks = [];
  let n = 0;
  const step = () => {
    window.__advance(1);
    const pic = X.fn('picture');
    const rec = { f: n++, b: {}, reach: [] };
    const loopsOf = {};
    if (pic) for (const l of pic.leaves) {
      const id = l.path[0].body.id; (loopsOf[id] = loopsOf[id] || []).push(...l.loops);
      // REACH is a leaf's own business, and a nested leaf is drawn in root px
      // while its body's seed is in its own hive's px: walk the path and add
      // each ancestor's offset, or the measure compares two different pages.
      let ox = 0, oy = 0;
      for (let k = 0; k + 1 < l.path.length; k++) { const h = l.path[k].body.hive; if (h) { ox += h.ox; oy += h.oy; } }
      const sx = l.body.x + ox, sy = l.body.y + oy;
      let a = 0, far = 0, farAt = null, nl = 0;
      for (const lp of l.loops) {
        const s = Math.abs(ra(lp)); a += lp.hole ? -s : s;
        if (lp.hole) continue; nl++;
        for (const q of lp) { const d = Math.hypot(q[0] - sx, q[1] - sy); if (d > far) { far = d; farAt = [Math.round(q[0]), Math.round(q[1])]; } }
      }
      if (a > 2000) rec.reach.push({ id: l.path.map(e => e.body.id).join('/'), depth: l.path.length,
        rr: +(far / Math.sqrt(a / Math.PI)).toFixed(1), farPx: +far.toFixed(0), aPx: Math.round(a), loops: nl,
        exA: l.body.holeExtra ? Math.round(l.body.holeExtra.reduce((t, pc) => t + Math.abs(ra(pc)), 0)) : 0,
        st: l.body.wall ? 'W' : l.body.hole ? 'H' : 'F', at: farAt });
    }
    for (const bd of r.bodies) {
      if (bd.isSelf) continue;
      const lps = loopsOf[bd.id] || [];
      // the mask, for the symmetric difference against last frame
      const m = new Uint8Array(GW * GH);
      for (const lp of lps) if (!lp.hole) fillLoop(m, lp, 1);
      for (const lp of lps) if (lp.hole) fillLoop(m, lp, 0);
      const prev = masks[bd.id];
      let sd = 0, area = 0;
      for (let i = 0; i < m.length; i++) { if (m[i]) area++; if (prev && m[i] !== prev[i]) sd++; }
      masks[bd.id] = m;
      rec.b[bd.id] = {
        x: +bd.x.toFixed(2), y: +bd.y.toFixed(2),
        aPx: area * CELL * CELL, sdPx: sd * CELL * CELL,
        cr: +bd.crystal.toFixed(4), w: !!bd.wall, h: !!bd.hole, v: !!bd.isVoid, lv: !!bd.leaving,
      };
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
  const tele = [], reach = [];
  let bodyFrames = 0, sdSum = 0, aSum = 0;
  for (let k = 1; k < frames.length; k++) {
    const F = frames[k], P = frames[k - 1];
    const [sc, sf] = sceneOf(F.f);
    for (const id in F.b) {
      const b = F.b[id], p = P.b[id];
      if (!p || b.v || b.lv || b.aPx < 2000) continue;
      bodyFrames++; sdSum += b.sdPx; aSum += b.aPx;
      const seedDx = Math.hypot(b.x - p.x, b.y - p.y);
      // How much of itself did it repaint, and how much could its own motion
      // explain? A cell of area A translating by d sweeps about perimeter*d;
      // for a roughly round cell that is ~2*sqrt(pi*A)*d. Anything past that
      // was not travel.
      const rEq = Math.sqrt(b.aPx / Math.PI);
      const explained = 2 * Math.PI * rEq * seedDx;
      const excess = b.sdPx - explained;
      if (b.sdPx > 0.25 * b.aPx && excess > 0.15 * b.aPx) {
        tele.push({ f: F.f, scene: sc, sf, id: +id, sdShare: +(b.sdPx / b.aPx).toFixed(2), seedDx: +seedDx.toFixed(1), aPx: b.aPx, excessShare: +(excess / b.aPx).toFixed(2), st: b.w ? 'W' : b.h ? 'H' : 'F', cr: b.cr });
      }
    }
    for (const q of (F.reach || [])) if (q.rr > 3.5) reach.push({ f: F.f, scene: sc, sf, ...q });
  }
  const byScene = {}; for (const t of tele) byScene[t.scene] = (byScene[t.scene] || 0) + 1;
  const reachScene = {}; for (const t of reach) reachScene[t.scene] = (reachScene[t.scene] || 0) + 1;
  const worstT = tele.slice().sort((a, b) => b.excessShare - a.excessShare).slice(0, 10);
  const worstR = reach.slice().sort((a, b) => b.rr - a.rr).slice(0, 10);
  return {
    frames: frames.length, clock: { dtMs: DT, jitterMs: JIT }, pointer: [PX, PY], bodyFrames,
    churnShareMean: +(sdSum / Math.max(1, aSum)).toFixed(4),
    teleports: tele.length, teleportByScene: byScene,
    reaches: reach.length, reachByScene: reachScene,
    reachNested: reach.filter(r => r.depth > 1).length, reachAdopting: reach.filter(r => r.exA > 0).length,
    worstTeleports: worstT, worstReaches: worstR,
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
  if (DUMP) fs.writeFileSync(DUMP, JSON.stringify(data));
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  const { worstTeleports, worstReaches, ...head } = m;
  console.log(JSON.stringify(head));
  console.log('worst teleports:'); for (const t of worstTeleports) console.log('  ' + JSON.stringify(t));
  console.log('worst reaches:'); for (const t of worstReaches) console.log('  ' + JSON.stringify(t));
})().catch(e => { console.error(e); process.exit(1); });
