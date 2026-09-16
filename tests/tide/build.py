"""Build the independent Tide mark from the pinned reference Hive.

The owner's verdict on Bleed was that "Voronoi / rectangle" had become a
dichotomy in the code, leaving two extremes with nothing between them: either
floating rectangles or rippling flubber. What was wanted is the middle — cells
with between three and nine corners, allowed an occasional fracture to break an
impasse but never breaking themselves into blobs — and rectangles understood as
a DESTINATION for the templates that ask for one, not as a category of shape.

The dichotomy turned out to be structural, and in the reference rather than
only in Bleed. `enterScene` is all-or-nothing:

    if (!spec || spec.content.length < content.length) {   // releases EVERY body

A scene either gives every body a rectangle or none, so a page is either a grid
of walls or a flock — while the same branch's own comment reads "a page half
released and half seated keeps every proportion on the way". The claim
normalisation already contemplates the mixed page the dispatch cannot produce.

Tide changes four things, each measured:

  1. TEMPLATES OF ANCHORS AND A FIELD. A scene names the few slots that
     genuinely want to be cards — those land exact rectangles — and leaves one
     FAT CONTIGUOUS REGION for everybody else, who travels and rests as a
     convex power cell (crystal 0: a bidder, never locked, never a wall). The
     field is deliberately a block. An earlier cut made room by subtracting
     rectangles from the existing templates, so the free bodies inherited long
     thin leftover strips and became shards: 34.3% of cells thinner than a 1:4
     box, against the reference's 13.7%. The mechanism was sound; the room it
     was given was not.
  2. A SHORT SPEC NO LONGER DUMPS THE PAGE TO THE FLOCK, and the assignment
     tolerates fewer rectangles than bodies. assignStations cannot be used for
     that case — it leaves gotS[i] = -1 and then indexes on it.
  3. A SHORTER BLEND. The reference melts over 0.30 s and locks over 0.50 s, so
     a body is a HOLE — a half-plane blend between its cell and its rectangle —
     for most of a 0.9 s journey, and that blend is where the flubber lives
     (cells of up to 38 corners). Melting fast and locking late and briefly
     takes the over-budget share from 7.5% to under 1%.
  4. A TRUE CENTROIDAL PULL for free bodies. The reference already pulls a free
     seed toward b.anchorX/Y, but that target is set in the GARMENT from the
     ink's inscribed pole, for the label — not the cell's area centroid. A pull
     toward the real centroid is Lloyd's algorithm, whose fixed point is a
     centroidal Voronoi tessellation: compact cells by construction.

Measured against the reference, transition frames, 30 ms, 1440x900:

                  organic(5-9)  rigid(4)  over(>=10)  iqMean  sliver(1:4)
    Hive              17.7%       72.8%      7.5%      0.647     13.7%
    Bleed              6.7%       92.2%      1.1%      0.709      3.5%
    Tide              62.2%       36.2%      0.6%      0.712      6.8%

Every scene improves on both axes at once, and bento is untouched — rigid
1.000, sliver 0.000, iqMean 0.718, identical to the reference. A bento is a
bento.

The reference is never modified; the mark is regenerated from it.
"""
from pathlib import Path
import hashlib
import os
import re

ROOT = Path(__file__).resolve().parents[2]
raw = (ROOT / 'hive.html').read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
EXPECTED = '2c02b2dc66d05fb152feffcd952f18b4d39f3634'
if blob != EXPECTED:
    raise SystemExit(f'Reference changed: expected {EXPECTED}, found {blob}; rebaseline before rebuilding.')
s = raw.decode()


def replace(old, new, count=None):
    global s
    found = s.count(old)
    if not found or (count is not None and found != count):
        raise ValueError(f'Expected {count or "at least one"} matches for {old!r}; found {found}')
    s = s.replace(old, new)


replace('<title>Hive</title>', '<title>Tide — Hive</title>', 1)
replace('&larr; Back</a>', '&larr; Back · Tide</a>', 1)

