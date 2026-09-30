# Amoeba: the hive is one body

Baseline: Membrane, `membrane.html` on this branch, SHA-256
`ace6b09cbad969678114efa8cfd7df089c014b24618a7a879aa38434a0efcd68`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Membrane. From this mark on,
the class is iterated and measured on a desk (1440×900) only; a phone
version waits for whatever wins.

## What it proves

Membrane had two flaws.

- **The cells turned into blobs.** Membrane cut every travelling cell by its
  own reach, a disc about its seed. Wherever a cell's ground reached further
  than its disc, the sea took it: its outer side, and every corner where it
  met its neighbours. Cells on the hive's edge went round, and the sea showed
  through between them.
- **A change broke the page's structure at once, and then moved.**
  - The rules of the sea ran on clocks of their own from the ask: a leaving
    whitespace melted into the sea over 0.3 s, and a cell went liquid over
    the same.
  - The page's hero gave up, in the first frame, its share of the text's room
    (Tandem's page rule). Opening Moss from the sidebar, that is 28,000 px²
    handed from the image to the text's whitespace in one frame: the hero
    halves, and its neighbours jump 50 px. Tempo does the same.

Amoeba tests whether the hive can be one body, with one smooth edge and
Voronoi cells inside it, and a change that starts from the page as it was.

## How it works

- **The sea is soft.** The sea bids zero everywhere, and a cell's bid at a
  point is its power there, as ever. But the hive bids as one body.
  - At a point, the hive's presence is the sum over its cells of
    exp(−bid / T), and the sea wins where the presence is below one.
  - A cell alone is still exactly its disc: its bid is zero at its reach.
  - Cells side by side are one hill, so the notches between their reaches,
    and the holes where three reaches failed to meet, are the hive's. Only
    the hive's rim meets the sea, and every cell inside is a polygon.
  - The auction is still exact, with the Jacobian of the soft edge: a unit of
    a cell's weight moves the edge by that cell's share of the presence
    there, over how steeply the presence falls.
- **How T was chosen.** T is 2r², r the cell's own radius: each cell's bell
  is a Gaussian as wide as the cell. Two equal Gaussians make one hill as
  long as their centres are no more than two widths apart, and two equal
  cells that touch have their seeds two radii apart. So two cells that touch
  are one hill, never two. Nothing else is chosen.
- **A cell the edge crosses is cut on a grid** over it, exact to the cell's
  own sides.
  - Each square holds the part of it inside the hive, the presence at its
    corners taken as linear along its sides, and each part is cut to the
    cell.
  - The squares are 4 to 64 px, a power of two, 8 to 16 across the cell, and
    aligned to the page, so a moving cell is cut on the same grid and its
    edge moves only as the presence does.
  - A cell wholly inside the hive is not cut.
- **Everything the sea does runs on the change's own clock.**
  - A cell is liquid as far as it is between its two rests: 4p(1 − p) of its
    progress, none at either rest, all of it halfway. A liquid cell keeps its
    plan its own radius clear of the screen, as on Membrane.
  - The whitespace melts into the sea by the same measure of the change's
    progress, read off its paced travellers. The sea comes in as gently as
    the change sets off, and is gone as it lands.
  - Only a cell has a reach. Whitespace that is still its own cell keeps its
    straight borders.
  - A sea too small to see appear stays out, as a seed does.
- **The hero gives back the text's room on its own clock.** What the image
  holds of the text's rectangle as it sets off, it gives back as it goes,
  and no faster than it leaves it. Nothing is handed over at the ask.
- **The hive keeps its size.** Nothing is given to the sea but whitespace.
  Membrane's shrinking, down to half a cell's size while it touched the
  screen, is gone, and with it the one number that was a choice.
- **Scope.** The page's own changes. The stories keep their own whitespace
  and choreography, and the fields inside cells are unchanged. Thinking and
  pace are Tempo's; a rehearsal runs the same sea.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame on every mark alike.

**The hive as one body**, over every frame while the sea is in:
- the share of a travelling cell's outline that lies on the sea;
- discs: cells more than nine tenths on the sea, a frame;
- sea shut in among the cells (meeting neither whitespace nor the screen's
  edge), in px²-frames, on a grid of 8 px.

| | Membrane | Amoeba |
|---|---|---|
| Outline on the sea, tour of 25 changes | 24.8% | 7.5% |
| Discs a frame, tour | 0.168 | 0 |
| Sea shut in, tour | 25,385,344 | 345,664 |
| Outline on the sea, 56 page-to-page changes | 29.9% | 9.6% |
| Discs a frame, page to page | 0.294 | 0.0006 |
| Sea shut in, page to page | 6,013,312 | 1,088 |

- What is left shut in on the tour (343,104 px²-frames) is the change from
  the frame to the sidebar: the frame's layout is a ring, and its centre
  melts into the sea inside it.
- The only discs are six frames of one cell: Aurora, the page's old hero,
  crossing the screen alone on its way out. A cell alone is its disc.

**A change starts gently.** On the first frame of every change: the area the
drawn cells hand each other, as seen on the screen, plus every cell's drawn
movement beyond its seed's, at 100 px² a pixel.

| | Tempo | Membrane | Amoeba |
|---|---|---|---|
| Tour of 25 changes | 171,750 | 582,171 | 30,093 |
| 56 page-to-page changes | 1,028,850 | 1,460,760 | 357,483 |

On the tour that is 17,084 px² and 130 px of movement in all. The largest
share left is going home from Dune (11,163), where the gallery's cards come
back on as specks, as on Tempo.

**The screen leaned on:** the length of the travelling cells' outlines lying
along the screen's edges, summed over every frame while a change runs.

| Pixel-frames | Tempo | Membrane | Amoeba |
|---|---|---|---|
| Tour of 25 changes | 6,038,845 | 2,461,805 | 5,647,489 (−6.5%) |
| 56 page-to-page changes | 31,541,332 | 9,498,729 | 24,428,683 (−23%) |

The percentages are against Tempo. Membrane's hive shrank off the screen;
this one keeps its size.

**Defects drawn** (lurch, slivers, splits, near-collisions, start shock):

| | Shoal | Tempo | Membrane | Amoeba |
|---|---|---|---|---|
| Tour of 25 changes | 25,352 | 22,226 | 23,630 | 23,575 |
| 56 page-to-page changes | 165,165 | 119,095 | 96,234 | 136,779 |

- **The tour** is on a par with Membrane and 6% above Tempo.
- **The page-to-page changes** are 42% above Membrane and 15% above Tempo:
  - *Slivers* (thin cells, 50 a frame) are as many as on Tempo, 1,161
    frames against 1,173. Membrane had 412: its cells on the edge were
    round, and round cells are not thin.
  - *Splits* are new: 47 frames (9,380) of a cell the hive's edge cuts in
    two.
  - *Lurch* is 42,626, against 39,586 on Tempo and 23,995 on Membrane. The
    worst change is Dune → Tide (17,345 against 3,812), where eleven of the
    gallery's cards leave as specks at once and for eight frames the
    auction does not converge.
  - *The start shock* is 11,747, against 6,569 on Tempo and 37,514 on
    Membrane.
- **Thinking:** 25 moves on the tour and 122 on the page-to-page changes;
  none late. 10,946 frames were laid bit for bit on the worker's rehearsal of
  its move.

**How the cells move** on the tour: the seeds' acceleration is 425 px/s² on
the mean and 1,438 at the 99th percentile (Tempo: 376 and 1,312); a cell's
peak speed over its average is 1.90 at the median (Tempo: 1.82).

**In Chromium**, headless, 12 changes, with the budget measured:

| | Tempo | Membrane | Amoeba |
|---|---|---|---|
| Frames drawn | 1,817 | 1,624 | 1,472 (−9% on Membrane) |
| Longest frame | 357 ms | 80 ms | 169 ms |
| Moves | 12 | 4 | 4 |
| First motion after the ask | 8–57 ms | 16–105 ms | 5–66 ms |

- **Errors:** none.
- **The soft sea costs frames.** A cell the hive's edge crosses is cut on
  its grid on every try of the auction, and the worker's rounds cost more,
  so fewer answers come in time. In node, over five changes with no
  thinking, a frame costs 11.9 ms, against 10.0 on Membrane and 3.6 on
  Tempo.

## Known

- **The page-to-page changes draw more defects** (see Measured): slivers
  back at Tempo's level, splits, and specks the auction cannot hold while
  many leave at once.
- **A cell leaving on its own, tried and not in.** A card leaving the page
  was made none of the hive's: no bell of its own, cut by its own disc. On
  Dune → Tide the auction then converged far better (the worst frame 96%
  off its areas, not 680%), but the page-to-page changes as a whole drew no
  fewer defects (135,815), and the tour 5% fewer.
- **Shrinking, tried and not in.** With the soft sea, Membrane's shrinking
  (down to half a cell's size while it touches the screen) no longer makes
  blobs: the hive floats clear of the screen as one rounded body. In a
  prototype, on the tour with thinking on the page, the screen was leaned on
  for 1.76M pixel-frames, against 2.32M without shrinking and 2.63M on
  Tempo. But the flock's cells collapsed to specks and jumped, the tour drew
  7% more defects, and the least size is still a chosen number. It is the
  next mark's to settle.
- **Whitespace crossing the hive leaves a pocket among its cells**, as on
  Tempo: a whitespace's sites travel to their places through the hive, and
  whitespace bids as its own cell until it has melted.
- **A lone cell is its disc.** Only cells side by side are one hill.
- **The gallery's cards come back on as specks** going home, as on Tempo.
- **Inherited from Wings:** the fields inside cells are not rehearsed, and a
  move can slow a cell and let it catch up, not hurry one.
- **No phone.** The class is iterated on a desk; a phone version waits for
  whatever wins.
- **The landing page is unchanged.** Amoeba has no card yet.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and the worker of Wings headless (a second copy of the page's script,
its messages crossing as structured clones), thinking 16 rehearsed frames a
frame. Tempo and Membrane run beside it under the same worker. Everything is
on a desk (1440×900; the Cue story at 1900×810).

It runs two sets of changes:
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **The sea and the hero's clock are the only other changes.** With no
  budget, and the sea, the hero's clock and Tempo's pace taken out, every
  frame of the tour is Shoal's, the world and every drawing command: 11,550
  frames.
- **Nothing is sea at rest.** When each change is over, no whitespace's claim
  is the sea's and no cell is liquid.
- **The hive is one body.** On the tour and on the page-to-page changes,
  less of the cells' outlines lies on the sea than on Membrane, fewer cells
  are discs, and less sea is shut in among them.
- **A change starts gently.** Its first frame changes the drawn cells less
  than on Tempo and on Membrane, on the tour and on the page-to-page
  changes.
- **The hive leans on the screen less than on Tempo**, on both.
- **Every change of the page has one pace**, as on Tempo.
- **Nothing waits.** From the ask, the page's clock runs every frame.
- **What the worker rehearses is what the page plays**, to the bit, frame by
  frame, from each move until the next acts, while the page and its
  rehearsal both have the change running.
- **With no worker the hive thinks on the page**, makes moves, and plays what
  it rehearsed there, frame by frame: 1,306 frames laid on the tour.
- **Still correct.**
  - Nothing fractures on any frame. The shape rule knows the hive's edge: a
    cell's side on the sea, as the auction handed it back, is one smooth
    edge, and its points are no corners.
  - Every page at rest is exact as on Shoal: the image on its rectangle and
    covering it, the text covering its own with the title in it, the
    whitespace exact, no field, one site to a cell.
- **A story keeps its own pace and its whitespace, and is not thought about.**
  - No sea while a Cue story is told, and no cell is liquid.
  - With the sea, the hero's clock and the pace taken out, a Cue story is
    Shoal's frame by frame (2,040 frames, the world and every drawing
    command).
  - Cue's own story checks pass.
  - A Tell and a Tell II story run to their end and home without a fractured
    cell.

The defects drawn are reported against Membrane's, Tempo's and Shoal's, not
held to them.

## Run

```bash
python3 tests/amoeba/build.py
node tests/amoeba/validate.cjs
```
