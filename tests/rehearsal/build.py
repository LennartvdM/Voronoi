"""Build Rehearsal from Shoal: the hive rehearses a change before it plays it.

Every mark so far reacted frame by frame: at the click every rule started at
full strength and none of them knew where the change was going, so the
auction reconciled them live, and the cells fought. Here, when a change is
asked for, the hive plays it first where nobody sees it: a copy of the whole
world (the page, its fields, the reel, the page's image, the clocks) run
ahead headless to the change's end, the defects counted as it goes (a
drawing that lurches, a cell squeezed into a sliver or cut in two, two
travellers that meet, a shock at the start). Then it revises the plan and
rehearses again, and plays the plan that rehearsed best. The engine is
deterministic, so what it rehearsed is what it plays.

Its one power, for now, is when each cell sets off. A cell may leave later,
and arrives when the rest do, travelling faster. It rehearses the changes
at home and between home and a page, asked for from rest; a change from page
to page, the flock, and a story, is Shoal's. It thinks for most of each
frame, and until it has its plan it holds still.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'shoal.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '86519224fcc304ac24442832f445ee918850b9ca787cc48bc1f4d4d93f3cac47'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Shoal — Hive</title>', '<title>Rehearsal — Hive</title>')
replace('''&larr; Back · Shoal</a>''', '''&larr; Back · Rehearsal</a>''')
replace(''' · Shoal: a group moves as one ·''', ''' · Shoal: a group moves as one · Rehearsal: the hive plays a change first where nobody sees it ·''')
# the budget is the page's to set: none plays a change at once, as Shoal does
replace('''      <input type="range" id="stagger" min="0" max="100" value="30" title="mean time for a change to cross one shared edge"><span class="val" id="staggerVal">.30s</span>
    </div>''', '''      <input type="range" id="stagger" min="0" max="100" value="30" title="mean time for a change to cross one shared edge"><span class="val" id="staggerVal">.30s</span>
    </div>
    <div class="group"><span class="lbl">Rehearse</span>
      <input type="range" id="rehearse" min="0" max="8" value="6" title="rehearsals a change may have before it is played; none plays it at once"><span class="val" id="rehearseVal">6</span>
    </div>''')
replace('''bindSlider('stagger', v => { config.stagger = v / 100; document.getElementById('staggerVal').textContent = '.' + String(v).padStart(2, '0') + 's'; });''', '''bindSlider('stagger', v => { config.stagger = v / 100; document.getElementById('staggerVal').textContent = '.' + String(v).padStart(2, '0') + 's'; });
bindSlider('rehearse', v => { rehearsalBudget = v; document.getElementById('rehearseVal').textContent = v; });   // REHEARSAL''')

# THE WORLD CAN BE REHEARSED. The simulation is the part of the frame before
# the picture; the page's root becomes a binding that a rehearsal can swap.
replace('''const root = new Hive({ depth: 0, minCount: 3, scene: config.scene, W: 320, H: 240 });''',
        '''let root = new Hive({ depth: 0, minCount: 3, scene: config.scene, W: 320, H: 240 });   // REHEARSAL: a binding, so a rehearsal can put a copy of the world in its place''')
replace('''  if (dt > 0.05) dt = 0.05;
  simTime += dt;
  frame++;

  guestLeft = changeEnds(root) - simTime;
  tellFlow(dt); tellStep(dt); tell2Flow(dt); tell2Step(); cueFlow(dt);
  reelFlow(dt);
  reelStep();

  // 1-5. the page, and every hive inside it
  root.step(dt, simTime);
''', '''  if (dt > 0.05) dt = 0.05;
  rehearsalDts.push(dt); if (rehearsalDts.length > 15) rehearsalDts.shift();   // REHEARSAL: the page's pace
  simulate(dt);
  if (rehearsalJob) { requestAnimationFrame(tick); return; }   // REHEARSAL: the hive is thinking. Nothing has moved, and the picture stands as it was: what it rehearses is what it plays
''')
replace('''let lastT = 0;
function tick(nowMs) {''', '''let lastT = 0;
// the simulation of a frame: everything before the picture. A rehearsal runs
// this and nothing else. A change asked for since the last frame is
// rehearsed first, before anything has moved: the hive thinks for as long
// as a frame allows, and until it has a plan it holds still.
function simulate(dt) {
  if (!rehearsing && rehearsalPending) {
    rehearsalLog = { t0: rehearsalPending.t0, ms: 0, frames: 0, held: 0 };
    rehearsalJob = rehearsalPlan(rehearsalPending.t0); rehearsalPending = null;
    guestLeft = Math.max(guestLeft, changeEnds(root) - simTime);   // a change is asked for: the pointer is a guest from now
  }
  if (!rehearsing && rehearsalJob) {
    const began = performance.now();
    for (let n = 0; n < rehearsalSlice.frames && performance.now() - began < rehearsalSlice.ms; n++) { rehearsalLog.frames++; if (rehearsalJob.next().done) { rehearsalJob = null; break; } }
    rehearsalLog.ms += performance.now() - began;
    if (rehearsalJob) { rehearsalLog.held++; return; }   // nothing has moved yet, and nothing moves until the plan is made
  }
  simTime += dt;
  frame++;

  guestLeft = changeEnds(root) - simTime;
  tellFlow(dt); tellStep(dt); tell2Flow(dt); tell2Step(); cueFlow(dt);
  reelFlow(dt);
  reelStep();

  // 1-5. the page, and every hive inside it
  root.step(dt, simTime);
}
function tick(nowMs) {''')

# A FIELD IS NOT REHEARSED. Nothing flows back up from a field: its outer
# cell is the page's, settled before the field looks at it. So a rehearsal
# steps the page alone, neither re-rostering nor running the fields, and
# shares them with the live page untouched.
replace('''    for (const b of this.bodies) {
      if (b.fieldAt < 0 || t < b.fieldAt) continue;''', '''    for (const b of this.bodies) {
      if (b.fieldAt < 0 || t < b.fieldAt || rehearsing) continue;   // REHEARSAL: the fields are not rehearsed''')
replace('''    // 4. the fields: each one told the size of its cell, then run in full.''', '''    if (rehearsing) return;   // REHEARSAL: the page alone
    // 4. the fields: each one told the size of its cell, then run in full.''')

# A CHANGE TO REHEARSE: a change of the page's scene, asked for with no story
# told, at most one page image in it (home's scenes, and home to a page and
# back), and from rest (nothing travelling, and not the flock, whose cells
# are always on the wing), so that holding still while the hive thinks stops
# nothing that is moving. Asked for here, rehearsed at the next frame, once
# the change is wholly laid out. A change asked for while the hive is still
# thinking about the last one starts it afresh: nothing of the last one moved.
replace('''  enterScene(name, origin) {
    this.scene = name;''', '''  enterScene(name, origin) {
    const rehearsalPrev = this.scene, rehearsalRest = this === root && !rehearsing && rehearsalPrev !== 'flock' && (!!rehearsalJob || !!rehearsalPending || changeEnds(this) <= this.t);   // REHEARSAL: the scene a change leaves, and whether anything was still moving
    if (this === root && !rehearsing) { rehearsalJob = null; rehearsalPending = null; }
    this.scene = name;''')
replace('''      for (const j of js) { j.delay = 0; j.dur = dur; }
    }''', '''      for (const j of js) { j.delay = 0; j.dur = dur; }
      if (rehearsalBudget > 0 && rehearsalRest && name !== rehearsalPrev && !(name in PORTAL_TEMPLATES && rehearsalPrev in PORTAL_TEMPLATES)) rehearsalPending = { t0: this.t };   // REHEARSAL: played first where nobody sees it
    }''')

# REHEARSAL. A copy of the whole world: the page and every hive in it, the
# reel, the page's image, the clocks; one copy, so a body the page's image
# names is the body the copied page holds. Swapped in, run, swapped out.
replace('''// How much of the change is still to run, in seconds: > 0 is a page mid-change''', '''let rehearsalBudget = 6;          // rehearsals a change may have, the first its own plan; none plays it at once (the Rehearse slider)
const REHEARSAL_STEP = 0.15;      // s: how much later a cell may set off, a move at a time
const REHEARSAL_MAX = 0.45;       // s: and at most
const REHEARSAL_MIN_DUR = 0.5;    // s: the shortest journey a later start may leave a cell
const REHEARSAL_SPAN = 4;         // s: the longest a rehearsal runs
let rehearsalSlice = { ms: 12, frames: Infinity };   // what one frame of the page may spend thinking: wall time (the picture stands, so most of the frame), or rehearsed frames (for a probe that counts)
let rehearsalPending = null, rehearsalJob = null, rehearsing = false, rehearsalLog = null;
const rehearsalDts = [];          // the page's last frame lengths: a rehearsal runs at their median, so one slow frame does not set its pace
function rehearsalCopy(x, seen) {
  if (x === null || typeof x !== 'object') return x;   // numbers, strings and functions are shared
  if (x instanceof Hive && x.depth > 0) return x;      // a field is not rehearsed: its outer cell is the page's, and nothing in it reaches back out
  const had = seen.get(x); if (had) return had;
  if (ArrayBuffer.isView(x)) { const y = x.slice(); seen.set(x, y); return y; }
  const y = Array.isArray(x) ? new Array(x.length) : Object.create(Object.getPrototypeOf(x));
  seen.set(x, y);
  for (const k of Object.keys(x)) y[k] = rehearsalCopy(x[k], seen);   // an array's own named keys too (a loop's hole flag)
  return y;
}
function rehearsalWorld() { return { root, reel, portalFocus, portalFlip, simTime, frame, guestLeft, shoalOn, cueWho, reelDrift }; }
function rehearsalEnter(w) { root = w.root; reel = w.reel; portalFocus = w.portalFocus; portalFlip = w.portalFlip; simTime = w.simTime; frame = w.frame; guestLeft = w.guestLeft; shoalOn = w.shoalOn; cueWho = w.cueWho; reelDrift = w.reelDrift; }
// THE DEFECTS, counted as the rehearsal runs: a drawing whose motion changes
// by more than 10 px from one frame to the next (a teleport, a cell taken
// out of a field, is not one), a cell drawn thin that is no rectangle, a
// cell drawn in two, two travellers whose seeds come within 0.35 of their
// reaches added, and in the first quarter second, drawings moving further
// than their seeds (the shock). Each is laid at the door of the cells that
// suffer it, and of the traveller nearest them as they do.
function rehearsalScorer(dt) {
  const prev = new Map(), pairs = new Map(), blame = new Map(), partner = new Map(), u = (dt || 1 / 60) * 60, lu = u * u;   // u: page frames a frame; a lurch grows with the square of the frame
  let lurch = 0, sliver = 0, split = 0, shock = 0, frames = 0, running = 0;
  const add = (m, k, v) => m.set(k, (m.get(k) || 0) + v);
  return {
    frame() {
      frames++;
      const R = root, cells = R.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.loops && b.loops.length);
      const trav = cells.filter(b => b.journey && b.progress > 0 && b.progress < 1), reach = b => 0.5 * Math.sqrt(Math.max(b.claim, CLAIM_MIN) * R.PW * R.PH);
      for (const b of cells) {
        let A = 0, x = 0, y = 0;
        for (const L of b.loops) for (let i = 0; i < L.length; i++) { const p = L[i], q = L[(i + 1) % L.length], f = p[0] * q[1] - q[0] * p[1]; A += f; x += (p[0] + q[0]) * f; y += (p[1] + q[1]) * f; }
        if (Math.abs(A) < 1e-6) continue;
        const c = [x / (3 * A), y / (3 * A)], p = prev.get(b.id);
        let bl = 0;
        if (p && p.c1 && Math.hypot(c[0] - p.c[0], c[1] - p.c[1]) < 300 * u && Math.hypot(p.c[0] - p.c1[0], p.c[1] - p.c1[1]) < 300 * u) { const d = Math.max(0, Math.hypot(c[0] - 2 * p.c[0] + p.c1[0], c[1] - 2 * p.c[1] + p.c1[1]) / lu - 10) * u; lurch += d; bl += d; }
        if (p && frames * u <= 15) { const d = Math.max(0, Math.hypot(c[0] - p.c[0], c[1] - p.c[1]) - Math.hypot(b.x - p.s[0], b.y - p.s[1])); if (Math.hypot(c[0] - p.c[0], c[1] - p.c[1]) < 300 * u) { shock += d; bl += d; } }
        if (b.loops.length === 1) {
          const L = b.loops[0], a = Math.abs(ringArea(L));
          if (a > 2000) { let P = 0, x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity; for (let i = 0; i < L.length; i++) { const q = L[(i + 1) % L.length]; P += Math.hypot(q[0] - L[i][0], q[1] - L[i][1]); x0 = Math.min(x0, L[i][0]); y0 = Math.min(y0, L[i][1]); x1 = Math.max(x1, L[i][0]); y1 = Math.max(y1, L[i][1]); }
            if (4 * Math.PI * a / (P * P) < 0.3 && a < 0.97 * (x1 - x0) * (y1 - y0)) { sliver += u; bl += 50 * u; } }
        } else if (b.loops.map(L => Math.abs(ringArea(L))).sort((m, v) => v - m)[1] > 50) { split += u; bl += 200 * u; }
        prev.set(b.id, { c, c1: p ? p.c : null, s: [b.x, b.y] });
        if (bl > 0) {
          add(blame, b.id, bl);
          let near = null, nd = Infinity; for (const o of trav) { if (o === b) continue; const d = Math.hypot(o.x - b.x, o.y - b.y); if (d < nd) { nd = d; near = o; } }
          if (near) { if (!partner.has(b.id)) partner.set(b.id, new Map()); add(partner.get(b.id), near.id, bl); }
        }
      }
      for (let i = 0; i < trav.length; i++) for (let j = i + 1; j < trav.length; j++) {
        const a = trav[i], c = trav[j], k = a.id + ':' + c.id, d = Math.hypot(a.x - c.x, a.y - c.y) / (reach(a) + reach(c));
        if (!(pairs.get(k) <= d)) { if (d < 0.35 && !(pairs.get(k) < 0.35)) running += 100; pairs.set(k, d); }
      }
      return lurch + 50 * sliver + 200 * split + shock + running;   // the score so far
    },
    result() {
      let collisions = 0;
      for (const [k, d] of pairs) if (d < 0.35) {
        collisions++;
        const [a, c] = k.split(':').map(Number);
        add(blame, a, 100); add(blame, c, 100);
        if (!partner.has(a)) partner.set(a, new Map()); add(partner.get(a), c, 100);
        if (!partner.has(c)) partner.set(c, new Map()); add(partner.get(c), a, 100);
      }
      return { score: lurch + 50 * sliver + 200 * split + 100 * collisions + shock, lurch, sliver, split, collisions, shock, frames, blame, partner };
    },
  };
}
// one rehearsal of a plan (the departures it moves, by body): the world
// copied, the plan written onto the copy's journeys, the copy run at the
// page's pace to the change's end, the defects counted. (Its fields are the
// live page's, not stepped, so the end is the page's own: a field's change,
// once the page's change reaches it, may run on.) The live world is
// given back after every frame (a yield), so the thinking can be spread over
// the page's own frames.
function* rehearse(t0, D, plan, dt, bound) {
  let w = rehearsalCopy(rehearsalWorld(), new Map());
  for (const b of w.root.bodies) { const d = plan.get(b.id), j = b.journey; if (d && j && j.t0 === t0) { j.delay = d; j.dur = Math.max(REHEARSAL_MIN_DUR, D - d); } }
  const sc = rehearsalScorer(dt);
  for (let n = 0; n < REHEARSAL_SPAN / dt; n++) {
    const live = rehearsalWorld();
    let score = -1;
    rehearsing = true; rehearsalEnter(w);
    try {
      if (simTime < changeEnds(root)) { simulate(dt); root.hoveredId = -1; score = sc.frame(); }   // the page's frame; while a change runs the pointer takes nothing
    } finally { w = rehearsalWorld(); rehearsalEnter(live); rehearsing = false; }
    if (score < 0) break;
    if (score >= bound) { const r = sc.result(); r.score = Infinity; return r; }   // already no better than the best: not worth the rest of the run
    yield;
  }
  return sc.result();
}
// THE PLAN. Its own first (everyone sets off together and lands together);
// then, while the budget lasts, the cell that suffered most, and the
// traveller nearest it as it did: one of them sets off later, arriving as
// before, and the move is kept if the change rehearses better. The plan it
// keeps is written onto the page's own journeys, before anything has moved.
function* rehearsalPlan(t0) {
  const trav = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.path && b.journey && b.journey.t0 === t0);
  if (trav.length < 2) return;
  const ids = new Set(trav.map(b => b.id)), D = Math.max(...trav.map(b => b.journey.dur));
  const dt = rehearsalDts.length ? [...rehearsalDts].sort((a, b) => a - b)[rehearsalDts.length >> 1] : 1 / 60;
  let plan = new Map(), best = yield* rehearse(t0, D, plan, dt, Infinity), n = 1;
  const base = best, tried = new Set();
  while (n < rehearsalBudget) {
    const victims = [...best.blame].filter(([id, v]) => ids.has(id) && v > 0).sort((a, b) => b[1] - a[1] || a[0] - b[0]).map(([id]) => id);
    let moved = false;
    for (const v of victims) {
      const pm = best.partner.get(v), p = pm ? [...pm].filter(([id]) => ids.has(id)).sort((a, b) => b[1] - a[1] || a[0] - b[0])[0] : null;
      const moves = [];
      for (const id of [p ? p[0] : null, v]) {
        if (id === null) continue;
        const d = Math.min(REHEARSAL_MAX, (plan.get(id) || 0) + REHEARSAL_STEP), key = id + '@' + d.toFixed(2);
        if (d <= (plan.get(id) || 0) + 1e-9 || tried.has(key)) continue;
        tried.add(key); moves.push(new Map(plan).set(id, d));
      }
      let won = null;
      for (const m of moves) { if (n >= rehearsalBudget) break; const r = yield* rehearse(t0, D, m, dt, won ? won.r.score : best.score); n++; if (r.score < (won ? won.r.score : best.score) - 1e-6) won = { m, r }; }
      if (won) { plan = won.m; best = won.r; moved = true; break; }
      if (n >= rehearsalBudget) break;
    }
    if (!moved) break;
  }
  for (const b of trav) { const d = plan.get(b.id); if (d) { b.journey.delay = d; b.journey.dur = Math.max(REHEARSAL_MIN_DUR, D - d); } }
  const parts = r => ({ lurch: r.lurch, sliver: r.sliver, split: r.split, collisions: r.collisions, shock: r.shock });
  Object.assign(rehearsalLog, { dt, base: base.score, chosen: best.score, baseParts: parts(base), parts: parts(best), plan: [...plan], rehearsals: n });
}

// How much of the change is still to run, in seconds: > 0 is a page mid-change''')

(ROOT / 'rehearsal.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
