// Tell adds a scroll-tell: the cluster is laid once beside a reading column
// and stays while a story of blurbs scrolls through the column, each slide's
// hero swelling where it stands. Without the Tell button, the real tick must produce exactly
// the same state and the same drawing commands as Reel, a click, a scroll and
// home included; with the story, the cluster never moves, every hero is the
// card nearest its slide's place swollen in place with the column exact, the
// text comes once the entry has ended and the rules a beat later and stays,
// the wheel, a drag and a flick move the story, a slow story snaps to its
// slide, the story stops at its ends, and home returns the count.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const rectsEqual=(a,b)=>a&&b&&a.length>=4&&b.length>=4&&a.slice(0,4).every((v,i)=>Math.abs(v-b[i])<1e-6);
const files=[path.resolve(__dirname,'../../reel.html'),path.resolve(__dirname,'../../tell.html')];
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
 assert(!es[1].tell(),'a story without the Tell button');
 report.clickIdentity={frames:frame,kind:'band'};
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
const column=e=>e.root.bodies.find(v=>v.isVoid&&!v.leaving&&v.rect&&v.rect.portalText);
const rectKey=r=>r.slice(0,4).map(v=>v.toFixed(6)).join(',');
// THE HEROES ARE CHOSEN FROM THE CLUSTER AS LAID: for each slide the card whose
// rectangle's centre is nearest the slide's place, not one of the last two
function expectedHeroes(e,layout){const g=e.tellPage(N).region,out=[];for(const sd of e.slides()){const px=g[0]+sd.at[0]*(g[2]-g[0]),py=g[1]+sd.at[1]*(g[3]-g[1]),recent=out.slice(-2);let best=null,bd=Infinity;for(const [b,r] of layout){if(recent.includes(b))continue;const d=Math.hypot((r[0]+r[2])/2-px,(r[1]+r[3])/2-py);if(d<bd){bd=d;best=b;}}out.push(best);}return out;}
// A SLIDE, SETTLED: the cluster is where it was laid at the start (every card's
// rectangle the same, no re-lay, nothing travelling); the hero is the slide's,
// swollen to a fifth of the cluster where it stands, the page's image; the
// column is exactly its rectangle; every cell one site, none a wall, none a
// field, none fractured, the count kept; the blurb titled with the hero's name
// inside the column and nowhere else, its lines set, the rules drawn; the
// hero without its label; no other card swollen.
function settled(st,k,label){
 const e=st.e,T=e.tell();assert(T&&T.k===k,label+': the story is on slide '+(T&&T.k)+', not '+k);
 const b=e.focus();assert(b&&T.heroes[k]===b,label+': the image is not the slide\'s hero');
 assert.equal(e.root.serial,st.serial,label+': the cluster was laid again');
 for(const q of roots(e)){assert.equal(rectKey(q.rect),rectKey(st.layout.get(q)),label+': '+q.name+' moved from where the cluster was laid');assert(!q.journey||q.progress>=1,label+': '+q.name+' is travelling');}
 assert.equal(roots(e).length,N,label+': '+roots(e).length+' cells');
 for(const q of roots(e))assert.equal(q.subs.length,1,label+': '+q.name+' has '+q.subs.length+' sites');
 assert(!e.root.bodies.some(q=>q.wall&&!q.isVoid),label+': a card is a wall');
 assert(!st.pic.leaves.some(l=>l.path.length>1),label+': a field on the story');
 const vx=voidsExact(st);assert(vx.ok,label+': '+vx.why);
 const sh=shapes(st);assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst));
 const px=parseFloat(e.meters().mGap[0])+parseFloat(e.meters().mOver[0]);
 assert(px<=0.003*e.root.W*e.root.H,label+': seam residual '+e.meters().mGap[0]+' gap, '+e.meters().mOver[0]+' overlap');
 // the swell: the hero holds a fifth of the cluster, to a hairline; every other card its mix at zero
 const g=e.tellPage(N).region,cluster=(g[2]-g[0])*(g[3]-g[1])*e.root.PW*e.root.PH,lf=rootsOf(st.pic).find(l=>l.body===b);
 assert(lf,label+': the hero has no cell');const share=area(lf)/cluster;
 assert(Math.abs(share-0.2)<0.01,label+': the hero holds '+(share*100).toFixed(1)+'% of the cluster, not 20%');
 assert(Math.abs(b.tellMix-1)<1e-3,label+': the hero\'s mix is '+b.tellMix);   // the snap leaves the story a hair off its slide
 for(const q of roots(e))if(q!==b)assert(!(q.tellMix>1e-3),label+': '+q.name+' is swollen too ('+q.tellMix+')');
 const v=column(e);assert(v&&v.crystal>=.99,label+': no seated column');const r=v.rect,PW=e.root.PW,PH=e.root.PH;
 assert(rectsEqual(r,e.tellPage(N).voids[0]),label+': the column is not the story\'s');
 const inVoid=q=>q[2]>=r[0]*PW&&q[2]<=r[2]*PW&&q[3]>=r[1]*PH&&q[3]<=r[3]*PH;
 const texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===b.name);   // the hero's name: the blurb's title, and nowhere else (the cards keep their numbers)
 assert(T.alpha>.99&&T.rule>.95,label+': the text or the rules are not full: '+T.alpha.toFixed(2)+' '+T.rule.toFixed(2));
 assert(texts.some(inVoid),label+': no title in the column');
 assert(!texts.some(c=>!inVoid(c)),label+': the hero\'s name outside the column');
 assert(e.commands.filter(c=>c[0]==='fill').length>=2,label+': no lines in the column');
 assert(b.caption.alpha<.05,label+': the hero still carries its label');
 return{k,hero:b.name,share:+share.toFixed(3),rest:{rectangle:sh.rectangle,voronoi:sh.voronoi,cut:sh.cut,shortEdged:sh.shortEdged}};
}
// THE ENTRY: no fractured cell on any frame; the text begins only once the
// change has ended, the rules only a beat after the text is full; no hero
// swells before the entry has ended
function through(st,label,frames=420){
 const e=st.e;let endAt=-1,textAt=-1,textFull=-1,ruleAt=-1,ruleFull=-1,swellAt=-1;
 for(let f=0;f<frames;f++){st.step(1);const T=e.tell(),sh=shapes(st);assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst)+' at frame '+f);
  if(endAt<0&&e.changeLeft()<=0)endAt=f;
  if(endAt<0)assert(T.alpha<1e-6,label+': the text began at frame '+f+' before the change ended');
  if(endAt<0)assert(!(T.enter>0),label+': a hero swelled at frame '+f+' before the change ended');
  if(swellAt<0&&T.enter>0.02)swellAt=f;
  if(textAt<0&&T.alpha>0.02)textAt=f;if(textFull<0&&T.alpha>0.97)textFull=f;
  if(textFull<0)assert(T.rule<1e-6,label+': a rule was drawn at frame '+f+' before the text had fully appeared');
  if(ruleAt<0&&T.rule>0.02)ruleAt=f;if(ruleFull<0&&T.rule>0.95)ruleFull=f;}
 assert(endAt>=0&&textAt>=endAt,label+': the text came at '+textAt+', the change ended at '+endAt);
 assert(swellAt>=endAt,label+': the hero swelled at '+swellAt+', the change ended at '+endAt);
 assert(textFull>=0&&ruleAt>=textFull+12&&ruleFull>ruleAt,label+': the rules did not follow the text a beat later: text full '+textFull+', rules from '+ruleAt+' full '+ruleFull);
 return{endAt,swellAt,textAt,textFull,ruleAt,ruleFull};
}
// the cluster as laid: every card's rectangle after the entry, and the page's serial
function laid(st){const e=st.e;st.layout=new Map(roots(e).map(b=>[b,b.rect.slice(0,4)]));st.serial=e.root.serial;}
{ // the story begins: the cluster laid once beside the column, the heroes chosen from it
 const st=fresh(desk),e=st.e;assert.equal(roots(e).length,N);
 e.tellStart();
 assert.equal(e.config.scene,'tell','the scene is not tell');assert(e.tell()&&e.tell().k===0,'not on slide 0');
 assert.equal(e.tell().heroes.length,e.slides().length,'not every slide has a hero');
 report.text=through(st,'start');laid(st);
 const want=expectedHeroes(e,st.layout);e.tell().heroes.forEach((h,k)=>assert(h===want[k],'slide '+k+'\'s hero is '+h.name+', the nearest card not among the last two was '+want[k].name));
 for(let k=0;k<want.length;k++)assert(want[k]!==want[k-1]&&want[k]!==want[k-2],'slide '+k+' reuses a recent hero');
 report.start=settled(st,0,'slide 0');report.slides.push(report.start);
 // a wheel notch: the story moves on one slide; the cluster stays, the next hero swells where it stands as the first shrinks, the text stays
 const prev=e.focus();e.tellPush(100);let changed=-1,minAlpha=1,crossing=false;
 for(let f=0;f<240;f++){st.step(1);const T=e.tell();minAlpha=Math.min(minAlpha,T.alpha);if(changed<0&&T.k===1)changed=f;
  if(T.y>0.3*e.root.H&&T.y<0.7*e.root.H){crossing=true;assert(Math.abs(T.heroes[0].tellMix+T.heroes[1].tellMix-1)<1e-9,'the two heroes\' mixes do not sum to one between the slides');}
  for(const q of roots(e))assert.equal(rectKey(q.rect),rectKey(st.layout.get(q)),'the cluster moved at frame '+f+' of the notch');}
 assert(changed>=0,'the notch did not turn the slide');assert(e.focus()!==prev,'the hero did not change');assert(crossing,'the story never crossed between the slides');
 assert(minAlpha>0.97,'the text was hidden by the slide change: alpha '+minAlpha.toFixed(2));
 st.step(120);report.push={changedAt:changed,...settled(st,1,'slide 1')};report.slides.push(report.push);
 // a drag held half way: both heroes half swollen, the cluster exact; a flick carries the story on to snap onto a slide
 let t=e.time()*1000;assert(e.tellDragStart(900,600,t),'the drag did not take the story');const y0=e.tell().y;
 for(let f=1;f<=6;f++){t=e.time()*1000;e.tellDragMove(900,600-e.root.H/12*f,t);st.step(1);}st.step(30);
 assert(Math.abs(e.tell().y-y0-e.root.H/2)<1e-6,'the story did not follow the hand: '+(e.tell().y-y0).toFixed(1));
 {const T=e.tell();assert(Math.abs(T.heroes[1].tellMix-0.5)<1e-9&&Math.abs(T.heroes[2].tellMix-0.5)<1e-9,'held half way the heroes are not half swollen');
  const v=voidsExact(st);assert(v.ok,'held half way: '+v.why);const g=e.tellPage(N).region,cluster=(g[2]-g[0])*(g[3]-g[1])*e.root.PW*e.root.PH;
  const s1=area(rootsOf(st.pic).find(l=>l.body===T.heroes[1]))/cluster,s2=area(rootsOf(st.pic).find(l=>l.body===T.heroes[2]))/cluster;
  assert(s1>0.1&&s1<0.2&&s2>0.1&&s2<0.2,'held half way the heroes hold '+(s1*100).toFixed(0)+'% and '+(s2*100).toFixed(0)+'%');}
 for(let f=1;f<=6;f++){t=e.time()*1000;e.tellDragMove(900,300-60*f,t);st.step(1);}
 e.tellDragEnd(e.time()*1000);assert(e.tell().v>600,'no flick: v '+e.tell().v.toFixed(0));
 let frac=0;for(let f=0;f<300;f++){st.step(1);frac+=shapes(st).fractured;}assert.equal(frac,0,'a fractured cell in the flick');
 const kd=e.tell().k;assert(kd>=2,'the flick carried the story only to slide '+kd);
 assert(Math.abs(e.tell().y-kd*e.root.H)<0.5,'the story did not snap to its slide: y '+e.tell().y.toFixed(1));
 report.drag={slide:kd,...settled(st,kd,'slide '+kd+' after the flick')};report.slides.push(report.drag);
 // every slide on: each hero swells in its place, the cluster never moving
 for(let k=kd+1;k<e.slides().length;k++){e.tellGo(k);st.step(150);report.slides.push(settled(st,k,'slide '+k));}
 // the ends: a push past the last slide stays on it, and the story stays exact
 const last=(e.slides().length-1)*e.root.H;e.tellPush(1000);st.step(300);
 assert(Math.abs(e.tell().y-last)<1e-6&&e.tell().k===e.slides().length-1,'the story ran past its end: y '+e.tell().y.toFixed(0));
 {const v=voidsExact(st);assert(v.ok,'not exact at the end: '+v.why);}
 // back to the start: the same heroes, the same cluster
 e.tellGo(0);st.step(150);assert.equal(e.tell().k,0,'the story did not go back to slide 0');
 e.tellPush(-1000);st.step(300);assert(e.tell().y===0,'the story ran past its start');
 report.ends={last:e.slides().length-1};report.back=settled(st,0,'slide 0 again');
 // home: the hero clicked goes home, the count returns, every root cell numbered, nothing swollen
 const b=e.focus();e.click(b.x,b.y);assert.equal(e.config.scene,'bento');assert.equal(e.focus(),null);assert(!e.tell(),'the story stayed');
 st.step(300);const rs=rootsOf(st.pic);assert.equal(roots(e).length,N,'home lost cells');assert(rs.length>=5&&rs.every(q=>q.body.caption.alpha>.95),'home lost numbers');   // home is the bento with its fields: some cells are clusters
 assert(!roots(e).some(q=>q.tellMix>0||q.reelPinned),'a card kept its swell or its pin at home');
 report.home={cells:roots(e).length,roots:rs.length,numbers:rs.filter(q=>q.body.caption.alpha>.95).length};
}
{ // a notch is a slide, whatever its size: one on, a tiny one on, one back; three quick ones spin the story on by less than three
 const st=fresh(desk),e=st.e;e.tellStart();st.step(420);laid(st);
 const notch=(dy,k,label)=>{e.tellPush(dy);st.step(150);assert.equal(e.tell().k,k,label+': slide '+e.tell().k+', not '+k);assert(Math.abs(e.tell().y-k*e.root.H)<0.5,label+': not settled on its slide: y '+e.tell().y.toFixed(1));};
 notch(100,1,'a notch');notch(120,2,'a larger notch');notch(3,3,'a trackpad tick');notch(-100,2,'a notch back');
 e.tellPush(100);st.step(10);e.tellPush(100);st.step(10);e.tellPush(100);st.step(300);const spun=e.tell().k-2;assert(spun>=1&&spun<=2,'three quick notches turned '+spun+' slides');
 settled(st,e.tell().k,'slide '+e.tell().k+' by notches');report.notch={one:1,tiny:1,back:-1,threeQuick:spun};
}
{ // the snap: a short move eases back to its slide, a long one on to the next
 const st=fresh(desk),e=st.e;e.tellStart();st.step(420);laid(st);
 e.tellMove(0.3*e.root.H);st.step(180);assert.equal(e.tell().k,0,'a short move turned the slide');assert(e.tell().y<0.5,'a short move did not ease back: y '+e.tell().y.toFixed(1));
 e.tellMove(0.6*e.root.H);st.step(180);assert.equal(e.tell().k,1,'a long move did not turn the slide');assert(Math.abs(e.tell().y-e.root.H)<0.5,'a long move did not settle on the slide: y '+e.tell().y.toFixed(1));
 settled(st,1,'slide 1 by a move');report.snap={short:0.3,long:0.6};
}
{ // a notch during the entry: the story turns, the cluster still arrives as laid, and settles exact
 const st=fresh(desk),e=st.e;e.tellStart();st.step(18);e.tellPush(100);
 let frac=0,k=-1;for(let f=0;f<420;f++){st.step(1);frac+=shapes(st).fractured;if(k<0&&e.tell().k!==0)k=f;}
 assert.equal(frac,0,'a fractured cell in the interrupted entry');assert(k>=0,'the notch during the entry did not turn the slide');laid(st);
 report.interrupted={turnedAt:k,...settled(st,1,'interrupted')};
}
{ // a phone: the column a band across the top, the cluster below; the story turns the same way
 const st=fresh(phone),e=st.e;e.tellStart();
 const tx=through(st,'phone');laid(st);
 const want=expectedHeroes(e,st.layout);e.tell().heroes.forEach((h,k)=>assert(h===want[k],'phone: slide '+k+'\'s hero is '+h.name+', not '+want[k].name));
 const r0=settled(st,0,'phone slide 0');
 const v=column(e);assert(rectsEqual(v.rect,[0,0,e.root.COLS,Math.round(0.3*e.root.ROWS)]),'phone: the column is not the band across the top');
 for(const q of roots(e))assert(q.rect[1]>=Math.round(0.3*e.root.ROWS)-1e-6,'phone: '+q.name+' is not below the band');
 e.tellPush(100);st.step(240);const r1=settled(st,1,'phone slide 1');
 report.phone={text:tx,slides:[r0,r1]};
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without the Tell button, state and every drawing command must exactly match Reel, a click, a scroll, a drag and home included; with the story, the cluster is laid once beside the column and never moves again, every slide\'s hero is the card nearest the slide\'s place (not one of the last two), swollen where it stands to a fifth of the cluster with the column exactly the rectangle it was given, every cell one site and never fractured, the text set once the entry has ended and the rules a beat later and kept through every slide, a wheel notch of any size turning one slide, a drag held half way leaving two heroes half swollen, a flick carrying the story on, a slow story snapping to its slide, the story stopping at its ends, and home returning the count.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,drawingCommands:commandsTotal,story:report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,story:report}));
