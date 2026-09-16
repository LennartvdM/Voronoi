"""Build the Bellows mark: the overflow buffer made continuous.

Murmur's margin is a switch. jolt.js, measuring each frame against the four
frames on either side of it, finds exactly two spikes per transition scene and
they are the first frame and the last:

    scene     opening frame   closing frame    neighbours   worst spike
    bento         33.0 px         31.4 px          1 - 5 px        10x
    hero          30.0 px        184.8 px          1 - 5 px        50x
    sidebar      176.7 px        131.3 px          1 - 5 px        59x
    frame         86.1 px        182.0 px          1 - 4 px        61x

muOpen() is true on the first and false on the last. Nothing between them
exceeds twice its neighbours, and Bleed — whose margin is permanently open,
and therefore never switches — has no spike at all. The switch is the skip.

BELLOWS REMOVES THE SWITCH WITHOUT REMOVING THE BUFFER, by making the domain
itself the buffer and letting it grow from nothing.

  THE DOMAIN IS ALWAYS EXACTLY AS BIG AS WHAT THE PAGE HAS ASKED FOR.

`solveWeights` (hive.html:634) hands each body

    tgt_i = claim_i * domainArea / SUM(claims)

so claims are SHARES, not areas, and the partition is re-derived exactly every
frame at any domain size. Choose the domain area to be the page's total claim
in lattice units:

    g = clamp( 1 + loan / (COLS*ROWS), 1, 1 + BW_CAP )     // loan: see THE SWELL
    domainArea = g * W * H
    m = ( -(W+H) + sqrt( (W+H)^2 + 4*(g-1)*W*H ) ) / 4     // (W+2m)(H+2m) = g*W*H

and the identity falls out: tgt_i = claim_i * W*H/(COLS*ROWS) = claim_i * PW*PH,
for every body, at every value of g, as long as the unlent claims sum to the
window — which is what the reference normalises them to. Three things follow,
and they are the whole mark:

  1. AT REST THERE IS NO MARGIN AT ALL. Nothing is travelling, so the loan is
     zero, so g = 1 and m = 0 EXACTLY — not a ring held empty by a reserve, no
     ring. The page is the window with its gutter intact.
  2. THE MARGIN CANNOT STEP. m is a continuous function of the loan, the loan
     is a sum of the travellers' own swells, and each swell is a rate-limited
     state rather than a reading of progress — so it stays continuous even
     when a body is retargeted mid-journey and its progress is reset to 0,
     which is what happens whenever a scene is chosen before the last has
     settled. It grows out of zero and returns to zero. Nothing switches.
  3. A SETTLED CELL IS UNAFFECTED BY ANOTHER BODY'S TRAVEL. Its area is
     claim_i * PW * PH whatever anyone else is doing. Murmur's reserve had to
     defend the ring to approximate this; here it is an identity.

WHAT MAKES IT A BUFFER RATHER THAN A ZOOM. Growing the domain alone would
enlarge every cell in proportion — a zoom, which relieves nothing. The SWELL
decides who the new room belongs to: a travelling body's claim is raised on a
hump that is exactly zero at both ends of its journey, and because the domain
grows by exactly the total of those raises, the extra ground is created for
the travellers and NOBODY IS SQUEEZED TO PAY FOR IT. The page makes room
along the route and gives it back as the last body lands.

The reserve, its ring sites, its ledger, its four physics guards and the
per-body seed box all go. With no ring sites there are no extra bidders, so
no extra neighbours and no extra corners — Murmur's worst cell reached ten
because of them.

Read against Brim, which deletes the buffer outright. If Brim is as good,
this was never needed; if Bellows is smooth AND keeps what Brim gives up,
the buffer was load-bearing and only its switch was wrong.

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


replace('<title>Hive</title>', '<title>Bellows — Hive</title>')
replace('&larr; Back</a>', '&larr; Back · Bellows</a>')

# --------------------------------------------------------------- the constants
replace('const scenes = {', '''// ============================================================ BELLOWS
const BW_SWELL = 0.35;    // extra claim a traveller carries at mid-journey, per unit of its own (0: off)
const BW_CAP = 0.25;      // most the domain may exceed the window by, as a share of it
const BW_SLEW = 1.2;      // fastest the swell may change, per second (0: no limit)
const BW_EPS = 1e-9;

// A hump on a body's own journey: zero at the start, zero at the end, one in
// the middle. It has to vanish at both ends or the page would not be the
// window at rest — and because progress is easeInOutCubic, whose slope is
// zero at both ends, the hump leaves and returns with zero slope too.
function bwHump(p) { return p > 0 && p < 1 ? 4 * p * (1 - p) : 0; }

// ON ITS WAY SOMEWHERE — the only bodies the page makes room for. A journey is
// not enough on its own: `steer` refuses to end one for a body that is
// `leaving` or that keeps a `table`, and a void keeps its table for good once
// a scene has opened it. Progress is the truthful clock. And the path must go
// somewhere: `retireBody` gives a body a path from where it stands to where it
// stands, and a bystander is re-seated where it already was. Neither is
// travelling, and neither needs room to do it.
function bwTravelling(b) {
  if (b.isSelf || b.leaving) return false;
  if (!b.journey || b.progress >= 1) return false;
  const p = b.path;
  return !!p && Math.hypot(p.ex - p.sx, p.ey - p.sy) > 1;
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
  bwG() {
    if (this.depth !== 0) return 1;
    const base = this.COLS * this.ROWS;
    if (!(base > 0)) return 1;
    return Math.max(1, Math.min(1 + BW_CAP, 1 + (this.bwLoan || 0) / base));
  }

  // the rim, in px, uniform on all four sides: (W + 2m)(H + 2m) = g*W*H
  bwM() {
    const g = this.bwG();
    if (g <= 1 + BW_EPS) return 0;
    const W = this.W, H = this.H, s = W + H;
    return (-s + Math.sqrt(s * s + 4 * (g - 1) * W * H)) / 4;
  }

  bwBox() {
    const m = this.bwM();
    return [-m, -m, this.W + m, this.H + m];
  }

  domainPts() {
    if (this.depth === 0 && !this.domainPolyActive()) {
      const [x0, y0, x1, y1] = this.bwBox();
      return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    }
    return this.bwOldDomainPts();
  }

  bwOldDomainPts() {''')

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
        const box = this.bwBox();
        b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
        b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));
      }''')
replace('''        b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));
        b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));''',
'''        {
          const box = this.bwBox();
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
// inside BW_CAP.
const bwOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  bwOldPlace.call(this);
  if (this.depth !== 0 || BW_SWELL <= 0) return;
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
  // at all, moves 298.5 px against Bellows' 304.2. The rim collapse is worth
  // fixing because it breaks the mark's own invariant and because it drops the
  // buffer at the exact moment the page needs it, not because it is the bump.)
  //
  // So each body carries its swell and the swell is rate-limited. It can be
  // asked for anything by anything; it can only ever get there smoothly. The
  // domain is sized from what was actually applied, so the identity
  // tgt = claim * PW * PH survives the limiter exactly.
  const dt = Math.max(0, Math.min(0.25, this.t - (this.bwT === undefined ? this.t : this.bwT)));
  this.bwT = this.t;
  const step = BW_SLEW > 0 ? BW_SLEW * dt : Infinity;
  const rows = [];
  let want = 0;
  for (const b of this.bodies) {
    if (b.isSelf) continue;
    let own = 0; for (const sub of b.subs) own += sub.claim;
    const target = (own > 0 && bwTravelling(b)) ? BW_SWELL * bwHump(b.progress) : 0;
    const cur = b.bwSwell || 0;
    const d = target - cur;
    b.bwSwell = Math.abs(d) <= step ? target : cur + Math.sign(d) * step;
    if (b.bwSwell > BW_EPS && own > 0) { rows.push({ b, own }); want += b.bwSwell * own; }
    else if (b.bwSwell < BW_EPS) b.bwSwell = 0;
  }
  this.bwLoan = 0;
  if (want <= 0) return;
  const cap = BW_CAP * this.COLS * this.ROWS;
  const k = want > cap ? cap / want : 1;
  for (const r of rows) {
    const g = 1 + r.b.bwSwell * k;
    for (const sub of r.b.subs) sub.claim *= g;
  }
  this.bwLoan = want * k;
};

/* --------------------------------------------------------------- START */''')

# THE CACHE MUST SEE THE RIM. solveMain's signature carries this.W/this.H and a
# domainSig that is EMPTY whenever the domain is a rectangle, so a domain that
# changes size while the window does not would otherwise be invisible to it and
# a stale solve would be served. Quantised to a tenth of a pixel.
replace("""    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|';""",
        """    let sig = active.length + '|' + (this.W * 8 | 0) + 'x' + (this.H * 8 | 0) + '|' + (domain ? this.domainSig : '') + '|B' + (this.bwM() * 10 | 0) + '|';""")
