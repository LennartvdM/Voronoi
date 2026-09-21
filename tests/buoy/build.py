"""Build Buoy from the exact accepted Ferry source in PR #263."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (HERE / 'ferry.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'f5930f96e356a17f95b56195383d514ce80eddbdce4bfd8ad56ffa7f0b20debf'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Ferry — Hive</title>', '<title>Buoy — Hive</title>')
replace('&larr; Back · Ferry</a>', '&larr; Back · Buoy</a>')
replace('''    b.plCurrent = cur;
    for (let i = 0; i < cur.length; i++) {''', '''    b.plCurrent = cur;
    // placeSeeds already funded the content body's eased hover request.
    // Forming the seams must distribute that funded claim, not replace it
    // with the unboosted base claim. Whitespace retains its own ledger.
    const budget = b.isVoid ? b.claim : b.subs[0].claim;
    for (let i = 0; i < cur.length; i++) {''')
replace('sub.claim = b.claim * p.q / sum;', 'sub.claim = budget * p.q / sum;')
(ROOT / 'buoy.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
