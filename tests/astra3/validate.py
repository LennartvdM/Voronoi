"""Five-clock before/after validation. Raw regressions are retained."""
from pathlib import Path
import hashlib, json, math, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'astra3-results';OUT.mkdir(exist_ok=True)
subprocess.run([sys.executable,str(ROOT/'tests/astra3/probes.py')],check=True)
clocks=[('240hz',1000/240,0),('120hz',1000/120,0),('60hz',1000/60,0),('30ms',30,0),('jitter',25,12)]
selected=os.environ.get('ASTRA_CLOCKS')
if selected:clocks=[c for c in clocks if c[0] in selected.split(',')]
summary={'referenceSHA256':hashlib.sha256((ROOT/'astra-i.html').read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256((ROOT/'astra-iii.html').read_bytes()).hexdigest(),'viewport':[1440,900],'pointer':[-1000,-1000],'warmupMs':3600,'sceneHoldMs':5500,'clocks':{},'passedGeometry':False}
for name,dt,jit in clocks:
    row=summary['clocks'][name]={}
    for build in ['astra-i','astra-iii']:
        vals={}
        probes=['score']+(['strobe'] if name!='120hz' else [])+(['flicker'] if name in ['60hz','30ms','jitter'] else [])
        for probe in probes:
            stem=f'{build}-{probe}-{name}';dest=OUT/(stem+'.json')
            cmd=['node',str(ROOT/'probe-runtime'/f'{probe}.js'),str(ROOT/(build+'.html')),str(dest),'--dt',str(dt),'--jitter',str(jit),'--frames',str(math.ceil(5500/dt)),'--parkx','-1000','--parky','-1000']
            print('RUN',stem,flush=True)
            with (OUT/(stem+'.log')).open('w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            vals[probe]=json.loads(dest.read_text());assert not vals[probe].get('pageErrors'),stem
        s=vals['score'];r=row[build]={'transitionAreaJumps':sum(v for k,v in s['byScene'].items() if k!='flock0'),'byScene':s['byScene'],'vanish':s['vanish'],'gapMax':s['gapMax'],'overMax':s['overMax'],'settledScenes':s['settledScenes'],'relativeQuotaResidualMax':s['errMax'],'msP50':s['msP50'],'msP95':s['msP95']}
        if 'strobe' in vals:
            t=vals['strobe'];r['shapeEventsByScene']=t['teleportByScene'];r['transitionShapeEvents']=sum(v for k,v in t['teleportByScene'].items() if k!='flock0')
        if 'flicker' in vals:
            f=vals['flicker'];r['shapeBackShare']=f['shapeBackShare'];r['flickerByScene']=f['scenes']
        if build=='astra-iii':
            assert s['vanish']==0 and s['gapMax']==0 and s['overMax']==0,(name,r)
            assert s['errMax']<=1.01e-6 and s['settledScenes']=='5/5',(name,r)
summary['regressions']=[]
for name,row in summary['clocks'].items():
    for metric in ['transitionAreaJumps','transitionShapeEvents','shapeBackShare','msP95']:
        if metric in row['astra-i'] and row['astra-iii'][metric]>row['astra-i'][metric]:summary['regressions'].append({'clock':name,'metric':metric,'before':row['astra-i'][metric],'after':row['astra-iii'][metric]})
summary['passedGeometry']=True
(OUT/('summary'+('-'+selected if selected else '')+'.json')).write_text(json.dumps(summary,indent=2))
print(json.dumps(summary),flush=True)
