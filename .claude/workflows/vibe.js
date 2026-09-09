export const meta = {
  name: 'vibe',
  description: 'Diagnose, design, build and judge fixes for the fighting cells: ablation lenses, a design panel, worktree builds, adversarial verification, one ranked table',
  whenToUse: 'The transition jitter gauntlet for hive.html. Run after reading .claude/gauntlet/VIBE.md. args: { mode: "diagnose" | "design" | "full", build: 3 }',
  phases: [
    { title: 'Diagnose', detail: 'one ablation lens per suspected mechanism, each on its own copy of hive.html, measured by flicker.js and score.js' },
    { title: 'Design', detail: 'five proposals from five angles, three judges, a ranking' },
    { title: 'Build', detail: 'the top designs built in worktrees, each verified by a refuter and scored' },
    { title: 'Judge', detail: 'one table, one recommendation, and what was not tried' },
  ],
}

// ------------------------------------------------------------ inputs
const A = args || {}
const MODE = A.mode || 'full'            // 'diagnose' stops after phase 1; 'design' after phase 2
const BUILD = A.build || 3               // how many designs to build
const REPO = '/home/user/Voronoi'
const BRIEF = REPO + '/.claude/gauntlet/VIBE.md'
const HARNESS = REPO + '/.claude/gauntlet'
const SCRATCH = '/tmp/claude-0/-home-user-Voronoi/75dbc440-48ad-59c3-a8c5-dea8806ca42b/scratchpad/vibe'

const COMMON = `
You are one agent in a structured gauntlet on the Voronoi repo (a single-file page, ${REPO}/hive.html).
Read the brief first, completely: ${BRIEF}. It says what the file is, what the owner sees, what has been
measured, how to measure (the deterministic harness in ${HARNESS}: flicker.js is the instrument for this
problem, score.js the one for jumps, peek.js the per-body inspector, cap.js the frame capturer), the
invariants, and the vocabulary. Never write any AI model name or identifier into any file. Harness
scripts print harmless "[agent-proxy]" lines on stderr; ignore them. Never use pkill -f with a pattern
that matches your own command. Scorer runs take 20 to 40 s; run them in the foreground.
Your final output is data for a script, not prose for a person: fill the structured output exactly.`

