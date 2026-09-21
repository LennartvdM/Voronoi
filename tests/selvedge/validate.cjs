// Numerical continuity regression for the actual inline engine. DOM and paint
// are stubbed; motion, auctions, nested fields, and outlines run unchanged.
// This does not measure browser frame time or certify visual smoothness.
const fs = require('node:fs');
const { performance } = require('node:perf_hooks');

function loadEngine(file, width = 1900, height = 810, fields = 0) {
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
const ROOT = path.resolve(__dirname, '../..');
const SCENES = ['flock','bento','hero','sidebar','frame'];
const WIDTH=1900, HEIGHT=810, FIELDS=.55;
const rows=[];
const settle=(e,dt,seconds=8)=>{for(let i=0;i<Math.ceil(seconds/dt);i++)e.advance(dt);};
const finite=(root)=>{
  for(const b of root.bodies) for(const p of b.loops||[]) for(const q of p)
    assert(q.every(Number.isFinite),'nonfinite outline');
  for(const b of root.bodies) if(!b.isVoid&&!b.isSelf&&!b.leaving)
    assert(b.loops?.some(p=>p.length>=3),'content body lost its outline');
};
const voids=(e)=>e.root.bodies.filter(b=>b.isVoid&&b.plCurrent)
  .map(b=>({body:b,sites:b.subs.slice(),claim:b.claim}));
const retained=(old,e)=>{
  for(const {body,sites} of old) {
    if(body.reaped)continue;
    for(let i=0;i<sites.length;i++)assert.equal(body.subs[i],sites[i],
      `void ${body.id} replaced or dropped site ${i}`);
  }
};
function run(file,from,to,dt){
  const e=loadEngine(path.join(ROOT,file),WIDTH,HEIGHT,FIELDS);
  settle(e,dt);
  if(from!=='bento'){e.scene(from);settle(e,dt);}
  const before=measures(e.root), old=voids(e);
  e.scene(to); e.advance(1e-6);
  finite(e.root);
  const opening=displacement(before,measures(e.root)).px;
  if(file==='selvedge.html')retained(old,e);
  let prev=measures(e.root), maxFramePx=0,maxAreaError=0;
  for(let i=0;i<Math.ceil(7/dt);i++){
    e.advance(dt);finite(e.root);
    const now=measures(e.root);
    maxFramePx=Math.max(maxFramePx,displacement(prev,now).px);
    maxAreaError=Math.max(maxAreaError,e.root.solved?.maxRelErr||0);
    prev=now;
  }
  return {openingPx:opening,maxFramePx,maxAreaError};
}
for(const dt of [1/60,.03]){
  for(const from of SCENES)for(const to of SCENES){
    if(from===to)continue;
    const baseline=run('weave.html',from,to,dt);
    const candidate=run('selvedge.html',from,to,dt);
    if(['hero','sidebar','frame'].includes(from)){
      assert(candidate.openingPx<baseline.openingPx,
        `${from}->${to}: opening displacement did not decrease`);
      if(to==='flock'||to==='bento')assert(candidate.openingPx<.25,
        `${from}->${to}: more than a quarter pixel moved at negligible elapsed time`);
    }
    rows.push({dt,from,to,weave:baseline,selvedge:candidate});
  }
  console.log(`Measured all 20 directed transitions at ${(dt*1000).toFixed(3)} ms`);
}
// Rapid retargeting freezes the CURRENT formation, not its previous destination.
for(const delay of [.08,.23,.6]){
  const e=loadEngine(path.join(ROOT,'selvedge.html'),WIDTH,HEIGHT,FIELDS);
  settle(e,1/60);e.scene('sidebar');settle(e,1/60);
  for(const to of ['hero','frame','flock','sidebar','bento']){
    const old=voids(e);e.scene(to);e.advance(1e-6);retained(old,e);
    settle(e,1/60,delay);finite(e.root);
  }
  settle(e,1/60);finite(e.root);
}
// Resizing used to truncate root voids without rebuilding their morph arrays.
{
  const e=loadEngine(path.join(ROOT,'selvedge.html'),WIDTH,HEIGHT,FIELDS);
  settle(e,1/60);e.scene('sidebar');settle(e,1/60);
  const old=voids(e);
  e.root.fit([0,0,1440,720],[[0,0],[1440,0],[1440,720],[0,720]],true,0,0);
  e.advance(1/60);retained(old,e);finite(e.root);settle(e,1/60);finite(e.root);
}
const exits=rows.filter(r=>['hero','sidebar','frame'].includes(r.from));
const output={scope:'Opening discontinuity only. Later motion and resting Frame geometry remain unresolved.',
  engineOnly:true,viewport:[WIDTH,HEIGHT],fields:FIELDS,
  openingImproved:exits.length,openingCases:exits.length,
  worstOpeningPx:{weave:Math.max(...exits.map(r=>r.weave.openingPx)),
    selvedge:Math.max(...exits.map(r=>r.selvedge.openingPx))},
  interruptedRetargets:15,resizePassed:true,rows};
fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({...output,rows:undefined},null,2));
