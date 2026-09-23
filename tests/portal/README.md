# Portal: a click on a cell opens that cell's page

Baseline: Plaque, `plaque.html` on this branch, SHA-256
`1fb47c3acf61e10ac996682bd85d340f34ed9f0d3503b798f656db4bcf1458ef`.
The builder reads that file from the repository root and checks the hash.

## What it proves

That the cells are atoms of a web page: the same twelve elements rearrange,
on a click, into serious web structures, and back. Until Portal nothing on
the page could be clicked; hover, the scene buttons and the sliders were the
only input.

## What a page is

Every page is the same three things. The page's **text**, set in a reading
void where it is not read through a photograph. One large **hero image**,
the clicked cell, pinned to the scene's first slot. A **gallery** of the
other cells to browse. The cells are meant to carry photographs, so text on
top of them is a caption at most; the reading lives in the whitespace.

## The page grid

A page is a rectangular partition of the lattice, written as a template in
fractions of the page:

```
folio: { cols: [0.24, 0.46, 0.30], rows: [1],
         image: [1, 0, 2, 1], text: [0, 0, 1, 1], gallery: [[2, 0, 3, 1]], rules: ['right'] }
```

`image` is the hero block, `text` the reading void (or `null` for a
full-cell page), `gallery` the regions the other cells are cut into as rows
of rectangular cards, and `rules` the edges of the text block that get a
hairline. The blocks must partition the grid.

The engine draws root cells as free bodies in a power diagram, so a cell is
a rectangle only where its neighbours' seeds line up with its own. A void
already gets one seed per neighbouring cell so that its seams come out
straight (the Plumb and Weave lineage). Portal extends that to content: every
block is subdivided by the union of the page's cut lines and carries one
site per sub-cell. Adjacent sub-cells across any seam then share an extent,
and the power diagram at rest **is** the partition: every seam straight,
every cell a four-vertex rectangle, on every page kind, at every count. In
transit the sites ride with their body, and the page is as organic as it
ever was. The engine change is three lines: a content body with sites on its
rest rectangle takes them as its formation, and keeps them when its
formation is refreshed.

The meters report a few hundred px² of gap or overlap on a settled page.
That is rasterisation of exact seams, not geometry: a pixel sampler finds
no overlap anywhere and "gaps" only on points lying exactly on cut lines
that fall on integer pixels. `validate.cjs` allows a residual under 0.3% of
the page and asserts the rectangles directly.

## The kinds

A cell's kind is its id modulo the number of kinds, so pages repeat without
being unique. The set is in `PORTAL_TEMPLATES` in the builder; each was
judged on a settled screenshot and its lab metrics before it was kept.

## Visible change

- **A click on a cell opens its page.** The change spreads from the point
  clicked, so the page opens outward from the cell you touched. A member of
  a field opens the field.
- **On a page every cell is one card.** Fields are not rostered while a page
  is open; the browsing cards stay cards.
- **The image carries no label** on a page with text: its title is set in
  the reading void beside it. On a full-cell page the title and one line sit
  in the image's bottom-left corner. The image does not hover; the cards
  beside it do, and the page recovers.
- **The text fades in with its void**: the image's name as a title with a
  short rule under it, and its paragraphs as bars, in one measure or in two
  columns when the block is a band wider than two measures. A reading column
  narrower than 90 px (a phone) gets no text.
- **Rules**: 1 px hairlines at 22% white along the chosen edges of the text
  block, drawn in the gap. Style only; nothing reads them.
- **Home**: click the image, or press Escape. A scene button also leaves any
  open page. Whitespace is not a cell; a press that moved more than 6 px or
  lasted over half a second is not a click.

Labels are Plaque's, unchanged. No footer controls were added; a one-line
hint sits beside the back link.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without a click, Portal and Plaque produce exactly equal state and
  exactly equal drawing commands: 13,506 frames over all layouts, both void
  crossings, hover, interrupted changes, Organic and Grid fields, add/remove
  and resize, at 120 Hz, 60 Hz, 30 ms and 50 ms.
- With clicks, at 1900 x 810 with fields at 55%, for every kind: the page
  opens from its cell; seven seconds on, the clicked cell's rect is the
  scene's first slot, it is the largest cell, no cell is a field, every root
  cell has exactly four vertices, the rect meter reads 100%, and the seam
  residual is under 0.3%. On a page with text the title is drawn inside the
  seated reading void with paragraph bars, the image carries no label and no
  stray text; on a full-cell page there is no whitespace and the caption is
  drawn below the image's centre.
- Clicking the image returns to Bento with every root cell numbered. A
  member's click opens its field as one card. A click on the reading void
  does nothing. A click 0.3 s into a change wins the change. `home()`
  (Escape) returns to Bento. The image does not hover, a card beside it
  does, and the grid is exact again after the pointer leaves. Adding and
  removing a cell on an open page keeps the image in its slot and the grid
  exact. At 390 x 720 every kind opens the same way.

There is no benchmark: a page carries a few more seeds than a scene (one
per sub-cell), the same order as a field's members.

## Reproduce

From the repository root:

```sh
python3 tests/portal/build.py
node tests/portal/validate.cjs
```

The builder writes only `portal.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/portal.html` on the deploy
preview to judge it. Prior marks are unchanged.
