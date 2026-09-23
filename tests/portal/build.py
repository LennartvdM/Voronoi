"""Build Portal from Plaque: a click on a cell opens that cell's page.

A page is text in the whitespace, one large hero image, and a gallery of
smaller cells to browse. A page is a claim table like the engine's own
scenes: one site per cell, the text a void, and the void drawn exactly the
way the Hero scene's is, from an authored rest diagram. The clicked cell
becomes the hero image; its text is set in the page's reading void, where it
is not read through a photograph. On the existing scenes the tick, the
picture and every drawing command are Plaque's (validate.cjs).
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'plaque.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '1fb47c3acf61e10ac996682bd85d340f34ed9f0d3503b798f656db4bcf1458ef'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Plaque — Hive</title>', '<title>Portal — Hive</title>')
replace('&larr; Back · Plaque</a>', '&larr; Back · Portal</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · click the image again for home</span>')

# --- page grids, kinds, and the focus pin --------------------------------------
GRID = '''// PORTAL. A page is a scene a cell was clicked into. Every page is the same
// three things: the page's TEXT, set in a reading void where it is not read
// through a photograph; one large HERO IMAGE, the clicked cell, pinned to the
// scene's first slot; and a GALLERY of the other cells to browse.
//
// A page is a claim table, like the engine's own scenes: every cell ONE site
// with a rectangle as its destination and its claim, the text a void. Cells
// are convex power cells, straight where they meet the void or the page and
// organic where they meet each other. The void is the rectangle it was given
// the way the Hero and Frame scenes' voids are: its sites are authored so the
// rest diagram draws it exactly (portalDecorate), and the auction is handed
// that diagram's areas. Templates are in fractions of the page; forced cuts
// (x, y) keep a gallery's cards from straddling the void's corners; rules are
// hairlines drawn along the text block, style only.
const PORTAL_TEMPLATES = {
  // Two rules the templates keep. A void's corners are page corners or
  // another void's, so no cell meets a void at a corner of it, where two
  // edges' mirrors would have to agree. And the cards that touch the hero
  // stand beside its short edge, far across from its centre: a seam between
  // two cells is square to the line between their sites, so a card offset
  // far along the hero's edge and close across it is a wedge.
  spread:        { hero: [0, 0, 0.42, 1], text: [0.42, 0, 0.72, 1], galleries: [[0.72, 0, 1, 1]], rules: ['right'],
                   fit: (W, H) => { const v = Math.max(0.3, 0.54 * H / W); return { hero: [0, 0, 0.72 - v, 1], text: [0.72 - v, 0, 0.72, 1] }; } },
  folio:         { hero: [0.24, 0, 0.7, 1], text: [0, 0, 0.24, 1], galleries: [[0.7, 0, 1, 1]], rules: ['right'] },
  showcase:      { hero: [0.16, 0, 0.64, 1], text: [0.64, 0, 1, 1], galleries: [[0, 0, 0.16, 1]], rules: ['left'] },
  band:          { hero: [0, 0, 0.6, 0.62], text: [0, 0.62, 1, 1], galleries: [[0.6, 0, 1, 0.62]], rules: ['top'] },
  lead:          { hero: [0, 0.35, 0.6, 1], text: [0, 0, 1, 0.35], galleries: [[0.6, 0.35, 1, 1]], rules: ['bottom'] },
  documentation: { hero: [0.62, 0, 1, 1], text: [0.24, 0, 0.62, 1], galleries: [[0, 0, 0.24, 1]], rules: ['left', 'right'] },
  essay:         { hero: [0.12, 0, 0.88, 0.42], text: [0.12, 0.42, 0.88, 1], margins: [[0, 0.42, 0.12, 1], [0.88, 0.42, 1, 1]], galleries: [[0, 0, 0.12, 0.42], [0.88, 0, 1, 0.42]], rules: ['top'] },
  caption:       { hero: [0, 0, 0.84, 1], text: null, galleries: [[0.84, 0, 1, 1]], rules: [] },
};
// a portrait page stacks: the image, its text, the cards
const PORTAL_PORTRAIT = {
  text:    { hero: [0, 0, 1, 0.4], text: [0, 0.4, 1, 0.76], galleries: [[0, 0.76, 1, 1]], rules: ['top'] },
  caption: { hero: [0, 0, 1, 0.8], text: null, galleries: [[0, 0.8, 1, 1]], rules: [] },
};
const PORTAL_KINDS = ['spread', 'folio', 'showcase', 'band', 'lead', 'documentation', 'essay', 'caption'];
let portalFocus = null;                             // the body a page is open on; null at home
function portalKind(b) { return PORTAL_KINDS[b.id % PORTAL_KINDS.length]; }
const PORTAL_E = 1e-6;
// a gallery region cut into k cards: rows of cards, the rows chosen for the
// squarest card, the first rows a card wider where the count is uneven
function portalCards(r, k) {
  const r6 = v => Math.round(v * 1e6) / 1e6, w = r[2] - r[0], h = r[3] - r[1], cards = [];
  let rows = 1, bs = Infinity;
  for (let n = 1; n <= k; n++) { const cols = Math.ceil(k / n), score = Math.abs(Math.log((w / cols) / (h / n))) + 0.1 * (n * cols - k); if (score < bs) { bs = score; rows = n; } }
  const base = Math.floor(k / rows), extra = k - base * rows;
  for (let row = 0; row < rows; row++) {
    const cols = base + (row < extra ? 1 : 0), y0 = r6(r[1] + h * row / rows), y1 = r6(r[1] + h * (row + 1) / rows);
    for (let col = 0; col < cols; col++) cards.push([r6(r[0] + w * col / cols), y0, r6(r[0] + w * (col + 1) / cols), y1]);
  }
  return cards;
}
// the page's rectangles, in lattice units: the hero first, then the cards,
// and the voids, the text first
function portalPage(T0, C, R, n, W, H) {
  const T = W < H ? PORTAL_PORTRAIT[T0.text ? 'text' : 'caption'] : Object.assign({}, T0, T0.fit ? T0.fit(W, H) : {});
  const r6 = v => Math.round(v * 1e6) / 1e6, L = f => [r6(f[0] * C), r6(f[1] * R), r6(f[2] * C), r6(f[3] * R)];
  const hero = L(T.hero), regions = T.galleries.map(L);
  const m = n - 1, total = regions.reduce((s, g) => s + rectArea(g), 0);
  const counts = regions.map(g => Math.max(1, Math.floor(m * rectArea(g) / total)));
  let assigned = counts.reduce((s, c) => s + c, 0);
  while (assigned < m) { let best = 0, bs = -1; regions.forEach((g, i) => { const s = rectArea(g) / counts[i]; if (s > bs) { bs = s; best = i; } }); counts[best]++; assigned++; }
  while (assigned > m) { let best = -1, bs = Infinity; regions.forEach((g, i) => { if (counts[i] > 1) { const s = rectArea(g) / counts[i]; if (s < bs) { bs = s; best = i; } } }); if (best < 0) break; counts[best]--; assigned--; }
  const cards = [];
  regions.forEach((g, i) => cards.push(...portalCards(g, counts[i])));
  const voids = [];
  if (T.text) { const t = L(T.text); t.portalText = true; voids.push(t); }
  for (const f of T.margins || []) voids.push(L(f));
  return { content: [hero, ...cards], voids };
}
// THE VOID, EXACT. As the Hero scene's: the cells' weights are solved for
// their rectangles' areas with the voids cut out of the domain, one solve per
// pocket the voids leave; then every cell the solve puts against a void's
// edge is mirrored across that edge into the void, at the weight that makes
// the two tie exactly along the edge's whole line. The mirrors tile the
// void; their seams with one another meet the edge where the cells' own
// seams do; a cell that does not touch the void has the higher power all
// along it. Nothing else is inside the void, so it is drawn exactly. Rest
// targets only: the live auction, motion and one-site content bodies remain
// as they are, and the auction is handed the solve's areas, which are the
// rectangles' own.
function portalOutline(rects) {
  // the outline of a set of rectangles that tile a region: their directed
  // edges, split at every corner they pass, with the shared ones cancelled
  const E = 1e-6, xs = [...new Set(rects.flatMap(r => [r[0], r[2]]))].sort((p, q) => p - q), ys = [...new Set(rects.flatMap(r => [r[1], r[3]]))].sort((p, q) => p - q);
  const segs = new Map(), key = (p, q) => p.join(',') + '>' + q.join(',');
  const put = (p, q) => { const back = key(q, p); if (segs.has(back)) segs.delete(back); else segs.set(key(p, q), [p, q]); };
  const run = (p, q, axis, cuts) => {
    const lo = Math.min(p[axis], q[axis]), hi = Math.max(p[axis], q[axis]), inner = cuts.filter(c => c > lo + E && c < hi - E);
    const pts = [p, ...(p[axis] < q[axis] ? inner : inner.slice().reverse()).map(c => axis ? [p[0], c] : [c, p[1]]), q];
    for (let i = 0; i + 1 < pts.length; i++) put(pts[i], pts[i + 1]);
  };
  for (const r of rects) { run([r[0], r[1]], [r[2], r[1]], 0, xs); run([r[2], r[1]], [r[2], r[3]], 1, ys); run([r[2], r[3]], [r[0], r[3]], 0, xs); run([r[0], r[3]], [r[0], r[1]], 1, ys); }
  const byStart = new Map(); for (const [p, q] of segs.values()) byStart.set(p.join(','), q);
  let best = null;
  const seen = new Set();
  for (const [p] of segs.values()) {
    const k0 = p.join(','); if (seen.has(k0)) continue;
    const loop = []; let cur = p;
    while (cur && !seen.has(cur.join(','))) { seen.add(cur.join(',')); loop.push(cur); cur = byStart.get(cur.join(',')); }
    if (!best || Math.abs(ringArea(loop)) > Math.abs(ringArea(best))) best = loop;
  }
  return best;
}
function portalDecorate(content, voids, W, H, C, R) {
  const PW = W / C, PH = H / R, E = 1e-6, px = r => [r[0] * PW, r[1] * PH, r[2] * PW, r[3] * PH];
  const rects = content.map(px), vr = voids.map(px), n = rects.length;
  const seeds = rects.map(r => [(r[0] + r[2]) / 2, (r[1] + r[3]) / 2]), weights = new Array(n).fill(0);
  // the pockets: cells grouped by the edges they share
  const parent = rects.map((_, i) => i), find = i => parent[i] === i ? i : (parent[i] = find(parent[i]));
  const touch = (p, q) => ((Math.abs(p[2] - q[0]) < E || Math.abs(p[0] - q[2]) < E) && Math.min(p[3], q[3]) - Math.max(p[1], q[1]) > E) || ((Math.abs(p[3] - q[1]) < E || Math.abs(p[1] - q[3]) < E) && Math.min(p[2], q[2]) - Math.max(p[0], q[0]) > E);
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (touch(rects[i], rects[j])) parent[find(i)] = find(j);
  const pockets = new Map(); for (let i = 0; i < n; i++) { const k = find(i); if (!pockets.has(k)) pockets.set(k, []); pockets.get(k).push(i); }
  const mirrors = voids.map(() => []);   // per void: [x, y, weight]
  for (const idx of pockets.values()) {
    const poly = portalOutline(idx.map(i => rects[i]));
    const ref = idx.length === 1 ? null : solveWeights(idx.map(i => seeds[i]), idx.map(i => (rects[i][2] - rects[i][0]) * (rects[i][3] - rects[i][1])), poly, null, { maxIter: 60, tol: 1e-9 });
    const cells = ref ? ref.diagram.cells : [{ pts: poly }];
    idx.forEach((i, k) => weights[i] = ref ? ref.weights[k] : 0);
    // the contacts: a cell's edge lying on a void's edge. The pocket's gauge
    // puts the mean power at the contacts' midpoints at zero, and a mirror
    // sits close behind its edge: a cell's power varies along its edge by
    // the square of half the edge's length, and the mirrors from the void's
    // far side must stay above that all along it, which they do when the
    // void is at least that half-length deep and the mirrors sit close
    const contacts = [];
    idx.forEach((i, k) => {
      const pts = cells[k].pts;
      for (let e = 0; e < pts.length; e++) {
        const p = pts[e], q = pts[(e + 1) % pts.length];
        if (Math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-5) continue;
        vr.forEach((v, vi) => {
          const on = (c, lo, hi, ax) => Math.abs(p[ax] - c) < 1e-5 && Math.abs(q[ax] - c) < 1e-5 && Math.min(p[1 - ax], q[1 - ax]) > lo - 1e-5 && Math.max(p[1 - ax], q[1 - ax]) < hi + 1e-5;
          let side = null;
          if (on(v[0], v[1], v[3], 0)) side = 'left'; else if (on(v[2], v[1], v[3], 0)) side = 'right'; else if (on(v[1], v[0], v[2], 1)) side = 'top'; else if (on(v[3], v[0], v[2], 1)) side = 'bottom';
          if (side && !contacts.some(c => c.i === i && c.vi === vi && c.side === side)) contacts.push({ i, vi, side, mid: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] });
        });
      }
    });
    if (contacts.length) {
      let mean = 0;
      for (const c of contacts) mean += (c.mid[0] - seeds[c.i][0]) ** 2 + (c.mid[1] - seeds[c.i][1]) ** 2 - weights[c.i];
      mean /= contacts.length;
      for (const i of idx) weights[i] += mean;
    }
    for (const c of contacts) {
      const v = vr[c.vi], s = seeds[c.i], w = weights[c.i];
      let d, g, x, y;
      if (c.side === 'left') { d = v[0] - s[0]; g = Math.min(d, 0.03 * (v[2] - v[0])); x = v[0] + g; y = s[1]; }
      else if (c.side === 'right') { d = s[0] - v[2]; g = Math.min(d, 0.03 * (v[2] - v[0])); x = v[2] - g; y = s[1]; }
      else if (c.side === 'top') { d = v[1] - s[1]; g = Math.min(d, 0.03 * (v[3] - v[1])); x = s[0]; y = v[1] + g; }
      else { d = s[1] - v[3]; g = Math.min(d, 0.03 * (v[3] - v[1])); x = s[0]; y = v[3] - g; }
      mirrors[c.vi].push([x, y, w + g * g - d * d]);
    }
  }
  // one site where two adjacent voids mirror the same cell across the same
  // line: it goes to the void it stands in, and is counted once
  const near = (p, q) => Math.abs(p[0] - q[0]) < 1e-6 && Math.abs(p[1] - q[1]) < 1e-6 && Math.abs(p[2] - q[2]) < 1e-6;
  const inside = (m, v) => m[0] > v[0] - 1e-6 && m[0] < v[2] + 1e-6 && m[1] > v[1] - 1e-6 && m[1] < v[3] + 1e-6;
  mirrors.forEach((list, vi) => { mirrors[vi] = list.filter(m => !mirrors.some((other, vj) => vj !== vi && other.some(o => near(o, m)) && (inside(m, vr[vj]) && !inside(m, vr[vi]) || (vj < vi && inside(m, vr[vj]) === inside(m, vr[vi]))))); });
  const allSeeds = seeds.slice(), allWeights = weights.slice(), owned = [];
  mirrors.forEach(list => { const s0 = allSeeds.length; for (const [x, y, w] of list) { allSeeds.push([x, y]); allWeights.push(w); } owned.push([s0, allSeeds.length]); });
  const d = computeDiagram(allSeeds, allWeights, [[0, 0], [W, 0], [W, H], [0, H]]);
  const rows = content.map((r, i) => { const q = r.slice(); q.mfArea = d.areas[i] / (PW * PH); q.mfSeed = [seeds[i][0] / PW, seeds[i][1] / PH]; q.mfRest = true; return q; });
  const vs = voids.map((v, k) => {
    const q = v.slice(), cx = (v[0] + v[2]) / 2, cy = (v[1] + v[3]) / 2;
    q.mfSites = [];
    for (let i = owned[k][0]; i < owned[k][1]; i++) if (d.areas[i] > 1e-6) q.mfSites.push({ x: allSeeds[i][0] / PW - cx, y: allSeeds[i][1] / PH - cy, q: d.areas[i] / (PW * PH) });
    q.mfArea = q.mfSites.reduce((s, p) => s + p.q, 0);   // its claim: what its sites hold, which adjacent voids may share
    q.mfKey = JSON.stringify(q.mfSites); q.mfRest = true; if (v.portalText) q.portalText = true;
    return q;
  });
  return { content: rows, voids: vs, seeds: allSeeds, weights: allWeights, owned };
}
const portalCache = new Map();
function portalScene(h, name, n) {
  const key = [name, h.COLS, h.ROWS, n, h.W, h.H].join('|');
  if (portalCache.has(key)) return portalCache.get(key);
  const p = portalPage(PORTAL_TEMPLATES[name], h.COLS, h.ROWS, n, h.W, h.H), s = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);
  portalCache.set(key, s); if (portalCache.size > 24) portalCache.delete(portalCache.keys().next().value);
  return s;
}
function portalPin(content, gotS, name) {
  if (!portalFocus || !(name in PORTAL_TEMPLATES)) return;
  const k = content.indexOf(portalFocus);
  if (k < 0) return;
  const j = gotS.indexOf(0);
  if (j < 0 || j === k) return;
  gotS[j] = gotS[k]; gotS[k] = 0;          // the focus takes slot 0; its holder takes the focus's slot
}

'''
replace('const scenes = {\n  flock: null,\n', GRID + 'const scenes = {\n  flock: null,\n')
replace('''    return { content: distribute(ring, n, 4), voids: [[2, 1, C - 2, R - 1]] };
  },
};''', '''    return { content: distribute(ring, n, 4), voids: [[2, 1, C - 2, R - 1]] };
  },
};
for (const kind of Object.keys(PORTAL_TEMPLATES)) scenes[kind] = (C, R, n) => portalPage(PORTAL_TEMPLATES[kind], C, R, n, root.W, root.H);   // PORTAL page kinds''')
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : scenes[name] ? scenes[name](this.COLS, this.ROWS, content.length) : null;''', '''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && (name in PORTAL_TEMPLATES) ? portalScene(this,name,content.length) : scenes[name] ? scenes[name](this.COLS, this.ROWS, content.length) : null;   // PORTAL: a page is an authored rest diagram too''')
replace('''    const gotS = assignStations(content, centers);
''', '''    const gotS = assignStations(content, centers);
    portalPin(content, gotS, name);
''')

# --- the open page's image is one card, never a field -------------------------
replace('''    const gallery = b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);
    const k = gallery && this.depth < MAX_DEPTH && slots >= 4 ? Math.min(MAX_MEMBERS, Math.round(slots * 0.5 + 1)) : 0;''',
        '''    const gallery = !portalFocus && b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);   // PORTAL: on a page every cell is one card
    const k = gallery && this.depth < MAX_DEPTH && slots >= 4 ? Math.min(MAX_MEMBERS, Math.round(slots * 0.5 + 1)) : 0;''')

# --- the text, in the whitespace; the caption, on the image -------------------
replace('''// PLAQUE TAG. A field's members carry numbers, not the field's name.''', '''// PORTAL PROSE. The page's text lives in the whitespace: the image's name as
// a title and its paragraphs as bars, set in the page's reading void once
// that void has seated, fading in with it. Never on a photograph. The rules
// are hairlines along the text block, in the gap, and a short one under the
// title: style only, nothing reads them.
const portalProse = { alpha: 0, seen: -1 };
function portalProseStep(ctx, type, dt, t) {
  const p = portalProse, gap = t - p.seen, el = p.seen < 0 || gap > 0.1 ? dt : gap;
  if (gap > 0.1) p.alpha = 0;
  p.seen = t;
  let v = null;
  const T = portalFocus && PORTAL_TEMPLATES[config.scene];
  if (T && T.text)
    for (const b of root.bodies) if (b.isVoid && !b.leaving && b.rect && b.rect.portalText && b.crystal >= 0.99) v = b;
  p.alpha += ((v ? 1 : 0) - p.alpha) * (1 - Math.exp(-el / (v ? 0.30 : 0.08)));
  if (!v || p.alpha < 0.01) return;
  const q = v.rect, r = [q[0] * root.PW, q[1] * root.PH, q[2] * root.PW, q[3] * root.PH], pad = Math.max(16, Math.min(48, 0.024 * W));
  const x0 = r[0] + pad, y0 = r[1] + pad, bottom = r[3] - pad;
  if (r[2] - pad - x0 < 90) return;
  const title = Math.round(type.num * 0.9), line = Math.max(4, Math.round(type.name * 0.55)), lead = Math.round(line * 2.1);
  ctx.save();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.globalAlpha = 0.22 * p.alpha; ctx.beginPath();
  // in the gutter: half the padding in from the seam, so the line sits
  // between the text's margin and the neighbouring cards' ink
  const g = Math.round(pad / 2) + 0.5;
  const rules = (W < H ? PORTAL_PORTRAIT.text : T).rules;
  for (const e of rules) {
    if (e === 'left') { ctx.moveTo(r[0] + g, r[1] + pad); ctx.lineTo(r[0] + g, r[3] - pad); }
    if (e === 'right') { ctx.moveTo(r[2] - g, r[1] + pad); ctx.lineTo(r[2] - g, r[3] - pad); }
    if (e === 'top') { ctx.moveTo(r[0] + pad, r[1] + g); ctx.lineTo(r[2] - pad, r[1] + g); }
    if (e === 'bottom') { ctx.moveTo(r[0] + pad, r[3] - g); ctx.lineTo(r[2] - pad, r[3] - g); }
  }
  ctx.stroke();
  ctx.globalAlpha = 0.5 * p.alpha; ctx.beginPath(); ctx.moveTo(x0, y0 + Math.round(title * 1.3) + 0.5); ctx.lineTo(x0 + Math.round(title * 1.6), y0 + Math.round(title * 1.3) + 0.5); ctx.stroke();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.globalAlpha = 0.92 * p.alpha; ctx.font = `600 ${title}px system-ui, sans-serif`;
  ctx.fillText(portalFocus.name, x0, y0);
  ctx.globalAlpha = 0.20 * p.alpha;
  // the paragraphs: one measure, or two columns of it when the block is a
  // band wider than two measures
  const measure = Math.min(560, r[2] - pad - x0), gutter = Math.round(title * 1.5);
  const cols = r[2] - pad - x0 >= 2 * Math.min(400, measure) + gutter ? 2 : 1, colW = cols === 2 ? Math.min(400, Math.floor((r[2] - pad - x0 - gutter) / 2)) : measure;
  const runs = [[1, 1, 0.94, 1, 0.66], [1, 0.9, 1, 0.48], [1, 0.97, 0.8], [1, 1, 0.72]];
  let y = y0 + Math.round(title * 1.8), col = 0, x = x0;
  for (const run of runs) {
    if (y + run.length * lead > bottom) { if (cols === 2 && col === 0) { col = 1; x = x0 + colW + gutter; y = y0 + Math.round(title * 1.8); if (y + run.length * lead > bottom) break; } else break; }
    for (const f of run) { roundedPath(ctx, [[x, y], [x + colW * f, y], [x + colW * f, y + line], [x, y + line]], line / 2, false); ctx.fill(); y += lead; }
    y += Math.round(lead * 0.8);
  }
  ctx.restore();
}

// PORTAL CAPTION. On a full-cell page the image is the page; its name and one
// line sit in its bottom-left corner, on the ink, inside the ink clip.
function portalCaption(ctx, pts, loops, c, type, alpha) {
  let x0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const p of pts) { if (p[0] < x0) x0 = p[0]; if (p[0] > x1) x1 = p[0]; if (p[1] > y1) y1 = p[1]; }
  const pad = Math.max(config.cornerRadius + 8, Math.min(40, 0.02 * W)), title = Math.round(type.num * 0.8), line = Math.max(4, Math.round(type.name * 0.55));
  const width = Math.min(360, 0.5 * (x1 - x0)), h = title + Math.round(line * 2.4);
  if (width < 60) return;
  // bottom left; where a seam cuts that corner off, a little higher, else
  // the top left, which a page's image always keeps
  let y0 = Infinity; for (const p of pts) if (p[1] < y0) y0 = p[1];
  const bx = x0 + pad; let by = -1;
  for (const y of [y1 - pad - h, y1 - pad - 2 * h, y0 + pad]) if (plaqueBoxFits(pts, loops, bx, y, bx + width, y + h, PLAQUE_MARGIN)) { by = y; break; }
  if (by < 0) return;
  ctx.save();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.globalAlpha = 0.9 * alpha; ctx.font = `600 ${title}px system-ui, sans-serif`;
  ctx.fillText(portalFocus.name, bx, by);
  ctx.globalAlpha = 0.28 * alpha;
  const y = by + title + Math.round(line * 1.2);
  roundedPath(ctx, [[bx, y], [bx + width * 0.7, y], [bx + width * 0.7, y + line], [bx, y + line]], line / 2, false); ctx.fill();
  ctx.restore();
}

// PLAQUE TAG. A field's members carry numbers, not the field's name.''')
replace('''    const c = plaqueStep(ctx, b, bigPts, leaf.loops, leaf.labels, leaf.label, type, leaf.path.some(e => travelling(e.body)), dt, t, bigA, inner.absX + b.anchorX, inner.absY + b.anchorY);
    if (c.alpha > 0.01) {
      ctx.save();
      if (bigTrace) { bigTrace(); ctx.clip('nonzero'); }''', '''    // the open page's image carries no label: its title is set in the text
    // block beside it, or, on a full-cell page, as a caption on the image
    const pageT = b === portalFocus && PORTAL_TEMPLATES[config.scene];
    const c = plaqueStep(ctx, b, bigPts, leaf.loops, leaf.labels, leaf.label, type, leaf.path.some(e => travelling(e.body)) || (pageT && !!pageT.text), dt, t, bigA, inner.absX + b.anchorX, inner.absY + b.anchorY);
    const captioned = pageT && !pageT.text;   // the image is the page: a caption, not a label
    if (c.alpha > 0.01 && captioned) {
      ctx.save();
      if (bigTrace) { bigTrace(); ctx.clip('nonzero'); }
      portalCaption(ctx, bigPts, leaf.loops, c, type, fade * c.alpha);
      ctx.restore();
    }
    if (c.alpha > 0.01 && !captioned) {
      ctx.save();
      if (bigTrace) { bigTrace(); ctx.clip('nonzero'); }''')
replace('''      plaqueTag(ctx, leaf.path[k].hive, fb, type, leaf.path.slice(0, k + 1).some(e => travelling(e.body)), dt, t);
    }
  }
}''', '''      plaqueTag(ctx, leaf.path[k].hive, fb, type, leaf.path.slice(0, k + 1).some(e => travelling(e.body)), dt, t);
    }
  }
  portalProseStep(ctx, type, dt, t);
}''')

# --- no hover on the open page's image: a page is not a card ------------------
replace('''  const path = guestLeft > 0 ? [] : (hitLeaves(picture, mouseX, mouseY) || root.hitPath(mouseX, mouseY));
''', '''  const under = guestLeft > 0 ? [] : (hitLeaves(picture, mouseX, mouseY) || root.hitPath(mouseX, mouseY));
  const path = under.length && under[0].body === portalFocus ? [] : under;   // the open page's image is not a card
''')

# --- the click ---------------------------------------------------------------
replace('''canvas.addEventListener('pointerleave', () => { mouseX = -1e9; mouseY = -1e9; });
''', '''canvas.addEventListener('pointerleave', () => { mouseX = -1e9; mouseY = -1e9; });

// PORTAL. A click on a cell opens that cell's page, spreading from the point
// clicked; a click on the open page's image goes home the same way. A member
// of a field opens the field. Whitespace is not a cell. A press that moved
// or lingered is not a click.
function portalEnter(name, origin) {
  config.scene = name;
  document.querySelectorAll('.scene-btn').forEach(el => el.classList.toggle('active', el.dataset.scene === name));
  root.enterScene(name, origin);
}
function portalHome(origin) { portalFocus = null; portalEnter('bento', origin); }
function portalClick(x, y) {
  const path = hitLeaves(picture, x, y) || root.hitPath(x, y);
  if (!path || !path.length) return false;
  const b = path[0].body;
  if (b.isVoid || b.isSelf || b.leaving) return false;
  if (b === portalFocus) portalHome({ x, y });
  else { portalFocus = b; portalEnter(portalKind(b), { x, y }); }
  return true;
}
let portalPress = null;
canvas.addEventListener('pointerdown', (e) => { const [x, y] = pointerPos(e); portalPress = { x, y, at: performance.now() }; });
canvas.addEventListener('pointerup', (e) => {
  const press = portalPress; portalPress = null;
  if (!press) return;
  const [x, y] = pointerPos(e);
  if (Math.hypot(x - press.x, y - press.y) > 6 || performance.now() - press.at > 500) return;
  portalClick(x, y);
});
window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && portalFocus) portalHome(); });
''')
replace('''document.querySelectorAll('.scene-btn').forEach(b => b.addEventListener('click', () => {
  config.scene = b.dataset.scene;''', '''document.querySelectorAll('.scene-btn').forEach(b => b.addEventListener('click', () => {
  portalFocus = null;                        // a scene button leaves any open page
  config.scene = b.dataset.scene;''')

(ROOT / 'portal.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
