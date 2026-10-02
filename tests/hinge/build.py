"""Build Hinge from Conveyor: Frame II's cells turn the corners as solid fronts.

On Conveyor's belt each cell's seed rides the band's centre line and the
auction cuts the band between the seeds. Along a straight that is a slice of
the band; round a corner it is not: a Voronoi cell slides round the bend a
part at a time, and the large cells drip round it.

Hinge draws the belt's cells as the band itself, cut by fronts.

- A front is a cut across the band at an area along the belt. On a straight it
  is square across the band. In a corner block it is a ray from the middle's
  corner, the hinge, and it swings clockwise from the cut of the side it comes
  from to the cut of the side it goes to.
- It swings by area: the block is the fan of its two outer edges about the
  hinge, and each edge holds one lattice unit of it, so the front sweeps the
  block at the belt's own pace.
- Each cell is the band between its two fronts, exactly, at its share of the
  band: a slice of a straight, a sector of a corner, or both, joined along the
  front they share. The cells tile the band.
- The fronts start where the cells sat: each cell's stretch is laid in the
  order the cells sat, as near the stretches they held at rest (read where
  they meet the page's edge) as the order allows.
- While the belt runs the cells are holes in the auction's ground, drawn
  exactly as cut, and the middle a wall: the auction has nothing to do.
- The cells come onto the belt from the shapes they rest in, as the belt gets
  up to speed: each is a blend from its resting shape to its stretch. A frame
  whose cells rest in slices of the band (every even count from eight, and
  four) hardly changes; at an odd count the cell in a corner of the frame,
  which no stretch can be, changes over the 3 s instead of in a frame.
- Any change stops the belt; the middle lets go at once, and the cells go
  back to the auction on the change's own clock, the one whitespace melts into
  the sea on. Each stays a hole whose shape goes, piece by piece, from its
  stretch to the cell the auction would give it (from a shadow auction run
  first in the frame, so it is this frame's cell), as far as the sea has come
  in. Where one comes in and another goes, the one coming in has the ground.
  When the sea is all in, halfway through the change, every cell is its
  auction cell, and they all close in one frame, the auction taking up the
  weights that drew them.
- While Frame II's cells are holes the auction's ground is its own box, with
  walls and holes as without them (a ground cut from the page alone lost the
  room the page's change may overflow into the frame the last wall or hole
  went), and on the way back, ground nobody bids for is whitespace, the sea's.

Everything else is Conveyor's to the bit.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'conveyor.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '915ce50299253f429c9f2d20a32fa792412c2088d8f07fb1d7b2409d18f142d5'
s = raw.decode()

def replace(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Conveyor — Hive</title>', '<title>Hinge — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Conveyor</a>', '<a class="back" href="index.html">&larr; Back · Hinge</a>')
replace("""const CONVEYOR = true;                              // CONVEYOR: Frame II, its cells going round the frame""",
"""const CONVEYOR = true;                              // CONVEYOR: Frame II, its cells going round the frame
const HINGE = true;                                 // HINGE: the belt's cells are the band between fronts, and turn its corners as solid fronts""")