// ------------------------------------------------------------ schemas
const NUM = { type: 'number' }
const FLICK = {
  type: 'object',
  properties: { shapeBackShare: NUM, shapeBackPx2: NUM, flipFrames: NUM, wasteC: NUM, wasteA: NUM, revC: NUM, revA: NUM, fight: NUM, lag: NUM, pressureMean: NUM, settleTotal: NUM, jumps: NUM, reversals: NUM, shockPx2: NUM, gapMax: NUM, overMax: NUM, vanish: NUM, settledScenes: { type: 'string' } },
  required: ['shapeBackShare', 'shapeBackPx2', 'flipFrames', 'wasteC', 'fight', 'lag', 'jumps', 'reversals', 'shockPx2', 'gapMax', 'overMax', 'vanish'],
}
const DIAG_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    ablation: { type: 'string', description: 'exactly what was changed in the copy, as a one-line diff description' },
    baseline: FLICK, ablated: FLICK,
    verdict: { type: 'string', enum: ['cause', 'contributor', 'innocent', 'inconclusive'] },
    where: { type: 'array', items: { type: 'string' }, description: 'scene and frame ranges where the ablation changed the most, with body ids' },
    evidence: { type: 'string', description: 'three to six sentences: what moved, by how much, and the mechanism as you now understand it' },
    hivePath: { type: 'string' },
  },
  required: ['lens', 'ablation', 'baseline', 'ablated', 'verdict', 'where', 'evidence', 'hivePath'],
}
const DESIGN_SCHEMA = {
  type: 'object',
  properties: {
    angle: { type: 'string' },
    title: { type: 'string', description: 'the rule, in the file\'s own voice, one sentence' },
    rule: { type: 'string', description: 'the design as rules a builder can implement without you: what changes, where (function names), and what stays' },
    mechanismsAddressed: { type: 'array', items: { type: 'string' } },
    expected: { type: 'string', description: 'which flicker numbers should move, and roughly how far' },
    risks: { type: 'string' },
    cost: { type: 'string', description: 'per-frame cost and code size, honestly' },
    boids: { type: 'string', description: 'why this reads as a flock (anticipation, yielding, flow) and not as collision resolution' },
  },
  required: ['angle', 'title', 'rule', 'mechanismsAddressed', 'expected', 'risks', 'cost', 'boids'],
}
const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    scores: { type: 'array', items: { type: 'object', properties: { index: NUM, score: NUM, why: { type: 'string' } }, required: ['index', 'score', 'why'] } },
    graft: { type: 'string', description: 'ideas from lower-ranked designs worth carrying into the winners' },
  },
  required: ['scores', 'graft'],
}
const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    worktree: { type: 'string' }, patch: { type: 'string', description: 'absolute path of the .patch file' }, report: { type: 'string', description: 'absolute path of the .md report' },
    before: FLICK, after: FLICK,
    invariantsHeld: { type: 'boolean' },
    rule: { type: 'string', description: 'what was actually built, as the rule it implements' },
    left: { type: 'string', description: 'what the design asked for that was not built, and why' },
  },
  required: ['title', 'worktree', 'patch', 'report', 'before', 'after', 'invariantsHeld', 'rule', 'left'],
}
const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    reproduced: { type: 'boolean', description: 'the after numbers reproduce exactly on the worktree file' },
    refuted: { type: 'boolean', description: 'true if the build does not do what its rule says, breaks an invariant, or buys its numbers by hiding motion (a rate limit, a freeze, a duck) rather than removing the fight' },
    duck: { type: 'boolean', description: 'true if any part of the gain comes from holding shapes still against a target that still moves' },
    findings: { type: 'array', items: { type: 'string' } },
    lookedAt: { type: 'array', items: { type: 'string' }, description: 'the captures or frames you inspected' },
  },
  required: ['reproduced', 'refuted', 'duck', 'findings', 'lookedAt'],
}
const FINAL_SCHEMA = {
  type: 'object',
  properties: {
    ranking: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, rank: NUM, why: { type: 'string' } }, required: ['title', 'rank', 'why'] } },
    recommendation: { type: 'string', description: 'what to ship, what to combine, what to drop, in five sentences' },
    notTried: { type: 'array', items: { type: 'string' }, description: 'designs or lenses the gauntlet did not cover and should' },
  },
  required: ['ranking', 'recommendation', 'notTried'],
}

// ------------------------------------------------------------ phase 1: diagnose by ablation
phase('Diagnose')
const LENSES = [
  { key: 'separate', what: 'the liquid repulsion separate() (line ~2049): set its force F to 0 so travelling bodies never push each other' },
  { key: 'spring', what: 'the carrot spring in steer() (k1 ~62, k2 13.5): make the seed sit exactly on its carrot every frame (b.x = px, b.y = py, velocity zero) so there is no lag and no overshoot' },
  { key: 'wobble', what: 'the resting wobble (wob) in steer() and the free-drift wander: set both to 0' },
  { key: 'newton', what: 'the auctions\' iteration cap: maxIter 3 -> 30 in solveMain and solveShadow, so every frame is fully converged' },
  { key: 'cutorder', what: 'the holes\' cut order (computeWalls sorts holes by crystal descending so the more settled keeps its shape): sort by body id instead, so the order never flips when two crystals cross' },
  { key: 'holetau', what: 'the target clock HOLE_TAU 0.08 -> 0.30 s, so a hole\'s shape follows its shadow cell four times more slowly' },
  { key: 'stagger', what: 'the change\'s spread config.stagger 0.30 -> 0.90 s so journeys are far more sequenced (a cheap first look at right of way); also record 0.05 (everything at once)' },
  { key: 'pointer', what: 'the pointer: move it off the canvas (setMouse(-1e9,-1e9) in the harness copy) so no hover shard exists' },
  { key: 'timing', what: 'nothing in the file: the clock. The owner watches at real, uneven frame times, and the harness runs at a steady 60 fps. Run flicker.js on the UNTOUCHED copy at --dt 16.67 (the baseline), at --dt 30, and at --dt 25 --jitter 12, and score.js too where it accepts the same flags; report how every number moves with the clock. If the fight grows with dt or with jitter, say which terms in steer()/separate()/the auction are integrated per frame rather than per second, and which frame-count constants (Newton iterations per frame, HOLE_TAU on lastDt, the linger) make the picture depend on the frame rate' },
  { key: 'assignment', what: 'the target assignment (greedy nearest + 2-opt on squared travel, makeAssignment or similar): count how many journeys cross each other per scene change, and correlate the flicker\'s worst bodies and frames with crossings; then ablate by assigning targets to minimise crossings (or, if that is too much, by reporting the correlation alone)' },
]
const diag = (await parallel(LENSES.map(L => () => agent(`${COMMON}
Your lens: "${L.key}". Ablate ${L.what}
Method: copy ${REPO}/hive.html to ${SCRATCH}/abl-${L.key}/hive.html and edit only the copy. First run flicker.js and score.js on the UNTOUCHED copy and confirm the brief's baseline numbers reproduce exactly. Apply the ablation. Run both again. Use peek.js and the flicker --dump on the worst bodies to say WHERE the change concentrates (scene, frame range, body ids). Judge: is this mechanism a cause of the fighting (removing it removes most of shapeBackShare/flipFrames/fight), a contributor, or innocent? An ablation may break invariants or the design (a seed glued to its carrot is not a design); that is fine for a lens, say so, and still report what it teaches. Leave the copy in place and report its path.`,
  { label: `lens:${L.key}`, phase: 'Diagnose', schema: DIAG_SCHEMA, effort: 'high' })))).filter(Boolean)
