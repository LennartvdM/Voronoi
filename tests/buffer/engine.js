// True buffer: one permanent larger world, with the viewport only a crop.
// The exterior reserve owns the ring at rest. A local route borrows absolute
// area from that reserve; unused capacity never inflates every visible quota.
const bfParams=new URLSearchParams(location.search);
const BUFFER_SETTINGS = Object.assign({width: 120, cascade: bfParams.get('cascade')!=='off', locked: bfParams.get('reserve')==='locked', capacity: .4}, window.BUFFER_OPTIONS || {});
if(bfParams.has('width'))BUFFER_SETTINGS.width=Number(bfParams.get('width'));
if(bfParams.has('capacity'))BUFFER_SETTINGS.capacity=Number(bfParams.get('capacity'));
BUFFER_SETTINGS.width=Number.isFinite(BUFFER_SETTINGS.width)?Math.max(0,Math.min(260,BUFFER_SETTINGS.width)):120;
BUFFER_SETTINGS.capacity=Number.isFinite(BUFFER_SETTINGS.capacity)?Math.max(0,Math.min(.75,BUFFER_SETTINGS.capacity)):.4;
function bfMargin(h) { return Math.min(BUFFER_SETTINGS.width, .22*Math.min(h.W,h.H)); }
function bfBounds(h) { const b=bfMargin(h); return [[-b,-b],[h.W+b,-b],[h.W+b,h.H+b],[-b,h.H+b]]; }
function bfClip(poly, r) {
  let p=poly;
  for(const [a,b,c] of [[-1,0,-r[0]],[1,0,r[2]],[0,-1,-r[1]],[0,1,r[3]]]) {
    if(p.pts.length<3)return {pts:[],labs:[]};
    p=clipHalfPlane(p,a,b,c,-901);
  }
  return p;
}
function bfAmount(poly){return poly.pts.length<3?0:Math.abs(ringArea(poly.pts));}
// The contact graph uses real shared edges, including those in the ring.
// Routes are chosen once, not re-decided for every small frame correction.
function bfRoutes(h) {
 h.bufferRoutes=[]; if(!bfMargin(h)||!h.bufferWorld)return;
 const w=h.bufferWorld,graph=new Map(h.bodies.map(b=>[b,new Set()]));
 w.cells.forEach((c,i)=>{for(const pc of c.pieces||[c])for(const j of pc.labs)if(j>=0&&w.bodies[j]!==w.bodies[i]&&graph.has(w.bodies[j]))graph.get(w.bodies[i])?.add(w.bodies[j]);});
 const content=h.bodies.filter(b=>!b.isVoid&&!b.leaving&&b.path&&b.progress<1);
 const border=b=>b.loops&&b.loops.some(lp=>lp.some(p=>p[0]<2||p[1]<2||p[0]>h.W-2||p[1]>h.H-2));
 const candidates=[];
 for(const taker of content) {
  if(Math.hypot(taker.path.ex-taker.x,taker.path.ey-taker.y)<50)continue;
  for(const blocker of graph.get(taker)||[]) {
   if(blocker.isVoid||blocker.leaving||!blocker.path)continue;
   const occupied=a2Intersection(h,blocker,taker.rect||[0,0,0,0]);
   if(occupied<.08*Math.min(taker.paintArea,blocker.paintArea))continue;
   const queue=[[blocker]],seen=new Set([taker,blocker]);let route=null;
   while(queue.length){const path=queue.shift(),b=path[path.length-1];if(border(b)){route=path;break;}if(path.length>=5)continue;
    const ns=[...(graph.get(b)||[])].filter(n=>!seen.has(n)&&!n.leaving&&!n.isVoid&&n.path);
    ns.sort((a,b)=>Math.min(a.x,a.y,h.W-a.x,h.H-a.y)-Math.min(b.x,b.y,h.W-b.x,h.H-b.y));
    for(const n of ns){seen.add(n);queue.push([...path,n]);}
   }
   if(route)candidates.push({taker,route,score:occupied/(1+.3*route.length)});
  }
 }
 candidates.sort((a,b)=>b.score-a.score);const used=new Set();
 for(const c of candidates) {
  if(h.bufferRoutes.length>=2)break;
  if(c.route.some(b=>used.has(b))||used.has(c.taker))continue;
  const last=c.route[c.route.length-1];
  const normals=[[last.x,[-1,0]],[h.W-last.x,[1,0]],[last.y,[0,-1]],[h.H-last.y,[0,1]]].sort((a,b)=>a[0]-b[0]);
  const normal=normals[0][1], amplitude=.65*bfMargin(h);
  const end=Math.max(...[c.taker,...c.route].map(b=>b.journey.t0+b.journey.delay+b.journey.dur));
  const start=h.t, duration=Math.max(.8,end-start);
  const nodes=c.route.map((b,i)=>{const next=c.route[i+1];let dx=next?next.x-b.x:normal[0],dy=next?next.y-b.y:normal[1],d=Math.hypot(dx,dy)||1;
   return {b,v:[dx/d,dy/d],delay:(c.route.length-1-i)*.06,amplitude:amplitude*(.75+.25*(i+1)/c.route.length)};});
  h.bufferRoutes.push({taker:c.taker,nodes,start,duration});for(const b of [...c.route,c.taker])used.add(b);
 }
 h.bufferRouteHistory=(h.bufferRouteHistory||[]).concat(h.bufferRoutes.map(r=>({scene:h.scene,start:r.start,ids:[r.taker.id,...r.nodes.map(n=>n.b.id)]})));
}
function bfLevel(r,t) {
 if(r.retireAt!==undefined)return r.retireLevel*(1-S3((t-r.retireAt)/.45));
 const u=Math.min(1,Math.max(0,(t-r.start)/r.duration));return 64*u*u*u*(1-u)*(1-u)*(1-u);
}
const bfScene= a2SpillScene;
Hive.prototype.enterScene=function(name,origin) {
 if(this.depth!==0)return bfScene.call(this,name,origin);
 const retiring=(this.bufferRoutes||[]).filter(r=>bfLevel(r,this.t)>1e-7);
 for(const r of retiring){r.retireLevel=bfLevel(r,this.t);r.retireAt=this.t;r.motionRetired=true;}
 bfScene.call(this,name,origin);this.a2CanReview=!!this.solved;this.a2Loans=[];
 bfRoutes(this);this.bufferRoutes=retiring.concat(this.bufferRoutes);
 for(const r of this.bufferRoutes)for(const b of [r.taker,...r.nodes.map(n=>n.b)])b.bufferReservedUntil=r.start+r.duration;
 
};
// Preserve Astra II's formation and contact handling; replace its simulated
// outside allowance with a genuine exterior partition and reserve account.
Hive.prototype.placeSeeds=a2SpillPlace;
a2ExternalCarrot=function(h,b,t) {
 if(h.depth!==0||!BUFFER_SETTINGS.cascade)return [0,0];let x=0,y=0;
 for(const r of h.bufferRoutes||[])if(!r.motionRetired)for(const n of r.nodes)if(n.b===b){
  const u=Math.min(1,Math.max(0,(t-r.start-n.delay)/Math.max(.6,r.duration-n.delay)));
  const f=(r.retireAt!==undefined?bfLevel(r,t):64*u*u*u*(1-u)*(1-u)*(1-u))*n.amplitude;
  x+=n.v[0]*f;y+=n.v[1]*f;
 }
 return [x,y];
};
Hive.prototype.enforcePreconditions=function(dt) {
 if(this.depth!==0)return a2SpillPre.call(this,dt);
 const B=bfMargin(this);
 for(const b of this.bodies){b.x=Math.max(-B+SEED_MARGIN,Math.min(this.W+B-SEED_MARGIN,b.x));b.y=Math.max(-B+SEED_MARGIN,Math.min(this.H+B-SEED_MARGIN,b.y));}
 for(let i=0;i<this.bodies.length;i++)for(let j=i+1;j<this.bodies.length;j++){
  const a=this.bodies[i],b=this.bodies[j];let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);
  if(d<SEED_MIN_SEP){if(d<1e-9){dx=1;dy=0;d=1;}const k=(SEED_MIN_SEP-d)/(2*d);a.x-=dx*k;a.y-=dy*k;b.x+=dx*k;b.y+=dy*k;}
 }
};

