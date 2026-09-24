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
the engine decides who comes out.

## The rules

- **Matched by distance.** The cells take the slots nearest them: greedy, then
  2-opt on squared travel (the engine's `assignStations`). The cluster's front
  cell comes out, and the cells going home go where the cluster has room. Paths
  do not cross, so seeds never pass close to each other.
- **Bystanders.** A cell sitting exactly on a place the new slide keeps holds
  it, as a body sitting where a scene puts it does. Without this, squared
  travel prefers to shift the whole cast one place along rather than bring one
  cell the whole way out.
- **The bench.** When a new sequence begins, the last sequence's cast may not
  take a place, so a fresh cell comes out. This is the one rule the story adds.
- **The whitespace is cut once.** The page, less every place and the cluster, is
  cut along their edges (Tell II's cut). An empty place is a piece of its own,
  so a slide changes only the pieces a cell lands in or leaves.
- **Whitespace a cell will cross is cut again.** A piece on a traveller's path
  does not keep its identity across the change. It closes as its crossers come
  (they are on its ledger until they enter it), and the new piece waits for
  them to pass before it opens (Portal's rule). A piece that stays with other
  mirrors is re-seated on its own clock, like any body given a new rectangle,
  so its claim eases instead of stepping.
- **Every cell is one card on a story**, as on a page: no gallery opens a field.

None of Tell II's own machinery runs: no planned revolver or slots handed out,
no yielding whitespace, no handed weights, and no cast held as walls.

## Measured (1440×900, 12 cells, 30 ms frames; scratchpad instruments)

| Transition | Worst fling (px) | Flings over 40 px | Peak/mean speed | Area spike max |
|---|---|---|---|---|
| Engine scenes (bento, hero, sidebar, frame, flock) | 11–123 | 0–2 | 2.4–5.0 | 1.1–1.7 |
| Tell II slides | 77–454 | 2–17 | 8.3–13.0 | 27–62 |
| Cue entry | 60 | 6 | 3.1 | 1.3 |
| Cue slides (ordinary) | 26–64 | 0–3 | 2.7–4.3 | 1.4–2.0 |
| Cue slides (fresh) | 30–40 | 0 | 3.0–4.0 | 1.4–1.8 |

A fling is a cell's diagram centroid moving more than its own seed in one
frame, which reads as a wall swinging it.

What each rule was worth, measured on the way here:

- Portal's rule that new whitespace waits for its crossers took the entry from
  26 flings to 1.
- Re-cutting crossed whitespace took the fresh slides' worst fling from 292 px
  to 45 px.
- Cutting the whitespace per slide instead of once had a cell on the stage bend
  into a sliver whenever its neighbouring pieces were re-cut.
- A gutter of whitespace around each place, or pieces no larger than the grid,
  kept the stage cells steadier but brought flings back (13 on the entry, up to
  11 on a fresh slide), because more pieces put more mirror sites in the
  travellers' way.

## Known

- **A cell on the stage swells** while a traveller crosses the whitespace
  beside it, up to about 1.6× its area, then back. That whitespace is a column
  strip the length of the page, and a crossing anywhere along it cuts all of
  it again. Finer pieces fix the swell and cost flings; this mark keeps the
  flings down.
- **A cell on the stage is nudged** up to 16 px by a cell passing it (10 px on
  a phone), then springs back onto its place. Nothing is a wall at the root,
  so a bystander is held only by its spring. Tell II held its cast still by
  making it walls.
- **Exact to 4 px at rest, not 2.** No weights are handed over, so the live
  auction settles a hair off the authored diagram where two pieces of
  whitespace meet a cell's corner (3.3 px at worst).
- **A change takes 2.3–3.0 s**, as the engine's journeys run.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed. Without the
Cue button, 17,332 frames and 15,708,550 drawing commands are identical to
Tell II's (the scene matrix, a click, a scroll, a drag, a Tell story, a Tell II
story and home). With the story, on a desk and a phone, it checks every slide
settled, every change and a notch back through the slides (see
`validation.json`).

## Run

```bash
python3 tests/cue/build.py
node tests/cue/validate.cjs
```
