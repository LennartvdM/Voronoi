"""Build the Pane mark: whitespace that is the rectangle it was given.

Plumb draws the CARDS on axis. It never touched the whitespace, and neither
did any number this repository published, because plumb.js drops l.isVoid.
Measured against the rectangle each void was actually handed - the area of the
symmetric difference over the area of the rect, and the corner count after
collinear points are collapsed:

                    Plumb                 Pane
    hero      miss 0.1157,  6 corners   0.0188, 4
    sidebar   miss 0.0461,  7 corners   0.0000, 4
    frame     miss 0.3100, 11 corners   0.0224, 5

frame is the scene that shows why it matters: the layout is a frame around a
hole and a third of that hole was somewhere else.

WHY IT FANS. enterScene makes each void ONE body at its rect's centre and
refreshFormation pins b.subs.length = 1 - one seed per body, which is exactly
what keeps every CARD convex and the 3-9 corner budget an identity. One seed
cannot draw a rectangle; it draws a radial fan.

WHY NOT ASTRA I'S ANSWER. Astra I has all of this right, and it is worth being
exact about how: probed at rest, ALL THIRTEEN of its bodies are walls,
crystal == 1, root.walls.length == 13. Nothing in Astra I is a power cell when
settled. Its exact rectangles and the taxonomical dichotomy are the same
mechanism, applied to everything. Plumb has walls == 0.

WHAT THIS MARK DOES. A wall is the reference's own exact rectangle cut from the
auction ground, and whitespace draws no card - so making the WHITESPACE a wall
adds no second kind of card. Every card is still a one-seed bidder. But a wall
that switches on is a skip: measured at 29.7% of the screen repainted in one
frame, because domainPieces cuts the ground into convex pieces the instant a
wall exists and every card is re-solved on a domain that changed shape at once.

So the pane GROWS, and the auction's books stay balanced while it does:

  THE CUT IS A BAND, swept across the rect from one edge. Grown about the
  centre instead, it swallows the void's own seed and leaves its cell an
  annulus, which a convex power cell cannot be - measured 416. Swept, what is
  left of the void is itself a rectangle, its seed sits in the middle of that,
  and wall + cell together are the whole rectangle at every value of s.

  THE CLAIM LEAVES WITH THE AREA. solveWeights normalises
  tgt[i] = claim[i] * domainArea / sum(claims), so claims are SHARES: what
  leaves the domain must leave the sum of claims in the same frame or every
  other cell's target area jumps. The band takes s * a; the void bids for the
  rest.

  AND IT IS SET ON THE SEED, NOT THE BODY. placeSeeds ends with
      s.claim = b.wall ? 0 : b.claim * hover;      (hive.html:2228)
  so the frame the band first appears the whitespace is dropped from the
  auction ENTIRELY rather than by the width of the band, and the cards flood
  the whole rectangle. That was one card going 28,354 -> 66,521 px2 in a single
  frame, and it is why a SLOWER sweep measured worse: the mismatch lasted
  longer. The same restoration is needed through the melt-out, because a
  retiring void still has a wall and placeSeeds still zeroes it.

  IT FIRMS ONLY ONCE THE WHITESPACE OWNS ITS RECTANGLE. While a void is still
  opening, cards are vacating it and it owns only a*f; cutting a band then puts
  its claim and its geometry at odds and the page fills with slivers - 0.317
  against Plumb's 0.106.

WHAT IT COSTS, AND IT IS NOT NOTHING. One frame entering the sidebar repaints
12.2% of the screen against 2.8% either side - jolt reads spikeMax 13.53 with 3
spike frames over the run, against Plumb's 2.71 with none. That frame is the
ground's convex decomposition gaining pieces, which is COMBINATORIAL and so
cannot be rate-limited: measured identical at sweep rates from 0.35 to 3.0,
and unchanged by fitting a field to all of its loops rather than its largest.
It is a quarter of what the switched wall cost, and it is still a hitch.
Everything else holds or improves: vertsMax 9, overBudget 0.0000, iqMin 0.245,
sliverShare 0.081 against Plumb's 0.106.
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


replace('<title>Hive</title>', '<title>Plumb — Hive</title>')
replace('&larr; Back</a>', '&larr; Back · Plumb</a>')

# --------------------------------------------------------------- the constants
replace('const scenes = {', '''// ============================================================ PLUMB
const PN_PANE = 1;      // whitespace firms into its own rectangle
const PN_SLEW = 0.8;    // how fast it firms, in units of s per second
const PN_CAP = 0.98;    // the live band never closes entirely: its seed needs room
const PN_EPS = 1e-4;
const PL_SWELL = 0.35;    // extra claim a traveller carries at mid-journey, per unit of its own (0: off)
const PL_CAP = 0.25;      // most the domain may exceed the window by, as a share of it
const PL_SLEW = 1.2;      // fastest the swell may change, per second (0: no limit)
// MEASURED, AND SWITCHED OFF. With this on, whitespace takes one site per
// cell it borders, mirrored to that cell's own centre line and claiming the
// band it ought to own. It works, and spectacularly: the sidebar goes to an
// axis-aligned share of 0.999 and EVERY cell in it becomes a true rectangle,
// which is Astra I's result with no wall anywhere. It also brings the skip
// back. jolt.js puts every one of its spikes at normalised position 0.00 —
// the frame `enterScene` assigns new rectangles and the void's whole site set
// is rebuilt at once — worst 65.2 against 2.7 with it off, and two spike
// frames where there were none. That is the switch Bellows exists to remove,
// reached by another road, and a straighter seam is not worth it. Left in,
// off, because the finding is worth keeping and the fix is a crossfade of the
// old site set into the new one rather than a rebuild.
const PL_SEAM_SITES = 0;
const PL_EPS = 1e-9;

// A hump on a body's own journey: zero at the start, zero at the end, one in
// the middle. It has to vanish at both ends or the page would not be the
// window at rest — and because progress is easeInOutCubic, whose slope is
// zero at both ends, the hump leaves and returns with zero slope too.
function plHump(p) { return p > 0 && p < 1 ? 4 * p * (1 - p) : 0; }

// ON ITS WAY SOMEWHERE — the only bodies the page makes room for. A journey is
// not enough on its own: `steer` refuses to end one for a body that is
// `leaving` or that keeps a `table`, and a void keeps its table for good once
// a scene has opened it. Progress is the truthful clock. And the path must go
// somewhere: `retireBody` gives a body a path from where it stands to where it
// stands, and a bystander is re-seated where it already was. Neither is
// travelling, and neither needs room to do it.
function plTravelling(b) {
  if (b.isSelf || b.leaving) return false;
  if (!b.journey || b.progress >= 1) return false;
  const p = b.path;
  return !!p && Math.hypot(p.ex - p.sx, p.ey - p.sy) > 1;
}

// A DISSECTION THE DIAGRAM CAN ACTUALLY DRAW.
//
// A vertical seam between two cells is plumb only when their two seeds share a
// y, and a seed sits at its rectangle's centre — so a vertical seam is
// realizable only when its two rectangles have IDENTICAL y-extents, not merely
// a shared cut. Horizontal seams are the same with the axes swapped. The
// dissections that satisfy that everywhere are the GRIDS: unequal rows and
// unequal columns are fine, but every cell in a row must share the row's top
// and bottom, and every cell in a column its left and right.
//
// `guillotine` (hive.html:749) satisfies it only by accident. Split a region
// into A|B and then cut A across, and A1 and A2 each share a vertical seam
// with B while spanning different heights; no weight can straighten what that
// produces, because a weight slides an edge along its normal and never rotates
// it. Measured on the templates themselves, the share of seam LENGTH that is
// realizable as drawn:
//
//     bento 0.826    sidebar 0.622    hero 0.409    frame 0.326
//
// which is exactly the order in which the scenes look rectangular. Bento leads
// because its dissection happens to align, not because anything asked it to.
//
// `quilt` asks. It picks the grid whose cells are nearest square and whose
// surplus is smallest, cuts unequal rows and columns from a salt so it is not
// graph paper, and hands the surplus slots back as whitespace rather than
// stretching a row to swallow them — a row of a different width would break
// the very alignment the grid is for.
function quilt(rect, n, salt) {
  const x0 = rect[0], y0 = rect[1], x1 = rect[2], y1 = rect[3];
  const w = x1 - x0, h = y1 - y0;
  if (n <= 1 || w < 1 || h < 1) return [rect.slice()];
  // A grid that gives every cell a whole lattice unit is preferred, because
  // the jittered cut below needs one to work with. But WHEN NONE FITS THE
  // MARK MUST NOT SILENTLY LAPSE: at 12 columns the sidebar is 5 units wide,
  // so a page short enough for 4 or 5 rows holds at most 20 or 25 whole
  // slots while the roster goes to 30. Falling back to `guillotine` there
  // put the fanned column back exactly — measured identical to Bellows to
  // four decimals at 1440x620 with 24 elements, 0.3505 against 0.3505. A
  // sub-unit row is still a row: every cell in it shares one y-extent, which
  // is the whole of what makes a seam drawable plumb. Integers were never
  // the requirement, only `guillotine`'s habit.
  let best = null, loose = null;
  for (let cols = 1; cols <= n; cols++) {
    const rows = Math.ceil(n / cols);
    const ar = (w / cols) / (h / rows);
    const score = (cols * rows - n) * 0.9 + Math.abs(Math.log(ar));
    const cand = { cols: cols, rows: rows, score: score };
    if (cols <= w && rows <= h) { if (!best || score < best.score) best = cand; }
    else if (!loose || score < loose.score) loose = cand;
  }
  best = best || loose;
  if (!best) return guillotine(rect, n, salt);
  const cuts = (a, len, k, sa) => {
    const at = [a];
    if (k <= 1) { at.push(a + len); return at; }
    // Less than a lattice unit per cell: cut evenly. The jitter below rounds
    // to whole units and would collapse every cell but the last onto 1.
    if (len / k < 1) {
      for (let i = 1; i < k; i++) at.push(a + len * i / k);
      at.push(a + len);
      return at;
    }
    let left = len;
    for (let i = 0; i < k - 1; i++) {
      const want = left / (k - i), jitter = 0.78 + 0.44 * hash01(i + 1, sa);
      const take = Math.max(1, Math.min(left - (k - 1 - i), Math.round(want * jitter)));
      at.push(at[at.length - 1] + take); left -= take;
    }
    at.push(a + len);
    return at;
  };
  const xs = cuts(x0, w, best.cols, salt + 11), ys = cuts(y0, h, best.rows, salt + 29);
  const all = [];
  for (let r = 0; r < best.rows; r++) for (let c = 0; c < best.cols; c++) all.push([xs[c], ys[r], xs[c + 1], ys[r + 1]]);
  return all;
}

const scenes = {''')

# ------------------------------------------------------------- one kind of body
replace('''  updateCrystal(b, t) {
    if (b.table && b.table.mode === 'open') return;      // an opening void reads its vacators' clocks''',
'''  updateCrystal(b, t) {
    // ONE SPECIES. A rectangle is a DESTINATION — a place to travel to and an
    // area to claim — never a category the body belongs to.
    if (this.depth === 0) { b.crystal = 0; b.pin = 0; return; }
    if (b.table && b.table.mode === 'open') return;      // an opening void reads its vacators' clocks''')

# ----------------------------------------------------------- a journey that ends
replace('        if (!b.rect && !b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;',
        '        if (!b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;')

# ------------------------------------------------------------- the breathing domain
replace('  domainPts() {', '''  // How much bigger than the window the ground has to be: exactly enough to
  // cover what has been LENT to the travellers this frame, and nothing else.
  //
  // The first cut sized the domain from the page's WHOLE claim — g = SUM(all
  // claims) / (COLS*ROWS) — which is a prettier identity and the wrong rule.
  // A claim total drifts above the window for reasons that have nothing to do
  // with travel: a void dissolving hands its area back faster than the bodies
  // taking it give up their own, and a free body's rest size carries a 5%
  // breathing wobble (easeClaims, hive.html:2209). Measured, that opened a rim
  // of up to 61 px in the FLOCK, where nothing has a path at all and no room
  // is needed — 230,028 px2 of ink outside the window across 70% of its
  // frames. A buffer that opens when nobody is travelling is not a buffer.
  //
  // Sized from the loan instead, the rim is zero unless somebody is on their
  // way somewhere, and it is exactly as deep as their journeys have asked for.
  plG() {
    if (this.depth !== 0) return 1;
    const base = this.COLS * this.ROWS;
    if (!(base > 0)) return 1;
    return Math.max(1, Math.min(1 + PL_CAP, 1 + (this.plLoan || 0) / base));
  }

  // the rim, in px, uniform on all four sides: (W + 2m)(H + 2m) = g*W*H
  plM() {
    const g = this.plG();
    if (g <= 1 + PL_EPS) return 0;
    const W = this.W, H = this.H, s = W + H;
    return (-s + Math.sqrt(s * s + 4 * (g - 1) * W * H)) / 4;
  }

  plBox() {
    const m = this.plM();
    return [-m, -m, this.W + m, this.H + m];
  }

  domainPts() {
    if (this.depth === 0 && !this.domainPolyActive()) {
      const [x0, y0, x1, y1] = this.plBox();
      return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    }
    return this.plOldDomainPts();
  }

  plOldDomainPts() {''')

# A seed may stand anywhere on the ground, and the ground is the window until
# somebody is travelling. ONE RULE FOR EVERY BODY: Murmur needed a per-body seed
# box — the window for a settled body, the ring for a traveller — because its
# ring existed at full size the moment anything moved, and a settled body left
# free to drift would have gone and sat in it. Here the rim is only ever as
# deep as the travel demands and returns to zero, so a body that wanders out is
# carried back by the domain itself, continuously.
replace('''      b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
      b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''      {
        const box = this.plBox();
        b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
        b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));
      }''')
replace('''        b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
        b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''        {
          const box = this.plBox();
          b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
          b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));
        }''')

# ------------------------------------------------------------------- the swell
replace('/* --------------------------------------------------------------- START */', '''
// THE SWELL — who the new ground belongs to.
//
// Growing the domain on its own would enlarge every cell in proportion, which
// is a zoom and relieves nothing. A body on its way somewhere needs room it
// does not need at rest: its seed is between two configurations and the area
// it is owed does not fit the shape it is passing through. Left alone it takes
// that room from whoever it is passing, and the crushed neighbour takes it
// back the instant the traveller has gone — the shove and recoil that reads as
// a spring uncoiling.
//
// Here a traveller's claim is raised instead, on a hump that is exactly zero
// at both ends of its journey, and because the domain is sized from the TOTAL
// of the claims, the ground to cover it is created rather than taken. Every
// settled cell keeps exactly claim * PW * PH throughout. Several travellers
// are accommodated at once, out of one page, and the whole of it drains as the
// last one lands.
//
// The raise is capped as a share of the window, so a scene that moves
// everything at once borrows what there is and no more, and the rim stays
// inside PL_CAP.
// EVERY SEAM GETS A PAIR OF SITES, ONE EACH SIDE, ALIGNED ACROSS IT.
//
// A power cell's edge against a neighbour is perpendicular to the line joining
// their two SITES — a weight slides that edge along its normal and can never
// rotate it (computeDiagram, hive.html:225). So the direction of every edge on
// the page is decided by where the seeds are, and by nothing else. One seed
// per body, at its rectangle's centre, is what Bellows has, and it makes a
// seam plumb only by luck.
//
// The luck is measurable. Reading the templates' own rectangles, the share of
// seam LENGTH whose two bodies are already aligned across it (equal y for a
// vertical seam, equal x for a horizontal one), at rest:
//
//     scene    aligned <0.1   0.1-0.3   0.3-1.0   >= 1.0   cells wholly on axis
//     bento       0.826        0.000     0.065    0.109           0.667
//     sidebar     0.622        0.000     0.189    0.189           0.000
//     hero        0.409        0.000     0.114    0.477           0.100
//     frame       0.326        0.000     0.087    0.587           0.250
//
// Two things follow. The share already aligned is exactly the ranking of how
// rectangular each scene looks — bento leads because its dissection happens to
// align, not because anything asked it to. And the distribution is BIMODAL:
// there is nothing at all between 0.1 and 0.3 in any scene, so a seam is
// either already true or badly out, and no small nudge of the seeds can help
// because there are no near misses to fix.
//
// Nor can the seeds simply be solved for. A vertical seam is realizable only
// when its two rectangles have IDENTICAL y-extents — not merely a shared cut —
// so the realizable dissections are the grids, and a guillotine is not one.
// Moving a seed to satisfy a constraint also drags its cell off the slot the
// template gave it, because a seed's position sets its cell's position as well
// as its edges' directions.
//
// So give a body MORE THAN ONE SITE. The renderer already merges every site a
// body owns into one leaf with one dressing and one gap (collectLeaves,
// hive.html:3295-3313), and a field has used many sites since the reference
// was written. For each seam a body has, it takes a site placed at its own
// centre line along one axis and the SEAM'S midpoint along the other:
//
//     a vertical seam at x = c, spanning y in [y0, y1]
//         the body on the left  takes a site at (its own cx, (y0+y1)/2)
//         the body on the right takes a site at (its own cx, (y0+y1)/2)
//
// The pair now shares a y, so the edge between them is exactly vertical, and
// it stays vertical whatever the weights do — which is the point, because the
// weights are what carry the areas and they are not free. Horizontal seams are
// the same with the axes swapped. Nothing is declared a rectangle; the sites
// are placed where a rectangle is what the diagram HAS to draw.
//
// The sites travel with the body. Each is stored as an OFFSET from the body's
// own centre, so during a journey the whole group follows the seed along its
// path and the pairs come back into alignment exactly as the bodies arrive.
function plRectsKey(bodies) {
  let k = '';
  for (const b of bodies) { const r = b.formRect || b.rect; if (r) k += b.id + ':' + r.join(',') + ';'; }
  return k;
}

Hive.prototype.plSeamSites = function() {
  if (this.depth !== 0 || !PL_SEAM_SITES) return;
  const E = 1e-6, PW = this.PW, PH = this.PH;
  const live = [];
  for (const b of this.bodies) if (!b.isSelf && (b.formRect || b.rect)) live.push(b);
  const key = plRectsKey(live);
  if (this.plKey !== key) {
    this.plKey = key;
    // ONE SITE EACH, then whitespace collects one more per cell it borders.
    // Content keeps exactly one site and therefore stays CONVEX, which is what
    // holds the three-to-nine corner budget. Giving content a site per seam
    // was tried and does straighten seams — sidebar's axis-aligned share goes
    // 0.700 -> 0.842 — but the union of several power cells is not convex and
    // the census collapses with it: over-budget 0.000 -> 0.662, worst cell 9
    // corners -> 36. That is the flubber four marks were spent removing,
    // bought back for a straighter seam. A void draws nothing, so its own cell
    // may be any shape at all, and only it may have more than one.
    for (const b of live) b.plOff = [[0, 0]];
    const over = (a0, a1, b0, b1) => Math.min(a1, b1) - Math.max(a0, b0) > E;
    for (const v of live) {
      if (!v.isVoid) continue;
      const rv = v.formRect || v.rect;
      const cv = [(rv[0] + rv[2]) / 2, (rv[1] + rv[3]) / 2];
      const off = [], share = [];
      for (const c of live) {
        if (c === v || c.isVoid) continue;
        const rc = c.formRect || c.rect;
        // The whitespace takes a site at the cell's OWN centre line, so the
        // pair is level across the seam and the edge it draws is plumb. Its
        // CLAIM is the band it ought to own — the cell's span along the
        // boundary, times the void's depth. That matters as much as the
        // position: a power bisector sits at the midpoint of two sites only
        // when their weights agree, and the solver sets weights to hit areas.
        // Give each site the area of its own band and the area constraint puts
        // the boundary exactly on the cell's edge; give them equal shares, as
        // the first cut did, and a long cell's edge breaks into the facets of
        // whichever neighbours' sites reach into it.
        if (Math.abs(rc[2] - rv[0]) < E && over(rc[1], rc[3], rv[1], rv[3])) {
          off.push([0, (rc[1] + rc[3]) / 2 - cv[1]]); share.push((rc[3] - rc[1]) * (rv[2] - rv[0]));
        } else if (Math.abs(rc[0] - rv[2]) < E && over(rc[1], rc[3], rv[1], rv[3])) {
          off.push([0, (rc[1] + rc[3]) / 2 - cv[1]]); share.push((rc[3] - rc[1]) * (rv[2] - rv[0]));
        } else if (Math.abs(rc[3] - rv[1]) < E && over(rc[0], rc[2], rv[0], rv[2])) {
          off.push([(rc[0] + rc[2]) / 2 - cv[0], 0]); share.push((rc[2] - rc[0]) * (rv[3] - rv[1]));
        } else if (Math.abs(rc[1] - rv[3]) < E && over(rc[0], rc[2], rv[0], rv[2])) {
          off.push([(rc[0] + rc[2]) / 2 - cv[0], 0]); share.push((rc[2] - rc[0]) * (rv[3] - rv[1]));
        }
      }
      if (off.length) { v.plOff = off; v.plShare = share; }
    }
  }
  for (const b of live) {
    const off = b.plOff;
    if (!off || !off.length) continue;
    if (b.subs.length !== off.length) b.subs = off.map(() => ({ body: b, x: 0, y: 0, w: 0, claim: 0, live: false }));
    const sh = b.plShare && b.plShare.length === off.length ? b.plShare : null;
    let tot = 0; if (sh) for (const q of sh) tot += q;
    for (let i = 0; i < off.length; i++) {
      const sub = b.subs[i];
      sub.x = b.x + off[i][0] * PW;
      sub.y = b.y + off[i][1] * PH;
      sub.claim = sh && tot > 0 ? b.claim * (sh[i] / tot) : b.claim / off.length;
    }
  }
};

const plOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  plOldPlace.call(this);
  this.plSeamSites();
  if (this.depth !== 0 || PL_SWELL <= 0) return;
  // THE SWELL IS A STATE, NOT A FUNCTION OF PROGRESS — and it has to be, for
  // the one case the hump cannot describe.
  //
  // A journey's hump is continuous while that journey runs. But `seatBody`
  // resets `b.progress` to 0 when a body is RETARGETED, which is what happens
  // every time a scene is chosen before the last one has settled. Read straight
  // off progress, a body mid-journey at hump 0.9 drops to hump 0 in one frame,
  // the loan collapses with it, and the rim steps — measured, 33.68 px to 0 in
  // a single frame on an interrupt 30 frames into a change. That is precisely
  // the discontinuity this mark exists to remove, reached by another road, and
  // the five-clock gate never saw it because it waits 6.6 s between clicks.
  //
  // (What it is NOT: the visible jump. A retarget moves the page about 300 px
  // in that frame whatever the rim does — Murmur, whose ring does not change
  // at all, moves 298.5 px against Plumb' 304.2. The rim collapse is worth
  // fixing because it breaks the mark's own invariant and because it drops the
  // buffer at the exact moment the page needs it, not because it is the bump.)
  //
  // So each body carries its swell and the swell is rate-limited. It can be
  // asked for anything by anything; it can only ever get there smoothly. The
  // domain is sized from what was actually applied, so the identity
  // tgt = claim * PW * PH survives the limiter exactly.
  const dt = Math.max(0, Math.min(0.25, this.t - (this.plT === undefined ? this.t : this.plT)));
  this.plT = this.t;
  const step = PL_SLEW > 0 ? PL_SLEW * dt : Infinity;
  const rows = [];
  let want = 0;
  for (const b of this.bodies) {
    if (b.isSelf || b.isVoid) continue;
    let own = 0; for (const sub of b.subs) own += sub.claim;
    const target = (own > 0 && plTravelling(b)) ? PL_SWELL * plHump(b.progress) : 0;
    const cur = b.plSwell || 0;
    const d = target - cur;
    b.plSwell = Math.abs(d) <= step ? target : cur + Math.sign(d) * step;
    if (b.plSwell > PL_EPS && own > 0) { rows.push({ b, own }); want += b.plSwell * own; }
    else if (b.plSwell < PL_EPS) b.plSwell = 0;
  }
  this.plLoan = 0;
  if (want <= 0) return;
  const cap = PL_CAP * this.COLS * this.ROWS;
  const k = want > cap ? cap / want : 1;
  for (const r of rows) {
    const g = 1 + r.b.plSwell * k;
    for (const sub of r.b.subs) sub.claim *= g;
  }
  this.plLoan = want * k;
};

/* --------------------------------------------------------------- START */''')

# THE CACHE MUST SEE THE RIM. solveMain's signature carries this.W/this.H and a
# domainSig that is EMPTY whenever the domain is a rectangle, so a domain that
# changes size while the window does not would otherwise be invisible to it and
# a stale solve would be served. Quantised to a tenth of a pixel.
replace("""    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|';""",
        """    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|B' + (this.plM() * 10 | 0) + '|';""")
