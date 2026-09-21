# Ferry

Ferry starts from the accepted Harbor geometry (PR #261), not Cadence. It
addresses cells being squeezed across void generators in Frame → Sidebar
and Hero → Sidebar. The standalone page has the original footer controls
and a landing-page entry; earlier marks are unchanged.

The trace distinguishes the moving seed from the cell that is actually
painted. Harbor's seed can move 27 px while its cell centroid travels over
500 px in one 30 ms frame. Removing physical repulsion from void bodies did
not remove that jump. The large incoming Sidebar void places its generators
inside the departure route: a weighted cell can stay on one side of those
generators, become a thin wedge, then rapidly transfer to the other side.
Cadence's longer clocks do not remove that geometric crossing.

Ferry changes three related parts of the crossing:

- Full-height edge voids approach from beyond the departing content seeds.
  Their clearance returns to zero displacement once the original rest
  formation is clear. It is bounded by the rest geometry's actual spacing,
  so the accepted rectangle targets are retained.
- A retiring interior void keeps all its generators, weights and claim
  shares. Each generator follows the centroid of its previous owned patch
  at a bounded speed while its existing ledger drains. It does not collapse
  its formation into a single point or become a cutout.
- Within a destination row, a cell waiting ahead of a departing neighbour
  may depart sooner. No journey duration is increased or shortened; no
  spring, path, speed limit or global deadline is changed.

Interruption exposed an inherited ledger discontinuity: a replacement
journey counted as instant completion of its old void debt. Outstanding
shares now finish on the original journey clock. Spatial state survives
interruption and scales with viewport size.

The fixture `harbor.html` is byte-identical to the accepted source at
`2f2f8265ac403da91acc51a17785d1763d46c4c2`, Git blob
`c4885ad49e293cfb99a1aa0d4f283aadf4d03687`. Harbor was unmerged when Ferry
was prepared, so the fixture keeps this PR independently reproducible from
current main.

Build with `python3 tests/ferry/build.py`.
Run the diagnostic with `node tests/ferry/validate.cjs`.

The screen compares the reported crossings at 60 Hz, 30 ms and a variable
25 ± 12 ms clock. It records root-cell and final leaf centroids separately,
with nested fields enabled. It also exercises the other directed scene
changes, four additional viewport/count configurations, repeated
interruptions, resizing and count changes. The DOM and paint are stubbed;
this is geometry evidence, not a substitute for live Netlify viewing.

In the 1900 × 810, 12-element, 30 ms runs, the maximum root-cell step falls
from about 519 to 56 px for Frame → Sidebar and 663 to 44 px for Hero →
Sidebar. The original journey durations are identical. The final leaf
centroid peak also falls in all six targeted clock/transition cases.

Limits: this is a correction to crossing behaviour, not a global speed cap.
The original 900 px/s seed limit remains. Some nested-field and other scene
transitions still have large centroid changes, especially at different
counts or sizes; those are recorded in `results.json`. Hero → Sidebar has
more sustained motion even though its extreme spike is much lower. Live
viewing determines whether that motion feels right.
