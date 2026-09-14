const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/pyvenv/lib/python3.13/site-packages/playwright/driver/package');
const options=JSON.parse(process.env.BUFFER_TEST_OPTIONS||'{}');
const src=path.resolve(process.argv[2]||'buffer.html'),out=process.argv[3]||'results/audit.json',dt=+(process.argv[4]||30);
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:process.env.PLAYWRIGHT_MODULE?{}:{executablePath:'/usr/bin/chromium'}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.evaluate(({dt})=>{let t=0,q=[];window.__realNow=performance.now.bind(performance);performance.now=()=>t;requestAnimationFrame=cb=>(q.push(cb),q.length);window.__step=()=>{t+=dt;for(const f of q.splice(0))f(t);};},{dt});
 await page.evaluate(options=>window.BUFFER_OPTIONS=options,options);
 let s=fs.readFileSync(src,'utf8'),i=s.lastIndexOf('})();');s=s.slice(0,i)+`\nwindow.__bf={get root(){return root},get picture(){return picture},ringArea,convexHull,config,setMouse:(x,y)=>{mouseX=x;mouseY=y;}};\n`+s.slice(i);
 await page.setContent(s);
 const result=await page.evaluate(({dt})=>{
  const X=window.__bf,h=X.root,ra=X.ringArea;
  X.setMouse(-1000,-1000);
  const step=()=>window.__step();for(let i=0;i<Math.ceil(3600/dt);i++)step();
  const scenes=[],frames=[];
  for(const scene of ['hero','sidebar','frame','bento','flock']){
   document.querySelector('[data-scene="'+scene+'"]').click();
   const rows=[],outside0=new Map((h.bufferStorage?[...h.bufferStorage]:[]).map(([b,a])=>[b.id,a.outside]));
   for(let f=0;f<Math.ceil(5500/dt);f++){
    const t0=window.__realNow();step();const ms=window.__realNow()-t0;
    const bodies=h.bodies.filter(b=>!b.isVoid&&!b.leaving).map(b=>{
     const a=h.bufferStorage?.get(b)||{visible:b.paintArea,total:b.paintArea,outside:0};
     let perimeter=0,points=0;for(const l of b.loops||[])for(let k=0;k<l.length;k++){perimeter+=Math.hypot(l[k][0]-l[(k+1)%l.length][0],l[k][1]-l[(k+1)%l.length][1]);points++;}
     const all=(b.loops||[]).flat(), hull=all.length?X.convexHull(all):[],hullArea=hull.length?Math.abs(ra(hull)):0;
     return {id:b.id,x:b.x,y:b.y,...a,perimeter,points,concavity:hullArea?1-b.paintArea/hullArea:0,cr:b.crystal};
    });
    const row={scene,f,t:h.t,ms,credit:h.bufferCredit||0,outside:h.bufferActualOutside||0,contentOutside:h.bufferContentOutside||0,voidOutside:h.bufferVoidOutside||0,quotaError:h.bufferQuotaError||0,allocations:h.bufferAllocations||[],reserve:h.bufferReserveArea||0,ledger:h.bufferLedgerError||0,visibleError:h.bufferVisibleError||0,bodies};rows.push(row);frames.push(row);
   }
   const maxRow=rows.reduce((a,b)=>a.contentOutside>b.contentOutside?a:b);
   scenes.push({scene,maxContentOutside:Math.max(...rows.map(r=>r.contentOutside)),maxVoidOutside:Math.max(...rows.map(r=>r.voidOutside)),maxQuotaError:Math.max(...rows.map(r=>r.quotaError)),peakContentFrame:maxRow.f,peakContentBodies:maxRow.bodies, routes:(h.bufferRouteHistory||[]).filter(r=>r.scene===scene),maxOutside:Math.max(...rows.map(r=>r.outside)),maxCredit:Math.max(...rows.map(r=>r.credit)),maxLedger:Math.max(...rows.map(r=>r.ledger)),maxVisibleError:Math.max(...rows.map(r=>r.visibleError)),minVisible:Math.min(...rows.flatMap(r=>r.bodies.map(b=>b.visible))),maxStorageError:Math.max(...rows.map(r=>Math.abs(r.outside-r.credit))),endOutside:rows.at(-1).outside,endCredit:rows.at(-1).credit,maxOutsideFraction:Math.max(...rows.flatMap(r=>r.bodies.map(b=>b.outside/Math.max(1,b.total))))});
  }
  return {scenes,frames};
 },{dt});
 await browser.close();fs.writeFileSync(out,JSON.stringify({src,dt,options,errors,...result}));console.log(JSON.stringify({errors,scenes:result.scenes}));
})().catch(e=>{console.error(e);process.exit(1)});