# the band cut by fronts
replace("""// CONVEYOR: the belt starts once Frame II has landed: each cell a stretch as""", """// HINGE: THE BAND CUT BY FRONTS. A front at area u along the belt is a cut
// across the band: on a straight, square across it; in a corner block, a ray
// from the middle's corner, its hinge, swinging clockwise from the cut of the
// side it comes from to the cut of the side it goes to. It swings by area: the
// block is the fan of its two outer edges about the hinge, and each edge holds
// one lattice unit, so the front sweeps the block at the belt's own pace.
// slice(lo, hi): the band between the fronts at lo and hi, as its convex
// pieces in px, a front shared by two cells the same to the bit in both;
// uOf(p): the area along the belt of the front through p (px), or null at a
// hinge, which every front of its corner passes through.
function hingeBand(C, R, PW, PH) {
  const fan = (hinge, B) => ({ area: 2, hinge, B }), cut = (area, rect, u) => ({ area, rect, u });
  const pcs = [
    fan([2, 1], [[0, 1], [0, 0], [2, 0]]),
    cut(C - 4, (a0, a1) => [2 + a0, 0, 2 + a1, 1], (x, y) => x >= 2 && x <= C - 2 && y <= 1 ? x - 2 : null),
    fan([C - 2, 1], [[C - 2, 0], [C, 0], [C, 1]]),
    cut(2 * (R - 2), (a0, a1) => [C - 2, 1 + a0 / 2, C, 1 + a1 / 2], (x, y) => x >= C - 2 && y >= 1 && y <= R - 1 ? 2 * (y - 1) : null),
    fan([C - 2, R - 1], [[C, R - 1], [C, R], [C - 2, R]]),
    cut(C - 4, (a0, a1) => [C - 2 - a1, R - 1, C - 2 - a0, R], (x, y) => x >= 2 && x <= C - 2 && y >= R - 1 ? C - 2 - x : null),
    fan([2, R - 1], [[2, R], [0, R], [0, R - 1]]),
    cut(2 * (R - 2), (a0, a1) => [0, R - 1 - a1 / 2, 2, R - 1 - a0 / 2], (x, y) => x <= 2 && y >= 1 && y <= R - 1 ? 2 * (R - 1 - y) : null),
  ];
  let A = 0; for (const p of pcs) { p.u0 = A; A += p.area; }
  const Q = (p, a) => { const [B0, B1, B2] = p.B; return a < 1 ? [B0[0] + (B1[0] - B0[0]) * a, B0[1] + (B1[1] - B0[1]) * a] : [B1[0] + (B2[0] - B1[0]) * (a - 1), B1[1] + (B2[1] - B1[1]) * (a - 1)]; };
  const px = q => [q[0] * PW, q[1] * PH];
  const slice = (lo, hi) => {
    const out = [];
    for (let L = Math.floor(lo / A) - 1; L * A < hi; L++) for (const p of pcs) {
      const u0 = p.u0 + L * A, a0 = Math.max(lo, u0) - u0, a1 = Math.min(hi, u0 + p.area) - u0;
      if (!(a1 - a0 > 1e-9)) continue;
      let q;
      if (p.rect) { const r = p.rect(a0, a1); q = [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]]; }
      else { q = [p.hinge, Q(p, a0)]; if (a0 < 1 && a1 > 1) q.push(p.B[1]); q.push(Q(p, a1)); }
      out.push(q.map(px));
    }
    return out;
  };
  const uOf = q => {
    const x = q[0] / PW, y = q[1] / PH;
    for (const p of pcs) {
      if (p.rect) { const a = p.u(x, y); if (a !== null) return p.u0 + a; continue; }
      const [hx, hy] = p.hinge, dx = x - hx, dy = y - hy;
      if (Math.hypot(dx, dy) < 1e-3) return null;
      for (let k = 0; k < 2; k++) {
        const P0 = p.B[k], P1 = p.B[k + 1], ex = P1[0] - P0[0], ey = P1[1] - P0[1], cr = dx * ey - dy * ex;
        if (Math.abs(cr) < 1e-12) continue;
        const mu = (dx * (hy - P0[1]) - dy * (hx - P0[0])) / cr, lam = ((P0[0] - hx) * ey - (P0[1] - hy) * ex) / cr;
        if (mu >= -1e-9 && mu <= 1 + 1e-9 && lam >= 1 - 1e-9) return p.u0 + k + Math.min(1, Math.max(0, mu));
      }
    }
    return null;
  };
  return { A, slice, uOf };
}
// HINGE: the stretch of the belt a cell held at rest, read where its outline
// meets the page's edge: every front crosses the band to the edge, and there
// the area along the belt is as steady as the edge is long (by the hinge it is
// not: a corner's fronts all pass through it). Its middle, or null if it has
// no edge to read.
function hingeRest(band, b, W, H) {
  const us = [];
  for (const l of b.loops || []) for (const q of l) { if (Math.min(q[0], W - q[0], q[1], H - q[1]) > 0.5) continue; const u = band.uOf([Math.min(W, Math.max(0, q[0])), Math.min(H, Math.max(0, q[1]))]); if (u !== null) us.push(u); }
  if (!us.length) return null;
  const ref = us[0]; let lo = 0, hi = 0;
  for (const u of us) { let d = u - ref; d -= band.A * Math.round(d / band.A); lo = Math.min(lo, d); hi = Math.max(hi, d); }
  return ref + (lo + hi) / 2;
}
// CONVEYOR: the belt starts once Frame II has landed: each cell a stretch as""")

