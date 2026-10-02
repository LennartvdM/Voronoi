// Hinge: Frame II's cells turn the corners as solid fronts. Conveyor's belt held each cell's seed on the band's centre
// line and let the auction cut the band between the seeds, so round a corner a cell slid round a part at a time; here
// every cell on the belt is the band between two fronts, a front square across a straight and, in a corner block, a
// ray from the middle's corner that swings round it by area. The cells come onto the belt from where they rest, and go
// back to the auction on the change's own clock. Built from Conveyor.
// Checked on a desk (1440×900), at frames of 1/64 s, with the worker of Wings (headless, a second copy of the page's
// script) thinking sixteen rehearsed frames a frame:
// - everything but Frame II is Conveyor's: with the rule in, and no budget, the tour of changes and the chain through
//   every page from every other are Conveyor's, the world and every drawing command, frame by frame;
// - from Bento, Frame II is Frame frame by frame until the change has landed; then, for a minute from when the belt is
//   up to speed, every cell is drawn, nothing fractures, nothing is drawn in the middle, every seed goes clockwise
//   round the middle and never back, no faster than 40 px/s, every cell is drawn exactly its stretch and they tile
//   the band, and every front in a corner passes through the middle's corner (on Conveyor, reported);
// - at every count from 4 to 30 cells tried, the belt starts with nothing moving further than on Conveyor;
// - leaving the belt early, mid-way and late for Bento, Frame, Sidebar and a page: no cell moves further in a frame
//   than on Conveyor (to half a pixel), and nothing fractures;
// - into Frame II and out of it to a page, home and two scenes, with the worker thinking: nothing waits or fractures,
//   what is rehearsed is what is played, every change has one pace, every page at rest is exact;
// - a Cue story is Conveyor's frame by frame.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {loadEngine}=require('./probe.cjs');
const rectsEqual=(a,b)=>a&&b&&a.length>=4&&b.length>=4&&a.slice(0,4).every((v,i)=>Math.abs(v-b[i])<1e-6);
const files=[path.resolve(__dirname,'../../conveyor.html'),path.resolve(__dirname,'../../hinge.html')];
const report={trace:null,home:null,desk:null,pages:null,onPage:null,story:null,tell:null};
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
 if(out.length>=3)return out;a.round=true;return a;};   // fewer than three corners: a cell rounded all over has no corner to break
// AMOEBA: a cell's sides on the sea, as the auction handed them back: the hive's one smooth edge
const SEA=-3000;
const seaSides=R=>{const m=new Map();if(!R.solved||!R.solved.sea)return m;const cells=R.solved.diagram.cells;
 R.solvedSubs.forEach((s,i)=>{const c=cells[i];if(!c||s.body.isVoid)return;const L=m.get(s.body)||[];for(const p of (c.pieces||[c]))for(let k=0;k<p.pts.length;k++)if(p.labs[k]===SEA)L.push([p.pts[k],p.pts[(k+1)%p.pts.length]]);m.set(s.body,L);});return m;};
function shapes(st){
 const e=st.e,W=e.root.W,H=e.root.H,rigid=[],pic=st.pic,sides=seaSides(e.root);
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
 for(const l of leaves)for(const lp0 of l.loops){const c=cls.get(lp0);if(!c)continue;const lp=c.lp,sea=sides.get(l.body)||[],onSea=p=>sea.some(([a,b])=>segDist(p,a,b)<1);
  if(c.cls==='rectangle'){out.rectangle++;continue;}if(c.cls==='notched'){out.notched++;continue;}
  const m=lp.length,sgn=Math.sign(lp.reduce((q,p,i,a)=>{const n=a[(i+1)%a.length];return q+p[0]*n[1]-n[0]*p[1];},0))||1;let reflex=0,unexplained=0,shortEdges=0;
  for(let k=0;k<m;k++){const p=lp[(k+m-1)%m],cpt=lp[k],q=lp[(k+1)%m];const ux=cpt[0]-p[0],uy=cpt[1]-p[1],vx=q[0]-cpt[0],vy=q[1]-cpt[1];const cr=(ux*vy-uy*vx)/(Math.hypot(ux,uy)*Math.hypot(vx,vy)||1);if(Math.hypot(vx,vy)<2&&!onSea(cpt))shortEdges++;if(cr*sgn<-1e-3){reflex++;if(!near(cpt)&&!onSea(cpt))unexplained++;}}
  // AMOEBA: a cell's side on the sea is the hive's one smooth edge; its points are no corners
  const corners=lp.filter(p=>!onSea(p)).length;
  const blend=l.body&&(l.body.conveyBack||l.body.conveyIn);   // HINGE: a cell on its way onto the belt or back is a blend of two convex shapes: its corners are the blend's, and only a dent is a fracture
  if(unexplained||(corners>24&&!lp.round&&!blend)){out.fractured++;out.worst=out.worst||{name:l.body.name,verts:m,corners,reflex,unexplained};}
  else if(shortEdges)out.shortEdged++;else if(!reflex&&m<=16)out.voronoi++;else out.cut++;}
 return out;
}
const desk={width:1900,height:810,fields:.55};
const N=12;
const roots=e=>e.root.bodies.filter(q=>!q.isVoid&&!q.isSelf&&!q.leaving);
const overlap=(a,b)=>Math.min(a[2],b[2])-Math.max(a[0],b[0])>1e-6&&Math.min(a[3],b[3])-Math.max(a[1],b[1])>1e-6;
// A SLIDE, SETTLED: the cast is the sequence's places so far, each cell on
// its place, a rectangle to 4 px, unlabelled; every cell one site, none a
// field, none fractured, the count kept; the whitespace exact and, with the
// cells, covering the page; the blurb titled with the cast's names, in the box
const clipRect=(P,r)=>{let o=P;const cl=(a,b,c)=>{const n=[];for(let i=0;i<o.length;i++){const p=o[i],q=o[(i+1)%o.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;if(dp<=0)n.push(p);if(dp*dq<0){const t=dp/(dp-dq);n.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}}o=n;};cl(-1,0,-r[0]);cl(1,0,r[2]);cl(0,-1,-r[1]);cl(0,1,r[3]);return o.length>=3?ring(o):0;};
const cenOf=l=>{let A=0,x=0,y=0;for(const pts of l.loops)for(let i=0;i<pts.length;i++){const p=pts[i],q=pts[(i+1)%pts.length],f=p[0]*q[1]-q[0]*p[1];A+=f;x+=(p[0]+q[0])*f;y+=(p[1]+q[1])*f;}return Math.abs(A)>1e-6?[x/(3*A),y/(3*A)]:null;};

// --- A CHANGE THOUGHT THROUGH AS IT PLAYS -------------------------------------------------
const FMS=15.625;   // ms: a frame of 1/64 s, which a float holds exactly
const BUDGET=16;    // rehearsed frames a page frame: a worker's, measured in Chromium at 12 to 42
const TOUR=['scene:frame','scene:sidebar','scene:hero','scene:flock','scene:bento','scene:hero','scene:bento','open:Moss','home','open:Aurora','home','open:Coal','open:Aurora','home','open:Petal','home','open:Drift','home','open:Ember','open:Tide','home','open:Dune','home','open:Jazz','home'];
// the page as a rehearsal steps it: every cell's seed, speed, claim, crystal and progress, and its sites; the same text runs in the page
const SNAP='R => R.bodies.flatMap(b => [b.id, b.x, b.y, b.vx, b.vy, b.claim, b.crystal || 0, b.progress || 0, b.leaving ? 1 : 0, ...b.subs.flatMap(s => [s.x, s.y, s.w])])',snap=eval(SNAP);
const same=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]||(v!==v&&b[i]!==b[i]));
const fit=(js,a,b)=>{assert.equal(js.split(a).length,2,'the probe does not fit the page: '+a.slice(0,50));return js.replace(a,b);};
// each round's rehearsal of the move it made, frame by frame, kept for the check
const traced=js=>{
 js=fit(js,'  const sc = rehearsalScorer(dt), cost = improvCost(dt);\n','  const sc = rehearsalScorer(dt), cost = improvCost(dt), trace = [], snapOf = '+SNAP+';\n');
 js=fit(js,'score = sc.frame(); }','score = sc.frame(); trace.push([simTime, snapOf(root), guestLeft]); }');
 js=fit(js,'  return sc.result();\n}\n// THE ROUNDS.','  const rr = sc.result(); rr.trace = trace; return rr;\n}\n// THE ROUNDS.');
 js=fit(js,'  return { base: base.score, chosen: won ? won.r.score : base.score, move: won ? won.m : null, tried: moves.length };','  return { base: base.score, chosen: won ? won.r.score : base.score, move: won ? won.m : null, tried: moves.length, trace: won ? won.r.trace : null };');
 return fit(js,'move: res.move && !late ? res.move.id : null, late: !!res.move && late, offstage: !!offstage });','move: res.move && !late ? res.move.id : null, late: !!res.move && late, offstage: !!offstage, trace: res.move && !late ? res.trace : null });');};
