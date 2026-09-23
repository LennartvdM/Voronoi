"""Build Portal from Plaque: a click on a cell opens that cell's page.

A page is text in the whitespace, one large hero image, and a gallery of
smaller cells to browse. The clicked cell becomes the hero image; its text is
set in the page's reading void, where it is not read through a photograph.
Nothing else changes: on the existing scenes the tick, the picture and every
drawing command are Plaque's (validate.cjs).
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

# --- page kinds, the focus pin, and two page layouts -------------------------
replace('''const scenes = {
  flock: null,
''', '''// PORTAL. A page is a scene a cell was clicked into. Every page is the same
// three things: the page's TEXT, set in a reading void where it is not read
// through a photograph; one large HERO image, the clicked cell, pinned to the
// scene's first slot; and a GALLERY of the other cells to browse. Three
// kinds by the cell's id, most of them articles, so a page is recognisable
// without being unique:
//   article  the engine's Hero: a reading column at the left, the image, strips
//   gallery  the image at the left, the reading column beside it, a column to browse
//   caption  the full-cell section: the image is the page, with a caption on it
const PORTAL_KINDS = ['article', 'gallery', 'article', 'caption'];
const PORTAL_BASE = { article: 'hero' };            // a page kind drawn by an existing scene
const PORTAL_PROSE = { article: true, gallery: true };   // kinds whose text lives in a void
let portalFocus = null;                             // the body a page is open on; null at home
function portalKind(b) { return PORTAL_KINDS[b.id % PORTAL_KINDS.length]; }
function portalPin(content, gotS, name) {
  if (!portalFocus || !(name in PORTAL_KINDS.reduce((o, k) => (o[k] = 1, o), {}))) return;
  const k = content.indexOf(portalFocus);
  if (k < 0) return;
  const j = gotS.indexOf(0);
  if (j < 0 || j === k) return;
  gotS[j] = gotS[k]; gotS[k] = 0;          // the focus takes slot 0; its holder takes the focus's slot
}

const scenes = {
  flock: null,
''')
replace('''    return { content: distribute(ring, n, 4), voids: [[2, 1, C - 2, R - 1]] };
  },
};''', '''    return { content: distribute(ring, n, 4), voids: [[2, 1, C - 2, R - 1]] };
  },

  // PORTAL pages. content[0] is the image; voids[0] the reading column.
  gallery(C, R, n) {
    const w = Math.max(2, Math.round(C * 0.36)), m = Math.min(C - Math.ceil((n - 1) / R), Math.max(w + 2, Math.round(C * 0.62)));
    return { content: [[0, 0, w, R], ...distribute([[m, 0, C, R]], n - 1, 8)], voids: [[w, 0, m, R]] };
  },
  caption(C, R, n) {                                        // the column must seat every other cell: one slot each at least
    const w = Math.max(2, C - Math.max(2, Math.round(C * 0.17), Math.ceil((n - 1) / R)));
    return { content: [[0, 0, w, R], ...distribute([[w, 0, C, R]], n - 1, 9)], voids: [] };
  },
};''')
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : scenes[name] ? scenes[name](this.COLS, this.ROWS, content.length) : null;''',
        '''    const base = PORTAL_BASE[name] || name;
    const spec = this.depth===0 && (base==='hero'||base==='frame') ? mfScene(this,base,content.length) : scenes[base] ? scenes[base](this.COLS, this.ROWS, content.length) : null;''')
replace('''    if (this.depth===0 && (this.scene==='hero'||this.scene==='frame')) this.mfResize=true;''',
        '''    if (this.depth===0 && ((PORTAL_BASE[this.scene]||this.scene)==='hero'||this.scene==='frame')) this.mfResize=true;''')
replace('''    const gotS = assignStations(content, centers);
''', '''    const gotS = assignStations(content, centers);
    portalPin(content, gotS, name);
''')

# --- the open page's image is one card, never a field ------------------------
replace('''    const gallery = b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);
    const k = gallery && this.depth < MAX_DEPTH && slots >= 4 ? Math.min(MAX_MEMBERS, Math.round(slots * 0.5 + 1)) : 0;''',
        '''    const gallery = b !== portalFocus && b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);   // PORTAL: the page's image is one card
    const k = gallery && this.depth < MAX_DEPTH && slots >= 4 ? Math.min(MAX_MEMBERS, Math.round(slots * 0.5 + 1)) : 0;''')

# --- the text, in the whitespace; the caption, on the image -------------------
replace('''// PLAQUE TAG. A field's members carry numbers, not the field's name.''', '''// PORTAL PROSE. The page's text lives in the whitespace: the image's name as
// a title and its paragraphs as bars, set in the page's reading void once
// that void has seated, fading in with it. Never on a photograph.
const portalProse = { alpha: 0, seen: -1 };
function portalProseStep(ctx, type, dt, t) {
  const p = portalProse, gap = t - p.seen, el = p.seen < 0 || gap > 0.1 ? dt : gap;
  if (gap > 0.1) p.alpha = 0;
  p.seen = t;
  // the reading void: the largest seated void; its rectangle, in page px
  let v = null;
  if (portalFocus && PORTAL_PROSE[config.scene])
    for (const b of root.bodies) if (b.isVoid && !b.leaving && b.rect && b.crystal >= 0.99 && (!v || rectArea(b.rect) > rectArea(v.rect))) v = b;
  p.alpha += ((v ? 1 : 0) - p.alpha) * (1 - Math.exp(-el / (v ? 0.30 : 0.08)));
  if (!v || p.alpha < 0.01) return;
  const q = v.rect, r = [q[0] * root.PW, q[1] * root.PH, q[2] * root.PW, q[3] * root.PH], pad = Math.max(16, Math.min(48, 0.024 * W));
  const x0 = r[0] + pad, y0 = r[1] + pad, bottom = r[3] - pad, width = Math.min(560, r[2] - pad - x0);
  if (width < 90) return;
  const title = Math.round(type.num * 0.9), line = Math.max(4, Math.round(type.name * 0.55)), lead = Math.round(line * 2.1);
  ctx.save();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.globalAlpha = 0.92 * p.alpha; ctx.font = `600 ${title}px system-ui, sans-serif`;
  ctx.fillText(portalFocus.name, x0, y0);
  ctx.globalAlpha = 0.20 * p.alpha;
  let y = y0 + Math.round(title * 1.6);
  for (const run of [[1, 1, 0.94, 1, 0.66], [1, 0.9, 1, 0.48], [1, 0.97, 0.8]]) {
    if (y + run.length * lead > bottom) break;
    for (const f of run) { roundedPath(ctx, [[x0, y], [x0 + width * f, y], [x0 + width * f, y + line], [x0, y + line]], line / 2, false); ctx.fill(); y += lead; }
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
      if (bigTrace) { bigTrace(); ctx.clip('nonzero'); }''', '''    const c = plaqueStep(ctx, b, bigPts, leaf.loops, leaf.labels, leaf.label, type, leaf.path.some(e => travelling(e.body)), dt, t, bigA, inner.absX + b.anchorX, inner.absY + b.anchorY);
    const captioned = b === portalFocus && config.scene === 'caption';   // the image is the page: a caption, not a label
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

# --- no hover on the open page's image: a page is not a card -----------------
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
