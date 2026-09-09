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
