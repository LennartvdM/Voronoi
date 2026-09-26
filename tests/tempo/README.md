# Tempo: a change paced by what happens in it

Baseline: Wings, `wings.html` on this branch, SHA-256
`462bbd3059fbf3b693f69e8fd45ef6f3622f4e342b1e85626f964a723c6180ab`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Since Wings the changes read as aggressive: punchy, not clumsy. Two things
in the engine speed a cell up in the middle of its trip.

- **The ease.** Every change ran its cells' progress on easeInOutCubic: slow
  away, three times the average speed at the middle, slow in. That is the
  pace for one thing crossing empty space, where the middle of the trip is
  the dull part. A change of the page has no dull part.
  - Measured on the planned paths of the tour's 24 paced changes at both
    sizes, a change is about as busy per unit of progress all the way
    through: its middle is 0.74 to 1.11 times as busy as its ends.
  - So the ease crams what happens into the middle third. There it happens
    at 2.72 to 3.24 times its average rate.
- **The move.** A move of Improv's slowed a cell's clock at once to a crawl,
  and 0.3 s later at once to a hurry. Wings makes such moves in the browser
  (Improv hardly did, at desk size), so Wings is where they started to
  show. Each is a step in a cell's planned speed: the plan's acceleration
  at its worst was 19 to 20 times Shoal's.

Tempo tests whether a change paced by what happens in it moves more calmly,
and whether it still draws fewer defects than Shoal.

## How it paces

- **What happens.** At the click, the change's planned paths are measured
  at 33 points of its progress:
  - every moving cell is one thing to follow;
  - every pair of cells moving against each other is one more, weighted by
    how close they are.
- **The pace.** The change runs so that what happens, not distance, follows
  the smoothest rest-to-rest profile there is: minimum jerk, the profile
  of a person's reaching hand. It is slower where much happens and quicker
  where little does, and soft at both ends.
  - Its peak rate is 1.875 times its average, against the cubic's 3.
  - The landing time does not change.
  - Between the points, what happens is taken as a straight line. The
    progress is then solved exactly, so its speed never steps.
- **Scope.** One pace for the whole change, shared by all its travellers,
  since the cells set off and land together. The page's own changes are
  paced. The stories keep their choreography.
- **A move, smooth.** A move holds a cell's clock back by the same 0.255 s
  as Improv's crawl did.
  - The time is taken and given back by minimum jerk, never slower than
    Improv's crawl rate of 0.15.
  - It is given back no faster than it was taken, so a move needs 1.125 s
    of its cell's trip left.
- **When an answer is due** (Improv's deadline: when the cells have gone a
  twentieth of their way) is read off the change's own pace.

The header's captions are gone.

## Measured

The validator's figures. Frames are 1/64 s, and the worker of Wings thinks
16 rehearsed frames a frame on Wings and on Tempo alike.

**How fast things happen**, per change of the tour (24 paced at each size,
and the flock, where nothing travels):

| | easeInOutCubic (Shoal, Wings) | Tempo |
|---|---|---|
| Peak rate of what happens, against its average | 2.72 to 3.24 | 1.87 |
| Peak rate of progress, against its average | 3 | 1.81 to 2.07 |

**How the cells move** on the tour. Seeds are what a cell is drawn around;
the plan is the point on its path the seed follows. "Close pairs" is close
pairs of cells moving against each other: relative speed weighted by
closeness.

| 1440×900 | Shoal | Wings | Tempo |
|---|---|---|---|
| Seed acceleration, mean (px/s²) | 461 | 468 | 376 (−20%) |
| Seed acceleration, 99th percentile | 1,766 | 1,855 | 1,312 (−29%) |
| The plan's acceleration at its worst | 3,383 | 67,686 | 3,627 |
| A cell's peak speed over its average (median) | 2.34 | 2.34 | 1.82 |
| Close pairs, 99th percentile | 1,885 | 1,871 | 1,611 (−14%) |

| 390×720 | Shoal | Wings | Tempo |
|---|---|---|---|
| Seed acceleration, mean (px/s²) | 313 | 317 | 258 (−19%) |
| Seed acceleration, 99th percentile | 1,367 | 1,480 | 1,101 (−26%) |
| The plan's acceleration at its worst | 2,028 | 38,267 | 2,671 |
| A cell's peak speed over its average (median) | 2.23 | 2.23 | 1.81 |
| Close pairs, 99th percentile | 958 | 908 | 814 (−10%) |

The percentages are against Wings.

**Defects drawn:**

| | Shoal | Wings | Tempo |
|---|---|---|---|
| Tour of 25 changes, 1440×900 | 25,352 | 21,277 | 22,226 (+4%) |
| Tour of 25 changes, 390×720 | 18,528 | 17,544 | 17,752 (+1%) |
| 56 page-to-page changes, 1440×900 | 165,165 | 123,704 | 119,095 (−4%) |
| 56 page-to-page changes, 390×720 | 62,631 | 37,520 | 41,518 (+11%) |

