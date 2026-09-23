// Portal adds a click and three page layouts. Without a click, the real tick
// must produce exactly the same state and the same drawing commands as
// Plaque; with clicks, every behaviour the page promises is checked.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const files=[path.resolve(__dirname,'../../plaque.html'),path.resolve(__dirname,'../../portal.html')];
const hash=x=>require('node:crypto').createHash('sha256').update(x).digest('hex');
const KINDS=['article','gallery','article','caption'];
function state(e,p){
 const seen=new Map(),anchors=[];
 e.root.walk(h=>{for(const b of h.bodies){const c=b.anchorState;if(c)anchors.push([b.id,...['init','tox','toy','tr','at','area'].map(k=>c[k])]);}});
 return JSON.stringify([e.root,anchors,p.leaves.map(l=>({path:l.path.map(x=>x.body.id),pieces:l.pieces,loops:l.loops,holes:l.loops.map(x=>!!x.hole),hv:l.hv,fade:l.fade})),e.meters()],(k,v)=>{
   if(['solveMs','content','anchorState','caption','plaque'].includes(k))return undefined;
   if(v&&typeof v==='object'){if(seen.has(v))return{$ref:seen.get(v)};seen.set(v,seen.size);}
   return v;
 });
}
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
// --- clicks -------------------------------------------------------------------
const area=l=>Math.abs(l.loops[0].reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
const rootsOf=pic=>pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.length===1&&!l.body.leaving);
function fresh(cfg){const e=loadEngine(files[1],{...cfg,record:true});let ms=1000;const st={e,pic:null,step(n){for(let f=0;f<n;f++){e.clear();st.pic=e.advance(ms);ms+=1000/60;}return st.pic;}};st.step(300);return st;}
function whereIs(st,name){
 const l=st.pic.leaves.find(l=>!l.isVoid&&l.loops.length&&l.path[0].body.name===name);assert(l,'no cell '+name);const b=l.path[0].body;
 if(l.path.length>1){const p=l.path[0].hive.cellPoly(b);let x=0,y=0;for(const q of p){x+=q[0];y+=q[1];}return{b,x:x/p.length,y:y/p.length,field:true};}
 return{b,x:b.caption.x,y:b.caption.y,field:false};
}
function slot0(st){const e=st.e,n=e.root.bodies.filter(b=>!b.isVoid&&!b.leaving&&!b.isSelf).length;const base=e.config.scene==='article'?'hero':e.config.scene;return e.scenes[base](e.root.COLS,e.root.ROWS,n).content[0];}
function opened(st,b,label){
 const e=st.e;assert(e.focus()===b,label+': focus');assert.equal(e.config.scene,KINDS[b.id%4],label+': kind');
 st.step(300);
 assert(e.rectsEqual(b.rect,slot0(st)),label+': the focus did not take slot 0 '+JSON.stringify([b.rect,slot0(st)]));
 const roots=rootsOf(st.pic).sort((p,q)=>area(q)-area(p));
 assert(roots[0].body===b,label+': the focus is not the largest cell');
 assert(!st.pic.leaves.some(l=>l.path.length>1&&l.path[0].body===b),label+': the focus became a field');
 assert(b.caption.alpha>.95,label+': the image lost its label');
 // the text: in the reading void on an article or gallery page (the title
 // inside the largest seated void, and paragraph bars); on the image, in its
 // bottom-left, on a caption page
 const texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===b.name),fills=e.commands.filter(c=>c[0]==='fill').length;
 if(e.config.scene==='caption'){
  assert(!st.pic.leaves.some(l=>l.isVoid&&l.loops.length),label+': a caption page has whitespace');
  const t=texts.find(t=>t[3]>b.caption.y);assert(t,label+': no caption on the image');assert(fills>=1,label+': no caption line');
 }else{
  const voids=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect&&v.crystal>=.99).sort((p,q)=>(q.rect[2]-q.rect[0])*(q.rect[3]-q.rect[1])-(p.rect[2]-p.rect[0])*(p.rect[3]-p.rect[1]));
  assert(voids.length,label+': no reading void');const r=voids[0].rect,PW=e.root.PW,PH=e.root.PH;
  const inVoid=t=>t[2]>=r[0]*PW&&t[2]<=r[2]*PW&&t[3]>=r[1]*PH&&t[3]<=r[3]*PH;
  if(st.e.root.W>=1000){assert(texts.some(inVoid),label+': no title in the reading void');assert(fills>=8,label+': no paragraphs in the reading void');}
  assert(!texts.some(t=>t[2]===b.caption.x&&t[3]!==b.caption.y+b.caption.off&&t[3]!==b.caption.y),label+': stray text on the image');
 }
 return roots;
}
const desk={width:1900,height:810,fields:.55},phone={width:390,height:720,fields:.55};
const report={pages:[],home:null,field:null,void:null,interrupted:null,escape:null,hover:null,phone:null};
{
 const st=fresh(desk),names={};for(const b of st.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&!(b.id%4 in names))names[b.id%4]=b.name;
 assert.equal(Object.keys(names).length,4);
 for(const k of [0,1,3]){
  const s=fresh(desk),w=whereIs(s,names[k]);
  assert(s.e.click(w.x,w.y),'click missed '+names[k]);
  const roots=opened(s,w.b,names[k]);
  report.pages.push({cell:names[k],scene:s.e.config.scene,focusArea:area(roots[0])|0,nextArea:area(roots[1])|0,rect:s.e.meters().mRect[0]});
  if(k===0){
   // the focus, clicked, goes home; every root cell is numbered again
   assert(s.e.click(w.b.caption.x,w.b.caption.y));assert.equal(s.e.config.scene,'bento');assert.equal(s.e.focus(),null);
   s.step(300);const rs=rootsOf(s.pic);assert(rs.length>=7&&rs.every(l=>l.body.caption.alpha>.95),'home lost numbers');
   report.home={roots:rs.length,numbers:rs.filter(l=>l.body.caption.alpha>.95).length};
  }
 }
}
{ // a member of a field opens the field, as one card
 const s=fresh(desk);const member=s.pic.leaves.find(l=>!l.isVoid&&l.loops.length&&l.path.length>1&&l.body.caption&&l.body.caption.alpha>.5);assert(member,'no field member visible');
 const fb=member.path[0].body;assert(s.e.click(member.body.caption.x,member.body.caption.y));opened(s,fb,'field '+fb.name);report.field={field:fb.name,scene:s.e.config.scene};
}
{ // whitespace is not a cell
 const s=fresh(desk),names={};for(const b of s.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&b.id%4===0){names.article=b.name;break;}
 const w=whereIs(s,names.article);assert(s.e.click(w.x,w.y));s.step(300);
 const hit=s.e.click(1900*0.1,810*0.5);assert.equal(hit,false,'a click on the reading column did something');assert.equal(s.e.config.scene,'article');assert(s.e.focus()===w.b);
 report.void={scene:s.e.config.scene,marginClick:hit};
}
{ // a click mid-change is the change that wins
 const s=fresh(desk),rs=rootsOf(s.pic);const a=rs[0].body,b=rs[1].body;
 assert(s.e.click(a.caption.x,a.caption.y));s.step(18);
 const l=s.pic.leaves.find(l=>!l.isVoid&&l.loops.length&&l.path[0].body===b);let x=0,y=0;for(const p of l.loops[0]){x+=p[0];y+=p[1];}x/=l.loops[0].length;y/=l.loops[0].length;
 assert(s.e.click(x,y),'second click missed');const roots=opened(s,b,'interrupted');report.interrupted={first:a.name,second:b.name,scene:s.e.config.scene};
}
{ // escape goes home
 const s=fresh(desk),rs=rootsOf(s.pic),a=rs[0].body;assert(s.e.click(a.caption.x,a.caption.y));s.step(300);s.e.home();
 assert.equal(s.e.config.scene,'bento');assert.equal(s.e.focus(),null);s.step(300);report.escape={numbers:rootsOf(s.pic).filter(l=>l.body.caption.alpha>.95).length};
}
{ // the open page's focus does not hover; a card beside it does
 const s=fresh(desk),rs=rootsOf(s.pic),a=rs[0].body;assert(s.e.click(a.caption.x,a.caption.y));s.step(300);
 s.e.pointer(a.caption.x,a.caption.y);s.step(60);assert(s.e.root.hoveredId!==a.id&&a.hoverMix<.05,'the focus hovered');
 const other=rootsOf(s.pic).find(l=>l.body!==a).body;s.e.pointer(other.caption.x,other.caption.y);s.step(60);assert.equal(s.e.root.hoveredId,other.id,'a card beside the focus did not hover');
 report.hover={focusHoverMix:+a.hoverMix.toFixed(3),cardHovered:other.name};
}
{ // a phone: the page opens the same way; its reading column is too narrow for text, which is skipped
 const s=fresh(phone),rs=rootsOf(s.pic).filter(l=>l.body.caption.alpha>.5);assert(rs.length,'no phone cell to click');const a=rs[0].body;
 assert(s.e.click(a.caption.x,a.caption.y));opened(s,a,'phone');report.phone={cell:a.name,scene:s.e.config.scene,rect:s.e.meters().mRect[0]};
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without a click, state and every drawing command must exactly match Plaque; with clicks, each page kind, its text placement and every click behaviour are asserted.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,drawingCommands:commandsTotal,clicks:report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,clicks:report}));
