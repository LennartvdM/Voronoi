// Run the shipped inline engines unchanged; the DOM and renderer are stubbed.
// These measurements screen geometry and discontinuities, not aesthetic quality.
const {loadEngine,measures,displacement}=require('./probe.cjs');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..'),names=['selvedge','harbor','quay'];
const scenes=['flock','bento','hero','sidebar','frame'];
const area=p=>Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-a[1]*b[0];},0)/2);
function clip(p,axis,value,sign){const out=[];for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length],da=sign*(a[axis]-value),db=sign*(b[axis]-value);if(da>=0)out.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}}return out;}
function voidError(h){let sum=0,total=0,maxEdge=0;for(const b of h.bodies){if(!b.isVoid||b.leaving||!b.rect)continue;const r=b.rect.map((x,i)=>x*(i%2?h.PH:h.PW)),target=(r[2]-r[0])*(r[3]-r[1]);let owned=0,inside=0;
 h.solvedSubs.forEach((s,i)=>{if(s.body!==b)return;const c=h.solved.diagram.cells[i];for(const pc of c.pieces||[c]){owned+=area(pc.pts);let p=pc.pts;for(const [a,k,sign]of[[0,r[0],1],[0,r[2],-1],[1,r[1],1],[1,r[3],-1]])p=clip(p,a,k,sign);inside+=area(p);}});
 for(const p of b.loops||[])for(let i=0;i<p.length;i++)for(const t of[0,.25,.5,.75]){const a=p[i],z=p[(i+1)%p.length],x=a[0]+t*(z[0]-a[0]),y=a[1]+t*(z[1]-a[1]);maxEdge=Math.max(maxEdge,Math.min(Math.abs(x-r[0]),Math.abs(x-r[2]),Math.abs(y-r[1]),Math.abs(y-r[3])));}
 sum+=Math.max(0,owned+target-2*inside);total+=target;
 }return total?{pct:100*sum/total,edgePx:maxEdge}:null;}
function advance(e,dt,seconds){for(let i=0;i<Math.ceil(seconds/dt);i++)e.advance(dt);}
function engine(name,w=1900,h=810,n=12){return loadEngine(path.join(ROOT,name+'.html'),w,h,.55,n);}
function inspect(h){let missing=0,maxCorners=0,nonconvex=0,minFat=1;for(const b of h.bodies){if(b.isSelf||b.isVoid||b.leaving)continue;if(!b.loops?.length){missing++;continue;}assert.equal(b.subs.length,1,'visible body became a lattice');for(const p of b.loops){let pos=false,neg=false,per=0;maxCorners=Math.max(maxCorners,p.length);for(let i=0;i<p.length;i++){const a=p[i],z=p[(i+1)%p.length],q=p[(i+2)%p.length];assert(a.every(Number.isFinite));const cross=(z[0]-a[0])*(q[1]-z[1])-(z[1]-a[1])*(q[0]-z[0]);pos||=cross>1e-4;neg||=cross< -1e-4;per+=Math.hypot(z[0]-a[0],z[1]-a[1]);}nonconvex+=pos&&neg?1:0;minFat=Math.min(minFat,4*Math.PI*area(p)/(per*per));}}
 assert.equal(h.walls.length,0);assert.equal(h.holes.length,0);return {missing,maxCorners,nonconvex,minFat};}
