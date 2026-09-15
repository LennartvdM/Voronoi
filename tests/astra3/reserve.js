// Capacity is committed to the coordinated plan, not conjured by enlarging
// every target. At rest the entire exterior belongs to a non-visible reserve.
const a3PlanBase=a3Plan;
a3Plan=function(h){
 const retiring=(h.a3Loans||[]).map(l=>({...l,amount:a3LoanValue(l,h.t),start:h.t,duration:.4,retiring:true})).filter(l=>l.amount>.01);
 a3PlanBase(h);const B=Math.min(130,.23*Math.min(h.W,h.H)),plans=[];
 for(const b of h.bodies){const p=b.a3Path;if(!p||b.leaving||b.isVoid||p.length<25)continue;
  let maxOutside=0;
  const src=b.a3SourceBox||a3Box(h,b),r=b.rect,target=r?[(r[2]-r[0])*h.PW/2,(r[3]-r[1])*h.PH/2]:[0,0];
  for(let k=1;k<24;k++){const u=k/24,q=a3S5(u),[x,y]=a3Curve(p,p.start+u*p.duration),hx=src[0]+q*(target[0]-src[0]),hy=src[1]+q*(target[1]-src[1]);
   const visible=Math.max(0,Math.min(h.W,x+hx)-Math.max(0,x-hx))*Math.max(0,Math.min(h.H,y+hy)-Math.max(0,y-hy));
   maxOutside=Math.max(maxOutside,4*hx*hy-visible);
  }
  if(maxOutside<200)continue;
  let receiver=null,best=-Infinity;
  for(const q of h.bodies){if(q===b||q.isVoid||q.leaving)continue;const d=Math.hypot(q.x-b.x,q.y-b.y),growth=Math.max(0,q.claimTarget-q.claim0);const score=(1+growth)/(50+d);if(score>best){best=score;receiver=q;}}
  if(receiver)plans.push({exit:b,receiver,start:p.start,duration:p.duration,amount:Math.min(maxOutside*.7,h.W*h.H*.055)});
 }
 plans.sort((a,b)=>b.amount-a.amount);h.a3Loans=retiring.concat(plans.slice(0,3));h.a3BufferMargin=B;
};
function a3LoanValue(l,t){const u=Math.max(0,Math.min(1,(t-l.start)/l.duration));return l.amount*(l.retiring?1-a3S5(u):64*u**3*(1-u)**3);}
function a3Credit(h){
 const credit=new Map();let total=0;if(window.__ASTRA_III_OPTIONS?.buffer===false)return {credit,total};
 for(const l of h.a3Loans||[]){if(!h.bodies.includes(l.receiver)||!l.receiver.subs.length||l.receiver.subs[0].claim<ACTIVE_MIN)continue;const amount=a3LoanValue(l,h.t);credit.set(l.receiver,(credit.get(l.receiver)||0)+amount);total+=amount;}
 return {credit,total};
}
function a3ClipViewport(pts,W,H){let p={pts,labs:pts.map(()=>-9)};for(const [x,y,v]of [[-1,0,0],[0,-1,0],[1,0,W],[0,1,H]]){if(p.pts.length<3)break;p=clipHalfPlane(p,x,y,v,-9);}return p.pts;}
const a3InnerSolve=Hive.prototype.solve;
Hive.prototype.solve=function(){
 if(this.depth!==0)return a3InnerSolve.call(this);
 const allowance=a3Credit(this);this.a3Credit=allowance.total;
 if(allowance.total<.1){a3InnerSolve.call(this);this.a3Storage=[];this.a3Outside=0;return;}
 const bs=this.bodies.filter(b=>b.subs[0].claim>=ACTIVE_MIN),sum=bs.reduce((a,b)=>a+b.subs[0].claim,0),V=this.W*this.H,B=this.a3BufferMargin;
 const shapes=a3Shapes(this,bs),target=bs.map(b=>b.subs[0].claim*V/sum+(allowance.credit.get(b)||0)),ring=(this.W+2*B)*(this.H+2*B)-V;
 const t0=performance.now(),full=a3Solve(this,shapes.concat({reserve:true,W:this.W,H:this.H,B}),target.concat(ring-allowance.total),bs.map(b=>b.subs[0].w).concat(this.a3ReserveWeight||0),B);
 this.a3ReserveWeight=full.weights[bs.length];this.a3World=full.diagram;
 this.solved={...full,weights:full.weights.slice(0,bs.length),diagram:{cells:full.diagram.cells.slice(0,bs.length),areas:full.diagram.areas.slice(0,bs.length)}};
 this.solvedSubs=bs.map(b=>b.subs[0]);this.ownerOf=bs.map(b=>b.id);this.solvedSubs.forEach((s,i)=>s.w=this.solved.weights[i]);
 this.a3SolvedShapes=shapes;this.lastIters=full.iterations;this.solveMs=performance.now()-t0;this.exact=true;this.shadowOn=false;this.shadowAt=null;this.ground=null;this.walls=[];this.holes=[];
 this.a3Storage=bs.map((b,i)=>{const c=full.diagram.cells[i];let visible=0;for(const l of c.a3Loops)visible+=Math.sign(ringArea(l.pts))*Math.abs(ringArea(a3ClipViewport(l.pts,this.W,this.H)));return {id:b.id,isVoid:b.isVoid,total:full.diagram.areas[i],visible,outside:full.diagram.areas[i]-visible};});
 this.a3Outside=this.a3Storage.reduce((a,b)=>a+b.outside,0);this.recordAreas();
};
