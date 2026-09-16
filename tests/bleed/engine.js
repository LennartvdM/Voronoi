/* ====================================================================== BLEED
 * A mark whose cells are RECTANGLES OR VORONOI CELLS, nothing between, and
 * whose page has a margin past the viewport that the layout may use.
 *
 * The reference already has the two shapes and the machinery for both: a
 * settled body is a WALL (its rectangle, cut out of the auction's ground),
 * a body in the auction is a POINT SITE (its cell a convex power cell, cut
 * by the walls where it meets them), and a body between is a HOLE, a rigid
 * convex shape cut out of the ground. Astra I and Tessera replaced the
 * holes with lattices of sites that blend toward the rectangle, and every
 * tooth, wedge and step the owner has seen since is a lattice meeting a
 * lattice. This mark keeps the reference's shapes and changes the POLICY:
 *
 *   - a settled tile asked to move travels as it is: a rigid rectangle,
 *     a hole in the ground at wherever it is this frame (Tessera's journey,
 *     no pre-melt), landing as a wall when its pin takes;
 *   - a tile a traveller pushes is a rigid rectangle displaced, and comes
 *     back on its own clock (Tessera's packing pass);
 *   - everything else keeps the reference's own clocks and shapes: a body
 *     leaving for the flock melts along the reference's convex blend, a
 *     body arriving from it locks along the same blend, a void fills and
 *     empties as a point site.
 */

const BL_RETURN_TAU = 0.22;   // s: a displaced footprint's return clock
const BL_PIN_POW = 4;         // the lock's grip on a displacement: kept as (1 - pin^POW), so a low power pulls a shoved tile home early and a high one holds it to the last frames
const BL_PUSH_MAX = 0;        // px, 0 = no cap: the furthest the packing may hold a tile from where it is going, as a share of its own half-size
const BL_PACK_ITERS = 2;      // packing sweeps per motion step
const BL_PACK_TAU = 0.06;     // s: an overlap is taken out on this clock, not in one frame
const BL_SNAP = 0.02;         // px: a displacement below this is none
const BL_TRAVEL_COMP = 0.1;   // a traveller yields this much against a yielder's 1
const BL_DEPART_PUSH = 40;    // px: a waiter shoved this far off its slot departs now
const BL_MARGIN = 1;          // lattice cells of page past the viewport on every side: the bleed
const BL_RESERVE_MIN = 0.25;  // slots: a margin cell freer than this bids for its free area; below it, its neighbours take it
const BL_RESERVE_PITCH = 3;   // margin cells per reserve site along an edge: whitespace needs no fine lattice, and every site is a bidder the auction pays for
const BL_ITERS = 20;          // Newton iterations the root may take in a frame: the reserve's cells change claims as tiles cross the margin, and ten left frames a tenth off
const BL_ROUTE = 1;           // a traveller's curve bows around the tiles that stay, out to the margin if that is where the room is
const BL_LEAD = 0;            // s: the packing reads a traveller's footprint this far ahead (0.05 s measured: two more teleports, twenty more notched frames; off)
const BL_YIELD = 1;           // a waiter in a traveller's way yields the whole overlap the frame it appears, not on the packing's clock
const BL_EXTEND = 0.5;        // lattice cells: a scene rectangle on the lattice's edge runs this far into the bleed, so the page's ink runs off the crop
const BL_FILL = 1;            // the flock fills the page: its rest sizes are scaled to the whole page, not the window (0: the flock keeps to the window and the reserve holds the ring)

// The rigid footprint this body shows this frame, in px: null unless the
// body is a tile (crystal 1, seated or travelling rigid). A tile changing
// size on the way holds exactly its claim's area at every instant.
Hive.prototype.blFootprint = function(b) {
  if (b.isSelf || b.isVoid || b.leaving || !b.rect) return null;
  const PW = this.PW, PH = this.PH, j = b.journey, r = b.rect;
  let hw = (r[2] - r[0]) * PW / 2, hh = (r[3] - r[1]) * PH / 2;
  if (j && j.stamp && b.sizeFrom) {
    const e = b.progress;
    hw = b.sizeFrom[0] * PW * (1 - e) + hw * e;
    hh = b.sizeFrom[1] * PH * (1 - e) + hh * e;
    const k = Math.sqrt(Math.max(1e-9, b.claim * PW * PH) / (4 * hw * hh));
    hw *= k; hh *= k;
  }
  // a stamp journey lingers on a landed tile: it is in flight until its pin
  const travelling = !!(j && j.stamp) && !(b.pin >= 1);
  if (!travelling && b.crystal < 1) return null;
  return { hw, hh, rect: r, travelling };
};

// Where the rigid footprint stands: a traveller at its body, a seated tile
// on its slot, both plus the packing's displacement as long as the pin
// has not taken it back.
Hive.prototype.blPlace = function(b, fp) {
  const pk = blPinKeep(b), p = b.tesP || { x: 0, y: 0 };
  let x, y;
  if (fp.travelling) { x = b.x; y = b.y; }
  else { const c = this.rectCenter(b.rect); x = c[0]; y = c[1]; }
  return { x: x + p.x * pk, y: y + p.y * pk, hw: fp.hw, hh: fp.hh };
};

// A settled tile asked to go somewhere departs as it is: rigid, no melt.
const blOldSeat = Hive.prototype.seatBody;
Hive.prototype.seatBody = function(b, rect, T = 0, timing) {
  if (this.depth !== 0) return blOldSeat.call(this, b, rect, T, timing);
  // a tile, seated or in flight: a rigid tile re-seated mid-way (a change
  // interrupted by the next) turns toward its new slot as it is, from where
  // it is, at the size it has — never through the reference's melt
  const fp = this.blFootprint(b), had = b.journey;
  const tile = !!fp;
  blOldSeat.call(this, b, rect, T, timing);
  if (b.journey === had || !b.journey) return;
  if (!tile) return;
  b.journey.hold = 0;
  b.journey.stamp = true;
  b.journey.c0 = 1;
  b.sizeFrom = [fp.hw / this.PW, fp.hh / this.PH];
  b.formRect = b.rect;
};

// A tile stays a tile: crystal 1 the whole way; the lock is only the pin.
const blOldCrystal = Hive.prototype.updateCrystal;
Hive.prototype.updateCrystal = function(b, t) {
  const j = b.journey;
  if (this.depth !== 0 || !j || !j.stamp || (b.table && b.table.mode === 'open')) return blOldCrystal.call(this, b, t);
  const s = t - j.t0 - j.delay;
  if (s < 0) return;
  const L = b.rect && !b.leaving ? S3((s - j.dur + 0.35) / 0.50) : 0;
  b.crystal = 1;
  b.pin = L;
};

function blPinKeep(b) { return 1 - Math.pow(b.pin || 0, BL_PIN_POW); }

Hive.prototype.blCompliance = function(b) {
  const pk = blPinKeep(b);
  if (pk < 1e-3) return 0;
  const j = b.journey;
  const travelling = j && j.stamp && b.progress > 0 && b.progress < 1;
  return pk * (travelling ? BL_TRAVEL_COMP : 1);
};

