# Rehearsal: the hive plays a change first where nobody sees it

Baseline: Shoal, `shoal.html` on this branch, SHA-256
`86519224fcc304ac24442832f445ee918850b9ca787cc48bc1f4d4d93f3cac47`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Every mark so far reacts frame by frame. At the click every rule starts at
full strength, none of them knows where the change is going, and the
auction reconciles them live. The cells fight, and the hive looks as if it
does not know what it is doing. Right of way and faster heroes only moved
the pressure elsewhere.

Rehearsal tests whether a hive that plays a change ahead can choose a
better way to make it. When a change is asked for, the hive plays it first
where nobody sees it:

- a copy of the world is run ahead to the change's end;
- its defects are counted;
- the plan is revised, and rehearsed again;
- the plan that rehearsed best is played.

The engine is deterministic, so what it rehearses is what it plays. For now
it has one power: when each cell sets off.

## How a change is rehearsed

- **A copy of the world.** One deep copy of everything the simulation moves:
  - the page;
  - the reel;
  - the page's image;
  - the clocks.

  It is one copy, so a body the page's image names is the body the copied
  page holds. The copy is swapped into the page's own bindings, run, and
  swapped out, so every rule the page runs is the rule the rehearsal runs.

  The simulation of a frame became one function, `simulate(dt)`: everything
  before the picture. A rehearsal runs that and nothing else. The fields
  inside the cells are the live page's and are not stepped: nothing flows
  back up from a field within the page's change.
- **The defects.** Counted each rehearsed frame:
  - a drawing whose motion changes by more than 10 px from one frame to the
    next (a lurch);
  - a cell drawn thin that is no rectangle (a sliver);
  - a cell drawn in two pieces;
  - two travellers whose seeds come within 0.35 of their reaches added;
  - in the first quarter second, drawings moving further than their seeds
    (the shock).

  The score is lurch + 50 per sliver frame + 200 per split frame + 100 per
  near-collision + shock. Each defect is laid at the door of the cell that
  suffers it, and of the traveller nearest it as it does.
- **The plan.** The first plan is Shoal's own: everyone sets off together
  and lands together. Then, while the budget lasts:
  1. take the cell that suffered most, and the traveller nearest it;
  2. one of them sets off 0.15 s later (0.45 s at most), arriving as before
     and travelling faster;
  3. keep the move if the change rehearses better.

  A rehearsal already scoring worse than the best is stopped early. The
  budget is six rehearsals. The plan kept is written onto the page's
  journeys before anything has moved.
- **Thinking.** The page's frame gives the hive 12 ms to think. Until it has
  a plan, the hive holds still: nothing moves, the clock stands, and the
  picture stands as it was. A change asked for while it thinks starts the
  thinking afresh, since nothing of the last change moved. A rehearsal runs
  at the median of the page's last 15 frame lengths, so one slow frame does
  not set its pace.
- **What is rehearsed.** A change of scene with no story told and at most
  one page image in it, asked for from rest. That covers:
  - home's scenes;
  - home to a page, and back.

  Not rehearsed, and played as on Shoal:
  - page to page;
  - the stories;
  - the flock and changes out of it, because its cells are always on the
    wing and holding still would stop them;
  - a change asked for while another is still running.
- **The Rehearse slider** sets the budget (0–8, 6 by default). At 0 a
  change is played at once, as on Shoal.

## Measured

**The validator's tour** (below), at 1440×900 and 390×720, frames of
1/64 s. There are 25 changes; 21 are rehearsed. Each rehearsed change is
scored twice from the same start: once with Shoal's plan (the first
rehearsal) and once with the plan chosen.

| 21 rehearsed changes | desk: Shoal's plan | desk: chosen | phone: Shoal's plan | phone: chosen |
|---|---|---|---|---|
| score | 20,408 | 18,325 (−10%) | 11,031 | 9,588 (−13%) |
| lurch | 11,749 | 10,440 | 2,455 | 1,973 |
| sliver frames | 73 | 68 | 70 | 52 |
| near-collisions | 32 | 27 | 37 | 37 |
| shock | 1,803 | 1,762 | 1,360 | 1,336 |

