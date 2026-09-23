"""Build Portal from Plaque: a click on a cell opens that cell's page.

Portal adds three page layouts and a click. Nothing else changes: on the
existing scenes the tick, the picture and every drawing command are Plaque's
(validate.cjs), and Plaque's labels are unchanged.
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
replace('&larr; Back · Plaque</a>', '&larr; Back · Portal</a> <span style="opacity:.55;margin-left:.6em">click a cell to open it · click it again for home</span>')

# --- three page layouts, and the focus pin ------------------------------------
replace('''const scenes = {
  flock: null,
''', '''// PORTAL. A page is a scene a cell was clicked into: a layout of its kind,
// with that cell pinned to the layout's first slot, the FOCUS. Three kinds,
// by the cell's id, so a page is recognisable without being unique. Each
// keeps the focus's boundaries near-vertical: a wide cell over a row of cells
// fans in a power diagram, which is why there is no banner layout here.
const PORTAL_KINDS = ['story', 'hall', 'reader'];
let portalFocus = null;        // the body a page is open on; null at home
function portalKind(b) { return PORTAL_KINDS[b.id % PORTAL_KINDS.length]; }
function portalPin(content, gotS, spec) {
  if (!portalFocus || !spec.focus) return;
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

  // PORTAL pages. content[0] is the focus.
  story(C, R, n) {                                          // an article: the focus left, the rest listed at the right
    const w = Math.max(2, Math.min(C - 2, Math.round(C * 0.64)));
    return { focus: true, content: [[0, 0, w, R], ...distribute([[w, 0, C, R]], n - 1, 5)], voids: [] };
  },
  hall(C, R, n) {                                           // a gallery: the focus centred, the rest in two flanking columns
    const w = Math.max(2, Math.round(C * 0.25)), x0 = w, x1 = Math.max(x0 + 2, C - w);
    return { focus: true, content: [[x0, 0, x1, R], ...distribute([[0, 0, x0, R], [x1, 0, C, R]], n - 1, 6)], voids: [] };
  },
  reader(C, R, n) {                                         // a document: a nav column, the focus as a reading column, a margin
    const nav = Math.max(2, Math.round(C * 0.24)), col = Math.min(C, Math.max(nav + 2, Math.round(C * 0.74)));
    const all = quilt([0, 0, nav, R], n - 1, 7);
    return { focus: true, content: [[nav, 0, col, R], ...all.slice(0, n - 1)], voids: all.slice(n - 1).concat([[col, 0, C, R]]) };
  },
};''')
replace('''    const gotS = assignStations(content, centers);
''', '''    const gotS = assignStations(content, centers);
    portalPin(content, gotS, spec);
''')

# --- the open page's focus reads as a page -----------------------------------
replace('''// PLAQUE TAG. A field's members carry numbers, not the field's name.''', '''// PORTAL. The open page's focus reads as a page: a few lines of body text,
// as bars under its name, when they fit the ink. Drawn inside the ink clip.
function portalBody(ctx, pts, loops, c, type, alpha) {
  const lines = 3, lh = Math.round(type.name * 0.6), gap = Math.round(type.name * 0.7);
  let x0 = Infinity, x1 = -Infinity;
  for (const p of pts) { if (p[0] < x0) x0 = p[0]; if (p[0] > x1) x1 = p[0]; }
  const width = Math.min(440, 0.55 * (x1 - x0)), top = c.y + c.off + type.name + gap, height = lines * lh + (lines - 1) * gap;
  if (width < 60 || !plaqueBoxFits(pts, loops, c.x - width / 2, top, c.x + width / 2, top + height, PLAQUE_MARGIN)) return;
  ctx.save();
  ctx.globalAlpha = 0.16 * alpha; ctx.fillStyle = '#fff';
  for (let k = 0; k < lines; k++) {
    const lw = width * (k === lines - 1 ? 0.62 : 1), y = top + k * (lh + gap), x = c.x - width / 2;
    roundedPath(ctx, [[x, y], [x + lw, y], [x + lw, y + lh], [x, y + lh]], lh / 2, false); ctx.fill();
  }
  ctx.restore();
}

// PLAQUE TAG. A field's members carry numbers, not the field's name.''')
replace('''        ctx.font = type.nameFont;
        ctx.fillText(b.name, c.x, c.y + c.off);
      }
      ctx.restore();''', '''        ctx.font = type.nameFont;
        ctx.fillText(b.name, c.x, c.y + c.off);
        if (b === portalFocus) portalBody(ctx, bigPts, leaf.loops, c, type, fade * c.nameAlpha);
      }
      ctx.restore();''')

# --- no hover on the open page's focus: a page is not a card -----------------
replace('''  const path = guestLeft > 0 ? [] : (hitLeaves(picture, mouseX, mouseY) || root.hitPath(mouseX, mouseY));
''', '''  const under = guestLeft > 0 ? [] : (hitLeaves(picture, mouseX, mouseY) || root.hitPath(mouseX, mouseY));
  const path = under.length && under[0].body === portalFocus ? [] : under;   // the open page's focus is not a card
''')

# --- the click ---------------------------------------------------------------
replace('''canvas.addEventListener('pointerleave', () => { mouseX = -1e9; mouseY = -1e9; });
''', '''canvas.addEventListener('pointerleave', () => { mouseX = -1e9; mouseY = -1e9; });

// PORTAL. A click on a cell opens that cell's page, spreading from the point
// clicked; a click on the open page's focus goes home the same way. A member
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

# --- the open page's focus is a page, not a gallery -----------------------------
replace('''    const gallery = b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);
    const k = gallery && this.depth < MAX_DEPTH && slots >= 4 ? Math.min(MAX_MEMBERS, Math.round(slots * 0.5 + 1)) : 0;''',
        '''    const gallery = b !== portalFocus && b.kindRoll < config.fieldDensity * (this.depth === 0 ? 1 : 0.5);   // PORTAL: a page is one card
    const k = gallery && this.depth < MAX_DEPTH && slots >= 4 ? Math.min(MAX_MEMBERS, Math.round(slots * 0.5 + 1)) : 0;''')

(ROOT / 'portal.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