# the stretches: the band's, tiled, laid as the cells sat
replace("""  const cells = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.rect).map(b => ({ b, home: [b.x, b.y], a: Math.max(CLAIM_MIN, b.claim), at: belt.along([b.x, b.y]) }));
  if (!v || !cells.length) return;
  cells.sort((p, q) => p.at - q.at);
  let S = 0; for (const c of cells) { c.u = S + c.a / 2; S += c.a; }""", """  const band = HINGE ? hingeBand(C, R, root.PW, root.PH) : null;   // HINGE: the stretch each cell held at rest, where it can be read
  const cells = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.rect).map(b => { const at = band ? hingeRest(band, b, root.W, root.H) : null; return { b, home: [b.x, b.y], a: Math.max(CLAIM_MIN, b.claim), at: at !== null ? at : belt.along([b.x, b.y]) }; });
  if (!v || !cells.length) return;
  cells.sort((p, q) => p.at - q.at);
  if (band) { let T = 0; for (const c of cells) T += c.a; for (const c of cells) c.a *= belt.A / T; }   // HINGE: the cells tile the band, each at its share of it: its claim, as the frame's claims are the band
  let S = 0; for (const c of cells) { c.lo = S; c.u = S + c.a / 2; S += c.a; }
  if (band) for (let i = 0; i < cells.length; i++) cells[i].hi = i + 1 < cells.length ? cells[i + 1].lo : belt.A;   // HINGE: two cells share a front, to the bit""")
replace("""  for (const c of cells) c.u += off;
  v.conveyWall = true;""", """  for (const c of cells) { c.u += off; c.lo += off; if (band) c.hi += off; }
  v.conveyWall = true;""")
replace("""  convey = { serial: root.serial, belt, cells, t: 0, s: 0 };
}""", """  if (band) for (const c of cells) { const pts = (c.b.loops || []).flat(), hull = pts.length >= 3 ? convexHull(pts) : null; c.b.conveyIn = hull && hull.length >= 3 ? { from: hull, h: 0 } : null; }   // HINGE: the shape each cell rests in, which it leaves for its stretch as the belt gets up to speed
  convey = { serial: root.serial, belt, band, cells, t: 0, s: 0 };
}""")

# each frame: every cell the band between its fronts
replace("""    b.path = { sx: x, sy: y, cx: x, cy: y, ex: x, ey: y };
    b.x = x; b.y = y; b.vx = 0; b.vy = 0; b.journey = null; b.progress = 1;
  }
}""", """    b.path = { sx: x, sy: y, cx: x, cy: y, ex: x, ey: y };
    b.x = x; b.y = y; b.vx = 0; b.vy = 0; b.journey = null; b.progress = 1;
    if (convey.band) { b.conveyShape = convey.band.slice(c.lo + convey.s, c.hi + convey.s); if (b.conveyIn) { b.conveyIn.h = k; if (k >= 1) b.conveyIn = null; } }   // HINGE: the band between its fronts, reached from where it rested as the belt gets up to speed
  }
}""")

# a change hands each cell back to the auction as a closing hole
replace("""function conveyStop() {
  convey = null;""", """function conveyStop() {
  // HINGE: each cell goes back to the auction from the pieces it is drawn in
  if (convey) for (const c of convey.cells) { const b = c.b; if (!b.conveyShape) continue; const pieces = (b.conveyIn && b.hole ? b.hole.pieces : b.conveyShape).map(p => p.slice()); b.conveyIn = null; b.conveyShape = null; b.holeLinger = false; b.lingerTime = 0; b.holeCore = null; if (pieces.length) b.conveyBack = { pieces, to: null, h: 0 }; }
  convey = null;""")
