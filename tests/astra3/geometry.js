/* A compact continuous support rectangle replaces the oscillating lattice.
 * The lower envelope is integrated on a fixed, common triangular mesh.
 * Geometry is shared, not independently rounded or temporally interpolated.
 */
function a3SupportCost(x,y,s) {
  if(s.reserve){const d=Math.max(-x,x-s.W,-y,y-s.H,0);return (s.B-d)**2;}
  const dx=Math.abs(x-s.x)-s.hx,dy=Math.abs(y-s.y)-s.hy;
  const regularizer=(s.regularizer??1e-4)*((x-s.x)**2+(y-s.y)**2);
  if(dx<=0&&dy<=0){const d=Math.max(dx,dy);return -d*d+regularizer;}
  return Math.max(0,dx)**2+Math.max(0,dy)**2+regularizer;
}
function a3Field(h,shapes,spacing=20,B=0) {
  const innerNX=h.COLS*Math.max(1,Math.ceil(h.PW/spacing)),innerNY=h.ROWS*Math.max(1,Math.ceil(h.PH/spacing));
  const ringN=B>0?Math.max(1,Math.ceil(B/spacing)):0;
  const axis=(L,N)=>{const a=[];for(let k=0;k<ringN;k++)a.push(-B+B*k/ringN);for(let k=0;k<=N;k++)a.push(L*k/N);for(let k=1;k<=ringN;k++)a.push(L+B*k/ringN);return a;};
  const xs=axis(h.W,innerNX),ys=axis(h.H,innerNY),nx=xs.length-1,ny=ys.length-1,nv=(nx+1)*(ny+1),n=shapes.length;
  const values=shapes.map(s=>{const a=new Float64Array(nv);let k=0;for(const y of ys)for(const x of xs)a[k++]=a3SupportCost(x,y,s);return a;});
  const evaluate=(weights,trace=false)=>{
    const winner=new Int32Array(nv),outsideWinner=new Int32Array(nv),areas=new Float64Array(n),J=Array.from({length:n},()=>new Float64Array(n));
    for(let k=0;k<nv;k++){let best=Infinity,id=0;for(let i=0;i<n-(B>0?1:0);i++){const v=values[i][k]-weights[i];if(v<best){best=v;id=i;}}winner[k]=id;outsideWinner[k]=B>0&&values[n-1][k]-weights[n-1]<best?n-1:id;}
    const edges=trace?Array.from({length:n},()=>[]):null;
    const process=(ids,pts,labs,outside)=>{
      const winners=outside?outsideWinner:winner,triArea=Math.abs(ringArea(pts));
      const i0=winners[ids[0]];
      if(i0===winners[ids[1]]&&i0===winners[ids[2]]){
        areas[i0]+=triArea;
        if(trace)for(let e=0;e<3;e++)edges[i0].push({a:pts[e],b:pts[(e+1)%3],label:labs[e]});
        return;
      }
      // Dominance at all three vertices is sufficient to discard an affine
      // bidder. Unlike taking only vertex winners, this retains triple sites.
      const v0=ids.map(k=>values[i0][k]-weights[i0]),cand=[];
      for(let i=0;i<n-(!outside&&B>0?1:0);i++)if(i===i0||ids.some((k,e)=>values[i][k]-weights[i]<=v0[e]))cand.push(i);
      const [A,Bv,C]=pts,det=(Bv[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(Bv[1]-A[1]);
      const aff=cand.map(i=>{
        const z=ids.map(k=>values[i][k]-weights[i]);
        const gx=((z[1]-z[0])*(C[1]-A[1])-(z[2]-z[0])*(Bv[1]-A[1]))/det;
        const gy=((Bv[0]-A[0])*(z[2]-z[0])-(C[0]-A[0])*(z[1]-z[0]))/det;
        return [gx,gy,z[0]];
      });
      for(let ci=0;ci<cand.length;ci++){
        const i=cand[ci],a=aff[ci];let poly={pts:pts.map(p=>[p[0]-A[0],p[1]-A[1]]),labs};
        for(let cj=0;cj<cand.length&&poly.pts.length>=3;cj++)if(cj!==ci){const b=aff[cj];poly=clipHalfPlane(poly,a[0]-b[0],a[1]-b[1],b[2]-a[2],cand[cj]);}
        if(poly.pts.length<3)continue;
        const ar=Math.abs(ringArea(poly.pts));if(ar<1e-12)continue;
        areas[i]+=ar;
        for(let e=0;e<poly.pts.length;e++){
          const j=poly.labs[e],p=poly.pts[e],q=poly.pts[(e+1)%poly.pts.length];
          if(j>=0){const b=aff[cand.indexOf(j)],grad=Math.hypot(a[0]-b[0],a[1]-b[1]);if(grad>1e-9)J[i][j]-=Math.hypot(q[0]-p[0],q[1]-p[1])/grad;}
          if(trace)edges[i].push({a:[p[0]+A[0],p[1]+A[1]],b:[q[0]+A[0],q[1]+A[1]],label:j});
        }
      }
    };
    const seam=(i,j)=>-1000-Math.min(i,j)*nv-Math.max(i,j);
    for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
      const k=y*(nx+1)+x,outside=x<ringN||x>=ringN+innerNX||y<ringN||y>=ringN+innerNY;
      const win=outside?outsideWinner:winner,wi=win[k],same=wi===win[k+1]&&wi===win[k+nx+1]&&wi===win[k+nx+2];
      if(same){
       areas[wi]+=(xs[x+1]-xs[x])*(ys[y+1]-ys[y]);
       if(trace){
        const pts=[[xs[x],ys[y]],[xs[x+1],ys[y]],[xs[x+1],ys[y+1]],[xs[x],ys[y+1]]];
        const ids=[k,k+1,k+nx+2,k+nx+1],nb=[[x,y-1],[x+1,y],[x,y+1],[x-1,y]];
        for(let e=0;e<4;e++){const [xx,yy]=nb[e];if(xx>=0&&yy>=0&&xx<nx&&yy<ny){const outside=xx<ringN||xx>=ringN+innerNX||yy<ringN||yy>=ringN+innerNY,ww=outside?outsideWinner:winner,kk=yy*(nx+1)+xx;if(ww[kk]===wi&&ww[kk+1]===wi&&ww[kk+nx+1]===wi&&ww[kk+nx+2]===wi)continue;}
        const a=pts[e],b=pts[(e+1)%4],label=seam(ids[e],ids[(e+1)%4]);edges[wi].push({a,b,label});}
       }continue;
      }
      const A=[xs[x],ys[y]],B0=[xs[x+1],ys[y]],C=[xs[x+1],ys[y+1]],D=[xs[x],ys[y+1]];
      process([k,k+1,k+nx+2],[A,B0,C],[seam(k,k+1),seam(k+1,k+nx+2),seam(k+nx+2,k)],outside);
      process([k,k+nx+2,k+nx+1],[A,C,D],[seam(k,k+nx+2),seam(k+nx+2,k+nx+1),seam(k+nx+1,k)],outside);
    }
    // Cancel mesh seams by their shared mesh-edge identity. Keeping only
    // labelled bisectors loses real boundaries when they coincide with a
    // mesh edge (especially the first 240 Hz departure frame).
    if(trace)for(let i=0;i<n;i++){
      const keep=[],groups=new Map();
      for(const e of edges[i]){if(e.label>=0)keep.push(e);else{if(!groups.has(e.label))groups.set(e.label,[]);groups.get(e.label).push(e);}}
      for(const seg of groups.values()){
        if(seg.length===1){keep.push(seg[0]);continue;}
        if(seg.length===2&&Math.hypot(seg[0].a[0]-seg[1].b[0],seg[0].a[1]-seg[1].b[1])<1e-7&&Math.hypot(seg[0].b[0]-seg[1].a[0],seg[0].b[1]-seg[1].a[1])<1e-7)continue;
        const ref=seg[0],axis=Math.abs(ref.a[0]-ref.b[0])>=Math.abs(ref.a[1]-ref.b[1])?0:1;
        if(Math.abs(ref.a[axis]-ref.b[axis])<1e-9)continue;
        const points=seg.flatMap(e=>[e.a[axis],e.b[axis]]).sort((a,b)=>a-b),cuts=[];
        for(const v of points)if(!cuts.length||v-cuts[cuts.length-1]>1e-8)cuts.push(v);
        const at=v=>{const t=(v-ref.a[axis])/(ref.b[axis]-ref.a[axis]);return [ref.a[0]+t*(ref.b[0]-ref.a[0]),ref.a[1]+t*(ref.b[1]-ref.a[1])];};
        for(let k=0;k+1<cuts.length;k++){const l=cuts[k],r=cuts[k+1],m=(l+r)/2;if(r-l<1e-8)continue;let winding=0;
         for(const e of seg)if(m>Math.min(e.a[axis],e.b[axis])-1e-9&&m<Math.max(e.a[axis],e.b[axis])+1e-9)winding+=e.b[axis]>e.a[axis]?1:-1;
         if(winding)keep.push({a:at(winding>0?l:r),b:at(winding>0?r:l),label:-9});
        }
      }
      edges[i]=keep;
    }
    for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)J[i][j]=J[j][i]=.5*(J[i][j]+J[j][i]);
    for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(i!==j)J[i][i]-=J[i][j];
    return {areas,J,edges};
  };
  return {evaluate,nx,ny};
}
function a3Chain(edges) {
  const key=p=>p.a3Key!==undefined?p.a3Key:Math.round(p[0]*1e6)+','+Math.round(p[1]*1e6),out=[];
  const links=new Map(),used=new Set();
  edges=edges.filter(e=>key(e.a)!==key(e.b));
  edges.forEach((e,i)=>{const k=key(e.a);if(!links.has(k))links.set(k,[]);links.get(k).push(i);});
  for(let i=0;i<edges.length;i++)if(!used.has(i)){
    const pts=[],labs=[];let j=i,start=key(edges[i].a),closed=false;
    for(let k=0;k<=edges.length;k++){
      if(used.has(j))break;used.add(j);const e=edges[j];pts.push(e.a);labs.push(e.label);
      if(key(e.b)===start){closed=true;break;}
      const candidates=links.get(key(e.b))||[];j=candidates.find(q=>!used.has(q));if(j===undefined)break;
    }
    if(closed){
      const queue=[pts];
      while(queue.length){const part=queue.pop(),seen=new Map();let split=false;
       for(let k=0;k<part.length;k++){const id=key(part[k]);if(seen.has(id)){const at=seen.get(id);queue.push(part.slice(at,k),part.slice(0,at).concat(part.slice(k)));split=true;break;}seen.set(id,k);}
       if(split||part.length<3||Math.abs(ringArea(part))<=1e-6)continue;
       const clean=simplifyLoop(part,1e-4,1e-5);out.push({pts:clean,labs:clean.map(()=>-9)});
      }
    }
  }
  return out.sort((a,b)=>Math.abs(ringArea(b.pts))-Math.abs(ringArea(a.pts)));
}
function a3Solve(h,shapes,target,w0,B=0) {
  const field=a3Field(h,shapes,24,B),n=shapes.length;
  let w=Float64Array.from(w0),cur=field.evaluate(w),it=0,evals=1;
  for(let pass=0;pass<Math.min(64,3*n)&&minOf(cur.areas)<=0;pass++)for(let i=0;i<n;i++)if(cur.areas[i]<=0){
    let lo=w[i],hi=w[i]+h.W*h.W+h.H*h.H;
    for(let k=0;k<25;k++){w[i]=(lo+hi)/2;const a=field.evaluate(w).areas[i];evals++;if(a<Math.min(target[i]*.1,minOf(target)*.25))lo=w[i];else hi=w[i];}
    w[i]=(lo+hi)/2;cur=field.evaluate(w);evals++;
  }
  if(B>0){const ring=(h.W+2*B)*(h.H+2*B)-h.W*h.H,requested=ring-target[n-1];
   if(requested>.05&&ring-cur.areas[n-1]<.01){let lo=w[n-1]-4*(h.W*h.W+h.H*h.H),hi=w[n-1];
    for(let k=0;k<28;k++){w[n-1]=(lo+hi)/2;const a=field.evaluate(w).areas[n-1];evals++;if(a<target[n-1])lo=w[n-1];else hi=w[n-1];}
    w[n-1]=(lo+hi)/2;cur=field.evaluate(w);evals++;
   }
  }
  const floor=.1*Math.min(minOf(target),minOf(cur.areas));
  const ringAreaTotal=B>0?(h.W+2*B)*(h.H+2*B)-h.W*h.H:0;
  const outsideFloor=B>0?.5*Math.min(ringAreaTotal-target[n-1],ringAreaTotal-cur.areas[n-1]):0;
  for(;it<32;it++){
    const residual=target.map((v,i)=>v-cur.areas[i]),err=Math.max(...residual.map((v,i)=>Math.abs(v)/target[i]));if(err<1e-6)break;
    // Exact mesh-edge contacts can leave the one-sided Jacobian disconnected.
    // Perturb the weights inside the solve, then converge the same quota target.
    const reached=new Set([0]),queue=[0];while(queue.length){const a=queue.pop();for(let j=0;j<n;j++)if(cur.J[a][j]<-1e-12&&!reached.has(j)){reached.add(j);queue.push(j);}}
    if(reached.size<n&&it<12){const amount=1e-3*Math.pow(4,it);w=w.map((v,i)=>v+amount*((i*.61803398875)%1-.5));cur=field.evaluate(w);evals++;continue;}
    const dw=solvePinned(cur.J,residual),norm=norm2(residual);let accepted=false;
    for(let s=1,k=0;k<22;k++,s/=2){const nw=w.map((v,i)=>v+s*dw[i]);if(!nw.every(Number.isFinite))break;const c=field.evaluate(nw);evals++;
      if(minOf(c.areas)>=floor&&(!B||ringAreaTotal-c.areas[n-1]>=outsideFloor)&&norm2(target.map((v,i)=>v-c.areas[i]))<=(1-s*.25)*norm){w=nw;cur=c;accepted=true;break;}
    }
    if(!accepted)break;
  }
  cur=field.evaluate(w,true);evals++;
  // Canonicalize shared intersections geometrically, not by a single rounded
  // hash bin: opposite calculations can lie on either side of a bin boundary.
  const nodes=new Map(),eps=1e-5;let nextNode=0;
  const canonical=p=>{const x=Math.floor(p[0]/eps),y=Math.floor(p[1]/eps);
   for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++)for(const q of nodes.get((x+dx)+','+(y+dy))||[])if(Math.abs(q[0]-p[0])<eps&&Math.abs(q[1]-p[1])<eps)return q;
   const k=x+','+y;if(!nodes.has(k))nodes.set(k,[]);p.a3Key=nextNode++;nodes.get(k).push(p);return p;
  };
  for(const edges of cur.edges)for(const e of edges){e.a=canonical(e.a);e.b=canonical(e.b);}
  const cells=cur.edges.map(edges=>{
    const loops=a3Chain(edges);
    let saved,components;
    const parts=()=>{if(components)return components;components=[];
      for(const outer of loops)if(ringArea(outer.pts)>0){const tris=triangulatePts(outer.pts);if(!tris)throw Error('Astra III: non-simple content outline');let one=tris.map(pts=>({pts,labs:pts.map(()=>-9)}));
       for(const hole of loops)if(ringArea(hole.pts)<0&&Math.abs(ringArea(hole.pts))<Math.abs(ringArea(outer.pts))){const t=triangulatePts(hole.pts);if(!t)throw Error('Astra III: non-simple hole');const c=t[0].reduce((a,p)=>[a[0]+p[0]/3,a[1]+p[1]/3],[0,0]);if(pointInPolygon(c[0],c[1],outer.pts))for(const tri of t)one=subtractConvex(one,tri)||one;}
       components.push(one);
      }return components;
    };
    return {pts:loops[0]?.pts||[],labs:loops[0]?.labs||[],a3Loops:loops,
      get a3Components(){return parts();},get pieces(){return saved||(saved=parts().flat());}
    };
  });
  const mean=w.reduce((a,b)=>a+b,0)/n;w=w.map(x=>x-mean);
  const err=Math.max(...target.map((v,i)=>Math.abs(v-cur.areas[i])/v));
  return {weights:w,diagram:{cells,areas:cur.areas},maxRelErr:err,iterations:it,converged:err<1e-6,evals};
}
