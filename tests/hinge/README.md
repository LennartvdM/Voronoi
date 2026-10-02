# Hinge: Frame II's cells turn the corners as solid fronts

Baseline: Conveyor, `conveyor.html` on this branch, SHA-256
`915ce50299253f429c9f2d20a32fa792412c2088d8f07fb1d7b2409d18f142d5`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Conveyor, on a desk
(1440×900). It changes Frame II and nothing else.

## What it proves

The owner found Conveyor's belt working well except at the corners: the large
cells drip round them. A cell's front could stay solid and turn about the
corner instead.

On Conveyor each cell's seed rides the band's centre line, and the auction cuts
the band between the seeds. Along a straight that cut is square across the
band. Round a corner it is a Voronoi bisector, and it passes where the seeds'
weights put it, not through the corner the cells turn about. So a cell slides
round the bend a part at a time.

Hinge tests a belt whose cells are the band itself, cut by fronts that turn
about the middle's corners.

## How it works

- **A front is a cut across the band**, at an area along the belt.
  - On a straight it is square across the band.
  - In a corner block it is a ray from the middle's corner, the hinge. It
    swings clockwise from the cut of the side it comes from to the cut of the
    side it goes to.
  - It swings by area. The block is the fan of its two outer edges about the
    hinge, and each edge holds one lattice unit of it, so the front sweeps the
    block at the belt's own pace.
- **Each cell is the band between its two fronts**, exactly, at its share of
  the band. That is a slice of a straight, a sector of a corner, or both,
  joined along the front they share. The cells tile the band.
- **The fronts start where the cells sat.** Each cell's stretch is laid in the
  order the cells sat, as near the stretches they held at rest as the order
  allows. The stretches are read where the cells meet the page's edge, where a
  front's place is steady; next to a hinge every front of its corner passes
  through the same point.
- **While the belt runs the cells are holes in the auction's ground**, drawn
  exactly as cut, and the middle is a wall. The auction has nothing to do.
- **The cells come onto the belt from the shapes they rest in**, as the belt
  gets up to speed over 3 s: each is a blend from its resting shape to its
  stretch. At an odd count, the frame puts a cell in a corner of the page,
  which no stretch can be. It changes shape over the 3 s instead of in a frame.
- **Any change stops the belt.** The middle lets go at once, and the cells go
  back to the auction on the change's own clock, the one whitespace melts into
  the sea on.
  - Each cell stays a hole whose shape goes, piece by piece, from its stretch
    to the cell the auction would give it, as far as the sea has come in.
  - Its target comes from a shadow auction run first in the frame, so it is
    this frame's cell, not the last.
  - Where one cell comes in and another goes, the one coming in has the ground.
  - When the sea is all in, halfway through the change, every cell is its
    auction cell, and they all close in one frame. The auction takes up the
    weights that drew them.
- **The ground is the one the auction will have.** While Frame II's cells are
  holes, the auction's ground is what it will be when they close: the box the
  change may overflow into, unless a wall of the page's own (a page's reel)
  keeps it to the page. Cut from the page alone while they were holes, it lost
  a third of the room the frame they closed, and every cell grew by as much at
  once. On the way back, ground nobody bids for is whitespace, the sea's.
- **Scope.** Every other scene, the pages and the stories are Conveyor's to the
  bit.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame.

**Everything but Frame II is Conveyor's.** With the rule in, the tour
(11,550 frames) and the chain through every page from every other
(25,950 frames) are Conveyor's to the last drawing command. A Cue story is
too (2,040 frames).

**Frame II lands as Frame.** From Bento, every frame is Frame's until the change
has landed, 120 frames in; the belt starts on the next.

**The belt**, for a minute from when it is up to speed (3,721 frames):

