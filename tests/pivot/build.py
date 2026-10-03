"""Build Pivot from Conveyor: the belt as the auction's own state.

On Conveyor's belt each cell's seed rides the band's centre line and the
auction cuts the band between the seeds: square across a straight, and round
a corner a bisector that passes where the seeds' weights put it, not through
the corner the cells turn about, so a large cell slides round the bend a part
at a time. Hinge drew the cells as the band cut by fronts through the corner,
as holes in the auction's ground, and blended them on and off the belt; the
owner does not accept shapes authored and cut to fit.

Pivot places the sites so that the auction's own bisectors are the fronts.

- A front is a cut across the band at an area along the belt: square across a
  straight; in a corner block a ray from the middle's corner, the hinge, that
  swings round it by area. Each cell is the band between its two fronts.
- A cell is one site as long as its stretch holds at most one corner: a slice
  of a straight, or a slice with a corner (an L round the hinge, which one site
  draws, since the middle cuts the corner out of its convex cell). A longer
  cell is split across the middle of each straight it spans whole, so every
  part holds one corner at most; the seam inside a cell is invisible, and may
  be anywhere. (A cell split at the block's edge instead pins its sector's
  site to the next slice's line, where the auction cannot use it: tried, and
  not in.)
- The sites are placed so that every front is the bisector of the two sites
  it lies between: perpendicular to their difference, and, through a hinge, at
  equal power from it. A slice's site stays on the centre line and moves along
  it only as the loop's weights must close; a site with a corner goes where
  its two fronts put it; and no two sites come within 20 px of each other,
  which the fronts alone would allow, and which puts two cells' sites on one
  point.
  Two sites of one cell that come within 8 px are one site: their parts are
  joined, and the one site, free, serves both fronts. The weights follow from
  the fronts, and the auction, given
  those sites and weights, has nothing left to solve: its diagram is the band
  cut by fronts, to the precision of the arithmetic.
- The cells come onto the belt from where they rest: as the belt gets up to
  speed over 3 s, each cell's sites go from its resting site to their places
  and its claim is shared out to them, and the auction draws what it is given.
- The middle is a wall while the belt runs, as on Conveyor, and lets go as it
  did. Any change stops the belt; a cell's extra sites then drain into its
  first over the melt and leave the auction, which draws every frame.
- The auction's ground is the box less the walls, with a wall in the frame as
  without (Conveyor's was cut from the page with a wall in it, and the cells
  grew by a third in the frame the middle let go).

Nothing is a hole, nothing is blended, nothing is cut to fit. Everything else
is Conveyor's to the bit.

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

replace('<title>Conveyor — Hive</title>', '<title>Pivot — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Conveyor</a>', '<a class="back" href="index.html">&larr; Back · Pivot</a>')
replace("""const CONVEYOR = true;                              // CONVEYOR: Frame II, its cells going round the frame""",
"""const CONVEYOR = true;                              // CONVEYOR: Frame II, its cells going round the frame
const PIVOT = true;                                 // PIVOT: the belt's cells are the auction's own, their sites placed so the fronts are its bisectors
const PIVOT_APART = 20;                             // px: no two sites come closer than this""")

