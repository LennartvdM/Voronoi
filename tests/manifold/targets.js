// Rest targets only. The live auction, motion and one-site content bodies
// remain Selvedge's. No walls, copied content lattices or arrival gates.
function mfDecorate(content, vr, seeds, weights, W, H, C, R) {
  const bounds = [[0,0],[W,0],[W,H],[0,H]], n = content.length;
  const d = computeDiagram(seeds, weights, bounds);
  const PW = W/C, PH = H/R, cx=(vr[0]+vr[2])/2, cy=(vr[1]+vr[3])/2;
  const rows=content.map((r,i)=>{const q=r.slice();q.mfArea=d.areas[i]/(PW*PH);q.mfSeed=[seeds[i][0]/PW,seeds[i][1]/PH];return q;});
  const v=vr.slice();v.mfSites=[];
  for(let i=n;i<seeds.length;i++)if(d.areas[i]>1e-6)v.mfSites.push({x:seeds[i][0]/PW-cx,y:seeds[i][1]/PH-cy,q:d.areas[i]/(PW*PH)});
  v.mfKey=JSON.stringify(v.mfSites);
  return {content:rows,voids:[v]};
}

function mfFrame(C,R,n,W,H) {
  const PW=W/C,PH=H/R,vr=[2,1,C-2,R-1],even=n%2?n-1:n;
  let best=null;
  for(let nx=3;nx<=even;nx++){
    const ny=(even+4)/2-nx;if(ny<3)continue;
    const xs=[0,2,...Array.from({length:nx-3},(_,i)=>2+(C-4)*(i+1)/(nx-2)),C-2,C];
    const ys=[0,1,...Array.from({length:ny-3},(_,i)=>1+(R-2)*(i+1)/(ny-2)),R-1,R];
    const content=[],inside=[];let score=0;
    for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
      const r=[xs[x],ys[y],xs[x+1],ys[y+1]];
      if(x===0||x===nx-1||y===0||y===ny-1){content.push(r);score+=Math.log((r[2]-r[0])*PW/((r[3]-r[1])*PH))**2;}
      else inside.push(r);
    }
    if(!best||score<best.score)best={content,inside,score};
  }
  const bounds=[[0,0],[W,0],[W,H],[0,H]];
  let content,seeds,weights;
  if(best){
    content=best.content;
    const all=content.concat(best.inside);
    seeds=all.map(r=>[(r[0]+r[2])*PW/2,(r[1]+r[3])*PH/2]);
    weights=all.map(r=>((r[2]-r[0])*PW/2)**2+((r[3]-r[1])*PH/2)**2);
  }else{
    // Four ordinary cells can support the four sides of a rectangular void.
    // Their corner regions are organic cells; no invisible extra content.
    content=[[2,0,C-2,1],[C-2,1,C,R-1],[2,R-1,C-2,R],[0,1,2,R-1]];
    const all=content.concat([vr]);
    seeds=all.map(r=>[(r[0]+r[2])*PW/2,(r[1]+r[3])*PH/2]);
    const center=seeds[4];weights=content.map((r,i)=>{
      const p=i===0?[center[0],PH]:i===1?[(C-2)*PW,center[1]]:i===2?[center[0],(R-1)*PH]:[2*PW,center[1]];
      return (p[0]-seeds[i][0])**2+(p[1]-seeds[i][1])**2-(p[0]-center[0])**2-(p[1]-center[1])**2;
    }).concat([0]);
  }
  // Odd counts refine an outer corner without taking area from the void.
  // Quotas are read from this authored rest diagram, not fed back per frame.
  while(content.length<n){
    const k=content.length-(best?even:4),corners=[[0,0],[W,0],[W,H],[0,H]],c=corners[k%4];
    const x=c[0]===0?PW*.42:W-PW*.42,y=c[1]===0?PH*.24:H-PH*.24;
    const d=computeDiagram(seeds,weights,bounds);let cap=Infinity;
    for(let i=content.length;i<seeds.length;i++)for(const p of d.cells[i].pts){
      cap=Math.min(cap,2*(seeds[i][0]-x)*p[0]+2*(seeds[i][1]-y)*p[1]+x*x+y*y-seeds[i][0]**2-seeds[i][1]**2+weights[i]);
    }
    const w=Math.min(cap-.01,entryWeight(x,y,PW*PH*.45,seeds,weights,bounds,null,4*(W*W+H*H)));
    const i=content.length;
    content.push([c[0]===0?0:C-1,c[1]===0?0:R-1,c[0]===0?1:C,c[1]===0?1:R]);
    seeds.splice(i,0,[x,y]);weights.splice(i,0,w);
  }
  return mfDecorate(content,vr,seeds,weights,W,H,C,R);
}

function mfHero(C,R,n,W,H,old) {
  if(MF_TEMPLATE_HERO){
    const col=Math.max(1,Math.round(C*.22)),end=Math.round(C*.72);
    return {content:[[col,0,end,R],...Array.from({length:n-1},(_,i)=>[end,R*i/(n-1),C,R*(i+1)/(n-1)])],voids:[[0,0,col,R]]};
  }
  const spec=old(C,R,n);if(spec.content.length<n)return spec;
  const PW=W/C,PH=H/R,vr=spec.voids[0],edge=vr[2]*PW;
  const seeds=spec.content.map(r=>[(r[0]+r[2])*PW/2,(r[1]+r[3])*PH/2]);
  const claims=spec.content.map(r=>rectArea(r)*PW*PH),domain=[[edge,0],[W,0],[W,H],[edge,H]];
  const ref=solveWeights(seeds,claims,domain,null,{maxIter:60,tol:1e-9});
  const weights=[...ref.weights],extra=[];
  for(let i=0;i<seeds.length;i++){
    const cell=ref.diagram.cells[i];let touches=false;
    for(let j=0;j<cell.pts.length;j++){const p=cell.pts[j],q=cell.pts[(j+1)%cell.pts.length];if(Math.abs(p[0]-edge)<1e-5&&Math.abs(q[0]-edge)<1e-5&&Math.abs(p[1]-q[1])>1e-5)touches=true;}
    if(!touches)continue;
    const distance=seeds[i][0]-edge,g=Math.min(distance,edge*.45);
    extra.push([edge-g,seeds[i][1]]);weights.push(ref.weights[i]+g*g-distance*distance);
  }
  return mfDecorate(spec.content,vr,seeds.concat(extra),weights,W,H,C,R);
}

const mfOriginalHero=scenes.hero,mfCache=new Map();
function mfScene(h,name,n){
  const key=[name,h.COLS,h.ROWS,n,h.W,h.H].join('|');
  if(mfCache.has(key))return mfCache.get(key);
  const s=name==='frame'?mfFrame(h.COLS,h.ROWS,n,h.W,h.H):mfHero(h.COLS,h.ROWS,n,h.W,h.H,mfOriginalHero);
  for(const r of s.content.concat(s.voids))r.mfRest=true;
  mfCache.set(key,s);if(mfCache.size>24)mfCache.delete(mfCache.keys().next().value);return s;
}