// A tile is not liquid: it meets its neighbours through the packing of
// footprints, not by shoving seeds.
const blOldSeparate = Hive.prototype.separate;
Hive.prototype.separate = function(dt) {
  if (this.depth !== 0) return blOldSeparate.call(this, dt);
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
        const f = F * (1 - Math.min(A.crystal, B.crystal)) * (1 - d / R) * dt / dn;
        A.vx -= dx * f * m[i]; A.vy -= dy * f * m[i];
        B.vx += dx * f * m[j]; B.vy += dy * f * m[j];
      }
    }
  }
};

// THE PACKING (Tessera's): rigid footprints do not lie on each other. Each
// sweep takes out a share of every overlap along the cheaper axis; a
// traveller has the right of way; a body shoved a third of a pitch off its
// slot while waiting departs now; the domain's edges are walls.
Hive.prototype.blPack = function(h) {
  if (!this.blContacts) this.blContacts = new Map();
  const contacts = this.blContacts;
  const decay = Math.exp(-h / BL_RETURN_TAU);
  const items = [];
  const box = this.domainPts();
  const X0 = box[0][0], Y0 = box[0][1], X1 = box[2][0], Y1 = box[2][1];
  for (const b of this.bodies) {
    if (!b.tesP) b.tesP = { x: 0, y: 0 };
    const p = b.tesP;
    const fp = this.blFootprint(b);
    if (!fp) { p.x = 0; p.y = 0; continue; }
    p.x *= decay; p.y *= decay;
    if (Math.abs(p.x) < BL_SNAP) p.x = 0;
    if (Math.abs(p.y) < BL_SNAP) p.y = 0;
    const comp = this.blCompliance(b), pk = blPinKeep(b);
    const at = this.blPlace(b, fp);
    const wx = at.x - p.x * pk, wy = at.y - p.y * pk;
    const lx = fp.travelling ? b.vx * BL_LEAD : 0, ly = fp.travelling ? b.vy * BL_LEAD : 0;
    // in motion: on its curve, between departure and landing (a waiter with
    // a journey pending, and a tile that has landed, are not)
    const jn = b.journey, moving = !!(jn && jn.stamp && b.progress > 0 && b.progress < 1);
    items.push({ b, hw: fp.hw, hh: fp.hh, x: at.x, y: at.y, comp, pk, wx, wy, x0: at.x, y0: at.y, lx, ly, tr: moving });
  }
  const live = new Set();
  const relax = 1 - Math.exp(-h / BL_PACK_TAU);
  for (let it = 0; it < BL_PACK_ITERS; it++) {
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
        let share = A.comp / (A.comp + B.comp), r = relax;
        // A WAITER YIELDS RIGIDLY: a tile that can move, in a traveller's
        // way, takes the whole overlap out the frame it appears, so the
        // picture never holds a traveller lying across a seated tile for
        // the packing's clock to clear; two travellers, or a traveller
        // against what cannot move, part on the clock as before
        if (BL_YIELD && A.tr !== B.tr && (A.tr ? B : A).comp >= 1) { share = A.tr ? 0 : 1; r = 1; }
        const against = (it, ax, ay, pen) => ((it.wx - it.x) * ax + (it.wy - it.y) * ay) < -(0.5 * pen + 1) ? 1 : 0;
        const cx = ox * (1 + 3 * (share * against(A, -sx, 0, ox) + (1 - share) * against(B, sx, 0, ox)));
        const cy = oy * (1 + 3 * (share * against(A, 0, -sy, oy) + (1 - share) * against(B, 0, sy, oy)));
        let axis = cx <= cy ? 'x' : 'y';
        const prev = contacts.get(key);
        if (prev && ((prev.axis === 'x' && cx <= 2 * cy) || (prev.axis === 'y' && cy <= 2 * cx))) axis = prev.axis;
        contacts.set(key, { axis });
        if (axis === 'x') { A.x -= sx * ox * share * r; B.x += sx * ox * (1 - share) * r; }
        else { A.y -= sy * oy * share * r; B.y += sy * oy * (1 - share) * r; }
        moved = true;
      }
    }
    for (const it of items) {
      if (it.comp <= 0) continue;
      const x0 = it.x - it.hw, x1 = it.x + it.hw, y0 = it.y - it.hh, y1 = it.y + it.hh;
      if (x0 < X0 && x1 <= X1) { it.x += X0 - x0; moved = true; } else if (x1 > X1 && x0 >= X0) { it.x -= x1 - X1; moved = true; }
      if (y0 < Y0 && y1 <= Y1) { it.y += Y0 - y0; moved = true; } else if (y1 > Y1 && y0 >= Y0) { it.y -= y1 - Y1; moved = true; }
    }
    if (!moved) break;
  }
  for (const key of Array.from(contacts.keys())) if (!live.has(key)) contacts.delete(key);
  for (const it of items) {
    if (it.pk < 1e-3) continue;
    it.b.tesP.x = (it.x - it.wx) / it.pk;
    it.b.tesP.y = (it.y - it.wy) / it.pk;
    // and no further from its slot than a share of its own size: a tile held
    // a hundred pixels off its slot is a tile that has to travel back
    if (BL_PUSH_MAX) {
      const mx = BL_PUSH_MAX * it.hw, my = BL_PUSH_MAX * it.hh;
      it.b.tesP.x = Math.max(-mx, Math.min(mx, it.b.tesP.x));
      it.b.tesP.y = Math.max(-my, Math.min(my, it.b.tesP.y));
    }
    const j = it.b.journey;
    if (j && j.stamp && this.t < j.t0 + j.delay && Math.hypot(it.b.tesP.x, it.b.tesP.y) > BL_DEPART_PUSH) j.delay = Math.max(0, this.t - j.t0);
  }
};

// The seeds' clamp: the page less the seed margin. A site may stand in the
// bleed; the reference's own text is patched to read this box.
Hive.prototype.blClampBox = function() {
  if (this.depth !== 0 || this.domainPolyActive()) return [SEED_MARGIN, SEED_MARGIN, this.W - SEED_MARGIN, this.H - SEED_MARGIN];
  const [x0, y0, x1, y1] = this.blBox();
  return [x0 + SEED_MARGIN, y0 + SEED_MARGIN, x1 - SEED_MARGIN, y1 - SEED_MARGIN];
};

