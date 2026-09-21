// Actual inline engines, with DOM/paint stubs. Motion metrics are diagnostics;
// live Netlify viewing remains the aesthetic test.
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const {loadEngine,measures}=require('./probe.cjs');
const ROOT=path.resolve(__dirname,'../..');
const files={harbor:path.join(__dirname,'harbor.html'),cadence:path.join(ROOT,'cadence.html')};
const scenes=['flock','bento','hero','sidebar','frame'];
const clocks={hz60:i=>1/60,ms30:i=>.03,jitter:i=>.025+.012*Math.sin(i*1.7)};
const advance=(e,seconds,dt=.03)=>{for(let t=0;t<seconds;t+=dt)e.advance(dt);};
const percentile=(a,p)=>a.length?[...a].sort((x,y)=>x-y)[Math.min(a.length-1,Math.floor(a.length*p))]:0;
const area=p=>Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-a[1]*b[0];},0)/2);
function clip(p,axis,value,sign){const out=[];for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length],da=sign*(a[axis]-value),db=sign*(b[axis]-value);if(da>=0)out.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}}return out;}
function rectangleError(h){let sum=0,total=0;for(const b of h.bodies){if(!b.isVoid||b.leaving||!b.rect)continue;const r=b.rect.map((x,i)=>x*(i%2?h.PH:h.PW)),target=(r[2]-r[0])*(r[3]-r[1]);let owned=0,inside=0;
 h.solvedSubs.forEach((s,i)=>{if(s.body!==b)return;const cell=h.solved.diagram.cells[i];for(const pc of cell.pieces||[cell]){owned+=area(pc.pts);let p=pc.pts;for(const [axis,v,sign]of[[0,r[0],1],[0,r[2],-1],[1,r[1],1],[1,r[3],-1]])p=clip(p,axis,v,sign);inside+=area(p);}});sum+=Math.max(0,owned+target-2*inside);total+=target;}return total?100*sum/total:null;}
