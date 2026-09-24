"""Build Cue from Tell II: the cells take the stage in turn, on the engine's own rules.

Tell II's story, stage and blurb, with every slide an ordinary scene to the
engine. A slide's page is the stage's places around the blurb, the cluster's
bento, and the whitespace the two leave, cut again for every slide; the change
between two slides is the engine's own, as between any two scenes: the cells
are matched to the slots by distance (greedy, then 2-opt on squared travel),
every one of them rides an eased, bent path on its own clock, the change
percolates from where it is largest, and the whitespace closes ahead of what
lands in it and opens behind what leaves it, each on its ledger. Nobody is
told where to go: a slide asks for its places, and the nearest cells take
them, so the cluster's front cell comes out, a cell already on the stage keeps
its place, and the cells going back go where the cluster has room. The one
rule a slide adds is the bench: when a new sequence begins, the last
sequence's cast may not take a place on the stage, so a fresh cell comes out.
None of Tell II's own machinery runs (the planned revolver, the slots it
handed out, the yielding whitespace, the handed weights, the cast held as
walls). The wheel, a drag or a flick moves the story, as on a Tell.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'tell2.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '900e0a5d61780788f4295472341836ab87ecd05e3a445f2cb3dbff59f0e69db2'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Tell II — Hive</title>', '<title>Cue — Hive</title>')
replace('&larr; Back · Tell II</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · Tell: the cluster stays, its heroes swell · Tell II: the cells take the stage in turn · click a hero or Escape for home</span>',
        '&larr; Back · Cue</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · Tell: the cluster stays, its heroes swell · Tell II: the cells take the stage in turn · Cue: the same story, every slide a scene change of the engine\'s own · click a hero or Escape for home</span>')
replace('''      <button class="scene-btn" data-scene="tell2">Tell II</button>''',
        '''      <button class="scene-btn" data-scene="tell2">Tell II</button>
      <button class="scene-btn" data-scene="cue">Cue</button>''')

# --- the page, the assignment, the story ---------------------------------------------
replace('''const scenes = {''', '''// CUE. Tell II's story on the engine's own rules: every slide is a scene like
// any other, and the change from one slide to the next is the engine's. A
// slide asks for its places around the blurb and the nearest cells take
// them: nobody is told where to go. The cluster is a revolver in a pen. Its
// slots are laid once for the story, a slot for every cell, and a cell that
// goes out holds its slot open, a niche of whitespace in the pen; a cell
// coming back takes the open niche nearest it, and every other cell of the
// cluster keeps its slot. So a cell comes and goes through a gap, the cells
// around it give a little as the gap opens and closes, and nothing else in
// the pen moves. A cell on the stage that the next slide keeps holds its
// place through the change, still. When a new sequence begins the last one's
// cast is benched, so a fresh cell comes out. The stage and the blurb are
// Tell II's.
const CUE_CLUSTER = [0.8, 0.14, 1, 0.86];
// the pen's slots: its region halved and halved again, each cut across the
// longer side near the share of the cells each side holds, a little off it,
// so the cells have about the same room, never quite the same, and the pen
// is never a grid
function cueBento(r, n, sx, sy, id = 1) {
  if (n <= 0) return [];
  if (n === 1) return [r];
  const r6 = v => Math.round(v * 1e6) / 1e6, a = Math.max(1, Math.min(n - 1, Math.round(n * (0.38 + 0.24 * hash01(id, 61))))), f = Math.max(0.2, Math.min(0.8, a / n + 0.16 * (hash01(id, 62) - 0.5)));
  if ((r[2] - r[0]) * sx >= (r[3] - r[1]) * sy) { const x = r6(r[0] + (r[2] - r[0]) * f); return cueBento([r[0], r[1], x, r[3]], a, sx, sy, 2 * id).concat(cueBento([x, r[1], r[2], r[3]], n - a, sx, sy, 2 * id + 1)); }
  const y = r6(r[1] + (r[3] - r[1]) * f); return cueBento([r[0], r[1], r[2], y], a, sx, sy, 2 * id).concat(cueBento([r[0], y, r[2], r[3]], n - a, sx, sy, 2 * id + 1));
}
const cueLattice = (C, R) => f => [Math.round(f[0] * C * 1e6) / 1e6, Math.round(f[1] * R * 1e6) / 1e6, Math.round(f[2] * C * 1e6) / 1e6, Math.round(f[3] * R * 1e6) / 1e6];
function cueSlots(C, R, n, W, H) { return cueBento(cueLattice(C, R)(W < H ? TELL2_PHONE.cluster : CUE_CLUSTER), n, W / C, H / R); }
// a slide's sequence begins at the last fresh slide; its cast is the places
// of the sequence so far
function cueSeq(k) { let s = Math.max(0, Math.min(TELL2_SLIDES.length - 1, k)); while (s > 0 && !TELL2_SLIDES[s].fresh) s--; return s; }
function cuePlaces(k) { return TELL2_SLIDES.slice(cueSeq(k), k + 1).map(sd => sd.place); }
// THE WHITESPACE is cut once for the story: the page less every place and
// the pen, cut along their edges (Tell II's cut). An empty place is a piece
// of its own, and so is an open niche, so a slide changes only the pieces a
// cell lands in or leaves. On a phone a place shares its column with others,
// and a column one of them fills is no piece.
const cueFixed = new Map();
let cueSlotsN = 0;
function cueWhitespace(C, R, W, H, places, n) {
  cueSlotsN = n; const L = cueLattice(C, R), key = [C, R, W, H, n].join('|');
  if (!cueFixed.has(key)) {
    const pen = L(W < H ? TELL2_PHONE.cluster : CUE_CLUSTER), E = 1e-6, cut = tell2Complement(C, R, Object.keys(TELL2_PLACES).map(p => L(tell2Place(p, W, H))).concat([pen]));
    // THE DOOR, the strip between the stage and the pen, in stretches: cut
    // across at every edge of the pen's slots along it, so a cell crossing it
    // cuts again only the stretch beside the slot it leaves or comes home to
    // (see the construction), and the rest of the door holds the pen's edge
    const slots = cueBento(pen, cueSlotsN || 1, W / C, H / R), out = [];
    for (const r of cut) {
      const door = W < H ? Math.abs(r[3] - pen[1]) < E && r[0] < pen[2] - E && r[2] > pen[0] + E : Math.abs(r[2] - pen[0]) < E && r[1] < pen[3] - E && r[3] > pen[1] + E;
      if (!door) { out.push(r); continue; }
      const ax = W < H ? 0 : 1, lines = [...new Set(slots.filter(q => Math.abs((W < H ? q[1] : q[0]) - (W < H ? pen[1] : pen[0])) < E).flatMap(q => [q[ax], q[ax + 2]]).map(v => Math.round(v * 1e6) / 1e6))].filter(v => v > r[ax] + E && v < r[ax + 2] - E).sort((a, b) => a - b);
      let lo = r[ax];
      for (const v of lines.concat([r[ax + 2]])) { const q = r.slice(); q[ax] = lo; q[ax + 2] = v; out.push(q); lo = v; }
    }
    cueFixed.set(key, out);
  }
  const voids = cueFixed.get(key).map(r => r.slice());
  for (const p of Object.keys(TELL2_PLACES)) {
    if (places.includes(p) || (W < H && places.some(q => TELL2_PHONE_COL[q] === TELL2_PHONE_COL[p]))) continue;
    const r = L(tell2Place(p, W, H)); if (!voids.some(v => rectsEqual(v, r))) voids.push(r);
  }
  return voids;
}
// A slide's page with the niches it names (by default the last slots): the
// stage's places first, then the pen's slots held, then the whitespace
function cuePage(k, C, R, n, W, H, niches) {
  const places = cuePlaces(k).slice(0, Math.max(0, n - 1)), L = cueLattice(C, R), stage = places.map(p => L(tell2Place(p, W, H))), slots = cueSlots(C, R, n, W, H);
  const open = niches || slots.map((r, s) => s).slice(slots.length - places.length);
  return { content: stage.concat(slots.filter((r, s) => !open.includes(s))), voids: cueWhitespace(C, R, W, H, places, n).concat(open.map(s => slots[s])), cast: stage.length, slots, niches: open };
}
// THE ENGINE'S MATCHING, for m cells and n slots of which the nearer are
// taken: greedy on squared travel, then 2-opt, a cell trading with another,
// a cell left out taking a matched one's slot, or a cell moving to a slot
// left open
function cueMatch(m, n, cost) {
  const pairs = [];
  for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) pairs.push([cost(i, j), i, j]);
  pairs.sort((p, q) => p[0] - q[0]);
  const a = new Array(m).fill(-1), b = new Array(n).fill(-1), want = Math.min(m, n);
  let got = 0;
  for (const [, i, j] of pairs) { if (got === want) break; if (a[i] < 0 && b[j] < 0) { a[i] = j; b[j] = i; got++; } }
  for (let pass = 0; pass < 30; pass++) {
    let better = false;
    for (let i = 0; i < m; i++) {
      for (let i2 = 0; i2 < m && a[i] >= 0; i2++) {
        if (i2 === i) continue;
        const j = a[i], j2 = a[i2];
        if (j2 >= 0) { if (cost(i, j2) + cost(i2, j) + 0.5 < cost(i, j) + cost(i2, j2)) { a[i] = j2; a[i2] = j; b[j2] = i; b[j] = i2; better = true; } }
        else if (cost(i2, j) + 0.5 < cost(i, j)) { a[i2] = j; b[j] = i2; a[i] = -1; better = true; }
      }
      if (a[i] < 0) continue;
      for (let j2 = 0; j2 < n; j2++) if (b[j2] < 0 && cost(i, j2) + 0.5 < cost(i, a[i])) { b[a[i]] = -1; a[i] = j2; b[j2] = i; better = true; }
    }
    if (!better) break;
  }
  return a;
}
// WHO GOES WHERE, the engine's matching under the pen's rules: a cell on (or
// bound for) a place the slide keeps keeps it, and holds still; the places
// left take the nearest cells not benched; a cell in (or bound for) a slot
// keeps it; and the cells left, the ones coming home, go to their own
// niches. A cell is bound for its rectangle, so a change interrupted
// is planned from where everyone was going.
function cuePlan(h, k, cells) {
  const C = h.COLS, R = h.ROWS, n = cells.length, L = cueLattice(C, R);
  const names = cuePlaces(k).slice(0, Math.max(0, n - 1)), stage = names.map(p => L(tell2Place(p, h.W, h.H))), slots = cueSlots(C, R, n, h.W, h.H);
  const bound = (b, r) => b.rect && rectsEqual(b.rect, r), d2 = (b, r) => { const [x, y] = h.rectCenter(r); return (b.x - x) * (b.x - x) + (b.y - y) * (b.y - y); };
  const place = stage.map(() => null), slot = slots.map(() => null), used = new Set(), kept = new Set();
  stage.forEach((r, j) => { const b = cells.find(b => !used.has(b) && !cue.bench.has(b) && bound(b, r)); if (b) { place[j] = b; used.add(b); kept.add(b); } });
  const open = stage.map((r, j) => j).filter(j => !place[j]), pool = cells.filter(b => !used.has(b) && !cue.bench.has(b));
  cueMatch(pool.length, open.length, (i, j) => d2(pool[i], stage[open[j]])).forEach((j, i) => { if (j >= 0) { place[open[j]] = pool[i]; used.add(pool[i]); } });
  slots.forEach((r, s) => { const b = cells.find(b => !used.has(b) && bound(b, r)); if (b) { slot[s] = b; used.add(b); } });
  // a cell coming home goes to its own niche, held open for it since it left
  // (at the front of the pen, where the nearest cell goes out from); a cell
  // whose niche is gone takes the open niche nearest it
  let home = cells.filter(b => !used.has(b));
  for (const b of home) if (b.cueHome !== undefined && b.cueHome < slots.length && !slot[b.cueHome]) slot[b.cueHome] = b;
  home = home.filter(b => !slot.includes(b));
  const free = slots.map((r, s) => s).filter(s => !slot[s]);
  cueMatch(home.length, free.length, (i, j) => d2(home[i], slots[free[j]])).forEach((j, i) => { if (j >= 0) slot[free[j]] = home[i]; });
  slot.forEach((b, s) => { if (b) b.cueHome = s; });   // its niche, for when it goes out
  return { names, stage, slots, place, slot, kept };
}
// THE PEN IS SOLVED WHOLE, AND A NICHE IS HELD FROM ITS EDGES. The page is
// laid as if every slot were held, so the pen is one pocket, its cells solved
// together as a cell of the pen always is. An open slot is then whitespace
// holding exactly the ground a cell there would, held the way Portal holds
// whitespace: for every cell of the pen beside it, a mirror of that cell
// close behind their shared edge, weighted so the edge stays where it was.
// Nothing stands at the niche's heart, where its cell sits as it leaves and
// will sit when it comes home: a site there would be a cell in the dark,
// pushing the leaver out and standing in the way of the one coming back.
const cueCache = new Map();
function cueNicheSites(whole, i, open) {
  const cell = whole.diag.cells[i], s = whole.seeds[i], w = whole.weights[i], n = whole.content.length, size = Math.sqrt(whole.diag.areas[i]), out = [];
  for (const j of new Set(cell.labs || [])) {
    if (!(j >= 0 && j < n) || j === i || open.has(j)) continue;   // a cell beside it, not the whitespace or another niche
    const t = whole.seeds[j], wj = whole.weights[j], dx = t[0] - s[0], dy = t[1] - s[1], L = Math.hypot(dx, dy);
    if (L < 1e-9) continue;
    const nx = dx / L, ny = dy / L, c = ((t[0] * t[0] + t[1] * t[1] - wj) - (s[0] * s[0] + s[1] * s[1] - w)) / (2 * L), d = nx * t[0] + ny * t[1] - c, g = Math.max(1e-3, Math.min(d, 0.05 * size));
    out.push([t[0] - nx * (d + g), t[1] - ny * (d + g), wj + g * g - d * d]);
  }
  return out;
}
function cueScene(h, n) {
  if (!cue) return null;
  const cells = h.bodies.filter(b => !b.isVoid && !b.leaving && !b.isSelf), p = cuePlan(h, cue.k, cells);
  const cast = p.place.map((b, j) => j).filter(j => p.place[j]), places = cast.map(j => p.names[j]), open = new Set(p.slots.map((r, s) => s).filter(s => !p.slot[s]).map(s => cast.length + s));
  const key = [h.COLS, h.ROWS, h.W, h.H, n, places.join(',')].join('|');
  let whole = cueCache.get(key);
  if (!whole) {
    whole = portalDecorate(cast.map(j => p.stage[j]).concat(p.slots), cueWhitespace(h.COLS, h.ROWS, h.W, h.H, places, n), h.W, h.H, h.COLS, h.ROWS);
    whole.diag = computeDiagram(whole.seeds, whole.weights, [[0, 0], [h.W, 0], [h.W, h.H], [0, h.H]]);
    whole.niches = new Map();
    cueCache.set(key, whole); if (cueCache.size > 24) cueCache.delete(cueCache.keys().next().value);
  }
  const nkey = [...open].join(',');
  if (!whole.niches.has(nkey)) {
    // the niches' mirrors, and every piece's ground with them in: each share
    // read again off the diagram as it is, niches open, so what the auction
    // is asked for is what these sites hold, and it settles on this page
    const PW = h.PW, PH = h.PH, nc = whole.content.length, mirrors = [...open].map(i => cueNicheSites(whole, i, open)), seeds = [], weights = [], idx = [], at = [];
    whole.seeds.forEach((q, i) => { if (i < nc && open.has(i)) { idx.push(-1); return; } idx.push(seeds.length); seeds.push(q); weights.push(whole.weights[i]); });
    mirrors.forEach(list => { at.push(seeds.length); for (const [x, y, w] of list) { seeds.push([x, y]); weights.push(w); } });
    const d = computeDiagram(seeds, weights, [[0, 0], [h.W, 0], [h.W, h.H], [0, h.H]]), area = k => d.areas[k] / (PW * PH);
    const sites = (r, list) => { const cx = (r[0] + r[2]) / 2, cy = (r[1] + r[3]) / 2, out = []; for (const [x, y, k] of list) if (d.areas[k] > 1e-6) out.push({ x: x / PW - cx, y: y / PH - cy, q: area(k) }); return out; };
    const held = (r, q, list) => { q.mfSites = sites(r, list); q.mfArea = q.mfSites.reduce((a, m) => a + m.q, 0); q.mfKey = JSON.stringify(q.mfSites); q.mfRest = true; return q; };
    const content = [], voids = [], niches = [];
    whole.content.forEach((r, i) => { if (open.has(i)) return; const q = r.slice(); q.mfArea = area(idx[i]); q.mfSeed = r.mfSeed; q.mfRest = true; content.push(q); });
    whole.voids.forEach((v, k) => { const q = v.slice(); if (v.portalText) { q.portalText = true; q.portalRules = v.portalRules; } const list = []; for (let i = whole.owned[k][0]; i < whole.owned[k][1]; i++) list.push([whole.seeds[i][0], whole.seeds[i][1], idx[i]]); voids.push(held(v, q, list)); });
    [...open].forEach((i, m) => { const r = whole.content[i]; niches.push(held(r, r.slice(), mirrors[m].map(([x, y], j) => [x, y, at[m] + j]))); });
    whole.niches.set(nkey, { content, voids: voids.concat(niches) });
  }
  const page = whole.niches.get(nkey);
  const owner = cast.map(j => p.place[j]).concat(p.slot.filter(Boolean));
  cue.prevOn = cue.on.slice();
  for (const b of cells) b.cueFrom = b.rect ? b.rect.slice(0, 4) : null;   // where it was, for the size a flight starts at
  cue.homeCell = new Map(); p.slot.forEach((b, s) => { if (b) { const c = whole.diag.cells[cast.length + s]; if (c && c.pts && c.pts.length >= 3) cue.homeCell.set(b, c.pts); } });   // the cell of the pen a cell coming home melts into
  cue.slotOf = new Map(owner.map((b, i) => [b, i])); cue.on = cast.map(j => p.place[j]); cue.slots = p.slots;
  for (const b of cells) b.cueStay = p.kept.has(b);
  return { content: page.content, voids: page.voids, cast: cast.length };
}
// the page's slots, by the plan: the matching above, handed to the engine
function cueAssign(content, centers) {
  const g = content.map(b => cue.slotOf.get(b));
  return g.some(v => v === undefined) ? assignStations(content, centers) : g;
}
// THE CHANGE LOOKS AHEAD. Every journey of a change is known when it is
// planned: its path, its delay, its clock. Two cells whose journeys would
// bring them together, their seeds nearer than three quarters of their
// reaches added at the same moment and both still on their way, would push
// through each other and grapple their way round; so the change is played forward before it runs,
// and for each such meeting one of the two bends round the other, on the
// side it is already on, just enough to pass close. The cell going out to
// the stage keeps its line and a cell going home gives way; of two alike,
// the one that sets off later gives way. A cell that is already travelling
// when the change comes is on it too, where it is. No bend carries a card
// further off the page than its own ends are.
// how far a card of half-size R strays off the page along a path, beyond
// what its ends already do: a bend may not carry a card to the wall
function cueOffPage(h, p, R) {
  const off = (x, y) => Math.max(0, R - x, R - y, x + R - h.W, y + R - h.H), ends = Math.max(off(p.sx, p.sy), off(p.ex, p.ey));
  let worst = 0;
  for (let k = 1; k < 20; k++) { const e = k / 20, m = 1 - e; worst = Math.max(worst, off(m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey) - ends); }
  return worst;
}
const CUE_CLEAR = 0.75;
function cueAvoid(h, content) {
  const movers = content.filter(b => b.path && b.journey && Math.hypot(b.path.ex - b.path.sx, b.path.ey - b.path.sy) > 4);
  cueClear(h, movers, content.filter(b => cue.on.includes(b) && !movers.includes(b) && b.rect));
  if (movers.length < 2) return;
  const PW = h.PW, PH = h.PH, reach = b => 0.5 * Math.sqrt(Math.max(b.claim0 || 0, b.claimTarget || 0) * PW * PH), out = b => cue.on.includes(b);
  const at = (b, t) => { const j = b.journey, u = Math.max(0, Math.min(1, (h.t + t - j.t0 - j.delay - (j.hold || 0)) / j.dur)), e = easeInOutCubic(u), m = 1 - e, p = b.path; return [m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey]; };
  let T = 0; for (const b of movers) { const j = b.journey; T = Math.max(T, j.t0 + j.delay + (j.hold || 0) + j.dur - h.t); }
  const steps = Math.ceil(T * 30);
  const moving = (b, t) => { const j = b.journey, u = (h.t + t - j.t0 - j.delay - (j.hold || 0)) / j.dur; return u > 0.05 && u < 0.9; };
  // a meeting is on the way: both still travelling, not two cells coming to rest side by side
  const meet = (a, b) => { let worst = Infinity, when = 0; const need = CUE_CLEAR * (reach(a) + reach(b)); for (let s = 0; s <= steps; s++) { if (!moving(a, s / 30) || !moving(b, s / 30)) continue; const p = at(a, s / 30), q = at(b, s / 30), d = Math.hypot(p[0] - q[0], p[1] - q[1]) - need; if (d < worst) { worst = d; when = s / 30; } } return { worst, when }; };
  for (let pass = 0; pass < 4; pass++) {
    let bent = false;
    for (let i = 0; i < movers.length; i++) for (let k = i + 1; k < movers.length; k++) {
      const a = movers[i], b = movers[k], m = meet(a, b);
      if (m.worst >= 0) continue;
      let y = out(a) !== out(b) ? (out(a) ? b : a) : ((a.journey.t0 + a.journey.delay) > (b.journey.t0 + b.journey.delay) ? a : b);
      if (y.journey.t0 !== h.t) y = y === a ? b : a;   // a path already under way keeps its line
      if (y.journey.t0 !== h.t) continue;
      const o = y === a ? b : a, p = y.path, L = Math.hypot(p.ex - p.sx, p.ey - p.sy), nx = -(p.ey - p.sy) / L, ny = (p.ex - p.sx) / L;
      const [ox, oy] = at(o, m.when), [yx, yy] = at(y, m.when), side = (yx - ox) * nx + (yy - oy) * ny >= 0 ? 1 : -1;
      const c0 = [p.cx, p.cy], others = movers.filter(q => q !== y), score = () => Math.min(...others.map(q => meet(y, q).worst));
      let best = { sc: score(), cx: c0[0], cy: c0[1] };
      const step = 0.25 * CUE_CLEAR * (reach(a) + reach(b));   // the bend grows by a quarter of the clearance it needs, to three times it
      for (let s = 1; s <= 12 && best.sc < 0; s++) {
        p.cx = c0[0] + side * nx * s * step; p.cy = c0[1] + side * ny * s * step;
        if (cueOffPage(h, p, reach(y)) > 2) break;   // not to the wall
        const sc = score(); if (sc > best.sc) best = { sc, cx: p.cx, cy: p.cy };
      }
      p.cx = best.cx; p.cy = best.cy; bent = true;
    }
    if (!bent) break;
  }
}
// a staying piece's new sites wait for the cells by it: until every cell
// whose path comes within its reach of the piece has gone by or landed
function cueReseat(h, v, r, content, T) {
  const g = [r[0] * h.PW, r[1] * h.PH, r[2] * h.PW, r[3] * h.PH];
  let wait = 0;
  for (const b of content) {
    const p = b.path, j = b.journey; if (!p || !j || j.t0 !== h.t || Math.hypot(p.ex - p.sx, p.ey - p.sy) < 4 || b.cueFly) continue;   // a card flies over the piece, whatever its sites
    const R = 0.5 * Math.sqrt(Math.max(b.claim0 || 0, b.claimTarget || 0) * h.PW * h.PH);
    let last = -1;
    for (let k = 0; k <= 20; k++) { const e = k / 20, m = 1 - e, x = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey; if (Math.hypot(Math.max(g[0] - x, 0, x - g[2]), Math.max(g[1] - y, 0, y - g[3])) < R) last = e; }
    if (last < 0) continue;
    const u = last < 0.5 ? Math.cbrt(last / 4) : 1 - Math.cbrt(2 * (1 - last)) / 2;   // easeInOutCubic, inverted
    wait = Math.max(wait, j.delay + (j.hold || 0) + j.dur * Math.min(1, u + 0.05));
  }
  if (wait <= T) { v.formRect = null; h.seatBody(v, r, 0, { t0: h.t, delay: T, dur: 0.9, c0: v.crystal }); delete v.cueDefer; }
  else v.cueDefer = { r, at: h.t + wait };   // seated when it comes (see cueFlow)
}
// A CARD FLIES AS A CARD. A cell has no shape of its own here: its outline
// is wherever its neighbours' claims stop, and a settled cell looks right
// only because every edge of it is held by a mirror made for it. A cell
// crossing the open stage has nothing holding it, so its outline ran to
// whatever stopped it, the page's edge most of all: a fly on the wall,
// finding its place only as it landed. So a cell that goes out to the stage
// becomes its card on the way: it leaves the auction, and its shape is the
// engine's blend of the cell it had as it set off (carried along with it)
// and a card centred on its seed, the card growing from its slot's size to
// its place's as its seed goes (by where it is, not by the journey's clock,
// which its seed trails on its spring), the blend all card within a reach and
// a half of setting off.
// It flies and lands as a card, and lands a wall: pinned on its place, its
// outline its card, out of the auction as the cast on the stage always is.
// (Handed back to the auction as it landed, it sprawled for the frames the
// whitespace round its place took to hold it; kept a hole, the page drifted
// off its diagram, and the shadow auction handed a hole back wrong.)
// Whitespace and pen give way round it. A
// card going home flies as a card and melts, over its last reach and a half,
// into the cell of the pen it is going to; so does any cell crossing the
// stage into the pen, as the cells of a page do when the story begins. A card that is a card when a
// change comes goes on as one. A flight is one state, from the change that
// plans it to its seed landing: out of the auction all the way, starting
// from exactly the cell it had at rest, the blend going only one way.
// AND A CARD IN FLIGHT GOES ROUND THE CARDS STANDING ON THE STAGE: played
// forward on its path and its clock, a card the size it will be at each
// moment, from its slot's to its place's, is not to cut into a card that
// stands, by a gap; where it would, its path bends away from that card, just
// enough, as for two cells meeting.
const CUE_GAP = 16;
function cueClear(h, movers, standing) {
  if (!standing.length) return;
  const PW = h.PW, PH = h.PH, px = r => [r[0] * PW, r[1] * PH, r[2] * PW, r[3] * PH];
  const blocks = standing.map(b => px(b.rect));
  for (const b of movers) {
    const p = b.path, j = b.journey; if (j.t0 !== h.t || !b.cueFrom || !cue.on.includes(b) && !(cue.prevOn || []).includes(b)) continue;
    const f = px(b.cueFrom), t = px(b.rect), w0 = f[2] - f[0], h0 = f[3] - f[1], w1 = t[2] - t[0], h1 = t[3] - t[1];
    const cut = () => {   // how deep the card cuts into a card standing, at worst over its flight
      let worst = -Infinity, when = 0, which = null;
      for (let k = 2; k <= 40; k++) {
        const e = k / 40, m = 1 - e, x = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey, w = w0 + (w1 - w0) * e, hh = h0 + (h1 - h0) * e;
        for (const q of blocks) {
          const d = Math.min(w / 2 + (q[2] - q[0]) / 2 + CUE_GAP - Math.abs(x - (q[0] + q[2]) / 2), hh / 2 + (q[3] - q[1]) / 2 + CUE_GAP - Math.abs(y - (q[1] + q[3]) / 2));
          if (d > worst) { worst = d; when = e; which = q; }
        }
      }
      return { worst, when, which };
    };
    let c = cut();
    if (c.worst <= 0) continue;
    const L = Math.hypot(p.ex - p.sx, p.ey - p.sy), nx = -(p.ey - p.sy) / L, ny = (p.ex - p.sx) / L, e = c.when, m = 1 - e;
    const x = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey, q = c.which;
    const side = (x - (q[0] + q[2]) / 2) * nx + (y - (q[1] + q[3]) / 2) * ny >= 0 ? 1 : -1, c0 = [p.cx, p.cy];
    let best = { worst: c.worst, cx: p.cx, cy: p.cy };
    for (let k = 1; k <= 16 && best.worst > 0; k++) {
      p.cx = c0[0] + side * nx * k * 0.25 * c.worst; p.cy = c0[1] + side * ny * k * 0.25 * c.worst;
      if (cueOffPage(h, p, 0.5 * Math.max(Math.min(w0, h0), Math.min(w1, h1))) > 2) break;   // not to the wall
      const n = cut(); if (n.worst < best.worst) best = { worst: n.worst, cx: p.cx, cy: p.cy };
    }
    p.cx = best.cx; p.cy = best.cy;
  }
}
// where on its path a card comes within its reach of the rectangle it lands
// in, and where a card leaving a rectangle is half its size clear of it
function cueNear(h, b, r) {
  const p = b.path; if (!p || !r) return 0;
  const g = [r[0] * h.PW, r[1] * h.PH, r[2] * h.PW, r[3] * h.PH], reach = 0.5 * Math.sqrt((g[2] - g[0]) * (g[3] - g[1]));
  for (let k = 0; k <= 40; k++) { const e = k / 40, m = 1 - e, x = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey; if (Math.hypot(Math.max(g[0] - x, 0, x - g[2]), Math.max(g[1] - y, 0, y - g[3])) <= reach) return Math.max(0, Math.min(0.95, e - 0.025)); }
  return 0.95;
}
function cueClearOf(h, b, r) {
  const p = b.path; if (!p) return 1;
  const g = [r[0] * h.PW, r[1] * h.PH, r[2] * h.PW, r[3] * h.PH], reach = 0.5 * Math.sqrt((g[2] - g[0]) * (g[3] - g[1]));
  for (let k = 1; k <= 40; k++) { const e = k / 40, m = 1 - e, x = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey; if (Math.hypot(Math.max(g[0] - x, 0, x - g[2]), Math.max(g[1] - y, 0, y - g[3])) >= reach) return Math.max(0.05, e); }
  return 1;
}
function cueFlyers(h, content) {
  const S = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); }, size = r => [(r[2] - r[0]) * h.PW, (r[3] - r[1]) * h.PH];
  for (const b of content) {
    const p = b.path, j = b.journey;
    if (!p || !j || j.t0 !== h.t) continue;
    const L = Math.hypot(p.ex - p.sx, p.ey - p.sy), out = cue.on.includes(b), was = b.cueFly ? cueFlyC(h, b) : 0;
    const fromCard = was > 0.5 || (cue.prevOn || []).includes(b);
    const crossing = !out && b.cueFrom && !cue.slots.some(r => rectsEqual(r, b.cueFrom));   // coming into the pen from off its slots: from the stage, or from the page the story began on
    if (L < 4 || (!out && !fromCard && !crossing)) { if (!(was > 0)) b.cueFly = null; continue; }   // a cell of the pen staying a cell of the pen does not fly
    const from = b.cueFly && b.cueFly.cur ? b.cueFly.cur : (b.cueFrom ? size(b.cueFrom) : size(b.rect)), to = size(b.rect);
    b.cueFly = { fromCard, toCard: out, from, to, R: 0.5 * Math.sqrt(Math.max(from[0] * from[1], to[0] * to[1])), core: null, at: null, home: out ? null : cue.homeCell.get(b) || null, S, c: undefined };
    if (!fromCard) {   // the cell it has at rest, as it sets off: the flight begins exactly there
      let parts = null;
      if (h.solved) for (let k = 0; k < h.solvedSubs.length; k++) if (h.solvedSubs[k].body === b) { const cell = h.solved.diagram.cells[k]; if (cell) parts = cell.pieces || [cell]; }
      const r = b.cueFrom ? [b.cueFrom[0] * h.PW, b.cueFrom[1] * h.PH, b.cueFrom[2] * h.PW, b.cueFrom[3] * h.PH] : [b.x - 1, b.y - 1, b.x + 1, b.y + 1], sh = parts ? cellCoreAndArms(parts, r) : null;
      b.cueFly.core = sh ? sh.core : [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]]; b.cueFly.at = [b.x, b.y];
    }
  }
}
function cueFlyC(h, b) {   // how much of a card it is: from the cell it was to the card, and back into the cell it is going to
  const f = b.cueFly, p = b.path, S = f.S;
  const a = f.fromCard ? 1 : S(Math.hypot(b.x - p.sx, b.y - p.sy) / (1.5 * f.R)), z = f.toCard ? 1 : S(Math.hypot(b.x - p.ex, b.y - p.ey) / (1.5 * f.R));
  return Math.min(a, z);
}
function cueFlyShape(h, b) {
  const f = b.cueFly, p = b.path;
  if (!p) { b.cueFly = null; return null; }
  const dS = Math.hypot(b.x - p.sx, b.y - p.sy), dE = Math.hypot(b.x - p.ex, b.y - p.ey), e = dS + dE > 1e-6 ? dS / (dS + dE) : 1, done = !b.journey && dE < 0.5;   // its size by where it is, not by its clock: a seed trails its clock
  if (done && f.toCard) { b.pin = 1; b.cueFly = null; return null; }   // landed: pinned on its place, drawn as its card, it is a wall from this frame (see computeWalls)
  if (done) { b.cueFly = null; return null; }   // melted into the pen: a cell of the auction again
  const c0 = cueFlyC(h, b), c = f.c === undefined ? c0 : f.toCard ? Math.max(f.c, c0) : e > 0.5 ? Math.min(f.c, c0) : c0;   // one way only: toward the card going out, toward the cell coming home
  f.c = c;
  const w = f.from[0] + (f.to[0] - f.from[0]) * e, hh = f.from[1] + (f.to[1] - f.from[1]) * e;
  f.cur = [w, hh];
  const rect = [b.x - w / 2, b.y - hh / 2, b.x + w / 2, b.y + hh / 2];
  // the cell under the card: the one it set off as, carried with it, and the
  // one of the pen it is going to, and between the two a blend of them
  const card = [[rect[0], rect[1]], [rect[2], rect[1]], [rect[2], rect[3]], [rect[0], rect[3]]], start = f.core ? f.core.map(q => [q[0] + b.x - f.at[0], q[1] + b.y - f.at[1]]) : null;
  const home = f.home ? f.home.map(q => [q[0] + b.x - p.ex, q[1] + b.y - p.ey]) : null;   // carried with it too, so the blend is centred on its seed and is its home cell exactly as it arrives
  let core;
  if (f.toCard) core = start || card;
  else if (f.fromCard) core = home || card;
  else if (start && home) { const t = Math.max(0, Math.min(1, (e - 0.3) / 0.4)); core = blendConvex(start, home, t * t * (3 - 2 * t), h.domainPts()) || (t < 0.5 ? start : home); }
  else core = start || home || card;
  const pts = planesPoly(holePlanes(core, rect, c), h.domainPts());
  if (!pts) return null;
  return { pieces: [pts], planes: [convexPlanes(pts)], rect, pts, raw: [pts] };
}
// the story: its scroll (px, a page's height a slide), its speed, the slide
// it is on, the cast on stage, the bench, and the text's clocks
let cue = null;
function cueStart(origin) {
  reelDrop(); tellDrop(); tell2Drop();
  portalFocus = null; portalFlip = false;
  cue = { y: 0, v: 0, k: 0, on: [], prevOn: [], slots: [], homeCell: new Map(), bench: new Set(), titles: [], tf: [], drag: null, entered: false, alpha: 0, rule: 0, fullAt: -1, seen: -1, changed: -1e9 };
  cueCache.clear();
  cueGo(0, origin || { x: W / 2, y: H / 2 });
}
function cueDrop() { if (!cue) return; cue = null; for (const b of root.bodies) { delete b.cueStay; delete b.cueFly; delete b.cueFrom; delete b.cueHome; } }
// a slide is a scene change, from where it is largest; a new sequence
// benches the cast on stage
function cueGo(k, origin) {
  if (!cue) return;
  cue.bench = new Set(cueSeq(k) !== cueSeq(cue.k) ? cue.on : []);
  cue.k = k; cue.changed = simTime;
  portalEnter('cue', origin);
  cue.bench = new Set();
  cue.titles[k] = cue.on.map(b => b.name).join(' · '); cue.tf[k] = 0;
}
// the flow of the story, a Tell's: a speed eases away, a slow story snaps
// to its slide, and the slide the story is on is the one nearest; a change
// is made at most every quarter second
function cueFlow(dt) {
  if (!cue) return;
  for (const v of root.bodies) if (v.cueDefer && (v.leaving || root.t >= v.cueDefer.at)) { const d = v.cueDefer; delete v.cueDefer; if (!v.leaving && rectsEqual(v.rect, d.r)) { v.formRect = null; root.seatBody(v, d.r, 0, { t0: root.t, delay: 0, dur: 0.9, c0: v.crystal }); } }   // a staying piece takes its new sites
  const pitch = H, last = (TELL2_SLIDES.length - 1) * pitch;
  if (!cue.drag) {
    const snapping = Math.abs(cue.v) < 60;
    cue.v *= Math.exp(-dt / (snapping ? TELL_SNAP : TELL_RELAX));
    if (Math.abs(cue.v) < 0.05) cue.v = 0;
    cue.y += cue.v * dt;
    if (cue.y < 0) { cue.y = 0; cue.v = 0; }
    if (cue.y > last) { cue.y = last; cue.v = 0; }
    if (snapping) { const target = Math.round(cue.y / pitch) * pitch; cue.y += (target - cue.y) * (1 - Math.exp(-dt / TELL_SNAP)); }
  }
  const k = Math.max(0, Math.min(TELL2_SLIDES.length - 1, Math.round(cue.y / pitch)));
  if (k !== cue.k && simTime - cue.changed > 0.25) cueGo(k, null);
  if (!cue.entered && guestLeft <= 0) cue.entered = true;
}
function cueScroll(dy) {
  if (!cue) return false;
  if (cue.drag || Math.abs(dy) < 1) return true;
  const aim = Math.max(0, Math.min(TELL2_SLIDES.length - 1, Math.round(cue.y / H) + Math.sign(dy)));
  cue.v = reelClampV((aim * H - cue.y) / TELL_RELAX);
  return true;
}
function cueDragStart(x, y, t) { if (!cue) return false; cue.drag = { y0: cue.y, p0: y, last: y, t, v: 0 }; cue.v = 0; return true; }
function cueDragMove(x, y, t) {
  if (!cue || !cue.drag) return false;
  const d = cue.drag, dt = Math.max(1e-3, (t - d.t) / 1000), last = (TELL2_SLIDES.length - 1) * H;
  cue.y = Math.max(0, Math.min(last, d.y0 + (d.p0 - y)));
  const v = (d.last - y) / dt; d.v += (v - d.v) * Math.min(1, dt / 0.05); d.last = y; d.t = t;
  return true;
}
function cueDragEnd(t) { if (!cue || !cue.drag) return false; const d = cue.drag; cue.v = t - d.t > 120 ? 0 : reelClampV(d.v); cue.drag = null; return true; }
// The blurbs, Tell II's: in the box, each at its place on the scroll, the
// slide's and its neighbours' as they pass, titled with the cast's names
// once the slide has its cast (a slide not reached yet has none), the title
// fading in as it is given
function cueProseStep(ctx, type, dt, t) {
  if (!cue) return;
  const p = cue, gap = t - p.seen, el = p.seen < 0 || gap > 0.1 ? dt : gap;
  p.seen = t;
  const v = p.entered;
  p.alpha += ((v ? 1 : 0) - p.alpha) * (1 - Math.exp(-el / (v ? 0.30 : 0.08)));
  if (!v || p.alpha <= 0.97) p.fullAt = -1; else if (p.fullAt < 0) p.fullAt = t;
  p.rule += ((v && p.fullAt >= 0 && t - p.fullAt > 0.25 ? 1 : 0) - p.rule) * (1 - Math.exp(-el / (v ? 0.45 : 0.08)));
  for (let k = 0; k < p.tf.length; k++) if (p.tf[k] !== undefined) p.tf[k] = Math.min(1, p.tf[k] + el / 0.35);
  if (!v || p.alpha < 0.01) return;
  const bx = W < H ? TELL2_PHONE.box : TELL2_BOX, r = [bx[0] * W, bx[1] * H, bx[2] * W, bx[3] * H], pad = Math.max(16, Math.min(48, 0.024 * W));
  const x0 = r[0] + pad, x1 = r[2] - pad, y0 = r[1] + pad, y1 = r[3] - pad;
  if (x1 - x0 < 90) return;
  const title = Math.round(type.num * 0.9), line = Math.max(4, Math.round(type.name * 0.55)), lead = Math.round(line * 2.1);
  ctx.save();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.globalAlpha = 0.22 * p.rule; ctx.beginPath();
  const g = Math.round(pad / 2) + 0.5;
  ctx.moveTo(r[0] + g, r[1] + pad); ctx.lineTo(r[0] + g, r[3] - pad);
  ctx.stroke();
  const measure = Math.min(560, x1 - x0), pitch = H, travel = y1 - y0;
  ctx.beginPath(); ctx.moveTo(r[0], r[1]); ctx.lineTo(r[2], r[1]); ctx.lineTo(r[2], r[3]); ctx.lineTo(r[0], r[3]); ctx.closePath(); ctx.clip();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  for (let k = p.k - 1; k <= p.k + 1; k++) {
    if (k < 0 || k >= TELL2_SLIDES.length) continue;
    const lines = TELL2_SLIDES[k].lines, hb = Math.round(title * 1.8) + lines.length * lead;
    const yk = y0 + (y1 - y0 - hb) / 2 + (k * pitch - p.y) / pitch * travel;
    const edge = Math.min(1, Math.max(0, (yk + hb - y0) / 40), Math.max(0, (y1 - yk) / 40));
    const a = p.alpha * edge;
    if (a < 0.01) continue;
    if (p.titles[k]) { ctx.globalAlpha = 0.92 * a * (p.tf[k] || 0); ctx.font = `600 ${title}px system-ui, sans-serif`; ctx.fillText(p.titles[k], x0, yk); }
    ctx.globalAlpha = 0.5 * a; ctx.beginPath(); ctx.moveTo(x0, yk + Math.round(title * 1.3) + 0.5); ctx.lineTo(x0 + Math.round(title * 1.6), yk + Math.round(title * 1.3) + 0.5); ctx.stroke();
    ctx.globalAlpha = 0.20 * a;
    let y = yk + Math.round(title * 1.8);
    for (const f of lines) { roundedPath(ctx, [[x0, y], [x0 + measure * f, y], [x0 + measure * f, y + line], [x0, y + line]], line / 2, false); ctx.fill(); y += lead; }
  }
  ctx.restore();
}
const scenes = {''')

# --- a Cue slide is a scene to the engine, matched by distance ---------------------
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell2' ? tell2Scene(this, content.length) :''',
        '''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'cue' ? cueScene(this, content.length) : this.depth===0 && name === 'tell2' ? tell2Scene(this, content.length) :''')
replace('''    const gotS = assignStations(content, centers);
    portalPin(content, gotS, name);''', '''    const gotS = name === 'cue' && cue && cue.slotOf ? cueAssign(content, centers) : assignStations(content, centers);   // CUE: the engine's matching, under the pen's rules
    portalPin(content, gotS, name);''')
# WHITESPACE THAT STAYS IS RE-SEATED, LIKE ANY BODY GIVEN A NEW RECTANGLE,
# ONCE THE CELLS BY IT HAVE GONE. A void stays across a change when the new
# page wants one exactly where it is. On a Cue page the piece beside a place
# holds the mirrors of the cell there, so when the place fills or empties the
# piece stays with other mirrors and another claim; kept on its old ledger
# (all paid) the new claim would be its claim the next frame, a step every
# neighbour feels, so such a piece is seated on the new page as a cell is,
# its claim and its mirrors eased over a journey. And it waits, as new
# whitespace waits for its crossers: its new sites (the mirror holding the
# edge of a cell coming to the place beside it, say) come in only once every
# cell passing within its reach has gone by or landed, or the cell coming
# would cross the mirror that is to hold its own edge. A piece whose mirrors
# are the same stays as it was.
replace('''    const stays = new Set(), newVoids = [], rectOfVoid = new Map();''',
        '''    const stays = new Set(), newVoids = [], rectOfVoid = new Map(), cueSeat = [];''')
replace('''      if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; if (name === 'tell2') same.claimTarget = Math.max(CLAIM_MIN, rectArea(r)); } stays.add(same); continue; }''',
        '''      if (same && name === 'cue') delete same.cueDefer;
      if (same && name === 'cue' && r.mfSites && same.rect.mfKey !== r.mfKey) { cueSeat.push([same, r]); stays.add(same); continue; }   // CUE: a staying piece with other mirrors is seated again
      if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; if (name === 'tell2') same.claimTarget = Math.max(CLAIM_MIN, rectArea(r)); } stays.add(same); continue; }''')

# NEW WHITESPACE WAITS FOR THE CELLS CROSSING IT. Portal's rule, and the one
# that matters most here: the stage is whitespace, and a cell going back to
# the cluster or coming out of it crosses it. A piece that opens on its own
# clock stands in the traveller's way, its mirrors a few px off the
# traveller's seed, and the wall between them swings the traveller's cell
# about; a piece with the crossers on its ledger opens behind them. Not for a
# card in flight: it carves its own way, the whitespace it flies over holds
# what ground the card leaves it, and whitespace waiting for the cards on the
# story's entry held a fifth of its claim, so every cell bidding was drawn at
# nearly four times its size.
replace('''        if (!(name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''',
        '''        if (!(name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2' || name === 'cue') || !b.path || !b.journey || b.journey.t0 !== this.t || b.cueFly) continue;   // CUE: a slide's whitespace waits for its crossers too, but not for a card, which carves its own way''')

# A CELL OF THE CAST THAT KEEPS ITS PLACE HOLDS STILL. At the root nothing is
# a wall, and a bystander re-seated on a journey of no length is held only by
# its spring: a cell passing nudges it, and the whitespace beside it, cut
# again as a traveller crosses, lets it swell. A cell of the cast the next
# slide keeps, sitting on its place, is not re-seated: it is pinned there,
# and pinned on its rectangle it is a wall for the change, as Tell II's was.
replace('''    if (b.tell2Stay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // TELL II: a cell of the cast keeping its place''',
        '''    if (b.tell2Stay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // TELL II: a cell of the cast keeping its place
    if (b.cueStay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // CUE: a cell of the cast keeping its place holds still''')

# the change looks ahead: once every journey is planned, and before the
# whitespace reads the paths for its ledgers, meetings are bent apart
replace('''    for (const b of pending) this.retireBody(b, 0.8, tOf(b));

    // an old void closes at the pace of what lands in it; a new one opens''',
        '''    for (const b of pending) this.retireBody(b, 0.8, tOf(b));
    if (name === 'cue' && cue) { cueAvoid(this, content); cueFlyers(this, content); for (const [v, r] of cueSeat) cueReseat(this, v, r, content, tOf(v)); }   // CUE: the change looks ahead; a staying piece takes its new sites once the cells by it have gone by

    // an old void closes at the pace of what lands in it; a new one opens''')

# WHITESPACE MAKES WAY WITHOUT GIVING GROUND. A piece that closed for a
# crossing left the auction's total short, and the auction hands every site
# its claim x ground / total: with half the page's whitespace closing ahead of
# the travellers of a fresh slide, every settled cell was handed twice its
# ground and the pen swelled out of its frame. Here nothing closes for a
# crossing. The sites of a piece in a traveller's way give way, the more the
# nearer, and hand what they give up to the piece's other sites, so the
# piece keeps its claim, the page its total, and every settled cell exactly
# its own ground; a piece all of whose sites are in the way gives way whole.
# The way a traveller asks for comes in over its first half-reach from where
# it set off and goes over its last half-reach to its place, by where its
# seed is, not by its clock: a seed trails its clock on its spring.
replace('''  this.ferryW=W; this.ferryH=H;
};''', '''  this.ferryW=W; this.ferryH=H;
};

const cueWay = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {   // CUE: whitespace makes way without giving ground
  cueWay.call(this);
  if (this.depth !== 0 || !cue || config.scene !== 'cue') return;
  const movers = [];
  const S = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };
  for (const b of this.bodies) {   // the way it asks for comes in as it sets off and goes as it lands, by where its seed is, so nothing snaps back
    const p = b.path;
    if (b.isVoid || b.isSelf || b.leaving || !p || Math.hypot(p.ex - p.sx, p.ey - p.sy) < 4 || b.cueFly) continue;   // a card in flight carves its own way: nothing gives way for it, and whitespace under it is flown over (see enforcePreconditions)
    const R = 0.5 * Math.sqrt(Math.max(b.claim0 || 0, b.claimTarget || 0) * this.PW * this.PH), on = S(Math.hypot(b.x - p.sx, b.y - p.sy) / (0.5 * R)) * S(Math.hypot(b.x - p.ex, b.y - p.ey) / (0.5 * R));
    if (on > 0) movers.push([b.x, b.y, R, on]);
  }
  if (!movers.length) return;
  for (const v of this.bodies) {
    if (!v.isVoid || v.isSelf || v.leaving || v.table && v.table.mode === 'open' && v.progress < 1) continue;   // a piece opening keeps its ledger's clock
    let all = 0, clear = 0, gone = 0; const f = [];
    for (const q of v.subs) {
      let k = 1;
      for (const [x, y, R, on] of movers) k = Math.min(k, 1 - on * (1 - S((Math.hypot(q.x - x, q.y - y) - 0.3 * R) / (0.9 * R))));   // in its way: nearer than its reach
      k = Math.max(0.02, k); f.push(k); all += q.claim; gone += q.claim * (1 - k); if (k > 0.98) clear += q.claim;
    }
    if (gone <= 0) continue;
    // what the sites in the way give up, the sites clear of it take, if they
    // hold enough of the piece to take it; else the piece gives way whole
    const g = clear > 0.25 * all ? 1 + gone / clear : 1;
    v.subs.forEach((q, i) => { q.claim *= f[i] > 0.98 ? g : f[i]; });
  }
};''')

# WHITESPACE OPENS AT THE PACE OF WHAT LEAVES IT. A new piece's ledger has
# the bodies leaving it, and whatever share they do not account for opens on
# the piece's own clock; for a niche opening behind its card that is most of
# it, growing beside the card before it has gone. On a Cue page a piece with
# a cell leaving it opens only as its leavers go.
replace('''      v.table = { mode: 'open', rows, wRem: Math.max(0, rectArea(r) - W), f: 0 };''',
        '''      v.table = { mode: 'open', rows, wRem: name === 'cue' && rows.some(q => this.inRect(r, q.body.x, q.body.y)) ? 0 : Math.max(0, rectArea(r) - W), f: 0 };   // CUE: it opens as its leavers go''')

# a card in flight is a hole of the shape it flies at: out of the auction,
# carved from everyone's ground, the whitespace and the pen flowing round it
replace('''      if (b.isSelf || !r) { b.holeCore = null; continue; }''',
        '''      if (b.isSelf || !r) { b.holeCore = null; continue; }
      if (b.cueFly && !b.leaving && this.depth === 0) { const hole = cueFlyShape(this, b); if (hole) { b.hole = hole; b.holeCore = null; this.holes.push(b); continue; } }   // CUE: a card in flight''')

# A PLACE OR A NICHE IS HELD OPEN UNTIL ITS CARD COMES, AND OPENS AS ITS CARD
# CLEARS IT. A ledger pays out on its bodies' clocks, so whitespace a card
# lands in closed from the moment the change began, while the card was still
# far off, and the ground went to its neighbours for the card to take back
# as it came; and whitespace a card leaves opened on the card's clock, while
# a card flying as a card had cleared the slot at once, the slot's
# neighbours flooding in. On a Cue page a piece a card lands in holds its
# ground until the card is within reach of it and closes as it comes in, all
# of it on the card's ledger; a piece a card leaves opens as the card clears
# it, open by the time the card is half its size clear.
replace('''      this.retireBody(v, 1.2, tOf(v));
      v.table = { mode: 'close', rows, wRem: Math.max(0, v.claim0 - W), f: 0 };''',
        '''      if (name === 'cue' && rows.length) { for (const q of rows) q.from = cueNear(this, q.body, v.rect); W = Math.max(W, v.claim); }   // CUE: held until its card comes
      this.retireBody(v, 1.2, tOf(v));
      v.table = { mode: 'close', rows, wRem: Math.max(0, v.claim0 - W), f: 0 };''')
replace('''        if (this.inRect(r, b.x, b.y)) { rows.push({ body: b, journey: b.journey, w: b.claim }); W += b.claim; continue; }''',
        '''        if (this.inRect(r, b.x, b.y)) { rows.push({ body: b, journey: b.journey, w: b.claim, until: name === 'cue' ? cueClearOf(this, b, r) : undefined }); W += b.claim; continue; }   // CUE: open as its card clears it''')
replace('''        for (const r of tb.rows) { const p = ferryLedgerProgress(this, r, t); num += r.w * p; den += r.w; pmin = Math.min(pmin, p); }''',
        '''        for (const r of tb.rows) { const p0 = ferryLedgerProgress(this, r, t), p = r.until ? Math.min(1, p0 / r.until) : r.from !== undefined ? Math.max(0, (p0 - r.from) / (1 - r.from)) : p0; num += r.w * p; den += r.w; pmin = Math.min(pmin, p); }   // CUE: paced by where the card is''')

# A CARD IN FLIGHT IS NOT PUSHED. Bodies push apart while liquid, whitespace
# bodies too, and a card setting off from the pen was pushed back by the
# cells around it and by its own niche opening at its heart: its journey ran
# ahead and its seed stayed in the slot, a third of the way through the
# journey's clock it had moved 20 px. A card in flight pushes, and is not
# pushed.
replace('''  mfFreedom(b) {''', '''  mfFreedom(b) {
    if (b.cueFly && b.hole) return 0;   // CUE: a card in flight is not pushed''')

# A CARD FLIES OVER WHITESPACE, NOT THROUGH IT. A body in a hole goes out
# through the hole's nearest side, and a card in flight is a hole: a piece of
# whitespace in its path was shoved ahead of it the whole way, and when the
# card landed and was pinned, a wall, the piece was on the wrong side of it
# for good (the pen settled 10 px off its page). Whitespace under a card in
# flight stays where it is, holding what ground the card leaves it, and is
# where it was once the card has passed. (Giving way to the card as it came
# was worse: a site coming out from under a card took its ground back at
# once, and cells split round the card.)
replace('''        if (!b.hole) for (const h of this.holes) {
          if (h === b) continue;''', '''        if (!b.hole) for (const h of this.holes) {
          if (h === b || h.cueFly && b.isVoid) continue;   // CUE: whitespace under a card in flight is flown over''')

# on a story, as on a page, every cell is one card: no gallery opens a field
replace('''    const gallery = !portalFocus && b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);   // PORTAL: on a page every cell is one card''',
        '''    const gallery = !portalFocus && !cue && b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);   // PORTAL: on a page every cell is one card; CUE: on a story too''')

# the cast carries no label (its names title the blurb) and does not hover
replace('''    const pageT = (b === portalFocus || (tell2 && tell2.on.includes(b))) && (PORTAL_TEMPLATES[config.scene] || (config.scene === 'tell' || config.scene === 'tell2' ? { text: true } : null));''',
        '''    const pageT = (b === portalFocus || (tell2 && tell2.on.includes(b)) || (cue && cue.on.includes(b))) && (PORTAL_TEMPLATES[config.scene] || (config.scene === 'tell' || config.scene === 'tell2' || config.scene === 'cue' ? { text: true } : null));''')
replace('''  const path = under.length && (under[0].body === portalFocus || (tell2 && tell2.on.includes(under[0].body))) ? [] : under;''',
        '''  const path = under.length && (under[0].body === portalFocus || (tell2 && tell2.on.includes(under[0].body)) || (cue && cue.on.includes(under[0].body))) ? [] : under;''')

# --- the tick, the paint, the events ---------------------------------------------
replace('''  tellFlow(dt); tellStep(dt); tell2Flow(dt); tell2Step();''', '''  tellFlow(dt); tellStep(dt); tell2Flow(dt); tell2Step(); cueFlow(dt);''')
replace('''  tell2ProseStep(ctx, type, dt, t);''', '''  tell2ProseStep(ctx, type, dt, t);
  cueProseStep(ctx, type, dt, t);''')
replace('''function tellStart(origin) {
  reelDrop(); tell2Drop();''', '''function tellStart(origin) {
  reelDrop(); tell2Drop(); cueDrop();''')
replace('''function tell2Start(origin) {
  reelDrop(); tellDrop();''', '''function tell2Start(origin) {
  reelDrop(); tellDrop(); cueDrop();''')
replace('''  if (b === portalFocus || (tell2 && tell2.on.includes(b))) { reelDrop(); tellDrop(); tell2Drop(); portalHome({ x, y }); }''',
        '''  if (b === portalFocus || (tell2 && tell2.on.includes(b)) || (cue && cue.on.includes(b))) { reelDrop(); tellDrop(); tell2Drop(); cueDrop(); portalHome({ x, y }); }   // CUE: any of the cast clicked goes home''')
replace('''    reelDrop(b); tellDrop(); tell2Drop();''', '''    reelDrop(b); tellDrop(); tell2Drop(); cueDrop();''')
replace('''if (e.key === 'Escape' && (portalFocus || tell || tell2)) { reelDrop(); tellDrop(); tell2Drop(); portalHome(); }''',
        '''if (e.key === 'Escape' && (portalFocus || tell || tell2 || cue)) { reelDrop(); tellDrop(); tell2Drop(); cueDrop(); portalHome(); }''')
replace('''if (tell2) { e.preventDefault(); tell2Scroll(dy); return; }''', '''if (cue) { e.preventDefault(); cueScroll(dy); return; } if (tell2) { e.preventDefault(); tell2Scroll(dy); return; }''')
replace('''if (tell2DragStart(x, y, performance.now()) ||''', '''if (cueDragStart(x, y, performance.now()) || tell2DragStart(x, y, performance.now()) ||''')
replace('''tell2DragMove(x, y, performance.now()); tellDragMove''', '''cueDragMove(x, y, performance.now()); tell2DragMove(x, y, performance.now()); tellDragMove''')
replace('''canvas.addEventListener('pointerup', () => { tell2DragEnd(performance.now());''', '''canvas.addEventListener('pointerup', () => { cueDragEnd(performance.now()); tell2DragEnd(performance.now());''')
replace('''canvas.addEventListener('pointercancel', () => { tell2DragEnd(-1e9);''', '''canvas.addEventListener('pointercancel', () => { cueDragEnd(-1e9); tell2DragEnd(-1e9);''')
replace('''  if (b.dataset.scene === 'tell2') { tell2Start(); return; }   // TELL II: the cast takes the stage
  reelDrop(); tellDrop(); tell2Drop();''', '''  if (b.dataset.scene === 'tell2') { tell2Start(); return; }   // TELL II: the cast takes the stage
  if (b.dataset.scene === 'cue') { cueStart(); return; }   // CUE: the story, on the engine's rules
  reelDrop(); tellDrop(); tell2Drop(); cueDrop();''')

(ROOT / 'cue.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