// THE WORKER, HEADLESS: the page's script loaded a second time as a worker loads it, and the page's copy told it has a
// worker to start. Messages cross as structured clones; an answer arrives at the frame a worker thinking the counted
// budget would have it in hand. Each tour gets its own.
function offstage(budget,file=files[1]){
 const q=[];let now=0,B=null,A=null;
 globalThis.Worker=class{constructor(){A=this;globalThis.self={postMessage:m=>{const c=structuredClone(m);q.push([now+(c.type==='answer'?Math.ceil(c.frames/budget)+1:1),c]);}};globalThis.IMPROV_WORKER=true;B=loadEngine(file,{width:1,height:1,count:12,transform:traced});delete globalThis.IMPROV_WORKER;}
  postMessage(m){const c=structuredClone(m);globalThis.self.onmessage({data:c});}};
 return{page:js=>fit(traced(js),"const WINGS_SOURCE = typeof document !== 'undefined' && document.currentScript ? document.currentScript.textContent : null;","const WINGS_SOURCE = 'headless';"),
  tick(){now++;for(let i=0;i<q.length;)if(q[i][0]<=now){const [,c]=q.splice(i,1)[0];if(A&&A.onmessage)A.onmessage({data:c});}else i++;},done(){delete globalThis.Worker;delete globalThis.self;}};
}
// the whole world and every drawing command of a frame
const digest=e=>{const h=crypto.createHash('sha1'),w=[];e.root.walk(g=>{for(const b of g.bodies)w.push(b.id,b.x,b.y,b.vx,b.vy,b.claim);});h.update(JSON.stringify(w));h.update(JSON.stringify(e.commands));return h.digest('hex');};
// THE DEFECTS AS DRAWN: a rehearsal's own count, taken on the picture's cells
const areaL=L=>Math.abs(L.reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
function drawnScorer(e,st){const R=e.root,u=FMS*60/1000,prev=new Map(),pairs=new Map();let lurch=0,sliver=0,split=0,shock=0,frames=0;
 return{frame(){frames++;const reach=b=>0.5*Math.sqrt(Math.max(b.claim,0.02)*R.PW*R.PH);
  for(const l of st.pic.leaves){if(l.path.length!==1||l.isVoid)continue;const b=l.body;if(b.isSelf||b.leaving)continue;const outer=l.loops.filter(L=>!L.hole);if(!outer.length)continue;
   let A=0,x=0,y=0;for(const L of l.loops)for(let i=0;i<L.length;i++){const p=L[i],q=L[(i+1)%L.length],f=p[0]*q[1]-q[0]*p[1];A+=f;x+=(p[0]+q[0])*f;y+=(p[1]+q[1])*f;}if(Math.abs(A)<1e-6)continue;
   const c=[x/(3*A),y/(3*A)],p=prev.get(b.id);
   if(p&&p.c1&&Math.hypot(c[0]-p.c[0],c[1]-p.c[1])<300*u&&Math.hypot(p.c[0]-p.c1[0],p.c[1]-p.c1[1])<300*u)lurch+=Math.max(0,Math.hypot(c[0]-2*p.c[0]+p.c1[0],c[1]-2*p.c[1]+p.c1[1])/(u*u)-10)*u;
   if(p&&frames*u<=15&&Math.hypot(c[0]-p.c[0],c[1]-p.c[1])<300*u)shock+=Math.max(0,Math.hypot(c[0]-p.c[0],c[1]-p.c[1])-Math.hypot(b.x-p.s[0],b.y-p.s[1]));
   const big=outer.map(areaL).sort((a,b)=>b-a);
   if(big[1]>50)split+=u;else if(outer.length===1&&big[0]>2000){const L=outer[0];let P=0,x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(let i=0;i<L.length;i++){const q=L[(i+1)%L.length];P+=Math.hypot(q[0]-L[i][0],q[1]-L[i][1]);x0=Math.min(x0,L[i][0]);y0=Math.min(y0,L[i][1]);x1=Math.max(x1,L[i][0]);y1=Math.max(y1,L[i][1]);}if(4*Math.PI*big[0]/(P*P)<0.3&&big[0]<0.97*(x1-x0)*(y1-y0))sliver+=u;}
   prev.set(b.id,{c,c1:p?p.c:null,s:[b.x,b.y]});}
  const trav=R.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving&&b.journey&&b.progress>0&&b.progress<1);
  for(let i=0;i<trav.length;i++)for(let j=i+1;j<trav.length;j++){const a=trav[i],c=trav[j],k=a.id+':'+c.id,d=Math.hypot(a.x-c.x,a.y-c.y)/(reach(a)+reach(c));if(!(pairs.get(k)<=d))pairs.set(k,d);}},
 result(){const coll=[...pairs.values()].filter(d=>d<0.35).length;return{score:+(lurch+50*sliver+200*split+100*coll+shock).toFixed(1),lurch:+lurch.toFixed(1),sliver:+sliver.toFixed(1),split:+split.toFixed(1),collisions:coll,shock:+shock.toFixed(1)};}};}
// HOW THE CELLS MOVE, frame by frame over a change: every traveller's seed (what the cell is drawn around) and the
// point of its plan it follows. Their accelerations; each cell's peak speed against its average over its trip; and
// close pairs moving against each other (their relative speed, weighted by closeness on the page's scale).
function mover(R,acc){const dt=FMS/1000,L=Math.sqrt(R.PW*R.PH),hist=new Map(),plan=new Map(),per=new Map();
 const carrot=b=>{const P=b.path,p=b.progress,m=1-p;return[m*m*P.sx+2*m*p*P.cx+p*p*P.ex,m*m*P.sy+2*m*p*P.cy+p*p*P.ey];};
 const push=(m,k,v)=>{const h=m.get(k)||[];h.push(v);if(h.length>3)h.shift();m.set(k,h);return h;};
 return{frame(){const cells=[];
  for(const b of R.bodies){if(b.isVoid||b.isSelf||b.leaving||!b.path||!b.journey)continue;
   const h=push(hist,b.id,[b.x,b.y]),c=push(plan,b.id,carrot(b));if(h.length<3)continue;
   const v=[(h[2][0]-h[1][0])/dt,(h[2][1]-h[1][1])/dt];
   acc.seed.push(Math.hypot(h[2][0]-2*h[1][0]+h[0][0],h[2][1]-2*h[1][1]+h[0][1])/dt/dt);
   acc.plan.push(Math.hypot(c[2][0]-2*c[1][0]+c[0][0],c[2][1]-2*c[1][1]+c[0][1])/dt/dt);
   const s=per.get(b.id)||{sum:0,n:0,peak:0,len:Math.hypot(b.path.ex-b.path.sx,b.path.ey-b.path.sy)},sv=Math.hypot(v[0],v[1]);s.sum+=sv;s.n++;s.peak=Math.max(s.peak,sv);per.set(b.id,s);
   cells.push({x:b.x,y:b.y,v});}
  let hh=0;for(let i=0;i<cells.length;i++)for(let k=i+1;k<cells.length;k++){const a=cells[i],c=cells[k];hh+=Math.exp(-Math.hypot(a.x-c.x,a.y-c.y)/L)*Math.hypot(a.v[0]-c.v[0],a.v[1]-c.v[1]);}acc.hectic.push(hh);},
 end(){for(const s of per.values())if(s.len>60&&s.n>10)acc.peak.push(s.peak/(s.sum/s.n));}};}
