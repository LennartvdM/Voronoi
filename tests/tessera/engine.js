/* ================================================================ TESSERA
 * The transition as rigid tiles whose lattices conform along every seam.
 *
 * Astra I put every transitioning body into one solved partition, with one
 * weight per body and a lattice of sites forming its rectangle. It calmed
 * the strobe, and it kept two habits the owner could still see. A tile
 * MELTS to a point before it travels (the electric shock at departure).
 * And a lattice that travels off the grid CORRUGATES against the lattices
 * it slides past (Astra II's ripple): the seam between two columns of
 * sites whose rows are offset is a zigzag of tilted bisectors, whatever
 * the weights say, with an amplitude of an eighth of the pitch.
 *
 * Tessera keeps the power diagram — the one solver in this file that is
 * well-conditioned everywhere, exact at rest and continuous in every
 * input — and removes the zigzag at its cause. A SEAM IS STRAIGHT WHEN THE
 * TWO COLUMNS IT LIES BETWEEN HAVE THE SAME ROWS. So along every seam a
 * tile's edge column carries, besides its own rows, a site at each row of
 * the tile across the seam (and that tile carries this one's rows): every
 * pair across the seam is then level, every bisector is the midline, and
 * the weights slide the whole seam as one line. A mirrored site fades in
 * over half a pitch at the seam's ends, so a seam that lengthens as tiles
 * slide past each other grows its straight part continuously; at a corner
 * the picture is the plain diagram's, a small wedge, never a wave.
 *
 * A tile therefore does not melt to move. It departs rigid, rides the same
 * bezier as before, changes size en route (its lattice stretches, edge
 * sites on the edges, interior sites evenly between — an interior site
 * that comes or goes is a seam inside the tile, invisible), and lands. A
 * small packing pass on the footprints keeps tiles from lying on top of
 * one another, so the change reads as bodies yielding rather than passing
 * through: a traveller has the right of way; a body waiting for its turn,
 * or sitting settled, moves aside along whichever axis costs less (dearer
 * when it would push a body back from where it is going) and returns on
 * its own clock. The page's edges are walls to the packing, so a footprint
 * is always its cell. Whitespace is whatever the tiles are not: a void is its
 * rectangle's lattice, never packed, its sites suppressed under any tile
 * that stands on them. The auction still hands every body its claim,
 * every frame, from these positions alone: nothing is stored, nothing is
 * tweened, no rate is limited.
 */
const TES_RETURN_TAU = 0.22;   // s: a displaced footprint's return clock
const TES_PACK_ITERS = 2;      // packing sweeps per motion step
const TES_PACK_TAU = 0.06;     // s: an overlap is taken out on this clock, not in one frame
const TES_PUSH_SPEED = 1e9;    // px/s: the most a footprint yields in a second (unbounded: see the packing note)
const TES_SNAP = 0.02;         // px: a displacement below this is none
const TES_TRAVEL_COMP = 0.1;   // a traveller yields this much against a yielder's 1
const TES_DEPART_PUSH = 40;    // px: a waiter shoved this far off its slot departs now

// Astra I's grouped solve, with a fixed offset per site: a body's sites bid
// at its one weight minus their own penalty.
// A full Gaussian solve with partial pivoting, for the damped system: it
// has no null space, so nothing is pinned.
function tesSolveFull(A, g) {
  const n = g.length, M = A.map((row, i) => { const out = new Float64Array(n + 1); out.set(row); out[n] = g[i]; return out; });
  for (let c = 0; c < n; c++) {
    let piv = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
    if (piv !== c) { const t = M[c]; M[c] = M[piv]; M[piv] = t; }
    const pv = M[c][c] || 1e-30;
    for (let r = c + 1; r < n; r++) {
      const f = M[r][c] / pv;
      if (f === 0) continue;
      for (let j = c; j <= n; j++) M[r][j] -= f * M[c][j];
    }
  }
  const x = new Float64Array(n);
  for (let c = n - 1; c >= 0; c--) {
    let s = M[c][n];
    for (let j = c + 1; j < n; j++) s -= M[c][j] * x[j];
    x[c] = s / (M[c][c] || 1e-30);
  }
  return x;
}

