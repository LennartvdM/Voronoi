# Slate: the image is its own shape

Baseline: Cohort, `cohort.html` on this branch, SHA-256
`708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Cohort, on a desk
(1440×900). It answers the image's sphere. Apace, built from Cohort beside it,
answers the screen.

## What it proves

While a page changes, each cell reaches into the sea as far as its bell: a
presence that falls off with the square of the distance from its seed, so its
level lines are circles and a lone cell is its disc. The image is the largest cell and the one most often
alone, so it travelled as a sphere.

Slate tests the image reaching as its own shape instead.

## How it works

- **The image's bell is its own shape.** The two images of a change to or
  from a page, the one that closes and the one that opens, measure distance
  from their seeds by the square of the L4 norm of the offset, taken in their
  own proportions, instead of the square of the distance. Their bells' level
  lines are rounded rectangles with the image's sides, not circles.
  - Of the same weight such a bell takes in an area 3.708 times its weight,
    where a disc's takes in π times; its width is set from that, as a
    disc's is.
  - The proportions turn from those of the seat the image leaves to those of
    the seat it takes, geometrically, as its size turns from the one to the
    other: an image that closes takes a card's proportions as it takes a
    card's size.
  - Everything else is Cohort's: the cards keep their discs, the images
    still meet them as one body, and the image's place in the diagram is
    found as before.
- **Scope.** Only a change to or from a page. Home's scenes and the stories
  are Cohort's to the bit.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame on both marks alike. The
page-to-page changes are a chain through all 56 ordered pairs of the eight
kinds of page; the tour is home's scenes, home to a page of every kind and
back, and two changes from page to page.

**The images' shape**, with the rule alone (no thinking), over the tour and
the chain (82 changes), on every frame of the middle half of a change: each
image's drawn area over its bounding box's on the screen. A disc fills
0.785 of its box and a rectangle all of it.

| | Cohort | Slate |
|---|---|---|
| Images larger than 60,000 px² | 0.776 | 0.815 |
| All images | 0.685 | 0.703 |
| Corners of an image's outline | 18.7 | 17.9 |

Going home the image's shape changes nothing the scorer sees: the tour's 8
changes home draw exactly Cohort's counts. Opening a page from home, 6 of the
8 differ.

**Defects drawn** (lurch, slivers at 50 a frame, splits at 200, near-
collisions at 100, start shock):

| | Cohort | Slate |
|---|---|---|
| The tour | 26,377 | 24,173 (−8%) |
| The chain of 56 page-to-page changes | 106,515 | 149,406 (+40%) |
| Lurch | 35,580 | 68,298 |
| Sliver frames | 830 | 904 |
| Split frames | 27.9 | 72.0 |
| Near-collisions | 117 | 115 |
| Start shock | 12,125 | 9,984 |
| The 14 changes to or from the essay | 41,563 | 84,011 |
| The other 42 | 64,952 | 65,396 |

All of the chain's cost is the essay's. Its image is a band nearly three
times as wide as it is tall, and leaving it, the band's bell stays a band
while the image is still large: Dune to Jazz draws 16,575 against 4,130, and
Dune to Aurora 12,102 against 2,703. The other 42 changes draw within 1% of
Cohort, fewer on 18 of them.

Started 0, 10 and 20 frames later than the validator's, with the hive
thinking 16 frames a frame on the page (a prototype harness, not the
validator's worker), Cohort's chain drew 129,743, 108,873 and 110,721, and
Slate's 139,735, 137,190 and 120,886.

**The screen leaned on** is Cohort's within 1%: 17.88M px-frames against
17.74M on the chain, 5.35M against 5.40M on the tour.

Thinking: on the chain 119 moves, none late, and 9,073 frames laid bit for
bit on the worker's rehearsal of its move; on the tour 25 moves, none late,
1,527 frames; with no worker, on the page, 28 moves.

**In Chromium**, headless, from home to Drift, then page to page through
Ember, Tide, Moss, Petal, Aurora, Dune, Jazz and Drift, and home; two runs
of each:

| | Cohort | Slate |
|---|---|---|
| Frames drawn in 32 s | 1,608 · 1,544 | 1,490 · 1,553 |
| Longest frame | 248 ms · 266 ms | 273 ms · 264 ms |
| First motion after the ask | 9–75 ms | 8–73 ms |
| Errors | none | none |

## Known

- **A bell that is not a disc disagrees with the diagram it is cut from.**
  A cell's side in the power diagram is where two cells' squared distances,
  less their weights, are equal: the measure of a disc's bell. The image's
  bell measures distance otherwise, so its rounded corners reach past the
  sides its weight gives it and are cut off there, and the image is drawn
  in two pieces more often (72 split frames against 28). The cure that
  keeps the diagram whole is an image made of a few sites set out in its
  proportions, a union of Voronoi cells, each with a disc's bell; it has to
  become one site again before it lands, since a rest is exact only for
  one, and that hand-over is the open problem.
- **The outline has as many corners as a disc's.** The owner expected a
  sphere to cost far more edges than a large Voronoi cell. Measured, an
  image's outline averages 18.7 corners in the middle of a change on
  Cohort and 17.9 on Slate: the shore is cut on the same grid either way,
  and a cell's sides are few.
- **Tried and not in.**
  - *The image a plain cell of the diagram* (its bell counted for its
    neighbours, its own cell not cut by the sea): a polygon, but the sea it
    gave up went between it and the gallery, which then floated apart.
  - *A rectangle of the image's area as its reach*: its area no longer
    answered its weight, and the auction lost hold of it (the chain's lurch
    passed 1.8M).
  - *Proportions no wider nor taller than the screen's*, to tame the essay's
    band: 142,694, 147,201 and 138,253 on the three starts above. No better.
  - *Proportions turning on the change's clock*, not with the image's size:
    145,275 on the first start.
  - *Slate with Apace's rule*: 149,579 on the first start, worse than either
    alone, so the two ship apart.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Slate has no card yet.


## Run

```bash
python3 tests/slate/build.py
node tests/slate/validate.cjs
```
