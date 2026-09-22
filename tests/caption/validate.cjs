const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const files=[path.join(__dirname,'skim.html'),path.resolve(__dirname,'../../caption.html')];
const hash=x=>require('node:crypto').createHash('sha256').update(x).digest('hex');
function state(e,p){
 const seen=new Map(),anchors=[];
 e.root.walk(h=>{for(const b of h.bodies){const c=b.content||b.anchorState;if(c)anchors.push([b.id,...['init','tox','toy','tr','at','area'].map(k=>c[k])]);}});
 return JSON.stringify([e.root,anchors,p.leaves.map(l=>({path:l.path.map(x=>x.body.id),pieces:l.pieces,loops:l.loops,holes:l.loops.map(x=>!!x.hole),hv:l.hv,fade:l.fade})),e.meters()],(k,v)=>{
   if(['solveMs','content','anchorState','caption'].includes(k))return undefined;
   if(v&&typeof v==='object'){if(seen.has(v))return{$ref:seen.get(v)};seen.set(v,seen.size);}
   return v;
 });
}
// Record actual fill/stroke geometry and style, separately from text masking.
function drawing(commands){
 let state={},stack=[],poly=[],grad=[];const paint=[],text=[];
 for(const [op,...args]of commands){
  if(op==='save')stack.push({...state});else if(op==='restore')state=stack.pop();
  else if(op==='set')state[args[0]]=args[1];
  else if(op==='beginPath')poly=[];
  else if(['arc','arcTo','lineTo','moveTo','closePath'].includes(op))poly.push([op,...args]);
  else if(op==='createLinearGradient')grad=[[op,...args]];
  else if(op==='addColorStop')grad.push([op,...args]);
  else if(op==='fillRect'||op==='stroke')paint.push({op,args,poly:poly.slice(),grad:grad.slice(),alpha:state.globalAlpha,width:state.lineWidth,stroke:state.strokeStyle,shadow:state.shadowBlur});
  else if(op==='fillText')text.push({args,font:state.font,alpha:state.globalAlpha});
 }
 return{paint,text};
}
const matrix=[
 {width:1900,height:810,count:12,fields:.55,dt:1000/60,inner:'flock'},
 {width:1900,height:810,count:24,fields:1,dt:30,inner:'bento'},
 {width:390,height:720,count:12,fields:.55,dt:1000/120,inner:'flock'},
 {width:1363,height:846,count:30,fields:0,dt:50,inner:'flock'}
];
let total=0,paintOps=0,textDraws=0;const fonts=new Set();
for(const cfg of matrix){
 const es=files.map(f=>loadEngine(f,{...cfg,record:true}));es.forEach(e=>e.inner(cfg.inner));
 let now=1000,frame=0,hoverFrames=0,compactFrames=0;
 const advance=seconds=>{for(let k=0;k<Math.ceil(seconds*1000/cfg.dt);k++){
  es.forEach(e=>e.clear());const ps=es.map(e=>e.advance(now));
  assert.equal(hash(state(es[1],ps[1])),hash(state(es[0],ps[0])),`cell motion changed: ${JSON.stringify(cfg)} frame ${frame}`);
  const ds=es.map(e=>drawing(e.commands));
  assert.equal(hash(JSON.stringify(ds[1].paint)),hash(JSON.stringify(ds[0].paint)),`cell painting changed: ${JSON.stringify(cfg)} frame ${frame}`);
  for(const d of ds[1].text){assert(d.args.slice(1).every(Number.isFinite));fonts.add(d.font);textDraws++;}
  for(const leaf of ps[1].leaves){const c=leaf.body.caption;if(c){assert(c.alpha>=0&&c.alpha<=1&&c.nameAlpha>=0&&c.nameAlpha<=1);if(leaf.labels&&c.alpha>.9&&c.nameAlpha<.1)compactFrames++;}}
  paintOps+=ds[1].paint.length;if(es[1].root.hoveredId>=0)hoverFrames++;
  now+=cfg.dt;frame++;total++;
 }};
 advance(7);
 for(const scene of ['frame','sidebar','hero','sidebar','flock','bento']){
  es.forEach(e=>e.scene(scene));advance(5);
  const b=es[0].root.bodies.find(b=>!b.isVoid&&!b.isSelf&&b.loops?.length),pts=b.loops[0];
  const x=pts.reduce((s,p)=>s+p[0],0)/pts.length,y=pts.reduce((s,p)=>s+p[1],0)/pts.length;
  es.forEach(e=>e.pointer(x,y));advance(.8);
  es.forEach(e=>e.pointer(-1e9,-1e9));advance(.4);
 }
 es.forEach(e=>e.scene('frame'));advance(.4);es.forEach(e=>e.scene('hero'));advance(.23);es.forEach(e=>e.scene('sidebar'));advance(5);
 es.forEach(e=>e.root.addBody());advance(2);es.forEach(e=>e.root.removeBody());advance(2);
 es.forEach(e=>e.size(cfg.width*.83,cfg.height*.93));advance(4);
 assert(hoverFrames>0,'hover fixture inactive');
 cfg.frames=frame;cfg.hoverFrames=hoverFrames;cfg.compactFrames=compactFrames;console.log(JSON.stringify(cfg));
}
assert.deepEqual([...fonts].sort(),['500 12px system-ui, sans-serif','600 20px system-ui, sans-serif','600 32px system-ui, sans-serif'].sort());
// Readability at rest: root labels are present and their font size does not
// breathe on hover; releasing hover returns the cell to the same shape.
const readability=[];
for(const scene of ['bento','hero','sidebar','frame']){
 const e=loadEngine(files[1],{fields:0,record:true});e.scene(scene);let now=1000;
 for(let f=0;f<400;f++){e.clear();e.advance(now);now+=30;}
 const bodies=e.root.bodies.filter(b=>!b.isVoid&&!b.leaving);
 const shown=bodies.filter(b=>b.caption?.alpha>.99).length;
 assert.equal(shown,12,`${scene}: default cells lost their numbers`);
 const names=bodies.filter(b=>b.caption?.nameAlpha>.99).length;
 const b=bodies[0];e.pointer(b.caption.x,b.caption.y);
 for(let f=0;f<80;f++){e.clear();e.advance(now);now+=30;}
 assert.equal(e.root.hoveredId,b.id);assert(b.hoverMix>.99);assert(b.caption.alpha>.99);
 const d=drawing(e.commands);assert(d.text.some(t=>t.font==='600 32px system-ui, sans-serif'));
 readability.push({scene,numbers:shown,names});
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Cell/anchor state and cell fill/stroke commands must exactly match Skim; text is intentionally changed.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,paintOps,textDraws,fonts:[...fonts],readability};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,paintOps,textDraws,readability}));