function tesseraSolve(seeds, owner, offset, targets, w0, bounds, maxIter = 16, lambda0 = 0, maxEvals = 32) {
  const n = targets.length, area = Math.abs(ringArea(bounds));
  const sum = targets.reduce((a, b) => a + b, 0);
  const target = targets.map(a => a * area / sum);
  let w = Float64Array.from(w0), evaluations = 0;
  const siteWeights = ws => owner.map((i, k) => ws[i] - offset[k]);
  const evaluate = ws => {
    const diagram = computeDiagram(seeds, siteWeights(ws), bounds);
    const areas = new Float64Array(n);
    diagram.areas.forEach((a, i) => { areas[owner[i]] += a; });
    evaluations++;
    return { diagram, areas };
  };
  let current = evaluate(w);
  for (let pass = 0; pass < 3 && minOf(current.areas) <= 0; pass++) {
    for (let i = 0; i < n; i++) {
      if (current.areas[i] > 0) continue;
      let lo = -8 * area - Math.max(...Array.from(w, Math.abs)) - Math.max(...offset);
      let hi = -lo;
      for (let k = 0; k < 36; k++) {
        const mid = (lo + hi) / 2; w[i] = mid;
        if (evaluate(w).areas[i] < target[i]) lo = mid; else hi = mid;
      }
      w[i] = (lo + hi) / 2;
      current = evaluate(w);
    }
  }
  const floor = .5 * Math.min(minOf(target), minOf(current.areas));
  // DAMPED NEWTON. The Newton step, with every body's own diagonal scaled by
  // (1 + lambda): at lambda 0 it is Newton, and as lambda grows each body
  // moves its own weight alone by its own residual, the step that cannot
  // overshoot. A step that does not lower the residual, or takes a body
  // below the floor, is refused and lambda grows fourfold; an accepted step
  // shrinks it by three. lambda is warm across frames, so a page that is
  // behaving is solved at Newton's pace and a page mid-contact at a safe one.
  // The budget is in evaluations, whatever it took: a frame is never held
  // for a solve that is not converging.
  let lam = lambda0, iterations = 0, maxRel = Infinity;
  const budget = maxEvals + evaluations;
  for (; iterations < maxIter && evaluations < budget; iterations++) {
    const residual = target.map((a, i) => a - current.areas[i]);
    maxRel = Math.max(...residual.map((a, i) => Math.abs(a) / target[i]));
    if (maxRel <= 1e-6) break;
    const J = Array.from({ length: n }, () => new Float64Array(n));
    current.diagram.cells.forEach((c, i) => {
      const a = owner[i];
      for (let k = 0; k < c.pts.length; k++) {
        const j = c.labs[k];
        if (j < 0 || owner[j] === a) continue;
        const p = c.pts[k], q = c.pts[(k + 1) % c.pts.length];
        const d = Math.hypot(seeds[i][0] - seeds[j][0], seeds[i][1] - seeds[j][1]);
        if (d > 1e-9) J[a][owner[j]] -= Math.hypot(q[0] - p[0], q[1] - p[1]) / (2 * d);
      }
    });
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) J[i][j] = J[j][i] = .5 * (J[i][j] + J[j][i]);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== j) J[i][i] -= J[i][j];
    const norm = norm2(residual);
    let accepted = false;
    for (let k = 0; k < 8 && evaluations < budget; k++) {
      const Jd = J.map((row, i) => { const r = Float64Array.from(row); r[i] *= 1 + lam; return r; });
      const dw = lam > 1e-9 ? tesSolveFull(Jd, residual) : solvePinned(J, residual);
      const nextW = Float64Array.from(w, (x, i) => x + dw[i]);
      if (!nextW.every(Number.isFinite)) { lam = Math.min(1e6, Math.max(1e-3, lam) * 4); continue; }
      const next = evaluate(nextW);
      if (minOf(next.areas) >= floor && norm2(target.map((x, i) => x - next.areas[i])) < norm) {
        w = nextW; current = next; accepted = true; lam = lam < 1e-3 ? 0 : lam / 3; break;
      }
      lam = Math.min(1e6, Math.max(1e-3, lam) * 4);
    }
    if (!accepted) break;
  }
  maxRel = Math.max(...target.map((a, i) => Math.abs(a - current.areas[i]) / a));
  const mean = w.reduce((a, b) => a + b, 0) / n;
  w = w.map(x => x - mean);
  return { weights: siteWeights(w), groupWeights: Array.from(w), diagram: current.diagram,
    maxRelErr: maxRel, converged: maxRel <= 1e-6, iterations, evals: evaluations, lambda: lam };
}

// The root keeps no walls and no holes between frames: every body is in
// the one partition. (At rest, solve() names every tile a wall.)
const tesOldWalls = Hive.prototype.computeWalls;
Hive.prototype.computeWalls = function() {
  if (this.depth !== 0) return tesOldWalls.call(this);
  this.walls = []; this.holes = [];
  for (const b of this.bodies) {
    b.wall = null; b.hole = null; b.holeCore = null; b.holeLinger = false; b.holeExtra = [];
  }
};

// The footprint this body shows: half sizes in px, and how much of a tile
// it is (mix 1: its rectangle; 0: a point). Null for a body with no
// rectangle to show.
Hive.prototype.tesFootprint = function(b) {
  if (b.isSelf) return null;
  const PW = this.PW, PH = this.PH, j = b.journey;
  if (b.isVoid) {
    const r = b.rect || b.formRect;
    return r ? { hw: (r[2] - r[0]) * PW / 2, hh: (r[3] - r[1]) * PH / 2, mix: 1, rect: r } : null;
  }
  if (b.rect && !b.leaving) {
    const r = b.rect;
    let hw = (r[2] - r[0]) * PW / 2, hh = (r[3] - r[1]) * PH / 2;
    if (j && j.stamp && b.sizeFrom) {
      // a tile changes size on the way, on the same curve it travels: its
      // proportions blend, and its footprint holds exactly its claim's area
      // at every instant, so the weight never has to dilate it into a blob
      const e = b.progress;
      hw = b.sizeFrom[0] * PW * (1 - e) + hw * e;
      hh = b.sizeFrom[1] * PH * (1 - e) + hh * e;
      const k = Math.sqrt(Math.max(1e-9, b.claim * PW * PH) / (4 * hw * hh));
      hw *= k; hh *= k;
    }
    return { hw, hh, mix: b.crystal, rect: r };
  }
  if (b.formRect && b.crystal > 0) {
    // melting out of a rectangle into the flock: the old formation, going
    const r = b.formRect;
    return { hw: (r[2] - r[0]) * PW / 2, hh: (r[3] - r[1]) * PH / 2, mix: b.crystal, rect: r };
  }
  return null;
};