const quant=(a,q)=>{const s=Float64Array.from(a).sort();return s[Math.min(s.length-1,Math.floor(q*s.length))];};
const motionOf=acc=>({seedAccel:{mean:+(acc.seed.reduce((a,b)=>a+b,0)/acc.seed.length).toFixed(0),p99:+quant(acc.seed,.99).toFixed(0)},planAccel:{p99:+quant(acc.plan,.99).toFixed(0),max:+Math.max(...acc.plan).toFixed(0)},peakOverMean:{median:+quant(acc.peak,.5).toFixed(2),p90:+quant(acc.peak,.9).toFixed(2)},hectic:{mean:+(acc.hectic.reduce((a,b)=>a+b,0)/acc.hectic.length).toFixed(0),p99:+quant(acc.hectic,.99).toFixed(0)}});
// THE PACE IS WHAT IT SAYS. Right after the ask: every traveller of the change has one pace; the pace is the measure of
// the planned paths, taken again here; its progress runs from 0 to 1, never back, from rest to rest; and at every point
// of its clock the change has had exactly the minimum-jerk share of what happens in it
const mj=u=>u*u*u*(10+u*(-15+6*u));
// the plan the page measured, recorded as it measures it (a page's gallery comes and goes about the change, and cells
// retire just after): every cell's place, and the path of each traveller of the change. The measure is taken again here.
const measured=js=>fit(js,'const pc = paceOf(this, js);','if (!rehearsing) globalThis.__paced = this.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).map(b => ({ x: b.x, y: b.y, path: b.path && b.journey && js.includes(b.journey) ? Object.assign({}, b.path) : null })); const pc = paceOf(this, js);');
function paceCheck(e,label){
 const R=e.root,js=R.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving&&b.journey&&b.journey.t0===R.t).map(b=>b.journey),cells=globalThis.__paced;
 if(!cells||!cells.some(c=>c.path)){assert(js.every(j=>!j.pace),label+': a pace on a change where nothing travels');return null;}   // the flock: its cells go nowhere
 const pcs=new Set(js.map(j=>j.pace));assert.equal(pcs.size,1,label+': the travellers of a change have '+pcs.size+' paces');
 const pc=js[0].pace;assert(pc&&pc.k&&pc.q,label+': a change of the page has no pace');
 const N=pc.k.length-1,L=Math.sqrt(R.PW*R.PH),K=[];
 for(let n=0;n<=N;n++){const p=n/N,m=1-p,x=[],v=[];
  for(const b of cells){const P=b.path;if(!P){x.push([b.x,b.y]);v.push([0,0]);continue;}
   x.push([m*m*P.sx+2*m*p*P.cx+p*p*P.ex,m*m*P.sy+2*m*p*P.cy+p*p*P.ey]);v.push([2*m*(P.cx-P.sx)+2*p*(P.ex-P.cx),2*m*(P.cy-P.sy)+2*p*(P.ey-P.cy)]);}
  let s=0;for(let i=0;i<cells.length;i++){s+=Math.hypot(...v[i]);for(let j=i+1;j<cells.length;j++)s+=Math.exp(-Math.hypot(x[i][0]-x[j][0],x[i][1]-x[j][1])/L)*Math.hypot(v[i][0]-v[j][0],v[i][1]-v[j][1]);}K.push(s);}
 const tot=K.reduce((a,k,n)=>n?a+(K[n-1]+k)/(2*N):a,0);
 K.forEach((k,n)=>assert(Math.abs(k/tot-pc.k[n])<=1e-9*Math.max(1,pc.k[n]),label+': the pace is not the measure of the planned paths at node '+n));
 const Qof=p=>{const x=p*N,n=Math.min(N-1,Math.floor(x)),t=x-n;return pc.q[n]+pc.k[n]/N*t+(pc.k[n+1]-pc.k[n])/(2*N)*t*t;};
 let prev=0,peak=0,off=0;const M=2000;
 assert.equal(e.paceAt(pc,0),0,label+': the pace does not start at 0');assert.equal(e.paceAt(pc,1),1,label+': the pace does not end at 1');
 for(let i=1;i<=M;i++){const u=i/M,p=e.paceAt(pc,u);assert(p>=prev,label+': the pace runs back at u='+u);peak=Math.max(peak,(p-prev)*M);prev=p;off=Math.max(off,Math.abs(Qof(p)-mj(u)));}
 assert(off<1e-9,label+': the change has not had the minimum-jerk share of what happens in it: off by '+off);
 const d=1e-4,v0=e.paceAt(pc,d)/d,v1=(1-e.paceAt(pc,1-d))/d;assert(v0<1e-3&&v1<1e-3,label+': the pace does not start and end at rest ('+v0+', '+v1+')');
 // how fast things happen in time, against its average over the change: on the pace, minimum jerk's 1.875 at most; on
 // easeInOutCubic, as Shoal and Wings run the same plan
 const Kat=p=>{const x=p*N,n=Math.min(N-1,Math.floor(x)),t=x-n;return pc.k[n]*(1-t)+pc.k[n+1]*t;},cubic=u=>u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;
 let cub=0,own=0;for(let i=0;i<M;i++){const u0=i/M,u1=(i+1)/M;cub=Math.max(cub,Kat((cubic(u0)+cubic(u1))/2)*(cubic(u1)-cubic(u0))*M);own=Math.max(own,Kat((e.paceAt(pc,u0)+e.paceAt(pc,u1))/2)*(e.paceAt(pc,u1)-e.paceAt(pc,u0))*M);}
 const kmax=Math.max(...pc.k),kmin=Math.min(...pc.k),mid=Kat(0.5),ends=(pc.k[0]+pc.k[N])/2;
 return{travellers:js.length,peakSpeed:+peak.toFixed(2),happensMaxOverMin:+(kmax/kmin).toFixed(2),happensMiddleOverEnds:+(mid/ends).toFixed(2),happeningPeakInTime:{cubic:+cub.toFixed(2),tempo:+own.toFixed(2)}};
}
// WHAT IT REHEARSES IS WHAT IT PLAYS: from each round that moved a cell, the page the performance stepped through is that
// round's rehearsal of the move, frame by frame, until the next move acts (or the round's horizon)
function checkRounds(log,live,label){
 const moved=log.rounds.filter(r=>r.move!==null).sort((x,y)=>x.a-y.a),out={moves:moved.length,late:log.rounds.filter(r=>r.late).length,rounds:log.rounds.length,framesChecked:0};
 moved.forEach((r,i)=>{
  assert(r.a>r.tau,label+': a move acts before its round began');
  const next=moved.find(q=>q.a>r.a),stop=next?next.a:Infinity;
  if(r.dt!==FMS/1000)return;   // a coarse round is a prediction; it cannot be laid frame by frame on the page's own
  for(const [t,f,gl] of r.trace){if(t>stop)break;const g=live.get(t);if(!g||!(gl>0))continue;   // while the page and its rehearsal both have the change running
  assert(same(f,g),label+': the performance left the rehearsal of its move at '+(t-log.t0).toFixed(3)+' s');out.framesChecked++;}
 });
 return out;
}
// THE SCREEN LEANED ON: the length of the travelling cells' outlines lying along the window's edges, a frame
const edgeOf=st=>{const W=st.e.root.W,H=st.e.root.H,on=(a,c,v)=>Math.abs(a-v)<0.5&&Math.abs(c-v)<0.5;let L=0;
 for(const l of st.pic.leaves){if(l.path.length!==1||l.isVoid||l.body.isSelf||l.body.leaving||l.body.wall)continue;
  for(const lp of l.loops)for(let k=0;k<lp.length;k++){const p=lp[k],q=lp[(k+1)%lp.length];if(on(p[0],q[0],0)||on(p[0],q[0],W)||on(p[1],q[1],0)||on(p[1],q[1],H))L+=Math.hypot(q[0]-p[0],q[1]-p[1]);}}
 return L;};
