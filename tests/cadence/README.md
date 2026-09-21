# Cadence

Cadence retains the accepted Harbor geometry and changes the timing of root
content cells travelling to a layout. The standalone page uses the original
footer controls. There is no comparison header or embedded preview.

Harbor already has a separate departure time for each body. The rush is not
a shared deadline: its travel duration caps at about 2.2 seconds, calculated
from the straight chord, while the moving target follows a curved route with
cubic easing. A spring then follows that target.

Cadence keeps the path, spring, stagger and destinations. It gives each route
at least enough time for the maximum quadratic-path derivative multiplied by
the peak derivative of quintic smootherstep (1.875), at a target speed of
160–340 px/s depending on viewport. This bounds the target's nominal speed;
it does not cap the rendered cell centroid or every force on the seed.
Smootherstep has zero velocity and acceleration at both ends.

A lagging seed can slow its own progress clock. The rate eases toward the
ratio of a comfortable spring lag to its actual lag, with a positive floor
of 0.18. Lost time extends that body's end time; it is never repaid by running
faster than the original pace. Position, area, void ledgers and margin claims
continue to read one progress value. Hover exclusion includes the extra time.
Nested-field motion and free Flock drift retain their existing rules.

`harbor.html` in this test directory is an immutable source fixture, copied
byte for byte from the accepted mark at commit
`2f2f8265ac403da91acc51a17785d1763d46c4c2` (PR #261). That PR was still unmerged
when Cadence was prepared. The fixture makes this branch independently
reproducible from current main without modifying or rebuilding older marks.

Rebuild with `python3 tests/cadence/build.py`. Validate with
`CADENCE_CLOCKS=hz60,ms30,jitter node tests/cadence/validate.cjs` and
`node tests/cadence/edge-cases.cjs`.

The motion screen runs all 20 directed transitions at 60 Hz, 30 ms and a
deterministic 25 ± 12 ms clock. It simulates nested fields but stubs the DOM
and paint. Root seed speed and the speed of the actual power-cell centroid
are measured separately. Late cells are the last quartile of departure
delays. These are motion diagnostics, not an aesthetic certification.

Across all 48 cases travelling into a layout, peak seed speeds and peak
root-cell centroid speeds are lower than Harbor's. Cadence's highest seed
speed in those cases is about 413 px/s, compared with Harbor reaching its
900 px/s limit. Late cells spend no time above 500 px/s in the screen, versus
about 43.9 accumulated body-seconds for Harbor across the same cases.
The longest measured journey finishes at about 8.1 seconds. The twelve
departures into Flock are also recorded; they do not use the new path clock.

Hero and Frame retain rectangle error below 0.001% in the tested transitions,
additional viewport/count cases, and resizes. The existing Sidebar geometry
is retained, including its small errors at some sizes/counts. A controlled
obstruction additionally exercises the lag governor: it adds about 2.84
seconds and the body eventually finishes after release. The obstruction is
test instrumentation, not a production pin.

Limits: changing layouts repeatedly before they finish still produces large
outline changes. The measured immediate jump in the interruption sequences
is roughly 70–130 px, versus 70–139 px in Harbor. Large later centroid changes
also remain in some transitions despite the speed reductions. Cadence is
intended to improve pacing, not to claim that every diagram discontinuity is
solved. Full measurements, source hashes and these limitations accompany the
new mark. Existing marks and shared hosting configuration are unchanged.
