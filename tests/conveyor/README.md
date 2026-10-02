# Conveyor: Frame II

Baseline: Cohort, `cohort.html` on this branch, SHA-256
`708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Cohort, on a desk
(1440×900). It adds one scene, Frame II, beside Frame.

## What it proves

Frame lays the cells round the edge of the page with whitespace in the middle,
and holds them there. Frame II tests the frame as a conveyor: the same layout,
and then the cells go round it clockwise, gently, and keep going.

## How it works

- **It lands as Frame.** Frame II's rest is Frame's, and the change into it is
  Frame's frame by frame. The belt starts once the change has landed.
- **The belt is the frame's band**, read clockwise from the top left corner as
  eight pieces: four straights and four corners.
  - Each piece is measured by its area, in lattice units, and holds a stretch
    of the band's centre line: a straight one, or at a corner a quarter of an
    ellipse from one side's centre line to the next's.
- **Each cell holds a stretch of the belt as long as its own area**, the
  stretches one after another in the order the cells sat. They are placed as
  near their seats as that order allows, by the circular mean of the
  difference.
- **The belt moves by area.** Where the band is one row deep, at the top and
  the bottom, that is a walking pace: 28 px/s, the reel's own. Down the sides,
  where the band is two columns wide, it is slower, as a stream runs slower
  where its bed is wide. A lap takes about 3.4 minutes.
- **Each cell's seed is held on the centre line**, at the middle of its
  stretch, and the auction gives every cell its own area, as ever. Along a
  straight the cells are slices of the band, and round a corner they turn it
  as Voronoi cells do.
- **The middle is whitespace a cell never enters.** While the belt runs it is
  a wall, out of the auction, drawn exactly as its rectangle.
- **It starts from rest.** The belt gets up to speed over 3 s, and the seeds
  go from where they sat to the belt's line over the same.
- **Any change stops it**, and the cells go on from where they are.
  - If the middle's whitespace leaves, the wall stays as its own cell while it
    melts into the sea: it shrinks about its centre as the whitespace's own
    share does on the change's clock, and lets go when that is gone. The cells
    flow into the room it gives up.
  - If the whitespace goes on to a place in the next layout, the wall lets go
    at once.
- **Scope.** Every other scene, the pages and the stories are Cohort's to the
  bit.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame.

**Everything but Frame II is Cohort's.** With the rule in, the tour (11,550
frames) and the chain through every page from every other (25,950 frames)
are Cohort's to the last drawing command. A Cue story is too (2,040 frames).

**Frame II lands as Frame.** From Bento, every frame is Frame's until the change
has landed, 120 frames in; the belt starts on the next.

**The belt**, for a minute from when it is up to speed (3,720 frames):

| | |
|---|---|
| Cells undrawn, fractured, or drawn in the middle | 0 |
| Seeds going back, frame to frame | 0 |
| The fastest seed | 28 px/s |
| Frames whose auction ended more than 1% off a claim | 0 |
| Turns round the middle in the minute | 0.19 to 0.35 |

A lap takes about 3.4 minutes.

**Into Frame II and out of it**, with the worker thinking: Frame II, then a
page, Frame II, home, Frame II, Sidebar, Frame II, Bento. Nothing waited or
fractured, and 10 moves were laid bit for bit on their rehearsals (759
frames). Defects drawn, against the same changes with Frame on Cohort:

| Change | Frame, on Cohort | Frame II |
|---|---|---|
| Into Frame II | 29, 217, 27, 384 | 29, 217, 27, 370 |
| To Moss's page | 1,544 | 882 |
| Home | 177 | 918 |
| Sidebar | 388 | 983 |
| Bento | 174 | 336 |
| All | 2,940 | 3,761 |

Leaving Frame II starts from cells on their way round, where Frame's start
from rest: three of the four ways out draw more, and the page fewer.

**In Chromium**, headless, 10 s of each once landed: Frame II drew 464 frames
(the longest 42 ms), Frame on Cohort 526 (34 ms). No errors.

## Known

- **Leaving the belt costs more than leaving Frame at rest**: home 918 against
  177, Sidebar 983 against 388. Tried and not in:
  - *Letting the middle go at once*: its whitespace rejoined the auction at its
    old resting sites, the middle's border moved in one frame, and the cells
    beside it jumped 6 to 36 px (5,000 defects over the same changes).
  - *A wall shrinking on the change's clock whatever the whitespace does*:
    while it was a wall its share was not the sea's, and when it let go 23
    lattice units became sea at once; and opening a page, where the
    whitespace goes on, the wall was in the way (2,322 to Moss's page).
- **The belt is the auction without the sea.** Nothing is changing while it
  runs, so the sea is not in; cells meet the middle along the wall's straight
  sides.
- **The sides run at half the pace of the top and the bottom.** That is the
  belt moving by area. A belt moving by length would have the cells on the
  sides stretch along it and the ones at the top squeeze.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Conveyor has no card yet.

## Run

```bash
python3 tests/conveyor/build.py
node tests/conveyor/validate.cjs
```
