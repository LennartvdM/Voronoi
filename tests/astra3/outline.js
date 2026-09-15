// Assemble material boundaries from convex pieces before drawing. A near-flat
// triangulation must not erase an entire nested member through loose endpoint
// matching. Splits and reverse-edge cancellation share canonical vertices.
function a3PieceLoops(pieces) {
  const eps=1e-7, bins=new Map(), nodes=[];
  const node=p=>{const x=Math.floor(p[0]/eps),y=Math.floor(p[1]/eps);
    for(let i=-1;i<=1;i++)for(let j=-1;j<=1;j++)for(const v of bins.get((x+i)+','+(y+j))||[])if(Math.hypot(v.p[0]-p[0],v.p[1]-p[1])<eps)return v;
    const v={p:[p[0],p[1]],id:nodes.length};v.p.a3Key=v.id;nodes.push(v);const k=x+','+y;if(!bins.has(k))bins.set(k,[]);bins.get(k).push(v);return v;
  };
  const rings=pieces.filter(c=>c.pts.length>=3).map(c=>c.pts.map(node));
  const edges=new Map();
  const put=(a,b)=>{if(a.id===b.id)return;const rev=b.id+','+a.id;if(edges.has(rev)){const count=edges.get(rev);if(count.length>1)count.pop();else edges.delete(rev);}else{const k=a.id+','+b.id;if(!edges.has(k))edges.set(k,[]);edges.get(k).push({a:a.p,b:b.p,label:-9});}};
  for(const ring of rings)for(let k=0;k<ring.length;k++){
    const a=ring[k],b=ring[(k+1)%ring.length],dx=b.p[0]-a.p[0],dy=b.p[1]-a.p[1],l2=dx*dx+dy*dy;if(l2<eps*eps)continue;
    const cuts=[{v:a,t:0},{v:b,t:1}],L=Math.sqrt(l2);
    for(const v of nodes){if(v===a||v===b)continue;const x=v.p[0]-a.p[0],y=v.p[1]-a.p[1],t=(x*dx+y*dy)/l2;if(t>eps/L&&t<1-eps/L&&Math.abs(x*dy-y*dx)<eps*L)cuts.push({v,t});}
    cuts.sort((a,b)=>a.t-b.t);for(let j=0;j+1<cuts.length;j++)put(cuts[j].v,cuts[j+1].v);
  }
  return a3Chain([...edges.values()].flat()).map(c=>{const p=c.pts;if(ringArea(p)<0)p.hole=true;return p;});
}
leafOutlines=a3PieceLoops;
