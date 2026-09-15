// A scene is planned in space-time. Routes are then followed analytically,
// rather than letting an independent spring undo every avoidance correction.
const a3S5=u=>u<=0?0:u>=1?1:u*u*u*(10+u*(-15+6*u));
function a3Curve(p,t){
 const u=Math.max(0,Math.min(1,(t-p.start)/p.duration)),q=a3S5(u),v=u-6*u**3+8*u**4-3*u**5;
 const f=64*u**3*(1-u)**3;
 return [p.sx+(p.ex-p.sx)*q+p.vx*p.duration*v+p.bx*f,p.sy+(p.ey-p.sy)*q+p.vy*p.duration*v+p.by*f];
}
function a3Plan(h){
 const bs=h.bodies.filter(b=>b.journey&&b.journey.t0===h.t&&!b.isSelf);
 let total=bs.reduce((s,b)=>s+b.claim,0),V=h.W*h.H;
 for(const b of bs){const j=b.journey;let end=b.path?[b.path.ex,b.path.ey]:[b.x+(h.W/2-b.x)*.16,b.y+(h.H/2-b.y)*.16];
  const D=Math.hypot(end[0]-b.x,end[1]-b.y),d=Math.max(1.5,j.dur),delay=Math.min(.65,j.delay||0);
  const p={sx:b.x,sy:b.y,ex:end[0],ey:end[1],vx:b.vx,vy:b.vy,bx:0,by:0,start:h.t+delay,duration:d,r:.55*Math.sqrt(Math.max(.1,b.claim)*V/total/Math.PI),length:D};
  // Already moving bodies do not stop to wait when a transition is interrupted.
  if(Math.hypot(p.vx,p.vy)>.01)p.start=h.t;
  b.a3Path=p;j.hold=0;j.delay=p.start-h.t;j.dur=d;
 }
 const moving=bs.filter(b=>!b.isVoid&&!b.leaving&&b.a3Path.length>12);
 // Shared circulation sign, with alternatives evaluated against all current
 // plans, including waiting participants. The cost does not prove collision freedom.
 const points=(p,bend)=>{const D=Math.hypot(p.ex-p.sx,p.ey-p.sy)||1;return { ...p,bx:-(p.ey-p.sy)/D*bend,by:(p.ex-p.sx)/D*bend};};
 const cost=(b,p)=>{let c=.025*(p.bx*p.bx+p.by*p.by);
  const duration=p.duration+Math.max(0,p.start-h.t);
  for(let k=0;k<=20;k++){const t=h.t+duration*k/20,[x,y]=a3Curve(p,t);
   const margin=60;const out=Math.max(0,-margin-x,x-h.W-margin,-margin-y,y-h.H-margin);c+=10*out*out;
   for(const other of h.bodies){if(other===b||other.leaving||other.isVoid)continue;const op=other.a3Path,[ox,oy]=op?a3Curve(op,t):[other.x,other.y];
    const R=p.r+(op?op.r:.55*Math.sqrt(Math.max(1,other.paintArea)/Math.PI));
    const depth=Math.max(0,R-Math.hypot(x-ox,y-oy));c+=depth*depth;
   }
  }return c;
 };
 for(let pass=0;pass<2;pass++)for(const b of moving){const p=b.a3Path,D=p.length;
  const sign=h.swirlSign||1,bow=Math.min(150,.25*D)*(config.swirl/.45);
  const options=window.__ASTRA_III_OPTIONS?.arcs===false?[0]:[0,sign*bow,sign*bow*1.5,-sign*bow*.65];let best=p,bc=cost(b,p);
  for(const bend of options){const q=points(p,bend),c=cost(b,q);if(c<bc){best=q;bc=c;}}
  b.a3Path=best;
 }
 h.a3PlanLog=moving.map(b=>({id:b.id,bend:Math.hypot(b.a3Path.bx,b.a3Path.by),distance:b.a3Path.length}));
}
function a3CurveVelocity(p,t){const u=Math.max(0,Math.min(1,(t-p.start)/p.duration));if(t<p.start||u>=1)return [0,0];const dq=30*u*u*(1-u)*(1-u)/p.duration,dv=1-18*u*u+32*u**3-15*u**4,df=192*u*u*(1-u)*(1-u)*(1-2*u)/p.duration;return [(p.ex-p.sx)*dq+p.vx*dv+p.bx*df,(p.ey-p.sy)*dq+p.vy*dv+p.by*df];}
const a3OldScene=Hive.prototype.enterScene;
Hive.prototype.enterScene=function(...args){
 a3OldScene.apply(this,args);if(this.depth===0)a3Plan(this);
};
const a3OldSteer=Hive.prototype.steer;
Hive.prototype.steer=function(dt,t){
 if(this.depth!==0)return a3OldSteer.call(this,dt,t);
 // The old free-drift behaviour remains only when no arranged journey exists.
 const free=this.bodies.filter(b=>!b.a3Path),all=this.bodies;
 this.bodies=free;a3OldSteer.call(this,dt,t);this.bodies=all;
 for(const b of all){const p=b.a3Path;if(!p)continue;
  const u=Math.max(0,Math.min(1,(t-p.start)/p.duration));b.progress=a3S5(u);this.updateCrystal(b,t);
  const [x,y]=a3Curve(p,t),[vx,vy]=a3CurveVelocity(p,t);
  b.x=x;b.y=y;b.vx=vx;b.vy=vy;
  if(u>=1){b.vx=b.vy=0;if(!b.rect&&!b.leaving){b.a3Path=null;b.journey=null;b.anchorX=b.x;b.anchorY=b.y;}}
 }
};
const a3OldSeparate=Hive.prototype.separate;
Hive.prototype.separate=function(dt){if(this.depth!==0)return a3OldSeparate.call(this,dt);if(!this.bodies.some(b=>b.a3Path))return a3OldSeparate.call(this,dt);};
const a3OldPre=Hive.prototype.enforcePreconditions;
Hive.prototype.enforcePreconditions=function(dt){if(this.depth!==0)return a3OldPre.call(this,dt);if(!this.bodies.some(b=>b.a3Path))return a3OldPre.call(this,dt);};
const a3OldSize=Hive.prototype.setSize;
Hive.prototype.setSize=function(W,H){
 const oldW=this.W,oldH=this.H;a3OldSize.call(this,W,H);if(this.depth!==0||!(oldW>0&&oldH>0))return;
 const sx=W/oldW,sy=H/oldH;
 for(const b of this.bodies){for(const key of ['a3Box','a3SourceBox'])if(b[key])b[key]=[b[key][0]*sx,b[key][1]*sy];
  const p=b.a3Path;if(p){for(const k of ['sx','ex','vx','bx'])p[k]*=sx;for(const k of ['sy','ey','vy','by'])p[k]*=sy;p.r*=Math.sqrt(sx*sy);p.length=Math.hypot(p.ex-p.sx,p.ey-p.sy);}
 }
 for(const l of this.a3Loans||[])l.amount*=sx*sy;
 this.a3BufferMargin=Math.min(130,.23*Math.min(W,H));this.a3ReserveWeight=(this.a3ReserveWeight||0)*sx*sy;
};
