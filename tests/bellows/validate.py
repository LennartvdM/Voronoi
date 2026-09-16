"""Validate the Bellows mark: a buffer that cannot switch, and drains to nothing.

Bellows keeps Murmur's overflow buffer and removes its switch, so its gate has
to hold three things at once — and any two of them are easy on their own.

  THE SKIP IS GONE.
    spikeMax      the worst frame's displacement over the median of the four
                  frames either side of it. Murmur's margin snaps into being
                  at the first frame of a change and out of it at the last:
                  30-177 px against neighbours moving 1 to 5 px, 61x at worst.
                  Bellows measures 2.5, and Bleed — whose margin is permanently
                  open and therefore never switches — 1.4.
    spikeFrames   no frame over the ratio at all.
    ...INTERRUPTED  and the same two, measured again with every scene chosen 30
                  frames into the previous change rather than after it. A
                  settled run cannot see this case: `seatBody` resets a
                  retargeted body's progress to 0, so anything read off
                  progress steps. Before the swell was made a rate-limited
                  state it read 10.3 here against 2.5 settled; it now reads
                  2.8, and Murmur reads 60.9.

  THE BUFFER IS STILL THERE AND STILL SHARED. Removing the skip by removing
  the margin is Brim's job, and Brim is the control; this mark has to keep it.
    scenesUsed    all three transitions must reach the margin.
    concentration the biggest single spiller's share, over frames with a spill
                  worth sharing. Low is the collective case.
    worstShare    and no single frame where one cell has nearly all of it.

  IT DRAINS TO NOTHING, AND OPENS FOR NOTHING ELSE.
    restingPx2    zero at every clock in every scene. Bleed left 572,610 px2
                  outside at rest; that is the page at 105% the owner threw
                  out two marks ago.
    flock         and the flock — where no body has a path, so nothing is
                  travelling — must not spill at all. The first cut sized the
                  rim from the page's whole claim rather than from the loan,
                  and a dissolving void's bookkeeping opened 61 px of margin
                  in a scene that needed none: 230,028 px2 across 70% of its
                  frames. This gate is what catches that returning.
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
OUT = ROOT / 'bellows-results'
OUT.mkdir(exist_ok=True)

CLOCKS = [('240hz', 1000 / 240, 0), ('120hz', 1000 / 120, 0),
          ('60hz', 1000 / 60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]
selected = os.environ.get('BELLOWS_CLOCKS', '').split(',')
if selected != ['']:
    CLOCKS = [c for c in CLOCKS if c[0] in selected]
DEEP_CLOCKS = ['60hz', '30ms', 'jitter']
SETTLE_MS = 6600        # simulated ms per scene, matching 220 frames at 30 ms

# ---- BOUNDS: measured over the five-clock matrix, with headroom -------------
ORGANIC_MIN = 0.58      # measured 0.663-0.666; the reference 0.174-0.178
OVER_MAX = 0.005        # measured 0.000; the reference 0.068-0.075
IQ_MIN = 0.655          # measured 0.684-0.685; the reference 0.644-0.647
IQMIN_MIN = 0.15        # the WORST cell: measured 0.199-0.259; Brim, with no buffer, 0.172-0.213
SLIVER_MAX = 0.120      # measured 0.103-0.104; Brim, with no buffer, 0.107-0.108
VERTS_MAX = 10          # measured 9; Murmur reaches 10 because its ring sites
                        # are extra neighbours. Bellows has no ring sites.
NETDISP_MIN = 300.0     # measured 348-360
WANDER_MAX = 2.30       # measured 1.26-1.30; the reference 1.41-2.63
BURST_MIN = 0.55        # measured 0.665-0.736
SETTLE_SHARE_MAX = 0.55  # measured 0.346-0.395
SPIKE_MAX = 5.0         # measured 1.3-2.7 over five clocks; Murmur 60.7
SPIKE_FRAMES_MAX = 0    # measured 0; Murmur 2 per transition scene
CONC_MAX = 0.45         # measured 0.281-0.285; Murmur 0.383, Tide 0.556
WORST_SHARE_MAX = 0.60  # measured 0.409-0.429; Murmur 0.604, Tide 0.750
USERS_MIN = 4.0         # measured 5.64-5.73
EDGES_MIN = 2.5         # measured 3.06-3.08 of four


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
    page = ROOT / 'bellows.html'
    if not page.exists():
        raise SystemExit('bellows.html missing; run tests/bellows/build.py first')
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
        # THE WORST CELL, not the average. This is where the buffer earns its
        # place: Bellows' thinnest cell is 0.199-0.259 against Brim's
        # 0.172-0.213 with the buffer deleted. If that margin goes, the buffer
        # has stopped doing the one thing it is for.
        if t['iqMin'] < IQMIN_MIN:
            bad(f"iqMin {t['iqMin']} < {IQMIN_MIN}: a cell has been crushed")
        if t['sliverShare'] > SLIVER_MAX:
            bad(f"sliverShare {t['sliverShare']} > {SLIVER_MAX}: shards, not cells")
        if t['vertsMax'] > VERTS_MAX:
            bad(f"vertsMax {t['vertsMax']} > {VERTS_MAX}")
        if c['worstRestingInset'] is not None and c['worstRestingInset'] < 0:
            bad(f"worstRestingInset {c['worstRestingInset']} < 0: the page does not rest at 100%")

        # THE SKIP. This is the mark, and it is one frame, so it is measured at
        # every clock: a coarse one can step straight over a single frame.
        j = run('jolt.js', page, extra)
        jt = j['transition']
        row['jolt'] = dict(jt, byScene={k: {kk: v[kk] for kk in ('spikeMax', 'spikeFrames', 'settleFrames')}
                                        for k, v in j['byScene'].items()})
        if jt['spikeMax'] > SPIKE_MAX:
            bad(f"spikeMax {jt['spikeMax']} > {SPIKE_MAX}: the buffer is stepping again")
        if jt['spikeFrames'] > SPIKE_FRAMES_MAX:
            bad(f"spikeFrames {jt['spikeFrames']} > {SPIKE_FRAMES_MAX}")

        # AND THE SAME CHANGE, INTERRUPTED. A settled run cannot see this: when
        # a scene is chosen before the last one has finished, `seatBody` resets
        # every retargeted body's progress to 0, so anything read off progress
        # steps. This is the case review found and the gate that would have
        # caught it.
        ji = run('jolt.js', page, extra + ['--interrupt', '30'])
        jit = ji['transition']
        row['joltInterrupted'] = {k: jit[k] for k in ('spikeMax', 'spikeFrames')}
        if jit['spikeMax'] > SPIKE_MAX:
            bad(f"interrupted spikeMax {jit['spikeMax']} > {SPIKE_MAX}: "
                f"a change cut short steps")
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
            bad(f"only {rt['scenesUsed']}/{rt['scenes']} transitions reached the margin: "
                f"a buffer that opens for one scene is not the page's")
        # NOBODY IS TRAVELLING IN THE FLOCK, so nothing may be borrowed for it.
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

    summary['passed'] = not failures
    summary['failures'] = failures
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=1))

    for f in failures:
        print('FAIL', f, file=sys.stderr)
    if failures:
        raise SystemExit(f'{len(failures)} bound(s) broken')
    print('Bellows: every bound held over', ', '.join(n for n, _, _ in CLOCKS))


main()