# the band's fronts, and the sites that make them the auction's bisectors
replace("""// CONVEYOR: the belt starts once Frame II has landed: each cell a stretch as""", """// PIVOT: THE BAND CUT BY FRONTS. A front at area u along the belt is a cut
// across the band: square across a straight; in a corner block a ray from the
// middle's corner, its hinge, swinging clockwise by area (the block is the fan
// of its two outer edges about the hinge, each edge one lattice unit of it).
// front(u): a point on it, its unit direction, and its hinge if it has one;
// slice(lo, hi): the band between two fronts, as convex pieces in px;
// parts(lo, hi): the stretch split across the middle of each straight it spans
// whole, so that each part holds one corner at most.
function pivotBand(C, R, PW, PH) {
  const fan = (hinge, B) => ({ area: 2, hinge, B }), cut = (area, rect) => ({ area, rect });
  const pcs = [
    fan([2, 1], [[0, 1], [0, 0], [2, 0]]),
    cut(C - 4, (a0, a1) => [2 + a0, 0, 2 + a1, 1]),
    fan([C - 2, 1], [[C - 2, 0], [C, 0], [C, 1]]),
    cut(2 * (R - 2), (a0, a1) => [C - 2, 1 + a0 / 2, C, 1 + a1 / 2]),
    fan([C - 2, R - 1], [[C, R - 1], [C, R], [C - 2, R]]),
    cut(C - 4, (a0, a1) => [C - 2 - a1, R - 1, C - 2 - a0, R]),
    fan([2, R - 1], [[2, R], [0, R], [0, R - 1]]),
    cut(2 * (R - 2), (a0, a1) => [0, R - 1 - a1 / 2, 2, R - 1 - a0 / 2]),
  ];
  let A = 0; for (const p of pcs) { p.u0 = A; A += p.area; }
  const Q = (p, a) => { const [B0, B1, B2] = p.B; return a < 1 ? [B0[0] + (B1[0] - B0[0]) * a, B0[1] + (B1[1] - B0[1]) * a] : [B1[0] + (B2[0] - B1[0]) * (a - 1), B1[1] + (B2[1] - B1[1]) * (a - 1)]; };
  const px = q => [q[0] * PW, q[1] * PH];
  const at = u => { const v = ((u % A) + A) % A; for (const p of pcs) if (v < p.u0 + p.area - 1e-12) return [p, v - p.u0]; return [pcs[0], 0]; };
  const front = u => {
    const [p, a] = at(u);
    if (p.rect) { const r0 = p.rect(a, a), r = p.rect(0, p.area), vert = Math.abs(r0[0] - r0[2]) < 1e-9; return { q: vert ? px([r0[0], (r[1] + r[3]) / 2]) : px([(r[0] + r[2]) / 2, r0[1]]), d: vert ? [0, 1] : [1, 0], hinge: null }; }
    const h = px(p.hinge), o = px(Q(p, a)), dx = o[0] - h[0], dy = o[1] - h[1], l = Math.hypot(dx, dy) || 1;
    return { q: h, d: [dx / l, dy / l], hinge: h };
  };
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
  const parts = (lo, hi) => {
    const pcsIn = []; let u = lo;   // the pieces the stretch runs through
    while (u < hi - 1e-9) { const [p, a] = at(u); const end = Math.min(hi, u + (p.area - a)); pcsIn.push({ lo: u, hi: end, p, whole: a < 1e-9 && end - u >= p.area - 1e-9 }); u = end; }
    const out = []; let cur = null, corners = 0;
    for (const q of pcsIn) {
      if (!cur) { cur = { lo: q.lo, hi: q.hi, corner: !q.p.rect, line: q.p.rect ? (Math.abs(q.p.rect(0, 0)[0] - q.p.rect(0, 0)[2]) < 1e-9 ? 'h' : 'v') : null }; continue; }
      if (!q.p.rect && cur.corner) {   // a second corner: cut across the middle of the straight before it (spanned whole, so the cut is inside the cell)
        const last = pcsIn[pcsIn.indexOf(q) - 1], mid = (last.lo + last.hi) / 2;
        out.push({ lo: cur.lo, hi: mid, kind: cur.corner ? 'free' : 'slice', line: cur.line });
        cur = { lo: mid, hi: q.hi, corner: true, line: last.p.rect ? (Math.abs(last.p.rect(0, 0)[0] - last.p.rect(0, 0)[2]) < 1e-9 ? 'h' : 'v') : null };
        continue;
      }
      cur.hi = q.hi; if (!q.p.rect) cur.corner = true;
    }
    if (cur) out.push({ lo: cur.lo, hi: cur.hi, kind: cur.corner ? 'free' : 'slice', line: cur.line });
    return out;
  };
  return { A, front, slice, parts };
}
// PIVOT: THE SITES THAT MAKE THE FRONTS THE AUCTION'S BISECTORS. Each cell's
// stretch is split at the band's pieces into parts (a part under PIVOT_MERGE
// folded into its neighbour), one site each. Every front, between consecutive
// sites round the loop, must be perpendicular to the two sites' difference; and
// round the loop the weight differences the fronts set (equal power at a point
// of each front) must sum to zero. A slice's site may move along its centre
// line, a sector's anywhere: the least such move from the centre line's point
// at each part's middle, by Gauss-Newton on the loop. The weights follow.
function pivotSites(band, belt, cells, s) {
  const sites = [];
  for (const c of cells) for (const p of band.parts(c.lo + s, c.hi + s)) sites.push({ cell: c, lo: p.lo, hi: p.hi, kind: p.kind, line: p.line, nat: belt.at((p.lo + p.hi) / 2), pieces: band.slice(p.lo, p.hi), area: 0 });
  const n = sites.length;
  if (!n) return sites;
  for (const st of sites) st.area = st.pieces.reduce((q, P) => q + Math.abs(ringArea(P)), 0);
  const F = sites.map(st => band.front(st.hi));
  // a slice moves along its line; a site with a corner anywhere
  const dof = [], cost = [];
  for (let i = 0; i < n; i++) { if (sites[i].kind === 'slice') { dof.push([i, sites[i].line === 'h' ? [1, 0] : [0, 1]]); cost.push(1); } else { dof.push([i, [1, 0]]); dof.push([i, [0, 1]]); cost.push(1); cost.push(1); } }
  const vec = ([, v]) => v;
  const a = sites.map(st => st.nat.slice());
  // the residuals: each front's perpendicularity, the loop's closure, and, for
  // every pair of sites closer than PIVOT_APART, how much closer
  const pairs = () => { const o = []; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (Math.hypot(a[j][0] - a[i][0], a[j][1] - a[i][1]) < PIVOT_APART) o.push([i, j]); return o; };
  const resid = (P) => {
    const r = [];
    for (let i = 0; i < n; i++) { const j = (i + 1) % n; r.push((a[j][0] - a[i][0]) * F[i].d[0] + (a[j][1] - a[i][1]) * F[i].d[1]); }
    let g = 0; for (let i = 0; i < n; i++) { const j = (i + 1) % n, q = F[i].q; g += (q[0] - a[j][0]) ** 2 + (q[1] - a[j][1]) ** 2 - (q[0] - a[i][0]) ** 2 - (q[1] - a[i][1]) ** 2; }
    r.push(g);
    for (const [i, j] of P || []) r.push(PIVOT_APART - Math.hypot(a[j][0] - a[i][0], a[j][1] - a[i][1]));
    return r;
  };
  const solve = (J, r) => {   // the least step, each move at its cost: C^-1 J^T (J C^-1 J^T)^-1 (-r)
    const m = J.length, k = J[0].length, M = Array.from({ length: m }, (_, i) => Array.from({ length: m }, (_, j) => J[i].reduce((q, v, t) => q + v * J[j][t] / cost[t], 0)));
    for (let i = 0; i < m; i++) M[i][i] += 1e-9;
    const b = r.map(v => -v);
    for (let i = 0; i < m; i++) {
      let p = i; for (let t = i + 1; t < m; t++) if (Math.abs(M[t][i]) > Math.abs(M[p][i])) p = t;
      [M[i], M[p]] = [M[p], M[i]]; [b[i], b[p]] = [b[p], b[i]];
      for (let t = i + 1; t < m; t++) { const f = M[t][i] / M[i][i]; for (let u = i; u < m; u++) M[t][u] -= f * M[i][u]; b[t] -= f * b[i]; }
    }
    const y = new Array(m).fill(0);
    for (let i = m - 1; i >= 0; i--) { let v = b[i]; for (let u = i + 1; u < m; u++) v -= M[i][u] * y[u]; y[i] = v / M[i][i]; }
    return Array.from({ length: k }, (_, t) => J.reduce((q, row, i) => q + row[t] * y[i], 0) / cost[t]);
  };
  let worst = Infinity;
  for (let it = 0; it < 60; it++) {
    const P = pairs(), r = resid(P); worst = Math.max(...r.map(Math.abs)); if (worst < 1e-9) break;
    const D = dof.map(vec), J = [];
    for (let i = 0; i < n; i++) { const j = (i + 1) % n; J.push(dof.map(([k], t) => ((k === j ? 1 : 0) - (k === i ? 1 : 0)) * (D[t][0] * F[i].d[0] + D[t][1] * F[i].d[1]))); }
    const g = sites.map(() => [0, 0]);
    for (let i = 0; i < n; i++) { const j = (i + 1) % n, q = F[i].q; g[j][0] += -2 * (q[0] - a[j][0]); g[j][1] += -2 * (q[1] - a[j][1]); g[i][0] += 2 * (q[0] - a[i][0]); g[i][1] += 2 * (q[1] - a[i][1]); }
    J.push(dof.map(([k], t) => g[k][0] * D[t][0] + g[k][1] * D[t][1]));
    for (const [i, j] of P) { const dx = a[j][0] - a[i][0], dy = a[j][1] - a[i][1], L = Math.hypot(dx, dy) || 1e-9, ux = dx / L, uy = dy / L; J.push(dof.map(([k], t) => ((k === i ? 1 : 0) - (k === j ? 1 : 0)) * (ux * D[t][0] + uy * D[t][1]))); }
    const d = solve(J, r);
    dof.forEach(([k], t) => { a[k][0] += d[t] * D[t][0]; a[k][1] += d[t] * D[t][1]; });
  }
  const w = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) { const j = i + 1, q = F[i].q; w[j] = w[i] + ((q[0] - a[j][0]) ** 2 + (q[1] - a[j][1]) ** 2) - ((q[0] - a[i][0]) ** 2 + (q[1] - a[i][1]) ** 2); }
  const base = -Math.min(...w);
  sites.forEach((st, i) => { st.x = a[i][0]; st.y = a[i][1]; st.w = w[i] + base; });
  sites.resid = Math.max(...resid(pairs()).map(Math.abs));   // how far the loop is from closing, for the validator
  return sites;
}
// CONVEYOR: the belt starts once Frame II has landed: each cell a stretch as""")