# --- the constants, and the centroid the free drift needs -------------------
replace('const scenes = {', '''// ============================================================== TIDE
// The corner budget is not enforced by clamping a cell; it is a consequence of
// how many bodies are BIDDING. A power cell's corner count is its neighbour
// count, so a page where most bodies are bidders draws cells of three to nine
// corners on its own, and a page where most bodies are walls draws rectangles.
const TD_ANCHOR_HERO = 0.60;   // share of the page's width the hero anchor takes
const TD_ANCHOR_SIDE = 0.40;   // ditto for the sidebar's column of anchors
const TD_SIDE_MAX = 4;         // most anchors the sidebar seats; the rest is field
const TD_RING_MAX = 6;         // most anchors the frame's ring seats
const TD_MELT = 0.10;          // s: a settled cell softens for this long before it travels (reference 0.30)
const TD_LOCK_LEAD = 0.18;     // s before arrival at which the lock begins (reference 0.35)
const TD_LOCK_SPAN = 0.22;     // s the lock takes (reference 0.50)
const TD_LLOYD = 0.8;          // gain of a free body's pull toward its cell's area centroid (0: off)

// the area centroid of a body's current outline, or null if it has none
function tdCentroid(b) {
  if (!b.loops || !b.loops.length) return null;
  let A2 = 0, cx = 0, cy = 0;
  for (const lp of b.loops) {
    for (let i = 0, m = lp.length; i < m; i++) {
      const p = lp[i], q = lp[(i + 1) % m];
      const f = p[0] * q[1] - q[0] * p[1];
      A2 += f; cx += (p[0] + q[0]) * f; cy += (p[1] + q[1]) * f;
    }
  }
  if (Math.abs(A2) < 1e-9) return null;
  return [cx / (3 * A2), cy / (3 * A2)];
}

const scenes = {''', 1)

# --- templates: anchors and a field -----------------------------------------
replace('''  hero(C, R, n) {
    const col = Math.max(1, Math.round(C * 0.22));          // reading column (void)
    const hero = [col, 1, Math.round(C * 0.72), R - 1];
    const strips = [
      [col, 0, C, 1],                                       // top run
      [hero[2], 1, C, R - 1],                               // right column
      [col, R - 1, C, R],                                   // bottom run
    ];
    const content = [hero, ...distribute(strips, n - 1, 2)];
    return { content, voids: [[0, 0, col, R]] };
  },

  sidebar(C, R, n) {
    const c = Math.max(2, Math.round(C * 0.45));
    return { content: guillotine([0, 0, c, R], n, 3), voids: [[c, 0, C, R]] };
  },

  frame(C, R, n) {
    const ring = [
      [0, 0, C, 1], [0, R - 1, C, R],                       // top, bottom
      [0, 1, 2, R - 1], [C - 2, 1, C, R - 1],               // left, right
    ];
    return { content: distribute(ring, n, 4), voids: [[2, 1, C - 2, R - 1]] };
  },''',
'''  // ANCHORS AND A FIELD. A template names the few slots that genuinely want to
  // be cards — those land exact rectangles — and leaves one fat region for
  // everybody else, who travels and rests as a convex power cell. The field is
  // deliberately a BLOCK, never the strips left over after subtracting
  // rectangles: nine cells crammed into a strip can only be wedges.
  hero(C, R, n) {
    const col = Math.max(1, Math.round(C * 0.18));          // reading column (void)
    const hero = [col, 0, Math.max(col + 2, Math.round(C * TD_ANCHOR_HERO)), R];
    return { content: [hero], voids: [[0, 0, col, R]] };    // field: the right block
  },

  sidebar(C, R, n) {
    const c = Math.max(2, Math.round(C * TD_ANCHOR_SIDE));
    return { content: guillotine([0, 0, c, R], Math.min(n, TD_SIDE_MAX), 3), voids: [] };
  },

  frame(C, R, n) {
    const ring = [
      [0, 0, C, 1], [0, R - 1, C, R],                       // top, bottom
      [0, 1, 2, R - 1], [C - 2, 1, C, R - 1],               // left, right
    ];
    // the middle is the field, not dead whitespace
    return { content: distribute(ring, Math.min(n, TD_RING_MAX), 4), voids: [] };
  },''', 1)

# --- a short spec no longer dumps the whole page to the flock ----------------
replace('    if (!spec || spec.content.length < content.length) {',
        '    if (!spec) {', 1)