// A SITE UNDER A TILE OR IN A HOLE GOES TO THE NEAREST FREE GROUND. The reference steps
// a seed out of a hole by half a pixel through its nearest side; between
// two tiles that share that side it is stepped into the other and back,
// every frame, and owns nothing (a scene of thirty over twelve tiles that
// cover the window left nineteen newcomers on the seams). Here the step is
// to the nearest point of the ground the auction will actually sell — the
// page less the walls and the holes — half a pixel inside it; when the
// window is full that ground is the bleed, and the newcomer's cell opens
// there and comes in as the tiles part.
Hive.prototype.blEvict = function(h) {
  if (this.depth !== 0) return;
  const damp = Math.pow(0.5, (h || 1 / 60) * 60);
  const walls = this.walls, holes = this.holes;
  const inRect = (x, y, r) => x > r[0] && x < r[2] && y > r[1] && y < r[3];
  // under a tile, or in a blended hole: the reference's holes are cut here
  // by the tiles' planes into dozens of pieces, and its half-pixel step out
  // of one piece is a step into the next
  const under = (b, q) => q !== b && (q.blRigid ? inRect(b.x, b.y, q.hole.rect) : q.hole.pieces.some(pc => pointInPolygon(b.x, b.y, pc)));
  const [CX0, CY0, CX1, CY1] = this.blClampBox();
  // two newcomers under one tile are not stepped to one point: a site keeps
  // two pixels from every other, or takes the next spot along the side
  const others = this.bodies.filter(q => !q.isSelf && !q.blIsReserve);
  let ground = null;
  for (const b of this.bodies) {
    if (b.isSelf || b.wall || b.hole || b.blIsReserve) continue;
    if (!holes.some(q => under(b, q)) && !walls.some(w => inRect(b.x, b.y, w.wall))) continue;
    if (!ground) ground = (this.domainPieces() || []).filter(p => p.length >= 3 && Math.abs(ringArea(p)) > 1);
    let best = null, bd = Infinity;
    const consider = (x, y) => {
      x = Math.min(CX1, Math.max(CX0, x)); y = Math.min(CY1, Math.max(CY0, y));
      const d = (x - b.x) * (x - b.x) + (y - b.y) * (y - b.y);
      if (d >= bd) return;
      for (const o of others) if (o !== b && (o.x - x) * (o.x - x) + (o.y - y) * (o.y - y) < 4) return;
      for (const p of ground) if (pointInPolygon(x, y, p)) { bd = d; best = [x, y]; return; }
    };
    for (const p of ground) {
      const o = ringArea(p) > 0 ? 1 : -1, n = p.length;
      let cx = 0, cy = 0; for (const q of p) { cx += q[0]; cy += q[1]; }
      consider(cx / n, cy / n);
      for (let k = 0; k < n; k++) {
        const P = p[k], Q = p[(k + 1) % n], dx = Q[0] - P[0], dy = Q[1] - P[1], L2 = dx * dx + dy * dy;
        if (L2 < 1e-12) continue;
        const L = Math.sqrt(L2), t0 = ((b.x - P[0]) * dx + (b.y - P[1]) * dy) / L2;
        // half a pixel in from the side, on the inward normal (the reverse of
        // convexPlanes' outward one), at the foot of the site and at the next spots along
        for (const off of [0, 3, -3, 6, -6, 12, -12]) {
          const t = Math.max(0, Math.min(1, t0 + off / L));
          consider(P[0] + t * dx - o * dy / L * 0.5, P[1] + t * dy + o * dx / L * 0.5);
        }
      }
    }
    if (best) { b.x = best[0]; b.y = best[1]; b.vx *= damp; b.vy *= damp; }
  }
};

const blOldPre = Hive.prototype.enforcePreconditions;
Hive.prototype.enforcePreconditions = function(h) {
  blOldPre.call(this, h);
  if (this.depth === 0) { this.blEvict(h); this.blPack(h || 1 / 60); }
};

const blOldSize = Hive.prototype.setSize;
Hive.prototype.setSize = function(W, H) {
  const oldW = this.W, oldH = this.H;
  blOldSize.call(this, W, H);
  if (this.depth === 0 && oldW > 0 && this.bodies.length) {
    const kx = W / oldW, ky = H / oldH;
    for (const b of this.bodies) if (b.tesP) { b.tesP.x *= kx; b.tesP.y *= ky; }
  }
};

