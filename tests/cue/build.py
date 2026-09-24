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
// keeps it; and the cells left, the ones coming home, take the open niches
// nearest them. A cell is bound for its rectangle, so a change interrupted
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
  const home = cells.filter(b => !used.has(b)), free = slots.map((r, s) => s).filter(s => !slot[s]);
  cueMatch(home.length, free.length, (i, j) => d2(home[i], slots[free[j]])).forEach((j, i) => { if (j >= 0) slot[free[j]] = home[i]; });
  return { names, stage, slots, place, slot, kept };
}
// THE PEN IS SOLVED WHOLE. The page is laid as if every slot were held, so
// the pen is one pocket, its cells solved together as a cell of the pen
// always is; then an open slot is whitespace holding exactly the ground a
// cell there would hold, one site at the slot's seed with the slot's share.
// So the pen keeps its shape at rest whichever slots are open, a niche is the
// gap its cell left, and a cell coming home into it finds its own ground.
const cueCache = new Map();
function cueScene(h, n) {
  if (!cue) return null;
  const cells = h.bodies.filter(b => !b.isVoid && !b.leaving && !b.isSelf), p = cuePlan(h, cue.k, cells);
  const cast = p.place.map((b, j) => j).filter(j => p.place[j]), places = cast.map(j => p.names[j]);
  const key = [h.COLS, h.ROWS, h.W, h.H, n, places.join(',')].join('|');
  let whole = cueCache.get(key);
  if (!whole) {
    whole = portalDecorate(cast.map(j => p.stage[j]).concat(p.slots), cueWhitespace(h.COLS, h.ROWS, h.W, h.H, places, n), h.W, h.H, h.COLS, h.ROWS);
    cueCache.set(key, whole); if (cueCache.size > 24) cueCache.delete(cueCache.keys().next().value);
  }
  const content = [], niches = [];
  whole.content.forEach((r, i) => {
    const s = i - cast.length;
    if (s < 0 || p.slot[s]) { content.push(r); return; }
    const q = r.slice(); q.mfSites = [{ x: r.mfSeed[0] - (r[0] + r[2]) / 2, y: r.mfSeed[1] - (r[1] + r[3]) / 2, q: r.mfArea }]; q.mfArea = r.mfArea; q.mfKey = JSON.stringify(q.mfSites); q.mfRest = true;
    niches.push(q);
  });
  const owner = cast.map(j => p.place[j]).concat(p.slot.filter(Boolean));
  cue.slotOf = new Map(owner.map((b, i) => [b, i])); cue.on = cast.map(j => p.place[j]);
  for (const b of cells) b.cueStay = p.kept.has(b);
  return { content, voids: whole.voids.concat(niches), cast: cast.length };
}
// the page's slots, by the plan: the matching above, handed to the engine
function cueAssign(content, centers) {
  const g = content.map(b => cue.slotOf.get(b));
  return g.some(v => v === undefined) ? assignStations(content, centers) : g;
}
// A PIECE OF WHITESPACE A CELL WILL BRUSH: one with a site within the
// cell's reach of its path, the bent path seatBody gives it. Only there can
// the wall between them swing the cell about; a piece a cell crosses far
// from its sites holds, so the whitespace that closes for a crossing is no
// more than the crossing needs, and the cells around it are left their frame.
function cueCrosses(h, r, content, rectOf) {
  const sites = (r.mfSites || []).map(q => [((r[0] + r[2]) / 2 + q.x) * h.PW, ((r[1] + r[3]) / 2 + q.y) * h.PH]);
  if (!sites.length) return false;
  for (const b of content) {
    const q = rectOf.get(b); if (!q) continue;
    const [ex, ey] = h.rectCenter(q), dx = ex - b.x, dy = ey - b.y;
    if (Math.hypot(dx, dy) < 4) continue;
    const reach = 0.5 * Math.sqrt((q[2] - q[0]) * h.PW * (q[3] - q[1]) * h.PH);   // half the side of the square it will fill
    const bend = config.swirl * 0.55 * h.swirlSign * (0.7 + 0.6 * hash01(b.id + h.shift, 12)), cx = (b.x + ex) / 2 - dy * bend, cy = (b.y + ey) / 2 + dx * bend;
    for (let i = 1; i <= 20; i++) { const e = i / 20, m = 1 - e, x = m * m * b.x + 2 * m * e * cx + e * e * ex, y = m * m * b.y + 2 * m * e * cy + e * e * ey; for (const s of sites) if (Math.hypot(s[0] - x, s[1] - y) < reach) return true; }
  }
  return false;
}
// the story: its scroll (px, a page's height a slide), its speed, the slide
// it is on, the cast on stage, the bench, and the text's clocks
let cue = null;
function cueStart(origin) {
  reelDrop(); tellDrop(); tell2Drop();
  portalFocus = null; portalFlip = false;
  cue = { y: 0, v: 0, k: 0, on: [], bench: new Set(), titles: [], tf: [], drag: null, entered: false, alpha: 0, rule: 0, fullAt: -1, seen: -1, changed: -1e9 };
  cueCache.clear();
  cueGo(0, origin || { x: W / 2, y: H / 2 });
}
function cueDrop() { if (!cue) return; cue = null; for (const b of root.bodies) delete b.cueStay; }
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
# WHITESPACE A CELL WILL CROSS IS CUT AGAIN; WHITESPACE THAT STAYS IS
# RE-SEATED, LIKE ANY BODY GIVEN A NEW RECTANGLE. A void stays across a
# change when the new page wants one exactly where it is. On a Cue page the
# stage is whitespace and the cells going home or coming out cross it: a
# piece in a traveller's way that stays holds its ground at its full claim
# and squeezes the traveller's cell to a wedge, so a piece a path crosses
# does not stay: it closes on its clock, and the new one opens behind the
# crossers (see below). And the piece beside a place holds the mirrors of the
# cell there, so when the place fills or empties the piece stays with other
# mirrors and another claim; kept on its old ledger (all paid) the new claim
# would be its claim the next frame, a step every neighbour feels, so such a
# piece is seated on the new page as a cell is, on its own clock from where
# the change reaches it, its claim and its mirrors eased over the journey.
# A piece nobody crosses whose mirrors are the same stays as it was.
replace('''      const same = oldVoids.find(v => rectsEqual(v.rect, r) && !stays.has(v));''',
        '''      let same = oldVoids.find(v => rectsEqual(v.rect, r) && !stays.has(v));''')