replace("""    let s = this.domainPolyActive() ? this.domainSig : '';""",
        """    let s = (this.domainPolyActive() ? this.domainSig : '') + 'P' + (this.plM() * 10 | 0);""")

# --- the sidebar asks for a grid, because a grid is what can be drawn -------
replace('  sidebar(C, R, n) {\n    const c = Math.max(2, Math.round(C * 0.45));\n    return { content: guillotine([0, 0, c, R], n, 3), voids: [[c, 0, C, R]] };\n  },',
        '  sidebar(C, R, n) {\n    const c = Math.max(2, Math.round(C * 0.45));\n    const all = quilt([0, 0, c, R], n, 3);\n    // the surplus slots are whitespace, not stretched neighbours\n    return { content: all.slice(0, n), voids: all.slice(n).concat([[c, 0, C, R]]) };\n  },')

# development only: PANE_VARS="PL_SWELL=0" builds a variant
for kv in filter(None, os.environ.get('PANE_VARS', '').split(',')):
    kk, vv = kv.split('=', 1)
    pat = re.compile(r'^(const %s = )([^;]+);' % re.escape(kk), re.M)
    n = len(pat.findall(s))
    if n != 1:
        raise SystemExit(f'PANE_VARS: {kk} found {n} times')
    s = pat.sub(lambda m: m.group(1) + vv + ';', s)

