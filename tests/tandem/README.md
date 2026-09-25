# Tandem: a page opens all at once

Baseline: Cue, `cue.html` on this branch, SHA-256
`1a912f7b8242722a5beb29c16ab3c167998600d9b5611043c1309bf3c4769714`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Aurora's page (documentation: the image on one side, the text in the middle,
the gallery on the other) is a good layout, but on Cue the change into it,
from any other layout, was awkward. The image first spread up against the
cluster; only then did the text's whitespace wedge itself in between the two,
and the image gave back what it had taken. Too many things took turns that
could have happened side by side. Every page did the same, in some measure;
Aurora showed it most. Tandem tests the explanation: a page is regions (an
image, a text, a gallery), and a change goes in turns when each region waits
on its own clock. Held by their own, the regions resolve together.

## Why Cue took turns

- **The image grew on its own clock.** Its bid reached its rectangle's area
  while the cells in that rectangle had yet to leave. A cell bidding for more
  than its own room holds takes the room beside it, so the image spread
  across the text's rectangle up to the cluster.
- **The text waited for the last crosser.** The text's whitespace did not open
  at all until the last cell crossing it was through (Portal's rule, so that
  nothing crossed it as a sliver). Then it opened into the image.
- **The ground nobody bid for went to everyone.** The auction hands out its
  ground in proportion to the bids. While the old page's whitespace closed
  faster than the new one opened, a third of the page had no bidder, and every
  cell, the image most, was drawn that much bigger than its bid. On Coal →
  Aurora the image was drawn at up to 58 units against its rectangle's 36.5.

## The rules

Each frame of a page's change, each region is measured on the diagram as it
stands: the room its rectangle has, less what every other cell and whitespace
(and every wall and card) covers of it.

- **The image bids no more than its own room.** Its bid is capped at the room
  its own rectangle has, plus what it still has to leave elsewhere. The text's
  rectangle is not its room, and whitespace opening in the image's rectangle
  gives way to it.
- **The text bids at least the room its rectangle has, as soon as it has it.**
  The same goes for any other whitespace opening on the page.
- **Rooms only grow.** Nothing opens and then closes again.
- **The unclaimed ground goes to the opening whitespace.** Ground no one bids
  for goes to the whitespace that is opening, not to everyone. It is eased
  over half a second and never exceeds what that whitespace bids at rest.
- **The text makes way for crossers.** Its sites in a cell's way give up their
  claim to its sites clear of it, as Cue's whitespace does for its travellers,
  so a cell crosses without being pressed into a sliver.

The bids are the sites' own, set after every other rule has set them, including
the swell a journey adds. What the auction is asked is what it hands out.

The result: the cells leave, the text opens behind them, and the image fills
its own room, at the same time. Without a page opened, nothing changes: the
tick and every drawing command are Cue's.

## Measured (scratchpad instruments, 12 cells, 60 fps)

A tour of 18 openings at 1440×900: from home to one page of each kind, and
between pages (Aurora to and from Moss, Tide, Coal, Dune and Petal, plus Ember
→ Coal and Dune → Petal).

- **Text lag:** px²·s of the text's rectangle that nobody else holds and the
  text does not yet paint.
- **Image outside:** px²·s of the image painted outside its own rectangle.

| 1440×900, 18 openings | Cue | Tandem |
|---|---|---|
| text lag | 3,450k | 513k |
| image outside its rectangle | 4,338k | 1,308k |
| image's worst share of the text's rectangle, worst opening | 67% | 28% |
| the same, averaged over the openings | 39% | 10% |
| worst fling (a cell's drawing outrunning its seed in a frame) | 586 px | 491 px |
| fling beyond 30 px, summed | 6,317 px | 7,893 px |
| frames of cells drawn as slivers | 447 | 363 |

The openings into Aurora, text lag / image outside, px²·s:

| Opening | Cue | Tandem |
|---|---|---|
| home → Aurora | 395k / 395k | 34k / 35k |
| Moss → Aurora | 247k / 247k | 3k / 3k |
| Tide → Aurora | 242k / 242k | 20k / 20k |
| Coal → Aurora | 654k / 654k | 10k / 10k |
| Dune → Aurora | 272k / 272k | 27k / 30k |
| Petal → Aurora | 360k / 360k | 28k / 28k |

On a phone (390×720, 7 openings), text lag fell from 499k to 71k, the image
outside its rectangle from 571k to 97k, flings beyond 30 px from 1,098 to
605 px, and sliver frames from 13 to 9. At 1920×1080 (the same 7), text lag
fell from 2,801k to 527k and the image outside from 3,006k to 722k; flings
beyond 30 px rose from 4,172 to 6,124 px and sliver frames fell from 74 to 71.

## Known

- **More flings on some openings.** Cells floating in the opening text slide
  across it, faster than their seeds move, as the text takes the ground
  nobody bids for. The worst is Moss → Aurora at 1920×1080 (fling sum 123 →
  2,060 px), where Petal is pressed into a needle for a few frames as it
  crosses and snaps back. On the desk tour the sum rose 25% and the worst single
  fling fell. Easing the whitespace's take over half a second cut the rise
  by about 40% (taken at once, the sum was 8,843 px). Giving the take only to
  the sites clear of every crosser made it worse (9,803 px).
- **The essay's hero still grows as a wedge.** It comes out of a field
  merge, as on Cue. Essay openings lag about as on Cue or less (Aurora → Dune
  215k → 116k).
- **The text first opens where the old page's cells left, not only between
  the image and the cluster.** It can open past the cluster, in the gallery's
  room, before the cluster crosses it.
- **The showcase and folio pages keep Cue's image overflow.** Their image's
  rectangle meets the gallery's power cells, which cover a few hundredths of it
  at rest, on Cue as here.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed.

**Identity without a page:** the scene matrix, and a Tell, a Tell II and a Cue
story and home, are identical to Cue's in state and in every drawing command
(18,798 frames and 16,405,157 drawing commands).

**On the tour of pages, at 1440×900 and 390×720,** every page at rest has:

- the image on its rectangle, covering it as much as on Cue;
- the text covering its rectangle, as much as on Cue, with the title in it;
- the whitespace exactly its rectangles;
- no field, and one site to a cell.

During every opening:

- nothing fractures on any frame;
- the image takes under 30% of the text's rectangle at worst, and on average
  half what it takes on Cue or less;
- the text's lag is under a quarter of Cue's over the tour, and no worse than
  Cue's on any opening.

Cue's figures are reported beside Tandem's in `validation.json`.

## Run

```bash
python3 tests/tandem/build.py
node tests/tandem/validate.cjs
```
