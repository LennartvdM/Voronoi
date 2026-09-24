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

The second revision answers the first review. Every change, the cards on the
stage responded to the cluster, and the cluster convulsed as if stuck to a
lattice. It was: every slide re-laid the cluster's bento for a new count, so
every cluster cell got a new slot and travelled. Now the cluster is a pen that
keeps its frame, and a card that leaves it holds its niche open.

## The rules

- **The pen.** The cluster's slots are laid once for the story, one for every
  cell. A cell that goes out holds its slot open as a niche of whitespace. A
  cell coming back takes the open niche nearest it. Every other cell keeps its
  slot and is sent nowhere; the cells around a gap give a little as it opens
  and closes.
- **The pen is solved whole.** The page is laid as if every slot were held, so
  the pen is one pocket. An open slot is then whitespace holding exactly the
  ground a cell there would: one site at the slot's seed, with the slot's
  share. The pen keeps its shape at rest whichever slots are open.
- **Matched by distance.** The places the slide adds take the nearest cells
  not benched, and the cells coming home take the nearest niches: greedy, then
  2-opt on squared travel (the engine's matching). A cell keeps what it is on
  or bound for, so an interrupted change is planned from where everyone was
  going.
- **The cast that stays holds still.** A card the next slide keeps is not
  re-seated: it is pinned on its place, a wall for the change, as Tell II's
  cast was. At the root nothing else is a wall, and a spring alone let passing
  cells nudge it and the whitespace beside it swell it.
- **The bench.** When a new sequence begins, the last sequence's cast may not
  take a place, so a fresh cell comes out.
- **The whitespace is cut once.** The page, less every place and the pen, is cut
  along their edges (Tell II's cut). An empty place and an open niche are
  pieces of their own. The door, the strip between the stage and the pen, is
  cut across at the edges of the pen's slots along it.
- **Whitespace a cell will brush is cut again.** A piece with a site within a
  traveller's reach of its path (half the side of the square it will fill)
  does not keep its identity across the change. It closes as the traveller
  comes and reopens once it has passed (Portal's rule). Every other piece
  holds: whitespace that closes leaves the auction's total short, and every
  settled cell is then handed more ground than its own.
- **Every cell is one card on a story**, as on a page: no gallery opens a field.

## Measured (1440×900, 12 cells, 30 ms frames; scratchpad instruments)

The frame, through each change: the worst area and spill of the cells that stay
(spill is how far a cell's outline reaches past its rest cell's bounds).

| | Stage cells that stay | Pen cells that stay | Traveller's area |
|---|---|---|---|
| First revision, ordinary slides | ×1.22–1.93, 159–479 px | none (the pen re-laid) | ×1.46–2.42 |
| This revision, ordinary slides | ×1.00, 0 px | all but the one going out: ×1.01–1.44, 66–161 px | ×1.00–1.46 |
| This revision, fresh slides | (none stay) | all but the one going out: ×1.23–2.45, 132–330 px | ×6.5–8.8 |

| Transition | Worst fling (px) | Flings over 40 px | Peak/mean speed | Area spike max |
|---|---|---|---|---|
| Engine scenes (bento, hero, sidebar, frame, flock) | 11–123 | 0–2 | 2.4–5.0 | 1.1–1.7 |
| Tell II slides | 77–454 | 2–17 | 8.3–13.0 | 27–62 |
| Cue entry | 125 | 6 | 3.5 | 1.3 |
| Cue slides (ordinary) | 6–35 | 0 | 1.9–2.3 | 1.1–1.4 |
| Cue slides (fresh) | 116–174 | 5–9 | 3.5–4.2 | 1.6–1.7 |

A fling is a cell's diagram centroid moving more than its own seed in one
frame, which reads as a wall swinging it.

What was tried on the way here:

- Cutting again every piece a traveller crosses (the first revision) closed so
  much whitespace that the auction's total fell short: the pen spilled 200–400
  px out of its frame and travellers ballooned over the text.
- Handing that shortfall to the travellers, on Plumb's hump, ballooned them
  further (×2.5–3.2 on ordinary slides) and did little for the pen.
- Holding all the whitespace around the pen kept it in frame but threw the
  cells coming home (up to 287 px), their paths running over the mirror sites
  that hold the pen's edge.
- Whitespace stepping aside from a traveller (its sites held off at a radius)
  kept its claim and the pen in frame, but did not reduce the flings.
- Pieces no larger than the grid, or a gutter around each place, brought flings
  back everywhere.

## Known

- **Fresh slides are still busy.** Three cells go home while one comes out, all
  through the door. The cells going home squeeze along the page's top edge,
  the pen gives around the door (up to 330 px on one slide), and 5–9 frames
  fling a cell by more than 40 px.
- **Exact to 4 px at rest, not 2**, outside the pen. No weights are handed
  over, so the live auction settles a hair off the authored diagram where two
  pieces of whitespace meet a cell's corner. The pen's cells and niches are its
  pocket's power cells, not rectangles.
- **A change takes 2.3–3.6 s**, as the engine's journeys run.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed. Without the
Cue button, 17,332 frames and 15,708,550 drawing commands are identical to
Tell II's (the scene matrix, a click, a scroll, a drag, a Tell story, a Tell II
story and home). With the story, on a desk and a phone, it checks every slide
settled (the cast on its places, every other cell on a slot of the pen, one
open niche per cast member), every change (the cast that stays does not move,
the pen's cells that stay are sent nowhere) and a notch back through the
slides (see `validation.json`).

## Run

```bash
python3 tests/cue/build.py
node tests/cue/validate.cjs
```
