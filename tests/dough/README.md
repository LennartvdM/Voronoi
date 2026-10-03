# Dough: the hive wets the pan

Baseline: Datum, `datum.html` on this branch, SHA-256
`e2e2745a5cc2b25e42c60b6f0030a976a1e974dc9c154ce6635a7233e5c88f94`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Datum, on a desk (1440×900).

## What it proves

The owner sees the hive, while a page changes, as a globule that avoids the
corners of the screen, and wants it to behave like a well hydrated dough: a
mass that spreads to the pan's walls and into its corners, rounded only where
it faces the air.

Measured on Datum, over the chain through every page from every other, the
cells hold 59% of the screen while a change runs, but only 47% of its
perimeter and 50% of its corner squares. The cause is not the shape of the
hive but its mass. Cohort's two images hand over where they pass: the closing
one shrinks to a card before their closest approach, and the opening one grows
only after. Halfway through Dune to Jazz the cells hold 13 of 96 slots, and
the sea 83. What is left of the hive is a ball in a void, and no rule about
its shape can fill the corners with it.

Dough tests the opposite rule: the mass is conserved, and the pan is the pan.

## How it works

- **The mass is conserved.** From page to page the closing image shrinks
  exactly as the opening one grows, each over its whole journey on the
  change's clock. What the cells and the whitespace hold adds up to the pan at
  every instant, and the two images press on each other as they pass, as
  dough does. Nothing is free ground: the sea is the whitespace in transit and
  nothing else.
- **The swarm does not float.** Since Membrane a liquid cell has kept its plan
  its own radius clear of the screen. Now its plan goes where the layout sends
  it, to the edge if the layout does; its reach is cut by the pan, and to hold
  its claim it grows, so a cell pressed against a wall spreads along it.
- **The pan is the same with a wall in it as without.** The auction's ground
  was cut from the page whenever a wall was in the frame (a reel's parked
  cards, on every page's change) and was the box the cells may overflow into
  otherwise, so cells overflowed on the home scenes and never on a page. Now it
  is the box less the walls, always.
- **Scope.** The page's own changes. The stories and the fields inside cells
  are Datum's.

The header carries no captions.

## Measured

`tests/dough/validate.cjs` builds nothing and reads `datum.html` and
`dough.html` from the repository root. Real full tick, native Canvas and the
browser DOM stubbed, frames of 1/64 s, a desk of 1440×900 (the stories at
1900×810), the worker of Wings thinking sixteen rehearsed frames a frame.
`tests/dough/validation.json` holds the figures.

- **The rule is the only change.** With it taken out and no thinking, the
  tour of changes and the chain through every page from every other are
  Datum's, the world and every drawing command, frame by frame (11,550 and
  25,950 frames).
- **The hive wets the pan**, with no thinking, every other frame while a
  change runs. Under a cell: the screen on a grid a quarter of a lattice unit
  apart, its perimeter a pixel in every 8 px, and its four corner squares (a
  lattice unit each). The sea's share of the pan, what the auction gives it,
  at its largest and on average; the mass, what the cells and the whitespace
  hold as their own, at its least.

  | the chain, 56 changes | Datum | Dough |
  |---|---|---|
  | screen under a cell | 58.9% | 70.1% |
  | perimeter under a cell | 46.6% | 58.7% |
  | corner squares under a cell | 49.8% | 58.6% |
  | the sea, on average | 26.7% | 13.0% |
  | the sea, at its largest | 83.0% | 61.1% |
  | the mass, at its least | 17.0% | 48.4% |

  | the tour, 25 changes | Datum | Dough |
  |---|---|---|
  | screen under a cell | 82.3% | 83.2% |
  | perimeter under a cell | 76.1% | 78.6% |
  | corner squares under a cell | 76.8% | 78.6% |
  | the sea, at its largest | 76.6% | 52.9% |
  | the mass, at its least | 23.4% | 45.6% |

- **Every page from every other, and the tour, with the worker thinking**:
  nothing waits or fractures, what is rehearsed is what is played, every
  change has one pace, every page at rest is exact and every cell drawn its
  own colour. Defects drawn (lurch, slivers, splits, near-collisions, start
  shock, one score):

  | | Datum | Dough |
  |---|---|---|
  | the chain, 56 changes | 84,857 | 119,453 |
  | of it, lurch | 13,776 | 23,352 |
  | slivers | 1,042 | 1,519 |
  | near-collisions | 115 | 133 |
  | start shock | 7,503 | 6,864 |
  | the tour, 25 changes | 16,125 | 24,934 |

  Dough is lower on 8 of the 56 changes and 9 of the 25. The worst against
  Datum: Petal to Jazz (467 to 3,943), Drift to Tide (268 to 2,523), Drift to
  Jazz (138 to 2,517).
- **In Chromium** (Playwright, the page itself with its worker, a desk of
  1440×900, the chain's first ten changes): Dough draws 153 to 193 frames in
  the 3.2 s after a click, its longest frame 24 to 60 ms, first motion 8 to
  61 ms after the click; Datum 159 to 193 frames, longest 26 to 90 ms, first
  motion 8 to 62 ms. No errors on either.
- **A Cue story is Datum's**: the page's world (every cell and whitespace:
  seat, claim, weight, state) within 1.1e-11 px and 5e-9 of a weight on every
  one of its 1,740 frames. A Tell and a Tell II story run to their end and
  home without a fractured cell (3,060 frames).

The first run of this mark was built from Facet and found a fault in the
sea's gauge there: with the sea small all through a change, the gauge ran
every other frame from a bracket with no root, and four cells between the two
images vanished and came back on alternate frames. That fix is Datum's, and
Dough is built from it.

## Known

- **The two images press on each other as they pass**, and the cells between
  them are squeezed and let go: lurch is 1.7 times Datum's over the chain and
  twice over the tour, and slivers half again. On Cohort's hand-over the
  closing image was a card before the two met, and nothing pressed. This is
  the cost of the mass being conserved; what to do with the pressure (a
  path that passes, a pace that lets one through) is a question for a mark of
  its own.
- **The whitespace in transit is still formless.** The sea is smaller
  (13% of the pan on average over the chain, Datum's 27%) but it is the same
  sea: where it is, the hive's edge is as it was.
- **Stories keep Datum's ground.** The ground rule holds on the page's own
  changes; a story choreographs its own whitespace, and keeps Datum's ground,
  cut from the page. The home scene a story starts from settles under Dough's
  rule, so its world is Datum's to floating noise, not to the bit, and the
  fields inside the cells, a flow of their own, take a path of their own from
  it.
- **The empty-site gauge** (Datum's Known) is unchanged.
- **Desk only.**

## Run

```bash
python3 tests/dough/build.py
node tests/dough/validate.cjs
```
