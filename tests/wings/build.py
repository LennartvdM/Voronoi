"""Build Wings from Improv: the hive thinks offstage.

Improv thought on the page's own thread, in the time each frame left. That
time is shared: a frame's script is only part of its work, and where the
browser was already short of time (a large canvas in software) the hive
found nothing to spare and hardly thought, and where it did think it cost a
few frames. Here the thinking has a thread of its own: a worker running
this same script, with the page's document stubbed out, the way the probe
runs it headless. The page hands it a round (a copy of the page as it is,
and what to rehearse) and plays on; the worker rehearses the round at its
own full speed and hands back the move, which the page makes if it comes in
time. Nothing is taken from the page's frames.

The copy crosses as a structured clone. Two things in it do not: the
reel's strip definitions carry two small functions (a strip's slots and
rectangles, a pure function of the strip's region and the page's size), and
a clone keeps no class, so the hives come back as plain objects. The page
sends each strip's region instead of its definition, and the worker
rebuilds the definitions and gives the hives their class back.

How much the worker can think is measured, as the page's was: what a
rehearsed frame takes there, answer by answer. How far and how finely a
round rehearses follows from that, by Improv's rule. Where no worker can be
had (a host that forbids one, or the probe), the hive thinks on the page as
Improv does.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'improv.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'd36159a3aeb3253f430c8bb81e1121b739c66e3b9b9e69d0f16bfd54d7dedd7e'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Improv — Hive</title>', '<title>Wings — Hive</title>')
replace('''&larr; Back · Improv</a>''', '''&larr; Back · Wings</a>''')
replace('''Improv: the hive thinks while it plays ·''', '''Improv: the hive thinks while it plays · Wings: the hive thinks offstage, on a thread of its own ·''')

# THE SCRIPT, KEPT: the worker runs this same script, handed its text.
replace('''<script>
(function () {
'use strict';
''', '''<script>
(function () {
'use strict';
// WINGS: this script's own text, for the worker that thinks offstage (none in the worker itself, or headless)
const WINGS_SOURCE = typeof document !== 'undefined' && document.currentScript ? document.currentScript.textContent : null;
const WINGS_OFFSTAGE = typeof IMPROV_WORKER !== 'undefined' && IMPROV_WORKER === true;   // this copy of the script is the worker
''')

# THE ROUND, apart from where it is thought: the page and the worker run the same.
a = s.index('''function* improvise(t0) {''')
b = s.index('''// THE HIVE'S BUDGET: as much thinking as never makes a frame late.''')
s = s[:a] + '''function* improvise(t0) {
  const log = rehearsalLog;
  const dtL = rehearsalDts.length ? [...rehearsalDts].sort((a, b) => a - b)[rehearsalDts.length >> 1] : 1 / 60;
  const trav0 = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.path && b.journey && b.journey.t0 === t0);
  if (trav0.length < 2) return;
  const D = Math.max(...trav0.map(b => { const j = b.journey; return j.delay + (j.hold || 0) + j.dur; })), due = IMPROV_DUE * D;
  for (;;) {
    const tau = simTime, end = changeEnds(root), offstage = wingsReady();
    // WINGS: offstage, what the worker's rehearsed frames have been taking; here, the page's spare time
    const F = improvBudget !== null ? improvBudget : offstage ? dtL * 1000 / wingsStepMs : improvRate();
    const per = due / dtL * F / (1 + IMPROV_MOVES), ahead = end - tau;   // the page's own frames each of the round's rehearsals may have before the answer is due; and every round rehearses to the change's end
    const dt = ahead / dtL <= per ? dtL : IMPROV_COARSE;   // at the page's own frame if that is in hand when due, else coarse
    const frames = Math.ceil(ahead / dt), a = tau + (Math.ceil((1 + IMPROV_MOVES) * frames * improvCost(dt) / F) + 1 + (offstage ? WINGS_LAG : 0)) * dtL;   // when the round's answer will be in hand
    if (!(F > 0) || frames < 2 || end - a < IMPROV_SLOW + 0.4) return;   // no time to think, or nothing left to change
    const snap = rehearsalCopy(rehearsalWorld(), new Map()), until = tau + ahead;
    let res;
    if (offstage) {   // WINGS: handed to the worker; the page plays on until the answer comes
      const id = ++wingsAsked;
      offstage.postMessage({ type: 'round', id, snap: wingsFreeze(snap), t0, a, dt, until, env: { W, H, config: Object.assign({}, config), mouse: [mouseX, mouseY] } });
      while (!(wingsAnswer && wingsAnswer.id === id)) { if (!wingsReady()) return; yield -1; }
      res = wingsAnswer; wingsAnswer = null;
    } else res = yield* improvRound(snap, t0, a, dt, until);
    const late = simTime > a;
    if (res.move && !late) { const b = root.bodies.find(q => q.id === res.move.id); if (b && b.journey && b.journey.t0 === t0 && !b.journey.warp) b.journey.warp = { a: res.move.a, h: res.move.h, r: res.move.r }; }
    log.rounds.push({ tau, a, until, dt, done: simTime, base: res.base, chosen: res.chosen, move: res.move && !late ? res.move.id : null, late: !!res.move && late, offstage: !!offstage });
    if (!res.tried) return;
  }
}
// ONE ROUND, wherever it is thought: from a copy of the page as it was, the
// plan as it stands, then a move for the cell that suffered most and for the
// traveller nearest it as it did, if that cell lands within what is
// rehearsed; the better, if either is better
function* improvRound(snap, t0, a, dt, until) {
  const arrives = j => j.t0 + j.delay + (j.hold || 0) + j.dur;
  const base = yield* improvRehearse(snap, null, dt, until, Infinity);
  const ok = id => { const b = snap.root.bodies.find(q => q.id === id); return b && b.path && b.journey && b.journey.t0 === t0 && !b.journey.warp && a + IMPROV_SLOW < arrives(b.journey) - 0.4 && arrives(b.journey) <= until; };   // a move whose whole consequence for its cell, the crawl and the catching up, the round has rehearsed
  const moves = [];
  for (const [v] of [...base.blame].sort((x, y) => y[1] - x[1] || x[0] - y[0])) {
    const pm = base.partner.get(v), p = pm ? [...pm].sort((x, y) => y[1] - x[1] || x[0] - y[0])[0] : null;
    for (const id of [p ? p[0] : null, v]) if (id !== null && ok(id) && !moves.some(m => m.id === id) && moves.length < IMPROV_MOVES) moves.push({ id, a, h: IMPROV_SLOW, r: IMPROV_CRAWL });
    if (moves.length >= IMPROV_MOVES) break;
  }
  let won = null;
  for (const m of moves) { const r = yield* improvRehearse(snap, m, dt, until, won ? won.r.score : base.score); if (r.score < (won ? won.r.score : base.score) - 1e-6) won = { m, r }; }
  return { base: base.score, chosen: won ? won.r.score : base.score, move: won ? won.m : null, tried: moves.length };
}

// WINGS. THE HIVE'S OTHER THREAD. A worker running this same script, the
// page's document stubbed out as the probe stubs it; it rehearses the rounds
// it is handed. Started once the page is up; until it answers that it is
// ready, and if it never can be (a host that forbids workers), the hive
// thinks on the page, as Improv does.
const WINGS_LAG = 2;          // page frames a round's message and its answer take, besides the rehearsing
const WINGS_STUBS = "const IMPROV_WORKER = true; const noop = () => {};" +
  "const ctx = new Proxy({}, { get: (o, k) => k === 'measureText' ? (t => ({ width: 9 * String(t).length })) : k === 'createLinearGradient' ? (() => ({ addColorStop: noop })) : k in o ? o[k] : noop, set: (o, k, v) => { o[k] = v; return true; } });" +
  "const el = { addEventListener: noop, style: {}, classList: { toggle: noop, add: noop, remove: noop }, dataset: {}, textContent: '', getContext: () => ctx, parentElement: { getBoundingClientRect: () => ({ width: 1, height: 1 }) } };" +
  "const document = { readyState: 'loading', addEventListener: noop, getElementById: () => el, querySelectorAll: () => [], currentScript: null };" +
  "const window = { addEventListener: noop, devicePixelRatio: 1 }; const requestAnimationFrame = noop;\\n";
let wings = null, wingsStarting = null, wingsAnswer = null, wingsAsked = 0, wingsStepMs = 1.5;   // the worker once ready; while it starts; its last answer; rounds asked; ms a rehearsed frame takes there
function wingsReady() { return wings || null; }
function wingsStart() {
  if (WINGS_OFFSTAGE || !WINGS_SOURCE || typeof Worker === 'undefined' || wings !== null || wingsStarting) return;
  try {
    const src = WINGS_STUBS + WINGS_SOURCE;
    let w;
    try { w = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' }))); }
    catch (e) { w = new Worker('data:text/javascript;charset=utf-8,' + encodeURIComponent(src)); }
    wingsStarting = w;
    w.onmessage = ev => {
      const m = ev.data;
      if (m.type === 'ready') { wings = w; wingsStarting = null; }
      else if (m.type === 'answer') { wingsAnswer = m; if (m.frames > 0) wingsStepMs += (m.ms / m.frames - wingsStepMs) * 0.3; }
    };
    w.onerror = () => { wings = false; wingsStarting = null; };   // it cannot run here: the page thinks, as Improv
  } catch (e) { wings = false; wingsStarting = null; }
}
// the copy of the page, for the crossing: every reel strip definition (it
// carries functions; the reel's strips and its page's spec both hold it),
// wherever it is held, as the region and count it is made from, one stand-in
// for each so what was shared stays shared
function wingsFreeze(snap) {
  const seen = new Set(), stand = new Map();
  const walk = x => {
    if (x === null || typeof x !== 'object' || seen.has(x) || ArrayBuffer.isView(x)) return;
    seen.add(x);
    if (x instanceof Map || x instanceof Set) { for (const v of x.values()) walk(v); return; }
    for (const k of Object.keys(x)) {
      const v = x[k];
      if (v && typeof v === 'object' && typeof v.slot === 'function' && typeof v.rect === 'function') { if (!stand.has(v)) stand.set(v, { wingsStrip: [v.g, v.k] }); x[k] = stand.get(v); }
      else walk(v);
    }
  };
  walk(snap);
  return snap;
}
// and on the other side: the hives their class again, the strips their definitions
function wingsThaw(w) {
  const seen = new Set();
  const fix = x => {
    if (x === null || typeof x !== 'object' || seen.has(x) || ArrayBuffer.isView(x)) return;
    seen.add(x);
    if (x instanceof Map) { for (const [k, v] of x) { fix(k); fix(v); } return; }
    if (x instanceof Set) { for (const v of x) fix(v); return; }
    if (!Array.isArray(x) && 'solvedSubs' in x && 'bodies' in x) Object.setPrototypeOf(x, Hive.prototype);
    for (const k of Object.keys(x)) fix(x[k]);
  };
  fix(w);
  const made = new Map(), seen2 = new Set();
  const back = x => {
    if (x === null || typeof x !== 'object' || seen2.has(x) || ArrayBuffer.isView(x)) return;
    seen2.add(x);
    if (x instanceof Map || x instanceof Set) { for (const v of x.values()) back(v); return; }
    for (const k of Object.keys(x)) {
      const v = x[k];
      if (v && typeof v === 'object' && v.wingsStrip) { if (!made.has(v)) made.set(v, reelStrip(v.wingsStrip[0], v.wingsStrip[1], W, H, w.root.COLS, w.root.ROWS)); x[k] = made.get(v); }
      else back(v);
    }
  };
  back(w);
  return w;
}
// the worker's side: each round rehearsed as it comes, the answer handed back
function wingsServe() {
  self.onmessage = ev => {
    const m = ev.data;
    if (m.type !== 'round') return;
    W = m.env.W; H = m.env.H; Object.assign(config, m.env.config); mouseX = m.env.mouse[0]; mouseY = m.env.mouse[1];
    const t = performance.now();
    try {
      const snap = wingsThaw(m.snap), g = improvRound(snap, m.t0, m.a, m.dt, m.until);
      let r, frames = 0;
      while (!(r = g.next()).done) frames += r.value;
      self.postMessage(Object.assign({ type: 'answer', id: m.id, ms: performance.now() - t, frames }, r.value));
    } catch (e) { self.postMessage({ type: 'answer', id: m.id, ms: performance.now() - t, frames: 0, base: 0, chosen: 0, move: null, tried: 0, failed: String(e) }); }   // a round it could not rehearse: no move
  };
  self.postMessage({ type: 'ready' });
}
''' + s[b:]

# the page's thinking waits, not spins, while the worker has the round; and
# no failure in thinking stops the page: the thought is dropped, and if it
# was the worker's, the hive thinks on the page from then on
replace('''    const r = rehearsalJob.next();
    if (r.done) { rehearsalJob = null; break; }
    spent += r.value; rehearsalLog.frames++;''', '''    let r;
    try { r = rehearsalJob.next(); } catch (e) { rehearsalJob = null; rehearsing = false; if (wingsReady()) wings = false; break; }   // WINGS: a thought that fails is dropped, never the page
    if (r.done) { rehearsalJob = null; break; }
    if (r.value < 0) break;   // WINGS: the worker has the round; nothing to do here until it answers
    spent += r.value; rehearsalLog.frames++;''')

# the worker is started once the page is up; in the worker, this script serves
replace('''window.addEventListener('resize', resize);
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
''', '''window.addEventListener('resize', resize);
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
if (WINGS_OFFSTAGE) wingsServe(); else wingsStart();   // WINGS
''')

(ROOT / 'wings.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
