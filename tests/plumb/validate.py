"""Validate the Plumb mark: Bellows' smoothness, now drawn on axis.

Plumb changes one thing about Bellows — the sidebar's template — so its gate
has to prove both halves of that trade, and either half alone is easy.

  THE RECTANGLES ARE THERE.
    plumb.js measures ANGLE, weighted by edge LENGTH, at rest. corners.js
    cannot do this: it counts corners, and a trapezoid has four just like a
    rectangle does. A fanned sidebar and a bento are both "four corners"; they
    are not both a bento.
    sidebarAxis   the share of the sidebar's outline length lying within 4
                  degrees of an axis. Bellows measures 0.700 — every cell in
                  that column is a trapezoid leaning a little differently from
                  its neighbour. Plumb measures 0.848-0.866.
    sidebarRect   the share of its CELLS that are wholly on axis. This is the
                  number the owner was looking at: Bellows makes ZERO true
                  rectangles in the sidebar, Astra I made all of them. Plumb
                  makes 0.556-0.600 of them, with no wall and no second kind
                  of cell anywhere on the page.
    bentoAxis/Rect  the control. bento was already the scene that worked
                  (0.932 / 0.667) and it is untouched here; if it moves, the
                  change leaked out of the template it was meant to be in.

    Why the template and not the seeds: the edge between two cells is always
    perpendicular to the line joining their two seeds (computeDiagram), so a
    weight slides an edge along its normal and can never turn it. Every angle
    on the page is fixed by seed position alone, and a seam is drawable plumb
    only where the two cells it parts have identical extent along it. Measured
    over the four templates, that misalignment is BIMODAL — nothing at all
    between 0.1 and 0.3 of a lattice unit in any scene — so there is no nudge
    small enough to be invisible and large enough to fix anything. The
    dissections that satisfy it everywhere are grids. Hence quilt().

    AND ON PAGES THE DEFAULT READING CANNOT SEE. The first cut of quilt()
    passed every bound in this file and still lapsed. wantCols() is 12 at
    depth 0, so the sidebar is always 5 lattice units wide; wantRows() falls
    to 4 or 5 on a short page, giving 20 or 25 whole slots against a roster
    that goes to 30. Over that, no candidate grid fitted and the template
    fell back to `guillotine` — the fanned column, reading 0.3505 against
    Bellows' 0.3505 at 1440x620 with 24 elements, identical to four decimals.
    The fix is that a sub-unit row is still a row: every cell in it shares
    one y-extent, which is the whole of what makes a seam drawable plumb.
    Integers were never the requirement, only `guillotine`'s habit. Those
    cases now read 0.936-0.959 with 0.767-0.867 of their cells true
    rectangles, and every case that already worked is unchanged to four
    decimals. STRESS is here so that lapse cannot return quietly.

    AND UNDER TWO HARDER READINGS, because both of plumb.js's defaults
    flatter a result and neither is relied on here.
      TOLERANCE. 4 degrees is a generous window. An independent nudge-based
      route measured on this same page reaches sidebar 0.849 at 4 degrees and
      0.696 at 2 — two thirds of its gain lives between the two. This mark
      reads 0.848/0.556 at 4 degrees and 0.848/0.556 at 2. Not one cell drops
      out, because the cells really are rectangles rather than near-misses.
      (Bellows, read the same way, falls 0.700 -> 0.655.)
      DENOMINATOR. plumb.js skips a body that has become a FIELD, since its
      members are emitted at path length 2 — so the default reading covers
      5-10 of 12 cards. --full reads every body's own outline instead. The
      sidebar comes out HIGHER there, 0.886/0.667 against 0.703/0.000, and
      the untouched scenes are identical between the two builds to four
      decimals: bento 0.8643/0.500, hero 0.5066/0.000. Note that bento's
      familiar 0.932/0.667 is a leaf-subset figure; over every body it is
      0.864/0.500, in BOTH builds. The mark's claim does not rest on it.

    AND EVERY BODY IS STILL BIDDING. This is the one thing an angle cannot
    see, and it is the invariant a grid template is most likely to break: a
    rectangle with no area sets claimTarget to 0, the body falls under
    ACTIVE_MIN and stops bidding, and the page silently loses a card while
    every angle on it still reads beautifully. A rival grid design measured
    on this page did exactly that — 96 zero-area rectangles over a roster
    sweep, four bodies not bidding and two cards missing from the window at
    one slider-drag from the default, with its axis score reading 0.966.
    So it is counted rather than inferred, at every clock and every stress
    case, and separately over R=4..10 x n=4..30: 189 templates, zero
    zero-area rectangles, exact tiling everywhere.

  AND THE SKIP DID NOT COME BACK. This is the half that is easy to lose: the
  straighter seam has a much better-scoring route, and that route brings the
  step back.
    spikeMax      the worst frame's displacement over the median of the four
                  frames either side. Plumb measures 1.7-3.3 over five clocks;
                  Bellows 1.3-2.7, Murmur 60.7.
    spikeFrames   none at all, at any clock.
    ...INTERRUPTED  and again with every scene chosen 30 frames into the
                  previous change. Plumb 1.3-2.2.

    Giving the whitespace one mirrored site per cell it borders takes the
    sidebar to an axis share of 0.999 with EVERY cell a true rectangle — Astra
    I's result, with no wall. It is in the source, switched off, because it
    also reads 65.2 here with two spike frames, every one of them at
    normalised position 0.00: the frame enterScene assigns new rectangles and
    the void's whole site set is rebuilt at once. That is the same switch
    Bellows exists to remove, reached by another road.

  AND EVERY BELLOWS BOUND STILL HOLDS, because a rectangle bought with
  flubber, a crushed cell or an undrained buffer is not worth having.
    overBudget    0.000 at every clock, as Bellows. One site per body, so each
                  power cell is convex and the 3-9 corner budget is an
                  identity rather than a hope.
    iqMin         THE HONEST COST, and it is stated rather than hidden: the
                  worst content cell in the whole run reads 0.152-0.249 where
                  Bellows reads 0.199-0.259 and Brim 0.172-0.213. Plumb's
                  worst single frame is thinner than either. sliverShare does
                  NOT move (0.106-0.109 against Bellows' 0.103-0.104), so this
                  is one transient frame in ten thousand body-frames and not a
                  page that has thinned. The bound is set to admit it, at 0.12,
                  and no lower.
    netDisp/wander  the other cost. The grid puts a cell's destination further
                  from where guillotine put it, so the page travels more:
                  netDisp 390-412 against Bellows' 348-360, wander 1.46-1.49
                  against 1.26-1.30. Both stay well inside the reference.
    peakRatio     and it still must not exceed the reference's on the same
                  clock — 4.1-5.0 against 5.9-7.0. The page travels; it does
                  not arrive.
    restingPx2    zero everywhere, and the flock — where nobody has a path —
                  must not open the margin at all.
"""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GAUNTLET = ROOT / '.claude/gauntlet'
PW = os.environ.get('PLAYWRIGHT_MODULE', '/opt/node22/lib/node_modules/playwright')
CHROME = os.environ.get('CHROMIUM_PATH')
LAUNCH = "executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',"
OUT = ROOT / 'plumb-results'
OUT.mkdir(exist_ok=True)

