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

The fifth revision answers the fourth. It worked so well that it did not seem
to need the niche, which raised more questions than it answered: a slot of
whitespace held open in the pen for as long as its cell was out. The niche is
gone. The pen is always whole: its cells share the room of a cell that is
out, each where it stands, settle in the pen, and give the room back as the
cell comes home. (Closing the pen over the gap with its cells held still, the
discarded Deal, left them static between turns and concave or broken during
them.) While a change is on, the pen is an auction of its own, so its edge is
the pen's whatever its cells do; each cell takes and gives its share of a
card's room as the card uncovers and covers it; a card is its slot's size in
the pen; and a cell a card comes over slips round it.

## The rules

- **A card flies as a card.** A cell going out to the stage leaves the auction
  as it sets off: its shape is the blend of the cell it had (carried with its
  seed) and a card centred on its seed, all card within a reach and a half,
  the card growing from its slot's size to its place's as it gets away from
  the pen (see below). It lands a wall, pinned on its place. A card going
  home, or a cell coming into the pen from off its slots (the story's entry),
  flies the other way and melts into its cell of the pen as it arrives, the
  cell carried with its seed so the blend is centred on it.
- **A card flies over whitespace.** Whitespace under a card stays where it is
  and holds what ground the card leaves it; it neither waits for the card to
  pass before it opens nor waits to take its new sites, and nothing gives way
  for a card, which carves its own way.
- **The pen is whole.** The cluster's slots are laid once for the story, one
  for every cell; a cell keeps its slot, and a cell coming home goes to its
  own. The cells that are home share the whole pen, each in the share its
  slot gives it, and settle in it (two rounds of a centroidal power diagram
  from the slots' hearts), so a cell that goes out leaves no gap: the cells
  of the pen spread into its room and make room again as it comes home.
  Nothing in the pen is whitespace, at rest or in a change.
- **The pen is a pocket of its own.** While a change is on, the ground is cut
  along the pen's edge and the two sides are two auctions, as ground walls
  cut in two is: the pen's cells bid in the pen, the whitespace outside it,
  wherever a site stands, and a cell melting into the pen enters on the pen's
  weights. Mirrors behind the edge hold it only for the cells they were made
  for; a cell going out or a card coming home left its neighbours pushing
  past them or falling short. Not on a change that brings cells in from off
  the story's pages (its entry): none of the pen was theirs, and the whitespace
  holds what nobody has yet.
- **The pen settles at the pace of its cards.** A cell of the pen takes its
  share of a leaving card's cell as the card uncovers it, and gives back its
  share of a returning card's cell as the card covers it; its share is of the
  pen between the pages, the cells staying in it with the pen to themselves.
- **A card goes out before the card coming home to its room,** as Ferry's
  leader does: a cell of the pen going out sets off no later than any card
  coming home into its cell.
- **A card is its slot's size in the pen,** by the time it reaches the pen's
  edge coming home, and until it is out of it leaving, so no card in the pen
  is bigger than its own room.
- **A cell a card comes over slips round it.** A seed in a card goes out by
  the card's nearest side; a seed of the pen ahead of a card also slips
  sideways along it, as far in a frame as the card goes, and once past its
  corner goes home round its side. Driven on ahead instead, a cell came out
  on the far side of the card's room, and the two changed places as the card
  melted and changed back.
- **Matched by distance.** The places the slide adds take the nearest cells not
  benched, and a cell coming home without a slot of its own takes the nearest
  free one: greedy, then 2-opt on squared travel. A cell keeps what it is on or
  bound for.
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
  II's cut); an empty place is a piece of its own, and the door between stage
  and pen is one piece.
- **Every cell is one card on a story**, as on a page: no gallery opens a field.

## Measured (1440×900, 12 cells, 30 ms frames; scratchpad instruments)

| | Fourth revision | This revision |
|---|---|---|
| Whitespace in the pen at rest | a slot-sized niche per cast member | none on any slide (its cells cover 100% of it) |
| Worst fling, ordinary / fresh / entry | 7 / 39 / 12 px | 5 / 15 / 15 px |
| Flings over 40 px, ordinary / fresh / entry | 0 / 0 / 0 | 0 / 0 / 0 |
| Worst fling on a phone (390×720), any change | 27 px | 28 px |
| Peak/mean speed, ordinary / fresh / entry | 2.27–2.44 / 2.45–3.39 / 4.16 | 2.23–2.30 / 2.42–3.08 / 4.41 |
| Area spike max, slides | 1.3–3.1 | 1.2–2.4 |
| Frames a cell is drawn in two pieces (the smaller over 50 px²), desk / phone | 13 / 3 | 7 / 22 |
| Frames a card drives a seed of the pen before it, desk / phone | – | 2 / 1 |
| A change settles, frames | 62–96 | 63–94 |

A fling is a cell's diagram centroid moving more than its own seed in one
frame, which reads as a wall swinging it. The engine's own scenes measure worst
flings of 11–123 px, peak/mean 2.4–5.0 and spikes of 1.1–1.7; Tell II's slides
77–454 px, 8.3–13.0 and 27–62.

What was tried on the way here:

- Without the niche and nothing else, the cells beside a card's room wrapped
  round the card as it went and as it came; mirrors behind the pen's edge
  made for the page at rest let a cell growing into a room push out past the
  edge, and one giving room back fall short of it, the whitespace reaching in.
- A niche for as long as its card was on its way (opening as the card cleared
  its slot, closing as the cells beside it settled in) was the gap again, for
  a second, in the middle of the pen.
- Scaling the pen's claims to the pen less what the cards cover, in the one
  auction, did nothing for the edge; in the pen's own auction it is what the
  auction does anyway, and on the story's entry it handed the first cells home
  the whole pen, round every card still coming.
- A path squared to the pen's edge, so a card comes straight in, ended the
  cells driven on ahead of cards, but a long flight across the stage turned
  into an L over the other cards' places, and squared only near the pen it
  met the cards the change had bent it round. A seed sent out of a card
  toward where it was going jumped the card's width in a frame.
- Choosing, for a flight that would drive a seed, a squared turn that met no
  other card, waiting up to a second: there was none on the two changes that
  needed it, and a card waiting was flown over.
- Earlier revisions: a card kept a hole once landed drifted 10 px off its
  diagram at rest, and handed back to the auction as it landed it sprawled; a
  card shoving the whitespace in its path ahead of it left a piece on the
  wrong side of its place for good (whitespace is now flown over); whitespace
  giving way to a card before it came split cells round it; cutting again
  every piece a traveller crosses closed so much whitespace that the pen
  spilled; a niche held by one site at its heart was a cell in the dark.

## Known

- **A card presses into the pen.** A card coming home dents the cells beside
  its room as it comes in, and a cell whose ground reaches round the card's
  far side shows a sliver there for a quarter of a second as the card melts
  (up to 1,300 px² on a phone's slide and 2,700 px² on its entry, 3,800 px²
  on a desk's fresh slide).
- **Cards pass over each other,** as in the fourth revision: two cards on the
  story's entry and on a fresh slide overlap in flight (at worst 34,000 px² on
  the entry, 9,500 px² on fresh slide 3 at 1440×900, against 32,800 and 8,900
  before), the one further from home drawn cut where they do. The validator's
  check reads the shapes as drawn, which never overlap.
- **Exact to 4 px at rest, not 2**, outside the pen. No weights are handed
  over. The pen's cells are its pocket's power cells, not rectangles.
- **A change takes 1.5–3 s** in the validator's stories, as the engine's
  journeys run.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed. Without the
Cue button, 17,332 frames and 15,708,550 drawing commands are identical to
Tell II's (the scene matrix, a click, a scroll, a drag, a Tell story, a Tell II
story and home). With the story, on a desk and a phone, it checks every slide
settled (the cast on its places, every other cell on a slot of the pen, no
whitespace in the pen, drawn or bid for, and the pen's cells covering it),
every change (the cast that stays does not move, the pen's cells that stay
keep their slots and settle inside the pen, nothing fractures on any frame, no
two cards in flight overlap as drawn, no two cells on their way that are not
both cards come within half their reaches added) and a notch back through the
slides (see `validation.json`).

## Run

```bash
python3 tests/cue/build.py
node tests/cue/validate.cjs
```
