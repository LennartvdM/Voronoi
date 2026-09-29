# Membrane: the hive in a membrane of its own

Baseline: Tempo, `tempo.html` on this branch, SHA-256
`17d8b48fc77404b6331da14e2184a9f892eaec7aa563028403c6064ea30dff9f`.
The builder reads that file from the repository root and checks the hash.

**The first mark of a new class.** Every mark before it tessellates the whole
screen on every frame. From Membrane on, a changing page is a hive in a sea.
Marks of this class are measured against each other, starting with this one,
not against Shoal's defect counts.

## What it proves

Every mark so far shared the whole screen out on every frame: the cells took
their claims, and the whitespace took the rest as cells of its own, seeded and
invisible. Whitespace built that way is a solid.
- Its straight borders pushed the travelling cells flat against the edges of
  the screen.
- A change always had to work out its edges as a group, and never looked
  like a swarm on its way somewhere.

Membrane tests whether the hive can be bounded by its own cells instead: a
membrane that is nothing but the cells' reaches together, drawn and steered by
nothing.

## How it works

- **The sea.** While the page changes, its whitespace is sea, as far as the
  whitespace has not settled into its place.
  - The sea bids the same everywhere, so a travelling cell reaches only as far
    as its own bid is below it: a disc about its seed, the size its claim
    needs.
  - Where cells meet they share a straight edge, as ever; where a cell faces
    the sea, its border is its own reach.
  - The auction is still exact: the sea is one more claim beside the cells',
    with a Jacobian term for each edge on the sea. The reach is cut as a
    64-sided polygon whose inradius is the reach, so the area and its
    derivative are exact for the shape drawn (within half a pixel of the
    circle up to a reach of 400 px).
- **Whitespace settles back.** A whitespace has its own cell only as far as
  it has settled:
  - all of it at rest, so every layout lands exactly as on Tempo;
  - none of it while it closes: it melts into the sea over the melt time, as
    a cell melts;
  - none of it while it opens, until the cells leaving it land, and then it
    settles in on its own crystal, which reads their clocks.
