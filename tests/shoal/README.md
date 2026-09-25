# Shoal: a group moves as one

Baseline: Tandem, `tandem.html` on this branch, SHA-256
`d891f8e3da06266b3b47ac6b6430c7bb677beae969f0b6a5da7485ef877fbe1b`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Changes into and out of Moss (the band page, its text a row across the foot)
were the worst on Tandem. The cells of a column had to turn into a row, and
they came apart on the way. A turn is a curve on which the inner cells travel
less than the outer ones, and when nobody knows in advance who is inner and
who is outer, the group scrambles. Shoal does not add a rule for band pages.
It changes how the engine moves any group from one layout to another, in the
home scenes and on pages alike.

## Why a group came apart

- **Who went where could not tell inner from outer.** The engine matched
  cells to places by least *squared* travel. Turning a column into a row costs
  exactly the same under that measure whoever goes where: the cross terms
  cancel. So the matching was arbitrary exactly where a turn needs it to be
  exact, and paths crossed. On a tour of 15 changes the matching planned 52
  pairs of crossing paths; the changes into Moss planned 8 to 10 each.
- **Every cell kept its own clock.** A cell set off when a wave from the
  pointer reached it, with a random delay on each step of the wave. It took
  its own time, with a random stretch, and bent its path by its own random
  amount. Neighbours never moved together, so even paths that did not cross
  met in time.

## The rules

- **Who goes where: least total travel.** Two paths that cross can always be
  swapped for two that do not, which are shorter together. So the matching of
  least total travel never crosses: on a turn the inner cells take the inner
  places and the outer cells the outer. Among matchings of the same total,
  squared travel breaks the tie, so a row shifting along steps every cell a
  little rather than sending one cell the length of the row. It is found
  exactly (Kuhn–Munkres). On a page, the image is held to its slot, the rest
  are matched around it, and any pair the tie-break let cross is swapped back.
- **One clock.** Every cell of a change sets off together and lands together.
  Paths that do not cross, run on one clock, never meet. On a turn the group
  wheels, the outer cells travelling farther in the same time. The change
  takes as long as its longest journey needs.
- **One bend.** Every path is bent by the swirl's own amount, no cell more or
  less than another.

While a story is told (Tell, Tell II, Cue), a change is Tandem's: the stories
keep their own choreography.

## Measured (scratchpad instruments, 12 cells, 60 fps)

**Group tour.** 15 changes: the home scenes (frame, sidebar, hero, flock,
bento), then pages opened from home and from one another (Moss, Aurora, Coal,
Moss, Petal, Moss, home, Coal, Aurora, home).

- **Crossing paths:** pairs of planned straight paths that cross.
- **Near-collisions:** pairs of travellers whose seeds come within 0.35 of
  their reaches added.
- **Against:** the share of neighbouring travellers moving in opposite
  directions.
- **Flings:** a cell's drawing outrunning its seed by more than 30 px in a
  frame, summed.
- **Slivers:** frames of a cell drawn thin, not counting rectangles.

| Group tour | Tandem | Shoal |
|---|---|---|
| crossing paths, 1440×900 | 52 | 22, all the image's |
| near-collisions, 1440×900 | 28 | 15 |
| neighbours moving against each other, 1440×900 | 11.6% | 6.4% |
| flings, 1440×900 | 12,261 px | 4,510 px |
| slivers, 1440×900 | 292 | 142 |
| time the changes take, 1440×900 | 46.6 s | 40.7 s |
| flings, 1920×1080 | 16,825 px | 8,722 px |
| slivers, 1920×1080 | 258 | 160 |
| flings, 390×720 | 1,254 px | 747 px |
| near-collisions, 390×720 | 21 | 21 |
| slivers, 390×720 | 412 | 421 |

**Page tour.** Tandem's 18 openings at 1440×900 (home to each kind, and page
to page).

| Page tour | Tandem | Shoal |
|---|---|---|
| text lag | 513k px²·s | 438k px²·s |
| image outside its rectangle | 1,308k px²·s | 954k px²·s |
| worst fling | 491 px | 175 px |
| flings | 7,893 px | 3,718 px |
| slivers | 363 | 247 |

At 1920×1080 (7 openings), flings fell from 6,124 to 3,356 px and the worst
fling from 1,190 to 209 px. Moss → Aurora, where Petal was pressed into a
needle, fell from 2,060 to 113 px.

## Known

- **The image still crosses the group.** It is held to its slot, so it
  crosses whom it must, and about half the near-collisions left are the
  image's.
- **On a phone the group holds about as well as on Tandem.** Flings fall by
  about half, but near-collisions and slivers are within a few percent
  either way. A phone's pages stack, and cells have little room to pass.
  Dune opens worse there (8 near-collisions against 3).
- **Aurora → Dune at 1920×1080 slivers more** (47 frames against 21), though
  its worst fling fell from 1,190 to 198 px.
- **The matching counts distance, not size.** On a phone's frame scene, a
  single cell rather than a field takes the tall strip down the side: a thin
  rectangle, correct but plain.
- **The stories are Tandem's.** Tell, Tell II and Cue keep their own
  choreography.
- **The stagger slider no longer shapes a scene change.** With one clock
  there is no wave to stagger. It still paces the flock's release.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed.

**Group checks.** On a tour of 21 changes (the home scenes, then pages of
every kind, from home and from one another), at 1440×900 and 390×720:

- every change runs on one clock: every traveller sets off at nought and takes
  the same time;
- no two planned paths cross, except the image's;
- nothing fractures on any frame;
- every page at rest is exact as on Tandem: the image on its rectangle and
  covering it, the text covering its own with the title in it, the whitespace
  exact, no field, one site to a cell;
- on a desk, near-collisions, flings and slivers are no more than on Tandem;
- on a phone, flings are fewer, and near-collisions and slivers are within 5%
  of Tandem's.

| Validator's tour, 21 changes | Tandem | Shoal |
|---|---|---|
| crossing paths, not the image's (desk / phone) | 49 / 25 | 0 / 0 |
| near-collisions (desk / phone) | 46 / 39 | 31 / 38 |
| flings (desk / phone) | 15,603 / 2,856 px | 6,937 / 1,561 px |
| slivers (desk / phone) | 601 / 453 | 523 / 455 |
| fractured cell-frames | 0 | 0 |

**Story checks.** Cue's own story checks pass on Shoal's Cue story, on a desk
and a phone:

- the slides settled;
- every change;
- a slide scrolled on before its change ends;
- a notch back through the slides.

A Tell and a Tell II story also run to their end and home without a fractured
cell. Tandem's figures are reported beside Shoal's in `validation.json`.

## Run

```bash
python3 tests/shoal/build.py
node tests/shoal/validate.cjs
```
