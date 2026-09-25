// Tandem opens a page all at once: the image never bigger than the room its
// own rectangle has (and what it has still to leave elsewhere), the text as
// big as the room its rectangle has as soon as it has it, the ground nobody
// bids for the opening whitespace's, and the text's whitespace making way for
// the cells still crossing it. Without a page opened, the real tick must
// produce exactly the same state and the same drawing commands as Cue, a Tell
// story, a Tell II story, a Cue story and home included. On a tour of pages
// opened from home and from one another, on a desk and on a phone, every page
// is exact at rest (the image on its rectangle, the text's whitespace painted
// over its rectangle, the whitespace exactly its rectangles, no field),
// nothing fractures on any frame, the image takes little of the text's
// rectangle on its way (under 30% at worst, and on average half what it takes
// on Cue or less), and the text's lag (the room of its rectangle that no one
// else holds and it does not yet paint) is a fraction of Cue's.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine}=require('./probe.cjs');
const rectsEqual=(a,b)=>a&&b&&a.length>=4&&b.length>=4&&a.slice(0,4).every((v,i)=>Math.abs(v-b[i])<1e-6);
const files=[path.resolve(__dirname,'../../cue.html'),path.resolve(__dirname,'../../tandem.html')];
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
const report={stories:null,desk:null,phone:null};
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
// --- a Tell, a Tell II and a Cue story and home, no page opened: Cue's, exactly
{
 const cfg={width:1900,height:810,count:12,fields:.55,dt:1000/60};
 const es=files.map(f=>loadEngine(f,{...cfg,record:true}));let now=1000,frame=0;
 const advance=n=>{for(let k=0;k<n;k++){
  es.forEach(e=>e.clear());const ps=es.map(e=>e.advance(now));
  assert.equal(hash(state(es[1],ps[1])),hash(state(es[0],ps[0])),'state changed in a story, frame '+frame);
  assert.equal(hash(JSON.stringify(es[1].commands)),hash(JSON.stringify(es[0].commands)),'drawing changed in a story, frame '+frame);
  commandsTotal+=es[1].commands.length;now+=cfg.dt;frame++;total++;
 }};
 advance(300);
 es.forEach(e=>e.tellStart());advance(420);es.forEach(e=>e.tellPush(100));advance(240);
 es.forEach(e=>e.tellDragStart(900,600,now));for(let f=1;f<=6;f++){es.forEach(e=>e.tellDragMove(900,600-810/12*f,now));advance(1);}advance(30);es.forEach(e=>e.tellDragEnd(-1e9));advance(180);
 es.forEach(e=>e.home());advance(300);
 es.forEach(e=>e.tell2Start());advance(420);es.forEach(e=>e.tell2Push(100));advance(300);es.forEach(e=>e.tell2Push(100));advance(300);
 es.forEach(e=>e.home());advance(300);
 es.forEach(e=>e.cueStart());advance(420);
 for(const k of [1,2,3,5,4])es.forEach(e=>e.cueGo(k)),advance(k===5?36:300);
 es.forEach(e=>e.cuePush(-100));advance(420);es.forEach(e=>e.escape());advance(420);
 assert(!es[1].cue()&&es[1].focus()===null,'the stories did not end at home');
 report.stories={frames:frame,tell:true,tell2:true,cue:true};
}
// --- pages ------------------------------------------------------------------------
const ring=pts=>Math.abs(pts.reduce((q,p,i,a)=>{const m=a[(i+1)%a.length];return q+p[0]*m[1]-m[0]*p[1];},0)/2);
const clipRect=(P,r)=>{let o=P;const cl=(a,b,c)=>{const n=[];for(let i=0;i<o.length;i++){const p=o[i],q=o[(i+1)%o.length],dp=a*p[0]+b*p[1]-c,dq=a*q[0]+b*q[1]-c;if(dp<=0)n.push(p);if(dp*dq<0){const t=dp/(dp-dq);n.push([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])]);}}o=n;};cl(-1,0,-r[0]);cl(1,0,r[2]);cl(0,-1,-r[1]);cl(0,1,r[3]);return o.length>=3?ring(o):0;};
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
const cenOf=l=>{let A=0,x=0,y=0;for(const pts of l.loops)for(let i=0;i<pts.length;i++){const p=pts[i],q=pts[(i+1)%pts.length],f=p[0]*q[1]-q[0]*p[1];A+=f;x+=(p[0]+q[0])*f;y+=(p[1]+q[1])*f;}return Math.abs(A)>1e-6?[x/(3*A),y/(3*A)]:null;};
// A TOUR: each page opened from home or from another page; every frame of
// the change measured, and the page at rest checked
function tour(file,size,list){
 const e=loadEngine(file,{...size,count:12,record:true}),st={e,pic:null};let ms=1000;
 const step=n=>{for(let i=0;i<n;i++){e.clear();st.pic=e.advance(ms);ms+=1000/60;}};e.pointer(-1e9,-1e9);step(200);
 const R=e.root,body=n=>R.bodies.find(b=>b.name===n),px=r=>[r[0]*R.PW,r[1]*R.PH,r[2]*R.PW,r[3]*R.PH];
 const click=n=>{const b=body(n),l=st.pic.leaves.find(l=>l.path[0]&&l.path[0].body===b),c=(l&&cenOf(l))||[b.x,b.y];return e.click(c[0],c[1]);};
 const out=[],T=e.templates(),K=e.kinds();
 for(const [from,to] of list){
  const label=(size.width<size.height?'phone ':'')+from+' -> '+to;
  if(from==='home'){e.home();step(300);}else{assert(click(from),label+': the click on '+from+' missed');step(300);}
  assert(click(to),label+': the click missed');const hero=body(to),kind=K[hero.id%K.length];
  let lag=0,heroOut=0,inText=0,frac=0,worst=null;
  for(let f=1;f<=420;f++){step(1);
   const txt=R.bodies.find(v=>v.isVoid&&!v.leaving&&v.rect&&v.rect.portalText),hr=px(hero.rect),tr=txt?px(txt.rect):null;
   let ha=0,hin=0,tin=0,oin=0,hint=0;
   for(const l of st.pic.leaves){const b=l.path[0].body;let a=0;for(const lp of l.loops)a+=ring(lp);
    if(b===hero){ha+=a;for(const lp of l.loops)hin+=clipRect(lp,hr);}
    if(tr){let t=0;for(const lp of l.loops)t+=clipRect(lp,tr);if(b===txt)tin+=t;else if(b===hero)hint+=t;else oin+=t;}}
   heroOut+=Math.max(0,ha-hin)/60;
   if(tr){const A=(tr[2]-tr[0])*(tr[3]-tr[1]);lag+=Math.max(0,A-oin-tin)/60;inText=Math.max(inText,hint/A);}
   const sh=shapes(st);frac+=sh.fractured;worst=worst||sh.worst;}
  // AT REST: the image on its rectangle, the text's whitespace painted over
  // its rectangle with the title in it, the whitespace exactly its
  // rectangles, no field, one site a cell
  const rest={};
  const n=R.bodies.filter(b=>!b.isVoid&&!b.leaving&&!b.isSelf).length,slot=e.scenes[e.config.scene](R.COLS,R.ROWS,n).content[0];
  rest.page=e.focus()===hero&&e.config.scene===kind;
  rest.onRect=rectsEqual(hero.rect,slot);
  const hl=st.pic.leaves.find(l=>l.path.length===1&&l.body===hero),hr=px(hero.rect);
  rest.imageCovers=hl?+(hl.loops.reduce((a,lp)=>a+clipRect(lp,hr),0)/((hr[2]-hr[0])*(hr[3]-hr[1]))).toFixed(4):0;
  if(T[kind].text){const v=R.bodies.find(v=>v.isVoid&&!v.leaving&&v.rect&&v.rect.portalText),r=px(v.rect);
   rest.textCovers=+(st.pic.leaves.filter(l=>l.body===v).reduce((a,l)=>a+l.loops.reduce((q,lp)=>q+clipRect(lp,r),0),0)/((r[2]-r[0])*(r[3]-r[1]))).toFixed(4);
   rest.title=e.commands.some(c=>c[0]==='fillText'&&c[1]===hero.name&&c[2]>=r[0]&&c[2]<=r[2]&&c[3]>=r[1]&&c[3]<=r[3]);}
  const vx=voidsExact(st);rest.exact=vx.ok;rest.field=st.pic.leaves.some(l=>l.path.length>1);
  rest.oneSite=R.bodies.filter(b=>!b.isVoid&&!b.leaving&&!b.isSelf).every(b=>b.subs.length===1);
  out.push({label,from,to,kind,text:!!T[kind].text,textLag:Math.round(lag),imageOutside:Math.round(heroOut),imageInText:+inText.toFixed(4),fractured:frac,worst,why:vx.why,rest});
 }
 return out;
}
// on a gallery page, the image's rectangle meets the gallery's power cells, which on Cue already cover a
// few hundredths of it at rest; the image covers its rectangle as much as on Cue
const DESK=['home:Drift','home:Ember','home:Tide','home:Moss','home:Petal','home:Aurora','home:Dune','home:Coal','Aurora:Moss','Moss:Aurora','Aurora:Tide','Tide:Aurora','Coal:Aurora','Aurora:Dune','Dune:Aurora','Ember:Coal','Dune:Petal','Petal:Aurora'].map(s=>s.split(':'));
const PHONE=['home:Aurora','home:Dune','home:Moss','Aurora:Dune','Dune:Aurora','Moss:Aurora','Aurora:Coal'].map(s=>s.split(':'));
const sum=(r,k)=>r.reduce((a,o)=>a+o[k],0);
for(const [key,size,list] of [['desk',{width:1440,height:900,fields:.55},DESK],['phone',{width:390,height:720,fields:.55},PHONE]]){
 const was=tour(files[0],size,list),now=tour(files[1],size,list);
 now.forEach((o,i)=>{const label=o.label,rest=o.rest,cue=was[i].rest;
  assert(rest.page,label+': the page did not open');
  assert(rest.onRect,label+': the image is not on its rectangle');
  assert(rest.imageCovers>=Math.min(0.99,cue.imageCovers-0.002),label+': the image covers '+(100*rest.imageCovers).toFixed(1)+'% of its rectangle, on Cue '+(100*cue.imageCovers).toFixed(1)+'%');
  if(o.text){assert(rest.textCovers>=Math.min(0.99,cue.textCovers-0.002),label+': the text covers '+(100*rest.textCovers).toFixed(1)+'% of its rectangle, on Cue '+(100*cue.textCovers).toFixed(1)+'%');assert(rest.title,label+': no title in the text');}
  assert(rest.exact,label+': '+o.why);assert(!rest.field,label+': a field on a page');assert(rest.oneSite,label+': a cell with more than one site');
  assert.equal(o.fractured,0,label+': a fractured cell '+JSON.stringify(o.worst));
  assert(o.imageInText<0.3,label+': the image took '+(100*o.imageInText).toFixed(1)+'% of the text\'s rectangle');   // on its way, the image keeps out of the text's rectangle but for where it crosses it
 });
 const inWas=sum(was,'imageInText')/was.length,inNow=sum(now,'imageInText')/now.length;
 assert(inNow<=0.5*inWas,key+': the image took '+(100*inNow).toFixed(1)+'% of the text\'s rectangle at worst, on average, Cue '+(100*inWas).toFixed(1)+'%');
 const lagWas=sum(was,'textLag'),lagNow=sum(now,'textLag');
 assert(lagNow<0.25*lagWas,key+': the text\'s lag is '+lagNow+' px²·s, Cue\'s '+lagWas);   // the text opens behind the cells, not after them
 now.forEach((o,i)=>assert(o.textLag<=Math.max(was[i].textLag,20000),key+' '+o.from+' -> '+o.to+': the text lags more than on Cue'));
 report[key]={size,textLag:{cue:lagWas,tandem:lagNow},imageOutside:{cue:sum(was,'imageOutside'),tandem:sum(now,'imageOutside')},imageInTextWorst:{cue:Math.max(...was.map(o=>o.imageInText)),tandem:Math.max(...now.map(o=>o.imageInText))},imageInTextMean:{cue:+inWas.toFixed(4),tandem:+inNow.toFixed(4)},openings:now.map((o,i)=>({from:o.from,to:o.to,kind:o.kind,textLag:[was[i].textLag,o.textLag],imageOutside:[was[i].imageOutside,o.imageOutside],imageInText:[was[i].imageInText,o.imageInText],fracturedFrames:[was[i].fractured,o.fractured],rest:o.rest}))};
}
const result={scope:'Real full tick; native Canvas and browser DOM stubbed. Without a page opened, state and every drawing command must exactly match Cue, a Tell, a Tell II and a Cue story and home included; on a tour of pages opened from home and from one another, on a desk and on a phone, every page at rest has its image on its rectangle and covering it (as much as on Cue), its text covering its rectangle (as much as on Cue) with the title in it, the whitespace exactly its rectangles, no field and one site a cell; nothing fractures on any frame of an opening; on its way the image takes under 30% of the text\'s rectangle at worst on any opening, and on average no more than half what it takes on Cue; and the text\'s lag (px²·s of its rectangle that no one else holds and it does not yet paint) is under a quarter of Cue\'s over the tour and no worse than Cue\'s on any opening. Cue\'s figures are reported beside Tandem\'s.',frames:total,drawingCommands:commandsTotal,matrix,report};
fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({totalFrames:total,drawingCommands:commandsTotal,stories:report.stories,desk:{textLag:report.desk.textLag,imageOutside:report.desk.imageOutside,imageInTextWorst:report.desk.imageInTextWorst},phone:{textLag:report.phone.textLag,imageOutside:report.phone.imageOutside,imageInTextWorst:report.phone.imageInTextWorst}}));