// A settled tile asked to go somewhere departs as it is: rigid, no melt.
// Everything else (a void, a body leaving for the flock, a body arriving
// from it) keeps Astra I's clocks.
const tesOldSeat = Hive.prototype.seatBody;
Hive.prototype.seatBody = function(b, rect, T = 0, timing) {
  if (this.depth !== 0) return tesOldSeat.call(this, b, rect, T, timing);
  const fp = this.tesFootprint(b), had = b.journey;
  const tile = !!fp && fp.mix >= 1 - 1e-9 && !b.isVoid && !b.leaving;
  tesOldSeat.call(this, b, rect, T, timing);
  if (b.journey === had || !b.journey) return;         // a bystander: nothing new
  if (!tile) return;
  b.journey.hold = 0;
  b.journey.stamp = true;
  b.journey.c0 = 1;
  b.sizeFrom = [fp.hw / this.PW, fp.hh / this.PH];
  b.formRect = b.rect;
};

// A tile stays a tile: crystal 1 the whole way; the lock is only the pin.
// A void is always its rectangle: it never melts, it only fills or empties.
const tesOldCrystal = Hive.prototype.updateCrystal;
Hive.prototype.updateCrystal = function(b, t) {
  const j = b.journey;
  if (this.depth !== 0 || !j || (b.table && b.table.mode === 'open')) return tesOldCrystal.call(this, b, t);
  if (b.isVoid && b.leaving) { b.crystal = 1; return; }
  if (!j.stamp) return tesOldCrystal.call(this, b, t);
  const s = t - j.t0 - j.delay;
  if (s < 0) return;
  const L = b.rect && !b.leaving ? S3((s - j.dur + 0.35) / 0.50) : 0;
  b.crystal = 1;
  b.pin = L;
};

// How much of a body's footprint displacement is in force: a landing tile
// gives its displacement up over the lock, so it is exactly on its slot
// the moment it is pinned.
function tesPinKeep(b) { return 1 - Math.pow(b.pin || 0, 4); }

// Who yields at a contact. A traveller has the right of way; a body waiting
// for its turn, or sitting settled, moves aside for it and comes back. A
// landing tile is immovable as its pin takes.
Hive.prototype.tesCompliance = function(b) {
  const pk = tesPinKeep(b);
  if (pk < 1e-3) return 0;
  const j = b.journey;
  const travelling = j && j.stamp && b.progress > 0 && b.progress < 1;
  return pk * (travelling ? TES_TRAVEL_COMP : 1);
};

// The seeds' repulsion is a law for liquid bodies. A tile is not liquid: it
// meets its neighbours through the packing of footprints, not by shoving
// seeds. Repelled as well, a tile is held back from its carrot until the
// pin takes it, and then it is yanked home — the one jump this design has
// no other source for. So a tile does not repel and is not repelled.
const tesOldSeparate = Hive.prototype.separate;
Hive.prototype.separate = function(dt) {
  if (this.depth !== 0) return tesOldSeparate.call(this, dt);
  const bodies = this.bodies;
  const mob = b => b.isSelf || b.isVoid || (b.journey && b.journey.stamp) ? 0 : 1 - b.crystal;
  const m = bodies.map(mob);
  if (m.every(v => v < 0.005)) return;
  let claimSum = 0;
  for (const b of bodies) claimSum += b.claim;
  const areaPer = (this.W * this.H) / Math.max(1e-9, claimSum);
  const rad = bodies.map(b => Math.sqrt(b.claim * areaPer / Math.PI));
  const F = 2600;
  for (let i = 0; i < bodies.length; i++) {
    const A = bodies[i];
    if (A.isSelf || A.isVoid) continue;
    for (let j = i + 1; j < bodies.length; j++) {
      const B = bodies[j];
      if (B.isSelf || B.isVoid) continue;
      const R = 0.85 * (rad[i] + rad[j]);
      const dx = B.x - A.x, dy = B.y - A.y, dn = Math.hypot(dx, dy);
      const ox = dx + (B.vx - A.vx) * SWERVE_LEAD, oy = dy + (B.vy - A.vy) * SWERVE_LEAD, d = Math.hypot(ox, oy);
      if (dn > 1e-6 && d < R) {
        const f = F * Math.max(m[i], m[j]) * (1 - d / R) * dt / dn;
        A.vx -= dx * f * m[i]; A.vy -= dy * f * m[i];
        B.vx += dx * f * m[j]; B.vy += dy * f * m[j];
      }
    }
  }
};