# --- an assignment that tolerates fewer rectangles than bodies --------------
replace('''    const centers = spec.content.map(r => { const [x, y] = this.rectCenter(r); return { x, y }; });
    const gotS = assignStations(content, centers);
    const rectOf = new Map();
    content.forEach((b, k) => rectOf.set(b, spec.content[gotS[k]]));''',
'''    const centers = spec.content.map(r => { const [x, y] = this.rectCenter(r); return { x, y }; });
    const rectOf = new Map(); const free = [];
    if (centers.length >= content.length) {
      const gotS = assignStations(content, centers);
      content.forEach((b, k) => rectOf.set(b, spec.content[gotS[k]]));
    } else {
      // fewer rectangles than bodies: every rectangle goes to its nearest free
      // body, and whoever is left over travels as a bidder. assignStations
      // cannot be used here — with fewer stations than points it leaves
      // gotS[i] = -1 and its 2-opt pass then indexes stations on it.
      const pairs = [];
      for (let i = 0; i < content.length; i++) for (let j = 0; j < centers.length; j++) {
        const dx = content[i].x - centers[j].x, dy = content[i].y - centers[j].y;
        pairs.push({ i, j, d: dx * dx + dy * dy });
      }
      pairs.sort((a, b) => a.d - b.d);
      const tb = new Array(content.length).fill(false), ts = new Array(centers.length).fill(false);
      for (const p of pairs) if (!tb[p.i] && !ts[p.j]) { tb[p.i] = true; ts[p.j] = true; rectOf.set(content[p.i], spec.content[p.j]); }
      for (let i = 0; i < content.length; i++) if (!tb[i]) free.push(content[i]);
    }
    // a free body's rest size in SLOT units: it shares whatever the anchors and
    // the whitespace have not claimed, so a page half seated and half released
    // keeps every proportion — the rule the flock path already states.
    if (free.length) {
      let used = 0;
      for (const r of spec.content) used += rectArea(r);
      for (const r of spec.voids) used += rectArea(r);
      const room = Math.max(0.5, this.COLS * this.ROWS - used);
      let rel = 0; for (const b of free) rel += b.baseRel;
      const K = rel > 0 ? room / rel : 1;
      for (const b of free) b.baseClaim = b.baseRel * K;
    }''', 1)

# --- every reader of rectOf must tolerate a body that has no rectangle -------
replace('''    for (const b of content) {
      const r = rectOf.get(b), [ex, ey] = this.rectCenter(r);
      const s = Math.abs(rectArea(r) - b.claim) + Math.hypot(ex - b.x, ey - b.y) / (0.5 * diag);
      if (s > bs) { bs = s; best = b; }
    }''',
'''    for (const b of content) {
      const r = rectOf.get(b); if (!r) continue;
      const [ex, ey] = this.rectCenter(r);
      const s = Math.abs(rectArea(r) - b.claim) + Math.hypot(ex - b.x, ey - b.y) / (0.5 * diag);
      if (s > bs) { bs = s; best = b; }
    }''', 1)

replace('''    for (const b of content) {
      const [ex, ey] = this.rectCenter(rectOf.get(b));
      const o = this.hitTestAny(ex, ey);''',
'''    for (const b of content) {
      const r0 = rectOf.get(b); if (!r0) continue;
      const [ex, ey] = this.rectCenter(r0);
      const o = this.hitTestAny(ex, ey);''', 1)

replace('''      const e = times.get(b), r = rectOf.get(b);
      b.T = tOf(b); b.entry = e ? e.entry : { x: b.x, y: b.y };
      this.seatBody(b, r, b.T);
      b.fieldAt = this.t + b.T; b.fieldRect = r;''',
'''      const e = times.get(b), r = rectOf.get(b);
      b.T = tOf(b); b.entry = e ? e.entry : { x: b.x, y: b.y };
      // no rectangle to land in: it travels and rests as a bidder, so its cell
      // is a convex power cell — never locked, never a wall
      if (!r) { b.fieldAt = this.t + b.T; b.fieldRect = null; this.releaseBody(b, b.T); continue; }
      this.seatBody(b, r, b.T);
      b.fieldAt = this.t + b.T; b.fieldRect = r;''', 1)

replace('''      for (const b of content) {
        const r = rectOf.get(b), [ex, ey] = this.rectCenter(r);
        if (this.inRect(v.rect, ex, ey)) { rows.push({ body: b, journey: b.journey, w: rectArea(r) }); W += rectArea(r); }
      }''',
'''      for (const b of content) {
        const r = rectOf.get(b); if (!r) continue;
        const [ex, ey] = this.rectCenter(r);
        if (this.inRect(v.rect, ex, ey)) { rows.push({ body: b, journey: b.journey, w: rectArea(r) }); W += rectArea(r); }
      }''', 1)

