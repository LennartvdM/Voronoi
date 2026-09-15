"""Build the isolated Astra III mark without rewriting the reference."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = '680ccf8755e5dda33755e6da8a336ba4f034f27828ed1619dfac8466de1be2a1'
base = (ROOT / 'astra-i.html').read_bytes()
assert hashlib.sha256(base).hexdigest() == REFERENCE, 'Astra I reference changed'
source = base.decode()
marker = '/* --------------------------------------------------------------- START */'
assert source.count(marker) == 1
parts = ['geometry', 'root', 'motion', 'render', 'reserve', 'outline']
engine = '\n\n'.join((ROOT / 'tests/astra3' / (p + '.js')).read_text().rstrip() for p in parts)
source = source.replace(marker, engine + '\n\n' + marker)
source = source.replace('<title>Astra I — Hive</title>', '<title>Astra III — Hive</title>')
source = source.replace('Back · Astra I', 'Back · Astra III')
assert hashlib.sha256(source.encode()).hexdigest() == '7f92b5052d6845bb8ef76fec48db510ca710487c7c84dd0789992f81527757a1', 'Source differs from tested release'
(ROOT / 'astra-iii.html').write_text(source)
print('Astra III SHA256', hashlib.sha256(source.encode()).hexdigest())
# The existing gallery and all old marks remain intact.
index = ROOT / 'index.html'
if index.exists():
    text = index.read_text()
    if '<!-- ASTRA III -->' not in text:
        card = '''        <!-- ASTRA III -->
        <a href="astra-iii.html" class="version-card">
            <h2>Astra III</h2><span class="mk">Astra III</span><span class="tag preview">Tested experiment</span>
            <p>Continuous support shapes instead of a corrugated lattice. Jointly planned smooth arcs, progressive departure deformation, and full-world contours cropped by the screen.</p>
        </a>
        <a href="astra-iii-compare.html" class="version-card">
            <h2>Compare Astra I / III</h2><span class="tag preview">Frame stepping</span>
            <p>Equal viewports, synchronized scene changes, and 4.17–30 ms frame steps.</p>
        </a>
        <!-- /ASTRA III -->
'''
        assert '<div class="previews">' in text
        text = text.replace('<div class="previews">', '<div class="previews">\n' + card, 1)
        index.write_text(text)
