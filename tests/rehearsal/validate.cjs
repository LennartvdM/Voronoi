// Rehearsal: the hive plays a change first where nobody sees it. A copy of
// the world is run ahead to the change's end and its defects counted; the
// plan (when each cell sets off) is revised while a budget of rehearsals
// lasts, and the plan that rehearsed best is played. Checked, on a tour of
// changes (home's scenes, home to a page of every kind and back, and page to
// page) on a desk and a phone, at frames of 1/64 s (a length a float holds
// exactly, so that every frame is as long as the rehearsal's):
// - a rehearsal leaves no trace: with a budget of one, the plan rehearsed is
//   Shoal's own, and every frame of the tour, the world and every drawing
//   command, is Shoal's;
// - what it rehearses is what it plays: on every rehearsed change the page
//   the performance steps through is the chosen rehearsal's, frame by frame,
//   every cell's seed, speed, claim and sites to the bit, and it scores what
//   the rehearsal scored;
// - it never plays worse than Shoal's plan: the chosen plan rehearses no
//   worse than Shoal's from the same start;
// - a change from page to page, and a story, is not rehearsed;
// - nothing fractures on any frame, and every page at rest is exact as on
//   Shoal;
// - thinking spread over the page's frames holds the page still (nothing
//   moves, the clock stands) and then plays what thinking at once plays; a
//   change asked for while it thinks starts the thinking afresh.
// While a story is told nothing is rehearsed: every frame of a Cue story is
// Shoal's, Cue's own story checks pass on a desk and a phone, and a Tell and
// a Tell II story run to their end and home.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {loadEngine}=require('./probe.cjs');
const rectsEqual=(a,b)=>a&&b&&a.length>=4&&b.length>=4&&a.slice(0,4).every((v,i)=>Math.abs(v-b[i])<1e-6);
const files=[path.resolve(__dirname,'../../shoal.html'),path.resolve(__dirname,'../../rehearsal.html')];
const report={trace:null,desk:null,phone:null,thinking:null,story:null,slides:[],changes:[],back:null,hurried:null,phone2:null,home:null,tell:null};
// --- the story ------------------------------------------------------------------
const area=l=>Math.abs(l.loops[0].reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
const rootsOf=pic=>pic.leaves.filter(l=>!l.isVoid&&l.loops.length&&l.path.length===1&&!l.body.leaving);
function fresh(cfg){const e=loadEngine(files[1],{...cfg,record:true});let ms=1000;const st={e,pic:null,step(n){for(let f=0;f<n;f++){e.clear();st.pic=e.advance(ms);ms+=1000/60;}return st.pic;}};st.step(300);return st;}
const ring=pts=>Math.abs(pts.reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
// THE WHITESPACE IS EXACT: every point of every void's outline lies in the
// union of the voids' rectangles, and no root cell's vertex lies inside one
function voidsExact(st,eps=.05,pen=[]){   // the pen's cells are its own pocket's power cells, not rectangles: the whitespace is exact outside the pen
 const e=st.e,PW=e.root.PW,PH=e.root.PH;
 const inPen=p=>pen.some(r=>p[0]>r[0]*PW-eps&&p[0]<r[2]*PW+eps&&p[1]>r[1]*PH-eps&&p[1]<r[3]*PH+eps);
 const boxes=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect).map(v=>[v.rect[0]*PW,v.rect[1]*PH,v.rect[2]*PW,v.rect[3]*PH]);
 const inBox=(p,b,d)=>p[0]>b[0]+d&&p[0]<b[2]-d&&p[1]>b[1]+d&&p[1]<b[3]-d;
 for(const l of st.pic.leaves){
  if(l.path.length!==1)continue;
  for(const lp of l.loops)for(const p of lp){
   if(inPen(p))continue;
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
 const slots=e.cueSlots(N),held=roots(e).filter(b=>!T.on.includes(b));
 for(const b of held)assert(slots.some(r=>rectsEqual(b.rect,r)),label+': '+b.name+' is not on a slot of the pen');
 assert.equal(new Set(held.map(b=>slots.findIndex(r=>rectsEqual(b.rect,r)))).size,held.length,label+': two cells on one slot');
 // THE PEN IS WHOLE: no whitespace in it, drawn or bid for, and its cells,
 // drawn, cover it
 const frame=e.penFrame(),fpx=[frame[0]*PW,frame[1]*PH,frame[2]*PW,frame[3]*PH];
 assert(!e.root.bodies.some(v=>v.isVoid&&!v.leaving&&v.rect&&overlap(v.rect,frame)),label+': whitespace bid for in the pen');
 for(const l of st.pic.leaves)if(l.path.length===1&&l.isVoid)for(const lp of l.loops)for(const q of lp)assert(!(q[0]>fpx[0]+4&&q[0]<fpx[2]-4&&q[1]>fpx[1]+4&&q[1]<fpx[3]-4),label+': whitespace drawn in the pen at '+q.map(v=>+v.toFixed(1)));
 const penDrawn=rootsOf(st.pic).filter(l=>held.includes(l.body)).reduce((q,l)=>q+l.loops.reduce((a,lp)=>a+(lp.hole?-1:1)*ring(lp),0),0),penArea=(fpx[2]-fpx[0])*(fpx[3]-fpx[1]);
 assert(Math.abs(penDrawn/penArea-1)<0.01,label+': the pen\'s cells cover '+(100*penDrawn/penArea).toFixed(1)+'% of it');
 for(const q of roots(e))assert.equal(q.subs.length,1,label+': '+q.name+' has '+q.subs.length+' sites');
 assert(!st.pic.leaves.some(l=>l.path.length>1),label+': a field on the story');
 const vx=voidsExact(st,4,[frame]);assert(vx.ok,label+': '+vx.why);   // to 4 px: no weights are handed, and the live auction settles a hair off the authored diagram where two pieces meet a cell's corner
 const sh=shapes(st);assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst));
 const px=parseFloat(e.meters().mGap[0])+parseFloat(e.meters().mOver[0]);
 assert(px<=0.003*e.root.W*e.root.H,label+': seam residual '+e.meters().mGap[0]+' gap, '+e.meters().mOver[0]+' overlap');
 const voids=e.root.bodies.filter(v=>v.isVoid&&!v.leaving&&v.rect);
 for(const v of voids)for(const q of roots(e))assert(!overlap(v.rect,q.rect),label+': whitespace over '+q.name);
 const total=voids.concat(T.on).reduce((s,q)=>s+(q.rect[2]-q.rect[0])*(q.rect[3]-q.rect[1]),0)+(frame[2]-frame[0])*(frame[3]-frame[1]);   // the whitespace, the cast and the pen, whose cells cover it (above)
 assert(Math.abs(total-e.root.COLS*e.root.ROWS)<1e-3,label+': the rectangles do not cover the page: '+total.toFixed(3));
 const title=T.on.map(b=>b.name).join(' · '),bx=e.root.W<e.root.H?[.04,.04,.96,.34]:[.23,.25,.59,.75];
 const inBox=q=>q[2]>=bx[0]*e.root.W&&q[2]<=bx[2]*e.root.W&&q[3]>=bx[1]*e.root.H&&q[3]<=bx[3]*e.root.H;
 const texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===title);
 assert(T.alpha>.99,label+': the text is not full');assert(texts.some(inBox),label+': no title in the box');assert(!texts.some(c=>!inBox(c)),label+': the title outside the box');
 return{k,cast:T.on.map(b=>b.name),penCovered:+(penDrawn/penArea).toFixed(4),offRect:+worst.toFixed(1),voids:voids.length,rest:{rectangle:sh.rectangle,voronoi:sh.voronoi,cut:sh.cut}};
}
// A CHANGE: the cells on the stage that the slide keeps hold still, the
// cells of the pen that stay keep their slots and settle in the pen, no two
// cards in flight overlap, and no two cells on their way that are not both
// cards come within half their reaches added; going
// on in a sequence, one cell comes out and the others keep their places; a
// fresh slide sends the last cast home and brings out a cell that was none
// of it; nothing fractures on any frame, and the change ends
// a convex polygon clipped to another, and a polygon's area
function clipConvex(S,C){let out=S,sg=0;const n=C.length;for(let i=0;i<n;i++){const p=C[i],q=C[(i+1)%n];sg+=p[0]*q[1]-q[0]*p[1];}sg=Math.sign(sg);
 for(let i=0;i<n&&out.length;i++){const A=C[i],B=C[(i+1)%n],side=P=>sg*((B[0]-A[0])*(P[1]-A[1])-(B[1]-A[1])*(P[0]-A[0])),inp=out;out=[];
  for(let j=0;j<inp.length;j++){const P=inp[j],Q=inp[(j+1)%inp.length],dp=side(P),dq=side(Q);if(dp>=0)out.push(P);if((dp>=0)!==(dq>=0)){const t=dp/(dp-dq);out.push([P[0]+t*(Q[0]-P[0]),P[1]+t*(Q[1]-P[1])]);}}}
 return out.length>=3?out:null;}