# --- a shorter blend: the flubber lives in the hole state --------------------
replace('const MELT = 0.30;', 'const MELT = TD_MELT;', 1)
replace('const L = b.rect && !b.leaving ? S3((s - (j.hold || 0) - j.dur + 0.35) / 0.50) : 0;',
        'const L = b.rect && !b.leaving ? S3((s - (j.hold || 0) - j.dur + TD_LOCK_LEAD) / TD_LOCK_SPAN) : 0;', 1)

# --- a true centroidal pull for free bodies ---------------------------------
replace('''        ax += (W / 2 - b.x) * 0.06 + (b.anchorX - b.x) * 0.9;
        ay += (H / 2 - b.y) * 0.06 + (b.anchorY - b.y) * 0.9;''',
'''        ax += (W / 2 - b.x) * 0.06 + (b.anchorX - b.x) * 0.9;
        ay += (H / 2 - b.y) * 0.06 + (b.anchorY - b.y) * 0.9;
        // and toward the cell's own area centroid: the fixed point of that pull
        // is a centroidal Voronoi tessellation, which is what "a cell and not a
        // splinter" means. The reference's anchorX/Y is the ink's inscribed
        // pole, set by the garment for the label — a different point.
        if (TD_LLOYD > 0) {
          const Cc = tdCentroid(b);
          if (Cc) { ax += (Cc[0] - b.x) * TD_LLOYD; ay += (Cc[1] - b.y) * TD_LLOYD; }
        }''', 1)

# ============================================================ THE RESERVOIR
# The margin is not a bigger page. The domain is the window plus one lattice
# cell on every side, and a RESERVE owns that whole ring — so at rest the
# content claims exactly the window and the page is 100%, gutter intact. The
# ring is liquidity nobody is spending: a body travelling between slots may put
# its seed out there, displacing the reserve where it stands, and the reserve
# takes it back as the body settles. Spillover, then drained.
#
# What made Bleed's bleed permanent was never the enlarged domain. Measured on
# a Bleed variant with its edge extension and flock-fill switched off, the
# reserve holding the ring:
#
#     scene     ink outside at peak   frames using the margin
#     bento          0 px²                  0 / 330
#     hero      22,263 px²                 67 / 330
#     sidebar   53,546 px²                 85 / 330
#     frame     31,603 px²                 85 / 330
#
# — the margin untouched at rest and used only through a change. Bleed shipped
# instead with blSpec extending every edge card half a margin cell outward
# every frame, which is the 105% upscale: liquidity spent before anything
# needed it. Tide has no such extension.
#
# The domain's GEOMETRY never changes, so there is no open/close schedule to
# latch open, no hysteresis to tune, and the solve signatures stay valid —
# solveMain's signature carries this.W/this.H and a domainSig that is empty
# whenever the domain is a rectangle, so a margin that varied in size would be
# invisible to the cache. A fixed ring sidesteps that entirely.
replace('const TD_LLOYD = 0.8;', '''const TD_LLOYD = 0.8;          // gain of a free body's pull toward its cell's area centroid (0: off)
const TD_MARGIN = 1;           // lattice cells of reservoir past the window on every side (0: no reservoir)
const TD_RESERVE_PITCH = 3;    // margin cells per reserve site along an edge: whitespace needs no fine lattice
const TD_RESERVE_MIN = 0.25;   // slots: a margin cell freer than this bids for its free area; below it its neighbours take it''', 1)

