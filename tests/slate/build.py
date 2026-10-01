"""Build Slate from Cohort: the image is its own shape.

While a page changes, a lone cell in the sea was its disc, and so the image,
the largest cell, travelled as a sphere. Here the two images of a change to or
from a page (the one that closes and the one that opens) reach as their own
shape: their bells' level lines are rounded rectangles of the image's
proportions (an L4 ball) instead of circles, turning from the old seat's
proportions to the new one's as the image's size turns. Everything else about
the sea is Cohort's: the cards keep their discs, and the images still meet
them as one body.

Every change that does not go to or from a page is Cohort's to the bit, and so
are the stories.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cohort.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Cohort — Hive</title>', '<title>Slate — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Cohort</a>', '<a class="back" href="index.html">&larr; Back · Slate</a>')

replace("""const COHORT = true;                                // COHORT: from page to page, the gallery is one body""",
"""const COHORT = true;                                // COHORT: from page to page, the gallery is one body
const SLATE = true;                                 // SLATE: the images of a change to or from a page reach as their own shape""")

# ---- SLATE: a bell's measure, a disc's or an image's -------------------------------------------------------------
replace("""function seaSoftCut(poly, i, seeds, weights, sea) {""",
"""// SLATE: HOW FAR A POINT IS FROM A SEED, AS ITS BELL MEASURES IT. A cell's
// bell measures the square of the distance, so its level lines are circles; an
// image's measures the L4 norm of the offset in its own proportions, so its
// level lines are rounded rectangles with the image's sides. Of the same
// weight, an image reaches SEA_SLATE_C w where a cell reaches pi w. sh is an
// image's [1/a, a], a the ratio of its sides; null for a cell. A bell's rise
// at a point is its weight less that measure (for a cell, as Cohort reckons
// it); its least rise over a box takes for an image a measure never larger.
const SEA_SLATE_C = 3.7081;   // the area of the L4 unit ball, 4 Γ(5/4)² / Γ(3/2)
function seaQ(dx, dy, sh) { const U = dx * dx * sh[0], V = dy * dy * sh[1]; return Math.sqrt(U * U + V * V); }
function seaRise(w, dx, dy, sh) { return sh ? w - seaQ(dx, dy, sh) : w - dx * dx - dy * dy; }
function seaRiseLow(w, dx, dy, sh) { return sh ? w - (dx * dx * sh[0] + dy * dy * sh[1]) / Math.SQRT2 : w - dx * dx - dy * dy; }
function seaQgrad(dx, dy, sh) { if (!sh) return [2 * dx, 2 * dy]; const U = dx * dx * sh[0], V = dy * dy * sh[1], q = Math.sqrt(U * U + V * V) || 1e-12; return [2 * U * dx * sh[0] / q, 2 * V * dy * sh[1] / q]; }
function seaSoftCut(poly, i, seeds, weights, sea) {""")
replace("""  let K = 0; const KX = [], KY = [], KW = [], KT = [];
  for (let j = 0; j < seeds.length; j++) {
    if (!sea.on[j]) continue;
    const sx = seeds[j][0], sy = seeds[j][1], dx = Math.max(x0 - sx, 0, sx - x1), dy = Math.max(y0 - sy, 0, sy - y1), it = 1 / sea.T[j];
    if ((weights[j] - dx * dx - dy * dy) * it > -36) { KX.push(sx); KY.push(sy); KW.push(weights[j]); KT.push(it); K++; }   // e^-36 of presence is none
  }""", """  let K = 0; const KX = [], KY = [], KW = [], KT = [], KS = [];
  for (let j = 0; j < seeds.length; j++) {
    if (!sea.on[j]) continue;
    const sx = seeds[j][0], sy = seeds[j][1], dx = Math.max(x0 - sx, 0, sx - x1), dy = Math.max(y0 - sy, 0, sy - y1), it = 1 / sea.T[j], sh = sea.shape ? sea.shape[j] : null;   // SLATE: and its shape
    if (seaRiseLow(weights[j], dx, dy, sh) * it > -36) { KX.push(sx); KY.push(sy); KW.push(weights[j]); KT.push(it); KS.push(sh); K++; }   // e^-36 of presence is none
  }""")
