/* What a moving pointer costs during a transition.
 *   node hoverprobe.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--park]
 * Every other harness parks the pointer at one spot for the whole run, so
 * nothing measures the thing the owner described: the cursor sitting over a
 * page that is rearranging under it, acquiring and losing cells frame by frame
 * while they fly past. This drives the SAME deterministic scenario as score.js
 * and sweeps the pointer across the canvas during each scene change (a fixed
 * lissajous path, so it is deterministic and covers the middle where the cells
 * are). --park reruns the identical scenario with the pointer held still, so
 * the DIFFERENCE is the cost of live hover during a change.
 *
 * Reports, on top of the usual jump counts:
 *   switches    how many times the hovered body changed (per scene, and total)
 *   churn       px2 of hover-shard area appearing or vanishing per frame,
 *               summed — a shard that grows and dies as the pointer crosses a
 *               flying cell is the visible cost
 *   acquired    hover acquisitions that happened while ANY body was mid-flight
 *               (crystal strictly between 0 and 1) — the ones idea A would
 *               refuse
 *   boostChurn  the same for the claim boost a hovered cell asks for, which is
 *               what actually reaches the auction
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0);
const FRAMES = +opt('--frames', 330), PARK = argv.includes('--park');
const PX = +opt('--parkx', 700), PY = +opt('--parky', 400);
const NAMES = ['root', 'ringArea', 'picture', 'W', 'H'];

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const exp = `\n window.__X = { fn: (n) => ({${NAMES.map(n => `${n}: typeof ${n} !== 'undefined' ? ${n} : undefined`).join(', ')}})[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const h = require('crypto').createHash('sha1').update(src).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'hoverprobe-' + h + '.html');
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

const RUN = ({ FRAMES, PARK, PX, PY }) => {
  const X = window.__X, r = X.fn('root'), ra = X.fn('ringArea');
  const W = X.fn('W'), H = X.fn('H');
  const frames = [], marks = [];
  let n = 0;
  // a deterministic sweep across the middle of the canvas: slow enough that
  // the pointer rests on a cell for several frames, fast enough to cross a
  // few during one change
  const at = (k) => [W * (0.5 + 0.32 * Math.sin(k * 0.031)), H * (0.5 + 0.30 * Math.sin(k * 0.047 + 1.1))];
  const step = () => {
    if (!PARK) { const [mx, my] = at(n); X.setMouse(mx, my); } else X.setMouse(PX, PY);
    window.__advance(1);
    const pic = X.fn('picture');
    const rec = { f: n++, a: {}, st: {}, hov: -1, shard: 0, boost: 0 };
    if (pic) for (const l of pic.leaves) {
      const rb = l.path[0].body; let a = 0;
      for (const lp of l.loops) a += (lp.hole ? -1 : 1) * Math.abs(ra(lp));
      rec.a[rb.id] = (rec.a[rb.id] || 0) + a;
    }
    // the hovered body, the shard it carries, and the boost that reaches the auction
    r.walk ? r.walk(h => { if (h.depth === 0) rec.hov = h.hoveredId; }) : (rec.hov = r.hoveredId);
    for (const sh of (r.shards || [])) rec.shard += Math.abs(sh.beyond || 0);
    for (const b of r.bodies) {
      if (b.isSelf) continue;
      rec.st[b.id] = { cr: +b.crystal.toFixed(4), hm: +(b.hoverMix || 0).toFixed(4), w: !!b.wall, h: !!b.hole, v: !!b.isVoid, lv: !!b.leaving };
      rec.boost += (b.hoverMix || 0) * (b.claim || 0);
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
  const anyFlying = (F) => { for (const id in F.st) { const b = F.st[id]; if (!b.v && !b.lv && b.cr > 0.001 && b.cr < 0.999) return true; } return false; };
  let switches = 0, acquired = 0, churn = 0, boostChurn = 0, jumps = 0, shock = 0;
  const perScene = {};
  for (let k = 1; k < frames.length; k++) {
    const F = frames[k], P = frames[k - 1], sc = sceneOf(F.f);
    const S = perScene[sc] = perScene[sc] || { switches: 0, acquired: 0, churn: 0, jumps: 0 };
    if (F.hov !== P.hov) { switches++; S.switches++; if (F.hov >= 0 && anyFlying(F)) { acquired++; S.acquired++; } }
    churn += Math.abs(F.shard - P.shard); S.churn += Math.abs(F.shard - P.shard);
    boostChurn += Math.abs(F.boost - P.boost);
    for (const id in F.a) {
      const a = F.a[id], q = P.a[id]; if (q === undefined) continue;
      const s = F.st[id]; if (!s || s.v || s.lv) continue;
      const d = Math.abs(a - q);
      if (d > 4000 && d / Math.max(a, q) > 0.12) { jumps++; shock += d; S.jumps++; }
    }
  }
  return {
    frames: frames.length, clock: { dtMs: DT, jitterMs: JIT }, pointer: PARK ? ('parked ' + PX + ',' + PY) : 'sweeping',
    hoverSwitches: switches, acquiredMidFlight: acquired,
    shardChurnPx2: Math.round(churn), boostChurn: +boostChurn.toFixed(1),
    jumps, shockPx2: Math.round(shock),
    scenes: Object.fromEntries(Object.entries(perScene).map(([k, v]) => [k, { switches: v.switches, acquired: v.acquired, churn: Math.round(v.churn), jumps: v.jumps }])),
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
  const data = await p.evaluate(RUN, { FRAMES, PARK, PX, PY });
  await b.close();
  const m = metrics(data); m.pageErrors = errs.length;
  if (OUT) fs.writeFileSync(OUT, JSON.stringify(m, null, 1));
  console.log(JSON.stringify(m));
})().catch(e => { console.error(e); process.exit(1); });
