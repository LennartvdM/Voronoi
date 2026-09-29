"""Build Membrane from Tempo: the hive in a membrane of its own.

The first mark of a new class. Every mark so far tessellated the whole
screen on every frame: the cells and the whitespace shared it out between
them, and the whitespace was cells too, seeded and invisible. Whitespace so
built is a solid. Its straight borders pushed the travelling cells flat
against the edges of the screen, and a change always had to work out its
edges as a group.

Here, while the page changes, its whitespace is a sea. The sea bids the same
everywhere, so a travelling cell reaches only as far as its own bid is below
it: a disc about its seed. Where cells meet they share a straight edge, as
ever; where one faces the sea its border is its own reach. The hive's outline
is nothing but its cells' reaches together, and nothing draws or steers it.

Whitespace has its own cell only as far as it has settled: all of it at rest,
so every layout lands exactly as before; none of it while it closes (it melts
into the sea as a cell melts) or while it opens (until the cells leaving it
land).

Each travelling cell also feels the screen. A cell is liquid from when it has
melted until it locks as it lands. A liquid cell keeps its plan its own
radius clear of the screen's edges. If it still touches the screen, it gives
up its size to the sea, down to half, and takes it back once clear; it is its
whole size again as it locks. The hive shrinks only as far as it needs to
float, and no cell is told to.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'tempo.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '17d8b48fc77404b6331da14e2184a9f892eaec7aa563028403c6064ea30dff9f'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Tempo — Hive</title>', '<title>Membrane — Hive</title>')
replace('&larr; Back · Tempo</a>', '&larr; Back · Membrane</a>')

# THE SEA'S CUT: a cell's own reach, as a polygon whose inradius is the reach
replace('''const WALL_TRI = -1000;   // label of an edge cut by a domain triangle: a wall, or a seam between two pieces
''', '''const WALL_TRI = -1000;   // label of an edge cut by a domain triangle: a wall, or a seam between two pieces
// MEMBRANE. THE SEA: ground no cell reaches. The sea bids zero everywhere, so
// a cell reaches exactly as far as its own bid is below zero: a disc of
// radius sqrt(w) about its seed. The disc is cut as a regular polygon of
// SEA_SIDES sides whose inradius is the reach, so its area grows with the
// weight exactly as the Jacobian says (each side moves out by the reach's
// own change).
const SEA = -3000;        // label of an edge a cell shares with the sea
const SEA_SIDES = 64;     // within half a pixel of the circle up to a reach of 400 px
const SEA_FIT_MIN = 0.5;  // the least a liquid cell shrinks to, giving the rest to the sea, while it cannot get clear of the screen
const SEA_DIRS = Array.from({ length: SEA_SIDES }, (_, k) => [Math.cos(2 * Math.PI * k / SEA_SIDES), Math.sin(2 * Math.PI * k / SEA_SIDES)]);
function seaCut(poly, sx, sy, w) {
  if (!(w > 0)) return { pts: [], labs: [] };
  const r = Math.sqrt(w);
  let far = 0; for (const p of poly.pts) far = Math.max(far, (p[0] - sx) * (p[0] - sx) + (p[1] - sy) * (p[1] - sy));
  if (far <= r * r) return poly;   // inside the reach's inscribed circle: the sea is nowhere near
  for (const [c, s] of SEA_DIRS) {
    const b = c * sx + s * sy + r;
    let out = false; for (const p of poly.pts) if (c * p[0] + s * p[1] > b) { out = true; break; }
    if (!out) continue;
    poly = clipHalfPlane(poly, c, s, b, SEA);
    if (poly.pts.length < 3) return { pts: [], labs: [] };
  }
  return poly;
}
''')

# THE DIAGRAM, with the sea: a cell's own reach first
replace('function computeDiagram(seeds, weights, boundsPts, tris, prepared) {', 'function computeDiagram(seeds, weights, boundsPts, tris, prepared, sea) {')
replace('''    let poly = { pts: boundsPts, labs: baseLabs };
    let rFar = plan.far[i];
    let dead = false;''', '''    let poly = { pts: boundsPts, labs: baseLabs };
    let rFar = plan.far[i];
    let dead = false;
    if (sea) {   // MEMBRANE: the cell's own reach first; it bounds the neighbours worth asking
      poly = seaCut(poly, sx, sy, wi);
      if (poly.pts.length < 3) dead = true;
      else { rFar = 0; for (const p of poly.pts) rFar = Math.max(rFar, Math.hypot(p[0] - sx, p[1] - sy)); }
    }''')
replace('''function cellAreaAt(sx, sy, w, seeds, weights, boundsPts, tris) {
  const pot = sx * sx + sy * sy - w;
  let poly = { pts: boundsPts, labs: boundsPts.map((_, k) => -1 - k) };''', '''function cellAreaAt(sx, sy, w, seeds, weights, boundsPts, tris, sea) {
  const pot = sx * sx + sy * sy - w;
  let poly = { pts: boundsPts, labs: boundsPts.map((_, k) => -1 - k) };
  if (sea) { poly = seaCut(poly, sx, sy, w); if (poly.pts.length < 3) return 0; }   // MEMBRANE''')
replace('function entryWeight(sx, sy, target, seeds, weights, boundsPts, tris, scale) {', 'function entryWeight(sx, sy, target, seeds, weights, boundsPts, tris, scale, sea) {')
replace('    if (cellAreaAt(sx, sy, mid, seeds, weights, boundsPts, tris) < target) lo = mid; else hi = mid;', '    if (cellAreaAt(sx, sy, mid, seeds, weights, boundsPts, tris, sea) < target) lo = mid; else hi = mid;')

# THE JACOBIAN: a cell's edge on the sea moves out with its reach
replace('function buildJacobian(diagram, seeds) {', 'function buildJacobian(diagram, seeds, seaW) {')
replace('''  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) if (j !== i) s += A[i][j];
    A[i][i] = -s;
  }
  return A;
}''', '''  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) if (j !== i) s += A[i][j];
    A[i][i] = -s;
  }
  if (seaW) {   // MEMBRANE: an edge on the sea stands at the reach sqrt(w), which moves by 1/(2 sqrt(w)) a unit of weight
    let shore = 0;
    for (let i = 0; i < n; i++) {
      const r = Math.sqrt(Math.max(1e-12, seaW[i]));
      for (const { pts, labs } of (diagram.cells[i].pieces || [diagram.cells[i]])) for (let k = 0, m = pts.length; k < m; k++) if (labs[k] === SEA) {
        const p = pts[k], q = pts[k + 1 === m ? 0 : k + 1], L = Math.hypot(q[0] - p[0], q[1] - p[1]);
        A[i][i] += L / (2 * r); shore += L;
      }
    }
    A.shore = shore;
  }
  return A;
}
// the whole system, pivoted: with the sea there is no free gauge to pin
function solveFull(A, g) {
  const n = g.length, M = [];
  for (let i = 0; i < n; i++) { const row = new Float64Array(n + 1); for (let j = 0; j < n; j++) row[j] = A[i][j]; row[n] = g[i]; M.push(row); }
  for (let c = 0; c < n; c++) {
    let piv = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
    if (piv !== c) { const t = M[c]; M[c] = M[piv]; M[piv] = t; }
    const pv = M[c][c] || 1e-30;
    for (let r = c + 1; r < n; r++) { const f = M[r][c] / pv; if (f === 0) continue; for (let j = c; j <= n; j++) M[r][j] -= f * M[c][j]; }
  }
  const x = new Float64Array(n);
  for (let c = n - 1; c >= 0; c--) { let s = M[c][n]; for (let j = c + 1; j < n; j++) s -= M[c][j] * x[j]; x[c] = s / (M[c][c] || 1e-30); }
  return x;
}''')

# THE SOLVER, with the sea: its claim beside the bidders', its own gauge
replace('''  let tSum = 0;
  for (const t of targets) {
    if (!(t > 0)) throw new Error('every claim must be positive');
    tSum += t;
  }
  const tgt = Float64Array.from(targets, t => t * domainArea / tSum);

  let w = w0 ? Float64Array.from(w0) : new Float64Array(n);
  const prepared = prepareDiagram(seeds, boundsPts);
  let evals = 0;
  let diag = computeDiagram(seeds, w, boundsPts, tris, prepared); evals++;''', '''  let tSum = 0;
  for (const t of targets) {
    if (!(t > 0)) throw new Error('every claim must be positive');
    tSum += t;
  }
  const sea = opts.sea && opts.sea.claim > 0 ? opts.sea : null;   // MEMBRANE: the sea's claim, beside the bidders'
  if (sea) tSum += sea.claim;
  const tgt = Float64Array.from(targets, t => t * domainArea / tSum);
  const seaTgt = sea ? sea.claim * domainArea / tSum : 0;

  let w = w0 ? Float64Array.from(w0) : (sea ? Float64Array.from(tgt, t => t / Math.PI) : new Float64Array(n));
  const prepared = prepareDiagram(seeds, boundsPts);
  let evals = 0;
  const diagramAt = ww => computeDiagram(seeds, ww, boundsPts, tris, prepared, !!sea);
  let diag = diagramAt(w); evals++;
  // MEMBRANE: A GAUGE FOR THE SEA. Weights from an auction without the sea
  // mean nothing to it (only their differences did). One shift of them all
  // gives the sea its area, and Newton goes on from there. The sea's area
  // falls as the shift grows, so the shift is found on a bracket by regula
  // falsi, the Illinois way: from the shift at which the first reach just
  // touches its cell (no sea yet; the cells as they are, uncut) down to the
  // one at which every reach is gone (all sea).
  if (sea) {
    const seaOf = d => { let a = 0; for (const x of d.areas) a += x; return domainArea - a; };
    let wmax = -Infinity, wmin = Infinity; for (const q of w) { wmax = Math.max(wmax, q); wmin = Math.min(wmin, q); }
    let reach = 0; for (const p of boundsPts) for (const s of seeds) reach = Math.max(reach, (p[0] - s[0]) ** 2 + (p[1] - s[1]) ** 2);
    const shore = () => { let L = 0; for (const c of diag.cells) for (const { pts, labs } of (c.pieces || [c])) for (let k = 0; k < pts.length; k++) if (labs[k] === SEA) L++; return L; };
    if (minOf(diag.areas) <= 0 || !shore()) {
      let hi = reach - wmin;
      if (!(minOf(diag.areas) <= 0)) { hi = Infinity; diag.cells.forEach((c, i) => { let R = 0; for (const pc of (c.pieces || [c])) for (const p of pc.pts) R = Math.max(R, (p[0] - seeds[i][0]) ** 2 + (p[1] - seeds[i][1]) ** 2); hi = Math.min(hi, R - w[i]); }); }
      let lo = -wmax, flo = domainArea - seaTgt, fhi = -seaTgt, side = 0, best = null;
      for (let k = 0; k < 24; k++) {
        let mid = (lo * fhi - hi * flo) / (fhi - flo);
        if (!(mid > lo && mid < hi)) mid = (lo + hi) / 2;
        const d = diagramAt(Float64Array.from(w, q => q + mid)); evals++;
        const f = seaOf(d) - seaTgt;
        best = { mid, d };
        if (Math.abs(f) <= 1e-4 * Math.max(1, seaTgt)) break;
        if (f > 0) { lo = mid; flo = f; if (side === 1) fhi /= 2; side = 1; }
        else { hi = mid; fhi = f; if (side === -1) flo /= 2; side = -1; }
      }
      w = Float64Array.from(w, q => q + best.mid); diag = best.d;
    }
  }''')
replace('''  if (w0 && minOf(diag.areas) <= 0) {''', '''  if (w0 && !sea && minOf(diag.areas) <= 0) {''')
replace('''  const eps0 = 0.5 * Math.min(minOf(tgt), minOf(diag.areas));''', '''  // MEMBRANE: a seed the sea's gauge leaves empty re-enters against everyone,
  // at its claim, with the sea
  if (sea && minOf(diag.areas) <= 0) {
    let scale = 0;
    for (const p of boundsPts) scale = Math.max(scale, 4 * (p[0] * p[0] + p[1] * p[1]));
    for (const q of w) scale = Math.max(scale, 4 * Math.abs(q));
    const inS = [], inW = [], empties = [];
    for (let i = 0; i < n; i++) { if (diag.areas[i] > 0) { inS.push(seeds[i]); inW.push(w[i]); } else empties.push(i); }
    for (const i of empties) { w[i] = entryWeight(seeds[i][0], seeds[i][1], Math.min(tgt[i], 0.98 * domainArea), inS, inW, boundsPts, tris, scale, true); inS.push(seeds[i]); inW.push(w[i]); }
    diag = diagramAt(w); evals++;
  }
  const eps0 = 0.5 * Math.min(minOf(tgt), minOf(diag.areas));''')
replace('''    const dw = solvePinned(buildJacobian(diag, seeds), g);''', '''    const J = buildJacobian(diag, seeds, sea ? w : null);
    const dw = sea && J.shore > 1e-9 ? solveFull(J, g) : solvePinned(J, g);''')
replace('''      const dt = computeDiagram(seeds, wt, boundsPts, tris, prepared); evals++;''', '''      const dt = diagramAt(wt); evals++;''')
replace('''  let mean = 0;
  for (let i = 0; i < n; i++) mean += w[i];
  mean /= n;
  for (let i = 0; i < n; i++) w[i] -= mean;

  return { weights: w, iterations: iter, evals, maxRelErr: maxRel, converged, diagram: diag, nonConvex: !!tris };''', '''  if (!sea) {   // MEMBRANE: with the sea the gauge is the sea's zero, and not free
    let mean = 0;
    for (let i = 0; i < n; i++) mean += w[i];
    mean /= n;
    for (let i = 0; i < n; i++) w[i] -= mean;
  }

  return { weights: w, iterations: iter, evals, maxRelErr: maxRel, converged, diagram: diag, nonConvex: !!tris, sea: !!sea };''')

# THE HIVE: whitespace's own share and the sea's, and the swarm feeling the screen
replace('''  // A CELL MAY BECOME A WALL AS SOON AS IT ALREADY IS ONE.''', '''  // MEMBRANE. WHILE THE PAGE CHANGES ITS WHITESPACE IS PART SEA: on the page,
  // outside the stories, which choreograph their whitespace
  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }
  // how much of a whitespace's claim is its own cell, not the sea's: all of
  // it at rest; whitespace that closes melts into the sea as a cell melts,
  // over MELT from when the change reaches it; whitespace that opens is sea
  // until the cells leaving it land, and settles into its place on its own
  // crystal, which reads their clocks
  seaBeta(b) {
    if (b.leaving) { const j = b.journey; if (!j) return 0; return 1 - S3((this.t - j.t0 - (j.delay || 0)) / MELT); }
    if (b.table && b.table.mode === 'open') return Math.max(0, Math.min(1, b.crystal));
    return 1;
  }
  // THE SWARM FEELS THE SCREEN. A cell is liquid from when it has melted
  // (MELT from when the change reaches it) until it locks as it lands (the
  // lock's own clock: the last 0.35 s of its journey and 0.15 s after). A
  // liquid cell touching the screen gives up its size to the sea, and takes
  // it back once clear, each over MELT; as it locks it is its whole size
  // again, whatever it gave up, so it lands exact.
  seaFeel(dt, t) {
    for (const b of this.bodies) {
      if (b.isVoid || b.isSelf || b.leaving || b.reelPinned || !this.seaOpen()) { b.seaLiquid = 0; b.seaFit = 1; continue; }
      const j = b.journey;
      if (!j) { b.seaLiquid = 0; b.seaFit = 1; continue; }
      if (b.seaJ !== j) { b.seaJ = j; j.l0 = b.seaLiquid || 0; }
      const s = t - j.t0 - (j.delay || 0);
      const melt = 1 - (1 - j.l0) * (1 - S3(Math.max(0, s) / MELT));
      const lock = b.rect ? S3((s - (j.hold || 0) - j.dur + 0.35) / 0.50) : 0;
      b.seaLiquid = melt * (1 - lock);
      let touch = false;
      if (b.loops) for (const L of b.loops) { for (let k = 0; k < L.length && !touch; k++) { const p = L[k], q = L[(k + 1) % L.length]; const on = (a, c, v) => Math.abs(a - v) < 0.5 && Math.abs(c - v) < 0.5; touch = on(p[0], q[0], 0) || on(p[0], q[0], this.W) || on(p[1], q[1], 0) || on(p[1], q[1], this.H); } if (touch) break; }
      const f = b.seaFit === undefined ? 1 : b.seaFit, k = 1 - Math.exp(-dt / MELT);
      b.seaFit = touch ? f + (SEA_FIT_MIN - f) * k : f + (1 - f) * k;
    }
  }
  // how much of its claim a cell of the swarm bids for: all of it, less what it has given the sea
  seaKeep(b) { return 1 - (b.seaLiquid || 0) * (1 - (b.seaFit === undefined ? 1 : b.seaFit)); }
  // the sea's claim: every whitespace's share that is not its own cell (a
  // hole's, what its shape has not yet taken), and what the cells have given it
  seaClaimOf(b) {
    if (b.isSelf || b.wall) return 0;
    if (!b.isVoid) { let c = 0; for (const q of b.subs) c += Math.max(0, q.claim); return c * (1 - this.seaKeep(b)); }
    const c = Math.max(0, b.claim);
    return b.hole ? c * (1 - Math.max(0, Math.min(1, b.crystal))) : c * (1 - this.seaBeta(b));
  }

  // A CELL MAY BECOME A WALL AS SOON AS IT ALREADY IS ONE.''')
replace('''  steer(dt, t) {
    const W = this.W, H = this.H;''', '''  steer(dt, t) {
    const W = this.W, H = this.H;
    if (this.depth === 0) this.seaFeel(dt, t);   // MEMBRANE''')
replace('''        const e = b.progress, m = 1 - e, p = b.path;
        const px = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex;
        const py = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey;''', '''        const e = b.progress, m = 1 - e, p = b.path;
        let px = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex;
        let py = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey;
        if (this.depth === 0 && b.seaLiquid > 0 && !b.isVoid && !b.reelPinned) {   // MEMBRANE: a liquid cell keeps its plan its own radius clear of the screen
          const r = b.seaLiquid * Math.sqrt(Math.max(0, b.claim * this.seaKeep(b)) * this.PW * this.PH / Math.PI);
          px = 2 * r >= W ? W / 2 : Math.min(W - r, Math.max(r, px));
          py = 2 * r >= H ? H / 2 : Math.min(H - r, Math.max(r, py));
        }''')

# THE MAIN AUCTION: whitespace bids its own share, a cell what it keeps; the rest is the sea's
replace('''    const active = subs.filter(s => s.claim >= ACTIVE_MIN && !s.body.hole);
    this.ground = null;''', '''    // MEMBRANE: whitespace bids only its own share, a cell what it keeps; the rest is the sea's
    const seaOn = this.seaOpen();
    const claimOf = s => !seaOn ? s.claim : s.claim * (s.body.isVoid ? this.seaBeta(s.body) : this.seaKeep(s.body));
    const active = subs.filter(s => claimOf(s) >= ACTIVE_MIN && !s.body.hole);
    const seaBodies = seaOn ? this.bodies.filter(b => this.seaClaimOf(b) > 0) : [];
    let seaClaim = 0; for (const b of seaBodies) seaClaim += this.seaClaimOf(b);
    this.ground = null;''')
replace('''    const claims = active.map(s => s.claim);
    // A seed entering the auction''', '''    const claims = active.map(claimOf);
    // A seed entering the auction''')
replace('''    const domainArea = tris ? Math.max(1, dArea) : Math.max(1, Math.abs(ringArea(bounds)));
    let tSum = 0; for (const c of claims) tSum += c;
    if (!live.length) {
      // a cold hive: weights by radius put every bisector about where the
      // claims want it, so the first solve is already close
      for (const s of active) s.w = s.claim * domainArea / tSum / Math.PI;''', '''    const domainArea = tris ? Math.max(1, dArea) : Math.max(1, Math.abs(ringArea(bounds)));
    let tSum = seaClaim; for (const c of claims) tSum += c;
    const seaIn = seaClaim > 0;
    if (!live.length) {
      // a cold hive: weights by radius put every bisector about where the
      // claims want it, so the first solve is already close
      for (const s of active) s.w = claimOf(s) * domainArea / tSum / Math.PI;''')
replace('''        const fair = s.claim * domainArea / tSum;
        if (!inSeeds.length) { s.w = fair / Math.PI; continue; }''', '''        const fair = claimOf(s) * domainArea / tSum;
        if (!inSeeds.length) { s.w = fair / Math.PI; continue; }''')
replace('''        } else s.w = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, tris, scale);
        inSeeds.push([s.x, s.y]); inW.push(s.w);''', '''        } else s.w = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, tris, scale, seaIn);
        inSeeds.push([s.x, s.y]); inW.push(s.w);''')
replace('''    let sig = active.length + '|' + (this.W * 8 | 0)''', '''    let sig = 'S' + (seaClaim * 1e4 | 0) + '|' + active.length + '|' + (this.W * 8 | 0)''')
replace('''      const live2 = comp.groups.map((_, k) => mine[k].length > 0);''', '''      const live2 = comp.groups.map((_, k) => mine[k].length > 0);
      const seaK = comp.groups.map(() => 0);   // MEMBRANE: each pocket's sea is the whitespace standing in it, and what its cells have given
      for (const b of seaBodies) { cueWho = b; seaK[this.pocketOf(comp, pieces, b.x, b.y)] += this.seaClaimOf(b); }
      cueWho = null;''')
replace('''        if (live2[k] && !crack[k]) continue;
        if (!live2[k] && this.holes.length) { this.adoptGround(comp.groups[k].map(pi => pieces[pi])); comp.groups[k] = []; continue; }''', '''        if (live2[k] && !crack[k]) continue;
        if (!live2[k] && this.holes.length) { this.adoptGround(comp.groups[k].map(pi => pieces[pi])); comp.groups[k] = []; continue; }
        if (!live2[k] && seaK[k] > 0) continue;   // MEMBRANE: ground only the sea stands in is the sea's''')
replace('''        const sol = idx.length === 1
          ? { weights: [gw[0]], diagram: computeDiagram([gs[0]], [gw[0]], bounds, gt), maxRelErr: 0, converged: true, iterations: 0 }
          : solveWeights(gs, gc, bounds, gw, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(i => this.sitePaint(active[i])) });''', '''        const sol = idx.length === 1 && !(seaK[k] > 0)
          ? { weights: [gw[0]], diagram: computeDiagram([gs[0]], [gw[0]], bounds, gt), maxRelErr: 0, converged: true, iterations: 0 }
          : solveWeights(gs, gc, bounds, gw, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(i => this.sitePaint(active[i])), sea: seaK[k] > 0 ? { claim: seaK[k] } : null });''')
replace('''        this.solved = { weights: W, diagram: { cells, areas }, maxRelErr: err, converged: conv, iterations: iters };''', '''        this.solved = { weights: W, diagram: { cells, areas }, maxRelErr: err, converged: conv, iterations: iters, sea: seaIn };''')
replace('''    if (active.length === 1) {
      // one bidder and no rival: the ground is all of it, no auction needed''', '''    if (active.length === 1 && !seaIn) {
      // one bidder and no rival: the ground is all of it, no auction needed''')
replace('''    const sol = solveWeights(seeds, claims, bounds, active.map(s => s.w), { maxIter: this.iterBudget(), tris, domainArea: tris ? dArea : undefined, paint: active.map(s => this.sitePaint(s)) });
    this.solveMs = performance.now() - t0;''', '''    const sol = solveWeights(seeds, claims, bounds, active.map(s => s.w), { maxIter: this.iterBudget(), tris, domainArea: tris ? dArea : undefined, paint: active.map(s => this.sitePaint(s)), sea: seaIn ? { claim: seaClaim } : null });
    this.solveMs = performance.now() - t0;''')

# THE SHADOW AUCTION, the same
replace('''    const bidders = subs.filter(s => !s.body.wall && s.claim >= ACTIVE_MIN);''', '''    const seaOn = this.seaOpen();
    const claimOf = s => !seaOn || s.body.hole ? s.claim : s.claim * (s.body.isVoid ? this.seaBeta(s.body) : this.seaKeep(s.body));   // MEMBRANE: a hole bids for the cell it would have at its claim, as ever
    const bidders = subs.filter(s => !s.body.wall && claimOf(s) >= ACTIVE_MIN);
    const seaBodies = seaOn ? this.bodies.filter(b => !b.isSelf && !b.wall && !b.hole && this.seaClaimOf(b) > 0) : [];''')
replace('''    for (const s of bidders) { cueWho = s.body; mine[comp ? this.pocketOf(comp, pieces, s.x, s.y) : 0].push(s); }
    cueWho = null;''', '''    for (const s of bidders) { cueWho = s.body; mine[comp ? this.pocketOf(comp, pieces, s.x, s.y) : 0].push(s); }
    const seaK = groups.map(() => 0);
    for (const b of seaBodies) { cueWho = b; seaK[comp ? this.pocketOf(comp, pieces, b.x, b.y) : 0] += this.seaClaimOf(b); }
    cueWho = null;''')
replace('''      let tSum = 0; for (const s of idx) tSum += s.claim;
      // A SEED ENTERS AT THE AREA IT IS PAINTED AT.''', '''      let tSum = seaK[k]; for (const s of idx) tSum += claimOf(s);
      // A SEED ENTERS AT THE AREA IT IS PAINTED AT.''')
replace('''        const fair = s.claim * ga / tSum;''', '''        const fair = claimOf(s) * ga / tSum;''')
replace('''        s.wShadow = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, gt, scale);''', '''        s.wShadow = entryWeight(s.x, s.y, target, inSeeds, inW, bounds, gt, scale, seaK[k] > 0);''')
replace('''      const seeds = idx.map(s => [s.x, s.y]), claims = idx.map(s => s.claim), w0 = idx.map(s => s.wShadow);
      const sol = idx.length === 1
        ? { weights: w0, diagram: computeDiagram(seeds, w0, bounds, gt) }
        : solveWeights(seeds, claims, bounds, w0, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(s => this.sitePaint(s)) });''', '''      const seeds = idx.map(s => [s.x, s.y]), claims = idx.map(claimOf), w0 = idx.map(s => s.wShadow);
      const sol = idx.length === 1 && !(seaK[k] > 0)
        ? { weights: w0, diagram: computeDiagram(seeds, w0, bounds, gt) }
        : solveWeights(seeds, claims, bounds, w0, { maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(s => this.sitePaint(s)), sea: seaK[k] > 0 ? { claim: seaK[k] } : null });''')

# A POINT IN THE SEA IS NOBODY'S
replace('''      const bid = dx * dx + dy * dy - w[i];
      if (bid < best) { best = bid; id = s.body.isVoid ? -1 : s.body.id; }
    }
    return id;''', '''      const bid = dx * dx + dy * dy - w[i];
      if (bid < best) { best = bid; id = s.body.isVoid ? -1 : s.body.id; }
    }
    return this.solved.sea && best > 0 ? -1 : id;   // MEMBRANE: the sea''')
replace('''      const bid = dx * dx + dy * dy - w[i];
      if (bid < best) { best = bid; body = s.body; }
    }
    return body;''', '''      const bid = dx * dx + dy * dy - w[i];
      if (bid < best) { best = bid; body = s.body; }
    }
    return this.solved.sea && best > 0 ? null : body;   // MEMBRANE: the sea''')

(ROOT / 'membrane.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
