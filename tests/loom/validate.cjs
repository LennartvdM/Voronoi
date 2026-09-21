// Numerical continuity regression for the actual inline engine. DOM and paint
// are stubbed; motion, auctions, nested fields, and outlines run unchanged.
// This does not measure browser frame time or certify visual smoothness.
const fs = require('node:fs');
const { performance } = require('node:perf_hooks');

function loadEngine(file, width = 1900, height = 810, fields = 0, count = 12) {
  const html = fs.readFileSync(file, 'utf8');
  let js = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const end = js.lastIndexOf('})();');
  js = js.slice(0, end) + `return {root, config, init, advance(dt) {
    simTime += dt; guestLeft = changeEnds(root) - simTime;
    root.step(dt, simTime); picture = buildPicture(root);
    return picture;
  }, scene(name) {config.scene=name; root.enterScene(name);}};\n` + js.slice(end);
  const noop = () => {};
  const el = {addEventListener:noop,style:{},classList:{toggle:noop},
    getContext:()=>({setTransform:noop}),
    parentElement:{getBoundingClientRect:()=>({width,height})}};
  const doc = {readyState:'loading',addEventListener:noop,
    getElementById:()=>el,querySelectorAll:()=>[]};
  const engine = Function('document','window','requestAnimationFrame','performance','return '+js.trim())(
    doc,{addEventListener:noop,devicePixelRatio:1},noop,performance);
  engine.config.fieldDensity = fields;
  engine.config.count = count;
  engine.init();
  return engine;
}

function measures(root) {
  const out = new Map();
  for (const b of root.bodies) {
    if (b.isVoid || b.isSelf || !b.loops) continue;
    let a2=0,x=0,y=0;
    for (const p of b.loops) for (let i=0;i<p.length;i++) {
      const q=p[(i+1)%p.length], z=p[i][0]*q[1]-q[0]*p[i][1];
      a2+=z; x+=(p[i][0]+q[0])*z; y+=(p[i][1]+q[1])*z;
    }
    if (Math.abs(a2)>1e-6) out.set(b.id,{area:Math.abs(a2/2),x:x/(3*a2),y:y/(3*a2)});
  }
  return out;
}

function displacement(a,b) {
  let px=0,area=0;
  for (const [id,p] of a) {
    const q=b.get(id); if (!q) continue;
    px=Math.max(px,Math.hypot(p.x-q.x,p.y-q.y));
    area=Math.max(area,Math.abs(p.area-q.area)/p.area);
  }
  return {px,area};
}

