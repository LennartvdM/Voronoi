"""Build the independent Astra I mark; never modify the reference Hive."""
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

replace('<title>Hive</title>', '<title>Astra I — Hive</title>', 1)
replace('&larr; Back</a>', '&larr; Back · Astra I</a>', 1)
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
marker = '/* --------------------------------------------------------------- START */'
replace(marker, (ROOT / 'tests/astra/engine.js').read_text() + '\n' + marker, 1)
(ROOT / 'astra-i.html').write_text(s)
index_path = ROOT / 'index.html'
index = index_path.read_text()
# Remove only our own previous gallery card, making generation idempotent.
index = re.sub(r'\s*<!-- ASTRA I -->.*?<!-- /ASTRA I -->', '', index, flags=re.S)
index = index.replace('class="version-card latest"', 'class="version-card"')
index = index.replace('<span class="latest-flag">Latest</span>', '')
card = '''
        <!-- ASTRA I -->
        <a href="astra-i.html" class="version-card latest">
            <h2>Astra I</h2><span class="latest-flag">Latest</span>
            <span class="mk">Astra I</span>
            <span class="tag preview">Tested experiment</span>
            <p>One shared weight per body, with sites that form its destination rectangle. Transitioning bodies stay in the full-domain partition instead of repeatedly removing and returning ground through holes.</p>
            <ul>
                <li>Grouped-site geometry, not interpolated pictures</li>
                <li>Frame-wise verification at 240, 120 and 60 Hz, 30 ms and jittered steps</li>
                <li>Existing Hive and GPT 2 retained for comparison</li>
            </ul>
        </a>
        <a href="astra-i-compare.html" class="version-card">
            <h2>Compare Hive / Astra I</h2>
            <span class="tag preview">Frame stepping</span>
            <p>Two identical-size canvases, a shared deterministic clock and no hover. Step through the same scene changes at 4.17–30 ms, or play them in slow motion.</p>
        </a>
        <!-- /ASTRA I -->
'''
anchor = '<div class="previews">'
if index.count(anchor) != 1:
    raise ValueError('Gallery anchor missing or ambiguous')
index_path.write_text(index.replace(anchor, anchor + card, 1))
print('Built astra-i.html from reference blob', EXPECTED)
print('Astra I SHA256', hashlib.sha256(s.encode()).hexdigest())
