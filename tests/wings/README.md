# Wings: the hive thinks offstage

Baseline: Improv, `improv.html` on this branch, SHA-256
`d36159a3aeb3253f430c8bb81e1121b739c66e3b9b9e69d0f16bfd54d7dedd7e`.
The builder reads that file from the repository root and checks the hash.

## What it proves

Improv thought on the page's own thread, in the time each frame left. That
time is shared with drawing. Where the browser was already short of it (a
large canvas rastered in software), the hive found nothing to spare and
hardly thought, and where it did think it cost a few frames. Wings gives
the thinking a thread of its own, and tests whether the hive can think more
and cost the page nothing.

## How it thinks offstage

- **The worker is this same script.** It runs in a Web Worker with the
  page's document stubbed out, the way the probe runs it headless. The
  worker's code is not a copy to keep in step: its rehearsals are the page's
  own code.
- **A round crosses as a structured clone.** The page copies itself as it
  is and posts the copy with what to rehearse. It plays on while the worker
  rehearses, and makes the worker's move if the answer comes in time; a late
  answer is dropped.
- **Two things do not survive a clone.**
  - The reel's strip definitions carry two small functions: a strip's slots
    and rectangles, a pure function of the strip's region and the page's
    size. The reel's strips and its page's spec both hold them. Every
    reference crosses as a stand-in with the region and count, one stand-in
    for each definition so that what was shared stays shared. The worker
    rebuilds each once.
  - A clone keeps no class, so the worker gives the hives theirs back.
- **How much the worker thinks is measured** answer by answer: what a
  rehearsed frame takes there. How far and how finely a round rehearses
  follows from that by Improv's rule, with two frames allowed for the
  message and the answer.
- **Where no worker can be had** (a host that forbids one, or the probe),
  the hive thinks on the page exactly as Improv does.
- **A failure in thinking never stops the page.** The thought is dropped,
  and if it was the worker's, the hive thinks on the page from then on.
  (Found building it: a round that could not be cloned used to throw inside
  the frame and stop the page's clock.)

## Measured

The validator's figures, with a worker's budget of 16 rehearsed frames a
frame. Chromium measured the worker at 10 to 45 on this machine. Frames are
1/64 s.

| Defects drawn | Shoal | Improv (8, on the page) | Wings (16, offstage) |
|---|---|---|---|
| Tour of 25 changes, 1440×900 | 25,352 | 22,641 | 21,277 (−16%) |
| Tour of 25 changes, 390×720 | 18,528 | 17,911 | 17,544 (−5%) |
| 56 page-to-page changes, 1440×900 | 165,165 | 139,033 | 123,704 (−25%) |
| 56 page-to-page changes, 390×720 | 62,631 | 46,616 | 37,520 (−40%) |

- **Moves:** 25 and 23 on the tours, 147 and 160 on the page-to-page
  changes. None was late.
- **Frames checked:** 30,239 frames of performance laid bit for bit on the
  worker's rehearsal of its move.

**In Chromium**, headless, 12 changes a size, with the budget measured:

| | Frames drawn, Shoal | Frames drawn, Wings | Moves made | Answers dropped as late |
|---|---|---|---|---|
| 1440×900 | 1,856 | 1,829 | 40 | 4 |
| 390×720 | 1,882 | 1,883 | 19 | 3 |

- **First motion** came 7–67 ms after the ask, against 8–51 ms on Shoal.
- **The page's own share of the thinking** was 6 to 30 ms a change: copying
  itself and posting.
- **The worker ran** from a file and from a server alike.
- **Errors:** none.

## Known

- **Late answers.** The worker's speed is estimated from earlier rounds. A
  page's rounds cost more than a scene's, so the first rounds after
  opening a page sometimes answer late, and their moves are dropped: a lost
  chance, not a defect.
- **The fields inside cells are still not rehearsed.** The copy the worker
  gets holds them as they were. A field that finishes merging on the page
  while the worker rehearses leaves the worker's copy counting the change a
  moment longer. On the tours this never reached the page's cells within a
  move's checked frames. Stepping the fields offstage was tried and is not
  in: a field's members drift toward label anchors that only painting sets,
  and a worker does not paint.
- **One power, one way:** a move can slow a cell and let it catch up; it
  cannot hurry one.
- **A host that forbids workers**, whether blob and data URLs are both
  refused or the worker errors, gets Improv.

## Validated

`validate.cjs` runs the real tick with Canvas and the DOM stubbed, frames of
1/64 s, and a counted budget. Headless there is no browser worker, so the
worker is a second copy of the page's script, loaded as the worker loads it:
the document stubbed, told it is the worker. Its messages cross as
structured clones, and an answer arrives at the frame a worker thinking 16
rehearsed frames a frame would have it in hand.

It runs two sets of changes, each on a desk (1440×900) and a phone
(390×720):
- **the tour:** home's scenes; home to Moss, Aurora, Coal, Petal, Drift,
  Ember, Dune and Jazz and back; and Coal → Aurora and Ember → Tide;
- **every page from every other kind:** a chain through all 56 ordered pairs
  of the eight kinds.

The checks:

- **Thinking leaves no trace of its own.** With no budget, every frame of
  the tour is Shoal's, the world and every drawing command: 11,550 frames on
  a desk and on a phone.
- **Nothing waits.** From the ask, the page's clock runs every frame.
- **What the worker rehearses is what the page plays.** From each round
  whose move was made at the page's own frame, the performance is the
  worker's rehearsal of the move, frame by frame, until the next move acts.
  That covers every cell's seed, speed, claim, crystal, progress and sites,
  to the bit. The copy crosses to the worker and back without losing a bit.
- **Every move acts when its answer was expected**, never before its round
  began.
- **Fewer defects than Shoal**, on the tour and on the page-to-page changes,
  at both sizes.
- **With no worker to be had, it is Improv:** every frame of a desk tour at
  Improv's budget of 8 is Improv's, the world and every drawing command.
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
python3 tests/wings/build.py
node tests/wings/validate.cjs
```
