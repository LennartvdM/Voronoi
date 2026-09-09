# SEED

**You are about to build the kernel of a UI language in which the elements of a website are free-moving cells with a hive intelligence.** This document is its founding brief.

## What this document is

Its writer, a prior session, had everything you do not: this repository, instrumented headless runs of every experiment, an adversarially verified review of those runs, long collaboration with the owner. You arrive with zero context; the brief is self-sufficient. Read it end to end before opening any file here. The mathematics section is precise enough to implement from; the appendix is a validated reference solver whose behavior is ground truth. The owner has not read it and does not need to — it is addressed to you.

**One rule governs everything: the FIXED list in the freedom ledger binds; every other sentence is advice, discardable the moment it fights you.**

# The dream

Picture a page with nothing asked of it. Thirty cells drift across the canvas like a school of fish — loose, curious, tessellated edge to edge, no gaps, no overlaps, the whole surface alive. Then a scene arrives: *navigation wants the top strip, the hero wants a third of everything, three cards want equal shares on the right, whitespace wants to pool at the margins.* Nothing teleports. The cells swim to their stations, trading territory as they go, and a layout condenses out of the flock like a crystal out of solution. Grab any cell and drag it — every neighbor renegotiates in real time, area conserved, junctions clean, the picture never tearing. Let go, and the scene reasserts itself like water finding level.

That is the language: not a layout engine with animations bolted on — elements as agents, layout a continuously re-derived consequence of what they currently want.

## The one verb

The entire grammar collapses to a single verb: **an agent changes its claim.**

- A *layout* is a **scene** — a named set of claims (area, region, adjacency).
- *Hover* is a temporary area claim: the hovered cell claims more, everyone yields; released on exit.
- *Insertion* is a new agent claiming its way in; the field makes room.
- *Removal* is a claim released; the field closes over the wound.
- A *transition* is one scene's claims swapping for another's; the field re-equilibrates.

Only **area claims** reach the solver — where the theorem lives; region and adjacency claims are steering goals, met by where agents put their seeds — the solve never sees them. A scene is concretely a claim table — *nav: 8%, top strip; hero: 33%; cards: 12% each, right; void: the rest, margins* — schema yours. Which agent takes which slot is morph's assignment problem — optimal assignment (minimize total squared travel) is affordable here; the policy is OPEN.

One mechanism, arbitrarily composed — the tessellation valid at every instant, **by theorem, not by hope**. Before adding a second mechanism, ask whether it is a claim in disguise; it almost always is.

# The wall

Eight experiments bought one theorem — an impossible triangle at the heart of the dream.

1. **Watertight tiling** — no gaps, no overlaps, ever.
2. **Shape sovereignty** — each cell owns its boundary geometry as intrinsic state.
3. **Free continuous motion** — cells go where they like, and their neighbors change.

Pick two.

A watertight tessellation is secretly **one global object**. Give every seed a potential — distance-squared-minus-weight — and take, at every point, the minimum over seeds. That single function's *lower envelope* IS the tessellation: a cell is where one seed's potential is lowest, an edge where two tie, a junction where three tie. Junctions agree — three edges meeting perfectly, everywhere, always — not because anything enforces it, but because all boundaries are level structure of the *same* function. Agreement is free. It cannot fail.

Store the boundary as n sovereign objects instead — each cell carrying its own curve, as mk5/mk6 did — and every triple junction demands three *independently owned* curves through one common point: a codimension-2 constraint per junction, on state nothing couples. Generically there is **no solution** — the target your local forces chase does not exist. So the forces oscillate; you add snapping, impasse detection, confidence thresholds — line for line, the mk5/mk6 log, which is not a record of bugs but the experimental confirmation: **boundaries owned per cell cannot close a tessellation.**

One road stores geometry and stays watertight: each junction stored *once*, shared by its three cells — the vertex-mesh of epithelial modeling. Nothing disagrees because nothing is duplicated; sovereignty has left the cells for shared structure. The price comes due at neighbor change: detect the collapsing edge, cut, re-tie — discrete surgery at the exact moments this language cares most about, mk5/mk6's snapping made systematic (mk4 is this road minus the surgery: watertight and dead). Biology models packed tissue both ways, vertex meshes and power diagrams of cell centers; this design takes the second — the derived field crosses every neighbor change smoothly, nothing to detect, nothing to sew.

## The corner you surrender

Keep watertightness and free motion; give up *instantaneous* shape insistence while packed: a packed cell does not hold its own outline against its neighbors moment to moment. Softness survives, mk7 proved it — a rest shape relaxed toward **when unpacked**, blended per edge: a memory the cell returns to, not a right exercised while packed. The open bet, for the owner's eye: cells wearing the collective equilibrium read as alive as softbody's free ones.

# The exhibits

Read the repository as a geologist reads a cliff face: nine HTML files — index.html the gallery, eight strata. (ARCHITECTURE.md is a fossil from two experiments in; this brief supersedes it.) Every number came from instrumented headless runs, adversarially re-verified (140 findings survived); causes confirmed in source; one-shot or randomized figures marked.

**voronoi.html: the diagram breathes.** Voronoi recomputed from moving seeds every frame; hover displaces seeds and the picture re-forms — nothing stored, nothing can tear. **STAMP: PROVED CHEAP AND CONTINUOUS.**

**softbody.html: the feel without the tiling.** Membrane cells, pressure, contact, no Voronoi. Each cell owns its shape — the most *alive* thing here: squish, resist, breathe. And never tessellates: gaps everywhere, always. **STAMP: PROVED THE TARGET SENSATION / NEVER TILES.** It defines what the garment must feel like, never how it is built.

**morph.html: layouts are seed configurations.** Named layouts as seed configs; transitions interpolate seeds, tiling valid mid-flight. **STAMP: KEEPER — scenes as claims.** It also exposed what "rearrange" hides: identity must persist, and which-cell-takes-which-slot — assignment — is a real problem.

**mk4.html: frozen topology.** Frozen half-edge topology, interpolated vertices: watertight — and dead; neighbors never change, nothing can pass, join, leave, or be born. **STAMP: PROVED FROZEN TOPOLOGY KILLS THE LIFE.**

**mk5.html / mk6.html (Voroboids): sovereignty tries to close the tiling.** The central negative result: every cell owns its boundary polygon and force systems try to make n sovereign boundaries agree. The commit log is the fossil record; the escalation, excerpted in order:

- `mk5: temporal smoothing on rest poly to eliminate shape flicker`
- `mk5: hard minimum size floor — cells refuse to become tiny`
- `mk5: close gaps — dynamic fill fraction + remove area cap`
- `mk5: northstar system — shared triple-point vertices`
- `mk5: dual northstar system — targets (should) + clusters (is) + force`
- `mk5: analyst overhaul — uncapped triple pull, wider clustering, confidence snap`
- `mk6: impasse detection — inject corners where edges converge`
- `mk6: max reach constraint — no more starburst spikes`

Each subject patches the previous patch — a local scheme chasing a target that does not exist. **STAMP: PROVED IMPOSSIBLE — per-cell-owned boundaries cannot close a tessellation.** Not an engineering shortfall to retry with better forces — the repository's most valuable possession.

**mk7.html: softness as a garment.** Edge-first: blend each boundary stretch between the Voronoi scaffold and the cell's rest shape, weighted by **engagement** — how contested the stretch is: 1 where a neighbor presses, 0 where the cell has slack. Packed, the scaffold wins; free, the rest shape breathes back. **STAMP: KEEPER — the rest-shape garment.**

**mk8.html: the merge, and the measured cost of ad-hoc math.** voronoi.html × morph's transitions, power-diagram weights for size, voids as first-class cells for whitespace. The voids idea is right; the tuned math fails measurably:

- The "1200 ms" transition takes 10.3 s, declared done at 1.46 s (recorded run: one seed still 634 px from home, coverage down to 11.2% mid-flight) — drift under 1 px only past 10 s. Cause: three time conventions in one method — dt as frames, as milliseconds, and absent.
- Hover lights the wrong cell: hit-testing used a different tessellation than rendering; under a settled hover **51% of the hovered cell's own drawn area** reports as another cell's.
- A weight constant is a land grab. mk8 maps weight w to power scale·w², scale = canvas area / (4·cell count); the bisector erases the lighter cell inside √scale·√(w₁²−w₂²) — at the default 13 cells, ~314 px for a 2.3 hero against a 0.7 neighbor, beyond the 287 px mean seed spacing, and ~492 px for the hand-set 3.5 void, which holds **79.8% of the canvas** at five content cells (sidebar layout; 84.3% at four). Weights mean nothing a designer can reason about; areas do.
- The repair loop never converges: `enforceMinAreas` ships non-converged geometry on most busy frames — **86% at 30 content cells** in the verified record — deficit oscillating (0.70 → 1.00 → 0.64 → 1.00…), never closing.
- And yet, headroom: the geometry pipeline is sub-millisecond at 31 agents, the slider's 30 content cells plus the void (computeBaseVoronoi 0.421 ms, updateDisplayPolygons 0.153 ms); median frame 16.7 ms, vsync-bound. Choose exactness wherever the math allows.

