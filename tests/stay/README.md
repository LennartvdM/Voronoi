# Stay: the image stays the image

Baseline: Cohort, `cohort.html` on this branch, SHA-256
`708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Cohort, on a desk
(1440×900). One of two answers to the same question; Yinyang is the other.

## What it proves

On Cohort, a change from page to page still swaps two cells of opposite
sizes. The image shrinks to a card and goes into the gallery, and the
clicked card leaves the gallery and balloons into the image. Most of
Cohort's rules exist to manage that exchange: the windows, the handover
where the two pass, and the free sea.

Stay tests the simpler answer: no cell changes role. The cell in the
image's place stays the image, and the cell in the clicked card's place
stays a card. Only what they are changes hands.

## How it works

- **The two bodies trade places at the click.** Each takes everything the
  other has except what it is: its place, its shape, its claim, its seat,
  its journey and its sites. Each keeps its own name, colour and kind of
  page. Whatever held one of them (the walls, the shapes cut from the
  ground, the auction's owners, the pointer's hover) now holds the other.
- **Each place's colour turns** from the colour it showed to its new body's
  own, on that body's journey.
- **Then the page changes as a layout.** The image's cell goes from its
  rectangle to the new page's, the gallery from its seats to its new ones,
  and nothing crosses.
- **Cohort's rules stay in.** The gallery keeps its side. With no exchange,
  Cohort's windows, its handover and its free sea never come into play.
- **Scope.** Only a change from a page to a page. Every other change is
  Cohort's to the bit.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame on both marks alike. The
page-to-page changes are a chain through all 56 ordered pairs of the eight
kinds of page.

**No cell changes role.** At the ask of each change from page to page, the
cell that ends as the image sets off at a size that is so many times, or so
many parts, of its own:

| 56 page-to-page changes | Cohort | Stay |
|---|---|---|
| Least | 7.8 | 1.01 |
| Most | 162.6 | 2.63 |

On Cohort that cell is the clicked card, setting off at a card's size. On
Stay it is the cell in the image's place, setting off at the old image's
size.

**Defects drawn** (lurch, slivers at 50 a frame, splits at 200, near-
collisions at 100, start shock):

| 56 page-to-page changes | Cohort | Stay |
|---|---|---|
| Score | 106,515 | 144,596 (+36%) |
| The 42 not to or from an essay | 64,952 | 61,042 (−6%) |
| The 14 to or from an essay | 41,563 | 83,554 (×2.0) |
| Lurch | 35,580 | 47,061 |
| Sliver frames | 830 | 1,196 |
| Split frames | 27.9 | 62.0 |
| Near-collisions | 117 | 125 |
| Start shock | 12,125 | 12,849 |

- *Most improved:* Ember → Tide (279 against 4,553), Ember → Moss, Tide →
  Ember, Tide → Aurora.
- *Most worsened:* all to or from the essay (Dune): Petal → Dune (9,637
  against 3,667), Dune → Aurora, Dune → Moss, Jazz → Dune.

**The gallery**, on the 42 changes not to or from an essay (Cohort's
measures; see Cohort's README). The measures of the two images in the
gallery's box do not apply, since no image enters or leaves it.

| | Cohort | Stay |
|---|---|---|
| Gallery crosses the screen | 0 | 0 |
| Cards' travel | 74,536 px | 82,259 px |
| Spill (cards outside the box), Mpx²-frames | 186 | 127 |
| Hole (box drawn by no cell) | 187 | 209 |

**The tour** (home's scenes, home to a page of every kind and back, and two
changes from page to page) draws 26,817 against 26,377 on Cohort. Its own
changes from page to page are better: Ember → Tide 2,722 against 5,661.
Going home from Tide is worse (9,842 against 3,404): the page Tide left
behind is laid out differently, so going home starts from another world.

**Thinking:** 82 moves on the page-to-page changes and 18 on the tour, none
late; 5,152 and 1,002 frames laid bit for bit on the worker's rehearsal of
its move.

## Known

- **The image goes round while it moves.** Once its rectangle melts it is
  a lone cell in the sea, and a lone cell is its disc, until it forms its
  new rectangle.
- **The essay page is Stay's weak spot.** Its image is a wide band across
  the top, and its gallery is two top corners. With the gallery keeping its
  side, half the cards must cross to the far corner, over the image, and are
  squeezed into slivers along the top edge.
- **The colours blend on the way.** Each place's colour turns in a straight
  line between the two, so two distant colours pass through a muddier one
  mid-change.
- **Tried and not in.**
  - *The image gliding as a rectangle*, a rigid shape from its old
    rectangle to its new one, as a card in flight. A full-height rectangle
    splits the page in two, and the auction on the gallery's side lost its
    cells mid-change.
  - *Cohort's free sea while the image moves*: 148,946 defects against
    144,569 without it, on the 56 page-to-page changes with thinking on the
    page.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Stay has no card yet.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and the worker of Wings headless (a second copy of the page's script,
its messages crossing as structured clones), thinking 16 rehearsed frames a
frame. Cohort runs beside it under the same worker. Everything is on a desk
(1440×900; the stories at 1900×810).

It runs two sets of changes:
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **Stay's rule is the only change.**
  - Taken out (one switch, `STAY`), with no budget, the tour and the chain
    are Cohort's, the world and every drawing command, frame by frame:
    11,550 and 25,950 frames.
  - With it in, every change that does not go from a page to a page is
    Cohort's to the bit: 10,650 frames.
- **No cell changes role:** on every change from page to page, the cell that
  ends as the image sets off at a size nearer its own than on any of
  Cohort's.
- **Nothing waits, and nothing fractures**, on the chain and on the tour.
- **What the worker rehearses is what the page plays**, to the bit, frame by
  frame, from each move until the next acts, while the page and its
  rehearsal both have the change running.
- **Every change of the page has one pace**, as on Tempo.
- **Every page at rest is exact**, as on Cohort, and every cell at rest is
  drawn its own colour: the colours have finished turning.
- **With no worker the hive thinks on the page**, makes moves, and plays what
  it rehearsed there: 16 moves and 1,019 frames laid on the first 12 changes
  of the chain.
- **A story is Cohort's.** A Cue story is Cohort's frame by frame (2,040
  frames). A Tell and a Tell II story run to their end and home without a
  fractured cell.

The defects drawn and the gallery's measures are reported against Cohort's,
not held to them.

## Run

```bash
python3 tests/stay/build.py
node tests/stay/validate.cjs
```