# ============================================================ PANE: the pane
# Whitespace draws no card, so its cell may be an exact rectangle without
# giving cards a second species. The reference can already do that - a wall is
# an exact rect cut from the auction ground - but a wall that switches on is a
# SKIP, measured at 29.7% of the screen repainted in one frame, because the
# ground's convex decomposition re-cuts and every card is re-solved on a domain
# that changed shape at once.
#
# So the cut GROWS. Its rect is the void's own rectangle scaled about its
# centre by s, so the area taken out of the ground is exactly s^2 * rectArea,
# and the void's claim is set to (1 - s^2) * rectArea in the same frame.
# solveWeights normalises tgt[i] = claim[i] * domainArea / sum(claims), so
# claims are SHARES: what leaves the domain must leave the sum of claims in
# lockstep or every other cell's target area jumps. It does, identically, at
# every value of s:
#     sum(cards) + void  =  (page - rect) + (1 - s^2) * rect  =  page - s^2*rect  =  domainArea
# At s = 0 this is Plumb exactly. At s = 1 the whitespace is its rectangle and
# claims nothing, because it IS the part of the page the auction does not own.

# ---------------------------------------------- never a blended hole
replace("""      // A hole at crystal 0 does not close until its shape is the cell the""",
"""      // A void is a rectangle or an ordinary bidder, never a blended hole: a
      // hole is a many-vertex polygon cut out of the ground, and the ground's
      // convex decomposition is combinatorial - it re-cuts in one frame.
      if (b.isVoid) { b.holeCore = null; continue; }
      // A hole at crystal 0 does not close until its shape is the cell the""")