function check(h){assert.equal(h.walls.length,0);assert.equal(h.holes.length,0);for(const b of h.bodies){if(b.isVoid||b.isSelf||b.leaving)continue;assert.equal(b.subs.length,1);assert(b.loops?.length,'missing cell');assert([b.x,b.y,b.claim,b.progress].every(Number.isFinite));for(const p of b.loops)for(const q of p)assert(q.every(Number.isFinite));}}
function run(name,from,to,clock){
 const e=loadEngine(files[name],1900,810,.55,12);advance(e,10);if(from!=='bento'){e.scene(from);advance(e,16);}
 let prev=measures(e.root),last=new Map(e.root.bodies.map(b=>[b.id,{x:b.x,y:b.y,vx:b.vx,vy:b.vy}]));
 e.scene(to);const delays=e.root.bodies.filter(b=>!b.isVoid&&!b.leaving).map(b=>b.journey?.delay||0),cut=percentile(delays,.75);
 const late=new Set(e.root.bodies.filter(b=>!b.isVoid&&!b.leaving&&(b.journey?.delay||0)>=cut).map(b=>b.id));
 let opening=0,seedPeak=0,lateSeedPeak=0,cellPeak=0,lateCellPeak=0,fastBodySeconds=0,lateFastBodySeconds=0,accelPeak=0,finish=0,maxSlip=0,previousProgress=new Map();const seedSpeeds=[],cellSpeeds=[],lateSpeeds=[];
 e.advance(1e-6);for(const[id,p]of prev){const q=measures(e.root).get(id);if(q)opening=Math.max(opening,Math.hypot(q.x-p.x,q.y-p.y));}prev=measures(e.root);
 let elapsed=0,i=0;
 while(elapsed<16){const dt=clocks[clock](i++);elapsed+=dt;e.advance(dt);check(e.root);const now=measures(e.root);let active=false;
  for(const b of e.root.bodies){if(b.isVoid||b.isSelf||b.leaving)continue;const a=last.get(b.id),p=prev.get(b.id),q=now.get(b.id),speed=a?Math.hypot(b.x-a.x,b.y-a.y)/dt:0,cs=p&&q?Math.hypot(q.x-p.x,q.y-p.y)/dt:0;
   const travelling=!!b.path&&(b.journey||Math.hypot(b.x-b.path.ex,b.y-b.path.ey)>2);
   if(travelling||to==='flock'){seedSpeeds.push(speed);cellSpeeds.push(cs);seedPeak=Math.max(seedPeak,speed);cellPeak=Math.max(cellPeak,cs);if(speed>500)fastBodySeconds+=dt;if(a)accelPeak=Math.max(accelPeak,Math.hypot(b.vx-a.vx,b.vy-a.vy)/dt);if(late.has(b.id)){lateSpeeds.push(speed);lateSeedPeak=Math.max(lateSeedPeak,speed);lateCellPeak=Math.max(lateCellPeak,cs);if(speed>500)lateFastBodySeconds+=dt;}}
   const j=b.journey;if(j?.cadence){const old=previousProgress.get(b.id)||0;assert(b.progress>=old-1e-12,'clock ran backwards');previousProgress.set(b.id,b.progress);assert(j.cadence.rate>0&&j.cadence.rate<=1.0000001);maxSlip=Math.max(maxSlip,j.cadenceSlip);}
   active||=!!j&&b.progress<.999999;
  }
  if(active)finish=elapsed;prev=now;last=new Map(e.root.bodies.map(b=>[b.id,{x:b.x,y:b.y,vx:b.vx,vy:b.vy}]));
 }
 assert(finish<15,'journey failed to finish');
 const voidPct=rectangleError(e.root);if(['hero','frame'].includes(to)&&voidPct!==null)assert(voidPct<.001,'resting rectangle changed');
 return {opening,seedPeak,lateSeedPeak,seedP95:percentile(seedSpeeds,.95),lateSeedP95:percentile(lateSpeeds,.95),cellPeak,lateCellPeak,cellP95:percentile(cellSpeeds,.95),fastBodySeconds,lateFastBodySeconds,accelPeak,finish,maxSlip,voidPct};
}
module.exports={rectangleError,check};
if(require.main===module){
const results=[];
for(const clock of(process.env.CADENCE_CLOCKS||'ms30').split(','))for(const from of scenes)for(const to of scenes){if(from===to)continue;if(process.env.CADENCE_PAIRS&&!process.env.CADENCE_PAIRS.split(',').includes(from+'-'+to))continue;const row={clock,from,to};for(const name of Object.keys(files))row[name]=run(name,from,to,clock);results.push(row);console.log(JSON.stringify(row));}
const summary={cases:results.length,seedP95Improved:results.filter(r=>r.cadence.seedP95<r.harbor.seedP95).length,lateP95Improved:results.filter(r=>r.cadence.lateSeedP95<r.harbor.lateSeedP95).length,cellP95Improved:results.filter(r=>r.cadence.cellP95<r.harbor.cellP95).length,lateFastBodySeconds:Object.fromEntries(Object.keys(files).map(n=>[n,results.reduce((s,r)=>s+r[n].lateFastBodySeconds,0)])),laterCentroidRegressions:results.filter(r=>r.cadence.cellPeak>1.1*r.harbor.cellPeak).map(r=>({clock:r.clock,from:r.from,to:r.to,harbor:r.harbor.cellPeak,cadence:r.cadence.cellPeak}))};
const hashes=Object.fromEntries(Object.entries(files).map(([n,f])=>[n,require('node:crypto').createHash('sha256').update(fs.readFileSync(f)).digest('hex')]));
fs.writeFileSync(path.join(__dirname,process.env.CADENCE_OUTPUT||'results.json'),JSON.stringify({scope:'Seed pacing and root outline centroids; nested fields simulated; renderer stubbed. Not a visual certification.',hashes,summary,results},null,2)+'\n');console.log('SUMMARY',JSON.stringify(summary));
}
