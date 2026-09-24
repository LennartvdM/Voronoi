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

The fourth revision answers the third. The cards bound for the stage went to
the screen's edge first, like a fly on the wall, and found their places only
as they landed; the cells leaned on too many crutches. They did: a cell has no
shape of its own, only where its neighbours' claims stop, and one crossing the
open stage has few neighbours, so its outline ran to whatever stopped it,
the page's edge most of all. Now a cell that leaves the pen becomes its card
on the way: out of the auction, a hole in everyone's ground, its shape the
engine's blend of the cell it was and its card. It flies and lands as its
card. A card going home melts back into its cell in the pen as it arrives.

## The rules

- **A card flies as a card.** A cell going out to the stage leaves the auction
  as it sets off: its shape is the blend of the cell it had (carried with its
  seed) and a card centred on its seed, all card within a reach and a half,
  the card growing from its slot's size to its place's by where its seed is.
  It lands a wall, pinned on its place. A card going home, or a cell coming
  into the pen from off its slots (the story's entry), flies the other way and
  melts into its cell of the pen as it arrives, the cell carried with its seed
  so the blend is centred on it.
- **A card flies over whitespace.** Whitespace under a card stays where it is
  and holds what ground the card leaves it; it neither waits for the card to
  pass before it opens nor waits to take its new sites, and nothing gives way
  for a card, which carves its own way.
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
  alike, the one that sets off later. A card is bent round the cards standing
  on the stage too.
- **Whitespace makes way without giving ground.** Nothing closes for a crossing.
  The sites of a piece in a traveller's way give way, the more the nearer, and
  hand what they give up to the piece's sites clear of it, so the piece keeps
  its claim and the page its total. A piece whose sites are all in the way
  gives way whole. The way comes in over a traveller's first half-reach and
  goes over its last, by where its seed is, not by its clock.
- **A staying piece takes its new sites once the cells by it have gone.** A piece
  whose mirrors change (the piece beside a place a cell comes to, say) is
  re-seated on its new page only once every cell (not card) passing within its
  reach has gone by or landed, so a cell never crosses the mirror that is to
  hold its own edge.
- **The cast that stays holds still,** pinned on its place for the change.
- **The bench.** When a new sequence begins, the last sequence's cast may not
  take a place, so a fresh cell comes out.
- **The whitespace is cut once,** the page less every place and the pen (Tell
  II's cut); an empty place and an open niche are pieces of their own, and the
  door between stage and pen is cut across at the edges of the pen's slots.
- **Every cell is one card on a story**, as on a page: no gallery opens a field.

## Measured (1440×900, 12 cells, 30 ms frames; scratchpad instruments)

| | Third revision | This revision |
|---|---|---|
| A traveller's cell on the page's edge while its seed is more than 150 px from every edge (frames, all slides) | 86 | 0 |
| Worst fling, ordinary / fresh / entry | 79 / 71 / 101 px | 7 / 39 / 12 px |
| Flings over 40 px, ordinary / fresh / entry | 0–4 / 2–10 / 22 | 0 / 0 / 0 |
| Peak/mean speed, ordinary / fresh / entry | 2.5–6.5 / 5.7–6.2 / 4.1 | 2.3–2.4 / 2.4–3.4 / 4.2 |
| Area spike max, slides | 1.5–2.8 | 1.3–3.1 |
| Worst swell through a change (the auction's ground over what is bid for: every cell bidding is drawn this much larger) | 1.02–1.59 | 1.01–1.16 |
| Pen cells that stay, ordinary slides | ×1.05–1.11, 41–155 px | ×1.01–1.13, 19–105 px |
| Pen cells that stay, fresh slides | ×1.24–1.42, 119–214 px | ×1.02–1.12, 69–181 px |
| Stage cells that stay | ×1.00, 0 px | ×1.00, 0 px |
| Two cards in flight overlapping | – | never (they touch at most) |
| A change settles, frames | 71–117 | 62–96 |

A fling is a cell's diagram centroid moving more than its own seed in one
frame, which reads as a wall swinging it. The engine's own scenes measure worst
flings of 11–123 px, peak/mean 2.4–5.0 and spikes of 1.1–1.7; Tell II's slides
77–454 px, 8.3–13.0 and 27–62.

What was tried on the way here:

- A card kept a hole once landed, until the page was still, drifted 10 px off
  its diagram at rest; handed back to the auction as it landed, it sprawled for
  the frames the whitespace round its place took to hold it.
- A card was a wall the frame it landed, and the pen settled 10 px off its page:
  a card in flight shoved the whitespace in its path ahead of it (a body in a
  hole goes out through its nearest side), and landed a wall, the piece was on
  its wrong side for good. Whitespace is now flown over.
- Whitespace giving way to a card before it came (its sites' claims fading by
  their distance from the card) flipped ground from one side of a card to the
  other and split cells round it; pacing a niche by how much of it a card
  covers measured the same as pacing it by where the card is.
- Melting a card home once it was all but its cell, not once its seed was
  home, took away the sliver described below but flung the cell as it melted.
- In the second and third revisions: cutting again every piece a traveller
  crosses closed so much whitespace that the pen spilled; whitespace stepping
  aside from a traveller flung cells as its sites swung round; a niche held by
  one site at its heart was a cell in the dark; pieces no larger than the grid,
  or a gutter round each place, brought flings back everywhere.

## Known

- **A sliver by a card coming home.** On a fresh slide, as a card all but
  arrived at its niche creeps its last pixels, a neighbour of the niche wraps
  round it and shows a sliver on its far side for a third of a second (up to
  3,700 px² on slide 3 at 1440×900), and a pen cell may reach 181 px past its
  rest cell.
- **Two cards pass close.** On a phone, two cards on a fresh slide pass within
  0.48 of their reaches added: edge to edge, never over each other.
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
the pen's cells that stay are sent nowhere, no two cards in flight overlap, no
two cells on their way that are not both cards come within half their reaches
added) and a notch back through the slides (see `validation.json`).

## Run

```bash
python3 tests/cue/build.py
node tests/cue/validate.cjs
```
