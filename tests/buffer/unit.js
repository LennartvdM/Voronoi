const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']});
 const p=await browser.newPage();let s=fs.readFileSync(process.argv[2]||'buffer.html','utf8'),i=s.lastIndexOf('})();');
 s=s.slice(0,i)+'\nwindow.__math={bfWorldDiagram,bfReserveSolve,bfBounds,bfMargin,bfRing,bfClip,bfAmount,computeDiagram,ringArea};\n'+s.slice(i);
 await p.evaluate(()=>{requestAnimationFrame=()=>0});await p.setContent(s);
 const result=await p.evaluate(()=>{
 const {bfWorldDiagram:fast,bfReserveSolve:solve,bfBounds,bfMargin,bfRing,bfClip,bfAmount,computeDiagram}=__math;
 const h={W:800,H:600},B=bfMargin(h),ring=(800+2*B)*(600+2*B)-480000;
 let seed=82471;const rnd=()=>((seed=(1664525*seed+1013904223)>>>0)/4294967296);
 let areaError=0,jacobianError=0,conservationError=0;const solves=[];
 const group=(d,o,n)=>{const a=Array(n).fill(0);d.areas.forEach((v,i)=>a[o[i]]+=v);return a;};
 const ref=(S,w,cs)=>{const inside=computeDiagram(S.slice(0,cs),w.slice(0,cs),[[0,0],[800,0],[800,600],[0,600]]),raw=computeDiagram(S,w,bfBounds(h)),rects=bfRing(h).map(r=>[r[0][0],r[0][1],r[2][0],r[2][1]]);return {areas:raw.cells.map((c,i)=>rects.reduce((a,r)=>a+bfAmount(bfClip(c,r)),0)+(i<cs?inside.areas[i]:0))};};
 const R=[[-60,-60],[400,-60],[860,-60],[860,300],[860,660],[400,660],[-60,660],[-60,300]];
 for(let trial=0;trial<32;trial++){
  const S=[],O=[];
  for(let body=0;body<4;body++)for(let k=0;k<2;k++){S.push([80+(body%2)*400+rnd()*100,70+Math.floor(body/2)*280+rnd()*100]);O.push(body);}
  const cs=S.length;S.push(...R);O.push(...R.map(()=>4));
  const w=Array.from({length:5},()=>20000*(rnd()-.5)),d=fast(h,S,O.map(i=>w[i]),cs),a=group(d,O,5),r=group(ref(S,O.map(i=>w[i]),cs),O,5);
  areaError=Math.max(areaError,...a.map((v,i)=>Math.abs(v-r[i])));
  conservationError=Math.max(conservationError,Math.abs(a.reduce((a,b)=>a+b,0)-480000-ring));
  const J=Array.from({length:5},()=>Array(5).fill(0));
  d.cells.forEach((c,i)=>{for(const pc of c.pieces)for(let k=0;k<pc.pts.length;k++){const j=pc.labs[k];if(j<0||O[i]===O[j])continue;const p=pc.pts[k],q=pc.pts[(k+1)%pc.pts.length],dist=Math.hypot(S[i][0]-S[j][0],S[i][1]-S[j][1]);J[O[i]][O[j]]-=Math.hypot(p[0]-q[0],p[1]-q[1])/(2*dist);}});
  for(let k=0;k<4;k++)J[4][k]=J[k][4];
  for(let a=0;a<5;a++)for(let b=a+1;b<5;b++)J[a][b]=J[b][a]=.5*(J[a][b]+J[b][a]);
  for(let a=0;a<5;a++)for(let b=0;b<5;b++)if(a!==b)J[a][a]-=J[a][b];
  for(let k=0;k<5;k++){const eps=.01,wa=w.slice(),wb=w.slice();wa[k]+=eps;wb[k]-=eps;const ap=group(fast(h,S,O.map(i=>wa[i]),cs),O,5),am=group(fast(h,S,O.map(i=>wb[i]),cs),O,5);for(let a=0;a<5;a++)jacobianError=Math.max(jacobianError,Math.abs((ap[a]-am[a])/(2*eps)-J[a][k]));}
  if(trial<8){const L=5000+trial*3000,Q=[120000+L,120000,120000,120000,ring-L];const sol=solve(h,S,O,Q,w,cs,40);solves.push({trial,credit:L,residual:sol.maxRelErr,converged:sol.converged});}
 }
 return {trials:32,areaError,jacobianError,conservationError,solves};
 });
 await browser.close();fs.writeFileSync(process.argv[3]||'results/unit.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 if(result.areaError>1e-5||result.jacobianError>1e-4||result.conservationError>1e-5||result.solves.some(s=>s.residual>1.01e-6))process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
