# VIBE — the brief for the fighting cells

This is the brief for the `vibe` workflow (`.claude/workflows/vibe.js`). It is
written for the agents the workflow spawns and for the operator who runs it.
Read all of it before touching the code.

## 0. The complaint, in the owner's words

> The cells still feel like they're fighting each other with extremely rapid
> recalculations. There's a lot of 'pressure' on these cells. During the
> transition cells often oscillate rapidly between two points, frame by
> frame. It's not that they're wrong, but there's a certain stupidity to it.
> As if they can't anticipate each other's trajectories and have to fight and
> dance for their place and then have to settle for the outcome of that
> chaos. It's almost depressing to watch. It's also not what the original
> boids were meant to prove. I think it's about letting various cells have
> right of way such that the others can chill. Givers and takers.

The last two gauntlets fixed the JUMPS (a cell changing more than 12% of
itself in one frame: 63 to 14 over five scene changes) and the paint cost.
This one is about what is left below that threshold: the frame-by-frame
fight, the pressure, the absence of anticipation. Boids prove that three
local rules (separate, align, cohere) make a flock that flows: each agent
reads its neighbours' velocities and yields before it collides. Our cells
read nothing: each frame the auction settles who owns what, given where the
seeds are, and the seeds are pushed around by forces that disagree.

## 1. What the file is

`hive.html`, one file, one IIFE, ~3800 lines. Page elements are bodies in a
power diagram (semi-discrete optimal transport: every seed gets the area its
claim says; damped Newton on the weights, 3 iterations per frame, warm).
`SEED.md` is the founding document; read its last five exhibits (from
"Rounding is an opening, not a budget" on) for the vocabulary and the model:
crystal, walls, holes, the shadow auction, the garment.

A body's states, keyed by `b.crystal` in [0, 1]: a FREE cell (crystal 0,
bidding in the main auction), a WALL (crystal 1, settled: its rectangle, cut
out of the ground), a HOLE (in between: a convex shape carried as half-planes,
travelling between the cell it would have — its cell in the SHADOW auction,
one auction per pocket where every non-wall body bids — and its rectangle,
smoothed on `HOLE_TAU` = 0.08 s).

## 2. What the file does to a body that is moving

Per frame (`step`, ~line 2783): `steer` → `computeWalls` → `separate` →
`enforcePreconditions` → `easeClaims` → `placeSeeds` → `solve` (main, then
shadow) → `computeOutlines` → the fields → the picture → the garment.

- **A scene change is a journey per body** (`enterScene` ~1808): targets
  assigned (greedy nearest + 2-opt on squared travel), a quadratic bezier
  path from where it is to its slot, `easeInOutCubic` progress over `dur`
  (~0.9 s), and a DELAY per body from `passageTimes`: the change percolates
  from an origin across the body graph at `config.stagger` (0.30 s mean per
  shared edge; a slider). This is the only sequencing there is. Bodies with
  similar delays move at once and cross each other's paths.
- **The seed chases a carrot on the path with an under-damped spring**
  (`steer` ~1972): `ax = (carrot + wobble − x)·k1 − vx·k2`, k1 ≈ 62, k2 =
  13.5, plus a resting wobble of 2.5 px scaled by (1 − crystal), a speed cap
  of 900 px/s. A landing body is then pinned to its slot as `pin` rises.
- **Liquid bodies repel** (`separate` ~2049): every pair closer than 0.85 ×
  the sum of their claim radii gets a push, F = 2600 × (1 − min crystal) ×
  (1 − d/R) × dt / d, scaled per body by (1 − its crystal). This is where a
  traveller shoves a neighbour off its path, and the spring pulls it back.
- **The crystal** (`updateCrystal` ~1991): melts over `MELT` = 0.30 s where
  the body stands (the journey has a `hold`), travels at 0, locks over the
  last 0.35 s of the journey + 0.15 s. The picture's switches (wall → hole →
  free → hole → wall) hang on this.
- **Holes are cut by walls and by stronger holes**, in crystal order
  (`computeWalls` ~2169); a hole's target is its shadow cell, smoothed; ground
  no seed stands in is adopted by the nearest hole (`adoptGround`).
- **The auction** (`solveMain` ~2394, `solveShadow` ~2620): one per pocket of
  the ground, 3 Newton iterations per frame from warm weights, a newcomer
  entering at the weight that reproduces its painted area.
- **Free drift** (no path): wander + weak centering + a pull toward the
  body's `anchorX/Y`, which is the ink's inscribed pole from the garment.
  (Yes: the garment feeds back into the seed, weakly. SEED's FIXED list says
  it never does. Known; the owner's decision; not this gauntlet's.)

## 3. What has been measured

The instrument is `.claude/gauntlet/flicker.js` (section 5). Baseline on the
current file (commit `6796222` + the garment probe fix, i.e. PR #228), the
scorer's scenario (pointer parked at 700,400; 120 frames settling in Flock;
Bento, Hero, Sidebar, Frame, Flock, 330 frames each):

| clock | shapeBackShare | flipFrames | wasteC | revA | fight | lag px | sliver mean / p95 | pressure mean |
|---|---|---|---|---|---|---|---|---|
| 60 fps steady | 0.022 | 50 | 0.062 | 0.020 | 0.225 | 52.8 | 2.92 / 9.31 | 0.21% |
| 30 ms steady | 0.038 | 58 | 0.075 | 0.037 | 0.204 | 51.7 | 2.46 / 8.34 | 0.32% |
| 25 ± 12 ms | 0.037 | 53 | 0.076 | 0.039 | 0.217 | 51.3 | 2.59 / 8.40 | 0.27% |

Read: 2.2% of all shape motion is undone within a frame at a steady 60 fps,
and 3.8% at 30 ms frames — the fight grows with frame time, which is how the
owner watches it. A travelling seed moves AWAY from its own carrot in 22% of
its travelling frames (49% in the opening Flock, 33% in Bento) and trails it
by 53 px on average. One cell in twenty is nine times thinner than a disc.
The auction is nearly converged every frame (mean residual 0.2%, over 1% in
0.5% of frames): NEWTON IS NOT THE FIGHTER. The worst bodies by undone
motion are 9, 7, 8, 0, 5; the worst scene is the opening Flock, then Frame
and Sidebar (per-scene numbers in `flicker-base.json` next to this file once
the operator runs the baseline; `--dump` gives every frame).

From the earlier gauntlets, still true: a pure rate limit on the shapes (the
control variant) buys numbers and moves the error to the switch — it is not
an answer, and the refuters in this workflow are told to call it. Ground
continuity (a seedless pocket keeps its last painter) and the free-cell
oscillation were the same event seen from two sides. The hover shard used to
appear whole in one frame; fixed.

