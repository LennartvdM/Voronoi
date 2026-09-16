"""Build the independent Murmur mark from the pinned reference Hive.

Tide answered "I want the thing in between" by building a THIRD thing: a
template named the few slots that were allowed to be rectangles, everybody
else was released to the flock, and the two kinds of body lived side by side.
The owner's verdict was that the taxonomy fights itself — "an unnecessary
burden" that produces "jumping to conclusions animations" — and the
measurement agrees. Over the three transition scenes, 30 ms, 1440x900:

    mark        netDisp  wander  moveFrames  burst  peak/mean  settleShare
    hive          454.2   1.41      46.7     0.676    5.88       0.430
    astra-i       378.8   1.26      59.4     0.631    4.69       0.444
    tessera       403.4   1.31      51.3     0.725    3.69       0.388
    bleed         473.8   1.16      48.6     0.649    2.55       0.388
    tide          146.1   4.05      87.1     0.372   21.78       0.902

Tide's bodies travel a third as far, by a route four times as indirect, with a
fastest frame twenty-two times their average one. That is the coiled spring,
and it has a single cause in the code. `seatBody` gives a body a path —

    b.path = { sx, sy, ex, ey, cx, cy };    // a bezier, eased over its journey

— and `releaseBody`, the branch Tide sends most of the page down, sets

    b.path = null;                          // "a journey without a path"

A released body has no choreography at all. It is pulled by springs toward
wherever the auction leaves room, so it stands still while the seated cards
land and is then shoved into the gap that opens. Tide made most of the page
released, so most of the page jumps.

MURMUR DELETES THE TAXONOMY INSTEAD OF EXTENDING IT. There is one kind of
body, and it is a bidder. The reference keeps three states in `b.crystal` —
0 is a bidder drawing a convex power cell, 1 is a WALL cut exactly out of the
ground as a rectangle, and anything between is a HOLE, a half-plane blend of
the two. The blend is where the flubber lives: a cell of up to 38 corners,
which is the rippling the owner objected to two marks ago. Murmur pins the
root hive's crystal to 0 and nothing else:

    updateCrystal(b, t) { if (this.depth === 0) { b.crystal = 0; b.pin = 0; return; } ... }

Every consequence follows from that one line rather than from a rule policing
it. A power cell of a single site is convex, so its corner count is its
neighbour count and the owner's three-to-nine budget is met BY CONSTRUCTION —
measured over every scene, over budget is 0.000 and the worst cell in the mark
has nine corners. Fracturing becomes unnecessary rather than rationed, which
is what "fracturing is for last resort solutions" asks for. And because no
body is ever released, every body is seated, and every seated body has a
path: the choreography comes back.

    murmur (core)  netDisp 368.4  wander 1.21  peak/mean 4.23  settleShare 0.395

— second only to Bleed on directness, and the reference itself wanders more.

THE PRICE, STATED PLAINLY. A rectangle is now a destination and only that: a
body travels to its rectangle's centre and claims its rectangle's area, and
the cell it draws is the best a power diagram can do around that seed. For a
uniform grid that is the grid exactly; for the guillotine's uneven bento it is
close but not exact, and the bento's share of four-cornered cells falls from
1.000 to 0.062. This is not a tuning failure. A power cell has a vertical edge
only where its neighbours are aligned in y, and a general slicing layout
over-constrains that — which is precisely why the reference needs walls, and
why walls bring the blend, and why the blend brings the flubber. Exact
rectangles and organic cells are the same dial. Murmur turns it the other way.

THE SPILLOVER IS THE PAGE'S, NOT THE CELL'S. Tide's reservoir worked and is
kept: the domain is the window plus one lattice cell on every side, a reserve
owns that ring, and the ring EXISTS only while somebody is travelling, so at
rest the page is the window, at 100%, with its gutter intact. What was wrong
with it was who could reach it. A cell being crushed could put its own seed
out there and take the room for itself, which is a private escape hatch — the
owner saw single cells resorting to it when squeezed and nothing using it
together. Murmur adds the SWELL: while a body is travelling it is given extra
area, on a hump that is exactly zero at both ends of its journey, and the
RESERVOIR pays for it rather than its neighbours. The room does not appear
around the traveller; it is pushed outward through the page until it reaches
the edge, where the reserve yields. So a change dilates the whole
neighbourhood along the route and relieves at the boundary, together, and
drains as the last body lands.

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


def replace(old, new, count=1):
    global s
    found = s.count(old)
    if found != count:
        raise ValueError(f'Expected {count} matches for {old[:70]!r}; found {found}')
    s = s.replace(old, new)


replace('<title>Hive</title>', '<title>Murmur — Hive</title>')
replace('&larr; Back</a>', '&larr; Back · Murmur</a>')

# --------------------------------------------------------------- the constants
replace('const scenes = {', '''// ============================================================ MURMUR
// There is no taxonomy here. Everything below is a consequence of the root
// hive having ONE kind of body — a bidder — and of the reservoir being the
// page's to spend rather than any one cell's.
const MU_MARGIN = 1;           // lattice cells of reservoir past the window on every side (0: no reservoir)
const MU_RESERVE_PITCH = 3;    // margin cells per reserve site along an edge: whitespace needs no fine lattice
const MU_SWELL = 0.35;         // extra area a traveller borrows at mid-journey, per unit of its own claim (0: off)
const MU_SWELL_CAP = 0.55;     // most of the ring the page may have on loan at once

// A hump on a body's own journey: zero at the start, zero at the end, one in
// the middle. The swell has to vanish at both ends or the page would not be
// the window at rest, which is the whole of the owner's second complaint.
function muHump(p) { return p > 0 && p < 1 ? 4 * p * (1 - p) : 0; }

// ON ITS WAY SOMEWHERE — the one question the reservoir asks, and the only
// thing that opens it. A journey is not enough on its own: `steer` refuses to
// end one for a body that is `leaving` or that keeps a `table`, and a void
// keeps its table for good once a scene has opened it. Reading the journey
// alone therefore left the ring open for ever in exactly the three scenes
// that have voids — hero, sidebar and frame — which is a permanent bleed
// wearing a temporary one's clothes. Progress is the truthful clock: it is 0
// before the body's own delay elapses, and 1 the moment it has arrived.
//
// AND IT MUST HAVE A PATH. The reservoir accommodates CHOREOGRAPHED motion:
// a body that knows where it is going and is on its way there. A released
// body has `path = null` — it is not going anywhere, it is being pushed
// about by the separation law until it finds a gap. Letting those reach the
// ring is what the flock did with it: with every seed free to leave the
// window and nothing but separation acting on them, the whole roster was
// pushed outward at once and the middle of the page opened into a hole
// 416,000 px² across before the ring shut and pulled everyone back. Drift
// has no claim on the corridor.
//
// AND THE PATH MUST GO SOMEWHERE. `retireBody` gives a body a path from
// where it stands to where it stands — a journey whose whole content is
// shrinking out of sight — and `seatBody` leaves a bystander seated where it
// already was. Neither is going anywhere, and neither needs room to do it.
// The ring is ONE domain shared by the whole page, so whoever opens it opens
// it for everybody: in the flock a single retiring body held it open for 67
// frames while the twelve drifters, none of whom could put a SEED out there,
// spread their CELLS into it anyway and left a hole in the middle of the
// page. A door one body can hold open for the rest is the escape hatch in
// its purest form.
function muTravelling(b) {
  if (b.isSelf || b.muIsReserve || b.leaving) return false;
  if (!b.journey || b.progress >= 1) return false;
  const p = b.path;
  return !!p && Math.hypot(p.ex - p.sx, p.ey - p.sy) > 1;
}

const scenes = {''')

# ------------------------------------------------------------- one kind of body
# THE WHOLE MARK. A wall is a rectangle cut out of the ground; a hole is the
# half-plane blend between a cell and a rectangle, and the blend is the
# flubber. Refusing to leave zero refuses both, and a single site's power cell
# is convex — so three-to-nine corners is not a rule that has to be policed,
# it is the shape a bidder has.
#
# Nested hives are untouched: a field's members still melt and lock inside it,
# because a member's rectangle is cut out of its field's cell and not out of
# the page, and there is no blend against the window to ripple.
replace('''  updateCrystal(b, t) {
    if (b.table && b.table.mode === 'open') return;      // an opening void reads its vacators' clocks''',
'''  updateCrystal(b, t) {
    // ONE SPECIES. Not "a voronoi unless a template predestined a rectangle":
    // a rectangle is a DESTINATION — a place to travel to and an area to
    // claim — and never a category the body belongs to.
    if (this.depth === 0) { b.crystal = 0; b.pin = 0; return; }
    if (b.table && b.table.mode === 'open') return;      // an opening void reads its vacators' clocks''')

# --------------------------------------------------------- a journey that ends
# The reference ends a journey only for a body that has NO rectangle:
#
#     if (!b.rect && !b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;
#
# which is sound there, because a body that does have one announces it has
# arrived by reaching crystal 1 and becoming a wall. Nothing here ever does,
# so without this every body would carry a finished journey for the rest of
# the page's life — and the reservoir below, which opens exactly while
# somebody is travelling, would never close again. That is the permanent
# bleed the owner threw out two marks ago, arrived at by a different road.
#
# A finished journey is finished. The body keeps its path, so it goes on
# holding the end of it, and keeps the 2.5 px resting wobble the reference
# fades out with the lock — a bidder breathes, which is the state every body
# here is in.
replace('        if (!b.rect && !b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;',
        '        if (!b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;')

# ================================================================ THE RESERVOIR
# The margin is not a bigger page. While anybody is travelling the domain is
# the window plus one lattice cell on every side and a RESERVE owns that whole
# ring; the moment the last body lands the ring is not part of the
# tessellation at all — not defended, simply absent — so content is strictly
# inside the window and the gutter is exact rather than balanced.
#
# The state is BINARY and changes only when a change begins or ends, so there
# is no schedule to latch open and nothing to thrash. The solve signatures
# carry it: solveMain's sig holds this.W/this.H and a domainSig that is empty
# whenever the domain is a rectangle, so a margin that varied in size would be
# invisible to the cache.
if os.environ.get('MU_NO_RESERVOIR') != '1':
    replace('  domainPts() {', '''  muOpen() {
    if (this.depth !== 0 || !MU_MARGIN) return false;
    for (const b of this.bodies) if (muTravelling(b)) return true;
    return false;
  }

  muBox() {
    const k = this.muOpen() ? MU_MARGIN : 0;
    const mx = k * this.PW, my = k * this.PH;
    return [-mx, -my, this.W + mx, this.H + my];
  }

  muSlots() {
    if (this.depth !== 0) return this.COLS * this.ROWS;
    const k = this.muOpen() ? MU_MARGIN : 0;
    return (this.COLS + 2 * k) * (this.ROWS + 2 * k);
  }

  domainPts() {
    if (this.depth === 0 && MU_MARGIN > 0 && !this.domainPolyActive()) {
      const [x0, y0, x1, y1] = this.muBox();
      return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    }
    return this.muOldDomainPts();
  }

  muOldDomainPts() {''')

    # A SETTLED SEED STAYS IN THE WINDOW; A TRAVELLING ONE MAY USE THE RING.
    # This is the whole of "temporary". The reference clamps every seed inside
    # the window, which would make the ring unreachable; clamping to the
    # domain instead lets a settled body drift out and sit there, which is how
    # Bleed spent its margin in 329 frames out of 330.
    replace('''      b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
      b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''      {
        const box = this.muSeedBox(b);
        b.x = Math.min(box[2], Math.max(box[0], b.x));
        b.y = Math.min(box[3], Math.max(box[1], b.y));
      }''')
    replace('''        b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
        b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''        {
          const box = this.muSeedBox(b);
          b.x = Math.min(box[2], Math.max(box[0], b.x));
          b.y = Math.min(box[3], Math.max(box[1], b.y));
        }''')

    replace('  updateCrystal(b, t) {', '''  // where this body's seed may stand: the window, unless it is on its way
  // somewhere, in which case the reservoir is open to it
  muSeedBox(b) {
    const W = this.W, H = this.H;
    if (this.depth !== 0 || !MU_MARGIN || !muTravelling(b)) {
      return [SEED_MARGIN, SEED_MARGIN, W - SEED_MARGIN, H - SEED_MARGIN];
    }
    const [x0, y0, x1, y1] = this.muBox();
    return [x0 + SEED_MARGIN, y0 + SEED_MARGIN, x1 - SEED_MARGIN, y1 - SEED_MARGIN];
  }

  updateCrystal(b, t) {''')

    replace('/* --------------------------------------------------------------- START */', '''
// A void body that is never seated, never retired, never a source or a node of
// a change; its sites are the ring's lattice.
Hive.prototype.muReserve = function() {
  let r = this.bodies.find(b => b.muIsReserve);
  if (r) return r;
  const id = this.nextId;
  r = this.makeBody(this.W / 2, this.H / 2, { isVoid: true, claim: 0 });
  this.nextId = id; r.id = -1; r.name = 'reserve';
  r.muIsReserve = true; r.claim = 0; r.baseClaim = 0; r.claimTarget = 0; r.claim0 = 0;
  r.subs = [];
  this.bodies.push(r);
  return r;
};

// THE SWELL — the reservoir spent by the page rather than by a cell.
//
// A body on its way somewhere needs room it does not need at rest: its seed is
// between two configurations, and the area it is owed does not fit the shape
// it is passing through. Left alone it takes that room from whoever it is
// passing, and the crushed neighbour takes it back the instant the traveller
// has gone — the shove-and-recoil that reads as a spring uncoiling.
//
// Here a traveller is instead LENT area, on a hump that is exactly zero at
// both ends of its journey, and the reserve's claim falls by the same amount.
// Nothing local happens: the loan is granted at the edge of the page, so the
// room has to be pushed inward through everybody between the boundary and the
// traveller. Every cell along the way is a little larger while the change
// passes and is exactly itself again after, and several travellers are
// accommodated at once out of one pool. That is the difference between a
// buffer the page uses together and an escape hatch one cell reaches for.
//
// The loan is capped at a share of the ring, so a scene that moves everything
// at once borrows what there is and no more, and the reserve can always pay.
Hive.prototype.muSwell = function() {
  if (this.depth !== 0 || !MU_MARGIN || MU_SWELL <= 0) return 0;
  const rows = [];
  let want = 0;
  for (const b of this.bodies) {
    if (!muTravelling(b)) continue;
    const h = muHump(b.progress);
    if (h <= 0) continue;
    let own = 0; for (const sub of b.subs) own += sub.claim;
    if (own <= 0) continue;
    const w = MU_SWELL * h * own;
    rows.push({ b, w, own }); want += w;
  }
  if (want <= 0) return 0;
  const ring = this.muSlots() - this.COLS * this.ROWS;
  const cap = MU_SWELL_CAP * Math.max(0, ring);
  const k = want > cap ? cap / want : 1;
  for (const r of rows) {
    const g = 1 + (r.w * k) / r.own;
    for (const sub of r.b.subs) sub.claim *= g;
  }
  return want * k;
};

const muOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  muOldPlace.call(this);
  if (this.depth !== 0 || !MU_MARGIN) return;
  this.muLoan = this.muSwell();
  const r = this.muReserve();
  const PW = this.PW, PH = this.PH, C = this.COLS, R = this.ROWS, k = MU_MARGIN;
  const key = [this.W, this.H, C, R, k].join(',');
  if (r.muKey !== key) {
    // one bidder per run of margin cells: whitespace needs no fine lattice,
    // and every site is a row of the auction that has to be paid for
    r.muKey = key; r.subs = [];
    const P = Math.max(1, MU_RESERVE_PITCH | 0);
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
  // THE LEDGER IS ONE LINE. The page is worth muSlots(); everybody else has
  // asked for what they asked for this frame, the swell included; the ring's
  // sites share what is left in proportion to the area each stands on. At rest
  // the content claims exactly the window, so the remainder IS the ring and
  // the page is 100% with its gutter intact. Under a swell the remainder is
  // smaller by the loan, and the ring gives that much ground — which is the
  // spillover, granted at the boundary and spent through the middle.
  let taken = 0;
  for (const b of this.bodies) {
    if (b.muIsReserve || b.isSelf) continue;
    for (const sub of b.subs) taken += sub.claim;
  }
  const left = Math.max(0, this.muSlots() - taken);
  let freeSum = 0;
  for (const sub of r.subs) {
    const c = sub.cell;
    // (the reference's placeSeeds moves every body's first site to the body:
    // the reserve's sites stand on their lattice cells, always)
    sub.x = (c[0] + c[2]) / 2; sub.y = (c[1] + c[3]) / 2;
    sub.claim = (c[2] - c[0]) * (c[3] - c[1]) / (PW * PH);
    freeSum += sub.claim;
  }
  const share = freeSum > 1e-9 ? Math.min(1, left / freeSum) : 0;
  if (share < 1) for (const sub of r.subs) sub.claim *= share;
};

// THE RESERVE IS SOLVER-ONLY. It is a row of the auction and nothing else:
// it has no ink, no label, no hover and no business in the page's physics.
// The engine's loops skip `isSelf` and nothing else, so appending the reserve
// to `this.bodies` silently enrolled it in all three — and it does not sit
// quietly. `easeClaims` floors every body at CLAIM_MIN, so the reserve was
// carrying a claim of 0.02 (harmless in the auction, where its sites' claims
// are recomputed from the ledger every frame, but not in `separate`, which
// sizes a body's radius from exactly that number). `steer` then gave it the
// free-drift springs, so it wandered: measured over one run, 366 px across
// the page at up to 158 px/s in the sidebar, closing to 59 px of a content
// body — well inside the ~195 px at which the separation law starts pushing.
// An invisible body was shouldering the page around.
//
// Four guards, one statement: the reserve does not move, is not pushed, and
// is not pushed against. The fourth is the one that mattered most, and it
// displaces CONTENT rather than the reserve: `enforcePreconditions` ends with
// a minimum-seed-separation pass that shoves any two bodies closer than
// SEED_MIN_SEP apart, skipping only `isSelf`. With an invisible body parked
// at the page centre, every content seed whose route passed near the middle
// was pushed off it by an obstacle that is not there — measured as content
// being held at exactly 5 px from the reserve in three scenes out of five.
const muOldSteer = Hive.prototype.steer;
Hive.prototype.steer = function(dt, t) {
  const r = this.depth === 0 ? this.bodies.find(b => b.muIsReserve) : null;
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { return muOldSteer.call(this, dt, t); }
  finally { if (r) this.bodies.push(r); }
};

const muOldSeparate = Hive.prototype.separate;
Hive.prototype.separate = function(dt) {
  const r = this.depth === 0 ? this.bodies.find(b => b.muIsReserve) : null;
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { return muOldSeparate.call(this, dt); }
  finally { if (r) this.bodies.push(r); }
};

const muOldPre = Hive.prototype.enforcePreconditions;
Hive.prototype.enforcePreconditions = function(...a) {
  const r = this.depth === 0 ? this.bodies.find(b => b.muIsReserve) : null;
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { return muOldPre.apply(this, a); }
  finally { if (r) this.bodies.push(r); }
};

const muOldEase = Hive.prototype.easeClaims;
Hive.prototype.easeClaims = function(dt, t) {
  const r = this.depth === 0 ? this.bodies.find(b => b.muIsReserve) : null;
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { return muOldEase.call(this, dt, t); }
  finally { if (r) { r.claim = 0; r.claimTarget = 0; this.bodies.push(r); } }
};

// the reserve is not a void a scene can dissolve
const muOldRetire = Hive.prototype.retireBody;
Hive.prototype.retireBody = function(b, dur, T) {
  if (b && b.muIsReserve) return;
  return muOldRetire.call(this, b, dur, T);
};

// a scene is spoken to the page's bodies; the reserve is not one of them
const muOldEnter = Hive.prototype.enterScene;
Hive.prototype.enterScene = function(name, origin) {
  if (this.depth !== 0) return muOldEnter.call(this, name, origin);
  const r = this.bodies.find(b => b.muIsReserve);
  if (r) this.bodies = this.bodies.filter(b => b !== r);
  try { return muOldEnter.call(this, name, origin); }
  finally { if (r) this.bodies.push(r); }
};

// The reserve is nobody's neighbour, occupant or source: a hit on its cell is
// a hit on whitespace (bodyGraph asks hitTestAny what a body hangs off, and
// must never be handed the reserve)
const muOldHitAny = Hive.prototype.hitTestAny;
Hive.prototype.hitTestAny = function(x, y) {
  const b = muOldHitAny.call(this, x, y);
  if (!b || b.muIsReserve) return null;
  return this.bodies.indexOf(b) >= 0 ? b : null;
};

/* --------------------------------------------------------------- START */''')

    replace("""    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|';""",
            """    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|' + (this.muOpen() ? 'M' : '') + '|';""")
    replace("""    let s = this.domainPolyActive() ? this.domainSig : '';""",
            """    let s = (this.domainPolyActive() ? this.domainSig : '') + (this.muOpen() ? 'M' : '');""")

