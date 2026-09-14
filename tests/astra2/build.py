"""Build Astra II from the exact, retained Astra I; do not rewrite old marks."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
raw = (ROOT / 'astra-i.html').read_bytes()
EXPECTED = '680ccf8755e5dda33755e6da8a336ba4f034f27828ed1619dfac8466de1be2a1'
if hashlib.sha256(raw).hexdigest() != EXPECTED:
    raise SystemExit('Astra I reference changed: rebaseline before rebuilding.')
s = raw.decode()

def replace(old, new):
    global s
    if s.count(old) != 1:
        raise ValueError(f'Build anchor missing or ambiguous: {old!r}')
    s = s.replace(old, new, 1)

replace('<title>Astra I — Hive</title>', '<title>Astra II — Hive</title>')
replace('&larr; Back · Astra I</a>', '&larr; Back · Astra II</a>')
replace('const px = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex;',
        'const spill=a2ExternalCarrot(this,b,t); const px = m * m * p.sx + 2 * m * e * p.cx + e * e * p.ex + spill[0];')
replace('const py = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey;',
        'const py = m * m * p.sy + 2 * m * e * p.cy + e * e * p.ey + spill[1];')
replace('const halfGap = config.gap / 2, corner = config.cornerRadius;', 'const halfGap = config.gap / 2;')
replace('const b = leaf.body, hv = leaf.hv, fade = leaf.fade;',
        'const b = leaf.body, hv = leaf.hv, fade = leaf.fade;\n'
        '    const scale=leaf.path[0].body.a2Scale || [1,1];\n'
        '    const corner=config.cornerRadius + Math.min(8,config.cornerRadius*.5)*(1-Math.min(...scale));')
replace('const allSeated = groups.length && groups.every(b=>b.rect && b.formRect===b.rect && b.crystal===1 && !b.leaving);',
        'const allSeated = groups.length && !(this.a2LoanCredit>1e-9) && groups.every(b=>b.rect && b.formRect===b.rect && b.crystal===1 && !b.leaving && (!b.a2Scale || b.a2Scale.every(x=>x===1)));')
marker = '/* --------------------------------------------------------------- START */'
replace(marker, (ROOT / 'tests/astra2/engine.js').read_text() + '\n' + marker)
(ROOT / 'astra-ii.html').write_text(s)
# The exact current gallery is used in CI. Only the new mark is regenerated.
index_path = ROOT / 'index.html'
if index_path.exists():
    index = index_path.read_text()
    index = re.sub(r'\s*<!-- ASTRA II -->.*?<!-- /ASTRA II -->', '', index, flags=re.S)
    index = index.replace('class="version-card latest"', 'class="version-card"')
    index = index.replace('<span class="latest-flag">Latest</span>', '')
    card = '''
        <!-- ASTRA II -->
        <a href="astra-ii.html" class="version-card latest">
            <h2>Astra II</h2><span class="latest-flag">Latest</span>
            <span class="mk">Astra II</span><span class="tag preview">Tested experiment</span>
            <p>Carry the existing footprint instead of melting before departure. Nearby roles may exchange; contact makes the moving participant yield, with bounded off-screen spill and locally balanced area credit.</p>
            <ul><li>No compulsory melt phase</li><li>Stable content identities, flexible destination roles</li><li>Selective yielding and repayable spillover</li></ul>
        </a>
        <a href="astra-ii-compare.html" class="version-card">
            <h2>Compare Astra I / II</h2><span class="tag preview">Frame stepping</span>
            <p>Equal viewports and one clock. Examine departures, crossings and recovery at 4.17–30 ms per frame.</p>
        </a>
        <!-- /ASTRA II -->
'''
    anchor = '<div class="previews">'
    if index.count(anchor) != 1:
        raise ValueError('Gallery anchor missing or ambiguous')
    index_path.write_text(index.replace(anchor, anchor + card, 1))
print('Astra II SHA256', hashlib.sha256(s.encode()).hexdigest())
