/* Departure and role audit: structural motion is sampled every frame. */
const fs=require('fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{
 const src=process.argv[2],output=process.argv[3],dt=Number(process.argv[4]||1000/120);
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']});
 const p=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];
 p.on('pageerror',e=>errors.push(e.message));
 await p.evaluate(dt=>{let t=0;const q=[];const realNow=performance.now.bind(performance);performance.now=()=>t;requestAnimationFrame=cb=>q.push(cb);window.advance=()=>{t+=dt;for(const cb of q.splice(0))cb(t)};window.realNow=realNow;},dt);
 let s=fs.readFileSync(src,'utf8'),i=s.lastIndexOf('})();');
 s=s.slice(0,i)+'\nwindow.AUDIT={get:()=>({root,picture,W,H}),mouseOff:()=>{mouseX=-1000;mouseY=-1000},diagram:computeDiagram,area:ringArea,loanLevel:(l,t)=>typeof a2LoanLevel!=="undefined"?a2LoanLevel(l,t):0};\n'+s.slice(i);
 await p.setContent(s);
 const results=await p.evaluate(dt=>{
  const X=AUDIT;X.mouseOff();for(let i=0;i<Math.ceil(3600/dt);i++)advance();
  const extent=b=>{let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;for(const s of b.subs){x0=Math.min(x0,s.x);x1=Math.max(x1,s.x);y0=Math.min(y0,s.y);y1=Math.max(y1,s.y);}return [x1-x0,y1-y0];};
  const rows=[];
  for(const scene of ['hero','sidebar','frame','bento','flock']){
   const r=X.get().root,initial=new Map(r.bodies.filter(b=>!b.isVoid&&!b.leaving).map(b=>[b.id,{x:b.x,y:b.y,extent:extent(b),loss:0,px:b.x,py:b.y,travel:0,name:b.name,color:JSON.stringify(b.color),hasMoved:false}]));
   const row={scene,axisSamples:[],supportLossBefore3px:[],travelPx:0,maxOutsidePx:0,outsideBodyFrames:0,minVisibleAreaPx2:Infinity,maxQuotaImbalance:0,loanFrameSamples:0,loanHistory:[],swaps:[],identityErrors:0,duplicateRoles:0,unfinished:0,nonrectAreaErrorMax:0};
   document.querySelector('[data-scene="'+scene+'"]').click();
   for(let f=0;f<Math.ceil(5500/dt);f++){
    advance();const {W,H}=X.get();
    if(f*dt<=150)row.axisSamples.push({ms:(f+1)*dt,axisPercent:r.rectPct});
    const roles=new Set();
    for(const b of r.bodies){if(b.isVoid||b.leaving)continue;
     const z=initial.get(b.id);if(!z)continue;
     if(b.name!==z.name||JSON.stringify(b.color)!==z.color)row.identityErrors++;
     if(b.rect){const key=b.rect.join(',');if(roles.has(key))row.duplicateRoles++;roles.add(key);}
     const step=Math.hypot(b.x-z.px,b.y-z.py);z.travel+=step;z.px=b.x;z.py=b.y;
     z.hasMoved ||= Math.hypot(b.x-z.x,b.y-z.y)>3;
     const ex=extent(b);
     if(!z.hasMoved&&f*dt<1600){let losses=[];for(let a=0;a<2;a++)if(z.extent[a]>1)losses.push(1-ex[a]/z.extent[a]);z.loss=Math.max(z.loss,...losses,0);}
     const outside=Math.max(0,-b.x,b.x-W,-b.y,b.y-H);row.maxOutsidePx=Math.max(row.maxOutsidePx,outside);if(outside>0)row.outsideBodyFrames++;
     row.minVisibleAreaPx2=Math.min(row.minVisibleAreaPx2,b.paintArea||0);
    }
    if(r.a2LoanCredit>1e-6){let expected=0,actual=0;for(const b of r.bodies){expected+=b.claim*(1+(1.6-1)*b.hoverMix*(1-b.crystal));actual+=b.subs[0]?.claim||0;}row.maxQuotaImbalance=Math.max(row.maxQuotaImbalance,Math.abs(actual-expected));row.loanFrameSamples++;}
   }
   for(const [id,z]of initial){row.supportLossBefore3px.push({id,loss:z.loss,travelPx:z.travel});row.travelPx+=z.travel;}
   row.prematureContractionCells=row.supportLossBefore3px.filter(z=>z.loss>.1).length;
   row.meanPrematureContraction=row.supportLossBefore3px.reduce((s,z)=>s+z.loss,0)/initial.size;
   row.swaps=(r.a2ExchangeLog||[]).slice();row.loanHistory=(r.a2LoanHistory||[]).filter(l=>l.scene===scene);
   row.unfinished=r.bodies.filter(b=>!b.isVoid&&!b.leaving&&b.rect&&!b.wall).length;
   for(const b of r.bodies){if(b.isVoid||b.leaving||!b.rect)continue;const target=(b.rect[2]-b.rect[0])*r.PW*(b.rect[3]-b.rect[1])*r.PH;row.nonrectAreaErrorMax=Math.max(row.nonrectAreaErrorMax,Math.abs((b.paintArea||0)-target));}
   rows.push(row);
  }
  return rows;
 },dt);
 await browser.close();fs.writeFileSync(output,JSON.stringify({dt,errors,results},null,2));console.log(JSON.stringify({dt,errors,results}));
})().catch(e=>{console.error(e);process.exit(1)});