## 3.5 WHAT THE DIAGNOSIS FOUND (supersedes section 4)

Ten ablation lenses ran, each on its own copy, each verified against the
baseline first. **Read this before designing anything; it kills most of
section 4 and most of section 6.**

**The headline: the last gauntlet's invariants are a 60 fps result, and the
owner does not watch at 60 fps.** On the untouched file:

| clock | jumps | reversals | shock px² |
|---|---|---|---|
| 60 fps steady | 14 | 1 | 157,637 |

*(Superseded twice since: the clock fix, then the swerve. On `claude/anticipation` the 60 fps row is 13 / 1 / 135,279 with gapMax 4. Always re-measure the baseline on the file you are actually building from — four agents in one round independently caught a stale row here.)*
| 25 ± 12 ms | 47 | 5 | 613,164 |
| 30 ms steady | 61 | 4 | 724,778 |

Four times the jumps at the frame times a real browser gives. This, not the
sub-threshold flicker, is most of what the owner is describing.

**What is NOT the cause (do not design for these):**

- *Path crossings.* The assignment (greedy + 2-opt on squared travel) is
  already cyclically monotone, i.e. crossing-free by construction: 0-4
  straight crossings per scene change out of 66 pairs. Correlation of
  crossings with undone shape is r = 0.036; total shape motion correlates at
  0.656. Forcing 200× more crossings *lowers* `fight`. Nothing to win.
- *Cut-order flips.* Two holes swap crystal order in 10 of 1771 frames,
  carrying ~0.2% of the undone motion. Hysteresis there wins nothing. The
  sort is not stability, it is priority, and it is load-bearing: by body id
  instead, jumps go 14 → 68 with a vanish.
- *The carrot spring.* Gluing the seed to its carrot is WORSE at both clocks
  (flips 50 → 66 steady, 53 → 85 jittered). The spring is a low-pass filter
  and a speed limiter, not a noise source.
- *Newton's iteration count, as an everyday matter.* Full convergence
  (maxIter 30) drives the residual to 1e-7 and moves `shapeBackShare` by
  0.000 at 60 fps.
- *Harder sequencing.* stagger 0.30 → 0.90 shatters everything (jumps 143,
  12 vanishes) and 0.05 (all at once) *lowers* the fight numbers. 0.30 is a
  tuned valley. Simultaneity is not the fighter.
- *The wobble.* Zeroing both noise terms leaves `shapeBackShare` at 0.023.
  (It is worth 27% of `shockPx2` though, and it is cosmetic — a separate,
  cheap decision for the owner, not a fix for this.)

**What IS the cause, in order of measured size:**

1. **Frame-rate dependence in three named places.** `maxIter: 3` is per
   FRAME at three sites (~2581, ~2617, ~2707): at 25-45 ms the auction gets
   1.5-2.7× fewer Newton iterations per second on a warm start 1.5-2.7×
   staler. On a rare frame the residual explodes (54% at sidebar f878),
   the frame paints a whole neighbourhood wrong — 34,000 px² reallocated
   among five cells — and the next frame takes it all back. `LINGER_MAX = 40`
   and its ramp `1 - lingerFrames/(LINGER_MAX-6)` are FRAME counts, so a
   closing hole's catch-up stretches 0.67 s → 1.2 s at 30 ms (12 'opening'
   jumps at 30 ms against 2 with the count in seconds).
   `enforcePreconditions` damps `vx *= 0.5` and ejects 0.5 px per FRAME.
   The semi-implicit integration adds an effective extra stiffness k1·dt²
   (12.6% of the gap at 45 ms), which is why `lag` falls as dt rises: a long
   frame tracks tighter and rings harder.
2. **The weakest hole is carved by everyone.** The worst single event at
   30 ms: Frame scene, body 9, painted area 37,936 → 8,413 → 20,589 px² in
   two frames while its own target core sits steady at 39,000-41,000. It is
   a hole at crystal 0 — the last in the cut order, so every wall and every
   stronger hole subtracts from it — lingering while it waits to catch up
   and close. It has no protection and no priority, and at coarse frames the
   things crossing it move far enough per frame to carve it to a fifth of
   itself and give it back.
3. **Repulsion is what makes a seed fight its own path** — `separate()`
   at F = 0 takes `fight` 0.225 → 0.085 (−62%), in every scene. But
   `shapeBackShare` does not move (0.022 → 0.023), so THE SEED FIGHT AND THE
   SHAPE OSCILLATION ARE DECOUPLED: calming the seeds does not calm the
   picture. And repulsion is load-bearing for coverage — at F = 0, gapMax
   8 → 1328 px² and overMax 0 → 20, a static hole in the landed picture.
   Anything that removes it must carry a coverage guarantee.
4. **A latent tie-break hole in the auction.** At flock0 f88
   `enforcePreconditions` ejects bodies 8 and 9 out of the same wall on the
   same side to exactly x = 840.5, both with claim exactly 1.000 — a
   perfectly symmetric pair the auction cannot separate; body 8's cell
   collapses to zero with maxRelErr 1.0 for ten frames. In the shipped
   scenario the tie is broken only by a leftover hoverMix of 0.01 on body 9.
   Park the pointer 350 px away and it reappears as vanish 1. The published
   baseline's clean invariants are partly an accident of pointer placement.

**A caution about the metric.** `shapeBackShare` grows with mean frame time
(0.015 at 8 ms, 0.022 at 16.7, 0.038 at 30, 0.053 at 45) while total shape
motion stays flat at ~25M px², and a control with the whole simulation on a
fixed 1/60 s clock and only the SAMPLING coarsened reproduces the same
curve. So most of that growth is the curvature of a legitimate trajectory
sampled coarsely, not a worse trajectory. **Never compare `shapeBackShare`
across clocks; compare at one clock.** `flipFrames` is chaos-noise at this
sample size (a 1e-16 perturbation moved one scene from 9 to 16) — rank on
`shapeBackPx2`, never on flip counts.

**And a warning for any right-of-way design.** `easeClaims` moves a body's
claim only with its own journey progress, so a body that yields keeps its
OLD claim on ground that the bodies which already landed have had cut out
from under it as walls. In the stagger ablation this starved the waiters:
their summed claims no longer fit the ground left to them, the auction
could not meet its targets, a body's leaf went 30k → 0 → 1k → 0 and
`enforcePreconditions` finally teleported the seed 147 px out of a wall it
was standing in. **A yielder must renegotiate its claim in step with its
yield, or it starves.** This is the single most important constraint on the
owner's own idea.