function bfRing(h) {
 const B=bfMargin(h),W=h.W,H=h.H;
 const rects=[[-B,-B,W+B,0],[-B,H,W+B,H+B],[-B,0,0,H],[W,0,W+B,H]];
 return rects.map(r=>[[r[0],r[1]],[r[2],r[1]],[r[2],r[3]],[r[0],r[3]]]);
}
function bfWorldDiagram(h,seeds,weights,contentSites) {
 // The same content lower envelope exists on both sides of the crop.
 // Exterior reserve sites compete only in the ring. They can never make
 // a visible hole. Clip their half-planes against content cells once.
 const B=bfMargin(h),W=h.W,H=h.H,ringArea=(W+2*B)*(H+2*B)-W*H;
 const raw=computeDiagram(seeds.slice(0,contentSites),weights.slice(0,contentSites),bfBounds(h));
 const rects=bfRing(h).map(r=>[r[0][0],r[0][1],r[2][0],r[2][1]]);
 const innerCells=raw.cells.map(c=>bfClip(c,[0,0,W,H]));
 const inner={cells:innerCells,areas:Float64Array.from(innerCells,bfAmount)};
 const exterior=[],extAreas=new Float64Array(seeds.length),areas=new Float64Array(seeds.length),cells=[];
 let stored=0;
 for(let i=0;i<contentSites;i++){
  let c=raw.cells[i];const [x,y]=seeds[i],pot=x*x+y*y-weights[i];
  for(let j=contentSites;j<seeds.length&&c.pts.length>=3;j++){
   const [rx,ry]=seeds[j];c=clipHalfPlane(c,rx-x,ry-y,(rx*rx+ry*ry-weights[j]-pot)/2,j);
  }
  const pieces=c.pts.length>=3?rects.map(r=>bfClip(c,r)).filter(c=>c.pts.length>=3):[];
  const a=pieces.reduce((a,p)=>a+bfAmount(p),0);
  exterior.push({pts:[],labs:[],pieces});extAreas[i]=a;stored+=a;areas[i]=a+inner.areas[i];
  cells.push({pts:[],labs:[],pieces:pieces.concat(inner.cells[i].pts.length>=3?[inner.cells[i]]:[])});
 }
 // Reserve is the exact geometric complement of these disjoint exterior
 // polygons. Its boundary Jacobian is supplied by the opposite content edge.
 for(let j=contentSites;j<seeds.length;j++){cells.push({pts:[],labs:[],pieces:[]});exterior.push({pts:[],labs:[],pieces:[]});}
 extAreas[contentSites]=areas[contentSites]=Math.max(0,ringArea-stored);
 return {cells,areas,inner,outer:{cells:exterior,areas:extAreas}};
}
function bfReserveSolve(h, seeds, owner, targets, w0, contentSites, maxIter = 28) {
  const n = targets.length, area = Math.abs(ringArea(bfBounds(h)));
  const sum = targets.reduce((a, b) => a + b, 0);
  const target = targets.map(a => a * area / sum);
  let w = Float64Array.from(w0), evaluations = 0;
  const evaluate = ws => {
    const diagram = bfWorldDiagram(h,seeds,owner.map(i=>ws[i]),contentSites);
    const areas = new Float64Array(n);
    diagram.areas.forEach((a, i) => { areas[owner[i]] += a; });
    evaluations++;
    return { diagram, areas };
  };
  let current = evaluate(w);
  // A whole body, rather than an individual lattice site, must stay alive.
  for (let pass = 0; pass < 3 && minOf(current.areas) <= 0; pass++) {
    for (let i = 0; i < n; i++) {
      if (current.areas[i] > 0) continue;
      let lo = -8 * area - Math.max(...Array.from(w, Math.abs));
      let hi = -lo;
      for (let k = 0; k < 36; k++) {
        const mid = (lo + hi) / 2; w[i] = mid;
        if (evaluate(w).areas[i] < target[i]) lo = mid; else hi = mid;
      }
      w[i] = (lo + hi) / 2;
      current = evaluate(w);
    }
  }
  // The reserve can temporarily win the entire ring. Then no active
  // content/reserve edge exists and Newton cannot see the direction that
  // opens capacity. Seed that contact monotonically, just as an empty body
  // is revived above, and retain a positive exterior share during line search.
  const ring = area - h.W*h.H, requestedOutside = ring-target[n-1];
  if(requestedOutside>1e-8 && ring-current.areas[n-1]<1e-6) {
    let lo=w[n-1]-8*area-Math.max(...Array.from(w,Math.abs)),hi=w[n-1];
    for(let k=0;k<36;k++){
      const mid=(lo+hi)/2;w[n-1]=mid;
      if(evaluate(w).areas[n-1]<target[n-1])lo=mid;else hi=mid;
    }
    w[n-1]=(lo+hi)/2;current=evaluate(w);
  }
  const outsideFloor=.5*Math.min(Math.max(0,requestedOutside),Math.max(0,ring-current.areas[n-1]));
  const floor = .5 * Math.min(minOf(target), minOf(current.areas));
  let iterations = 0, maxRel = Infinity;
  for (; iterations < maxIter; iterations++) {
    const residual = target.map((a, i) => a - current.areas[i]);
    maxRel = Math.max(...residual.map((a, i) => Math.abs(a) / target[i]));
    if (maxRel <= 1e-6) break;
    const J = Array.from({length:n}, () => new Float64Array(n));
    current.diagram.cells.forEach((c, i) => {
      const a = owner[i];
      for(const pc of c.pieces||[c]) for (let k = 0; k < pc.pts.length; k++) {
        const j = pc.labs[k];
        if (j < 0 || owner[j] === a) continue;
        const p = pc.pts[k], q = pc.pts[(k + 1) % pc.pts.length];
        const d = Math.hypot(seeds[i][0] - seeds[j][0], seeds[i][1] - seeds[j][1]);
        if (d > 1e-9) J[a][owner[j]] -= Math.hypot(q[0] - p[0], q[1] - p[1]) / (2 * d);
      }
    });
    for(let i=0;i<n-1;i++)J[n-1][i]=J[i][n-1];
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) J[i][j] = J[j][i] = .5 * (J[i][j] + J[j][i]);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== j) J[i][i] -= J[i][j];
    const dw = solvePinned(J, residual), norm = norm2(residual);
    let accepted = false;
    for (let t = 1, k = 0; k < 35; k++, t /= 2) {
      const nextW = Float64Array.from(w, (x, i) => x + t * dw[i]);
      if (!nextW.every(Number.isFinite)) break;
      const next = evaluate(nextW);
      if (minOf(next.areas) >= floor && ring-next.areas[n-1]>=outsideFloor && norm2(target.map((x, i) => x - next.areas[i])) <= (1 - t / 2) * norm) {
        w = nextW; current = next; accepted = true; break;
      }
    }
    if (!accepted) break;
  }
  maxRel = Math.max(...target.map((a, i) => Math.abs(a-current.areas[i])/a));
  const mean = w.reduce((a,b)=>a+b,0) / n;
  w = w.map(x=>x-mean);
  return {weights: owner.map(i=>w[i]), groupWeights:w, diagram:current.diagram,
    maxRelErr:maxRel, converged:maxRel<=1e-6, iterations, evals:evaluations};
}


