# Cohort: from page to page, the gallery is one body

Baseline: Amoeba, `amoeba.html` on this branch, SHA-256
`74cbb39341fdbc8ec4650fa1831cc38ac7aaa90535c4729466df2e2a0e5a56b1`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Amoeba, on a desk
(1440×900).

## What it proves

Amoeba's changes between the colour pages were its messiest. Most pages
share a shape: an image, a gallery of cards down one side, and whitespace
for the text. Yet a change from one page to the next ignored that shared
shape.

- **The gallery crossed the screen.** Every page opened on the side it was
  clicked from. So on 36 of the 56 changes between kinds of page, the
  gallery moved to the other side of the screen, through the images, and
  its cards found their new seats among each other on the way.
- **The clicked card grew in the gallery.** It grew on the change's clock
  from where it stood, among the cards, and shoved them aside.
- **The closing image stayed big.** The auction hands out the ground in
  proportion to the bids. So the ground the closing image gave up went back
  to everyone, and to the closing image most. It was drawn far bigger than
  it bid (from Jazz to Dune, Jazz was drawn at 727,000 px² while it bid
  492,000), and sat as a ball in the middle of the page that the opening
  image had to get past.

Cohort tests whether the cells can know what the two pages share: a gallery
that is one body and stays one, and an image that changes hands.

## How it works

- **The gallery keeps its side.** The next page opens the way that leaves
  its gallery nearest where this one's is, measured by the centroid of its
  seats, by area. If both ways are as near, it opens on the side clicked,
  as before.
- **An image is a card while it is in the gallery.**
  - The gallery is its cards' rectangles, each on its way from its old seat
    to its new one on the change's clock.
  - The clicked card grows only once a card of its size at its seed no
    longer touches any of them.
  - The closing image has shrunk to a card by the time its card touches
    them.
  - Each is a window on the journey's progress, found once along the path at
    the ask.
- **The two images hand over where they pass.** Take their seeds' closest
  approach on the way. If, at the sizes the clock gives them there, they
  would touch, the closing image is a card by then and the opening one
  starts to grow only after.
- **Each image's size runs on its window as a smooth step**, so no window
  starts or stops with a step in its rate.
- **While the images change hands, ground nobody claims is the sea's.** The
  sea claims whatever the cells and the whitespace leave unclaimed, in each
  pocket of the ground, in the main auction and in its shadow. Every cell is
  drawn the size it bids, and the closing image is seen to give way.
- **Scope.** Only a change from a page to a page. Everything else is
  Amoeba's, and every change that does not go from a page to a page is
  Amoeba's to the bit.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame on both marks alike. The
page-to-page changes are a chain through all 56 ordered pairs of the eight
kinds of page.

