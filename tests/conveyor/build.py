"""Build Conveyor from Cohort: Frame II, the frame as a conveyor.

A new scene, Frame II, beside Frame. It lands exactly as Frame does: the
cells round the edge of the page, the whitespace in the middle. Once it has
landed, the cells go round the frame clockwise, gently, and keep going.

- The belt is the frame's band, read clockwise from the top left corner as
  eight pieces: four straights and four corners. Each piece is measured by its
  area, in lattice units, and holds a stretch of the band's centre line: a
  straight one, or at a corner a quarter of an ellipse from one side's centre
  line to the next's.
- A cell holds a stretch of the belt as long as its own area, the stretches
  one after another in the order the cells sat. The belt moves by area: a
  walking pace (the reel's, 28 px/s) where the band is one row deep, at the top
  and the bottom, and slower where it is two columns wide, down the sides, as a
  stream runs slower where its bed is wide.
- Each cell's seed is the centre line's point at the middle of its stretch,
  held there exactly, and the auction gives every cell its own area, as
  ever. Along a straight the cells are slices of the band, and round a corner
  they turn it as Voronoi cells do.
- The middle is whitespace a cell never enters: while the belt runs it is a
  wall, out of the auction, drawn exactly as its rectangle.
- The belt gets up to speed over 3 s, and the seeds go from where they sat to
  the belt's line over the same, so the frame at rest is where it starts.
- Any change stops it, and the cells go on from where they are. If the
  middle's whitespace leaves, the wall stays as its own cell while it melts
  into the sea, shrinking about its centre as the whitespace's own share does
  on the change's clock, and lets go when that is gone; the cells flow into the
  room it gives up and nothing jumps. If the whitespace goes on to a place in
  the next layout, the wall lets go at once.

Every other scene, the pages and the stories are Cohort's to the bit.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cohort.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d'
s = raw.decode()

def replace(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Cohort — Hive</title>', '<title>Conveyor — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Cohort</a>', '<a class="back" href="index.html">&larr; Back · Conveyor</a>')
replace("""      <button class="scene-btn" data-scene="frame">Frame</button>""",
"""      <button class="scene-btn" data-scene="frame">Frame</button>
      <button class="scene-btn" data-scene="frame2">Frame II</button>""")
replace("""const COHORT = true;                                // COHORT: from page to page, the gallery is one body""",
"""const COHORT = true;                                // COHORT: from page to page, the gallery is one body
const CONVEYOR = true;                              // CONVEYOR: Frame II, its cells going round the frame""")

# Frame II lands as Frame
replace("""    if (this.depth===0 && (this.scene==='hero'||this.scene==='frame')) this.mfResize=true;""",
"""    if (this.depth===0 && (this.scene==='hero'||this.scene==='frame'||this.scene==='frame2')) this.mfResize=true;   // CONVEYOR: Frame II is Frame's""")
replace("""    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) :""",
"""    const spec = this.depth===0 && (name==='hero'||name==='frame'||name==='frame2') ? mfScene(this,name==='frame2'?'frame':name,content.length) :""")
replace("""  frame(C, R, n) {
    const ring = [""", """  frame2(C, R, n) { return scenes.frame(C, R, n); },   // CONVEYOR: Frame II's rest is Frame's
  frame(C, R, n) {
    const ring = [""")

# the middle is a wall while the belt runs, and bids nothing
replace("""      const r = b.formRect;
      if (b.isSelf || !r) { b.holeCore = null; continue; }""", """      if (b.conveyWall && b.conveyRect) { b.wall = b.conveyRect.slice(); this.walls.push(b); b.holeCore = null; continue; }   // CONVEYOR: the frame's middle is a wall while the belt runs, and while Frame II is left, whatever else it is
      const r = b.formRect;
      if (b.isSelf || !r) { b.holeCore = null; continue; }""")
replace("""    const active = subs.filter(s => claimOf(s) >= ACTIVE_MIN && !s.body.hole);""",
"""    const active = subs.filter(s => claimOf(s) >= ACTIVE_MIN && !s.body.hole && !s.body.conveyWall);   // CONVEYOR: the frame's middle, a wall, bids nothing""")