// the sea's claim this frame, in lattice slots, as the auction takes it: none where the sea is closed (a story)
const seaOf=R=>R.seaOpen()?R.bodies.reduce((a,b)=>a+R.seaClaimOf(b),0):0;
// THE HIVE AS ONE BODY, a frame while the sea is in: the share of each travelling cell's outline that lies on the sea,
// the cells almost all sea (discs: more than nine tenths of the outline), and the sea shut in among the cells (a hole
// in the hive: sea that meets neither whitespace nor the screen's edge), on a grid of 8 px
const G8=8;
function bodyOf(R){const cells=R.solved.diagram.cells,W=R.W,H=R.H,NX=Math.ceil(W/G8),NY=Math.ceil(H/G8),lab=new Uint8Array(NX*NY),who=[];let S=0,N=0,disc=0;
 const pip=(P,x,y)=>{let c=false;for(let i=0,j=P.length-1;i<P.length;j=i++){const a=P[i],b=P[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;};
 const paint=(P,v)=>{let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const p of P){x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);y0=Math.min(y0,p[1]);y1=Math.max(y1,p[1]);}
  for(let gy=Math.max(0,Math.floor(y0/G8));gy<=Math.min(NY-1,Math.floor(y1/G8));gy++)for(let gx=Math.max(0,Math.floor(x0/G8));gx<=Math.min(NX-1,Math.floor(x1/G8));gx++)if(!lab[gy*NX+gx]&&pip(P,(gx+.5)*G8,(gy+.5)*G8))lab[gy*NX+gx]=v;};
 R.solvedSubs.forEach((s,i)=>{const b=s.body,c=cells[i];if(!c)return;for(const pc of (c.pieces||[c]))if(pc.pts&&pc.pts.length>=3)paint(pc.pts,b.isVoid?2:1);
  if(!b.isVoid&&!b.isSelf&&!b.leaving&&c.pts&&c.pts.length>=3){let L=0,Ls=0;for(let k=0;k<c.pts.length;k++){const p=c.pts[k],q=c.pts[(k+1)%c.pts.length],l=Math.hypot(q[0]-p[0],q[1]-p[1]);L+=l;if(c.labs[k]===SEA)Ls+=l;}if(L>0){S+=Ls/L;N++;if(Ls/L>0.9){disc++;who.push(b.name);}}}});
 for(const w of R.walls){const r=w.wall;paint([[r[0],r[1]],[r[2],r[1]],[r[2],r[3]],[r[0],r[3]]],1);}
 for(const b of R.holes)for(const P of b.hole.pieces)paint(P,1);
 const seen=new Uint8Array(NX*NY);let holes=0;
 for(let s0=0;s0<NX*NY;s0++){if(lab[s0]||seen[s0])continue;const st=[s0];seen[s0]=1;let n=0,open=false;
  while(st.length){const c=st.pop();n++;const cx=c%NX,cy=(c/NX)|0;if(!cx||!cy||cx===NX-1||cy===NY-1)open=true;
   for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const x=cx+dx,y=cy+dy;if(x<0||y<0||x>=NX||y>=NY)continue;const k=y*NX+x;if(lab[k]===2)open=true;if(!lab[k]&&!seen[k]){seen[k]=1;st.push(k);}}}
  if(!open)holes+=n*G8*G8;}
 return{share:N?S/N:0,cells:N,disc,holes,who};}
