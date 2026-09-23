// Portal adds a click and page grids. Without a click, the real tick must
// produce exactly the same state and the same drawing commands as Plaque;
// with clicks, every page kind and every behaviour the page promises is
// checked, whatever the set of kinds is.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const files=[path.resolve(__dirname,'../../plaque.html'),path.resolve(__dirname,'../../portal.html')];
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
const travelling=b=>!!b.journey&&b.progress<1;
const matrix=[
 {width:1900,height:810,count:12,fields:.55,dt:1000/60,inner:'flock'},
 {width:1900,height:810,count:24,fields:1,dt:30,inner:'bento'},
 {width:390,height:720,count:12,fields:.55,dt:1000/120,inner:'flock'},
 {width:1363,height:846,count:30,fields:0,dt:50,inner:'flock'}
];
let total=0,commandsTotal=0;
for(const cfg of matrix){
 const es=files.map(f=>loadEngine(f,{...cfg,record:true}));es.forEach(e=>e.inner(cfg.inner));
 let now=1000,frame=0;
 const advance=seconds=>{for(let k=0;k<Math.ceil(seconds*1000/cfg.dt);k++){
  es.forEach(e=>e.clear());const ps=es.map(e=>e.advance(now));
  assert.equal(hash(state(es[1],ps[1])),hash(state(es[0],ps[0])),`state changed: ${JSON.stringify(cfg)} frame ${frame}`);
  assert.equal(hash(JSON.stringify(es[1].commands)),hash(JSON.stringify(es[0].commands)),`drawing changed: ${JSON.stringify(cfg)} frame ${frame}`);
  commandsTotal+=es[1].commands.length;now+=cfg.dt;frame++;total++;
 }};
 advance(7);
 for(const scene of ['frame','sidebar','hero','sidebar','flock','bento']){
  es.forEach(e=>e.scene(scene));advance(5);
  const b=es[0].root.bodies.find(b=>!b.isVoid&&!b.isSelf&&b.loops?.length),pts=b.loops[0];
  const x=pts.reduce((s,p)=>s+p[0],0)/pts.length,y=pts.reduce((s,p)=>s+p[1],0)/pts.length;
  es.forEach(e=>e.pointer(x,y));advance(.8);es.forEach(e=>e.pointer(-1e9,-1e9));advance(.4);
 }
 es.forEach(e=>e.scene('frame'));advance(.4);es.forEach(e=>e.scene('hero'));advance(.23);es.forEach(e=>e.scene('sidebar'));advance(5);
 es.forEach(e=>e.root.addBody());advance(2);es.forEach(e=>e.root.removeBody());advance(2);
 es.forEach(e=>e.size(cfg.width*.83,cfg.height*.93));advance(4);
 cfg.frames=frame;console.log(JSON.stringify(cfg));
}
// --- pages and clicks ------------------------------------------------------------
const area=l=>Math.abs(l.loops[0].reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
const rootsOf=pic=>pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.length===1&&!l.body.leaving);
function fresh(cfg){const e=loadEngine(files[1],{...cfg,record:true});let ms=1000;const st={e,pic:null,step(n){for(let f=0;f<n;f++){e.clear();st.pic=e.advance(ms);ms+=1000/60;}return st.pic;}};st.step(300);return st;}
function whereIs(st,name){
 const l=st.pic.leaves.find(l=>!l.isVoid&&l.loops.length&&l.path[0].body.name===name);assert(l,'no cell '+name);const b=l.path[0].body;
 if(l.path.length>1){const p=l.path[0].hive.cellPoly(b);let x=0,y=0;for(const q of p){x+=q[0];y+=q[1];}return{b,x:x/p.length,y:y/p.length,field:true};}
 return{b,x:b.caption.x,y:b.caption.y,field:false};
}
function isRect(pts,eps=.02){
 let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;for(const p of pts){x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1]);}
 const off=pts.filter(p=>Math.min(Math.abs(p[0]-x0),Math.abs(p[0]-x1))>eps&&Math.min(Math.abs(p[1]-y0),Math.abs(p[1]-y1))>eps);
 if(off.length)return{ok:false,why:'vertex off the box '+JSON.stringify(off.map(p=>p.map(v=>+v.toFixed(3))))};
 const a=Math.abs(pts.reduce((q,p,i,arr)=>{const m=arr[(i+1)%arr.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2),box=(x1-x0)*(y1-y0);
 if(Math.abs(a-box)>eps*2*((x1-x0)+(y1-y0)))return{ok:false,why:'area '+a.toFixed(2)+' of box '+box.toFixed(2)};
 return{ok:true,why:''};
}
function slot0(st){const e=st.e,n=e.root.bodies.filter(b=>!b.isVoid&&!b.leaving&&!b.isSelf).length;return e.scenes[e.config.scene](e.root.COLS,e.root.ROWS,n).content[0];}
function opened(st,b,label,phone){
 const e=st.e,KINDS=e.kinds(),T=e.templates();assert(e.focus()===b,label+': focus');assert.equal(e.config.scene,KINDS[b.id%KINDS.length],label+': kind');
 st.step(420);
 assert(e.rectsEqual(b.rect,slot0(st)),label+': the image did not take the first slot '+JSON.stringify([b.rect,slot0(st)]));
 const roots=rootsOf(st.pic).sort((p,q)=>area(q)-area(p));
 assert(roots[0].body===b,label+': the image is not the largest cell');
 assert(!st.pic.leaves.some(l=>l.path.length>1),label+': a field on a page');
 // the page grid is drawn exactly: every root cell a rectangle. The outline
 // keeps a vertex where a neighbour's seam meets an edge if the auction's
 // last residual left it a hair off the line, so the test is geometric: every
 // vertex on the cell's bounding box, and the cell filling that box
 for(const l of roots){const r=isRect(l.loops[0]);assert(r.ok,label+': a page cell is not a rectangle ('+l.body.name+': '+r.why+')');}
 assert.equal(e.meters().mRect[0],'100%',label+': rect meter '+e.meters().mRect[0]);
 // seams meet within a hairline: the auction's residual at a page's junctions,
 // gap and overlap together, stays under 0.3% of the page
 const px=parseFloat(e.meters().mGap[0])+parseFloat(e.meters().mOver[0]);
 assert(px<=0.003*e.root.W*e.root.H,label+': seam residual '+e.meters().mGap[0]+' gap, '+e.meters().mOver[0]+' overlap');
 const t=T[e.config.scene],texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===b.name),fills=e.commands.filter(c=>c[0]==='fill').length;
 if(t.text){
  // the text: the title inside the seated reading void with paragraph bars; no label on the image
  const voids=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect&&v.crystal>=.99).sort((p,q)=>(q.rect[2]-q.rect[0])*(q.rect[3]-q.rect[1])-(p.rect[2]-p.rect[0])*(p.rect[3]-p.rect[1]));
  assert(voids.length,label+': no reading void');const r=voids[0].rect,PW=e.root.PW,PH=e.root.PH;
  const inVoid=q=>q[2]>=r[0]*PW&&q[2]<=r[2]*PW&&q[3]>=r[1]*PH&&q[3]<=r[3]*PH;
  if(!phone){assert(texts.some(inVoid),label+': no title in the reading void');assert(fills>=8,label+': no paragraphs in the reading void');}
  assert(b.caption.alpha<.05,label+': the image still carries its label');
  assert(!texts.some(q=>!inVoid(q)),label+': stray text on the image');
 }else{
  assert(!st.pic.leaves.some(l=>l.isVoid&&l.loops.length),label+': a caption page has whitespace');
  const c=texts.find(q=>q[3]>b.caption.y);assert(c,label+': no caption on the image');assert(fills>=1,label+': no caption line');
 }
 return roots;
}
const desk={width:1900,height:810,fields:.55},phone={width:390,height:720,fields:.55};
const report={kinds:[],home:null,field:null,void:null,interrupted:null,escape:null,hover:null,phone:[]};
{
 const st=fresh(desk),KINDS=st.e.kinds(),names={};
 for(const b of st.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&!(b.id%KINDS.length in names))names[b.id%KINDS.length]=b.name;
 assert.equal(Object.keys(names).length,KINDS.length,'not every kind has a cell at 12');
 let first=true;
 for(const k of Object.keys(names).map(Number).sort((a,b)=>a-b)){
  const s=fresh(desk),w=whereIs(s,names[k]);
  assert(s.e.click(w.x,w.y),'click missed '+names[k]);
  const roots=opened(s,w.b,KINDS[k]);
  report.kinds.push({kind:KINDS[k],cell:names[k],imageShare:+(area(roots[0])/(1900*810)).toFixed(3),smallestCard:+(area(roots[roots.length-1])/(1900*810)).toFixed(4),rect:s.e.meters().mRect[0],gap:s.e.meters().mGap[0]});
  if(first){first=false;
   // the image, clicked, goes home; every root cell is numbered again
   const l=s.pic.leaves.find(l=>l.body===w.b);let x=0,y=0;for(const p of l.loops[0]){x+=p[0];y+=p[1];}x/=l.loops[0].length;y/=l.loops[0].length;
   assert(s.e.click(x,y));assert.equal(s.e.config.scene,'bento');assert.equal(s.e.focus(),null);
   s.step(300);const rs=rootsOf(s.pic);assert(rs.length>=7&&rs.every(q=>q.body.caption.alpha>.95),'home lost numbers');
   report.home={roots:rs.length,numbers:rs.filter(q=>q.body.caption.alpha>.95).length};
  }
 }
}
{ // a member of a field opens the field, as one card
 const s=fresh(desk);const member=s.pic.leaves.find(l=>!l.isVoid&&l.loops.length&&l.path.length>1&&l.body.caption&&l.body.caption.alpha>.5);assert(member,'no field member visible');
 const fb=member.path[0].body;assert(s.e.click(member.body.caption.x,member.body.caption.y));opened(s,fb,'field '+fb.name);report.field={field:fb.name,scene:s.e.config.scene};
}
{ // whitespace is not a cell: a click in the reading void does nothing
 const s=fresh(desk),KINDS=s.e.kinds(),T=s.e.templates();let name=null;
 for(const b of s.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&T[KINDS[b.id%KINDS.length]].text){name=b.name;break;}
 const w=whereIs(s,name);assert(s.e.click(w.x,w.y));s.step(420);const scene=s.e.config.scene;
 const v=s.e.root.bodies.filter(q=>q.isVoid&&!q.leaving&&q.rect).sort((p,q)=>(q.rect[2]-q.rect[0])*(q.rect[3]-q.rect[1])-(p.rect[2]-p.rect[0])*(p.rect[3]-p.rect[1]))[0];
 const hit=s.e.click((v.rect[0]+v.rect[2])/2*s.e.root.PW,(v.rect[1]+v.rect[3])/2*s.e.root.PH);
 assert.equal(hit,false,'a click on the reading void did something');assert.equal(s.e.config.scene,scene);assert(s.e.focus()===w.b);
 report.void={scene,voidClick:hit};
}
{ // a click mid-change is the change that wins
 const s=fresh(desk),rs=rootsOf(s.pic);const a=rs[0].body,b=rs[1].body;
 assert(s.e.click(a.caption.x,a.caption.y));s.step(18);
 const l=s.pic.leaves.find(l=>!l.isVoid&&l.loops.length&&l.path[0].body===b);let x=0,y=0;for(const p of l.loops[0]){x+=p[0];y+=p[1];}x/=l.loops[0].length;y/=l.loops[0].length;
 assert(s.e.click(x,y),'second click missed');opened(s,b,'interrupted');report.interrupted={first:a.name,second:b.name,scene:s.e.config.scene};
}
{ // escape goes home
 const s=fresh(desk),rs=rootsOf(s.pic),a=rs[0].body;assert(s.e.click(a.caption.x,a.caption.y));s.step(300);s.e.home();
 assert.equal(s.e.config.scene,'bento');assert.equal(s.e.focus(),null);s.step(300);report.escape={numbers:rootsOf(s.pic).filter(l=>l.body.caption.alpha>.95).length};
}
{ // the open page's image does not hover; a card beside it does, and the page recovers
 const s=fresh(desk),rs=rootsOf(s.pic),a=rs[0].body;assert(s.e.click(a.caption.x,a.caption.y));s.step(420);
 const l=s.pic.leaves.find(l=>l.body===a);let x=0,y=0;for(const p of l.loops[0]){x+=p[0];y+=p[1];}x/=l.loops[0].length;y/=l.loops[0].length;
 s.e.pointer(x,y);s.step(60);assert(s.e.root.hoveredId!==a.id&&a.hoverMix<.05,'the image hovered');
 const other=rootsOf(s.pic).find(q=>q.body!==a).body;s.e.pointer(other.caption.x,other.caption.y);s.step(60);assert.equal(s.e.root.hoveredId,other.id,'a card beside the image did not hover');
 s.e.pointer(-1e9,-1e9);s.step(180);assert.equal(s.e.meters().mRect[0],'100%','the page did not recover from hover');
 report.hover={imageHoverMix:+a.hoverMix.toFixed(3),cardHovered:other.name};
}
{ // add and remove a cell on an open page: the image keeps its slot, the grid stays exact
 const s=fresh(desk),rs=rootsOf(s.pic),a=rs[0].body;assert(s.e.click(a.caption.x,a.caption.y));s.step(420);
 s.e.root.addBody();s.step(360);assert(s.e.rectsEqual(a.rect,slot0(s)),'the image lost its slot after add');assert.equal(s.e.meters().mRect[0],'100%','not exact after add');
 s.e.root.removeBody();s.step(360);assert(s.e.rectsEqual(a.rect,slot0(s)),'the image lost its slot after remove');assert.equal(s.e.meters().mRect[0],'100%','not exact after remove');
}
{ // a phone: every kind opens the same way; a reading column under 90 px gets no text
 const st=fresh(phone),KINDS=st.e.kinds(),names={};
 for(const b of st.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&!(b.id%KINDS.length in names))names[b.id%KINDS.length]=b.name;
 for(const k of Object.keys(names).map(Number).sort((a,b)=>a-b)){
  const s=fresh(phone),w=whereIs(s,names[k]);assert(s.e.click(w.x,w.y),'phone click missed '+names[k]);opened(s,w.b,'phone '+KINDS[k],true);
  report.phone.push({kind:KINDS[k],rect:s.e.meters().mRect[0]});
 }
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without a click, state and every drawing command must exactly match Plaque; with clicks, every page kind is drawn as an exact rectangular grid with its text in the reading void, and every click behaviour is asserted.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,drawingCommands:commandsTotal,clicks:report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,clicks:report}));