# the belt
replace("""// the reel: the open page's strips, their cards and their scroll""", """// CONVEYOR: FRAME II'S BELT. The frame's band read clockwise from its top
// left corner, as eight pieces, each its area in lattice units and the stretch
// of the band's centre line it holds: a straight holds a straight one, a
// corner a quarter of an ellipse from one side's centre line to the next's.
// at(u): the centre line's point at area u along the belt (u wraps round);
// along(p): the area along the belt of the centre line's point nearest p.
const CONVEY_PACE = 28;   // px/s where the band is one row deep: the reel's own pace
const CONVEY_EASE = 3;    // s: the belt gets up to speed over this, and the seeds onto its line
let convey = null;        // the running belt: its cells, their stretches, how far it has gone
function conveyBelt(C, R, PW, PH) {
  const line = (a, b) => [a, b].map(p => [p[0] * PW, p[1] * PH]);
  const quarter = (cx, cy, f0, f1) => Array.from({ length: 33 }, (_, i) => { const f = f0 + (f1 - f0) * i / 32; return [(cx + Math.cos(f)) * PW, (cy + 0.5 * Math.sin(f)) * PH]; });
  const pcs = [
    { area: 2, pts: quarter(2, 1, Math.PI, 1.5 * Math.PI) },               // top left: up from the left side's line into the top's
    { area: C - 4, pts: line([2, 0.5], [C - 2, 0.5]) },
    { area: 2, pts: quarter(C - 2, 1, 1.5 * Math.PI, 2 * Math.PI) },
    { area: 2 * (R - 2), pts: line([C - 1, 1], [C - 1, R - 1]) },
    { area: 2, pts: quarter(C - 2, R - 1, 0, 0.5 * Math.PI) },
    { area: C - 4, pts: line([C - 2, R - 0.5], [2, R - 0.5]) },
    { area: 2, pts: quarter(2, R - 1, 0.5 * Math.PI, Math.PI) },
    { area: 2 * (R - 2), pts: line([1, R - 1], [1, 1]) },
  ];
  let A = 0;
  for (const p of pcs) {
    p.u0 = A; A += p.area;
    p.cum = [0]; for (let i = 1; i < p.pts.length; i++) p.cum.push(p.cum[i - 1] + Math.hypot(p.pts[i][0] - p.pts[i - 1][0], p.pts[i][1] - p.pts[i - 1][1]));
    p.len = p.cum[p.cum.length - 1];
  }
  const at = u => {
    u = ((u % A) + A) % A;
    let p = pcs[pcs.length - 1]; for (const q of pcs) if (u < q.u0 + q.area) { p = q; break; }
    const L = Math.min(1, Math.max(0, (u - p.u0) / p.area)) * p.len;
    let i = 1; while (i < p.cum.length - 1 && p.cum[i] < L) i++;
    const f = (L - p.cum[i - 1]) / Math.max(1e-9, p.cum[i] - p.cum[i - 1]), a = p.pts[i - 1], b = p.pts[i];
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
  };
  const along = q => {
    let best = Infinity, u = 0;
    for (const p of pcs) for (let i = 1; i < p.pts.length; i++) {
      const a = p.pts[i - 1], b = p.pts[i], ex = b[0] - a[0], ey = b[1] - a[1], L2 = ex * ex + ey * ey || 1e-9;
      const t = Math.max(0, Math.min(1, ((q[0] - a[0]) * ex + (q[1] - a[1]) * ey) / L2)), d = Math.hypot(a[0] + t * ex - q[0], a[1] + t * ey - q[1]);
      if (d < best) { best = d; u = p.u0 + p.area * (p.cum[i - 1] + t * (p.cum[i] - p.cum[i - 1])) / p.len; }
    }
    return u;
  };
  return { A, at, along };
}
// CONVEYOR: the belt starts once Frame II has landed: each cell a stretch as
// long as its area, one after another in the order the cells sit round the
// frame, placed as near their seats as the order allows; the middle a wall
function conveyStart() {
  const C = root.COLS, R = root.ROWS, mid = [2, 1, C - 2, R - 1];
  if (C < 5 || R < 3) return;
  const belt = conveyBelt(C, R, root.PW, root.PH);
  const v = root.bodies.find(b => b.isVoid && !b.leaving && b.rect && rectsEqual(b.rect, mid));
  const cells = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.rect).map(b => ({ b, home: [b.x, b.y], a: Math.max(CLAIM_MIN, b.claim), at: belt.along([b.x, b.y]) }));
  if (!v || !cells.length) return;
  cells.sort((p, q) => p.at - q.at);
  let S = 0; for (const c of cells) { c.u = S + c.a / 2; S += c.a; }
  let dx = 0, dy = 0; for (const c of cells) { let d = c.at - c.u; d -= belt.A * Math.round(d / belt.A); dx += Math.cos(2 * Math.PI * d / belt.A); dy += Math.sin(2 * Math.PI * d / belt.A); }
  const off = Math.atan2(dy, dx) * belt.A / (2 * Math.PI);   // the order's best fit to the seats, by the circular mean
  for (const c of cells) c.u += off;
  v.conveyWall = true; v.conveyRect = [mid[0] * root.PW, mid[1] * root.PH, mid[2] * root.PW, mid[3] * root.PH]; v.conveyMid = v.conveyRect.slice();
  convey = { serial: root.serial, belt, cells, t: 0, s: 0 };
}
// CONVEYOR: a change stops the belt. If the middle's whitespace leaves, the
// wall is its own cell as it melts into the sea: it shrinks about its centre to
// the share of the whitespace that is still its own (Cohort's melt, on the
// change's clock), and lets go when that is gone. If the whitespace goes on to
// a place in the next layout, the wall lets go at once.
// What it is doing lives on the middle's own body, so a rehearsal of the
// change, which copies the page, plays it too.
function conveyStop() {
  convey = null;
  for (const v of root.bodies) if (v.conveyWall) { if (v.conveyLeave) conveyRelease(v); else v.conveyLeave = root.serial + 1; }   // the change being laid; a second change lets go at once
}
function conveyRelease(v) { v.conveyWall = false; v.conveyRect = null; v.conveyMid = null; v.conveyLeave = 0; }   // the middle bids again
function conveyLeave(v) {
  if (root.serial !== v.conveyLeave || !v.leaving) { conveyRelease(v); return; }
  const f = root.seaBeta(v), m = v.conveyMid, cx = (m[0] + m[2]) / 2, cy = (m[1] + m[3]) / 2, k = Math.sqrt(f);
  if (f < 1e-3) { conveyRelease(v); return; }
  v.conveyRect = [cx + (m[0] - cx) * k, cy + (m[1] - cy) * k, cx + (m[2] - cx) * k, cy + (m[3] - cy) * k];
}
// CONVEYOR: each frame the belt moves on by its pace, and every seed is held
// on the belt's line at the middle of its cell's stretch
function conveyFlow(dt) {
  if (!CONVEYOR) return;
  for (const v of root.bodies) if (v.conveyWall && v.conveyLeave) { conveyLeave(v); return; }
  if (convey && (root.serial !== convey.serial || config.scene !== 'frame2')) { conveyStop(); for (const v of root.bodies) if (v.conveyWall) conveyLeave(v); return; }
  if (!convey && config.scene === 'frame2' && guestLeft <= 0 && !rehearsing && root.conveyAt !== root.serial) { root.conveyAt = root.serial; conveyStart(); }
  if (!convey) return;
  convey.t += dt;
  const k = S3(convey.t / CONVEY_EASE);
  convey.s += k * CONVEY_PACE / root.PW * dt;   // area per second: one row deep, a lattice unit is a column's width along the belt
  for (const c of convey.cells) {
    const b = c.b; if (b.leaving) continue;
    const p = convey.belt.at(c.u + convey.s), x = c.home[0] + (p[0] - c.home[0]) * k, y = c.home[1] + (p[1] - c.home[1]) * k;
    b.path = { sx: x, sy: y, cx: x, cy: y, ex: x, ey: y };
    b.x = x; b.y = y; b.vx = 0; b.vy = 0; b.journey = null; b.progress = 1;
  }
}
// the reel: the open page's strips, their cards and their scroll""")
replace("""  reelFlow(dt);
  reelStep();
""", """  reelFlow(dt);
  reelStep();
  conveyFlow(dt);   // CONVEYOR
""")
# leaving Frame II, the sea takes the middle's whitespace as the wall gives it up
replace("""    if (b.isSelf || b.wall || !b.isVoid) return 0;
    const c = Math.max(0, b.claim);""", """    if (b.conveyWall && b.wall && b.leaving && this.depth === 0) return Math.max(0, b.claim) * (1 - this.seaBeta(b));   // CONVEYOR: the middle leaving: its wall is its own cell, and the rest is the sea's, as any whitespace's
    if (b.isSelf || b.wall || !b.isVoid) return 0;
    const c = Math.max(0, b.claim);""")
# any change stops the belt first, so the change finds the middle whitespace again
replace("""const plOldPlace = Hive.prototype.placeSeeds;""", """// CONVEYOR: a change stops the belt before it is laid
const conveyEnter = Hive.prototype.enterScene;
Hive.prototype.enterScene = function (name, origin) {
  if (this.depth === 0 && (convey || this.bodies.some(v => v.conveyWall))) conveyStop();
  return conveyEnter.call(this, name, origin);
};
const plOldPlace = Hive.prototype.placeSeeds;""")

out = ROOT / 'conveyor.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
