// Cue tells Tell II's story on the engine's own rules: every slide is a scene
// change like any other, the cells matched to the slots by distance, the cast
// on stage kept as bystanders, a new sequence benching the last one's cast,
// and the whitespace cut once, the pieces a traveller crosses cut again.
// Without the Cue button, the real tick must produce exactly the same state
// and the same drawing commands as Tell II, a click, a scroll, a Tell story,
// a Tell II story and home included; with the story, every slide settled has
// its cast on its places as rectangles, a sequence builds up one cell a slide
// with the cells already on the stage never moving, a fresh slide's cell is
// none of the last sequence's, the whitespace is exact and covers the page,
// no cell is a field, nothing fractures on any frame of a change, a notch
// turns one slide, Escape goes home, and the same holds on a phone.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const rectsEqual=(a,b)=>a&&b&&a.length>=4&&b.length>=4&&a.slice(0,4).every((v,i)=>Math.abs(v-b[i])<1e-6);
const files=[path.resolve(__dirname,'../../tell2.html'),path.resolve(__dirname,'../../cue.html')];
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
const matrix=[
 {width:1900,height:810,count:12,fields:.55,dt:1000/60,inner:'flock'},
 {width:1900,height:810,count:24,fields:1,dt:30,inner:'bento'},
 {width:390,height:720,count:12,fields:.55,dt:1000/120,inner:'flock'},
 {width:1363,height:846,count:30,fields:0,dt:50,inner:'flock'}
];
let total=0,commandsTotal=0;
const report={clickIdentity:null,slides:[],changes:[],back:null,phone:null,home:null};
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
// --- a click, a scroll, a drag, a Tell and a Tell II story and home, without Cue: Tell II's, exactly
{
 const cfg={width:1900,height:810,count:12,fields:.55,dt:1000/60};
 const es=files.map(f=>loadEngine(f,{...cfg,record:true}));let now=1000,frame=0;
 const advance=n=>{for(let k=0;k<n;k++){
  es.forEach(e=>e.clear());const ps=es.map(e=>e.advance(now));
  assert.equal(hash(state(es[1],ps[1])),hash(state(es[0],ps[0])),'state changed with a click, frame '+frame);
  assert.equal(hash(JSON.stringify(es[1].commands)),hash(JSON.stringify(es[0].commands)),'drawing changed with a click, frame '+frame);
  commandsTotal+=es[1].commands.length;now+=cfg.dt;frame++;total++;
 }};
 advance(300);
 const b=es[0].root.bodies.find(b=>!b.isVoid&&!b.isSelf&&b.name&&es[0].kinds()[b.id%es[0].kinds().length]==='band');
 es.forEach(e=>assert(e.click(b.caption.x,b.caption.y)));advance(420);
 for(let f=0;f<60;f++){es.forEach(e=>e.wheel(4));advance(1);}advance(120);
 es.forEach(e=>{const R=e.reel(),S=R.strips[0],g=S.def.g,PW=e.root.PW,PH=e.root.PH;e.dragStart((g[0]+g[2])/2*PW,(g[1]+g[3])/2*PH,now);});
 for(let f=1;f<=10;f++){es.forEach(e=>{const R=e.reel(),S=R.strips[0],g=S.def.g,PW=e.root.PW,PH=e.root.PH;e.dragMove((g[0]+g[2])/2*PW,(g[1]+g[3])/2*PH-12*f,now);});advance(1);}
 es.forEach(e=>e.dragEnd(now));advance(120);
 es.forEach(e=>e.home());advance(300);
 // and a Tell story: pressed, a notch, a drag held half way, home
 es.forEach(e=>e.tellStart());advance(420);es.forEach(e=>e.tellPush(100));advance(240);
 es.forEach(e=>e.tellDragStart(900,600,now));for(let f=1;f<=6;f++){es.forEach(e=>e.tellDragMove(900,600-810/12*f,now));advance(1);}advance(30);es.forEach(e=>e.tellDragEnd(-1e9));advance(180);
 es.forEach(e=>e.home());advance(300);
 es.forEach(e=>e.tell2Start());advance(420);es.forEach(e=>e.tell2Push(100));advance(300);es.forEach(e=>e.tell2Push(100));advance(300);
 es.forEach(e=>e.home());advance(300);
 assert(!es[1].cue(),'a Cue story without the Cue button');
 report.clickIdentity={frames:frame,kind:'band',tell:true,tell2:true};
}
// --- the story ------------------------------------------------------------------
const area=l=>Math.abs(l.loops[0].reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
const rootsOf=pic=>pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.length===1&&!l.body.leaving);
function fresh(cfg){const e=loadEngine(files[1],{...cfg,record:true});let ms=1000;const st={e,pic:null,step(n){for(let f=0;f<n;f++){e.clear();st.pic=e.advance(ms);ms+=1000/60;}return st.pic;}};st.step(300);return st;}
const ring=pts=>Math.abs(pts.reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
// THE WHITESPACE IS EXACT: every point of every void's outline lies in the
// union of the voids' rectangles, and no root cell's vertex lies inside one
function voidsExact(st,eps=.05){
 const e=st.e,PW=e.root.PW,PH=e.root.PH;
 const boxes=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect).map(v=>[v.rect[0]*PW,v.rect[1]*PH,v.rect[2]*PW,v.rect[3]*PH]);
 const inBox=(p,b,d)=>p[0]>b[0]+d&&p[0]<b[2]-d&&p[1]>b[1]+d&&p[1]<b[3]-d;
 for(const l of st.pic.leaves){
  if(l.path.length!==1)continue;
  for(const lp of l.loops)for(const p of lp){
   if(l.isVoid){if(!boxes.some(b=>inBox(p,b,-eps)))return{ok:false,why:'whitespace outside its rectangles at '+p.map(v=>+v.toFixed(1))};}
   else if(boxes.some(b=>inBox(p,b,eps)))return{ok:false,why:(l.body.name||'a cell')+' inside the whitespace at '+p.map(v=>+v.toFixed(1))};
  }
 }
 return{ok:true,why:''};
}
// THE SHAPE RULE (.claude/gauntlet/shape.js): a root content cell is a
// rectangle, or a convex power cell, cut only where it meets a rigid
// neighbour or the page's edge. A reflex corner nothing explains is a
// fracture. Edges under 2 px are counted apart.
const clean=lp=>{let a=[];for(const p of lp){const q=a[a.length-1];if(!q||Math.hypot(p[0]-q[0],p[1]-q[1])>0.5)a.push(p);}
 while(a.length>1&&Math.hypot(a[0][0]-a[a.length-1][0],a[0][1]-a[a.length-1][1])<=0.5)a.pop();if(a.length<3)return a;
 const out=[];for(let i=0;i<a.length;i++){const p=a[(i+a.length-1)%a.length],c=a[i],q=a[(i+1)%a.length];const ux=c[0]-p[0],uy=c[1]-p[1],vx=q[0]-c[0],vy=q[1]-c[1];if(Math.abs(ux*vy-uy*vx)/(Math.hypot(ux,uy)*Math.hypot(vx,vy))>1e-3)out.push(c);}
 return out.length>=3?out:a;};
