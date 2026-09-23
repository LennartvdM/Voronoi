# Portal: a click on a cell opens that cell's page

Baseline: Plaque, `plaque.html` on this branch, SHA-256
`1fb47c3acf61e10ac996682bd85d340f34ed9f0d3503b798f656db4bcf1458ef`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Navigation. Until now nothing on the page could be clicked: hover, the
scene buttons and the sliders were the only input. Portal makes a cell the
thing that triggers a transition, using only what the engine already has:
a scene is a claim table, a change spreads from a point, assignment decides
who takes which slot.

## Visible change

- **A click on a cell opens its page.** The page is a scene of the cell's
  kind with the cell pinned to the scene's first slot, the focus. The
  change spreads from the point clicked, so the page opens outward from
  the cell you touched. A member of a field opens the field.
- **Three page kinds, by the cell's id** (`id % 3`), so a page is
  recognisable without being unique:
  - `story`: the focus fills the left two thirds, the rest are listed in a
    column at the right.
  - `hall`: the focus is centred, the rest flank it in two columns.
  - `reader`: a nav column at the left, the focus as a reading column, a
    margin of whitespace at the right.
  Each keeps the focus's boundaries near-vertical. A banner layout (a wide
  focus above a row of cells) was tried and rejected: a power diagram fans
  the row into wedges under a wide neighbour, the same effect the Plumb
  lineage fought for voids.
- **The focus is one card.** A cell whose slot is roomy would normally be
  rostered as a field of members; the open page's focus never is.
- **The focus reads as a page**: three lines of body text, as bars, under
  its name, when they fit the ink. It does not hover; the cards beside it
  do.
- **Home**: click the focus, or press Escape. A scene button also leaves
  any open page. Whitespace is not a cell; a press that moved more than 6 px
  or lasted over half a second is not a click.

Labels are Plaque's, unchanged. No footer controls were added; a one-line
hint sits beside the back link.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without a click, Portal and Plaque produce exactly equal state and
  exactly equal drawing commands: 13,506 frames, 12,887,553 commands, over
  all layouts, both void crossings, hover, interrupted changes, Organic and
  Grid fields, add/remove and resize, at 120 Hz, 60 Hz, 30 ms and 50 ms.
- With clicks, at 1900 x 810 with fields at 55%: each of the three kinds
  opens from its cell; five seconds on, the clicked cell's rect is the
  scene's first slot, it is the largest cell on the page, it is not a
  field, its number and name are shown and its body text is drawn.
- Clicking the focus returns to Bento with every root cell numbered.
  A member's click opens its field as one card. A click on the reader's
  margin does nothing. A click 0.3 s into a change wins the change. `home()`
  (Escape) returns to Bento. The focus does not hover while a card beside it
  does. At 390 x 720 a click opens a page the same way.

There is no benchmark: nothing runs per frame that did not before, apart
from three rounded bars on one cell.

## Reproduce

From the repository root:

```sh
python3 tests/portal/build.py
node tests/portal/validate.cjs
```

The builder writes only `portal.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/portal.html` on the deploy
preview to judge it. Prior marks are unchanged.