// THE PACKING. Footprints do not lie on top of each other: every overlapping
// pair is pushed apart along one axis, the move split by compliance. The
// axis is the cheaper penetration, made dearer when it would push a body
// back from where it is going (its wish lies beyond the other body), and
// once chosen it is kept while the pair stays in contact, so a corner
// meeting a corner does not change its mind every frame. A displacement
// relaxes on TES_RETURN_TAU when nothing holds it. Voids are whitespace:
// they neither push nor yield.
Hive.prototype.tesPack = function(h) {
  if (!this.tesContacts) this.tesContacts = new Map();
  const contacts = this.tesContacts;
  const decay = Math.exp(-h / TES_RETURN_TAU);
  const items = [];
  for (const b of this.bodies) {
    if (!b.tesP) b.tesP = { x: 0, y: 0 };
    const p = b.tesP;
    const fp = this.tesFootprint(b);
    if (!fp || b.isVoid || fp.mix < 0.02) { p.x = 0; p.y = 0; continue; }
    p.x *= decay; p.y *= decay;
    if (Math.abs(p.x) < TES_SNAP) p.x = 0;
    if (Math.abs(p.y) < TES_SNAP) p.y = 0;
    const comp = this.tesCompliance(b), pk = tesPinKeep(b);
    // THE PAIR IS TESTED WHERE IT IS GOING, as the seeds' swerve is: the
    // overlap is read on the footprints one short horizon ahead at today's
    // velocities, so a body yields while the other is still coming, gently,
    // and the push is spent before the contact is deep
    const lead = 0;   // read at today's positions: the horizon made crowded corners push harder, not calmer (measured: hero teleports 13 to 19)
    items.push({ b, hw: fp.hw * fp.mix, hh: fp.hh * fp.mix, x: b.x + p.x * pk, y: b.y + p.y * pk, comp, pk, wx: b.x, wy: b.y, lx: b.vx * lead, ly: b.vy * lead, x0: b.x + p.x * pk, y0: b.y + p.y * pk });
  }
  const live = new Set();
  // THE PACKING RELAXES, IT DOES NOT PROJECT. Each sweep takes out a share
  // of every overlap, so a crowded corner settles over a few frames instead
  // of being re-decided whole every frame in whatever order the pairs came:
  // the overlap left over is a few px, which the diagram splits continuously.
  const relax = 1 - Math.exp(-h / TES_PACK_TAU);
  for (let it = 0; it < TES_PACK_ITERS; it++) {
    let moved = false;
    for (let i = 0; i < items.length; i++) {
      const A = items[i];
      for (let j = i + 1; j < items.length; j++) {
        const B = items[j];
        if (A.comp + B.comp <= 0) continue;
        const dx = (B.x + B.lx) - (A.x + A.lx), dy = (B.y + B.ly) - (A.y + A.ly);
        const ox = A.hw + B.hw - Math.abs(dx), oy = A.hh + B.hh - Math.abs(dy);
        if (ox <= 0 || oy <= 0) continue;
        const key = A.b.id + ':' + B.b.id;
        live.add(key);
        const sx = dx >= 0 ? 1 : -1, sy = dy >= 0 ? 1 : -1;
        const share = A.comp / (A.comp + B.comp);
        // pushed against its wish: it wants to go further into the other
        // body than it is in already, so pushing it back settles nothing
        const against = (it, ax, ay, pen) => ((it.wx - it.x) * ax + (it.wy - it.y) * ay) < -(0.5 * pen + 1) ? 1 : 0;
        const cx = ox * (1 + 3 * (share * against(A, -sx, 0, ox) + (1 - share) * against(B, sx, 0, ox)));
        const cy = oy * (1 + 3 * (share * against(A, 0, -sy, oy) + (1 - share) * against(B, 0, sy, oy)));
        let axis = cx <= cy ? 'x' : 'y';
        const prev = contacts.get(key);
        if (prev && ((prev.axis === 'x' && cx <= 2 * cy) || (prev.axis === 'y' && cy <= 2 * cx))) axis = prev.axis;
        contacts.set(key, { axis });
        if (axis === 'x') { A.x -= sx * ox * share * relax; B.x += sx * ox * (1 - share) * relax; }
        else { A.y -= sy * oy * share * relax; B.y += sy * oy * (1 - share) * relax; }
        moved = true;
      }
    }
    // the page's edge is a wall: a footprint pushed through it is pushed
    // back, and the chain that pushed it resolves the other way. Off the
    // page a tile keeps its area only by weight, which dilates it unevenly
    // against its neighbours; on the page its footprint is its cell.
    for (const it of items) {
      if (it.comp <= 0) continue;
      const x0 = it.x - it.hw, x1 = it.x + it.hw, y0 = it.y - it.hh, y1 = it.y + it.hh;
      if (x0 < 0 && x1 <= this.W) { it.x -= x0; moved = true; } else if (x1 > this.W && x0 >= 0) { it.x -= x1 - this.W; moved = true; }
      if (y0 < 0 && y1 <= this.H) { it.y -= y0; moved = true; } else if (y1 > this.H && y0 >= 0) { it.y -= y1 - this.H; moved = true; }
    }
    if (!moved) break;
  }
  for (const key of Array.from(contacts.keys())) if (!live.has(key)) contacts.delete(key);
  // AND A PUSH IS A MOTION, NOT A TELEPORT: a footprint moves no faster
  // under the packing than a body travels
  const cap = TES_PUSH_SPEED * h;
  for (const it of items) {
    if (it.pk < 1e-3) continue;
    const mx = it.x - it.x0, my = it.y - it.y0, m = Math.hypot(mx, my);
    if (m > cap) { it.x = it.x0 + mx * cap / m; it.y = it.y0 + my * cap / m; }
    it.b.tesP.x = (it.x - it.b.x) / it.pk;
    it.b.tesP.y = (it.y - it.b.y) / it.pk;
    // THE PUSH IS THE CHANGE ARRIVING. A body still waiting for its turn
    // that has been shoved a third of a pitch off its slot is in the way of
    // somebody who is going: it goes now, and where it was going anyway.
    // The percolation clock says when the change reaches a body; a body
    // being pushed has been reached.
    const j = it.b.journey;
    if (j && j.stamp && this.t < j.t0 + j.delay && Math.hypot(it.b.tesP.x, it.b.tesP.y) > TES_DEPART_PUSH) j.delay = Math.max(0, this.t - j.t0);
  }
};

