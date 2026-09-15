/* Independent all-bidder triangle integration, derivatives and arc endpoints. */
const fs=require('fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']}),p=await browser.newPage();
 await p.evaluate(()=>requestAnimationFrame=()=>0);
 let s=fs.readFileSync(process.argv[2],'utf8'),at=s.lastIndexOf('})();');s=s.slice(0,at)+'window.U={a3SupportCost,a3Field,a3Solve,a3Curve,a3CurveVelocity,ringArea,clipHalfPlane};'+s.slice(at);await p.setContent(s);
 const data=await p.evaluate(()=>{
  let seed=137;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  const h={W:240,H:180,COLS:6,ROWS:6,PW:40,PH:30};let integrationMax=0,derivativeMax=0,quotaMax=0,outlineMax=0,solveRows=[];
  function independent(shapes,w,B){const sp=24,NX=h.COLS*Math.ceil(h.PW/sp),NY=h.ROWS*Math.ceil(h.PH/sp),nr=B?Math.ceil(B/sp):0;
   const axis=(L,N)=>{const a=[];for(let i=0;i<nr;i++)a.push(-B+B*i/nr);for(let i=0;i<=N;i++)a.push(L*i/N);for(let i=1;i<=nr;i++)a.push(L+B*i/nr);return a;};const xs=axis(h.W,NX),ys=axis(h.H,NY),a=shapes.map(()=>0);
   for(let y=0;y+1<ys.length;y++)for(let x=0;x+1<xs.length;x++){
    const outside=x<nr||x>=nr+NX||y<nr||y>=nr+NY,n=shapes.length-(!outside&&B?1:0),A=[xs[x],ys[y]],B0=[xs[x+1],ys[y]],C=[xs[x+1],ys[y+1]],D=[xs[x],ys[y+1]];
    for(const t of [[A,B0,C],[A,C,D]]){const [v0,v1,v2]=t,det=(v1[0]-v0[0])*(v2[1]-v0[1])-(v2[0]-v0[0])*(v1[1]-v0[1]);const f=shapes.slice(0,n).map((s,i)=>{const z=t.map(v=>U.a3SupportCost(...v,s)-w[i]);return [((z[1]-z[0])*(v2[1]-v0[1])-(z[2]-z[0])*(v1[1]-v0[1]))/det,((v1[0]-v0[0])*(z[2]-z[0])-(v2[0]-v0[0])*(z[1]-z[0]))/det,z[0]];});
     for(let i=0;i<n;i++){let p={pts:t.map(v=>[v[0]-v0[0],v[1]-v0[1]]),labs:[-1,-2,-3]};for(let j=0;j<n&&p.pts.length>=3;j++)if(i!==j)p=U.clipHalfPlane(p,f[i][0]-f[j][0],f[i][1]-f[j][1],f[j][2]-f[i][2],j);if(p.pts.length>=3)a[i]+=Math.abs(U.ringArea(p.pts));}
    }
   }return a;
  }
  for(let k=0;k<24;k++){
   const B=k%2?30:0,shapes=[[40,35],[190,35],[45,140],[185,145]].map(([x,y])=>({x:x+(rnd()-.5)*20,y:y+(rnd()-.5)*20,hx:rnd()*30,hy:rnd()*25,regularizer:.000101}));if(B)shapes.push({reserve:true,W:h.W,H:h.H,B});
   const w=shapes.map(()=>rnd()*200-100),field=U.a3Field(h,shapes,24,B),d=field.evaluate(w),truth=independent(shapes,w,B);
   for(let i=0;i<w.length;i++)integrationMax=Math.max(integrationMax,Math.abs(d.areas[i]-truth[i]));
   for(let j=0;j<w.length;j++){const hi=w.slice(),lo=w.slice();hi[j]+=.001;lo[j]-=.001;const a=field.evaluate(hi).areas,b=field.evaluate(lo).areas;for(let i=0;i<w.length;i++)derivativeMax=Math.max(derivativeMax,Math.abs((a[i]-b[i])/.002-d.J[i][j]));}
   if(k<8){const target=Array.from(d.areas,a=>Math.max(1,a)*(.9+.2*rnd())),world=(h.W+2*B)*(h.H+2*B),sum=target.reduce((a,b)=>a+b,0);for(let i=0;i<target.length;i++)target[i]*=world/sum;const s=U.a3Solve(h,shapes,target,w,B);if(!B||target[target.length-1]<world-h.W*h.H)quotaMax=Math.max(quotaMax,s.maxRelErr);else if(s.converged)throw Error('Infeasible reserve quota reported converged');solveRows.push({case:k,B,err:s.maxRelErr,reserveTarget:target[target.length-1],ring:world-h.W*h.H});s.diagram.cells.forEach((c,i)=>{const a=c.a3Loops.reduce((sum,p)=>sum+U.ringArea(p.pts),0);outlineMax=Math.max(outlineMax,Math.abs(a-s.diagram.areas[i]));});}
  }
  const curve={sx:25,sy:50,ex:300,ey:160,vx:32,vy:-20,bx:70,by:-120,start:2,duration:2.2};let endpointMax=0;for(const [t,pos,vel] of [[2,[25,50],[32,-20]],[4.2,[300,160],[0,0]]]){const a=U.a3Curve(curve,t),v=U.a3CurveVelocity(curve,t);endpointMax=Math.max(endpointMax,...a.map((x,i)=>Math.abs(x-pos[i])),...v.map((x,i)=>Math.abs(x-vel[i])));}
  return {cases:24,solves:8,integrationMax,derivativeMax,quotaMax,outlineMax,endpointMax,solveRows};
 });
 if(data.integrationMax>1e-6||data.derivativeMax>1e-4||data.quotaMax>1.01e-6||data.outlineMax>.1||data.endpointMax>1e-8)throw Error(JSON.stringify(data));
 fs.writeFileSync(process.argv[3],JSON.stringify(data,null,2));console.log(JSON.stringify(data));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