const bfSolve=Hive.prototype.solve;
Hive.prototype.solve=function() {
 if(this.depth!==0)return bfSolve.call(this);
 const B=bfMargin(this),V=this.W*this.H,world=(this.W+2*B)*(this.H+2*B),ring=world-V;
 const groups=this.bodies.filter(b=>b.subs.length&&b.claim>=ACTIVE_MIN);
 if(!groups.length)return bfSolve.call(this);
 const subs=groups.flatMap(b=>b.subs),indices=new Map(groups.map((b,i)=>[b,i]));
 const owner=subs.map(s=>indices.get(s.body)),seeds=subs.map(s=>[s.x,s.y]);
 const raw=groups.map(b=>b.subs[0].claim),sum=raw.reduce((a,b)=>a+b,0);
 const claims=raw.map(a=>a*V/sum),quota=claims.slice();
 let credit=0;this.bufferAllocations=[];
 for(const r of this.bufferRoutes||[]) {
  const receiver=indices.get(r.taker),donor=indices.get(r.nodes[r.nodes.length-1].b);
  if(receiver===undefined||donor===undefined)continue;
  const level=bfLevel(r,this.t);
  const amount=BUFFER_SETTINGS.locked?0:Math.min(BUFFER_SETTINGS.capacity*claims[donor],.12*V)*level;
  quota[receiver]+=amount;credit+=amount;this.bufferAllocations.push({receiver:groups[receiver].id,exit:groups[donor].id,amount,depth:r.nodes.length});
 }
 // Standalone reservoir control: no cascade still grants the same potential
 // liquidity to the same selected routes, but supplies no steering impulse.
 if(credit>.6*ring){const k=.6*ring/credit;for(let i=0;i<quota.length;i++)quota[i]=claims[i]+k*(quota[i]-claims[i]);for(const allocation of this.bufferAllocations)allocation.amount*=k;credit=.6*ring;}
 this.bufferCredit=credit;this.bufferBaseQuotas=new Map(groups.map((b,i)=>[b,claims[i]]));this.bufferTargetQuotas=new Map(groups.map((b,i)=>[b,quota[i]]));
 const allSeated=credit<.05&&groups.every(b=>b.rect&&b.formRect===b.rect&&b.crystal===1&&!b.leaving&&(!b.a2Scale||b.a2Scale.every(x=>x===1)));
 let sol;const t0=performance.now();
 if(B<=0||credit<.05||allSeated) {
  const viewport=[[0,0],[this.W,0],[this.W,this.H],[0,this.H]];
  if(allSeated){
   const key=[this.W,this.H,this.serial,...groups.map(b=>b.id)].join(',');
   if(this.bufferRestKey===key&&this.bufferRestSol)sol=this.bufferRestSol;
   else {const weights=seeds.map(()=>0);sol={weights,diagram:computeDiagram(seeds,weights,viewport),maxRelErr:0,iterations:0,converged:true};}
   this.bufferRestKey=key;this.bufferRestSol=sol;
  } else {this.bufferRestKey=null;sol=astraGroupSolve(seeds,owner,claims,groups.map(b=>b.subs[0].w),viewport,22);}
  this.bufferWorld={cells:sol.diagram.cells.map(c=>({...c,pieces:[c]})),bodies:subs.map(s=>s.body),bounds:bfBounds(this),reserve:bfRing(this),world};
  this.bufferReserveWeight=null;this.bufferStorage=new Map(groups.map(b=>[b,{total:0,visible:0,outside:0}]));
  subs.forEach((s,i)=>{const a=this.bufferStorage.get(s.body);a.total+=sol.diagram.areas[i];a.visible+=sol.diagram.areas[i];});
  this.bufferReserveArea=ring;this.bufferActualOutside=0;
 } else {
  this.bufferRestKey=null;
  const W=this.W,H=this.H,n=groups.length;
  const rs=[[-B*.5,-B*.5],[W*.5,-B*.5],[W+B*.5,-B*.5],[W+B*.5,H*.5],[W+B*.5,H+B*.5],[W*.5,H+B*.5],[-B*.5,H+B*.5],[-B*.5,H*.5]];
  const S=seeds.concat(rs),O=owner.concat(rs.map(()=>n));
  const Q=quota.concat([ring-credit]),w0=groups.map(b=>b.subs[0].w).concat([this.bufferReserveWeight||0]);
  const full=bfReserveSolve(this,S,O,Q,w0,subs.length);
  this.bufferReserveWeight=full.groupWeights[n];
  sol={...full,weights:full.weights.slice(0,subs.length),diagram:full.diagram.inner};
  this.bufferWorld={cells:full.diagram.cells,bodies:subs.map(s=>s.body).concat(rs.map(()=>null)),bounds:bfBounds(this),world};
  this.bufferStorage=new Map(groups.map(b=>[b,{total:0,visible:0,outside:0}]));
  subs.forEach((s,i)=>{const a=this.bufferStorage.get(s.body);a.total+=full.diagram.areas[i];a.visible+=full.diagram.inner.areas[i];a.outside+=full.diagram.outer.areas[i];});
  this.bufferReserveArea=full.diagram.areas.slice(subs.length).reduce((a,b)=>a+b,0);
  this.bufferActualOutside=[...this.bufferStorage.values()].reduce((s,a)=>s+a.outside,0);
 }
 this.bufferContentOutside=[...this.bufferStorage].reduce((s,[b,a])=>s+(b.isVoid?0:a.outside),0);
 this.bufferVoidOutside=this.bufferActualOutside-this.bufferContentOutside;
 this.bufferQuotaError=Math.max(...[...this.bufferStorage].map(([b,a])=>Math.abs(a.total-(this.bufferTargetQuotas.get(b)||0))));
 this.bufferLedgerError=Math.abs([...this.bufferStorage.values()].reduce((s,a)=>s+a.total,0)+this.bufferReserveArea-world);
 this.bufferVisibleError=Math.abs(sol.diagram.areas.reduce((a,b)=>a+b,0)-V);
 this.solved=sol;this.solvedSubs=subs;this.ownerOf=subs.map(s=>s.body.id);this.lastIters=sol.iterations;this.solveMs=performance.now()-t0;
 subs.forEach((s,i)=>{s.w=sol.weights[i];});
 this.shadowOn=false;this.shadowAt=null;this.ground=null;this.exact=true;
 this.walls=[];for(const b of this.bodies)b.wall=null;
 if(allSeated){this.walls=groups;for(const b of groups)b.wall=[b.rect[0]*this.PW,b.rect[1]*this.PH,b.rect[2]*this.PW,b.rect[3]*this.PH];}
 this.recordAreas();
};

const bfSetSize=Hive.prototype.setSize;
Hive.prototype.setSize=function(W,H){
 const ox=this.W,oy=this.H,oldB=bfMargin(this);bfSetSize.call(this,W,H);
 if(this.depth!==0||!(ox>0&&oy>0))return;
 const k=oldB?bfMargin(this)/oldB:1;
 for(const r of this.bufferRoutes||[])for(const n of r.nodes)n.amplitude*=k;
 this.bufferReserveWeight=null;this.bufferWorld=null;
};
