"""Apply explicit gates to audits and retain all recorded regressions."""
from pathlib import Path
import hashlib, json
from measure import audit, stress
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'astra3-results'
s=json.loads((OUT/'summary.json').read_text())
assert set(s['clocks'])=={'240hz','120hz','60hz','30ms','jitter'}
assert s['candidateSHA256']==hashlib.sha256((ROOT/'astra-iii.html').read_bytes()).hexdigest()
s['controls']=json.loads((OUT/'controls.json').read_text())
s['unit']=json.loads((OUT/'unit.json').read_text())
s['ui']=json.loads((OUT/'ui.json').read_text())
s['stress']=json.loads((OUT/'stress.json').read_text())
for c in s['stress']:
    assert not c['errors'],c
    for p in c['result']:
        assert p['vanish']==0 and p['invalid']==0 and p['roles']==0,p
        assert p['err']<=1.01e-6 and p['areaError']<1,p
        if not p['label'].startswith('interrupt-') and p['label']!='release':assert p['unseated']==0,p
s['stressPolygonChecks']=stress(OUT/'stress.json')
s['visualAudit']={name:audit(OUT/(name+'-audit.json')) for name in ['astra-i','astra-iii']}
for a in s['visualAudit'].values():
    assert a['sha256'] in [s['candidateSHA256'],s['referenceSHA256']],a['sha256']
candidate=s['visualAudit']['astra-iii']['scenes']
assert any(c['contentOutsideMax']>1000 and c['dressedCrossingLeavesMax']>0 for c in candidate)
assert all(c['outsideAtEnd']==0 for c in candidate)
assert sum(c['curvedPlans'] for c in candidate)>0
for c in candidate:
    for p in c['polygonWitness']:assert p['outsideDiscrepancy']<1,p
reference=s['visualAudit']['astra-i']['scenes']
assert sum(c['deformOver10PctBefore3px'] for c in candidate)<sum(c['deformOver10PctBefore3px'] for c in reference)
s['departureMetricScope']='During the first 150 ms after each scene change; compare actual outer contours to rigid translation of the previous contour, before centre travel exceeds 3 px. This is not an audit of every later individual departure.'
s['numericalScope']='Quota residuals refer to the shared piecewise-affine mesh field, not the analytic continuous field or the gapped ink. Coverage raster sampled every sixth frame; flagged stress samples independently integrated.'
s['legacyProbeCaution']='Old spring-carrot fight/lag fields are not applicable to the analytic arc planner. Shape masks, area and coverage remain applicable.'
for clock,row in s['clocks'].items():
    a=row['astra-i'].get('shapeEventsByScene',{});b=row['astra-iii'].get('shapeEventsByScene',{})
    for scene in sorted(set(a)|set(b)):
        if scene!='flock0' and b.get(scene,0)>a.get(scene,0):
            item={'clock':clock,'metric':'transitionShapeEvents','scene':scene,'before':a.get(scene,0),'after':b.get(scene,0)}
            if item not in s['regressions']:s['regressions'].append(item)
s['allRecordedMeasuresImproved']=not s['regressions']
s['validationPassed']=True
(OUT/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps({'validationPassed':True,'regressions':s['regressions'],'stressPolygonChecks':s['stressPolygonChecks']}))
