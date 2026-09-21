const fs = require('node:fs');
const { performance } = require('node:perf_hooks');

function loadEngine(file, width = 1900, height = 810, fields = 0, count = 12) {
  const html = fs.readFileSync(file, 'utf8');
  let js = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const end = js.lastIndexOf('})();');
  js = js.slice(0, end) + `return {root, config, init, advance(dt) {
    simTime += dt; guestLeft = changeEnds(root) - simTime;
    root.step(dt, simTime); picture = buildPicture(root);
    return picture;
  }, end() {return changeEnds(root);}, time() {return simTime;}, scene(name) {config.scene=name; root.enterScene(name);}};\n` + js.slice(end);
  const noop = () => {};
  const el = {addEventListener:noop,style:{},classList:{toggle:noop},
    getContext:()=>({setTransform:noop}),
    parentElement:{getBoundingClientRect:()=>({width,height})}};
  const doc = {readyState:'loading',addEventListener:noop,
    getElementById:()=>el,querySelectorAll:()=>[]};
  const engine = Function('document','window','requestAnimationFrame','performance','return '+js.trim())(
    doc,{addEventListener:noop,devicePixelRatio:1},noop,performance);
  engine.config.fieldDensity = fields;
  engine.config.count = count;
  engine.init();
  return engine;
}

function measures(root) {
  const out = new Map();
  for (const b of root.bodies) {
    if (b.isVoid || b.isSelf || !b.loops) continue;
    let a2=0,x=0,y=0;
    for (const p of b.loops) for (let i=0;i<p.length;i++) {
      const q=p[(i+1)%p.length], z=p[i][0]*q[1]-q[0]*p[i][1];
      a2+=z; x+=(p[i][0]+q[0])*z; y+=(p[i][1]+q[1])*z;
    }
    if (Math.abs(a2)>1e-6) out.set(b.id,{area:Math.abs(a2/2),x:x/(3*a2),y:y/(3*a2)});
  }
  return out;
}

function displacement(a,b) {
  let px=0,area=0;
  for (const [id,p] of a) {
    const q=b.get(id); if (!q) continue;
    px=Math.max(px,Math.hypot(p.x-q.x,p.y-q.y));
    area=Math.max(area,Math.abs(p.area-q.area)/p.area);
  }
  return {px,area};
}

module.exports={loadEngine,measures,displacement};