function polyArea(P){let a=0;for(let i=0;i<P.length;i++){const p=P[i],q=P[(i+1)%P.length];a+=p[0]*q[1]-q[0]*p[1];}return Math.abs(a/2);}
function change(st,k,label){
 const e=st.e,T=e.cue(),from=T.k,was=T.on.slice(),before=new Map(roots(e).map(b=>[b,{x:b.x,y:b.y,rect:b.rect.slice(0,4)}])),fresh=!!e.slides2()[k].fresh&&k>from;
 e.cueGo(k);st.step(2);
 const now=T.on.slice(),kept=was.filter(b=>now.includes(b));
 if(fresh){assert.equal(kept.length,0,label+': a cell of the last sequence stayed on');assert.equal(now.length,1,label+': a fresh slide has '+now.length+' on stage');}
 else if(k===from+1){assert.deepEqual(now.slice(0,was.length).map(b=>b.name),was.map(b=>b.name),label+': the cast already on the stage did not keep its places');assert.equal(now.length,was.length+1,label+': not one cell more');}
 const penStay=roots(e).filter(b=>!now.includes(b)&&!was.includes(b));
 const frame=e.penFrame(),PW=e.root.PW,PH=e.root.PH,inPen=(x,y)=>x>=frame[0]*PW-1&&x<=frame[2]*PW+1&&y>=frame[1]*PH-1&&y<=frame[3]*PH+1;
 let settle=0;for(const b of penStay){assert(rectsEqual(b.rect,before.get(b).rect),label+': '+b.name+', in the pen, left its slot');const p=b.path;if(!p)continue;settle=Math.max(settle,Math.hypot(p.ex-p.sx,p.ey-p.sy));
  for(let k=0;k<=10;k++){const t=k/10,m=1-t,x=m*m*p.sx+2*m*t*p.cx+t*t*p.ex,y=m*m*p.sy+2*m*t*p.cy+t*t*p.ey;assert(inPen(x,y),label+': '+b.name+', in the pen, was sent out of it');}}   // the cells of the pen settle where they are, in it
 let frames=0,frac=0,stayMove=0,close=Infinity,over=0;
 const movers=roots(e).filter(b=>b.path&&Math.hypot(b.path.ex-b.path.sx,b.path.ey-b.path.sy)>4&&!rectsEqual(b.rect,before.get(b).rect)),reach=b=>0.5*Math.sqrt(Math.max(b.claim0||0,b.claimTarget||0)*e.root.PW*e.root.PH),going=b=>b.journey&&b.progress>0.05&&b.progress<0.9;   // travellers: a cell settling on its own slot of the pen is none
 while(e.changeLeft()>0&&frames<600){st.step(1);frames++;frac+=shapes(st).fractured;for(const b of kept){const p=before.get(b);stayMove=Math.max(stayMove,Math.hypot(b.x-p.x,b.y-p.y));}
  for(let i=0;i<movers.length;i++)for(let j=i+1;j<movers.length;j++){const a=movers[i],c=movers[j];
   if(a.cueFly&&c.cueFly&&a.hole&&c.hole){const x=clipConvex(a.hole.pts,c.hole.pts);if(x)over=Math.max(over,polyArea(x)/Math.min(polyArea(a.hole.pts),polyArea(c.hole.pts)));continue;}   // two cards in flight: their shapes
   if(going(a)&&going(c))close=Math.min(close,Math.hypot(a.x-c.x,a.y-c.y)/(reach(a)+reach(c)));}}
 assert(close>=0.5,label+': two cells on their way came within '+close.toFixed(2)+' of their reaches added');   // the change looks ahead: they pass close, never through each other
 assert(over<0.01,label+': two cards in flight overlapped by '+(100*over).toFixed(1)+'% of the smaller');   // cards pass close, never over each other
 assert(frames<600,label+': the change did not end');assert.equal(frac,0,label+': a fractured cell in the change');
 assert(stayMove<1,label+': a cell on the stage moved '+stayMove.toFixed(1)+' px');
 st.step(240);
 return{k,fresh,cast:now.map(b=>b.name),kept:kept.length,penStayed:penStay.length,penSettle:+settle.toFixed(1),closest:close===Infinity?null:+close.toFixed(2),cardOverlap:+over.toFixed(4),seconds:+(frames/60).toFixed(1)};
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
{ // THE STORY SCROLLED ON BEFORE A CHANGE ENDS: a card of the cast still on
  // its way to the place the next slide keeps it on goes on as it was going,
  // on the same journey, and is still once it has landed; a card of the cast
  // that is still stays still
 const st=fresh(desk),e=st.e;e.cueStart();st.step(420);const out=[];
 for(const [a,b,c] of [[0,1,2],[5,6,7]]){
  e.cueGo(a);st.step(420);e.cueGo(b);st.step(36);
  const landing=e.cue().on.filter(q=>!q.wall).map(q=>({q,j:q.journey})),still=e.cue().on.filter(q=>q.wall);
  assert(landing.length,'slides '+a+'->'+b+'->'+c+': no card of the cast still on its way');
  e.cueGo(c);let wallAt=new Map();
  for(let f=0;f<240;f++){st.step(1);
   for(const {q,j} of landing){if(!wallAt.has(q)){if(q.wall)wallAt.set(q,f);else assert(q.journey===j||!q.journey,'slides '+a+'->'+b+'->'+c+': '+q.name+', still on its way, was planned again');}else assert(q.wall,'slides '+a+'->'+b+'->'+c+': '+q.name+' landed and moved again');}
   for(const q of still)assert(q.wall,'slides '+a+'->'+b+'->'+c+': '+q.name+', still, moved');}
  for(const {q} of landing)assert(wallAt.has(q),'slides '+a+'->'+b+'->'+c+': '+q.name+' had not landed 4 s on');
  out.push({slides:[a,b,c],landing:landing.map(({q})=>({name:q.name,wallAfter:wallAt.get(q)})),still:still.map(q=>q.name)});}
 report.hurried=out;
}
{ // a phone: the box a band across the top, the stage a row below it, the cluster at the foot
 const st=fresh(phone),e=st.e;e.cueStart();st.step(420);
 const out=[settled(st,0,'phone slide 0')],R=e.root.ROWS;
 for(let k=1;k<=5;k++){out.push(change(st,k,'phone slide '+(k-1)+'->'+k));out.push(settled(st,k,'phone slide '+k));for(const b of e.cue().on)assert(b.rect[1]>=0.36*R-1e-6&&b.rect[3]<=0.56*R+1e-6,'phone: the stage is not the row below the band');}
 report.phone2=out;
}
const clipRect=(P,r)=>{let o=P;const cl=(a,b,c)=>{const n=[];for(let i=0;i<o.length;i++){const p=o[i],q=o[(i+1)%o.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;if(dp<=0)n.push(p);if(dp*dq<0){const t=dp/(dp-dq);n.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}}o=n;};cl(-1,0,-r[0]);cl(1,0,r[2]);cl(0,-1,-r[1]);cl(0,1,r[3]);return o.length>=3?ring(o):0;};
const cenOf=l=>{let A=0,x=0,y=0;for(const pts of l.loops)for(let i=0;i<pts.length;i++){const p=pts[i],q=pts[(i+1)%pts.length],f=p[0]*q[1]-q[0]*p[1];A+=f;x+=(p[0]+q[0])*f;y+=(p[1]+q[1])*f;}return Math.abs(A)>1e-6?[x/(3*A),y/(3*A)]:null;};

// --- A CHANGE REHEARSED ---------------------------------------------------------------
const FMS=15.625;   // ms: a frame of 1/64 s, which a float holds exactly
const TOUR=['scene:frame','scene:sidebar','scene:hero','scene:flock','scene:bento','scene:hero','scene:bento','open:Moss','home','open:Aurora','home','open:Coal','open:Aurora','home','open:Petal','home','open:Drift','home','open:Ember','open:Tide','home','open:Dune','home','open:Jazz','home'];
// the page as a rehearsal steps it: every cell's seed, speed, claim, crystal and progress, and its sites; the same text runs in the page
const SNAP='R => R.bodies.flatMap(b => [b.id, b.x, b.y, b.vx, b.vy, b.claim, b.crystal || 0, b.progress || 0, b.leaving ? 1 : 0, ...b.subs.flatMap(s => [s.x, s.y, s.w])])',snap=eval(SNAP);
const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]||(v!==v&&b[i]!==b[i]));
const fit=(js,a,b)=>{assert.equal(js.split(a).length,2,'the probe does not fit the page: '+a.slice(0,50));return js.replace(a,b);};
// the chosen rehearsal's page, frame by frame, kept for the check
const traced=js=>{
 js=fit(js,'  const sc = rehearsalScorer(dt);\n','  const sc = rehearsalScorer(dt), trace = [], snap = '+SNAP+';\n');
 js=fit(js,'score = sc.frame(); }','score = sc.frame(); trace.push(snap(root)); }');
 js=fit(js,'  return sc.result();\n}\n// THE PLAN.','  const rr = sc.result(); rr.trace = trace; return rr;\n}\n// THE PLAN.');
 return fit(js,'plan: [...plan], rehearsals: n });','plan: [...plan], rehearsals: n, trace: best.trace });');};
