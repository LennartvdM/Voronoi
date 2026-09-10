/* Do the free walls slide because the holes are morphing? Per frame: how much
 * hole boundary moved (sym diff of every hole's raster, 4px) against the
 * mean decided slide of the free walls, transitions only, no hover. */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs'),path=require('path'),os=require('os');
const SRC=path.resolve(process.argv[2]||'hive.html'); const DT=+(process.argv[3]||30);
const s=fs.readFileSync(SRC,'utf8'); const i=s.lastIndexOf('})();');
const dst=path.join(os.tmpdir(),'hm-'+require('crypto').createHash('sha1').update(SRC+DT).digest('hex').slice(0,12)+'.html');
fs.writeFileSync(dst, s.slice(0,i)+`\n window.__X={fn:(n)=>({root,ringArea,W,H})[n], setMouse:(x,y)=>{mouseX=x;mouseY=y;}};\n`+s.slice(i));
const CLOCK=`(()=>{let t=0;const q=[];window.requestAnimationFrame=(cb)=>{q.push(cb);return q.length;};window.cancelAnimationFrame=()=>{};performance.now=()=>t;window.__advance=(n)=>{for(let i=0;i<n;i++){t+=${DT};const c=q.splice(0);for(const f of c)f(t);}};})();`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1440,height:900}}); await p.addInitScript(CLOCK); await p.goto('file://'+dst); await p.waitForTimeout(300);
const out=await p.evaluate(()=>{const X=window.__X,r=X.fn('root');X.setMouse(-100,-100);
 const W=X.fn('W'),H=X.fn('H'),CELL=4,GW=Math.ceil(W/CELL),GH=Math.ceil(H/CELL);
 const fill=(m,lp)=>{let y0=Infinity,y1=-Infinity;for(const q of lp){y0=Math.min(y0,q[1]);y1=Math.max(y1,q[1]);}
   const r0=Math.max(0,Math.floor(y0/CELL)),r1=Math.min(GH-1,Math.floor(y1/CELL)),L=lp.length;
   for(let row=r0;row<=r1;row++){const sy=(row+0.5)*CELL,xs=[];for(let k=0;k<L;k++){const a=lp[k],b=lp[(k+1)%L];if((a[1]<=sy)!==(b[1]<=sy))xs.push(a[0]+(sy-a[1])*(b[0]-a[0])/(b[1]-a[1]));}
     xs.sort((u,v)=>u-v);for(let k=0;k+1<xs.length;k+=2){const c0=Math.max(0,Math.round(xs[k]/CELL)),c1=Math.min(GW,Math.round(xs[k+1]/CELL));for(let c=c0;c<c1;c++)m[row*GW+c]=1;}}};
 const L=[],marks=[]; let n=0, prev=null;
 const step=()=>{ window.__advance(1); n++;
   const m=new Uint8Array(GW*GH); let nh=0; for(const bd of r.holes){ nh++; for(const pc of bd.hole.pieces) fill(m,pc); }
   let sd=0, hA=0; for(let k=0;k<m.length;k++){ if(m[k]) hA++; if(prev&&m[k]!==prev[k]) sd++; } prev=m;
   const w={},x={},y={},nb={};
   if(r.solvedSubs&&r.solved) r.solvedSubs.forEach((sb,k)=>{const id=sb.body.id;w[id]=r.solved.weights[k];x[id]=sb.x;y[id]=sb.y;const c=r.solved.diagram.cells[k],seen={};const scan=(pc)=>{if(!pc||!pc.labs)return;for(const l of pc.labs)if(l>=0&&r.solvedSubs[l])seen[r.solvedSubs[l].body.id]=1;};scan(c);if(c&&c.pieces)for(const pc of c.pieces)scan(pc);nb[id]=Object.keys(seen).map(Number);});
   L.push({f:n,holeSd:sd*CELL*CELL,holeA:hA*CELL*CELL,nh,w,x,y,nb});
 };
 for(let i=0;i<120;i++) step();
 for(const sc of ['bento','hero','sidebar','frame','flock']){marks.push({f:n,scene:sc});document.querySelector('.scene-btn[data-scene="'+sc+'"]').click();for(let i=0;i<330;i++)step();}
 return {L,marks};});
