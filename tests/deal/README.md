# Deal: Cue's story, the pen closed over the gap

Baseline: Cue, `cue.html` on this branch, SHA-256
`e23ede652562c50bb7fddc7c53bc00a81bcaf2fe0d7357e1f733941780fa48ef`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Cue dealt its cells to the stage as cards, and a cell that went out held its
slot of the pen open as a niche of whitespace until it came home. With the
cells flying as cards, the flight did not need the niche, and a dark gap in the
pen at rest asked what belonged there. Deal discards the niche: the pen is
always whole. It proves that the gap can close without the pen convulsing,
which is what the niche was first made to prevent (Cue's first revision re-laid
the pen for every count, and every cell of it travelled).

The answer turned out to be the one the flights gave: a cell of the pen that
changes is a card too. Everything in the pen is a card, pinned on its
rectangle, and only whitespace bids.

## The rules (the rest is Cue's)

- **The pen closes over the gap.** The pen's slots are still laid once for the
  story, one for every cell, by the bento's halving. Laid again with only the
  cells that are home: at a halving with one half empty, the other half takes
  the whole, its own halvings stretched across it as they were. So the cells
  that close a gap are the ones beside it, and they only stretch, along one
  axis. When the card comes home the half gives its ground back.
- **A cell of the pen stands where it is.** Every cell is seated at its own
  slot's heart, whatever its rectangle, so nothing in the pen travels.
- **A cell that closes a gap is a card changing size.** Its rectangle eases
  from the one it is drawn at to its new one, out of the auction, and it is
  pinned there, a wall, as it gets there.
- **At the pace of the card.** A cell closing a gap grows into it as the card
  that left it clears it. A cell giving a slot back holds it until the card
  coming home is within reach of it, and gives it back as the card comes in.
  Cue's niche opened and closed on the card's ledger in the same way.
- **A card coming home lands a wall**, as a card on the stage does, on its
  rectangle of the pen. Its shape blends from its card to that rectangle, and
  a card that has landed is its rectangle, whatever the cards still in flight
  clip from its outline.
- **A card whose rectangle stays holds still**, as the cast on the stage does.

## Measured (1440×900, 12 cells, 30 ms frames; scratchpad instruments)

| | Cue | Deal |
|---|---|---|
| A niche in the pen at rest | one for every card on the stage | none |
| Cells that move in a change (ordinary / fresh) | 10–11 / 12 | 2–3 / 5–7 |
| Pen cells that stay, ordinary slides | ×1.01–1.13, 19–105 px | ×1.00, 0 px |
| Pen cells that stay, fresh slides | ×1.02–1.12, 69–181 px | ×1.00, 0 px |
| Stage cells that stay | ×1.00, 0 px | ×1.00, 0 px |
| Worst fling, ordinary / fresh / entry | 7 / 39 / 12 px | 0 / 0 / 0 px |
| Peak/mean speed, ordinary / fresh / entry | 2.3–2.4 / 2.4–3.4 / 4.2 | 1.8–2.8 / 2.0–2.7 / 2.0 |
| Area spike max, slides | 1.3–3.1 | 1.1–2.5 |
| Route over net displacement, slides | 1.0–22 | 1.0–1.1 |
| A change settles, frames | 62–96 | 55–100 |
| A traveller on the page's edge while its seed is more than 150 px from every edge (frames, all slides) | 0 | 0 |
| Two cards in flight overlapping | never | never |

A fling is a cell's diagram centroid moving more than its own seed in one
frame. Route over net displacement is how far a cell's centroid wanders against
how far it gets; Cue's pen cells swayed round their seeds on the slides where
that reaches 14–22.

What was tried on the way here:

- The half beside the gap stretched as bidders, seated at their new
  rectangles' centres: whole halves of the pen travelled (five cells at once),
  and cells flung by up to 77 px on six of seven slides.
- Paced by the card but still travelling: one fling on four slides.
- Seated at their own slots and bidding: no flings on the ordinary slides, but
  a card melting home found its ground outside the pen for 0.6 s. Under a card
  a cell's weight answers to nothing, so the neighbour that gave the slot back
  reached right through it; Cue's niche had fenced the slot until the card
  melted. Joining the auction at its own weight in the page did not help: the
  whitespace under the card had drifted too, and the solve threw the weight
  away in one step.
- Landing home as walls, with the stretched cells bidding: a bidder among walls
  swayed 2–8 px on later changes and settled up to 15 px off its rectangle,
  since the page's weights hold a pen of bidders.

## Known

- **A gap shows for a moment in the pen on a fresh slide**, where a cell has
  given back part of a slot the card coming home has not yet covered.
- **The pen is a bento of cards**, exact rectangles, where Cue's pen was its
  pocket's power cells. The Voronoi is in the whitespace, and in the story's
  first frames as the page's cells take their slots.
- **Cue's names.** The story's code keeps Cue's identifiers and its scene key
  `cue`; the button reads Deal.
- **A change takes 2.1–3.6 s** on the desk (Cue's took 2.3–4.5 s), as the engine's
  journeys run.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed. Without the
Deal button, every frame's state and drawing commands are identical to Cue's
(the scene matrix, a click, a scroll, a drag, a Tell story, a Tell II story and
home). With the story, on a desk and a phone, it checks every slide settled
(the cast on its places, the pen whole: every other cell on its rectangle of
the pen, the rectangles tiling it, no whitespace in it), every change (the cast
that stays does not move, nor does a cell of the pen whose rectangle stays; a
cell closing a gap stays in the pen; no two cards in flight overlap) and a
notch back through the slides (see `validation.json`).

## Run

```bash
python3 tests/deal/build.py
node tests/deal/validate.cjs
```
