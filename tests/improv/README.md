# Improv: the hive thinks while it plays

Baseline: Rehearsal, `rehearsal.html` on this branch, SHA-256
`dc4681c996676b9df3e825d0549a393398925d862be3636f248231b4540356ad`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Rehearsal thought before it moved. At the click it held the page still,
rehearsed the change headless, and played the plan that rehearsed best. That
had three problems:

- **The pause was a defect of its own:** 0.4 to 1.6 s, and 1.2 to 2.6 s
  between pages.
- **A page is never still.** Its gallery flows on its own, so the hold stopped
  a moving thing.
- **No plan made before the click can know the page it will meet.**

The obvious fixes turn into choices: how long to think, how far ahead, how
finely. None of those should be a setting or a matter of taste. Improv tests
whether the hive can decide them itself, from what it measures.

## How it thinks

- **Nothing waits.** A change starts at once, as Shoal plays it. The hive
  thinks in rounds, in the time each frame leaves, while the change plays.
- **A round copies the page as it is**, gallery flow and all, and rehearses
  the rest of the change: first the plan as it stands, then a move for the
  cell that suffered most and one for the traveller nearest it as it did.
- **A move** slows a cell's clock for 0.3 s (to a crawl) and then runs it
  fast enough to land when it would have.
- **A move acts from the moment the round expected its answer.** So what was
  rehearsed is what is played. An answer that comes later than that is
  dropped.
- **Every round rehearses to the change's end.** Everyone of a change lands
  together, and a cell that crawls must hurry after, so a move's consequences
  run to the landing. Rounds that looked less far made moves whose hurrying
  they had not seen, and on a phone played worse than Shoal.
- **How finely follows from one deadline.** An answer is worth having until
  the cells it would move have gone a twentieth of their way, which
  easeInOutCubic reaches a quarter of the way through a journey. If the
  round's rehearsals reach the end by then at the page's own frame, it
  rehearses at that frame. If not, it rehearses coarse, at 1/16 s frames.
- **How much it thinks is measured, not set.**
  - The hive learns the display's period from the frames it does not think
    in.
  - Each frame, it watches whether the frame came late. A late frame halves
    the next frame's thinking; one on time adds 0.1 ms, never past what the
    frame's own work leaves.
  - It thinks as much as never costs a frame. That includes the browser's
    own work after the script, which the script's clock cannot see: a large
    canvas's raster was what a budget read off that clock overran.

What is thought about:
- a change of the page's scene, and a page opened from a page, with no story
  told;
- not the flock, whose cells go nowhere;
- not the stories.

A change need not start from rest, since nothing is held. The Rehearse
slider is gone.

## How the rule was found

Before the rule, the choices were measured. The fixed look-ahead,
fineness and thinking budget were run over the 56 changes between the eight
kinds of page (every page opened from every other kind), at 1440×900,
counting defects on what is drawn: lurch, slivers, splits, near-collisions,
start shock. Shoal draws 165,165 of them; Rehearsal, with its pause, 127,126.

| Budget (rehearsed frames a frame) | Best fixed look-ahead and frame | Defects |
|---|---|---|
| 2 | none arrives in time | 165,165 |
| 4 | 0.6 s ahead, 1/16 s frames | 146,523 |
| 8 | 1.2 s ahead, the page's frame | 136,365 |
| 16 | to the end, the page's frame | 121,097 |

With little thinking, coarse and short won. With more, fine and far won.
The same fixed choice was worse at another budget: 0.6 s at the page's
frame drew 171,712 at a budget of 4, more than Shoal.

A deadline-derived look-ahead (as far as the answer could reach by the
deadline) matched or beat the grid's best at 8 and 16, but played the phone
tour worse than Shoal. Rehearsing every round to the end fixed that, and is
what the rule keeps.

## Measured

The validator's figures, at a budget of 8 rehearsed frames a frame: Chromium
measured about 9 of the page's own simulated frames spare in each frame on
this machine. Frames are 1/64 s.

| Defects drawn | Shoal | Improv |
|---|---|---|
| Tour of 25 changes, 1440×900 | 25,352 | 22,641 (−10.7%) |
| Tour of 25 changes, 390×720 | 18,528 | 17,911 (−3.3%) |
| 56 page-to-page changes, 1440×900 | 165,165 | 139,033 (−15.8%) |
| 56 page-to-page changes, 390×720 | 62,631 | 46,616 (−25.6%) |

Over the page-to-page changes, the hive made 104 moves on a desk and 89 on a
phone, none of them late. There is no pause: a change moves on the frame
after it is asked for, as on Shoal.

**In Chromium**, headless on this machine, with the budget measured and 12
changes at each size:

| | Frames drawn, Shoal | Frames drawn, Improv | Moves |
|---|---|---|---|
| 390×720 | 1,876 | 1,853 (−1.2%) | 4 |
| 1440×900 | 1,637 | 1,563 (−4.5%) | 1 |

- **First motion** came 7–89 ms after the ask, against 6–70 ms on Shoal.
- **Errors:** none.
- **At 1440×900 the page drops frames even on Shoal** (108 to 131 frames in
  2.6 s on half the changes), so the hive finds little to spare and
  hardly thinks.

## Known

- **Thinking shares the page's thread.** It costs a few frames where the
  page is already short of time: 1 to 5% in headless Chromium. At desk size
  there, the hive barely thinks at all. A Web Worker would give the hive a
  core of its own, and a budget of 16 or more on a desktop. That was worth
  27% on the page-to-page changes in the grid, at no cost to the frame.
  Only two things stand in the way: two small functions in the reel's strip
  definitions, and the Hive prototype, which a structured clone drops.
- **A coarse round is a prediction.** Only rounds at the page's own frame
  are laid on the performance frame by frame. On the tours at a budget of 8
  most rounds are coarse, which is why the frames checked there are few.
- **One power, and only one way.** A move can slow a cell and let it catch
  up; it cannot hurry one. The size power (the cell that shrinks most
  sheds its size early) helped in 45 of the 56 changes in a prototype, but
  cost rehearsals, and is not in.
- **The returns home keep their scores.** Their lurch is one every plan
  shares.
- **Not thought about:** the stories, the flock, and the fields inside cells
  (which are not rehearsed).

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and a counted budget of 8 rehearsed frames a frame, so that what it
counts does not depend on the machine's speed.

It runs two sets of changes, each on a desk (1440×900) and a phone
(390×720):
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **Thinking leaves no trace of its own.** With no budget, every frame of
  the tour is Shoal's: the world and every drawing command, 11,550 frames on
  a desk and on a phone.
- **Nothing waits.** From the ask, the page's clock runs every frame.
- **What it rehearses is what it plays.** From each round that moved a cell
  at the page's own frame, the performance is that round's rehearsal of the
  move, frame by frame, until the next move acts. That covers every cell's
  seed, speed, claim, crystal, progress and sites, to the bit.
- **Every move acts when its answer was expected**, never before its round
  began.
- **Fewer defects than Shoal**, on the tour and on the page-to-page changes,
  at both sizes.
- **Still correct.**
  - Nothing fractures on any frame.
  - Every page at rest is exact as on Shoal: the image on its rectangle and
    covering it, the text covering its own with the title in it, the
    whitespace exact, no field, one site to a cell.
- **A story is not thought about.**
  - A Cue story is Shoal's frame by frame (2,040 frames, the world and every
    drawing command).
  - Cue's own story checks pass on a desk and a phone.
  - A Tell and a Tell II story run to their end and home without a fractured
    cell.

## Run

```bash
python3 tests/improv/build.py
node tests/improv/validate.cjs
```