const tesOldPre = Hive.prototype.enforcePreconditions;
Hive.prototype.enforcePreconditions = function(h) {
  tesOldPre.call(this, h);
  if (this.depth === 0) this.tesPack(h || 1 / 60);
};

const tesOldSize = Hive.prototype.setSize;
Hive.prototype.setSize = function(W, H) {
  const oldW = this.W, oldH = this.H;
  tesOldSize.call(this, W, H);
  if (this.depth === 0 && oldW > 0 && this.bodies.length) {
    const kx = W / oldW, ky = H / oldH;
    for (const b of this.bodies) if (b.tesP) { b.tesP.x *= kx; b.tesP.y *= ky; }
  }
};

// A tile's lattice: as many columns as its width holds, the outer ones on
// the edges, the rest evenly between; the same for rows.
function tesAxis(c, half, pitch) {
  // ceil, not round: the edge sites stay on the edges until the tile is a
  // single slot wide, where the two meet; rounding would pull them to the
  // centre at a slot and a half and step the outline
  const K = Math.max(1, Math.ceil(2 * half / pitch - 1e-6));
  if (K === 1) return [c];
  const out = [], span = 2 * half - pitch;
  for (let k = 0; k < K; k++) out.push(c - span / 2 + k * span / (K - 1));
  return out;
}