**The gallery as one body.** The gallery is the cards seated on both pages,
but the two images. Its box runs from the bounding box of the old page's
cards to the new page's, on the change's clock (the cards' mean progress).
Each frame is measured in px², and summed over the change:
- *spill*: the gallery's cards drawn outside the box;
- *swell*: the opening image in the box, beyond the card it was, which it
  gives back as it leaves;
- *bulk*: the closing image in the box, beyond the card it becomes, which
  it takes on as it lands;
- *bloat*: the closing image drawn anywhere beyond what it bids;
- *hole*: the box drawn by no cell.

Over the change, *crossings* count the changes on which the gallery's
centroid moves more than half the screen, and *travel* is the cards' seats'
movement. An essay's gallery is two corners about its image, so its box
holds the image, and its 14 changes are counted apart.

| 42 changes, essays apart | Amoeba | Cohort |
|---|---|---|
| Gallery crosses the screen | 36 | 0 |
| Cards' travel | 381,892 px | 74,536 px (−80%) |
| Spill, Mpx²-frames | 557 | 186 (−67%) |
| Swell | 135 | 40 (−71%) |
| Bulk | 231 | 24 (−89%) |
| Bloat | 38.3 | 3.7 (−90%) |
| Hole (reported) | 192 | 187 |

| 14 changes to or from an essay | Amoeba | Cohort |
|---|---|---|
| Gallery crosses the screen | 0 | 0 |
| Cards' travel | 70,033 px | 60,394 px |
| Swell, Mpx²-frames | 308 | 207 |
| Bulk | 378 | 257 |
| Bloat | 28.5 | 1.2 |
| Hole | 153 | 237 |

**Defects drawn** (lurch, slivers at 50 a frame, splits at 200, near-
collisions at 100, start shock):

| 56 page-to-page changes | Amoeba | Cohort |
|---|---|---|
| Score | 136,779 | 106,515 (−22%) |
| Lurch | 42,626 | 35,580 |
| Sliver frames | 1,161 | 830 |
| Split frames | 46.9 | 27.9 |
| Near-collisions | 150 | 117 |
| Start shock | 11,747 | 12,125 (+3%) |

Thinking on the page-to-page changes: 128 moves, none late, and 9,452 frames
laid bit for bit on the worker's rehearsal of its move.

**The tour** (home's scenes, home to a page of every kind and back, and two
changes from page to page) draws 26,377 against 23,575 on Amoeba.
- Of its two changes from page to page, Coal → Aurora draws 301 against
  1,104, and Ember → Tide 5,661 against 4,647.
- The rest of the difference is home's changes starting from another
  world: once Coal → Aurora has laid Aurora's page out differently, going home
  and opening Drift is a different change (3,001 against 272). Given the same start,
  every change that does not go from a page to a page is Amoeba's to the bit
  (checked below).

Thinking on the tour: 25 moves, none late, 1,454 frames laid.

**In Chromium**, headless, from home to Drift, then page to page through
Ember, Tide, Moss, Petal, Aurora, Dune, Jazz and Drift, and home; two runs
of each:

| | Amoeba | Cohort |
|---|---|---|
| Frames drawn in 32 s | 1,477 · 1,428 | 1,414 · 1,457 |
| Longest frame | 251 ms · 297 ms | 318 ms · 274 ms |
| First motion after the ask | 6–73 ms | 7–77 ms |
| Errors | none | none |

The frame cost is Amoeba's, within the runs' spread.

## Known

- **Keeping the side can send the clicked card across the screen.** From
  Jazz (its gallery a narrow strip on the right) to Drift (its image on the
  left), the gallery stays right, and Drift flies from the strip to the far
  left, past Jazz giving way. On Amoeba the page flipped and the gallery
  crossed instead.
- **A lone cell is still its disc.** As the page's whitespace melts into the
  sea, the closing image is a ball until it reaches its card's size; it now
  shrinks visibly, where on Amoeba it stayed big.
- **The sea shows inside the gallery's box** where its cards have yet to
  arrive. Every cell is drawn the size it claims, so the box is no longer
  filled by cells drawn bigger than they bid. The validator reports this and
  does not hold it to Amoeba.
- **The closing image still carries what the pointer gave it**, and gives it
  back across the change, as on Amoeba.
- **Tried and not in**, each on the 56 page-to-page changes with the same
  defect count, thinking 16 frames a frame on the page:
  - *The side that moves the least.* Opening the page the way that moves
    the least area the least distance, gallery and both images counted,
    sends the gallery across the screen on 32 of the 56 changes, for about
    the same defects (128,683, against 128,225 keeping the side, both without
    the free sea). The gallery staying one body is the point, so the side is
    kept.
  - *Matching the cards to the gallery's shape*, each card's place in the
    old gallery carried onto the new one's box: 8% more defects (138,031
    against 128,225, both without the free sea), and no more neighbours kept
    together (71.4% of the pairs, against 72.0%).
  - *A size whose radius runs with the path*: 9% more defects (135,933
    against 124,968, before the handover), lurch most.
  - *The image growing only into its own rectangle*, what it holds outside
    never growing: no difference once the free sea is in (105,479 against
    105,234).
  - *Linear windows* instead of smooth steps: 109,557 against 105,234 here,
    though fewer with no thinking (124,516 against 129,440).
- **An essay's gallery is two corners** about its image, so the gallery's
  box holds the image; its changes are counted apart.
- **No phone.** The class is iterated on a desk; a phone version waits for
  whatever wins.
- **The landing page is unchanged.** Cohort has no card yet.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and the worker of Wings headless (a second copy of the page's script,
its messages crossing as structured clones), thinking 16 rehearsed frames a
frame. Amoeba runs beside it under the same worker. Everything is on a desk
(1440×900; the stories at 1900×810).

It runs two sets of changes:
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **Cohort's rules are the only change.**
  - Taken out (one switch, `COHORT`), with no budget, the tour and the chain
    are Amoeba's, the world and every drawing command, frame by frame:
    11,550 and 25,950 frames.
  - With them in, every change that does not go from a page to a page is
    Amoeba's to the bit: home's scenes and home to every kind of page and
    back, 10,650 frames.
- **The gallery is one body**, on the chain, essays apart, against Amoeba:
  - it crosses the screen on fewer changes, and its cards travel less;
  - less of its cards' area is drawn outside its box;
  - the opening image swells less in it, and the closing image keeps less of
    its size in it;
  - the closing image is drawn beyond what it bids less.
  How much of the box no cell draws is reported, not held to Amoeba.
- **The page-to-page changes draw fewer defects than Amoeba's.**
- **Nothing waits, and nothing fractures**, on the chain and on the tour.
- **What the worker rehearses is what the page plays**, to the bit, frame by
  frame, from each move until the next acts, while the page and its
  rehearsal both have the change running.
- **Every change of the page has one pace**, as on Tempo.
- **Every page at rest is exact**, as on Amoeba: the image on its rectangle
  and covering it as much, the text covering its own with the title in it,
  the whitespace exact, no field, one site to a cell.
- **With no worker the hive thinks on the page**, makes moves, and plays what
  it rehearsed there, frame by frame: 34 moves and 2,284 frames laid on the
  first 12 changes of the chain.
- **A story is Amoeba's.** A Cue story is Amoeba's frame by frame (2,040
  frames, the world and every drawing command). A Tell and a Tell II story
  run to their end and home without a fractured cell.

The defects of the tour are reported against Amoeba's, not held to them.

## Run

```bash
python3 tests/cohort/build.py
node tests/cohort/validate.cjs
```
