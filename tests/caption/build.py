"""Build Caption from the exact accepted Skim page in PR #265."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (HERE / 'skim.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '44a3ab22b72ab444c28cfe20fa534e515a688d1a5a33e21c5f1eec62704c3a1f'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Skim — Hive</title>', '<title>Caption — Hive</title>')
replace('&larr; Back · Skim</a>', '&larr; Back · Caption</a>')

start = s.index('// CONTENT. A label does not need to be exact:')
end = s.index('// Dress and paint every leaf', start)
old = s[start:end]
# This target selection feeds the cell's steering. Keep its exact arithmetic,
# hysteresis and cadence, but remove the spring/size state used only by text.
a = old.index('  const tx = bx + c.tox')
b = old.index('  // the drift, on the offset')
anchor = old[a:b].replace('if (!c.init) { c.ox = c.tox; c.oy = c.toy; c.r = c.tr; c.init = true; }', 'if (!c.init) c.init = true;')
new = '''// CAPTION. Skim's old content target also steers free cells. It remains an
// independent movement anchor, with the same sampling and hysteresis; visible
// text no longer reads it. Changing typography cannot change the cell auction.
const CONTENT_SAMPLE = 0.33;
function driftAnchorStep(c, pts, big, area, t, bx, by) {
''' + anchor + '''}

// The printed block belongs to the visible area, without its own positional
// spring or size animation. Its type size is fixed even during hover. The
// centroid is computed in local coordinates to avoid cancellation in a tiny
// polygon far from the origin; empty/sliver outlines simply have no caption.
function captionCenter(pts) {
  if (pts.length < 3) return null;
  const ox = pts[0][0], oy = pts[0][1];
  let a = 0, x = 0, y = 0;
  for (let k = 0; k < pts.length; k++) {
    const p = pts[k], q = pts[(k + 1) % pts.length];
    const px = p[0] - ox, py = p[1] - oy;
    const qx = q[0] - ox, qy = q[1] - oy, z = px * qy - qx * py;
    a += z; x += (px + qx) * z; y += (py + qy) * z;
  }
  return Math.abs(a) > 1e-6 ? { x: ox + x / (3 * a), y: oy + y / (3 * a) } : null;
}

// Signed clearance for text fitting. Combine containment and squared edge
// distances in one pass, taking one square root for the whole polygon.
// This is visual-only; Skim's movement-anchor arithmetic is not changed.
function captionClearance(pts, x, y) {
  let inside = false, distance2 = Infinity;
  for (let k = 0; k < pts.length; k++) {
    const p = pts[k], q = pts[(k + 1) % pts.length];
    const ex = q[0] - p[0], ey = q[1] - p[1];
    if ((p[1] > y) !== (q[1] > y) && x < ex * (y - p[1]) / ey + p[0]) inside = !inside;
    const u = Math.max(0, Math.min(1, ((x - p[0]) * ex + (y - p[1]) * ey) / (ex * ex + ey * ey || 1e-9)));
    const dx = x - (p[0] + u * ex), dy = y - (p[1] + u * ey);
    distance2 = Math.min(distance2, dx * dx + dy * dy);
  }
  return (inside ? 1 : -1) * Math.sqrt(distance2);
}

// Hysteresis keeps a cell near the fit threshold from blinking. Only opacity
// eases; there is no private text trajectory. Actual ink still clips the text.
function captionStep(b, pts, loops, labels, fadeIn, fadeOut) {
  const c = b.caption || (b.caption = { alpha: 0, nameAlpha: 0, fits: false, nameFits: false, x: 0, y: 0 });
  const center = captionCenter(pts);
  if (!center) { c.alpha = c.nameAlpha = 0; c.fits = c.nameFits = false; return c; }
  c.x = center.x; c.y = center.y;
  let room = captionClearance(pts, c.x, c.y);
  for (const hole of loops) if (hole.hole) room = Math.min(room, -captionClearance(hole, c.x, c.y) - config.gap / 2);
  // The number stays centered when a narrow cell cannot also fit its name.
  // These conservative discs contain 32px root numbers, 20px child numbers,
  // and the short 12px names below; type never shrinks or changes position.
  const need = labels ? 28 : 20;
  c.fits = room >= need + (c.fits ? 0 : 6);
  const target = c.fits ? 1 : 0;
  c.alpha += (target - c.alpha) * (c.fits ? fadeIn : fadeOut);
  c.nameFits = labels && room >= 54 + (c.nameFits ? 0 : 6);
  c.nameAlpha += ((c.nameFits ? 1 : 0) - c.nameAlpha) * (c.nameFits ? fadeIn : fadeOut);
  return c;
}

'''
replace(old,new)

start = s.index('    // the content: its own clock, its own drift')
end = s.index('\n  };\n  let hovered = null;', start)
replace(s[start:end], '''    // Preserve Skim's movement feedback independently of visible typography.
    const anchor = b.anchorState || (b.anchorState = { init: false, tox: 0, toy: 0, tr: 0, at: -1, area: 0 });
    driftAnchorStep(anchor, bigPts, big, bigA, t, inner.absX + b.x, inner.absY + b.y);
    b.anchorX = b.x + anchor.tox; b.anchorY = b.y + anchor.toy;

    const c = captionStep(b, bigPts, leaf.loops, leaf.labels, captionIn, captionOut);
    if (c.alpha > 0.01) {
      ctx.save();
      if (bigTrace) { bigTrace(); ctx.clip('nonzero'); }
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      if (leaf.labels) {
        ctx.globalAlpha = (0.48 + 0.20 * hv) * fade * c.alpha;
        ctx.font = '600 32px system-ui, sans-serif';
        ctx.fillText(String(leaf.label), c.x, c.y);
        if (c.nameAlpha > 0.01) {
          ctx.globalAlpha = (0.72 + 0.20 * hv) * fade * c.nameAlpha;
          ctx.font = '500 12px system-ui, sans-serif';
          ctx.fillText(b.name, c.x, c.y + 27);
        }
      } else {
        ctx.globalAlpha = (0.48 + 0.20 * hv) * fade * c.alpha;
        ctx.font = '600 20px system-ui, sans-serif';
        ctx.fillText(String(leaf.label), c.x, c.y);
      }
      ctx.restore();
    }''')
replace('  const halfGap = config.gap / 2, corner = config.cornerRadius;', '''  const halfGap = config.gap / 2, corner = config.cornerRadius;
  const captionIn = 1 - Math.exp(-dt / 0.18), captionOut = 1 - Math.exp(-dt / 0.10);''')
(ROOT / 'caption.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