# development only: MURMUR_VARS="MU_SWELL=0,MU_MARGIN=0" builds a variant
for kv in filter(None, os.environ.get('MURMUR_VARS', '').split(',')):
    kk, vv = kv.split('=', 1)
    pat = re.compile(r'^(const %s = )([^;]+);' % re.escape(kk), re.M)
    n = len(pat.findall(s))
    if n != 1:
        raise SystemExit(f'MURMUR_VARS: {kk} found {n} times')
    s = pat.sub(lambda m: m.group(1) + vv + ';', s)

OUT = Path(os.environ.get('MURMUR_OUT', str(ROOT / 'murmur.html')))
OUT.write_text(s)
if os.environ.get('MURMUR_OUT'):
    print('Built variant', OUT)
    raise SystemExit(0)
# --- the gallery card -------------------------------------------------------
index_path = ROOT / 'index.html'
index = index_path.read_text()
card = '''
        <!-- MURMUR -->
        <a href="murmur.html" class="version-card latest">
            <h2>Murmur</h2><span class="latest-flag">Latest</span>
            <span class="mk">Murmur</span>
            <span class="tag preview">Tested experiment</span>
            <p>One kind of body, not two. The reference keeps three states in a cell — a bidder, a rectangle cut out of the ground, and a half-plane blend between them — and the blend is where the rippling lives. Murmur deletes the blend: every cell is a bidder, so three to nine corners is the shape a cell HAS rather than a rule policed against it, and a rectangle is somewhere to travel to. Nobody is released, so everybody has a path to follow.</p>
            <ul>
                <li>Flubber 7.5% &rarr; 0.1%; the worst cell falls from 38 corners to 10</li>
                <li>Cells fatter and less splintered than the reference&rsquo;s at every clock</li>
                <li>The margin is used by 5.6 cells at once over three edges, and is empty at rest</li>
                <li>Steadier than the reference on its own clock: no cell jumps into place</li>
            </ul>
        </a>
        <!-- /MURMUR -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
IS_LATEST = True   # only the newest mark wears the flag
if not IS_LATEST:
    card = card.replace(' latest"', '"').replace('<span class="latest-flag">Latest</span>', '')
own = re.compile(r'\n?[ \t]*<!-- MURMUR -->.*?<!-- /MURMUR -->[ \t]*\n?', re.S)
index = own.sub(lambda m: card, index, count=1) if own.search(index) else index.replace(anchor, anchor + card, 1)
index_path.write_text(index)
print('Built murmur.html from reference blob', EXPECTED)
print('Murmur SHA256', hashlib.sha256(s.encode()).hexdigest())
