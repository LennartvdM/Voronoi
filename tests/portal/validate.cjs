// Portal adds a click and page layouts. Without a click, the real tick must
// produce exactly the same state and the same drawing commands as Plaque;
// with clicks, every page kind and every behaviour the page promises is
// checked, whatever the set of kinds is: the whitespace is exactly the
// rectangles it was given, every cell is one convex power cell or a
// rectangle (the owner's shape rule, never a fractured edge), and the text
// is set in the reading void.
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
// fracture. Edges under 2 px are counted apart: a three-way junction a hair
// off, which Plaque's own scenes draw too.
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
function slot0(st){const e=st.e,n=e.root.bodies.filter(b=>!b.isVoid&&!b.leaving&&!b.isSelf).length;return e.scenes[e.config.scene](e.root.COLS,e.root.ROWS,n).content[0];}
function opened(st,b,label,phone){
 const e=st.e,KINDS=e.kinds(),T=e.templates();assert(e.focus()===b,label+': focus');assert.equal(e.config.scene,KINDS[b.id%KINDS.length],label+': kind');
 // through the change and at rest: never a fractured cell
 const tally={rectangle:0,notched:0,voronoi:0,cut:0,shortEdged:0,fractured:0};
 for(let f=0;f<420;f++){st.step(1);const sh=shapes(st);for(const k in tally)tally[k]+=sh[k];assert.equal(sh.fractured,0,label+': a fractured cell '+JSON.stringify(sh.worst)+' at frame '+f);}
 assert(e.rectsEqual(b.rect,slot0(st)),label+': the image did not take the first slot '+JSON.stringify([b.rect,slot0(st)]));
 const roots=rootsOf(st.pic).sort((p,q)=>area(q)-area(p));
 assert(roots[0].body===b,label+': the image is not the largest cell');
 assert(!st.pic.leaves.some(l=>l.path.length>1),label+': a field on a page');
 // the whitespace is exactly the rectangles it was given; the cells are one
 // site each; coverage is exact to a hairline of rasterisation
 const vx=voidsExact(st);assert(vx.ok,label+': '+vx.why);
 for(const l of roots)assert.equal(l.body.subs.length,1,label+': '+l.body.name+' has '+l.body.subs.length+' sites');
 const px=parseFloat(e.meters().mGap[0])+parseFloat(e.meters().mOver[0]);
 assert(px<=0.003*e.root.W*e.root.H,label+': seam residual '+e.meters().mGap[0]+' gap, '+e.meters().mOver[0]+' overlap');
 const t=T[e.config.scene],texts=e.commands.filter(c=>c[0]==='fillText'&&c[1]===b.name),fills=e.commands.filter(c=>c[0]==='fill').length;
 if(t.text){
  // the text: the title inside the seated reading void with paragraph bars; no label on the image
  const v=e.root.bodies.find(v=>v.isVoid&&!v.leaving&&v.rect&&v.rect.portalText);
  assert(v&&v.crystal>=.99,label+': no seated reading void');const r=v.rect,PW=e.root.PW,PH=e.root.PH;
  const inVoid=q=>q[2]>=r[0]*PW&&q[2]<=r[2]*PW&&q[3]>=r[1]*PH&&q[3]<=r[3]*PH;
  assert(texts.some(inVoid),label+': no title in the reading void');assert(fills>=8,label+': no paragraphs in the reading void');
  assert(b.caption.alpha<.05,label+': the image still carries its label');
  assert(!texts.some(q=>!inVoid(q)),label+': stray text on the image');
 }else{
  assert(!st.pic.leaves.some(l=>l.isVoid&&l.loops.length),label+': a caption page has whitespace');
  const c=texts.find(q=>q[3]>b.caption.y);assert(c,label+': no caption on the image');assert(fills>=1,label+': no caption line');
 }
 return{roots,tally,rest:shapes(st)};
}
const desk={width:1900,height:810,fields:.55},phone={width:390,height:720,fields:.55};
const report={kinds:[],home:null,field:null,void:null,interrupted:null,mirror:null,crossers:null,escape:null,hover:null,phone:[]};
{
 const st=fresh(desk),KINDS=st.e.kinds(),names={};
 for(const b of st.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&!(b.id%KINDS.length in names))names[b.id%KINDS.length]=b.name;
 assert.equal(Object.keys(names).length,KINDS.length,'not every kind has a cell at 12');
 let first=true;
 for(const k of Object.keys(names).map(Number).sort((a,b)=>a-b)){
  const s=fresh(desk),w=whereIs(s,names[k]);
  assert(s.e.click(w.x,w.y),'click missed '+names[k]);
  const {roots,tally,rest}=opened(s,w.b,KINDS[k]);
  report.kinds.push({kind:KINDS[k],cell:names[k],imageShare:+(area(roots[0])/(1900*810)).toFixed(3),smallestCard:+(area(roots[roots.length-1])/(1900*810)).toFixed(4),rest:{rectangle:rest.rectangle,voronoi:rest.voronoi,cut:rest.cut,shortEdged:rest.shortEdged},transition:tally,gap:s.e.meters().mGap[0]});
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
{ // the page opens on the side the click came from: the image's slot is the nearer of the template's and its mirror
 const st=fresh(desk),KINDS=st.e.kinds(),T=st.e.templates();let checked=0;
 for(const b of st.e.root.bodies){const k=KINDS[b.id%KINDS.length];if(b.isVoid||b.isSelf||!b.name||!T[k].text||k==='essay')continue;
  const s=fresh(desk),w=whereIs(s,b.name);if(!s.e.click(w.x,w.y))continue;s.step(60);
  const hx=(T[k].hero[0]+T[k].hero[2])/2*1900,slot=slot0(s),sx=(slot[0]+slot[2])/2*s.e.root.PW;
  const near=Math.abs(w.x-hx)<=Math.abs(w.x-(1900-hx))+1?hx:1900-hx;
  assert(Math.abs(sx-near)<Math.abs(sx-(1900-near)),k+' from '+b.name+': the image slot is on the far side of the click');checked++;
  if(checked>=3)break;}
 assert(checked>=1,'no mirror case checked');report.mirror={checked};
}
{ // a page's whitespace waits for the cells crossing it: the text is set only once the last crosser has landed
 const s=fresh(desk),KINDS=s.e.kinds(),T=s.e.templates();let name=null;
 for(const b of s.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&KINDS[b.id%KINDS.length]==='spread'){name=b.name;break;}
 const w=whereIs(s,name);assert(s.e.click(w.x,w.y));
 const e=s.e,v=e.root.bodies.find(q=>q.isVoid&&!q.leaving&&q.rect&&q.rect.portalText);assert(v,'no reading void');
 const r=v.rect,PW=e.root.PW,PH=e.root.PH,inR=(x,y)=>x>=r[0]*PW&&x<=r[2]*PW&&y>=r[1]*PH&&y<=r[3]*PH;
 const crossers=e.root.bodies.filter(b=>!b.isVoid&&!b.isSelf&&b.path&&b.journey&&!inR(b.x,b.y)).filter(b=>{const p=b.path;for(let k=1;k<20;k++){const t=k/20,m=1-t;if(inR(m*m*p.sx+2*m*t*p.cx+t*t*p.ex,m*m*p.sy+2*m*t*p.cy+t*t*p.ey))return true;}return false;});
 let textAt=-1,lastLanded=-1;
 for(let f=0;f<420;f++){s.step(1);if(textAt<0&&e.commands.some(c=>c[0]==='fillText'&&c[1]===w.b.name&&inR(c[2],c[3])))textAt=f;if(crossers.some(b=>b.journey&&b.progress<1))lastLanded=f;}
 assert(textAt>=0,'the text never came');assert(crossers.length>0,'no cell crossed the reading void');
 assert(textAt>lastLanded,'the text was set at frame '+textAt+' while a crosser was still travelling at frame '+lastLanded);
 report.crossers={count:crossers.length,lastLanded,textAt};
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
 s.e.pointer(-1e9,-1e9);s.step(180);{const v=voidsExact(s);assert(v.ok,'the page did not recover from hover: '+v.why);}
 report.hover={imageHoverMix:+a.hoverMix.toFixed(3),cardHovered:other.name};
}
{ // add and remove a cell on an open page: the image keeps its slot, the grid stays exact
 const s=fresh(desk),rs=rootsOf(s.pic),a=rs[0].body;assert(s.e.click(a.caption.x,a.caption.y));s.step(420);
 s.e.root.addBody();s.step(360);assert(s.e.rectsEqual(a.rect,slot0(s)),'the image lost its slot after add');{const v=voidsExact(s);assert(v.ok,'not exact after add: '+v.why);}
 s.e.root.removeBody();s.step(360);assert(s.e.rectsEqual(a.rect,slot0(s)),'the image lost its slot after remove');{const v=voidsExact(s);assert(v.ok,'not exact after remove: '+v.why);}
}
{ // a phone: every kind opens the same way, stacked, its text set full width
 const st=fresh(phone),KINDS=st.e.kinds(),names={};
 for(const b of st.e.root.bodies)if(!b.isVoid&&!b.isSelf&&b.name&&!(b.id%KINDS.length in names))names[b.id%KINDS.length]=b.name;
 for(const k of Object.keys(names).map(Number).sort((a,b)=>a-b)){
  const s=fresh(phone),w=whereIs(s,names[k]);assert(s.e.click(w.x,w.y),'phone click missed '+names[k]);const o=opened(s,w.b,'phone '+KINDS[k],true);
  report.phone.push({kind:KINDS[k],rest:{rectangle:o.rest.rectangle,voronoi:o.rest.voronoi,shortEdged:o.rest.shortEdged}});
 }
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without a click, state and every drawing command must exactly match Plaque; with clicks, every page kind opens with its whitespace exactly the rectangles it was given, every cell one site and never fractured, its text in the reading void, and every click behaviour is asserted.',hashes:files.map(f=>({file:path.basename(f),sha256:hash(fs.readFileSync(f))})),matrix,totalFrames:total,drawingCommands:commandsTotal,clicks:report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,clicks:report}));