# the belt keeps the stretches' ends, and the band
replace("""  let S = 0; for (const c of cells) { c.u = S + c.a / 2; S += c.a; }""",
"""  if (PIVOT) { let T = 0; for (const c of cells) T += c.a; for (const c of cells) c.a *= belt.A / T; }   // PIVOT: the cells tile the band, each at its share of it: its claim, as the frame's claims are the band
  let S = 0; for (const c of cells) { c.lo = S; c.u = S + c.a / 2; S += c.a; }
  if (PIVOT) for (let i = 0; i < cells.length; i++) cells[i].hi = i + 1 < cells.length ? cells[i + 1].lo : belt.A;   // PIVOT: two cells share a front""")
replace("""  for (const c of cells) c.u += off;
  v.conveyWall = true;""", """  for (const c of cells) { c.u += off; c.lo += off; c.hi += off; }
  v.conveyWall = true;""")
replace("""  convey = { serial: root.serial, belt, cells, t: 0, s: 0 };
}""", """  convey = { serial: root.serial, belt, band: PIVOT ? pivotBand(C, R, root.PW, root.PH) : null, cells, t: 0, s: 0 };
}""")

# each frame: the sites, and how the cells come onto the belt
replace("""  for (const c of convey.cells) {
    const b = c.b; if (b.leaving) continue;
    const p = convey.belt.at(c.u + convey.s), x = c.home[0] + (p[0] - c.home[0]) * k, y = c.home[1] + (p[1] - c.home[1]) * k;
    b.path = { sx: x, sy: y, cx: x, cy: y, ex: x, ey: y };
    b.x = x; b.y = y; b.vx = 0; b.vy = 0; b.journey = null; b.progress = 1;
  }
}""", """  for (const c of convey.cells) {
    const b = c.b; if (b.leaving) continue;
    const p = convey.belt.at(c.u + convey.s), x = c.home[0] + (p[0] - c.home[0]) * k, y = c.home[1] + (p[1] - c.home[1]) * k;
    b.path = { sx: x, sy: y, cx: x, cy: y, ex: x, ey: y };
    b.x = x; b.y = y; b.vx = 0; b.vy = 0; b.journey = null; b.progress = 1;
  }
  // PIVOT: THE CELLS ARE THE AUCTION'S. Each frame every cell's sites are placed
  // so that the fronts are the auction's own bisectors, with the weights that
  // make them so. As the belt gets up to speed each cell's sites go from its
  // resting site to their places and its claim is shared out to them, and the
  // auction draws what it is given; at speed the weights are exact and it has
  // nothing left to solve. The first site is the cell's largest part.
  if (convey.band) {
    const sites = pivotSites(convey.band, convey.belt, convey.cells.filter(c => !c.b.leaving), convey.s), U = root.PW * root.PH;
    convey.sites = sites.length; convey.resid = sites.resid; convey.joins = sites.filter(st => st.kind === 'free').length;   // joins: the sites with a corner
    for (const c of convey.cells) {
      const b = c.b; if (b.leaving) continue;
      const own = sites.filter(st => st.cell === c); if (!own.length) { b.conveySites = null; continue; }
      let big = 0; for (let i = 1; i < own.length; i++) if (own[i].area > own[big].area) big = i;
      const order = [own[big], ...own.filter((_, i) => i !== big)], total = order.reduce((q, st) => q + st.area, 0) / U;
      b.conveySites = order.map((st, i) => {
        const share = Math.max(CLAIM_MIN, b.claim * st.area / U / Math.max(1e-9, total)), claim = i === 0 ? b.claim - (b.claim - share) * k : CLAIM_MIN + (share - CLAIM_MIN) * k;
        return { x: c.home[0] + (st.x - c.home[0]) * k, y: c.home[1] + (st.y - c.home[1]) * k, claim, w: k >= 1 ? st.w : undefined };
      });
    }
  }
}""")

