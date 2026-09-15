"""Same release geometry with planned bows or exterior admission disabled."""
from pathlib import Path
import json, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'astra3-results'
source=(ROOT/'astra-iii.html').read_text();results={}
with tempfile.TemporaryDirectory(prefix='astra3-controls-') as tmp:
    for name,options in [('no-buffer',{'buffer':False}),('no-arcs',{'arcs':False})]:
        p=Path(tmp)/(name+'.html');p.write_text(source.replace('<script>','<script>window.__ASTRA_III_OPTIONS='+json.dumps(options)+';</script><script>',1))
        dest=OUT/(name+'-strobe-30ms.json')
        with (OUT/(name+'.log')).open('w') as log:subprocess.run(['node',str(ROOT/'probe-runtime/strobe.js'),str(p),str(dest),'--dt','30','--frames','184','--parkx','-1000','--parky','-1000'],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        d=json.loads(dest.read_text());assert not d.get('pageErrors');results[name]={'options':options,'transitionShapeEvents':sum(v for k,v in d['teleportByScene'].items() if k!='flock0'),'byScene':d['teleportByScene']}
(OUT/'controls.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