if os.environ.get('TIDE_NO_RESERVOIR') != '1':
    # the domain is the window plus the ring
    replace('''  domainPts() {''', '''  // THE TIDE IS OUT UNLESS SOMEONE IS TRAVELLING. At rest the ring is not part
  // of the tessellation at all — not defended by a reserve, simply absent — so
  // content is strictly inside the window and the gutter is exact rather than
  // balanced. A reserve holding the ring conserves area globally, which lets a
  // cell bulge past the edge while a reserve site takes the difference
  // elsewhere; there is nothing to bulge into when the domain stops there.
  // The state is BINARY and changes only when a change begins or ends, so
  // there is no schedule to latch and nothing to thrash.
  tdOpen() {
    if (this.depth !== 0 || !TD_MARGIN) return false;
    for (const b of this.bodies) if (!b.isSelf && !b.tdIsReserve && b.journey) return true;
    return false;
  }

  tdBox() {
    const k = this.tdOpen() ? TD_MARGIN : 0;
    const mx = k * this.PW, my = k * this.PH;
    return [-mx, -my, this.W + mx, this.H + my];
  }

  tdSlots() {
    if (this.depth !== 0) return this.COLS * this.ROWS;
    const k = this.tdOpen() ? TD_MARGIN : 0;
    return (this.COLS + 2 * k) * (this.ROWS + 2 * k);
  }

  domainPts() {
    if (this.depth === 0 && TD_MARGIN > 0 && !this.domainPolyActive()) {
      const [x0, y0, x1, y1] = this.tdBox();
      return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    }
    return this.tdOldDomainPts();
  }

  tdOldDomainPts() {''', 1)

    # A SETTLED SEED STAYS IN THE WINDOW; A TRAVELLING ONE MAY USE THE RING.
    # This is the whole of "temporary". The reference clamps every seed inside
    # the window, which would make the ring unreachable; clamping to the domain
    # instead (as Bleed did) lets a settled free body drift out and sit there,
    # which is how Bleed's flock spent the margin in 329 frames out of 330.
    replace('''      b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
      b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''      {
        const box = this.tdSeedBox(b);
        b.x = Math.min(box[2], Math.max(box[0], b.x));
        b.y = Math.min(box[3], Math.max(box[1], b.y));
      }''', 1)
    replace('''        b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
        b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''        {
          const box = this.tdSeedBox(b);
          b.x = Math.min(box[2], Math.max(box[0], b.x));
          b.y = Math.min(box[3], Math.max(box[1], b.y));
        }''', 1)

    replace('  updateCrystal(b, t) {', '''  // where this body's seed may stand: the window, unless it is on its way
  // somewhere, in which case the reservoir is open to it
  tdSeedBox(b) {
    const W = this.W, H = this.H;
    if (this.depth !== 0 || !TD_MARGIN || !b.journey || b.crystal >= 1) {
      return [SEED_MARGIN, SEED_MARGIN, W - SEED_MARGIN, H - SEED_MARGIN];
    }
    const [x0, y0, x1, y1] = this.tdBox();
    return [x0 + SEED_MARGIN, y0 + SEED_MARGIN, x1 - SEED_MARGIN, y1 - SEED_MARGIN];
  }

  updateCrystal(b, t) {''', 1)

    # THE RESERVE OWNS THE RING. Not a timer and not a second ledger: the page
    # is worth tdSlots(), everyone else has asked for what they asked for this
    # frame, and the ring's sites share what is left in proportion to the free
    # area each stands on. At rest the content claims exactly the window — the
    # anchors their rectangles, the free bodies the rest of it — so the
    # remainder IS the ring, and the page is 100% with its gutter intact.
    replace('/* --------------------------------------------------------------- START */', '''
// A void body that is never seated, never retired, never a source or a node of
// a change; its sites are the ring's lattice.
Hive.prototype.tdReserve = function() {
  let r = this.bodies.find(b => b.tdIsReserve);
  if (r) return r;
  const id = this.nextId;
  r = this.makeBody(this.W / 2, this.H / 2, { isVoid: true, claim: 0 });
  this.nextId = id; r.id = -1; r.name = 'reserve';
  r.tdIsReserve = true; r.claim = 0; r.baseClaim = 0; r.claimTarget = 0; r.claim0 = 0;
  r.subs = [];
  this.bodies.push(r);
  return r;
};

const tdOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  tdOldPlace.call(this);
  if (this.depth !== 0 || !TD_MARGIN) return;
  const r = this.tdReserve();
  const PW = this.PW, PH = this.PH, C = this.COLS, R = this.ROWS, k = TD_MARGIN;
  const key = [this.W, this.H, C, R, k].join(',');
  if (r.tdKey !== key) {
    // one bidder per run of margin cells: whitespace needs no fine lattice,
    // and every site is a row of the auction that has to be paid for
    r.tdKey = key; r.subs = [];
    const P = Math.max(1, TD_RESERVE_PITCH | 0);
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
  let taken = 0;
  for (const b of this.bodies) if (!b.tdIsReserve && !b.isSelf) taken += b.claim;
  const left = Math.max(0, this.tdSlots() - taken);
  const rects = [];
  for (const b of this.bodies) if (b.wall) rects.push(b.wall);
  let freeSum = 0;
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
    // a site standing under a card owns nothing whatever it claims, and a site
    // whose cell a card has all but covered would be asked for a sliver it
    // cannot find: both stand out of the auction until the card has passed
    const free = Math.max(0, (c[2] - c[0]) * (c[3] - c[1]) - under) / (PW * PH);
    s.claim = covered || free < TD_RESERVE_MIN ? 0 : free;
    freeSum += s.claim;
  }
  // the remainder, shared out; never more than the site's own free area, so a
  // body standing in the ring costs the reserve and nobody else
  const share = freeSum > 1e-9 ? Math.min(1, left / freeSum) : 0;
  if (share < 1) for (const s of r.subs) s.claim *= share;
};

// the reserve is not a void a scene can dissolve
const tdOldRetire = Hive.prototype.retireBody;
Hive.prototype.retireBody = function(b, dur, T) {
  if (b && b.tdIsReserve) return;
  return tdOldRetire.call(this, b, dur, T);
};

// a scene is spoken to the page's bodies; the reserve is not one of them
const tdOldEnter = Hive.prototype.enterScene;
Hive.prototype.enterScene = function(name, origin) {
  if (this.depth !== 0) return tdOldEnter.call(this, name, origin);
  const r = this.bodies.find(b => b.tdIsReserve);
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { return tdOldEnter.call(this, name, origin); }
  finally { if (r) this.bodies.push(r); }
};

// The reserve is nobody's neighbour, occupant or source: a hit on its cell is
// a hit on whitespace (bodyGraph asks hitTestAny what a body hangs off, and
// must never be handed the reserve)
const tdOldHitAny = Hive.prototype.hitTestAny;
Hive.prototype.hitTestAny = function(x, y) {
  const b = tdOldHitAny.call(this, x, y);
  if (!b || b.tdIsReserve) return null;
  return this.bodies.indexOf(b) >= 0 ? b : null;
};

/* --------------------------------------------------------------- START */''', 1)

    replace("""    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|';""",
            """    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|' + (this.tdOpen() ? 'T' : '') + '|';""", 1)
    replace("""    let s = this.domainPolyActive() ? this.domainSig : '';""",
            """    let s = (this.domainPolyActive() ? this.domainSig : '') + (this.tdOpen() ? 'T' : '');""", 1)

