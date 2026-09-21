// Geometry and crossing diagnostics for the real inline engines. DOM/paint
// are stubbed; the nested-field geometry and final picture are evaluated.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine,measures,displacement}=require('./probe.cjs');
const {rectangleError,check}=require('./geometry.cjs');
const files={harbor:path.join(__dirname,'harbor.html'),ferry:path.resolve(__dirname,'../../ferry.html')};
const clocks={hz60:i=>1/60,ms30:i=>.03,jitter:i=>.025+.012*Math.sin(i*1.7)};
const scenes=['flock','bento','hero','sidebar','frame'];
function advance(e,s){let picture;for(let t=0;t<s;t+=.03)picture=e.advance(.03);return picture;}
function leafMeasures(picture){const out=new Map();for(const l of picture.leaves){if(l.isVoid||l.fade<.5)continue;let a=0,x=0,y=0;for(const p of l.loops)for(let i=0;i<p.length;i++){const q=p[(i+1)%p.length],z=p[i][0]*q[1]-q[0]*p[i][1];a+=z;x+=(p[i][0]+q[0])*z;y+=(p[i][1]+q[1])*z;}if(Math.abs(a)>1000)out.set(l.body,{x:x/(3*a),y:y/(3*a),area:Math.abs(a/2)});}return out;}
const percentile=(a,p)=>a.length?[...a].sort((x,y)=>x-y)[Math.min(a.length-1,Math.floor(a.length*p))]:0;
function crossing(name,from,to,clock,w=1900,h=810,n=12){
 const e=loadEngine(files[name],w,h,.55,n);advance(e,10);e.scene(from);let picture=advance(e,12);
 let prev=measures(e.root),leaves=leafMeasures(picture),maxRootSpeed=0,maxLeafSpeed=0,fastBodySeconds=0,finish=0,maxSeedSpeed=0,previousSeed=new Map(e.root.bodies.map(b=>[b.id,[b.x,b.y]])),speeds=[];
 e.scene(to);const durations=e.root.bodies.filter(b=>!b.isVoid&&!b.leaving).map(b=>({id:b.id,delay:b.journey?.delay||0,duration:b.journey?.dur||0}));
 const end=e.end()-e.time();e.advance(1e-6);const opening=displacement(prev,measures(e.root)).px;prev=measures(e.root);
 let t=0,i=0;
 while(t<9){const dt=clocks[clock](i++);t+=dt;picture=e.advance(dt);check(e.root);const now=measures(e.root),nextLeaves=leafMeasures(picture);
  for(const [id,p]of prev){const q=now.get(id);if(q){const speed=Math.hypot(q.x-p.x,q.y-p.y)/dt;maxRootSpeed=Math.max(maxRootSpeed,speed);speeds.push(speed);if(speed>100/.03)fastBodySeconds+=dt;}}
  for(const [id,p]of leaves){const q=nextLeaves.get(id);if(q)maxLeafSpeed=Math.max(maxLeafSpeed,Math.hypot(q.x-p.x,q.y-p.y)/dt);}
  let active=false;for(const b of e.root.bodies){if(b.isVoid||b.isSelf||b.leaving)continue;active||=!!b.journey&&b.progress<.999999;const old=previousSeed.get(b.id);if(old)maxSeedSpeed=Math.max(maxSeedSpeed,Math.hypot(b.x-old[0],b.y-old[1])/dt);previousSeed.set(b.id,[b.x,b.y]);}
  if(active)finish=t;prev=now;leaves=nextLeaves;
 }
 assert(finish<8,'journey did not finish');
 const voidPct=rectangleError(e.root);if(['hero','frame'].includes(to))assert(voidPct!==null&&voidPct<.001,'resting rectangle changed');
 assert(!e.root.bodies.some(b=>b.isVoid&&b.leaving),'retiring void stuck');
 return {opening,maxRootSpeed,rootP95:percentile(speeds,.95),maxLeafSpeed,fastBodySeconds,maxSeedSpeed,finish,end,voidPct,durations};
}
const crossings=[];
for(const clock of ['hz60','ms30','jitter'])for(const from of['frame','hero']){
 const row={from,to:'sidebar',clock};for(const name of Object.keys(files))row[name]=crossing(name,from,'sidebar',clock);
 // Regression gate for the reported cases, not an aesthetic certification.
 assert(row.ferry.maxRootSpeed<row.harbor.maxRootSpeed*.4,'reported crossing spike did not materially improve');
 assert(row.ferry.finish<=row.harbor.finish+.15,'crossing took longer');
 for(const a of row.harbor.durations){const b=row.ferry.durations.find(b=>b.id===a.id);assert(Math.abs(a.duration-b.duration)<.01,'journey length changed');}
 crossings.push(row);console.log(JSON.stringify(row));
}
const otherTransitions=[];
for(const from of scenes)for(const to of scenes){if(from===to||to==='sidebar'&&['frame','hero'].includes(from))continue;const result=crossing('ferry',from,to,'ms30');delete result.durations;otherTransitions.push({from,to,...result});}
const edgeCases=[];
for(const [w,h,n]of[[390,760,12],[1440,620,24],[1900,810,13],[2560,1440,12]])for(const from of['hero','frame']){const r=crossing('ferry',from,'sidebar','ms30',w,h,n);delete r.durations;edgeCases.push({w,h,n,from,...r});}
const interruptions=[];
for(const name of Object.keys(files))for(const delay of[.08,.23,.6]){
 const e=loadEngine(files[name],1900,810,.55,12);advance(e,10);e.scene('frame');advance(e,12);let opening=0;
 for(const to of['sidebar','hero','bento','frame','hero']){const prev=measures(e.root);e.scene(to);e.advance(1e-6);opening=Math.max(opening,displacement(prev,measures(e.root)).px);advance(e,delay);check(e.root);}
 advance(e,14);check(e.root);assert(rectangleError(e.root)<.001);assert(!e.root.bodies.some(b=>b.isVoid&&b.leaving));interruptions.push({name,delay,opening});
}
for(const to of['hero','frame','sidebar']){
 const e=loadEngine(files.ferry,1900,810,.55,12);advance(e,10);e.scene('frame');advance(e,12);e.scene(to);advance(e,.5);e.root.fit([0,0,1440,720],[[0,0],[1440,0],[1440,720],[0,720]],true,0,0);advance(e,16);check(e.root);if(to!=='sidebar')assert(rectangleError(e.root)<.001);
 e.root.setCount(15);advance(e,12);check(e.root);assert.equal(e.root.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving).length,15);
}
const hashes=Object.fromEntries(Object.entries(files).map(([n,f])=>[n,require('node:crypto').createHash('sha256').update(fs.readFileSync(f)).digest('hex')]));
const summary={crossings:crossings.length,otherTransitions:otherTransitions.length,edgeCases:edgeCases.length,interruptions,resizesAndRosterChanges:3};
fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify({scope:'Real solver and final leaf geometry; DOM and paint stubbed. Live Netlify evaluation remains required.',hashes,summary,crossings,otherTransitions,edgeCases},null,2)+'\n');console.log('SUMMARY',JSON.stringify(summary));
