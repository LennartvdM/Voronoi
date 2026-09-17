"""Build the Plumb mark: a layout that asks for what the diagram can draw.

Bellows is the best the marks have been — the owner's words, after
twenty-nine of them: "the first time ... where the transitions feel smooth.
Where the user doesn't get that frantic or rushed feeling." It pays for that
with rectangles. Astra I drew them exactly, but only by cutting WALLS out of
the ground, and walls bring the half-plane blend, and the blend is the flubber
that four marks were spent removing. Bellows has no walls and no flubber, and
its sidebar is a skewed fan.

Except that its BENTO is not. The owner spotted it: "Bellows does seem to have
the capacity to create rectangles sometimes. It's just not using it in the
layouts where you'd expect them."

WHY, EXACTLY. A power cell's edge against a neighbour is perpendicular to the
line joining their two SITES. A weight slides that edge along its normal; it
can never rotate it (computeDiagram, hive.html:225). A seed sits at its
rectangle's centre, so a VERTICAL seam is drawn plumb only when its two
rectangles have IDENTICAL y-extents — not merely a shared cut — and a
horizontal seam likewise. The dissections that satisfy that everywhere are the
GRIDS: unequal rows and unequal columns are fine, but every cell in a row must
share the row's top and bottom.

`guillotine` (hive.html:749) satisfies it only by accident. Split a region into
A|B and then cut A across, and A1 and A2 each share a vertical seam with B
while spanning different heights. Measured on the templates themselves, the
share of seam LENGTH realizable as drawn, against what the scene looks like:

    scene     realizable seam   axis-aligned edge   cells that are rectangles
    bento          0.826              0.932                  0.667
    sidebar        0.622              0.700                  0.000
    hero           0.409              0.493                  0.100
    frame          0.326              0.617                  0.250

The first column predicts the third. Bento leads because its dissection happens
to align, not because anything asked it to.

SO THE TEMPLATE ASKS. `quilt` picks the grid whose cells are nearest square and
whose surplus is smallest, cuts unequal rows and columns from a salt so it is
not graph paper, and hands the surplus slots back as WHITESPACE rather than
stretching a row to swallow them — a row of a different width would break the
very alignment the grid is for. The sidebar asks for a quilt; every seam it
produces is realizable, and the auction draws it with no wall, no blend, and
one site per body.

    sidebar    axis 0.700 -> 0.848    cells that are rectangles 0.000 -> 0.556

and nothing else moves: over-budget stays 0.0000, the worst cell stays at nine
corners, the worst frame stays at 2.7 times its neighbours with no spike frame
at any clock, and the page still rests at 100% with its buffer drained.

THREE ROUTES THAT DID NOT WORK, measured rather than argued, because each is
the obvious next idea and each is a trap:

  A LATTICE OF WHITESPACE SITES. A content cell then borders two or three of
  them at different heights and its edge breaks into that many facets. Axis
  alignment barely moved (0.700 -> 0.724) and the page looked ragged.

  NUDGING THE SEEDS into alignment. There is nothing to nudge: the seam
  misalignment is BIMODAL. Length-weighted, no scene has ANY seam between 0.1
  and 0.3 lattice cells out — they are either true already or a whole cell
  wrong. And a seed that moves drags its cell off the slot the template gave
  it, because a seed's position sets its cell's position as well as its edges'
  directions.

  A SITE PER SEAM, paired across it. This straightens seams as advertised —
  sidebar 0.700 -> 0.842 — and destroys the corner budget doing it: the union
  of several power cells is not convex, and over-budget goes 0.000 -> 0.662
  with the worst cell at 36 corners. That is the flubber, bought back for a
  straighter edge. Convex cells and arbitrary plumb seams cannot both be had.

And one that worked and was still refused: see PL_SEAM_SITES.

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


replace('<title>Hive</title>', '<title>Plumb — Hive</title>')
replace('&larr; Back</a>', '&larr; Back · Plumb</a>')

# --------------------------------------------------------------- the constants
replace('const scenes = {', '''// ============================================================ PLUMB
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

# development only: PLUMB_VARS="PL_SWELL=0" builds a variant
for kv in filter(None, os.environ.get('PLUMB_VARS', '').split(',')):
    kk, vv = kv.split('=', 1)
    pat = re.compile(r'^(const %s = )([^;]+);' % re.escape(kk), re.M)
    n = len(pat.findall(s))
    if n != 1:
        raise SystemExit(f'PLUMB_VARS: {kk} found {n} times')
    s = pat.sub(lambda m: m.group(1) + vv + ';', s)

OUT = Path(os.environ.get('PLUMB_OUT', str(ROOT / 'plumb.html')))
OUT.write_text(s)
if os.environ.get('PLUMB_OUT'):
    print('Built variant', OUT)
    raise SystemExit(0)

# --- the gallery card -------------------------------------------------------
index_path = ROOT / 'index.html'
index = index_path.read_text()
card = '''
        <!-- PLUMB -->
        <a href="plumb.html" class="version-card latest">
            <h2>Plumb</h2><span class="latest-flag">Latest</span>
            <span class="mk">Plumb</span>
            <span class="tag preview">Tested experiment</span>
            <p>Bellows, drawn on axis. The edge between two cells is always perpendicular to the line joining their seeds, so a weight can slide an edge but never turn it: every angle on the page is decided by where the seeds sit, and a seam is drawable plumb only where the two cells it parts have the same extent along it. The sidebar's old template did not, so it fanned. This one lays its cells on a grid and gives the leftovers back as whitespace.</p>
            <ul>
                <li>Rectangles where a person expects rectangles, with no wall and no second kind of cell</li>
                <li>The sidebar goes from no true rectangle at all to more than half of them</li>
                <li>Bellows' smoothness kept intact — the skip does not come back</li>
                <li>plumb.js measures angle weighted by edge length, which a corner count cannot</li>
            </ul>
        </a>
        <!-- /PLUMB -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
IS_LATEST = True   # only the newest mark wears the flag
if not IS_LATEST:
    card = card.replace(' latest"', '"').replace('<span class="latest-flag">Latest</span>', '')
own = re.compile(r'\n?[ \t]*<!-- PLUMB -->.*?<!-- /PLUMB -->[ \t]*\n?', re.S)
index = own.sub(lambda m: card, index, count=1) if own.search(index) else index.replace(anchor, anchor + card, 1)
index_path.write_text(index)
print('Built plumb.html from reference blob', EXPECTED)
print('Plumb SHA256', hashlib.sha256(s.encode()).hexdigest())