replace('''    const stays = new Set(), newVoids = [], rectOfVoid = new Map();''',
        '''    const stays = new Set(), newVoids = [], rectOfVoid = new Map(), cueSeat = [];''')
replace('''      if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; if (name === 'tell2') same.claimTarget = Math.max(CLAIM_MIN, rectArea(r)); } stays.add(same); continue; }''',
        '''      if (same && name === 'cue' && cueCrosses(this, r, content, rectOf)) same = null;   // CUE: a piece a cell will cross is cut again
      if (same && name === 'cue' && r.mfSites && same.rect.mfKey !== r.mfKey) { cueSeat.push([same, r]); stays.add(same); continue; }   // CUE: a staying piece with other mirrors is seated again
      if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; if (name === 'tell2') same.claimTarget = Math.max(CLAIM_MIN, rectArea(r)); } stays.add(same); continue; }''')
replace('''    const tOf = b => { const e = times.get(b); return e ? e.T : 0; };

    // the occupant: whoever sits, right now, where a body is going''',
        '''    const tOf = b => { const e = times.get(b); return e ? e.T : 0; };
    for (const [v, r] of cueSeat) { v.formRect = null; this.seatBody(v, r, 0, { t0: this.t, delay: tOf(v), dur: 0.9, c0: v.crystal }); }   // CUE: on its own clock, from where the change reaches it

    // the occupant: whoever sits, right now, where a body is going''')

# AND A PIECE CUT AGAIN CLOSES ON THE CLOCKS OF THE CELLS CROSSING IT. On its
# own clock it would close as soon as the change reaches it, and the ground
# it gives up would go to whoever is beside it, the cell on the stage above
# it as much as the traveller, for as long as the traveller takes to come:
# the cell on the stage would swell into it and back. Its crossers are on its
# ledger instead, each until the point of its path where it enters: the
# piece gives up its ground as they come, and is gone as they arrive.
replace('''      this.retireBody(v, 1.2, tOf(v));
      v.table = { mode: 'close', rows, wRem: Math.max(0, v.claim0 - W), f: 0 };''',
        '''      if (name === 'cue' && !rows.length) for (const b of content) {   // CUE: a piece cut again closes as its crossers come
        const p = b.path; if (!p || !b.journey || b.journey.t0 !== this.t) continue;
        let enter = -1;
        for (let k = 1; k < 20 && enter < 0; k++) { const e = k / 20, m = 1 - e, x = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex, y = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey; if (this.inRect(v.rect, x, y)) enter = e; }
        if (enter > 0) { rows.push({ body: b, journey: b.journey, w: v.claim, until: enter }); W += v.claim; }
      }
      this.retireBody(v, 1.2, tOf(v));
      v.table = { mode: 'close', rows, wRem: Math.max(0, v.claim0 - W), f: 0 };''')
replace('''        for (const r of tb.rows) { const p = ferryLedgerProgress(this, r, t); num += r.w * p; den += r.w; pmin = Math.min(pmin, p); }''',
        '''        for (const r of tb.rows) { const p = r.until ? Math.min(1, ferryLedgerProgress(this, r, t) / r.until) : ferryLedgerProgress(this, r, t); num += r.w * p; den += r.w; pmin = Math.min(pmin, p); }   // CUE: a crosser counts until it enters''')

# NEW WHITESPACE WAITS FOR THE CELLS CROSSING IT. Portal's rule, and the one
# that matters most here: the stage is whitespace, and a cell going back to
# the cluster or coming out of it crosses it. A piece that opens on its own
# clock stands in the traveller's way, its mirrors a few px off the
# traveller's seed, and the wall between them swings the traveller's cell
# about; a piece with the crossers on its ledger opens behind them.
replace('''        if (!(name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''',
        '''        if (!(name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2' || name === 'cue') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;   // CUE: a slide's whitespace waits for its crossers too''')

# A CELL OF THE CAST THAT KEEPS ITS PLACE HOLDS STILL. At the root nothing is
# a wall, and a bystander re-seated on a journey of no length is held only by
# its spring: a cell passing nudges it, and the whitespace beside it, cut
# again as a traveller crosses, lets it swell. A cell of the cast the next
# slide keeps, sitting on its place, is not re-seated: it is pinned there,
# and pinned on its rectangle it is a wall for the change, as Tell II's was.
replace('''    if (b.tell2Stay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // TELL II: a cell of the cast keeping its place''',
        '''    if (b.tell2Stay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // TELL II: a cell of the cast keeping its place
    if (b.cueStay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // CUE: a cell of the cast keeping its place holds still''')

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
