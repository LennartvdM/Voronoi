"""Build the independent Bleed mark from the pinned reference Hive.

Bleed keeps the reference's shapes (walls, holes, point sites) and Astra I's
picture fixes, with a different root policy: tests/bleed/engine.js. The
reference is never modified; the mark is regenerated from it.
"""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
raw = (ROOT / 'hive.html').read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
EXPECTED = '2c02b2dc66d05fb152feffcd952f18b4d39f3634'
if blob != EXPECTED:
    raise SystemExit(f'Reference changed: expected {EXPECTED}, found {blob}; rebaseline before rebuilding.')
s = raw.decode()

def replace(old, new, count=None):
    global s
    found = s.count(old)
    if not found or (count is not None and found != count):
        raise ValueError(f'Expected {count or "at least one"} matches for {old!r}; found {found}')
    s = s.replace(old, new)

replace('<title>Hive</title>', '<title>Bleed — Hive</title>', 1)
replace('&larr; Back</a>', '&larr; Back · Bleed</a>', 1)
# Astra I's picture fixes: exact outlines, walls skipped in the leaf pass.
replace('simplifyLoop(l.pts)', 'simplifyLoop(l.pts, 1e-6, 1e-9)')
replace('simplifyLoop(l.pts, 0.05, 1e-5)', 'simplifyLoop(l.pts, 1e-6, 1e-9)')
replace('simplifyLoop(cell, 0.05, 1e-5)', 'simplifyLoop(cell, 1e-6, 1e-9)', 1)
replace('const loops = unionOutlines(parts).map(l => simplifyLoop(l.pts, 1e-6, 1e-9))',
        'const loops = unionOutlines(splitAtVertices(parts)).map(l => simplifyLoop(l.pts, 1e-6, 1e-9))', 1)
replace('for (const [b, subIdx] of idx) {\n      // every piece',
        'for (const [b, subIdx] of idx) {\n      if (b.wall) continue;\n      // every piece', 1)
replace('if (cell && cell.pts.length >= 3) own = cell.pieces || [cell];',
        'if (cell && cell.pts.length >= 3) { if (!own) own = []; own.push(...(cell.pieces || [cell])); }', 1)
replace('if (q.body === b) continue;', 'if (q.body === b || q.body.wall) continue;', 2)
replace('triangulate(simplifyLoop(cellPoly))', 'triangulate(simplifyLoop(cellPoly, 1e-6, 1e-9))', 1)
replace('triangulate(simplifyLoop(hl))', 'triangulate(simplifyLoop(hl, 1e-6, 1e-9))', 1)
# Two bodies' lattices may put a site on the same point (a tile waiting on
# a rectangle a void is opening in): the heavier site owns it outright and
# the lighter one has no cell. A tie goes to the lower index.
replace("        if (d / 2 + (wi - weights[j]) / (2 * d) > rFar) continue;   // exact per pair",
        "        if (d < 1e-9) { if (wi > weights[j] || (wi === weights[j] && i < j)) continue; poly = { pts: [], labs: [] }; dead = true; break; }\n"
        "        if (d / 2 + (wi - weights[j]) / (2 * d) > rFar) continue;   // exact per pair", 1)
# Whitespace paints nothing, so its outline is never dressed: its pieces are
# its loops as they are (the reserve is one leaf of many cells), and the union
# that chains cells into one outline is never asked for.
replace("  for (const leaf of leaves) leaf.loops = leafOutlines(leaf.pieces);",
        "  for (const leaf of leaves) leaf.loops = leaf.isVoid ? leaf.pieces.filter(pc => pc.pts.length >= 3).map(pc => pc.pts) : leafOutlines(leaf.pieces);", 1)
# the reserve's leaf carries the pockets nobody bid for (see adoptGround)
replace("        const pieces = [];\n        for (const i of subIdx) {",
        "        const pieces = b.blExtra ? b.blExtra.slice() : [];\n        for (const i of subIdx) {", 1)
# a newcomer's weight to a hundredth of a px² is enough (the reference bisects
# to a billionth: fifty-four auctions of one cell, a third of a slow frame)
replace("  let lo = -scale, hi = scale;\n  for (let k = 0; k < 54; k++) {", "  let lo = -scale, hi = scale;\n  for (let k = 0; k < 32; k++) {", 1)
marker = '/* --------------------------------------------------------------- START */'
replace(marker, (ROOT / 'tests/bleed/engine.js').read_text() + '\n' + marker, 1)
(ROOT / 'bleed.html').write_text(s)
print('Built bleed.html from reference blob', EXPECTED)
print('Bleed SHA256', hashlib.sha256(s.encode()).hexdigest())