# ---------------------------------------------- the pane grows, it never switches
replace("""  computeWalls() {
    this.walls = []; this.holes = [];
    for (const b of this.bodies) {
      b.wall = null; b.hole = null; b.holeExtra = [];
      const r = b.formRect;
      if (b.isSelf || !r) { b.holeCore = null; continue; }
      const rect = [r[0] * this.PW, r[1] * this.PH, r[2] * this.PW, r[3] * this.PH];""",
"""  computeWalls() {
    this.walls = []; this.holes = [];
    for (const b of this.bodies) {
      b.wall = null; b.hole = null; b.holeExtra = [];
      // THE PANE, handled before the formRect guard: a void that is retiring
      // has had its rect nulled already (retireBody, hive.html:1706), and if
      // the wall simply stopped being drawn on that frame it would vanish at
      // full size - which is the same switch, measured at 400.
      if (b.isVoid && this.depth === 0 && PN_PANE) {
        if (b.formRect) b.pnRect = b.formRect;
        const rr = b.formRect || b.pnRect;
        // THE PANE FIRMS ON THE LEDGER'S OWN CLOCK. An opening void already
        // knows how much of its rectangle it owns: tb.f is the share of the
        // bodies vacating it that have landed, and easeClaims gives it a claim
        // of a*f. The pane takes f^2 of that as wall and leaves f - f^2 as
        // cell, so wall + cell is a*f at EVERY instant and nothing switches:
        // at f = 0 there is no wall, at f = 1 the whitespace is all wall and
        // claims nothing, and ds/df -> 0 at the start, so the first frame of
        // the cut moves almost nothing. A closing or retiring void melts back
        // on the rate limiter, because it has no f to read.
        // THE PANE FIRMS ONLY ONCE THE WHITESPACE OWNS ITS RECTANGLE. While a
        // void is still opening it does not: cards are still vacating it, and
        // easeClaims gives it only a*f. Cutting a band out of it then makes
        // its claim and its geometry disagree, the neighbours flood the part
        // it has not paid for, and the page fills with slivers - measured,
        // sliverShare 0.317 against Plumb's 0.106. So the pane waits for the
        // ledger to close, and firms on its own eased clock.
        //   u is rate-limited; s eases out of u with ds/du = 0 at u = 0, so
        // the frame the cut opens moves a fraction of a percent of the
        // rectangle rather than the 4.8% a bare ramp took, which read as 57.
        const tb = b.table;
        const dt = Math.max(0, Math.min(0.1, this.lastDt || 0));
        const want = (b.leaving || !b.formRect) ? 0
                   : (tb && tb.mode === 'close') ? 0
                   : (tb && tb.mode === 'open' && !(tb.f >= 0.999)) ? 0 : 1;
        const u0 = b.pnU === undefined ? 0 : b.pnU;
        const step = PN_SLEW * dt;
        b.pnU = want > u0 ? Math.min(1, u0 + step) : Math.max(0, u0 - step);
        const u = b.pnU;
        b.pnS = PN_CAP * u * u * (3 - 2 * u);
        b.holeCore = null;
        // THE PANE IS ALWAYS THERE, EVEN AT NOTHING. domainPieces cuts the
        // ground into convex pieces the instant a wall EXISTS, at any width at
        // all, and every body is then re-emitted one loop per piece. That flip
        // is combinatorial, so no ramp can smooth it - measured identical at
        // sweep rates from 0.35 to 3.0. Keeping a floor-width pane from the
        // first frame means the decomposition has the same structure always,
        // and only the extent inside it moves.
        if (b.pnS > PN_EPS && rr) {
          const px0 = rr[0] * this.PW, py0 = rr[1] * this.PH, px1 = rr[2] * this.PW, py1 = rr[3] * this.PH;
          b.wall = [px0, py0, px0 + (px1 - px0) * b.pnS, py1];
          this.walls.push(b);
        }
        continue;
      }
      const r = b.formRect;
      if (b.isSelf || !r) { b.holeCore = null; continue; }
      const rect = [r[0] * this.PW, r[1] * this.PH, r[2] * this.PW, r[3] * this.PH];
""")