**STAMPS: voids KEEPER; tuned weights LETHAL.** Everything mk8 tunes, the concave dual below does by theorem.

**Exhibits, not foundations.** Study them for what is proven cheap, alive, impossible, lethal — then build from the theorems, not the code: no ported structures, extended force systems, or inherited constants; the owner asked for this severance. Trust the verdicts — every load-bearing one is re-derivable from the mathematics section — the implementations not at all.

# The resolution

The fix is not a better force law but a relocation of sovereignty.

In a real hive no individual carries a piece of the shared structure: an ant owns its motion and intent; the trail network is common property, produced by all, owned by none. (An ownership analogy, not a mechanism — real pheromone persists as world-state; this field is purer, re-derived every frame, no trace kept.)

The move:

- **Agents own position, area claim, and intent.** The hive layer, sovereign: identity, steering, goals, personality. The math never touches it.
- **The tessellation is the pheromone field.** Recomputed from agent state every frame, watertight by construction — the lower envelope of one function. Never stored, interpolated, or owned: no state to drift, tear, or disagree with itself.
- **Shape is worn, not owned.** Rounding, insets, rest-shape blends — applied *after* the solve, never fed back, kept inside the solved polygon so eye and hit-test cannot disagree.

A three-layer decomposition falls out — a recommendation, not law: **agents** (steering, claims, scene interpretation — the personality knobs), **solve** (seeds and claims in, exact watertight tessellation out — sealed, nothing aesthetic inside), **garment** (solved polygons dressed for display — the visual knobs). Two further rules, bought by mk8's failures, are FIXED: one authoritative tessellation per frame, one time convention. At validated scale performance is not a design constraint — mk8's geometry never threatened the frame budget; do the exact thing every frame.

# The mathematics of the field

One rule generates the field, one theorem guarantees every claim, one solver finds the weights, sub-millisecond — all implemented and measured first; the appendix is the source of every number.

## The bidding rule

Give every agent i a position `s_i` (its seed, px) and one scalar `w_i` (its weight, px²). For every point x of the canvas, agent i bids

```
bid_i(x) = |x − s_i|² − w_i
```

— distance squared, minus weight. Every point goes to the lowest bidder; agent i's cell is where it wins. That sentence is the entire tessellation: the *power diagram* of the seeds and weights. Three consequences, each a job the mk-series lost:

