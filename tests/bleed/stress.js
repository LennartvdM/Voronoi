const fs = require('fs');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/tmp/astra-runtime/node_modules/playwright');
(async()=>{
 const src=process.argv[2], output=process.argv[3];
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH ? {executablePath:process.env.CHROMIUM_PATH} : {}),args:['--no-sandbox']});
 const results=[];
 for(const width of [1440,390]) {
  const p=await browser.newPage({viewport:{width,height:900}});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.evaluate(()=>{let t=0;const q=[];performance.now=()=>t;requestAnimationFrame=cb=>q.push(cb);window.step=()=>{t+=30;for(const cb of q.splice(0))cb(t);};});
  let s=fs.readFileSync(src,'utf8'),i=s.lastIndexOf('})();');
  s=s.slice(0,i)+'\nwindow.__X={get:()=>({root,picture,W,H}),rasterCheck,setMouse:(x,y)=>{mouseX=x;mouseY=y;}};'+s.slice(i);
  // the coverage raster samples 0.01 px off the integer grid: at 390 px the
  // pitch is 65 px, so grid lines fall ON sample columns and a numerical seam
  // 1e-6 px either side of its line read as a whole column of gap or overlap
  s=s.replace('const c0 = Math.max(0, Math.ceil((xs[m] - S / 2) / S)), c1 = Math.min(gw - 1, Math.ceil((xs[m + 1] - S / 2) / S) - 1);','const c0 = Math.max(0, Math.ceil((xs[m] - S / 2 - 0.01) / S)), c1 = Math.min(gw - 1, Math.ceil((xs[m + 1] - S / 2 - 0.01) / S) - 1);');
  if(!s.includes('S / 2 - 0.01')) throw new Error('raster sample offset not applied');
  await p.setContent(s);
  const result=await p.evaluate(()=>{
   const X=window.__X;X.setMouse(-1000,-1000);
   const results=[];let n=0;
   const run=(label,frames,hover=false)=>{
    let gap=0,over=0,vanish=0,invalid=0,err=0,areaError=0;
    for(let k=0;k<frames;k++){
     if(hover){const {W,H}=X.get();X.setMouse(W*(.5+.45*Math.sin(n*.065)),H*(.5+.4*Math.cos(n*.037)));}
     step();n++;
     const {root,picture,W,H}=X.get();
     for(const b of root.bodies){if(!Number.isFinite(b.x+b.y))invalid++;if(!b.isVoid&&!b.leaving&&(b.paintArea||0)<1)vanish++;}
     if(root.solved)err=Math.max(err,root.solved.maxRelErr);
     areaError=Math.max(areaError,Math.abs(root.bodies.reduce((a,b)=>a+(b.paintArea||0),0)-W*H));
     for(const l of picture.leaves)for(const lp of l.loops)for(const q of lp)if(!Number.isFinite(q[0]+q[1]))invalid++;
     if(k%6===0){const z=X.rasterCheck(picture.leaves.flatMap(l=>l.loops.map(pts=>({pts,hole:!!pts.hole}))),W,H);gap=Math.max(gap,z.gap);over=Math.max(over,z.over);}
    }
    const {root}=X.get();results.push({label,frames,gap,over,vanish,invalid,err,areaError,unseated:root.bodies.filter(b=>!b.isVoid&&!b.leaving&&b.rect&&!b.wall).length});
   };
   run('startup',160);
   const scene=name=>document.querySelector('[data-scene="'+name+'"]').click();
   const slider=(id,n)=>{const e=document.getElementById(id);e.value=n;e.dispatchEvent(new Event('input'));};
   slider('count',30);scene('hero');run('30-hero',220);
   scene('sidebar');run('30-sidebar',220);
   for(const sc of ['frame','bento','hero','flock','sidebar','frame']){scene(sc);run('interrupt-'+sc,10);}
   run('interrupted-settle',220);
   slider('count',4);scene('bento');run('4-bento',220);
   slider('count',12);scene('frame');run('12-frame',220);
   run('hover-sweep',180,true);X.setMouse(-1000,-1000);scene('flock');run('release',200);
   return results;
  });
  results.push({width,errors,result});await p.close();
 }
 await browser.close();fs.writeFileSync(output,JSON.stringify(results,null,2));console.log(JSON.stringify(results));
})().catch(e=>{console.error(e);process.exit(1)});
