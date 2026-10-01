# Apace: the cells keep up

Baseline: Cohort, `cohort.html` on this branch, SHA-256
`708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d`.
The builder reads that file from the repository root and checks the hash.

A mark of the Membrane class, measured against Cohort, on a desk
(1440×900). It answers the screen: the cells either turned crisp before they
arrived or clicked onto the screen's edge at the end. Slate, built from Cohort
beside it, answers the image's sphere.

## What it proves

A seed followed its plan on a spring damped against the page. A spring like
that trails a moving target by its damping over its stiffness times the
target's speed: about a fifth of a second of travel, so a cell crossing the
page ran well behind its plan.

The sea, though, goes on the change's clock. It closed while the cells were
still on their way, so:

- **they turned crisp before they arrived**: over the tour and the chain, the
  cells still had 12.7 px to go on average when the hive turned crisp, and
  up to 488;
- **and then clicked into place**: they slid the rest of the way as crisp
  cells, onto their places and the screen's edges, after the sea that should
  have carried them was gone. A sixth of the screen's edge that the cells
  reach in a change, they reached in its last tenth.

Apace tests the simplest cure: a seed that keeps up with its plan.

## How it works

- **The spring damps against the plan's own motion.** On the page's own
  changes (where the sea is), a seed is pulled toward its plan as on Cohort,
  and damped against how fast its plan moves, not against standing still. So
  a seed keeps up with its plan, and arrives when its clock says.
  - The plan's speed is how far it moved since the frame before, on the same
    path; on a new path it starts from rest.
  - The spring's stiffness, its damping and its wobble are Cohort's. It still
    lags and overshoots when its plan turns, which is what reads as alive; it
    no longer trails.
- **Scope.** The page's own changes. The stories, which choreograph their own
  motion, and the fields inside cells are Cohort's.

The header carries no captions.

## Measured

The validator's figures, on a desk (1440×900). Frames are 1/64 s, and the
worker of Wings thinks 16 rehearsed frames a frame on both marks alike. The
page-to-page changes are a chain through all 56 ordered pairs of the eight
kinds of page; the tour is home's scenes, home to a page of every kind and
back, and two changes from page to page.

**How the cells come in**, with the rule alone (no thinking), over the tour
and the chain (82 changes):

| | Cohort | Apace |
|---|---|---|
| To go when the hive turns crisp, mean | 12.7 px | 7.2 px (−43%) |
| The most any cell still had to go | 488 px | 313 px |
| A seed behind its plan's end when its clock runs out, mean | 4.0 px | 3.0 px |
| The most | 40 px | 26 px |
| The screen's edge reached in a change's last tenth | 13,560 px of 77,892 (17.4%) | 11,184 px of 78,140 (14.3%) |

**Defects drawn** (lurch, slivers at 50 a frame, splits at 200, near-
collisions at 100, start shock):

| | Cohort | Apace |
|---|---|---|
| The tour | 26,377 | 17,407 (−34%) |
| Lurch | 11,929 | 6,305 |
| Sliver frames | 165 | 96 |
| Split frames | 4.6 | 2.8 |
| Near-collisions | 31 | 36 |
| Start shock | 2,160 | 2,158 |
| The chain of 56 page-to-page changes | 106,515 | 108,903 (+2%) |
| Lurch | 35,580 | 36,795 |
| Sliver frames | 830 | 812 |
| Split frames | 27.9 | 35.6 |
| Near-collisions | 117 | 128 |
| Start shock | 12,125 | 11,589 |

On the chain Apace draws fewer defects on 32 of the 56 changes. On the tour
most of the gain is in changes the hive used to finish late: home to Drift
draws 106 against 3,001, and Ember to Tide 1,798 against 5,661. Home to
Aurora draws more (1,023 against 671), and so does home to Petal (437
against 236).

**The chain's count depends on where it starts, Cohort's far more than
Apace's.** Started 0, 10 and 20 frames later than the validator's, with the
hive thinking 16 frames a frame on the page (a prototype harness, not the
validator's worker), Cohort's chain drew 129,743, 108,873 and 110,721, and
Apace's 102,827, 102,744 and 103,680. A seed that trails its plan carries
the change before into the next; one that keeps up does not.

**The screen leaned on** (the travelling cells' outlines lying along the
screen's edges, summed over every frame while a change runs) is Cohort's
within half a percent: 17.66M px-frames against 17.74M on the chain, 5.35M
against 5.40M on the tour.

Thinking: on the chain 108 moves, none late, and 8,414 frames laid bit for
bit on the worker's rehearsal of its move; on the tour 22 moves, none late,
1,170 frames; with no worker, on the page, 33 moves.

**In Chromium**, headless, from home to Drift, then page to page through
Ember, Tide, Moss, Petal, Aurora, Dune, Jazz and Drift, and home; two runs
of each:

| | Cohort | Apace |
|---|---|---|
| Frames drawn in 32 s | 1,608 · 1,544 | 1,545 · 1,560 |
| Longest frame | 248 ms · 266 ms | 218 ms · 191 ms |
| First motion after the ask | 9–75 ms | 8–74 ms |
| Errors | none | none |

## Known

- **The screen: what was tried and is not in.** The owner asked that the
  cells splash against the screen's edges and use the room past them,
  neither sharpening before they arrive nor clicking on. Apace's rule is
  the part that measured well. Measured in prototypes, with the hive
  thinking 16 frames a frame on the page, on the chain (defects) and on a
  tour of 17 changes (the screen):
  - *No cell kept clear of the screen*, Membrane's rule taken out, its seed
    kept on the screen so it cannot leave the view: the screen's edge
    reached in a change's last tenth 2,648 px against 2,744 with Apace's
    rule alone, the edge its cells keep left bare 0.904M px-frames against
    0.906M, and the chain drew 110,309 against 102,827. The clearance
    rarely binds, and taking it out freed nothing measurable.
  - *The hive mirrored in the screen's edges* (each bell with its images in
    the ground's edges, so an edge is never the sea's shore): cells already
    at an edge stayed at it (the edge they keep left bare 0.55M px-frames
    against 0.91M), but where an edge or a corner made the presence flat
    the auction's gauge lost its footing frame to frame, and the chain drew
    249,718 mirrored at the ground's edge and 304,740 at the screen's.
  - *The edge doubling a cell's presence*, falling off as its own bell: the
    cells reached the edge later (4,356 px in the last tenth).
  - *The sea going out as the cells arrive*, not on the clock: the
    whitespace's holes still form on the clock, the two clocks disagreed,
    and the cells clicked onto the screen more (the largest one-frame closes,
    summed, 11,248 px against 3,064 on Cohort).
  - *A wider rim while the page is liquid*, its ground the sea's: more of
    the screen's edge was sea (6.34M px-frames against 5.70M on Cohort).
- **The images still travel as discs.** That is Slate's question.
- **No phone.** The class is iterated on a desk.
- **The landing page is unchanged.** Apace has no card yet.


## Run

```bash
python3 tests/apace/build.py
node tests/apace/validate.cjs
```
