"""Build Cadence from the exact Harbor accepted in PR #261.

The source fixture is byte-identical to harbor.html at GitHub commit
2f2f8265ac403da91acc51a17785d1763d46c4c2. No network or prior build is needed.
"""
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

replace('<title>Harbor — Hive</title>', '<title>Cadence — Hive</title>')
replace('class="back" href="manifold.html"', 'class="back" href="index.html"')
replace('&larr; Compare · Harbor</a>', '&larr; Back · Cadence</a>')
replace('  steer(dt, t) {', (HERE / 'pacing.js').read_text() + '\n  steer(dt, t) {')
replace('''        const u = Math.min(1, Math.max(0, (t - j.t0 - j.delay - (j.hold || 0)) / j.dur));
        b.progress = easeInOutCubic(u);''', '''        const paced = this.depth === 0 && b.path && !b.isVoid && !b.leaving;
        const u = paced ? this.cadenceClock(b, dt, t)
          : Math.min(1, Math.max(0, (t - j.t0 - j.delay - (j.hold || 0)) / j.dur));
        b.progress = paced ? u*u*u*(10 + u*(-15 + 6*u)) : easeInOutCubic(u);''')
replace('''      const end = j.t0 + (j.delay || 0) + (j.hold || 0) + (j.dur || 0) + 0.15;''', '''      const end = j.t0 + (j.delay || 0) + (j.hold || 0) + (j.dur || 0) + (j.cadenceSlip || 0) + 0.15;''')
(ROOT / 'cadence.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