// the whole world and every drawing command of a frame
const digest=e=>{const h=crypto.createHash('sha1'),w=[];e.root.walk(g=>{for(const b of g.bodies)w.push(b.id,b.x,b.y,b.vx,b.vy,b.claim);});h.update(JSON.stringify(w));h.update(JSON.stringify(e.commands));return h.digest('hex');};
function tour(file,size,{rehearsal=false,transform,digests=null,budget}={}){
 const e=loadEngine(file,{...size,count:12,record:true,transform}),st={e,pic:null};let ms=1000;
 if(budget!==undefined)assert.equal(e.budget(budget),budget,'no budget to set');
 const step=()=>{e.clear();st.pic=e.advance(ms);ms+=FMS;if(digests)digests.push(digest(e));};
 e.pointer(-1e9,-1e9);for(let i=0;i<300;i++)step();
 const R=e.root,body=n=>R.bodies.find(b=>b.name===n),cells=()=>R.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving),T=e.templates(),K=e.kinds();
 const click=n=>{const b=body(n),l=st.pic.leaves.find(l=>l.path[0]&&l.path[0].body===b),c=(l&&cenOf(l))||[b.x,b.y];return e.click(c[0],c[1]);};
 const px=r=>[r[0]*R.PW,r[1]*R.PH,r[2]*R.PW,r[3]*R.PH];
 const out=[];
 for(const act of TOUR){
  const label=(size.width<size.height?'phone ':'')+act,onPage=!!e.focus(),fromFlock=e.config.scene==='flock',was=e.rehearsal();
  if(act==='home')e.home();else if(act.startsWith('open:'))assert(click(act.slice(5)),label+': the click missed');else e.scene(act.slice(6));
  const ask=!(onPage&&act.startsWith('open:'))&&!fromFlock&&act!=='scene:flock';   // a change of scene, and home to a page and back; page to page is Shoal's, and so is the flock, whose cells travel nowhere and are always on the wing
  const prev=new Map(),prevC=new Map(),closest=new Map();let frac=0,worst=null,fl=0,sl=0,frames=0;
  const measure=()=>{frames++;
   const cs=cells();for(const b of cs)prev.set(b,[b.x,b.y]);
   const reach=b=>0.5*Math.sqrt(Math.max(b.claim,0.02)*R.PW*R.PH),tr=cs.filter(b=>b.journey&&b.progress>0&&b.progress<1);
   for(let i=0;i<tr.length;i++)for(let j=i+1;j<tr.length;j++){const a=tr[i],c=tr[j],k=a.id+'-'+c.id;closest.set(k,Math.min(closest.get(k)??Infinity,Math.hypot(a.x-c.x,a.y-c.y)/(reach(a)+reach(c))));}
   for(const l of st.pic.leaves){if(l.path.length!==1||l.isVoid)continue;const b=l.body;if(b.isSelf)continue;const a=l.loops.reduce((q,lp)=>q+ring(lp),0);
    if(!b.hole&&l.loops.length===1&&a>2000){const lp=l.loops[0];let P=0,x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(let i=0;i<lp.length;i++){const q=lp[(i+1)%lp.length];P+=Math.hypot(q[0]-lp[i][0],q[1]-lp[i][1]);x0=Math.min(x0,lp[i][0]);y0=Math.min(y0,lp[i][1]);x1=Math.max(x1,lp[i][0]);y1=Math.max(y1,lp[i][1]);}if(4*Math.PI*a/(P*P)<0.3&&a<0.97*(x1-x0)*(y1-y0))sl++;}
    const c=cenOf(l);if(c){const p=prevC.get(b);if(p)fl+=Math.max(0,Math.hypot(c[0]-p.c[0],c[1]-p.c[1])-Math.hypot(b.x-p.s[0],b.y-p.s[1])-30);prevC.set(b,{c,s:[b.x,b.y]});}}
   const sh=shapes(st);frac+=sh.fractured;worst=worst||sh.worst;};
  const t0=R.t;step();measure();
  let rh=null;
  if(rehearsal){
   const log=e.rehearsal(),asked=log!==was&&!!log;
   assert.equal(asked,ask,label+(ask?': the change was not rehearsed':': a change from page to page was rehearsed'));
   if(asked&&log.base!==undefined){
    // WHAT IT REHEARSES IS WHAT IT PLAYS: the page, frame by frame, to the bit, and the score
    // (the fields inside the cells are not rehearsed: the rehearsal runs to the end of the page's own change, and the fields' may run on)
    const sc=e.scorer(log.dt),live=[snap(R)];sc.frame();
    while(live.length<log.trace.length){step();measure();live.push(snap(R));sc.frame();}
    const pageEnds=R.bodies.reduce((m,b)=>{const j=b.journey;return j?Math.max(m,j.t0+(j.delay||0)+(j.hold||0)+(j.dur||0)+0.15):m;},0);
    assert(e.time()>=pageEnds,label+': the rehearsal ended '+(pageEnds-e.time()).toFixed(2)+' s before the page\'s change');
    const at=live.findIndex((f,i)=>!same(f,log.trace[i]));assert.equal(at,-1,label+': the performance left its rehearsal at frame '+at);
    const got=sc.result();assert.equal(got.score,log.chosen,label+': the performance scored '+got.score+', its rehearsal '+log.chosen);
    // NEVER WORSE: the plan chosen rehearses no worse than Shoal's own from the same start
    assert(log.chosen<=log.base,label+': the plan chosen rehearsed '+log.chosen+', Shoal\'s '+log.base);
    rh={base:+log.base.toFixed(1),chosen:+log.chosen.toFixed(1),baseParts:log.baseParts,parts:log.parts,plan:log.plan.map(([id,d])=>[R.bodies.find(b=>b.id===id).name,+d.toFixed(2)]),rehearsals:log.rehearsals,rehearsedFrames:log.frames,thinkMs:+log.ms.toFixed(0),frames:live.length};
   }else if(asked)rh={base:null,why:'fewer than two travellers'};
   if(!ask){const trav=cells().filter(b=>b.journey&&b.journey.t0===t0&&b.path);assert(trav.every(b=>b.journey.delay===0)&&new Set(trav.map(b=>b.journey.dur)).size<=1,label+': a change not rehearsed is not on Shoal\'s one clock');}
  }
  while(frames<450){step();measure();}
  if(rehearsal)assert.equal(frac,0,label+': a fractured cell '+JSON.stringify(worst));
  // A PAGE AT REST, as on Shoal: the image on its rectangle, the text over its own, the whitespace exact, no field, one site a cell
  let rest=null;
  if(act.startsWith('open:')){const hero=body(act.slice(5)),kind=K[hero.id%K.length],n=cells().length,slot=e.scenes[e.config.scene](R.COLS,R.ROWS,n).content[0];
   rest={page:e.focus()===hero&&e.config.scene===kind,onRect:rectsEqual(hero.rect,slot)};
   const hl=st.pic.leaves.find(l=>l.path.length===1&&l.body===hero),hr=px(hero.rect);
   rest.imageCovers=hl?+(hl.loops.reduce((a,lp)=>a+clipRect(lp,hr),0)/((hr[2]-hr[0])*(hr[3]-hr[1]))).toFixed(4):0;
   if(T[kind].text){const v=R.bodies.find(v=>v.isVoid&&!v.leaving&&v.rect&&v.rect.portalText),r=px(v.rect);
    rest.textCovers=+(st.pic.leaves.filter(l=>l.body===v).reduce((a,l)=>a+l.loops.reduce((q,lp)=>q+clipRect(lp,r),0),0)/((r[2]-r[0])*(r[3]-r[1]))).toFixed(4);
    rest.title=e.commands.some(c=>c[0]==='fillText'&&c[1]===hero.name&&c[2]>=r[0]&&c[2]<=r[2]&&c[3]>=r[1]&&c[3]<=r[3]);}
   const vx=voidsExact(st);rest.exact=vx.ok;rest.why=vx.why;rest.field=st.pic.leaves.some(l=>l.path.length>1);rest.oneSite=cells().every(b=>b.subs.length===1);}
  const coll=[...closest.values()].filter(d=>d<0.35).length;
  out.push({act,label,rehearsed:rh,collisions:coll,fling:Math.round(fl),slivers:sl,fractured:frac,rest});
 }
 return out;
}
const sum=(r,k)=>r.reduce((a,o)=>a+o[k],0);
report.trace={};
for(const [key,size] of [['desk',{width:1440,height:900,fields:.55}],['phone',{width:390,height:720,fields:.55}]]){
 // A REHEARSAL LEAVES NO TRACE: rehearsed with a budget of one, the plan is Shoal's own, and the tour is Shoal's to the last drawing command
 const d0=[],d1=[];const was=tour(files[0],size,{digests:d0});tour(files[1],size,{budget:1,digests:d1});
 assert.equal(d1.length,d0.length,key+': the tours ran '+d0.length+' and '+d1.length+' frames');
 const at=d1.findIndex((d,i)=>d!==d0[i]);assert.equal(at,-1,key+': with a budget of one the tour left Shoal\'s at frame '+at);
 report.trace[key]={frames:d0.length,identical:true};
 const now=tour(files[1],size,{rehearsal:true,transform:traced});
 now.forEach((o,i)=>{if(!o.rest)return;const r=o.rest,t=was[i].rest;
  assert(r.page,o.label+': the page did not open');assert(r.onRect,o.label+': the image is not on its rectangle');
  assert(r.imageCovers>=Math.min(0.99,t.imageCovers-0.002),o.label+': the image covers '+(100*r.imageCovers).toFixed(1)+'% of its rectangle, on Shoal '+(100*t.imageCovers).toFixed(1)+'%');
  if(r.textCovers!==undefined){assert(r.textCovers>=Math.min(0.99,t.textCovers-0.002),o.label+': the text covers '+(100*r.textCovers).toFixed(1)+'% of its rectangle, on Shoal '+(100*t.textCovers).toFixed(1)+'%');assert(r.title,o.label+': no title in the text');}
  assert(r.exact,o.label+': '+r.why);assert(!r.field,o.label+': a field on a page');assert(r.oneSite,o.label+': a cell with more than one site');});
 const rehearsed=now.filter(o=>o.rehearsed&&o.rehearsed.base!==null).map(o=>o.rehearsed);
 const parts=k=>['lurch','sliver','split','collisions','shock'].reduce((a,p)=>({...a,[p]:+rehearsed.reduce((q,r)=>q+r[k][p],0).toFixed(1)}),{});
 const tot=r=>({collisions:sum(r,'collisions'),fling:sum(r,'fling'),slivers:sum(r,'slivers'),fractured:sum(r,'fractured')});
 report[key]={size,rehearsed:rehearsed.length,shoalPlan:+rehearsed.reduce((q,r)=>q+r.base,0).toFixed(1),chosen:+rehearsed.reduce((q,r)=>q+r.chosen,0).toFixed(1),shoalPlanParts:parts('baseParts'),chosenParts:parts('parts'),
  thinkMs:{mean:Math.round(rehearsed.reduce((q,r)=>q+r.thinkMs,0)/rehearsed.length),max:Math.max(...rehearsed.map(r=>r.thinkMs))},rehearsedFrames:{mean:Math.round(rehearsed.reduce((q,r)=>q+r.rehearsedFrames,0)/rehearsed.length),max:Math.max(...rehearsed.map(r=>r.rehearsedFrames))},
  tour:{shoal:tot(was),rehearsal:tot(now)},changes:now.map((o,i)=>({act:o.act,rehearsed:o.rehearsed,collisions:[was[i].collisions,o.collisions],fling:[was[i].fling,o.fling],slivers:[was[i].slivers,o.slivers],rest:o.rest}))};
 console.log(key,JSON.stringify({rehearsed:report[key].rehearsed,shoalPlan:report[key].shoalPlan,chosen:report[key].chosen,thinkMs:report[key].thinkMs,tour:report[key].tour}));
}

