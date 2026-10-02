"""Build Facet from Cohort: the hive with straight edges, light and steady.

Three rules, each with its own switch.

FACET. While a page changes, a cell reaches into the sea as far as its own
rectangle: of its seat's proportions, centred on its seed, of area pi w (as a
disc of the same weight would be), its proportions turning from the seat it
leaves to the seat it takes as its size turns. Whitespace's own share reaches
as a square, so it stays about its seed instead of spreading between the
cells. Where it meets a neighbour it
is cut by their bisector, as ever. So every cell is a polygon, and a cell on
its own is a large Voronoi cell with the sides of its frame, never a disc.
The soft sea's grid cut, which drew a cell's shore square by square and then
merged the squares back into one outline, is not used: a cell is four clips
more than its power cell, and the Jacobian of a side is exact (a side moves out
by its half side's own change).

STEADY. A site that holds no ground as a solve of the page's begins has no
edge, so no step of Newton's can give it any. On Cohort such a site (a
whitespace's seam site standing in a settled cell) stopped the whole auction
after one step, frame after frame, and the page held and then jumped. Here it
sits the solve out, its weight as it is, and the rest of the auction converges
without it.

STRIDE. While the sea is in, Newton takes 8 steps a frame, Cohort's own cap
for a long frame, instead of 3. A straight-edged frame costs a fraction of a
soft one, and a rectangle's response to its weight is stiffer than a bell's:
with 3 steps the auction fell behind as the sea came in.

The stories, which keep their own whitespace, and the fields inside cells are
Cohort's.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cohort.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d'
s = raw.decode()

def replace(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Cohort — Hive</title>', '<title>Facet — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Cohort</a>', '<a class="back" href="index.html">&larr; Back · Facet</a>')

replace("""const COHORT = true;                                // COHORT: from page to page, the gallery is one body""",
"""const COHORT = true;                                // COHORT: from page to page, the gallery is one body
const FACET = true;                                 // FACET: while the page changes, a cell reaches as far as its own rectangle
const STEADY = true;                                // STEADY: a site with no ground sits the solve out
const STRIDE = true;                                // STRIDE: while the sea is in, Newton takes 8 steps a frame""")

# ---- FACET: the reach --------------------------------------------------------------------------------------------
replace("const SEA_SIDES = 64;", """// FACET: A REACH WITH STRAIGHT SIDES. A cell reaches as far as its own
// rectangle: centred on its seed, of proportions a (width over height), with
// half sides sqrt(K w a) and sqrt(K w / a), so of area pi w, as a disc of the
// same weight. Its sides are the sea's; where it meets a neighbour, the
// bisector cuts it as ever.
const FACET_K = Math.PI / 4;
function facetHalf(w, a) { const r = Math.sqrt(Math.max(0, w) * FACET_K), q = Math.sqrt(a); return [r * q, r / q]; }
function facetCut(poly, sx, sy, w, a) {
  if (!(w > 0)) return [];
  const [hx, hy] = facetHalf(w, a);
  let q = poly;
  for (const [ax, ay, b] of [[1, 0, sx + hx], [-1, 0, hx - sx], [0, 1, sy + hy], [0, -1, hy - sy]]) {
    let out = false; for (const p of q.pts) if (ax * p[0] + ay * p[1] > b) { out = true; break; }
    if (!out) continue;
    q = clipHalfPlane(q, ax, ay, b, SEA); if (q.pts.length < 3) return [];
  }
  return [q];
}
// FACET: a cell's bid at an offset, as its own reach measures it: a disc's, or
// a rectangle's (whose level lines are its rectangles); and its gradient
function seaRise(w, dx, dy, a) { return a ? w - Math.max(dx * dx / (FACET_K * a), dy * dy * a / FACET_K) : w - dx * dx - dy * dy; }
function seaRiseGrad(dx, dy, a) { if (!a) return [2 * dx, 2 * dy]; return dx * dx / (FACET_K * a) >= dy * dy * a / FACET_K ? [2 * dx / (FACET_K * a), 0] : [0, 2 * dy * a / FACET_K]; }
const SEA_SIDES = 64;""")
replace("""    const parts = poly.pts.length < 3 ? [] : sea && sea.on[i] ? seaSoftCut(poly, i, seeds, weights, sea) : [poly], softCut""",
"""    const parts = poly.pts.length < 3 ? [] : sea && sea.facet && sea.facet[i] ? facetCut(poly, seeds[i][0], seeds[i][1], weights[i], sea.facet[i]) : sea && sea.on[i] ? seaSoftCut(poly, i, seeds, weights, sea) : [poly], softCut""")
# the soft cut, wherever it is still used, reads each bell by its own reach
replace("""  let K = 0; const KX = [], KY = [], KW = [], KT = [];""", """  let K = 0; const KX = [], KY = [], KW = [], KT = [], KA = [];""")
replace("""    if ((weights[j] - dx * dx - dy * dy) * it > -36) { KX.push(sx); KY.push(sy); KW.push(weights[j]); KT.push(it); K++; }   // e^-36 of presence is none""",
"""    const fa = sea.facet ? sea.facet[j] : 0;   // FACET
    if (seaRise(weights[j], dx, dy, fa) * it > -36) { KX.push(sx); KY.push(sy); KW.push(weights[j]); KT.push(it); KA.push(fa); K++; }   // e^-36 of presence is none""")
