"""Build Tell II from Tell: a small cluster, and the cells take the stage in turn.

A scroll-tell with the cluster as its cast. The cluster is small and sits to
one side; the text blurb stands in the open, in a box of its own. Each slide
sends one, two or three cells out of the cluster to the stage, places around
the blurb (above it, below it, beside it, on its diagonals, where their
corners may lie behind the text), and when the slide is done they go back
into the cluster as the next slide's cells come out: the cells take turns as
the illustration, and a slide with two or three shows a sequence. The stage
and the blurb are the same every slide; only the cast changes. Every slide
is a page like Portal's, one site a cell and the whitespace exact by the
same construction. The wheel, a drag or a flick moves the story, as on a
Tell. Without the Tell II button, the tick, the picture and every drawing
command are Tell's (validate.cjs).
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

# --- the stage, the cast, the story's page, its scroll and its blurbs -------------
replace('''const scenes = {''', '''// TELL II. A scroll-tell with the cluster as its cast. The cluster is small
// and sits to one side; the blurb stands in the open, in a box of its own.
// Each slide sends one, two or three cells out of the cluster to the stage,
// places around the blurb, and when the slide is done they go back into the
// cluster as the next slide's cells come out. The stage and the blurb are
// the same every slide; only the cast changes.
const TELL2_SLIDES = [
  { stage: ['top'],                   lines: [1, 0.86, 0.6] },
  { stage: ['tl', 'br'],              lines: [1, 0.72, 0.9, 0.5] },
  { stage: ['left'],                  lines: [0.94, 1, 0.66] },
  { stage: ['top', 'below', 'right'], lines: [1, 0.8] },
  { stage: ['bl'],                    lines: [0.9, 1, 0.76, 0.58] },
  { stage: ['tr', 'left'],            lines: [1, 0.68, 0.84] },
  { stage: ['below'],                 lines: [0.96, 1, 0.52] },
  { stage: ['tl', 'tr', 'bl'],        lines: [1, 0.9, 0.7] },
];
// The stage, in fractions of the page: three columns and three rows of
// places around the blurb's box, the box reaching a little over the places
// beside it, so a place on a diagonal has its corner behind the text. The
// rows touch and the places lie on a few shared lines, so the whitespace
// between places is never a sliver, and the cluster stands well off the
// stage: Portal's mirrors hold a cell's edge exactly, but another cell's
// mirror nearer a corner of the cell than the corner's own reach (about the
// cell's half-diagonal) would cut the corner, so the cluster's mirrors
// stand farther than that from the stage's corners.
const TELL2_COLS = { A: [0.09, 0.26], B: [0.33, 0.49], C: [0.56, 0.73] };
const TELL2_ROWS = { top: [0, 0.30], mid: [0.30, 0.70], bottom: [0.70, 1] };
const TELL2_PLACES = { top: ['B', 'top'], below: ['B', 'bottom'], left: ['A', 'mid'], right: ['C', 'mid'], tl: ['A', 'top'], tr: ['C', 'top'], bl: ['A', 'bottom'], br: ['C', 'bottom'] };
const TELL2_BOX = [0.23, 0.25, 0.59, 0.75];
const TELL2_CLUSTER = [0.83, 0.22, 1, 0.78];
const TELL2_PHONE = { box: [0.04, 0.04, 0.96, 0.34], row: [0.36, 0.56], cluster: [0.34, 0.70, 1, 1] };   // the stage's places touch each other and the page's sides; the cluster the page's corner
function tell2Place(where) { const [c, r] = TELL2_PLACES[where] || TELL2_PLACES.top, x = TELL2_COLS[c], y = TELL2_ROWS[r]; return [x[0], y[0], x[1], y[1]]; }
// THE WHITESPACE IS WHAT THE CELLS LEAVE: the page less the stage and the
// cluster, as rectangles. The page is cut along every rectangle's edges; the
// pieces nothing covers are the whitespace, run together along a row and
// then down the rows where their spans agree. Every corner of a piece is a
// page corner or another piece's, or lies on another piece's edge, which
// Portal's construction takes (one mirror where two voids share a line).
function tell2Complement(C, R, rects) {
  const r6 = v => Math.round(v * 1e6) / 1e6, E = 1e-9;
  const xs = [...new Set([0, C, ...rects.flatMap(r => [r[0], r[2]])].map(r6))].sort((a, b) => a - b);
  const ys = [...new Set([0, R, ...rects.flatMap(r => [r[1], r[3]])].map(r6))].sort((a, b) => a - b);
  const covered = (x, y) => rects.some(r => x > r[0] + E && x < r[2] - E && y > r[1] + E && y < r[3] - E);
  const out = [];
  for (let j = 0; j < ys.length - 1; j++) {
    let start = -1;
    for (let i = 0; i <= xs.length - 1; i++) {
      const free = i < xs.length - 1 && !covered((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2);
      if (free && start < 0) start = i;
      if (!free && start >= 0) {
        const piece = [xs[start], ys[j], xs[i], ys[j + 1]];
        const above = out.find(o => Math.abs(o[0] - piece[0]) < E && Math.abs(o[2] - piece[2]) < E && Math.abs(o[3] - piece[1]) < E);
        if (above) above[3] = piece[3]; else out.push(piece);
        start = -1;
      }
    }
  }
  return out;
}
// A slide's page, in lattice units: the stage's rectangles first, one a
// cell of the cast, then the cluster's cards (the bento's guillotine, drawn
// on a finer grid and fitted into the cluster's corner of the page), then
// the whitespace. A phone stacks: the blurb a band across the top, the
// stage a row below it, the cluster at the foot.
function tell2Page(k, C, R, n, W, H) {
  const sd = TELL2_SLIDES[k % TELL2_SLIDES.length], m = Math.min(sd.stage.length, Math.max(0, n - 1));
  const r6 = v => Math.round(v * 1e6) / 1e6, L = f => [r6(f[0] * C), r6(f[1] * R), r6(f[2] * C), r6(f[3] * R)];
  let stage, cluster, box;
  if (W < H) {
    const P = TELL2_PHONE, [y0, y1] = P.row, x0 = m === 1 ? 0.25 : 0, ww = m === 1 ? 0.5 : 1 / Math.max(1, m);
    stage = []; for (let i = 0; i < m; i++) stage.push([x0 + i * ww, y0, x0 + (i + 1) * ww, y1]);
    cluster = P.cluster; box = P.box;
  } else { stage = sd.stage.slice(0, m).map(tell2Place); cluster = TELL2_CLUSTER; box = TELL2_BOX; }
  const cl = L(cluster), cards = guillotine([0, 0, 8, 6], n - m, 1).map(r => [r6(cl[0] + r[0] / 8 * (cl[2] - cl[0])), r6(cl[1] + r[1] / 6 * (cl[3] - cl[1])), r6(cl[0] + r[2] / 8 * (cl[2] - cl[0])), r6(cl[1] + r[3] / 6 * (cl[3] - cl[1]))]);
  const content = [...stage.map(L), ...cards];
  return { content, voids: tell2Complement(C, R, content), box: L(box), cast: m };
}
const tell2Cache = new Map();
function tell2Scene(h, n) {
  const k = tell2 ? tell2.k : 0, key = [k, h.COLS, h.ROWS, n, h.W, h.H].join('|');
  if (tell2Cache.has(key)) return tell2Cache.get(key);
  const p = tell2Page(k, h.COLS, h.ROWS, n, h.W, h.H), sc = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);
  tell2Cache.set(key, sc); if (tell2Cache.size > 24) tell2Cache.delete(tell2Cache.keys().next().value);
  return sc;
}
// the story: its scroll (px, a page's height a slide), its speed, the slide
// it is on, the cast of every slide, the cells on stage now, and the text's
// clocks
let tell2 = null;
const tell2Pitch = () => H;
function tell2Start(origin) {
  reelDrop(); tellDrop();
  // the cast: the cells take turns in order, as many a slide as its stage
  // has places, round and round, so no cell is on stage two slides running
  const cells = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).sort((a, b) => a.id - b.id);
  const heroes = []; let next = 0;
  for (const sd of TELL2_SLIDES) { const m = Math.min(sd.stage.length, Math.max(0, cells.length - 1)), cast = []; for (let i = 0; i < m; i++) cast.push(cells[next++ % cells.length]); heroes.push(cast); }
  tell2 = { y: 0, v: 0, k: -1, heroes, on: [], drag: null, entered: false, alpha: 0, rule: 0, fullAt: -1, seen: -1, changed: -1e9 };
  tell2Go(0, origin || { x: W / 2, y: H / 2 });
}
function tell2Drop() {
  if (!tell2) return;
  tell2 = null;
  for (const v of root.bodies) if (v.rect && v.rect.reelLive) v.rect.reelLive = false;   // the whitespace's sites slew again as a page's do
}
// THE SETTLED SLIDE IS THE AUTHORED ONE. Once a slide's change has ended,
// the authored weights are handed to every body each frame, the cluster's,
// the cast's and the whitespace's mirrors alike, as a reel hands its own:
// the whitespace here is cut into pieces around the stage, and the live
// auction, solving the same claims from wherever it was, settles a hair
// off the authored diagram near a piece's mirrors, which sit close behind
// a short edge. Handed, the diagram is the authored one, exact.
function tell2Step() {
  if (!tell2 || guestLeft > 0) return;
  const n = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).length, sc = tell2Scene(root, n);
  for (const b of root.bodies) {
    if (b.isSelf || b.leaving || !b.rect || (!b.isVoid && b.journey)) continue;   // a void keeps its journey's record; a card still travelling is not handed
    if (b.isVoid) {
      if (!b.rect.reelLive) { const j = sc.voids.findIndex(r => rectsEqual(r, b.rect)); if (j < 0 || !sc.voids[j].mfSites.length) continue; const r = Object.assign([], sc.voids[j]); r.reelLive = true; b.rect = r; b.formRect = r; }   // a piece no mirror stands in (its whole is held by its neighbours' mirrors) keeps its own site
      b.claimTarget = rectArea(b.rect); b.claim = b.claimTarget;
    } else {
      const i = sc.content.findIndex(r => rectsEqual(r, b.rect)); if (i < 0) continue;
      b.claimTarget = sc.content[i].mfArea; b.claim = b.claimTarget;
      const [ex, ey] = root.rectCenter(b.rect); b.x = ex; b.y = ey; b.vx = 0; b.vy = 0;
      const q = b.subs[0]; q.w = sc.weights[i]; q.live = true;
    }
  }
}
// a slide: its cast takes the stage, the last slide's goes back into the
// cluster, a page change with Portal's smoothness; the first of the cast is
// the page's image, for the click home
function tell2Go(k, origin) {
  if (!tell2) return;
  tell2.k = k; tell2.on = tell2.heroes[k].filter(b => !b.leaving); tell2.changed = simTime;
  portalFocus = tell2.on[0] || null; portalFlip = false;
  portalEnter('tell2', origin || (portalFocus ? { x: portalFocus.x, y: portalFocus.y } : { x: W / 2, y: H / 2 }));
}
// the flow of the story, a Tell's: a speed eases away, a slow story snaps
// to its slide, the slide the story is on is the nearest, and a change is
// made at most every quarter second, since each is a page change
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
  const n = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving).length, q = tell2Page(p.k, root.COLS, root.ROWS, n, W, H).box;
  const r = [q[0] * root.PW, q[1] * root.PH, q[2] * root.PW, q[3] * root.PH], pad = Math.max(16, Math.min(48, 0.024 * W));
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
    const cast = p.heroes[k].map(b => b.name).join(' · ');
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
# The whitespace of a Tell II page is the page less the stage and the cluster,
# cut into rectangles, so a cell's edge can run along two of them; Portal's
# contact rule (the cell's edge within the void's) found neither, and the
# edge went unheld. An edge no void holds whole is held by the piece the
# seed faces: a mirror across the edge at the seed's own line holds the
# whole edge, whichever pieces it runs along. Portal's own pages are as
# they were: every edge of theirs a void holds whole.
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

# --- a Tell II slide is a page to the engine; its cast takes the stage's slots ------
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell' ? tellScene(this, content.length) :''',
        '''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell2' ? tell2Scene(this, content.length) : this.depth===0 && name === 'tell' ? tellScene(this, content.length) :''')
replace('''  if (!portalFocus || !(name in PORTAL_TEMPLATES || name === 'tell')) return;   // TELL: a story's hero takes the first slot when the page is laid again (an add, a remove, a resize)''',
        '''  if (name === 'tell2' && tell2) {   // TELL II: the cast takes the stage's slots, in order; each slot's holder takes the cast member's slot
    tell2.on.forEach((h, i) => { const k = content.indexOf(h); if (k < 0) return; const j = gotS.indexOf(i); if (j < 0 || j === k) return; gotS[j] = gotS[k]; gotS[k] = i; });
    return;
  }
  if (!portalFocus || !(name in PORTAL_TEMPLATES || name === 'tell')) return;   // TELL: a story's hero takes the first slot when the page is laid again (an add, a remove, a resize)''')
replace('''    if (name in PORTAL_TEMPLATES || name === 'tell') for (const b of content) { const j = b.journey, p = b.path;''',
        '''    if (name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') for (const b of content) { const j = b.journey, p = b.path;''')
replace('''    if ((name in PORTAL_TEMPLATES || name === 'tell') && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''',
        '''    if ((name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''')
replace('''        if (!(name in PORTAL_TEMPLATES || name === 'tell') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''',
        '''        if (!(name in PORTAL_TEMPLATES || name === 'tell' || name === 'tell2') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''')
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
