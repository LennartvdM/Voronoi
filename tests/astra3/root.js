function a3Shapes(h,bs){
 const shapes=bs.map(b=>({x:b.x,y:b.y,hx:b.a3Box[0],hy:b.a3Box[1],regularizer:b.a3Regularizer??1e-6}));
 // A newly born whitespace body can have the exact same support as its host.
 // Distinct finite-area participants require distinct distance fields.
 for(let pass=0;pass<3;pass++)for(let i=0;i<shapes.length;i++)for(let j=i+1;j<shapes.length;j++){
  const a=shapes[i],b=shapes[j];let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);
  if(d>=5||Math.abs(a.hx-b.hx)+Math.abs(a.hy-b.hy)>1)continue;
  if(d<1e-7){dx=1;dy=.618;d=Math.hypot(dx,dy);}
  const correction=(5-d)/d,wi=bs[i].isVoid?1:bs[j].isVoid?0:.5;
  a.x-=wi*dx*correction;a.y-=wi*dy*correction;b.x+=(1-wi)*dx*correction;b.y+=(1-wi)*dy*correction;
 }
 return shapes;
}
function a3Box(h,b){
 if(b.a3Box)return b.a3Box.slice();
 const r=b.formRect;return r?[(r[2]-r[0])*h.PW*.5*b.crystal,(r[3]-r[1])*h.PH*.5*b.crystal]:[0,0];
}
for(const name of ['seatBody','releaseBody','retireBody']){
 const old=Hive.prototype[name];
 Hive.prototype[name]=function(b,...args){
  if(this.depth!==0)return old.call(this,b,...args);
  const box=a3Box(this,b),j=b.journey;old.call(this,b,...args);
  if(b.journey!==j&&b.journey){b.journey.hold=0;b.a3SourceBox=box;b.a3Box=box;b.a3C0=b.journey.c0;}
 };
}
const a3OldCrystal=Hive.prototype.updateCrystal;
Hive.prototype.updateCrystal=function(b,t){
 if(this.depth!==0||!b.a3SourceBox||!b.journey)return a3OldCrystal.call(this,b,t);
 const q=b.progress,target=b.rect&&!b.leaving?1:0;
 b.crystal=Math.min(.999,(b.a3C0||0)*(1-q)+target*q);b.pin=target*S3((q-.85)/.15);
 if(q>=1){b.crystal=target;b.formRect=b.rect;}
};
const a3OldPlace=Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds=function(){
 if(this.depth!==0)return a3OldPlace.call(this);
 const known=new Set((this.solvedSubs||[]).map(s=>s.body)),oldShapes=this.a3SolvedShapes,oldWeights=this.solved?.weights;
 for(const b of this.bodies){
  const r=b.rect,target=r?[(r[2]-r[0])*this.PW*.5,(r[3]-r[1])*this.PH*.5]:[0,0];
  const q=b.progress,src=b.a3SourceBox||target;
  const p=b.a3Path,travel=p?p.length:0,change=Math.hypot(target[0]-src[0],target[1]-src[1]);
  const scale=(travel+2*change)/Math.max(1,Math.min(this.PW,this.PH));
  const relax=a3S5(Math.min(1,q*scale))*a3S5(Math.min(1,(1-q)*scale));
  b.a3Regularizer=1e-6+1e-4*relax;
  b.a3Box=[Math.max(0,src[0]+q*(target[0]-src[0])-.5*this.PW*relax),Math.max(0,src[1]+q*(target[1]-src[1])-.5*this.PH*relax)];
  let w=b.subs[0]?.w||0;
  if(!known.has(b)&&oldShapes&&oldWeights&&oldShapes.length===oldWeights.length){const mine={x:b.x,y:b.y,hx:b.a3Box[0],hy:b.a3Box[1],regularizer:b.a3Regularizer};let best=Infinity;for(let i=0;i<oldShapes.length;i++)best=Math.min(best,a3SupportCost(b.x,b.y,oldShapes[i])-oldWeights[i]);if(Number.isFinite(best))w=a3SupportCost(b.x,b.y,mine)-best;}
  const claim=Math.max(0,b.claim-(b.isVoid&&b.claim0<=CLAIM_MIN*1.01&&!b.leaving?CLAIM_MIN*(1-b.progress):0))*(1+(config.hoverBoost-1)*b.hoverMix*(1-b.crystal));
  b.subs=[{body:b,x:b.x,y:b.y,w,claim,live:true}];
 }
};
const a3OldSolve=Hive.prototype.solve;
Hive.prototype.solve=function(){
 if(this.depth!==0)return a3OldSolve.call(this);
 const bs=this.bodies.filter(b=>b.subs[0].claim>=ACTIVE_MIN),sum=bs.reduce((a,b)=>a+b.subs[0].claim,0);
 const t0=performance.now();
 const allSeated=bs.every(b=>b.rect&&b.formRect===b.rect&&b.crystal===1&&!b.leaving);
 if(allSeated){const cells=bs.map(b=>{const r=b.rect,pts=[[r[0]*this.PW,r[1]*this.PH],[r[2]*this.PW,r[1]*this.PH],[r[2]*this.PW,r[3]*this.PH],[r[0]*this.PW,r[3]*this.PH]],labs=pts.map(()=>-9);return {pts,labs,a3Loops:[{pts,labs}]};});
 this.solved={weights:bs.map(()=>0),diagram:{cells,areas:Float64Array.from(bs,b=>rectArea(b.rect)*this.PW*this.PH)},iterations:0,maxRelErr:0,converged:true};
 }else if(bs.every(b=>b.a3Box[0]<1e-6&&b.a3Box[1]<1e-6)){
 const factor=1.000001,sol=astraGroupSolve(bs.map(b=>[b.x,b.y]),bs.map((b,i)=>i),bs.map(b=>b.subs[0].claim),bs.map(b=>b.subs[0].w/factor),this.domainPts());
 sol.weights=sol.weights.map(w=>w*factor);for(const c of sol.diagram.cells)c.a3Loops=c.pts.length>=3?[{pts:c.pts,labs:c.labs}]:[];this.solved=sol;
 }else this.solved=a3Solve(this,a3Shapes(this,bs),bs.map(b=>b.subs[0].claim*this.W*this.H/sum),bs.map(b=>b.subs[0].w));
 this.solvedSubs=bs.map(b=>b.subs[0]);this.ownerOf=bs.map(b=>b.id);this.solvedSubs.forEach((s,i)=>s.w=this.solved.weights[i]);
 this.a3SolvedShapes=a3Shapes(this,bs);this.lastIters=this.solved.iterations;this.solveMs=performance.now()-t0;this.exact=true;this.shadowOn=false;this.shadowAt=null;this.ground=null;this.walls=[];this.holes=[];
 const seated=bs.every(b=>b.rect&&b.formRect===b.rect&&b.crystal===1&&!b.leaving);
 if(seated){this.walls=bs;for(const b of bs)b.wall=[b.rect[0]*this.PW,b.rect[1]*this.PH,b.rect[2]*this.PW,b.rect[3]*this.PH];}
 this.recordAreas();
};
const a3OldOutline=Hive.prototype.computeOutlines;
Hive.prototype.computeOutlines=function(){
 if(this.depth!==0||!this.solved?.diagram.cells[0]?.a3Loops)return a3OldOutline.call(this);
 for(const b of this.bodies){b.loops=[];b.holes=[];b.bigSeed=-1;}
 this.solved.diagram.cells.forEach((c,i)=>{const b=this.solvedSubs[i].body;b.loops=c.a3Loops.filter(l=>ringArea(l.pts)>0).map(l=>l.pts);b.holes=c.a3Loops.filter(l=>ringArea(l.pts)<0).map(l=>l.pts);b.bigSeed=i;});let axis=0,length=0;for(const b of this.bodies)for(const loop of b.loops)for(let i=0;i<loop.length;i++){const a=loop[i],c=loop[(i+1)%loop.length],dx=Math.abs(c[0]-a[0]),dy=Math.abs(c[1]-a[1]),l=Math.hypot(dx,dy);length+=l;if(Math.min(dx,dy)<.05)axis+=l;}this.rectPct=length?100*axis/length:100;
};

