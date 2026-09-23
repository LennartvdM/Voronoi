// Tell II adds a second scroll-tell: a small cluster, a revolver of chambers
// around a bore, a blurb in a box in the open, and sequences of slides that
// send one cell at a time out to a place around the box, the cast building
// up to three, and back into the cluster when the sequence is done. Without the Tell button, the real tick must produce exactly
// the same state and the same drawing commands as Reel, a click, a scroll and
// home included; with the story, the cluster never moves, every hero is the
// card nearest its slide's place swollen in place with the column exact, the
// text comes once the entry has ended and the rules a beat later and stays,
// the wheel, a drag and a flick move the story, a slow story snaps to its
// slide, the story stops at its ends, and home returns the count.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const rectsEqual=(a,b)=>a&&b&&a.length>=4&&b.length>=4&&a.slice(0,4).every((v,i)=>Math.abs(v-b[i])<1e-6);
const files=[path.resolve(__dirname,'../../tell.html'),path.resolve(__dirname,'../../tell2.html')];
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
const report={clickIdentity:null,start:null,slides:[],text:null,push:null,drag:null,notch:null,snap:null,ends:null,back:null,interrupted:null,home:null,phone:null};
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
// --- a click, a scroll, a drag and home, without the story: Reel's, exactly ------
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
 assert(!es[1].tell2(),'a second story without the Tell II button');
 report.clickIdentity={frames:frame,kind:'band',tell:true};
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
const rectKey=r=>r.slice(0,4).map(v=>v.toFixed(6)).join(',');
const overlap=(a,b)=>Math.min(a[2],b[2])-Math.max(a[0],b[0])>1e-6&&Math.min(a[3],b[3])-Math.max(a[1],b[1])>1e-6;
const seg=(a,b,c,d)=>{const o=(p,q,r)=>(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);const s1=o(a,b,c),s2=o(a,b,d),s3=o(c,d,a),s4=o(c,d,b);return s1*s2<0&&s3*s4<0;};
// THE PLAN: from the cells in id order, the ring holds them all; a slide
// takes the front cell for its place; a fresh slide first sends the cast
// back to the tail, in the order it went out
function expectedPlan(e){const cells=roots(e).slice().sort((a,b)=>a.id-b.id),slides=[];let arc=cells.slice(),cast=[];for(const sd of e.slides2()){if(sd.fresh){arc=arc.concat(cast.map(c=>c.b));cast=[];}if(arc.length){const b=arc[0];arc=arc.slice(1);cast=cast.concat([{b,place:sd.place}]);}slides.push({cast,arc});}return slides;}
// A SLIDE, SETTLED: every cell of the cast stands exactly on its place, a
// rectangle, unlabelled, the first the page's image; every cell of the arc
// in its chamber, in ring order; the bore and the chambers past the arc are
// whitespace that yields, at full claim; the whitespace, the page less the
// stage and the cluster, is exactly its rectangles; every cell one site,
// none a field, none fractured, the count kept; the blurb titled with the
// cast's names inside the box and nowhere else, its lines set, the rule
// drawn.
function settled(st,k,label){
 const e=st.e,T=e.tell2();assert(T&&T.k===k,label+': the story is on slide '+(T&&T.k)+', not '+k);
 const spec=e.tell2Page(k,N),sl=T.story[k],m=sl.cast.length;
 assert.equal(T.on.length,m,label+': '+T.on.length+' on stage, the cast is '+m);
 sl.cast.forEach((c,i)=>{const b=c.b;assert(T.on[i]===b,label+': '+b.name+' is not on stage');assert(!b.leaving,label+': '+b.name+' is leaving');
  assert(rectsEqual(b.rect,spec.content[i]),label+': '+b.name+' is not on its place '+JSON.stringify([b.rect,spec.content[i]]));
  assert(!b.journey||b.progress>=1,label+': '+b.name+' is travelling');assert(b.caption.alpha<.05,label+': '+b.name+' still carries its label');});
 for(let i=0;i<m;i++)for(let j=i+1;j<m;j++)assert(!overlap(sl.cast[i].b.rect,sl.cast[j].b.rect),label+': two of the cast overlap');
 assert(e.focus()===sl.cast[0].b,label+': the first of the cast is not the page\'s image');
 sl.arc.forEach((b,j)=>{assert(rectsEqual(b.rect,spec.content[m+j]),label+': '+b.name+' is not in chamber '+j+' of the ring');assert(!b.journey||b.progress>=1,label+': '+b.name+' is travelling');});
 assert.equal(m+sl.arc.length,N,label+': the cast and the ring do not hold every cell');
 assert.equal(roots(e).length,N,label+': '+roots(e).length+' cells');
 for(const q of roots(e))assert.equal(q.subs.length,1,label+': '+q.name+' has '+q.subs.length+' sites');
 assert(!st.pic.leaves.some(l=>l.path.length>1),label+': a field on the story');
 const vx=voidsExact(st,2);assert(vx.ok,label+': '+vx.why);   // to 2 px: the mirrors of two pieces meeting a chamber's corner cut it by a px or two
 const sh=shapes(st);assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst));
 const px=parseFloat(e.meters().mGap[0])+parseFloat(e.meters().mOver[0]);
 assert(px<=0.003*e.root.W*e.root.H,label+': seam residual '+e.meters().mGap[0]+' gap, '+e.meters().mOver[0]+' overlap');
 // the cast are rectangles: every point of a cast cell's outline lies on its rectangle's boundary, to 2 px
 {const PW=e.root.PW,PH=e.root.PH;for(const c of sl.cast){const b=c.b,l=rootsOf(st.pic).find(l=>l.body===b);assert(l,label+': '+b.name+' has no cell');const r=[b.rect[0]*PW,b.rect[1]*PH,b.rect[2]*PW,b.rect[3]*PH];
  for(const q of l.loops[0])assert(q[0]>r[0]-2&&q[0]<r[2]+2&&q[1]>r[1]-2&&q[1]<r[3]+2&&(Math.abs(q[0]-r[0])<2||Math.abs(q[0]-r[2])<2||Math.abs(q[1]-r[1])<2||Math.abs(q[1]-r[3])<2),label+': '+b.name+' is not a rectangle at '+q.map(v=>v.toFixed(1)));}}   // to 2 px, as the whitespace
 // the whitespace is what the cells leave: no void rectangle overlaps a cell's, and together they cover the page; the bore and the spent chambers yield, and hold their claims at rest
 const voids=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect);
 for(const v of voids)for(const q of roots(e))assert(!overlap(v.rect,q.rect),label+': whitespace over '+q.name);
 const total=voids.reduce((s,v)=>s+(v.rect[2]-v.rect[0])*(v.rect[3]-v.rect[1]),0)+roots(e).reduce((s,q)=>s+(q.rect[2]-q.rect[0])*(q.rect[3]-q.rect[1]),0);
 assert(Math.abs(total-e.root.COLS*e.root.ROWS)<1e-3,label+': the rectangles do not cover the page: '+total.toFixed(3));
 const yielding=voids.filter(v=>v.tell2Yield);assert.equal(yielding.length,1+(spec.chambers.length-sl.arc.length),label+': '+yielding.length+' yielding pieces, expected the bore and '+(spec.chambers.length-sl.arc.length)+' spent chambers');
 assert(voids.some(v=>rectsEqual(v.rect,spec.bore)&&v.tell2Yield),label+': the bore is not a yielding piece');
 for(const v of yielding)assert(v.claim>0.97*v.claimTarget,label+': a yielding piece has not taken its ground back: '+(v.claim/v.claimTarget).toFixed(2));
 const r=spec.box,PW=e.root.PW,PH=e.root.PH,inBox=q=>q[2]>=r[0]*PW&&q[2]<=r[2]*PW&&q[3]>=r[1]*PH&&q[3]<=r[3]*PH;
 const title=sl.cast.map(c=>c.b.name).join(' · '),texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===title);
 assert(T.alpha>.99&&T.rule>.95,label+': the text or the rule are not full: '+T.alpha.toFixed(2)+' '+T.rule.toFixed(2));
 assert(texts.some(inBox),label+': no title in the box');assert(!texts.some(c=>!inBox(c)),label+': the title outside the box');
 assert(e.commands.filter(c=>c[0]==='fill').length>=2,label+': no lines in the box');
 return{k,cast:sl.cast.map(c=>c.b.name+'@'+c.place),ring:sl.arc.map(b=>b.name),voids:voids.length,rest:{rectangle:sh.rectangle,voronoi:sh.voronoi,cut:sh.cut,shortEdged:sh.shortEdged}};
}
// THE ENTRY: no fractured cell on any frame; the text begins only once the
// change has ended, the rule only a beat after the text is full
function through(st,label,frames=480){
 const e=st.e;let endAt=-1,textAt=-1,textFull=-1,ruleAt=-1,ruleFull=-1;
 for(let f=0;f<frames;f++){st.step(1);const T=e.tell2(),sh=shapes(st);assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst)+' at frame '+f);
  if(endAt<0&&f>1&&e.changeLeft()<=0)endAt=f;
  if(endAt<0)assert(T.alpha<1e-6,label+': the text began at frame '+f+' before the change ended');
  if(textAt<0&&T.alpha>0.02)textAt=f;if(textFull<0&&T.alpha>0.97)textFull=f;
  if(textFull<0)assert(T.rule<1e-6,label+': a rule was drawn at frame '+f+' before the text had fully appeared');
  if(ruleAt<0&&T.rule>0.02)ruleAt=f;if(ruleFull<0&&T.rule>0.95)ruleFull=f;}
 assert(endAt>=0&&textAt>=endAt,label+': the text came at '+textAt+', the change ended at '+endAt);
 assert(textFull>=0&&ruleAt>=textFull+12&&ruleFull>ruleAt,label+': the rule did not follow the text a beat later: text full '+textFull+', rule from '+ruleAt+' full '+ruleFull);
 return{endAt,textAt,textFull,ruleAt,ruleFull};
}
// A CHANGE: what moves. One cell out (or the cast back on a fresh slide) and
// the ring one chamber, the cells already on the stage not moving; no path
// crosses another's on an ordinary slide; the whitespace keeps all but the
// pieces the change is about; nothing fractures; the text never dims.
function change(st,k,label){
 const e=st.e,T=e.tell2(),wasOn=T.on.slice(),before=new Map(roots(e).map(b=>[b,{x:b.x,y:b.y,rect:b.rect.slice(0,4)}])),vb=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect).map(v=>rectKey(v.rect));
 e.tell2Go(k);st.step(2);
 const sl=T.story[k],fresh=e.slides2()[k].fresh,staying=wasOn.filter(b=>sl.cast.some(c=>c.b===b));
 const journeys=roots(e).filter(b=>b.journey&&b.path).map(b=>({b,len:Math.hypot(b.path.ex-b.path.sx,b.path.ey-b.path.sy),from:[b.path.sx,b.path.sy],to:[b.path.ex,b.path.ey]})).filter(j=>j.len>1);
 for(const b of staying)assert(!journeys.some(j=>j.b===b),label+': '+b.name+', on the stage already, was sent on a journey');
 const long=journeys.filter(j=>j.len>250),expectedLong=1+(fresh?wasOn.length:0);
 assert(long.length<=expectedLong,label+': '+long.length+' long journeys, expected at most '+expectedLong);
 let crossings=0;for(let i=0;i<journeys.length;i++)for(let j=i+1;j<journeys.length;j++)if(seg(journeys[i].from,journeys[i].to,journeys[j].from,journeys[j].to))crossings++;
 if(!fresh)assert.equal(crossings,0,label+': paths cross');
 let frames=0,frac=0,minAlpha=1,stayMove=0;while(e.changeLeft()>0&&frames<600){st.step(1);frames++;frac+=shapes(st).fractured;minAlpha=Math.min(minAlpha,T.alpha);for(const b of staying){const p=before.get(b);stayMove=Math.max(stayMove,Math.hypot(b.x-p.x,b.y-p.y));}}
 assert.equal(frac,0,label+': a fractured cell in the change');assert(minAlpha>0.97,label+': the text dimmed to '+minAlpha.toFixed(2));
 assert(stayMove<1,label+': a cell on the stage moved '+stayMove.toFixed(1)+' px');
 const va=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect).map(v=>rectKey(v.rect)),kept=va.filter(r=>vb.includes(r)).length;
 assert(vb.length-kept<=2+(fresh?wasOn.length:0),label+': '+(vb.length-kept)+' pieces of whitespace went');
 st.step(180);
 return{k,fresh:!!fresh,moving:journeys.length,long:long.length,crossings,keptPieces:kept+' of '+vb.length,seconds:+(frames/60).toFixed(1)};
}
{ // the story begins: the plan, slide 0, the cast on its place
 const st=fresh(desk),e=st.e;assert.equal(roots(e).length,N);
 e.tell2Start();
 assert.equal(e.config.scene,'tell2','the scene is not tell2');assert(e.tell2()&&e.tell2().k===0,'not on slide 0');
 const want=expectedPlan(e),story=e.tell2().story;
 story.forEach((s,k)=>{assert(s.cast.length===want[k].cast.length&&s.cast.every((c,i)=>c.b===want[k].cast[i].b&&c.place===want[k].cast[i].place),'slide '+k+'\'s cast is not the plan\'s');assert(s.arc.length===want[k].arc.length&&s.arc.every((b,j)=>b===want[k].arc[j]),'slide '+k+'\'s ring is not the plan\'s');});
 const sizes=story.map(s=>s.cast.length);assert(sizes.includes(1)&&sizes.includes(2)&&sizes.includes(3),'the slides do not build up to one, two and three: '+sizes);
 for(let k=1;k<story.length;k++)if(!e.slides2()[k].fresh){assert.equal(story[k].cast.length,story[k-1].cast.length+1,'slide '+k+' does not add one cell');assert(story[k-1].cast.every((c,i)=>story[k].cast[i].b===c.b&&story[k].cast[i].place===c.place),'slide '+k+' moved a cell already on the stage');}
 report.text=through(st,'start');
 report.start=settled(st,0,'slide 0');report.slides.push(report.start);
 report.changes=[];
 for(let k=1;k<story.length;k++){report.changes.push(change(st,k,'slide '+(k-1)+'->'+k));report.slides.push(settled(st,k,'slide '+k));}
 // the ends: a push past the last slide stays on it
 const last=(e.slides2().length-1)*e.root.H;e.tell2Push(1000);st.step(300);
 assert(Math.abs(e.tell2().y-last)<1e-6&&e.tell2().k===e.slides2().length-1,'the story ran past its end: y '+e.tell2().y.toFixed(0));
 // back to the start: the same plan
 e.tell2Go(0);st.step(480);assert.equal(e.tell2().k,0,'the story did not go back to slide 0');
 e.tell2Push(-1000);st.step(300);assert(e.tell2().y===0,'the story ran past its start');
 report.ends={last:e.slides2().length-1};report.back=settled(st,0,'slide 0 again');
 // home: any of the cast clicked goes home, the count returns, every root cell numbered
 const b=e.tell2().on[0];e.click(b.x,b.y);assert.equal(e.config.scene,'bento');assert.equal(e.focus(),null);assert(!e.tell2(),'the story stayed');
 st.step(300);const rs=rootsOf(st.pic);assert.equal(roots(e).length,N,'home lost cells');assert(rs.length>=5&&rs.every(q=>q.body.caption.alpha>.95),'home lost numbers');
 assert(!e.root.bodies.some(q=>q.rect&&q.rect.reelLive)&&!e.root.bodies.some(q=>q.tell2Yield||q.tell2Stay),'the story left its marks at home');
 report.home={cells:roots(e).length,roots:rs.length,numbers:rs.filter(q=>q.body.caption.alpha>.95).length};
}
{ // a notch is a slide, whatever its size: one on, a tiny one on, one back; three quick ones spin the story on by less than three
 const st=fresh(desk),e=st.e;e.tell2Start();st.step(480);
 const notch=(dy,k,label)=>{e.tell2Push(dy);st.step(150);assert.equal(e.tell2().k,k,label+': slide '+e.tell2().k+', not '+k);assert(Math.abs(e.tell2().y-k*e.root.H)<0.5,label+': not settled on its slide: y '+e.tell2().y.toFixed(1));};
 notch(100,1,'a notch');notch(120,2,'a larger notch');notch(3,3,'a trackpad tick');notch(-100,2,'a notch back');
 e.tell2Push(100);st.step(10);e.tell2Push(100);st.step(10);e.tell2Push(100);st.step(480);const spun=e.tell2().k-2;assert(spun>=1&&spun<=2,'three quick notches turned '+spun+' slides');
 settled(st,e.tell2().k,'slide '+e.tell2().k+' by notches');report.notch={one:1,tiny:1,back:-1,threeQuick:spun};
}
{ // the drag and the flick, the snap
 const st=fresh(desk),e=st.e;e.tell2Start();st.step(480);
 let t=e.time()*1000;assert(e.tell2DragStart(900,600,t),'the drag did not take the story');const y0=e.tell2().y;
 for(let f=1;f<=12;f++){t=e.time()*1000;e.tell2DragMove(900,600-60*f,t);st.step(1);}
 assert(Math.abs(e.tell2().y-y0-720)<1e-6,'the story did not follow the hand: '+(e.tell2().y-y0).toFixed(1));
 e.tell2DragEnd(e.time()*1000);assert(e.tell2().v>600,'no flick: v '+e.tell2().v.toFixed(0));
 let frac=0;for(let f=0;f<600;f++){st.step(1);frac+=shapes(st).fractured;}assert.equal(frac,0,'a fractured cell in the flick');
 const kd=e.tell2().k;assert(kd>=2,'the flick carried the story only to slide '+kd);
 assert(Math.abs(e.tell2().y-kd*e.root.H)<0.5,'the story did not snap to its slide: y '+e.tell2().y.toFixed(1));
 report.drag={slide:kd,...settled(st,kd,'slide '+kd+' after the flick')};
 e.tell2Move(0.3*e.root.H);st.step(180);assert.equal(e.tell2().k,kd,'a short move turned the slide');assert(Math.abs(e.tell2().y-kd*e.root.H)<0.5,'a short move did not ease back');
 e.tell2Move(0.6*e.root.H);st.step(480);assert.equal(e.tell2().k,kd+1,'a long move did not turn the slide');settled(st,kd+1,'slide '+(kd+1)+' by a move');report.snap={short:0.3,long:0.6};
}
{ // a notch during the entry: the change that wins is the slide's, and it ends exact
 const st=fresh(desk),e=st.e;e.tell2Start();st.step(18);e.tell2Push(100);
 let frac=0,k=-1;for(let f=0;f<540;f++){st.step(1);frac+=shapes(st).fractured;if(k<0&&e.tell2().k!==0)k=f;}
 assert.equal(frac,0,'a fractured cell in the interrupted entry');assert(k>=0,'the notch during the entry did not turn the slide');
 report.interrupted={turnedAt:k,...settled(st,1,'interrupted')};
}
{ // a phone: the box a band across the top, the stage a row below it, the ring at the foot facing up; the story builds the same way
 const st=fresh(phone),e=st.e;e.tell2Start();
 const tx=through(st,'phone');const r0=settled(st,0,'phone slide 0');
 const R=e.root.ROWS;for(const b of e.tell2().on)assert(b.rect[1]>=0.36*R-1e-6&&b.rect[3]<=0.56*R+1e-6,'phone: the stage is not the row below the band');
 const rows=[];for(let k=1;k<=3;k++){rows.push(change(st,k,'phone slide '+(k-1)+'->'+k));}
 const r3=settled(st,3,'phone slide 3');
 report.phone={text:tx,slides:[r0,r3],changes:rows};
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without the Tell II button, state and every drawing command must exactly match Tell, a click, a scroll, a Tell story and home included; with the story, the plan builds each sequence up one cell at a time and sends it back on a fresh slide, every slide settled has its cast exactly on its places (rectangles, unlabelled, the first the page\'s image), the ring\'s cells in their chambers in the order they will go out, the bore and the spent chambers yielding whitespace at full claim, the whitespace exactly the rectangles the cells leave, every cell one site and never fractured; every change moves one cell out (the cast back on a fresh slide) and the ring one chamber with the cells on the stage still, no path crossing another on an ordinary slide, at most two pieces of whitespace changing, no fracture and the text never dimming; the wheel, a drag and a flick move the story, a slow story snaps to its slide, the story stops at its ends, and home returns the count.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,drawingCommands:commandsTotal,story:report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,story:report}));
