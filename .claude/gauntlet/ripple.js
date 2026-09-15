/* THE RIPPLE: a membrane that is not straight where nothing bends it.
 *   node ripple.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--frames N] [--parkx X --parky Y]
 *
 * score.js reads areas, strobe.js reads what moved without travelling. Neither
 * reads the SHAPE of a cell's edge, and the owner's complaint about Astra II
 * was exactly that: a corrugated membrane, an edge with many small bends
 * where a straight seam should be. Two things are read off every root leaf of
 * every frame's picture, on its raw outline (before the garment rounds it):
 *
 *   BENDS. A vertex where the outline turns one way and, within 0.6 of a
 *     lattice pitch, turns back the other way: a zigzag tooth. A rectangle
 *     has none; a corrugated seam has one per tooth. Counted per body-frame,
 *     summed per scene, transition frames only (the cold settle excluded).
 *   TEETH. The bends whose step aside is 6 px or more — the ones the garment
 *     cannot round away — and DEPTH, the sum of every bend's step in px.
 *   CORRUGATIONS. Runs of three or more TEETH in a row along one edge: the
 *     periodic zigzag of two misaligned lattices, which is the complaint. An
 *     isolated step at a seam's end is a tooth but not a corrugation, and a
 *     wiggle under 6 px is neither.
 *   AXIS SHARE. The share of the outline's length that runs along an axis:
 *     100% for a page of rectangles, lower for organic cells. Not a score by
 *     itself (a liquid flock is legitimately low), but the number that says
 *     whether a "tile" transition keeps its tiles.
 *
 * Same deterministic clock and scenario as the rest of the harness. Nested
 * members are not read: a field's own auction is nesterr.js's business.
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
  const dst = path.join(os.tmpdir(), 'ripple-' + Buffer.from(src).toString('hex').slice(-24) + '.html');
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
  const step = () => {
    window.__advance(1);
    const pic = X.fn('picture');
    const rec = { f: n++, b: {} };
    const PW = r.PW, PH = r.PH;
    if (pic) for (const l of pic.leaves) {
      if (l.path.length !== 1 || l.isVoid) continue;
      const id = l.body.id;
      let bends = 0, teeth = 0, runs = 0, runLen = 0, depthSum = 0, axis = 0, total = 0, verts = 0;
      for (const lp of l.loops) {
        if (lp.hole) continue;
        const m = lp.length;
        if (m < 3) continue;
        verts += m;
        const turn = new Array(m), len = new Array(m);
        for (let k = 0; k < m; k++) {
          const a = lp[(k + m - 1) % m], b = lp[k], c = lp[(k + 1) % m];
          const ux = b[0] - a[0], uy = b[1] - a[1], vx = c[0] - b[0], vy = c[1] - b[1];
          const cr = ux * vy - uy * vx;
          turn[k] = Math.abs(cr) < 1e-6 ? 0 : (cr > 0 ? 1 : -1);
          const L = Math.hypot(vx, vy);
          len[k] = L; total += L;
          if (Math.min(Math.abs(vx), Math.abs(vy)) < 0.05 * Math.max(Math.abs(vx), Math.abs(vy))) axis += L;
        }
        const isBend = new Array(m).fill(false);
        for (let k = 0; k < m; k++) {
          const p = (k + 1) % m;
          if (turn[k] && turn[p] && turn[k] !== turn[p] && len[k] < 0.6 * Math.min(PW, PH)) {
            bends++;
            // the tooth's depth: how far the short edge steps aside from
            // the direction the outline had before it
            const a = lp[(k + m - 1) % m], b = lp[k], c = lp[p];
            const ux = b[0] - a[0], uy = b[1] - a[1], L = Math.hypot(ux, uy) || 1;
            const depth = Math.abs((ux * (c[1] - b[1]) - uy * (c[0] - b[0])) / L);
            depthSum += depth;
            if (depth >= 6) { teeth++; isBend[k] = true; }
          }
        }
        // a corrugation: three or more teeth in a row along one edge, the
        // periodic zigzag of two misaligned lattices; an isolated step is not
        let run = 0, first = -1;
        for (let k = 0; k < m; k++) if (!isBend[k]) { first = k; break; }
        if (first >= 0) for (let q = 1; q <= m; q++) {
          const k = (first + q) % m;
          if (isBend[k]) run++;
          else { if (run >= 3) { runs++; runLen += run; } run = 0; }
        } else { runs++; runLen += m; }
      }
      rec.b[id] = { bends, teeth, runs, runLen, depth: +depthSum.toFixed(1), axis: +(total > 0 ? axis / total : 1).toFixed(3), verts, len: Math.round(total) };
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
  const worst = [];
  for (const F of frames) {
    const [sc] = sceneOf(F.f);
    const o = byScene[sc] = byScene[sc] || { bodyFrames: 0, bends: 0, teeth: 0, runs: 0, runLen: 0, depth: 0, bendFrames: 0, axisSum: 0, vertsMax: 0 };
    for (const id in F.b) {
      const b = F.b[id];
      o.bodyFrames++; o.bends += b.bends; o.teeth += b.teeth; o.runs += b.runs; o.runLen += b.runLen; o.depth += b.depth; if (b.bends) o.bendFrames++; o.axisSum += b.axis; o.vertsMax = Math.max(o.vertsMax, b.verts);
      if (b.teeth >= 3 || b.runs) worst.push({ f: F.f, scene: sc, id: +id, bends: b.bends, teeth: b.teeth, runs: b.runs, runLen: b.runLen, depth: b.depth, verts: b.verts, axis: b.axis });
    }
  }
  const out = {};
  for (const sc in byScene) { const o = byScene[sc]; out[sc] = { bodyFrames: o.bodyFrames, bends: o.bends, teeth: o.teeth, corrugations: o.runs, corrugationTeeth: o.runLen, depthPx: Math.round(o.depth), bendsPerBodyFrame: +(o.bends / Math.max(1, o.bodyFrames)).toFixed(3), bendFrames: o.bendFrames, axisShareMean: +(o.axisSum / Math.max(1, o.bodyFrames)).toFixed(3), vertsMax: o.vertsMax }; }
  const sum = (k) => ['hero', 'sidebar', 'frame'].reduce((a, sc) => a + (byScene[sc] ? byScene[sc][k] : 0), 0);
  return { frames: frames.length, clock: { dtMs: DT, jitterMs: JIT }, pointer: [PX, PY], transitionBends: sum('bends'), transitionTeeth: sum('teeth'), transitionCorrugations: sum('runs'), transitionCorrugationTeeth: sum('runLen'), transitionDepthPx: Math.round(sum('depth')), byScene: out, worst: worst.sort((a, b) => b.runLen - a.runLen || b.teeth - a.teeth).slice(0, 12) };
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
