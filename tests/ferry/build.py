"""Build Ferry from the exact accepted Harbor source in PR #261."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (HERE / 'harbor.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '6d12a211b52708d00fb743109a2aa51f949609f82f6914c8f4dc48e46730c8a7'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Harbor — Hive</title>', '<title>Ferry — Hive</title>')
replace('class="back" href="manifold.html"', 'class="back" href="index.html"')
replace('&larr; Compare · Harbor</a>', '&larr; Back · Ferry</a>')
replace('r.body.reaped || r.body.journey !== r.journey ? 1 : r.body.progress',
        'ferryLedgerProgress(this, r, t)')
marker = '/* --------------------------------------------------------------- START */'
replace(marker, (HERE / 'crossings.js').read_text() + '\n' + marker)
(ROOT / 'ferry.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
