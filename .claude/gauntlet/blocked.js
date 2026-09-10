/* THE GRIDLOCK, IN THE FORM THIS FILE CAN HAVE ONE.
 *   node blocked.js <hive.html> [out.json] [--dt 30] [--jitter 12] [--parkx -100 --parky -100]
 *
 * The seeds of this page arrive on time (stuck.js: no seed sits still away
 * from its carrot in any transition). What arrives late is the GROUND. A
 * travelling body is going to a slot in the new lattice, and that slot is
 * still under somebody else's wall until that body melts and leaves. Until
 * then the traveller's cell can only be made of whatever ground is left —
 * a wedge, a strip, a piece somewhere else — and the frame the wall goes
 * the ground opens and the cell is handed its slot in a stride instead of
 * travelling there. That is a gridlock: not a seed that cannot move, a
 * destination that is not free.
 *
 *   BLOCKED. A body with a journey and a slot, whose slot is more than HALF
 *            covered by other bodies' walls (exact, rect on rect) or holes
 *            (their drawn pieces' boxes), for MIN frames or more. Recorded
 *            with who is sitting on it, and whether that body is itself on a
 *            journey (just late) or seated for good (the slot was never going
 *            to be free).
 *   RELEASE. The WIN frames after the slot comes free: the body's own area
 *            change and the largest slide of any wall it shares.
 *   THE TEST. Of every wall slide in the top decile (transitions only), the
 *            share that falls in a release window, against the share of all
 *            pair-frames that do. Enrichment well above 1 means the strobe
 *            lives where gridlocks break.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const OUT = argv[1] && !argv[1].startsWith('--') ? argv[1] : null;
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0), FRAMES = +opt('--frames', 330);
const PX = +opt('--parkx', -100), PY = +opt('--parky', -100);
const COVER = +opt('--cover', 0.5), MIN = +opt('--min', 3), WIN = +opt('--win', 5);

function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  if (i < 0) throw new Error('IIFE close not found');
  const h = require('crypto').createHash('sha1').update(src + DT + JIT + PX + PY).digest('hex').slice(0, 16);
  const dst = path.join(os.tmpdir(), 'blocked-' + h + '.html');
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
  const L = [], marks = [];
  let n = 0;
  const step = () => {
    window.__advance(1); n++;
    const pic = X.fn('picture');
    const area = {};
    if (pic) for (const l of pic.leaves) { const id = l.path[0].body.id; let a = 0; for (const lp of l.loops) a += (lp.hole ? -1 : 1) * Math.abs(ra(lp)); area[id] = (area[id] || 0) + a; }
    const b = {};
    for (const bd of r.bodies) {
      if (bd.isSelf) continue;
      const dest = bd.rect ? [bd.rect[0] * r.PW, bd.rect[1] * r.PH, bd.rect[2] * r.PW, bd.rect[3] * r.PH] : null;
      let hbox = null;
      if (bd.hole) { let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; for (const pc of bd.hole.pieces) for (const p of pc) { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); } hbox = [x0, y0, x1, y1]; }
      b[bd.id] = { x: bd.x, y: bd.y, dest, wall: bd.wall ? bd.wall.slice() : null, hbox, cr: +bd.crystal.toFixed(4), j: !!bd.journey, v: !!bd.isVoid, lv: !!bd.leaving, a: area[bd.id] || 0, prog: +(bd.progress || 0).toFixed(3), edge: Math.min(bd.x, bd.y, r.W - bd.x, r.H - bd.y) };
    }
    const w = {}, nb = {};
    if (r.solvedSubs && r.solved) r.solvedSubs.forEach((sb, k) => {
      const id = sb.body.id; w[id] = r.solved.weights[k];
      const c = r.solved.diagram.cells[k], seen = {};
      const scan = (pc) => { if (!pc || !pc.labs) return; for (const l of pc.labs) if (l >= 0 && r.solvedSubs[l]) seen[r.solvedSubs[l].body.id] = 1; };
      scan(c); if (c && c.pieces) for (const pc of c.pieces) scan(pc);
      nb[id] = Object.keys(seen).map(Number);
    });
    L.push({ f: n, b, w, nb });
  };
  for (let i = 0; i < 120; i++) step();
  for (const sc of ['bento', 'hero', 'sidebar', 'frame', 'flock']) {
    marks.push({ f: n, scene: sc });
    document.querySelector('.scene-btn[data-scene="' + sc + '"]').click();
    for (let i = 0; i < FRAMES; i++) step();
  }
  return { L, marks };
};

function metrics({ L, marks }) {
  const sceneOf = (f) => { let s = 'flock0'; for (const m of marks) if (f >= m.f) s = m.scene; return s; };
  const inter = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
  const rarea = (a) => (a[2] - a[0]) * (a[3] - a[1]);
  // per body-frame: how much of its destination is under somebody else
  const cover = (F, id) => {
    const me = F.b[id]; if (!me || !me.dest) return null;
    const A = rarea(me.dest); if (!(A > 1)) return null;
    let byWall = 0, byHole = 0, who = null, whoA = 0, whoJ = false;
    for (const o in F.b) {
      if (+o === +id) continue; const q = F.b[o];
      let c = 0, kind = null;
      if (q.wall) { c = inter(me.dest, q.wall); kind = 'wall'; }
      else if (q.hbox) { c = inter(me.dest, q.hbox); kind = 'hole'; }
      if (c <= 0) continue;
      if (kind === 'wall') byWall += c; else byHole += c;
      if (c > whoA) { whoA = c; who = +o; whoJ = q.j; }
    }
    return { frac: Math.min(1, (byWall + byHole) / A), wallFrac: byWall / A, holeFrac: byHole / A, who, whoJ };
  };
  const runs = [], windows = new Set(), blockedNow = new Set();   // 'f:id' while blocked
  const churnBlocked = [], churnFree = [];                            // |dA|/A per body-frame, travelling bodies
  const ids = new Set(); for (const F of L) for (const id in F.b) ids.add(+id);
  for (const id of ids) {
    let run = null;
    for (let k = 0; k < L.length; k++) {
      const F = L[k], b = F.b[id];
      const travelling = b && b.j && b.dest && !b.v && !b.lv && b.cr < 0.999;
      const cv = travelling ? cover(F, id) : null;
      const blocked = cv && cv.frac > COVER;
      if (travelling && k > 0 && L[k - 1].b[id] && L[k - 1].b[id].a > 2000) {
        const ch = Math.abs(b.a - L[k - 1].b[id].a) / L[k - 1].b[id].a;
        (blocked ? churnBlocked : churnFree).push(ch);
      }
      if (blocked) {
        blockedNow.add(F.f + ':' + id);
        if (!run) run = { id, f0: F.f, frames: 0, scene: sceneOf(F.f), fracSum: 0, wallSum: 0, blockers: {}, blockerLate: 0, a0: Math.round(b.a), cr0: b.cr, prog0: b.prog, edge: +b.edge.toFixed(0), chain: 0 };
        run.frames++; run.fracSum += cv.frac; run.wallSum += cv.wallFrac;
        // the chain: is my blocker itself blocked this frame
        if (cv.who !== null) { const bc = cover(F, cv.who); if (bc && bc.frac > COVER) run.chain++; }
        if (cv.who !== null) { run.blockers[cv.who] = (run.blockers[cv.who] || 0) + 1; if (cv.whoJ) run.blockerLate++; }
      } else if (run) {
        if (run.frames >= MIN) { run.f1 = L[k - 1].f; runs.push(run); }
        run = null;
      }
    }
    if (run && run.frames >= MIN) { run.f1 = L[L.length - 1].f; runs.push(run); }
  }
  for (const run of runs) {
    const k1 = L.findIndex(F => F.f === run.f1);
    let maxDa = 0, maxSlide = 0, a1 = null;
    for (let k = k1 + 1; k <= Math.min(L.length - 1, k1 + WIN); k++) {
      const F = L[k], P = L[k - 1], b = F.b[run.id], p = P.b[run.id];
      windows.add(F.f + ':' + run.id);
      if (b && p && p.a > 2000) maxDa = Math.max(maxDa, Math.abs(b.a - p.a) / p.a);
      if (b && a1 === null && k === k1 + WIN) a1 = Math.round(b.a);
      if (F.nb[run.id]) for (const j of F.nb[run.id]) {
        if (!(run.id in P.w) || !(j in P.w) || !(j in F.w) || !F.b[j]) continue;
        const d = Math.hypot(F.b[run.id].x - F.b[j].x, F.b[run.id].y - F.b[j].y); if (!(d > 1)) continue;
        maxSlide = Math.max(maxSlide, Math.abs((F.w[run.id] - F.w[j]) - (P.w[run.id] - P.w[j])) / (2 * d));
      }
    }
    run.meanCover = +(run.fracSum / run.frames).toFixed(2); run.meanWallCover = +(run.wallSum / run.frames).toFixed(2);
    run.blockerLateShare = +(run.blockerLate / run.frames).toFixed(2);
    run.chainShare = +(run.chain / run.frames).toFixed(2); delete run.chain;
    run.releaseDa = +maxDa.toFixed(3); run.releaseSlidePx = +maxSlide.toFixed(1); run.aAfter = a1;
    delete run.fracSum; delete run.wallSum; delete run.blockerLate;
  }
  // the test
  const slides = [];
  for (let k = 1; k < L.length; k++) {
    const F = L[k], P = L[k - 1], sc = sceneOf(F.f);
    if (sc === 'flock0' || sc === 'bento') continue;
    const done = {};
    for (const id in F.nb) for (const j of F.nb[id]) {
      if (j == id || !(id in P.w) || !(j in P.w) || !(j in F.w) || !F.b[id] || !F.b[j]) continue;
      const key = Math.min(id, j) + '-' + Math.max(id, j); if (done[key]) continue; done[key] = 1;
      const d = Math.hypot(F.b[id].x - F.b[j].x, F.b[id].y - F.b[j].y); if (!(d > 1)) continue;
      const dec = Math.abs((F.w[id] - F.w[j]) - (P.w[id] - P.w[j])) / (2 * d);
      slides.push({ dec, inWin: windows.has(F.f + ':' + id) || windows.has(F.f + ':' + j), blocked: blockedNow.has(F.f + ':' + id) || blockedNow.has(F.f + ':' + j) });
    }
  }
  slides.sort((a, b) => a.dec - b.dec);
  const top = slides.slice(Math.floor(slides.length * 0.9));
  const share = (arr) => arr.length ? arr.filter(s => s.inWin).length / arr.length : 0;
  const shareB = (arr) => arr.length ? arr.filter(s => s.blocked).length / arr.length : 0;
  const mean = (v) => v.length ? +(v.reduce((a, b) => a + b, 0) / v.length).toFixed(4) : null;
  const p90 = (v) => { if (!v.length) return null; const s = v.slice().sort((a, b) => a - b); return +s[Math.floor(s.length * 0.9)].toFixed(4); };
  const byScene = {};
  for (const run of runs) { const S = byScene[run.scene] = byScene[run.scene] || { runs: 0, bodyFrames: 0, byWall: 0, byHole: 0, blockerLate: 0 }; S.runs++; S.bodyFrames += run.frames; if (run.meanWallCover > run.meanCover / 2) S.byWall++; else S.byHole++; if (run.blockerLateShare > 0.5) S.blockerLate++; }
  const trans = runs.filter(r => r.scene !== 'flock0' && r.scene !== 'bento');
  return {
    clock: { dtMs: +DT.toFixed(3), jitterMs: JIT }, pointer: [PX, PY], thresholds: { cover: COVER, minFrames: MIN, releaseWin: WIN },
    blockedRuns: runs.length, blockedBodyFrames: runs.reduce((s, r) => s + r.frames, 0),
    transitionRuns: trans.length, transitionBodyFrames: trans.reduce((s, r) => s + r.frames, 0),
    meanRunFrames: +(runs.length ? runs.reduce((s, r) => s + r.frames, 0) / runs.length : 0).toFixed(1),
    blockerIsLate: runs.filter(r => r.blockerLateShare > 0.5).length, blockerIsSeated: runs.filter(r => r.blockerLateShare <= 0.5).length,
    topDecileSlidesInRelease: +share(top).toFixed(3), allSlidesInRelease: +share(slides).toFixed(3),
    releaseEnrichment: share(slides) > 0 ? +(share(top) / share(slides)).toFixed(2) : null,
    // DURING the block, not after it: big slides whose pair has a blocked member right now
    topDecileSlidesWhileBlocked: +shareB(top).toFixed(3), allSlidesWhileBlocked: +shareB(slides).toFixed(3),
    blockedEnrichment: shareB(slides) > 0 ? +(shareB(top) / shareB(slides)).toFixed(2) : null,
    // a travelling body's own area churn per frame, blocked against free
    churn: { blockedMean: mean(churnBlocked), blockedP90: p90(churnBlocked), blockedN: churnBlocked.length, freeMean: mean(churnFree), freeP90: p90(churnFree), freeN: churnFree.length },
    chainedRuns: runs.filter(r => r.chainShare > 0.5).length,
    seedNearEdge: runs.filter(r => r.edge < 40).length,
    meanReleaseSlidePx: +(trans.length ? trans.reduce((s, r) => s + r.releaseSlidePx, 0) / trans.length : 0).toFixed(1),
    meanReleaseDa: +(trans.length ? trans.reduce((s, r) => s + r.releaseDa, 0) / trans.length : 0).toFixed(3),
    byScene,
    worstRuns: trans.slice().sort((a, b) => b.releaseSlidePx - a.releaseSlidePx).slice(0, 14),
    longestRuns: trans.slice().sort((a, b) => b.frames - a.frames).slice(0, 8),
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
  console.log('worst releases (transitions; the wall that slid furthest when a slot came free):');
  for (const r of worstRuns) console.log('  ' + JSON.stringify(r));
  console.log('longest blocked runs (transitions):');
  for (const r of longestRuns) console.log('  ' + JSON.stringify(r));
})().catch(e => { console.error(e); process.exit(1); });
