# Tell: a story scrolls, the cluster stays and its heroes swell

Baseline: Reel, `reel.html` on this branch, SHA-256
`62ca63c8af9b3a424b628ee08fd9178275714a58db14a8736f3571b233f1fcf3`.
The builder reads that file from the repository root and checks the hash.

## What it proves

The inverse of a page. On a Portal page a cell is clicked and the page is
laid around it; on a Tell the cells stay. The cluster is laid once beside
a reading column and does not move again, and a story of short blurbs
scrolls through the column like a slide show. Each slide names a place in
the cluster, and the card nearest it is the slide's hero: it swells where
it stands, its neighbours giving way, and shrinks back as the next hero
swells, linked to the scroll, so the cluster turns like a carousel under
the text while the illustration stays one thing throughout. The column is
exact under every swell by Portal's construction, authored again for the
swell and handed to the auction.

## What a tell is

**The page.** The column is a full-height void a quarter of the width
with its corners on the page's edges, so the whitespace is exact by
Portal's construction; its rules run along the side facing the cells. The
cluster is the bento's own guillotine of the rest, so it looks like the
home page's cells, not a grid. A phone stacks: the column a band across
the top, the cluster below. The entry is a page change like Portal's, and
it is the only change the story makes.

**The slides.** Eight, each a place in the cluster (a fraction across
and down it) and the lines of its blurb. The heroes are chosen when the
story begins, from the cluster as laid: for each slide the card whose
rectangle's centre is nearest the slide's place, not one of the last two
slides' heroes, so the emphasis moves round the cluster. The story is the
same every time it is read.

**The swell.** Slide k's hero holds a share that peaks on its slide and is
gone a slide away (a tent over the scroll), so as the story moves from one
slide to the next one hero shrinks as the next grows, and the story reads
backwards the same way. A hero grows from its card's area to a fifth of
the cluster, whatever its card, so every hero is the same size; the other
cards are scaled to what is left. Whenever a share changes the page is
authored again: Portal's construction solves the cluster's weights for
those areas with the column cut out, mirrors every contact across the
column's edge, and the solved weights are handed to every body at once,
so the diagram is the authored one on the frame it changes, the hero
grows where it stands, and the column stays exact. The first swell arrives
over a third of a second once the entry has ended. The hero is the page's
image: it carries no label, its name titles the blurb, it does not hover,
and a click on it goes home.

**The scroll.** The story is a scroll in pixels, a page's height a slide,
with a speed that eases away with a time constant of 0.35 s, half a
reel's, so a slide arrives in about a second. The wheel aims: a notch,
whatever its size (a mouse's 100 px or a trackpad's few), sends the story
one slide on, or back, at the speed whose easing carries it there, so a
slide show turns a slide a notch; notches spun quickly aim on again once
the story has crossed half a slide, so three in a third of a second turn
two, and a long trackpad swipe passes slides one by one. A pointer pressed
takes the story in hand, its travel the pointer's exactly, and a release
flicks it on at the hand's speed. The story stops at its first and last
slide. Once the story is slower than 60 px/s it eases onto the nearest
slide in about a quarter second, and what speed it had left dies away as
fast, so it does not creep. The slide the story is on is the nearest.

**The blurbs.** In the column, each blurb stands at its place on the
scroll: the slide's and its neighbours' as they pass, a column's height
apart, so at rest the neighbours stand outside the column and a scroll
slides one out as the next comes in, fading over the column's ends. A
blurb is its hero's name over its lines, the lines Plaque's paragraph
bars. The text is set once the entry has ended and the column is seated,
fading in over 0.3 s, and stays for the whole story, since no slide moves
the cluster; the rules along the column's side come a beat after the text
has fully appeared, 0.25 s, fading in over 0.45 s.

## The engine changes

- A Tell button among the scenes: the story begins from wherever the
  cells are. A click on the hero, Escape and the other scene buttons drop
  the story and go home; a click on another cell opens its page as before.
- The story's page is a scene to the engine (`tellScene`, cached by count
  and size), entered as a Portal page is (`portalEnter`), with the page's
  journey rules.
- The construction takes a swell: a card's target area is its rectangle's
  times its swell (1 for every card of every other page).
- A story's cards bid throughout: never a wall, so a hero can grow into
  its neighbours and they can give the ground back. After the entry the
  cards are pinned as a reel's are (bidding, seeded at their centres,
  unclamped), and the column's mirrors follow each handoff at once.
- The story's flow and its handoff run in the tick before the reel's; its
  blurbs are painted after Portal's prose.
- The wheel and the pointer go to the story first when one is open, then
  to a reel; on a story the wheel aims a slide rather than pushing.

## Not done

- The blurbs are bars, not words; a real story would set them.
- The story does not pause under the pointer.
- An add, a remove or a resize lays the cluster again; the heroes keep
  their cells wherever they land.
- The cards stay single cells; no clusters ride a story.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without the Tell button, Tell and Reel produce exactly equal state and
  exactly equal drawing commands over Reel's four layouts, and over a page
  opened by a click, its reel pushed by the wheel, dragged and flicked,
  and home again: 14,836 frames, 14,103,659 drawing commands.
- The story, on the desktop: pressed from home it opens slide 0 with every
  slide's hero chosen as the card nearest its place not among the last
  two; through the entry no cell is fractured on any frame, no hero swells
  and the text does not begin before the change has ended, and the rules
  begin only a beat after the text has fully appeared. Settled, every
  slide is checked: the cluster is where it was laid (every card's
  rectangle the same, the page not laid again, nothing travelling); the
  hero is the slide's, the page's image, holding a fifth of the cluster to
  within a percent, no other card swollen; the column exactly its
  rectangle; twelve cells, one site each, none a wall, none a field, none
  fractured; the seam residual a hairline; the blurb titled with the
  hero's name inside the column and nowhere else, its lines set, the rules
  drawn; the hero without its label. A wheel notch turns the slide within
  a second while the cluster stays, the two heroes' shares summing to one
  between the slides and the text never dimming; a drag held half way
  leaves both heroes half swollen and the column exact, and a flick
  carries the story on past slides, without a fracture, to snap onto one;
  every slide on swells its hero in place; a push past the end stays on
  the last slide, exact, and one past the start on the first; a notch of
  100 px, one of 120, a tick of 3 and a notch back each turn exactly one
  slide, and three quick notches turn fewer than three; a short move eases
  back to its slide and a long one on to the next; a notch during the
  entry turns the slide and the cluster still settles as laid, exact;
  home returns twelve cells, every root cell numbered, nothing swollen or
  pinned.
- On a phone the column is the band across the top, the cluster below it,
  the heroes chosen the same way, and the story turns the same way.

## Reproduce

From the repository root:

```sh
python3 tests/tell/build.py
node tests/tell/validate.cjs
```

The builder writes only `tell.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/tell.html` on the deploy
preview to judge it. Prior marks are unchanged.