replace("""(KW[k] - dx * dx - dy * dy) * KT[k]""", """seaRise(KW[k], dx, dy, KA[k]) * KT[k]""", 2)
# the Jacobian
replace("""        const x = (p[0] + q[0]) / 2, y = (p[1] + q[1]) / 2;
        let gx = 0, gy = 0; const ks = [];""", """        if (seaSoft.facet && seaSoft.facet[i]) {   // FACET: a side of the cell's rectangle moves out by its half side's own change, h / 2w a unit of weight
          if (seaW[i] > 1e-9) { const h = facetHalf(seaW[i], seaSoft.facet[i]), vert = Math.abs(q[0] - p[0]) < Math.abs(q[1] - p[1]); A[i][i] += L * (vert ? h[0] : h[1]) / (2 * seaW[i]); }
          continue;
        }
        const x = (p[0] + q[0]) / 2, y = (p[1] + q[1]) / 2;
        let gx = 0, gy = 0; const ks = [];""")
replace("""          const dx = x - seeds[j][0], dy = y - seeds[j][1], e = (seaW[j] - dx * dx - dy * dy) / seaSoft.T[j];
          if (e < -36) continue;
          const kj = Math.exp(Math.min(SEA_SOFT_CAP, e)); ks.push([j, kj]);
          gx -= 2 * kj * dx / seaSoft.T[j]; gy -= 2 * kj * dy / seaSoft.T[j];""",
"""          const fa = seaSoft.facet ? seaSoft.facet[j] : 0, dx = x - seeds[j][0], dy = y - seeds[j][1], e = seaRise(seaW[j], dx, dy, fa) / seaSoft.T[j];   // FACET
          if (e < -36) continue;
          const kj = Math.exp(Math.min(SEA_SOFT_CAP, e)), gr = seaRiseGrad(dx, dy, fa); ks.push([j, kj]);
          gx -= kj * gr[0] / seaSoft.T[j]; gy -= kj * gr[1] / seaSoft.T[j];""")
