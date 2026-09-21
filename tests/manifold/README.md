# Manifold: a bounded geometry screen

Harbor is the selected **live candidate**, not a declaration that the motion
problem is solved. Quay is an explicitly weaker comparison. Selvedge is the
unchanged control, with its source pinned by the builder.

The batch tested three materially different hypotheses:

1. Reallocate the overlapping whitespace bands into a disjoint partition.
   At exact template centres, the remaining void mismatch was 3.43% in Hero
   and 24.33% in Frame. This failed before animation testing.
2. Derive void generators and quotas from the neighbouring content's power
   geometry. This gives Hero a rectangular void without changing its visible
   layout or making a content body a lattice. Reflection alone still misses
   Frame by 13.45%, so it is used only for Hero. Attempts to fit the original
   Frame's corner weights did not establish a valid construction and were
   discarded.
3. Give Frame a compatible row/column template. Whitespace alone may own
   multiple generators. Visible bodies retain exactly one site. Odd counts
   refine an outer corner, with the new weight capped so it cannot take area
   from the central void; its quotas come from the authored rest diagram.
   Four through seven bodies use four ordinary supporting cells and corner
   refinements. No roster is silently padded or truncated.

Harbor combines the successful Hero construction and Frame template. Quay
uses the same Frame but replaces Hero with a full-height card and a side
stack. Quay was not selected: the large card has more facets, its neighbours
are thinner, and its transition measurements are substantially worse.

Ambient wobble and repulsion otherwise keep the bodies permanently away
from the valid rest solution. For the new Hero/Frame destinations only, these
forces decay over the body's existing progress. There is no second clock,
whole-page arrival gate, pin, domain wall, live cut, or visible-cell lattice.
Flock, Bento and Sidebar retain their original targets and force rules.

The Hero reference solve occurs once per layout/viewport/count and is cached.
It uses the intended content region to derive compatible generators and
areas. This region is **not** cut out of the live animation domain: the live
root remains one power auction, including the whitespace. Selvedge's site
objects, warm weights and outgoing-void lifetime are retained.

## Reproduction

Build the pinned Selvedge source with `python3 tests/selvedge/build.py`, then
the two candidates with `python3 tests/manifold/build.py`. Run
`node tests/manifold/validate.cjs` for the comparison and
`node tests/manifold/static-screen.cjs` for the initial geometry screen.
The candidate builder intentionally does not rewrite the shared gallery.

The validator runs the actual inline engines with DOM/paint stubs, including
nested fields. It measures 21 layout/viewport/count cases, all 20 directed
scene transitions at 60 Hz and 30 ms, rapid interrupted sequences at three
delays, and resize cases. It checks finite geometry, one site per visible
body, absent root walls/holes, missing cells, convexity, departure jumps and
resting rectangle error. Shape-change events compare consecutive outlines
after removing centroid translation; they do not measure browser rendering
or establish the quality of the choreography.

## Results and limits

At 1900 × 810 with 12 bodies, Harbor reduces the resting Hero rectangle
mismatch from 7.28% to 0.0000081%, and Frame from 39.36% to 0.0000053%.
Across the tested non-fallback Hero/Frame cases, mismatch remains below
0.001%. Sidebar's recorded control results are identical.

Across 40 directed transition cases, the count of body-frames exceeding 12%
centred outline change is 1327 for Selvedge, 1246 for Harbor and 2429 for
Quay. These totals are not a universal smoothness claim. Harbor has a peak
centroid step more than 10% worse than Selvedge in **12 of 40** cases.
Frame → Sidebar is a material regression: at 30 ms its peak is about 598 px
against 379 px. Both versions can still undergo large changes later in a
transition. All per-transition results and regressions remain in
`results.json`.

Rapid interruptions still produce large jumps in both engines, although
Harbor improves the three measured sequences (about 122/124/160 px versus
150/152/173 px). The original over-capacity Hero fallback persists: at
1900 × 810 with 30 elements the old Hero template supplies too few slots,
so Harbor and Selvedge both fall back to Flock. Higher counts can also exceed
nine outline vertices despite every visible cell being convex. These are
open limitations, not passed requirements.

The Netlify comparison loads one animation at a time. Its replay button
settles the selected source layout for eight seconds before clicking the
destination. The standalone mark is the full-window performance reference.