# ---------------------------------------------- the claim leaves in lockstep
replace("""  this.plSeamSites();""",
"""  this.plSeamSites();
  // What has been taken out of the ground must leave the sum of claims in the
  // same frame: claims are shares, not areas (solveWeights, hive.html:634).
  if (this.depth === 0 && PN_PANE) {
    for (const b of this.bodies) {
      // A RETIRING VOID TOO. Its wall is still melting, so placeSeeds still
      // sees b.wall and still zeroes its seed; if the claim is not restored
      // here the band it has not yet given back goes unclaimed for the whole
      // melt, and the cards pour into it. Its rectangle is gone by then
      // (retireBody, hive.html:1706) so the pane's remembered one stands in.
      if (!b.isVoid || b.pnS === undefined || b.pnS <= PN_EPS) continue;
      const r = b.formRect || b.pnRect;
      if (!r) continue;
      // ON THE SEED, NOT ON THE BODY. placeSeeds ends with
      //     s.claim = b.wall ? 0 : b.claim * hover;          (hive.html:2228)
      // so the frame the pane's band first appears, the whitespace's seed is
      // dropped from the auction ENTIRELY - not by the width of the band, but
      // outright - and the cards flood the whole rectangle rather than the
      // sliver that was actually taken from them. That is the 28354 -> 66521
      // px2 card, and it is why a SLOWER sweep measured worse: the mismatch
      // simply lasted longer. What the pane has taken as wall comes out of
      // what the void owns this frame; the rest it still bids for.
      const a = Math.max(0, (r[2] - r[0]) * (r[3] - r[1]));
      const sub = b.subs && b.subs[0];
      if (sub) {
        sub.claim = Math.max(CLAIM_MIN, b.claim - b.pnS * a);
        const x0 = r[0] + (r[2] - r[0]) * b.pnS;
        // the SEED only. b.x/b.y are the body's place in the physics - steer,
        // separate and its path all read them - and writing them here moved
        // the flock, a scene with no whitespace in it at all, by 100 px.
        //
        // AND IT ARRIVES, IT DOES NOT SNAP. placeSeeds puts the seed at b.x
        // every frame, which is the body's physics position and not the middle
        // of the band; jumping it there on the frame the pane engages read as
        // 13.5 at EVERY sweep rate, which is what a rate-independent step
        // looks like. It walks in on the pane's own eased clock instead.
        // Straight to the middle of the band, not eased toward it: the seed's
        // place is what MAKES the remainder the band. Easing it leaves the
        // seed off-centre while the claim already assumes it is there, and the
        // cell that results is crushed - iqMin 0.245 -> 0.012, measured.
        sub.x = (x0 + r[2]) * 0.5 * this.PW;
        sub.y = (r[1] + r[3]) * 0.5 * this.PH;
      }
    }
  }""")