// THE WALLS AND HOLES OF THIS FRAME. The reference's own rule, plus one:
// a tile whose rigid footprint is not on its slot this frame (travelling,
// or displaced by the packing) is a HOLE at that footprint, a rectangle,
// never a wall at the slot and never a bidder. It joins the reference's
// holes before the overlap pass, ranked by how settled it is, so where two
// rigid shapes still overlap by the few px the packing leaves, the more
// settled keeps its shape and the other loses exactly the overlap.
const blOldWalls = Hive.prototype.computeWalls;
Hive.prototype.computeWalls = function() {
  if (this.depth !== 0) return blOldWalls.call(this);
  // every tile's rigid rectangle this frame, and whether it is on its slot
  const tiles = [];
  for (const b of this.bodies) {
    b.blRigid = false;
    const PW = this.PW, PH = this.PH;
    if (b.isVoid && !b.blIsReserve && b.rect && !b.leaving && b.crystal >= 1) {
      // whitespace at rest is a wall to the reference; to a tile crossing
      // it, it is room: it yields the overlap, and nobody sees the notch
      const r = b.rect, rect = [r[0] * PW, r[1] * PH, r[2] * PW, r[3] * PH];
      tiles.push({ b, rect, onSlot: true, landed: true, fp: null, isVoid: true });
      continue;
    }
    const fp = this.blFootprint(b);
    if (!fp) continue;
    const at = this.blPlace(b, fp);
    const r = b.rect;
    const slot = [r[0] * PW, r[1] * PH, r[2] * PW, r[3] * PH];
    const rect = [at.x - at.hw, at.y - at.hh, at.x + at.hw, at.y + at.hh];
    const onSlot = rect.every((v, i) => Math.abs(v - slot[i]) < 1e-6);
    const landed = !fp.travelling || b.pin >= 1;
    tiles.push({ b, rect, onSlot, landed, fp });
  }
  // a tile on its slot with nothing across it is a wall (the reference's
  // rule); a tile off its slot, or one another tile lies across, is a HOLE
  // at its rectangle this frame
  const rigid = new Map();
  for (let i = 0; i < tiles.length; i++) {
    const t = tiles[i];
    let crossed = false;
    for (let j = 0; j < tiles.length && !crossed; j++) {
      if (j === i) continue;
      const u = tiles[j];
      if (u.rect[0] < t.rect[2] - 1e-6 && u.rect[2] > t.rect[0] + 1e-6 && u.rect[1] < t.rect[3] - 1e-6 && u.rect[3] > t.rect[1] + 1e-6) crossed = true;
    }
    if (t.onSlot && t.landed && t.b.crystal >= 1 && !crossed) continue;   // the reference makes it a wall (a void too)
    if (t.isVoid && !crossed) continue;
    rigid.set(t.b, t);
  }
  if (!rigid.size) return blOldWalls.call(this);
  // keep the reference from making these walls at their slots: it reads
  // crystal and formRect; hand it crystal 0 and no formRect for the pass
  const saved = [];
  for (const [b] of rigid) { saved.push([b, b.crystal, b.formRect, b.holeLinger]); b.crystal = 0; b.formRect = null; b.holeLinger = false; }
  blOldWalls.call(this);
  for (const [b, c, f, hl] of saved) { b.crystal = c; b.formRect = f; b.holeLinger = hl; }
  // WHO KEEPS ITS SHAPE where two rigid rectangles still overlap by the few
  // px the packing leaves: the one that does not yield in the packing. A
  // landed tile is immovable; a traveller has the right of way; a seated
  // tile displaced, or crossed, moves aside. So the overlap is cut from
  // the one that is moving aside anyway, and the notch lasts as long as
  // the packing takes to clear it.
  const rank = t => t.isVoid ? -1 : (t.landed && t.onSlot ? 3 : (t.fp.travelling ? 2 + (t.b.progress || 0) : 1 - this.blCompliance(t.b)));
  const list = Array.from(rigid.values()).sort((a, b) => rank(b) - rank(a));
  const unit = (hp) => hp.filter(h => Math.hypot(h.ax, h.ay) > 1e-9).map(h => { const L = Math.hypot(h.ax, h.ay); return { ax: h.ax / L, ay: h.ay / L, b: h.b / L }; });
  const placed = this.walls.map(w => { const r = w.wall; return [[{ ax: -1, ay: 0, b: -r[0] }, { ax: 1, ay: 0, b: r[2] }, { ax: 0, ay: -1, b: -r[1] }, { ax: 0, ay: 1, b: r[3] }]]; });
  const rigidPlanes = [];
  for (const t of list) {
    const b = t.b, rect = t.rect;
    const corners = [[rect[0], rect[1]], [rect[2], rect[1]], [rect[2], rect[3]], [rect[0], rect[3]]];
    let pieces = [corners];
    for (const other of placed) {
      for (const op of other) {
        const next = [];
        for (const p of pieces) next.push(...subtractPlanes(p, op));
        pieces = next;
      }
      if (!pieces.length) break;
    }
    pieces = pieces.filter(p => p.length >= 3 && Math.abs(ringArea(p)) > 1e-3);
    // a tile another has entirely covered keeps its rectangle rather than
    // vanish into the auction for a frame; the packing is already parting them
    if (!pieces.length) pieces = [corners];
    let big = pieces[0], bigA = 0;
    for (const p of pieces) { const a = Math.abs(ringArea(p)); if (a > bigA) { bigA = a; big = p; } }
    b.wall = null;
    b.hole = { pieces, planes: pieces.map(p => unit(convexPlanes(p))), rect, pts: big, raw: [corners] };
    b.holeCore = { core: corners, arms: [] };
    b.holeExtra = [];
    b.blRigid = true;
    this.holes.push(b); placed.push(b.hole.planes); rigidPlanes.push(b.hole.planes);
  }
  // the reference's own holes (a body melting or locking) are less settled
  // than any rigid tile: where one lies across a rigid footprint it loses
  // exactly the overlap, and where nothing is left it is gone
  if (rigidPlanes.length) {
    const kept = [];
    for (const h of this.holes) {
      if (h.blRigid) { kept.push(h); continue; }
      let pieces = h.hole.pieces;
      for (const planes of rigidPlanes) {
        for (const op of planes) { const next = []; for (const p of pieces) next.push(...subtractPlanes(p, op)); pieces = next; }
        if (!pieces.length) break;
      }
      pieces = pieces.filter(p => p.length >= 3 && Math.abs(ringArea(p)) > 1e-3);
      if (!pieces.length) { h.hole = null; h.holeCore = null; continue; }
      let big = pieces[0], bigA = 0;
      for (const p of pieces) { const a = Math.abs(ringArea(p)); if (a > bigA) { bigA = a; big = p; } }
      h.hole = { pieces, planes: pieces.map(p => unit(convexPlanes(p))), rect: h.hole.rect, pts: big, raw: h.hole.raw };
      kept.push(h);
    }
    this.holes = kept;
  }
  this.holes.sort((a, b) => b.crystal - a.crystal);
};

/* ------------------------------------------------------------- THE BLEED
 * The page is wider than the window. The tessellation's domain is the
 * viewport plus BL_MARGIN lattice cells on every side, and the canvas is
 * a window onto it: a cell that crosses the window's edge is drawn cut by
 * the edge, not bordered along it. Whitespace outside the window is the
 * RESERVE, one point site per margin cell, each bidding for exactly the
 * free area of its cell (its cell less any wall or rigid tile standing in
 * it), so nothing on the page is inflated by the margin and a tile pushed
 * into the margin displaces exactly the reserve it stands on. The reserve
 * is always in the auction, so ground nobody bids for is never adopted by
 * a hole: what no card claims, whitespace does.
 */
Hive.prototype.blBox = function() {
  const mx = BL_MARGIN * this.PW, my = BL_MARGIN * this.PH;
  return [-mx, -my, this.W + mx, this.H + my];
};

const blOldDomainPts = Hive.prototype.domainPts;
Hive.prototype.domainPts = function() {
  if (this.depth !== 0 || this.domainPolyActive()) return blOldDomainPts.call(this);
  const [x0, y0, x1, y1] = this.blBox();
  return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
};

const blOldPieces = Hive.prototype.domainPieces;
Hive.prototype.domainPieces = function(withHoles) {
  if (this.depth !== 0 || this.domainPolyActive()) return blOldPieces.call(this, withHoles);
  const [x0, y0, x1, y1] = this.blBox();
  // a rigid tile is a rectangle: it goes into the sweep with the walls,
  // which leaves the ground in a few pieces, where cutting it out plane by
  // plane left it in a hundred (and the auction's cost with it)
  const rects = this.walls.map(b => b.wall);
  for (const b of this.holes) if (b.blRigid) rects.push(b.hole.rect);   // to the shadow too: a rigid tile never gives its ground back
  const morphs = withHoles ? [] : this.holes.filter(b => !b.blRigid).flatMap(b => b.hole.raw.map(p => convexPlanes(p)));
  let pieces = rects.length ? blMergeRects(coverRects(x0, y0, x1, y1, rects)) : [[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]];
  for (const planes of morphs) {
    const next = [];
    for (const p of pieces) next.push(...subtractPlanes(p, planes));
    pieces = next;
  }
  return pieces;
};

// The sweep leaves the ground as strips, one per column between two
// tiles' edges; every auction then clips every cell to every strip. Two
// strips that share a side and an extent are one rectangle: merged
// across, then down, the same ground is a fifth as many pieces.
function blMergeRects(pieces) {
  const rects = [], other = [];
  for (const p of pieces) {
    if (p.length === 4 && p.every((q, i) => { const r = p[(i + 1) % 4]; return Math.abs(q[0] - r[0]) < 1e-9 || Math.abs(q[1] - r[1]) < 1e-9; })) {
      const xs = p.map(q => q[0]), ys = p.map(q => q[1]);
      rects.push([Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]);
    } else other.push(p);
  }
  const same = (a, b) => Math.abs(a - b) < 1e-7;
  const mergeAlong = (list, ax) => {
    // ax 0: merge rects with the same y-extent that touch in x; ax 1: the reverse
    const lo = ax, hi = ax + 2, olo = 1 - ax, ohi = 3 - ax;
    list.sort((a, b) => (a[olo] - b[olo]) || (a[ohi] - b[ohi]) || (a[lo] - b[lo]));
    const out = [];
    for (const r of list) {
      const last = out[out.length - 1];
      if (last && same(last[olo], r[olo]) && same(last[ohi], r[ohi]) && same(last[hi], r[lo])) last[hi] = r[hi];
      else out.push(r.slice());
    }
    return out;
  };
  let list = rects;
  for (let pass = 0; pass < 2; pass++) { list = mergeAlong(list, 0); list = mergeAlong(list, 1); }
  return list.map(r => [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]]).concat(other);
}

