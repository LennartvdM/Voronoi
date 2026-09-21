const assert=require('node:assert/strict');
const area=p=>Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-a[1]*b[0];},0)/2);
function clip(p,axis,value,sign){const out=[];for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length],da=sign*(a[axis]-value),db=sign*(b[axis]-value);if(da>=0)out.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);out.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);}}return out;}
function rectangleError(h){let sum=0,total=0;for(const b of h.bodies){if(!b.isVoid||b.leaving||!b.rect)continue;const r=b.rect.map((x,i)=>x*(i%2?h.PH:h.PW)),target=(r[2]-r[0])*(r[3]-r[1]);let owned=0,inside=0;
 h.solvedSubs.forEach((s,i)=>{if(s.body!==b)return;const cell=h.solved.diagram.cells[i];for(const pc of cell.pieces||[cell]){owned+=area(pc.pts);let p=pc.pts;for(const [axis,v,sign]of[[0,r[0],1],[0,r[2],-1],[1,r[1],1],[1,r[3],-1]])p=clip(p,axis,v,sign);inside+=area(p);}});sum+=Math.max(0,owned+target-2*inside);total+=target;}return total?100*sum/total:null;}
function check(h){assert.equal(h.walls.length,0);assert.equal(h.holes.length,0);for(const b of h.bodies){if(b.isVoid||b.isSelf||b.leaving)continue;assert.equal(b.subs.length,1);assert(b.loops?.length,'missing cell');assert([b.x,b.y,b.claim,b.progress].every(Number.isFinite));for(const p of b.loops)for(const q of p)assert(q.every(Number.isFinite));}}

module.exports={rectangleError,check};