# HINGE: the middle lets go at once: its whitespace goes into the auction, and the sea, with the cells' own way back
replace("""  for (const v of root.bodies) if (v.conveyWall) { if (v.conveyLeave) conveyRelease(v); else v.conveyLeave = root.serial + 1; }   // the change being laid; a second change lets go at once""", """  for (const v of root.bodies) if (v.conveyWall) { if (v.conveyLeave || HINGE) conveyRelease(v); else v.conveyLeave = root.serial + 1; }   // the change being laid; a second change lets go at once   // HINGE: the middle lets go at once, behind the cells' own way back""")
replace("""      if (b.conveyWall && b.conveyRect) { b.wall = b.conveyRect.slice(); this.walls.push(b); b.holeCore = null; continue; }""",
"""      if (b.conveyWall && b.conveyRect) { b.wall = b.conveyRect.slice(); this.walls.push(b); b.holeCore = null; continue; }
      if (b.conveyShape && b.conveyIn && this.depth === 0) {   // HINGE: a cell coming onto the belt: from the shape it rested in to its stretch (whose hull the middle's wall cuts back to it), as the belt gets up to speed
        const to = convexHull(b.conveyShape.flat()), hole = to && to.length >= 3 ? hingeBackHole(this, b, { from: b.conveyIn.from, to, h: b.conveyIn.h }) : null;
        if (hole) { b.hole = hole; b.holeCore = null; this.holes.push(b); continue; }
      }
      if (b.conveyShape && this.depth === 0) {   // HINGE: a cell on the belt is the band between its fronts, a hole drawn exactly as cut
        const P = b.conveyShape; let big = P[0], bigA = -1, x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
        for (const p of P) { const a = Math.abs(ringArea(p)); if (a > bigA) { bigA = a; big = p; } for (const q of p) { x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1]); } }
        b.hole = { pieces: P.slice(), planes: P.map(p => convexPlanes(p)), rect: [x0, y0, x1, y1], pts: big, raw: P.slice() }; b.holeCore = null; this.holes.push(b); continue;
      }
      if (b.conveyBack && this.depth === 0) { const hole = b.conveyBack.last || hingeBackHole(this, b); if (hole) { b.hole = hole; b.holeCore = null; this.holes.push(b); continue; } }   // HINGE: a cell going back to the auction, from its stretch to its auction cell as far as the sea has come in: as the frame before left it, until the frame's own shadow cuts it again""")

