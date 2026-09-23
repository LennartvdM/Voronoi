# Tell: a story scrolls, the cells volunteer

Baseline: Reel, `reel.html` on this branch, SHA-256
`62ca63c8af9b3a424b628ee08fd9178275714a58db14a8736f3571b233f1fcf3`.
The builder reads that file from the repository root and checks the hash.

## What it proves

The inverse of a page. On a Portal page a cell is clicked and the page is
laid around it; on a Tell the cells stay on the page and a story of short
blurbs scrolls through a reading column like a slide show. Each blurb is a
slide with a place for an image beside the column, and the cluster
volunteers the cell nearest that place to be the slide's image, the rest
tiling the remainder as cards. A slide is a page like Portal's, one site a
cell and the column exact by the same construction, and a slide change is a
page change with Portal's smoothness: the cells travel, the column stays.
The wheel, a drag or a flick moves the story, and the slides snap.

## What a tell is

**The slides.** Eight slides, each with its column (left, centre or right
of the page, a quarter of the width), the side of the column its image is
on, the band of the height the image spans, and the lines of its blurb.
The slides are the story's fixed layout, as the page kinds are Portal's.

**A slide's page.** The column is a full-height void with its corners on
the page's edges, so the whitespace is exact by Portal's construction, with
the text flag and its rules along the sides facing the cells. The image is
a rectangle beside the column on the slide's side, over the slide's band of
the height, and the cards fill what is left: the far side of the column
whole, and the pieces above and below the image, each region tiled by
Portal's squarest cards for the count it gets by area. A phone stacks: the
blurb a band across the top, the image below it on its side, the cards
beside and below.

**The volunteer.** The slide's image is the cell nearest its place on the
page at the moment the slide comes up, among the cells that were not one of
the last two images, so the image moves round the cluster rather than one
cell keeping it. A slide seen before keeps its image if it can. The image
takes the first slot, as on a Portal page, carries no label, and its name
titles the blurb.

**The scroll.** The story is a scroll in pixels, a page's height a slide,
with a speed that eases away with a time constant of 0.35 s, half a
reel's, so a slide arrives in about a second. The wheel aims: a notch, whatever its size (a mouse's 100 px or a
trackpad's few), sends the story one slide on, or back, at the speed whose
easing carries it there, so a slide show turns a slide a notch; notches
spun quickly aim on again once the story has crossed half a slide, so
three in a third of a second turn two, and a long trackpad swipe passes
slides one by one. A pointer pressed takes the story in hand, its travel
the pointer's exactly, and a release flicks it on at the hand's speed. The
story stops at its first and last slide. Once the story is slower than 60
px/s it eases onto the nearest slide in about a quarter second, and what
speed it had left dies away as fast, so it does not creep on. The slide
the story is on is the nearest, and a change is made at most every quarter
second, so a flick passes slides without opening each.

**The blurbs.** In the column, each blurb stands at its place on the
scroll: the slide's and its neighbours' as they pass, a column's height
apart, so at rest the neighbours stand outside the column and a scroll
slides one out as the next comes in, fading over the column's ends. A blurb is its image's name over
its lines, the lines Plaque's paragraph bars. The text is set only once the
change has ended, fading in over 0.3 s; the rules along the column's sides
come a beat after the text has fully appeared, 0.25 s, fading in over
0.45 s.

## The engine changes

- A Tell button among the scenes: the story begins from wherever the
  cells are. A click on the image, Escape and the other scene buttons drop
  the story and go home; a click on a card opens its page as before.
- A slide is a scene to the engine (`tellScene`, cached by slide, count and
  size), entered as a Portal page is (`portalEnter`), with the image pinned
  to the first slot and the page's journey rules.
- The story's flow runs in the tick before the reel's; its blurbs are
  painted after Portal's prose.
- The wheel and the pointer go to the story first when one is open, then
  to a reel; on a story the wheel aims a slide rather than pushing.

## Not done

- The blurbs are bars, not words; a real story would set them.
- The story does not pause under the pointer, and a resize does not re-lay
  the slide until the next change.
- The cards stay single cells; no clusters ride a slide.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without the Tell button, Tell and Reel produce exactly equal state and
  exactly equal drawing commands over Reel's four layouts, and over a page
  opened by a click, its reel pushed by the wheel, dragged and flicked,
  and home again: 14,836 frames, 14,103,659 drawing commands.
- The story, on the desktop: pressed from home it opens slide 0 with the
  cell nearest the image's place as its image; through the change no cell
  is fractured on any frame, the text begins only once the change has
  ended, and the rules only a beat after the text has fully appeared.
  Settled, every slide is checked: the image is the slide's, pinned to its
  place; the column is exactly its rectangle; twelve cells, one site each,
  none a wall, none a field, none fractured; the seam residual a hairline;
  the blurb titled with the image's name inside the column and nowhere
  else, its lines set, the rules drawn; the image without its label. A
  wheel notch turns the slide within a second, to a fresh volunteer, the
  nearest cell not among the last two images; a notch of 100 px, one of
  120, a tick of 3 and a notch back each turn exactly one slide, and
  three quick notches turn fewer than three; a drag moves the story
  exactly the hand's travel and a flick carries it on past slides, without
  a fracture, to snap onto one; every slide on to the last takes a fresh
  volunteer; a push past the end stays on the last slide, exact; back at
  the start the first slide keeps its image; a push past the start stays
  on it; home returns twelve cells, every root cell numbered. A short move
  eases back to its slide and a long one on to the next. A push made
  mid-change turns the slide without a fracture and ends exact.
- On a phone the column is the band across the top, the image below it on
  the slide's side, and the story turns the same way.

## Reproduce

From the repository root:

```sh
python3 tests/tell/build.py
node tests/tell/validate.cjs
```

The builder writes only `tell.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/tell.html` on the deploy
preview to judge it. Prior marks are unchanged.