// The page in slots: the window's lattice plus the bleed's ring. The
// reference's flock scales its rest sizes to COLS*ROWS — the window — and
// the reference's line is patched to ask for this instead, so a released
// page fills the PAGE and every edge cell is cut by the crop.
Hive.prototype.blSlots = function() {
  if (this.depth !== 0) return this.COLS * this.ROWS;
  return (this.COLS + 2 * BL_MARGIN) * (this.ROWS + 2 * BL_MARGIN);
};

// THE PAGE'S INK RUNS OFF THE CROP. A scene rectangle on the lattice's
// edge is extended half a margin cell into the bleed (content and void
// alike), so a settled page bleeds on all four sides: the outer gutter
// and the rounded corner are off-screen, and the crop cuts the ink. The
// reserve owns the outer half of the ring. (The reference's enterScene is
// patched to pass every scene specification through here.)
Hive.prototype.blSpec = function(spec) {
  if (!spec || this.depth !== 0 || !BL_EXTEND) return spec;
  const C = this.COLS, R = this.ROWS, e = BL_EXTEND * BL_MARGIN;
  const ext = r => { const q = r.slice(); if (q[0] === 0) q[0] = -e; if (q[1] === 0) q[1] = -e; if (q[2] === C) q[2] = C + e; if (q[3] === R) q[3] = R + e; return q; };
  const out = Object.assign({}, spec);
  if (spec.content) out.content = spec.content.map(ext);
  if (spec.voids) out.voids = spec.voids.map(ext);
  return out;
};

// HOVER ON A TILE IS A LIFT, NOT A BULGE. The reference grows a hovered
// wall a ring cut out of its neighbours, and lets a hovered member burst
// past its field into the page's cells: both break the rule at the root
// (a rectangle with a bulge, a neighbour with a bite). Here the root keeps
// no shards: a hovered tile lifts into its own gutter and glows, as the
// garment already draws it; inside a field the members' cells still grow
// against each other, Voronoi cells growing, within the field's rectangle.
const blOldShards = Hive.prototype.computeShards;
Hive.prototype.computeShards = function() {
  if (this.depth !== 0) return blOldShards.call(this);
  this.shards = [];
};

// The reserve: a void body that is never seated, never retired, never a
// source or a node of a change; its sites are the margin's lattice.
Hive.prototype.blReserve = function() {
  let r = this.bodies.find(b => b.blIsReserve);
  if (r) return r;
  const id = this.nextId;
  r = this.makeBody(this.W / 2, this.H / 2, { isVoid: true, claim: 0 });
  this.nextId = id; r.id = -1; r.name = 'reserve';
  r.blIsReserve = true; r.claim = 0; r.baseClaim = 0; r.claimTarget = 0; r.claim0 = 0;
  r.subs = [];
  this.bodies.push(r);
  return r;
};

const blOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  blOldPlace.call(this);
  if (this.depth !== 0) return;
  const r = this.blReserve();
  const PW = this.PW, PH = this.PH, C = this.COLS, R = this.ROWS, k = BL_MARGIN;
  const key = [this.W, this.H, C, R, k].join(',');
  if (r.blKey !== key) {
    // THE MARGIN'S SITES. One per cell of the ring is one bidder per cell
    // for ground that is whitespace either way, and every bidder is a row of
    // the auction: the ring's cells are gathered into runs of BL_RESERVE_PITCH
    // along each side (a run is a rectangle, so a site still stands in the
    // middle of what it claims), and the corners keep a site of their own.
    r.blKey = key; r.subs = [];
    const P = Math.max(1, BL_RESERVE_PITCH | 0);
    const add = (x0, y0, x1, y1) => r.subs.push({ body: r, x: (x0 + x1) / 2, y: (y0 + y1) / 2, w: 0, claim: 0, live: false, cell: [x0, y0, x1, y1] });
    const runs = (from, to) => { const out = []; for (let a = from; a < to; a += P) out.push([a, Math.min(to, a + P)]); return out; };
    for (let row = -k; row < 0; row++) for (const [a, b] of runs(0, C)) add(a * PW, row * PH, b * PW, (row + 1) * PH);
    for (let row = R; row < R + k; row++) for (const [a, b] of runs(0, C)) add(a * PW, row * PH, b * PW, (row + 1) * PH);
    for (let col = -k; col < 0; col++) for (const [a, b] of runs(0, R)) add(col * PW, a * PH, (col + 1) * PW, b * PH);
    for (let col = C; col < C + k; col++) for (const [a, b] of runs(0, R)) add(col * PW, a * PH, (col + 1) * PW, b * PH);
    for (let row = -k; row < 0; row++) for (let col = -k; col < 0; col++) add(col * PW, row * PH, (col + 1) * PW, (row + 1) * PH);
    for (let row = -k; row < 0; row++) for (let col = C; col < C + k; col++) add(col * PW, row * PH, (col + 1) * PW, (row + 1) * PH);
    for (let row = R; row < R + k; row++) for (let col = -k; col < 0; col++) add(col * PW, row * PH, (col + 1) * PW, (row + 1) * PH);
    for (let row = R; row < R + k; row++) for (let col = C; col < C + k; col++) add(col * PW, row * PH, (col + 1) * PW, (row + 1) * PH);
  }
  // each margin site claims the free area of its cell, in slots
  // what stands in the margin: walls and rigid tiles as rectangles, the
  // reference's blended holes as their convex pieces
  // THE RESERVE TAKES WHAT IS LEFT. Not a timer and not a second ledger:
  // the page is worth blSlots(), everyone else has asked for what they have
  // asked for this frame, and the margin's sites share the remainder in
  // proportion to the free area each of them stands on. At rest in a scene
  // that remainder IS the free margin, so each site claims its own free
  // area, the local rule; released, the flock's rest sizes are scaled to
  // the page, the remainder falls to nothing, and the ring goes to the
  // content on the content's own clock — no easing of ours to wobble
  // against theirs, and the claims sum to the page every frame.
  let taken = 0;
  for (const b of this.bodies) if (!b.blIsReserve && !b.isSelf) taken += b.claim;
  const left = Math.max(0, this.blSlots() - taken);
  const rects = [], polys = [];
  for (const b of this.bodies) {
    if (b.wall) rects.push(b.wall);
    else if (b.hole) { if (b.blRigid) rects.push(b.hole.rect); else for (const p of b.hole.pieces) polys.push(p); }
  }
  let freeSum = 0;
  const inPoly = (x, y, poly) => { let inside = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const a = poly[i], b = poly[j]; if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) inside = !inside; } return inside; };
  for (const s of r.subs) {
    const c = s.cell;
    // (the reference's placeSeeds moves every body's first site to the body:
    // the reserve's sites stand on their lattice cells, always)
    s.x = (c[0] + c[2]) / 2; s.y = (c[1] + c[3]) / 2;
    let under = 0, covered = false;
    for (const q of rects) {
      const ox = Math.min(c[2], q[2]) - Math.max(c[0], q[0]), oy = Math.min(c[3], q[3]) - Math.max(c[1], q[1]);
      if (ox > 0 && oy > 0) under += ox * oy;
      if (s.x > q[0] && s.x < q[2] && s.y > q[1] && s.y < q[3]) covered = true;
    }
    for (const p of polys) if (inPoly(s.x, s.y, p)) { covered = true; break; }
    // a site standing under a tile owns nothing whatever it claims, and a
    // site whose cell a tile has all but covered would be asked for a sliver
    // it cannot find in five iterations (a tiny target beside its own dead
    // neighbours is an ill-conditioned row): both stand out of the auction
    // until the tile has passed, and the sliver is whitespace either way
    const free = Math.max(0, (c[2] - c[0]) * (c[3] - c[1]) - under) / (PW * PH);
    s.claim = covered || free < BL_RESERVE_MIN ? 0 : free;
    freeSum += s.claim;
  }
  // the remainder, shared out; never more than the site's own free area
  // (a tile standing in the margin covers sites and only the reserve shrinks)
  const share = freeSum > 1e-9 ? Math.min(1, left / freeSum) : 0;
  if (share < 1) for (const s of r.subs) s.claim *= share;
  // A MARGIN SITE ENTERS AT ITS NEIGHBOURS' WEIGHT. The reference brings a
  // newcomer in by bisection, fifty-odd auctions of one cell, and revives a
  // site whose cell came out empty the same way; a tile crossing the margin
  // cuts the ring into pockets whose weights drift apart, and a frame with
  // twelve tiles moving spent a hundred such bisections. A margin cell is a
  // lattice cell like the ones beside it: it enters, and comes back, at the
  // mean weight of its lattice neighbours that held a cell last frame.
  const qSlots = q => (q.cell[2] - q.cell[0]) * (q.cell[3] - q.cell[1]) / (PW * PH);
  const areaOf = new Map();
  if (this.solved && this.solvedSubs) this.solvedSubs.forEach((q, i) => { if (q.body === r) areaOf.set(q, this.solved.diagram.areas[i]); });
  const held = q => q.live && (areaOf.get(q) || 0) > 1;
  const byCell = new Map(r.subs.map(q => [Math.round(q.x) + ',' + Math.round(q.y), q]));
  for (const q of r.subs) {
    if (q.claim < ACTIVE_MIN) continue;
    if (held(q)) continue;
    // at the neighbour's weight, corrected for the claims: a lattice cell's
    // area moves about twice as fast as its weight (four sides a pitch long,
    // each bisector shifting by the weight difference over twice the pitch),
    // so a site claiming less than its neighbour enters that much lower
    let wSum = 0, wN = 0;
    const est = nb => nb.w + (q.claim / Math.max(1e-9, qSlots(q)) - nb.claim / Math.max(1e-9, qSlots(nb))) * PW * PH / 2;
    for (const nb of r.subs) {
      if (nb === q || !held(nb)) continue;
      // a neighbour is a site whose run touches this one: within a run's
      // span plus a cell, in both axes
      if (Math.abs(nb.x - q.x) > (q.cell[2] - q.cell[0]) / 2 + (nb.cell[2] - nb.cell[0]) / 2 + PW / 2) continue;
      if (Math.abs(nb.y - q.y) > (q.cell[3] - q.cell[1]) / 2 + (nb.cell[3] - nb.cell[1]) / 2 + PH / 2) continue;
      wSum += est(nb); wN++;
    }
    if (!wN) for (const nb of r.subs) if (held(nb)) { wSum += est(nb); wN++; }
    if (wN) { q.w = wSum / wN; q.live = true; }
  }
  r.x = this.W / 2; r.y = this.H / 2; r.vx = 0; r.vy = 0;
  r.crystal = 0; r.hoverMix = 0;
};

// The pockets are the SOLVE'S, not the frame's: a frame whose signature is
// unchanged keeps the auction it had, and must keep the ground that auction
// gave the reserve with it — cleared per frame, a cached frame painted the
// page without them, and the pocket read as a gap.
const blOldMain = Hive.prototype.solveMain;
Hive.prototype.solveMain = function() {
  if (this.depth !== 0) return blOldMain.call(this);
  const r = this.blReserve(), keep = r.blExtra || [], sig = this.lastSig;
  r.blExtra = [];
  const out = blOldMain.call(this);
  if (this.lastSig === sig && !r.blExtra.length) r.blExtra = keep;   // the solve was cached: so are its pockets
  return out;
};

// Ground nobody bids for — a pocket the tiles have closed around — is
// whitespace, not the nearest tile's: the reserve shows it, unpainted.
const blOldAdopt = Hive.prototype.adoptGround;
Hive.prototype.adoptGround = function(pieces) {
  if (this.depth !== 0) return blOldAdopt.call(this, pieces);
  const r = this.blReserve();
  if (!r.blExtra) r.blExtra = [];
  for (const p of pieces) if (p.length >= 3) r.blExtra.push({ pts: p, labs: p.map(() => WALL_TRI) });
};

// the reserve is not a void a scene can dissolve
const blOldRetire = Hive.prototype.retireBody;
Hive.prototype.retireBody = function(b, dur, T) {
  if (b.blIsReserve) return;
  return blOldRetire.call(this, b, dur, T);
};

// a scene is spoken to the page's bodies; the reserve is not one of them
const blOldEnter = Hive.prototype.enterScene;
Hive.prototype.enterScene = function(name, origin) {
  if (this.depth !== 0) return blOldEnter.call(this, name, origin);
  const r = this.bodies.find(b => b.blIsReserve);
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { const out = blOldEnter.call(this, name, origin); if (BL_ROUTE) this.blRoute(); return out; }
  finally { if (r) this.bodies.push(r); }
};