# the solve
replace("""on: Uint8Array.from(seeds, (_, i) => !sea.reach || sea.reach[i] ? 1 : 0) } : null;""",
"""on: Uint8Array.from(seeds, (_, i) => !sea.reach || sea.reach[i] ? 1 : 0), facet: sea.facet || null } : null;   // FACET: and each cell's rectangle""")
replace("""diag.cells.forEach((c, i) => { if (!reaches(i)) return; let R = 0; for (const pc of (c.pieces || [c])) for (const p of pc.pts) R = Math.max(R, (p[0] - seeds[i][0]) ** 2 + (p[1] - seeds[i][1]) ** 2); hi = Math.min(hi, R - w[i]); });""",
"""diag.cells.forEach((c, i) => { if (!reaches(i)) return; const fa = sea.facet ? sea.facet[i] : 0; let R = 0; for (const pc of (c.pieces || [c])) for (const p of pc.pts) R = Math.max(R, fa ? w[i] - seaRise(w[i], p[0] - seeds[i][0], p[1] - seeds[i][1], fa) : (p[0] - seeds[i][0]) ** 2 + (p[1] - seeds[i][1]) ** 2); hi = Math.min(hi, R - w[i]); });""")   # FACET: a rectangle's reach covers its cell when its farthest point is in it
replace("""{ T: inI.map(j => seaSoft.T[j]), on: inI.map(j => seaSoft.on[j]), T0: seaSoft.T[i], on0: seaSoft.on[i] }""",
"""{ T: inI.map(j => seaSoft.T[j]), on: inI.map(j => seaSoft.on[j]), T0: seaSoft.T[i], on0: seaSoft.on[i], facet: seaSoft.facet ? inI.map(j => seaSoft.facet[j]) : null, F0: seaSoft.facet ? seaSoft.facet[i] : 0 }""")
replace("""  const parts = sea && sea !== true && sea.on0 ? seaSoftCut(poly, 0, [[sx, sy], ...seeds], [w, ...weights], { T: [sea.T0, ...sea.T], on: [1, ...sea.on] }) : [poly];""",
"""  const parts = sea && sea !== true && sea.F0 ? facetCut(poly, sx, sy, w, sea.F0) : sea && sea !== true && sea.on0 ? seaSoftCut(poly, 0, [[sx, sy], ...seeds], [w, ...weights], { T: [sea.T0, ...sea.T], on: [1, ...sea.on], facet: sea.facet ? [0, ...sea.facet] : null }) : [poly];   // FACET: a newcomer's own reach""")
# the hive hands every solve its cells' rectangles
replace("""      const bell = q => 2 * claimOf(q) * domainArea / tSum / Math.PI, inT = live.map(bell), inOn = live.map(q => q.body.isVoid ? 0 : 1);""",
"""      const bell = q => 2 * claimOf(q) * domainArea / tSum / Math.PI, inT = live.map(bell), inOn = live.map(q => q.body.isVoid ? 0 : 1), inF = live.map(q => this.facetOf(q.body));   // FACET""")
replace("""seaIn && !s.body.isVoid ? { T: inT, on: inOn, T0: bell(s), on0: 1 } : false""",
"""seaIn && !s.body.isVoid ? { T: inT, on: inOn, T0: bell(s), on0: 1, facet: inF, F0: this.facetOf(s.body) } : false""")
replace("""        inSeeds.push([s.x, s.y]); inW.push(s.w); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1);""",
"""        inSeeds.push([s.x, s.y]); inW.push(s.w); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1); inF.push(this.facetOf(s.body));""")
replace("""reach: idx.map(i => !active[i].body.isVoid) } : null });""", """reach: idx.map(i => !active[i].body.isVoid), facet: idx.map(i => this.facetOf(active[i].body)) } : null });""")
replace("""reach: active.map(s => !s.body.isVoid) } : null });""", """reach: active.map(s => !s.body.isVoid), facet: active.map(s => this.facetOf(s.body)) } : null });""")
replace("""reach: idx.map(s => !s.body.isVoid) } : null });""", """reach: idx.map(s => !s.body.isVoid), facet: idx.map(s => this.facetOf(s.body)) } : null });""")
replace("""  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }""", """  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }
  // FACET: A BODY'S PROPORTIONS THIS FRAME (width over height). A cell's
  // turn from the seat it left to the seat it takes, geometrically, as its
  // size turns, or as its journey goes if its size hardly does. Whitespace's
  // own share, as it melts into the sea or settles out of it, reaches as a
  // square: kept about its seed, not spread between the cells.
  facetOf(b) {
    if (!FACET || this.depth !== 0) return 0;
    if (b.isVoid) return 1;
    if (b.facetAt !== this.serial || !b.facetAr) return 1;   // a cell this change did not seat: a square
    const d = (b.claimTarget || 0) - (b.claim0 || 0), q = Math.max(0, Math.min(1, Math.abs(d) > 0.05 * Math.max(b.claim0 || 0, b.claimTarget || 0) ? (b.claim - b.claim0) / d : b.progress || 0));
    return b.facetAr[0] ** (1 - q) * b.facetAr[1] ** q;
  }""")
