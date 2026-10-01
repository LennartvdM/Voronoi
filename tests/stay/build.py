"""Build Stay from Cohort: the image stays the image.

On Cohort, a change from page to page still swapped two cells of opposite
sizes: the image shrank to a card and went into the gallery, and the clicked
card left the gallery and ballooned into the image. Most of Cohort's rules
manage that exchange.

Here no cell changes role. The cell in the image's place stays the image; the
cell in the clicked card's place stays a card. What changes hands is what
they are, not where they are: at the click the two bodies trade places, each
keeping its own name, colour and kind of page, and each place's colour turns
from the one it showed to its new body's on that body's journey. Then the
page changes as a layout: the image's cell goes from its rectangle to the
new page's, the gallery from its seats to its new ones, and nothing crosses.

With no exchange, Cohort's windows, its handover and its free sea never come
into play. The gallery keeps its side, as on Cohort.

Every change that does not go from a page to a page is Cohort's to the bit.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cohort.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Cohort — Hive</title>', '<title>Stay — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Cohort</a>', '<a class="back" href="index.html">&larr; Back · Stay</a>')

replace("""const COHORT = true;                                // COHORT: from page to page, the gallery is one body""",
"""const COHORT = true;                                // COHORT: from page to page, the gallery is one body
const STAY = true;                                  // STAY: from page to page, the image stays the image""")
replace("""    portalWas = portalFocus && config.scene in PORTAL_TEMPLATES ? portalFocus : null; portalFocus = b; portalEnter(portalKind(b), { x, y }); portalWas = null;""",
"""    // STAY: from a page, the clicked card and the image trade places, so the
    // image's place stays the image's and no cell changes role
    for (const q of root.bodies) q.shown = null;
    const img = STAY && portalFocus && config.scene in PORTAL_TEMPLATES && portalFocus !== b && !portalFocus.leaving && !b.leaving && !b.hive && !portalFocus.hive ? portalFocus : null;
    if (img) portalTrade(b, img);
    portalWas = img ? null : portalFocus && config.scene in PORTAL_TEMPLATES ? portalFocus : null; portalFocus = b; portalEnter(portalKind(b), { x, y }); portalWas = null;
    if (img) for (const q of [b, img]) q.shown.j = q.journey;""")
replace("""// COHORT: where the open page's gallery is: its cards' seats' centroid, by area""",
"""// STAY: what a body is, as against where it is
const PORTAL_SELF = new Set(['id', 'name', 'color', 'baseRel', 'baseClaim', 'kindRoll', 'wanderPhase', 'content', 'label', 'caption', 'isVoid', 'isSelf', 'shown']);
// STAY: two bodies trade places: each takes everything the other has but
// what it is, and whatever held one of them holds the other
function portalTrade(a, b) {
  const was = { [a.id]: portalColor(a), [b.id]: portalColor(b) };
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    if (PORTAL_SELF.has(k)) continue;
    const t = a[k]; a[k] = b[k]; b[k] = t;
    if (a[k] === undefined) delete a[k]; if (b[k] === undefined) delete b[k];
  }
  for (const s of a.subs) s.body = a; for (const s of b.subs) s.body = b;
  const sw = q => q === a ? b : q === b ? a : q, si = i => i === a.id ? b.id : i === b.id ? a.id : i;
  root.walls = root.walls.map(sw); root.holes = root.holes.map(sw);
  if (root.ownerOf) root.ownerOf = root.ownerOf.map(si);
  root.hoveredId = si(root.hoveredId);
  a.shown = { from: was[b.id] }; b.shown = { from: was[a.id] };   // each place keeps the colour it showed, and turns
}
// STAY: a body's colour, turning from what its place showed to its own on its
// journey
function portalColor(b) {
  const s = b.shown; if (!s || !s.j || b.journey !== s.j) return b.color;
  const p = Math.max(0, Math.min(1, b.progress || 0)), h = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16)), A = h(s.from), B = h(b.color);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * p).toString(16).padStart(2, '0')).join('');
}
// COHORT: where the open page's gallery is: its cards' seats' centroid, by area""")
assert s.count("body: b, color: b.color, hv:") == 2
s = s.replace("body: b, color: b.color, hv:", "body: b, color: portalColor(b), hv:")   # STAY: a place's colour turns

out = ROOT / 'stay.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