// THE ROUTE. A traveller's path is the reference's quadratic curve, bowed
// by the swirl. Where that curve carries a rigid tile across a tile that is
// staying where it is, the two would have to fit — one notched, the other
// shoved — for as long as the crossing lasts. So the bow is chosen at the
// change: of the curves through a fan of control points either side of the
// chord, the one whose swept footprint crosses the least of what stays,
// the page's margin counting as room. A curve that swings out past the
// window's edge and back is the sweep the owner asked for, and it is what
// the margin is for.
Hive.prototype.blRoute = function() {
  const t0 = this.t, PW = this.PW, PH = this.PH, [X0, Y0, X1, Y1] = this.blBox();
  const stays = [];
  for (const b of this.bodies) {
    if (b.isVoid || b.isSelf || b.leaving || !b.rect || b.crystal < 1) continue;
    if (b.journey && b.journey.t0 === t0 && b.journey.stamp) continue;   // moving this change
    const r = b.rect; stays.push([r[0] * PW, r[1] * PH, r[2] * PW, r[3] * PH]);
  }
  const movers = this.bodies.filter(b => b.journey && b.journey.stamp && b.journey.t0 === t0 && b.path)
    .map(b => { const r = b.rect, j = b.journey; return { b, p: b.path, hw: Math.max(b.sizeFrom ? b.sizeFrom[0] * PW : 0, (r[2] - r[0]) * PW / 2), hh: Math.max(b.sizeFrom ? b.sizeFrom[1] * PH : 0, (r[3] - r[1]) * PH / 2), start: j.t0 + j.delay + (j.hold || 0), dur: j.dur }; })
    .sort((a, b) => a.start - b.start);
  const ease = u => u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
  const at = (mv, tau) => { const u = Math.max(0, Math.min(1, (tau - mv.start) / mv.dur)), e = ease(u), m = 1 - e, p = mv.p; return [m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey]; };
  this.blRouted = 0;
  for (const mv of movers) {
    const b = mv.b, p = mv.p, hw = mv.hw, hh = mv.hh;
    const cost = (cx, cy) => {
      let sum = 0;
      for (let k = 1; k < 24; k++) {
        const t = k / 24, e = ease(t), m = 1 - e;
        const x = m * m * p.sx + 2 * m * e * cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * cy + e * e * p.ey;
        if (x - hw < X0 || x + hw > X1 || y - hh < Y0 || y + hh > Y1) return Infinity;   // off the page: not a route
        for (const q of stays) {
          const ox = Math.min(x + hw, q[2]) - Math.max(x - hw, q[0]), oy = Math.min(y + hh, q[3]) - Math.max(y - hh, q[1]);
          if (ox > 0 && oy > 0) sum += ox * oy;
        }
        // the other travellers, where each will be at this moment
        const tau = mv.start + t * mv.dur;
        for (const o of movers) {
          if (o === mv) continue;
          const [qx, qy] = at(o, tau);
          const ox = Math.min(x + hw, qx + o.hw) - Math.max(x - hw, qx - o.hw), oy = Math.min(y + hh, qy + o.hh) - Math.max(y - hh, qy - o.hh);
          if (ox > 0 && oy > 0) sum += 0.5 * ox * oy;
        }
      }
      return sum;
    };
    const base = cost(p.cx, p.cy);
    if (!(base > 0)) continue;
    const dx = p.ex - p.sx, dy = p.ey - p.sy, L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
    const mx = (p.sx + p.ex) / 2, my = (p.sy + p.ey) / 2;
    let best = base, bcx = p.cx, bcy = p.cy;
    for (const f of [0.35, 0.7, 1.05, 1.4, 1.75]) for (const sg of [1, -1]) {
      const cx = mx + nx * f * L * sg, cy = my + ny * f * L * sg;
      const c = cost(cx, cy);
      if (c < best - 1e-6) { best = c; bcx = cx; bcy = cy; }
    }
    if (bcx !== p.cx || bcy !== p.cy) this.blRouted++;
    p.cx = bcx; p.cy = bcy;
  }
};

// The shadow auction reads the cell a blended hole would have. A rigid tile
// never asks: it lands as a wall. With only rigid holes on the page the
// shadow is the main auction, as the reference says of a page with none.
const blOldShadow = Hive.prototype.solveShadow;
Hive.prototype.solveShadow = function() {
  if (this.depth !== 0 || !this.holes.length) return blOldShadow.call(this);
  if (this.holes.some(h => !h.blRigid)) {
    // a blended hole on the page: the shadow runs, with the rigid tiles as
    // walls to it (their ground cut out, see domainPieces) and not bidding
    const saved = [];
    for (const h of this.holes) if (h.blRigid) for (const q of h.subs) { saved.push([q, q.claim]); q.claim = 0; }
    // the margin's shadow is its main standing: the two grounds differ only
    // by the blended holes, and a shadow weight drifting on its own emptied
    // the whole ring every frame (twenty-six bisections a frame)
    const r = this.blReserve();
    for (const q of r.subs) { q.wShadow = q.w; q.shadowLive = q.live; }
    try { return blOldShadow.call(this); } finally { for (const [q, c] of saved) q.claim = c; }
  }
  // (a hole body keeps the shadow standing it had: cleared, it would enter
  // the next shadow by bisection, every frame a blended hole is on the page)
  for (const b of this.bodies) if (!b.hole) for (const s of b.subs) { s.wShadow = s.w; s.shadowLive = s.live; }
  this.shadowOn = false; this.shadowAt = null;
};

// The reserve is nobody's neighbour, occupant or source: a hit on its cell
// is a hit on whitespace (the reference's bodyGraph asks hitTestAny for what
// a body hangs off, and must never be handed the reserve)
const blOldHitAny = Hive.prototype.hitTestAny;
Hive.prototype.hitTestAny = function(x, y) {
  const b = blOldHitAny.call(this, x, y);
  return b && b.blIsReserve ? null : b;
};

// Newton's budget at the root: the reference allows three to eight
// iterations by the frame's length; a frame in which margin sites enter or
// leave (a tile crossing the margin's lattice) starts further from its
// answer than any frame the reference budgeted for, and five iterations
// left a whitespace cell at twice its target. Ten is enough; the cost is a
// few diagram evaluations on those frames only, since a converged auction
// stops early.
const blOldBudget = Hive.prototype.iterBudget;
Hive.prototype.iterBudget = function() {
  const n = blOldBudget.call(this);
  return this.depth === 0 ? Math.max(n, BL_ITERS) : n;
};

/* ------------------------------------------------------ PRESENTATION
 * The canvas is the window: a cell that crosses its edge is cut by the
 * edge, its ink continuing past it, no border drawn along the crop (the
 * True Buffer's mistake). Two things are added for the window's sake: a
 * label sits in the part of its cell that is on screen, and a MARGIN VIEW
 * (the button, or ?view=bleed) draws the same picture zoomed out to the
 * whole page, the window as the owner's green dashed content zone, the
 * bleed's edge orange, the reserve's cells faint — the very polygons the
 * auction produced, not a second animation.
 */
const blClipWindow = (pts) => {
  let q = pts;
  for (const [ax, ay, b] of [[-1, 0, 0], [1, 0, W], [0, -1, 0], [0, 1, H]]) { q = clipPts(q, ax, ay, b); if (!q || q.length < 3) return null; }
  return q;
};
const blOldContentStep = contentStep;
contentStep = function(c, pts, big, area, t, dt, bx, by) {
  const cb = blClipWindow(big), cp = cb && blClipWindow(pts);
  if (cb && cp) return blOldContentStep(c, cp, cb, Math.abs(ringArea(cb)), t, dt, bx, by);
  return blOldContentStep(c, pts, big, area, t, dt, bx, by);
};

