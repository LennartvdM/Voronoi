/* Counts, interruptions, hover release, and an actual mid-transition resize. */
const fs=require('fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{
 const src=process.argv[2],output=process.argv[3];
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']});
 const cases=[];
 for(const width of [1440,390]){
  const p=await browser.newPage({viewport:{width,height:900}}),errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  await p.evaluate(()=>{let t=0;const q=[];performance.now=()=>t;requestAnimationFrame=cb=>q.push(cb);window.step=()=>{t+=30;for(const cb of q.splice(0))cb(t)};});
  let s=fs.readFileSync(src,'utf8'),i=s.lastIndexOf('})();');
  s=s.slice(0,i)+'\nwindow.T={get:()=>({root,picture,W,H}),rasterCheck,mouse:(x,y)=>{mouseX=x;mouseY=y}};\n'+s.slice(i);
  await p.setContent(s);
  const result=await p.evaluate(()=>{
   const X=T;X.mouse(-1000,-1000);const rows=[];let frame=0;window.worstCoverage=null;window.coverageSamples=[];let worst=0;
   window.runPhase=(label,frames,hover=false)=>{
    let gap=0,over=0,vanish=0,invalid=0,err=0,areaError=0,roles=0,maxPositionJump=0,maxVelocityJump=0,maxLoanCredit=0,maxStorage=0,maxLedger=0,maxQuotaError=0,maxStorageError=0;
    for(let k=0;k<frames;k++){
     if(hover){const {W,H}=X.get();X.mouse(W*(.5+.45*Math.sin(frame*.065)),H*(.5+.4*Math.cos(frame*.037)));}
     step();frame++;
     const {root:r,picture,W,H}=X.get(),assigned=new Set();
     for(const b of r.bodies){if(!Number.isFinite(b.x+b.y+b.vx+b.vy))invalid++;if(!b.isVoid&&!b.leaving){if((b.paintArea||0)<1)vanish++;if(b.rect){const key=b.rect.join(',');if(assigned.has(key))roles++;assigned.add(key);}}}
     for(const e of r.a2ExchangeLog||[]){maxPositionJump=Math.max(maxPositionJump,e.positionJump);maxVelocityJump=Math.max(maxVelocityJump,e.velocityJump);}
     maxLoanCredit=Math.max(maxLoanCredit,r.bufferCredit||0);maxStorage=Math.max(maxStorage,r.bufferContentOutside||0);maxLedger=Math.max(maxLedger,r.bufferLedgerError||0);maxQuotaError=Math.max(maxQuotaError,r.bufferQuotaError||0);maxStorageError=Math.max(maxStorageError,Math.abs((r.bufferActualOutside||0)-(r.bufferCredit||0)));
     err=Math.max(err,r.solved?.maxRelErr||0);areaError=Math.max(areaError,Math.abs(r.bodies.reduce((sum,b)=>sum+(b.paintArea||0),0)-W*H));
     for(const l of picture.leaves)for(const lp of l.loops)for(const q of lp)if(!Number.isFinite(q[0]+q[1]))invalid++;
     if(k%6===0){const z=X.rasterCheck(picture.leaves.flatMap(l=>l.loops.map(pts=>({pts,hole:!!pts.hole}))),W,H);gap=Math.max(gap,z.gap);over=Math.max(over,z.over);
      if(z.gap+z.over>0){window.coverageSamples.push({label,k,W,H,gap:z.gap,over:z.over,leaves:picture.leaves.map(l=>l.loops.map(pts=>({pts,hole:!!pts.hole})))});}
      if(z.gap+z.over>worst){worst=z.gap+z.over;window.worstCoverage={label,k,W,H,gap:z.gap,over:z.over,leaves:picture.leaves.map(l=>l.loops.map(pts=>({pts,hole:!!pts.hole})))};}
     }
    }
    const r=X.get().root;
    const row={label,frames,gap,over,vanish,invalid,err,areaError,roles,maxPositionJump,maxVelocityJump,maxLoanCredit,maxStorage,maxLedger,maxQuotaError,maxStorageError,endStorage:r.bufferActualOutside||0,endCredit:r.bufferCredit||0,unseated:r.bodies.filter(b=>!b.isVoid&&!b.leaving&&b.rect&&!b.wall).length};
    rows.push(row);return row;
   };
   const scene=sc=>document.querySelector('[data-scene="'+sc+'"]').click();
   const slider=(id,n)=>{const el=document.getElementById(id);el.value=n;el.dispatchEvent(new Event('input'));};
   runPhase('startup',160);slider('count',30);scene('hero');runPhase('30-hero',220);scene('sidebar');runPhase('30-sidebar',220);
   for(const sc of ['frame','bento','hero','flock','sidebar','frame']){scene(sc);runPhase('interrupt-'+sc,10);}runPhase('interrupted-settle',220);
   slider('count',4);scene('bento');runPhase('4-bento',220);slider('count',12);scene('frame');runPhase('12-frame',220);
   runPhase('hover-sweep',180,true);X.mouse(-1000,-1000);scene('flock');runPhase('release',200);
   scene('hero');runPhase('interrupt-resize',15);
   return rows;
  });
  await p.setViewportSize({width:width===1440?820:600,height:760});
  await p.evaluate(()=>window.dispatchEvent(new Event('resize')));
  result.push(await p.evaluate(()=>runPhase('resized-settle',260)));
  const worst=await p.evaluate(()=>window.coverageSamples);
  if(worst.length)fs.writeFileSync(output.replace('.json',`-${width}-coverage.json`),JSON.stringify(worst));
  cases.push({width,errors,result});await p.close();
 }
 await browser.close();fs.writeFileSync(output,JSON.stringify(cases,null,2));console.log(JSON.stringify(cases));
})().catch(e=>{console.error(e);process.exit(1)});