// A CHANGE STARTS GENTLY: what the drawn cells change on the first frame of it, as seen on the screen (each body's cells
// clipped to it, together): the area that changes hands, and every cell's drawn movement beyond its seed's, at 100 px²
// a pixel
const clipScreen=(P,W,H)=>{let o=P;const cl=(a,b,c)=>{const n=[];for(let i=0;i<o.length;i++){const p=o[i],q=o[(i+1)%o.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;if(dp<=0)n.push(p);if(dp*dq<0){const t=dp/(dp-dq);n.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}}o=n;};cl(-1,0,0);cl(1,0,W);cl(0,-1,0);cl(0,1,H);return o;};
function seen(st){const R=st.e.root,m=new Map();for(const l of st.pic.leaves){const b=l.path[0]&&l.path[0].body;if(!b||b.isVoid||b.isSelf||l.isVoid)continue;let A=0,x=0,y=0;
  for(const lp0 of l.loops){const lp=clipScreen(lp0,R.W,R.H);for(let i=0;i<lp.length;i++){const p=lp[i],q=lp[(i+1)%lp.length],f=p[0]*q[1]-q[0]*p[1];A+=f;x+=(p[0]+q[0])*f;y+=(p[1]+q[1])*f;}}
  if(Math.abs(A)<1e-6)continue;const o=m.get(b.id)||{A:0,X:0,Y:0,s:[b.x,b.y]};o.A+=Math.abs(A)/2;o.X+=x/3;o.Y+=y/3;m.set(b.id,o);}
 for(const o of m.values())o.c=[o.X/(2*o.A),o.Y/(2*o.A)];return m;}
function jolt(before,after){let dA=0,dd=0;for(const [id,v] of after){const p=before.get(id);if(!p){dA+=v.A;continue;}dA+=Math.abs(v.A-p.A);dd+=Math.max(0,Math.hypot(v.c[0]-p.c[0],v.c[1]-p.c[1])-Math.hypot(v.s[0]-p.s[0],v.s[1]-p.s[1]));}
 for(const [id,p] of before)if(!after.has(id))dA+=p.A;return{area:+dA.toFixed(1),beyond:+dd.toFixed(2),score:+(dA+100*dd).toFixed(1)};}
// THE GALLERY AS ONE BODY, on a change from page to page. The gallery: the cards seated on both pages but the two
// images. Its box runs from the bounding box of the old page's cards (the closing image's seat aside) to the new page's
// (the opening image's aside) on the change's clock, the gallery's cards' mean progress. A frame, in px²:
//   spill: the gallery's cards drawn outside the box            hole: the box drawn by no cell
//   swell: the opening image in the box beyond the card it was, given back as it leaves
//   bulk:  the closing image in the box beyond the card it becomes, taken in as it lands
//   bloat: the closing image drawn, anywhere, beyond what it bids (its claim, and what the pointer gave it, which it
//          gives back across the change)
// and over the change, the travel of the gallery's cards (their seats' centres) and whether the gallery crossed the
// screen (its seats' centroid, by area, moved more than half the screen's width). An essay's gallery is two corners
// whose bounding box holds its image: its changes are counted apart.
const seats=R=>{const m=new Map();for(const b of R.bodies)if(!b.isVoid&&!b.isSelf&&!b.leaving&&b.rect&&!b.reelParked)m.set(b,[b.rect[0]*R.PW,b.rect[1]*R.PH,b.rect[2]*R.PW,b.rect[3]*R.PH]);return m;};
const sArea=L=>{let a=0;for(let i=0;i<L.length;i++){const p=L[i],q=L[(i+1)%L.length];a+=p[0]*q[1]-q[0]*p[1];}return a/2;};
const clipBox=(L,r)=>{let o=L;const cl=(a,b,c)=>{const n=[];for(let i=0;i<o.length;i++){const p=o[i],q=o[(i+1)%o.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;if(dp<=0)n.push(p);if(dp*dq<0){const t=dp/(dp-dq);n.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}}o=n;};cl(-1,0,-r[0]);cl(1,0,r[2]);cl(0,-1,-r[1]);cl(0,1,r[3]);return o.length>=3?sArea(o):0;};
const leafIn=(l,r)=>Math.abs(l.loops.reduce((a,L)=>a+(r?clipBox(L,r):sArea(L)),0));
const boxOf=rs=>rs.reduce((b,r)=>[Math.min(b[0],r[0]),Math.min(b[1],r[1]),Math.max(b[2],r[2]),Math.max(b[3],r[3])],[1e9,1e9,-1e9,-1e9]);
const rA=r=>Math.max(0,r[2]-r[0])*Math.max(0,r[3]-r[1]);
const centroid=m=>{let X=0,A=0;for(const r of m.values()){const a=rA(r);X+=(r[0]+r[2])/2*a;A+=a;}return X/A;};
function galleryOf(R,s0,f0,f1,essay){
 const s1=seats(R),G=[...s1.keys()].filter(b=>b!==f0&&b!==f1&&s0.has(b)),old=new Map([...s0].filter(([b])=>b!==f0)),neu=new Map([...s1].filter(([b])=>b!==f1));
 const B0=boxOf([...old.values()]),B1=boxOf([...neu.values()]),c1=rA(s0.get(f1)||[0,0,0,0]),c0=rA(s1.get(f0)||[0,0,0,0]),g={spill:0,hole:0,swell:0,bulk:0,bloat:0,pass:Infinity};
 const role=Math.max(...R.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving&&b.claim0>0&&b.claimTarget>0).map(b=>Math.max(b.claim0/b.claimTarget,b.claimTarget/b.claim0))),U=R.PW*R.PH;
 const travel=G.reduce((a,b)=>{const p=s0.get(b),q=s1.get(b);return a+Math.hypot((p[0]+p[2]-q[0]-q[2])/2,(p[1]+p[3]-q[1]-q[3])/2);},0),crossed=Math.abs(centroid(neu)-centroid(old))>R.W/2;
 return{frame(pic){const tr=G.filter(b=>b.journey),pc=tr.length?tr.reduce((a,b)=>a+Math.max(0,Math.min(1,b.progress||0)),0)/tr.length:1,Rt=B0.map((v,j)=>v+(B1[j]-v)*pc);let all=0;
   let d0=0;for(const l of pic.leaves){if(l.path.length!==1||l.isVoid)continue;const b=l.body;if(b.isSelf||b.leaving)continue;const a=leafIn(l,Rt);all+=a;
    if(G.includes(b))g.spill+=leafIn(l)-a;else if(b===f1)g.swell+=Math.max(0,a-c1*(1-pc));else if(b===f0){g.bulk+=Math.max(0,a-c0*pc);d0+=leafIn(l);}}
   g.pass=Math.min(g.pass,Math.hypot(f0.x-f1.x,f0.y-f1.y)/((Math.sqrt(Math.max(0,f0.claim)*U)+Math.sqrt(Math.max(0,f1.claim)*U))/2));g.hole+=Math.max(0,rA(Rt)-all);g.bloat+=Math.max(0,d0-f0.subs.reduce((q,x)=>q+x.claim,0)*R.PW*R.PH);},
  result(){return{from:f0.name,to:f1.name,essay,crossed,travel:Math.round(travel),spill:Math.round(g.spill),hole:Math.round(g.hole),swell:Math.round(g.swell),bulk:Math.round(g.bulk),bloat:Math.round(g.bloat),role:+role.toFixed(2),pass:+g.pass.toFixed(3)};}};
}
function tour(file,size,{improv=false,transform,digests=null,budget,acts=TOUR,worker=null,motion=null,paced=false,sea=false,hiveBody=false,gallery=false}={}){
 const e=loadEngine(file,{...size,count:12,record:true,transform:js=>{js=worker?worker.page(js):transform?transform(js):js;return paced?measured(js):js;}}),st={e,pic:null};let ms=1000;
 if(budget!==undefined)assert.equal(e.budget(budget),budget,'no budget to set');
 const step=()=>{if(worker)worker.tick();e.clear();st.pic=e.advance(ms);ms+=FMS;if(digests)digests.push(digest(e));};
 e.pointer(-1e9,-1e9);for(let i=0;i<300;i++)step();
 const R=e.root,body=n=>R.bodies.find(b=>b.name===n),cells=()=>R.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving),T=e.templates(),K=e.kinds();
 const click=n=>{const b=body(n),l=st.pic.leaves.find(l=>l.path[0]&&l.path[0].body===b),c=(l&&cenOf(l))||[b.x,b.y];return e.click(c[0],c[1]);};
 const px=r=>[r[0]*R.PW,r[1]*R.PH,r[2]*R.PW,r[3]*R.PH];
 const out=[];
 for(const act of acts){
  const label=act,was=e.rehearsal();globalThis.__paced=null;const before=seen(st),f0=e.focus(),s0=gallery&&f0&&act.startsWith('open:')?seats(R):null;
  if(act==='home')e.home();else if(act.startsWith('open:'))assert(click(act.slice(5)),label+': the click missed');else e.scene(act.slice(6));
  const gal=s0?galleryOf(R,s0,f0,e.focus(),[f0,e.focus()].some(b=>K[b.id%K.length]==='essay')):null;
  const pace=paced?paceCheck(e,label):null,mv=motion?mover(R,motion):null;
  const sc=drawnScorer(e,st),live=new Map();let frac=0,worst=null,frames=0,t=e.time(),waits=0,edge=0,seaMax=0,start=null;const hive={frames:0,share:0,disc:0,holes:0,discs:{}};
  while(frames<450){step();frames++;if(frames===1)start=jolt(before,seen(st));if(!(e.time()>t))waits++;t=e.time();if(frames<=400&&(frames<3||e.changeLeft()>0)){sc.frame();if(mv)mv.frame();if(gal)gal.frame(st.pic);}
   if(e.changeLeft()>0){live.set(e.time(),snap(R));edge+=edgeOf(st);if(sea)seaMax=Math.max(seaMax,seaOf(R));if(hiveBody&&R.solved&&R.solved.sea){const h=bodyOf(R);hive.frames++;hive.share+=h.share;hive.disc+=h.disc;hive.holes+=h.holes;for(const n of h.who)hive.discs[n]=(hive.discs[n]||0)+1;}}
   const sh=shapes(st);frac+=sh.fractured;worst=worst||sh.worst;}
  let rested=null;if(sea){rested={sea:seaOf(R),liquid:R.bodies.filter(b=>b.seaLiquid>0).length};assert(rested.sea===0&&rested.liquid===0,label+': at rest '+JSON.stringify(rested));}
  if(mv)mv.end();
  if(improv){assert.equal(waits,0,label+': the page waited '+waits+' frames');assert.equal(frac,0,label+': a fractured cell '+JSON.stringify(worst));}
  let rounds=null;const log=e.rehearsal();if(improv&&log&&log!==was&&log.rounds)rounds=checkRounds(log,live,label);
  // A PAGE AT REST, as on Cohort: the image on its rectangle, the text over its own, the whitespace exact, no field, one site a cell
  let rest=null;
  if(act.startsWith('open:')){const hero=body(act.slice(5)),kind=K[hero.id%K.length],n=cells().length,slot=e.scenes[e.config.scene](R.COLS,R.ROWS,n).content[0];
   rest={page:e.focus()===hero&&e.config.scene===kind,onRect:rectsEqual(hero.rect,slot)};
   const hl=st.pic.leaves.find(l=>l.path.length===1&&l.body===hero),hr=px(hero.rect);
   rest.imageCovers=hl?+(hl.loops.reduce((a,lp)=>a+clipRect(lp,hr),0)/((hr[2]-hr[0])*(hr[3]-hr[1]))).toFixed(4):0;
   if(T[kind].text){const v=R.bodies.find(v=>v.isVoid&&!v.leaving&&v.rect&&v.rect.portalText),r=px(v.rect);
    rest.textCovers=+(st.pic.leaves.filter(l=>l.body===v).reduce((a,l)=>a+l.loops.reduce((q,lp)=>q+clipRect(lp,r),0),0)/((r[2]-r[0])*(r[3]-r[1]))).toFixed(4);
    rest.title=e.commands.some(c=>c[0]==='fillText'&&c[1]===hero.name&&c[2]>=r[0]&&c[2]<=r[2]&&c[3]>=r[1]&&c[3]<=r[3]);}
   const vx=voidsExact(st);rest.exact=vx.ok;rest.why=vx.why;rest.field=st.pic.leaves.some(l=>l.path.length>1);rest.ownColour=st.pic.leaves.every(l=>l.path.length!==1||l.isVoid||!l.body||l.color===l.body.color);rest.oneSite=cells().every(b=>b.subs.length===1);}
  out.push({act,label,gallery:gal?gal.result():null,drawn:sc.result(),rounds,fractured:frac,rest,pace,edge:Math.round(edge),seaMax:+seaMax.toFixed(3),rested,start,hive:hiveBody?hive:null});
 }
 return out;
}
const restChecks=(now,was)=>now.forEach((o,i)=>{if(!o.rest)return;const r=o.rest,t=was[i].rest;
 assert(r.page,o.label+': the page did not open');assert(r.onRect,o.label+': the image is not on its rectangle');
 assert(r.imageCovers>=Math.min(0.99,t.imageCovers-0.002),o.label+': the image covers '+(100*r.imageCovers).toFixed(1)+'% of its rectangle, on Cohort '+(100*t.imageCovers).toFixed(1)+'%');
 if(r.textCovers!==undefined){assert(r.textCovers>=Math.min(0.99,t.textCovers-0.002),o.label+': the text covers '+(100*r.textCovers).toFixed(1)+'% of its rectangle, on Cohort '+(100*t.textCovers).toFixed(1)+'%');assert(r.title,o.label+': no title in the text');}
 assert(r.exact,o.label+': '+r.why);assert(r.ownColour,o.label+': a cell at rest is not drawn its own colour');assert(!r.field,o.label+': a field on a page');assert(r.oneSite,o.label+': a cell with more than one site');});