// THE SITES. A free body is a point. A body setting or melting is Astra I's
// lattice, spread by its crystal. A tile is its stretched lattice, and
// then, along every seam it shares with another tile, its edge column (or
// row) carries every row (or column) the column across the seam carries,
// so the seam is one straight line. A void claims the ground its tiles do
// not cover, its own sites suppressed under them.
const tesOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  if (this.depth !== 0) return tesOldPlace.call(this);
  const PW = this.PW, PH = this.PH;
  // 1. where every body stands
  const info = new Map();
  for (const b of this.bodies) {
    if (b.formRect !== b.rect && b.crystal === 0 && !b.isVoid) b.formRect = b.rect;
    const fp = this.tesFootprint(b), mix = fp ? fp.mix : 0;
    const p = b.tesP || { x: 0, y: 0 }, pk = tesPinKeep(b);
    // whitespace stands on its rectangle, whatever its seed does
    const [fx, fy] = b.isVoid && fp ? this.rectCenter(fp.rect) : [b.x + p.x * pk, b.y + p.y * pk];
    const box = fp && mix > 0.02 ? { x0: fx - fp.hw * mix, x1: fx + fp.hw * mix, y0: fy - fp.hh * mix, y1: fy + fp.hh * mix } : null;
    info.set(b, { fp, mix, fx, fy, box });
  }
  // 2. WHITESPACE IS WHAT THE TILES ARE NOT. A void's claim is the ground of
  // its rectangle no content body stands on (a closing void also yields to
  // the voids opening over it), so it never asks for area where its sites
  // are dead, and never holds ground a tile has taken.
  const overlap = (a, b) => Math.max(0, Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0)) * Math.max(0, Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0));
  const contentBoxes = [], openVoids = [];
  for (const b of this.bodies) { const q = info.get(b); if (!q.box) continue; if (b.isVoid) { if (!b.leaving) openVoids.push(q.box); } else contentBoxes.push(q.box); }
  for (const b of this.bodies) {
    if (!b.isVoid) continue;
    const q = info.get(b);
    if (!q.box) continue;
    let free = (q.box.x1 - q.box.x0) * (q.box.y1 - q.box.y0);
    for (const c of contentBoxes) free -= overlap(q.box, c);
    if (b.leaving) for (const o of openVoids) free -= overlap(q.box, o);
    b.claim = Math.max(0, free / (PW * PH));
  }
  // and the whitespace as one thing: the page, less the content's claims.
  // That is the one claim the voids' sites bid for together, and since a
  // tile's footprint holds exactly its claim, it is the page less the tiles:
  // the weights come out alike and every front is where the footprints put
  // it. (Not the ground the tiles leave uncovered: a body melting into the
  // flock covers little and claims much, and whitespace must not take the
  // difference.)
  let whitespace = this.COLS * this.ROWS;
  for (const b of this.bodies) if (!b.isVoid && !b.isSelf) whitespace -= b.claim;
  whitespace = Math.max(0, whitespace);
  // 3. the sites
  const tiles = [];
  // the void that hosts the whitespace: one that is staying or opening, so a
  // closing void (which has no rectangle to be seated in) never keeps the
  // settled page from being read as settled
  const host = this.bodies.find(b => b.isVoid && !b.leaving && info.get(b).box) || this.bodies.find(b => b.isVoid && info.get(b).box) || null;
  for (const b of this.bodies) {
    const { fp, mix, fx, fy } = info.get(b);
    const claim = b.isVoid ? (b === host ? whitespace : 0) : b.claim * (1 + (config.hoverBoost - 1) * b.hoverMix * (1 - mix));
    const weight = b.tesW || 0;
    const site = (x, y, off) => ({ body: b, x, y, w: weight, off, claim, live: true });
    const sites = [];
    b.tesLat = null;
    if (b.isVoid) {
      // whitespace: the page's own lattice, on the one void that hosts it
      if (b === host) for (let r = 0; r < this.ROWS; r++) for (let c = 0; c < this.COLS; c++) sites.push(site((c + .5) * PW, (r + .5) * PH, 0));
      else sites.push({ body: b, x: fx, y: fy, w: weight, off: 0, claim: 0, live: false });
      if (b === host) { b.tesLat = { x0: 0, x1: this.W, y0: 0, y1: this.H }; tiles.push(b); }
    } else if (fp && mix >= 1 - 1e-9) {
      const xs = tesAxis(fx, fp.hw, PW), ys = tesAxis(fy, fp.hh, PH);
      for (const y of ys) for (const x of xs) sites.push(site(x, y, 0));
      // the two edge columns (rows) each carry a set of the rows (columns)
      // they hold; closer than half a pitch they are one edge and share it
      const xl = xs[0], xr = xs[xs.length - 1], yt = ys[0], yb = ys[ys.length - 1];
      const colSet = xr - xl < PW / 2 ? [new Set(ys)] : [new Set(ys), new Set(ys)];
      const rowSet = yb - yt < PH / 2 ? [new Set(xs)] : [new Set(xs), new Set(xs)];
      b.tesLat = { x0: fx - fp.hw, x1: fx + fp.hw, y0: fy - fp.hh, y1: fy + fp.hh, xs, ys,
        colRows: new Map([[xl, colSet[0]], [xr, colSet[colSet.length - 1]]]),
        rowCols: new Map([[yt, rowSet[0]], [yb, rowSet[rowSet.length - 1]]]),
        colsOf: new Map([[colSet[0], xr - xl < PW / 2 ? [xl, xr] : [xl]], [colSet[colSet.length - 1], xr - xl < PW / 2 ? [xl, xr] : [xr]]]),
        rowsOf: new Map([[rowSet[0], yb - yt < PH / 2 ? [yt, yb] : [yt]], [rowSet[rowSet.length - 1], yb - yt < PH / 2 ? [yt, yb] : [yb]]]),
        mirrorOff: new Map() };
      tiles.push(b);
    } else if (fp && mix > 0.02) {
      const r = fp.rect, [cx, cy] = this.rectCenter(r);
      for (let y = r[1]; y < r[3]; y++) for (let x = r[0]; x < r[2]; x++) sites.push(site(fx + mix * ((x + .5) * PW - cx), fy + mix * ((y + .5) * PH - cy), 0));
    }
    if (!sites.length) sites.push(site(fx, fy, 0));
    b.subs = sites;
  }
  const content = tiles.filter(b => !b.isVoid);
  // 4. the seams. Every pair of content tiles facing each other across a
  // gap (or touching): the row sets of the two edge columns are made equal,
  // and again until nothing changes, so a one-column tile carries what both
  // its neighbours carry and each of them carries the other's rows too.
  const occluded = (A, B, lo, hi, axis, v) => {
    for (const C of content) {
      if (C === A || C === B) continue;
      const L = C.tesLat;
      if (axis === 'x') { if (L.x1 > lo + 1 && L.x0 < hi - 1 && L.y0 < v && L.y1 > v) return true; }
      else if (L.y1 > lo + 1 && L.y0 < hi - 1 && L.x0 < v && L.x1 > v) return true;
    }
    return false;
  };
  const seams = [];
  for (const A of content) for (const B of content) {
    if (A === B) continue;
    const LA = A.tesLat, LB = B.tesLat;
    // facing, touching, or overlapping by up to a third of a pitch (the
    // packing takes an overlap out on a clock, so a few px are always there;
    // a seam that lost its mirrors for those px would corrugate)
    if (LB.x0 >= LA.x1 - PW / 3 && LA.y0 < LB.y1 && LB.y0 < LA.y1) {
      const xa = LA.xs[LA.xs.length - 1], xb = LB.xs[0];
      if (xb - xa >= 0.5 * PW) seams.push({ A, B, axis: 'x', xa, xb });
    }
    if (LB.y0 >= LA.y1 - PH / 3 && LA.x0 < LB.x1 && LB.x0 < LA.x1) {
      const ya = LA.ys[LA.ys.length - 1], yb = LB.ys[0];
      if (yb - ya >= 0.5 * PH) seams.push({ A, B, axis: 'y', ya, yb });
    }
  }
  const carry = (T, LT, axis, at, v, A, B, lo, hi) => {
    // T's edge column at x=at (axis x) gets a site at row v, if it has none.
    // Only within the span of T's own rows, fading out over a quarter pitch
    // beyond the last: a mirror that stuck out past the last row would face
    // the tile across T's other seam and dent it by up to half a pitch.
    const sets = axis === 'x' ? LT.colRows.get(at) : LT.rowCols.get(at);
    // a row within a twelfth of a pitch of one already there is the same
    // row: the seam steps by half that at most, and the diagram stays small
    for (const have of sets) if (Math.abs(have - v) < (axis === 'x' ? PH : PW) / 12) return false;
    if (occluded(A, B, lo, hi, axis, v)) return false;
    const own = axis === 'x' ? LT.ys : LT.xs, pitch = axis === 'x' ? PH : PW, cross = axis === 'x' ? PW : PH;
    const e = Math.max(0, own[0] - v, v - own[own.length - 1]);
    if (e >= pitch / 4) return false;
    const off = Math.pow(4 * e * cross / pitch, 2);
    sets.add(v);
    LT.mirrorOff.set(sets, (LT.mirrorOff.get(sets) || new Map()).set(v, off));
    const lines = axis === 'x' ? LT.colsOf.get(sets) : LT.rowsOf.get(sets);
    for (const line of lines) T.subs.push({ body: T, x: axis === 'x' ? line : v, y: axis === 'x' ? v : line, w: T.subs[0].w, off, claim: T.subs[0].claim, live: true, mirror: true });
    return true;
  };
  for (let pass = 0; pass < 6; pass++) {
    let changed = false;
    for (const sm of seams) {
      const LA = sm.A.tesLat, LB = sm.B.tesLat;
      if (sm.axis === 'x') {
        const ra = LA.colRows.get(sm.xa), rb = LB.colRows.get(sm.xb);
        for (const v of Array.from(rb)) if (carry(sm.A, LA, 'x', sm.xa, v, sm.A, sm.B, LA.x1, LB.x0)) changed = true;
        for (const v of Array.from(ra)) if (carry(sm.B, LB, 'x', sm.xb, v, sm.A, sm.B, LA.x1, LB.x0)) changed = true;
      } else {
        const ca = LA.rowCols.get(sm.ya), cb = LB.rowCols.get(sm.yb);
        for (const v of Array.from(cb)) if (carry(sm.A, LA, 'y', sm.ya, v, sm.A, sm.B, LA.y1, LB.y0)) changed = true;
        for (const v of Array.from(ca)) if (carry(sm.B, LB, 'y', sm.yb, v, sm.A, sm.B, LA.y1, LB.y0)) changed = true;
      }
    }
    if (!changed) break;
  }
  // 5. WHITESPACE CONFORMS TO THE TILES STANDING IN IT. A void's own lattice
  // is dead within a pitch of any content tile, and around every such tile
  // the void carries a ring of sites one pitch outside the tile's own rows,
  // columns and corners: the tile's cell against whitespace is then exactly
  // its rectangle, dilated by its weight, never a zigzag. The ring fades
  // out across the void's own edge, and dies under any other tile. A
  // closing void's sites are dead where a void is opening over it.
  if (host) {
    const v = host, w = v.subs[0].w, claim = v.subs[0].claim;
    for (const T of content) {
      // the ring conforms to each edge as it is, mirrors included, carrying
      // the same penalty a fading mirror carries: a seam sits on the weight
      // difference, and a pair that fades together stays on the midline
      const L = T.tesLat, ring = [];
      const offOf = (set, key) => { const m = L.mirrorOff.get(set); return m && m.has(key) ? m.get(key) : 0; };
      const right = L.colRows.get(L.xs[L.xs.length - 1]), left = L.colRows.get(L.xs[0]);
      for (const r of right) ring.push([L.x1 + PW / 2, r, offOf(right, r)]);
      for (const r of left) ring.push([L.x0 - PW / 2, r, offOf(left, r)]);
      const bottom = L.rowCols.get(L.ys[L.ys.length - 1]), top = L.rowCols.get(L.ys[0]);
      for (const c of bottom) ring.push([c, L.y1 + PH / 2, offOf(bottom, c)]);
      for (const c of top) ring.push([c, L.y0 - PH / 2, offOf(top, c)]);
      ring.push([L.x1 + PW / 2, L.y1 + PH / 2, 0], [L.x0 - PW / 2, L.y1 + PH / 2, 0], [L.x1 + PW / 2, L.y0 - PH / 2, 0], [L.x0 - PW / 2, L.y0 - PH / 2, 0]);
      for (const [x, y, off] of ring) {
        if (x < -PW || x > this.W + PW || y < -PH || y > this.H + PH) continue;
        v.subs.push({ body: v, x, y, w, off, claim, live: true, ringOf: T });
      }
    }
    for (const s of v.subs) {
      let pen = 0;
      for (const c of content) {
        if (s.ringOf === c) continue;
        const L = c.tesLat;
        const out = Math.max(L.x0 - s.x, s.x - L.x1, L.y0 - s.y, s.y - L.y1);
        // a grid site: dead within a pitch, alive at a pitch and a half; a
        // ring site of another tile: dead inside, alive a quarter pitch out
        const lo = s.ringOf ? 0 : PW, hi = s.ringOf ? PW / 4 : 1.5 * PW;
        if (out < hi) { const u = out <= lo ? 1 : 1 - (out - lo) / (hi - lo); pen = Math.max(pen, 8 * PW * PW * u * u); }
      }
      s.off += pen;
    }
    // a site four pitches dead is dead against anything within two pitches
    // of it: it costs the diagram and buys nothing
    v.subs = v.subs.filter(s => s.off < 4 * PW * PW);
    // whitespace with nowhere to be stays out of the auction this frame
    if (!v.subs.length) v.subs.push({ body: v, x: this.W / 2, y: this.H / 2, w, off: 0, claim: 0, live: false });
  }
};

