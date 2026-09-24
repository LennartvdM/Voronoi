# Tell II: a small cluster, and the cells take the stage in turn

Baseline: Tell, `tell.html` on this branch, SHA-256
`0cd09badc2ed802684a9883c28474480a65265e0d123555eb9df93b663e03c93`.
The builder reads that file from the repository root and checks the hash.

## What it proves

A scroll-tell with the cluster as its cast, and transitions that move as
little as the story needs. The cluster is small and sits to one side; the
blurb stands in the open, in a box of its own. The story is a set of
sequences: a slide sends one cell out of the cluster to a place around the
blurb (above it, below it, beside it, on its diagonals, where a corner
lies behind the text) and the cells already on the stage stay where they
are, so a sequence builds up one, two, three; the next sequence sends them
back into the cluster as its own first cell comes out. The cluster is a
revolver: a ring of chambers around a bore, holding the cells not on
stage in the order they will go out, so it always has the right poise.
Every slide is a page like Portal's, one site a cell and the whitespace
exact by the same construction.

## What a tell is here

**The stage.** Three columns and three rows of places around the blurb's
box, in fractions of the page: a place is a column by a row (top, below,
left, right, and the four diagonals). The rows touch and the places lie on
a few shared lines, so the whitespace between places is never a sliver. The
box reaches a little over the places beside it, so a place on a diagonal
has its corner behind the text; the text is painted over whatever is
there. On a phone the stage is a row of three places under the box, a
place's column fixed for the story, so a cell on the stage never moves for
a newcomer.

**The revolver.** The cluster stands at the right, well off the stage
(nearer, a cluster cell's mirror would cut a corner of a cell on a place).
Its chambers are the rim of a g by g grid, g chosen so the rim holds every
cell (four by four for twelve); the bore is what the rim leaves. The ring
is ordered from the chamber facing the stage, the middle of the cluster's
left side (its top on a phone), round the rim, so the chambers just behind
the front come last. The cells not on stage fill the ring from the front in
the order they will go out. The front chamber fires: its cell goes to its
place, and every cell behind it moves up one chamber, a ripple the engine's
own percolation runs round the ring from the front. On a fresh slide the
last cast comes back first, into the spent chambers just behind the front,
in the order it went out, and the sequence's first cell fires in the same
change. The bore and the spent chambers are whitespace.

**The plan.** The story is planned when it begins, from the cells in id
order: the ring holds them all; a slide takes the front cell for its
place; a fresh slide sends the cast to the tail first. So every slide's
page is known from the start, the same every time the story is read, and
the engine is told which cell takes which slot: nothing is matched by
distance.

**What moves at a change.** One cell out, and the ring one chamber; on a
fresh slide the cast back as well. The cells already on the stage are
bystanders, as a settled cell is on the engine's own pages: not re-seated,
no journey, so they do not drift off while they wait for a change that is
not theirs. No path crosses another's on an ordinary slide. The whitespace
keeps every piece but the place taken and the chamber vacated; a piece
kept across a change takes the new page's claim (kept, it kept the claim
it had, though the new page may give it other mirrors or none, and ten
pieces' worth of stale claim had the auction handing every cell less than
its due, the invisible push under the old transitions). The bore and the
spent chambers yield: they give up their ground the moment the page
changes and take it back over a third of a second once it has ended, so
nothing on the move fights a hole.

**A slide's page.** The stage's rectangles first, one a cell of the cast,
then the ring's chambers, one a cell of the arc, then the whitespace: the
page cut along every rectangle's edge into a grid, the cells of the grid
nothing covers run together down a column where they follow one another
and never across a grid line, so every corner of a piece is a page corner
or a corner of the piece or rectangle beside it (a corner on another's
edge, where two pieces' mirrors meet a chamber's corner, cuts it by a few
px); the bore; the spent chambers; the empty places.

**Exact under the pieces.** Four things Portal's construction did not
meet on these pages, and what was done:

- A cell's edge can run along two pieces of whitespace, and Portal's
  contact rule (the cell's edge within the void's) found neither. An edge
  no void holds whole is held by the piece the seed faces.