const total=r=>['score','lurch','sliver','split','collisions','shock'].reduce((a,k)=>({...a,[k]:+r.reduce((q,o)=>q+o.drawn[k],0).toFixed(1)}),{});
const roundsTotal=r=>r.filter(o=>o.rounds).reduce((a,o)=>({changes:a.changes+1,rounds:a.rounds+o.rounds.rounds,moves:a.moves+o.rounds.moves,late:a.late+o.rounds.late,framesChecked:a.framesChecked+o.rounds.framesChecked}),{changes:0,rounds:0,moves:0,late:0,framesChecked:0});
const hiveTotal=r=>{const h=r.reduce((a,o)=>({frames:a.frames+o.hive.frames,share:a.share+o.hive.share,disc:a.disc+o.hive.disc,holes:a.holes+o.hive.holes}),{frames:0,share:0,disc:0,holes:0}),discs=[];r.forEach((o,i)=>{for(const [n,k] of Object.entries(o.hive.discs))discs.push({change:(i?r[i-1].act.replace('open:','')+' → ':'')+o.act.replace('open:',''),cell:n,frames:k});});return{seaFrames:h.frames,outlineOnSea:+(h.share/Math.max(1,h.frames)).toFixed(4),discsPerFrame:+(h.disc/Math.max(1,h.frames)).toFixed(4),discCellFrames:h.disc,holePxFrames:Math.round(h.holes),discs};};
const startTotal=r=>({score:+r.reduce((a,o)=>a+o.start.score,0).toFixed(1),area:+r.reduce((a,o)=>a+o.start.area,0).toFixed(1),beyond:+r.reduce((a,o)=>a+o.start.beyond,0).toFixed(2)});
report.trace={};report.pace={};report.motion={};report.edge={};report.body={};report.start={};
const unpaced=js=>fit(js,'if (pc) for (const j of js) j.pace = pc; }','if (pc && false) for (const j of js) j.pace = pc; }');   // the pace taken out
const unsea=js=>fit(js,'seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }','seaOpen() { return false; }');   // the sea taken out
const untandem=js=>fit(js,'const hj = hero.journey, hp =','const hj = null, hp =');   // the hero's own clock for the text's room taken out
const acc0=()=>({seed:[],plan:[],peak:[],hectic:[]});
const edgeSum=r=>r.reduce((a,o)=>a+o.edge,0);const size={width:1440,height:900,fields:.55};
// EVERY PAGE FROM EVERY OTHER: a chain through all 56 ordered pairs of the eight kinds
const reps=['Drift','Ember','Tide','Moss','Petal','Aurora','Dune','Jazz'],outs=reps.map((_,i)=>reps.map((_,j)=>j).filter(j=>j!==i)),stack=[0],circ=[];
while(stack.length){const v=stack[stack.length-1];if(outs[v].length)stack.push(outs[v].shift());else circ.push(stack.pop());}circ.reverse();
const CHAIN=circ.map(i=>'open:'+reps[i]);
const asFrame=acts=>acts.map(a=>a==='scene:frame2'?'scene:frame':a);   // on Cohort, Frame II is Frame

{ // EVERYTHING BUT FRAME II IS CONVEYOR'S: with the rule in, and no budget, the tour and the chain are Conveyor's to the last
  // drawing command
 report.trace={};
 for(const [name,acts] of [['tour',TOUR],['pages',CHAIN]]){
  const d0=[],d1=[];tour(files[0],size,{budget:0,digests:d0,acts});tour(files[1],size,{budget:0,digests:d1,acts});
  assert.equal(d1.length,d0.length,name+': the runs ran '+d0.length+' and '+d1.length+' frames');
  const at=d1.findIndex((d,i)=>d!==d0[i]);assert.equal(at,-1,name+': the run left Conveyor\'s at frame '+at);
  report.trace[name]={frames:d0.length,identical:true};
 }
 console.log('trace',JSON.stringify(report.trace));
}
const ringA=l=>{let a=0;for(let i=0;i<l.length;i++){const p=l[i],q=l[(i+1)%l.length];a+=p[0]*q[1]-q[0]*p[1];}return a/2;};
const cenA=ls=>{let A=0,x=0,y=0;for(const pts of ls)for(let i=0;i<pts.length;i++){const p=pts[i],q=pts[(i+1)%pts.length],f=p[0]*q[1]-q[0]*p[1];A+=f;x+=(p[0]+q[0])*f;y+=(p[1]+q[1])*f;}return [x/(3*A),y/(3*A),Math.abs(A/2)];};
// how far each cell moved since the last frame: its centroid, or its size (the side of a square of its area), whichever
// is further; a move over 300 px is a teleport, as the lurch has it, and left aside
const moves=(R,prev)=>{const now=new Map();for(const b of R.bodies)if(!b.isVoid&&!b.isSelf&&b.loops&&b.loops.length)now.set(b.id,cenA(b.loops));let mx=0;
 if(prev)for(const [id,c] of now){const p=prev.get(id);if(!p)continue;const d=Math.max(Math.hypot(c[0]-p[0],c[1]-p[1]),Math.abs(Math.sqrt(c[2])-Math.sqrt(p[2])));if(d<300)mx=Math.max(mx,d);}return{now,mx};};