## 3.6 THE STROBE — what the owner is looking at now (read this first)

The owner came back with two complaints and one of them cannot be
screenshotted:

> "a corner of a cell is stuck behind other cells and stretched like chewing
> gum across the screen ... but that's not the only issue. The other issue is
> one that I can't screenshot because each individual frame looks fine. but
> when you move frame by frame the cells jump all over the place. Each frame
> they got a new position without even bothering to travel there."

Six probes ran on the current file. Here is what they found, including two
things that are **not** the cause, which are as useful as the one that is.

**The auction is not broken.** It converges to a relative residual of 1e-8 to
1e-12 in two to four iterations, every frame, in every scene. Per body the
gap between the cell it painted and the area it was asked for is 0.0% almost
everywhere. Nothing here is a solver bug and nothing here is fixed by more
iterations or a tighter tolerance.

**The pocket partition is not the cause.** Suspecting that a body carried a
warm weight across a change of auction — weights are only defined up to a
constant *per auction*, so a repartition would arrive in a new gauge — the
partition was recorded frame by frame. It changes in 1% of frames, 62 body
frames in the whole run. Meanwhile 4,733 body frames whose auction did not
change at all carry weight changes with a mean of 1,900 and a maximum of
219,051. Refuted: the strobe happens inside a stable auction.

**What it is: nothing bounds how far a wall may move.** The wall between two
cells is where |x−sᵢ|² − wᵢ = |x−sⱼ|² − wⱼ. It is perpendicular to the line
joining the seeds and it sits offset from their midpoint by

        (wᵢ − wⱼ) / (2 d),     d = the seed separation

so a wall moves for exactly two reasons: the seeds travelled and it came
with them, or the seeds stood still and the auction handed back a different
weight difference than last frame. `wall.js` measures both, in pixels:

| clock | walls decided (mean px/frame) | walls travelled (mean px/frame) | ratio |
|---|---|---|---|
| 60 fps | 3.26 | 2.80 | **1.16** |
| `--dt 30` | 4.22 | 3.82 | **1.10** |

**The walls of this page move further from being re-decided than from
anything moving.** Per scene at `--dt 30` the ratio is 3.45 in the opening
Flock, 1.09 in Frame, 1.21 in Flock, 0.72 in Sidebar, 0.54 in Hero. In the
Flock the decision is three and a half times the travel. That is the thing
that has no screenshot: every frame is a correct picture of a slightly
different page.

The tail is worse than the mean. 127 walls at `--dt 30` slid more than 40 px
in a single frame; the worst slid **1,720 px** between two seeds **13 px
apart**. Which is the second complaint:

**The chewing gum is the same equation with a small d.** The offset divides
by the separation, so as two seeds drift together the wall between them runs
away — a weight difference of 20,000 across a pair 8 px apart puts their
shared wall 1,250 px from the midpoint, and the cell that owns that side
becomes a wedge stretched across the page. `strobe.js` counts 1,073 of these
at `--dt 30` (a painted piece further than 3.5 equivalent radii from its own
seed). The worst is a free cell of 2,065 px² — a disc 26 px across — with a
vertex **405 px** away. `SEED_MIN_SEP` is 5 px and only separates pairs
closer than 1 px, so nothing in the file stops d from going where the
division cannot follow.

Both complaints are one sentence: **a weight is a place, and unlike every
other place in this file it is teleported to rather than travelled to.**

The two instruments for it:

    node .claude/gauntlet/wall.js   <hive.html> [out.json] [--dt 30] [--jitter 12]
    node .claude/gauntlet/strobe.js <hive.html> [out.json] [--dt 30] [--jitter 12]

`wall.js` fields: `strobeRatio` (decided ÷ travelled, the headline),
`decidedPx`/`travelPx` (mean/med/p90/p99/max px per pair-frame),
`reachPx` (|wᵢ−wⱼ|/2d, how far outside its own pair a wall sits),
`slidOver40`, `reachOffPage`, per-scene breakdown, `worstSlides`.
`strobe.js` fields: `teleports` (a painted mask that changed more than its
own seed's travel can explain), `reaches` (a piece more than 3.5 equivalent
radii from its own seed), `reachNested`, `churnShareMean`.

**Baseline on the current file** (`claude/masked`, after the clock, the
anticipation, the guest pointer and the mask), so nobody quotes a stale row
again:

| clock | jumps | reversals | shock px² | gapMax | teleports | reaches | strobeRatio |
|---|---|---|---|---|---|---|---|
| 60 fps | 11 | 1 | 65,777 | 8 | 85 | 1,976 | 1.16 |
| `--dt 30` | 27 | 2 | 202,939 | 8 | 119 | 1,073 | 1.10 |
| `--dt 25 --jitter 12` | 18 | 1 | 132,275 | 4 | — | — | — |

`vanish` 0, `overMax` 0, `settledScenes` 5/5, `pageErrors` 0 at all three.
Section 5's invariants are superseded by this row: do not give any of it back.

**The design question this opens.** Every weight vector gives a watertight
power diagram — a valid, gap-free, overlap-free partition of the ground.
The weights do not have to be the exact answer for the picture to be
correct; they only have to be the exact answer for the *areas* to be what
the claims asked for. So the file is free to let a weight travel to its
answer instead of arriving at it, exactly as a seed travels to its carrot,
and pay for it in area lag rather than in position. That is one direction of
many and the panel should not treat it as the brief; a rate limit that
merely holds shapes still against a moving target is the duck this brief has
rejected twice, and the difference between the two is whether the areas
converge when the page stops. They must: `settledScenes` 5/5 and exact
rectangles at rest are still hard invariants.

## 3.7 THE FIRST STROBE ROUND — nothing shipped, and what it established

Five designs, two judges, three builds in worktrees, six refuters. **No build
shipped.** The round is worth more than a build would have been, because it
killed the obvious cure and named the real one.

**Operator error first, so it is not repeated.** All three worktrees were cut
at `852d235` — four commits stale, before the clock fix, the swerve, the guest
pointer and the mask — while the brief handed the builders a baseline row
belonging to `02b52b7`. The table's baseline column and its build columns
described different programs, and the stale base is itself a two-to-threefold
regression on the shipped file. **A builder must copy `${REPO}/hive.html` into
its worktree before touching anything, and re-measure its own baseline there.**
Never trust the worktree's checkout.

