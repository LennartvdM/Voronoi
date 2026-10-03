# Datum: the sea's gauge brackets from the first reach to touch

Baseline: Facet, `facet.html` on this branch, SHA-256
`17087c3d4e4145f947614cfaa06f17d5158dc54269187053cc1f576a1e5eee6a`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Facet, on a desk (1440×900).
It changes one bracket in the auction's solver and nothing else.

## What it proves

Found while building Dough, whose conserved mass keeps the sea small all
through a change. On Dough's Drift to Aurora, on alternate frames, four cells
between the two images vanished and came back, and the images' drawn centres
jumped by 200 px frame to frame. The cause is in Membrane, and Facet has it
too.

With the sea, the auction's weights have one gauge: a shift of them all that
gives the sea its area (a shift moves no bisector, only every reach). When a
solve begins with no sea at all, every reach covering its cell and no shore,
the solver brackets the shift between the one at which every reach is gone
(all sea) and the one at which the first reach just touches its own cell (no
sea yet), and closes the bracket by regula falsi, twenty-four steps at most.

Two things were wrong with the bracket's high end.

- **It was the least of the touching shifts, not the greatest.** A site's
  reach covers its cell down to the shift at which it touches the cell's
  farthest corner, and the sea appears as soon as one reach has let go: at the
  greatest of those shifts. The least of them is where the last reach has
  shrunk onto its cell, with the sea nearly the whole ground. Both ends of the
  bracket then drown the sites, the root is outside it, and regula falsi walks
  to the high end: every weight down by about a million, most sites left with
  no ground and re-entered one at a time against whoever is left, and the ones
  buried under a later entrant sit the solve out (Facet's rule) and are not
  drawn that frame. The next frame repairs them, the one after drowns them
  again.
- **It was read over the cells alone.** Amoeba's rule, where only a cell had
  a reach. Since Facet whitespace reaches too, as a square, and the sea
  appears in a whitespace's cell as in any other; left out, its squares had
  let the sea in long before the first cell's reach touched. The least and
  greatest weights the bracket's low end reads were the cells' alone too.

The branch runs only when the sea has vanished at a warm start: rare while
the sea holds free ground, constant when the sea is small.

## How it works

- **The bracket is taken over every site the sea cuts**: a cell by its reach,
  whitespace by its square.
- **Its high end is the greatest of their touching shifts**, the shift at
  which the first reach touches. The bracket holds the root, and regula falsi
  closes it in a handful of steps.
- **Scope.** The one bracket. With the rule taken out the page is Facet's to
  the bit.

The header carries no captions.

## Measured

`tests/datum/validate.cjs` builds nothing and reads `facet.html` and
`datum.html` from the repository root. Real full tick, native Canvas and the
browser DOM stubbed, frames of 1/64 s, a desk of 1440×900 (the stories at
1900×810), the worker of Wings thinking sixteen rehearsed frames a frame.
`tests/datum/validation.json` holds the figures.

- **The gauge**, with no thinking, in every solve of the page's with the sea
  over the chain through every page from every other (10,210 frames of
  change):

  | | Facet | Datum |
  |---|---|---|
  | gauges from a solve with no shore | 95 | 95 |
  | of them, the sea left over a tenth of the ground from its area | 95 | 0 |
  | over half | 13 | 0 |
  | run to their last step | 95 | 1 |
  | gauges from a solve with a site holding no ground | 773 | 778 |
  | of them, over a tenth off | 1 | 0 |
  | the largest miss, as a share of the ground | 61% | 5.3% |
  | sites sitting a solve out (undrawn that frame) | 196 | 101 |

- **The rule is the only change.** With it taken out and no thinking, the
  tour of changes and the chain are Facet's, the world and every drawing
  command, frame by frame (11,550 and 25,950 frames).
- **Every page from every other, and the tour, with the worker thinking**:
  nothing waits or fractures, what is rehearsed is what is played, every
  change has one pace, every page at rest is exact. Defects drawn (lurch,
  slivers, splits, near-collisions, start shock, one score):

  | | Facet | Datum |
  |---|---|---|
  | the chain, 56 changes | 94,949 | 84,857 |
  | of it, lurch | 19,844 | 13,776 |
  | start shock | 13,321 | 7,503 |
  | the tour, 25 changes | 21,690 | 16,125 |
  | of it, lurch | 9,530 | 4,025 |

  Of the 56 changes 21 are Facet's to the bit (the gauge never ran from a
  solve without a shore), 25 are lower and 10 higher; of the tour's 25, 14
  are Facet's, 10 lower and 1 higher. Slivers and near-collisions are
  Facet's within a few.
- **In Chromium** (Playwright, the page itself with its worker, a desk of
  1440×900, the chain's first ten changes): 159 to 193 frames in the 3.2 s
  after a click, the longest frame 26 to 90 ms, first motion 8 to 62 ms. No
  errors.

- **Where Facet lost cells for a frame.** On Facet, over the chain, cells sat
  a solve out and were not drawn on alternate frames at the start of several
  changes: Petal to Drift, frames 5, 8 and 10, Aurora, Jazz and Coal; Dune to
  Petal, frames 6 and 9, Ember, Jazz, Mint and Coral; Dune to Moss, frame 5,
  ten sites. On Datum none of these.
- **A Cue story is Facet's frame by frame** (2,040 frames); a Tell and
  a Tell II story run to their end and home without a fractured cell.

## Known

- **One no-shore gauge on the chain still runs to its last step** (Petal to
  Jazz, frame 173), and leaves the sea 145 px² of 1.3 million from its area
  for Newton. The sea's area against the shift has a plateau there: the first
  reach to let go is a whitespace's square whose whole cell, 584 px², goes to
  the sea by the time the next reach touches, 140,000 lower; the sea's claim
  that frame is 637 px², just above the plateau, and regula falsi walks the
  plateau. Facet's 95 no-shore gauges all ran to their last step.
- **The empty-site case keeps its wide bracket.** When a solve begins with a
  site holding no ground, the high end is the shift at which every reach
  covers the whole ground, as on Facet; a tighter one would read the cells'
  touching shifts off polygons the sea has already cut, which is wrong (tried:
  misses of up to 82%). Those gauges run to their last step a fifth of the
  time, as on Facet, and miss by at most a twentieth of the ground, which
  Newton takes up in the same solve.
- **Sites still sit a solve out**: whitespace's seam sites standing in a
  settled cell, Facet's own case, and on the fourth frame of every change
  from Dune one or two cells, as on Facet, a site empty at the warm start that
  its re-entry does not seat. That case is not this mark's.
- **Desk only.**

## Run

```bash
python3 tests/datum/build.py
node tests/datum/validate.cjs
```
