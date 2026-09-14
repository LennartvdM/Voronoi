// Astra I root partition: one shared weight per body, several sites
// per forming rectangle. Sites of one body compete together, not for a
// separate quota each. The domain never loses an arriving body as a hole.
function astraGroupSolve(seeds, owner, targets, w0, bounds, maxIter = 16) {
  const n = targets.length, area = Math.abs(ringArea(bounds));
  const sum = targets.reduce((a, b) => a + b, 0);
  const target = targets.map(a => a * area / sum);
  let w = Float64Array.from(w0), evaluations = 0;
  const evaluate = ws => {
    const diagram = computeDiagram(seeds, owner.map(i => ws[i]), bounds);
    const areas = new Float64Array(n);
    diagram.areas.forEach((a, i) => { areas[owner[i]] += a; });
    evaluations++;
    return { diagram, areas };
  };
  let current = evaluate(w);
  // A whole body, rather than an individual lattice site, must stay alive.
  for (let pass = 0; pass < 3 && minOf(current.areas) <= 0; pass++) {
    for (let i = 0; i < n; i++) {
      if (current.areas[i] > 0) continue;
      let lo = -8 * area - Math.max(...Array.from(w, Math.abs));
      let hi = -lo;
      for (let k = 0; k < 36; k++) {
        const mid = (lo + hi) / 2; w[i] = mid;
        if (evaluate(w).areas[i] < target[i]) lo = mid; else hi = mid;
      }
      w[i] = (lo + hi) / 2;
      current = evaluate(w);
    }
  }
  const floor = .5 * Math.min(minOf(target), minOf(current.areas));
  let iterations = 0, maxRel = Infinity;
  for (; iterations < maxIter; iterations++) {
    const residual = target.map((a, i) => a - current.areas[i]);
    maxRel = Math.max(...residual.map((a, i) => Math.abs(a) / target[i]));
    if (maxRel <= 1e-6) break;
    const J = Array.from({length:n}, () => new Float64Array(n));
    current.diagram.cells.forEach((c, i) => {
      const a = owner[i];
      for (let k = 0; k < c.pts.length; k++) {
        const j = c.labs[k];
        if (j < 0 || owner[j] === a) continue;
        const p = c.pts[k], q = c.pts[(k + 1) % c.pts.length];
        const d = Math.hypot(seeds[i][0] - seeds[j][0], seeds[i][1] - seeds[j][1]);
        if (d > 1e-9) J[a][owner[j]] -= Math.hypot(q[0] - p[0], q[1] - p[1]) / (2 * d);
      }
    });
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) J[i][j] = J[j][i] = .5 * (J[i][j] + J[j][i]);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== j) J[i][i] -= J[i][j];
    const dw = solvePinned(J, residual), norm = norm2(residual);
    let accepted = false;
    for (let t = 1, k = 0; k < 35; k++, t /= 2) {
      const nextW = Float64Array.from(w, (x, i) => x + t * dw[i]);
      if (!nextW.every(Number.isFinite)) break;
      const next = evaluate(nextW);
      if (minOf(next.areas) >= floor && norm2(target.map((x, i) => x - next.areas[i])) <= (1 - t / 2) * norm) {
        w = nextW; current = next; accepted = true; break;
      }
    }
    if (!accepted) break;
  }
  maxRel = Math.max(...target.map((a, i) => Math.abs(a-current.areas[i])/a));
  const mean = w.reduce((a,b)=>a+b,0) / n;
  w = w.map(x=>x-mean);
  return {weights: owner.map(i=>w[i]), groupWeights:w, diagram:current.diagram,
    maxRelErr:maxRel, converged:maxRel<=1e-6, iterations, evals:evaluations};
}

const astraOldWalls = Hive.prototype.computeWalls;
Hive.prototype.computeWalls = function() {
  if (this.depth !== 0) return astraOldWalls.call(this);
  this.walls = []; this.holes = [];
  for (const b of this.bodies) {
    b.wall = null; b.hole = null; b.holeCore = null; b.holeLinger = false; b.holeExtra = [];
  }
};
const astraOldPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  if (this.depth !== 0) return astraOldPlace.call(this);
  for (const b of this.bodies) {
    if (b.formRect !== b.rect && b.crystal === 0) b.formRect = b.rect;
    const r = b.formRect, mix = b.crystal;
    const weight = b.subs[0] ? b.subs[0].w : 0;
    const sites = [];
    const claim = b.claim * (1 + (config.hoverBoost - 1) * b.hoverMix * (1 - mix));
    if (r && mix > 1e-5) {
      const [cx, cy] = this.rectCenter(r);
      for (let y = r[1]; y < r[3]; y++) for (let x = r[0]; x < r[2]; x++) {
        sites.push({body:b, x:b.x+mix*((x+.5)*this.PW-cx), y:b.y+mix*((y+.5)*this.PH-cy), w:weight, claim, live:true});
      }
    }
    if (!sites.length) sites.push({body:b,x:b.x,y:b.y,w:weight,claim,live:true});
    b.subs = sites;
  }
};
const astraOldSolve = Hive.prototype.solve;
Hive.prototype.solve = function() {
  if (this.depth !== 0) return astraOldSolve.call(this);
  const groups = this.bodies.filter(b=>b.subs[0].claim >= ACTIVE_MIN);
  const subs = groups.flatMap(b=>b.subs), indices = new Map(groups.map((b,i)=>[b,i]));
  const owners = subs.map(s=>indices.get(s.body)), seeds = subs.map(s=>[s.x,s.y]);
  const claims = groups.map(b=>b.subs[0].claim), w0 = groups.map(b=>b.subs[0].w);
  const allSeated = groups.length && groups.every(b=>b.rect && b.formRect===b.rect && b.crystal===1 && !b.leaving);
  const t0 = performance.now();
  let sol;
  if (allSeated) {
    const key = [this.W, this.H, ...groups.flatMap(b => [b.id, ...b.rect])].join(',');
    if (this.astraRestKey === key && this.solved) sol = this.solved;
    else {
      const weights = seeds.map(() => 0), diagram = computeDiagram(seeds, weights, this.domainPts());
      sol = { weights, diagram, maxRelErr: 0, converged: true, iterations: 0 };
    }
    this.astraRestKey = key;
    this.walls=groups;
    for (const b of groups) b.wall=[b.rect[0]*this.PW,b.rect[1]*this.PH,b.rect[2]*this.PW,b.rect[3]*this.PH];
  } else {
    this.astraRestKey = null;
    sol = astraGroupSolve(seeds, owners, claims, w0, this.domainPts());
  }
  this.solveMs=performance.now()-t0; this.lastIters=sol.iterations;
  this.solved=sol; this.solvedSubs=subs; this.ownerOf=subs.map(s=>s.body.id);
  subs.forEach((s,i)=>{s.w=sol.weights[i];});
  this.shadowOn=false; this.shadowAt=null; this.ground=null; this.exact=true;
  this.recordAreas();
};
