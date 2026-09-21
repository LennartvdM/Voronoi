// Execute the real tick, including label springs/anchors, hover and meters.
// Only native Canvas drawing, browser layout and requestAnimationFrame are stubbed.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const files=[path.join(__dirname,'buoy.html'),path.resolve(__dirname,'../../skim.html')];
const hash=x=>require('node:crypto').createHash('sha256').update(x).digest('hex');
function state(e,p){
 const seen=new Map();
 return JSON.stringify([e.root,p.leaves.map(l=>({path:l.path.map(x=>x.body.id),pieces:l.pieces,loops:l.loops,holes:l.loops.map(x=>!!x.hole),hv:l.hv,fade:l.fade})),e.meters()],(k,v)=>{
   if(k==='solveMs')return undefined; // measured CPU duration is expected to differ
   if(v&&typeof v==='object'){if(seen.has(v))return {$ref:seen.get(v)};seen.set(v,seen.size);}
   return v;
 });
}
const matrix=[
 {width:1900,height:810,count:12,fields:.55,dt:1000/60,inner:'flock'},
 {width:1900,height:810,count:24,fields:1,dt:30,inner:'bento'},
 {width:390,height:720,count:12,fields:.55,dt:1000/120,inner:'flock'},
 {width:1363,height:846,count:30,fields:0,dt:50,inner:'flock'}
];
let total=0,drawCommands=0;
for(const cfg of matrix){
 const es=files.map(f=>loadEngine(f,{...cfg,record:true}));
 es.forEach(e=>e.inner(cfg.inner));
 let now=1000,frame=0,hoverFrames=0;
 const advance=seconds=>{
  const frames=Math.ceil(seconds*1000/cfg.dt);
  for(let k=0;k<frames;k++){
   es.forEach(e=>e.clear());const ps=es.map(e=>e.advance(now));
   assert.equal(hash(state(es[1],ps[1])),hash(state(es[0],ps[0])),`engine state changed: ${JSON.stringify(cfg)} frame ${frame}`);
   assert.equal(hash(JSON.stringify(es[1].commands)),hash(JSON.stringify(es[0].commands)),`paint changed: ${JSON.stringify(cfg)} frame ${frame}`);
   drawCommands+=es[0].commands.length;if(es[0].root.hoveredId>=0)hoverFrames++;
   now+=cfg.dt;frame++;total++;
  }
 };
 advance(7);
 for(const scene of ['frame','sidebar','hero','sidebar','flock','bento']){
  es.forEach(e=>e.scene(scene));advance(6);
  // A settled cell's actual label lies inside its painted ink.
  const b=es[0].root.bodies.find(b=>!b.isVoid&&!b.isSelf&&b.loops?.length);
  const pts=b.loops[0],x=pts.reduce((s,p)=>s+p[0],0)/pts.length,y=pts.reduce((s,p)=>s+p[1],0)/pts.length;
  es.forEach(e=>e.pointer(x,y));advance(1);
  es.forEach(e=>e.pointer(-1e9,-1e9));advance(.5);
 }
 es.forEach(e=>e.scene('frame'));advance(.4);
 es.forEach(e=>e.scene('hero'));advance(.23);
 es.forEach(e=>e.scene('sidebar'));advance(6);
 es.forEach(e=>e.root.addBody());advance(3);
 es.forEach(e=>e.root.removeBody());advance(3);
 es.forEach(e=>e.size(cfg.width*.83,cfg.height*.93));advance(5);
 es.forEach(e=>{e.config.gap=0;e.config.cornerRadius=0;e.config.hoverBoost=2.6;});advance(1);
 assert(hoverFrames>0,'fixture never acquired hover');
 cfg.frames=frame;cfg.hoverFrames=hoverFrames;
 console.log(JSON.stringify(cfg));
}
// Differential meter fixtures: holes, nested islands, coincident boundaries,
// reversed winding, clipping beyond the viewport and gaps narrower than S.
const [a,b]=files.map(f=>loadEngine(f,{fields:0}));
let seed=17;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
let rasterCases=0;
for(let k=0;k<500;k++){
 const W=10+rand()*300,H=10+rand()*200,cells=[];
 for(let j=0;j<1+Math.floor(rand()*30);j++){
  const x=rand()*W*1.5-W*.25,y=rand()*H*1.5-H*.25,w=rand()*W,h=rand()*H;
  const pts=j%3?[[x,y],[x+w,y],[x+w,y+h],[x,y+h]]:[[x,y],[x+w,y],[x+w*.5,y+h*.5],[x+w,y+h],[x,y+h]];
  if(j%4===0)pts.reverse();cells.push({pts,hole:j%7===0});
 }
 assert.deepEqual(b.rasterCheck(cells,W,H),a.rasterCheck(cells,W,H));rasterCases++;
}
for(const cells of [[],[{pts:[[0,0],[101,0],[101,99],[0,99]]}], [{pts:[[0,0],[51,0],[51,99],[0,99]]},{pts:[[51,0],[101,0],[101,99],[51,99]]}]]){
 assert.deepEqual(b.rasterCheck(cells,101,99),a.rasterCheck(cells,101,99));rasterCases++;
}
const result={scope:'Exact complete-frame state and Canvas command equivalence. Native Canvas rendering/GPU and browser layout are excluded.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,drawCommands,rasterCases};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({totalFrames:total,drawCommands,rasterCases}));
