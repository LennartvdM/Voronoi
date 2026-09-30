"""Build Amoeba from Membrane: the hive is one body.

Membrane cut every travelling cell by its own reach, a disc about its seed,
so wherever a cell's ground reached further than its disc the sea took it:
its outer side, and every corner where it met its neighbours. Cells on the
hive's edge went round, and the sea showed through between them. Its rules
also ran on clocks of their own, from the ask: a leaving whitespace melted
into the sea over 0.3 s, and the page's hero gave up its share of the text's
room in the first frame. A change broke the page's structure at once, and
then moved.

Here the hive bids as one body. At a point, its presence is the sum over its
cells of exp(-bid / T), T = 2 r² with r the cell's own radius, and the sea
wins where the presence is below one. A cell alone is still exactly its disc,
and the auction is still exact; but cells side by side are one hill, so the
notches between them and the holes where three reaches failed to meet are
the hive's. Only the hive's rim meets the sea, as one smooth edge, and every
cell inside is a polygon.

And everything the sea does runs on the change's own clock:
- a cell is liquid as far as it is between its two rests, 4p(1 - p), and the
  whitespace melts into the sea by the same measure of the change's progress;
- only a cell has a reach (whitespace that is still its own cell keeps its
  straight borders), and a sea too small to see appear stays out, as a seed
  does;
- the hero gives back what it holds of the text's room at the ask on its own
  clock, no faster than it leaves it.

The hive keeps its size: nothing is given to the sea but whitespace.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'membrane.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'ace6b09cbad969678114efa8cfd7df089c014b24618a7a879aa38434a0efcd68'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Membrane — Hive</title>', '<title>Amoeba — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Membrane</a>', '<a class="back" href="index.html">&larr; Back · Amoeba</a>')

SOFT = r"""// AMOEBA: THE SEA IS SOFT. The sea bids zero everywhere, and a cell's bid
// at a point is its power there, as ever; but the hive bids as one body: at
// a point, its presence is the sum over its cells of exp(-bid / T), and the
// sea wins where that presence is below one. A cell alone is exactly its
// disc (its bid is zero at its reach). Cells side by side are one body: the
// notches between their reaches, and the holes where three reaches failed to
// meet, are the hive's. T is 2 r², r the cell's own radius: a bell as wide as
// the cell, so two cells that touch are one hill, never two.
const SEA_SOFT_CAP = 50;   // an exponent past which a point is inside by any measure
const SEA_SEAM = -3001;   // label of a side between two squares of one cell's cut: inside it
// a half-plane cut whose new points are found the same way from either side
// of an edge two pieces share, so the pieces meet exactly
function seaClip(poly, ax, ay, b, lab) {
  const pts = poly.pts, labs = poly.labs, n = pts.length, oP = [], oL = [];
  const at = (A, B) => { const lo = A[0] < B[0] || (A[0] === B[0] && A[1] < B[1]), P = lo ? A : B, Q = lo ? B : A, pv = ax * P[0] + ay * P[1] - b, qv = ax * Q[0] + ay * Q[1] - b, t = pv / (pv - qv); return [P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])]; };
  let A = pts[n - 1], aL = labs[n - 1], av = ax * A[0] + ay * A[1] - b;
  for (let k = 0; k < n; k++) {
    const B = pts[k], bL = labs[k], bv = ax * B[0] + ay * B[1] - b;
    if (av <= 0) { if (bv <= 0) { oP.push(B); oL.push(bL); } else { oP.push(at(A, B)); oL.push(lab); } }
    else if (bv <= 0) { oP.push(at(A, B)); oL.push(aL); oP.push(B); oL.push(bL); }
    A = B; aL = bL; av = bv;
  }
  return { pts: oP, labs: oL };
}
// the outline of a cell the hive's edge cuts: its pieces' edges less the
// seams between them (the grid's are labelled so; the ground's own are met
// from both sides), chained end to end. Every loop is kept, the largest first.
function seaOutline(pieces) {
  const key = p => p[0] + ',' + p[1], edges = [], wall = new Set();
  for (const { pts, labs } of pieces) for (let k = 0, m = pts.length; k < m; k++) {
    if (labs[k] === SEA_SEAM) continue;
    const a = pts[k], b = pts[k + 1 === m ? 0 : k + 1], ka = key(a), kb = key(b);
    if (ka === kb) continue;
    edges.push({ a, b, lab: labs[k], ka, kb, used: false });
    if (labs[k] === WALL_TRI) wall.add(ka + '|' + kb);
  }
  const from = new Map();
  for (const e of edges) {
    if (e.lab === WALL_TRI && wall.has(e.kb + '|' + e.ka)) { e.used = true; continue; }   // a seam of the ground's pieces
    if (!from.has(e.ka)) from.set(e.ka, []); from.get(e.ka).push(e);
  }
  const loops = [];
  for (const e0 of edges) {
    if (e0.used) continue;
    const pts = [], labs = []; let e = e0;
    for (let guard = 0; guard <= edges.length && e && !e.used; guard++) { e.used = true; pts.push(e.a); labs.push(e.lab); const nx = from.get(e.kb); e = nx ? nx.find(q => !q.used) : null; }
    if (pts.length < 3) continue;
    // a straight side cut into lengths by the grid is one side again
    const m = pts.length, keep = [];
    for (let k = 0; k < m; k++) {
      const a = pts[(k + m - 1) % m], b = pts[k], c = pts[(k + 1) % m];
      const straight = labs[(k + m - 1) % m] === labs[k] && labs[k] !== SEA && Math.abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) <= 1e-9 * (Math.hypot(b[0] - a[0], b[1] - a[1]) * Math.hypot(c[0] - b[0], c[1] - b[1]) + 1e-12);
      if (!straight) keep.push(k);
    }
    const loop = keep.length >= 3 ? { pts: keep.map(k => pts[k]), labs: keep.map(k => labs[k]) } : { pts, labs };
    loop.area = Math.abs(ringArea(loop.pts)); loops.push(loop);
  }
  loops.sort((x, y) => y.area - x.area);
  return { pts: loops.length ? loops[0].pts : [], labs: loops.length ? loops[0].labs : [], loops };
}
function seaGridStep(side) { let g = 4; while (g < 64 && g * 16 < side) g *= 2; return g; }   // about 8 to 16 squares across the cell, a power of two so every cell is cut on one page-wide grid
// A cell the hive's edge crosses is cut on a grid over it, exact to the
// cell's own sides: each square of the grid holds the part of it inside the
// hive (its corners' presence, taken as linear along its sides), and each
// such part is cut to the cell. The squares are aligned to the page, so a
// cell that moves is cut on the same grid, and the edge they draw moves only
// as the presence does.
function seaSoftCut(poly, i, seeds, weights, sea) {
  const pts = poly.pts, labs = poly.labs, n = pts.length;
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const p of pts) { if (p[0] < x0) x0 = p[0]; if (p[0] > x1) x1 = p[0]; if (p[1] < y0) y0 = p[1]; if (p[1] > y1) y1 = p[1]; }
  // the bells that reach this ground, as flat arrays
  let K = 0; const KX = [], KY = [], KW = [], KT = [];
  for (let j = 0; j < seeds.length; j++) {
    if (!sea.on[j]) continue;
    const sx = seeds[j][0], sy = seeds[j][1], dx = Math.max(x0 - sx, 0, sx - x1), dy = Math.max(y0 - sy, 0, sy - y1), it = 1 / sea.T[j];
    if ((weights[j] - dx * dx - dy * dy) * it > -36) { KX.push(sx); KY.push(sy); KW.push(weights[j]); KT.push(it); K++; }   // e^-36 of presence is none
  }
  // the presence, and whether it is at least one: a sum of bells that has reached one is there whatever the rest add
  const F = (x, y) => { let f = 0; for (let k = 0; k < K; k++) { const dx = x - KX[k], dy = y - KY[k]; f += Math.exp(Math.min(SEA_SOFT_CAP, (KW[k] - dx * dx - dy * dy) * KT[k])); } return f; };
  const IN = (x, y) => { let f = 0; for (let k = 0; k < K; k++) { const dx = x - KX[k], dy = y - KY[k]; f += Math.exp(Math.min(SEA_SOFT_CAP, (KW[k] - dx * dx - dy * dy) * KT[k])); if (f >= 1) return true; } return false; };
  let whole = true;
  for (let k = 0; k < n && whole; k++) { const p = pts[k], q = pts[k + 1 === n ? 0 : k + 1]; if (!IN(p[0], p[1]) || !IN((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)) whole = false; }
  if (whole) return [poly];   // all of it inside the hive
  const o = ringArea(pts) > 0 ? 1 : -1, PA = [], PB = [], PC = [];
  for (let k = 0; k < n; k++) { const p = pts[k], q = pts[k + 1 === n ? 0 : k + 1]; PA.push(o * (q[1] - p[1])); PB.push(-o * (q[0] - p[0])); PC.push(o * ((q[1] - p[1]) * p[0] - (q[0] - p[0]) * p[1])); }
  const g = seaGridStep(Math.max(x1 - x0, y1 - y0));
  const ga = Math.floor(x0 / g), gb = Math.floor(y0 / g), NX = Math.max(1, Math.ceil(x1 / g) - ga), NY = Math.max(1, Math.ceil(y1 / g) - gb), W1 = NX + 1;
  // the cell's reach along each band of squares, exactly (every side clipped to the band)
  const bandLo = new Float64Array(NY), bandHi = new Float64Array(NY);
  for (let b = 0; b < NY; b++) {
    const ya = (gb + b) * g, yb = ya + g; let lo = Infinity, hi = -Infinity;
    for (let k = 0; k < n; k++) {
      const p = pts[k], q = pts[k + 1 === n ? 0 : k + 1];
      const ymin = Math.min(p[1], q[1]), ymax = Math.max(p[1], q[1]);
      if (ymax < ya || ymin > yb) continue;
      if (ymax === ymin) { lo = Math.min(lo, p[0], q[0]); hi = Math.max(hi, p[0], q[0]); continue; }
      const ta = Math.max(0, Math.min(1, (ya - p[1]) / (q[1] - p[1]))), tb = Math.max(0, Math.min(1, (yb - p[1]) / (q[1] - p[1])));
      const xa = p[0] + ta * (q[0] - p[0]), xb = p[0] + tb * (q[0] - p[0]);
      lo = Math.min(lo, xa, xb); hi = Math.max(hi, xa, xb);
    }
    bandLo[b] = lo; bandHi[b] = hi;
  }
  // the presence at the corners near the cell: its sign, and its value where the edge crosses
  const V = new Float64Array(W1 * (NY + 1)).fill(-2), aLo = new Int32Array(NY), aHi = new Int32Array(NY);
  for (let b = 0; b < NY; b++) {
    if (!(bandHi[b] >= bandLo[b])) { aLo[b] = 1; aHi[b] = 0; continue; }
    aLo[b] = Math.max(0, Math.floor(bandLo[b] / g) - ga); aHi[b] = Math.min(NX - 1, Math.ceil(bandHi[b] / g) - ga - 1);
    for (let a = aLo[b]; a <= aHi[b] + 1; a++) for (const bb of [b, b + 1]) { const k = bb * W1 + a; if (V[k] === -2) V[k] = IN((ga + a) * g, (gb + bb) * g) ? 1 : -1; }
  }
  const exact = new Uint8Array(W1 * (NY + 1));
  const val = k => { if (!exact[k]) { exact[k] = 1; V[k] = F((ga + k % W1) * g, (gb + ((k / W1) | 0)) * g) - 1; } return V[k]; };
  const pieces = [];
  const add = (P, L) => {
    let q = { pts: P, labs: L };
    for (let k = 0; k < n; k++) {   // cut by the sides of the cell it crosses
      let out = false; for (const p of q.pts) if (PA[k] * p[0] + PB[k] * p[1] > PC[k]) { out = true; break; }
      if (!out) continue;
      q = seaClip(q, PA[k], PB[k], PC[k], labs[k]); if (q.pts.length < 3) return;
    }
    if (q.pts.length >= 3 && Math.abs(ringArea(q.pts)) > 1e-9) pieces.push(q);
  };
  // where the edge crosses a grid side, from the lower corner of the side, so both squares that share it agree
  const cross = (ax, ay, va, bx, by, vb) => { if (bx < ax || by < ay) { let t = ax; ax = bx; bx = t; t = ay; ay = by; by = t; t = va; va = vb; vb = t; } const t = va / (va - vb); return [ax + t * (bx - ax), ay + t * (by - ay)]; };
  const CX = [0, 0, 0, 0], CY = [0, 0, 0, 0], CV = [0, 0, 0, 0], CI = [false, false, false, false];
  for (let b = 0; b < NY; b++) {
    if (aHi[b] < aLo[b]) continue;
    const ya = (gb + b) * g, yb = ya + g;
    let run = -1;
    for (let a = aLo[b]; a <= aHi[b] + 1; a++) {
      const k0 = b * W1 + a, k3 = k0 + W1;
      const inside = a <= aHi[b];
      const full = inside && V[k0] > 0 && V[k0 + 1] > 0 && V[k3 + 1] > 0 && V[k3] > 0;
      if (full) { if (run < 0) run = a; continue; }
      if (run >= 0) { const P = []; for (let q = run; q <= a; q++) P.push([(ga + q) * g, ya]); for (let q = a; q >= run; q--) P.push([(ga + q) * g, yb]); add(P, P.map(() => SEA_SEAM)); run = -1; }
      if (!inside) continue;
      if (!(V[k0] > 0 || V[k0 + 1] > 0 || V[k3 + 1] > 0 || V[k3] > 0)) continue;   // all sea
      const xa = (ga + a) * g, xb = xa + g;
      CX[0] = xa; CY[0] = ya; CV[0] = val(k0); CX[1] = xb; CY[1] = ya; CV[1] = val(k0 + 1); CX[2] = xb; CY[2] = yb; CV[2] = val(k3 + 1); CX[3] = xa; CY[3] = yb; CV[3] = val(k3);
      let m = 0; for (let k = 0; k < 4; k++) { CI[k] = CV[k] >= 0; if (CI[k]) m++; }
      if (m === 0) continue;
      const side = k => { const k1 = (k + 1) & 3; return cross(CX[k], CY[k], CV[k], CX[k1], CY[k1], CV[k1]); };
      if (m === 2 && CI[0] === CI[2] && (CV[0] + CV[1] + CV[2] + CV[3]) / 4 < 0) {   // a saddle the centre leaves open
        for (let k = 0; k < 4; k++) if (CI[k]) add([[CX[k], CY[k]], side(k), side((k + 3) & 3)], [SEA_SEAM, SEA, SEA_SEAM]);
        continue;
      }
      const P = [], T = [];
      for (let k = 0; k < 4; k++) { if (CI[k]) { P.push([CX[k], CY[k]]); T.push(0); } if (CI[k] !== CI[(k + 1) & 3]) { P.push(side(k)); T.push(1); } }
      const L = []; for (let k = 0; k < P.length; k++) L.push(T[k] && T[(k + 1) % P.length] ? SEA : SEA_SEAM);
      add(P, L);
    }
  }
  return pieces;
}
"""

# THE SEA IS SOFT: the hive bids as one body
replace("""const SEA_FIT_MIN = 0.5;  // the least a liquid cell shrinks to, giving the rest to the sea, while it cannot get clear of the screen
""", "")
replace("""function buildJacobian(diagram, seeds, seaW) {""", SOFT + """function buildJacobian(diagram, seeds, seaW, seaSoft) {""")
replace("""    if (sea) {   // MEMBRANE: the cell's own reach first; it bounds the neighbours worth asking
      poly = seaCut(poly, sx, sy, wi);
      if (poly.pts.length < 3) dead = true;
      else { rFar = 0; for (const p of poly.pts) rFar = Math.max(rFar, Math.hypot(p[0] - sx, p[1] - sy)); }
    }
""", "")
replace("""    if (poly.pts.length < 3) { cells[i] = { pts: [], labs: [] }; areas[i] = 0; }
    else if (!tris) { cells[i] = poly; areas[i] = Math.abs(ringArea(poly.pts)); }
    else {
      const pieces = [];
      let a = 0;
      for (const tri of tris) {
        let q = poly;
        for (let e = 0; e < tri.length && q.pts.length >= 3; e++) q = clipHalfPlane(q, tri[e].ax, tri[e].ay, tri[e].b, WALL_TRI);
        if (q.pts.length >= 3) { pieces.push(q); a += Math.abs(ringArea(q.pts)); }
      }
      if (!pieces.length) { cells[i] = { pts: [], labs: [], pieces }; areas[i] = 0; }
      else { const o = unionOutline(pieces); cells[i] = { pts: o.pts, labs: o.labs, pieces }; areas[i] = a; }
    }
  }
  return { cells, areas };""", """    const parts = poly.pts.length < 3 ? [] : sea && sea.on[i] ? seaSoftCut(poly, i, seeds, weights, sea) : [poly], softCut = parts.length !== 1 || parts[0] !== poly;   // AMOEBA: where the hive ends, if it ends in this cell (only a cell has a reach)
    if (!parts.length) { cells[i] = { pts: [], labs: [] }; areas[i] = 0; }
    else if (!tris && parts.length === 1) { cells[i] = parts[0]; areas[i] = Math.abs(ringArea(parts[0].pts)); }
    else {
      const pieces = [];
      let a = 0;
      for (const part of parts) for (const tri of (tris || [[]])) {
        let q = part;
        for (let e = 0; e < tri.length && q.pts.length >= 3; e++) q = softCut ? seaClip(q, tri[e].ax, tri[e].ay, tri[e].b, WALL_TRI) : clipHalfPlane(q, tri[e].ax, tri[e].ay, tri[e].b, WALL_TRI);
        if (q.pts.length >= 3) { pieces.push(q); a += Math.abs(ringArea(q.pts)); }
      }
      if (!pieces.length) { cells[i] = { pts: [], labs: [], pieces }; areas[i] = 0; }
      else if (softCut) { const o = seaOutline(pieces); cells[i] = { pts: o.pts, labs: o.labs, pieces: o.loops }; areas[i] = a; }   // AMOEBA: a cell the hive's edge cuts is its outline, every loop of it
      else { const o = unionOutline(pieces); cells[i] = { pts: o.pts, labs: o.labs, pieces }; areas[i] = a; }
    }
  }
  return { cells, areas };""")
replace("""  if (seaW) {   // MEMBRANE: an edge on the sea stands at the reach sqrt(w), which moves by 1/(2 sqrt(w)) a unit of weight
    let shore = 0;
    for (let i = 0; i < n; i++) {
      const r = Math.sqrt(Math.max(1e-12, seaW[i]));
      for (const { pts, labs } of (diagram.cells[i].pieces || [diagram.cells[i]])) for (let k = 0, m = pts.length; k < m; k++) if (labs[k] === SEA) {
        const p = pts[k], q = pts[k + 1 === m ? 0 : k + 1], L = Math.hypot(q[0] - p[0], q[1] - p[1]);
        A[i][i] += L / (2 * r); shore += L;
      }
    }
    A.shore = shore;
  }""", """  if (seaW) {   // AMOEBA: an edge on the sea stands where the hive's presence is one; a unit of a cell's weight moves it by that cell's share of the presence there, over how steeply the presence falls
    let shore = 0;
    for (let i = 0; i < n; i++) {
      for (const { pts, labs } of (diagram.cells[i].pieces || [diagram.cells[i]])) for (let k = 0, m = pts.length; k < m; k++) if (labs[k] === SEA) {
        const p = pts[k], q = pts[k + 1 === m ? 0 : k + 1], L = Math.hypot(q[0] - p[0], q[1] - p[1]);
        shore += L;
        const x = (p[0] + q[0]) / 2, y = (p[1] + q[1]) / 2;
        let gx = 0, gy = 0; const ks = [];
        for (let j = 0; j < n; j++) {
          if (!seaSoft.on[j]) continue;
          const dx = x - seeds[j][0], dy = y - seeds[j][1], e = (seaW[j] - dx * dx - dy * dy) / seaSoft.T[j];
          if (e < -36) continue;
          const kj = Math.exp(Math.min(SEA_SOFT_CAP, e)); ks.push([j, kj]);
          gx -= 2 * kj * dx / seaSoft.T[j]; gy -= 2 * kj * dy / seaSoft.T[j];
        }
        const G = Math.hypot(gx, gy);
        if (!(G > 1e-12)) { const r = Math.sqrt(Math.max(1e-12, seaW[i])); A[i][i] += L / (2 * r); continue; }
        for (const [j, kj] of ks) A[i][j] += L * kj / seaSoft.T[j] / G;
      }
    }
    A.shore = shore;
  }""")
# a newcomer enters at the weight that makes it its size against the soft sea too
replace("""function cellAreaAt(sx, sy, w, seeds, weights, boundsPts, tris, sea) {
  const pot = sx * sx + sy * sy - w;
  let poly = { pts: boundsPts, labs: boundsPts.map((_, k) => -1 - k) };
  if (sea) { poly = seaCut(poly, sx, sy, w); if (poly.pts.length < 3) return 0; }   // MEMBRANE
  for (let j = 0; j < seeds.length; j++) {
    const p2 = seeds[j][0] * seeds[j][0] + seeds[j][1] * seeds[j][1] - weights[j];
    poly = clipHalfPlane(poly, seeds[j][0] - sx, seeds[j][1] - sy, (p2 - pot) / 2, j);
    if (poly.pts.length < 3) return 0;
  }
  if (!tris) return Math.abs(ringArea(poly.pts));
  let a = 0;
  for (const tri of tris) {
    let q = poly;
    for (let e = 0; e < tri.length && q.pts.length >= 3; e++) q = clipHalfPlane(q, tri[e].ax, tri[e].ay, tri[e].b, WALL_TRI);
    if (q.pts.length >= 3) a += Math.abs(ringArea(q.pts));
  }
  return a;
}""", """function cellAreaAt(sx, sy, w, seeds, weights, boundsPts, tris, sea) {
  const pot = sx * sx + sy * sy - w;
  let poly = { pts: boundsPts, labs: boundsPts.map((_, k) => -1 - k) };
  if (sea === true) { poly = seaCut(poly, sx, sy, w); if (poly.pts.length < 3) return 0; }   // MEMBRANE: its own disc, where no bells are given
  for (let j = 0; j < seeds.length; j++) {
    const p2 = seeds[j][0] * seeds[j][0] + seeds[j][1] * seeds[j][1] - weights[j];
    poly = clipHalfPlane(poly, seeds[j][0] - sx, seeds[j][1] - sy, (p2 - pot) / 2, j);
    if (poly.pts.length < 3) return 0;
  }
  // AMOEBA: where the hive ends, if it ends in this cell, with everyone's bells and its own
  const parts = sea && sea !== true && sea.on0 ? seaSoftCut(poly, 0, [[sx, sy], ...seeds], [w, ...weights], { T: [sea.T0, ...sea.T], on: [1, ...sea.on] }) : [poly];
  let a = 0;
  for (const part of parts) for (const tri of (tris || [[]])) {
    let q = part;
    for (let e = 0; e < tri.length && q.pts.length >= 3; e++) q = clipHalfPlane(q, tri[e].ax, tri[e].ay, tri[e].b, WALL_TRI);
    if (q.pts.length >= 3) a += Math.abs(ringArea(q.pts));
  }
  return a;
}""")
replace("""function entryWeight(sx, sy, target, seeds, weights, boundsPts, tris, scale, sea) {
  let lo = -scale, hi = scale;""", """function entryWeight(sx, sy, target, seeds, weights, boundsPts, tris, scale, sea) {
  if (sea && sea !== true) {   // AMOEBA: against the soft sea each try costs a cut, so the bracket closes by regula falsi (Illinois)
    let lo = -scale, hi = scale, flo = -target, fhi = null, side = 0, mid = 0;
    for (let k = 0; k < 60; k++) {
      mid = fhi === null ? (lo + hi) / 2 : (lo * fhi - hi * flo) / (fhi - flo);
      if (!(mid > lo && mid < hi)) mid = (lo + hi) / 2;
      const f = cellAreaAt(sx, sy, mid, seeds, weights, boundsPts, tris, sea) - target;
      if (Math.abs(f) <= 1e-6 * target || hi - lo <= 1e-9 * scale) return mid;
      if (f < 0) { lo = mid; flo = f; if (side === -1 && fhi !== null) fhi /= 2; side = -1; }
      else { hi = mid; fhi = f; if (side === 1) flo /= 2; side = 1; }
    }
    return mid;
  }
  let lo = -scale, hi = scale;""")
replace("""  const diagramAt = ww => computeDiagram(seeds, ww, boundsPts, tris, prepared, !!sea);""", """  const seaSoft = sea ? { T: Float64Array.from(tgt, t => 2 * t / Math.PI), on: Uint8Array.from(seeds, (_, i) => !sea.reach || sea.reach[i] ? 1 : 0) } : null;   // AMOEBA: each cell's bell, as wide as the cell; only a cell has a reach
  const diagramAt = ww => computeDiagram(seeds, ww, boundsPts, tris, prepared, seaSoft || false);
  const reaches = i => !sea || !sea.reach || sea.reach[i];""")
replace("""    let wmax = -Infinity, wmin = Infinity; for (const q of w) { wmax = Math.max(wmax, q); wmin = Math.min(wmin, q); }""", """    let wmax = -Infinity, wmin = Infinity; for (let i = 0; i < n; i++) if (reaches(i)) { wmax = Math.max(wmax, w[i]); wmin = Math.min(wmin, w[i]); }   // AMOEBA: over the cells that reach""")
replace("""      if (!(minOf(diag.areas) <= 0)) { hi = Infinity; diag.cells.forEach((c, i) => { let R = 0;""", """      if (!(minOf(diag.areas) <= 0)) { hi = Infinity; diag.cells.forEach((c, i) => { if (!reaches(i)) return; let R = 0;""")
replace("""    const inS = [], inW = [], empties = [];
    for (let i = 0; i < n; i++) { if (diag.areas[i] > 0) { inS.push(seeds[i]); inW.push(w[i]); } else empties.push(i); }
    for (const i of empties) { w[i] = entryWeight(seeds[i][0], seeds[i][1], Math.min(tgt[i], 0.98 * domainArea), inS, inW, boundsPts, tris, scale, true); inS.push(seeds[i]); inW.push(w[i]); }""", """    const inS = [], inW = [], inI = [], empties = [];
    for (let i = 0; i < n; i++) { if (diag.areas[i] > 0) { inS.push(seeds[i]); inW.push(w[i]); inI.push(i); } else empties.push(i); }
    for (const i of empties) { w[i] = entryWeight(seeds[i][0], seeds[i][1], Math.min(tgt[i], 0.98 * domainArea), inS, inW, boundsPts, tris, scale, { T: inI.map(j => seaSoft.T[j]), on: inI.map(j => seaSoft.on[j]), T0: seaSoft.T[i], on0: seaSoft.on[i] }); inS.push(seeds[i]); inW.push(w[i]); inI.push(i); }""")
replace("""    const J = buildJacobian(diag, seeds, sea ? w : null);""", """    const J = buildJacobian(diag, seeds, sea ? w : null, seaSoft);""")

# ON THE CHANGE'S OWN CLOCK: a cell is liquid as far as it is between its
# rests, and the whitespace melts by the same measure of the change
replace("""  seaBeta(b) {
    if (b.leaving) { const j = b.journey; if (!j) return 0; return 1 - S3((this.t - j.t0 - (j.delay || 0)) / MELT); }
    if (b.table && b.table.mode === 'open') return Math.max(0, Math.min(1, b.crystal));
    return 1;
  }""", """  seaBeta(b) {
    if (b.leaving || (b.table && b.table.mode === 'open')) return 1 - (this.seaE || 0);   // AMOEBA: on the change's own clock
    return 1;
  }""")
a = s.index("""  // THE SWARM FEELS THE SCREEN.""")
b = s.index("""  // the sea's claim: every whitespace's share that is not its own cell""")
s = s[:a] + """  // AMOEBA: A CELL IS LIQUID AS FAR AS IT IS BETWEEN ITS TWO RESTS, on the
  // change's own clock: none of it at either rest, all of it halfway, 4p(1 - p).
  // A liquid cell keeps its plan its own radius clear of the screen (see
  // steer). The whitespace melts into the sea by the same measure of the
  // change's progress, read off its paced travellers: the sea comes in as
  // gently as the change sets off, and is gone as it lands.
  seaFeel(dt, t) {
    for (const b of this.bodies) {
      if (b.isVoid || b.isSelf || b.leaving || b.reelPinned || !this.seaOpen() || !b.journey) { b.seaLiquid = 0; continue; }
      const pr = Math.max(0, Math.min(1, b.progress || 0));
      b.seaLiquid = 4 * pr * (1 - pr);
    }
    let n = 0, P = 0;
    for (const b of this.bodies) if (!b.isVoid && !b.isSelf && !b.leaving && b.journey && b.journey.pace) { P += Math.max(0, Math.min(1, b.progress || 0)); n++; }
    const pc = n ? P / n : 0;
    this.seaE = this.seaOpen() ? 4 * pc * (1 - pc) : 0;
  }
""" + s[b:]
replace("""          const r = b.seaLiquid * Math.sqrt(Math.max(0, b.claim * this.seaKeep(b)) * this.PW * this.PH / Math.PI);""", """          const r = b.seaLiquid * Math.sqrt(Math.max(0, b.claim) * this.PW * this.PH / Math.PI);   // AMOEBA: a cell keeps its size""")
replace("""  // the sea's claim: every whitespace's share that is not its own cell (a
  // hole's, what its shape has not yet taken), and what the cells have given it
  seaClaimOf(b) {
    if (b.isSelf || b.wall) return 0;
    if (!b.isVoid) { let c = 0; for (const q of b.subs) c += Math.max(0, q.claim); return c * (1 - this.seaKeep(b)); }""", """  // the sea's claim: every whitespace's share that is not its own cell (a
  // hole's, what its shape has not yet taken); a cell keeps its size (AMOEBA)
  seaClaimOf(b) {
    if (b.isSelf || b.wall || !b.isVoid) return 0;""")
replace("""    const claimOf = s => !seaOn ? s.claim : s.claim * (s.body.isVoid ? this.seaBeta(s.body) : this.seaKeep(s.body));""", """    const claimOf = s => !seaOn || !s.body.isVoid ? s.claim : s.claim * this.seaBeta(s.body);   // AMOEBA: a cell keeps its size""")
replace("""    const claimOf = s => !seaOn || s.body.hole ? s.claim : s.claim * (s.body.isVoid ? this.seaBeta(s.body) : this.seaKeep(s.body));   // MEMBRANE: a hole bids for the cell it would have at its claim, as ever""", """    const claimOf = s => !seaOn || s.body.hole || !s.body.isVoid ? s.claim : s.claim * this.seaBeta(s.body);   // MEMBRANE: a hole bids for the cell it would have at its claim, as ever (AMOEBA: and a cell keeps its size)""")

# ONLY A CELL HAS A REACH, AND A SEA TOO SMALL TO SEE APPEAR STAYS OUT
replace("""    const seaIn = seaClaim > 0;""", """    const seaIn = seaClaim >= ACTIVE_MIN;   // AMOEBA: a sea too small to see appear stays out, as a seed does""")
replace("""      const inSeeds = live.map(q => [q.x, q.y]), inW = live.map(q => q.w);""", """      const inSeeds = live.map(q => [q.x, q.y]), inW = live.map(q => q.w);
      const bell = q => 2 * claimOf(q) * domainArea / tSum / Math.PI, inT = live.map(bell), inOn = live.map(q => q.body.isVoid ? 0 : 1);   // AMOEBA: everyone's bell, for the soft sea""")
replace("""        } else s.w = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, tris, scale, seaIn);
        inSeeds.push([s.x, s.y]); inW.push(s.w);""", """        } else s.w = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, tris, scale, seaIn && !s.body.isVoid ? { T: inT, on: inOn, T0: bell(s), on0: 1 } : false);
        inSeeds.push([s.x, s.y]); inW.push(s.w); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1);""")
replace("""        if (!live2[k] && seaK[k] > 0) continue;   // MEMBRANE: ground only the sea stands in is the sea's""", """        if (!live2[k] && seaK[k] >= ACTIVE_MIN) continue;   // MEMBRANE: ground only the sea stands in is the sea's""")
replace("""        const sol = idx.length === 1 && !(seaK[k] > 0)
""", """        const sol = idx.length === 1 && !(seaK[k] >= ACTIVE_MIN)
""")
replace("""          : solveWeights(gs, gc, bounds, gw, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(i => this.sitePaint(active[i])), sea: seaK[k] > 0 ? { claim: seaK[k] } : null });""", """          : solveWeights(gs, gc, bounds, gw, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(i => this.sitePaint(active[i])), sea: seaK[k] >= ACTIVE_MIN ? { claim: seaK[k], reach: idx.map(i => !active[i].body.isVoid) } : null });""")
replace("""    const sol = solveWeights(seeds, claims, bounds, active.map(s => s.w), { maxIter: this.iterBudget(), tris, domainArea: tris ? dArea : undefined, paint: active.map(s => this.sitePaint(s)), sea: seaIn ? { claim: seaClaim } : null });""", """    const sol = solveWeights(seeds, claims, bounds, active.map(s => s.w), { maxIter: this.iterBudget(), tris, domainArea: tris ? dArea : undefined, paint: active.map(s => this.sitePaint(s)), sea: seaIn ? { claim: seaClaim, reach: active.map(s => !s.body.isVoid) } : null });""")
replace("""      for (const s of idx) if (s.shadowLive) { inSeeds.push([s.x, s.y]); inW.push(s.wShadow); }""", """      const bell = q => 2 * claimOf(q) * ga / tSum / Math.PI, inT = [], inOn = [];   // AMOEBA: everyone's bell, for the soft sea
      for (const s of idx) if (s.shadowLive) { inSeeds.push([s.x, s.y]); inW.push(s.wShadow); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1); }""")
replace("""        if (!inSeeds.length) { s.wShadow = fair / Math.PI; inSeeds.push([s.x, s.y]); inW.push(s.wShadow); continue; }""", """        if (!inSeeds.length) { s.wShadow = fair / Math.PI; inSeeds.push([s.x, s.y]); inW.push(s.wShadow); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1); continue; }""")
replace("""        s.wShadow = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, gt, scale, seaK[k] > 0);
        inSeeds.push([s.x, s.y]); inW.push(s.wShadow);""", """        s.wShadow = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, gt, scale, seaK[k] >= ACTIVE_MIN && !s.body.isVoid ? { T: inT, on: inOn, T0: bell(s), on0: 1 } : false);
        inSeeds.push([s.x, s.y]); inW.push(s.wShadow); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1);""")
replace("""      const sol = idx.length === 1 && !(seaK[k] > 0)
""", """      const sol = idx.length === 1 && !(seaK[k] >= ACTIVE_MIN)
""")
replace("""        : solveWeights(seeds, claims, bounds, w0, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(s => this.sitePaint(s)), sea: seaK[k] > 0 ? { claim: seaK[k] } : null });""", """        : solveWeights(seeds, claims, bounds, w0, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(s => this.sitePaint(s)), sea: seaK[k] >= ACTIVE_MIN ? { claim: seaK[k], reach: idx.map(s => !s.body.isVoid) } : null });""")
# a point is the sea's where the cell that bids best there does not reach it
replace("""      if (bid < best) { best = bid; id = s.body.isVoid ? -1 : s.body.id; }
    }
    return this.solved.sea && best > 0 ? -1 : id;   // MEMBRANE: the sea""", """      if (bid < best) { best = bid; id = s.body.isVoid ? -1 : s.body.id; at = i; }
    }
    return this.solved.sea && at >= 0 && !this.seaHas(at, x, y) ? -1 : id;   // AMOEBA: the sea""")
replace("""  hitTest(x, y) {
    const wb = this.wallAt(x, y);
    if (wb) return wb.isVoid ? -1 : wb.id;
    if (!this.solved) return -1;
    if (!this.domainPoly && (x < 0 || y < 0 || x > this.W || y > this.H)) return -1;
    let best = Infinity, id = -1;""", """  // AMOEBA: whether the cell of site i holds the point: the sea is wherever a
  // cell's own ground is not
  seaHas(i, x, y) {
    const c = this.solved.diagram.cells[i], s = this.solvedSubs[i];
    if (!c || s.body.isVoid) return true;
    for (const p of (c.pieces || [c])) if (p.pts && p.pts.length >= 3 && pointInPolygon(x, y, p.pts)) return true;
    return false;
  }
  hitTest(x, y) {
    const wb = this.wallAt(x, y);
    if (wb) return wb.isVoid ? -1 : wb.id;
    if (!this.solved) return -1;
    if (!this.domainPoly && (x < 0 || y < 0 || x > this.W || y > this.H)) return -1;
    let best = Infinity, id = -1, at = -1;""")
replace("""    let best = Infinity, body = null;
    const subs = this.solvedSubs, w = this.solved.weights;
    for (let i = 0; i < subs.length; i++) {
      const s = subs[i];
      const dx = x - s.x, dy = y - s.y;
      const bid = dx * dx + dy * dy - w[i];
      if (bid < best) { best = bid; body = s.body; }
    }
    return this.solved.sea && best > 0 ? null : body;   // MEMBRANE: the sea""", """    let best = Infinity, body = null, at = -1;
    const subs = this.solvedSubs, w = this.solved.weights;
    for (let i = 0; i < subs.length; i++) {
      const s = subs[i];
      const dx = x - s.x, dy = y - s.y;
      const bid = dx * dx + dy * dy - w[i];
      if (bid < best) { best = bid; body = s.body; at = i; }
    }
    return this.solved.sea && at >= 0 && !this.seaHas(at, x, y) ? null : body;   // AMOEBA: the sea""")

# THE HERO GIVES BACK THE TEXT'S ROOM ON ITS OWN CLOCK: nothing is handed over at the ask
replace("""  const total = b => b.subs.reduce((a, s) => a + s.claim, 0), scale = (b, want) => { const t = total(b); if (t > 0) for (const s of b.subs) s.claim *= want / t; };
  regions.forEach((g, i) => {""", """  const total = b => b.subs.reduce((a, s) => a + s.claim, 0), scale = (b, want) => { const t = total(b); if (t > 0) for (const s of b.subs) s.claim *= want / t; };
  // AMOEBA: what the image holds of the whitespace's rooms as it sets off, it
  // gives back on its own clock, and no faster than it leaves them: nothing
  // is handed over at the ask
  const hj = hero.journey, hp = hj ? Math.max(0, Math.min(1, hero.progress || 0)) : 1;
  if (hj && !hj.tandemHeld) { hj.tandemHeld = {}; regions.forEach((g, i) => { if (i > 0) hj.tandemHeld[g.b.id] = heroIn[i] / PA; }); }
  const held = regions.map((g, i) => i > 0 && hj ? Math.min(heroIn[i] / PA, (hj.tandemHeld[g.b.id] || 0) * (1 - hp)) : 0), kept = held.reduce((a, q) => a + q, 0);
  regions.forEach((g, i) => {""")
replace("""      if (total(hero) > j.tandemRoom) scale(hero, Math.max(CLAIM_MIN, j.tandemRoom));""", """      if (total(hero) > j.tandemRoom + kept) scale(hero, Math.max(CLAIM_MIN, j.tandemRoom + kept));""")
replace("""      const t = g.b.table; t.room = Math.max(t.room || 0, Math.min(g.b.claimTarget, room));""", """      const t = g.b.table; t.room = Math.max(t.room || 0, Math.min(g.b.claimTarget, room - held[i]));""")

assert 'seaKeep' not in s and 'seaFit' not in s and 'SEA_FIT_MIN' not in s
(ROOT / 'amoeba.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