**A correction to 3.6, caught by two agents independently.** The `reaches`
figure for 60 fps in the table above was 777; it is **1,976**. The 777 came
from a run of `strobe.js` taken before its reach measure was fixed, and it was
printed next to a `--dt 30` figure taken after. Both numbers in that row are
now post-fix. **1,162 of the 1,976 are inside nested fields.**

### What was refuted

**"The weight travels", the whole family, is refuted on the mathematics.**
It was the obvious cure — every other place in this file is travelled to on a
spring, so give the weight the same treatment — and it is wrong, for a reason
worth keeping:

> The areas a diagram hands back are not bounded by the areas at either end of
> the line between two weight vectors, so a step taken half way is not a
> picture taken half way. A cell asked to grow a little can be handed several
> times its claim in the middle of the move and give all of it back at the
> end — and that giving-back is the jump you were trying to prevent.

The build that tried it (a scalar λ on the whole step, bounding the worst
wall's slide to 500 px/s) took 60 fps jumps from 14 to **210**, reversals from
1 to **62**, shock to **4.3 million**, and lost a cell (`vanish` 1). Both
refuters returned DUCK: a control that simply forbids any single weight from
moving more than K·dt — knowing nothing about walls, seeds or pixels —
reproduces its headline to 1.5% at all three clocks with 41% fewer jumps and
no vanish. And the decomposition is the damning part: the cap empties the
middle of the slide distribution and refills the far end (pair-frames over
160 px: 2 → 18), so a design whose whole sentence is "a wall should travel,
not teleport" deleted the travelling slides and multiplied the teleports.

The other two builds were refuted on attribution rather than on physics. One's
named invariant (a reach rail on the weight difference) was **bit-identical to
base** in two independent ablations — it had been tuned until it did nothing,
and the file still paid an O(n²) clamp on every line-search trial for it; its
ranked win came from six lines of approach-velocity damping that had nothing
to do with its sentence, and a flat 100 px pair floor with its yardstick
deleted beat it on 8 of 9 cells. The other's three rules were two-thirds
inert, and its live rule's win was located, on four instruments at three
clocks, in the **120-frame cold settle before any scene button is pressed** —
`--dt 30` jumps went flock0 20 → 3 while hero 12 → 16, sidebar 21 → 20,
frame 5 → 6, flock 3 → 6. The owner's complaint is about transitions.

### What was established: the walls are not arguing, they are catching up

`wall.js` now answers this directly. Over an eight-frame window — a fifth of a
second at the owner's clock — a wall that is going somewhere sums its steps,
and a wall being re-decided in place goes back and forth and cancels. `carry`
is the share of a wall's motion that got it anywhere:

| scene | carry | strobeRatio | decided px/frame | travelled px/frame |
|---|---|---|---|---|
| flock0 | 0.89 | 3.45 | 12.89 | 3.74 |
| hero | 0.83 | 0.54 | 4.63 | 8.57 |
| sidebar | 0.86 | 0.71 | 8.52 | 11.93 |
| frame | 0.84 | 1.10 | 9.42 | 8.54 |
| flock | 0.97 | 0.98 | 1.36 | 1.39 |
| **whole run** | **0.92** | 1.10 | 4.22 | 3.82 |

**92% of every pixel a wall moves gets it somewhere.** The walls of this page
are not oscillating and they are not changing their minds. They are travelling
in a consistent direction, in strides three to four times longer than the
seeds' — which is what "each frame they got a new position without even
bothering to travel there" actually looks like from the inside. So:

> The strobe is not the auction changing its mind too fast; it is the auction
> catching up, and a wall that arrives late arrives further. Slow the world
> that invalidates the warm start, not the answer that repairs it.

That is the brief for the next round, and one more measurement says where to
aim it. The seeds travel smoothly because springs see to it; the target does
not. `tgt_i = claim_i × groundArea / Σclaims`, so rank the wall's slide against
each term over the 9,857 transition pair-frames (Spearman, `flock0` and
`bento` excluded because the cold settle is not the complaint):

| the wall's slide against | ρ |
|---|---|
| the change in Σclaims — **the denominator** | **0.697** |
| the seeds' own travel | 0.664 |
| the change in this pair's own target | 0.627 |
| the change in the ground's area | **−0.013** |

**The ground's area is innocent, and an earlier reading of this brief that
blamed it was wrong.** It swings by 16%, 29%, 45% in single frames and it
moves no wall at all, because the normalisation divides it straight back out
— exactly as the algebra says it should. What is left is the denominator and
the claims: a body crossing `ACTIVE_MIN` in or out of the auction is a step in
Σclaims by construction, and one such step moves **every** target on the page
at once, including the targets of bodies that are standing still.

The deciles say the same thing and say where it hurts:

| decile of |dTarget| | mean |dTarget| | mean wall slide | mean seed travel |
|---|---|---|---|
| 1–5 | 0.04–0.12% | 0.44–0.75 px | 0.86–1.71 px |
| 6–9 | 0.15–3.44% | 1.34–7.58 px | 2.63–8.87 px |
| **10** | **12.91%** | **10.71 px** | **7.38 px** |

In nine deciles out of ten the seeds outrun the wall: the page is travelling
and its walls are coming along. **In the top decile alone the wall outruns the
seeds**, and that decile is where the strobe lives. It is a tenth of the
pair-frames, and it is bought entirely by the target stepping.

**This page has a continuous position field and a discontinuous area field.**
A bidder should fade in and out, not appear.

The chewing gum is a separate tail and still stands: the offset divides by the
separation, `SEED_MIN_SEP` is 5 px and only separates pairs already closer than
1 px, and nobody has yet tried making the auction itself aware that a pair is
degenerate — a claim that shrinks as its own pair closes, rather than a floor
that shoves the seeds apart after the fact.

## 3.8 THE HARNESS, AND WHAT IT IS NOT ALLOWED TO DECIDE

Three defects were found in the harness itself. All are fixed; the rules
below are binding on every future round.

**1. Rank per scene, never on the aggregate.** The run is 120 frames of cold
settle followed by five scenes. `flock0` — the cold settle — dominates every
whole-run mean in the file: it holds the worst `strobeRatio` (3.45 against
0.54 in Hero) and a third of the teleports. A build can halve an aggregate by
improving only the part of the run the owner never sees. One did. **Report
every headline per scene and rank on the transition scenes.**

**2. Measure the chaos band before claiming a difference.**

    node .claude/gauntlet/twins.js <hive.html> [--dt 30] [--jitter 12]

runs the same file three times at `dt` and `dt·(1 ± 1e-12)`. Nothing about the
file changes, so the spread is the page's own chaos and any difference smaller
than it is a coin toss. Measured on the current file, at three clocks:

| metric | 60 fps and jitter | `--dt 30` |
|---|---|---|
| `vanish`, `overMax`, `settledScenes` | stable | stable |
| `jumps` | stable (11, 18) | **25–27** |
| `reversals` | stable (1) | **1–2** |
| `shockPx2` | within 0.8% | **2.71%** |
| `gapMax` | **8 → 24.** Not an acceptance test. | unstable |

An earlier reading of this section said `jumps` and `reversals` were stable at
every clock. They are not stable at `--dt 30`, which is the ranked clock; two
builders and a refuter caught it. And there is a floor below the clock band
that is worse: two **mathematically null** rewrites of the file's own target
arithmetic — changes that provably compute the same numbers — land at 25/1/193,273
and 24/1/167,378 against base's 27/2/202,939, purely from floating-point
re-association over 1,770 frames. **Any build that touches the target arithmetic
is comparable only to about ±3 jumps and ±17% of shock at `--dt 30`.** Run an
identity-rewrite control of your own change alongside `twins.js`, or your win is
arithmetic.

Note this band belongs to `02b52b7`. On the stale `852d235` the same
perturbations moved `gapMax` 20 → 164 and `shockPx2` ±30%; the clock fix
removed most of that, and a chaos band quoted from an old base does not
transfer. **Take the band on the file you are actually comparing.**

**3. A number can fall because its sample vanished.** `wall.js` reads only
pairs among the root main auction's live bidders. A change that pushes cells
into the hole or shadow path lowers `decidedPx` by deleting pair-frames rather
than motion — one build's Hero sample collapsed 741 → 42 pair-frames while
each surviving pair got 54% worse. `wall.js` now prints `pairFrames` and
`distinctPairs` per scene. **A mean is comparable only against a run with a
comparable sample; quote both.**

And the blind spot that made all of this possible:

    node .claude/gauntlet/nesterr.js <hive.html> [out.json] [--dt 30]

`score.js` reads the root diagram, `wall.js` the root main auction. A cell of
this page can hold a hive of its own, and until now nothing measured whether
those auctions were being answered — one build took the worst nested residual
from 0.4% to 6,180% and scored clean everywhere. On the current file the
nested auctions are healthy: median relative error 1e-11, p99 9.3e-7, 5
unconverged hive-frames in 5,649. **Every build reports this.**

## 3.9 THE SCOREBOARD WAS PARTLY MEASURING THE MOUSE

Round two shipped nothing — three builds, six refuters, six refutations — and
its most useful residual was a jump cluster nobody had diagnosed: **17 of the
27 jumps at the ranked clock are Sidebar**, and eight of them are `W>W`, a
settled wall changing area with its crystal pinned at 1 at both ends and every
claim on the page standing still. Three builders reproduced it to the pixel and
every build reproduced it bit-identically, so it is upstream of everything the
two rounds were building.

It is upstream of the auction entirely. Watched frame by frame, bodies 3, 4 and
6 enter Sidebar as settled walls painting **5% of their own rectangles** and
climb back: body 6 goes 2,579 → 7,184 → 13,631 → 21,229 → 29,283 → 36,999 →
43,499 → 47,116 px² against a rectangle of 55,474 that never moves. They are not
growing. **They are being uncrushed.** The pointer is parked at (700, 400) for
the whole run, in Hero that lands inside the hero card, the card expands on
hover and flattens its neighbours to slivers, and when the scene changes and the
boost is handed back the slivers spring out to their rectangles in eight frames.

`score.js` now takes `--parkx` / `--parky` and prints the pointer in its output.
Move it, at `--dt 30`:

| pointer | jumps | shock px² | byScene |
|---|---|---|---|
| **700, 400** (inside the hero card) | **27** | 202,939 | flock0 6, hero 1, **sidebar 17**, flock 3 |
| **40, 860** (bottom-left corner) | **16** | 164,060 | flock0 6, hero 3, **sidebar 2**, frame 2, flock 3 |
| **1400, 40** (top-right corner) | **40** | 907,782 | flock0 6, **hero 30**, sidebar 1, flock 3 |

The whole Sidebar cluster — all eight `W>W` jumps with it — evaporates when the
pointer is not leaning on a cell that expands, and a different park invents
thirty jumps in Hero instead. The score moves by 2.5× on the pointer alone.
Three rounds of ranking have therefore been ranking, in part, on where the mouse
happened to sit.

**Binding from here: every claim at three parks.** (700, 400), (40, 860) and
(1400, 40), at each clock you quote. A win at one park is not a win. Report the
pointer beside every number; the field is in `score.js`'s output so that a row
can never again be read without it.

Two things follow that are worth more than the correction.

**The Sidebar cluster is a real thing the owner can see, and it is not the
strobe.** A cell crushed to a sliver by its neighbour's hover, springing back
eighteenfold in a quarter of a second when the page changes, is a visible snap
with a named cause. The guest-pointer rule already says the held hover is handed
back across the change; the hand-back is linear in the boost and the area
response to it is not. That is its own problem, at its own site, and it has been
sitting in the middle of the scoreboard being counted as an auction defect.

**And the hard floors move with the pointer too.** At (1400, 40) at 60 fps the
untouched file reports `overMax` 4 — cells overlapping — where the standard park
reports 0. It is four square pixels and invisible, but it means the coverage
invariants were being certified at one pointer position and asserted generally.

## 3.10 ROUND TWO, AND THE ONE LIVE LEAD

Three builds, all refuted by both their refuters, on the round's own rules:

- **A held exchange rate between the claim and the ground** (low-pass the
  denominator, route the mismatch). Refuted by its own algebra: it deletes a
  per-frame step worth a fraction of a percent of the ground and then spends the
  *accumulated* lag, which in a transition is many times larger than the step.
  Transition jumps 21 → 22, whole-run shock 202,939 → 576,545, `overMax` 0 → 4,
  nested `bodyMiss` median 3.05e-12 → 1.88e-4, `carry` down in three scenes.
- **One clock for the area handover** (round one's survivor, rebuilt). Refuted
  again and now with a mechanism that generalises: gating a claim to the last
  melt-end forces every body but the last to **lock with a part-moved claim**,
  and a crystallising body's shadow cell is sized by that claim — the same
  disagreement it set out to remove, moved from the melt to the landing.
  Transition jumps 21 → 44, hero 1 → 19, `overMax` 0 → 2,380. Its whole-run
  improvements were 82–88% the cold settle.
- **The orphan pocket divided rather than awarded** (ground nobody bid for, cut
  up among every hole that borders it). The only build with a transition gain
  anywhere, and inert: deleting the division while keeping the rest reproduces
  its headline with an identical `kinds` and `byScene` histogram. **86% of its
  win was in which hole the argmax picks, not in dividing anything.** It also
  regressed the nested hives, and it found the coupling any successor must avoid:
  `holeExtra` reaches `b.loops`, `b.loops` gates `cellIsRect`, `cellIsRect` is
  the early-wall shortcut, and `b.hole.pieces.concat(b.holeExtra)` is a nested
  field's whole domain. **A hole holding a share of somebody else's pocket is no
  longer a rectangle.**

### The seed yardstick

What the third refutation leaves is six lines at the same site. `adoptGround`
picks the hole that receives an orphan pocket by comparing the pocket's centroid
to the centroids of the hole's **drawn pieces** — a shape re-derived every frame,
whose middle hops as the shape morphs, so the winner can change with nothing
having moved and a whole pocket changes colour. Pick by the hole's own **seed**
instead: the one thing about a hole that travels.

Measured on the shipped file, three parks, three clocks, by the operator:

| clock | park | base jumps / shock | seed yardstick |
|---|---|---|---|
| 60 fps | 700,400 | 11 / 65,777 | **9 / 52,635 (−20.0%)** |
| 60 fps | 40,860 | 9 / 74,270 | **7 / 64,745 (−12.8%)** |
| 60 fps | 1400,40 | 28 / 701,688 | 27 / 724,039 (+3.2%) |
| `--dt 30` | 700,400 | 27 / 202,939 | 26 / 208,871 (+2.9%) |
| `--dt 30` | 40,860 | 16 / 164,060 | 16 / 174,647 (+6.5%) |
| `--dt 30` | 1400,40 | 40 / 907,782 | 40 / 937,500 (+3.3%) |
| jitter | 700,400 | 18 / 132,275 | 18 / 134,771 (+1.9%) |

Floors clean: `nesterr` identical to base (median 1.31e-11, p99 9.31e-7, 5
unconverged of 5,649, over-5% 1); `carry` 0.917 against 0.919 with flock0, hero,
sidebar and frame **bit-identical** on carry, strobeRatio and pairFrames;
`vanish` 0, `overMax` unchanged at every park, settled 5/5.

Read it honestly. **Transition jumps fall at all six park-and-clock
combinations** (21→18, 10→8, 34→32 at `--dt 30`; 11→9, 9→7, 28→27 at 60 fps),
the Hero adoption jump is removed outright rather than demoted, and the 60 fps
shock win is far outside the 0.67% band at two parks of three. Against that:
**flock0 gains two jumps at every park**, and the `--dt 30` shock rise of
2.9–6.5% straddles a band of 2.71%.

It has never faced a refuter. It goes into the next round as the starting
position at that site, not as a ship.

## 3.11 THE OWNER WAS RIGHT ABOUT WHERE, AND THE INSTRUMENTS NOW SAY EXACTLY WHERE

The owner's correction, after mk14: the hover crush is real but negligible in
his hands; the strobe is in the layout transitions, from gridlocks; and the
bleed was rejected on a build that never tested it. All three were taken as
hypotheses and measured, with the pointer **off the canvas** so nothing is
hovered and the run is the transitions alone. That is now the primary park:
`--parkx -100 --parky -100`, and every instrument takes it.

**No-hover baseline** (`--dt 30`): 16 jumps / 164,060 shock, byScene flock0 6,
hero 3, sidebar 2, frame 2, flock 3; `carry` 0.915, `strobeRatio` 1.10,
decided 4.11 px against travelled 3.74, 123 slides over 40 px; teleports 99,
reaches 867 (451 nested). 60 fps: 9 / 74,270. Jitter: 13 / 127,827.

**The seed gridlock does not exist.** `stuck.js` — a body on a journey whose
seed is more than 30 px from its carrot and moving slower than 40 px/s for
three frames — finds five runs at `--dt 30`, all in the cold settle, none in
any transition. The seeds arrive on time.

**The ground gridlock does, and it is a queue.** `blocked.js` — a body on a
journey whose new slot is more than half under somebody else's wall or hole —
finds 45 runs in the transitions, 623 body-frames. In Hero seven bodies wait
34–51 frames (1–1.5 s) with their slots 69–100% covered. Every blocker is
itself on a journey (60 of 60), never seated: the slot was always going to be
free, the body sitting on it is just late, and nine of the runs are chains
(7←9←10, 3←2←0). 97% of the blocking is by **holes**, which no auction
instrument can see: `wall.js` measures pairs of bidders, and a hole is not a
bidder.

**But the block is not where the strobe is.** A blocked body's own churn is
2.2% of itself per frame against 1.8% free — barely different. Big slides on
its walls are enriched 1.3× while blocked and 1.8× in the five frames after
release, and the two together hold about 12% of the top decile. The queue is
real and it is the chewing gum (a blocked cell is a wedge of leftover ground);
it is not the frame-by-frame jumping.

**Where the strobe is: at the state changes.** `events.js` lines every pair's
slide up against the frames where a body changes state — wall→hole (WH),
hole→free (HF), free→hole (FH), hole→wall (HW), and a bidder entering or
leaving the auction — and asks what share of the top decile sits within a few
frames of one:

| `--dt 30`, no hover | frames | mean slide | p90 of the frame's worst slide |
|---|---|---|---|
| a state change within ±2 frames | 189 | **6.38 px** | 27.6 px |
| quiet | 310 | **1.22 px** | 6.4 px |

**Five to one.** 70% of the top-decile slides sit within ±2 frames of an event
(20% of all slides do); 86% within ±5. By kind, enrichment of the top decile:

| event | ±2 | ±5 | 60 fps ±2 |
|---|---|---|---|
| hole → wall (a cell locks) | **7.3×** | 6.7× | 5.9× |
| free → hole (a cell starts to lock) | **5.6×** | 5.3× | 3.6× |
| bidder leaves the auction | **4.8×** | 4.2× | 3.2× |
| hole → free (a cell melts loose) | 2.6× | 2.8× | 1.2× |
| bidder enters the auction | 2.6× | 2.8× | 1.2× |
| wall → hole (a cell starts to melt) | 1.3× | 1.4× | 0.4× |

The arrival side is the strobe. A cell that locks leaves the bidding (the
denominator steps), its shape is cut from the ground as a hole (the ground
steps), and when its hole becomes a wall the morphed shape is replaced by the
exact rectangle (the ground steps again). Every free wall in the pocket answers
each step. The melting side, where a cell's claim and hole are handed *to* the
auction, is two to five times gentler — which is the paintArea handover doing
its job on the way in and nothing doing it on the way out.

So the owner's sentence, corrected by the instruments: **the least jarring way
to lock a cell.** Four discontinuities, each at a named site, each measurable
by its own row in the table above.

**The bleed, built as real liquidity, is refuted — and for a reason.** The old
build pinned every cell's on-page area to what it would have been without the
bleed ("growing the domain moves no cell's page area by one px²"): inert by
construction, and never a test. This one lets cells hold part of themselves off
the page: the ground reaches 15% of the short side past the edge at full melt,
claims are shares of that ground, seeds may enter 40% of it. `--dt 30`,
no hover: **283 jumps against 16**, shock +1,592%, `vanish` 7, `gapMax` 1,144,
teleports 99 → 244, blocked runs 45 → 68, every scene worse at every clock.
The mechanism: in a power diagram every px² is owned and every area is exact,
so extra ground is either shared — every target inflates by the bleed ratio as
the page melts and deflates as it locks, and the whole page breathes — or owned
by a slack agent, which is the inert version. **There is no such thing as
slack.** The room the idea wants has to come from a cell yielding its claim
while it waits, not from ground.

`score.js` now clips every loop to the page before measuring it (inert on the
shipped file: 16 / 164,060 before and after), so a cell that spills is not
scored as having grown.

## 3.12 WHAT MOVES A WALL WHOSE SEED IS STILL

Everything below is `--dt 30`, pointer off the canvas, the shipped file.

**Refuted this round, each by its own control:**

- *The 80 ms shadow relocation of a newborn hole.* A locking hole kept at its
  birth core and blended to its rectangle on the crystal alone (`pin > 0`
  skips the pull): FH enrichment 5.6 → 5.58, HW 7.34 → 7.27, `out` 4.84 →
  4.84. Nothing moved. A control skipping the pull for every hole: the same.
  In a transition a hole's birth cell is already close to its shadow cell; the
  pull moves it little. (It also wrecks the cold settle, 6 → 31 jumps, where
  birth cells are bad and the pull was correcting them.)
- *The hole cut from the ground is not the cell it replaces.* It is: 0.99 by
  area at every FH. *The pockets are re-cut at the event.* One pocket before
  and after, every time. *A wall's seed keeps bidding.* `s.claim = b.wall ? 0
  : …`. All three dead at the event frames (`atevent.js`, scratch).
- *The lock's rate.* Ramp 0.50 → 1.00 s: mean slide in event frames 6.38 →
  5.81 px (−9%), jumps 16 → 22, shock +121%, a 1,060 px² gap opens. The morph's
  speed is not what sets the slide.
- *The stagger.* 0.30 → 0.60 s per edge: jumps 16 → **54**, Hero 3 → 27, Hero
  walls 3.98 → 10.11 px mean and 15.7 → 200 px at p99, an overlap of 2,316 px².
  Spreading the departures out makes bodies travel through each other's slots
  in sequence instead of together. **A short stagger is protective.**

**What stands (`holemorph.js`):** frames with no hole, the free walls slide
**1.44 px**; frames with a hole, **9.27 px**. In the top quintile of hole
motion — 100,000 px² of hole boundary moving per frame, ~5 holes at once —
11.7 px. And holding the seeds' own travel fixed:

| seed travel (px/frame) | wall slide, no hole | wall slide, holes present |
|---|---|---|
| 0–2 | **0.85** | **4.76** |
| 2–5 | 1.64 | 4.86 |
| 10–30 | 8.91 | 10.44 |

Per pixel of seed travel: 0.74 px of wall without holes, 1.16 with. When the
seeds are fast the seeds drive the walls and the holes add a fifth — that is
the page rearranging, and it is the design. **When the seeds are still, the
walls slide 5.6× more if a hole is present anywhere in the pocket** — and that
is the complaint: a cell that is not moving, handed a new position each frame
because a neighbour is crystallising, because the auction re-partitions the
whole pocket on every change to its ground and every wall in it answers.

The strobe, then, is not a step and not a rate. It is **locality**: a change
anywhere in a pocket is paid for everywhere in it. Two designs follow, both
well posed and neither yet built:

1. **A cell that is not moving is not re-decided.** A free cell whose seed is
   still and whose neighbours' seeds are still keeps its weight; its target
   is what it holds; the cells that are moving are solved over what is left.
   Exact, watertight, converged — a power diagram with some weights held is
   still a power diagram. The still cell's walls against still cells do not
   move; its walls against moving cells move by the mover's weight alone. A
   change is absorbed by the cells around it. When the still cell next moves
   it re-enters at what it holds (the paintArea handover) and converges to
   its share while it travels — the one moment motion is expected anyway.
   This is not the refuted family: it holds a weight *whose problem has not
   changed*, not a partial step toward one that has.
2. **Right of way.** The ground gridlock (3.11) is a queue: a body's slot is
   under a body that is late, in chains. Order the departures so a body whose
   slot is wanted leaves first — the dependency graph, sorted — and the
   blocked wedges (the chewing gum) never form. The owner's original idea,
   never built.

## 4. Hypotheses, ranked, with what would confirm each

H1 **The seed fights itself.** Repulsion (`separate`) shoves a traveller off
its path, the spring pulls it back, the wobble adds noise, and the cap
clips it: four laws on one seed that disagree. Evidence: fight 22%, lag
53 px, seed reversals. Confirmed if ablating `separate` or gluing the seed to
its carrot removes most of `fight` AND most of `shapeBackShare`.

H2 **Simultaneity.** Bodies with similar percolation delays depart together
and cross; the crossings are where slivers and flips concentrate. Confirmed
if flips and slivers cluster on crossing pairs and if `stagger` 0.30 → 0.90
lowers them (at the cost of a slower change, which is a different problem).

H3 **Flips from re-decided orders.** The holes' cut order flips when two
crystals cross; pocket membership flips when a hole's shape splits and
rejoins a pocket; a newcomer enters. Each is a frame where a body's answer
changes without the world having moved. Confirmed if the `cutorder` lens
removes flips on the worst bodies.

H4 **Frame-rate dependence.** Newton iterations are per frame, the spring is
integrated explicitly with dt, `HOLE_TAU` reads `lastDt`, the linger counts
frames. Confirmed by the `timing` lens: which numbers move with dt and
jitter, and which terms cause it.

H5 **The target moves under the smoothing.** A hole follows its shadow cell
on 0.08 s; as neighbours fly the shadow cell moves and the hole trails it,
and the trail reads as recalculation. Confirmed if `holetau` 0.08 → 0.30
changes `shapeBackShare` without changing `jumps` — and refuted as a FIX by
principle (smoothing a moving target is the duck).

H6 **Nothing anticipates.** Even with H1–H5 fixed, a cell only learns a
neighbour is coming when the neighbour's seed arrives; a flock would read the
velocity and yield beforehand. Not an ablation; a design (section 6).

## 5. The instrument (mandatory before and after any change)

All scripts are in `.claude/gauntlet/`. Node: `/opt/node22`; Playwright
`/opt/node22/lib/node_modules/playwright`; Chromium
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. Temp files are named by
a hash of the hive path, so parallel runs on different copies do not collide.
Every script replaces the animation frame with a fixed-step clock, so two runs
of the same file agree frame for frame; timing fields (`ms*`) are the only
thing that varies.

    node .claude/gauntlet/flicker.js <hive.html> [out.json] [--dt 25 --jitter 12] [--dump frames.json]
    node .claude/gauntlet/score.js   <hive.html> [out.json] [--dump frames.json]
    node .claude/gauntlet/peek.js    <hive.html> <frame0> <frame1> <bodyId>
    node .claude/gauntlet/cap.js     <hive.html> <tag>          # deterministic captures at chosen scene frames
    node .claude/gauntlet/paintdet.js <hive.html> <tag>          # garment cost at the stress sliders

`flicker.js` fields: `shapeBackShare` (the share of shape motion undone within
a frame; the number for "oscillates between two points"), `flipFrames`
(body-frames where more than half of the previous frame's motion came back),
`wasteC`/`wasteA` (motion undone within 6 frames, centroid and area),
`revC`/`revA` (step reversals), `fight` (share of travelling frames the seed
moves away from its carrot), `lag` (seed to carrot, px), `sliverMean/P95`
(perimeter²/4πA of the painted shape), `pressureMean/P95` (the auction's
residual), `settle` (frames from a scene's last switch to quiet; Flock is
liquid and never settles by design), `worstBodies`.

Run BOTH clocks for any number you report: the steady 60 fps and
`--dt 25 --jitter 12`. A change that helps only at one clock is telling you
something about H4.

Hard invariants (from `score.js`): `vanish` 0; `overMax` 0; `gapMax` ≤ 8;
`settledScenes` 5/5; no page errors; `jumps` ≤ 14, `reversals` ≤ 1,
`shockPx2` ≤ 160,000 (do not give back what the last gauntlet won). And the
file's own rules: the tessellation is derived every frame from agent state,
boundaries never stored or tweened; continuity by construction, not by
budget; no rate limit that hides a moving target; exact rectangles at rest;
one auction per hive per frame at most beyond the two that exist.

Score to minimise, in this order: **`jumps` and `shockPx2` at `--dt 30`**
(the clock the owner watches, where the file scores 61 / 724,778 against
14 / 157,637 at 60 fps — closing that gap is the prize), then
`shapeBackPx2` at one fixed clock, then `fight`, then `wasteC`, then
`sliverP95`. Never compare `shapeBackShare` across clocks. Never rank on
`flipFrames` — it is chaos-noise. `lag` and `settle` are diagnostic only.
A build that lowers these by holding shapes still against a moving target
is a duck and ranks last; the refuters are told so.

Report every number at all three clocks: default (60 fps), `--dt 30`, and
`--dt 25 --jitter 12`. The 60 fps invariants (jumps ≤ 14, reversals ≤ 1,
shock ≤ 160,000) must not regress, but they are no longer the target.

## 6. The design space (for the panel; builders get one design each)

- **Right of way — givers and takers.** A rule decides who moves and who
  yields at a conflict (the larger claim, the shorter journey, the one whose
  path is crossed, the percolation order, the one already moving), and a
  yielder holds, slows, or detours until the way is clear, then goes. A
  yielder holding is NOT a duck: it holds because the world says wait, and
  its target does not move while it waits. The design must say how a
  conflict is detected before it happens (paths and timing are known at
  `enterScene`), what yielding looks like, and how the total change time is
  bounded.
- **Anticipation.** Solve the auction for where the seeds are going, not
  where they are: on the carrot, or on the seed extrapolated by its velocity
  over a short horizon, so the cell leads the seed and a neighbour's cell
  yields before contact. Bodies read neighbours' velocities (alignment). The
  picture must still be exact at rest and derived from agent state.
- **Choreography.** Assign targets to minimise path crossings, bend the
  bezier control points so paths do not cross, depart in waves, or let the
  percolation order carry more meaning. The fight is avoided by never asking
  two bodies for the same place at the same time.
- **One motion law.** Replace the disagreeing laws on a travelling seed with
  one: a critically damped follow, repulsion folded into the path (or
  dropped — cells cannot overlap anyway, the auction guarantees that), the
  wobble only at rest. The seed never fights itself.
- **Hysteresis for every re-decided order.** The cut order when crystals
  cross, pocket membership, the newcomer entry: a body changes its answer
  only when the world has moved past a margin, not when it wobbled across a
  threshold.

Designs may combine. Every design must say which flicker numbers it should
move, what it costs per frame, and why it reads as a flock rather than as
collision resolution.

## 7. How the workflow runs (operator notes)

    Workflow({ name: 'vibe', args: { mode: 'full', build: 3 } })

`mode: 'diagnose'` runs the ten ablation lenses and stops; `'design'` adds
the panel and the judges; `'full'` builds the top `build` designs in
worktrees, refutes each, scores each, and returns one table. Phases are
independent enough that the operator should read the diagnosis before
letting the panel run: `resumeFromRunId` replays cached agents, so running
`diagnose` first, then `full`, costs nothing extra.

Agents write into `/tmp/claude-0/-home-user-Voronoi/75dbc440-48ad-59c3-a8c5-dea8806ca42b/scratchpad/vibe/`
(ablation copies as `abl-<lens>/hive.html`, builds as `build-N.patch` and
`build-N.md`); builders work in git worktrees under `.claude/worktrees/` and
do not commit. The operator verifies the winner by running both scorers on
its worktree file, reads its patch, looks at captures, then ships it as its
own PR on `claude/have-a-look-kcycaj` (one change per PR; restart the branch
from `origin/main` after a merge; commit trailers as in the repo's recent
history; never a model name in any file), with a SEED.md exhibit written in
the file's voice.

What the last gauntlets taught about running one: verify every reported
number yourself (the harness is deterministic, so a mismatch is a lie or a
different file); read the patch before the numbers; a variant that "fixes" a
symptom by freezing something will score well and be wrong; the brief is
sometimes wrong and the agents will say so — listen.
