# Plaque: labels that belong to a settled cell

Baseline: accepted Caption on main, commit
`ca142d8` (PR #266), `caption.html` SHA-256
`b595913da13062c7f0acfb1db15d0b65fe4ee30c17f9fe02829fa770005922c5`.
The builder reads that file from the repository root and checks the hash.

## Visible change

Text only. Cell motion, hover, the auction, voids and every cell fill and
stroke are Caption's.

- **A travelling cell carries no text.** While a cell, or the field it sits
  in, has a journey in progress, its label fades out in about 60 ms and no
  label geometry is computed for it: no centroid, no fit, no text
  measurement, no `fillText`. The label returns over about 220 ms when that
  cell lands, so names come back with the cells that arrive first. Hover,
  Flock drift and resize are not journeys: labels stay and follow.
- **Type is set per viewport, never per cell or per hover.** 32/20/13 px for
  root numbers, nested numbers and names from 1200 px wide, scaling down to
  20/12/11 px on a phone. It changes only on resize.
- **A label is fitted as the box it prints,** using measured text widths, 3 px
  of padding and 3 px of ink clearance, with 3 px of hysteresis, against the
  same ink outline and holes Caption used. The number keeps its place when
  the name below it no longer fits; the number goes when it no longer fits.
  Caption's discs demanded 34 px of clearance for a 32 px numeral that
  measures 45 x 23 px, which is why phone layouts lost most of their labels.
- **Centroid first, pole second.** A label sits at the ink's area centroid.
  When the box does not fit there (a concave shape), it moves to the
  inscribed pole the steering anchor already computes for cell motion, at no
  extra cost. Which of the two is in use has hysteresis.
- **An 80 ms lag on position,** no spring. A label follows its ink through a
  first-order lag, so a change of place (a split cell's larger piece, the
  centroid/pole switch) is a short glide, never a jump. A label that has not
  been drawn for 100 ms starts fresh at its new place rather than sliding in.
- **Fields are named.** A field's members carry numbers only, so the field's
  own number and name go in a small tag near the top-left corner of its cell,
  above its members, on the same clocks as every other label. A narrow field
  gets the name alone. This is the one new visual element; it is a single
  `plaqueTag` call in the builder if it should go.
- Room is re-measured every 250 ms, or when the ink's area moves by 1%; the
  place is updated every frame. The measured text widths are cached per font.

No header controls were added. Fonts, alpha (0.48 numbers, 0.72 names, +0.20
on hover) and the ink clip are Caption's.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed,
Caption and Plaque side by side on the same clock:

- 13,506 frames have exactly equal cell/steering state, final leaf
  geometry, movement-anchor state and gap/overlap meter results.
- 710,850 cell fill/stroke operations match exactly, including paths,
  gradients, opacity, stroke width and shadow blur. Text and the field tags
  are intentionally different.
- Covers all layouts, both void crossings, hover/release, interrupted
  changes, Organic/Grid fields, add/remove and resize, at 120 Hz, 60 Hz,
  30 ms and 50 ms.
- No text is drawn on a cell that has been travelling for 0.3 s: the 60 ms
  fade passes the 1% draw cutoff at 0.28 s (0 violations over
  129,555 travelling leaf-frames). A third of a second into a change
  from a settled Bento, every travelling cell is bare; four seconds on, every
  root number is back.
- The largest move of a visible label in one frame is 61.9 px, against
  Caption's 332 px. A label's motion is bounded by the 80 ms lag, so at
  50 ms frames a 130 px change of place shows as a 60 px step, never a jump.
- At 1900 x 810 every settled layout shows all 12 numbers and all 12 names
  (Caption showed 11 names in Hero). With fields on, every root cell keeps
  its number and name and every field carries its tag. A settled cell still
  acquires hover with its number at its fixed size.
- At 390 x 720 with no fields the settled layouts show 12, 11, 8, 12 and 12
  numbers (Bento, Hero, Sidebar, Frame, Flock); Caption's Sidebar showed
  none. With fields on, every layout keeps at least three root numbers.

Label stability over the standard 1600-frame probe run (five scene changes
and two hovers), measured on `probe.cjs` with a session script; the
travelling and step figures are the ones `validate.cjs` reproduces:

| | Caption | Plaque |
|---|---|---|
| Label moves over 30 px within its cell, per frame, while visible | 75 | 0 |
| Settled label wander, max | 1.7 px | 2.0 px |
| Label visible on a travelling cell | always | never |
| Root numbers visible, 390 x 720, share of frames | 47% | 58% |

Plaque's labels fade out and in once per cell per change by design, so a
raw flip count is no longer a flicker measure.

`benchmark.cjs` runs the full tick in Node with native Canvas, GPU, layout
and compositor excluded; it is a CPU regression check, not a browser FPS
claim. Five alternating-order pairs per workload after two warmups:

| workload | Caption ms | Plaque ms | change |
|---|---|---|---|
| default transitions (12 cells, fields 0.55) | 2,039 | 2,015 | -1.1% |
| dense transitions (24 cells, fields 1) | 3,730 | 3,788 | +1.5% |
| settled sidebar (12 cells, fields 0) | 697 | 731 | +4.9% |

There is no measurable CPU saving. All three differences sit inside this
benchmark's run-to-run spread (6% to 21% between the five samples of one
mark). Label geometry was already a small share of the tick; the steering
anchor's pole search stays because cell motion reads it; and at rest Plaque
re-measures its room on a 250 ms clock, which costs about what Caption's
per-frame disc test did. Over the validation fixture Plaque issues 347,694
text draws against Caption's 304,590, because it labels more at rest (names
on every desktop cell, phone cells, field tags) and none while a cell
travels. The fade earns its place visually, not in the profiler.

## Reproduce

From the repository root:

```sh
python3 tests/plaque/build.py
node tests/plaque/validate.cjs
node tests/plaque/benchmark.cjs
```

The builder writes only `plaque.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a separate promotion PR; open `/plaque.html` on
the deploy preview to judge it. Prior marks are unchanged.
