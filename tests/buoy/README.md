# Buoy

Buoy is the accepted Ferry mark with one hover-budget correction. Ferry's
crossing mechanics, paths, clocks and resting geometry are retained.

`placeSeeds` already eases the hover request and raises a content body's
site claim. The seam pass runs afterwards and replaced that funded claim
with `b.claim`, the unboosted base. Every root body with a layout rectangle
went through this pass, so hover was detected and highlighted but expansion
was silently cancelled. Flock did not use that pass.

The seam pass now distributes the funded content claim. Void bodies keep
reading their existing whitespace ledger. This reuses the existing hover
ramp, slider, pointer routing and neighbour response.

The older inert-rectangle defect recorded in PR #223 was different: settled
walls had left the area auction entirely and needed hover shards. That
mechanism remains for nested walls. Ferry's root content is already bidding
with crystal zero, so adding another wall-unlocking mechanism would address
the wrong cause here.

The source fixture is byte-identical to Ferry at
`e441232988597593bce1128451050277d52f51e0` (PR #263), Git blob
`8c8cbde908a0b33d70fcd14935989c7cadb8d647`. The PR is built independently
from current main because Ferry has not yet merged. Existing marks are not
rewritten.

Build: `python3 tests/buoy/build.py`.
Check: `node tests/buoy/validate.cjs`.

The diagnostic reproduces Ferry's inert hover in Bento, Sidebar, Frame and
Hero and measures expansion and release in Buoy. It exercises the slider,
pointer transfer, nested Organic/Grid controls, and starting a transition
while hovered. The probe runs the page's actual pointer-routing block and
solver, with DOM and paint stubbed.

With the pointer absent, 2,031 consecutive simulated frames have exactly the
same root state and final leaf geometry as Ferry, including Frame → Sidebar,
Hero → Sidebar and interrupted transitions. This is an exact comparison, not
a claim based on similar motion scores. Hover is a deliberate change and
must still be evaluated in the live Netlify preview. The page has only the
original footer controls and its own landing-page card.
