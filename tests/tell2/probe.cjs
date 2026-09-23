const fs=require('node:fs');
const {performance}=require('node:perf_hooks');
function loadEngine(file,{width=1900,height=810,fields=.55,count=12,profile=false,record=false,transform=x=>x}={}) {
 let js=transform(fs.readFileSync(file,'utf8').match(/<script>([\s\S]*?)<\/script>/)[1]);
 const stats={},stack=[];
 const wrap=(name,fn)=>function(...args){
   const parent=stack.at(-1),entry={children:0},t=performance.now(); stack.push(entry);
   try{return fn.apply(this,args);}finally{const ms=performance.now()-t; stack.pop(); if(parent)parent.children+=ms;
   const s=stats[name]||(stats[name]={calls:0,ms:0,self:0});s.calls++;s.ms+=ms;s.self+=ms-entry.children;}
 };
 const functions=['tick','computeDiagram','solveWeights','buildJacobian','solvePinned','leafOutlines','splitAtVertices','unionOutlines','buildPicture','paintPicture','garment','inkPath','roundedPath','contentStep','inscribedPole','rasterCheck','shade','changeEnds'];
 const methods=['step','steer','computeWalls','separate','enforcePreconditions','easeClaims','placeSeeds','solve','solveMain','solveShadow','recordAreas','computeOutlines','computeShards','collectLeaves','collectShards','plSeamSites'];
 const instrument=profile?functions.map(n=>`if(typeof ${n}==='function') ${n}=wrap('${n}',${n});`).join('\n')+methods.map(n=>`if(Hive.prototype.${n}) Hive.prototype.${n}=wrap('Hive.${n}',Hive.prototype.${n});`).join('\n'):'';
 const end=js.lastIndexOf('})();');
 js=js.slice(0,end)+instrument+`\nreturn {root,config,init,resize,computeDiagram,solveWeights,rasterCheck,advance(ms){tick(ms);return picture;},pointer(x,y){mouseX=x;mouseY=y;},scene(n){config.scene=n;root.enterScene(n);},time(){return simTime;},changeLeft(){return guestLeft;},click(x,y){return portalClick(x,y);},home(){portalHome();},focus(){return portalFocus;},kinds(){return PORTAL_KINDS;},templates(){return PORTAL_TEMPLATES;},page(name,n){return portalScene(root,name,n);},flip(v){portalFlip=!!v;return portalFlip;},scroll(dy){return reelMove(dy);},tellStart(){tellStart();},tell2Start(){tell2Start();},tell2(){return tell2;},tell2Push(dy){return tell2Scroll(dy);},tell2Move(dy){if(!tell2)return false;tell2.y=Math.max(0,tell2.y+dy);return true;},tell2Go(k){if(tell2){tell2.y=k*H;}},slides2(){return TELL2_SLIDES;},tell2Page(k,n){return tell2Page(k,root.COLS,root.ROWS,n,W,H,tell2?tell2.story:tell2Plan(root.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving).sort((a,b)=>a.id-b.id)));},ring(n){return tell2Ring(n,W,H);},plan(){return tell2Plan(root.bodies.filter(b=>!b.isVoid&&!b.isSelf&&!b.leaving).sort((a,b)=>a.id-b.id));},tell2DragStart(x,y,t){return tell2DragStart(x,y,t);},tell2DragMove(x,y,t){return tell2DragMove(x,y,t);},tell2DragEnd(t){return tell2DragEnd(t);},complement(r){return tell2Complement(root.COLS,root.ROWS,r);},tell(){return tell;},tellPush(dy){return tellScroll(dy);},tellMove(dy){if(!tell)return false;tell.y=Math.max(0,tell.y+dy);return true;},tellGo(k){if(tell){tell.y=k*H;}},slides(){return TELL_SLIDES;},tellPage(n){return tellPage(root.COLS,root.ROWS,n,W,H);},tellDragStart(x,y,t){return tellDragStart(x,y,t);},tellDragMove(x,y,t){return tellDragMove(x,y,t);},tellDragEnd(t){return tellDragEnd(t);},wheel(dy){return reelScroll(dy);},drift(v){if(v!==undefined)reelDrift=v;return reelDrift;},flow(){return reel?reel.strips.map(S=>S.v):null;},dragStart(x,y,t){return reelDragStart(x,y,t);},dragMove(x,y,t){return reelDragMove(x,y,t);},dragEnd(t){return reelDragEnd(t);},reel(){return reel;},prose(){return portalProse;},garment,decorate(c,v,w){return portalDecorate(c,v,W,H,root.COLS,root.ROWS,w);},convexPlanes,graph(){return bodyGraph(root);},passage(o){return passageTimes(bodyGraph(root),root.sourcesFor(o,null),config.stagger,40+root.serial+1,root.shift);},scenes,rectsEqual,end(){return changeEnds(root);},inner(n){config.inner=n;root.walk(h=>{if(h.depth>0)h.enterScene(n);});}};\n`+js.slice(end);
 const noop=()=>{}, commands=[];
 const ctx={};
 for(const name of ['arc','arcTo','beginPath','clearRect','clip','closePath','fill','fillRect','fillText','lineTo','moveTo','restore','save','setTransform','stroke'])ctx[name]=record?(...a)=>commands.push([name,...a]):noop;
 // Plaque measures text (Portal inherits it); the stub answers with a deterministic width from the font's px size.
 ctx.measureText=s=>({width:0.58*parseFloat((String(ctx.font).match(/(\d+(?:\.\d+)?)px/)||[0,16])[1])*String(s).length});
 ctx.createLinearGradient=(...a)=>{if(record)commands.push(['createLinearGradient',...a]);return {addColorStop:record?(...b)=>commands.push(['addColorStop',...b]):noop};};
 const context=record?new Proxy(ctx,{set(obj,k,v){if(k!=='fillStyle'||typeof v!=='object')commands.push(['set',k,v]); obj[k]=v;return true;}}):ctx;
 const els=new Map();
 const el=id=>{if(!els.has(id))els.set(id,{addEventListener:noop,style:{},classList:{toggle:noop},getContext:()=>context,parentElement:{getBoundingClientRect:()=>({width,height})}});return els.get(id);};
 const doc={readyState:'loading',addEventListener:noop,getElementById:el,querySelectorAll:()=>[]};
 const e=Function('document','window','requestAnimationFrame','performance','wrap','return '+js.trim())(doc,{addEventListener:noop,devicePixelRatio:1},noop,performance,wrap);
 e.config.fieldDensity=fields;e.config.count=count;e.init();
 return Object.assign(e,{stats,commands,meters(){return Object.fromEntries([...els].filter(([k])=>k.startsWith('m')&& !['mIter','mInner'].includes(k)).map(([k,v])=>[k,[v.textContent,v.className]]));},clear(){commands.length=0;},size(w,h){width=w;height=h;e.resize();}});
}
function run(e,frames=1600,dt=1000/60){
 let pic;
 for(let f=0;f<frames;f++){
  if(f===200)e.scene('frame');
  if(f===500)e.scene('sidebar');
  if(f===800)e.scene('hero');
  if(f===1100)e.scene('sidebar');
  if(f===1350)e.scene('flock');
  if(f===450||f===740)e.pointer(350,350);
  if(f===490||f===790)e.pointer(-1e9,-1e9);
  pic=e.advance(1000+f*dt);
 }
 return pic;
}
module.exports={loadEngine,run};
if(require.main===module){
 for(const [count,fields] of [[12,.55],[24,1]]){
 const e=loadEngine(process.argv[2],{count,fields,profile:true});
 run(e);
 console.log(JSON.stringify({count,fields,total:e.stats.tick.ms,stats:Object.entries(e.stats).sort((a,b)=>b[1].self-a[1].self).map(([name,s])=>({name,calls:s.calls,total:+s.ms.toFixed(1),self:+s.self.toFixed(1)}))},null,2));
 }
}