- **By kind, against Wings:**
  - Lurch is down everywhere, by half on the phone tour (1,724 → 840).
  - The start shock is up on the tours (1,672 → 1,949 on a desk; 1,133 →
    1,399 on a phone).
  - On the phone's page-to-page changes the rise is all slivers: 261
    frames to 342, at 50 each.
- **Thinking:** 16 and 17 moves on the tours; 116 and 131 on the
  page-to-page changes. None was late. 20,467 frames were laid bit for bit
  on the worker's rehearsal of its move.

**In Chromium**, headless, 12 changes a size, with the budget measured:

| | Frames drawn, Wings | Frames drawn, Tempo | Moves, Wings | Moves, Tempo |
|---|---|---|---|---|
| 1440×900 | 1,842 | 1,828 | 20 | 10 |
| 390×720 | 1,878 | 1,882 | 22 | 14 |

- **First motion** came 9–75 ms after the ask, against 9–54 ms on Wings.
- **Errors:** none.

## Known

- **Slivers stay longer.** A change's slivers come in its middle: on Shoal,
  most of them between 0.4 and 0.7 of its time. The pace spends more time
  there, and so the thin mid-change shapes are on screen for more frames.
  That is the price of not rushing the middle. On a narrow phone, where
  mid-change cells are often thin, it costs the page-to-page changes 11%
  against Wings. It is still a third fewer defects than Shoal.
- **The ends are livelier.** What the middle gives up, the start and the
  end take back. A tenth of the way through its time, a cell has gone about
  twice as far as on the cubic. The start shock (drawings outrunning their
  seeds in the first quarter second) is up on the tours.
- **Fewer moves.** A smooth move needs 1.125 s of its cell's trip left, so
  the hive made about half as many moves as Wings in Chromium. An answer is also
  due sooner, when the cells have gone a twentieth of their way: about 19%
  of the change on the pace, against 23% on the cubic. On the page at a
  desk's budget of 8, that left every round coarse, so none could be laid
  on the performance frame by frame. The validator checks the on-page path
  at 16.
- **What happens is measured on the plan, at the click.** The cells'
  shapes and sizes changing are not counted, nor the cells a page's gallery
  brings in after the click. Measured by the plan alone, a change is as
  busy at its ends as in its middle, so the pace comes out close to plain
  minimum jerk. The ease was the problem more than the geometry.
- **The spring is the same.** The seed follows its plan on the spring it
  always has (a damping ratio of about 0.86, a small overshoot). The spring is not what sped
  the middle up.
- **Inherited from Wings:** the fields inside cells are not rehearsed, and
  a move can slow a cell and let it catch up, not hurry one.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and the worker of Wings headless: a second copy of the page's
script, its messages crossing as structured clones, answering when a worker
thinking 16 rehearsed frames a frame would.

It runs two sets of changes, each on a desk (1440×900) and a phone
(390×720):
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **The pace is what it says.** Right after each ask:
  - every traveller of the change has one pace, and the flock (whose cells
    go nowhere) has none;
  - the pace is the measure of the planned paths, taken again by the
    validator from the plan as the page measured it;
  - its progress runs from 0 to 1, never back, from rest to rest;
  - at every point of its clock the change has had exactly the minimum-jerk
    share of what happens in it.
- **The pace is the only change besides the thinking.** With no budget and
  the pace taken out, every frame of the tour is Shoal's, the world and
  every drawing command: 11,550 frames on a desk and on a phone.
- **Calmer than Wings and than Shoal**, on the tour at both sizes:
  - the seeds' acceleration, mean and 99th percentile;
  - a cell's peak speed against its average;
  - close pairs moving against each other.
  - The plan's acceleration at its worst is also below Wings's.
- **Nothing waits.** From the ask, the page's clock runs every frame.
- **What the worker rehearses is what the page plays**, to the bit, frame by
  frame, from each move made at the page's own frame until the next move
  acts.
- **Every move acts when its answer was expected.**
- **Fewer defects than Shoal**, on the tour and on the page-to-page changes,
  at both sizes.
- **With no worker the hive thinks on the page** (at a counted budget of
  16), makes moves, and plays what it rehearsed there, frame by frame: 1,403
  frames laid bit for bit on the desk tour.
- **Still correct.**
  - Nothing fractures on any frame.
  - Every page at rest is exact as on Shoal: the image on its rectangle and
    covering it, the text covering its own with the title in it, the
    whitespace exact, no field, one site to a cell.
- **A story keeps its own pace and is not thought about.**
  - A Cue story is Shoal's frame by frame (2,040 frames, the world and every
    drawing command).
  - Cue's own story checks pass on a desk and a phone.
  - A Tell and a Tell II story run to their end and home without a fractured
    cell.

## Run

```bash
python3 tests/tempo/build.py
node tests/tempo/validate.cjs
```