const assert = require('node:assert/strict');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const ROOT = path.resolve(__dirname, '../..');
const scratch = fs.mkdtempSync(path.join(ROOT, '.loom-validation-'));
const baseline = path.join(scratch, 'selvedge.html');
const candidate = path.join(ROOT, 'loom.html');
const settle = (e, dt, seconds=8) => {for(let i=0;i<Math.ceil(seconds/dt);i++)e.advance(dt);};
const signedArea = p => p.reduce((a,q,i)=>{const z=p[(i+1)%p.length];return a+q[0]*z[1]-z[0]*q[1];},0)/2;
function clip(p,axis,k,sign){
  const out=[];
  for(let i=0;i<p.length;i++){
    const a=p[i],b=p[(i+1)%p.length],da=sign*(a[axis]-k),db=sign*(b[axis]-k);
    if(da>=0)out.push(a);
    if((da>=0)!=(db>=0)){const t=da/(da-db);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}
  }
  return out;
}
function voidError(e){
  let error=0,total=0,maxEdgePx=0;
  for(const b of e.root.bodies){
    if(!b.isVoid||b.leaving||!b.rect)continue;
    const r=b.rect.map((v,i)=>v*(i%2?e.root.PH:e.root.PW));
    const target=(r[2]-r[0])*(r[3]-r[1]);
    let owned=0,intersection=0;
    for(const p of b.loops){
      owned+=signedArea(p);
      let c=p;for(const [axis,k,sign]of[[0,r[0],1],[0,r[2],-1],[1,r[1],1],[1,r[3],-1]])c=clip(c,axis,k,sign);
      intersection+=signedArea(c);
      // Include segment interiors: an off-axis edge can have both endpoints
      // on the rectangle's top/bottom and still bow away from its side.
      for(let i=0;i<p.length;i++)for(const t of[0,.25,.5,.75]){
        const a=p[i],z=p[(i+1)%p.length],q=[a[0]+t*(z[0]-a[0]),a[1]+t*(z[1]-a[1])];
        maxEdgePx=Math.max(maxEdgePx,Math.min(Math.abs(q[0]-r[0]),Math.abs(q[0]-r[2]),Math.abs(q[1]-r[1]),Math.abs(q[1]-r[3])));
      }
    }
    error+=Math.max(0,Math.abs(owned)+target-2*Math.abs(intersection));total+=target;
  }
  if(!total)return null; // Original scene templates may fall back to Flock when over capacity.
  return {symmetricDifferencePct:100*error/total,maxEdgePx};
}
function finite(e){
  for(const b of e.root.bodies){
    for(const p of b.loops||[])for(const q of p)assert(q.every(Number.isFinite));
    if(!b.isVoid&&!b.isSelf&&!b.leaving)assert(b.loops?.some(p=>p.length>=3),'content lost its outline');
  }
  assert.equal(e.root.walls.length,0,'root geometry became a domain wall');
  assert.equal(e.root.holes.length,0,'root geometry became a domain cut');
}
function retained(old){
  for(const {body,sites}of old)for(let i=0;i<sites.length;i++)assert.equal(body.subs[i],sites[i],'site object discarded');
}
const sites=e=>e.root.bodies.filter(b=>!b.isSelf&&b.plCurrent).map(body=>({body,sites:body.subs.slice()}));
function transition(file,from,to,dt){
  const e=loadEngine(file,1900,810,.55);settle(e,dt);
  if(from!=='bento'){e.scene(from);settle(e,dt);}
  let before=measures(e.root);const old=sites(e);
  e.scene(to);e.advance(1e-6);finite(e);
  if(file===candidate)retained(old);
  let now=measures(e.root),openingPx=displacement(before,now).px,maxFramePx=0,maxRelativeAreaError=0;
  before=now;
  for(let i=0;i<Math.ceil(7/dt);i++){
    e.advance(dt);finite(e);now=measures(e.root);
    maxFramePx=Math.max(maxFramePx,displacement(before,now).px);
    maxRelativeAreaError=Math.max(maxRelativeAreaError,e.root.solved?.maxRelErr||0);before=now;
  }
  return {openingPx,maxFramePx,maxRelativeAreaError};
}
try {
  const build=spawnSync('python3',[path.join(__dirname,'build.py')],{env:{...process.env,LOOM_BASELINE_OUT:baseline},encoding:'utf8'});
  assert.equal(build.status,0,build.stderr);console.log(build.stdout.trim());
  const geometry=[],transitions=[];
  for(const [width,height,count]of[[1900,810,12],[1440,620,24],[390,760,12],[1900,810,30]]){
    for(const scene of ['hero','sidebar','frame']){
      const result={width,height,count,scene};
      for(const [name,file]of[['selvedge',baseline],['loom',candidate]]){
        const e=loadEngine(file,width,height,.55,count);settle(e,1/30);e.scene(scene);settle(e,1/30,10);finite(e);
        const geometry=voidError(e);
        result[name]=geometry?{...geometry,activeSites:e.root.solvedSubs.length}:null;
      }
      if(!result.selvedge){assert.equal(result.loom,null,'over-capacity fallback changed');result.fallback='Existing template falls back to Flock';geometry.push(result);continue;}
      if(scene==='sidebar')assert(Math.abs(result.loom.symmetricDifferencePct-result.selvedge.symmetricDifferencePct)<1e-7,'Sidebar changed');
      else {
        assert(result.loom.symmetricDifferencePct<.01,`${scene}: rectangular void error exceeds .01%`);
        assert(result.loom.maxEdgePx<.1,`${scene}: void edge differs by more than .1px`);
      }
      geometry.push(result);
    }
    console.log(`Geometry: ${width}x${height}, ${count} elements`);
  }
  for(const dt of[1/60,.03]){
    for(const from of['flock','bento','hero','sidebar','frame'])for(const to of['flock','bento','hero','sidebar','frame']){
      if(from===to)continue;
      const selvedge=transition(baseline,from,to,dt),loom=transition(candidate,from,to,dt);
      if(['hero','sidebar','frame'].includes(from)&&(to==='flock'||to==='bento'))assert(loom.openingPx<.25,'release snap');
      assert(loom.openingPx<=Math.max(3,selvedge.openingPx+.1),'opening discontinuity regressed');
      transitions.push({dt,from,to,selvedge,loom});
    }
    console.log(`All 20 directed transitions: ${(dt*1000).toFixed(3)}ms`);
  }
  for(const delay of[.08,.23,.6]){
    const e=loadEngine(candidate,1900,810,.55);settle(e,1/60);e.scene('frame');settle(e,1/60);
    for(const to of['hero','sidebar','frame','flock','bento']){
      const old=sites(e);e.scene(to);e.advance(1e-6);retained(old);settle(e,1/60,delay);finite(e);
    }
    settle(e,1/60);finite(e);
  }
  for(const scene of['hero','frame']){
    const e=loadEngine(candidate,1900,810,.55);settle(e,1/60);e.scene(scene);settle(e,1/60);
    const old=sites(e);e.root.fit([0,0,1440,720],[[0,0],[1440,0],[1440,720],[0,720]],true,0,0);
    e.advance(1/60);retained(old);settle(e,1/60);finite(e);assert(voidError(e).symmetricDifferencePct<.01);
  }
  const worseLater=transitions.filter(r=>r.loom.maxFramePx>r.selvedge.maxFramePx*1.1);
  const output={scope:'Rectangular resting voids and continuity at release. Later motion is measured, not certified smooth.',engineOnly:true,
    geometry,transitions,interruptedRetargets:15,resizes:2,
    laterMotionRegressions:worseLater.map(r=>({dt:r.dt,from:r.from,to:r.to,selvedgePx:r.selvedge.maxFramePx,loomPx:r.loom.maxFramePx}))};
  fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(output,null,2)+'\n');
  console.log(JSON.stringify({geometryCases:geometry.length,transitionCases:transitions.length,laterMotionRegressions:output.laterMotionRegressions},null,2));
} finally {fs.rmSync(scratch,{recursive:true,force:true});}
