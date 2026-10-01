# Yinyang: the two images swap by a rule of their own

Baseline: Cohort, `cohort.html` on this branch, SHA-256
`708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Cohort, on a desk
(1440×900). One of two answers to the same question; Stay is the other.

## What it proves

A change from page to page has two cells unlike the rest, and the hive
knows which ones before it starts. One is the image that closes, which will
shrink to a card. The other is the card that was clicked, which will
balloon into the image. On Cohort they still travelled like any other cell,
on the shallow bend every path shares, and only their sizes were timed so
that they would not collide.

Yinyang tests a discrete rule for the two of them: they swing round each
other, as yin and yang turn, and they have right of way over the cards.

## How it works

- **The two images swing round each other.**
  - Both paths are bent the same way about their chords, so the two pass
    side by side instead of head on.
  - The bend is the least that lets them pass clear: their seeds as far
    apart as their two half sides, at the sizes the change's clock gives
    them, all the way.
  - It is no more than a chord's length off the chord, about a half circle,
    and no more than keeps both arcs on the page, since a seed cannot leave
    it.
  - They turn the way that needs the lesser bend.
  - The arcs are laid as the change is laid, before the journeys' lengths
    and the change's pace are read from the paths.
- **They have right of way.** While they swap they push the cards in their
  way and are not pushed back.
- **Cohort's handover is taken out.** The arcs keep the two clear, so the
  old image no longer has to be a card by the time they pass. The rest of
  Cohort stands: the gallery keeps its side, an image is a card while it is
  in the gallery, and while the images change hands, ground nobody claims
  is the sea's.
- **Breathe, a slider.** The cards of both pages can give way too: each
  bids less by the slider's share of its size at the change's middle, on
  the change's own clock (none at either rest, all of it halfway), so the
  swap has more room. It is at 0 by default; at 40 every card dips to 60%
  of its size. See Measured for why it is off.
- **Scope.** Only a change from a page to a page. Every other change is
  Cohort's to the bit.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame on both marks alike. The
page-to-page changes are a chain through all 56 ordered pairs of the eight
kinds of page.

**The swap.** The two images' closest pass is their seeds' distance over
their two half sides, by claim, at its least over the change (1 or more is
clear), averaged over the 56 changes.

| | Cohort | Yinyang | Yinyang, Breathe 40 |
|---|---|---|---|
| Closest pass | 0.76 | 0.93 | 0.94 |

**Defects drawn** (lurch, slivers at 50 a frame, splits at 200, near-
collisions at 100, start shock):

| 56 page-to-page changes | Cohort | Yinyang | Yinyang, Breathe 40 |
|---|---|---|---|
| Score | 106,515 | 111,212 (+4%) | 120,965 (+14%) |
| Lurch | 35,580 | 37,117 | 37,984 |
| Sliver frames | 830 | 906 | 939 |
| Split frames | 27.9 | 28.1 | 62.1 |
| Near-collisions | 117 | 112 | 118 |
| Start shock | 12,125 | 11,989 | 11,884 |
| The 14 changes to or from an essay | 41,563 | 44,477 | 48,175 |
| The other 42 | 64,952 | 66,735 | 72,790 |

**The gallery** (Cohort's measures, on the 42 changes that are not to or
from an essay, in Mpx²-frames; see Cohort's README for their definitions):

| | Cohort | Yinyang | Yinyang, Breathe 40 |
|---|---|---|---|
| Gallery crosses the screen | 0 | 0 | 0 |
| Cards' travel | 74,536 px | 74,478 px | 74,478 px |
| Spill (cards outside the box) | 186 | 177 | 71 |
| Hole (box drawn by no cell) | 187 | 189 | 346 |
| Swell (opening image in the box) | 40 | 60 | 108 |
| Bulk (closing image in the box) | 24 | 28 | 40 |

Breathing does free the room it is meant to: the cards spill 60% less. But
the images take that room inside the gallery's box, and the changes draw
more defects, so the slider stays at 0.

**The tour** (home's scenes, home to a page of every kind and back, and two
changes from page to page) draws 25,369 against 26,377 on Cohort. The
difference is all Ember → Tide, a change from page to page: 4,794 against
5,661.

**Thinking:** 109 moves on the page-to-page changes and 26 on the tour, none
late; 9,192 and 1,529 frames laid bit for bit on the worker's rehearsal of
its move.

## Known

- **The arcs are wide, and the images lag them.** The images keep further
  apart than on Cohort, but on wider, faster curves their seeds trail their
  plans more: 1.33M px-frames off their paths, against 1.09M on Cohort,
  with no thinking.
- **Right of way does little.** The images were not being pushed much in
  the first place. With right of way taken out, they strayed from their
  paths 2% more (1.45M px-frames against 1.42M, before the arcs were kept
  on the page).
- **They still come close.** At the sizes they actually have, the two
  images would touch at their closest on 41 of the 56 changes, against 40 on
  Cohort (no thinking).
  The arcs are laid for the sizes the change's clock gives them, and the
  windows and the auction make the real sizes differ.
- **Breathing costs defects.** It frees room: less of the cards' area spills
  outside the gallery's box. But the images take that room inside the box,
  and the changes draw more defects (see Measured). Breathing only the cards
  near the arcs was worse still: 137,398 against 114,481 for the arcs
  alone, before they were kept on the page.
- **A lone cell is still its disc**, as on Cohort.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Yinyang has no card yet.

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

- **Yinyang's rules are the only change.**
  - Taken out (one switch, `YINYANG`), with no budget, the tour and the
    chain are Cohort's, the world and every drawing command, frame by frame:
    11,550 and 25,950 frames.
  - With them in, every change that does not go from a page to a page is
    Cohort's to the bit: 10,650 frames.
- **The images swing round each other:** at their closest they pass further
  apart, over their sizes, than on Cohort.
- **Nothing waits, and nothing fractures**, on the chain, on the chain with
  Breathe at 40, and on the tour.
- **What the worker rehearses is what the page plays**, to the bit, frame by
  frame, from each move until the next acts, while the page and its
  rehearsal both have the change running.
- **Every change of the page has one pace**, as on Tempo.
- **Every page at rest is exact**, as on Cohort, and every cell at rest is
  drawn its own colour.
- **With no worker the hive thinks on the page**, makes moves, and plays what
  it rehearsed there: 29 moves and 2,323 frames laid on the first 12 changes
  of the chain.
- **A story is Cohort's.** A Cue story is Cohort's frame by frame (2,040
  frames). A Tell and a Tell II story run to their end and home without a
  fractured cell.

The defects drawn and the gallery's measures are reported against Cohort's,
and with Breathe at 40, not held to them.

## Run

```bash
python3 tests/yinyang/build.py
node tests/yinyang/validate.cjs
```