# the sites placed, and how they drain when the belt stops
replace("""  placeSeeds() {
    for (const b of this.bodies) {
      if (b.formRect !== b.rect && b.crystal === 0) { b.formRect = b.rect; this.refreshFormation(b); }
      const s = b.subs[0];""", """  placeSeeds() {
    for (const b of this.bodies) {
      if (b.formRect !== b.rect && b.crystal === 0) { b.formRect = b.rect; this.refreshFormation(b); }
      if (PIVOT && b.conveySites && this.depth === 0) {   // PIVOT: a cell on the belt: its sites as the belt places them, with their weights when the belt is at speed
        const S = b.conveySites;
        while (b.subs.length < S.length) b.subs.push(makeSub(b, b.x, b.y));
        b.subs.length = S.length;
        S.forEach((st, i) => { const q = b.subs[i]; q.x = st.x; q.y = st.y; q.claim = st.claim; if (st.w !== undefined) { q.w = st.w; q.live = true; } });
        continue;
      }
      if (PIVOT && b.conveyDrain && this.depth === 0) {   // PIVOT: a cell back from the belt: its extra sites, carried along, draining into its first
        const D = b.conveyDrain, f = Math.max(0, 1 - D.t / MELT);
        let extra = 0;
        D.subs.forEach((d, i) => { const q = b.subs[i + 1]; if (!q) return; q.x = b.x + d.dx; q.y = b.y + d.dy; q.claim = d.claim * f; extra += q.claim; });
        const s0 = b.subs[0]; s0.x = b.x; s0.y = b.y; s0.claim = Math.max(CLAIM_MIN, b.claim * (1 + (config.hoverBoost - 1) * b.hoverMix) - extra);
        continue;
      }
      const s = b.subs[0];""")
