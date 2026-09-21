const fs=require('node:fs'), {performance}=require('node:perf_hooks');
let js=fs.readFileSync(require('node:path').join(__dirname,'../../selvedge.html'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const end=js.lastIndexOf('})();');
js=js.slice(0,end)+'return {scenes,computeDiagram,solveWeights,convexPlanes,ringArea,clipHalfPlane};'+js.slice(end);
const noop=()=>{},el={addEventListener:noop,style:{},classList:{toggle:noop},getContext:()=>({setTransform:noop}),parentElement:{getBoundingClientRect:()=>({width:1900,height:810})}};
const K=Function('document','window','requestAnimationFrame','performance','return '+js.trim())({readyState:'loading',addEventListener:noop,getElementById:()=>el,querySelectorAll:()=>[]},{addEventListener:noop,devicePixelRatio:1},noop,performance);
const W=1900,H=810,C=12,R=5,PW=W/C,PH=H/R;
const bounds=[[0,0],[W,0],[W,H],[0,H]], box=r=>[[r[0],r[1]],[r[2],r[1]],[r[2],r[3]],[r[0],r[3]]];
const scale=r=>r.map((v,i)=>v*(i%2?PH:PW)),center=r=>[(r[0]+r[2])/2,(r[1]+r[3])/2],area=r=>(r[2]-r[0])*(r[3]-r[1]);
function metric(diag,n,vr){let a=0,inter=0;for(const c of diag.cells.slice(n)){for(const pc of c.pieces||[c]){a+=Math.abs(K.ringArea(pc.pts));let p=pc;for(const [ax,ay,b]of [[-1,0,-vr[0]],[1,0,vr[2]],[0,-1,-vr[1]],[0,1,vr[3]]])if(p.pts.length)p=K.clipHalfPlane(p,ax,ay,b,-1);inter+=Math.abs(K.ringArea(p.pts));}}return 100*(a+area(vr)-2*inter)/area(vr);}
function outside(v){return [[0,0,W,v[1]],[0,v[3],W,H],[0,v[1],v[0],v[3]],[v[2],v[1],W,v[3]]].filter(r=>area(r)>1).map(r=>K.convexPlanes(box(r)));}
function adjacent(rects,v){const out=[],over=(a,b,c,d)=>Math.min(b,d)>Math.max(a,c)+1e-6;
rects.forEach((r,i)=>{if(Math.abs(r[2]-v[0])<1e-6&&over(r[1],r[3],v[1],v[3]))out.push({i,axis:0,edge:v[0],sign:1});
if(Math.abs(r[0]-v[2])<1e-6&&over(r[1],r[3],v[1],v[3]))out.push({i,axis:0,edge:v[2],sign:-1});
if(Math.abs(r[3]-v[1])<1e-6&&over(r[0],r[2],v[0],v[2]))out.push({i,axis:1,edge:v[1],sign:1});
if(Math.abs(r[1]-v[3])<1e-6&&over(r[0],r[2],v[0],v[2]))out.push({i,axis:1,edge:v[3],sign:-1});});return out;}
if(require.main===module)for(const scene of ['sidebar','hero','frame']){
const sp=K.scenes[scene](C,R,12),rects=sp.content.map(scale),v=scale(sp.voids.at(-1)),seeds=rects.map(center),claims=rects.map(area),n=seeds.length;
const adj=adjacent(rects,v),vc=center(v),spanSeeds=[];
for(const a of adj){const p=vc.slice();p[1-a.axis]=Math.max(v[1-a.axis]+.01,Math.min(v[3-a.axis]-.01,seeds[a.i][1-a.axis]));if(!spanSeeds.some(q=>Math.hypot(q[0]-p[0],q[1]-p[1])<.1))spanSeeds.push(p);}
const vd=K.computeDiagram(spanSeeds,spanSeeds.map(()=>0),box(v));
const span=K.solveWeights(seeds.concat(spanSeeds),claims.concat([...vd.areas]),bounds,null,{maxIter:100});
console.log(JSON.stringify({scene,variant:'disjoint-bands',error:metric(span.diagram,n,v),residual:span.maxRelErr}));
const ref=K.solveWeights(seeds,claims,bounds,null,{maxIter:100,tris:outside(v),domainArea:W*H-area(v)});
for(const mode of ['reflect','inside']){
const gs=[],gw=[];
for(const a of adj){const p=seeds[a.i].slice(),d=Math.abs(p[a.axis]-a.edge),g=mode==='reflect'?d:Math.min(d,(v[a.axis+2]-v[a.axis])*.45);p[a.axis]=a.edge+a.sign*g;
if(p[1-a.axis]<v[1-a.axis]||p[1-a.axis]>v[3-a.axis])continue;
if(gs.some(q=>Math.hypot(q[0]-p[0],q[1]-p[1])<.1))continue;
gs.push(p);gw.push(ref.weights[a.i]+g*g-d*d);}
const d=K.computeDiagram(seeds.concat(gs),[...ref.weights,...gw],bounds);
console.log(JSON.stringify({scene,variant:mode,error:metric(d,n,v),contentError:Math.max(...claims.map((x,i)=>Math.abs(d.areas[i]-x)/x)),sites:gs.length}));
}
}
module.exports={K,metric,box,outside,adjacent};
