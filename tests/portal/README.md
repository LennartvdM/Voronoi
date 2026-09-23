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

## What a page is

Every page is the same three things. The page's **text**, set in a reading
void where it is not read through a photograph. One large **hero image**,
the clicked cell, pinned to the scene's first slot. A **gallery** of the
other cells to browse. The cells are meant to carry photographs, so text
on top of them is a caption at most; the reading lives in the whitespace.

Three kinds, by the cell's id (`id % 4`, two of the four articles), so a
page is recognisable without being unique:

- `article`: the engine's own Hero scene, whose void its source already
  calls the reading column. Text at the left, the image beside it, the rest
  in strips around the image. The manifold void keeps the column's edge
  straight.
- `gallery`: the image at the left, the reading column beside it, a column
  of cells to browse at the right.
- `caption`: the full-cell section, allowed but not the way to run a site:
  the image is the page, its name and one line sit in its bottom-left
  corner, the rest in a narrow column at the right. No whitespace.

An earlier draft opened every cell into its own section (a two-thirds
block, a centred hall, a reading column with the image as the column). It
was rejected by the owner: it defeats the void, and it puts reading text on
photographs.

## Visible change

- **A click on a cell opens its page.** The change spreads from the point
  clicked, so the page opens outward from the cell you touched. A member of
  a field opens the field.
- **The image is one card.** A cell whose slot is roomy would normally be
  rostered as a field of members; the open page's image never is. It keeps
  its Plaque label as its caption and does not hover; the cards beside it
  do.
- **The text fades in with its void**: once the reading void has seated,
  the image's name as a title and its paragraphs as bars, three runs of
  them, as many as the column holds. A reading column narrower than 90 px
  (a phone) gets no text.
- **Home**: click the image, or press Escape. A scene button also leaves
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
- With clicks, at 1900 x 810 with fields at 55%: each kind opens from its
  cell; five seconds on, the clicked cell's rect is the scene's first slot,
  it is the largest cell on the page, it is not a field, it is labelled. On
  an article or gallery page the title is drawn inside the largest seated
  void and the paragraph bars are drawn; on a caption page there is no
  whitespace and the caption is drawn below the image's centre. No stray
  text is drawn on the image.
- Clicking the image returns to Bento with every root cell numbered. A
  member's click opens its field as one card. A click on the reading column
  does nothing. A click 0.3 s into a change wins the change. `home()`
  (Escape) returns to Bento. The image does not hover while a card beside
  it does. At 390 x 720 a click opens a page the same way.

There is no benchmark: nothing runs per frame that did not before, apart
from the prose in one void.

## Reproduce

From the repository root:

```sh
python3 tests/portal/build.py
node tests/portal/validate.cjs
```

The builder writes only `portal.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/portal.html` on the deploy
preview to judge it. Prior marks are unchanged.
