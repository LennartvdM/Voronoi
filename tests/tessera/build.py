"""Build the independent Tessera mark from the pinned reference Hive.

Tessera is Astra I's picture pipeline (the same outline and coverage fixes)
with a different root engine: tests/tessera/engine.js. The reference is
never modified; the mark is regenerated from it.
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

replace('<title>Hive</title>', '<title>Tessera — Hive</title>', 1)
replace('&larr; Back</a>', '&larr; Back · Tessera</a>', 1)
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
# its loops as they are, and the union that chains a hundred cells into one
# outline (and, once in a thousand frames, drops a piece) is never asked for.
replace("  for (const leaf of leaves) leaf.loops = leafOutlines(leaf.pieces);",
        "  for (const leaf of leaves) leaf.loops = leaf.isVoid ? leaf.pieces.filter(pc => pc.pts.length >= 3).map(pc => pc.pts) : leafOutlines(leaf.pieces);", 1)
marker = '/* --------------------------------------------------------------- START */'
replace(marker, (ROOT / 'tests/tessera/engine.js').read_text() + '\n' + marker, 1)
(ROOT / 'tessera.html').write_text(s)
index_path = ROOT / 'index.html'
index = index_path.read_text()
# idempotent: the block goes with the newline that follows it and any blank
# lines a previous build left, so a rebuild reproduces index.html byte for byte
index = re.sub(r'\s*<!-- TESSERA -->.*?<!-- /TESSERA -->[ \t]*\n(?:[ \t]*\n)*', '\n', index, flags=re.S)
index = index.replace('class="version-card latest"', 'class="version-card"')
index = index.replace('<span class="latest-flag">Latest</span>', '')
card = '''
        <!-- TESSERA -->
        <a href="tessera.html" class="version-card latest">
            <h2>Tessera</h2><span class="latest-flag">Latest</span>
            <span class="mk">Tessera</span>
            <span class="tag preview">Tested experiment</span>
            <p>Rigid tiles on conforming lattices. A settled tile departs as it is, no pre-melt; along every seam a tile's edge column carries the rows of the column across it, so the seam is straight; whitespace is one bidder with a ring that conforms to every tile's edge; a packing pass gives travellers right of way.</p>
            <ul>
                <li>No pre-melt: a settled tile moves as it is</li>
                <li>Conforming seams: no two lattices corrugate against each other</li>
                <li>Footprints yield and return; measured against Hive and Astra I</li>
            </ul>
        </a>
        <a href="tessera-compare.html" class="version-card">
            <h2>Compare Astra I / Tessera</h2>
            <span class="tag preview">Frame stepping</span>
            <p>Two identical-size canvases, a shared deterministic clock and no hover. Step through the same scene changes at 4.17–30 ms, or play them in slow motion.</p>
        </a>
        <!-- /TESSERA -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
index_path.write_text(index.replace(anchor, anchor + card, 1))
print('Built tessera.html from reference blob', EXPECTED)
print('Tessera SHA256', hashlib.sha256(s.encode()).hexdigest())
