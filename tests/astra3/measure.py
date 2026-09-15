"""Independent polygon accounting and rigid-transport departure comparison."""
from pathlib import Path
import json, math
from shapely.geometry import Polygon, box, GeometryCollection
from shapely import make_valid, affinity
from shapely.ops import unary_union

def material(loops):
    # XOR preserves positive islands inside holes. Loops describe one partition.
    g = GeometryCollection()
    for lp in sorted(loops, key=lambda l: -abs(Polygon(l['pts']).area)):
        if len(lp['pts']) >= 3:
            g = g.symmetric_difference(make_valid(Polygon(lp['pts'])))
    return g

def audit(file):
    data = json.loads(Path(file).read_text()); result=[]
    assert not data['errors'], data['errors']
    for sc in data['scenes']:
        old = {b['id']: b for b in sc['source']}; deform={}; witness=[]
        shapes = {i: material(b['loops']) for i,b in old.items()}
        for frame in sc['early']:
            for b in frame['bodies']:
                if b['id'] not in old: continue
                a=old[b['id']];d=math.hypot(b['x']-a['x'],b['y']-a['y'])
                if d > 3: continue
                g=affinity.translate(material(b['loops']),a['x']-b['x'],a['y']-b['y'])
                rate=g.symmetric_difference(shapes[b['id']]).area/max(1,shapes[b['id']].area)
                deform[b['id']]=max(deform.get(b['id'],0),rate)
        if sc['peak']:
            crop=box(0,0,sc['width'],sc['height'])
            for b in sc['peak']['bodies']:
                g=material(b['loops']);visible=g.intersection(crop).area;outside=g.difference(crop).area
                recorded=next((q for q in sc['peak']['storage'] if q['id']==b['id']),None)
                if recorded: witness.append({'id':b['id'],'total':g.area,'visible':visible,'outside':outside,'outsideDiscrepancy':abs(outside-recorded['outside'])})
        result.append({'scene':sc['scene'],'observedBodies':len(deform),'deformOver10PctBefore3px':sum(v>.1 for v in deform.values()),'maxDeformation':max(deform.values(),default=0),'perBodyDeformation':deform,'contentOutsideMax':sc['maxContentOutside'],'dressedCrossingLeavesMax':sc['maxDressedCrossingLeaves'],'outsideAtEnd':sc['outsideAtEnd'],'curvedPlans':sum(p['bend']>1 for p in sc['arcPlans']),'polygonWitness':witness})
    return {'sha256':data['sha256'],'scenes':result}

def stress(prefix):
    results=[]
    for file in Path(prefix).parent.glob(Path(prefix).stem+'-*-coverage.json'):
        for c in json.loads(file.read_text()):
            crop=box(0,0,c['W'],c['H']);gs=[material(l).intersection(crop) for l in c['leaves']];u=unary_union(gs)
            row={'file':file.name,'phase':c['label'],'frame':c['k'],'rasterGap':c['gap'],'rasterOverlap':c['over'],'polygonGap':c['W']*c['H']-u.area,'polygonOverlap':sum(g.area for g in gs)-u.area};results.append(row)
            assert row['polygonGap']<.3 and row['polygonOverlap']<.3, row
    return results

if __name__=='__main__':
    import sys
    a=audit(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(a,indent=2));print(json.dumps(a))
