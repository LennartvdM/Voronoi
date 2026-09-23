# Tell II: a small cluster, and the cells take the stage in turn

Baseline: Tell, `tell.html` on this branch, SHA-256
`0cd09badc2ed802684a9883c28474480a65265e0d123555eb9df93b663e03c93`.
The builder reads that file from the repository root and checks the hash.

## What it proves

A scroll-tell with the cluster as its cast. The cluster is small and sits
to one side; the blurb stands in the open, in a box of its own. Each slide
sends one, two or three cells out of the cluster to the stage, places
around the blurb (above it, below it, beside it, on its diagonals, where a
corner lies behind the text), and when the slide is done they go back into
the cluster as the next slide's cells come out: the cells take turns as the
illustration, and a slide with two or three shows a sequence. The stage and
the blurb are the same every slide; only the cast changes. Every slide is a
page like Portal's, one site a cell and the whitespace, the page less the
stage and the cluster, exact by the same construction.

## What a tell is here

**The stage.** Three columns and three rows of places around the blurb's
box, in fractions of the page: a place is a column by a row (top, below,
left, right, and the four diagonals). The rows touch and the places lie on
a few shared lines, so the whitespace between places is never a sliver. The
box reaches a little over the places beside it, so a place on a diagonal
has its corner behind the text; the text is painted over whatever is
there. The cluster stands at the right, a fifth of the width by half the
height, well off the stage. A phone stacks: the box a band across the top,
the stage a row below it (the places touching each other and the page's
sides), the cluster at the foot.

**The slides.** Eight, each the places it fills (one, two or three) and
the lines of its blurb. The cast takes turns: slide k's cells are the next
in id order, round and round, as many as its stage has places, so no cell
is on stage two slides running and the story is the same every time it is
read.

**A slide's page.** The stage's rectangles first, one a cell of the cast,
then the cluster's cards (the bento's guillotine drawn on a finer grid and
fitted into the cluster's corner of the page), then the whitespace: the
page cut along every rectangle's edges, the pieces nothing covers run
together along a row and then down the rows where their spans agree. A
slide change is a page change with Portal's smoothness: the cast travels
to its places, the last cast back into the cluster, and the cluster closes
ranks. The first of the cast is the page's image; none of the cast carries
a label, hovers, or is anything but home when clicked.

**Exact under the pieces.** Two things Portal's construction did not meet
on these pages, and what was done:

- A cell's edge can run along two pieces of whitespace, and Portal's
  contact rule (the cell's edge within the void's) found neither, so the
  edge went unheld. An edge no void holds whole is held by the piece the
  seed faces: a mirror across the edge at the seed's own line holds the
  whole edge, whichever pieces it runs along. Portal's own pages are as
  they were, every edge of theirs a void holds whole.
- The live auction, solving the same claims from wherever the last slide
  left it, settled a hair off the authored diagram near a piece's mirrors,
  which sit close behind a short edge. Once a slide's change has ended the
  authored weights are handed to every body each frame, the cluster's, the
  cast's and the whitespace's mirrors alike, as a reel hands its own, and
  the diagram is the authored one. A piece no mirror stands in (its whole
  is held by its neighbours' mirrors) keeps its own site.

And one thing the layout must keep: another cell's mirror nearer a corner
of a cell than the corner's own reach (about the cell's half-diagonal)
cuts the corner, so the cluster stands farther than that from the stage.

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
  journey rules; the cast takes the stage's slots in order when the page
  is laid.
- The construction holds an edge that lies along several voids (above).
- The settled slide is handed to the auction each frame (above).
- The story's flow and its handoff run in the tick before the reel's; its
  blurbs are painted after Tell's.
- The wheel and the pointer go to this story first when one is open, then
  to a Tell, then to a reel.

## Not done

- The blurbs are bars, not words; the story's places and casts are a
  placeholder sequence, there to show one, two and three at once.
- The story does not pause under the pointer.
- The cards stay single cells; no clusters ride a story.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without the Tell II button, Tell II and Tell produce exactly equal state
  and exactly equal drawing commands over Reel's four layouts, and over a
  page opened by a click, its reel pushed, dragged and flicked, home, a
  Tell story pressed, turned by a notch, held half way by a drag, and
  home again: 16,012 frames, 14,910,618 drawing commands.
- The story, on the desktop: pressed from home, every slide's cast is the
  next cells in turn, no cell on stage two slides running, and the slides
  show one, two and three; through the entry no cell is fractured on any
  frame, the text does not begin before the change has ended, and the
  rule begins only a beat after the text has fully appeared. Settled,
  every slide is checked: every cell of the cast stands exactly on its
  place, a rectangle to a px, unlabelled, the first the page's image, no
  two overlapping; every other cell is in the cluster; the whitespace's
  rectangles overlap no cell's and together with the cells' cover the
  page, and the whitespace is exactly those rectangles; twelve cells, one
  site each, none a field, none fractured; the seam residual a hairline;
  the blurb titled with the cast's names inside the box and nowhere else,
  its lines set, the rule drawn. A wheel notch turns the slide with no
  fracture and the text never dimming, and the last cast is back in the
  cluster; a drag moves the story exactly the hand's travel and a flick
  carries it past slides, without a fracture, to snap onto one; every
  slide on puts its cast on its places and the last back in the cluster;
  a push past the end stays on the last slide, exact, and one past the
  start on the first; a notch of 100 px, one of 120, a tick of 3 and a
  notch back each turn exactly one slide, and three quick notches turn
  fewer than three; a short move eases back to its slide and a long one on
  to the next; a notch during the entry turns the slide and it settles
  exact; home returns twelve cells, every root cell numbered, and the
  whitespace's sites unhanded.
- On a phone the box is the band across the top, the stage the row below
  it, and slides with one, two and three cells settle exact.

## Reproduce

From the repository root:

```sh
python3 tests/tell2/build.py
node tests/tell2/validate.cjs
```

The builder writes only `tell2.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/tell2.html` on the deploy
preview to judge it. Prior marks are unchanged.