function outlines(h){const m=measures(h),out=new Map();for(const b of h.bodies){const c=m.get(b.id);if(c&&b.loops?.length===1)out.set(b.id,b.loops[0].map(p=>[p[0]-c.x,p[1]-c.y]));}return out;}
function intersection(a,b){let out=a;const sign=b.reduce((s,p,i)=>{const q=b[(i+1)%b.length];return s+p[0]*q[1]-p[1]*q[0];},0)>0?1:-1;for(let j=0;j<b.length&&out.length;j++){const p=b[j],q=b[(j+1)%b.length],next=[];const value=a=>sign*((q[0]-p[0])*(a[1]-p[1])-(q[1]-p[1])*(a[0]-p[0]));for(let i=0;i<out.length;i++){const a=out[i],z=out[(i+1)%out.length],da=value(a),db=value(z);if(da>=0)next.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);next.push([a[0]+t*(z[0]-a[0]),a[1]+t*(z[1]-a[1])]);}}out=next;}return area(out);}
function reshape(a,b){let worst=0,events=0;for(const[id,p]of a){const q=b.get(id);if(!q)continue;const A=area(p),B=area(q),change=Math.max(0,(A+B-2*intersection(p,q))/Math.max(A,B,1));worst=Math.max(worst,change);if(change>.12)events++;}return {worst,events};}
const geometry=[],transitions=[],interruptions=[],resizes=[];
for(const [w,h,n]of[[1900,810,12],[1440,620,24],[390,760,12],[1900,810,30],[1900,810,13],[1900,810,4],[1900,810,7]])for(const scene of['hero','sidebar','frame']){
 const row={w,h,n,scene};for(const name of names){const e=engine(name,w,h,n);advance(e,.03,7);e.scene(scene);advance(e,.03,10);row[name]={void:voidError(e.root),...inspect(e.root),residual:e.root.solved?.maxRelErr,sites:e.root.solvedSubs.length};}
 geometry.push(row);console.log('geometry',w,h,n,scene,JSON.stringify(row));
}
if(!process.env.MF_GEOMETRY_ONLY){
 for(const dt of[1/60,.03])for(const from of scenes)for(const to of scenes){if(from===to)continue;const row={dt,from,to};for(const name of names){const e=engine(name);advance(e,dt,7);if(from!=='bento'){e.scene(from);advance(e,dt,7);}let prev=measures(e.root),shape=outlines(e.root);e.scene(to);e.advance(1e-6);const opening=displacement(prev,measures(e.root)).px;prev=measures(e.root);let maxMove=0,maxShape=0,shapeEvents=0,missing=0,nonconvex=0,maxCorners=0,maxResidual=0,minFat=1;for(let i=0;i<Math.ceil(7/dt);i++){e.advance(dt);const m=measures(e.root),s=outlines(e.root),r=reshape(shape,s),g=inspect(e.root);maxMove=Math.max(maxMove,displacement(prev,m).px);maxShape=Math.max(maxShape,r.worst);shapeEvents+=r.events;missing+=g.missing;nonconvex+=g.nonconvex;maxCorners=Math.max(maxCorners,g.maxCorners);minFat=Math.min(minFat,g.minFat);maxResidual=Math.max(maxResidual,e.root.solved?.maxRelErr||0);prev=m;shape=s;}row[name]={opening,maxMove,maxShape,shapeEvents,missing,nonconvex,maxCorners,minFat,maxResidual};}transitions.push(row);console.log('transition',dt,from,to,JSON.stringify(row));}
 for(const name of names)for(const delay of[.08,.23,.6]){const e=engine(name);advance(e,1/60,7);e.scene('frame');advance(e,1/60,7);const row={name,delay,maxOpening:0,missing:0};for(const to of ['hero','sidebar','frame','flock','bento']){const prev=measures(e.root);e.scene(to);e.advance(1e-6);row.maxOpening=Math.max(row.maxOpening,displacement(prev,measures(e.root)).px);advance(e,1/60,delay);row.missing+=inspect(e.root).missing;}advance(e,1/60,10);row.missing+=inspect(e.root).missing;interruptions.push(row);}
 for(const name of names)for(const scene of ['hero','frame']){const e=engine(name);advance(e,.03,7);e.scene(scene);advance(e,.03,8);e.root.fit([0,0,1440,720],[[0,0],[1440,0],[1440,720],[0,720]],true,0,0);advance(e,.03,10);resizes.push({name,scene,...inspect(e.root),void:voidError(e.root)});}
}
for(const row of geometry){
 assert.equal(row.harbor.missing,0,'Harbor lost content');
 if(row.scene==='sidebar')assert.deepEqual(row.harbor,row.selvedge,'Sidebar control changed');
 else if(row.harbor.void)assert(row.harbor.void.pct<.001,'Harbor resting void is not rectangular');
 else assert.equal(row.selvedge.void,null,'unexpected scene fallback');
}
for(const row of transitions){
 assert.equal(row.harbor.missing,0);assert.equal(row.harbor.nonconvex,0);
 if(['hero','sidebar','frame'].includes(row.from)&&['flock','bento'].includes(row.to))assert(row.harbor.opening<.25,'release discontinuity');
}
for(const row of resizes)if(row.name==='harbor')assert(row.void&&row.void.pct<.001,'resize lost the rectangle');
const laterRegressions=transitions.filter(r=>r.harbor.maxMove>1.1*r.selvedge.maxMove).map(r=>({dt:r.dt,from:r.from,to:r.to,baseline:r.selvedge.maxMove,harbor:r.harbor.maxMove}));
const hashes=Object.fromEntries(names.map(n=>[n,require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(ROOT,n+'.html'))).digest('hex')]));
const result={scope:'Actual root motion and nested-field simulation; renderer stubbed. Whole-transition shape change is measured. Visual selection requires Netlify.',hashes,selected:'harbor',geometryGatesPassed:true,allTransitionsImproved:laterRegressions.length===0,laterRegressions,geometry,transitions,interruptions,resizes};
fs.writeFileSync(path.join(__dirname,process.env.MF_GEOMETRY_ONLY?'geometry.json':'results.json'),JSON.stringify(result,null,2)+'\n');
console.log('Completed',geometry.length,'geometry cases,',transitions.length,'directed transition cases,',interruptions.length,'interruption sequences');