const a3OldHitAny=Hive.prototype.hitTestAny,a3OldHit=Hive.prototype.hitTest;
Hive.prototype.hitTestAny=function(x,y){if(this.depth!==0)return a3OldHitAny.call(this,x,y);if(x<0||y<0||x>this.W||y>this.H)return null;for(const b of this.bodies){let winding=0;for(const p of b.loops||[])if(pointInPolygon(x,y,p))winding++;for(const p of b.holes||[])if(pointInPolygon(x,y,p))winding--;if(winding>0)return b;}return null;};
Hive.prototype.hitTest=function(x,y){if(this.depth!==0)return a3OldHit.call(this,x,y);const b=this.hitTestAny(x,y);return b&&!b.isVoid?b.id:-1;};
// Nested fields occupy the largest component. Detached positive material is
// still owned by its parent, including islands inside a negative hole loop.
const a3OldCollect=Hive.prototype.collectLeaves;
Hive.prototype.collectLeaves=function(out,ox,oy,fade){const begin=out.length;a3OldCollect.call(this,out,ox,oy,fade);if(this.depth!==0||!this.solved)return;
 this.solved.diagram.cells.forEach((c,i)=>{const b=this.solvedSubs[i].body;if(!c.a3Components||c.a3Components.length<2||!b.hive||b.hive.dormant||!out.slice(begin).some(l=>l.path[0]?.body===b&&l.path.length>1))return;
  for(let k=out.length-1;k>=begin;k--)if(out[k].body===b&&out[k].path.length===1&&!out[k].labels)out.splice(k,1);
  const pieces=c.a3Components.slice(1).flat().map(p=>({pts:p.pts.map(v=>[v[0]+ox,v[1]+oy]),labs:p.labs}));if(pieces.length)out.push({path:[{hive:this,body:b}],body:b,color:b.color,hv:b.hoverMix,fade:fade*Math.max(0,Math.min(1,(b.claim-CLAIM_MIN)/.14)),isVoid:b.isVoid,labels:false,label:b.label??b.id+1,pieces,loops:null,touched:false});
 });
};
