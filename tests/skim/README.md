# Skim: preserve Buoy while doing less repeated work

Baseline: the accepted Buoy page from PR #264, commit
`843c66171bb2f58383254fba8aa2dc7b810756d9`, Git blob
`a34434449e06bd4cf78a1fa8282793f8fbce2207`.
The exact source is included as `buoy.html`; the builder checks its SHA-256.
This makes the mark reproducible independently of unmerged experiment branches.

## Findings and changes

Profiling the complete frame identified diagram evaluation as the largest CPU
consumer. Each Newton/line-search evaluation was rebuilding buckets, sorting
neighbour rings and recomputing seed distances even though the seeds and domain
remain fixed throughout that solve. Skim prepares these once per solve and
populates ordered rings on demand. The object is discarded after the solve;
there is no cache across frames, approximate key or stale geometry. Weights,
clipping order, pruning, tolerances and iteration budgets are unchanged.

The diagnostic rasterizer was another significant cost. It visited each covered
sample individually, then scanned the entire coverage bitmap. Skim accumulates
scanline coverage events and counts constant-coverage runs. Intersections,
S=2 samples, half-open edges, signed holes and the every-12-frames cadence remain
the same. The diagnostics have not been disabled or sampled less often.

Motion clocks, void handling, hover claims, label springs, Canvas drawing, nested
layouts and footer controls are untouched. Earlier mark pages are not modified.

## Measured CPU cost

Median of five paired runs in alternating order, following two warmup runs for
each mark and workload. Each measured run contains 1,600 frames at 60 Hz,
1900 x 810. The transition workload includes Frame -> Sidebar and Hero -> Sidebar,
Flock, hover acquisition and release. Each settled run has a separate warmup.

| Workload | Buoy total | Skim total | Less computation |
| --- | ---: | ---: | ---: |
| 12 elements, Fields 55%, transitions | 1,345.5 ms | 1,076.0 ms | 20.0% |
| 24 elements, Fields 100%, transitions | 2,612.6 ms | 2,029.7 ms | 22.3% |
| 12 elements, Fields 0%, settled Sidebar | 686.9 ms | 491.8 ms | 28.4% |

These are **JavaScript CPU measurements in Node**, executing the real tick with
Canvas methods and DOM writes stubbed. They include paint geometry, content
springs/anchors, solver, pointer routing and diagnostics. They exclude native
Canvas drawing, GPU, browser layout and compositor cost; they are not browser FPS
claims. Absolute timings and percentages depend on the machine. Raw samples,
runtime and CPU information are in `benchmark.json`. Instrumented attribution is
kept separately in `profile.json` and is not used for the speedup claims.

## Behaviour verification

`validate.cjs` compares the actual full tick against the pinned Buoy source:

- 16,490 frames with exactly equal engine state (except measured solve duration),
  final leaf geometry, gap/overlap meters and 16,538,248 Canvas drawing commands.
- Desktop, narrow viewport, dense counts, Organic/Grid fields and fixed clocks
  at 120 Hz, 60 Hz, 30 ms and 50 ms.
- All five layouts, hover/release, interrupted changes, add/remove, resizing and
  zero gap/corners. Each fixture must actually acquire hover.
- 503 additional raster cases cover holes, overlapping polygons, reversed
  winding, notches, offscreen geometry and coincident sample boundaries.

`validation.json` records source hashes, frame counts and fixture details. Label
placement is included because its anchors feed back into free-cell motion.

## Reproduce

From the repository root:

```sh
python3 tests/skim/build.py
node tests/skim/validate.cjs
node tests/skim/benchmark.cjs
node tests/skim/profile.cjs
```

The build writes only `skim.html`. The gallery entry is a separate ordinary
`index.html` change. Open `/skim.html` on the PR's Netlify deployment for the live
motion check. No new header controls are added.

## Remaining opportunity

Outline assembly and label-pole searches remain measurable costs. They were left
out of this change: both can affect geometry or motion, and the two optimizations
above already provide a measured improvement without changing results.
