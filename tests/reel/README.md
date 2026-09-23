# Reel: a page's gallery is an endless strip

Baseline: Portal, `portal.html` on this branch, SHA-256
`63bc171f373b706256b916dcb20fec25ba060eeeda5de1a3bc07492040eda550`.
The builder reads that file from the repository root and checks the hash.

## What it proves

That a page's cards can be browsed without leaving the tiling. On a Portal
page the gallery is the cells that are not the image, laid in the region
the page kind gives them, and there are as many as the page has. Reel makes
that region a window on a strip that has no end and runs on its own, an
upward waterfall: cards rise at a walking pace, slide in at one edge and
out at the other, and come round again; the wheel pushes the flow along or
holds it back, a drag takes the strip in hand and a flick sends it on. The
whitespace, the image and the text stay exactly what the page authored.
The strip needs only a band's worth of cards more than the region shows.

## What a reel is

**A strip of slots.** The gallery region is a strip along its long axis.
Its visible bands are the page's own layout, the squarest cards the count
allows; beyond them the bands follow a pattern, one as wide as the page's,
one a card narrower and a quarter taller, one a little shorter, one a card
wider. A card's slot is its band's stretch of the strip and its share
across it. A slot index runs on without end in both directions.

**A card is its slot clipped by the region.** Every card is still one root
cell with one site, a rectangle as its destination and its claim. Under a
scroll its rectangle is the part of its slot inside the region, so the
region is tiled at every position: the band nearest each end reaches the
end, whatever is parked. At an end that is the page's edge a card
**overflows**: its rectangle is still cut at the page, but its seed is its
whole slot's centre, off the page if need be, so it slides in and out as
itself, its seams with its neighbours unchanged, instead of squeezing in
as a sliver. At an end that is a divider (whitespace or the image) it is
clipped, seed and all; nothing overflows into the whitespace.

**The page is authored again at every scroll step.** The page's rest
diagram (Portal's construction: the cells' weights solved per pocket with
the whitespace cut out, every contact mirrored across the whitespace's
edge) is rebuilt for the clipped rectangles, and handed to every body at
once, weights included: each site enters the auction at the solved weight,
so the diagram is the authored one on the frame it changes and the auction
has nothing to chase. The whitespace's sites are the authored mirrors,
exactly, with no site padded at its centre from a formation that had more.
Nothing is a wall on a reel: a pinned body whose cell is its rectangle would
leave the auction, and the authored diagram has every cell bid, the image
included.

**Made-up cards.** A page's own cards cannot fill a window that lies across
more bands than the page shows, so the reel makes up as many more as the
widest such window needs, at least a band's worth and one. They are root
cells like the others (Neon, Sage, Ruby, Sky, Amber, Dusk and so on, with
the same colours and numbers) and they retire on the next change, so the
page keeps its count. A made-up card clicked becomes the next image, and
an original retires in its place.

**The window.** The strip's cards hold M consecutive slots. Each step the
region's needed slots are found, from the first band whose end is past
the region's start to the last whose start is before its end, and the
window shifts only when it must: the card past one end takes the slot
beyond the other. No slot under the region is ever empty, and a card is
never handed back and forth at an edge.

**The flow.** The strip has a speed, and the page is authored again
wherever that speed has carried it each frame; nothing is stepped. Left
alone the speed is the flow's own pace, 28 px a second along the strip,
cards rising. The wheel is a push: each pixel of wheel adds 4 px/s along
the flow, or against it, and the speed eases back to the flow's pace with
a time constant of 0.7 s, so one notch carries the strip about 300 px and
settles within a couple of seconds. A pointer pressed on the gallery takes
the strip in hand: its travel along the strip is the pointer's, exactly,
and the flow waits. Let go moving, the strip goes on at the hand's speed
(smoothed over the last 50 ms) and eases back to the flow; let go after
holding still, it starts again from rest. A speed is capped at 2400 px/s.

**Parking.** A card with less than twice the claim floor under the region
is parked, its band with it: the auction would draw it larger than
authored. A parked card leaves the page: it is a wall at a rectangle off
the page's top left, which cuts nothing from the ground, bids nothing and
draws nothing. The page keeps its count and its tiling owes it no sliver.

## The engine changes

- `reelStep()` runs in the tick before the page steps: recycling, parking,
  clipping, the authored diagram, the handoff.
- The whitespace's seam sites follow a reel at once (no slew), are exactly
  the authored mirrors, and take the solved weights.
- A reel's body is pinned (its seed holds its rectangle's centre) but never
  a wall while it shows; parked, it is a wall off the page. A reel's seed is
  not clamped to the page's seed margin, so it can stand off the page.
- The authored diagram takes a card's seed where the reel puts it.
- A made-up card's going is no change: the reaper does not re-lay the page
  for it.
- The flow carries the strips in the tick before the reel step lays them.
- The wheel pushes the open page's gallery along its flow (line and page
  deltas normalised); a pointer drag on the gallery takes it in hand, with
  pointer capture, and a release flicks it. A click on the image, Escape
  and the scene buttons drop the reel first. The hint line says so.

## Not done

- The flow does not pause under the pointer; a card is clicked on the move.
- A resize or an add/remove drops the reel and re-lays the page.
- The cards stay single cells; no clusters or fields ride in the strip.

## Verification

`validate.cjs` runs the real inline tick with native Canvas and DOM stubbed.

- Without a click, Reel and Portal produce exactly equal state and exactly
  equal drawing commands over the same four layouts as Portal's validator:
  14,226 frames, 12,887,553 drawing commands.
- With a click and no scroll, every card of the page stands exactly in
  Portal's rectangle for it, the made-up cards are walls off the page, and
  nothing that shows is a wall.
- Portal's whole click suite: every kind opens from its cell with no
  fractured cell on any frame, the whitespace exact, one site per cell, the
  text set in the reading void; mirroring, crossers, home, Escape, hover,
  the interrupted change, add/remove, the phone.
- The reel, for five kinds with the flow held: with the specks parked the
  page is exact and every cell one site; a scroll of 720 px at 8 px a
  frame moves the cards,
  brings new ones in, re-lays nothing and fractures nothing, no cell is
  ever more than 1 px into the whitespace while moving, a card's seed
  stands off the page only at a page-edge end and never past a divider,
  every parked card is a wall off the page, and at a page edge some card
  overflows; settled,
  the whitespace is exact again; 3000 px on, cards have come round the
  strip; the same way back, every first card is back in its slot and the
  whitespace exact; home returns twelve root cells and no reel. A made-up
  card clicked becomes the image and the page keeps its twelve.
- The flow, for two kinds: left alone the strip moves 28 px in a second;
  a wheel notch speeds it by over 300 px/s, carries it over 260 px and
  eases back to within 1 px/s in five seconds; a wheel back turns it; a
  drag moves the strip exactly the hand's 150 px; a flick sends it on at
  over 600 px/s and 300 px, then eases back within five seconds; a hand
  held still releases it at rest and the flow resumes within three; the
  whitespace holds to 1.5 px through every push, drag and flick, and is
  exact again in the flow. On a phone the strip runs sideways under the
  text and the flow holds the whitespace to 1.5 px over five seconds (it
  measures 0.9 px, at the page's corner). Portal's page checks run with
  the flow held, as the page is judged as it opens.

## Reproduce

From the repository root:

```sh
python3 tests/reel/build.py
node tests/reel/validate.cjs
```

The builder writes only `reel.html`. Per `EXPERIMENT_WORKFLOW.md` the
gallery entry is left for a promotion PR; open `/reel.html` on the deploy
preview to judge it. Prior marks are unchanged.
