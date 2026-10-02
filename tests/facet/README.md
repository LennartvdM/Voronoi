# Facet: the hive with straight edges, light and steady

Baseline: Cohort, `cohort.html` on this branch, SHA-256
`708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Cohort, on a desk
(1440×900).

## What it proves

The owner found the Membrane class heavy on calculations and hesitant, with
the images still round globules in flight. Measured on Cohort, all three are
real and have causes.

- **Heavy.** The soft sea cuts every cell the hive's edge crosses on a grid of
  8 to 16 squares across it, then merges the squares back into one outline.
  Over the 56 page-to-page changes, with no thinking, a quarter of the frames
  ran over 16 ms (913 of 3,600, against 7 on Tempo, before the sea), up to
  131 ms.
- **Hesitant.** Dropped frames are one cause. The other is the auction falling
  behind.
  - A third of the frames while a change runs end with some site more than 1%
    off its claim, in runs of up to 81 frames (1.3 s). The cells drift off
    their sizes and are pulled back.
  - Most of it is Newton running out of its 3 steps a frame.
  - Some of it is one site with no ground. A whitespace's seam site standing
    in a settled cell can hold none, so no step can give it any. Newton then
    stopped after one step, frame after frame, and the page held and then
    jumped (Tide to Moss: 10 frames held, then every cell 4 to 15 px in one).
- **Globules.** A lone cell in the sea is exactly its disc, and the image is
  the cell most often alone.

Facet tests a hive whose every edge is straight, with an auction that keeps
up.

## How it works

- **A cell reaches as far as its own rectangle.** While the page changes, a
  cell faces the sea along the sides of a rectangle, and its neighbours along
  their bisectors, as ever.
  - The rectangle is centred on its seed, of area π w, as a disc of the same
    weight would be.
  - Its proportions are its seat's, turning from the seat it leaves to the
    seat it takes, geometrically, as its size turns (or as its journey goes,
    if its size hardly does).
  - So every cell is a polygon. A cell on its own is a large Voronoi cell with
    the sides of its frame, and the image travels as one.
  - A cell is four clips more than its power cell: no grid, no merging. The
    Jacobian of a side is exact: a side moves out by its half side's own
    change, h / 2w for a unit of weight.
- **A site with no ground sits the solve out.** When a solve with the sea
  begins, a site that holds no ground keeps its weight and leaves the system,
  and the rest of the auction converges without it. It rejoins when it holds
  ground again.
- **While the sea is in, Newton takes 8 steps a frame**, Cohort's own cap for a
  long frame, instead of 3. A straight-edged frame costs a fraction of a soft
  one, and a rectangle's area answers its weight more stiffly than a bell's:
  with 3 steps the auction fell behind the moment the sea came in (every cell
  13 to 26 px in one frame, Petal to Drift).
- **Scope.** The page's own changes, where the sea is. The stories, which keep
  their own whitespace, and the fields inside cells are Cohort's.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s.

**With the rules taken out, Facet is Cohort.** The tour (11,550 frames) and the
chain through every page from every other (25,950 frames) are Cohort's to the
last drawing command. With the rules in, a Cue story is still Cohort's (2,040
frames), and a Tell and a Tell II story run to their end without a fractured
cell (3,060 frames).

**The hive itself**, over the tour and the chain (82 changes), with no thinking.
Times are node's, on a machine running other work, so they compare and do not
predict a browser's:

| | Cohort | Facet |
|---|---|---|
| A frame, median | 14.2 ms | 5.0 ms |
| 90th percentile | 31.8 ms | 10.9 ms |
| 99th percentile | 72.5 ms | 29.1 ms |
| Frames over 16 ms | 6,184 | 554 |
| Frames over 50 ms | 348 | 26 |
| Sea sides at an angle | 573,412 of 574,606 | 0 of 175,296 |
| Corners of the image in flight | 18.7 | 6.6 |
| How much of its rectangle the image fills | 0.685 | 0.801 |
| Frames ending more than 1% off a claim | 4,649 (33%) | 416 (2.9%) |
| The longest run of them | 81 frames | 17 frames |

**Drawn**, with the worker of Wings thinking 16 rehearsed frames a frame.
Nothing waited or fractured, and every move was laid bit for bit on its
rehearsal (122 moves over the chain, 28 over the tour).

| | Chain, Cohort | Chain, Facet | Tour, Cohort | Tour, Facet |
|---|---|---|---|---|
| Lurch | 35,580 | 19,844 | 11,929 | 9,530 |
| Slivers | 830 | 1,010 | 165 | 138 |
| Splits | 27.9 | 0 | 4.6 | 0 |
| Near collisions | 117 | 113 | 31 | 32 |
| Shock | 12,125 | 13,321 | 2,160 | 2,070 |
| **Defects** | **106,515** | **94,949** | **26,377** | **21,690** |

Thinking on the page, with no worker, the hive plays what it rehearsed (67
rounds over 12 changes, none late).

**In Chromium**, headless, ten page changes, 3.2 s each, two runs:

| | Cohort | Facet |
|---|---|---|
| Frames drawn | 906, 937 | 1,590, 1,548 |
| The longest frame | 262 ms, 391 ms | 77 ms, 84 ms |
| Errors | none | none |

## Known

- **Slivers are up a fifth on the chain** (830 to 1,010) and the shock a tenth
  (12,125 to 13,321). Lurch is down by nearly half and splits are gone, so
  the total is down, but those two are not.
- **Some changes draw more than on Cohort.** On the tour, Coal's page from
  home draws 2,663 against 318, and home from Moss's 3,834 against
  2,258. On the chain, Drift to Aurora draws 1,285 against 290, and Aurora
  to Ember 1,990 against 443.
- **The screen is leaned on more** over the chain: 20.1 million px-frames
  against 17.7 million.
- **Whitespace reaches as a square.** Tried with the proportions of its seats,
  as a cell's: the chain drew 114,086 against 93,684 in the on-page harness.
  With no reach for whitespace at all, 149,856.
- **A site with no ground sits out only where the sea is.** On every solve
  the Cue story left Cohort's at frame 391.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Facet has no card yet.

## Run

```bash
python3 tests/facet/build.py
node tests/facet/validate.cjs
```
