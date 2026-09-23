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

## The page

A page is a claim table, like the engine's own scenes: every cell one site
with a rectangle as its destination and its claim, the text a void. Cells
are convex power cells, straight where they meet the whitespace or the
page and organic where they meet each other. That is the rule this
repository's marks have kept since Bleed, and the one Caption keeps: a cell
is either an axis-aligned rectangle or a convex Voronoi cell of a point
site, cut straight where it meets a rectangle or the page's edge, and an
edge fractured beyond what fitting requires is a fault. No cell here has a
lattice of sites; nothing is subdivided.

**The whitespace is exact by construction**, the way the Hero and Frame
scenes' voids are. The cells' weights are solved for their rectangles'
areas with the voids cut out of the domain, one solve per pocket the voids
leave. Then every cell the solve puts against a void's edge is mirrored
across that edge into the void, at the weight that makes the pair tie
exactly along the edge's whole line. The mirrors tile the void; their seams
with one another meet the edge where the cells' own seams do; a cell that
does not touch the void has the higher power all along it. Nothing else is
inside the void, so it is drawn as its rectangle, and the auction is handed
that diagram's areas, which are the rectangles' own. The engine change is
one line: a page kind is dispatched to its authored rest diagram as the
Hero and Frame scenes are.

Two rules make that hold, and the templates keep them:

- **A void's corners are page corners, or another void's.** A cell that met
  a void at a corner of it would need the mirrors across two edges to
  agree, and a single site's power varies along its own edge by the square
  of half that edge's length; nothing makes them agree.
- **The cards that touch the hero stand beside its short edge, far across
  from its centre.** A seam between two cells is square to the line
  between their sites, so a card offset far along the hero's edge and close
  across it is a wedge. Where the hero meets only whitespace and the page,
  it is a rectangle.

A pocket's weights are gauged so the mean power at its contacts with the
whitespace is zero, and a mirror sits close behind its edge: a cell's power
along its edge varies by the square of half the edge's length, and the
mirrors from a void's far side must stay above that all along it, which
they do when the void is at least that half-length deep or ends at the
page. The spread's reading column widens on a squarer screen for that
reason. In portrait every kind stacks: the image, its text, the cards.

## The change

A click is a scene change like any other: the same journeys, the same
percolation from the point clicked, the same clocks. Four things are the
page's own, because a page asks more of a change than a scene does: one
cell grows to a third of the page or more, and the rest cross it.

- **The page opens on the side the click came from.** The template is
  mirrored left-right when its image slot is nearer the click that way, so
  the clicked cell grows where it is instead of leaping across the page.
- **The image grows no faster than the page clears for it.** Its journey,
  and so its claim, ends when the last card's does. Left on its own clock
  it was full size in under a second while the cards still had two seconds
  to go, and crushed them into slivers against the edge.
- **A page's whitespace waits for the cells whose journeys pass through
  it.** They are on its ledger, and it does not open on its own clock until
  the last of them is through, so nothing crosses it as a sliver and its
  text is not set under a traveller.
- **Long journeys take the time they need.** The engine caps a journey at
  2.2 s and a seed at 900 px/s; a card crossing the page hit both and moved
  in a straight line at one speed. On a page a journey lasts at least its
  length over 600 px/s, so an eased trip peaks under the cap.

Measured on the same engine, the same twelve cells, a click and a button:
a page change has the shock and the jumps of a scene change and a few more
cells thin for a frame; where it differs is length, about three seconds
against two and a half, which is the cards' distance.

## The kinds

A cell's kind is its id modulo the number of kinds, so pages repeat without
being unique. The set is in `PORTAL_TEMPLATES` in the builder:

- **Spread**: the image a full-height column on the left, the text a
  column beside it, the cards a grid down the right. The image is a
  rectangle. A magazine opening.
- **Folio**: text, image, cards, left to right. The reading column is the
  page's margin.
- **Showcase**: a column of thumbnails, the image, the text at the right.
  A product page.
- **Band**: the image top left with cards beside it, the text a band across
  the bottom, in two columns.
- **Lead**: the text a band across the top, the image and the cards below
  it. A headline and standfirst over the picture.
- **Documentation**: a grid of cards, the text, the image, in three
  columns. The image is a rectangle. A manual.
- **Essay**: the image centred at the top with thumbnails at its sides,
  the text centred under it between white margins. The image is a
  rectangle. A long read.
- **Caption**: no text block. The image fills the page but for one column
  of cards, its title and one line set in its own corner. Enough for a
  picture that only needs a caption.

Five of these came out of a judged panel of ten designs and were then
re-cut to the two rules; the rest were added for the shapes the panel
lacked. Rules are 1 px hairlines at 22% white along the chosen edges of
the text block, drawn in the gap. Style only; nothing reads them.

## Visible change

- **A click on a cell opens its page.** The change spreads from the point
  clicked, so the page opens outward from the cell you touched. A member of
  a field opens the field.
- **On a page every cell is one card.** Fields are not rostered while a page
  is open; the browsing cards stay cards.
- **The image carries no label** on a page with text: its title is set in
  the reading void beside it. On a full-cell page the title and one line sit
  in the image's bottom-left corner, or a little higher where a seam cuts
  that corner off. The image does not hover; the cards beside it do, and
  the page recovers.
- **The text fades in with its void**: the image's name as a title with a
  short rule under it, and its paragraphs as bars, in one measure or in two
  columns when the block is a band wider than two measures and the first
  column runs out. On a phone the page stacks and the text is set full
  width.
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
  opens from its cell; on every one of the seven seconds' frames through the
  change and at rest, no root cell is fractured by the shape lens's rule
  (`.claude/gauntlet/shape.js`: a reflex corner no rigid neighbour or page
  edge explains); at rest the clicked cell's rect is the scene's first
  slot, it is the largest cell, no cell is a field, every cell has one
  site, every point of the whitespace's outline lies in the rectangles the
  whitespace was given and no cell's vertex lies inside them, and the seam
  residual is under 0.3%. On a page with text the title is drawn inside the
  seated reading void with paragraph bars, the image carries no label and
  no stray text; on a full-cell page there is no whitespace and the caption
  is drawn below the image's centre.
- The page opens on the side the click came from: for three kinds the
  image's slot is the nearer of the template's and its mirror. The reading
  void's text is set only after the last cell whose journey crossed the
  void has landed.
- Clicking the image returns to Bento with every root cell numbered. A
  member's click opens its field as one card. A click on the reading void
  does nothing. A click 0.3 s into a change wins the change. `home()`
  (Escape) returns to Bento. The image does not hover, a card beside it
  does, and the whitespace is exact again after the pointer leaves. Adding
  and removing a cell on an open page keeps the image in its slot and the
  whitespace exact. At 390 x 720 every kind opens the same way, stacked,
  with its text set full width.

Edges under 2 px, a three-way junction a hair off, are counted apart from
fractures and reported: Plaque's own scenes draw them too.

There is no benchmark: a page carries a few more seeds than a scene (one
mirror per cell against the whitespace), the same order as the Hero scene's.

## Reproduce

From the repository root:

```sh
python3 tests/portal/build.py
node tests/portal/validate.cjs
```

The builder writes only `portal.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/portal.html` on the deploy
preview to judge it. Prior marks are unchanged.