replace("""    let s = this.domainPolyActive() ? this.domainSig : '';""",
        """    let s = (this.domainPolyActive() ? this.domainSig : '') + 'B' + (this.bwM() * 10 | 0);""")

# development only: BELLOWS_VARS="BW_SWELL=0" builds a variant
for kv in filter(None, os.environ.get('BELLOWS_VARS', '').split(',')):
    kk, vv = kv.split('=', 1)
    pat = re.compile(r'^(const %s = )([^;]+);' % re.escape(kk), re.M)
    n = len(pat.findall(s))
    if n != 1:
        raise SystemExit(f'BELLOWS_VARS: {kk} found {n} times')
    s = pat.sub(lambda m: m.group(1) + vv + ';', s)

OUT = Path(os.environ.get('BELLOWS_OUT', str(ROOT / 'bellows.html')))
OUT.write_text(s)
if os.environ.get('BELLOWS_OUT'):
    print('Built variant', OUT)
    raise SystemExit(0)

# --- the gallery card -------------------------------------------------------
index_path = ROOT / 'index.html'
index = index_path.read_text()
card = '''
        <!-- BELLOWS -->
        <a href="bellows.html" class="version-card latest">
            <h2>Bellows</h2><span class="latest-flag">Latest</span>
            <span class="mk">Bellows</span>
            <span class="tag preview">Tested experiment</span>
            <p>The overflow buffer with its switch removed. Murmur's margin snaps into existence when a change starts and out of it when the change ends, and those two frames are the skip. Here there is no ring and no reserve: the ground itself is sized to the page's total claim, so it grows out of nothing as the travellers ask for room and returns to nothing as they land. At rest the domain is the window exactly.</p>
            <ul>
                <li>Every cell gets exactly its claim, at any rim depth — an identity, not a ledger</li>
                <li>A settled cell is untouched by anyone else's journey</li>
                <li>No ring sites, so no extra neighbours and no extra corners</li>
                <li>Read against Brim, which deletes the buffer instead</li>
            </ul>
        </a>
        <!-- /BELLOWS -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
IS_LATEST = True   # only the newest mark wears the flag
if not IS_LATEST:
    card = card.replace(' latest"', '"').replace('<span class="latest-flag">Latest</span>', '')
own = re.compile(r'\n?[ \t]*<!-- BELLOWS -->.*?<!-- /BELLOWS -->[ \t]*\n?', re.S)
index = own.sub(lambda m: card, index, count=1) if own.search(index) else index.replace(anchor, anchor + card, 1)
index_path.write_text(index)
print('Built bellows.html from reference blob', EXPECTED)
print('Bellows SHA256', hashlib.sha256(s.encode()).hexdigest())