await b.close();
const {L,marks}=out; const sceneOf=(f)=>{let s='flock0';for(const m of marks) if(f>=m.f) s=m.scene; return s;};
const rows=[];
for(let k=1;k<L.length;k++){const F=L[k],P=L[k-1];const sc=sceneOf(F.f); if(sc==='flock0'||sc==='bento') continue;
  let sum=0,nn=0;const done={};
  for(const id in F.nb)for(const j of F.nb[id]){if(j==id||!(id in P.w)||!(j in P.w)||!(j in F.w))continue;const key=Math.min(id,j)+'-'+Math.max(id,j);if(done[key])continue;done[key]=1;const d=Math.hypot(F.x[id]-F.x[j],F.y[id]-F.y[j]);if(!(d>1))continue;sum+=Math.abs((F.w[id]-F.w[j])-(P.w[id]-P.w[j]))/(2*d);nn++;}
  // the same pairs' seed travel this frame
  let tr=0,tn=0; for(const id in F.nb){ if(!(id in P.w)) continue; tr+=Math.hypot(F.x[id]-P.x[id],F.y[id]-P.y[id]); tn++; }
  if(nn) rows.push({sc,slide:sum/nn,trav:tn?tr/tn:0,holeSd:F.holeSd,nh:F.nh,holeA:F.holeA});}
const rank=(v)=>{const idx=v.map((x,i)=>[x,i]).sort((a,b)=>a[0]-b[0]);const r=new Array(v.length);idx.forEach(([,i],k)=>r[i]=k);return r;};
const sp=(a,b)=>{const ra=rank(a),rb=rank(b),n=a.length;let s=0;for(let i=0;i<n;i++){const d=ra[i]-rb[i];s+=d*d;}return +(1-6*s/(n*(n*n-1))).toFixed(3);};
console.log('transition frames with free walls:',rows.length);
console.log('Spearman  free-wall slide vs hole boundary moved (px2/frame):',sp(rows.map(r=>r.slide),rows.map(r=>r.holeSd)));
console.log('Spearman  free-wall slide vs number of holes            :',sp(rows.map(r=>r.slide),rows.map(r=>r.nh)));
const srt=rows.slice().sort((a,b)=>a.holeSd-b.holeSd);const D=5,per=Math.floor(srt.length/D);
console.log('\nquintile of hole motion   mean hole px2 moved/frame   holes   mean free-wall slide px');
for(let q=0;q<D;q++){const g=srt.slice(q*per,(q+1)*per);const m=(f)=>g.reduce((a,b)=>a+f(b),0)/g.length;
  console.log(String(q+1).padStart(8),String(Math.round(m(r=>r.holeSd))).padStart(22),String(m(r=>r.nh).toFixed(1)).padStart(8),String(m(r=>r.slide).toFixed(2)).padStart(20));}
const quiet=rows.filter(r=>r.nh===0), busy=rows.filter(r=>r.nh>0);
const amp=(g)=>{const t=g.reduce((a,b)=>a+b.trav,0)/g.length, d=g.reduce((a,b)=>a+b.slide,0)/g.length; return {frames:g.length, seedTravel:+t.toFixed(2), wallSlide:+d.toFixed(2), slidePerPxTravel:+(d/Math.max(1e-9,t)).toFixed(2)};};
console.log('\nAMPLIFICATION: wall slide per px of seed travel');
console.log('  no hole   :', JSON.stringify(amp(quiet)));
console.log('  with holes:', JSON.stringify(amp(busy)));
// and holding seed travel roughly fixed: bins of travel
const bins=[[0,2],[2,5],[5,10],[10,30]];
console.log('  by seed-travel bin (px/frame): no-hole slide vs with-hole slide');
for(const [lo,hi] of bins){ const q=quiet.filter(r=>r.trav>=lo&&r.trav<hi), b=busy.filter(r=>r.trav>=lo&&r.trav<hi);
  const m=(g)=>g.length?(g.reduce((a,c)=>a+c.slide,0)/g.length).toFixed(2):'-';
  console.log('    '+String(lo).padStart(3)+'-'+String(hi).padEnd(3),' no-hole',m(q),'('+q.length+' frames)   with-hole',m(b),'('+b.length+' frames)'); }
console.log('\nframes with NO hole at all:',quiet.length,' mean slide',quiet.length?(quiet.reduce((a,b)=>a+b.slide,0)/quiet.length).toFixed(2):'-','   with holes:',busy.length,' mean slide',(busy.reduce((a,b)=>a+b.slide,0)/busy.length).toFixed(2));
})().catch(e=>{console.error(e);process.exit(1);});