replace("""const plOldPlace = Hive.prototype.placeSeeds;""", """// FACET: AT A CHANGE OF THE PAGE, each cell's proportions, from the seat it
// leaves to the seat it takes (no flatter than 1 to 5)
const facetEnter = Hive.prototype.enterScene;
Hive.prototype.enterScene = function (name, origin) {
  const ar = r => r ? Math.max(0.2, Math.min(5, (r[2] - r[0]) * this.PW / Math.max(1e-9, (r[3] - r[1]) * this.PH))) : 0;
  const was = FACET && this.depth === 0 ? new Map(this.bodies.map(b => [b, ar(b.rect)])) : null;
  const out = facetEnter.call(this, name, origin);
  if (was) for (const b of this.bodies) if (!b.isVoid) { const a1 = ar(b.rect) || was.get(b) || 1; b.facetAt = this.serial; b.facetAr = [was.get(b) || a1, a1]; }
  return out;
};
const plOldPlace = Hive.prototype.placeSeeds;""")

# ---- STEADY ------------------------------------------------------------------------------------------------------
replace("""  const eps0 = 0.5 * Math.min(minOf(tgt), minOf(diag.areas));""", """  // STEADY: a site that holds no ground as the solve begins has no edge, so
  // no step of Newton's can give it any: it sits this solve out, its weight as
  // it is, and the rest of the auction converges without it (on the page,
  // outside the stories, whose hive says so)
  const out = Uint8Array.from(diag.areas, a => STEADY && opts.steady && !(a > 0) ? 1 : 0), anyOut = out.some(x => x);
  let inMin = Infinity; for (let i = 0; i < n; i++) if (!out[i]) inMin = Math.min(inMin, diag.areas[i]);
  const eps0 = 0.5 * Math.min(minOf(tgt), anyOut ? inMin : minOf(diag.areas));""")
replace("""      g[i] = tgt[i] - diag.areas[i];
      const r = Math.abs(g[i]) / tgt[i];""", """      g[i] = out[i] ? 0 : tgt[i] - diag.areas[i];   // STEADY
      const r = Math.abs(g[i]) / tgt[i];""")
replace("""    const J = buildJacobian(diag, seeds, sea ? w : null, seaSoft);""", """    const J = buildJacobian(diag, seeds, sea ? w : null, seaSoft);
    if (anyOut) for (let i = 0; i < n; i++) if (out[i]) { for (let j = 0; j < n; j++) { J[i][j] = 0; J[j][i] = 0; } J[i][i] = 1; }   // STEADY: its weight stands""")
replace("""      for (let i = 0; i < n; i++) {
        const gi = tgt[i] - dt.areas[i];
        gnT += gi * gi;
        if (dt.areas[i] < mn) mn = dt.areas[i];
      }""", """      for (let i = 0; i < n; i++) {
        if (out[i]) continue;   // STEADY
        const gi = tgt[i] - dt.areas[i];
        gnT += gi * gi;
        if (dt.areas[i] < mn) mn = dt.areas[i];
      }""")

# the page's own solves, outside the stories, may sit a site out
for old in ["{ maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(i => this.sitePaint(active[i])),",
            "{ maxIter: this.iterBudget(), tris, domainArea: tris ? dArea : undefined, paint: active.map(s => this.sitePaint(s)),",
            "{ maxIter: this.iterBudget(), tris: gt, domainArea: ga, paint: idx.map(s => this.sitePaint(s)),"]:
    replace(old, old.replace("{ maxIter: this.iterBudget(),", "{ steady: this.seaOpen(), maxIter: this.iterBudget(),"))

# ---- STRIDE ------------------------------------------------------------------------------------------------------
replace("""  iterBudget() { return Math.max(3, Math.min(8, Math.round(3 * (this.lastDt || 1 / 60) * 60))); }""",
"""  iterBudget() { return STRIDE && this.depth === 0 && this.seaOpen() && this.seaE > 0 ? 8 : Math.max(3, Math.min(8, Math.round(3 * (this.lastDt || 1 / 60) * 60))); }   // STRIDE: while the sea is in, Cohort's cap""")

out = ROOT / 'facet.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
