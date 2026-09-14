/* Geometric witnesses: actual outside polygons at each scene's maximum storage. */
const fs=require('fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.evaluate(()=>{let t=0,q=[];performance.now=()=>t;requestAnimationFrame=f=>{q.push(f);return q.length;};window.step=()=>{t+=1000/120;for(const f of q.splice(0))f(t);};});
 let s=fs.readFileSync(process.argv[2],'utf8'),i=s.lastIndexOf('})();');s=s.slice(0,i)+'\nwindow.BF={get root(){return root},mouse:()=>{mouseX=-1000;mouseY=-1000;}};\n'+s.slice(i);await page.setContent(s);
 const result=await page.evaluate(()=>{
  BF.mouse();for(let k=0;k<432;k++)step();const states=[];
  for(const scene of ['hero','sidebar','frame','bento','flock']){
   document.querySelector('[data-scene="'+scene+'"]').click();let best=null,peak=-1;
   for(let f=0;f<660;f++){step();const h=BF.root;if(h.bufferContentOutside>peak){peak=h.bufferContentOutside;
    best={scene,f,W:h.W,H:h.H,t:h.t,credit:h.bufferCredit,contentOutside:h.bufferContentOutside,voidOutside:h.bufferVoidOutside,reserveArea:h.bufferReserveArea,bounds:h.bufferWorld.bounds,cells:h.bufferWorld.cells.map((c,i)=>({id:h.bufferWorld.bodies[i]?.id??null,isVoid:!!h.bufferWorld.bodies[i]?.isVoid,pieces:(c.pieces||[c]).map(p=>p.pts)})),storage:[...h.bufferStorage].map(([b,a])=>({id:b.id,isVoid:b.isVoid,...a}))};}
   }states.push(best);
  }return states;
 });
 await browser.close();fs.writeFileSync(process.argv[3],JSON.stringify({errors,states:result}));if(errors.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