replace("""  const F = (x, y) => { let f = 0; for (let k = 0; k < K; k++) { const dx = x - KX[k], dy = y - KY[k]; f += Math.exp(Math.min(SEA_SOFT_CAP, (KW[k] - dx * dx - dy * dy) * KT[k])); } return f; };
  const IN = (x, y) => { let f = 0; for (let k = 0; k < K; k++) { const dx = x - KX[k], dy = y - KY[k]; f += Math.exp(Math.min(SEA_SOFT_CAP, (KW[k] - dx * dx - dy * dy) * KT[k])); if (f >= 1) return true; } return false; };""",
"""  const F = (x, y) => { let f = 0; for (let k = 0; k < K; k++) { const dx = x - KX[k], dy = y - KY[k]; f += Math.exp(Math.min(SEA_SOFT_CAP, seaRise(KW[k], dx, dy, KS[k]) * KT[k])); } return f; };
  const IN = (x, y) => { let f = 0; for (let k = 0; k < K; k++) { const dx = x - KX[k], dy = y - KY[k]; f += Math.exp(Math.min(SEA_SOFT_CAP, seaRise(KW[k], dx, dy, KS[k]) * KT[k])); if (f >= 1) return true; } return false; };""")
replace("""          if (!seaSoft.on[j]) continue;
          const dx = x - seeds[j][0], dy = y - seeds[j][1], e = (seaW[j] - dx * dx - dy * dy) / seaSoft.T[j];
          if (e < -36) continue;
          const kj = Math.exp(Math.min(SEA_SOFT_CAP, e)); ks.push([j, kj]);
          gx -= 2 * kj * dx / seaSoft.T[j]; gy -= 2 * kj * dy / seaSoft.T[j];""",
"""          if (!seaSoft.on[j]) continue;
          const sh = seaSoft.shape ? seaSoft.shape[j] : null, dx = x - seeds[j][0], dy = y - seeds[j][1], e = seaRise(seaW[j], dx, dy, sh) / seaSoft.T[j];   // SLATE: by its own measure
          if (e < -36) continue;
          const kj = Math.exp(Math.min(SEA_SOFT_CAP, e)), gq = seaQgrad(dx, dy, sh); ks.push([j, kj]);
          gx -= kj * gq[0] / seaSoft.T[j]; gy -= kj * gq[1] / seaSoft.T[j];""")