log(`Diagnosed ${diag.length}/${LENSES.length} lenses: ` + diag.map(d => `${d.lens}=${d.verdict}`).join(', '))
if (MODE === 'diagnose') return { diag }

// ------------------------------------------------------------ phase 2: design panel
phase('Design')
const diagText = JSON.stringify(diag.map(d => ({ lens: d.lens, verdict: d.verdict, where: d.where, evidence: d.evidence, before: d.baseline, after: d.ablated })), null, 1)
const ANGLES = [
  { key: 'frame-rate', ask: 'THE CLOCK. The measured prize: at 30 ms frames the untouched file scores 61 jumps and 724,778 px2 of shock against 14 and 157,637 at 60 fps, and the diagnosis names three frame-counted mechanisms (maxIter 3 per FRAME at three sites, LINGER_MAX 40 and its ramp as frame counts, enforcePreconditions damping and ejecting per FRAME) plus the semi-implicit integration adding an effective k1*dt^2 stiffness. Design the fix so the picture a body paints depends on TIME, not on how often the browser asked. Options a designer must weigh: iterations per second rather than per frame; an absolute-area safety valve that re-solves when a frame would reallocate more than N px2 (the diagnosis says residual SIZE is not the predictor, area is); the linger and its ramp in seconds; per-second damping and ejection. Say what happens when a frame is very long (a tab wakes), and keep the 60 fps numbers from regressing.' },
  { key: 'weakest-hole', ask: 'THE HOLE NOBODY PROTECTS. A hole at crystal 0 is last in the cut order, so every wall and every stronger hole subtracts from it, and it is exactly the body that is lingering while it waits to catch up and close. Measured worst case at 30 ms: Frame scene body 9, painted area 37,936 -> 8,413 -> 20,589 px2 in two frames while its own target core sat steady at 39,000-41,000. Design what protects a body that is about to close, or gives it standing in the cut order, or lets it close and hand its ground to the main auction sooner, or makes the carving continuous rather than a one-frame bite. The cut order is priority, not stability, and reversing it is catastrophic (jumps 14 -> 68) — so do not simply reorder. Keep coverage exact.' },
  { key: 'right-of-way', ask: 'GIVERS AND TAKERS — the owner\'s own idea, done properly. Some bodies have right of way and move; the others yield until the way is clear. THE BINDING CONSTRAINT, measured: easeClaims moves a body\'s claim only with its own journey progress, so a body that yields keeps its OLD claim on ground the landed bodies have already had cut out from under them as walls; in the stagger ablation this starved the waiters until a leaf went 30k -> 0 -> 1k -> 0 and the seed was teleported 147 px out of a wall. A yielder MUST renegotiate its claim in step with its yield. Also measured: simply sequencing harder is not right of way — stagger 0.90 shatters everything (jumps 143, 12 vanishes) and 0.05, everything at once, LOWERS the fight numbers. So design the rule (who yields to whom and on what evidence), the claim renegotiation that goes with it, what yielding looks like on screen, and how total change time stays bounded.' },
  { key: 'anticipation', ask: 'ANTICIPATION — the one hypothesis no lens tested, and the owner\'s actual complaint ("as if they cannot anticipate each other\'s trajectories"). Solve the auction for where the seeds are GOING, not where they are: cells lead their seeds (solve on the carrot, or on the seed extrapolated by velocity over a short horizon), and a body reads its neighbours\' velocities so it yields before contact instead of discovering them by collision. Note what the diagnosis says you cannot lean on: the seed-level fight and the shape-level oscillation are decoupled (killing repulsion takes fight -62% and moves shapeBackShare by nothing), so an anticipation design must say which of the two it is buying and prove it. The picture must still be exact at rest and derived from agent state every frame, never stored or tweened.' },
  { key: 'one-law', ask: 'ONE MOTION LAW, WITH THE COVERAGE IT WAS SECRETLY CARRYING. separate() owns 62% of the seed fight (F=0 takes fight 0.225 -> 0.085 in every scene) but it is load-bearing for geometry, not only motion: at F=0 the picture leaves 1,328 px2 of ground unpainted and 20 px2 overlapped, a static hole in the landed picture. And the spring is not noise — gluing the seed to its carrot is worse at both clocks. So design one consistent law for a travelling seed that keeps what repulsion was silently guaranteeing (a minimum separation that keeps every pocket adoptable) while removing the shove-and-recover: repulsion folded into the path at assignment time, a soft constraint on the carrot rather than on the seed, or a separation term that acts along the path rather than across it. Say explicitly how coverage stays exact.' },
]
const designs = (await parallel(ANGLES.map(G => () => agent(`${COMMON}
You are on the design panel, angle "${G.key}". ${G.ask}
Read the brief — SECTION 3.5 FIRST, it supersedes the hypotheses and kills most of section 6 — then the code the brief's code map names (steer, separate, updateCrystal, enterScene and its assignment, computeWalls, solveMain, solveShadow, placeSeeds). Here is what the diagnosis phase found, lens by lens:
${diagText}
Design ONE proposal from your angle that a builder can implement in a few hours without you. It must keep every invariant in the brief (nothing vanishes, no overlap, gap no worse, exact rectangles at rest, every scene settles) and the file's principles (the tessellation is derived every frame from agent state, boundaries never stored or tweened; continuity by construction, not by budget; no rate limit that hides a moving target). Say which flicker numbers it should move and why it reads as a flock rather than as collision resolution.`,
  { label: `design:${G.key}`, phase: 'Design', schema: DESIGN_SCHEMA, effort: 'high' })))).filter(Boolean)
