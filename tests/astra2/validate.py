"""Validate the new mark without concealing tradeoffs in a generic green score."""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'astra2-results'
OUT.mkdir(exist_ok=True)
PW = os.environ.get('PLAYWRIGHT_MODULE', '/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package')
CHROME = os.environ.get('CHROMIUM_PATH', '' if 'PLAYWRIGHT_MODULE' in os.environ else '/usr/bin/chromium')
CLOCKS = [('240hz', 1000/240, 0), ('120hz', 1000/120, 0), ('60hz', 1000/60, 0), ('30ms', 30, 0), ('jitter', 25, 12)]

def run(cmd, name):
    with (OUT / (name + '.log')).open('w') as log:
        subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=600)
    return json.loads((OUT / (name + '.json')).read_text())

summary = {'referenceSHA256': hashlib.sha256((ROOT/'astra-i.html').read_bytes()).hexdigest(),
           'candidateSHA256': hashlib.sha256((ROOT/'astra-ii.html').read_bytes()).hexdigest(),
           'warmupMs': 3600, 'sceneHoldMs': 5500, 'pointer': [-1000, -1000],
           'viewport': [1440, 900], 'clocks': {}, 'regressions': [],
           'geometryAndDepartureChecksPassed': False}
with tempfile.TemporaryDirectory(prefix='astra2-probes-') as tmp:
    probes = Path(tmp)
    for name in ['score', 'strobe', 'flicker']:
        text = (ROOT/'.claude/gauntlet'/(name+'.js')).read_text()
        text = text.replace('/opt/node22/lib/node_modules/playwright', PW)
        text = text.replace("executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',", ('executablePath: '+json.dumps(CHROME)+',') if CHROME else '')
        text = text.replace('await p.addInitScript(CLOCK);', 'await p.evaluate(CLOCK);')
        text = text.replace("await p.goto('file://' + dst);", "await p.setContent(fs.readFileSync(dst, 'utf8'));")
        text = text.replace('X.setMouse(700, 400)', 'X.setMouse(-1000, -1000)')
        text = text.replace('window.__advance = (n) => {', 'window.__warmup = Math.ceil(3600 / DT); window.__advance = (n) => {')
        text = text.replace('for (let i = 0; i < 120; i++) step();', 'for (let i = 0; i < window.__warmup; i++) step();')
        (probes/(name+'.js')).write_text(text)
    for clock, dt, jitter in CLOCKS:
        row = summary['clocks'][clock] = {}
        for build in ['astra-i', 'astra-ii']:
            tests = ['score'] + (['strobe'] if clock != '120hz' else []) + (['flicker'] if clock in ['60hz','30ms','jitter'] else [])
            row[build] = {}
            for test in tests:
                tag = f'{build}-{test}-{clock}'
                print('RUN', tag, flush=True)
                cmd = ['node', str(probes/(test+'.js')), str(ROOT/(build+'.html')), str(OUT/(tag+'.json')),
                       '--dt',str(dt),'--jitter',str(jitter),'--frames',str(math.ceil(5500/dt)),'--parkx','-1000','--parky','-1000']
                data = run(cmd, tag)
                assert not data.get('pageErrors'), (tag, data)
                if test == 'score':
                    row[build].update({k:data[k] for k in ['jumps','byScene','vanish','gapMax','overMax','settledScenes','errMax','msP50','msP95']})
                    row[build]['transitionJumps'] = sum(v for k,v in data['byScene'].items() if k!='flock0')
                    if build == 'astra-ii':
                        assert data['vanish']==0 and data['gapMax']==0 and data['overMax']==0, (tag,data)
                        assert data['settledScenes']=='5/5' and data['errMax']<=1.01e-6, (tag,data)
                elif test == 'strobe':
                    row[build]['teleportsByScene']=data['teleportByScene']
                    row[build]['transitionTeleports']=sum(v for k,v in data['teleportByScene'].items() if k!='flock0')
                    row[build]['churnShareMean']=data['churnShareMean']
                else:
                    row[build]['shapeBackShare']=data['shapeBackShare']
                    row[build]['flickerByScene']=data['scenes']
            if build=='astra-ii':
                for measure in ['transitionJumps','transitionTeleports','shapeBackShare']:
                    if measure in row[build] and row[build][measure]>row['astra-i'][measure]:
                        summary['regressions'].append({'clock':clock,'measure':measure,'reference':row['astra-i'][measure],'candidate':row[build][measure]})
    summary['departure']={}
    for build in ['astra-i','astra-ii']:
        tag=build+'-departure'
        summary['departure'][build]=run(['node','tests/astra2/audit.js',build+'.html',str(OUT/(tag+'.json')),str(1000/120)],tag)
    old=summary['departure']['astra-i']; new=summary['departure']['astra-ii']
    assert not old['errors'] and not new['errors']
    before=sum(r['meanPrematureContraction'] for r in old['results'] if r['scene']!='flock')
    after=sum(r['meanPrematureContraction'] for r in new['results'] if r['scene']!='flock')
    assert after < before*.5, (before,after)
    for r in new['results']:
        assert not r['identityErrors'] and not r['duplicateRoles'] and not r['unfinished'], r
        assert r['maxQuotaImbalance']<1e-8 and r['minVisibleAreaPx2']>=1, r
        assert all(e['positionJump']==0 and e['velocityJump']==0 for e in r['swaps']),r
    assert max(r['maxOutsidePx'] for r in new['results'])>1, 'Spill policy did not actually leave the viewport'
    summary['stress']=run(['node','tests/astra2/stress.js','astra-ii.html',str(OUT/'stress.json')],'stress')
    for case in summary['stress']:
        assert not case['errors'],case
        for phase in case['result']:
            assert not phase['vanish'] and not phase['invalid'] and not phase['roles'],phase
            assert phase['maxPositionJump']==0 and phase['maxVelocityJump']==0,phase
            if not phase['label'].startswith('interrupt-') and phase['label']!='release':
                assert phase['unseated']==0,phase
    # Raw raster warnings are retained. Every flagged sample is checked geometrically,
    # not only the largest raster count (a near-edge sample can exaggerate a tiny seam).
    from shapely.geometry import Polygon,box
    from shapely.ops import unary_union
    summary['coverageSeams']=[]
    for path in OUT.glob('stress-*-coverage.json'):
        for rec in json.loads(path.read_text()):
            domain=box(0,0,rec['W'],rec['H']); parts=[]
            for loops in rec['leaves']:
                outer=[];holes=[]
                for loop in loops:
                    poly=Polygon(loop['pts'])
                    assert poly.is_valid,(path.name,rec['label'],rec['k'],'invalid polygon')
                    (holes if loop['hole'] else outer).append(poly)
                parts.append(unary_union(outer).difference(unary_union(holes)).intersection(domain))
            combined=unary_union(parts)
            gap=domain.difference(combined).area;over=max(0,sum(p.area for p in parts)-combined.area)
            summary['coverageSeams'].append({'source':path.name,'phase':rec['label'],'frame':rec['k'],'rasterGapPx2':rec['gap'],'rasterOverlapPx2':rec['over'],'polygonGapPx2':gap,'polygonOverlapPx2':over})
            assert gap<.1 and over<.1,(path.name,rec['label'],rec['k'],gap,over)
summary['geometryAndDepartureChecksPassed']=True
summary['allRecordedMotionMeasuresImproved']=not summary['regressions']
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2),flush=True)