replace("""{ T: [sea.T0, ...sea.T], on: [1, ...sea.on] }) : [poly];""",
"""{ T: [sea.T0, ...sea.T], on: [1, ...sea.on], shape: sea.shape || sea.S0 ? [sea.S0 || null, ...(sea.shape || sea.T.map(() => null))] : null }) : [poly];   // SLATE: and the shapes""")
replace("""  const seaSoft = sea ? { T: Float64Array.from(tgt, t => 2 * t / Math.PI), on: Uint8Array.from(seeds, (_, i) => !sea.reach || sea.reach[i] ? 1 : 0) } : null;""",
"""  const seaSoft = sea ? { T: Float64Array.from(tgt, (t, i) => 2 * t / (sea.shape && sea.shape[i] ? SEA_SLATE_C : Math.PI)), on: Uint8Array.from(seeds, (_, i) => !sea.reach || sea.reach[i] ? 1 : 0), shape: sea.shape || null } : null;   // SLATE: an image's bell as wide as the image""")
replace("""{ T: inI.map(j => seaSoft.T[j]), on: inI.map(j => seaSoft.on[j]), T0: seaSoft.T[i], on0: seaSoft.on[i] }""",
"""{ T: inI.map(j => seaSoft.T[j]), on: inI.map(j => seaSoft.on[j]), T0: seaSoft.T[i], on0: seaSoft.on[i], shape: seaSoft.shape ? inI.map(j => seaSoft.shape[j]) : null, S0: seaSoft.shape ? seaSoft.shape[i] : null }""")
replace("""      const bell = q => 2 * claimOf(q) * domainArea / tSum / Math.PI, inT = live.map(bell), inOn = live.map(q => q.body.isVoid ? 0 : 1);   // AMOEBA: everyone's bell, for the soft sea""",
"""      const bell = q => 2 * claimOf(q) * domainArea / tSum / (this.seaShape(q.body) ? SEA_SLATE_C : Math.PI), inT = live.map(bell), inOn = live.map(q => q.body.isVoid ? 0 : 1), inSh = live.map(q => this.seaShape(q.body));   // AMOEBA: everyone's bell, for the soft sea (SLATE: an image's its own shape)""")
replace("""seaIn && !s.body.isVoid ? { T: inT, on: inOn, T0: bell(s), on0: 1 } : false""",
"""seaIn && !s.body.isVoid ? { T: inT, on: inOn, T0: bell(s), on0: 1, shape: inSh, S0: this.seaShape(s.body) } : false""")
replace("""        inSeeds.push([s.x, s.y]); inW.push(s.w); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1);""",
"""        inSeeds.push([s.x, s.y]); inW.push(s.w); inT.push(bell(s)); inOn.push(s.body.isVoid ? 0 : 1); inSh.push(this.seaShape(s.body));""")
replace("""reach: idx.map(i => !active[i].body.isVoid) } : null });""",
"""reach: idx.map(i => !active[i].body.isVoid), shape: idx.map(i => this.seaShape(active[i].body)) } : null });""")
replace("""reach: active.map(s => !s.body.isVoid) } : null });""",
"""reach: active.map(s => !s.body.isVoid), shape: active.map(s => this.seaShape(s.body)) } : null });""")
replace("""reach: idx.map(s => !s.body.isVoid) } : null });""",
"""reach: idx.map(s => !s.body.isVoid), shape: idx.map(s => this.seaShape(s.body)) } : null });""")
replace("""  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }""",
"""  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }
  // SLATE: AN IMAGE'S SHAPE ON ITS WAY: the ratio of its sides turning from
  // its old seat's to its new one's (geometrically) as its size turns from the
  // one to the other, so an image that closes takes a card's proportions as it
  // takes a card's size; null for a cell, and for an image once another change
  // has begun
  seaShape(b) {
    if (!SLATE || this.depth !== 0 || b.slateAt !== this.serial || !b.slateAr) return null;
    const d = (b.claimTarget || 0) - (b.claim0 || 0), q = Math.max(0, Math.min(1, Math.abs(d) > 1e-9 ? (b.claim - b.claim0) / d : b.progress || 0)), ar = b.slateAr[0] ** (1 - q) * b.slateAr[1] ** q;
    return [1 / ar, ar];
  }""")
replace("""function portalEnter(name, origin) {
  config.scene = name;
  document.querySelectorAll('.scene-btn').forEach(el => el.classList.toggle('active', el.dataset.scene === name));
  root.enterScene(name, origin);
}""", """let portalImage = null;                              // SLATE: the body that is the open page's image
function portalEnter(name, origin) {
  const out = config.scene in PORTAL_TEMPLATES ? portalImage : null;   // SLATE: the image that closes
  config.scene = name;
  document.querySelectorAll('.scene-btn').forEach(el => el.classList.toggle('active', el.dataset.scene === name));
  portalImage = name in PORTAL_TEMPLATES ? portalFocus : null;
  const ar = r => r ? (r[2] - r[0]) * root.PW / Math.max(1e-9, (r[3] - r[1]) * root.PH) : 1, was = new Map([out, portalImage].filter(Boolean).map(b => [b, ar(b.rect)]));
  root.enterScene(name, origin);
  for (const [b, a] of was) { b.slateAt = root.serial; b.slateAr = [a, ar(b.rect)]; }   // SLATE: the images of this change, from the proportions of the seat each leaves to those of the seat it takes
}""")

out = ROOT / 'slate.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