{ // THINKING SPREAD OVER FRAMES: forty rehearsed frames a frame of the page. The page holds still (no seed moves, the clock
  // stands) until the plan is made, and then plays what thinking at once plays, frame by frame; a change asked for while
  // the hive thinks starts the thinking afresh, nothing of the last one having moved
 const size={width:1440,height:900,fields:.55},mk=()=>{const e=loadEngine(files[1],{...size,count:12});let ms=1000;const o={e,pic:null,step(){o.pic=e.advance(ms);ms+=FMS;}};e.pointer(-1e9,-1e9);for(let i=0;i<300;i++)o.step();return o;};
 const a=mk(),b=mk(),out=[];b.e.think({ms:Infinity,frames:40});
 for(const act of ['scene:hero','scene:sidebar']){
  a.e.scene(act.slice(6));b.e.scene(act.slice(6));
  const still=snap(b.e.root),t=b.e.time();let held=0;
  b.step();while(b.e.thinking()){assert(same(snap(b.e.root),still),act+': the page moved while the hive thought');assert.equal(b.e.time(),t,act+': the clock ran while the hive thought');held++;b.step();}
  a.step();
  const la=a.e.rehearsal(),lb=b.e.rehearsal();
  assert(held>0,act+': the thinking was not spread');assert.equal(lb.held,held,act+': the log counts '+lb.held+' frames held, the page '+held);
  assert.deepEqual(lb.plan,la.plan,act+': thinking spread chose another plan');assert.equal(lb.chosen,la.chosen,act+': thinking spread rehearsed another score');
  for(let f=0;f<300;f++){assert(same(snap(b.e.root),snap(a.e.root)),act+': thinking spread played another change at frame '+f);a.step();b.step();}
  out.push({act,held,rehearsedFrames:lb.frames,rehearsals:lb.rehearsals,plan:lb.plan});
 }
 // asked for again while thinking: the hive holds still through both, and thinks the second afresh
 // (asking again lays the change out afresh, its whitespace and its journeys; what must not change is where anything is)
 const where=()=>new Map(b.e.root.bodies.map(q=>[q.id,[q.x,q.y,q.vx,q.vy]])),moved=(m0,m1)=>[...m1].some(([id,v])=>m0.has(id)&&!same(v,m0.get(id)));
 b.e.scene('hero');const still=where(),t=b.e.time();b.step();b.step();assert(b.e.thinking(),'the hive is not thinking');const first=b.e.rehearsal();
 b.e.scene('frame');b.step();const second=b.e.rehearsal();assert(second!==first&&second.frames>0,'the second change was not thought afresh');
 let frac=0;while(b.e.thinking()){assert(!moved(still,where()),'the page moved while the hive thought again');assert.equal(b.e.time(),t,'the clock ran while the hive thought again');b.step();}
 for(let f=0;f<300;f++){b.step();frac+=shapes(b).fractured;}
 assert.equal(frac,0,'a fractured cell after the thinking afresh');
 assert.equal(b.e.config.scene,'frame','the second change did not play');
 out.push({act:'hero, then frame while thinking',held:second.held,plan:second.plan});
 report.thinking=out;
}

