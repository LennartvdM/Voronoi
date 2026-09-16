"""Validate the Brim mark: the same page, with nothing to overflow into.

Brim is Murmur minus the overflow buffer and nothing else, so its gate is
Murmur's gate plus two changes that carry the whole experiment:

  THE SKIP, which is why this mark exists.
    spikeMax      the worst frame's displacement over the median of the four
                  frames on either side of it. Murmur's margin switches on at
                  the first frame of a change and off at the last, and those
                  two frames move 33 px and 130-184 px against neighbours
                  moving 1 to 5 px — 61x at worst. With nothing to switch this
                  must be small, and it is measured at 2.6.
    spikeFrames   and there must be NO frame over the ratio at all.

  THE MARGIN, which must not exist.
    spillShare    zero in every scene, at every clock. Not "empty at rest" —
                  never occupied, because there is nowhere to go. This is the
                  gate that makes Brim a control rather than a variant: if any
                  ink leaves the window, the thing being tested is still there.

Everything else is inherited from Murmur and bounded where Brim measures, so
a regression in the shared machinery fails here too. The two that matter most
are the ones no earlier instrument could see:

  overBudget    a cell of ten corners or more is flubber, which is what the
                wall/hole blend produces. Brim has no blend, so this is 0.000.
  sliverShare   AND THIS IS WHERE BRIM IS EXPECTED TO BE WORSE. With no margin
                to borrow, a travelling body's room comes from its neighbours,
                so if the buffer was load-bearing the price shows as cells
                driven thin. The bound is set where Brim actually sits, not
                where Murmur sits, precisely so the cost is recorded rather
                than hidden — and still under the reference's 0.137.
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
OUT = ROOT / 'brim-results'
OUT.mkdir(exist_ok=True)

CLOCKS = [('240hz', 1000 / 240, 0), ('120hz', 1000 / 120, 0),
          ('60hz', 1000 / 60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]
selected = os.environ.get('BRIM_CLOCKS', '').split(',')
if selected != ['']:
    CLOCKS = [c for c in CLOCKS if c[0] in selected]
DEEP_CLOCKS = ['60hz', '30ms', 'jitter']
SETTLE_MS = 6600        # simulated ms per scene, matching 220 frames at 30 ms

# ---- BOUNDS: measured over the five-clock matrix, with headroom -------------
ORGANIC_MIN = 0.58      # measured 0.663-0.667; the reference 0.174-0.178
OVER_MAX = 0.005        # measured 0.000; the reference 0.068-0.075
IQ_MIN = 0.655          # measured 0.683-0.684; the reference 0.644-0.647
IQMIN_MIN = 0.12        # the WORST cell: measured 0.172-0.213; Bellows 0.199-0.259
SLIVER_MAX = 0.125      # measured 0.107-0.108; the reference 0.137-0.141
VERTS_MAX = 10          # measured 9; the reference reaches 36-42
NETDISP_MIN = 300.0     # measured 364-372
WANDER_MAX = 2.30       # measured 1.24-1.35; the reference 1.41-2.63
BURST_MIN = 0.55        # measured 0.716-0.771
SETTLE_SHARE_MAX = 0.55  # measured 0.346-0.395
SPIKE_MAX = 5.0         # measured 1.5-2.7 over five clocks; Murmur 60.7
SPIKE_FRAMES_MAX = 0    # measured 0; Murmur 2 per transition scene


def run(script, page, extra=()):
    src = (GAUNTLET / script).read_text().replace('/opt/node22/lib/node_modules/playwright', PW)
    src = src.replace(LAUNCH, ('executablePath: ' + json.dumps(CHROME) + ',') if CHROME else '')
    tmp = OUT / ('_' + script)
    tmp.write_text(src)
    # NO default --dt here: the probes resolve options with argv.indexOf, which
    # takes the FIRST occurrence, so a hardcoded --dt would silently win over
    # the per-clock one and measure every clock at that rate.
    p = subprocess.run(['node', str(tmp), str(page), *extra], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f'{script} failed on {page}:\n{p.stderr[-2000:]}')
    return json.loads(p.stdout)


def main():
    page = ROOT / 'brim.html'
    if not page.exists():
        raise SystemExit('brim.html missing; run tests/brim/build.py first')
    reference = ROOT / 'hive.html'

    summary = {'clocks': {}, 'passed': False}
    failures = []

    for name, dt, jit in CLOCKS:
        # THE SAME SIMULATED TIME AT EVERY CLOCK: the probes take a frame COUNT,
        # so a fixed one measures less and less of the page as the clock gets
        # faster, and the "seated" sample lands mid-transition.
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
        # THE WORST CELL, not the average. Losing the buffer costs Brim exactly
        # here — its thinnest cell is 0.172-0.213 against Bellows' 0.199-0.259 —
        # so the floor is set where Brim sits, to record the cost rather than
        # hide it, and low enough that only a real collapse trips it.
        if t['iqMin'] < IQMIN_MIN:
            bad(f"iqMin {t['iqMin']} < {IQMIN_MIN}: a cell has been crushed")
        if t['sliverShare'] > SLIVER_MAX:
            bad(f"sliverShare {t['sliverShare']} > {SLIVER_MAX}: shards, not cells")
        if t['vertsMax'] > VERTS_MAX:
            bad(f"vertsMax {t['vertsMax']} > {VERTS_MAX}")
        if c['worstRestingInset'] is not None and c['worstRestingInset'] < 0:
            bad(f"worstRestingInset {c['worstRestingInset']} < 0: ink off the crop at rest")

        # THE SKIP. This is the mark. Measured at every clock, not the cheap
        # ones only: a spike is one frame, and a coarse clock can step over it.
        j = run('jolt.js', page, extra)
        jt = j['transition']
        row['jolt'] = dict(jt, byScene={k: {kk: v[kk] for kk in ('spikeMax', 'spikeFrames', 'settleFrames')}
                                        for k, v in j['byScene'].items()})
        if jt['spikeMax'] > SPIKE_MAX:
            bad(f"spikeMax {jt['spikeMax']} > {SPIKE_MAX}: a frame the page cannot explain")
        if jt['spikeFrames'] > SPIKE_FRAMES_MAX:
            bad(f"spikeFrames {jt['spikeFrames']} > {SPIKE_FRAMES_MAX}")

        # THERE IS NO MARGIN. Every scene, every frame, at every clock. Without
        # this bound Brim is not a control — the thing under test could still
        # be present and merely quiet.
        r = run('reservoir.js', page, extra)
        row['reservoir'] = {'restingPx2': r['restingPx2'],
                            'byScene': {k: v['spillShare'] for k, v in r['byScene'].items()},
                            'outsideMaxPx2': {k: v['outsideMaxPx2'] for k, v in r['byScene'].items()}}
        for sc, v in r['byScene'].items():
            if v['spillFrames']:
                bad(f"{sc}: ink outside the window in {v['spillFrames']} frames "
                    f"(max {v['outsideMaxPx2']} px2) — Brim has no margin to use")

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
        # peakRatio rises with the frame rate for everybody, so an absolute
        # number here would bound the clock and not the mark. The reference is
        # measured in this same run; its blob is pinned by the build.
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
    print('Brim: every bound held over', ', '.join(n for n, _, _ in CLOCKS))


main()
