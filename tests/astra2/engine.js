// Astra II: transport the footprint, not a melt/travel/lock cycle.
function a2Offsets(h,b) {
  return b.subs.map(s=>[s.x-b.x,s.y-b.y]);
}
function a2Destination(h,r) {
  if (!r) return [[0,0]];
  const [cx,cy]=h.rectCenter(r), out=[];
  for(let y=r[1];y<r[3];y++) for(let x=r[0];x<r[2];x++) out.push([(x+.5)*h.PW-cx,(y+.5)*h.PH-cy]);
  return out;
}
function a2PairSites(a,b) {
  if(!a.length)a=[[0,0]]; if(!b.length)b=[[0,0]];
  const pairs=[], edges=[], usedA=new Set(),usedB=new Set();
  for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)edges.push({i,j,d:(a[i][0]-b[j][0])**2+(a[i][1]-b[j][1])**2});
  edges.sort((a,b)=>a.d-b.d||a.i-b.i||a.j-b.j);
  for(const e of edges)if(!usedA.has(e.i)&&!usedB.has(e.j)){usedA.add(e.i);usedB.add(e.j);pairs.push([a[e.i],b[e.j]]);}
  for(let i=0;i<a.length;i++)if(!usedA.has(i)){const e=edges.find(e=>e.i===i);pairs.push([a[i],b[e.j]]);}
  for(let j=0;j<b.length;j++)if(!usedB.has(j)){const e=edges.find(e=>e.j===j);pairs.push([a[e.i],b[j]]);}
  return pairs;
}
function a2Begin(h,b,source,c0) {
  if(!b.journey)return;
  b.journey.hold=0;b.a2Scale=[1,1];
  b.a2Morph={pairs:a2PairSites(source,a2Destination(h,b.rect)),c0,source,serial:h.serial};
}
const a2Seat=Hive.prototype.seatBody;
Hive.prototype.seatBody=function(b,r,T,timing){
  if(this.depth!==0)return a2Seat.call(this,b,r,T,timing);
  const source=a2Offsets(this,b),c0=b.crystal,old=b.journey;
  a2Seat.call(this,b,r,T,timing);
  if(b.journey!==old)a2Begin(this,b,source,c0);
};
const a2Release=Hive.prototype.releaseBody;
Hive.prototype.releaseBody=function(b,T){
  if(this.depth!==0)return a2Release.call(this,b,T);
  const source=a2Offsets(this,b),c0=b.crystal,old=b.journey;
  a2Release.call(this,b,T);
  if(b.journey!==old)a2Begin(this,b,source,c0);
};
const a2Retire=Hive.prototype.retireBody;
Hive.prototype.retireBody=function(b,dur,T){
  if(this.depth!==0)return a2Retire.call(this,b,dur,T);
  const source=a2Offsets(this,b),c0=b.crystal,old=b.journey;
  a2Retire.call(this,b,dur,T);
  if(b.journey!==old)a2Begin(this,b,source,c0);
};
const a2Crystal=Hive.prototype.updateCrystal;
Hive.prototype.updateCrystal=function(b,t){
  if(this.depth!==0||!b.a2Morph||!b.journey)return a2Crystal.call(this,b,t);
  const j=b.journey,s=t-j.t0-j.delay;if(s<0)return;
  const q=b.progress, target=b.rect&&!b.leaving?1:0;
  b.crystal=Math.min(.999,b.a2Morph.c0*(1-q)+target*q);
  const u=Math.min(1,Math.max(0,s/j.dur));
  b.pin=target*S3((u-.75)/.25);
  if(q>=1){b.crystal=target;b.formRect=b.rect;}
};
const a2Place=Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds=function(){
  if(this.depth!==0)return a2Place.call(this);
  for(const b of this.bodies){
    const morph=b.a2Morph;
    if(!morph){ // Existing steady-state or fresh single-site body.
      const r=b.formRect,mix=b.crystal,w=b.subs[0]?b.subs[0].w:0;
      const claim=b.claim*(1+(config.hoverBoost-1)*b.hoverMix*(1-mix));
      const off=a2Destination(this,r).map(p=>[mix*p[0],mix*p[1]]), seen=new Set();
      b.subs=[];
      for(const p of off){const key=p.map(v=>v.toFixed(6)).join(',');if(seen.has(key))continue;seen.add(key);b.subs.push({body:b,x:b.x+p[0],y:b.y+p[1],w,claim,live:true});}
      continue;
    }
    const q=b.progress,w=b.subs[0]?b.subs[0].w:0;
    const claim=b.claim*(1+(config.hoverBoost-1)*b.hoverMix*(1-b.crystal)),seen=new Set();
    b.subs=[];
    for(const [a,d] of morph.pairs){
      const x=a[0]+q*(d[0]-a[0]),y=a[1]+q*(d[1]-a[1]);
      const key=x.toFixed(6)+','+y.toFixed(6);if(seen.has(key))continue;seen.add(key);
      b.subs.push({body:b,x:b.x+x,y:b.y+y,w,claim,live:true});
    }
    if(q>=1){b.formRect=b.rect;}
  }
};
function a2Match(cost) {
 const n=cost.length,m=cost[0]?.length||0;if(!n)return[];if(m<n)throw Error('Not enough roles');
 const u=new Float64Array(n+1),v=new Float64Array(m+1),p=new Int32Array(m+1),way=new Int32Array(m+1);
 for(let i=1;i<=n;i++){p[0]=i;let j0=0;const min=new Float64Array(m+1).fill(Infinity),used=new Uint8Array(m+1);
 do{used[j0]=1;const i0=p[j0];let delta=Infinity,j1=0;for(let j=1;j<=m;j++)if(!used[j]){const cur=cost[i0-1][j-1]-u[i0]-v[j];if(cur<min[j]){min[j]=cur;way[j]=j0;}if(min[j]<delta){delta=min[j];j1=j;}}
 for(let j=0;j<=m;j++){if(used[j]){u[p[j]]+=delta;v[j]-=delta;}else min[j]-=delta;}j0=j1;}while(p[j0]);do{const j1=way[j0];p[j0]=p[j1];j0=j1;}while(j0);}
 const ans=Array(n);for(let j=1;j<=m;j++)if(p[j])ans[p[j]-1]=j-1;return ans;
}
function a2Intersection(h,b,r) {
 let total=0;
 for(const [loops,sign]of [[b.loops||[],1],[b.holes||[],-1]])for(const l of loops){
   let p={pts:l,labs:l.map(()=>-1)};
   for(const hp of [[-1,0,-r[0]*h.PW],[1,0,r[2]*h.PW],[0,-1,-r[1]*h.PH],[0,1,r[3]*h.PH]]){if(p.pts.length<3)break;p=clipHalfPlane(p,...hp,-1);}
   if(p.pts.length>=3)total+=sign*Math.abs(ringArea(p.pts));
 }return Math.max(0,total);
}
function a2MassCenter(b){let area=0,x=0,y=0;for(const [loops,sign] of [[b.loops||[],1],[b.holes||[],-1]])for(const pts of loops){let a=0,cx=0,cy=0;for(let i=0;i<pts.length;i++){const q=pts[i],r=pts[(i+1)%pts.length],v=q[0]*r[1]-r[0]*q[1];a+=v;cx+=(q[0]+r[0])*v;cy+=(q[1]+r[1])*v;}if(Math.abs(a)>1e-8){const k=sign*Math.abs(a)/2;area+=k;x+=k*cx/(3*a);y+=k*cy/(3*a);}}return area>1?[x/area,y/area]:[b.x,b.y];}
function a2RoleCost(h,b,r){const [x,y]=h.rectCenter(r),[cx,cy]=a2MassCenter(b);return .3*((x-b.x)**2+(y-b.y)**2)+.7*((x-cx)**2+(y-cy)**2)-.5*a2Intersection(h,b,r);}
const a2AssignOld=assignStations;
assignStations=function(points,stations){
 if(points[0]?.a2AssignHive){const h=points[0].a2AssignHive;return a2Match(points.map(b=>h.a2Spec.content.map(r=>a2RoleCost(h,b,r))));}
 return a2AssignOld(points,stations);
};
const a2Scene=Hive.prototype.enterScene;
Hive.prototype.enterScene=function(name,origin){
 if(this.depth!==0)return a2Scene.call(this,name,origin);
 this.a2CanReview=!!this.solved;this.a2Reassignments=0;this.a2ExchangeLog=[];
 const content=this.bodies.filter(b=>!b.isVoid&&!b.leaving&&!b.isSelf);
 this.a2Spec=scenes[name]?scenes[name](this.COLS,this.ROWS,content.length):null;
 for(const b of content)b.a2SwapCount=0;
 if(this.solved)for(const b of content)b.a2AssignHive=this;
 a2Scene.call(this,name,origin);
 for(const b of content)delete b.a2AssignHive;
};
const a2ReviewSteer=Hive.prototype.steer;
Hive.prototype.steer=function(dt,t){
 if(this.depth===0&&this.solved&&this.a2CanReview&&t-(this.a2LastReview||0)>.12){
  this.a2LastReview=t;
  const moving=this.bodies.filter(b=>!b.isVoid&&!b.leaving&&b.rect&&b.path&&b.journey&&b.progress<.8&&b.pin<.5&&!(b.a2SwapCount>0));
  let best=null,gain=0;
  for(let i=0;i<moving.length;i++)for(let k=i+1;k<moving.length;k++){
   const a=moving[i],b=moving[k];
   const near=Math.hypot(a.x-b.x,a.y-b.y)<1.4*(Math.sqrt(Math.max(1,a.paintArea)/Math.PI)+Math.sqrt(Math.max(1,b.paintArea)/Math.PI));if(!near)continue;
   const old=a2RoleCost(this,a,a.rect)+a2RoleCost(this,b,b.rect),next=a2RoleCost(this,a,b.rect)+a2RoleCost(this,b,a.rect);
   const da=Math.hypot(a.x-a.path.ex,a.y-a.path.ey),db=Math.hypot(b.x-b.path.ex,b.y-b.path.ey);
   const benefit=old-next;
   if(benefit>Math.max(3000,.15*(da*da+db*db))&&benefit>gain){gain=benefit;best=[a,b];}
  }
  if(best){const[a,b]=best,ar=a.rect,br=b.rect;
   const end=Math.max(a.journey.t0+a.journey.delay+a.journey.dur,b.journey.t0+b.journey.delay+b.journey.dur),dur=Math.max(.65,Math.min(1.8,end-t));
   const states=best.map(b=>[b.x,b.y,b.vx,b.vy]);
   this.seatBody(a,br,0,{t0:t,delay:0,dur,c0:a.crystal});this.seatBody(b,ar,0,{t0:t,delay:0,dur,c0:b.crystal});
   for(const q of best){q.a2SwapCount=1;q.a2Gate=null;q.fieldRect=q.rect;q.fieldAt=t+.1;for(const v of this.bodies)if(v.table)for(const row of v.table.rows)if(row.body===q)row.journey=q.journey;}
   this.a2Reassignments=(this.a2Reassignments||0)+1;
   (this.a2ExchangeLog||(this.a2ExchangeLog=[])).push({t,ids:[a.id,b.id],from:[ar,br],gain,positionJump:Math.max(...best.map((q,i)=>Math.hypot(q.x-states[i][0],q.y-states[i][1]))),velocityJump:Math.max(...best.map((q,i)=>Math.hypot(q.vx-states[i][2],q.vy-states[i][3])))});
  }
 }
 return a2ReviewSteer.call(this,dt,t);
};
// Sites retain their shape until two proposed footprints physically overlap.
// The moving participant yields first; a waiting neighbour is not pre-melted.
const a2YieldPlace=Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds=function(){
 a2YieldPlace.call(this);if(this.depth!==0)return;
 const active=this.bodies.filter(b=>!b.leaving&&b.subs.length), boxes=new Map(), want=new Map();
 for(const b of active){let x=0,y=0;for(const s of b.subs){x=Math.max(x,Math.abs(s.x-b.x));y=Math.max(y,Math.abs(s.y-b.y));}boxes.set(b,[x,y]);want.set(b,[1,1]);}
 const mobility=b=>(b.isVoid?.3:1)*(.02+Math.min(1,Math.hypot(b.vx,b.vy)/120))*(1-.8*(b.pin||0));
 for(let i=0;i<active.length;i++)for(let j=i+1;j<active.length;j++){
  const a=active[i],b=active[j],A=boxes.get(a),B=boxes.get(b),dx=Math.abs(a.x-b.x),dy=Math.abs(a.y-b.y),pad=4;
  if(dx>=A[0]+B[0]+pad||dy>=A[1]+B[1]+pad)continue;
  const first=mobility(a)>=mobility(b)?a:b,other=first===a?b:a,F=boxes.get(first),O=boxes.get(other);
  const fx=F[0]>1?(dx-O[0]-pad)/F[0]:-Infinity,fy=F[1]>1?(dy-O[1]-pad)/F[1]:-Infinity;
  const axis=fx>fy?0:1,f=Math.max(.2,Math.min(1,Math.max(fx,fy)));
  want.get(first)[axis]=Math.min(want.get(first)[axis],f);
 }
 for(const b of active){const old=b.a2Scale||[1,1],target=want.get(b),dt=this.lastDt||1/60;
  const next=target.map((x,i)=>{const z=old[i]+(x-old[i])*(1-Math.exp(-dt/(x<old[i]?.12:.24)));return Math.abs(z-1)<.001?1:z;});
  b.a2Scale=next;b.a2YieldDemand=target;
  for(const s of b.subs){s.x=b.x+(s.x-b.x)*next[0];s.y=b.y+(s.y-b.y)*next[1];}
 }
};
// Local, repayable visible-area credit accompanies an actual excursion
// outside the viewport. The spill ring never inflates every cell's quota.
function a2LoanLevel(l,t){
 if(l.retireAt!==undefined)return l.retireLevel*(1-S3((t-l.retireAt)/.35));
 const u=Math.min(1,Math.max(0,(t-l.start)/l.duration));return 64*u*u*u*(1-u)*(1-u)*(1-u);
}
function a2ExternalCarrot(h,b,t){
 if(h.depth!==0)return [0,0];let x=0,y=0;
 for(const l of h.a2Loans||[]){if(l.giver!==b||l.retireAt!==undefined)continue;const f=a2LoanLevel(l,t)*l.shift;x+=f*l.n[0];y+=f*l.n[1];}
 return [x,y];
}
const a2SpillScene=Hive.prototype.enterScene;
Hive.prototype.enterScene=function(name,origin){
 const had=this.solved,loans=this.a2Loans||[];
 for(const l of loans)if(l.retireAt===undefined){l.retireLevel=a2LoanLevel(l,this.t);l.retireAt=this.t;}
 a2SpillScene.call(this,name,origin);if(this.depth!==0||!had)return;
 this.a2Loans=loans.filter(l=>l.retireLevel>1e-6);this.a2Bleed=Math.min(100,.15*Math.min(this.W,this.H));
 const cells=this.bodies.filter(b=>!b.isVoid&&!b.leaving&&b.rect&&b.path&&b.journey?.t0===this.t);
 let best=null,score=0;
 for(const b of cells){
  const edges=[{d:b.x,n:[-1,0],end:b.path.ex},{d:this.W-b.x,n:[1,0],end:this.W-b.path.ex},{d:b.y,n:[0,-1],end:b.path.ey},{d:this.H-b.y,n:[0,1],end:this.H-b.path.ey}].sort((a,b)=>a.d-b.d);
  const edge=edges[0],limit=Math.min(this.W,this.H)*.25;
  if(edge.d>limit||edge.end>limit||Math.hypot(b.path.ex-b.x,b.path.ey-b.y)<25)continue;
  for(const q of cells){if(q===b)continue;const area=a2Intersection(this,b,q.rect);const value=area/(20+edge.d+edge.end);
   if(area>Math.min(b.paintArea,q.paintArea)*.12&&value>score){score=value;best={giver:b,taker:q,n:edge.n,d:edge.d,end:edge.end};}
  }
 }
 if(best&&this.a2Loans.length<2){
  best.start=this.t+best.giver.journey.delay;best.duration=Math.max(.9,.72*best.giver.journey.dur);
  best.shift=.8*best.d+.2*best.end+.5*this.a2Bleed;best.maxCredit=.22*Math.min(best.giver.claim,best.giver.claimTarget);
  best.giver.a2MaySpill=true;this.a2Loans.push(best);(this.a2LoanHistory||(this.a2LoanHistory=[])).push({scene:name,giver:best.giver.id,taker:best.taker.id,normal:best.n,start:best.start,duration:best.duration});
 }
};
const a2SpillPre=Hive.prototype.enforcePreconditions;
Hive.prototype.enforcePreconditions=function(dt){
 if(this.depth!==0)return a2SpillPre.call(this,dt);
 for(const b of this.bodies){
  // A departed loan does not grant permanent permission to wander off-screen.
  const pending=(this.a2Loans||[]).some(l=>l.giver===b&&(this.t<=l.start||a2LoanLevel(l,this.t)>1e-8));
  if(b.a2MaySpill&&!pending&&b.x>=SEED_MARGIN&&b.x<=this.W-SEED_MARGIN&&b.y>=SEED_MARGIN&&b.y<=this.H-SEED_MARGIN)b.a2MaySpill=false;
  const B=b.a2MaySpill?(this.a2Bleed||0):0;b.x=Math.min(this.W+B-SEED_MARGIN,Math.max(-B+SEED_MARGIN,b.x));b.y=Math.min(this.H+B-SEED_MARGIN,Math.max(-B+SEED_MARGIN,b.y));}
 for(let i=0;i<this.bodies.length;i++)for(let j=i+1;j<this.bodies.length;j++){
  const a=this.bodies[i],b=this.bodies[j];let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);if(d<SEED_MIN_SEP){if(d<1e-6){dx=1;dy=0;d=1;}const k=(SEED_MIN_SEP-d)/2/d;a.x-=dx*k;a.y-=dy*k;b.x+=dx*k;b.y+=dy*k;}
 }
};
const a2SpillPlace=Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds=function(){
 a2SpillPlace.call(this);if(this.depth!==0)return;
 const live=new Set(this.bodies);this.a2LoanCredit=0;
 this.a2Loans=(this.a2Loans||[]).filter(l=>a2LoanLevel(l,this.t)>1e-8||this.t<=l.start);
 for(const l of this.a2Loans){const give=l.giver,take=l.taker;
  if(!live.has(give)||!live.has(take)||!give.subs.length||!take.subs.length)continue;
  if((give.leaving||take.leaving)&&l.retireAt===undefined){l.retireLevel=a2LoanLevel(l,this.t);l.retireAt=this.t;}
  const credit=Math.min(give.subs[0].claim*.22,l.maxCredit)*a2LoanLevel(l,this.t);
  for(const s of give.subs)s.claim-=credit;for(const s of take.subs)s.claim+=credit;
  this.a2LoanCredit+=credit;
 }
};
const a2SetSize=Hive.prototype.setSize;
Hive.prototype.setSize=function(W,H){
 const ox=this.W,oy=this.H;
 a2SetSize.call(this,W,H);
 if(this.depth!==0||!(ox>0&&oy>0))return;
 const sx=W/ox,sy=H/oy;
 for(const b of this.bodies){if(b.a2Morph){b.a2Morph.pairs=b.a2Morph.pairs.map(pair=>pair.map(p=>[p[0]*sx,p[1]*sy]));b.a2Morph.source=b.a2Morph.source.map(p=>[p[0]*sx,p[1]*sy]);}}
 for(const l of this.a2Loans||[]){l.shift*=l.n[0]?sx:sy;}
 this.astraRestKey=null;
};
