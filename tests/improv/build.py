"""Build Improv from Rehearsal: the hive thinks while it plays.

Rehearsal thought before it moved: at the click it held the page still,
rehearsed a change headless, and played the plan that rehearsed best. That
pause (half a second to a second and a half, two seconds between pages)
is itself a defect, and a page is never still to begin with: its gallery
flows on its own, so the hold stopped a moving thing, and no plan made
ahead of the click can know the page it will meet.

Here nothing waits. A change starts at once, as Shoal plays it, and the hive
thinks in rounds while it plays. A round copies the page as it is, flow and
all, rehearses the rest of the change, and tries a move on it: a cell's clock
crawls for a moment and then runs fast enough to land when it would have.
The move acts from the moment the round's answer will be in hand, so what
was rehearsed is what is played; an answer that comes later than that is
dropped.

How much it thinks is no setting. The hive learns the display's period
from the frames it does not think in, and while it thinks it watches its
frames: one that comes late means it thinks less the next, one on time a
little more. It thinks as much as never costs a frame, whatever the device
and whatever else the browser has to do after the script (a large canvas's
raster is not the script's time, and was what a budget read off the
script's own clock overran).

How far ahead a round looks is no setting either. Everyone of a change
lands together, and a cell that crawls must hurry after, so a move's
consequences run to the landing: a round rehearses to the change's end
(rounds that looked less far made moves whose hurrying they had not seen,
and on a phone played worse than Shoal). How finely follows from the budget
and one deadline: an answer is worth having until the cells it would move
have gone a twentieth of their way, which easeInOutCubic reaches a quarter
of the way through a journey. A round rehearses at the page's own frame if
its answer is in hand by then, and coarse (1/16 s frames) if not.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'rehearsal.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'dc4681c996676b9df3e825d0549a393398925d862be3636f248231b4540356ad'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Rehearsal — Hive</title>', '<title>Improv — Hive</title>')
replace('''&larr; Back · Rehearsal</a>''', '''&larr; Back · Improv</a>''')
replace('''Rehearsal: the hive plays a change first where nobody sees it ·''', '''Rehearsal: the hive plays a change first where nobody sees it · Improv: the hive thinks while it plays ·''')

# NO SETTING. How hard the hive thinks is measured, not chosen.
replace('''    <div class="group"><span class="lbl">Rehearse</span>
      <input type="range" id="rehearse" min="0" max="8" value="6" title="rehearsals a change may have before it is played; none plays it at once"><span class="val" id="rehearseVal">6</span>
    </div>
''', '')
replace('''
bindSlider('rehearse', v => { rehearsalBudget = v; document.getElementById('rehearseVal').textContent = v; });   // REHEARSAL''', '')

# A JOURNEY'S OWN CLOCK. A move slows it from a moment on; unmoved, it is the page's.
replace('''        const u = Math.min(1, Math.max(0, (t - j.t0 - j.delay - (j.hold || 0)) / j.dur));
        b.progress = b.cueTie''', '''        const u = Math.min(1, Math.max(0, (improvClock(j, t) - j.t0 - j.delay - (j.hold || 0)) / j.dur));   // IMPROV: its own clock
        b.progress = b.cueTie''')

# A CHANGE TO THINK ABOUT: any change of the page's scene, and a page opened
# from a page, with no story told; not the flock, whose cells go nowhere. It
# need not start from rest: nothing waits for the hive, so nothing is held.
replace('''    const rehearsalPrev = this.scene, rehearsalRest = this === root && !rehearsing && rehearsalPrev !== 'flock' && (!!rehearsalJob || !!rehearsalPending || changeEnds(this) <= this.t);   // REHEARSAL: the scene a change leaves, and whether anything was still moving''',
        '''    const rehearsalPrev = this.scene;   // the scene a change leaves''')
replace('''      if (rehearsalBudget > 0 && rehearsalRest && name !== rehearsalPrev && !(name in PORTAL_TEMPLATES && rehearsalPrev in PORTAL_TEMPLATES)) rehearsalPending = { t0: this.t };   // REHEARSAL: played first where nobody sees it''',
        '''      if (this === root && !rehearsing && rehearsalPrev !== 'flock' && (name !== rehearsalPrev || name in PORTAL_TEMPLATES)) rehearsalPending = { t0: this.t };   // IMPROV: a change the hive thinks about as it plays it''')

# THE KNOBS REHEARSAL HAD: gone. Its world, its copy and its defects stay.
replace('''let rehearsalBudget = 6;          // rehearsals a change may have, the first its own plan; none plays it at once (the Rehearse slider)
const REHEARSAL_STEP = 0.15;      // s: how much later a cell may set off, a move at a time
const REHEARSAL_MAX = 0.45;       // s: and at most
const REHEARSAL_MIN_DUR = 0.5;    // s: the shortest journey a later start may leave a cell
const REHEARSAL_SPAN = 4;         // s: the longest a rehearsal runs
let rehearsalSlice = { ms: 12, frames: Infinity };   // what one frame of the page may spend thinking: wall time (the picture stands, so most of the frame), or rehearsed frames (for a probe that counts)
let rehearsalPending = null, rehearsalJob = null, rehearsing = false, rehearsalLog = null;''', '''const REHEARSAL_SPAN = 4;         // s: the longest a rehearsal runs
const IMPROV_MOVES = 2;           // moves a round tries beside the plan as it stands
const IMPROV_SLOW = 0.3;          // s: a move: a cell's clock crawls this long from when the answer is in hand,
const IMPROV_CRAWL = 0.15;        // at this rate, then runs fast enough to land when it would have
const IMPROV_DUE = Math.cbrt(0.05 / 4);   // of a journey: when easeInOutCubic has gone a twentieth of the way, and an answer is due
const IMPROV_COARSE = 1 / 16;     // s: the coarse frame
const IMPROV_LATE = 1.15;         // a frame this much longer than the display's period is late
let improvBudget = null;          // rehearsed frames a page frame may think, for a probe that counts; null: as much as never makes a frame late
let improvSlice = 2, improvStepMs = 1, improvThought = false;   // ms a frame thinks; ms a rehearsed frame takes; whether the last frame thought
const improvIdle = [];            // the intervals of frames the hive did not think in: the display's own period
let rehearsalPending = null, rehearsalJob = null, rehearsing = false, rehearsalLog = null;''')

a = s.index('''// one rehearsal of a plan (the departures it moves, by body): the world''')
b = s.index('''// How much of the change is still to run, in seconds: > 0 is a page mid-change''')
s = s[:a] + '''// A JOURNEY'S OWN CLOCK: the page's, until a move slows it. From w.a it
// crawls for w.h at w.r, then runs fast enough to arrive when it would have.
function improvClock(j, t) {
  const w = j.warp; if (!w || t <= w.a) return t;
  const A = j.t0 + j.delay + (j.hold || 0) + j.dur, e = w.a + w.h, slow = w.a + (Math.min(t, e) - w.a) * w.r;
  if (t <= e) return slow;
  return Math.min(A, slow + (t - e) * (A - slow) / (A - e));
}
// what a rehearsed frame costs, in the page's own simulated frames: the
// auction's rounds, which grow with the frame's length
const improvCost = dt => Math.max(3, Math.min(8, Math.round(3 * dt * 60))) / 3;
// ONE REHEARSAL, from a copy of the page as it was when the round began, with
// a move written onto the copy, run to the round's horizon, the defects
// counted. The live page is given back after every frame (a yield, with the
// frame's cost), so the thinking fits in the page's spare time.
function* improvRehearse(snap, mv, dt, until, bound) {
  let w = rehearsalCopy(snap, new Map());
  if (mv) { const b = w.root.bodies.find(q => q.id === mv.id); if (b && b.journey) b.journey.warp = { a: mv.a, h: mv.h, r: mv.r }; }
  const sc = rehearsalScorer(dt), cost = improvCost(dt);
  for (let n = 0; n < REHEARSAL_SPAN / dt; n++) {
    const live = rehearsalWorld();
    let score = -1;
    rehearsing = true; rehearsalEnter(w);
    try {
      if (simTime < until) { simulate(dt); root.hoveredId = -1; score = sc.frame(); }   // the page's frame; while a change runs the pointer takes nothing
    } finally { w = rehearsalWorld(); rehearsalEnter(live); rehearsing = false; }
    if (score < 0) break;
    if (score >= bound) { const r = sc.result(); r.score = Infinity; return r; }   // already no better than the best: not worth the rest of the run
    yield cost;
  }
  return sc.result();
}
// THE ROUNDS. Each copies the page as it is and rehearses the rest of the
// change: the plan as it stands, then a move for the cell that suffered most
// and for the traveller nearest it as it did, if that cell lands within what
// was rehearsed (a cell that crawls must hurry after, and a round makes no
// move whose hurrying it has not seen). A move that rehearses better is
// written onto the page's own journey, to act from the moment the round
// expected its answer to be in hand; if the answer is later than that, it is
// dropped. Rounds go on while the change has time left to change.
//
// HOW FINELY: every round rehearses to the change's end. Its rehearsals
// share what the hive can think before the answer is due (the spare time of
// that many frames); if at the page's own frame they reach the end in that,
// they rehearse at it, and if not, coarse.
function* improvise(t0) {
  const log = rehearsalLog;
  const dtL = rehearsalDts.length ? [...rehearsalDts].sort((a, b) => a - b)[rehearsalDts.length >> 1] : 1 / 60;
  const trav0 = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.path && b.journey && b.journey.t0 === t0);
  if (trav0.length < 2) return;
  const D = Math.max(...trav0.map(b => { const j = b.journey; return j.delay + (j.hold || 0) + j.dur; })), due = IMPROV_DUE * D;
  const arrives = j => j.t0 + j.delay + (j.hold || 0) + j.dur;
  for (;;) {
    const tau = simTime, end = changeEnds(root);
    const F = improvBudget !== null ? improvBudget : improvRate();
    const per = due / dtL * F / (1 + IMPROV_MOVES), H = end - tau;   // the page's own frames each of the round's rehearsals may have before the answer is due; and every round rehearses to the change's end
    const dt = H / dtL <= per ? dtL : IMPROV_COARSE;   // at the page's own frame if that is in hand when due, else coarse
    const frames = Math.ceil(H / dt), a = tau + (Math.ceil((1 + IMPROV_MOVES) * frames * improvCost(dt) / F) + 1) * dtL;   // when the round's answer will be in hand
    if (!(F > 0) || frames < 2 || end - a < IMPROV_SLOW + 0.4) return;   // no time to think, or nothing left to change
    const snap = rehearsalCopy(rehearsalWorld(), new Map()), until = tau + H;
    const base = yield* improvRehearse(snap, null, dt, until, Infinity);
    const ok = id => { const b = root.bodies.find(q => q.id === id); return b && b.path && b.journey && b.journey.t0 === t0 && !b.journey.warp && a + IMPROV_SLOW < arrives(b.journey) - 0.4 && arrives(b.journey) <= until; };   // a move whose whole consequence for its cell, the crawl and the catching up, the round has rehearsed
    const moves = [];
    for (const [v] of [...base.blame].sort((x, y) => y[1] - x[1] || x[0] - y[0])) {
      const pm = base.partner.get(v), p = pm ? [...pm].sort((x, y) => y[1] - x[1] || x[0] - y[0])[0] : null;
      for (const id of [p ? p[0] : null, v]) if (id !== null && ok(id) && !moves.some(m => m.id === id) && moves.length < IMPROV_MOVES) moves.push({ id, a, h: IMPROV_SLOW, r: IMPROV_CRAWL });
      if (moves.length >= IMPROV_MOVES) break;
    }
    let won = null;
    for (const m of moves) { const r = yield* improvRehearse(snap, m, dt, until, won ? won.r.score : base.score); if (r.score < (won ? won.r.score : base.score) - 1e-6) won = { m, r }; }
    const late = simTime > a;
    if (won && !late) { const b = root.bodies.find(q => q.id === won.m.id); b.journey.warp = { a: won.m.a, h: won.m.h, r: won.m.r }; }
    log.rounds.push({ tau, a, until, dt, done: simTime, base: base.score, chosen: won ? won.r.score : base.score, move: won && !late ? won.m.id : null, late: !!won && late });
    if (!moves.length) return;
  }
}
// THE HIVE'S BUDGET: as much thinking as never makes a frame late. The
// display's period is the median interval of the frames it did not think in;
// a frame that came late halves the next frame's thinking, one on time adds a
// tenth of a millisecond, up to what four fifths of the period leaves after
// the frame's own work: slow to take, quick to give back, and learnt on every
// frame, so it is known before a change needs it. In rehearsed frames: what that time holds, at what a rehearsed
// frame has been taking.
const improvMedian = a => { if (!a.length) return 0; const r = [...a].sort((x, y) => x - y); return r[r.length >> 1]; };
function improvRate() { return improvSlice / improvStepMs; }
function improvThink(frameMs, began) {
  if (improvBudget === null && frameMs > 0) {
    if (!improvThought) { improvIdle.push(frameMs); if (improvIdle.length > 15) improvIdle.shift(); }
    const T = improvMedian(improvIdle) || 1000 / 60, work = performance.now() - began;
    if (frameMs > IMPROV_LATE * T) improvSlice = Math.max(0.25, improvSlice * 0.5);   // late, whether it thought or not: there is less to spare
    else improvSlice = Math.min(Math.max(0.25, 0.8 * T - work), improvSlice + 0.1);   // on time: a little more, never past what the frame's own work leaves
  }
  improvThought = false;
  if (!rehearsalJob) return;
  const t = performance.now(), until = t + improvSlice;
  let spent = 0;
  while (improvBudget !== null ? spent < improvBudget : performance.now() < until) {
    const r = rehearsalJob.next();
    if (r.done) { rehearsalJob = null; break; }
    spent += r.value; rehearsalLog.frames++;
  }
  const took = performance.now() - t;
  if (improvBudget === null && spent > 0) improvStepMs += (took / spent - improvStepMs) * 0.2;
  rehearsalLog.ms += took; improvThought = true;
}

''' + s[b:]

replace('''// the simulation of a frame: everything before the picture. A rehearsal runs
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
  simTime += dt;''', '''// the simulation of a frame: everything before the picture. A rehearsal runs
// this and nothing else. A change asked for since the last frame is played
// at once, and the hive begins to think about it (at the frame's end, in the
// time the frame leaves).
function simulate(dt) {
  if (!rehearsing && rehearsalPending) {
    rehearsalLog = { t0: rehearsalPending.t0, ms: 0, frames: 0, rounds: [] };
    rehearsalJob = improvise(rehearsalPending.t0); rehearsalPending = null;
  }
  simTime += dt;''')
replace('''function tick(nowMs) {
  const now = nowMs / 1000;
  let dt = lastT ? now - lastT : 1 / 60;''', '''function tick(nowMs) {
  const began = performance.now();   // IMPROV: the frame's own work, timed
  const now = nowMs / 1000;
  let dt = lastT ? now - lastT : 1 / 60;
  const frameMs = lastT ? (now - lastT) * 1000 : 0;   // IMPROV: how long since the last frame: late, if the hive thought too much in it''')
replace('''  rehearsalDts.push(dt); if (rehearsalDts.length > 15) rehearsalDts.shift();   // REHEARSAL: the page's pace
  simulate(dt);
  if (rehearsalJob) { requestAnimationFrame(tick); return; }   // REHEARSAL: the hive is thinking. Nothing has moved, and the picture stands as it was: what it rehearses is what it plays
''', '''  rehearsalDts.push(dt); if (rehearsalDts.length > 15) rehearsalDts.shift();   // REHEARSAL: the page's pace
  simulate(dt);
''')
replace('''    meterEls.inner.textContent = '0';
    meterEls.inner.className = '';
  }

  requestAnimationFrame(tick);
}''', '''    meterEls.inner.textContent = '0';
    meterEls.inner.className = '';
  }

  improvThink(frameMs, began);   // IMPROV: the hive thinks in what the frame leaves
  requestAnimationFrame(tick);
}''')

(ROOT / 'improv.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