| | Conveyor | Hinge |
|---|---|---|
| Fronts between two cells in a corner block | 7,294 | 7,252 |
| Of those, more than 2 px off the middle's corner | 6,980 | 0 |
| The furthest off | 116.9 px | 0.01 px |
| On average | 33.76 px | 0 px |
| A cell drawn off its stretch | (the auction's cells) | 0.00743 px |
| The cells off the band | | 0.000734 px |
| Cells undrawn, fractured, or drawn in the middle | 0 | 0 |
| Seeds going back, frame to frame | 0 | 0 |
| The fastest seed | 28 px/s | 28 px/s |
| Turns round the middle in the minute | 0.187 to 0.354 | 0.187 to 0.354 |
| The largest move as the belt starts | 3.508 px | 2.037 px |

"Off its stretch" is the area between a cell's drawing and its stretch over the
length of its outline, which the outline builder holds to 0.05 px.

**At every count tried**, 12 s of Frame II each. Nothing is undrawn, fractured
or in the middle, and every cell is its stretch:

| Cells | Corner fronts | Off the corner, Hinge | Off the corner, Conveyor | Belt starts, Hinge | Belt starts, Conveyor |
|---|---|---|---|---|---|
| 4 | 736 | 0 | 474 (up to 80.18 px) | 0.008 px | 0 px |
| 5 | 864 | 0 | 792 (up to 80.09 px) | 0.008 px | 0.005 px |
| 6 | 1,095 | 0 | 1,056 (up to 175.16 px) | 0.011 px | 0.003 px |
| 7 | 1,342 | 0 | 1,408 (up to 173.21 px) | 0.01 px | 0.014 px |
| 8 | 1,492 | 0 | 1,376 (up to 112.7 px) | 0.008 px | 0.001 px |
| 9 | 1,918 | 0 | 1,975 (up to 131.5 px) | 0.021 px | 0.02 px |
| 10 | 1,504 | 0 | 1,430 (up to 106.76 px) | 0.007 px | 0.001 px |
| 12 | 1,816 | 0 | 1,650 (up to 76.35 px) | 2.037 px | 3.508 px |
| 13 | 2,054 | 0 | 2,250 (up to 133.17 px) | 0.029 px | 0.028 px |
| 16 | 1,882 | 0 | 1,812 (up to 61.26 px) | 0.065 px | 0.027 px |
| 20 | 1,890 | 0 | 1,840 (up to 56.64 px) | 0.012 px | 0.002 px |
| 25 | 2,557 | 0 | 2,800 (up to 123.41 px) | 0.01 px | 0.01 px |
| 30 | 2,524 | 0 | 2,448 (up to 82.07 px) | 0.014 px | 0.02 px |

At 12 cells the start's 2.0 px is the landing's own last settle; Conveyor's is
3.5 px.

**Leaving the belt**, as it gets up to speed (3.5 s after the ask), 12 s after
and 45 s after, for four places. The largest move of any cell in a frame over
the first 4 s, teleports over 300 px aside:

| To | After | Conveyor | Hinge |
|---|---|---|---|
| Bento | 3.5 s | 42.2 px | 16.6 px |
| Frame | 3.5 s | 9.2 px | 9.2 px |
| Sidebar | 3.5 s | 25.7 px | 16.7 px |
| Moss's page | 3.5 s | 40.6 px | 46.8 px |
| Bento | 12 s | 44 px | 12.7 px |
| Frame | 12 s | 42.5 px | 10 px |
| Sidebar | 12 s | 23.8 px | 20.3 px |
| Moss's page | 12 s | 37.9 px | 31.1 px |
| Bento | 45 s | 54.6 px | 11.8 px |
| Frame | 45 s | 163.4 px | 9.3 px |
| Sidebar | 45 s | 31.3 px | 22.3 px |
| Moss's page | 45 s | 126.3 px | 19.3 px |
| **Largest** | | **163.4 px** | **46.8 px** |
| **Summed** | | **641.5 px** | **226.1 px** |

Nothing fractured. A cell on its way onto the belt or back is a blend of convex
shapes, so it is judged by its dents, not by how many corners it has.

**Into Frame II and out of it**, with the worker thinking: Frame II, then a
page, Frame II, home, Frame II, Sidebar, Frame II, Bento. Nothing waited or
fractured, every page at rest was exact, and 8 moves were laid bit for bit on
their rehearsals (657 frames). Defects drawn:

| Change | Conveyor | Hinge |
|---|---|---|
| Into Frame II | 28 | 28 |
| To Moss's page | 882 | 631 |
| Into Frame II | 217 | 217 |
| Home | 918 | 9 |
| Into Frame II | 27 | 27 |
| Sidebar | 983 | 102 |
| Into Frame II | 370 | 370 |
| Bento | 336 | 8 |
| **All** | **3,761** | **1,391** |

**In Chromium**, headless, three runs: 10 s of the belt once landed, then 3.2 s
of leaving for Bento.

| | Conveyor | Hinge |
|---|---|---|
| Belt: frames drawn | 552, 546, 519 | 571, 576, 562 |
| Belt: the longest frame | 35, 37, 37 ms | 27, 32, 30 ms |
| Leaving: frames drawn | 74, 77, 78 | 70, 78, 75 |
| Leaving: the longest frame | 407, 140, 387 ms | 299, 316, 110 ms |
| Errors | none | none |

## Known

- **One way out moves a cell further than on Conveyor.** Opening Moss's page
  3.5 s after the ask, one frame moves a cell 46.8 px, against Conveyor's 40.6
  px. The cells close on the hulls of their auction cells, and in that frame the
  sea's curved edge had made one of them concave (32,353 px² against a hull of
  51,275). Tried and not in:
  - *following the auction on a hole's clock and closing once the change has
    landed*: Frame II to Frame moved up to 30 px against 10;
  - *closing only on a frame where every cell is within 1% of its hull*: they
    closed late and moved up to 83 px;
  - *cutting the hull's pockets in from their lids*: a sliver broke the
    garment's offset.
- **On the way back the cells are blends of convex shapes.** Their sides are
  straight, and their sides on the sea are chords of the auction's curves until
  they close.
- **Going back costs more in node, not in Chromium.** Leaving for Bento, the
  first 72 frames cost 69 to 79 ms a frame in node against 41 to 51 on Conveyor.
  The shadow auction does Conveyor's auction work; the rest is building,
  cutting and drawing the cells on their way. On the belt it is 2.9 ms a frame
  (median) against 2.6. In Chromium Hinge draws more frames on the belt, and
  about as many leaving it.
- **The drawing holds to 0.05 px, not to the bit.** A front within a hair of a
  corner block's edge leaves a sliver about 0.1 px wide, which the outline
  builder's tolerance drops.
- **The stretches are laid once.** Each cell's stretch is its claim when the
  belt starts. The claims settle on afterwards by up to 1.5e-6 of a share.
- **At an odd count a corner cell changes shape as the belt starts.** The frame
  puts it in a corner of the page, which no stretch can be. It goes to its
  stretch over the belt's first 3 s.
- **The ground rule is Frame II's only.** Elsewhere, when the last wall or hole
  goes, the auction's ground still grows from the page to its box at once, as
  in Conveyor and Cohort.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Hinge has no card yet.

## Run

```bash
python3 tests/hinge/build.py
node tests/hinge/validate.cjs
```