# the cells go back to the auction on the change's clock
replace("""function conveyFlow(dt) {
  if (!CONVEYOR) return;""", """// HINGE: THE CELLS GO BACK TO THE AUCTION ON THE CHANGE'S CLOCK. How far a cell
// has gone from its stretch to its auction cell is how far the sea has come in:
// 4p(1 - p) of the change's progress p, read off its paced travellers as the
// sea's is, until it is all in at p = 1/2 (with nothing paced, over MELT). Then
// every cell is its auction cell, and they all close in one frame, the auction
// taking up the weights that drew them.
function hingeBack(dt) {
  const back = root.bodies.filter(b => b.conveyBack);
  if (!back.length) return;
  let n = 0, P = 0;
  for (const b of root.bodies) if (!b.isVoid && !b.isSelf && !b.leaving && b.journey && b.journey.pace) { P += Math.max(0, Math.min(1, b.progress || 0)); n++; }
  const pc = n ? P / n : -1;
  for (const b of back) { const k = b.conveyBack; k.h = Math.min(1, Math.max(k.h, pc < 0 ? k.h + dt / MELT : pc < 0.5 ? 4 * pc * (1 - pc) : 1)); }
  if (back.every(b => b.conveyBack.h >= 1 - 1e-3)) { for (const b of back) b.conveyBack = null; root.conveyAdopt = true; }
}
// HINGE: a convex shape on its way from A to B: the blend of their supports, as
// Cohort's holes blend, and exactly B at 1
function hingeBlend(A, B, t, box) {
  const support = (P, nx, ny) => { let m = -Infinity; for (const p of P) m = Math.max(m, nx * p[0] + ny * p[1]); return m; };
  const planes = [];
  for (const P of [B, A]) for (const h of convexPlanes(P)) {
    const L = Math.hypot(h.ax, h.ay);
    if (L < 1e-9) continue;
    const nx = h.ax / L, ny = h.ay / L;
    planes.push({ ax: nx, ay: ny, b: (1 - t) * support(A, nx, ny) + t * support(B, nx, ny) });
  }
  return planesPoly(planes, box);
}
// HINGE: a convex polygon cut down to n corners, inside it: the corner whose
// triangle holds the least is cut off first
function hingeFew(P, n) {
  const q = P.slice();
  const tri = i => { const a = q[(i + q.length - 1) % q.length], b = q[i], c = q[(i + 1) % q.length]; return Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])); };
  while (q.length > n) { let best = 0, bv = Infinity; for (let i = 0; i < q.length; i++) { const v = tri(i); if (v < bv) { bv = v; best = i; } } q.splice(best, 1); }
  return q;
}
// HINGE: a cell between two shapes, as a hole: each convex piece of the shape it
// leaves on its way to the convex shape it goes to, the pieces kept apart, so it
// is exactly the one at 0 and exactly the other at 1, and never the hull of the
// first (a stretch round a corner is not convex: its hull holds the middle's)
function hingeBackHole(h, b, k = b.conveyBack) {
  const box = h.domainPts(), t = k.to ? k.h : 0;
  let P = [];
  for (const fp of k.pieces || [k.from]) {
    const q = hingeBlend(fp, k.to || fp, t, box);
    if (!q) continue;
    let parts = [q];
    for (const prev of P) { const pl = convexPlanes(prev), next = []; for (const x of parts) next.push(...subtractPlanes(x, pl)); parts = next; if (!parts.length) break; }
    for (const x of parts) if (x.length >= 3 && Math.abs(ringArea(x)) > 1e-3) P.push(x);
  }
  if (!P.length) return null;
  // in two tiers: the ground its auction cell will hold, and the ground it still
  // holds; every cell's first tier keeps apart before any second tier does. The
  // tiers only say who has the ground first, so the cell is read as a few-sided
  // polygon inside it: the fewer the sides, the fewer the pieces
  let tiers = [P, []];
  if (k.to && k.h > 0) {
    const tp = convexPlanes(hingeFew(k.to, 8)), near = [], far = [];
    for (const p of P) { let q = p; for (const t of tp) { q = clipPts(q, t.ax, t.ay, t.b); if (!q) break; } if (q && q.length >= 3 && Math.abs(ringArea(q)) > 1e-3) near.push(q); for (const o of subtractPlanes(p, tp)) if (o.length >= 3 && Math.abs(ringArea(o)) > 1e-3) far.push(o); }
    tiers = [near, far]; P = near.concat(far);
    if (!P.length) return null;
  }
  let big = P[0], bigA = -1, x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const p of P) { const a = Math.abs(ringArea(p)); if (a > bigA) { bigA = a; big = p; } for (const z of p) { x0 = Math.min(x0, z[0]); y0 = Math.min(y0, z[1]); x1 = Math.max(x1, z[0]); y1 = Math.max(y1, z[1]); } }
  return { pieces: P, planes: P.map(p => convexPlanes(p)), rect: [x0, y0, x1, y1], pts: big, raw: P.slice(), tiers };
}
function conveyFlow(dt) {
  if (!CONVEYOR) return;
  if (HINGE) hingeBack(dt);""")
# the shadow hands each its target; the auction takes up the shadow's weights when they close together
replace("""      const shape = parts.length ? cellCoreAndArms(parts, b.hole.rect) : null;
      if (!shape) { b.holeLinger = false; b.lingerTime = 0; continue; }""", """      const shape = parts.length ? cellCoreAndArms(parts, b.hole.rect) : null;
      if (b.conveyBack) { if (shape) { b.conveyBack.to = shape.core; b.conveyBack.sea = parts.flatMap(pc => pc.pts.map((p, i) => pc.labs && pc.labs[i] === SEA ? [p, pc.pts[(i + 1) % pc.pts.length]] : null).filter(Boolean)); } b.holeLinger = false; b.lingerTime = 0; b.holeCore = null; continue; }   // HINGE: a cell going back to the auction goes to the cell the auction would give it (and keeps where that cell meets the sea)
      if (!shape) { b.holeLinger = false; b.lingerTime = 0; continue; }""")
replace("""    if (this.shadowOn && !this.holes.length && this.shadowAt === this.shadowSig()) {""", """    const adopt = this.conveyAdopt; this.conveyAdopt = false;   // HINGE: the cells back from the belt close together, on the weights that drew them
    if (this.shadowOn && !this.holes.length && (this.shadowAt === this.shadowSig() || adopt)) {""")

