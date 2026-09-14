"""Run the repository's picture probes in Chromium, with identical clocks.

Only runtime paths, transport and warmup duration are adapted. Thresholds and
picture metrics are the original probes'. A green job requires improvement
and invariant checks, not merely successful measurement commands.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'astra-results'
OUT.mkdir(exist_ok=True)
PW = os.environ.get('PLAYWRIGHT_MODULE', '/tmp/astra-runtime/node_modules/playwright')
CHROME = os.environ.get('CHROMIUM_PATH')
CLOCKS = [('240hz', 1000 / 240, 0), ('120hz', 1000 / 120, 0),
          ('60hz', 1000 / 60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]
selected = os.environ.get('ASTRA_CLOCKS', '').split(',')
if selected != ['']:
    CLOCKS = [c for c in CLOCKS if c[0] in selected]

with tempfile.TemporaryDirectory(prefix='astra-probes-') as tmp:
    probes = Path(tmp)
    for name in ['score', 'strobe', 'flicker']:
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
        for build in ['hive', 'astra-i']:
            # Full-frequency area/coverage sampling; mask probes at the three
            # display clocks. A separate 240 Hz mask run is retained in evidence.
            tests = ['score'] + (['strobe', 'flicker'] if clock in ['60hz', '30ms', 'jitter'] else [])
            for test in tests:
                name = f'{build}-{test}-{clock}'
                cmd = ['node', str(probes / (test + '.js')), str(ROOT / (build + '.html')),
                       str(OUT / (name + '.json')), '--dt', str(dt), '--jitter', str(jitter),
                       '--frames', str(math.ceil(5500 / dt)), '--parkx', '-1000', '--parky', '-1000']
                print('RUN', name, flush=True)
                with (OUT / (name + '.log')).open('w') as log:
                    subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=300)
                results[name] = json.loads((OUT / (name + '.json')).read_text())
                if results[name].get('pageErrors'):
                    raise AssertionError(f'{name}: JavaScript errors')
    summary = {'referenceBlob': '2c02b2dc66d05fb152feffcd952f18b4d39f3634',
               'candidateSHA256': hashlib.sha256((ROOT / 'astra-i.html').read_bytes()).hexdigest(),
               'warmupMs': 3600, 'sceneHoldMs': 5500, 'viewport': [1440, 900],
               'pointer': [-1000, -1000], 'clocks': {}, 'passed': False}
    for clock, _, _ in CLOCKS:
        row = summary['clocks'][clock] = {}
        for build in ['hive', 'astra-i']:
            a = results[f'{build}-score-{clock}']
            row[build] = {'jumpsIncludingStartup': a['jumps'],
                          'transitionJumps': sum(v for k, v in a['byScene'].items() if k != 'flock0'),
                          'byScene': a['byScene'], 'gapMax': a['gapMax'], 'overMax': a['overMax'],
                          'vanish': a['vanish'], 'settledScenes': a['settledScenes'],
                          'areaRelativeErrorMax': a['errMax']}
            if build == 'astra-i':
                assert a['vanish'] == 0 and a['pageErrors'] == 0, (clock, a)
                assert a['gapMax'] == 0 and a['overMax'] == 0, (clock, a)
                assert a['settledScenes'] == '5/5' and a['errMax'] <= 1.01e-6, (clock, a)
            if clock in ['60hz', '30ms', 'jitter']:
                t = results[f'{build}-strobe-{clock}']
                f = results[f'{build}-flicker-{clock}']
                row[build]['transitionTeleports'] = sum(v for k, v in t['teleportByScene'].items() if k != 'flock0')
                row[build]['teleportsByScene'] = t['teleportByScene']
                row[build]['shapeBackShare'] = f['shapeBackShare']
        assert row['astra-i']['transitionJumps'] <= row['hive']['transitionJumps'], row
        if clock in ['60hz', '30ms', 'jitter']:
            assert row['astra-i']['transitionTeleports'] < row['hive']['transitionTeleports'], row
            assert row['astra-i']['shapeBackShare'] < row['hive']['shapeBackShare'], row
    summary['passed'] = True
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)