CLOCKS = [('240hz', 1000 / 240, 0), ('120hz', 1000 / 120, 0),
          ('60hz', 1000 / 60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]
selected = os.environ.get('PLUMB_CLOCKS', '').split(',')
if selected != ['']:
    CLOCKS = [c for c in CLOCKS if c[0] in selected]
DEEP_CLOCKS = ['60hz', '30ms', 'jitter']
SETTLE_MS = 6600        # simulated ms per scene, matching 220 frames at 30 ms

# ---- BOUNDS: measured over the five-clock matrix, with headroom -------------
# THE MARK ITSELF
SIDEBAR_AXIS_MIN = 0.78   # measured 0.848-0.866; Bellows 0.700
SIDEBAR_RECT_MIN = 0.45   # measured 0.556-0.600; Bellows 0.000
BENTO_AXIS_MIN = 0.88     # measured 0.932-0.934; unchanged from Bellows
BENTO_RECT_MIN = 0.55     # measured 0.667; unchanged from Bellows
# THE MARK AGAIN, ON PAGES THE DEFAULT READING CANNOT SEE. The lattice is
# sized from the viewport and the roster runs to 30, so these are the cases
# where a grid template runs out of whole lattice slots.
STRESS = [(1440, 540, 30), (1440, 620, 24), (1440, 720, 30)]
STRESS_AXIS_MIN = 0.85    # measured 0.936-0.959; before the sub-unit grid,
STRESS_RECT_MIN = 0.65    # 0.266-0.387 and ZERO rectangles — Bellows exactly
# THE HEADLINE, READ TWO HARDER WAYS.
STRICT_TOL = 2            # degrees. A nudge-based route measured on this page
STRICT_AXIS_MIN = 0.78    # loses two thirds of its gain between 4 and 2; this
STRICT_RECT_MIN = 0.45    # mark loses NOTHING (0.848/0.556 at both).
FULL_AXIS_MIN = 0.82      # --full: every body's own outline, so a body that has
FULL_RECT_MIN = 0.55      # become a field counts too. Measured 0.886/0.667,
                          # BETTER than the leaf reading, against Bellows' 0.703/0.000.
# INHERITED FROM BELLOWS
ORGANIC_MIN = 0.55      # measured 0.640-0.678; the reference 0.174-0.178
OVER_MAX = 0.005        # measured 0.000; the reference 0.068-0.075
IQ_MIN = 0.655          # measured 0.684-0.693
IQMIN_MIN = 0.12        # the WORST cell: measured 0.152-0.249. Below Bellows'
                        # 0.199-0.259 and Brim's 0.172-0.213 — see the header.
SLIVER_MAX = 0.125      # measured 0.106-0.109; Bellows 0.103-0.104
VERTS_MAX = 10          # measured 9
NETDISP_MIN = 320.0     # measured 390-412; Bellows 348-360
WANDER_MAX = 2.30       # measured 1.46-1.49; the reference 1.41-2.63
BURST_MIN = 0.55        # measured 0.679-0.729
SETTLE_SHARE_MAX = 0.55  # measured 0.391-0.417
SPIKE_MAX = 5.0         # measured 1.7-3.3 over five clocks; Murmur 60.7, and
                        # the mirrored-site variant of THIS mark 65.2
SPIKE_FRAMES_MAX = 0    # measured 0; Murmur 2 per transition scene
CONC_MAX = 0.45         # measured 0.274-0.297; Murmur 0.383, Tide 0.556
WORST_SHARE_MAX = 0.60  # measured 0.404-0.467; Murmur 0.604, Tide 0.750
USERS_MIN = 4.0         # measured 5.57-5.70
EDGES_MIN = 2.5         # measured 2.98-3.02 of four


def run(script, page, extra=()):
    src = (GAUNTLET / script).read_text().replace('/opt/node22/lib/node_modules/playwright', PW)
    src = src.replace(LAUNCH, ('executablePath: ' + json.dumps(CHROME) + ',') if CHROME else '')
    tmp = OUT / ('_' + script)
    tmp.write_text(src)
    # NO default --dt here: the probes resolve options with argv.indexOf, which
    # takes the FIRST occurrence, so a hardcoded --dt would silently win.
    p = subprocess.run(['node', str(tmp), str(page), *extra], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f'{script} failed on {page}:\n{p.stderr[-2000:]}')
    return json.loads(p.stdout)


def main():
    page = ROOT / 'plumb.html'
    if not page.exists():
        raise SystemExit('plumb.html missing; run tests/plumb/build.py first')
    reference = ROOT / 'hive.html'

    summary = {'clocks': {}, 'passed': False}
    failures = []

    for name, dt, jit in CLOCKS:
        frames = max(60, round(SETTLE_MS / dt))
        extra = ['--dt', str(dt), '--jitter', str(jit), '--frames', str(frames)]
        row = {}
        summary['clocks'][name] = row

        def bad(msg):
            failures.append(f'[{name}] {msg}')

        # THE MARK. Read at rest, because a settled layout is when the page is
        # making its claim about what shape it is.
        pl = run('plumb.js', page, extra)
        sb, bt = pl['byScene']['sidebar'], pl['byScene']['bento']
        row['plumb'] = {s: {k: pl['byScene'][s][k] for k in ('axisShare', 'rectShare', 'tiltMean')}
                        for s in pl['byScene']}
        row['plumb']['pageErrors'] = pl['pageErrors']
        if pl['pageErrors']:
            bad(f"{pl['pageErrors']} page errors in the plumb probe")
        if sb['axisShare'] < SIDEBAR_AXIS_MIN:
            bad(f"sidebar axisShare {sb['axisShare']} < {SIDEBAR_AXIS_MIN}: the column is fanning again")
        if sb['rectShare'] < SIDEBAR_RECT_MIN:
            bad(f"sidebar rectShare {sb['rectShare']} < {SIDEBAR_RECT_MIN}: "
                f"the sidebar has stopped making rectangles, which is the whole mark")
        if bt['axisShare'] < BENTO_AXIS_MIN:
            bad(f"bento axisShare {bt['axisShare']} < {BENTO_AXIS_MIN}: "
                f"the scene that already worked has regressed")
        if bt['rectShare'] < BENTO_RECT_MIN:
            bad(f"bento rectShare {bt['rectShare']} < {BENTO_RECT_MIN}")

        # THE ROSTER, which no angle can see. A template that hands out a
        # rectangle with no area drops that body below ACTIVE_MIN and it stops
        # bidding: the page quietly loses a card while every angle still reads
        # beautifully. This is counted, not inferred.
        row['roster'] = {'bodiesMin': pl['bodiesMin'], 'notBiddingMax': pl['notBiddingMax'],
                         'zeroAreaMax': pl['zeroAreaMax'], 'byScene': pl['roster']}
        if pl['zeroAreaMax']:
            bad(f"{pl['zeroAreaMax']} body(s) hold a rectangle with no area")
        if pl['notBiddingMax']:
            bad(f"{pl['notBiddingMax']} body(s) stopped bidding: the page has lost a card")

        c = run('corners.js', page, extra)
        t = c['transition']
        row['corners'] = {k: t[k] for k in ('organicShare', 'rigidShare', 'overBudget',
                                            'iqMean', 'iqMin', 'sliverShare', 'vertsMax')}
        row['corners']['worstRestingInset'] = c['worstRestingInset']
        row['corners']['pageErrors'] = c['pageErrors']
        if c['pageErrors']:
            bad(f"{c['pageErrors']} page errors")
        if t['overBudget'] > OVER_MAX:
            bad(f"overBudget {t['overBudget']} > {OVER_MAX}: flubber is back")
        if t['organicShare'] < ORGANIC_MIN:
            bad(f"organicShare {t['organicShare']} < {ORGANIC_MIN}: the cells have stopped being cells")
        if t['iqMean'] < IQ_MIN:
            bad(f"iqMean {t['iqMean']} < {IQ_MIN}: the cells have thinned")
        if t['iqMin'] < IQMIN_MIN:
            bad(f"iqMin {t['iqMin']} < {IQMIN_MIN}: a cell has been crushed")
        if t['sliverShare'] > SLIVER_MAX:
            bad(f"sliverShare {t['sliverShare']} > {SLIVER_MAX}: shards, not cells")
        if t['vertsMax'] > VERTS_MAX:
            bad(f"vertsMax {t['vertsMax']} > {VERTS_MAX}")
        if c['worstRestingInset'] is not None and c['worstRestingInset'] < 0:
            bad(f"worstRestingInset {c['worstRestingInset']} < 0: the page does not rest at 100%")

        # THE SKIP, which the straighter seam is very good at bringing back.
        j = run('jolt.js', page, extra)
        jt = j['transition']
        row['jolt'] = dict(jt, byScene={k: {kk: v[kk] for kk in ('spikeMax', 'spikeFrames', 'settleFrames')}
                                        for k, v in j['byScene'].items()})
        if jt['spikeMax'] > SPIKE_MAX:
            bad(f"spikeMax {jt['spikeMax']} > {SPIKE_MAX}: the page is stepping again")
        if jt['spikeFrames'] > SPIKE_FRAMES_MAX:
            bad(f"spikeFrames {jt['spikeFrames']} > {SPIKE_FRAMES_MAX}")

        ji = run('jolt.js', page, extra + ['--interrupt', '30'])
        jit = ji['transition']
        row['joltInterrupted'] = {k: jit[k] for k in ('spikeMax', 'spikeFrames')}
        if jit['spikeMax'] > SPIKE_MAX:
            bad(f"interrupted spikeMax {jit['spikeMax']} > {SPIKE_MAX}: a change cut short steps")
        if jit['spikeFrames'] > SPIKE_FRAMES_MAX:
            bad(f"interrupted spikeFrames {jit['spikeFrames']} > {SPIKE_FRAMES_MAX}")

        # THE BUFFER, AND ITS DRAIN.
        r = run('reservoir.js', page, extra)
        rt = r['transition']
        row['reservoir'] = dict(rt, restingPx2=r['restingPx2'],
                                byScene={k: {kk: v[kk] for kk in ('spillShare', 'outsideMaxPx2', 'restingPx2')}
                                         for k, v in r['byScene'].items()})
        if r['pageErrors']:
            bad(f"{r['pageErrors']} page errors in the reservoir probe")
        if r['restingPx2'] != 0:
            bad(f"restingPx2 {r['restingPx2']} != 0: the buffer has not drained")
        if rt['scenesUsed'] < rt['scenes']:
            bad(f"only {rt['scenesUsed']}/{rt['scenes']} transitions reached the margin")
        fl = r['byScene'].get('flock', {})
        if fl.get('spillFrames'):
            bad(f"flock: ink outside the window in {fl['spillFrames']} frames "
                f"(max {fl['outsideMaxPx2']} px2) — no body there has a path")
        if rt['concentration'] > CONC_MAX:
            bad(f"concentration {rt['concentration']} > {CONC_MAX}: one cell is taking the margin")
        if rt['worstShare'] > WORST_SHARE_MAX:
            bad(f"worstShare {rt['worstShare']} > {WORST_SHARE_MAX}: a private escape hatch")
        if rt['usersMean'] < USERS_MIN:
            bad(f"usersMean {rt['usersMean']} < {USERS_MIN}: too few cells share it")
        if rt['edgesMean'] < EDGES_MIN:
            bad(f"edgesMean {rt['edgesMean']} < {EDGES_MIN}: the spill is on one side")

        if name not in DEEP_CLOCKS:
            continue

        m = run('motion.js', page, extra)['transition']
        ref = run('motion.js', reference, extra)['transition']
        row['motion'] = m
        row['motionReference'] = {k: ref[k] for k in ('peakRatio', 'netDisp', 'wander', 'burst')}
        if m['netDisp'] < NETDISP_MIN:
            bad(f"netDisp {m['netDisp']} < {NETDISP_MIN}: the page barely moves")
        if m['wander'] > WANDER_MAX:
            bad(f"wander {m['wander']} > {WANDER_MAX}: shoved about, not travelling")
        if m['burst'] < BURST_MIN:
            bad(f"burst {m['burst']} < {BURST_MIN}: the change happens in a snap")
        if m['settleShare'] > SETTLE_SHARE_MAX:
            bad(f"settleShare {m['settleShare']} > {SETTLE_SHARE_MAX}")
        if m['peakRatio'] > ref['peakRatio']:
            bad(f"peakRatio {m['peakRatio']} exceeds the reference's {ref['peakRatio']} "
                f"on the same clock: the page arrives rather than travels")

    # THE PAGES THE DEFAULT READING CANNOT SEE. This gate exists because the
    # first cut of quilt() passed every bound above and still lapsed: at 12
    # columns the sidebar is 5 lattice units wide, so a page short enough for
    # 4 or 5 rows holds 20 or 25 whole slots against a roster of 30, and the
    # surplus sent it back to `guillotine` — the fanned column, measured
    # identical to Bellows to four decimals. One viewport and one roster size
    # cannot see that, so the gate reads more than one of each.
    # THE SAME CLAIM, READ TWO HARDER WAYS. A 4-degree window is generous,
    # and plumb's default denominator skips a body that has become a field
    # (its members are emitted at path length 2). Both are stated rather than
    # relied on: at 2 degrees this mark reads exactly what it reads at 4,
    # because the cells really are rectangles and not near-misses; and over
    # every body, fields included, it reads BETTER than the leaf view.
    harder = {}
    summary['harder'] = harder
    for label, extra, amin, rmin in (
            ('tol2', ['--tol', str(STRICT_TOL)], STRICT_AXIS_MIN, STRICT_RECT_MIN),
            ('full', ['--full', '1'], FULL_AXIS_MIN, FULL_RECT_MIN)):
        pl = run('plumb.js', page, ['--dt', '30', '--frames', '220', *extra])
        sb = pl['byScene']['sidebar']
        harder[label] = {k: sb[k] for k in ('axisShare', 'rectShare', 'cells')}
        if sb['axisShare'] < amin:
            failures.append(f"[{label}] sidebar axisShare {sb['axisShare']} < {amin}")
        if sb['rectShare'] < rmin:
            failures.append(f"[{label}] sidebar rectShare {sb['rectShare']} < {rmin}: "
                            f"the rectangles do not survive a harder reading")

    stress = {}
    summary['stress'] = stress
    for vw, vh, n in STRESS:
        key = f'{vw}x{vh}@{n}'
        pl = run('plumb.js', page, ['--dt', '30', '--frames', '220',
                                    '--vw', str(vw), '--vh', str(vh), '--count', str(n)])
        sb = pl['byScene']['sidebar']
        stress[key] = {k: sb[k] for k in ('axisShare', 'rectShare', 'cells')}
        stress[key]['pageErrors'] = pl['pageErrors']
        if pl['pageErrors']:
            failures.append(f'[{key}] {pl["pageErrors"]} page errors')
        if sb['axisShare'] < STRESS_AXIS_MIN:
            failures.append(f"[{key}] sidebar axisShare {sb['axisShare']} < {STRESS_AXIS_MIN}: "
                            f"the grid ran out of whole lattice slots and the column fanned")
        if sb['rectShare'] < STRESS_RECT_MIN:
            failures.append(f"[{key}] sidebar rectShare {sb['rectShare']} < {STRESS_RECT_MIN}")
        if pl['zeroAreaMax']:
            failures.append(f"[{key}] {pl['zeroAreaMax']} body(s) hold a rectangle with no area")
        if pl['notBiddingMax']:
            failures.append(f"[{key}] {pl['notBiddingMax']} body(s) stopped bidding")

    summary['passed'] = not failures
    summary['failures'] = failures
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=1))

    for f in failures:
        print('FAIL', f, file=sys.stderr)
    if failures:
        raise SystemExit(f'{len(failures)} bound(s) broken')
    print('Plumb: every bound held over', ', '.join(n for n, _, _ in CLOCKS))


main()
