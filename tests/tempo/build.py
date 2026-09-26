"""Build Tempo from Wings: a change paced by what happens in it.

Every change so far ran its cells' progress on easeInOutCubic: slow away,
three times the average speed at the middle, slow in. That is the right
pace for one thing crossing empty space, where the middle of the trip is the
dull part. A change of the page is not that. Per unit of its progress it is
about as busy all the way through, cells crossing and trading places, so the
ease crams what happens into the middle third, at up to three times its
average rate.

Here a change's clock is paced by what happens in it. At the click the
planned paths are measured: at each point of the change's progress, how
much there is to follow (every moving cell, and every pair of cells moving
against each other, the closer the more). The change is then run so that
what happens, not the distance, follows the smoothest rest-to-rest profile
there is (minimum jerk): slower where much happens, quicker where little
does, soft at both ends. The landing time is unchanged.

The move Improv makes (a cell's clock crawls, then hurries to land on time)
jumped its clock's rate twice: at once to a crawl, and at once to a hurry.
Here a move holds a cell's clock back by the same time, taken and given back
by minimum jerk, never slower than Improv's crawl, and given back no faster
than it was taken.

The header's captions are gone.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'wings.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '462bbd3059fbf3b693f69e8fd45ef6f3622f4e342b1e85626f964a723c6180ab'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Wings — Hive</title>', '<title>Tempo — Hive</title>')
a = s.index('''    <a class="back" href="index.html">&larr; Back · Wings</a> <span''')
b = s.index('''</span>''', a) + len('''</span>''')
s = s[:a] + '''    <a class="back" href="index.html">&larr; Back · Tempo</a>''' + s[b:]

# THE PACE: measured on the planned paths at the click, and run by the
# journey's own ease
replace('''function cueEase(j, u) { return j && j.cueBurst ?''', '''// TEMPO. HOW MUCH HAPPENS in a change at each point of its progress: every
// moving cell is one thing to follow, and every pair of cells moving against
// each other one more, the closer the more. Measured on the planned paths at
// the click, at PACE_NODES + 1 points of progress, and kept with the integral
// that makes the whole change one.
const PACE_NODES = 32;
function paceMinJerk(u) { return u * u * u * (10 + u * (-15 + 6 * u)); }   // the smoothest rest-to-rest profile: least jerk
function paceOf(h, js) {
  const cells = h.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving), N = PACE_NODES, L = Math.sqrt(h.PW * h.PH);
  const k = new Array(N + 1).fill(0), q = new Array(N + 1).fill(0);
  for (let n = 0; n <= N; n++) {
    const p = n / N, m = 1 - p, x = [], v = [];
    for (const b of cells) {
      const P = b.path;
      if (!P || !b.journey || !js.includes(b.journey)) { x.push([b.x, b.y]); v.push([0, 0]); continue; }   // a cell that stays is still there to pass
      x.push([m * m * P.sx + 2 * m * p * P.cx + p * p * P.ex, m * m * P.sy + 2 * m * p * P.cy + p * p * P.ey]);
      v.push([2 * m * (P.cx - P.sx) + 2 * p * (P.ex - P.cx), 2 * m * (P.cy - P.sy) + 2 * p * (P.ey - P.cy)]);
    }
    let s = 0;
    for (let i = 0; i < cells.length; i++) {
      s += Math.hypot(v[i][0], v[i][1]);
      for (let j = i + 1; j < cells.length; j++) s += Math.exp(-Math.hypot(x[i][0] - x[j][0], x[i][1] - x[j][1]) / L) * Math.hypot(v[i][0] - v[j][0], v[i][1] - v[j][1]);
    }
    k[n] = s;
  }
  for (let n = 1; n <= N; n++) q[n] = q[n - 1] + (k[n - 1] + k[n]) / (2 * N);
  if (!(q[N] > 1e-9)) return null;   // nothing moves
  return { k: k.map(x => x / q[N]), q: q.map(x => x / q[N]) };
}
// THE PACE: at its clock's u, the change has had paceMinJerk(u) of what
// happens in it, and its progress is wherever that is. What happens
// between the nodes is taken as straight, so its integral is a quadratic,
// solved exactly: the progress's speed has no step anywhere.
function paceAt(pc, u) {
  if (!(u > 0)) return 0; if (u >= 1) return 1;   // the ends exactly: a cell lands at 1, not a rounding short of it
  const Q = paceMinJerk(u), N = PACE_NODES, k = pc.k, q = pc.q;
  let n = 0; while (n < N - 1 && q[n + 1] < Q) n++;
  const a = (k[n + 1] - k[n]) / (2 * N), b = k[n] / N, c = q[n] - Q;   // Q = q[n] + b s + a s^2 across the node's span
  const s = Math.abs(a) < 1e-12 ? (b > 0 ? -c / b : 0) : (-b + Math.sqrt(Math.max(0, b * b - 4 * a * c))) / (2 * a);
  return Math.min(1, (n + Math.max(0, Math.min(1, s))) / N);
}
function cueEase(j, u) { return j && j.pace ? paceAt(j.pace, u) : j && j.cueBurst ?''')
replace('''      for (const j of js) { j.delay = 0; j.dur = dur; }
''', '''      for (const j of js) { j.delay = 0; j.dur = dur; }
      if (this === root && name !== 'cue' && name !== 'tell' && name !== 'tell2') { const pc = paceOf(this, js); if (pc) for (const j of js) j.pace = pc; }   // TEMPO: the page's own changes, paced by what happens in them; a story keeps its own
''')

# a retargeted cell finishes its old share on the old journey's clock, as it
# was running: its pace and its move
replace('''  return easeInOutCubic(Math.max(0, Math.min(1,
    (t-j.t0-j.delay-(j.hold || 0))/j.dur)));''', '''  if (j.pace) return paceAt(j.pace, Math.max(0, Math.min(1,
    (improvClock(j, t)-j.t0-j.delay-(j.hold || 0))/j.dur)));   // TEMPO: a paced change's, on its pace and its move
  return easeInOutCubic(Math.max(0, Math.min(1,
    (t-j.t0-j.delay-(j.hold || 0))/j.dur)));''')

# THE MOVE, SMOOTH: held back by the same time, taken and given back by
# minimum jerk, never slower than Improv's crawl
replace('''const IMPROV_SLOW = 0.3;          // s: a move: a cell's clock crawls this long from when the answer is in hand,
const IMPROV_CRAWL = 0.15;        // at this rate, then runs fast enough to land when it would have''', '''const IMPROV_CRAWL = 0.15;        // a move: a cell's clock runs no slower than this,
const IMPROV_HOLD = 0.3 * (1 - IMPROV_CRAWL);                  // s: and is held back this long (Improv's crawl of 0.3 s),
const IMPROV_SLOW = 1.875 * IMPROV_HOLD / (1 - IMPROV_CRAWL);  // s: taken by minimum jerk over this long, from when the answer is in hand; given back no faster''')
replace('''const IMPROV_DUE = Math.cbrt(0.05 / 4);   // of a journey: when easeInOutCubic has gone a twentieth of the way, and an answer is due''', '''const IMPROV_DUE = Math.cbrt(0.05 / 4);   // of a journey: when easeInOutCubic has gone a twentieth of the way, and an answer is due (TEMPO: a paced change, when its pace has)''')
replace('''// A JOURNEY'S OWN CLOCK: the page's, until a move slows it. From w.a it
// crawls for w.h at w.r, then runs fast enough to arrive when it would have.
function improvClock(j, t) {
  const w = j.warp; if (!w || t <= w.a) return t;
  const A = j.t0 + j.delay + (j.hold || 0) + j.dur, e = w.a + w.h, slow = w.a + (Math.min(t, e) - w.a) * w.r;
  if (t <= e) return slow;
  return Math.min(A, slow + (t - e) * (A - slow) / (A - e));
}''', '''// TEMPO: when an answer is due on a paced change: when its cells have gone a
// twentieth of their way on its pace
function paceDue(j) {
  if (!j.pace) return IMPROV_DUE;
  let lo = 0, hi = 1; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (paceAt(j.pace, m) < 0.05) lo = m; else hi = m; }
  return hi;
}
// A JOURNEY'S OWN CLOCK: the page's, until a move holds it back. From w.a it
// falls behind by w.d over w.h, and makes it up by the time it lands, both by
// minimum jerk: its rate never steps (TEMPO).
function improvClock(j, t) {
  const w = j.warp; if (!w || t <= w.a) return t;
  const A = j.t0 + j.delay + (j.hold || 0) + j.dur, e = w.a + w.h;
  if (t >= A) return t;
  return t - w.d * (t <= e ? paceMinJerk((t - w.a) / w.h) : 1 - paceMinJerk((t - e) / (A - e)));
}''')
replace('''  const D = Math.max(...trav0.map(b => { const j = b.journey; return j.delay + (j.hold || 0) + j.dur; })), due = IMPROV_DUE * D;''', '''  const D = Math.max(...trav0.map(b => { const j = b.journey; return j.delay + (j.hold || 0) + j.dur; })), due = paceDue(trav0[0].journey) * D;   // TEMPO''')
replace('''    if (!(F > 0) || frames < 2 || end - a < IMPROV_SLOW + 0.4) return;   // no time to think, or nothing left to change''', '''    if (!(F > 0) || frames < 2 || end - a < 2 * IMPROV_SLOW) return;   // no time to think, or nothing left to change (TEMPO: time to take and give back)''')
replace('''a + IMPROV_SLOW < arrives(b.journey) - 0.4 && arrives(b.journey) <= until; };   // a move whose whole consequence for its cell, the crawl and the catching up, the round has rehearsed''', '''a + 2 * IMPROV_SLOW <= arrives(b.journey) && arrives(b.journey) <= until; };   // a move whose whole consequence for its cell, the holding back and the making up, the round has rehearsed; made up no faster than held back (TEMPO)''')
replace('''moves.push({ id, a, h: IMPROV_SLOW, r: IMPROV_CRAWL })''', '''moves.push({ id, a, h: IMPROV_SLOW, d: IMPROV_HOLD })''')
replace('''b.journey.warp = { a: mv.a, h: mv.h, r: mv.r }''', '''b.journey.warp = { a: mv.a, h: mv.h, d: mv.d }''')
replace('''b.journey.warp = { a: res.move.a, h: res.move.h, r: res.move.r }''', '''b.journey.warp = { a: res.move.a, h: res.move.h, d: res.move.d }''')

(ROOT / 'tempo.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