replace("""function conveyStop() {
  convey = null;""", """function conveyStop() {
  // PIVOT: the cells go back to the auction as they are: each keeps its sites,
  // the first where its body is, the others carried along and draining into
  // the first over the melt
  if (convey && convey.band) for (const c of convey.cells) { const b = c.b, S = b.conveySites; b.conveySites = null; if (!S || !S.length) continue;
    b.x = S[0].x; b.y = S[0].y; b.path = { sx: b.x, sy: b.y, cx: b.x, cy: b.y, ex: b.x, ey: b.y };
    b.conveyDrain = S.length > 1 ? { t: 0, subs: S.slice(1).map(st => ({ dx: st.x - b.x, dy: st.y - b.y, claim: st.claim })) } : null; }
  convey = null;""")
replace("""function conveyFlow(dt) {
  if (!CONVEYOR) return;""", """// PIVOT: the extra sites of a cell back from the belt drain over the melt, and
// leave the auction when they are too small to see
function pivotDrain(dt) {
  for (const b of root.bodies) {
    const D = b.conveyDrain; if (!D) continue;
    D.t += dt;
    if (D.t >= MELT || D.subs.every(d => d.claim * Math.max(0, 1 - D.t / MELT) < ACTIVE_MIN)) { b.subs.length = 1; b.conveyDrain = null; }
  }
}
function conveyFlow(dt) {
  if (!CONVEYOR) return;
  if (PIVOT) pivotDrain(dt);""")
