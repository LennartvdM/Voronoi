// Plaque changes text only. Against the accepted Caption page, the real tick
// must produce exactly the same cell/steering state and the same cell
// fill/stroke commands; text and the field tags are what differs.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const files=[path.resolve(__dirname,'../../caption.html'),path.resolve(__dirname,'../../plaque.html')];
const hash=x=>require('node:crypto').createHash('sha256').update(x).digest('hex');
function state(e,p){
 const seen=new Map(),anchors=[];
 e.root.walk(h=>{for(const b of h.bodies){const c=b.anchorState;if(c)anchors.push([b.id,...['init','tox','toy','tr','at','area'].map(k=>c[k])]);}});
 return JSON.stringify([e.root,anchors,p.leaves.map(l=>({path:l.path.map(x=>x.body.id),pieces:l.pieces,loops:l.loops,holes:l.loops.map(x=>!!x.hole),hv:l.hv,fade:l.fade})),e.meters()],(k,v)=>{
   if(['solveMs','content','anchorState','caption','plaque'].includes(k))return undefined;
   if(v&&typeof v==='object'){if(seen.has(v))return{$ref:seen.get(v)};seen.set(v,seen.size);}
   return v;
 });
}
// Cell painting is fillRect (through the ink clip) and stroke. Text is
// fillText; a field tag's pill is the only fill(). Each is kept apart.
function drawing(commands){
 let state={},stack=[],poly=[],grad=[];const paint=[],text=[],tags=[];
 for(const [op,...args]of commands){
  if(op==='save')stack.push({...state});else if(op==='restore')state=stack.pop();
  else if(op==='set')state[args[0]]=args[1];
  else if(op==='beginPath')poly=[];
  else if(['arc','arcTo','lineTo','moveTo','closePath'].includes(op))poly.push([op,...args]);
  else if(op==='createLinearGradient')grad=[[op,...args]];
  else if(op==='addColorStop')grad.push([op,...args]);
  else if(op==='fillRect'||op==='stroke')paint.push({op,args,poly:poly.slice(),grad:grad.slice(),alpha:state.globalAlpha,width:state.lineWidth,stroke:state.strokeStyle,shadow:state.shadowBlur});
  else if(op==='fillText')text.push({args,font:state.font,alpha:state.globalAlpha});
  else if(op==='fill')tags.push({poly:poly.slice(),alpha:state.globalAlpha});
 }
 return{paint,text,tags};
}
const travelling=b=>!!b.journey&&b.progress<1;
const matrix=[
 {width:1900,height:810,count:12,fields:.55,dt:1000/60,inner:'flock'},
 {width:1900,height:810,count:24,fields:1,dt:30,inner:'bento'},
 {width:390,height:720,count:12,fields:.55,dt:1000/120,inner:'flock'},
 {width:1363,height:846,count:30,fields:0,dt:50,inner:'flock'}
];
const FONT=/^(600|500) (\d+)px system-ui, sans-serif$/;
let total=0,paintOps=0,textDraws=0,tagDraws=0,ghosts=0,maxLabelStep=0,labelSteps20=0;const fonts=new Set();
for(const cfg of matrix){
 const es=files.map(f=>loadEngine(f,{...cfg,record:true}));es.forEach(e=>e.inner(cfg.inner));
 let now=1000,frame=0,hoverFrames=0,hiddenFrames=0;const prev=new Map();
 const advance=seconds=>{for(let k=0;k<Math.ceil(seconds*1000/cfg.dt);k++){
  es.forEach(e=>e.clear());const ps=es.map(e=>e.advance(now));
  assert.equal(hash(state(es[1],ps[1])),hash(state(es[0],ps[0])),`cell motion changed: ${JSON.stringify(cfg)} frame ${frame}`);
  const ds=es.map(e=>drawing(e.commands));
  assert.equal(hash(JSON.stringify(ds[1].paint)),hash(JSON.stringify(ds[0].paint)),`cell painting changed: ${JSON.stringify(cfg)} frame ${frame}`);
  for(const d of ds[1].text){assert(d.args.slice(1).every(Number.isFinite));fonts.add(d.font);textDraws++;}
  tagDraws+=ds[1].tags.length;
  const t=es[1].time();
  // text is drawn at exactly the label's place, so a draw can be matched to its leaf
  const drawnAt=new Set(ds[1].text.map(d=>d.args[1]+','+d.args[2]));
  for(const leaf of ps[1].leaves){
   if(leaf.isVoid||!leaf.loops.length)continue;const c=leaf.body.caption;if(!c)continue;
   assert(c.alpha>=0&&c.alpha<=1&&c.nameAlpha>=0&&c.nameAlpha<=1);
   const moving=leaf.path.some(q=>travelling(q.body));
   if(moving)hiddenFrames++;
   // a cell travelling for 0.3 s has no text drawn on it (the 60 ms fade
   // passes the 1% draw cutoff at 0.28 s)
   if(moving&&leaf.path.every(q=>!q.body.journey||t-q.body.journey.t0>0.3)&&(drawnAt.has(c.x+','+c.y)||drawnAt.has(c.x+','+(c.y+c.off))))ghosts++;
   const key=leaf.path.map(q=>q.body.id).join('/'),p=prev.get(key);
   if(p&&p.f===frame-1&&p.alpha>.5&&c.alpha>.5){const s=Math.hypot(c.x-p.x,c.y-p.y);if(s>maxLabelStep)maxLabelStep=s;if(s>20)labelSteps20++;}
   prev.set(key,{f:frame,alpha:c.alpha,x:c.x,y:c.y});
  }
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
 assert(hoverFrames>0,'hover fixture inactive');assert(hiddenFrames>0,'no travelling cells seen');
 cfg.frames=frame;cfg.hoverFrames=hoverFrames;cfg.travellingLeafFrames=hiddenFrames;console.log(JSON.stringify(cfg));
}
for(const f of fonts){const m=f.match(FONT);assert(m,`unexpected font ${f}`);assert(+m[2]>=11&&+m[2]<=32,`font size out of range ${f}`);}
assert.equal(ghosts,0,'text drawn on a travelling cell');
assert(maxLabelStep<=80,`a label moved ${maxLabelStep}px in one frame`);
// Readability at rest, and the field tags: every root cell numbered and named
// where the desktop layouts leave room, and each field named once.
const rest=[];
function settle(cfg,scene){const e=loadEngine(files[1],{...cfg,record:true});e.scene(scene);let now=1000;for(let f=0;f<400;f++){e.clear();e.advance(now);now+=30;}
 const pic=e.advance(now);const roots=pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.length===1&&!l.body.leaving);
 const galleries=[...new Set(pic.leaves.filter(l=>!l.isVoid&&l.path.length>1).map(l=>l.path[0].body))];
 return{e,now,pic,roots,numbers:roots.filter(l=>l.body.caption?.alpha>.95).length,names:roots.filter(l=>l.body.caption?.nameAlpha>.95).length,galleries:galleries.length,tags:galleries.filter(b=>b.plaque?.alpha>.95).length};}
for(const scene of ['bento','hero','sidebar','frame','flock']){
 const d=settle({width:1900,height:810,fields:0},scene);
 assert.equal(d.numbers,12,`${scene}: a desktop cell lost its number`);assert.equal(d.names,12,`${scene}: a desktop cell lost its name`);
 // hover a settled cell: the number stays, at its fixed size
 const b=d.roots[0].body;d.e.pointer(b.caption.x,b.caption.y);let now=d.now;for(let f=0;f<80;f++){d.e.clear();d.e.advance(now);now+=30;}
 assert.equal(d.e.root.hoveredId,b.id);assert(b.hoverMix>.99);assert(b.caption.alpha>.99);
 assert(drawing(d.e.commands).text.some(t=>t.font==='600 32px system-ui, sans-serif'));
 const g=settle({width:1900,height:810,fields:.55},scene);
 assert.equal(g.numbers,g.roots.length,`${scene}: a desktop cell beside fields lost its number`);assert.equal(g.tags,g.galleries,`${scene}: a field lost its tag`);
 const p=settle({width:390,height:720,fields:0},scene);
 assert(p.numbers>=(scene==='sidebar'?8:scene==='hero'?10:12),`${scene}: phone numbers ${p.numbers}`);
 const q=settle({width:390,height:720,fields:.55},scene);
 assert(q.numbers>=3,`${scene}: phone numbers beside fields ${q.numbers}`);
 rest.push({scene,desktop:{numbers:d.numbers,names:d.names},desktopFields:{roots:g.roots.length,numbers:g.numbers,names:g.names,galleries:g.galleries,tags:g.tags},phone:{numbers:p.numbers,names:p.names},phoneFields:{roots:q.roots.length,numbers:q.numbers,names:q.names,galleries:q.galleries,tags:q.tags}});
}
// A change: from a settled page, a third of a second in, every travelling
// cell is bare and no text is drawn for it; four seconds on, all are back.
{
 const e=loadEngine(files[1],{width:1900,height:810,fields:.55,record:true});e.scene('bento');let now=1000;
 for(let f=0;f<300;f++){e.clear();e.advance(now);now+=1000/60;}
 e.scene('hero');let pic;for(let f=0;f<21;f++){e.clear();pic=e.advance(now);now+=1000/60;}
 const moving=pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.some(q=>travelling(q.body)));
 assert(moving.length>=8,`only ${moving.length} travelling leaves`);
 for(const l of moving)assert(l.body.caption.alpha<.05,'text on a travelling cell');
 const texts=drawing(e.commands).text;
 for(const l of moving)for(const tx of texts)assert(Math.hypot(tx.args[1]-l.body.caption.x,tx.args[2]-l.body.caption.y)>1e-6||l.body.caption.alpha>=.01,'text drawn for a bare cell');
 for(let f=0;f<240;f++){e.clear();pic=e.advance(now);now+=1000/60;}
 const roots=pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.length===1&&!l.body.leaving);
 assert(roots.every(l=>l.body.caption.alpha>.95),'a number did not return after the change');
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Cell/anchor state and cell fill/stroke commands must exactly match Caption; text and field tags are intentionally changed.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,paintOps,textDraws,tagDraws,fonts:[...fonts].sort(),ghosts,maxLabelStepPx:+maxLabelStep.toFixed(1),labelStepsOver20px:labelSteps20,rest};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,paintOps,textDraws,tagDraws,ghosts,maxLabelStepPx:result.maxLabelStepPx,labelStepsOver20px:labelSteps20}));
