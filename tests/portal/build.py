"""Build Portal from Plaque: a click on a cell opens that cell's page.

A page is text in the whitespace, one large hero image, and a gallery of
smaller cells to browse, on a rectangular grid the engine draws exactly. The
clicked cell becomes the hero image; its text is set in the page's reading
void, where it is not read through a photograph. On the existing scenes the
tick, the picture and every drawing command are Plaque's (validate.cjs).
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
// PORTAL GRID. A page is a rectangular partition of the lattice: a TEXT block
// (the reading void), an IMAGE block (the focus) and GALLERY regions cut into
// the other cells. Every block is subdivided by the union of the page's cut
// lines and carries one site per sub-cell, the way a manifold void does, so
// the power diagram at rest IS the partition: every seam straight, every cell
// a rectangle. In transit the sites ride with their body and the page is as
// organic as ever. Templates are in fractions of the page; grid indices name
// the blocks; rules are hairlines drawn along the text block, style only.
const PORTAL_TEMPLATES = {
  spread:        { cols: [0.44, 0.33, 0.23], rows: [0.75, 0.25], image: [0, 0, 1, 2], text: [1, 0, 2, 1], gallery: [[1, 1, 2, 2], [2, 0, 3, 2]], rules: ['right', 'bottom'] },
  folio:         { cols: [0.24, 0.46, 0.3], rows: [1], image: [1, 0, 2, 1], text: [0, 0, 1, 1], gallery: [[2, 0, 3, 1]], rules: ['right'] },
  showcase:      { cols: [0.12, 0.51, 0.37], rows: [0.72, 0.28], image: [1, 0, 2, 1], text: [2, 0, 3, 1], gallery: [[0, 0, 1, 1], [0, 1, 3, 2]], rules: ['left', 'bottom'] },
  wall:          { cols: [0.58, 0.42], rows: [0.38, 0.62], image: [0, 0, 1, 2], text: [1, 0, 2, 1], gallery: [[1, 1, 2, 2]], rules: ['bottom'] },
  interview:     { cols: [0.57, 0.43], rows: [0.415, 0.2925, 0.2925], image: [1, 0, 2, 2], text: [0, 0, 1, 1], gallery: [[0, 1, 1, 3], [1, 2, 2, 3]], rules: ['bottom'] },
  documentation: { cols: [0.12, 0.48, 0.4], rows: [0.62, 0.38], image: [2, 0, 3, 1], text: [1, 0, 2, 2], gallery: [[0, 0, 1, 2], [2, 1, 3, 2]], rules: ['left', 'right'] },
  essay:         { cols: [0.2, 0.6, 0.2], rows: [0.42, 0.38, 0.2], image: [1, 0, 2, 1], text: [1, 1, 2, 2], gallery: [[0, 0, 1, 1], [2, 0, 3, 1], [0, 1, 1, 2], [2, 1, 3, 2], [0, 2, 3, 3]], rules: ['top', 'bottom'] },
  caption:       { cols: [0.84, 0.16], rows: [1], image: [0, 0, 1, 1], text: null, gallery: [[1, 0, 2, 1]], rules: [] },
};
const PORTAL_KINDS = ['spread', 'folio', 'showcase', 'wall', 'interview', 'documentation', 'essay', 'caption'];
let portalFocus = null;                             // the body a page is open on; null at home
function portalKind(b) { return PORTAL_KINDS[b.id % PORTAL_KINDS.length]; }
function portalCuts(fr) { const out = [0]; let s = 0; for (const f of fr) { s += f; out.push(s); } out[out.length - 1] = 1; return out; }
function portalGrid(T, C, R, n) {
  const r6 = v => Math.round(v * 1e6) / 1e6;   // cuts are compared for identity; keep them exact
  const xs = portalCuts(T.cols).map(f => r6(f * C)), ys = portalCuts(T.rows).map(f => r6(f * R));
  const rect = g => [xs[g[0]], ys[g[1]], xs[g[2]], ys[g[3]]];
  const image = rect(T.image), text = T.text ? rect(T.text) : null;
  // the other n-1 cells over the gallery regions, by area; a region is cut
  // into rows of cells, the first rows a cell wider where the count is uneven
  const regions = T.gallery.map(rect), m = n - 1;
  const total = regions.reduce((s, r) => s + rectArea(r), 0);
  const counts = regions.map(r => Math.max(1, Math.floor(m * rectArea(r) / total)));
  let assigned = counts.reduce((s, c) => s + c, 0);
  while (assigned < m) { let best = 0, bs = -1; regions.forEach((r, i) => { const s = rectArea(r) / counts[i]; if (s > bs) { bs = s; best = i; } }); counts[best]++; assigned++; }
  while (assigned > m) { let best = -1, bs = Infinity; regions.forEach((r, i) => { if (counts[i] > 1) { const s = rectArea(r) / counts[i]; if (s < bs) { bs = s; best = i; } } }); if (best < 0) break; counts[best]--; assigned--; }
  // a cell edge that lands within a quarter of a lattice unit of a cut the
  // page already has takes that cut: a near miss would slice every block it
  // crosses into a hair-thin sub-cell, a site with next to no ground to hold
  const SNAP = 0.25, cutsX = xs.slice(), cutsY = ys.slice();
  const snap = (v, cuts, span) => {
    let best = v, bd = Infinity;
    for (const c of cuts) { const d = Math.abs(c - v); if (d < bd) { bd = d; best = c; } }
    if (bd <= Math.min(SNAP, 0.3 * span)) return best;
    cuts.push(v); return v;
  };
  const cells = [];
  regions.forEach((r, i) => {
    const k = counts[i], w = r[2] - r[0], h = r[3] - r[1];
    let rows = 1, bs = Infinity;
    for (let q = 1; q <= k; q++) { const cols = Math.ceil(k / q), score = Math.abs(Math.log((w / cols) / (h / q))) + 0.1 * (q * cols - k); if (score < bs) { bs = score; rows = q; } }
    const base = Math.floor(k / rows), extra = k - base * rows;
    for (let row = 0; row < rows; row++) {
      const cols = base + (row < extra ? 1 : 0), y0 = snap(r6(r[1] + h * row / rows), cutsY, h / rows), y1 = snap(r6(r[1] + h * (row + 1) / rows), cutsY, h / rows);
      for (let col = 0; col < cols; col++) cells.push([snap(r6(r[0] + w * col / cols), cutsX, w / cols), y0, snap(r6(r[0] + w * (col + 1) / cols), cutsX, w / cols), y1]);
    }
  });
  const content = [image, ...cells], voids = text ? [text] : [];
  const X = new Set(), Y = new Set();
  for (const r of content.concat(voids)) { X.add(r[0]); X.add(r[2]); Y.add(r[1]); Y.add(r[3]); }
  const xcut = [...X].sort((a, b) => a - b), ycut = [...Y].sort((a, b) => a - b), E = 1e-9;
  const sites = r => {
    const cx = (r[0] + r[2]) / 2, cy = (r[1] + r[3]) / 2, out = [];
    for (let i = 0; i + 1 < xcut.length; i++) {
      const x0 = xcut[i], x1 = xcut[i + 1]; if (x0 < r[0] - E || x1 > r[2] + E) continue;
      for (let j = 0; j + 1 < ycut.length; j++) { const y0 = ycut[j], y1 = ycut[j + 1]; if (y0 < r[1] - E || y1 > r[3] + E) continue; out.push({ x: (x0 + x1) / 2 - cx, y: (y0 + y1) / 2 - cy, q: (x1 - x0) * (y1 - y0) }); }
    }
    return out;
  };
  const dress = r => { const q = r.slice(); q.mfSites = sites(q); q.mfKey = JSON.stringify(q.mfSites); q.mfRest = true; return q; };
  return { focus: true, content: content.map(dress), voids: voids.map(dress) };
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
for (const kind of Object.keys(PORTAL_TEMPLATES)) scenes[kind] = (C, R, n) => portalGrid(PORTAL_TEMPLATES[kind], C, R, n);   // PORTAL page kinds''')
replace('''    const gotS = assignStations(content, centers);
''', '''    const gotS = assignStations(content, centers);
    portalPin(content, gotS, name);
''')

# --- a content block on a page grid carries a site per sub-cell ---------------
replace('''    for (const v of live) {
      if (!v.isVoid || v.leaving) continue;
      const rv = v.formRect || v.rect;''', '''    for (const v of live) {
      if (v.leaving) continue;
      const rv = v.formRect || v.rect;
      // PORTAL: a content block on a page grid carries a site per sub-cell,
      // the way a manifold void does, so every seam it has is drawn straight
      if (!v.isVoid) { if (rv && rv.mfSites) v.wvTo = rv.mfSites.map(p => ({ ...p })); continue; }''')
replace('''    if (this.depth === 0 && b.isVoid && b.plCurrent) return;
    b.subs.length = 1;''', '''    if (this.depth === 0 && b.plCurrent && (b.isVoid || b.plCurrent.length > 1)) return;   // PORTAL: a block keeps its sites too
    b.subs.length = 1;''')

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
    for (const b of root.bodies) if (b.isVoid && !b.leaving && b.rect && b.crystal >= 0.99 && (!v || rectArea(b.rect) > rectArea(v.rect))) v = b;
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
  for (const e of T.rules) {
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
  const bx = x0 + pad, by = y1 - pad - h;
  if (width < 60 || !plaqueBoxFits(pts, loops, bx, by, bx + width, by + h, PLAQUE_MARGIN)) return;
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

# --- a block travels as one cell and becomes its rectangle as it lands --------
replace('''    b.wvU = Math.min(1, (b.wvU || 0) + du);
    const u = b.wvU * b.wvU * (3 - 2 * b.wvU);
    const cur = [];
    let sum = 0;
    for (let i = 0; i < b.wvFrom.length; i++) {
      const a = b.wvFrom[i], z = b.wvTo[i];
      const q = Math.max(WV_SITE_FLOOR, a.q + (z.q - a.q) * u);
      const p = { x: a.x + (z.x - a.x) * u, y: a.y + (z.y - a.y) * u, q };
      cur.push(p); sum += q;
    }''', '''    b.wvU = Math.min(1, (b.wvU || 0) + du);
    const u = b.wvU * b.wvU * (3 - 2 * b.wvU);
    const cur = [];
    let sum = 0;
    // PORTAL: a travelling content block does not carry its formation across
    // the page. Its sites close to one over the first third of the journey
    // and open to the destination's over the last stretch, so a cell travels
    // as one cell and becomes its rectangle as it lands. Whitespace, and a
    // block re-cut where it stands, keep the slew.
    const S = v => { v = Math.max(0, Math.min(1, v)); return v * v * (3 - 2 * v); };
    const journeying = !b.isVoid && b.journey && b.progress < 1;
    const s1 = journeying ? S(b.progress / 0.35) : 0, s2 = journeying ? S((b.progress - 0.55) / 0.45) : 0;
    for (let i = 0; i < b.wvFrom.length; i++) {
      const a = b.wvFrom[i], z = b.wvTo[i];
      let p;
      if (journeying) {
        const m = { x: 0, y: 0, q: i === 0 ? 1 : WV_SITE_FLOOR };
        const x1 = a.x + (m.x - a.x) * s1, y1 = a.y + (m.y - a.y) * s1, q1 = a.q + (m.q - a.q) * s1;
        p = { x: x1 + (z.x - x1) * s2, y: y1 + (z.y - y1) * s2, q: Math.max(WV_SITE_FLOOR, q1 + (z.q - q1) * s2) };
      } else {
        p = { x: a.x + (z.x - a.x) * u, y: a.y + (z.y - a.y) * u, q: Math.max(WV_SITE_FLOOR, a.q + (z.q - a.q) * u) };
      }
      cur.push(p); sum += p.q;
    }''')

(ROOT / 'portal.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
