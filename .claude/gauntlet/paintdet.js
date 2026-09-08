// paintdet.js <hive> [tag]: deterministic garment profile at the stress settings (30 elements, all fields, gap 28, corner 34), Hero then Sidebar
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs'),path=require('path'),os=require('os');
const SRC=path.resolve(process.argv[2]), TAG=process.argv[3]||'pd'; const s=fs.readFileSync(SRC,'utf8'); const i=s.lastIndexOf('})();');
const dst=path.join(os.tmpdir(),'pd-'+Buffer.from(SRC).toString('hex').slice(-16)+'.html');
fs.writeFileSync(dst, s.slice(0,i)+`\n const __g=garment; garment=(l,g,r)=>{const t=window.__realNow(); const o=__g(l,g,r); const dt=window.__realNow()-t; let cv=true; const n=l.length; const o0=ringArea(l)>0?1:-1; for(let k=0;k<n;k++){const a=l[(k+n-1)%n],b=l[k],c=l[(k+1)%n]; if(((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))*o0<-1e-6){cv=false;break;}} (window.__GT=window.__GT||[]).push([n,+dt.toFixed(2),o.cores.length,cv?1:0,Math.round(Math.abs(ringArea(l))),window.__frame|0, n>=24?l.map(q=>[+q[0].toFixed(1),+q[1].toFixed(1)]):null]); return o;};\n window.__X={setMouse:(x,y)=>{mouseX=x;mouseY=y;}};\n`+s.slice(i));
const CLOCK=`(() => { let t=0; const q=[]; const realNow=performance.now.bind(performance); window.__realNow=realNow; window.requestAnimationFrame=(cb)=>{q.push(cb);return q.length;}; window.cancelAnimationFrame=()=>{}; performance.now=()=>t; window.__advance=(n)=>{for(let i=0;i<n;i++){t+=1000/60; window.__frame=(window.__frame|0)+1; const cbs=q.splice(0); for(const cb of cbs) cb(t);}}; })();`;
(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1440,height:900}}); await p.addInitScript(CLOCK); await p.goto('file://'+dst); await p.waitForTimeout(300);
await p.evaluate(()=>{ const s=(id,v)=>{const el=document.getElementById(id); el.value=v; el.dispatchEvent(new Event('input'));}; s('fields','100'); s('count','30'); s('gap',28); s('corner',34); window.__X.setMouse(700,400); window.__advance(240); window.__GT=[]; });
for (const sc of ['hero','sidebar']) await p.evaluate((sc)=>{ document.querySelector('.scene-btn[data-scene="'+sc+'"]').click(); window.__advance(120); }, sc);
const T=await p.evaluate(()=>window.__GT); await b.close();
const buckets={}; let tot=0; for(const t of T){ const [n,dt,c,cv]=t; const k=(cv?'convex':'notched')+' '+(n<8?'<8':n<16?'8-15':n<24?'16-23':n<40?'24-39':'40+'); const B=buckets[k]=buckets[k]||{calls:0,ms:0,max:0}; B.calls++; B.ms+=dt; B.max=Math.max(B.max,dt); tot+=dt; }
console.log('calls',T.length,'total ms',tot.toFixed(0),'frames 240');
for(const k of Object.keys(buckets).sort()) console.log(' ',k.padEnd(16),'calls',String(buckets[k].calls).padStart(5),'ms',buckets[k].ms.toFixed(0).padStart(6),'max',buckets[k].max.toFixed(1));
const top=T.slice().sort((a,b)=>b[1]-a[1]).slice(0,5); console.log('top [verts, ms, cores, convex, area, frame]:', JSON.stringify(top.map(t=>t.slice(0,6))));
const dumps=T.filter(t=>t[6]).sort((a,b)=>b[1]-a[1]).slice(0,3);
if(dumps.length){ let svg='<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900"><rect width="1440" height="900" fill="#fff"/>'; const col=['#e33','#36f','#3a3'];
  dumps.forEach((t,k)=>{ const pts=t[6]; svg+=`<polygon points="${pts.map(q=>q.join(',')).join(' ')}" fill="${col[k]}" fill-opacity="0.15" stroke="${col[k]}" stroke-width="1"/>`; pts.forEach(q=>{ svg+=`<circle cx="${q[0]}" cy="${q[1]}" r="2.5" fill="${col[k]}"/>`; }); });
  svg+='</svg>'; fs.writeFileSync(path.join(__dirname,TAG+'-loops.svg'),svg); fs.writeFileSync(path.join(__dirname,TAG+'-loops.json'),JSON.stringify(T.filter(t=>t[6]).sort((a,b)=>b[1]-a[1]).slice(0,12).map(t=>({n:t[0],ms:t[1],area:t[4],frame:t[5],pts:t[6]}))));
  for(const t of dumps){ const pts=t[6]; const L=pts.map((q,j)=>{const r=pts[(j+1)%pts.length]; return Math.hypot(r[0]-q[0],r[1]-q[1]);}).sort((a,b)=>a-b); console.log('loop',t.slice(0,6).join('/'),'edges: min',L[0].toFixed(2),'p25',L[L.length>>2].toFixed(1),'median',L[L.length>>1].toFixed(1),'n<2px',L.filter(x=>x<2).length,'n<5px',L.filter(x=>x<5).length); } }
})();