function shapes(st){
 const e=st.e,W=e.root.W,H=e.root.H,rigid=[],pic=st.pic;
 for(const l of pic.leaves)if(l.path.length===1&&(l.body.wall||l.body.hole))for(const lp of l.loops)if(!lp.hole&&lp.length>=3)rigid.push(lp);
 for(const b of e.root.walls){const q=b.wall;if(q)rigid.push([[q[0],q[1]],[q[2],q[1]],[q[2],q[3]],[q[0],q[3]]]);}
 for(const b of e.root.holes)if(b.hole&&b.hole.pieces)for(const pc of b.hole.pieces)if(pc.length>=3)rigid.push(pc);
 const rects=[],leaves=pic.leaves.filter(l=>l.path.length===1&&!l.isVoid),cls=new Map();
 for(const l of leaves)for(const lp0 of l.loops){if(lp0.hole)continue;const lp=clean(lp0);if(lp.length<3)continue;
  let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;for(const p of lp){x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1]);}
  const onBox=lp.every(p=>Math.abs(p[0]-x0)<0.5||Math.abs(p[0]-x1)<0.5||Math.abs(p[1]-y0)<0.5||Math.abs(p[1]-y1)<0.5);
  const axisAll=lp.every((p,i)=>{const q=lp[(i+1)%lp.length];return Math.abs(p[0]-q[0])<0.5||Math.abs(p[1]-q[1])<0.5;});
  if(onBox&&axisAll&&ring(lp)>=0.995*(x1-x0)*(y1-y0)){rects.push([x0,y0,x1,y1]);cls.set(lp0,{cls:'rectangle',lp});continue;}
  cls.set(lp0,{cls:axisAll?'notched':null,lp});}
 const segDist=(p,a,b)=>{const ex=b[0]-a[0],ey=b[1]-a[1],L2=ex*ex+ey*ey||1e-9;let t=((p[0]-a[0])*ex+(p[1]-a[1])*ey)/L2;t=Math.max(0,Math.min(1,t));return Math.hypot(a[0]+t*ex-p[0],a[1]+t*ey-p[1]);};
 const near=p=>{if(Math.abs(p[0])<1||Math.abs(p[0]-W)<1||Math.abs(p[1])<1||Math.abs(p[1]-H)<1)return true;
  for(const q of rects){const inX=p[0]>q[0]-1&&p[0]<q[2]+1,inY=p[1]>q[1]-1&&p[1]<q[3]+1;if((Math.abs(p[0]-q[0])<1||Math.abs(p[0]-q[2])<1)&&inY)return true;if((Math.abs(p[1]-q[1])<1||Math.abs(p[1]-q[3])<1)&&inX)return true;}
  for(const lp of rigid)for(let k=0;k<lp.length;k++)if(segDist(p,lp[k],lp[(k+1)%lp.length])<1)return true;return false;};
 const out={rectangle:0,notched:0,voronoi:0,cut:0,shortEdged:0,fractured:0,worst:null};
 for(const l of leaves)for(const lp0 of l.loops){const c=cls.get(lp0);if(!c)continue;const lp=c.lp;
  if(c.cls==='rectangle'){out.rectangle++;continue;}if(c.cls==='notched'){out.notched++;continue;}
  const m=lp.length,sgn=Math.sign(lp.reduce((q,p,i,a)=>{const n=a[(i+1)%a.length];return q+p[0]*n[1]-n[0]*p[1];},0))||1;let reflex=0,unexplained=0,shortEdges=0;
  for(let k=0;k<m;k++){const p=lp[(k+m-1)%m],cpt=lp[k],q=lp[(k+1)%m];const ux=cpt[0]-p[0],uy=cpt[1]-p[1],vx=q[0]-cpt[0],vy=q[1]-cpt[1];const cr=(ux*vy-uy*vx)/(Math.hypot(ux,uy)*Math.hypot(vx,vy)||1);if(Math.hypot(vx,vy)<2)shortEdges++;if(cr*sgn<-1e-3){reflex++;if(!near(cpt))unexplained++;}}
  if(unexplained||m>24){out.fractured++;out.worst=out.worst||{name:l.body.name,verts:m,reflex,unexplained};}
  else if(shortEdges)out.shortEdged++;else if(!reflex&&m<=16)out.voronoi++;else out.cut++;}
 return out;
}
const desk={width:1900,height:810,fields:.55},phone={width:390,height:720,fields:.55};
const N=12;
const roots=e=>e.root.bodies.filter(q=>!q.isVoid&&!q.isSelf&&!q.leaving);
const overlap=(a,b)=>Math.min(a[2],b[2])-Math.max(a[0],b[0])>1e-6&&Math.min(a[3],b[3])-Math.max(a[1],b[1])>1e-6;
// A SLIDE, SETTLED: the cast is the sequence's places so far, each cell on
// its place, a rectangle to 4 px, unlabelled; every cell one site, none a
// field, none fractured, the count kept; the whitespace exact and, with the
// cells, covering the page; the blurb titled with the cast's names, in the box
function settled(st,k,label){
 const e=st.e,T=e.cue();assert(T&&T.k===k,label+': the story is on slide '+(T&&T.k)+', not '+k);
 const spec=e.cuePage(k,N);assert.equal(T.on.length,spec.cast,label+': '+T.on.length+' on stage, the slide has '+spec.cast+' places');
 const PW=e.root.PW,PH=e.root.PH;let worst=0;
 T.on.forEach((b,i)=>{
  assert(rectsEqual(b.rect,spec.content[i]),label+': '+b.name+' is not on place '+i);
  assert(!b.journey||b.progress>=1,label+': '+b.name+' is travelling');
  assert(b.caption.alpha<.05,label+': '+b.name+' still carries its label');
  const l=rootsOf(st.pic).find(l=>l.body===b);assert(l,label+': '+b.name+' has no cell');
  const r=[b.rect[0]*PW,b.rect[1]*PH,b.rect[2]*PW,b.rect[3]*PH];
  for(const q of l.loops[0]){const d=Math.max(Math.min(Math.abs(q[0]-r[0]),Math.abs(q[0]-r[2]),Math.abs(q[1]-r[1]),Math.abs(q[1]-r[3])),r[0]-q[0],q[0]-r[2],r[1]-q[1],q[1]-r[3]);worst=Math.max(worst,d);}
 });
 assert(worst<4,label+': a cell of the cast is '+worst.toFixed(1)+' px off its rectangle');
 for(let i=0;i<T.on.length;i++)for(let j=i+1;j<T.on.length;j++)assert(!overlap(T.on[i].rect,T.on[j].rect),label+': two of the cast overlap');
 assert.equal(roots(e).length,N,label+': '+roots(e).length+' cells');
 for(const q of roots(e))assert.equal(q.subs.length,1,label+': '+q.name+' has '+q.subs.length+' sites');
 assert(!st.pic.leaves.some(l=>l.path.length>1),label+': a field on the story');
 const vx=voidsExact(st,4);assert(vx.ok,label+': '+vx.why);   // to 4 px: no weights are handed, and the live auction settles a hair off the authored diagram where two pieces meet a cell's corner
 const sh=shapes(st);assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst));
 const px=parseFloat(e.meters().mGap[0])+parseFloat(e.meters().mOver[0]);
 assert(px<=0.003*e.root.W*e.root.H,label+': seam residual '+e.meters().mGap[0]+' gap, '+e.meters().mOver[0]+' overlap');
 const voids=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect);
 for(const v of voids)for(const q of roots(e))assert(!overlap(v.rect,q.rect),label+': whitespace over '+q.name);
 const total=voids.concat(roots(e)).reduce((s,q)=>s+(q.rect[2]-q.rect[0])*(q.rect[3]-q.rect[1]),0);
 assert(Math.abs(total-e.root.COLS*e.root.ROWS)<1e-3,label+': the rectangles do not cover the page: '+total.toFixed(3));
 const title=T.on.map(b=>b.name).join(' · '),bx=e.root.W<e.root.H?[.04,.04,.96,.34]:[.23,.25,.59,.75];
 const inBox=q=>q[2]>=bx[0]*e.root.W&&q[2]<=bx[2]*e.root.W&&q[3]>=bx[1]*e.root.H&&q[3]<=bx[3]*e.root.H;
 const texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===title);
 assert(T.alpha>.99,label+': the text is not full');assert(texts.some(inBox),label+': no title in the box');assert(!texts.some(c=>!inBox(c)),label+': the title outside the box');
 return{k,cast:T.on.map(b=>b.name),offRect:+worst.toFixed(1),voids:voids.length,rest:{rectangle:sh.rectangle,voronoi:sh.voronoi,cut:sh.cut}};
}
// A CHANGE: the cells on the stage that the slide keeps are not sent anywhere
// and are nudged at most a few px by a cell passing them; going
// on in a sequence, one cell comes out and the others keep their places; a
// fresh slide sends the last cast home and brings out a cell that was none
// of it; nothing fractures on any frame, and the change ends
function change(st,k,label){
 const e=st.e,T=e.cue(),from=T.k,was=T.on.slice(),before=new Map(roots(e).map(b=>[b,{x:b.x,y:b.y}])),fresh=!!e.slides2()[k].fresh&&k>from;
 e.cueGo(k);st.step(2);
 const now=T.on.slice(),kept=was.filter(b=>now.includes(b));
 if(fresh){assert.equal(kept.length,0,label+': a cell of the last sequence stayed on');assert.equal(now.length,1,label+': a fresh slide has '+now.length+' on stage');}
 else if(k===from+1){assert.deepEqual(now.slice(0,was.length).map(b=>b.name),was.map(b=>b.name),label+': the cast already on the stage did not keep its places');assert.equal(now.length,was.length+1,label+': not one cell more');}
 let frames=0,frac=0,stayMove=0;
 while(e.changeLeft()>0&&frames<600){st.step(1);frames++;frac+=shapes(st).fractured;for(const b of kept){const p=before.get(b);stayMove=Math.max(stayMove,Math.hypot(b.x-p.x,b.y-p.y));}}
 assert(frames<600,label+': the change did not end');assert.equal(frac,0,label+': a fractured cell in the change');
 assert(stayMove<20,label+': a cell on the stage was pushed '+stayMove.toFixed(1)+' px');   // no wall at the root: a bystander is held by its spring, and a cell passing it nudges it (it settles back on its place, see settled)
 st.step(240);
 return{k,fresh,cast:now.map(b=>b.name),kept:kept.length,nudge:+stayMove.toFixed(1),seconds:+(frames/60).toFixed(1)};
}
{ // the story on a desk: slide 0, every slide in turn, back to the first a notch at a time, home
 const st=fresh(desk),e=st.e;e.cueStart();st.step(420);
 assert.equal(e.config.scene,'cue','the scene is not cue');
 report.slides.push(settled(st,0,'slide 0'));
 for(let k=1;k<e.slides2().length;k++){report.changes.push(change(st,k,'slide '+(k-1)+'->'+k));report.slides.push(settled(st,k,'slide '+k));}
 const sizes=report.slides.map(s=>s.cast.length);assert(sizes.includes(1)&&sizes.includes(2)&&sizes.includes(3),'the slides do not build up to one, two and three: '+sizes);
 for(let k=e.slides2().length-2;k>=0;k--){e.cuePush(-100);st.step(420);assert.equal(e.cue().k,k,'a notch back did not turn one slide');}
 report.back=settled(st,0,'slide 0 by notches back');
 e.escape();st.step(420);
 assert(!e.cue(),'the story did not end');assert.equal(roots(e).length,N,'home lost cells');
 report.home={cells:roots(e).length,scene:e.config.scene};
}
{ // a phone: the box a band across the top, the stage a row below it, the cluster at the foot
 const st=fresh(phone),e=st.e;e.cueStart();st.step(420);
 const out=[settled(st,0,'phone slide 0')],R=e.root.ROWS;
 for(let k=1;k<=5;k++){out.push(change(st,k,'phone slide '+(k-1)+'->'+k));out.push(settled(st,k,'phone slide '+k));for(const b of e.cue().on)assert(b.rect[1]>=0.36*R-1e-6&&b.rect[3]<=0.56*R+1e-6,'phone: the stage is not the row below the band');}
 report.phone=out;
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without the Cue button, state and every drawing command must exactly match Tell II, a click, a scroll, a Tell story, a Tell II story and home included; with the story, every slide settled has its cast on its places (rectangles to 4 px, unlabelled), a sequence builds up one cell a slide with the cells already on the stage never moving, a fresh slide brings out a cell that was none of the last sequence, the whitespace is exact and covers the page, no field, one site a cell, nothing fractures on any frame of a change, a notch turns one slide, and the same on a phone.',frames:total,drawingCommands:commandsTotal,matrix,report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,story:report}));
