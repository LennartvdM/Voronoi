# Cue: Tell II's story, on the engine's own rules

Baseline: Tell II, `tell2.html` on this branch, SHA-256
`900e0a5d61780788f4295472341836ab87ecd05e3a445f2cb3dbff59f0e69db2`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Tell and Tell II moved clumsily between slides, where the engine's own scenes
(flock, bento, hero, sidebar, frame) move well. Cue tests the explanation: the
engine's calm comes from a few rules, and a scroll-tell that keeps them moves
the same way. Every slide of Tell II's story is an ordinary scene change here.
Nobody is told where to go: a slide asks for its places around the blurb, and
the engine's matching decides who comes out.

The second revision answered the first review. Every change, the cards on the
stage responded to the cluster, and the cluster convulsed as if stuck to a
lattice. It was: every slide re-laid the cluster's bento for a new count, so
every cluster cell got a new slot and travelled. The cluster became a pen that
keeps its frame, and a card that leaves it holds its niche open.

The third revision answers the second. The niches were dark cells: one site at
the heart of the slot, exactly where its card sits, so a site grew under a card
as it left and a card came home onto a site still draining. And cells cycling
in and out met their predecessor or successor head-on in the door, blind to
each other. Now a niche is held from its edges, the change looks ahead and
bends meetings apart, and whitespace makes way for a traveller without giving
up ground, so the pen stays braced.

## The rules

- **The pen.** The cluster's slots are laid once for the story, one for every
  cell. A cell that goes out holds its slot open as a niche of whitespace. A
  cell coming back takes the open niche nearest it. Every other cell keeps its
  slot and is sent nowhere.
- **The pen is solved whole; a niche is held from its edges.** The page is laid
  as if every slot were held, so the pen is one pocket. An open slot is then
  whitespace holding exactly the ground a cell there would, held the way
  Portal holds whitespace: for each cell of the pen beside it, a mirror of that
  cell close behind their shared edge, weighted so the edge stays where it was.
  Nothing stands at the niche's heart. Every piece's share is then read again
  off the diagram as it is, niches open, so the auction settles on this page.
- **A niche opens at the pace of its card leaving,** all of it on its card's
  ledger, not on a clock of its own beside the card.
- **Matched by distance.** The places the slide adds take the nearest cells not
  benched, and the cells coming home take the nearest niches: greedy, then
  2-opt on squared travel. A cell keeps what it is on or bound for.
- **The change looks ahead.** Every journey is played forward before it runs.
  Two cells that would meet mid-journey (seeds nearer than three quarters of
  their reaches added, both still on their way) are bent apart: one curves round
  the other on the side it is already on, just enough to pass close. The cell
  going out to the stage keeps its line; a cell going home gives way; of two
  alike, the one that sets off later.
- **Whitespace makes way without giving ground.** Nothing closes for a crossing.
  The sites of a piece in a traveller's way give way, the more the nearer, and
  hand what they give up to the piece's sites clear of it, so the piece keeps
  its claim and the page its total. A piece whose sites are all in the way
  gives way whole. The way comes in over a traveller's first half-reach and
  goes over its last, by where its seed is, not by its clock.
- **A staying piece takes its new sites once the cells by it have gone.** A piece
  whose mirrors change (the piece beside a place a cell comes to, say) is
  re-seated on its new page only once every cell passing within its reach has
  gone by or landed, so a cell never crosses the mirror that is to hold its own
  edge.
- **The cast that stays holds still,** pinned on its place for the change.
- **The bench.** When a new sequence begins, the last sequence's cast may not
  take a place, so a fresh cell comes out.
- **The whitespace is cut once,** the page less every place and the pen (Tell
  II's cut); an empty place and an open niche are pieces of their own, and the
  door between stage and pen is cut across at the edges of the pen's slots.
- **Every cell is one card on a story**, as on a page: no gallery opens a field.

## Measured (1440×900, 12 cells, 30 ms frames; scratchpad instruments)

| | Second revision | This revision |
|---|---|---|
| Total claim through a change, lowest (the auction hands every settled cell its claim × ground / total) | 42–62% of the page | 70–86% |
| Pen cells that stay, ordinary slides | ×1.01–1.44, 66–161 px | ×1.05–1.11, 41–155 px |
| Pen cells that stay, fresh slides | ×1.23–2.45, 132–330 px | ×1.24–1.42, 119–214 px |
| Stage cells that stay | ×1.00, 0 px | ×1.00, 0 px |
| Closest two travellers, fresh slides (in their reaches added) | 0.16, 0.74 | 1.03, 1.03 |
| Worst fling, ordinary / fresh / entry | 35 / 174 / 125 px | 79 / 71 / 101 px |
| Flings over 40 px, ordinary / fresh / entry | 0 / 5–9 / 6 | 0–4 / 2–10 / 22 |
| Peak/mean speed, slides | 1.9–4.2 | 2.5–6.5 |
| Area spike max, slides | 1.1–1.7 | 1.5–2.8 |

A fling is a cell's diagram centroid moving more than its own seed in one
frame, which reads as a wall swinging it. The engine's own scenes measure worst
flings of 11–123 px, peak/mean 2.4–5.0 and spikes of 1.1–1.7; Tell II's slides
77–454 px, 8.3–13.0 and 27–62.

What was tried on the way here:

- Cutting again every piece a traveller crosses (the first revision) closed so
  much whitespace that the auction's total fell short: the pen spilled out of
  its frame and travellers ballooned over the text. Handing that shortfall to
  the travellers ballooned them further. Cutting again only the pieces whose
  sites a traveller brushes still let the total fall to 43% on a fresh slide,
  and the pen's cells swelled by exactly the inverse (×2.37).
- Whitespace stepping aside from a traveller (its sites held off at a radius)
  kept the pen in frame but flung cells as the sites swung round.
- A niche held by one site at its heart (the second revision) is a cell in the
  dark; mirrors of its neighbours hold it instead, but only once every piece's
  share is read again with them in (otherwise the stage drifted 10 px).
- Pieces no larger than the grid, or a gutter around each place, brought flings
  back everywhere.

## Known

- **The travellers' shapes.** Crossing the open stage, a traveller's cell is
  bounded by few whitespace sites, and those near it give way, so it reaches
  out as triangles and strips while it keeps its size. Cells going home on a
  fresh slide are flattened along the page's top and bottom edges.
- **Softer than the engine.** Area spikes of up to 2.8 and peak/mean speeds of
  up to 6.5 on the slides, against the engine's 1.1–1.7 and 2.4–5.0; a change
  settles a quarter to a half later than the second revision's on most slides
  (the staying pieces take their new sites after the travellers have landed). The entry flings 22
  frames.
- **Exact to 4 px at rest, not 2**, outside the pen. No weights are handed
  over. The pen's cells and niches are its pocket's power cells, not
  rectangles.
- **A change takes 2.3–4.5 s**, as the engine's journeys run.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed. Without the
Cue button, 17,332 frames and 15,708,550 drawing commands are identical to
Tell II's (the scene matrix, a click, a scroll, a drag, a Tell story, a Tell II
story and home). With the story, on a desk and a phone, it checks every slide
settled (the cast on its places, every other cell on a slot of the pen, one
open niche per cast member), every change (the cast that stays does not move,
the pen's cells that stay are sent nowhere, no two cells on their way come
within half their reaches added) and a notch back through the slides (see
`validation.json`).

## Run

```bash
python3 tests/cue/build.py
node tests/cue/validate.cjs
```
