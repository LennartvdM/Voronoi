"""Build Tell II from Tell: a small cluster, and the cells take the stage in turn.

A scroll-tell with the cluster as its cast. The cluster is small and sits to
one side; the text blurb stands in the open, in a box of its own. The story
is a set of sequences: a slide sends one cell out of the cluster to a place
around the blurb (above it, below it, beside it, on its diagonals, where its
corner lies behind the text) and the cells already on the stage stay where
they are, so a sequence builds up one, two, three; the next sequence sends
them back into the cluster as its first cell comes out. The cluster is a
revolver: a ring of chambers around a bore, holding the cells not on stage
in the order they will go out. The chamber facing the stage fires, the ring
turns one chamber, and the cells that come back reload the chambers just
behind the front. The bore and the spent chambers are whitespace that yields
at once when the page changes and re-forms after. Every slide is a page like
Portal's, one site a cell and the whitespace exact by the same construction;
the whitespace around the stage is cut once for the whole story. The wheel, a
drag or a flick moves the story, as on a Tell. Without the Tell II button,
the tick, the picture and every drawing command are Tell's (validate.cjs).
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'tell.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '0cd09badc2ed802684a9883c28474480a65265e0d123555eb9df93b663e03c93'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Tell — Hive</title>', '<title>Tell II — Hive</title>')
replace('&larr; Back · Tell</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · Tell: a story scrolls, the cluster stays and its heroes swell · click the hero or Escape for home</span>',
        '&larr; Back · Tell II</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · Tell: the cluster stays, its heroes swell · Tell II: the cells take the stage in turn · click a hero or Escape for home</span>')
replace('''      <button class="scene-btn" data-scene="tell">Tell</button>''',
        '''      <button class="scene-btn" data-scene="tell">Tell</button>
      <button class="scene-btn" data-scene="tell2">Tell II</button>''')

# --- the stage, the revolver, the story's page, its scroll and its blurbs ---------
replace('''const scenes = {''', '''// TELL II. A scroll-tell with the cluster as its cast. The cluster is small
// and sits to one side; the blurb stands in the open, in a box of its own.
// A slide sends one cell out of the cluster to a place around the blurb, and
// the cells already on the stage stay where they are, so a sequence builds
// up; a fresh slide sends the last sequence's cells back into the cluster as
// its own first cell comes out. The cluster is a revolver: a ring of
// chambers around a bore, holding the cells not on stage in the order they
// will go out; the chamber facing the stage fires, the ring turns one
// chamber, and the cells that come back reload the chambers just behind the
// front. The stage and the blurb are the same every slide.
const TELL2_SLIDES = [
  { place: 'top', fresh: true,   lines: [1, 0.86, 0.6] },
  { place: 'br',                 lines: [1, 0.72, 0.9, 0.5] },
  { place: 'left',               lines: [0.94, 1, 0.66] },
  { place: 'bl', fresh: true,    lines: [1, 0.8] },
  { place: 'tr',                 lines: [0.9, 1, 0.76, 0.58] },
  { place: 'below', fresh: true, lines: [1, 0.68, 0.84] },
  { place: 'tl',                 lines: [0.96, 1, 0.52] },
  { place: 'right',              lines: [1, 0.9, 0.7] },
];
// The stage, in fractions of the page: three columns and three rows of
// places around the blurb's box, the box reaching a little over the places
// beside it, so a place on a diagonal has its corner behind the text. The
// rows touch and the places lie on a few shared lines, so the whitespace
// between places is never a sliver, and the cluster stands well off the
// stage: a cluster cell's mirror nearer a corner of a cell on the stage than
// the corner's own reach (about the cell's half-diagonal) would cut it. On a
// phone the stage is a row of three places under the box, a place's column
// fixed for the story, so a cell on the stage never moves for a newcomer.
const TELL2_COLS = { A: [0.09, 0.26], B: [0.33, 0.49], C: [0.56, 0.73] };
const TELL2_ROWS = { top: [0, 0.30], mid: [0.30, 0.70], bottom: [0.70, 1] };
const TELL2_PLACES = { top: ['B', 'top'], below: ['B', 'bottom'], left: ['A', 'mid'], right: ['C', 'mid'], tl: ['A', 'top'], tr: ['C', 'top'], bl: ['A', 'bottom'], br: ['C', 'bottom'] };
const TELL2_PHONE_COL = { top: 1, below: 1, left: 0, right: 2, tl: 0, tr: 2, bl: 0, br: 2 };
const TELL2_BOX = [0.23, 0.25, 0.59, 0.75];
const TELL2_CLUSTER = [0.83, 0.20, 1, 0.80];
const TELL2_PHONE = { box: [0.04, 0.04, 0.96, 0.34], row: [0.36, 0.56], cluster: [0.34, 0.70, 1, 1] };
function tell2Place(where, W, H) {
  if (W < H) { const c = TELL2_PHONE_COL[where] || 0, [y0, y1] = TELL2_PHONE.row; return [c / 3, y0, (c + 1) / 3, y1]; }
  const [c, r] = TELL2_PLACES[where] || TELL2_PLACES.top, x = TELL2_COLS[c], y = TELL2_ROWS[r]; return [x[0], y[0], x[1], y[1]];
}
// THE REVOLVER: the ring of chambers around the cluster's edge, a g by g
// grid's rim, g chosen so the ring holds every cell; the bore is what the
// rim leaves. The ring is ordered from the chamber facing the stage (the
// middle of the cluster's left side, or of its top on a phone) round the
// rim, so the chambers just behind the front come last: the spent ones,
// where the cells coming back reload.
function tell2Ring(n, W, H) {
  const g = Math.max(3, Math.ceil(n / 4) + 1), P = [];
  for (let c = 0; c < g; c++) P.push([c, 0]);
  for (let r = 1; r < g; r++) P.push([g - 1, r]);
  for (let c = g - 2; c >= 0; c--) P.push([c, g - 1]);
  for (let r = g - 2; r >= 1; r--) P.push([0, r]);
  const m = Math.floor((g - 1) / 2), front = W < H ? P.findIndex(q => q[0] === m && q[1] === 0) : P.findIndex(q => q[0] === 0 && q[1] === m);
  return { g, ring: P.slice(front).concat(P.slice(0, front)) };
}
// THE WHITESPACE IS WHAT THE CELLS LEAVE: the page less the stage and the
// cluster, as rectangles. The page is cut along every rectangle's edges into
// a grid; the cells of the grid nothing covers are the whitespace, run
// together down a column where they follow one another, never across a
// grid line: so every corner of a piece is a page corner or a corner of
// the piece or rectangle beside it, never a point on another's edge, where
// the mirrors of two voids meeting a cell's corner would cut the corner by
// a few px. A cell's edge along several pieces is held by the piece its
// seed faces (see the construction).
function tell2Complement(C, R, rects) {
  const r6 = v => Math.round(v * 1e6) / 1e6, E = 1e-9;
  const xs = [...new Set([0, C, ...rects.flatMap(r => [r[0], r[2]])].map(r6))].sort((a, b) => a - b);
  const ys = [...new Set([0, R, ...rects.flatMap(r => [r[1], r[3]])].map(r6))].sort((a, b) => a - b);
  const covered = (x, y) => rects.some(r => x > r[0] + E && x < r[2] - E && y > r[1] + E && y < r[3] - E);
  const out = [];
  for (let i = 0; i < xs.length - 1; i++) {
    let open = null;
    for (let j = 0; j < ys.length - 1; j++) {
      const free = !covered((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2);
      if (free && open) open[3] = ys[j + 1];
      else if (free) { open = [xs[i], ys[j], xs[i + 1], ys[j + 1]]; out.push(open); }
      else open = null;
    }
  }
  return out;
}
// THE STORY IS PLANNED WHEN IT BEGINS, from the cells in id order: the ring
// holds them all; a slide takes the front cell for its place; a fresh slide
// first sends the cast back to the tail, in the order it went out. So the
// cluster always holds the right poise: the next cell out is at the front.
function tell2Plan(cells) {
  const slides = []; let arc = cells.slice(), cast = [];
  for (const sd of TELL2_SLIDES) {
    if (sd.fresh) { arc = arc.concat(cast.map(c => c.b)); cast = []; }
    if (arc.length) { const b = arc[0]; arc = arc.slice(1); cast = cast.concat([{ b, place: sd.place }]); }
    slides.push({ cast, arc });
  }
  return slides;
}
// A slide's page, in lattice units: the stage's rectangles first, one a
// cell of the cast, then the ring's chambers, one a cell of the arc, then
// the whitespace: the bore, the spent chambers, the empty places, and the
// pieces around the stage and the cluster, cut once for the whole story.
// The bore and the spent chambers yield: they give up their ground the
// moment the page changes and take it back once the change has ended.
const tell2Fixed = new Map();
function tell2Page(k, C, R, n, W, H, story) {
  const r6 = v => Math.round(v * 1e6) / 1e6, L = f => [r6(f[0] * C), r6(f[1] * R), r6(f[2] * C), r6(f[3] * R)];
  const sl = story[Math.min(k, story.length - 1)] || { cast: [], arc: [] };
  const cl = L(W < H ? TELL2_PHONE.cluster : TELL2_CLUSTER), { g, ring } = tell2Ring(n, W, H);
  const cw = (cl[2] - cl[0]) / g, ch = (cl[3] - cl[1]) / g, chamber = ([c, r]) => [r6(cl[0] + c * cw), r6(cl[1] + r * ch), r6(cl[0] + (c + 1) * cw), r6(cl[1] + (r + 1) * ch)];
  const stage = sl.cast.map(c => L(tell2Place(c.place, W, H)));
  const content = [...stage, ...ring.slice(0, sl.arc.length).map(chamber)];
  const key = [C, R, W, H].join('|');
  if (!tell2Fixed.has(key)) tell2Fixed.set(key, tell2Complement(C, R, [...Object.keys(TELL2_PLACES).map(p => L(tell2Place(p, W, H))), cl]));
  const filled = new Set(sl.cast.map(c => c.place));
  const voids = tell2Fixed.get(key).map(r => r.slice());
  for (const p of Object.keys(TELL2_PLACES)) if (!filled.has(p) && !(W < H && [...filled].some(q => TELL2_PHONE_COL[q] === TELL2_PHONE_COL[p]))) { const r = L(tell2Place(p, W, H)); if (!voids.some(v => rectsEqual(v, r))) voids.push(r); }
  const bore = [r6(cl[0] + cw), r6(cl[1] + ch), r6(cl[0] + (g - 1) * cw), r6(cl[1] + (g - 1) * ch)]; bore.tell2Yield = true; voids.push(bore);
  for (const q of ring.slice(sl.arc.length)) { const r = chamber(q); r.tell2Yield = true; voids.push(r); }
  voids.tell2 = true;   // solved on its rectangles (see the construction)
  return { content, voids, box: L(W < H ? TELL2_PHONE.box : TELL2_BOX), cast: sl.cast.length, bore, chambers: ring.map(chamber) };
}
const tell2Cache = new Map();
function tell2Scene(h, n) {
  if (!tell2) return null;
  const cells = h.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).sort((a, b) => a.id - b.id);
  if (tell2.n !== cells.length) { tell2.n = cells.length; tell2.story = tell2Plan(cells); tell2Cache.clear(); }   // an add or a remove: the story is planned again from the cells there are
  const k = Math.max(0, tell2.k), sl = tell2.story[Math.min(k, tell2.story.length - 1)];
  tell2.slotOf = new Map(); sl.cast.forEach((c, i) => tell2.slotOf.set(c.b, i)); sl.arc.forEach((b, j) => tell2.slotOf.set(b, sl.cast.length + j));
  const key = [k, h.COLS, h.ROWS, n, h.W, h.H].join('|');
  if (tell2Cache.has(key)) return tell2Cache.get(key);
  const p = tell2Page(k, h.COLS, h.ROWS, n, h.W, h.H, tell2.story), sc = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);
  sc.voids.forEach((q, i) => { if (p.voids[i].tell2Yield) q.tell2Yield = true; });
  tell2Cache.set(key, sc); if (tell2Cache.size > 24) tell2Cache.delete(tell2Cache.keys().next().value);
  return sc;
}
// the story: its scroll (px, a page's height a slide), its speed, the slide
// it is on, its plan, the cells on stage now, and the text's clocks
let tell2 = null;
const tell2Pitch = () => H;
function tell2Start(origin) {
  reelDrop(); tellDrop();
  const cells = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).sort((a, b) => a.id - b.id);
  tell2 = { y: 0, v: 0, k: -1, n: cells.length, story: tell2Plan(cells), on: [], slotOf: null, drag: null, entered: false, alpha: 0, rule: 0, fullAt: -1, seen: -1, changed: -1e9 };
  tell2Cache.clear();
  tell2Go(0, origin || { x: W / 2, y: H / 2 });
}
function tell2Drop() {
  if (!tell2) return;
  tell2 = null;
  for (const v of root.bodies) { if (v.rect && v.rect.reelLive) v.rect.reelLive = false; v.tell2Yield = false; }
}
// a slide: the front cell takes its place; on a fresh slide the last cast
// goes back into the ring first; a page change with Portal's smoothness,
// spreading from the front. The first of the cast is the page's image, for
// the click home.
function tell2Go(k, origin) {
  if (!tell2) return;
  tell2.k = k; const sl = tell2.story[Math.min(k, tell2.story.length - 1)];
  const was = tell2.on.slice();
  tell2.on = sl.cast.map(c => c.b).filter(b => !b.leaving); tell2.changed = simTime;
  for (const b of root.bodies) b.tell2Stay = false;
  for (const c of sl.cast) if (was.includes(c.b)) c.b.tell2Stay = true;   // on the stage already, at its place: a bystander to this change
  const front = tell2.on[tell2.on.length - 1] || null;
  portalFocus = tell2.on[0] || null; portalFlip = false;
  portalEnter('tell2', origin || (front ? { x: front.x, y: front.y } : { x: W / 2, y: H / 2 }));
}
// the flow of the story, a Tell's: a speed eases away, a slow story snaps
// to its slide, the slide the story is on is the one nearest, and a change
// is made at most every quarter second, since each is a page change. The
// bore and the spent chambers are marked to yield.
function tell2Flow(dt) {
  if (!tell2) return;
  const pitch = tell2Pitch(), last = (TELL2_SLIDES.length - 1) * pitch;
  if (!tell2.drag) {
    const snapping = Math.abs(tell2.v) < 60;
    tell2.v *= Math.exp(-dt / (snapping ? TELL_SNAP : TELL_RELAX));
    if (Math.abs(tell2.v) < 0.05) tell2.v = 0;
    tell2.y += tell2.v * dt;
    if (tell2.y < 0) { tell2.y = 0; tell2.v = 0; }
    if (tell2.y > last) { tell2.y = last; tell2.v = 0; }
    if (snapping) { const target = Math.round(tell2.y / pitch) * pitch; tell2.y += (target - tell2.y) * (1 - Math.exp(-dt / TELL_SNAP)); }
  }
  const k = Math.max(0, Math.min(TELL2_SLIDES.length - 1, Math.round(tell2.y / pitch)));
  if (k !== tell2.k && simTime - tell2.changed > 0.25) tell2Go(k, null);
  if (!tell2.entered && guestLeft <= 0) tell2.entered = true;
  for (const v of root.bodies) if (v.isVoid) v.tell2Yield = !!(v.rect && v.rect.tell2Yield);
}
// THE SETTLED SLIDE IS THE AUTHORED ONE. Once a slide's change has ended the
// authored weights are handed to every body each frame, the ring's, the
// cast's and the whitespace's mirrors alike, as a reel hands its own (the
// bore and the spent chambers once they have taken their ground back): the
// whitespace here is cut into pieces, and the live auction, solving the
// same claims from wherever it was, settles a hair off the authored diagram
// near a piece's mirrors, which sit close behind a short edge. Handed, the
// diagram is the authored one, exact. A piece no mirror stands in (its whole
// is held by its neighbours' mirrors) keeps its own site.
function tell2Step() {
  if (!tell2 || guestLeft > 0) return;
  const n = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).length, sc = tell2Scene(root, n);
  if (!sc) return;
  for (const b of root.bodies) {
    if (b.isSelf || b.leaving || !b.rect || (!b.isVoid && b.journey)) continue;   // a void keeps its journey's record; a card still travelling is not handed
    if (b.isVoid) {
      if (b.tell2Yield && b.claim < 0.99 * b.claimTarget) continue;   // still taking its ground back: it grows at its own pace among the handed
      if (!b.rect.reelLive) { const j = sc.voids.findIndex(r => rectsEqual(r, b.rect)); if (j < 0) continue; if (!sc.voids[j].mfSites.length) { b.claimTarget = CLAIM_MIN; b.claim = CLAIM_MIN; continue; } const r = Object.assign([], sc.voids[j]); r.reelLive = true; b.rect = r; b.formRect = r; }   // a piece no mirror stands in holds nothing: its whole is held by its neighbours' mirrors
      b.claimTarget = rectArea(b.rect); b.claim = b.claimTarget;
    } else {
      const i = sc.content.findIndex(r => rectsEqual(r, b.rect)); if (i < 0) continue;
      b.claimTarget = sc.content[i].mfArea; b.claim = b.claimTarget;
      const [ex, ey] = root.rectCenter(b.rect); b.x = ex; b.y = ey; b.vx = 0; b.vy = 0;
      const q = b.subs[0]; q.w = sc.weights[i]; q.live = true;
    }
  }
}
function tell2Scroll(dy) {
  if (!tell2) return false;
  if (tell2.drag || Math.abs(dy) < 1) return true;
  const pitch = tell2Pitch(), aim = Math.max(0, Math.min(TELL2_SLIDES.length - 1, Math.round(tell2.y / pitch) + Math.sign(dy)));
  tell2.v = reelClampV((aim * pitch - tell2.y) / TELL_RELAX);
  return true;
}
function tell2DragStart(x, y, t) { if (!tell2) return false; tell2.drag = { y0: tell2.y, p0: y, last: y, t, v: 0 }; tell2.v = 0; return true; }
function tell2DragMove(x, y, t) {
  if (!tell2 || !tell2.drag) return false;
  const d = tell2.drag, dt = Math.max(1e-3, (t - d.t) / 1000), last = (TELL2_SLIDES.length - 1) * tell2Pitch();
  tell2.y = Math.max(0, Math.min(last, d.y0 + (d.p0 - y)));
  const v = (d.last - y) / dt; d.v += (v - d.v) * Math.min(1, dt / 0.05); d.last = y; d.t = t;
  return true;
}
function tell2DragEnd(t) { if (!tell2 || !tell2.drag) return false; const d = tell2.drag; tell2.v = t - d.t > 120 ? 0 : reelClampV(d.v); tell2.drag = null; return true; }
// The blurbs, in the box: each at its place on the scroll, the slide's and
// its neighbours' as they pass, a box's height apart, titled with its cast's
// names over its lines, fading at the box's ends. The text is set once the
// entry has ended and stays: the cast changes under it, and a corner of a
// cell on the stage may lie behind it. A rule along the box's left edge
// comes a beat after the text has fully appeared.
function tell2ProseStep(ctx, type, dt, t) {
  if (!tell2) return;
  const p = tell2, gap = t - p.seen, el = p.seen < 0 || gap > 0.1 ? dt : gap;
  p.seen = t;
  const v = p.entered;
  p.alpha += ((v ? 1 : 0) - p.alpha) * (1 - Math.exp(-el / (v ? 0.30 : 0.08)));
  if (!v || p.alpha <= 0.97) p.fullAt = -1; else if (p.fullAt < 0) p.fullAt = t;
  p.rule += ((v && p.fullAt >= 0 && t - p.fullAt > 0.25 ? 1 : 0) - p.rule) * (1 - Math.exp(-el / (v ? 0.45 : 0.08)));
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
  const measure = Math.min(560, x1 - x0), pitch = tell2Pitch(), travel = y1 - y0;
  ctx.beginPath(); ctx.moveTo(r[0], r[1]); ctx.lineTo(r[2], r[1]); ctx.lineTo(r[2], r[3]); ctx.lineTo(r[0], r[3]); ctx.closePath(); ctx.clip();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  for (let k = p.k - 1; k <= p.k + 1; k++) {
    if (k < 0 || k >= TELL2_SLIDES.length) continue;
    const lines = TELL2_SLIDES[k].lines, hb = Math.round(title * 1.8) + lines.length * lead;
    const yk = y0 + (y1 - y0 - hb) / 2 + (k * pitch - p.y) / pitch * travel;
    const edge = Math.min(1, Math.max(0, (yk + hb - y0) / 40), Math.max(0, (y1 - yk) / 40));
    const a = p.alpha * edge;
    if (a < 0.01) continue;
    const cast = (p.story[k] ? p.story[k].cast : []).map(c => c.b.name).join(' · ');
    ctx.globalAlpha = 0.92 * a; ctx.font = `600 ${title}px system-ui, sans-serif`; ctx.fillText(cast, x0, yk);
    ctx.globalAlpha = 0.5 * a; ctx.beginPath(); ctx.moveTo(x0, yk + Math.round(title * 1.3) + 0.5); ctx.lineTo(x0 + Math.round(title * 1.6), yk + Math.round(title * 1.3) + 0.5); ctx.stroke();
    ctx.globalAlpha = 0.20 * a;
    let y = yk + Math.round(title * 1.8);
    for (const f of lines) { roundedPath(ctx, [[x0, y], [x0 + measure * f, y], [x0 + measure * f, y + line], [x0, y + line]], line / 2, false); ctx.fill(); y += lead; }
  }
  ctx.restore();
}
const scenes = {''')

# --- the construction holds an edge that lies along several voids ------------------
# The whitespace of a Tell II page is cut into rectangles, so a cell's edge
# can run along two of them; Portal's contact rule (the cell's edge within
# the void's) found neither, and the edge went unheld. An edge no void holds
# whole is held by the piece the seed faces: a mirror across the edge at the
# seed's own line holds the whole edge, whichever pieces it runs along.
# Portal's own pages are as they were: every edge of theirs a void holds whole.
replace('''        vr.forEach((v, vi) => {
          const on = (c, lo, hi, ax) => Math.abs(p[ax] - c) < 1e-5 && Math.abs(q[ax] - c) < 1e-5 && Math.min(p[1 - ax], q[1 - ax]) > lo - 1e-5 && Math.max(p[1 - ax], q[1 - ax]) < hi + 1e-5;
          let side = null;
          if (on(v[0], v[1], v[3], 0)) side = 'left'; else if (on(v[2], v[1], v[3], 0)) side = 'right'; else if (on(v[1], v[0], v[2], 1)) side = 'top'; else if (on(v[3], v[0], v[2], 1)) side = 'bottom';
          if (side && !contacts.some(c => c.i === i && c.vi === vi && c.side === side)) contacts.push({ i, vi, side, mid: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] });
        });''',
        '''        let held = false;
        vr.forEach((v, vi) => {
          const on = (c, lo, hi, ax) => Math.abs(p[ax] - c) < 1e-5 && Math.abs(q[ax] - c) < 1e-5 && Math.min(p[1 - ax], q[1 - ax]) > lo - 1e-5 && Math.max(p[1 - ax], q[1 - ax]) < hi + 1e-5;
          let side = null;
          if (on(v[0], v[1], v[3], 0)) side = 'left'; else if (on(v[2], v[1], v[3], 0)) side = 'right'; else if (on(v[1], v[0], v[2], 1)) side = 'top'; else if (on(v[3], v[0], v[2], 1)) side = 'bottom';
          if (side) { held = true; if (!contacts.some(c => c.i === i && c.vi === vi && c.side === side)) contacts.push({ i, vi, side, mid: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] }); }
        });
        if (!held) vr.forEach((v, vi) => {   // TELL II: an edge along several voids is held by the piece the seed faces
          const s = seeds[i];
          const on = (c, lo, hi, ax) => Math.abs(p[ax] - c) < 1e-5 && Math.abs(q[ax] - c) < 1e-5 && Math.max(p[1 - ax], q[1 - ax]) > lo + 1e-5 && Math.min(p[1 - ax], q[1 - ax]) < hi - 1e-5 && s[1 - ax] > lo - 1e-5 && s[1 - ax] < hi + 1e-5;
          let side = null;
          if (on(v[0], v[1], v[3], 0)) side = 'left'; else if (on(v[2], v[1], v[3], 0)) side = 'right'; else if (on(v[1], v[0], v[2], 1)) side = 'top'; else if (on(v[3], v[0], v[2], 1)) side = 'bottom';
          if (side && !contacts.some(c => c.i === i && c.vi === vi && c.side === side)) contacts.push({ i, vi, side, mid: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] });
        });''')

# --- the ring's pocket is solved on its own ground -----------------------------------
# The pocket's outline is its bounds to the solver, and a ring's outline is
# not convex: clipped by its edges' half-planes as a convex bound, a cell
# came out with edges that were nobody's. A Tell II pocket's bounds are its
# box; its ground is the pieces.
replace('''const portalCache = new Map();''', '''function portalBox(rects) {   // TELL II: a pocket's box, a convex bound for a ring
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const r of rects) { x0 = Math.min(x0, r[0]); y0 = Math.min(y0, r[1]); x1 = Math.max(x1, r[2]); y1 = Math.max(y1, r[3]); }
  return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
}
const portalCache = new Map();''')
# The ring's chambers enclose the bore, and Portal's pocket outline keeps only
# the largest loop, so the pocket's ground took in the bore and the spent
# chambers and the cells were solved as if they owned them. A Tell II page's
# pocket is solved on its rectangles themselves, handed to the solver as
# convex pieces, so its ground is exactly the chambers and the stage; a cell
# solved on pieces has a piece per rectangle it lies on, and every piece's
# edges are looked at for contacts. Portal's own pages are solved as before.
replace('''    const ref = idx.length === 1 ? null : solveWeights(idx.map(i => seeds[i]), idx.map(i => (rects[i][2] - rects[i][0]) * (rects[i][3] - rects[i][1]) * (content[i].mfSwell || 1)), poly, null, { maxIter: 60, tol: 1e-9 });   // TELL: a hero's area is its card's, times its swell''',
        '''    const ref = idx.length === 1 ? null : solveWeights(idx.map(i => seeds[i]), idx.map(i => (rects[i][2] - rects[i][0]) * (rects[i][3] - rects[i][1]) * (content[i].mfSwell || 1)), voids.tell2 ? portalBox(idx.map(i => rects[i])) : poly, null, voids.tell2 ? { maxIter: 60, tol: 1e-9, tris: idx.map(i => convexPlanes([[rects[i][0], rects[i][1]], [rects[i][2], rects[i][1]], [rects[i][2], rects[i][3]], [rects[i][0], rects[i][3]]])), domainArea: idx.reduce((q, i) => q + (rects[i][2] - rects[i][0]) * (rects[i][3] - rects[i][1]) * (content[i].mfSwell || 1), 0) } : { maxIter: 60, tol: 1e-9 });   // TELL: a hero's area is its card's, times its swell   // TELL II: the pocket's ground is its rectangles''')
replace('''    idx.forEach((i, k) => {
      const pts = cells[k].pts;
      for (let e = 0; e < pts.length; e++) {''', '''    idx.forEach((i, k) => {
      for (const part of (cells[k].pieces || [cells[k]])) {   // TELL II: a cell solved on pieces has a piece per rectangle; a piece of no area (a tie along a neighbour's edge) is no contact
      if (part !== cells[k] && Math.abs(ringArea(part.pts)) < 1e-6) continue;
      const pts = part.pts;
      for (let e = 0; e < pts.length; e++) {''')
replace('''          if (side && !contacts.some(c => c.i === i && c.vi === vi && c.side === side)) contacts.push({ i, vi, side, mid: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] });
        });
      }
    });''', '''          if (side && !contacts.some(c => c.i === i && c.vi === vi && c.side === side)) contacts.push({ i, vi, side, mid: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] });
        });
      }
      }
    });''')

# --- a Tell II slide is a page to the engine; every cell takes its own slot --------
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell' ? tellScene(this, content.length) :''',
        '''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell2' ? tell2Scene(this, content.length) : this.depth===0 && name === 'tell' ? tellScene(this, content.length) :''')
replace('''  if (!portalFocus || !(name in PORTAL_TEMPLATES || name === 'tell')) return;   // TELL: a story's hero takes the first slot when the page is laid again (an add, a remove, a resize)''',
        '''  if (name === 'tell2' && tell2 && tell2.slotOf) {   // TELL II: the cast takes the stage's slots and the ring's cells their chambers, as the story plans; nothing is matched by distance
    content.forEach((b, k) => { const slot = tell2.slotOf.get(b); if (slot !== undefined && slot < gotS.length) gotS[k] = slot; });
    return;
  }
  if (!portalFocus || !(name in PORTAL_TEMPLATES || name === 'tell')) return;   // TELL: a story's hero takes the first slot when the page is laid again (an add, a remove, a resize)''')
replace('''    if (name in PORTAL_TEMPLATES || name === 'tell') for (const b of content) { const j = b.journey, p = b.path;''',
        '''    if (name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') for (const b of content) { const j = b.journey, p = b.path;''')
replace('''    if ((name in PORTAL_TEMPLATES || name === 'tell') && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''',
        '''    if ((name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''')
replace('''        if (!(name in PORTAL_TEMPLATES || name === 'tell') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''',
        '''        if (!(name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''')
# A PIECE OF WHITESPACE THAT STAYS TAKES THE NEW PAGE'S CLAIM. A void kept
# across a page change (its rectangle in the new page too) kept the claim it
# had, though the new page may give it other mirrors or none: a piece beside
# the stage holds mirrors of a cell on a place one slide and nothing the
# next, and a stale claim of several cells' worth, times ten pieces, had the
# auction handing every cell less than its due. On a Tell II page a staying
# void's target is the new page's; other pages are as they were.
replace('''      if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; } stays.add(same); continue; }''',
        '''      if (same) { if(r.mfSites) { same.rect=r; same.formRect=r; if (name === 'tell2') same.claimTarget = Math.max(CLAIM_MIN, rectArea(r)); } stays.add(same); continue; }   // TELL II: a staying piece takes the new page's claim''')
# a cell of the cast that keeps its place is a BYSTANDER, as a settled cell
# is on the engine's own pages: not re-seated, no journey, so it does not
# drift off while it waits for a change that is not its own
replace('''    if (rectsEqual(rect, b.rect) && b.formRect === b.rect && b.crystal === 1 && !b.leaving
        && Math.abs(b.x - ex) < 0.01 && Math.abs(b.y - ey) < 0.01) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); return; }''',
        '''    if (rectsEqual(rect, b.rect) && b.formRect === b.rect && b.crystal === 1 && !b.leaving
        && Math.abs(b.x - ex) < 0.01 && Math.abs(b.y - ey) < 0.01) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); return; }
    if (b.tell2Stay && rectsEqual(rect, b.rect) && !b.leaving && !b.journey && Math.abs(b.x - ex) < 1 && Math.abs(b.y - ey) < 1) { b.claim0 = b.claim; b.claimTarget = rectArea(rect); b.pin = 1; return; }   // TELL II: a cell of the cast keeping its place''')
# the bore and the spent chambers yield: their ground goes the moment the page changes and comes back once it has ended
replace('''      if (b.table) {
        // a void keeps a ledger: its claim is the claim-weighted progress of''',
        '''      if (b.isVoid && b.tell2Yield && !b.table) {   // TELL II: whitespace that yields, at once when the page changes, back over a third of a second after
        const want = guestLeft > 0 ? CLAIM_MIN : b.claimTarget;
        b.claim += (want - b.claim) * (1 - Math.exp(-dt / (want < b.claim ? 0.12 : 0.35)));
        continue;
      }
      if (b.table) {
        // a void keeps a ledger: its claim is the claim-weighted progress of''')
# a cell on the stage carries no label (its name titles the blurb) and does not hover
replace('''    const pageT = b === portalFocus && (PORTAL_TEMPLATES[config.scene] || (config.scene === 'tell' ? { text: true } : null));   // TELL: the slide's image carries no label''',
        '''    const pageT = (b === portalFocus || (tell2 && tell2.on.includes(b))) && (PORTAL_TEMPLATES[config.scene] || (config.scene === 'tell' || config.scene === 'tell2' ? { text: true } : null));   // TELL: the slide's image carries no label; TELL II: nor does any of the cast''')
replace('''  const path = under.length && under[0].body === portalFocus ? [] : under;   // the open page's image is not a card''',
        '''  const path = under.length && (under[0].body === portalFocus || (tell2 && tell2.on.includes(under[0].body))) ? [] : under;   // the open page's image is not a card; TELL II: nor is the cast''')

# --- the tick, the paint, the events ---------------------------------------------
replace('''  tellFlow(dt); tellStep(dt);''', '''  tellFlow(dt); tellStep(dt); tell2Flow(dt); tell2Step();''')
replace('''  tellProseStep(ctx, type, dt, t);''', '''  tellProseStep(ctx, type, dt, t);
  tell2ProseStep(ctx, type, dt, t);''')
replace('''function tellStart(origin) {
  reelDrop();''', '''function tellStart(origin) {
  reelDrop(); tell2Drop();''')
replace('''  if (b === portalFocus) { reelDrop(); tellDrop(); portalHome({ x, y }); }
  else {
    reelDrop(b); tellDrop();''', '''  if (b === portalFocus || (tell2 && tell2.on.includes(b))) { reelDrop(); tellDrop(); tell2Drop(); portalHome({ x, y }); }   // TELL II: any of the cast clicked goes home
  else {
    reelDrop(b); tellDrop(); tell2Drop();''')
replace('''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && (portalFocus || tell)) { reelDrop(); tellDrop(); portalHome(); } });''',
        '''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && (portalFocus || tell || tell2)) { reelDrop(); tellDrop(); tell2Drop(); portalHome(); } });''')
replace('''if (tell) { e.preventDefault(); tellScroll(dy); return; } if (!reel) return;''',
        '''if (tell2) { e.preventDefault(); tell2Scroll(dy); return; } if (tell) { e.preventDefault(); tellScroll(dy); return; } if (!reel) return;''')
replace('''if (tellDragStart(x, y, performance.now()) || reelDragStart(x, y, performance.now()))''',
        '''if (tell2DragStart(x, y, performance.now()) || tellDragStart(x, y, performance.now()) || reelDragStart(x, y, performance.now()))''')
replace('''tellDragMove(x, y, performance.now()); reelDragMove(x, y, performance.now()); });''',
        '''tell2DragMove(x, y, performance.now()); tellDragMove(x, y, performance.now()); reelDragMove(x, y, performance.now()); });''')
replace('''canvas.addEventListener('pointerup', () => { tellDragEnd(performance.now()); reelDragEnd(performance.now()); });''',
        '''canvas.addEventListener('pointerup', () => { tell2DragEnd(performance.now()); tellDragEnd(performance.now()); reelDragEnd(performance.now()); });''')
replace('''canvas.addEventListener('pointercancel', () => { tellDragEnd(-1e9); reelDragEnd(-1e9); });''',
        '''canvas.addEventListener('pointercancel', () => { tell2DragEnd(-1e9); tellDragEnd(-1e9); reelDragEnd(-1e9); });''')
replace('''  if (b.dataset.scene === 'tell') { tellStart(); return; }   // TELL: the story begins
  reelDrop(); tellDrop();''', '''  if (b.dataset.scene === 'tell') { tellStart(); return; }   // TELL: the story begins
  if (b.dataset.scene === 'tell2') { tell2Start(); return; }   // TELL II: the cast takes the stage
  reelDrop(); tellDrop(); tell2Drop();''')

(ROOT / 'tell2.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
