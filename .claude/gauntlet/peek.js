// peek.js <hive> <frame0> <frame1> <bodyId>: drive the fixed clock like score.js and print one body's hole state per frame
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs'),path=require('path'),os=require('os');
const SRC=path.resolve(process.argv[2]); const F0=+process.argv[3], F1=+process.argv[4], ID=+process.argv[5];
const s=fs.readFileSync(SRC,'utf8'); const i=s.lastIndexOf('})();');
const dst=path.join(os.tmpdir(),'peek-'+Buffer.from(SRC).toString('hex').slice(-16)+'.html');
fs.writeFileSync(dst, s.slice(0,i)+`\n window.__X={fn:(n)=>({root,ringArea,picture,MELT,HOLE_TAU})[n], setMouse:(x,y)=>{mouseX=x;mouseY=y;}};\n`+s.slice(i));
const CLOCK=`(() => { let t=0; const q=[]; window.requestAnimationFrame=(cb)=>{q.push(cb);return q.length;}; window.cancelAnimationFrame=()=>{}; performance.now=()=>t; window.__advance=(n)=>{for(let i=0;i<n;i++){t+=1000/60; const cbs=q.splice(0); for(const cb of cbs) cb(t);}}; })();`;
(async()=>{
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1440,height:900}}); await p.addInitScript(CLOCK); await p.goto('file://'+dst); await p.waitForTimeout(300);
const out=await p.evaluate(({F0,F1,ID})=>{ const X=window.__X, r=X.fn('root'), ra=X.fn('ringArea'); X.setMouse(700,400); const lines=[]; let n=0;
  const step=()=>{ window.__advance(1); n++; };
  const scenes=['bento','hero','sidebar','frame','flock']; let next=120, si=0;
  const A=pc=>Math.round(Math.abs(ra(pc))/1000);
  while(n<=F1){ if(n===next && si<scenes.length){ document.querySelector('.scene-btn[data-scene="'+scenes[si]+'"]').click(); si++; next+=330; }
    step();
    if(n>=F0){ const bd=r.bodies.find(b=>b.id===ID); const j=bd.journey||{}; const line={f:n, t:+r.t.toFixed(3), cr:+bd.crystal.toFixed(3), pin:+bd.pin.toFixed(3), lv:!!bd.leaving, rect:bd.rect?bd.rect.map(v=>Math.round(v)):null, formRect:bd.formRect?bd.formRect.map(v=>+v.toFixed(3)):null, j:{t0:+(j.t0||0).toFixed(2),delay:+(j.delay||0).toFixed(2),hold:j.hold,dur:j.dur,c0:j.c0}, xy:[Math.round(bd.x),Math.round(bd.y)], wall:!!bd.wall, hole:bd.hole?{pieces:bd.hole.pieces.map(A), raw:bd.hole.raw.map(A), planes:bd.hole.planes.length, rect:bd.hole.rect.map(v=>Math.round(v))}:null, core:bd.holeCore&&bd.holeCore.core?A(bd.holeCore.core):0, coreN:bd.holeCore&&bd.holeCore.core?bd.holeCore.core.length:0, sideOn:!!bd.sideOn, linger:!!bd.holeLinger, walls:r.walls.map(w=>w.id), holes:r.holes.map(h=>h.id+'@'+h.crystal.toFixed(2)) };
      const leaf=X.fn('picture').leaves.find(l=>l.path[0].body===bd); line.leafA=leaf?Math.round(leaf.loops.reduce((s,lp)=>s+(lp.hole?-1:1)*Math.abs(ra(lp)),0)/1000):null; line.leafPieces=leaf?leaf.pieces.map(pc=>A(pc.pts)):null;
      lines.push(JSON.stringify(line)); } }
  return lines; },{F0,F1,ID});
console.log(out.join('\n')); await b.close(); })();