log(`Designs: ` + designs.map(d => d.title).join(' | '))
const JUDGE_LENSES = ['continuity and correctness: which design cannot break the invariants and cannot hide motion', 'the flock: which design most makes the cells anticipate and yield, reading as alive rather than as collision resolution', 'feasibility and cost: which design a builder will actually finish, at what per-frame cost, with the fewest new failure modes']
const judged = (await parallel(JUDGE_LENSES.map((lens, j) => () => agent(`${COMMON}
You are judge ${j + 1} of 3 on the design panel. Your lens: ${lens}.
Diagnosis: ${diagText}
Designs (index in order):
${designs.map((d, i) => `[${i}] ${d.title}\nANGLE ${d.angle}\nRULE ${d.rule}\nEXPECTED ${d.expected}\nRISKS ${d.risks}\nCOST ${d.cost}\nBOIDS ${d.boids}`).join('\n\n')}
Score each design 0..10 through your lens with a reason, and name ideas from lower-ranked designs worth grafting into the winners.`,
  { label: `judge:${j + 1}`, phase: 'Design', schema: JUDGE_SCHEMA, effort: 'high' })))).filter(Boolean)
const totals = designs.map((d, i) => ({ i, d, score: judged.reduce((s, J) => s + ((J.scores.find(x => x.index === i) || { score: 0 }).score), 0) }))
totals.sort((a, b) => b.score - a.score)
const chosen = totals.slice(0, BUILD)
const graft = judged.map(J => J.graft).join('\n')
log(`Ranking: ` + totals.map(t => `${t.d.title} (${t.score})`).join(' > '))
if (MODE === 'design') return { diag, designs, judged, ranking: totals.map(t => ({ title: t.d.title, score: t.score })) }

