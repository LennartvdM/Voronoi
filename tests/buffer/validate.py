"""Validate actual exterior storage and motion, retaining all regressions.

The legacy probes measure painted geometry. This validator separately audits
world-space polygons, reserve accounting and liveness. It never treats a lower
jump count as proof of a visually improved membrane.
"""
from pathlib import Path
import hashlib, json, math, os, subprocess, tempfile
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'buffer-results';OUT.mkdir(exist_ok=True)
PW=os.environ.get('PLAYWRIGHT_MODULE','/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package')
CHROME=os.environ.get('CHROMIUM_PATH','' if 'PLAYWRIGHT_MODULE' in os.environ else '/usr/bin/chromium')
CLOCKS=[('240hz',1000/240,0),('120hz',1000/120,0),('60hz',1000/60,0),('30ms',30,0),('jitter',25,12)]
select=os.environ.get('BUFFER_CLOCKS','').split(',')
if select!=['']: CLOCKS=[c for c in CLOCKS if c[0] in select]

def run(cmd,name,env=None):
    print('RUN',name,flush=True)
    with (OUT/(name+'.log')).open('w') as log:
        subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900,env=env)
    return json.loads((OUT/(name+'.json')).read_text())

summary={'referenceSHA256':hashlib.sha256((ROOT/'astra-ii.html').read_bytes()).hexdigest(),
         'candidateSHA256':hashlib.sha256((ROOT/'astra-buffer.html').read_bytes()).hexdigest(),
         'warmupMs':3600,'sceneHoldMs':5500,'pointer':[-1000,-1000],'viewport':[1440,900],
         'clocks':{},'controls':{},'regressions':[],'bufferAndGeometryChecksPassed':False}
with tempfile.TemporaryDirectory(prefix='true-buffer-') as tmp:
    probes=Path(tmp)
    for name in ['score','strobe','flicker']:
        s=(ROOT/'.claude/gauntlet'/(name+'.js')).read_text()
        s=s.replace('/opt/node22/lib/node_modules/playwright',PW)
        s=s.replace("executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',",('executablePath: '+json.dumps(CHROME)+',') if CHROME else '')
        s=s.replace('await p.addInitScript(CLOCK);','await p.evaluate(CLOCK);')
        s=s.replace("await p.goto('file://' + dst);","await p.setContent(fs.readFileSync(dst, 'utf8'));")
        s=s.replace('X.setMouse(700, 400)','X.setMouse(-1000, -1000)')
        s=s.replace('window.__advance = (n) => {','window.__warmup = Math.ceil(3600 / DT); window.__advance = (n) => {')
        s=s.replace('for (let i = 0; i < 120; i++) step();','for (let i = 0; i < window.__warmup; i++) step();')
        # Explicit control injection occurs before any app code, not by changing
        # solver thresholds or instrument logic.
        s=s.replace("await p.setContent(fs.readFileSync(dst, 'utf8'));","await p.evaluate(opts=>window.BUFFER_OPTIONS=opts,JSON.parse(process.env.BUFFER_TEST_OPTIONS||'{}'));\n  await p.setContent(fs.readFileSync(dst, 'utf8'));")
        (probes/(name+'.js')).write_text(s)
    for clock,dt,jit in CLOCKS:
        row=summary['clocks'][clock]={}
        for build in ['astra-ii','astra-buffer']:
            entry=row[build]={}
            tests=['score']+(['strobe'] if clock!='120hz' else [])+(['flicker'] if clock in ['60hz','30ms','jitter'] else [])
            for test in tests:
                tag=f'{build}-{test}-{clock}'
                cmd=['node',str(probes/(test+'.js')),build+'.html',str(OUT/(tag+'.json')),'--dt',str(dt),'--jitter',str(jit),'--frames',str(math.ceil(5500/dt)),'--parkx','-1000','--parky','-1000']
                d=run(cmd,tag); assert not d.get('pageErrors'),(tag,d)
                if test=='score':
                    entry.update({k:d[k] for k in ['jumps','byScene','vanish','gapMax','overMax','settledScenes','errMax','msP50','msP95']})
                    entry['transitionJumps']=sum(v for k,v in d['byScene'].items() if k!='flock0')
                    if build=='astra-buffer':
                        assert d['vanish']==0 and d['gapMax']==0 and d['overMax']==0,(tag,d)
                        assert d['settledScenes']=='5/5' and d['errMax']<=1.01e-6,(tag,d)
                elif test=='strobe':
                    entry['teleportsByScene']=d['teleportByScene'];entry['transitionTeleports']=sum(v for k,v in d['teleportByScene'].items() if k!='flock0');entry['churnShareMean']=d['churnShareMean']
                else: entry['shapeBackShare']=d['shapeBackShare'];entry['flickerByScene']=d['scenes']
        for metric in ['transitionJumps','transitionTeleports','shapeBackShare']:
            if row['astra-buffer'].get(metric,0)>row['astra-ii'].get(metric,0):summary['regressions'].append({'clock':clock,'metric':metric,'before':row['astra-ii'][metric],'after':row['astra-buffer'][metric]})
    for name,options in [('locked',{'locked':True}),('no-cascade',{'cascade':False})]:
        tag=name+'-strobe-30ms';env={**os.environ,'BUFFER_TEST_OPTIONS':json.dumps(options)}
        d=run(['node',str(probes/'strobe.js'),'astra-buffer.html',str(OUT/(tag+'.json')),'--dt','30','--frames','184','--parkx','-1000','--parky','-1000'],tag,env)
        assert not d.get('pageErrors');summary['controls'][name]={'options':options,'teleportsByScene':d['teleportByScene'],'transitionTeleports':sum(v for k,v in d['teleportByScene'].items() if k!='flock0')}
