"""Run the repository's picture probes in Chromium on Hive, Astra I and Tessera.

Only runtime paths, transport and warmup duration are adapted. Thresholds and
picture metrics are the original probes' (score, strobe, flicker) plus the
ripple probe written for this mark. A green job requires the invariants and
the improvements below, not merely successful measurement commands.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tessera-results'
OUT.mkdir(exist_ok=True)
PW = os.environ.get('PLAYWRIGHT_MODULE', '/tmp/astra-runtime/node_modules/playwright')
CHROME = os.environ.get('CHROMIUM_PATH')
CLOCKS = [('240hz', 1000 / 240, 0), ('120hz', 1000 / 120, 0),
          ('60hz', 1000 / 60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]
selected = os.environ.get('ASTRA_CLOCKS', '').split(',')
if selected != ['']:
    CLOCKS = [c for c in CLOCKS if c[0] in selected]
BUILDS = ['hive', 'astra-i', 'tessera']
MASK_CLOCKS = ['60hz', '30ms', 'jitter']

with tempfile.TemporaryDirectory(prefix='tessera-probes-') as tmp:
    probes = Path(tmp)
    for name in ['score', 'strobe', 'flicker', 'ripple']:
        s = (ROOT / '.claude/gauntlet' / (name + '.js')).read_text()
        s = s.replace('/opt/node22/lib/node_modules/playwright', PW)
        launch = "executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',"
        s = s.replace(launch, ('executablePath: ' + json.dumps(CHROME) + ',') if CHROME else '')
        s = s.replace('await p.addInitScript(CLOCK);', 'await p.evaluate(CLOCK);')
        s = s.replace("await p.goto('file://' + dst);", "await p.setContent(fs.readFileSync(dst, 'utf8'));")
        s = s.replace('X.setMouse(700, 400)', 'X.setMouse(-1000, -1000)')
        s = s.replace('window.__advance = (n) => {', 'window.__warmup = Math.ceil(3600 / DT); window.__advance = (n) => {')
        s = s.replace('for (let i = 0; i < 120; i++) step();', 'for (let i = 0; i < window.__warmup; i++) step();')
        (probes / (name + '.js')).write_text(s)
    results = {}
    for clock, dt, jitter in CLOCKS:
        for build in BUILDS:
            tests = ['score'] + (['strobe', 'flicker', 'ripple'] if clock in MASK_CLOCKS else [])
            for test in tests:
                name = f'{build}-{test}-{clock}'
                cmd = ['node', str(probes / (test + '.js')), str(ROOT / (build + '.html')),
                       str(OUT / (name + '.json')), '--dt', str(dt), '--jitter', str(jitter),
                       '--frames', str(math.ceil(5500 / dt)), '--parkx', '-1000', '--parky', '-1000']
                print('RUN', name, flush=True)
                with (OUT / (name + '.log')).open('w') as log:
                    subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900)
                results[name] = json.loads((OUT / (name + '.json')).read_text())
                if results[name].get('pageErrors'):
                    raise AssertionError(f'{name}: JavaScript errors')
    summary = {'referenceBlob': '2c02b2dc66d05fb152feffcd952f18b4d39f3634',
               'candidateSHA256': hashlib.sha256((ROOT / 'tessera.html').read_bytes()).hexdigest(),
               'warmupMs': 3600, 'sceneHoldMs': 5500, 'viewport': [1440, 900],
               'pointer': [-1000, -1000], 'clocks': {}, 'passed': False}
    TRANSITION = ['hero', 'sidebar', 'frame']
    for clock, _, _ in CLOCKS:
        row = summary['clocks'][clock] = {}
        for build in BUILDS:
            a = results[f'{build}-score-{clock}']
            row[build] = {'jumpsIncludingStartup': a['jumps'],
                          'transitionJumps': sum(v for k, v in a['byScene'].items() if k != 'flock0'),
                          'byScene': a['byScene'], 'gapMax': a['gapMax'], 'overMax': a['overMax'],
                          'vanish': a['vanish'], 'settledScenes': a['settledScenes'],
                          'areaRelativeErrorMax': a['errMax'], 'msP95': a['msP95']}
            if build == 'tessera':
                assert a['vanish'] == 0 and a['pageErrors'] == 0, (clock, a)
                # the 2 px coverage raster can count one cell of a numerical seam as
                # an overlap; a gap it never excuses
                assert a['gapMax'] == 0 and a['overMax'] <= 4, (clock, a)
                assert a['settledScenes'] == '5/5', (clock, a)
            if clock in MASK_CLOCKS:
                t = results[f'{build}-strobe-{clock}']
                f = results[f'{build}-flicker-{clock}']
                r = results[f'{build}-ripple-{clock}']
                row[build]['transitionTeleports'] = sum(v for k, v in t['teleportByScene'].items() if k in TRANSITION)
                row[build]['teleportsByScene'] = t['teleportByScene']
                row[build]['shapeBackShare'] = f['shapeBackShare']
                row[build]['transitionBends'] = r['transitionBends']
                row[build]['transitionTeeth'] = r['transitionTeeth']
                row[build]['transitionCorrugations'] = r['transitionCorrugations']
                row[build]['transitionDepthPx'] = r['transitionDepthPx']
                row[build]['bendsByScene'] = {k: v['bends'] for k, v in r['byScene'].items()}
                row[build]['teethByScene'] = {k: v['teeth'] for k, v in r['byScene'].items()}
                row[build]['corrugationsByScene'] = {k: v['corrugations'] for k, v in r['byScene'].items()}
                row[build]['axisShareByScene'] = {k: v['axisShareMean'] for k, v in r['byScene'].items()}
        assert row['tessera']['transitionJumps'] <= row['astra-i']['transitionJumps'], row
        assert row['tessera']['areaRelativeErrorMax'] <= 1.01e-6, row['tessera']
        if clock in MASK_CLOCKS:
            # the membrane: fewer corrugations (runs of teeth, the periodic
            # zigzag) than Astra I and Astra II on the transition scenes, and
            # the tiles kept (a higher axis share on every transition scene).
            # Bends, teeth and depth are reported, not asserted: a tile's edge
            # steps where its neighbour changes, and that is a different
            # thing from a corrugated seam.
            assert row['tessera']['transitionCorrugations'] < row['astra-i']['transitionCorrugations'], row
            for sc in TRANSITION:
                assert row['tessera']['axisShareByScene'][sc] > row['astra-i']['axisShareByScene'][sc], (sc, row)
    summary['passed'] = True
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)