- **The swarm feels the screen.** A cell is liquid from when it has melted
  until it locks as it lands (the lock's own clock).
  - A liquid cell keeps its plan its own radius clear of the screen's edges.
  - If it still touches the screen, it gives up its size to the sea, down to
    half, and takes it back once clear, each over the melt time.
  - It is its whole size again as it locks, so it lands exactly.
  - The hive shrinks only as far as it needs to float. No cell is told to.
- **Scope.** The page's own changes. The stories keep their own whitespace
  and choreography, and the fields inside cells are unchanged.
- **Thinking and pace** are Tempo's. A rehearsal runs the same sea.

The header carries no captions.

## Measured

The validator's figures. Frames are 1/64 s, and the worker of Wings thinks 16
rehearsed frames a frame on Tempo and on Membrane alike.

**The screen leaned on:** the length of the travelling cells' outlines lying
along the screen's edges, summed over every frame while a change runs.

| Pixel-frames | Tempo | Membrane |
|---|---|---|
| Tour of 25 changes, 1440×900 | 6,038,845 | 2,461,805 (−59%) |
| Tour of 25 changes, 390×720 | 3,207,559 | 1,739,302 (−46%) |
| 56 page-to-page changes, 1440×900 | 31,541,332 | 9,498,729 (−70%) |
| 56 page-to-page changes, 390×720 | 18,935,440 | 7,056,751 (−63%) |

**Defects drawn** (lurch, slivers, splits, near-collisions, start shock):

| | Shoal | Tempo | Membrane |
|---|---|---|---|
| Tour of 25 changes, 1440×900 | 25,352 | 22,226 | 23,630 (+6%) |
| Tour of 25 changes, 390×720 | 18,528 | 17,752 | 20,569 (+16%) |
| 56 page-to-page changes, 1440×900 | 165,165 | 119,095 | 96,234 (−19%) |
| 56 page-to-page changes, 390×720 | 62,631 | 41,518 | 36,973 (−11%) |

The percentages are against Tempo.

**Thinking:** 23 and 30 moves on the tours, 145 and 139 on the page-to-page
changes; none late. 25,801 frames were laid bit for bit on the worker's
rehearsal of its move.

**In Chromium**, headless, 12 changes a size, with the budget measured:

| | Frames drawn, Tempo | Frames drawn, Membrane | Longest frame, Tempo | Longest frame, Membrane | Moves, Tempo | Moves, Membrane |
|---|---|---|---|---|---|---|
| 1440×900 | 1,840 | 1,683 (−8.5%) | 40 ms | 67 ms | 15 | 6 |
| 390×720 | 1,879 | 1,837 (−2%) | 58 ms | 71 ms | 12 | 0 |

- **First motion** came 12–88 ms after the ask, against 10–61 ms on Tempo.
- **Errors:** none.
- **The sea costs frames and thinking.** A reach is cut as up to 64 sides,
  so the diagram and the cells' outlines carry more vertices, and the
  worker's rounds cost more, so fewer answers come in time. On a desk the
  page draws 8.5% fewer frames.

## How the least size was chosen

`SEA_FIT_MIN`, the least a liquid cell shrinks to while it cannot get clear of
the screen, is the one new number that is a choice. It trades freedom from
the screen against defects. Measured on the tour in a prototype, with thinking
on the page at a budget of 16:

| Least size | Screen leaned on, desk | Screen leaned on, phone | Defects, desk | Defects, phone |
|---|---|---|---|---|
| 1 (never shrinks) | 2.22M | 1.45M | 20,099 | 19,005 |
| 0.75 | 1.62M | 1.07M | 22,634 | 18,378 |
| 0.5 | 1.34M | 0.89M | 23,927 | 20,034 |
| 0.25 | 1.20M | 0.76M | 25,302 | 21,957 |

Half its size is the middle of that curve: most of the freedom, and short of
where the defects climb fastest. It is a choice, and the next mark of the
class should let the hive make it.

## Known

- **The tours draw more defects than Tempo** (+6% on a desk, +16% on a
  phone). A cell that shrinks and regrows changes its size and its place at
  once, so lurch and start shock rise. The returns home, into the full-bleed
  layout, add the most. The page-to-page changes draw fewer.
- **A hive too big to float still leans on the screen.** Mid-way to the
  sidebar the cells cover about half the screen, and a blob that size cannot
  be clear of a 900 px window even at half size.
- **Tried, and not in.**
  - Drawing the plan together toward the swarm's centre changed nothing: a
    layout of rectangles is already about as compact as its cells' areas
    allow. The hive is not loose, it is big.
  - Gravity by centrality: each cell drawn toward its cluster's cells, each
    as hard as it is central, whatever its size. As a force on the seeds it
    barely moved the hive off the screen and doubled the lurch: the pull
    jumps whenever a cell joins or leaves a cluster, and a seed's spring holds
    it within about 40 px of its plan anyway. Its place is splitting and
    merging the hive into several, planned, not freeing it from the screen.
- **The shape rule changed.** A cell's own reach is one smooth side, and a
  cell rounded all over has no corner to break. Tempo's rule counted a disc's
  64 sides as corners.
- **Inherited from Wings:** the fields inside cells are not rehearsed, and a
  move can slow a cell and let it catch up, not hurry one.
- **The landing page is unchanged.** Membrane has no card yet.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and the worker of Wings headless (a second copy of the page's script,
its messages crossing as structured clones), thinking 16 rehearsed frames a
frame. Tempo runs beside it under the same worker.

It runs two sets of changes, each on a desk (1440×900) and a phone
(390×720):
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **The sea is the only other change.** With no budget, and both the sea and
  Tempo's pace taken out, every frame of the tour is Shoal's, the world and
  every drawing command: 11,550 frames on a desk and on a phone.
- **Nothing is sea at rest.** When each change is over, no whitespace's claim
  is the sea's, no cell is liquid, and every cell bids its whole claim.
- **The hive leans on the screen less.** The sea is there while changes run,
  and the travelling cells' outlines lie along the screen's edges for fewer
  pixel-frames than on Tempo: on the tour and on the page-to-page changes, at
  both sizes.
- **Every change of the page has one pace**, as on Tempo.
- **Nothing waits.** From the ask, the page's clock runs every frame.
- **What the worker rehearses is what the page plays**, to the bit, frame by
  frame, from each move until the next acts, while the page and its
  rehearsal both have the change running. The fields inside cells are not
  rehearsed (Wings), so the two can part by a frame on when a change is
  over, and the page's gallery starts to flow then; neither is the change.
- **With no worker the hive thinks on the page**, makes moves, and plays what
  it rehearsed there, frame by frame.
- **Still correct.**
  - Nothing fractures on any frame. The shape rule now knows the membrane: a
    cell's own reach is one smooth side (its points all stand at one radius
    from the cell's seed), and a cell rounded all over, a disc or a lens,
    has no corner to break.
  - Every page at rest is exact as on Shoal: the image on its rectangle and
    covering it, the text covering its own with the title in it, the
    whitespace exact, no field, one site to a cell.
- **A story keeps its own pace and its whitespace, and is not thought about.**
  - No sea while a Cue story is told, and no cell gives up size.
  - With the sea and the pace taken out, a Cue story is Shoal's frame by frame
    (2,040 frames, the world and every drawing command).
  - Cue's own story checks pass on a desk and a phone.
  - A Tell and a Tell II story run to their end and home without a fractured
    cell.

The defects drawn are reported against Tempo's and Shoal's, not held to them.

## Run

```bash
python3 tests/membrane/build.py
node tests/membrane/validate.cjs
```