# The geometry audit is repeated for the locked reserve with the same route planner.
for name,options in [('audit',{}),('locked-audit',{'locked':True})]:
    d=run(['node','tests/buffer/audit.js','astra-buffer.html',str(OUT/(name+'.json')),str(1000/120)],name,{**os.environ,'BUFFER_TEST_OPTIONS':json.dumps(options)})
    assert not d['errors'];summary[name]=d['scenes']
    for row in d['scenes']:
        assert row['maxLedger']<1e-4 and row['maxVisibleError']<1e-4,row
        assert row['minVisible']>=1 and row['endOutside']==0 and row['endCredit']==0,row
        assert row['maxStorageError']<1.5 and row['maxQuotaError']<1.5,row
    if name=='audit':
        assert max(r['maxContentOutside'] for r in d['scenes'])>1000
        assert any(len(route['ids'])>=3 for r in d['scenes'] for route in r['routes']),'No multi-hop route exercised'
    else: assert max(r['maxOutside'] for r in d['scenes'])==0
summary['unit']=run(['node','tests/buffer/unit.js','astra-buffer.html',str(OUT/'unit.json')],'unit')
summary['stress']=run(['node','tests/buffer/stress.js','astra-buffer.html',str(OUT/'stress.json')],'stress')
for case in summary['stress']:
    assert not case['errors'],case
    for phase in case['result']:
        assert not phase['vanish'] and not phase['invalid'] and not phase['roles'],phase
        assert phase['maxPositionJump']==0 and phase['maxVelocityJump']==0,phase
        assert phase['maxLedger']<1e-4 and phase['err']<=1.01e-6,phase
        assert phase['maxQuotaError']<1.5 and phase['maxStorageError']<1.5,phase
        if not phase['label'].startswith('interrupt-') and phase['label']!='release':assert phase['unseated']==0,phase
summary['coverageSeams']=[]
for p in OUT.glob('stress-*-coverage.json'):
    for rec in json.loads(p.read_text()):
        domain=box(0,0,rec['W'],rec['H']);parts=[]
        for loops in rec['leaves']:
            outer=[];holes=[]
            for loop in loops:
                poly=Polygon(loop['pts']);assert poly.is_valid,(p.name,rec['label'],rec['k'],'invalid polygon')
                (holes if loop['hole'] else outer).append(poly)
            parts.append(unary_union(outer).difference(unary_union(holes)).intersection(domain))
        u=unary_union(parts);gap=domain.difference(u).area;over=max(0,sum(p.area for p in parts)-u.area)
        summary['coverageSeams'].append({'source':p.name,'phase':rec['label'],'frame':rec['k'],'rasterGapPx2':rec['gap'],'rasterOverlapPx2':rec['over'],'polygonGapPx2':gap,'polygonOverlapPx2':over})
        assert gap<.1 and over<.1,(p.name,rec['label'],rec['k'],gap,over)
summary['bufferAndGeometryChecksPassed']=True
summary['allRecordedMotionMeasuresImproved']=not summary['regressions']
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2),flush=True)
