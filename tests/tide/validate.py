"""Validate the Tide mark: the corner budget, the fatness, and the tide itself.

The bounds here are the claims the mark makes, in a form that fails if they
stop being true. They are taken from measurement, not from hope, and each is
set where the mark actually sits with room for clock-to-clock variation — not
so loose that a regression slips through.

The two that matter most are the ones no earlier instrument could see:

  organicShare   a page of floating rectangles scores perfectly clean on the
                 shape taxonomy, which is how the previous mark shipped with no
                 organic feel at all. This gate fails if the cells stop being
                 cells.
  sliverShare    a corner budget cannot tell a cell from a splinter — a
                 five-cornered wedge counts exactly like a five-cornered cell.
                 This gate fails if the page turns to shards while still
                 passing the corner census.

And the tide:

  worstRestingInset >= 0    at rest the page is the window and nothing is off
                            the crop. A negative inset is a bleed being spent
                            when nothing needs it, which is the whole of the
                            owner's second complaint.
  cropBorders == 0          no cell is bordered along a window edge it crosses:
                            what runs off the crop is cut by the crop, never
                            computed wide and painted narrow.
  the margin is USED        at least one scene borrows it during a change. A
                            reservoir that never opens is a disabled feature,
                            and this gate is what stops the previous bound
                            being met by simply switching the tide off.
"""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GAUNTLET = ROOT / '.claude/gauntlet'
PW = os.environ.get('PLAYWRIGHT_MODULE', '/opt/node22/lib/node_modules/playwright')
OUT = ROOT / 'tide-results'
OUT.mkdir(exist_ok=True)

CLOCKS = [('240hz', 1000 / 240, 0), ('120hz', 1000 / 120, 0),
          ('60hz', 1000 / 60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]
selected = os.environ.get('TIDE_CLOCKS', '').split(',')
if selected != ['']:
    CLOCKS = [c for c in CLOCKS if c[0] in selected]
MASK_CLOCKS = ['60hz', '30ms', 'jitter']    # the raster probes cost a full-frame mask

# measured on 4ee96cb; each bound is where the mark sits, with headroom
ORGANIC_MIN = 0.55      # measured 0.78 at 30 ms
OVER_MAX = 0.05         # measured 0.012; the reference is 0.075
SLIVER_MAX = 0.11       # measured 0.064; the reference is 0.137
IQ_MIN = 0.68           # measured 0.756; the reference is 0.647
VERTS_MAX = 24          # measured 16; the reference reaches 38
RIGID_BENTO_MIN = 0.99  # a bento is a bento: every slot a rectangle


def run(script, page, extra=()):
    src = (GAUNTLET / script).read_text().replace('/opt/node22/lib/node_modules/playwright', PW)
    tmp = OUT / ('_' + script)
    tmp.write_text(src)
    cmd = ['node', str(tmp), str(page), '--dt', '30', *extra]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f'{script} failed on {page}:\n{p.stderr[-2000:]}')
    return json.loads(p.stdout)


def main():
    page = ROOT / 'tide.html'
    if not page.exists():
        raise SystemExit('tide.html missing; run tests/tide/build.py first')

    summary = {'clocks': {}, 'passed': False}
    failures = []

    for name, dt, jit in CLOCKS:
        extra = ['--dt', str(dt), '--jitter', str(jit)]
        c = run('corners.js', page, extra)
        t = c['transition']
        row = {
            'organicShare': t['organicShare'], 'rigidShare': t['rigidShare'],
            'overBudget': t['overBudget'], 'iqMean': t['iqMean'],
            'sliverShare': t['sliverShare'], 'vertsMax': t['vertsMax'],
            'worstRestingInset': c['worstRestingInset'],
            'restingInset': c['restingInset'],
            'bentoRigid': c['byScene'].get('bento', {}).get('rigidShare'),
            'pageErrors': c['pageErrors'],
        }
        summary['clocks'][name] = row

        def bad(msg):
            failures.append(f'[{name}] {msg}')

        if c['pageErrors']:
            bad(f"{c['pageErrors']} page errors")
        if t['organicShare'] < ORGANIC_MIN:
            bad(f"organicShare {t['organicShare']} < {ORGANIC_MIN}: the cells have stopped being cells")
        if t['overBudget'] > OVER_MAX:
            bad(f"overBudget {t['overBudget']} > {OVER_MAX}: flubber")
        if t['sliverShare'] > SLIVER_MAX:
            bad(f"sliverShare {t['sliverShare']} > {SLIVER_MAX}: shards, not cells")
        if t['iqMean'] < IQ_MIN:
            bad(f"iqMean {t['iqMean']} < {IQ_MIN}: the cells have thinned")
        if t['vertsMax'] > VERTS_MAX:
            bad(f"vertsMax {t['vertsMax']} > {VERTS_MAX}")
        # THE TIDE IS OUT AT REST. This is the owner's second complaint in one
        # number: a negative inset is ink off the crop when nothing needs it.
        if c['worstRestingInset'] is not None and c['worstRestingInset'] < 0:
            bad(f"worstRestingInset {c['worstRestingInset']} < 0: the page does not rest at 100%")
        if row['bentoRigid'] is not None and row['bentoRigid'] < RIGID_BENTO_MIN:
            bad(f"bento rigidShare {row['bentoRigid']} < {RIGID_BENTO_MIN}: a bento should be a bento")

        if name in MASK_CLOCKS:
            s = run('spill.js', page, extra)
            by = s.get('byScene', {})
            summary['clocks'][name]['spill'] = {
                k: {'outsideMaxPx2': v.get('outsideMaxPx2'), 'straddlerFrames': v.get('straddlerFrames'),
                    'frames': v.get('frames'), 'cropBorders': v.get('cropBorders')}
                for k, v in by.items()
            }
            for sc, v in by.items():
                if v.get('cropBorders'):
                    bad(f"{sc}: {v['cropBorders']} crop borders — computed wide, painted narrow")
            # a settled bento must never reach the margin
            bento = by.get('bento', {})
            if bento.get('straddlerFrames'):
                bad(f"bento used the margin in {bento['straddlerFrames']} frames: the tide is not out at rest")
            # ...and the reservoir must actually be a reservoir. Without this,
            # every bound above is satisfied by switching the tide off.
            used = sum(v.get('straddlerFrames', 0) for v in by.values())
            summary['clocks'][name]['marginFramesUsed'] = used
            if used == 0:
                bad('no scene used the margin: a reservoir that never opens is a disabled feature')

    summary['passed'] = not failures
    summary['failures'] = failures
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=1))

    for f in failures:
        print('FAIL', f, file=sys.stderr)
    if failures:
        raise SystemExit(f'{len(failures)} bound(s) broken')
    print('Tide: every bound held over', ', '.join(n for n, _, _ in CLOCKS))


main()