{ // A STORY IS NOT REHEARSED: every frame of a Cue story, the world and every drawing command, is Shoal's
 const run=file=>{const e=loadEngine(file,{...desk,count:12,record:true}),d=[];let ms=1000;const step=n=>{for(let i=0;i<n;i++){e.clear();e.advance(ms);ms+=1000/60;d.push(digest(e));}};
  step(300);e.cueStart();step(420);for(let k=1;k<4;k++){e.cueGo(k);step(300);}e.cuePush(-100);step(420);return d;};
 const d0=run(files[0]),d1=run(files[1]);const at=d1.findIndex((x,i)=>x!==d0[i]);
 assert.equal(at,-1,'the Cue story left Shoal\'s at frame '+at);report.story={frames:d0.length,identical:true};
}

{ // a Tell and a Tell II story, told to the end and home: nothing fractures, the cells all come home
 const st=fresh(desk),e=st.e;let frac=0;const run=n=>{for(let f=0;f<n;f++){st.step(1);frac+=shapes(st).fractured;}};
 e.tellStart();run(420);for(let k=0;k<3;k++){e.tellPush(100);run(240);}e.home();run(300);
 e.tell2Start();run(420);for(let k=0;k<3;k++){e.tell2Push(100);run(300);}e.home();run(300);
 assert.equal(frac,0,'a fractured cell in a Tell story');assert.equal(roots(e).length,N,'the stories lost cells');
 report.tell={frames:2*420+3*240+3*300+2*300,fractured:frac};
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed; frames of 1/64 s on the tours. On a tour of changes (home scenes, home to a page of every kind and back, page to page) on a desk and a phone: a rehearsal leaves no trace (with a budget of one the tour is Shoal\'s, the world and every drawing command, frame by frame); on every rehearsed change the performance is the chosen rehearsal to the bit (every cell\'s seed, speed, claim, crystal, progress and sites, frame by frame) and scores what it rehearsed; the plan chosen rehearses no worse than Shoal\'s own from the same start; page to page is not rehearsed and runs on Shoal\'s one clock; nothing fractures on any frame; every page at rest is exact as on Shoal. Thinking spread over frames holds the page still and then plays what thinking at once plays, and a change asked for while thinking is thought afresh. A Cue story is Shoal\'s frame by frame; Cue\'s own story checks pass on a desk and a phone; a Tell and a Tell II story run to their end and home without a fractured cell.',report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({trace:report.trace,desk:{shoalPlan:report.desk.shoalPlan,chosen:report.desk.chosen},phone:{shoalPlan:report.phone.shoalPlan,chosen:report.phone.chosen},thinking:report.thinking.map(o=>o.held),story:report.story,cue:{slides:report.slides.length,changes:report.changes.length},tell:report.tell}));
