// cap.js <hive> <tag>: deterministic captures at chosen scene frames of the scorer's scenario
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs'),path=require('path'),os=require('os');
const SRC=path.resolve(process.argv[2]), TAG=process.argv[3]||'cap';
// the clock, as in score.js/flicker.js: a capture is a capture at a clock
const opt=(n,d)=>{const i=process.argv.indexOf(n); return i>=0?+process.argv[i+1]:d;};
const DT=opt('--dt',1000/60), JIT=opt('--jitter',0);
const s=fs.readFileSync(SRC,'utf8'); const i=s.lastIndexOf('})();');
const dst=path.join(os.tmpdir(),'cap-'+Buffer.from(SRC).toString('hex').slice(-16)+'.html');
fs.writeFileSync(dst, s.slice(0,i)+`\n window.__X={setMouse:(x,y)=>{mouseX=x;mouseY=y;}};\n`+s.slice(i));
const CLOCK=`(() => { let t=0, seed=12345; const q=[]; const DT=${DT}, JIT=${JIT};
  const rnd=()=>{ seed=(seed*1103515245+12345)&0x7fffffff; return seed/0x7fffffff; };
  window.requestAnimationFrame=(cb)=>{q.push(cb);return q.length;}; window.cancelAnimationFrame=()=>{}; performance.now=()=>t;
  window.__advance=(n)=>{for(let i=0;i<n;i++){t+=DT+(JIT?(2*rnd()-1)*JIT:0); const cbs=q.splice(0); for(const cb of cbs) cb(t);}}; })();`;
const WANT={hero:[12,30,60], sidebar:[18,30,60], frame:[20,40], flock:[12,18,24,40,80]};
(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1440,height:900}}); await p.addInitScript(CLOCK); await p.goto('file://'+dst); await p.waitForTimeout(300);
await p.evaluate(()=>{ window.__X.setMouse(700,400); window.__advance(120); });
for (const sc of ['bento','hero','sidebar','frame','flock']) {
  await p.evaluate((sc)=>{ document.querySelector('.scene-btn[data-scene="'+sc+'"]').click(); }, sc);
  let at=0; for (const f of (WANT[sc]||[])) { await p.evaluate((n)=>window.__advance(n), f-at); at=f; await p.screenshot({path:path.join(__dirname,`${TAG}-${sc}-${String(f).padStart(3,'0')}.png`), clip:{x:0,y:0,width:1440,height:760}}); }
  await p.evaluate((n)=>window.__advance(n), 330-at);
}
await b.close(); })();