- A ring's pocket encloses the bore, and Portal's pocket outline keeps only
  the largest loop, so the pocket's ground took in the bore and the cells
  were solved as if they owned it; and a ring's outline is not convex,
  and clipped by it as a convex bound a cell came out with edges that were
  nobody's. A Tell II pocket is solved on its rectangles themselves, handed
  to the solver as convex pieces, within the pocket's box; a piece of a
  cell with no area (a tie along a neighbour's edge) is no contact.
- The live auction, solving the same claims from wherever the last slide
  left it, settled a hair off the authored diagram near a piece's mirrors.
  Once a slide's change has ended the authored weights are handed to every
  body each frame, as a reel hands its own, the bore and the spent chambers
  once they have taken their ground back; a piece no mirror stands in holds
  nothing.
- A staying piece takes the new page's claim (above).

**The scroll and the blurbs.** A Tell's: the wheel aims a slide a notch, a
drag takes the story in hand, a flick carries it on, a slow story snaps to
its slide, and the story stops at its ends; a change is made at most every
quarter second, since each is a page change. The blurbs stand in the box a
box's height apart, titled with the cast's names, fading at the box's
ends. The text is set once the entry has ended and stays: the cast changes
under it. A rule along the box's left edge comes a beat after the text.

## The engine changes

- A Tell II button among the scenes. A click on any of the cast, Escape
  and the other scene buttons drop the story and go home; a click on
  another cell opens its page as before.
- The story's page is a scene to the engine (`tell2Scene`, cached by
  slide, count and size), entered as a Portal page is, with the page's
  journey rules; every cell takes the slot the plan gives it.
- The construction holds an edge along several voids, solves a Tell II
  pocket on its pieces within its box, and skips a cell's pieces of no
  area (above).
- On a Tell II page a staying void takes the new page's claim; a cell of
  the cast keeping its place is a bystander; the bore and the spent
  chambers yield while the page changes (above).
- The settled slide is handed to the auction each frame (above).
- The story's flow and its handoff run in the tick before the reel's; its
  blurbs are painted after Tell's.
- The wheel and the pointer go to this story first when one is open, then
  to a Tell, then to a reel.

## Not done

- The blurbs are bars, not words; the sequence is a placeholder, there to
  show a cast building up to one, two and three.
- A fresh slide moves the cast back and the next cell out in one change;
  it could be two, the cast back first.
- A cell crossing the page is drawn as the engine draws every crosser: a
  large cell over the whitespace that waits for it.
- The story does not pause under the pointer. The cards stay single cells.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without the Tell II button, Tell II and Tell produce exactly equal state
  and exactly equal drawing commands over Reel's four layouts, and over a
  page opened by a click, its reel pushed, dragged and flicked, home, a
  Tell story pressed, turned by a notch, held half way by a drag, and
  home again: 16,012 frames, 14,910,618 drawing commands.
- The story, on the desktop: pressed from home, its plan is the one the
  cells in id order give, every ordinary slide adds one cell to the cast
  with the cells already there at their places, and the slides build up to
  one, two and three; through the entry no cell is fractured on any frame,
  the text does not begin before the change has ended, and the rule begins
  only a beat after the text has fully appeared. Every slide, settled: the
  cast exactly on its places, rectangles to a px, unlabelled, the first the
  page's image, none overlapping; the ring's cells in their chambers in
  the plan's order, the cast and the ring together every cell; the bore and
  the spent chambers whitespace that yields, at full claim; the
  whitespace's rectangles overlapping no cell's and covering the page with
  them, and the whitespace those rectangles to 2 px; twelve cells, one site
  each, none a field, none fractured; the seam residual a hairline; the
  blurb titled with the cast's names inside the box and nowhere else, its
  lines set, the rule drawn. Every change: no cell already on the stage is
  sent on a journey or moves a px; at most one long journey, plus the
  cast's on a fresh slide; no path crosses another's on an ordinary slide;
  at most two pieces of whitespace go, plus the cast's places on a fresh
  slide; no fracture; the text never dims. A push past the end stays on
  the last slide and one past the start on the first; back at the start
  the page is slide 0's; home returns twelve cells, every root cell
  numbered, and no mark of the story on any body. A notch of 100 px, one
  of 120, a tick of 3 and a notch back each turn exactly one slide, and
  three quick notches turn fewer than three; a drag moves the story
  exactly the hand's travel and a flick carries it past slides, without a
  fracture, to snap onto one; a short move eases back and a long one on; a
  notch during the entry turns the slide and it settles exact.
- On a phone the box is the band across the top, the stage the row below
  it, and the first three changes and slides 0 and 3 pass the same checks.

## Reproduce

From the repository root:

```sh
python3 tests/tell2/build.py
node tests/tell2/validate.cjs
```

The builder writes only `tell2.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/tell2.html` on the deploy
preview to judge it. Prior marks are unchanged.