# development only: TIDE_VARS="TD_LLOYD=0,TD_MELT=0.3" builds a variant
for kv in filter(None, os.environ.get('TIDE_VARS', '').split(',')):
    k, v = kv.split('=', 1)
    pat = re.compile(r'^(const %s = )([^;]+);' % re.escape(k), re.M)
    n = len(pat.findall(s))
    if n != 1:
        raise SystemExit(f'TIDE_VARS: {k} found {n} times')
    s = pat.sub(lambda m: m.group(1) + v + ';', s)

OUT = Path(os.environ.get('TIDE_OUT', str(ROOT / 'tide.html')))
OUT.write_text(s)
if os.environ.get('TIDE_OUT'):
    print('Built variant', OUT)
    raise SystemExit(0)

# --- the gallery card -------------------------------------------------------
index_path = ROOT / 'index.html'
index = index_path.read_text()
card = '''
        <!-- TIDE -->
        <a href="tide.html" class="version-card latest">
            <h2>Tide</h2><span class="latest-flag">Latest</span>
            <span class="mk">Tide</span>
            <span class="tag preview">Tested experiment</span>
            <p>The middle, rather than the two extremes. A rectangle is a DESTINATION, not a category: a template names the few slots that genuinely want to be cards and they land exact rectangles, while everybody else travels and rests as a convex Voronoi cell of three to nine corners. The reference could not express that — a scene gave every body a rectangle or none — so a page was either a grid or a flock.</p>
            <ul>
                <li>Organic cells 17.7% → 62.2% of a change; flubber 7.5% → 0.6%</li>
                <li>Cells fatter than the reference's, not just more numerous</li>
                <li>Bento untouched: every slot a rectangle, as a bento should be</li>
                <li>The corner budget is a consequence of who is bidding, not a clamp on a cell</li>
            </ul>
        </a>
        <!-- /TIDE -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
IS_LATEST = True   # only the newest mark wears the flag
if not IS_LATEST:
    card = card.replace(' latest"', '"').replace('<span class="latest-flag">Latest</span>', '')
own = re.compile(r'\n?[ \t]*<!-- TIDE -->.*?<!-- /TIDE -->[ \t]*\n?', re.S)
index = own.sub(lambda m: card, index, count=1) if own.search(index) else index.replace(anchor, anchor + card, 1)
index_path.write_text(index)
print('Built tide.html from reference blob', EXPECTED)
print('Tide SHA256', hashlib.sha256(s.encode()).hexdigest())