- **Watertight by construction, always.** Every point has a lowest bidder, so the cells cover the canvas exactly — for any weights, converged or not. Measured: total cell area within 1e−9 px² of canvas area in every test, including garbage random weights leaving six cells empty (defect 2.3e−10 px²). Watertightness never depends on the solver.
- **Straight edges, free junctions.** An edge is where two bids tie; a triple junction where three tie. Junctions agree because all boundaries fall out of the one function `min_i bid_i(x)` — the codimension-2 agreement sovereignty could not buy.
- **One smooth function.** Bids vary smoothly with positions and weights, so cells deform continuously; motion cannot tear the picture. Measured, 1 px steps with weights frozen: max area change 965 px² (0.09% of a 1440×743 canvas), median 909, max within 7% of median — uniform, no pops (one layout's absolutes; the uniformity is the finding).

Raising `w_i` pushes agent i's boundaries outward: weight turns claim into area. Only differences matter (adding 12345.678 to every weight moved areas ≤ 3.5e−10 px²); equal weights give plain Voronoi; expect large negative values (the hero-and-void scene spanned [−250361, +111645] px²; normal). Hit-testing is the bid run backward: a point's owner is its lowest bidder — one O(n) scan, no geometry, by definition the tessellation the frame renders.

## Claims are honored exactly

**Theorem (Aurenhammer's Minkowski-type theorem; equivalently semi-discrete optimal transport with quadratic cost).** For any distinct seed positions and any positive target areas summing to the domain's area, weights exist whose power diagram gives every cell exactly its target area — unique up to the shared constant.

*Any* distinct positions, *any* positive claims: agents move however they like; the honoring weights always exist. Annihilation is impossible — a positive claim buys a nonempty cell, every time. A void is an agent with a declared claim and no ink; magic constants and repair loops retire.

## Why the auction always clears

The weights are found by maximizing one function of all the weights,

```
Φ(w) = Σ_i target_i · w_i  +  ∫_canvas min_i bid_i(x) dx
```

At each fixed x the winning bid is a minimum of straight lines in w; minima of lines, summed and integrated, stay concave — so Φ is concave: one summit, no false peaks, any uphill walk arrives. The slope along `w_i` is `target_i − area_i(w)`, the area still owed, so the summit is where every claim is met. Raise the underclaimed, lower the overweight — the auction cannot circle; damped Newton arrives in a handful of steps.

## The solver, as validated

Per solve: the domain, one **convex** polygon — load-bearing: step 4's connectivity and step 1's clipping assume it, all validation ran on rectangles, and non-convex probes produced degenerate cell rings and slow convergence (out of contract; mask in the garment). Seeds distinct and strictly inside. Targets positive in any units, rescaled internally to sum to the measured domain area — a raise taxes the rest pro rata; callers never balance a budget; caller drift cannot make it infeasible. Starting weights: the previous frame's, else all zeros = Voronoi. Each iteration:

1. **Diagram.** Cell i is the domain polygon clipped (Sutherland–Hodgman) by the n−1 half-planes `x · (s_j − s_i) ≤ (pot_j − pot_i)/2`, `pot_k = |s_k|² − w_k`; label each edge with its neighbor (negative ids for walls); areas by shoelace. O(n²), no geometry library — any correct construction serves.
2. **Residual.** `g_i = target_i − area_i`. Converged when `max_i |g_i| / target_i ≤ 1e−6`.
3. **Jacobian.** `A = ∂(areas)/∂(weights)` is a weighted graph Laplacian read off the diagram: for each shared edge, `A_ij = −L_ij / (2 d_ij)` and `A_ii = +Σ_j L_ij / (2 d_ij)`, with `L_ij` the shared edge length, `d_ij = |s_i − s_j|`. Signs as implemented — your own raise grows you, a neighbor's shrinks you — verified against central finite differences: max relative deviation 1.5e−9. (The dual's Hessian is −A — `H·dw = −g` equals `A·dw = g`; pick one convention and finite-difference it: the classic sign-flip trap.)
4. **Step.** Solve `A·dw = g` with one weight pinned to zero: the shared constant makes A singular by exactly one dimension; while every cell has positive area the adjacency graph is connected and the pinned system nonsingular. Gaussian elimination with partial pivoting suffices at n ≤ 64.
5. **Damped acceptance.** Try `t = 1, 1/2, 1/4, …`; accept `w + t·dw` at the first t satisfying **both** (i) every cell's area stays ≥ `eps0 = 0.5 · min(smallest target, smallest starting area)`, fixed once per solve, and (ii) `‖g(w + t·dw)‖₂ ≤ (1 − t/2) · ‖g(w)‖₂`. This is Kitagawa–Mérigot–Thibert damping, under which convergence is a theorem: global, quadratic near the summit.

**Corrections from validation — the standard statement omits them; working code cannot:**

- **The area floor is relative to the start, not just the targets.** Rejecting steps below half the smallest *target* deadlocks whenever the starting diagram already has a smaller cell (a cold start in a crowd, a warm start mid-squeeze): every step is rejected, fixes included — hence the floor above.
- **The floor alone does not force progress.** Without test (ii), acceptance admits steps that wander at constant error; both tests together are the theorem's hypothesis. Backtracking engages — the validated hero/void cold start spent 8 diagram evaluations on 5 iterations (which starts backtrack varies by layout; the need for (ii) does not).
- **Warm starts can be stale.** A big enough one-frame teleport leaves the old weight an empty cell — zero Jacobian row, no Newton step; on any zero starting area, restart from all-zero weights (Voronoi — every interior seed gets a nonempty cell). Validated: the lightest of 31 agents teleported to 3 px from the heaviest — old cell 0.00 px², reset, converged in 6 iterations.

If a solve fails to converge (none did, in any test), the diagram is still watertight — only areas drift: render it, keep moving, re-solve next frame; the solver enforces claims, it never keeps the tiling closed.

The recipe is validated, not sacred: tol 1e−6, the ½ in eps0, the 40-step halving, pin-last, mean-centering, direct elimination are implementation choices — none aesthetic, all swappable wherever the acceptance tests pass.

## Preconditions and degenerate cases

Four preconditions, guaranteed by the agent layer every frame: seeds pairwise **distinct** (epsilon-separate on contact), **strictly inside** the domain (clamp inward; inset OPEN), domain **convex**, claims **positive**. Only the claim check throws; geometry fails *silently* — coincident seeds produce overlapping duplicate cells, no exception — so enforce upstream, not in the solver. 2 px separation is already comfortable: the pair row split 3:1 exactly (160488.0 / 53496.0 px²) in 5 iterations, one seed left outside its own cell, harmlessly.

- **A crowded cell may not contain its own seed** — legal, stable. Anchor content and pointer semantics to the polygon, never the seed — anything tied to a seed can exit its cell too.
- **Insertion and removal live inside the same math.** Enter with a small positive claim at weight 0 — any value is safe (zero-area entry triggers the Voronoi reset); the entry frame solves near-cold, ~5 iterations, sub-frame. Leave by ramping the claim to a small floor, then deleting; zero never reaches the solve.
- **Zero-length edges and on-line vertices are harmless** — zero length, zero area — and the flip that turns neighbors into strangers passes through them continuously.

## The 60fps path

Keep each agent's weight across frames and re-solve from it. Motion and claim changes are the same perturbation, and solved weights vary smoothly with both, so warm starts stay in Newton's quadratic zone:

- **Motion:** per-frame moves re-solve in 2 iterations (the warm rows); faster degrades gracefully — 20 px: 3; 60 px: 4; 150 px: 5.
- **Claims:** a hover eased 4.5% → 9% over 20 frames held 2 iterations per frame, worst error 6.8e−8; the same doubling in one frame took 3.

Measured (Node 22, one core, the appendix code, zero optimization): medians over 100–200 solves, except the portrait row's single-run time. Layouts unstated: treat digits as an envelope — reruns land within ±1 iteration, same order of time.

| scenario | n | start | iterations | max \|area err\|/target | solve time |
|---|---|---|---|---|---|
| hero 25% + void 30% + ten 4.5%, 1440×743 | 12 | cold (Voronoi) | 5 | 9.3e−8 | 0.46 ms |
| claims ramped 1..50 (50:1 extremes) | 31 | cold | 6 | 2.6e−11 | 1.29 ms |
| same claims, portrait 743×1440 | 12 | cold | 5 | 1.3e−12 | 0.59 ms |
| pair 2px apart claiming 15% / 5% | 12 | cold | 5 | 7.7e−11 | 0.29 ms |
| one seed moved 5px | 12 | warm | 2 | 3.5e−8 | 0.14 ms |
| one seed moved 5px | 31 | warm | 2 | 5.1e−10 | 0.47 ms |
| random claims 1–2× | 64 | cold | 4 | 1.5e−7 | 2.80 ms |
| one seed moved 5px | 64 | warm | 2 | ≤1e−6 (tol) | 1.74 ms |

Diagram-only (the render path when nothing re-solves): 0.071 ms at n = 31, 0.334 at 64.

# Invariants and acceptance tests

Correctness here is *seen*: the owner verifies with eyes, and no eye reads 1e−6 — the meters turn theorems into something an eye can watch holding.

**One authoritative tessellation per frame.** The solver's accepted output is the frame's single truth — rendering, hit-testing, meters all read it; a pixel's owner is its lowest bidder there, styled gaps included. Forbidden: a second tessellation for a different consumer — mk8 hit-tested one and drew another; the 51% hover was the price. Not forbidden: the solver's internal trials, or rasterizing these polygons for meters.

**One time convention.** Durations and rates in seconds; `dt` in seconds at every integration site. Absolute-clock scheduling is fine — mk8's one correct timing path used it; the sin was three dt units in one method.

**The meter row**: four numbers, on-screen in every development and acceptance build (shipped surfaces may fold them behind a toggle; they must exist):

- *max area error %*: worst `|target − area| / target`. Below 1e−4% when converged.
- *gap px²*, *overlap px²*: rasterize the frame's polygons offscreen counting coverage per pixel — 0 is gap, 2+ overlap (a last-writer index buffer misses the second write). Both sit at antialiasing noise every frame, mid-drag and mid-transition; the analytic twin — tiling defect `|Σ areas − domain area|` < 1e−6 px² — comes free.
- *solver iterations*: ≤ 3 warm at ordinary motion, ~5 under violent drags (measured), ≤ 10 cold. Sustained breach at gentle motion means colliding seeds or degenerate claims — upstream bugs, never the math.

**The continuity test.** Sweep one seed 1 px per step, 30 warm re-solves: 2 iterations at every step, worst error 7.8e−11, no visible pop — neighbor swaps must be invisible; any discontinuity is your geometry code, not the field.

**The performance contract.** Validated to **n = 64 agents on one core**, past the dream's thirty; larger casts are new territory — the O(n²) diagram and O(n³) step expire, the theorems scale (sparse Laplacian, prunable geometry), the contract must be re-earned. Within scale the table is a floor with an order-of-magnitude margin (a warm solve at 31 agents ≈ 3% of a 60fps frame); if exact per-frame solves are unaffordable, the implementation regressed, not the mathematics.

# Irreducible tradeoffs

Three tensions do not dissolve with cleverness; decide them consciously or they decide themselves badly.

**1. No instantaneous shape insistence while packed.** Surrendered at the wall. The licensed outlet for softness is the rest-shape garment — mk7's exhibit, restated so nothing need be inherited: each cell remembers a rest shape; draw the scaffold where engagement is high, relax toward the rest shape where it drops, always inside the solved polygon. Direction fixed — softness worn over the derived field, never enforced against it; measure and blend OPEN. The menu is short: fight the impossibility (mk5/mk6 show the ending) or accept the trade packed tissue accepts. Accept it.

**2. Rectilinearity versus motion.** Moving point seeds under a quadratic metric give sloped convex edges — never true bento rectangles. The menu: (a) change the metric — L-infinity or anisotropic costs tend axis-aligned; the dual stays concave, but straight edges, cell convexity, the Laplacian Hessian, and the damped-Newton theorem all go, the solver re-earned on harder ground; (b) a rest-state relaxation easing settled cells toward per-cell rectangles, gated by motion so movement melts them back — rectilinearity as garment behavior on stillness, the sealed solver untouched; (c) embrace the organic look as the language's identity. The departing session read the owner as leaning (c), (b) the pragmatic middle — an identity call in the owner's jurisdiction: decide with them, by looking.

**3. Content inside deforming cells.** A continuously re-shaping polygon needs its own anchoring. Centroid anchoring jitters and escapes concave garment shapes; the seed is unsafe (it can exit its cell). Recommended: the *inscribed pole* (center of the largest inscribed circle — the natural visual center); size content to that circle; smooth it separately, calmer than its cell; bind the pointer likewise — a drag grabs the hit-tested cell's agent and moves its seed. Beyond that — clip, scale, or fade — settle by looking, with the owner.

**4. Rigid perimeter, organic interior.** The owner will ask for it: a rectangle with exact edges holding cells that are Voronoi inside and squished flat against the border — a gallery section on a bento page. It is not one diagram, and no weight, metric, or image trick makes it one. *The straight-edge lemma:* every edge of a power diagram is perpendicular to the segment joining its two seeds. Let a straight line carry the boundary, cell *i* (inside) meeting cell *j* (outside) along one stretch and cell *i′* meeting the same *j* along the next. Then s_i and s_i′ both lie on the perpendicular to the line through s_j, so their own bisector is parallel to the line — and it passes through the vertex where *i* hands over to *i′*, which lies ON the line. The bisector of *i* and *i′* is the line itself; both cannot be inside. Hence along any straight boundary the cells pair off one-to-one across it: every handover on one side is a handover on the other, every vertex on the line a four-way junction, every seed pair mirror-aligned with equal bids on the line. The inside dictates the outside. A lattice satisfies this everywhere (that is why equal weights on a grid are exact rectangles); an organic interior satisfies it only if the exterior is its reflection — image seeds, cell for cell, in a gutter as deep as the boundary cells. Against a locked neighbour, the interior's boundary cells would each have to be one lattice slot tall: a skin, not a tessellation.

The resolution is the box model. Clipping a diagram to the rectangle gives exactly the diagram of the seeds plus their reflections, restricted to the rectangle (a reflected seed never wins on its own side of the mirror), so the rigid perimeter is not enforced on the cells: it is the domain of a second auction. A cell that holds cells is a hive — the same kernel one level down, its domain the cell it lives in, content box inside padding inside border. The page's tessellation is settled before any field reads it; nothing flows back up. "Rigid outside, organic inside" is then not a mode but numbers: the page's bodies at crystal 1 and the field's at 0. All at 1 is a nested grid; all at 0 is organic all the way down.

"One authoritative tessellation per frame" survives, refined: one per hive, and the frame's picture is the tree's leaves — each level its own solve, hit-test, meters. The inner domain is whatever shape the cell has this frame, non-convex included: the theorem integrates a lower envelope over any region, only the clipper wanted convexity, and a clipper that cuts each cell by a triangulation of the domain removes that (areas exact, Jacobian from the pieces' shared edges). A travelling blob's interior tiles it exactly; a grid inside stretches to the box and is clipped, since rectangles cannot follow a curve.

**The voronoi conquers the rectangle.** The owner's picture: a hovered member breaks through its field's edge into the neighbouring card, and the card's straight edge is cut around the shard. Do not model this as negotiation. Letting the member bid in the page's auction is exact, honest, and wrong: Newton makes both sides settle, so the neighbour's lattice seeds recover their lost area as steps along every other edge and the intrusion leaks across the page as jitter. There are no two sides here. The shard is its own ruleset, and it grows from the corners where the member's cell meets the field's edge — only from there. Its side walls are the member's own sibling bisectors continued straight through the edge (its own auction's weights, so it is one cell with its inner part); its front is the neighbours' bisectors at their frozen weights — true Voronoi facets, nobody bidding back — set so the member holds the whole band half a depth out from its contact, and bounded by the depth itself, the field's rectangle pushed out by h. The bound must never be the whole front: a shard that is only the rectangle pushed out reads as a rectangle, parallel edge and square corners, and the owner will see it at once. Nothing may cut across the attachment: a member that touches the edge encroaches along its whole contact, never bursts out of part of it (a tie rule that let the member win only where its bid beat the page produced exactly that pimple). A few vertices, no solve. The rectangle yields by difference and never pushes back: its claim stays exact in the auction underneath, and the carved area is metered rather than hidden. Zero pressure, zero depth, zero shard: rest is untouched. The lemma is obeyed, not violated: the straight edge is straight exactly where nothing organic touches it.

**One picture, one gap.** The garment is one routine over one flat list. Every frame the tree's leaves are gathered — every cell that is not a field, as convex pieces in page coordinates with the chain of bodies it belongs to; a field contributes no ink of its own, its members are the leaves and their aligned outer edges are its rectangle. Shards are geometry in that list: the member's polygon grows by its shard, every polygon the shard lies over is cut by it (the stronger of two shards keeps their overlap), each leaf is chained into its outline, and every outline is dressed identically — inset by half the gap, rounded, filled, stroked, numbered. There is one gap width, dialled once; nothing is masked, tinted, padded, or erased; a member meets the card across the field's edge exactly as two cards meet. Hit-testing and the gap and overlap meters read the same leaves, so the picture — shards, notches and all — is what is checked for watertightness, not the auction underneath.

The tessellation ledger reads, refined: the auction's result, then the shards carved from it, then the one flat picture — all derived every frame from agent state, read alike by render, hit-test and meters.

**Nothing appears; everything grows.** Measured on the owner's own test — the five scenes in a cycle, the total area every visible cell changes between consecutive frames — the shocks were never the cell count. They were instant changes of the seed set or of a formation where a claim should have grown from the floor: whole fields dropped in one frame, seventy lattice seeds crossing the entry gate together, a formation swapped for the next scene's while its seeds were still spread, a melt of four frames. Three rules remove them. A field splits and merges through its SELF: the field's own card is a member of its own hive, holding whatever the members do not yet hold, so members bud out of it and retire back into it, and the hive dissolves when only the self is left — the outer cell never moves. The crystal moves seeds, never claims: a lattice seed is out of the auction until the crystal has carried it 25 px from its core, then holds an equal share of its body until it leaves the same way, the core holding the shares of everyone not in; claims that shrank with the crystal asked Newton to shrink seventy cells three-hundredfold in ten frames, and it lagged, then jolted. And a seed entering or leaving carries a warm weight computed from what it joins or leaves — a lattice seed a little under its core's, a core taking back its seeds the weight that keeps their edges where last frame's diagram had them, anyone else a sliver a few px wide beside its nearest neighbour — because a seed that enters with a stale weight grabs a slot and the solver spends frames taking it back. The formation swap waits for crystal zero. Whitespace dissolves at the pace the cells move. The worst frame on the cycle fell from 1,440,000 px² to 150,000, and that one is six fields budding their members.

**Content is lazy.** A label can float anywhere in its cell and never look wrong, so it does not read the tessellation every frame: it samples its target — the cell's inscribed pole — a few times a second or when the cell has clearly changed, keeps the target it has unless a new one is clearly better, and drifts toward it on a slow critically damped spring, in the cell's own frame so a travelling cell carries it, its size on the same slow clock in 2 px steps. The cells themselves cannot be lazy: everything reads them. The labels were what was sweating.

**No clock of the whole.** With the shocks gone the owner could still tell the stages apart — a melt, a journey, a wait, a lock — because the crystal was one number per hive: every rectangle softened together before anything moved, the early arrivals sat as blobs until the slowest landed, then the whole page locked at once. The rule that removes the stages is that a change reaches the cells by percolation. A scene is spoken once; it enters at a source — the cell under the pointer, else the cell changing most, plus every new element and every patch of whitespace about to open — and crosses the tessellation's shared edges, each edge open after its own random while: first-passage percolation on the adjacency graph, the stagger slider its mean edge time, slower across a corner than a shared side, a rough front that overtakes itself, shaped by position and by nothing else. Each body then does everything on its own clock: it melts over 0.30 s from wherever it was, travels liquid, and locks over the last 0.35 s of its journey and 0.15 s after, the lock part of its crystal pinning it to its slot every frame so there is no snap. A body already sitting where the scene puts it never melts; it conducts the change, and its edges toward a melting neighbour go organic by the diagram alone. A field re-rosters when the change reaches it, and its members bud and retire on the same rule one level down, sourced at the facet the change came through. A void keeps a ledger: it opens at the claim-weighted pace of the bodies leaving it and crystallises only when the last of them is all but gone; it closes at the pace of the bodies landing in it. A cell born inside another is a hole in that leaf, drawn even-odd with the one gap around it. Nothing reads a crystal of the hive; the two readings a hive keeps of its bodies' — liquid throughout, locked throughout — gate only the domain polygon, the shards and the meters, and at rest every body is at crystal 1, so the lattice gives the exact grid as before. Measured on the cycle, the worst frames fell to 60,000–80,000 px² and the totals to the baseline's or below, the activity spread over the whole transition instead of three moments of it.

**A settled cell is a wall, not a bid.** The stages gone, what was left to see was the cells' own bones: a cell mid-transition broke into ten or twelve edge fragments where it has five neighbours — the "ripple". It was never a chosen look and never a solver convenience; it is what the straight-edge lemma costs when a LATTICE meets something that is not one. A power cell carries one facet per neighbouring seed, a body is the union of its seeds' cells, and a rectangle made of one seed per grid SLOT shows a three-slot side facing one neighbour as three facets. Pairing the slots across the edge does not fix it (measured: the same ten, and the solver lagging in five times as many frames), because any interpolation of a lattice is a lattice meeting a non-lattice somewhere.

The resolution is the box model again, turned on the page itself. A cell that has settled is not bidding for anything: its rectangle is CUT OUT of the auction's domain and it is drawn as exactly that rectangle — a wall. Exact rectangles at rest are then true by construction rather than by convergence, and a page at rest solves nothing at all. The auction runs on what is left, among the cells still moving, and every body is ONE seed for its whole life: its cell shows one edge per moving neighbour and the walls' own straight lines everywhere else. A cell has as many sides as it has neighbours, at every instant. The lattice, the formation, the entry gate are gone.

Four things make it hold. The domain is a set of convex pieces, not one polygon, so "the page less the walls" needs no ear clipping and no slits — one vertical sweep into axis-aligned rectangles (measured on the sealed solver: four iterations, worst relative area error 1.7e-8, coverage exact). A seed entering the auction takes the weight at which its cell is exactly the size it claims, found by bisection on that one weight, so a cell that was a wall comes back its own size in its first frame instead of growing from a speck. A cell may become a wall as soon as it ALREADY is one — a body landing among settled neighbours is bounded by their edges, so the auction has already made its cell its rectangle and the switch costs nothing; the test is the symmetric difference. And a wall stands where the body is, not where it is going: it melts where it stands before it travels.

The recursion is unchanged, one level down: a field whose members have all settled has no auction either, and its walls are its picture. Hover still carves at rest, its front built from the walls around a field, each standing at the centre of its own rectangle. Measured on the cycle against the lattice build: edges per neighbour mid-transition 2.04 to 1.35, outline vertices at the ninetieth percentile 16 to 7, the worst frame's summed area change 89,000 to 46,000 px², frames with solver error over 1% 69 to 22, the worst frame's solve 16.2 ms to 4.8 ms, gap and overlap zero throughout.

**Rounding is an opening, not a budget.** A hover sandwich at a wide gap with big corners showed corners scooped inward and corners gone sharp, worst where a cell sat between one neighbour still shrinking and another just expanded. Both came from the garment. It inset a cell by offsetting every edge and intersecting neighbours, and a side shorter than the inset — a power diagram makes them constantly, wherever two neighbours nearly meet — turned inside out, so the rounding drew a bow-tie: the "negative" corner. And it budgeted each corner's radius by half its adjacent sides, so a side shrinking to nothing took the rounding at both its ends to zero and then, the moment the side vanished, handed the single corner the full radius. Measured in a sandwich run at gap 28 and radius 34: 454 of 12,000 painted outlines crossed themselves, in one frame of four.

The garment is now a morphological OPENING. Erode the cell by the gap plus the radius — for a convex cell exactly the intersection of its edges' offset half-planes, so a short side vanishes instead of crossing; a notched cell takes the exact cut, a strip about every edge and a disc about every reflex vertex taken out of its triangles (a mitered offset with collapsed features dropped was tried first, with checks for a crossing or a vertex outside the cell: it passed them and was still wrong two times in five, a diagonal half of the cell or a sliver of it, and which frames it passed flickered — a strobe under every hover) — then dilate the core by the radius with round joins. Every convex corner is an arc of exactly the radius; a side too short for two arcs makes its two corners one, continuously; the ink never leaves the eroded cell, so the gap holds along every straight side. Where a cell is too thin to afford it, the radius gives way first, down to four pixels, and then the gap, found by bisection on one test: the erosion by gap plus R is non-empty exactly when the ink can hold a disc of radius R. Both concessions are continuous in the cell's shape, so nothing snaps. Measured: crossed outlines 454 to 0, the radius never reduced in the same run, paint cost unchanged at a millisecond a frame.

And a fit is ONE core. A cell dented to less than twice the gap plus the radius — a narrow column bitten by a hovered neighbour, a strip of a cell mid-transition — erodes into two pieces, and two pieces dilated back overlap where they meet: a waist at best, and under an even-odd fill the overlap painted as a round hole in the cell, a corner gone convex the wrong way. So a split counts as not fitting, and the radius gives way first, as it does for a cell too thin to hold it; only a cell that cannot be kept whole even at the ink minimum takes a split. And the ink is filled nonzero, so a path that overlaps itself paints solid, and a hole is a hole only because it is wound the other way — which the outline chaining guarantees, since a hole's edges are traversed with the same interior on the same side. Measured on a 130-px column with a 45-px dent at gap 14 and radius 34: two cores of 4,900 px² became one of 15,000 at a radius of 27.7; in a 30-element sweep with both sliders at their ends no painted cell split; crossed outlines stayed at 0; paint 2.7 ms a frame at the median and 6.2 at the ninety-fifth.

**A hovered wall asks the same way.** Rectangles did not expand on hover; only cells did, because a cell asks by raising its claim and a wall has no claim to raise — it is not bidding. So it lifted instead, into its own gap, and read as inert. Now a hovered wall asks the way a field's member does beyond its field: its rectangle pushed out by the depth a uniform growth would need to gain what a cell gains at the hover slider's boost, the front the neighbours' bisectors at the weight that wins the band half a depth out along all four sides, and the ring beyond its rectangle is its shard — joined to it, cut from whatever it lies over, walls and members alike, which is why the garment had to be robust to notched cells first. Only a leaf asks; a field's members ask for themselves, inside their field. The depth follows the body's crystal as well as the hover, so a wall that melts under the pointer lets its shard go as its claim takes over and a cell landing under the pointer grows its shard as it sets; the hover itself releases when the scene changes and the shard fades with it. Measured: a card of 111,000 px² carves 60,000 at the default boost, the target being 60%; across a scene change the hovered card's worst single-frame change is 3% of its area; gap and overlap stay zero; the paint costs 2.2 ms a frame in the stress case (30 elements, every one a field, the sliders at their ends, a card hovered) against 1.1 before, and nothing at rest.

**A cell becomes its rectangle the way it became a cell: by degrees.** With the walls in place the last snap was the switch itself. A cell landing became its rectangle in the frame its crystal reached 1, and a wall melting became a power cell in the frame it left; each frame moved a median of 7% of the cell and, one time in ten, 40%. Neither had a reason to be instant: the shape at both ends is known, and the crystal already runs on a clock between them.

So while its crystal is between 0 and 1 a body is a HOLE in the auction's ground, and the hole's shape travels between the cell it would have (crystal 0) and its rectangle (crystal 1). The shape is carried as half-planes, and THE BLEND IS A BLEND OF SUPPORTS, NOT OF SIDES: every direction that is a side of either shape keeps its direction, and only how far out the side stands is blended — the support function of (1-c)·cell + c·rect on those directions, so the hole holds that blend at every c and is never thinner than the thinner of the two. (Turning the sides' directions instead, as the first build did, let two opposite sides cross mid-way and made a needle of the hole, which then cut every cell it lay across — the diagonal halves and slivers of the first screenshots.) The cell's convex HULL is what travels, because a power cell is convex: what bends the cell it leaves behind is the ground's own cuts, a wall's corner or a stronger hole, and those cut the hole too, so hull less cuts is exactly the cell and the hole opens and closes on the cell itself. Its wedges are kept exactly as cut, hairs included, because that is what chains them back into one outline; a hair the garment cannot dress it leaves out.

The cell it would have is read from a SHADOW auction: one auction beside the main one, per pocket — the page as it would be if nothing were crystallising, its ground the page less the walls alone, every body that is not a wall bidding in it at its claim, holes and voids included, on its own warm weights in one gauge. A hole's target is its cell in that partition, so the holes' targets add up instead of each pretending the others were not there. Nothing crosses between the two auctions but a body's own painted area: a weight is one auction's gauge and means nothing in another, but the area a body is drawn at this instant means the same in every gauge, so a seed entering either auction enters at the weight that gives it exactly that, and the auction moves it toward its claim from there. The frame the last hole closes the two auctions are one again, and the main takes the shadow's weights whole, already converged. The target follows the shadow auction on a short clock (80 ms), because the auction's frame-to-frame reshuffling is not the cell's motion. A hole at crystal 0 does not close until its shape is the cell the auction would hand it, and the question is asked every frame, not at 0 — asked at 0 the answer arrives a frame after the hole is gone; while it lingers the clock shortens toward the instant, so a linger ends because the hole has caught up, never because a budget ran out. Holes never overlap a wall or each other: the more settled keeps its shape and the other loses exactly the overlap, as convex pieces. Voids morph like everything else.

Three things had to be made exact underneath: the ground's pockets are found by shared edges, not by boxes, once the ground is wedges and not rectangles; a seed's pocket is the piece it stands in, not the box it is nearest; and a repeated vertex is no side — a zero plane made every cut emit its piece twice, which is where a page of overlaps came from. Measured on the cycle, cell against its own previous outline: a settling cell's excess move 6.7% to 0.0% median and 40% to 2.1% at the ninetieth percentile; a melting cell's 9.3% to 0.0% and 55% to 0.0%; switches moving more than 10% of the cell, 46 to 0. The cost, stated: mid-morph a cell has more sides than a bid (outline vertices at the ninetieth percentile 7 to 12, edges per neighbour 1.35 to 1.68), the per-frame reshaping mid-transition is livelier (frames with a body changing more than 12% of itself 23 to 42, none at a switch), and the side auctions cost the stress case (30 elements, every one a field) a frame-time p95 of 39 ms against 23; at the default count no frame passes 35 ms. Gap and overlap zero, exact rectangles at rest, nothing solved at rest. Not carried: a cell's arm around a wall's corner as its own shrinking piece — built, measured, and dropped, because every arm is a cut in the ground and the ground's fragments multiplied faster than the handover smoothed.

**A cell holds its own contents.** The number and the name follow their cell on a slower clock than the cell moves, and that lag is deliberate: it is what gives a card weight, the sense that something is being carried rather than drawn. But the content was painted straight onto the canvas after the cell's clip was released, so while a cell travelled its label trailed OUTSIDE it, across the gap and over whatever lay behind, and a page of labels sliding over each other's cells is clutter the lag never asked for. Now the same path that paints the cell clips what it holds — the ink, not the cell, so a label is masked by the border the viewer can actually see, and the holes are wound out of it too, so a cell that contains another never writes across it. The lag is untouched; what changes is that it now reads as the content sliding under its own edge rather than escaping it. Paint only: the picture is derived exactly as before and the scorer is bit-identical at every clock.

**The pointer is a guest while the page is changing.** Every harness this project ever ran parked the pointer in one spot, so nothing measured the thing the owner was actually doing: holding a cursor over a page that rearranges under it. A cursor left resting where it was IS a moving pointer relative to a moving page. It catches every cell that flies past, and each catch is a claim boost and a shard the auction must hand out and take straight back — the cells fighting over ground the POINTER asked for, not the layout. Measured with a probe that sweeps the pointer during each change, at 30 ms frames: 116 jumps against 48 for a parked pointer, where parking anywhere else gives 33 to 52. The cursor was more than doubling the jumping, and no number had ever seen it.

So from the moment a change is asked for until the change is over, no cell is ACQUIRED. The end of the change is not a flag set at the button and cleared by a timer, and not "when everything looks quiet" — the flock is liquid and never is. It is read off the bodies every frame like everything else here: the last clock the change handed out, run to its end, so a second change arriving mid-flight hands out later clocks and the horizon moves out with them. A hover that was already there is not cut. It is handed back LINEARLY across the change rather than in the fifth of a second a pointer-leave takes, because every px² of that shard has to go back to a neighbour that is already moving, and linear means it is gone exactly when the change is. Measured: mid-flight acquisitions 10 to 0, and the jumps under a sweeping pointer 116 to 32; parked, 48 to 27 at 30 ms and 13 to 11 at 60 fps.

And hover moves at the pace ground moves here. What hover buys a settled cell is a shard worth 60% of its rectangle, every px² of it cut out of a neighbour; taken over a tenth of a second that is a seventh of the shard in one frame on a page otherwise at rest, a bigger step than any transition makes. Taken over a journey instead it arrives at the speed a body travels. THE RAMP IS NOT COSMETIC AND IT IS NOT FREE: it is the dial between a jumpy acquisition and a slow tail, and the curve was measured. At the journey's pace the sweeping jumps are 32 and the Hero scene keeps drifting for 131 frames after its last switch; at a third of that pace they are 67 and the drift is 91 frames; faster still and the 60 fps invariant breaks outright. The jumpy end is the thing being complained about and the drifting end is not, so the slow ramp is chosen with its cost known and written down.

Two repairs travelled with it, and they are why the numbers stop depending on where the pointer is parked. The auction had a tie it could not break: two bodies ejected out of the same wall on the same side land at exactly the same coordinate carrying exactly equal claims, and one cell collapses to zero for ten frames. In the shipped page that tie was broken only by an accident — a leftover 1% of hover boost on one of them — so freezing hover would have exposed it as a vanished cell. A tie that is broken by where the mouse happens to be is not broken.

**A pair is tested where it is going, not where it is.** The owner's complaint was that the cells cannot anticipate each other's trajectories and must fight for their place. Read literally, that named the repulsion: it was given only the distance two bodies have RIGHT NOW, so neither yielded until both were already in the other's way, the push landed late and head-on, and the spring spent the next frames taking it back. A flock reads velocities. Now the distance the law is given is the one the pair will have a short horizon from now at today's velocities, and the horizon is the seed spring's own response time — a body yields over exactly the span its spring would need to answer, so the swerve is spent before the spring can argue with it. Everything else is untouched: the strength, the radii, the crystal gates, the step. The push still runs along the offset the pair has now, because aiming it at the predicted offset turns a nearly head-on pair sideways in a direction made of noise and costs 2,300 px² of coverage. And when nothing is moving relative to anything, the predicted distance IS today's distance and this is the old law byte for byte — which is what keeps the landed picture whole, and what the F = 0 ablation proved was at stake: with the push simply removed, the settled picture opens a 1,328 px² hole nothing adopts.

Two other anticipations were built beside it and both failed honestly, which is why three were built. Solving the auction on the LEAD POINT — the cell drawn a fraction of the spring's lag ahead of its seed, so the ground opens before the traveller arrives — is a real mechanism (a control setting the lead to zero is bit-identical to the baseline) and a measured loss, monotone in its own size: at 30 ms frames the jumps go 48, 53, 55, 61 as the lead grows, because a lead that must vanish at rest is a non-uniform shift in time, and its ramp is extra seed speed that costs more the longer the frame. And handing the auction a ground defined by each hole's PAINTED pieces rather than its raw ones is exact and inert: the painted ground is a superset of the raw one, so the thing it was meant to fix does not exist.

The round's most useful result is about measurement, not motion. Perturbing the repulsion's strength by four parts in ten trillion — a change no arithmetic can see — moves the summed shock at 30 ms from 576,196 px² to 543,556 or to 524,872, and moves the uncovered ground from 4 px² to 284. THE SHOCK TOTAL IS CHAOS AT EVERY CLOCK, and so is any single-frame extremum. Jump COUNTS are stable enough to rank on and the invariants are pass or fail, but a shock number quoted to five figures is a story about a coin toss. This build is shipped on its mechanism and its invariants, not on its score: it is the one place in the file where an agent reads a neighbour's velocity and yields before contact, it costs one square root, and it cannot break the coverage its predecessor guaranteed.

**A number is a number at a clock.** The owner said the cells still fought, and every measurement said they had stopped. Both were true: the whole harness ran at a perfect 60 fps, and the page is watched at whatever frame times a browser gives. Asked at 30 ms a frame, the same file that scored 14 jumps and 157,637 px² of shock scored 61 and 724,778 — four times the jumps, on the same code, in the same scenes. Ten ablations then said what it was not. Not the path crossings: the assignment is already cyclically monotone, so it is crossing-free by construction, crossings correlate with the undone motion at 0.036, and forcing two hundred times more of them LOWERS the fight. Not the cut order: two holes swap in ten frames of 1,771, worth 0.2%. Not the spring that lags each seed behind its path — glued to its carrot the picture fights more, because the spring is a low-pass filter and a speed limit, not a noise source. Not the wobble, not the auction's iteration count as an everyday matter, and not simultaneity: sequencing harder shatters the picture and sequencing not at all lowers the fight, so the stagger is a tuned valley between two failure modes.

What it was: THREE CLOCKS COUNTED IN FRAMES. Newton's three iterations were three per FRAME, so at 30 ms the auction did half the work per second on a warm start twice as stale; the closing hole's catch-up budget was forty FRAMES, so it stretched from 0.67 s to 1.2 s and the hole closed by expiry instead of by catching up — which is the file's own definition of a snap; and the eviction that pushes a seed out of a wall damped its speed by half per FRAME. On top of those the motion pass, tuned at 1/60 s, was asked to act across the whole frame, and a semi-implicit step adds an effective extra stiffness of k1·dt², so a long frame tracks tighter and rings harder. Now every clock is measured in seconds: the iteration budget scales with the step (floored at today's three, capped at eight), the linger and its ramp are seconds, the eviction damps at a rate, and the motion pass is subdivided into whole 1/60 s substeps, so no force is ever asked to act across a step longer than the one it was tuned on. At 60 fps every one of these is exactly the identity — the same 14 jumps, the same kinds, the same reversal — and the file behaves as it always did. Measured at 30 ms: jumps 61 to 48, shock 724,778 to 576,196, uncovered ground 20 px² to 4, the auction's residual 0.32% to 0.002%; at 25 ± 12 ms, 47 jumps to 40 and 613,164 to 502,916. Gap, overlap, vanishing and exact rectangles at rest all hold at every clock.

Three fixes were built against each other and two were refuted by their own verifiers, which is the point of building three. One claimed a hole should open into its cell rather than the hull of its cell; a control that deleted the single line doing the cutting reproduced its whole headline, so the rule was inert and its gains came from somewhere else. One gave a body right of way by slowing its own journey clock — the only construction anyone found that lets a body yield without starving, since its claim, its crystal and its place on the path are one clock and slowing it renegotiates its share in step — but as shipped it painted two leaves over the same ground at an uneven clock, and the safety net it promised to retire fired more often, not less. Its reparametrisation is kept for a later pass. And a caution for the next instrument: the share of shape motion undone within a frame grows with frame time even when the simulation runs on a fixed step and only the sampling coarsens, because that is the curvature of a legitimate trajectory read at coarser intervals. Never compare it across clocks.

**The world at crystal 0 is one auction, not one per hole.** With the morph in place the transitions still opened and closed in a jitter, and the owner asked whether it was the pace: a complex layout needing more moves in the right order, rushed. Slowing every clock made it worse (per-body jumps 22 to 42 over the same cycle), so it was measured instead, on a fixed-step clock that makes two runs of one file identical frame for frame: 63 jumps of more than 12% of a cell in one frame over five scene changes, 15 of them reversed within five frames. The cause was structural. Each hole's side auction bid it against the free seeds in its pocket and never against the other melting bodies, so when a whole layout melted at once (Frame to Flock, the only free seed a void of near-zero claim) every hole's target was nearly the whole pocket — 680,000 px² for a body whose rectangle was 83,000 and whose fair share was 120,000 — and while the void was itself still a hole there was no bidder at all and every core was held at its rectangle, until the frame the void closed, when four cores lurched together. Smoothing a wrong target only spreads the wrongness over time. Two more things were wrong at the switches: a body entering an auction carried a weight from another auction, and a power diagram's weights are defined only up to a constant per auction, so the receiver spent frames recovering; and the linger at crystal 0 never armed, because it was asked only once the crystal was 0 and read a frame later, when the hole was already gone.

Five variants were built against each other on the same scorer. A pure rate limit on the cores — the fix that ducks the calculation — took the jumps from 63 to 23 and the reversals from 15 to 2, and moved the error to the end: a hole that had travelled thirteen frames toward a wrong target gave it all back in one frame when it closed, 27% at the switch. Ground continuity alone (a seedless pocket painted by whoever painted it last frame) took the reversals to 7, and found that the free cells' oscillation was the same event seen from the cell's side: a sole bidder paints its pocket, and a hole's shape was splitting the pocket and rejoining it. The shadow auction took the jumps to 14, the reversals to 1 and the summed shock from 1,180,000 px² to 158,000, without a rate limit and without a snap at the switch; of the 14 that remain, five are a field's members fading in, three are the first scene settling, two are adoption. Two repairs travelled with it: the support blend takes every direction that is a side of either shape (on the new shape's directions alone it returned the old shape circumscribed, larger than either, and larger again every frame the two were held apart), and a hovered body asks from where it stands, within the depth of its own shape, so its shard vanishes with the depth instead of appearing whole the frame the depth crosses its floor. Measured: crossed outlines 0, gap 4 px², overlap 8, exact rectangles at rest, the worst single-frame move of a cell 36,000 px² against 130,000, frame time unchanged. The rule for the next such choice: duck where the target is known and only the path is in question — that is what the clock is for; calculate where the target itself is wrong.

# The freedom ledger

The owner's instruction outranks everything else here: *"You don't have to be constrained by prior work... my biggest worry is that all my fumbling will be respected too much."*

**FIXED — non-negotiable, because theorem or measured failure:**

- The resolution stands: the tessellation is derived every frame from agent state; boundary geometry never stored, interpolated, or tweened — scenes, easing, choreography act on seeds and claims only; no force-and-snap on owned boundaries, ever.
- The solve's contract: prescribed areas on a power diagram via the concave dual — exact, convergence guaranteed by theorem (validated route: damped Newton with the KMT floor), never iterated-until-it-looks-okay; the reference's constants and algorithms free wherever the acceptance tests pass.
- Claims strictly positive for an agent's whole life (removal ramps to a floor, then deletes) — annihilation impossible; the solver rescales claims internally, callers never balance a budget; voids are agents with declared area.
- Preconditions guaranteed upstream every frame: seeds pairwise distinct, strictly inside a convex domain; they fail silently — agent-layer bugs.
- One authoritative tessellation per frame, per hive, for rendering, hit-testing, meters alike (a page is a tree of hives and the frame's picture is its leaves — tradeoff 4); the garment display-only, never fed back.
- One time convention: seconds.
- The meters exist, on-screen in development and acceptance builds.

FIXED is amended only in its own currency — a theorem or a measurement — never by preference.

**OPEN — everything else:**

- The entire garment: rounding, insets, rest shapes, engagement's measure and curves, color, texture; tradeoff 1 is a start, not law.
- Verbs beyond claim, if one earns its place (be suspicious first).
- Scene format, composition, interpolation, interruption — on seeds and claims only, per FIXED.
- Steering (boids or better) and who writes a claim (agent autonomy, scene overlay, both); fixed only that agents own position, claim, intent.
- Assignment policy for scene transitions.
- Pointer bindings: hover magnitude and easing, drag semantics, the clamp inset.
- All naming: "claim," "scene," "garment," "agent" are working titles.
- File structure, modules, tooling; one file or a library.
- Content anchoring beyond the inscribed pole.
- Rectilinearity: (b) or (c) freely; (a) only as a FIXED amendment.
- The three-layer decomposition itself; discard it if it fights you.

**Everything outside FIXED may be discarded the moment it fights you.** The list is short on purpose: it is exactly the load-bearing part.

# The owner

A designer with exceptional visual judgment and self-described weak math and physics, the owner iterates by building and looking. They do not need to understand this document — only that you can vividly see and think on it.

**Their jurisdiction is taste; inside it their word is final:** whether motion reads as alive, whitespace breathes, a transition feels like a flock or furniture sliding; do not litigate aesthetics — iterate.

**The contract: sealed solver, visible truth.** The math lives behind an interface the owner never opens; the meters let them *see* the theorem holding, no trust required. **Every knob a designer can turn lives in agent-space or garment-space; nothing aesthetic lives inside the math** (numerical constants like tolerance are not knobs — nobody tunes them for look). A magic constant inside the solve is mk8's land grab rebuilt: if a knob seems to belong in the solver, the design is wrong — move the meaning into a claim.

**Three mental models to maintain for them** — write the kernel's comments to teach exactly these and nothing harder:

1. Every seed *bids* distance-squared-minus-weight for every point of the canvas; every point goes to the lowest bidder.
2. The solver is an *auctioneer*: it raises the weight of any agent getting less than its claim and lowers the overweight ones, and a theorem guarantees the auction always clears.
3. The whole picture is *one smooth function* of the seed positions — so motion can never tear it. Nothing needs to be stitched, because nothing was ever in pieces.

**The naming reflex.** The owner spent months in mk5/mk6 throwing forces at a constraint with no solution — not for lack of skill; the wall had no name. The most valuable service a collaborator provided was naming it *before* proposing anything. Adopt the reflex: when a fix breeds three regressions, when tuning is whack-a-mole — stop, name the thing, decide together out loud: wall to route around, or problem to solve. Named, this owner redirects immediately; unnamed, a wall consumes months.

# Appendix: the reference solver

Ground truth for behavior, not digits: the table's layouts were not recorded — match the envelope (cold ≤ 7 iterations, warm 2–3, errors at tolerance, timings of this order); exact-output matching only against your own tests. The harness ran, in order: a central finite-difference check of the Jacobian; the eight table scenarios; the 1 px continuity sweep; eased and abrupt claim changes; the stale-teleport fallback; watertightness under arbitrary random weights; shift invariance under a constant added to all weights. Rebuild it before trusting a reimplementation.

```js
'use strict';
/*
 * Reference solver: power diagram with prescribed cell areas.
 * Plain JS, no dependencies. Intended for n <= 64: O(n^2) geometry per diagram,
 * O(n^3) linear solve per Newton step. All units are pixels and px^2.
 *
 * The three pictures to hold while reading:
 *   1. BIDDING. Every agent i bids |x - s_i|^2 - w_i for every point x of the
 *      domain; every point goes to the lowest bidder. Agent i's cell is where
 *      it wins. All boundaries fall out of this one rule, so the tiling is
 *      watertight at every instant, whatever the weights are.
 *   2. AUCTION. The solver raises the weight of any agent holding less area
 *      than its claim and lowers the overweight ones. A theorem (Aurenhammer;
 *      Kitagawa-Merigot-Thibert) says the auction always clears: weights
 *      giving every agent exactly its claimed area exist, and damped Newton
 *      finds them from any start.
 *   3. ONE SMOOTH FUNCTION. The diagram is a single continuous function of
 *      seed positions and weights. Move a seed and the picture deforms; it
 *      cannot tear, gap, or pop.
 */

// ------------------------------------------------------------------ geometry

// Signed ring area (shoelace). Callers take Math.abs; orientation-agnostic.
function ringArea(pts) {
  let a = 0;
  for (let k = 0, n = pts.length; k < n; k++) {
    const p = pts[k], q = pts[k + 1 === n ? 0 : k + 1];
    a += p[0] * q[1] - q[0] * p[1];
  }
  return a / 2;
}

// Sutherland-Hodgman clip of a labeled polygon to the half-plane
// ax*x + ay*y <= b. labs[k] labels the edge pts[k] -> pts[k+1]: a neighbor
// index >= 0, or a negative wall id. Edges created on the clip line get `lab`.
function clipHalfPlane(poly, ax, ay, b, lab) {
  const pts = poly.pts, labs = poly.labs, n = pts.length;
  const oP = [], oL = [];
  let A = pts[n - 1], aL = labs[n - 1];
  let av = ax * A[0] + ay * A[1] - b;
  for (let k = 0; k < n; k++) {
    const B = pts[k], bL = labs[k];
    const bv = ax * B[0] + ay * B[1] - b;
    if (av <= 0) {
      if (bv <= 0) { oP.push(B); oL.push(bL); }
      else {
        const t = av / (av - bv);
        oP.push([A[0] + t * (B[0] - A[0]), A[1] + t * (B[1] - A[1])]);
        oL.push(lab); // the new edge runs along the clip line: neighbor `lab`
      }
    } else if (bv <= 0) {
      const t = av / (av - bv);
      oP.push([A[0] + t * (B[0] - A[0]), A[1] + t * (B[1] - A[1])]);
      oL.push(aL); // surviving tail of the original edge keeps its label
      oP.push(B); oL.push(bL);
    }
    A = B; av = bv; aL = bL;
  }
  return { pts: oP, labs: oL };
}

// The whole diagram: for each agent, clip the domain polygon by its n-1
// bidding half-planes. Agent i beats agent j at x iff
//   |x-s_i|^2 - w_i <= |x-s_j|^2 - w_j   <=>   x.(s_j - s_i) <= (pot_j - pot_i)/2
// with pot_k = |s_k|^2 - w_k. Direct O(n^2); measured sub-millisecond at n=64.
function computeDiagram(seeds, weights, boundsPts) {
  const n = seeds.length;
  const cells = new Array(n);
  const areas = new Float64Array(n);
  const baseLabs = boundsPts.map((_, k) => -1 - k); // wall ids -1..-m
  const pot = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    pot[i] = seeds[i][0] * seeds[i][0] + seeds[i][1] * seeds[i][1] - weights[i];
  }
  for (let i = 0; i < n; i++) {
    let poly = { pts: boundsPts, labs: baseLabs }; // clip copies; never mutated
    for (let j = 0; j < n; j++) {
      if (j === i || poly.pts.length < 3) continue;
      poly = clipHalfPlane(poly,
        seeds[j][0] - seeds[i][0], seeds[j][1] - seeds[i][1],
        (pot[j] - pot[i]) / 2, j);
    }
    if (poly.pts.length < 3) { cells[i] = { pts: [], labs: [] }; areas[i] = 0; }
    else { cells[i] = poly; areas[i] = Math.abs(ringArea(poly.pts)); }
  }
  return { cells, areas };
}

// ------------------------------------------------- calculus of the diagram

// Jacobian A = d(areas)/d(weights): a weighted graph Laplacian.
//   A[i][j] = -L_ij / (2 d_ij)   for neighbors (a neighbor's raise shrinks you)
//   A[i][i] = +sum_j L_ij / (2 d_ij)   (your own raise grows you)
// with L_ij = shared edge length, d_ij = |s_i - s_j|. Rows sum to zero: the
// diagram only feels weight differences. (The concave dual's Hessian is -A.)
// Sign convention verified against central finite differences in the tests.
function buildJacobian(diagram, seeds) {
  const n = seeds.length;
  const A = [];
  for (let i = 0; i < n; i++) A.push(new Float64Array(n));
  for (let i = 0; i < n; i++) {
    const { pts, labs } = diagram.cells[i];
    for (let k = 0, m = pts.length; k < m; k++) {
      const j = labs[k];
      if (j < 0) continue; // wall edges do not move with weights
      const p = pts[k], q = pts[k + 1 === m ? 0 : k + 1];
      const L = Math.hypot(q[0] - p[0], q[1] - p[1]);
      const d = Math.hypot(seeds[j][0] - seeds[i][0], seeds[j][1] - seeds[i][1]);
      A[i][j] -= L / (2 * d);
    }
  }
  // Cells i and j each measured L_ij independently; average the two readings.
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) A[i][j] = A[j][i] = (A[i][j] + A[j][i]) / 2;
  }
  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) if (j !== i) s += A[i][j];
    A[i][i] = -s;
  }
  return A;
}

// Solve A x = g with x[n-1] pinned to 0. Weights are defined only up to one
// shared constant (adding c to every bid changes nothing), so A is singular by
// exactly one dimension; pinning removes it. While every cell has positive
// area the adjacency graph of a partition of a convex domain is connected and
// the pinned system is nonsingular. Gaussian elimination, partial pivoting.
function solvePinned(A, g) {
  const n = g.length, m = n - 1;
  const M = [];
  for (let i = 0; i < m; i++) {
    const row = new Float64Array(m + 1);
    for (let j = 0; j < m; j++) row[j] = A[i][j];
    row[m] = g[i];
    M.push(row);
  }
  for (let c = 0; c < m; c++) {
    let piv = c;
    for (let r = c + 1; r < m; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
    if (piv !== c) { const t = M[c]; M[c] = M[piv]; M[piv] = t; }
    const pv = M[c][c] || 1e-30;
    for (let r = c + 1; r < m; r++) {
      const f = M[r][c] / pv;
      if (f === 0) continue;
      for (let j = c; j <= m; j++) M[r][j] -= f * M[c][j];
    }
  }
  const x = new Float64Array(n); // x[n-1] stays 0
  for (let c = m - 1; c >= 0; c--) {
    let s = M[c][m];
    for (let j = c + 1; j < m; j++) s -= M[c][j] * x[j];
    x[c] = s / (M[c][c] || 1e-30);
  }
  return x;
}

// ---------------------------------------------------------------- the solver

function norm2(v) { let s = 0; for (const x of v) s += x * x; return Math.sqrt(s); }
function minOf(v) { let m = Infinity; for (const x of v) if (x < m) m = x; return m; }

// solveWeights(seeds, targets, boundsPts, w0?, opts?)
//   seeds:   [[x,y],...] distinct points strictly inside the bounds polygon
//   targets: positive claims in any units; rescaled to sum to |bounds| exactly
//   w0:      previous frame's weights (warm start), else all-zero (Voronoi)
// Returns { weights, iterations, evals, maxRelErr, converged, diagram }.
// evals counts diagram computations (the dominant cost), including backtracks.
function solveWeights(seeds, targets, boundsPts, w0, opts = {}) {
  const n = seeds.length;
  const tol = opts.tol !== undefined ? opts.tol : 1e-6; // max_i |err_i|/target_i
  const maxIter = opts.maxIter !== undefined ? opts.maxIter : 50;
  const domainArea = Math.abs(ringArea(boundsPts));

  let tSum = 0;
  for (const t of targets) {
    if (!(t > 0)) throw new Error('every claim must be positive');
    tSum += t;
  }
  const tgt = Float64Array.from(targets, t => t * domainArea / tSum);

  let w = w0 ? Float64Array.from(w0) : new Float64Array(n);
  let evals = 0;
  let diag = computeDiagram(seeds, w, boundsPts); evals++;
  if (w0 && minOf(diag.areas) <= 0) {
    // Stale warm start (a seed moved far since these weights were valid):
    // fall back to the all-zero start, which is plain Voronoi and gives every
    // interior seed a nonempty cell.
    w = new Float64Array(n);
    diag = computeDiagram(seeds, w, boundsPts); evals++;
  }

  // Global-convergence guard (Kitagawa-Merigot-Thibert): during the whole run,
  // never let any cell's area fall below half the smaller of (smallest claim,
  // smallest starting area). Keeps every cell alive, the adjacency graph
  // connected, and the Newton system nonsingular.
  const eps0 = 0.5 * Math.min(minOf(tgt), minOf(diag.areas));

  const g = new Float64Array(n);
  const refreshResidual = () => {
    let mr = 0;
    for (let i = 0; i < n; i++) {
      g[i] = tgt[i] - diag.areas[i];
      const r = Math.abs(g[i]) / tgt[i];
      if (r > mr) mr = r;
    }
    return mr;
  };
  let maxRel = refreshResidual();
  let gn = norm2(g);
  let iter = 0;
  let converged = maxRel <= tol;

  while (!converged && iter < maxIter) {
    const dw = solvePinned(buildJacobian(diag, seeds), g); // A dw = g
    let accepted = false;
    let t = 1;
    for (let bt = 0; bt < 40 && !accepted; bt++, t /= 2) {
      const wt = new Float64Array(n);
      for (let i = 0; i < n; i++) wt[i] = w[i] + t * dw[i];
      const dt = computeDiagram(seeds, wt, boundsPts); evals++;
      let gnT = 0, mn = Infinity;
      for (let i = 0; i < n; i++) {
        const gi = tgt[i] - dt.areas[i];
        gnT += gi * gi;
        if (dt.areas[i] < mn) mn = dt.areas[i];
      }
      gnT = Math.sqrt(gnT);
      // Accept the largest step that (i) keeps every cell above the floor and
      // (ii) shrinks the residual norm by the damped-Newton margin.
      if (mn >= eps0 && gnT <= (1 - t / 2) * gn) {
        w = wt; diag = dt; gn = gnT; accepted = true;
      }
    }
    iter++;
    if (!accepted) break; // report converged=false; diagram is still watertight
    maxRel = refreshResidual();
    converged = maxRel <= tol;
  }

  // Center the weights. The diagram only feels differences, so this changes
  // nothing on screen; it keeps warm-start numbers small over long runs.
  let mean = 0;
  for (let i = 0; i < n; i++) mean += w[i];
  mean /= n;
  for (let i = 0; i < n; i++) w[i] -= mean;

  return { weights: w, iterations: iter, evals, maxRelErr: maxRel, converged, diagram: diag };
}

module.exports = { ringArea, clipHalfPlane, computeDiagram, buildJacobian, solvePinned, solveWeights };
```
