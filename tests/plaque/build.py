"""Build Plaque from the accepted Caption page on main.

Plaque changes text only. Cell motion, hover, the auction and every cell
fill/stroke are Caption's, byte for byte in the drawing commands; see
validate.cjs.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'caption.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'b595913da13062c7f0acfb1db15d0b65fe4ee30c17f9fe02829fa770005922c5'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Caption — Hive</title>', '<title>Plaque — Hive</title>')
replace('&larr; Back · Caption</a>', '&larr; Back · Plaque</a>')

# --- the label functions -----------------------------------------------------
start = s.index('// The printed block belongs to the visible area, without its own positional')
end = s.index('// Dress and paint every leaf the same way. ctx is in root px.', start)
old = s[start:end]
# keep Caption's centroid and signed-clearance helpers verbatim
keep = old[old.index('function captionCenter'):old.index('// Hysteresis keeps a cell near the fit threshold')]
new = '''// PLAQUE. Type is set per viewport, never per cell and never per hover. A
// label is a printed box, fitted where it is printed: at the ink's area
// centroid, or at the pole the steering anchor already found when the
// centroid has no room. A travelling cell carries no text and computes no
// text geometry; its name returns when it lands.
''' + keep + '''
const PLAQUE_OUT = 0.06;    // s: text leaves as a change begins
const PLAQUE_IN = 0.22;     // s: text returns once the change has ended
const PLAQUE_UNFIT = 0.10;  // s: text leaves a cell that has no room for it
const PLAQUE_LAG = 0.08;    // s: the box follows its place; no spring, no teleport
const PLAQUE_REFIT = 0.25;  // s: how often a resting cell re-measures its room
const PLAQUE_PAD = 3, PLAQUE_MARGIN = 3, PLAQUE_ENTER = 3;   // px: box padding, ink clearance, fit hysteresis
let plaqueType = null;
const plaqueWidths = new Map();
function plaqueTypeFor(w) {
  if (plaqueType && plaqueType.w === w) return plaqueType;
  const s = Math.max(0.62, Math.min(1, w / 1200));
  const num = Math.max(20, Math.round(32 * s)), sub = Math.max(12, Math.round(20 * s)), name = Math.max(11, Math.round(13 * s));
  plaqueWidths.clear();
  return plaqueType = { w, num, sub, name, gap: 4,
    numFont: `600 ${num}px system-ui, sans-serif`, subFont: `600 ${sub}px system-ui, sans-serif`, nameFont: `500 ${name}px system-ui, sans-serif` };
}
function plaqueWidth(ctx, text, font) {
  const key = font + '|' + text;
  let w = plaqueWidths.get(key);
  if (w === undefined) { ctx.font = font; w = ctx.measureText(text).width; plaqueWidths.set(key, w); }
  return w;
}

// Does the box sit on the ink, `margin` px clear of its edge and of every
// hole? Eight points of the box against the signed clearance.
function plaqueBoxFits(pts, loops, x0, y0, x1, y1, margin) {
  const xm = (x0 + x1) / 2, ym = (y0 + y1) / 2;
  const P = [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [xm, y0], [xm, y1], [x0, ym], [x1, ym]];
  for (const [x, y] of P) {
    if (captionClearance(pts, x, y) < margin) return false;
    for (const hole of loops) if (hole.hole && captionClearance(hole, x, y) > -margin - config.gap / 2) return false;
  }
  return true;
}

// One cell's text: where it goes, whether it fits, how visible it is. The
// room is re-measured on a slow clock or when the ink's area moves; the
// place follows the ink every frame through a short lag.
function plaqueStep(ctx, b, pts, loops, labels, label, type, hidden, dt, t, area, ax, ay) {
  const c = b.caption || (b.caption = { alpha: 0, nameAlpha: 0, fits: false, nameFits: false, pole: false, x: 0, y: 0, tx: 0, ty: 0, off: 0, at: -1, area: 0, seen: -1 });
  // the label's own clock, the time since it was last drawn: a leaf painted
  // only every other frame still fades at the same rate; one not drawn for
  // a while starts over, so no ghost
  const gap = t - c.seen, el = c.seen < 0 || gap > 0.1 ? dt : gap;
  if (gap > 0.1) { c.alpha = c.nameAlpha = 0; c.fits = c.nameFits = false; c.at = -1; }
  c.seen = t;
  const kOut = 1 - Math.exp(-el / PLAQUE_OUT), kUnfit = 1 - Math.exp(-el / PLAQUE_UNFIT);
  if (hidden) {
    c.alpha -= c.alpha * kOut; c.nameAlpha -= c.nameAlpha * kOut;
    c.fits = c.nameFits = false; c.at = -1;
    return c;
  }
  const center = captionCenter(pts);
  if (!center) { c.alpha -= c.alpha * kUnfit; c.nameAlpha -= c.nameAlpha * kUnfit; c.fits = c.nameFits = false; c.at = -1; return c; }
  if (c.at < 0 || t - c.at > PLAQUE_REFIT || Math.abs(area - c.area) > 0.01 * c.area) {
    c.at = t; c.area = area;
    const text = String(label), font = labels ? type.numFont : type.subFont, size = labels ? type.num : type.sub;
    const wn = plaqueWidth(ctx, text, font) + 2 * PLAQUE_PAD, hn = 0.8 * size + 2 * PLAQUE_PAD;
    const named = labels && !!b.name;
    const wm = named ? plaqueWidth(ctx, b.name, type.nameFont) + 2 * PLAQUE_PAD : 0, hm = named ? 0.9 * type.name + 2 * PLAQUE_PAD : 0;
    const off = named ? 0.5 * size + type.gap + 0.5 * type.name : 0;
    const wb = Math.max(wn, wm);
    const mNum = PLAQUE_MARGIN + (c.fits ? 0 : PLAQUE_ENTER), mBoth = PLAQUE_MARGIN + (c.nameFits ? 0 : PLAQUE_ENTER);
    const fitAt = (x, y, extra) => {
      const both = named && plaqueBoxFits(pts, loops, x - wb / 2, y - hn / 2, x + wb / 2, y + off + hm / 2, mBoth + extra);
      return { both, num: both || plaqueBoxFits(pts, loops, x - wn / 2, y - hn / 2, x + wn / 2, y + hn / 2, mNum + extra) };
    };
    // the centroid, unless the box already sits at the pole and the centroid
    // has not clearly made room; else the pole, if the anchor has found one
    let at = fitAt(center.x, center.y, c.pole ? PLAQUE_ENTER : 0), pole = false;
    if (!at.num && b.anchorState && b.anchorState.init && pointInPolygon(ax, ay, pts)) {
      const ap = fitAt(ax, ay, 0);
      if (ap.num) { at = ap; pole = true; }
    }
    c.fits = at.num; c.nameFits = at.both; c.pole = pole; c.off = off;
  }
  c.tx = c.pole ? ax : center.x; c.ty = c.pole ? ay : center.y;
  if (c.alpha < 0.02) { c.x = c.tx; c.y = c.ty; }
  else { const k = 1 - Math.exp(-el / PLAQUE_LAG); c.x += (c.tx - c.x) * k; c.y += (c.ty - c.y) * k; }
  const kIn = 1 - Math.exp(-el / PLAQUE_IN);
  c.alpha += ((c.fits ? 1 : 0) - c.alpha) * (c.fits ? kIn : kUnfit);
  c.nameAlpha += ((c.nameFits ? 1 : 0) - c.nameAlpha) * (c.nameFits ? kIn : kUnfit);
  return c;
}

// PLAQUE TAG. A field's members carry numbers, not the field's name. The
// name goes in a corner of the field's cell as a small tag above its
// members, on the same clocks as every other label.
function plaqueTag(ctx, hive, fb, type, hidden, dt, t) {
  const g = fb.plaque || (fb.plaque = { alpha: 0, fits: false, x: 0, y: 0, tx: 0, ty: 0, w: 0, h: 0, at: -1, text: '', seen: -1 });
  const fade = Math.max(0, Math.min(1, (fb.claim - CLAIM_MIN) / 0.14));
  const gap = t - g.seen, el = g.seen < 0 || gap > 0.1 ? dt : gap;
  if (gap > 0.1) { g.alpha = 0; g.fits = false; g.at = -1; }
  g.seen = t;
  const kOut = 1 - Math.exp(-el / PLAQUE_OUT), kUnfit = 1 - Math.exp(-el / PLAQUE_UNFIT);
  if (hidden || !fb.name || fade < 0.02) { g.alpha -= g.alpha * kOut; g.fits = false; g.at = -1; return; }
  if (g.at < 0 || t - g.at > PLAQUE_REFIT) {
    const was = g.fits ? g.text : null;
    g.at = t; g.fits = false;
    const poly = hive.cellPoly(fb);
    if (poly && poly.length >= 3) {
      const pts = poly.map(p => [p[0] + hive.absX, p[1] + hive.absY]);
      let x0 = Infinity, y0 = Infinity, cx = 0, cy = 0;
      for (const p of pts) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); cx += p[0]; cy += p[1]; }
      cx /= pts.length; cy /= pts.length;
      const clear = config.gap / 2 + 2, inset = config.gap / 2 + 12;
      let v = pts[0], best = Infinity;
      for (const p of pts) { const d = (p[0] - x0) + (p[1] - y0); if (d < best) { best = d; v = p; } }
      const dx = cx - v[0], dy = cy - v[1], L = Math.hypot(dx, dy) || 1;
      // the box's top-left corner, else the nearest ink vertex, each stepped
      // in a little further when a slanted edge leaves the first spot short
      const places = [];
      for (const k of [0, 10]) places.push([x0 + inset + k, y0 + inset + k]);
      for (const k of [0, 8, 16]) places.push([v[0] + dx / L * (inset + k), v[1] + dy / L * (inset + k)]);
      const full = `${fb.label !== undefined ? fb.label : fb.id + 1} · ${fb.name}`;
      // number and name, else the name alone on a narrow field; the text in
      // use keeps its place unless another clearly fits better
      outer: for (const text of [was, full, fb.name]) {
        if (!text || (text !== was && text === g.text && was)) continue;
        const w = plaqueWidth(ctx, text, type.nameFont) + 12, h = type.name + 10, m = text === was ? clear : clear + PLAQUE_ENTER;
        for (const [x, y] of places) {
          if (plaqueBoxFits(pts, [], x, y, x + w, y + h, m)) { g.text = text; g.w = w; g.h = h; g.tx = x; g.ty = y; g.fits = true; break outer; }
        }
      }
    }
  }
  if (g.alpha < 0.02) { g.x = g.tx; g.y = g.ty; }
  else { const k = 1 - Math.exp(-el / PLAQUE_LAG); g.x += (g.tx - g.x) * k; g.y += (g.ty - g.y) * k; }
  const kIn = 1 - Math.exp(-el / PLAQUE_IN);
  g.alpha += ((g.fits ? 1 : 0) - g.alpha) * (g.fits ? kIn : kUnfit);
  if (g.alpha > 0.01) {
    ctx.save();
    ctx.globalAlpha = 0.42 * fade * g.alpha;
    ctx.fillStyle = '#000';
    roundedPath(ctx, [[g.x, g.y], [g.x + g.w, g.y], [g.x + g.w, g.y + g.h], [g.x, g.y + g.h]], 6, false);
    ctx.fill();
    ctx.globalAlpha = 0.85 * fade * g.alpha;
    ctx.fillStyle = '#fff'; ctx.font = type.nameFont; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText(g.text, g.x + 6, g.y + g.h / 2);
    ctx.restore();
  }
}

'''
replace(old, new)

# --- the paint routine ---------------------------------------------------------
replace('  const captionIn = 1 - Math.exp(-dt / 0.18), captionOut = 1 - Math.exp(-dt / 0.10);',
        '  const type = plaqueTypeFor(W);\n'
        '  // a travelling cell carries no text, nor do the members of a travelling field\n'
        '  const travelling = b => !!b.journey && b.progress < 1;')

start = s.index('    const c = captionStep(b, bigPts, leaf.loops, leaf.labels, captionIn, captionOut);')
end = s.index('  if (hovered) paint(hovered);\n}', start) + len('  if (hovered) paint(hovered);\n}')
replace(s[start:end], '''    const c = plaqueStep(ctx, b, bigPts, leaf.loops, leaf.labels, leaf.label, type, leaf.path.some(e => travelling(e.body)), dt, t, bigA, inner.absX + b.anchorX, inner.absY + b.anchorY);
    if (c.alpha > 0.01) {
      ctx.save();
      if (bigTrace) { bigTrace(); ctx.clip('nonzero'); }
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.globalAlpha = (0.48 + 0.20 * hv) * fade * c.alpha;
      ctx.font = leaf.labels ? type.numFont : type.subFont;
      ctx.fillText(String(leaf.label), c.x, c.y);
      if (leaf.labels && c.nameAlpha > 0.01) {
        ctx.globalAlpha = (0.72 + 0.20 * hv) * fade * c.nameAlpha;
        ctx.font = type.nameFont;
        ctx.fillText(b.name, c.x, c.y + c.off);
      }
      ctx.restore();
    }
  };
  let hovered = null;
  for (const leaf of picture.leaves) { if (leaf.body === hoveredBody) hovered = leaf; else paint(leaf); }
  if (hovered) paint(hovered);
  // every field on the page, named once, above its members
  const tagged = new Set();
  for (const leaf of picture.leaves) {
    if (leaf.isVoid) continue;
    for (let k = 0; k + 1 < leaf.path.length; k++) {
      const fb = leaf.path[k].body;
      if (tagged.has(fb)) continue;
      tagged.add(fb);
      plaqueTag(ctx, leaf.path[k].hive, fb, type, leaf.path.slice(0, k + 1).some(e => travelling(e.body)), dt, t);
    }
  }
}''')

(ROOT / 'plaque.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