# the ground with walls and holes is the auction's own box, as it is without them
replace("""    if (!poly) pieces = rects.length ? coverRects(0, 0, this.W, this.H, rects) : [[[0, 0], [this.W, 0], [this.W, this.H], [0, this.H]]];""", """    const [X0, Y0, X1, Y1] = this.hingeBox();   // HINGE: while Frame II's belt is in play, the box the cells may overflow into, with walls and holes as without
    if (!poly) pieces = rects.length ? coverRects(X0, Y0, X1, Y1, rects) : [[[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]];""")
replace("""    if (!pieces) pieces = [[[0, 0], [this.W, 0], [this.W, this.H], [0, this.H]]];""", """    if (!pieces) { const [X0, Y0, X1, Y1] = this.hingeBox(); pieces = [[[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]]; }   // HINGE: as the main auction's""")
replace("""  plBox() {
    const m = this.plM();""", """  // HINGE: THE GROUND IS THE AUCTION'S BOX, WITH WALLS AND HOLES AS WITHOUT. A
  // ground cut from the page alone gave the page's change, which may overflow
  // the screen, a third less room the frame its last wall or hole went, and
  // every cell grew by as much in one frame. Scoped to Frame II's belt and its
  // way back; everything else is Conveyor's.
  hingeBox() {
    if (HINGE && this.depth === 0 && this.bodies.some(b => b.conveyWall || b.conveyShape || b.conveyBack)) return this.plBox();
    return [0, 0, this.W, this.H];
  }
  plBox() {
    const m = this.plM();""")

# the holes kept apart, as a step of its own, so the cells going back can be cut again within the frame
replace("""    // Holes never overlap a wall or each other: a blend of two shapes can
    // bulge past both. The more settled keeps its shape; the other loses
    // exactly the overlap, as convex pieces, and nothing beyond it.
    this.holes.sort((a, b) => b.crystal - a.crystal);""", """    this.holesApart();
  }
  // Holes never overlap a wall or each other: a blend of two shapes can
  // bulge past both. The more settled keeps its shape; the other loses
  // exactly the overlap, as convex pieces, and nothing beyond it.
  holesApart() {   // HINGE: computeWalls' own last step, apart
    this.holes.sort((a, b) => b.crystal - a.crystal);""")
# the cells going back keep apart in their two tiers, before every other hole
replace("""    const placed = this.walls.map(w => { const r = w.wall; return [[{ ax: -1, ay: 0, b: -r[0] }, { ax: 1, ay: 0, b: r[2] }, { ax: 0, ay: -1, b: -r[1] }, { ax: 0, ay: 1, b: r[3] }]]; });
    const kept = [];
    for (const b of this.holes) {""", """    const placed = this.walls.map(w => { const r = w.wall; return [[{ ax: -1, ay: 0, b: -r[0] }, { ax: 1, ay: 0, b: r[2] }, { ax: 0, ay: -1, b: -r[1] }, { ax: 0, ay: 1, b: r[3] }]]; });
    const kept = [];
    // HINGE: THE CELLS GOING BACK FROM THE BELT KEEP APART IN TWO TIERS: first
    // the ground each one's auction cell will hold, then the ground each still
    // holds of its stretch. Where one cell comes in and another goes, the one
    // coming in has it.
    const back = HINGE ? this.holes.filter(b => (b.conveyBack || b.conveyIn) && b.hole.tiers) : [];
    if (back.length) {
      const cut = P => { for (const other of placed) { for (const op of other) { const next = []; for (const p of P) next.push(...subtractPlanes(p, op)); P = next; } if (!P.length) break; } return P.filter(p => p.length >= 3 && Math.abs(ringArea(p)) > 1e-3); };
      const got = new Map();
      for (const tier of [0, 1]) for (const b of back) { const P = b.hole.done ? (tier ? [] : b.hole.pieces) : cut(b.hole.tiers[tier]); got.set(b, (got.get(b) || []).concat(P)); if (P.length) placed.push(b.hole.done ? b.hole.planes : P.map(p => unit(convexPlanes(p)))); }   // a cell as the frame before left it is apart already
      for (const b of back) {
        const pieces = got.get(b);
        if (!pieces.length) { b.hole = null; b.holeCore = null; continue; }
        let big = pieces[0], bigA = 0;
        for (const p of pieces) { const a = Math.abs(ringArea(p)); if (a > bigA) { bigA = a; big = p; } }
        b.hole = { pieces, planes: b.hole.done ? b.hole.planes : pieces.map(p => unit(convexPlanes(p))), rect: b.hole.rect, pts: big, raw: b.hole.raw, tiers: b.hole.tiers, done: b.hole.done };
        b.holeExtra = []; kept.push(b);
      }
    }
    for (const b of this.holes) {
      if (back.includes(b)) continue;""")
