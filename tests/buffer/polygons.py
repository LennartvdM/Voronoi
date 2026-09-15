"""Independently integrate captured world polygons; reject detached storage."""
from pathlib import Path
import json
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'buffer-results'
data=json.loads((OUT/'witness.json').read_text());assert not data['errors'];rows=[]
for s in data['states']:
    viewport=box(0,0,s['W'],s['H']);world=Polygon(s['bounds']);groups={};void={}
    for c in s['cells']:
        if c['id'] is None:continue
        void[c['id']]=c['isVoid']
        for points in c['pieces']:
            if len(points)<3:continue
            p=Polygon(points);assert p.is_valid,(s['scene'],c['id'],'invalid polygon')
            groups.setdefault(c['id'],[]).append(p)
    unions={i:unary_union(p) for i,p in groups.items()};combined=unary_union(list(unions.values()))
    stored=content=detached=0.;body=[]
    for i,p in unions.items():
        outside=p.difference(viewport).area;stored+=outside
        if not void[i]:content+=outside
        # Only numerical edge contacts are bridged. Area metrics above use
        # untouched polygons. Detached storage must not pass as spilling.
        connection=p.buffer(1e-7)
        components=list(connection.geoms) if hasattr(connection,'geoms') else [connection]
        isolated=sum(c.difference(viewport).area for c in components if c.intersection(viewport).area<1e-8)
        detached+=isolated;body.append({'id':i,'outsidePx2':outside,'detachedOutsidePx2':isolated})
    row={'scene':s['scene'],'frame':s['f'],'outsidePx2':stored,'contentOutsidePx2':content,'detachedOutsidePx2':detached,
         'storageCreditErrorPx2':abs(stored-s['credit']),'viewportGapPx2':viewport.difference(combined).area,
         'overlapPx2':max(0,sum(p.area for p in unions.values())-combined.area),
         'reservePx2':world.difference(combined).area,'bodies':body}
    assert row['viewportGapPx2']<.01 and row['overlapPx2']<.01,row
    assert row['storageCreditErrorPx2']<1.5 and detached<.01,row
    rows.append(row)
(OUT/'polygon-witness.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