// ------------------------------------------------------------ phase 3: build, verify, score (pipeline: no barrier)
phase('Build')
const built = await pipeline(chosen,
  (t, _, k) => agent(`${COMMON}
You are builder ${k + 1}. Build this design in your worktree (you are in an isolated git worktree of the repo; edit hive.html only; do not commit or push):
TITLE ${t.d.title}
RULE ${t.d.rule}
EXPECTED ${t.d.expected}
RISKS ${t.d.risks}
Grafts the judges asked for, where they fit: ${graft}
Diagnosis the design rests on: ${diagText}
Method: run flicker.js and score.js on the untouched file first and confirm the brief's baseline numbers reproduce exactly, at ALL THREE clocks (default, --dt 30, --dt 25 --jitter 12; both scripts take these flags). The 30 ms numbers are the target: 61 jumps and 724,778 px2 of shock on the untouched file against 14 and 157,637 at 60 fps. Report every number at all three clocks and never compare shapeBackShare across clocks. Build. Measure after every change; look at the worst bodies with peek.js and at captures with cap.js; iterate until the invariants hold and the design's numbers moved, or two more iterations bought nothing. Then write the deliverables: git diff of your worktree to ${SCRATCH}/build-${k + 1}.patch, and a one-page report to ${SCRATCH}/build-${k + 1}.md (the rule as built, before/after numbers from both scorers, what the design asked for that you did not build and why, what the brief has wrong). Keep the file's voice: short comments that say why. No model names anywhere.`,
    { label: `build:${t.d.title.slice(0, 40)}`, phase: 'Build', schema: BUILD_SCHEMA, isolation: 'worktree', effort: 'high' }),
  (b, t) => b && agent(`${COMMON}
You are the refuter for a build. Try to REFUTE it. Default to refuted=true if you cannot reproduce it.
Build: ${JSON.stringify({ title: b.title, worktree: b.worktree, patch: b.patch, report: b.report, rule: b.rule, before: b.before, after: b.after, left: b.left })}
Design it was meant to implement: ${t.d.rule}
Do: run flicker.js and score.js yourself on ${b.worktree}/hive.html and compare to the reported after numbers (they must match exactly; the harness is deterministic). Read the patch. Look for a duck: any hold, cap, freeze, rate limit, or smoothing of a shape against a target that still moves, which buys numbers by hiding motion rather than removing the fight (the brief's control variant did exactly this and moved the error to the switch). Check every invariant in the brief. Capture frames with cap.js and look at at least four mid-transition captures; a shape that lags its rectangle at landing, a cell that vanishes, or a hole that overlaps a wall is a refutation. Report what you looked at.`,
    { label: `refute:${(b && b.title || '').slice(0, 40)}`, phase: 'Build', schema: VERDICT_SCHEMA, effort: 'high' }).then(v => ({ build: b, verdict: v, design: t.d })),
)
const results = built.filter(Boolean).filter(r => r.build)
log(`Built ${results.length}/${chosen.length}; refuted: ${results.filter(r => r.verdict && r.verdict.refuted).length}`)

// ------------------------------------------------------------ phase 4: one table
phase('Judge')
const table = results.map(r => ({ title: r.build.title, before: r.build.before, after: r.build.after, invariantsHeld: r.build.invariantsHeld, refuted: r.verdict ? r.verdict.refuted : null, duck: r.verdict ? r.verdict.duck : null, findings: r.verdict ? r.verdict.findings : [], patch: r.build.patch, report: r.build.report, worktree: r.build.worktree, left: r.build.left }))
const final = await agent(`${COMMON}
You are the final judge. Here is everything: the diagnosis, the designs and their panel scores, and the builds with their refuters' verdicts.
Diagnosis: ${diagText}
Designs and scores: ${JSON.stringify(totals.map(t => ({ title: t.d.title, score: t.score, rule: t.d.rule })), null, 1)}
Builds: ${JSON.stringify(table, null, 1)}
Rank the builds (a refuted or ducking build ranks last whatever its numbers), recommend what to ship, what to combine and what to drop, and list what the gauntlet did not try and should. Read the reports and patches before you rank; numbers alone are not the vibe. Say in one sentence per build whether the cells now anticipate and yield, or still fight.`,
  { label: 'final judge', phase: 'Judge', schema: FINAL_SCHEMA, effort: 'high' })
return { diag, designs, ranking: totals.map(t => ({ title: t.d.title, score: t.score })), builds: table, final }