# a draining cell keeps its sites through a formation change
replace("""  refreshFormation(b) {
    // A root void's sites are its current geometry. Clearing its destination""", """  refreshFormation(b) {
    if (PIVOT && b.conveyDrain) return;   // PIVOT: a cell back from the belt keeps its sites while they drain
    // A root void's sites are its current geometry. Clearing its destination""")
# the wall's body never carries belt sites
replace("""  v.conveyWall = true; v.conveyRect = [mid[0] * root.PW, mid[1] * root.PH, mid[2] * root.PW, mid[3] * root.PH]; v.conveyMid = v.conveyRect.slice();""",
"""  v.conveyWall = true; v.conveyRect = [mid[0] * root.PW, mid[1] * root.PH, mid[2] * root.PW, mid[3] * root.PH]; v.conveyMid = v.conveyRect.slice();
  for (const c of cells) { c.b.conveySites = null; c.b.conveyDrain = null; }   // PIVOT: fresh""")

# the whitespace's site-placing leaves a belt cell's sites alone
replace("""    if (!b.isSelf && (b.formRect || b.rect || (b.isVoid && b.plCurrent))) live.push(b);""",
"""    if (PIVOT && (b.conveySites || b.conveyDrain)) continue;   // PIVOT: a cell on the belt, or back from it, places its own sites
    if (!b.isSelf && (b.formRect || b.rect || (b.isVoid && b.plCurrent))) live.push(b);""")

# the ground is the box less the walls, with a wall in the frame as without
replace("""    if (!poly) pieces = rects.length ? coverRects(0, 0, this.W, this.H, rects) : [[[0, 0], [this.W, 0], [this.W, this.H], [0, this.H]]];""",
"""    const [X0, Y0, X1, Y1] = PIVOT && this.depth === 0 ? this.plBox() : [0, 0, this.W, this.H];   // PIVOT: the ground is the box the cells may overflow into, less the walls, with a wall in the frame as without
    if (!poly) pieces = rects.length ? coverRects(X0, Y0, X1, Y1, rects) : [[[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]];""")
replace("""    if (!pieces) pieces = [[[0, 0], [this.W, 0], [this.W, this.H], [0, this.H]]];""",
"""    if (!pieces) { const [X0, Y0, X1, Y1] = PIVOT && this.depth === 0 ? this.plBox() : [0, 0, this.W, this.H]; pieces = [[[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]]; }   // PIVOT: as the main auction's""")

# while the cells come onto the belt the auction takes its full stride: sites and claims move fast, and three steps fall behind
replace("""  iterBudget() {""", """  iterBudget() {
    if (PIVOT && this.depth === 0 && convey && convey.t < CONVEY_EASE) return 8;   // PIVOT: the cells coming onto the belt: their sites and claims move, and the auction keeps up
""")

out = ROOT / 'pivot.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