// the front two cells share: the points of one outline on the other's, and the chord between the two furthest apart
const segD=(p,a,b)=>{const ex=b[0]-a[0],ey=b[1]-a[1],L2=ex*ex+ey*ey||1e-12;let t=((p[0]-a[0])*ex+(p[1]-a[1])*ey)/L2;t=Math.max(0,Math.min(1,t));return Math.hypot(a[0]+t*ex-p[0],a[1]+t*ey-p[1]);};
const onLoop=(p,l)=>{let d=Infinity;for(let i=0;i<l.length;i++)d=Math.min(d,segD(p,l[i],l[(i+1)%l.length]));return d;};
function frontOf(A,B){const P=[];for(const l of A.loops)for(const p of l)if(B.loops.some(m=>onLoop(p,m)<0.5))P.push(p);if(P.length<2)return null;
 let a=null,b=null,bd=-1;for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const d=Math.hypot(P[i][0]-P[j][0],P[i][1]-P[j][1]);if(d>bd){bd=d;a=P[i];b=P[j];}}return bd<2?null:{a,b};}
// FRAME II, frame by frame from the ask: the world and every drawing command, and the belt
function frame2(file,scene,secs,count=12){
 const e=loadEngine(file,{...size,count,record:true}),st={e,pic:null};let ms=1000;const d=[];
 const step=()=>{e.clear();const t0=process.hrtime.bigint();st.pic=e.advance(ms);ms+=FMS;d.push(digest(e));return Number(process.hrtime.bigint()-t0)/1e6;};
 e.pointer(-1e9,-1e9);for(let i=0;i<300;i++)step();e.scene('bento');for(let i=0;i<450;i++)step();d.length=0;
 e.scene(scene);const R=e.root,W=R.W,H=R.H,PW=R.PW,PH=R.PH,C=R.COLS,RR=R.ROWS,mid=[2*PW,PH,(C-2)*PW,(RR-1)*PH],cx=(mid[0]+mid[2])/2,cy=(mid[1]+mid[3])/2,band=W*H-(mid[2]-mid[0])*(mid[3]-mid[1]);
 const cells=()=>R.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving);
 let landed=-1,started=-1,mv=null,startJump=0;const o={frames:0,lost:0,fractured:0,inMiddle:0,back:0,fastest:0,share:0,tiled:0,corner:0,offHinge:0,hingeMax:0,hingeSum:0,cost:[],turned:new Map()};const prev=new Map();
 for(let k=0;k<64*secs;k++){const t=step();
  if(landed<0&&e.changeLeft()<=0)landed=k;
  const m=moves(R,mv&&mv.now);if(started<0&&e.convey&&e.convey())started=k;if(k===started)startJump=m.mx;mv=m;
  if(landed<0||k<landed+64*CONVEY_EASE_S)continue;   // the belt is up to speed
  o.frames++;o.cost.push(t);const cs=cells();let A=0,claims=0;
  for(const b of cs){if(!st.pic.leaves.some(l=>l.path[0]&&l.path[0].body===b))o.lost++;const p=prev.get(b.id);
   if(p){o.fastest=Math.max(o.fastest,Math.hypot(b.x-p[0],b.y-p[1])*64);let da=Math.atan2(b.y-cy,b.x-cx)-Math.atan2(p[1]-cy,p[0]-cx);da-=2*Math.PI*Math.round(da/(2*Math.PI));if(da<-1e-6)o.back++;o.turned.set(b.id,(o.turned.get(b.id)||0)+da);}
   prev.set(b.id,[b.x,b.y]);claims+=b.claim;A+=(b.loops||[]).reduce((q,l)=>q+Math.abs(ringA(l)),0);}
  // each cell drawn at its stretch, its share of the band when the belt started; how far the claims have moved since, reported
  const cv=e.convey&&e.convey();if(cv)for(const c of cv.cells){const b=c.b;if(b.leaving)continue;const a=(b.loops||[]).reduce((q,l)=>q+Math.abs(ringA(l)),0),str=c.a*PW*PH;o.share=Math.max(o.share,Math.abs(a-str)/str);o.drift=Math.max(o.drift||0,Math.abs(c.a/cv.belt.A-b.claim/claims)/(c.a/cv.belt.A));}
  o.tiled=Math.max(o.tiled,Math.abs(A-band)/band);
  for(let i=0;i<cs.length;i++)for(let j=i+1;j<cs.length;j++){if(!cs[i].loops||!cs[j].loops)continue;const f=frontOf(cs[i],cs[j]);if(!f)continue;
   const mx=(f.a[0]+f.b[0])/2/PW,my=(f.a[1]+f.b[1])/2/PH,Hn=mx<2&&my<1?[2,1]:mx>C-2&&my<1?[C-2,1]:mx>C-2&&my>RR-1?[C-2,RR-1]:mx<2&&my>RR-1?[2,RR-1]:null;if(!Hn)continue;
   const hx=Hn[0]*PW,hy=Hn[1]*PH,ex=f.b[0]-f.a[0],ey=f.b[1]-f.a[1],dd=Math.abs(ex*(hy-f.a[1])-ey*(hx-f.a[0]))/Math.hypot(ex,ey);o.corner++;o.hingeSum+=dd;o.hingeMax=Math.max(o.hingeMax,dd);if(dd>2)o.offHinge++;}
  for(const l of st.pic.leaves){if(l.isVoid||!l.loops)continue;for(const L of l.loops)for(const q of L)if(q[0]>mid[0]+0.5&&q[0]<mid[2]-0.5&&q[1]>mid[1]+0.5&&q[1]<mid[3]-0.5)o.inMiddle++;}
  o.fractured+=shapes(st).fractured;}
 const turns=[...o.turned.values()].map(a=>a/(2*Math.PI)),c=o.cost.sort((a,b)=>a-b);
 return{digests:d,landed,started,startJump:+startJump.toFixed(3),frames:o.frames,lost:o.lost,fractured:o.fractured,inMiddle:o.inMiddle,back:o.back,fastest:+o.fastest.toFixed(1),
  shareOff:+o.share.toExponential(2),claimDrift:+(o.drift||0).toExponential(2),bandOff:+o.tiled.toExponential(2),cornerFronts:o.corner,offHinge:o.offHinge,hingeMax:+o.hingeMax.toFixed(2),hingeMean:+(o.hingeSum/Math.max(1,o.corner)).toFixed(2),
  turnsLeast:turns.length?+Math.min(...turns).toFixed(3):0,turnsMost:turns.length?+Math.max(...turns).toFixed(3):0,costMedian:c.length?+c[c.length>>1].toFixed(2):0,costP90:c.length?+c[Math.floor(c.length*.9)].toFixed(2):0};
}
const CONVEY_EASE_S=3;
{ // FRAME II LANDS AS FRAME, AND THEN GOES ROUND: from Bento, every frame is Frame's until the change has landed; then,
  // with the belt up to speed, for a minute: every cell drawn, nothing fractured, nothing in the middle, every seed
  // going clockwise round the middle and never back, no faster than a walking pace, every cell drawn at its share of
  // the band and the band tiled, and every front in a corner through the middle's corner
 const f=frame2(files[1],'frame',20),g=frame2(files[1],'frame2',63),was=frame2(files[0],'frame2',63);
 const at=g.digests.findIndex((x,i)=>x!==f.digests[i]);
 assert(at>=f.landed,'Frame II left Frame at frame '+at+', before the change landed at '+f.landed);
 assert.equal(g.lost,0,'Frame II: a cell went undrawn '+g.lost+' times');
 assert.equal(g.fractured,0,'Frame II: a fractured cell');
 assert.equal(g.inMiddle,0,'Frame II: a cell was drawn in the middle');
 assert.equal(g.back,0,'Frame II: a seed went back');
 assert(g.turnsLeast>0,'Frame II: a cell did not go round');
 assert(g.fastest<=40,'Frame II: a seed went '+g.fastest+' px/s');
 assert(g.shareOff<1e-9,'Frame II: a cell drawn '+g.shareOff+' off its stretch');
 assert(g.bandOff<1e-6,'Frame II: the cells cover the band '+g.bandOff+' off');
 assert(g.cornerFronts>0&&g.offHinge===0&&g.hingeMax<0.5,'Frame II: a front in a corner missed its hinge by '+g.hingeMax+' px');
 assert(was.offHinge>0,'Conveyor\'s fronts all pass through the hinges: nothing to show');
 assert(g.startJump<=was.startJump+1e-9,'Frame II: the belt starts with a cell moving '+g.startJump+' px (Conveyor '+was.startJump+')');
 for(const x of [g,was])delete x.digests;report.frame2={leftFrameAt:at,landedAt:f.landed,hinge:g,conveyor:was};
 console.log('frame2',JSON.stringify(report.frame2));
}
{ // AT EVERY COUNT: from 4 to 30 cells, 12 s of Frame II: nothing undrawn, fractured or in the middle, every front in
  // a corner through its hinge, and the belt starts with nothing moving further than on Conveyor (where the cells rest
  // in what the band cuts, not at all)
 report.counts=[];
 for(const n of [4,5,6,7,8,9,10,12,13,16,20,25,30]){const g=frame2(files[1],'frame2',12,n),was=frame2(files[0],'frame2',12,n);
  assert.equal(g.lost+g.fractured+g.inMiddle,0,n+' cells: undrawn '+g.lost+', fractured '+g.fractured+', in the middle '+g.inMiddle);
  assert(g.offHinge===0,n+' cells: a front in a corner missed its hinge by '+g.hingeMax+' px');
  assert(g.shareOff<1e-9&&g.bandOff<1e-6,n+' cells: a cell off its stretch, or the band not covered');
  assert(g.startJump<=Math.max(0.05,was.startJump),n+' cells: the belt starts with a cell moving '+g.startJump+' px (Conveyor '+was.startJump+')');
  report.counts.push({cells:n,startJump:g.startJump,conveyorStartJump:was.startJump,cornerFronts:g.cornerFronts,conveyorOffHinge:was.offHinge,conveyorHingeMax:was.hingeMax});}
 console.log('counts',JSON.stringify(report.counts));
}
{ // LEAVING THE BELT: as it gets up to speed (3.5 s after the ask), and 12 s and 45 s after, for Bento, Frame, Sidebar
  // and Moss's page: no cell moves further in a frame than on Conveyor, teleports aside, and nothing fractures
 report.leave=[];
 const run=(file,wait,act)=>{const e=loadEngine(file,{...size,count:12,record:true}),st={e,pic:null};let ms=1000;
  const step=()=>{e.clear();const t0=process.hrtime.bigint();st.pic=e.advance(ms);ms+=FMS;return Number(process.hrtime.bigint()-t0)/1e6;};
  e.pointer(-1e9,-1e9);for(let i=0;i<300;i++)step();e.scene('bento');for(let i=0;i<450;i++)step();e.scene('frame2');for(let i=0;i<Math.round(64*wait);i++)step();
  const R=e.root;let mv=moves(R,null);
  if(act.startsWith('open:')){const b=R.bodies.find(q=>q.name===act.slice(5)),l=st.pic.leaves.find(l=>l.path[0]&&l.path[0].body===b),c=(l&&cenOf(l))||[b.x,b.y];assert(e.click(c[0],c[1]),act+': the click missed');}else e.scene(act.slice(6));
  let mx=0,fr=0,worst=null,back=0,cost=0;const js=[];
  for(let k=0;k<64*4;k++){cost+=step();mv=moves(R,mv.now);js.push(mv.mx);mx=Math.max(mx,mv.mx);const s=shapes(st);fr+=s.fractured;worst=worst||s.worst;if(R.holes.some(b=>b.conveyBack))back++;}
  js.sort((a,b)=>a-b);return{max:+mx.toFixed(1),p99:+js[Math.floor(js.length*.99)].toFixed(1),fractured:fr,worst,backFrames:back,ms:+(cost/js.length).toFixed(1)};};
 for(const wait of [3.5,12,45])for(const act of ['scene:bento','scene:frame','scene:sidebar','open:Moss']){
  const was=run(files[0],wait,act),now=run(files[1],wait,act),label=act+' after '+wait+' s';
  assert.equal(now.fractured,0,label+': a fractured cell '+JSON.stringify(now.worst));
  assert(now.backFrames>0,label+': no cell went back from the belt');
  assert(now.max<=was.max+0.5,label+': a cell moved '+now.max+' px in a frame (Conveyor '+was.max+')');   // to half a pixel
  report.leave.push({act,wait,conveyor:{max:was.max,p99:was.p99,msPerFrame:was.ms},hinge:{max:now.max,p99:now.p99,backFrames:now.backFrames,msPerFrame:now.ms}});}
 console.log('leave',JSON.stringify(report.leave));
}
{ // INTO FRAME II AND OUT, with the worker thinking: nothing waits or fractures, what is rehearsed is what is played,
  // every change has one pace, every page at rest is exact
 const acts=['scene:frame2','open:Moss','scene:frame2','home','scene:frame2','scene:sidebar','scene:frame2','scene:bento'];
 const w0=offstage(BUDGET,files[0]),was=tour(files[0],size,{improv:true,budget:BUDGET,worker:w0,acts,paced:true,sea:true});w0.done();
 const w1=offstage(BUDGET),now=tour(files[1],size,{improv:true,budget:BUDGET,worker:w1,acts,paced:true,sea:true});w1.done();
 restChecks(now,was);
 report.inOut={acts,conveyor:total(was),mark:total(now),thinking:roundsTotal(now),changes:now.map((o,i)=>({act:o.act,conveyor:was[i].drawn.score,mark:o.drawn.score}))};
 console.log('inOut',JSON.stringify({conveyor:report.inOut.conveyor.score,mark:report.inOut.mark.score,thinking:report.inOut.thinking}));
}
{ // A STORY IS CONVEYOR'S: every frame of a Cue story, the world and every drawing command
 const run=file=>{const e=loadEngine(file,{...desk,count:12,record:true}),d=[];let ms=1000;const step=n=>{for(let i=0;i<n;i++){e.clear();e.advance(ms);ms+=1000/60;d.push(digest(e));}};
  step(300);e.cueStart();step(420);for(let k=1;k<4;k++){e.cueGo(k);step(300);}e.cuePush(-100);step(420);return d;};
 const d0=run(files[0]),d1=run(files[1]),at=d1.findIndex((x,i)=>x!==d0[i]);assert.equal(at,-1,'the Cue story left Conveyor\'s at frame '+at);
 report.story={frames:d0.length,identical:true};
}
const SCOPE='Real full tick; native Canvas and browser DOM stubbed; frames of 1/64 s; a desk of 1440×900 (the Cue story at 1900×810); the worker of Wings headless thinking sixteen rehearsed frames a frame. With the rule in and no budget, the tour and the chain through every page from every other (none of them Frame II) are Conveyor\'s, the world and every drawing command, frame by frame. From Bento, Frame II is Frame frame by frame until the change has landed; then, from when its belt is up to speed and for a minute, every cell is drawn, nothing fractures, no cell is drawn in the middle, every seed goes clockwise round the middle and never back, no faster than 40 px/s, every cell is drawn exactly its stretch (its share of the band when the belt started) and the cells cover the band, and every front between two cells in a corner block passes through the middle\'s corner (on Conveyor, reported). At every count tried from 4 to 30 cells the same holds for 12 s, and the belt starts with no cell moving further in a frame than on Conveyor. Leaving the belt as it gets up to speed, 12 s and 45 s after the ask, for Bento, Frame, Sidebar and a page, no cell moves further in a frame than on Conveyor, to half a pixel (moves over 300 px aside), and nothing fractures (a cell on its way back fractures only by a dent). Into Frame II and out of it to a page, home and two scenes, with the worker thinking, nothing waits or fractures, what is rehearsed is what is played, every change has one pace and every page at rest is exact. A Cue story is Conveyor\'s frame by frame.';
const result={scope:SCOPE,report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({trace:report.trace,frame2:report.frame2,inOut:{conveyor:report.inOut.conveyor.score,mark:report.inOut.mark.score},story:report.story}));
