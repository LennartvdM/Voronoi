const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine,measures,displacement}=require('./probe.cjs');
const {rectangleError}=require('./validate.cjs');
const files={harbor:path.join(__dirname,'harbor.html'),cadence:path.resolve(__dirname,'../../cadence.html')};
const advance=(e,s)=>{for(let t=0;t<s;t+=.03)e.advance(.03);};
function validate(e){for(const b of e.root.bodies){if(b.isVoid||b.isSelf||b.leaving)continue;assert.equal(b.subs.length,1);assert(b.loops?.length);assert([b.x,b.y,b.progress,b.claim].every(Number.isFinite));}assert.equal(e.root.holes.length,0);assert.equal(e.root.walls.length,0);}
function caught(e){return e.root.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving).every(b=>!b.journey||b.progress>=.999999);}
const interruptions=[],sizes=[],governor=[];
for(const name of Object.keys(files))for(const delay of[.08,.23,.6]){
 const e=loadEngine(files[name],1900,810,.55,12);advance(e,12);e.scene('frame');advance(e,15);let maxOpening=0,maxSlip=0;
 for(const to of['sidebar','hero','bento','frame','hero']){const prev=measures(e.root);e.scene(to);e.advance(1e-6);maxOpening=Math.max(maxOpening,displacement(prev,measures(e.root)).px);advance(e,delay);validate(e);}
 for(let t=0;t<18;t+=.03){e.advance(.03);for(const b of e.root.bodies)maxSlip=Math.max(maxSlip,b.journey?.cadenceSlip||0);validate(e);}
 assert(caught(e));interruptions.push({name,delay,maxOpening,maxSlip});
}
for(const [w,h,n]of[[390,760,12],[1440,620,24],[1900,810,13],[2560,1440,12]])for(const scene of['hero','frame','sidebar']){
 const e=loadEngine(files.cadence,w,h,.55,n);advance(e,12);e.scene(scene);advance(e,24);validate(e);assert(caught(e));
 const voidPct=rectangleError(e.root);if(scene!=='sidebar')assert(voidPct!==null&&voidPct<.001,'resting rectangle changed at another size/count');
 sizes.push({w,h,n,scene,voidPct,remaining:e.end()-e.time(),content:e.root.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving).length});
}
// A controlled obstruction tests the dormant catch-up branch: hold one seed
// back briefly while its journey runs, then release. This is a test fixture,
// not a production pin or a claim about how often real layouts need it.
{
 const e=loadEngine(files.cadence,1900,810,0,12);advance(e,12);e.scene('sidebar');e.advance(.03);
 const b=e.root.bodies.filter(b=>!b.isVoid&&b.path).sort((a,b)=>b.journey.dur-a.journey.dur)[0],j=b.journey;
 const x=b.x,y=b.y;let maxSlip=0,minRate=1;for(let t=0;t<9;t+=.03){if(t<6){b.x=x;b.y=y;b.vx=0;b.vy=0;}e.advance(.03);maxSlip=Math.max(maxSlip,j.cadenceSlip);minRate=Math.min(minRate,j.cadence.rate);assert(e.end()>=j.t0+j.delay+j.dur+j.cadenceSlip);}
 advance(e,22);assert(caught(e));assert(maxSlip>.1);assert(minRate<.9);governor.push({maxSlip,minRate,finished:!b.journey||b.progress>=.999999});
}
// Resize mid-flight, then use normal scene rebuilding and check eventual rest.
for(const scene of['hero','frame']){const e=loadEngine(files.cadence,1900,810,.55,12);advance(e,12);e.scene(scene);advance(e,.5);e.root.fit([0,0,1440,720],[[0,0],[1440,0],[1440,720],[0,720]],true,0,0);advance(e,20);validate(e);assert(caught(e));assert(rectangleError(e.root)<.001);}
fs.writeFileSync(path.join(__dirname,'edge-results.json'),JSON.stringify({interruptions,sizes,governor,resizesPassed:2},null,2)+'\n');console.log(JSON.stringify({interruptions,sizes,governor,resizesPassed:2}));