# ------------------------------------------ a field's frame is its WHOLE cell
# The ground's convex decomposition is discrete: the frame a wall exists at any
# width at all, domainPieces cuts the ground into convex pieces and every body
# is re-emitted one loop per piece. The cell's AREA does not move across that
# frame - measured identical to the pixel - but `cellPoly` hands a field only
# its LARGEST loop, so a field fitted to a fragment teleports its whole inner
# world. Fit to the extent of ALL the loops and the re-cut stops being visible.
replace("""      const cell = this.cellPoly(b);
      if (!cell) { b.hive.dormant = true; continue; }
      // the frame: the cell's box; the cell is exactly a rectangle when locked
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const p of cell) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); }""",
"""      const cell = this.cellPoly(b);
      if (!cell) { b.hive.dormant = true; continue; }
      // the frame: the cell's box; the cell is exactly a rectangle when locked
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      const ext = (b.wall || !b.loops || !b.loops.length) ? [cell] : b.loops;
      for (const lp of ext) for (const p of lp) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1]); }""")

OUT = Path(os.environ.get('PANE_OUT', str(ROOT / 'pane.html')))
OUT.write_text(s)
if os.environ.get('PANE_OUT'):
    print('Built variant', OUT)
    raise SystemExit(0)

# --- the gallery card -------------------------------------------------------
index_path = ROOT / 'index.html'
index = index_path.read_text()
card = '''
        <!-- PANE -->
        <a href="pane.html" class="version-card latest">
            <h2>Pane</h2><span class="latest-flag">Latest</span>
            <span class="mk">Pane</span>
            <span class="tag preview">Tested experiment</span>
            <p>The whitespace, which no mark before this one ever measured. Plumb drew the cards on axis and left the empty space a radial fan &mdash; a third of the frame layout&rsquo;s hole sat somewhere other than where the layout put it. Here the whitespace is cut from the ground as a band that sweeps in once the space is its own, and the claim it gives up leaves the auction in the same frame, so nothing else changes size. It is not the smooth one: read Plumb beside it.</p>
            <ul>
                <li>The sidebar&rsquo;s whitespace becomes a true rectangle; the frame&rsquo;s goes from 31% wrong to 2%</li>
                <li>Still one kind of card &mdash; every card a single-seed bidder, no card ever a wall</li>
                <li>Corner budget intact and slivers better than Plumb&rsquo;s at every clock</li>
                <li>And it hitches: 3 to 8 stepped frames where Plumb has none, worst on a fast display</li>
            </ul>
        </a>
        <!-- /PANE -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
IS_LATEST = True   # only the newest mark wears the flag
if not IS_LATEST:
    card = card.replace(' latest"', '"').replace('<span class="latest-flag">Latest</span>', '')
own = re.compile(r'\n?[ \t]*<!-- PANE -->.*?<!-- /PANE -->[ \t]*\n?', re.S)
index = own.sub(lambda m: card, index, count=1) if own.search(index) else index.replace(anchor, anchor + card, 1)
index_path.write_text(index)
print('Built pane.html from reference blob', EXPECTED)
print('Pane SHA256', hashlib.sha256(s.encode()).hexdigest())