// A cell read by the field inside it: its real corners, not the seam's
// vertices, so a rectangle is a rectangle to the hive it holds.
const tesOldCellPoly = Hive.prototype.cellPoly;
Hive.prototype.cellPoly = function(b) {
  const poly = tesOldCellPoly.call(this, b);
  if (this.depth !== 0 || !poly || b.wall) return poly;
  const clean = simplifyLoop(poly, 0.05, 1e-4);
  return clean.length >= 3 ? clean : poly;
};

const tesOldSolve = Hive.prototype.solve;
Hive.prototype.solve = function() {
  if (this.depth !== 0) return tesOldSolve.call(this);
  const groups = this.bodies.filter(b => b.subs[0].claim >= ACTIVE_MIN);
  const seated = b => b.rect && b.formRect === b.rect && b.crystal === 1 && !b.leaving
    && (!b.journey || b.pin >= 1) && (!b.tesP || (b.tesP.x === 0 && b.tesP.y === 0));
  const allSeated = groups.length && groups.every(seated);
  const t0 = performance.now();
  let sol, subs;
  if (allSeated) {
    // the settled page: exact rectangles, and the slot lattice at equal
    // weights, which is the diagram of those rectangles exactly
    const key = [this.W, this.H, ...groups.flatMap(b => [b.id, ...b.rect])].join(',');
    if (this.tesRestKey === key && this.solved) { sol = this.solved; subs = this.solvedSubs; }
    else {
      subs = [];
      for (const b of groups) {
        const r = b.rect;
        for (let y = r[1]; y < r[3]; y++) for (let x = r[0]; x < r[2]; x++) subs.push({ body: b, x: (x + .5) * this.PW, y: (y + .5) * this.PH, w: 0, off: 0, claim: b.subs[0].claim, live: true });
      }
      const seeds = subs.map(s => [s.x, s.y]), weights = seeds.map(() => 0);
      sol = { weights, diagram: computeDiagram(seeds, weights, this.domainPts()), maxRelErr: 0, converged: true, iterations: 0, rest: true };
    }
    this.tesRestKey = key;
    this.walls = groups;
    for (const b of groups) { b.wall = [b.rect[0] * this.PW, b.rect[1] * this.PH, b.rect[2] * this.PW, b.rect[3] * this.PH]; b.tesW = 0; }
  } else {
    this.tesRestKey = null;
    subs = groups.flatMap(b => b.subs);
    // WHITESPACE IS ONE BIDDER. Every void's sites bid at one shared weight
    // for the sum of their claims: a tile's front against whitespace is then
    // the same front whichever void's site is across it, and a void closing
    // under a void opening hands its ground over without a seam moving.
    const content = groups.filter(b => !b.isVoid), voids = groups.filter(b => b.isVoid);
    const units = voids.length ? content.concat([voids]) : content;
    const indices = new Map();
    content.forEach((b, i) => indices.set(b, i));
    for (const v of voids) indices.set(v, content.length);
    const owners = subs.map(s => indices.get(s.body)), seeds = subs.map(s => [s.x, s.y]), offs = subs.map(s => s.off);
    const targets = content.map(b => b.subs[0].claim).concat(voids.length ? [voids.reduce((a, v) => a + v.subs[0].claim, 0)] : []);
    const w0 = content.map(b => b.tesW || 0).concat(voids.length ? [this.tesVoidW || 0] : []);
    sol = tesseraSolve(seeds, owners, offs, targets, w0, this.domainPts(), 16, this.tesLambda || 0);
    this.tesLambda = sol.lambda;
    content.forEach((b, i) => { b.tesW = sol.groupWeights[i]; });
    if (voids.length) { this.tesVoidW = sol.groupWeights[content.length]; for (const v of voids) v.tesW = this.tesVoidW; }
    subs.forEach((s, i) => { s.w = sol.weights[i]; });
  }
  this.solveMs = performance.now() - t0; this.lastIters = sol.iterations;
  this.solved = sol; this.solvedSubs = subs; this.ownerOf = subs.map(s => s.body.id);
  this.shadowOn = false; this.shadowAt = null; this.ground = null; this.exact = true;
  this.recordAreas();
};