# HINGE: the cells going back, cut again to this frame's targets, on the frame's own walls
replace("""  plBox() {
    const m = this.plM();""", """  // HINGE: the cells going back cut again, each to the cell this frame's shadow
  // gives it, on the walls the frame began with; every other hole as it was
  hingeRecut() {
    for (const b of this.holes) { const hole = b.conveyBack ? hingeBackHole(this, b) : null; b.hole = hole || { pieces: b.hole.raw.slice(), planes: b.hole.raw.map(convexPlanes), rect: b.hole.rect, pts: b.hole.pts, raw: b.hole.raw }; }
    this.holesApart();
    for (const b of this.holes) if (b.conveyBack) b.conveyBack.last = { ...b.hole, done: true };   // what the next frame begins with
  }
  plBox() {
    const m = this.plM();""")
# while the cells go back, each is this frame's: the shadow first, the holes cut to it, then the auction
replace("""  solve() {
    this.solveMain();
    this.solveShadow();
    this.recordAreas();
  }""", """  solve() {
    // HINGE: WHILE THE CELLS GO BACK FROM THE BELT, EACH IS THIS FRAME'S. The
    // shadow auction does not read the holes' shapes, only where they stand, so
    // it goes first; the cells going back are cut to the cells it gives them,
    // and the auction is held on what is left. A hole a frame behind its cell
    // would close a frame late, at the change's fastest.
    if (HINGE && this.depth === 0 && this.holes.some(b => b.conveyBack)) { this.solveShadow(); this.hingeRecut(); this.solveMain(); this.recordAreas(); return; }
    this.solveMain();
    this.solveShadow();
    this.recordAreas();
  }""")

# ground nobody bids for, while the belt's cells are holes, is whitespace
replace("""      if (this.holes.length) { this.ground = this.domainPieces(); if (this.ground) this.adoptGround(this.ground); }""", """      if (this.holes.length && !(HINGE && this.holes.some(b => b.conveyBack || (b.conveyShape && !b.conveyIn)))) { this.ground = this.domainPieces(); if (this.ground) this.adoptGround(this.ground); }   // HINGE: while the belt's cells are holes, ground nobody bids for is whitespace, the sea's""")

replace("""        if (!live2[k] && this.holes.length) { this.adoptGround(comp.groups[k].map(pi => pieces[pi])); comp.groups[k] = []; continue; }""", """        if (!live2[k] && this.holes.length && !(HINGE && this.holes.some(b => b.conveyBack || (b.conveyShape && !b.conveyIn)))) { this.adoptGround(comp.groups[k].map(pi => pieces[pi])); comp.groups[k] = []; continue; }   // HINGE: as above, a pocket nobody stands in is whitespace while the belt's cells are holes""")

replace("""    const active = subs.filter(s => claimOf(s) >= ACTIVE_MIN && !s.body.hole && !s.body.conveyWall);   // CONVEYOR: the frame's middle, a wall, bids nothing""", """    let active = subs.filter(s => claimOf(s) >= ACTIVE_MIN && !s.body.hole && !s.body.conveyWall);   // CONVEYOR: the frame's middle, a wall, bids nothing
    if (HINGE && this.depth === 0 && active.every(s => s.body.isVoid) && this.holes.some(b => b.conveyBack)) active = [];   // HINGE: while the cells go back, whitespace alone has nothing to draw; when they close, the auction takes up the shadow's weights, the whitespace's with them""")

out = ROOT / 'hinge.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
