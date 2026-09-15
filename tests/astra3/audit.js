/* Actual departure contours, arc plans and dressed-contour edge crossings. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{
 const file=process.argv[2],out=process.argv[3],source=fs.readFileSync(file,'utf8');
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']});
 const p=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.evaluate(()=>{let t=0;const q=[];performance.now=()=>t;requestAnimationFrame=f=>q.push(f);window.advance=n=>{for(let i=0;i<n;i++){t+=1000/120;for(const f of q.splice(0))f(t);}};});
 const i=source.lastIndexOf('})();');await p.setContent(source.slice(0,i)+'\nwindow.X={root,get:()=>({picture,W,H}),ringArea,garment,config,mouse:()=>{mouseX=mouseY=-1000;}};\n'+source.slice(i));
 await p.evaluate(()=>{X.mouse();advance(432);window.audit=[];window.snapshot=()=>X.root.bodies.filter(b=>!b.isVoid&&!b.leaving).map(b=>({id:b.id,x:b.x,y:b.y,loops:(b.loops||[]).map(pts=>({pts,hole:false})).concat((b.holes||[]).map(pts=>({pts,hole:true})))}));});
 for(const scene of ['hero','sidebar','frame','bento','flock']){
  await p.evaluate(scene=>{const r=X.root;window.current={scene,source:snapshot(),early:[],samples:[],maxContentOutside:0,maxDressedCrossingLeaves:0,peak:null,arcPlans:[],width:r.W,height:r.H};document.querySelector('[data-scene="'+scene+'"]').click();current.arcPlans=r.a3PlanLog||[];},scene);
  for(let chunk=0;chunk<55;chunk++){
   await p.evaluate(()=>{for(let k=0;k<12;k++){
    advance(1);const r=X.root,{picture,W,H}=X.get();current.frame=(current.frame||0)+1;
    if(current.frame<=18)current.early.push({ms:current.frame*1000/120,bodies:snapshot()});
    let crossings=0;
    for(const leaf of picture.leaves){if(leaf.isVoid||leaf.path[0].body.isVoid)continue;
     for(const loop of leaf.loops){if(loop.hole)continue;const g=X.garment(loop,X.config.gap/2,X.config.cornerRadius);
      if(g.cores.some(p=>{const xs=p.map(q=>q[0]),ys=p.map(q=>q[1]);return Math.min(...xs)<-1||Math.max(...xs)>W+1||Math.min(...ys)<-1||Math.max(...ys)>H+1;})){crossings++;break;}
     }
    }
    current.maxDressedCrossingLeaves=Math.max(current.maxDressedCrossingLeaves,crossings);
    const storage=r.a3Storage||[],outside=storage.reduce((s,b)=>s+(b.isVoid?0:Math.max(0,b.outside)),0);
    if(outside>current.maxContentOutside){current.maxContentOutside=outside;current.peak={frame:current.frame,ms:current.frame*1000/120,storage,credit:r.a3Credit||0,bodies:snapshot(),leaves:picture.leaves.filter(l=>!l.isVoid&&!l.path[0].body.isVoid).map(l=>({root:l.path[0].body.id,loops:l.loops.map(pts=>({pts,hole:!!pts.hole}))}))};}
    if(current.frame%12===0)current.samples.push({ms:current.frame*1000/120,bodies:snapshot()});
   }});
   if(scene==='hero'&&[0,8,14,24].includes(chunk))await p.screenshot({path:out.replace('.json',`-${scene}-${(chunk+1)*100}ms.png`)});
  }
  await p.evaluate(()=>{current.outsideAtEnd=X.root.a3Outside||0;current.creditAtEnd=X.root.a3Credit||0;audit.push(current);});
 }
 const data=await p.evaluate(()=>({scenes:audit}));data.errors=errors;data.sha256=crypto.createHash('sha256').update(source).digest('hex');data.dtMs=1000/120;
 fs.writeFileSync(out,JSON.stringify(data));console.log(JSON.stringify({file,errors,scenes:data.scenes.map(s=>({scene:s.scene,outside:s.maxContentOutside,paintedCrossings:s.maxDressedCrossingLeaves,end:s.outsideAtEnd,arcs:s.arcPlans.filter(p=>p.bend>1).length}))}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
