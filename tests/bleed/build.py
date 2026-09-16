"""Build the independent Bleed mark from the pinned reference Hive.

Bleed keeps the reference's shapes (walls, holes, point sites) and Astra I's
picture fixes, with a different root policy: tests/bleed/engine.js. The
reference is never modified; the mark is regenerated from it.
"""
from pathlib import Path
import os
import sys
import re
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
        "  for (const leaf of leaves) leaf.loops = leaf.isVoid ? leaf.pieces.filter(pc => pc.pts.length >= 3).map(pc => pc.pts) : leafOutlines(leaf.pieces);\n  blClipNested(leaves);", 1)
# the reserve's leaf carries the pockets nobody bid for (see adoptGround)
replace("        const pieces = [];\n        for (const i of subIdx) {",
        "        const pieces = b.blExtra ? b.blExtra.slice() : [];\n        for (const i of subIdx) {", 1)
# a newcomer's weight to a hundredth of a px² is enough (the reference bisects
# to a billionth: fifty-four auctions of one cell, a third of a slow frame)
# A SEED ENTERS AT THE AREA THAT SEED IS PAINTED AT. The reference reads a
# BODY's painted area, which is the same thing while every body has one site;
# the reserve has one per run of margin cells, so a margin site returning to
# the auction asked for the whole ring — half the page — and the bisection
# handed it a weight the solve then had to undo. Each site carries its own.
replace("    if (this.solved) { const ar = this.solved.diagram.areas; this.solvedSubs.forEach((s, i) => { s.body.paintArea += ar[i] || 0; }); }",
        "    for (const b of this.bodies) for (const s of b.subs) s.blPaint = 0;\n"
        "    if (this.solved) { const ar = this.solved.diagram.areas; this.solvedSubs.forEach((s, i) => { s.body.paintArea += ar[i] || 0; s.blPaint = ar[i] || 0; }); }", 1)
replace("const target = Math.min(s.body.paintArea > 1 ? s.body.paintArea : fair, 0.98 * domainArea);",
        "const sPaint = s.blPaint !== undefined ? s.blPaint : s.body.paintArea;\n"
        "        const target = Math.min(sPaint > 1 ? sPaint : fair, 0.98 * domainArea);", 1)
replace("const target = Math.min(s.body.paintArea > 1 ? s.body.paintArea : fair, 0.98 * ga);",
        "const sPaintS = s.blPaint !== undefined ? s.blPaint : s.body.paintArea;\n"
        "        const target = Math.min(sPaintS > 1 ? sPaintS : fair, 0.98 * ga);", 1)
replace("paint: idx.map(i => active[i].body.paintArea) });",
        "paint: idx.map(i => active[i].blPaint !== undefined ? active[i].blPaint : active[i].body.paintArea) });", 1)
replace("paint: active.map(s => s.body.paintArea) });",
        "paint: active.map(s => s.blPaint !== undefined ? s.blPaint : s.body.paintArea) });", 1)
replace("paint: idx.map(s => s.body.paintArea) });",
        "paint: idx.map(s => s.blPaint !== undefined ? s.blPaint : s.body.paintArea) });", 1)

# the line search: the reference refuses a Newton step that would take any
# cell below half the smallest target or area, and halves the step forty
# times before giving up (development: BLEED_EPS0 and BLEED_HALVINGS)
EPS0 = os.environ.get('BLEED_EPS0', '0.5')
HALVINGS = os.environ.get('BLEED_HALVINGS', '40')
replace('  const eps0 = 0.5 * Math.min(minOf(tgt), minOf(diag.areas));', '  const eps0 = ' + EPS0 + ' * Math.min(minOf(tgt), minOf(diag.areas));', 1)
replace('    for (let bt = 0; bt < 40 && !accepted; bt++, t /= 2) {', '    for (let bt = 0; bt < ' + HALVINGS + ' && !accepted; bt++, t /= 2) {', 1)
# the flock's rest sizes are scaled to the page, not the window
replace('      const K = rel > 0 ? this.COLS * this.ROWS / rel : 1;',
        '      const K = rel > 0 ? (BL_FILL ? this.blSlots() : this.COLS * this.ROWS) / rel : 1;', 1)
