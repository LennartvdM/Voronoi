"""Build Shoal from Tandem: a group moves as one.

A scene change moves every cell from where it is to a place of the new
layout, and on Tandem the group came apart on the way. Who went where was the
matching of least squared travel, which cannot tell the inner cells of a turn
from the outer ones: turning a column into a row costs the same whoever goes
where, so the paths crossed. And each cell set off on its own clock, when a
wave from the pointer reached it, and took its own time, bent its own way, so
neighbours never moved together. Here who goes where is the matching of least
total travel, whose paths never cross (two that cross can always be swapped
for two shorter ones): on a turn the inner cells take the inner places and
the outer the outer. And every cell of a change sets off together and lands
together, on one clock, its path bent like every other's, so the group keeps
its order all the way: on a turn it wheels, the outer cells travelling
farther in the same time.

The stories (Tell, Tell II, Cue) keep their own choreography: while one is
told, a change is Tandem's.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'tandem.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'd891f8e3da06266b3b47ac6b6430c7bb677beae969f0b6a5da7485ef877fbe1b'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Tandem — Hive</title>', '<title>Shoal — Hive</title>')
replace('''&larr; Back · Tandem</a>''', '''&larr; Back · Shoal</a>''')
replace(''' · Tandem: a page opens all at once · click a hero or Escape for home</span>''',
        ''' · Tandem: a page opens all at once · Shoal: a group moves as one · click a hero or Escape for home</span>''')

# WHO GOES WHERE. The matching of least total travel, not least squared
# travel. Two paths that cross can always be swapped for two that do not,
# which are shorter together, so the least total travel never crosses: on a
# turn, the inner cells take the inner places and the outer the outer.
# Squared travel cannot tell them apart (turning a column into a row costs
# the same whoever goes where), and among matchings of the same total it is
# the tie-break, so a row shifting along steps every cell a little rather
# than one cell the length of the row. Found exactly (Kuhn-Munkres), with the
# page's image held to its slot, the rest matched around it, and any pair
# whose paths the tie-break let cross swapped back.
replace('''// Inset an outline by d without letting a feature shorter than d turn''', '''// SHOAL: whether a change moves as one group: not while a story is told,
// whose changes keep their own choreography
let shoalOn = false;
const SHOAL_TIE = 0.05;   // how much squared travel counts, beside total travel, to break its ties
function shoalAssign(points, stations, pin) {
  const nA = points.length, nS = stations.length, gotS = new Array(nA).fill(-1);
  let D = 1; for (const p of points.concat(stations)) D = Math.max(D, Math.hypot(p.x, p.y));
  const cost = (a, q) => { const d = Math.hypot(a.x - q.x, a.y - q.y); return d + SHOAL_TIE * d * d / D; };
  const rows = [], cols = [];
  for (let i = 0; i < nA; i++) if (i !== pin) rows.push(i);
  for (let j = 0; j < nS; j++) if (!(pin >= 0 && j === 0)) cols.push(j);
  if (pin >= 0) gotS[pin] = 0;   // the image takes the first slot
  const C = cols.map((j, r) => cols.map(jj => r < rows.length ? cost(points[rows[r]], stations[jj]) : 0));
  const a = shoalHungarian(C);
  rows.forEach((i, r) => { gotS[i] = cols[a[r]]; });
  shoalUncross(points, stations, gotS, pin);
  return gotS;
}
// the assignment of least cost in a square matrix: row i takes column a[i]
function shoalHungarian(C) {
  const n = C.length, u = new Array(n + 1).fill(0), v = new Array(n + 1).fill(0), p = new Array(n + 1).fill(0), way = new Array(n + 1).fill(0);
  for (let i = 1; i <= n; i++) {
    p[0] = i; let j0 = 0; const minv = new Array(n + 1).fill(Infinity), used = new Array(n + 1).fill(false);
    do {
      used[j0] = true; const i0 = p[j0]; let dl = Infinity, j1 = 0;
      for (let j = 1; j <= n; j++) if (!used[j]) { const cur = C[i0 - 1][j - 1] - u[i0] - v[j]; if (cur < minv[j]) { minv[j] = cur; way[j] = j0; } if (minv[j] < dl) { dl = minv[j]; j1 = j; } }
      for (let j = 0; j <= n; j++) if (used[j]) { u[p[j]] += dl; v[j] -= dl; } else minv[j] -= dl;
      j0 = j1;
    } while (p[j0] !== 0);
    do { const j1 = way[j0]; p[j0] = p[j1]; j0 = j1; } while (j0);
  }
  const a = new Array(n); for (let j = 1; j <= n; j++) a[p[j] - 1] = j - 1;
  return a;
}
// two paths that cross are swapped for the two that do not; the image keeps its slot
function shoalUncross(points, stations, gotS, pin) {
  const side = (p, q, r) => Math.sign((q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x));
  const crosses = (a, sa, b, sb) => side(a, sa, b) * side(a, sa, sb) < 0 && side(b, sb, a) * side(b, sb, sa) < 0;
  for (let pass = 0; pass < 50; pass++) {
    let swapped = false;
    for (let i = 0; i < gotS.length; i++) for (let j = i + 1; j < gotS.length; j++) {
      if (i === pin || j === pin) continue;
      if (crosses(points[i], stations[gotS[i]], points[j], stations[gotS[j]])) { const t = gotS[i]; gotS[i] = gotS[j]; gotS[j] = t; swapped = true; }
    }
    if (!swapped) break;
  }
}

// Inset an outline by d without letting a feature shorter than d turn''')
replace('''    const gotS = name === 'cue' && cue && cue.slotOf ? cueAssign(content, centers) : assignStations(content, centers);   // CUE: the engine's matching, under the pen's rules''',
        '''    shoalOn = !tell && !tell2 && !cue;   // SHOAL: a change moves as one group, but not while a story is told
    const gotS = name === 'cue' && cue && cue.slotOf ? cueAssign(content, centers) : shoalOn ? shoalAssign(content, centers, portalFocus && name in PORTAL_TEMPLATES ? content.indexOf(portalFocus) : -1) : assignStations(content, centers);   // CUE: the engine's matching, under the pen's rules''')

# ONE CLOCK, ONE BEND. Every cell of a change sets off together and lands
# together, and every path is bent alike (the swirl's own amount, no cell
# more or less), so neighbours move together all the way and the group keeps
# its order: matched without crossings, paths that start together and end
# together never meet. On a turn the group wheels, the outer cells going
# farther in the same time. The change takes as long as its longest journey
# needs, which is as long as a change took when that journey ran last.
replace('''    const bend = config.swirl * 0.55 * this.swirlSign * (0.7 + 0.6 * hash01(k, 12));''',
        '''    const bend = config.swirl * 0.55 * this.swirlSign * (shoalOn ? 1 : 0.7 + 0.6 * hash01(k, 12));   // SHOAL: every path bent alike''')
replace('''      dur: Math.min(2.2, 0.9 + dist / 520) * (0.9 + 0.2 * hash01(k, 13)),''',
        '''      dur: Math.min(2.2, 0.9 + dist / 520) * (shoalOn ? 1 : 0.9 + 0.2 * hash01(k, 13)),''')
replace('''      j.dur = Math.max(j.dur, o.journey.delay - j.delay + 0.9);
    }
''', '''      j.dur = Math.max(j.dur, o.journey.delay - j.delay + 0.9);
    }
    if (shoalOn) {   // SHOAL: one clock for the change: everyone sets off together and lands together
      const js = content.map(b => b.journey).filter(j => j && j.t0 === this.t);
      let dur = 0; for (const j of js) dur = Math.max(dur, j.dur);
      for (const j of js) { j.delay = 0; j.dur = dur; }
    }
''')

(ROOT / 'shoal.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