Where the one power helps most (score, Shoal's plan → chosen):

| Change | Score |
|---|---|
| desk, hero → bento | 119 → 18 |
| desk, home → Dune | 1,497 → 781 |
| desk, home → Moss | 1,232 → 822 |
| desk, home → Aurora | 948 → 721 |
| desk, home → Coal | 308 → 207 |
| phone, → hero | 1,394 → 856 |
| phone, → frame | 870 → 537 |

Where it does not help: going home. The worst change on the desk tour
(Dune → home, 4,938, seven near-collisions) found no better start, and the
others moved by 1% or less.

The tour, measured with Shoal's own instruments against Shoal's run of the
same tour:

| Tour | desk: Shoal | desk: Rehearsal | phone: Shoal | phone: Rehearsal |
|---|---|---|---|---|
| near-collisions | 34 | 29 | 40 | 40 |
| flings | 4,330 px | 4,804 px | 315 px | 199 px |
| sliver frames | 413 | 411 | 796 | 782 |
| fractured cell-frames | 0 | 0 | 0 | 0 |

**The pause, in Chromium** (from the ask to the first frame a cell moves,
six rehearsals):

| | desk, 1440×900 | phone, 390×720 |
|---|---|---|
| hold before first motion | 0.38–1.18 s | 0.51–1.57 s |
| thinking in that hold | 0.25–0.88 s | 0.35–1.19 s |

The page's frames during the hold are about 20 ms, 54 ms at worst. With the
slider at 0 a cell moves 66–75 ms after the ask, as on Shoal. There were no
console errors. The longest holds are the pages opened on a phone (Aurora,
Coal, Moss) and going home on a desk.

**Tried.**

- **A coarse rehearsal** (frames of 1/20 s, 2.5 times cheaper) is another
  system. Its plans played worse than they rehearsed. The frame scene
  rehearsed at 120 and played at 329; Moss rehearsed at 4 and played at
  468.
- **Rehearsing the fields** doubled the cost and was not needed: the page is
  exact without them.
- **The budget.** This was measured on a first tour of 20 changes, whose
  states part from change to change.
  - Desk: three rehearsals gained 6% of the tour's score, four 9%, six 14%
    and eight 15%.
  - Phone: the totals were noisy (−5%, +7%, −8% and −2%).

## Known

- **The pause reads as a pause.** A hold of half a second to a second and a
  half before anything moves is longer than any mark's start so far. The
  next step is for the hive to think before it is asked. At rest it is idle:
  it could rehearse the change under the pointer (the page a hovered cell
  opens, the scene a hovered button asks for). A plan would then usually be
  ready at the click.
- **One power is little.** Setting off later helps where two cells meet;
  it does nothing for a lurch that every plan shares. The returns home keep
  their scores, and those are the largest.
- **Flings rise on some desk openings.** A cell that sets off later travels
  faster, and the score does not count flings: Moss 472 → 716 px, Petal
  592 → 783 px.
- **In the browser a rehearsal is a close prediction, not the bit.** The
  page's frames are not all the same length. The rehearsal runs at their
  median; the performance runs at whatever each frame takes.
- **Not rehearsed: the fields inside the cells, and painting.** Painting
  moves the label anchor a freely drifting cell steers to. On the tour
  neither changed the page by a bit. In a scene where the page's cells
  drift (the flock, not rehearsed) it would.
- **During the hold the pointer changes nothing.** Hover and labels stand
  still. A click asks afresh.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed. The tours
use frames of 1/64 s, a length a float holds exactly, so every frame is as
long as the rehearsal's.

The tour, at 1440×900 and 390×720:
- home's scenes (frame, sidebar, hero, flock, bento, hero, bento);
- home to Moss, Aurora, Coal, Petal, Drift, Ember, Dune and Jazz and back;
- Coal → Aurora and Ember → Tide.

- **A rehearsal leaves no trace.** With a budget of one, the plan rehearsed
  is Shoal's own. Every frame of the tour is Shoal's: the world, every
  drawing command, 11,550 frames on a desk and on a phone.
- **What it rehearses is what it plays.** On all 21 rehearsed changes, desk
  and phone, the performance steps the page through the chosen rehearsal
  frame by frame, to the bit. That covers every cell's seed, speed, claim,
  crystal, progress and sites. The rehearsal ran to the end of the page's
  change, and the performance scored what the rehearsal scored.
- **Never worse than Shoal's plan.** The plan chosen rehearses no worse than
  Shoal's own from the same start.
- **Not rehearsed where it should not be.** Page to page and the flock are
  not rehearsed, and run on Shoal's one clock.
- **Still correct.**
  - Nothing fractures on any frame.
  - Every page at rest is exact as on Shoal: the image on its rectangle and
    covering it, the text covering its own with the title in it, the
    whitespace exact, no field, one site to a cell.
- **Thinking spread over frames** (40 rehearsed frames to a frame of the
  page):
  - the page holds still and the clock stands, for 14 and 19 frames;
  - then it plays what thinking at once plays, frame by frame;
  - a change asked for while the hive thinks is thought afresh, with
    nothing having moved.
- **A story is not rehearsed.**
  - A Cue story is Shoal's frame by frame (2,040 frames, the world and every
    drawing command).
  - Cue's own story checks pass on a desk and a phone.
  - A Tell and a Tell II story run to their end and home without a fractured
    cell.

## Run

```bash
python3 tests/rehearsal/build.py
node tests/rehearsal/validate.cjs
```
