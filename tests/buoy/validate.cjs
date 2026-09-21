// Run the actual inline solver and its own pointer-routing block. Canvas
// paint is stubbed; root outlines and final nested leaf geometry are real.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {loadEngine,measures}=require('./probe.cjs');
const {rectangleError,check}=require('./geometry.cjs');
const files={ferry:path.join(__dirname,'ferry.html'),buoy:path.resolve(__dirname,'../../buoy.html')};
const advance=(e,s)=>{let p;for(let t=0;t<s;t+=.03)p=e.advance(.03);return p;};
const geometry=p=>{let a=0,x=0,y=0;for(const ring of p)for(let i=0;i<ring.length;i++){const q=ring[(i+1)%ring.length],z=ring[i][0]*q[1]-q[0]*ring[i][1];a+=z;x+=(ring[i][0]+q[0])*z;y+=(ring[i][1]+q[1])*z;}return{area:Math.abs(a/2),x:x/(3*a),y:y/(3*a)};};
const hovering=[];
for(const scene of['bento','sidebar','frame','hero'])for(const name of Object.keys(files)){
 const e=loadEngine(files[name],1900,810,0,12);advance(e,10);e.scene(scene);advance(e,12);
 const b=e.root.bodies.find(b=>!b.isVoid&&!b.isSelf&&!b.leaving),before=measures(e.root).get(b.id);
 e.pointer(before.x,before.y);advance(e,2);check(e.root);assert.equal(e.root.hoveredId,b.id);assert(b.hoverMix>.99);
 const ratio=measures(e.root).get(b.id).area/before.area;
 if(name==='ferry')assert(Math.abs(ratio-1)<.001,'control no longer reproduces inert hover');else assert(ratio>1.4&&ratio<1.61,'hover did not request and receive more area');
 e.pointer(-1e9,-1e9);advance(e,5);check(e.root);const restored=measures(e.root).get(b.id).area/before.area;assert(Math.abs(restored-1)<.001,'hover did not release');
 const voidPct=rectangleError(e.root);if(['hero','frame'].includes(scene))assert(voidPct<.001);
 hovering.push({name,scene,ratio,restored,voidPct});
}
// Slider endpoints and a fixed pointer moving onto another cell.
const slider=[];
for(const boost of[1,2.6]){
 const e=loadEngine(files.buoy);advance(e,12);e.config.hoverBoost=boost;
 const b=e.root.bodies.find(b=>!b.isVoid&&!b.isSelf),before=measures(e.root).get(b.id);e.pointer(before.x,before.y);advance(e,2);
 const ratio=measures(e.root).get(b.id).area/before.area;
 if(boost===1)assert(Math.abs(ratio-1)<.001);else assert(ratio>1.8&&ratio<2.61);slider.push({boost,ratio});
 const next=e.root.bodies.find(q=>!q.isVoid&&!q.isSelf&&q!==b),point=measures(e.root).get(next.id);e.pointer(point.x,point.y);advance(e,3);assert.equal(e.root.hoveredId,next.id);assert(b.hoverMix<.001);check(e.root);
}
// Hover a child through the real hit path, in organic and grid interiors.
const nested=[];
for(const inner of['organic','grid']){
 const e=loadEngine(files.buoy,1900,810,.55,12);const innerScene=inner==='grid'?'bento':'flock';e.config.inner=innerScene;e.root.walk(h=>{if(h.depth>0)h.enterScene(innerScene);});const p=advance(e,16);
 const candidates=p.leaves.filter(l=>!l.isVoid&&l.path.length>1).sort((a,b)=>geometry(b.loops).area-geometry(a.loops).area);
 assert(candidates.length,'nested fixture missing');const leaf=candidates[0],before=geometry(leaf.loops),parent=leaf.path[0].body;
 const parentBefore=measures(e.root).get(parent.id).area;e.pointer(before.x,before.y);let after=advance(e,3);
 const same=after.leaves.find(l=>l.body===leaf.body);assert(same,'hovered child vanished');assert(leaf.body.hoverMix>.9,'child did not receive pointer');assert(parent.hoverMix>.9,'parent did not receive pointer');
 const ratio=geometry(same.loops).area/before.area,parentRatio=measures(e.root).get(parent.id).area/parentBefore;
 assert(ratio>1.1&&parentRatio>1.1,'nested hover did not grow');check(e.root);
 e.pointer(-1e9,-1e9);advance(e,6);assert(parent.hoverMix<.001);nested.push({inner,ratio,parentRatio});
}
// Exact equality with Ferry while there is no hover, including interruptions
// and both accepted void crossings. Geometry and claims, not timing metrics.
const engines=Object.values(files).map(f=>loadEngine(f,1900,810,.55,12));let comparedFrames=0;
function shape(e,p){return {root:e.root.bodies.map(b=>({id:b.id,x:b.x,y:b.y,claim:b.claim,progress:b.progress,subs:b.subs.map(s=>[s.x,s.y,s.claim,s.w]),loops:b.loops})),leaves:p.leaves.map(l=>({ids:l.path.map(x=>x.body.id),loops:l.loops}))};}
function together(s){for(let t=0;t<s;t+=.03){const p=engines.map(e=>e.advance(.03));assert.deepEqual(shape(engines[0],p[0]),shape(engines[1],p[1]),'Ferry motion changed without hover');comparedFrames++;}}
together(10);for(const [scene,seconds]of[['frame',8],['sidebar',8],['hero',8],['sidebar',8],['flock',5],['bento',5],['frame',.6],['hero',.23],['sidebar',8]]){for(const e of engines)e.scene(scene);together(seconds);}
// Depart while still hovered: the existing guest rule must relinquish the
// request, keep all cells alive, and restore the target once it has arrived.
const release=[];
for(const from of['hero','frame']){
 const e=loadEngine(files.buoy,1900,810,.55,12);advance(e,10);e.scene(from);advance(e,12);const b=e.root.bodies.find(b=>!b.isVoid&&!b.isSelf),m=measures(e.root).get(b.id);e.pointer(m.x,m.y);advance(e,2);assert(b.hoverMix>.99);
 e.scene('sidebar');e.advance(.03);assert.equal(e.root.hoveredId,-1);for(let t=0;t<1;t+=.03){e.advance(.03);check(e.root);}const decay=b.hoverMix;assert(decay<.99);
 e.pointer(-1e9,-1e9);advance(e,12);check(e.root);assert(!e.root.bodies.some(b=>b.isVoid&&b.leaving));release.push({from,hoverAfterOneSecond:decay});
}
const hashes=Object.fromEntries(Object.entries(files).map(([n,f])=>[n,require('node:crypto').createHash('sha256').update(fs.readFileSync(f)).digest('hex')]));
const result={scope:'Actual solver and pointer routing; DOM/paint stubbed. Live Netlify hover remains the visual check.',hashes,hovering,slider,nested,comparedFrames,release};
fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