let blView = new URLSearchParams(location.search).get('view') === 'bleed';
// the window-to-page map of the margin view: page px = (canvas px - o) / s
function blViewMap() {
  const [x0, y0, x1, y1] = root.blBox();
  const bw = x1 - x0, bh = y1 - y0, s = Math.min(W / bw, H / bh);
  return { s, ox: (W - bw * s) / 2 - x0 * s, oy: (H - bh * s) / 2 - y0 * s, x0, y0, bw, bh };
}
const blOldPaintPicture = paintPicture;
paintPicture = function(ctx, picture, hoveredPath, dt, t) {
  if (!blView) return blOldPaintPicture(ctx, picture, hoveredPath, dt, t);
  const m = blViewMap();
  ctx.save();
  ctx.setTransform(dpr * m.s, 0, 0, dpr * m.s, dpr * m.ox, dpr * m.oy);
  ctx.fillStyle = '#13141d'; ctx.fillRect(m.x0, m.y0, m.bw, m.bh);
  ctx.fillStyle = '#0a0a0f'; ctx.fillRect(0, 0, W, H);
  // the reserve's cells: whitespace the margin's sites hold, unpainted in the window
  ctx.fillStyle = '#1b1d2a'; ctx.strokeStyle = '#262838'; ctx.lineWidth = 1 / m.s;
  for (const leaf of picture.leaves) {
    if (!leaf.isVoid || !leaf.body || !leaf.body.blIsReserve) continue;
    for (const lp of leaf.loops) { if (lp.length < 3) continue; ctx.beginPath(); ctx.moveTo(lp[0][0], lp[0][1]); for (let k = 1; k < lp.length; k++) ctx.lineTo(lp[k][0], lp[k][1]); ctx.closePath(); ctx.fill(); ctx.stroke(); }
  }
  blOldPaintPicture(ctx, picture, hoveredPath, dt, t);
  ctx.setLineDash([8 / m.s, 5 / m.s]); ctx.strokeStyle = 'rgba(120, 220, 140, 0.9)'; ctx.lineWidth = 2 / m.s; ctx.strokeRect(0, 0, W, H);
  ctx.setLineDash([]); ctx.strokeStyle = 'rgba(255, 150, 50, 0.9)'; ctx.lineWidth = 3 / m.s; ctx.strokeRect(m.x0, m.y0, m.bw, m.bh);
  ctx.restore();
};
// hover in the margin view: the pointer's canvas px mapped back to the page
const blOldHitLeaves = hitLeaves;
hitLeaves = function(picture, x, y) {
  if (!blView) return blOldHitLeaves(picture, x, y);
  const m = blViewMap();
  return blOldHitLeaves(picture, (x - m.ox) / m.s, (y - m.oy) / m.s);
};
const blOldHitPath = Hive.prototype.hitPath;
Hive.prototype.hitPath = function(x, y) {
  if (this.depth !== 0 || !blView) return blOldHitPath.call(this, x, y);
  const m = blViewMap();
  return blOldHitPath.call(this, (x - m.ox) / m.s, (y - m.oy) / m.s);
};
{
  const bar = document.querySelector('.bar');
  if (bar) {
    const g = document.createElement('div');
    g.className = 'group';
    g.innerHTML = '<span class="lbl">Margin</span><button class="btn" id="bl-toggle">Show margin</button>';
    bar.appendChild(g);
    const btn = g.querySelector('#bl-toggle');
    const sync = () => { btn.textContent = blView ? 'Hide margin' : 'Show margin'; };
    btn.addEventListener('click', () => { blView = !blView; sync(); });
    sync();
  }
}

// A field inside a rigid tile reads the tile's rectangle, notched or not:
// the notch is the picture's last resort, not the field's world.
// (for its world only: the picture clips the field's leaves to what the
// tile actually paints, notch and all, or the members would paint into it)
const blOldCellPoly = Hive.prototype.cellPoly;
Hive.prototype.cellPoly = function(b) {
  if (this.depth === 0 && !this.blPainting && b.hole && b.blRigid) { const r = b.hole.rect; return [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]]; }
  return blOldCellPoly.call(this, b);
};
const blOldCollect = Hive.prototype.collectLeaves;
Hive.prototype.collectLeaves = function(out, ox, oy, fade) {
  if (this.depth !== 0) return blOldCollect.call(this, out, ox, oy, fade);
  this.blPainting = true;
  let res;
  try { res = blOldCollect.call(this, out, ox, oy, fade); } finally { this.blPainting = false; }
  // A POCKET IS PAINTED EVEN WHEN THE RESERVE HOLDS NOTHING ELSE. The
  // reference gathers a body's leaf from the cells it won; on a page whose
  // tiles cover every margin site the reserve wins none, and the pockets it
  // adopted would be painted by nobody — a hole in the page where the
  // auction has an owner. Its leaf is gathered here instead.
  const r = this.blReserve();
  if (r.blExtra && r.blExtra.length && !out.some(l => l.body === r)) {
    const pieces = r.blExtra.map(pc => ({ pts: pc.pts.map(q => [q[0] + (ox || 0), q[1] + (oy || 0)]), labs: pc.labs }));
    out.push({ path: [{ hive: this, body: r }], body: r, color: r.color, hv: 0, fade: fade === undefined ? 1 : fade, isVoid: true, labels: false, label: '', pieces, loops: null, touched: false });
  }
  return res;
};
// A FIELD INSIDE A NOTCHED TILE IS PAINTED INSIDE THE NOTCH. The field lays
// itself out in the tile's rectangle (cellPoly above: the layout does not
// re-solve as a notch passes), so where the tile yields a corner to a tile
// across it, the field's outlines are cut to the tile's pieces here, in
// the picture, and no ink lies under another tile's. (Called where the
// picture chains its leaves' outlines, on the root's leaves.)
function blClipNested(leaves) {
  for (const leaf of leaves) {
    if (!leaf.path || leaf.path.length < 2 || !leaf.loops) continue;
    const b = leaf.path[0].body;
    if (!b || !b.blRigid || !b.hole) continue;
    const r = b.hole.rect, pieces = b.hole.pieces;
    if (pieces.length === 1 && Math.abs(Math.abs(ringArea(pieces[0])) - (r[2] - r[0]) * (r[3] - r[1])) < 1e-6) continue;
    const planes = pieces.map(pc => convexPlanes(pc));
    const loops = [];
    for (const lp of leaf.loops) for (const hp of planes) {
      let q = lp;
      for (const h of hp) { if (!q) break; q = clipPts(q, h.ax, h.ay, h.b); }
      if (q && q.length >= 3 && Math.abs(ringArea(q)) > 1e-6) { if (lp.hole) q.hole = true; loops.push(q); }
    }
    leaf.loops = loops;
  }
}