# every scene specification passes through the engine: edge rectangles run into the bleed
replace("    const spec = scenes[name] ? scenes[name](this.COLS, this.ROWS, content.length) : null;",
        "    const spec = scenes[name] ? this.blSpec(scenes[name](this.COLS, this.ROWS, content.length)) : null;", 1)
# the seed clamp is the page's, not the window's: a site evicted from a tile
# may stand in the bleed when that is where the nearest free ground is
replace('    const bodies = this.bodies, W = this.W, H = this.H;\n',
        '    const bodies = this.bodies, W = this.W, H = this.H;\n    const [CX0, CY0, CX1, CY1] = this.blClampBox ? this.blClampBox() : [SEED_MARGIN, SEED_MARGIN, W - SEED_MARGIN, H - SEED_MARGIN];\n', 1)
replace('b.x = Math.min(W - SEED_MARGIN, Math.max(SEED_MARGIN, b.x));', 'b.x = Math.min(CX1, Math.max(CX0, b.x));', 2)
replace('b.y = Math.min(H - SEED_MARGIN, Math.max(SEED_MARGIN, b.y));', 'b.y = Math.min(CY1, Math.max(CY0, b.y));', 2)
replace("  let lo = -scale, hi = scale;\n  for (let k = 0; k < 54; k++) {", "  let lo = -scale, hi = scale;\n  for (let k = 0; k < 32; k++) {", 1)
marker = '/* --------------------------------------------------------------- START */'
engine = (ROOT / 'tests/bleed/engine.js').read_text()
# development only: BLEED_VARS="BL_YIELD=0,BL_LEAD=0" builds a variant with those constants
for kv in filter(None, os.environ.get('BLEED_VARS', '').split(',')):
    k, v = kv.split('=')
    n = len(re.findall(r'^const ' + re.escape(k) + r' = [^;]+;', engine, flags=re.M))
    if n != 1:
        raise SystemExit(f'BLEED_VARS: {k} found {n} times')
    engine = re.sub(r'^const ' + re.escape(k) + r' = [^;]+;', f'const {k} = {v};', engine, flags=re.M)
replace(marker, engine + '\n' + marker, 1)
import os
OUT = Path(os.environ.get('BLEED_OUT', str(ROOT / 'bleed.html')))   # a variant build for an experiment, off the tree
OUT.write_text(s)
if OUT != ROOT / 'bleed.html':
    print('Built variant ' + str(OUT))
    sys.exit(0)
index_path = ROOT / 'index.html'
index = index_path.read_text()
# idempotent: the block goes with the newline that follows it and any blank
# lines a previous build left, so a rebuild reproduces index.html byte for byte
index = re.sub(r'\s*<!-- BLEED -->.*?<!-- /BLEED -->[ \t]*\n(?:[ \t]*\n)*', '\n', index, flags=re.S)
index = index.replace('class="version-card latest"', 'class="version-card"')
index = index.replace('<span class="latest-flag">Latest</span>', '')
card = '''
        <!-- BLEED -->
        <a href="bleed.html" class="version-card latest">
            <h2>Bleed</h2><span class="latest-flag">Latest</span>
            <span class="mk">Bleed</span>
            <span class="tag preview">Tested experiment</span>
            <p>Every cell a rectangle or a Voronoi cell. A settled tile asked to move travels as a rigid rectangle, a hole in the auction's ground; everything else is a convex power cell, cut straight where it meets a tile. The page is wider than the window: one lattice cell of margin on every side, whitespace the reserve bids for, into which tiles are pushed and cells spill, visibly.</p>
            <ul>
                <li>No lattices of sites: nothing corrugates, nothing steps</li>
                <li>A bleed margin the layout uses; a margin view shows the whole page</li>
                <li>Measured against Tessera and Astra I: shape, spill, motion, coverage</li>
            </ul>
        </a>
        <a href="bleed-compare.html" class="version-card">
            <h2>Compare Tessera / Bleed</h2>
            <span class="tag preview">Frame stepping</span>
            <p>Two identical-size canvases, a shared deterministic clock and no hover. Step through the same scene changes at 4.17–30 ms, or play them in slow motion.</p>
        </a>
        <!-- /BLEED -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
index_path.write_text(index.replace(anchor, anchor + card, 1))
print('Built bleed.html from reference blob', EXPECTED)
print('Bleed SHA256', hashlib.sha256(s.encode()).hexdigest())
