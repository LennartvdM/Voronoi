"""Build Selvedge from the immutable Weave source.

Keep a retiring void's seam sites until its claim drains, and preserve site
objects so scene changes retain the auction's converged weights. Templates,
claims, travel clocks, and the resting seam targets stay as they are in Weave.
"""
from pathlib import Path
import hashlib
import os

ROOT = Path(__file__).resolve().parents[2]
raw = (ROOT / 'weave.html').read_bytes()
EXPECTED = '4ce0be4882f5c1e1268b3d39ed64df38fa450b8f'
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
if blob != EXPECTED:
    raise SystemExit(f'Weave changed: expected {EXPECTED}, found {blob}')
s = raw.decode()


def replace(old, new, count=1):
    global s
    found = s.count(old)
    if found != count:
        raise ValueError(f'Expected {count} matches for {old[:70]!r}; found {found}')
    s = s.replace(old, new)


replace('<title>Weave — Hive</title>', '<title>Selvedge — Hive</title>')
replace('&larr; Back · Weave</a>', '&larr; Back · Selvedge</a>')

replace('''  refreshFormation(b) {
    b.subs.length = 1;
  }''', '''  refreshFormation(b) {
    // A root void's sites are its current geometry. Clearing its destination
    // on retirement or resizing the page must not erase that geometry while
    // the void still owns area. plSeamSites places and funds these same sites
    // until the existing claim ledger has drained and reap removes the body.
    if (this.depth === 0 && b.isVoid && b.plCurrent) return;
    b.subs.length = 1;
  }''')

replace('''  for (const b of this.bodies) if (!b.isSelf && (b.formRect || b.rect)) live.push(b);''',
'''  for (const b of this.bodies) {
    if (!b.isSelf && (b.formRect || b.rect || (b.isVoid && b.plCurrent))) live.push(b);
  }''')

replace('''      b.wvTo = [{ x: 0, y: 0, q: 1 }];''', '''      // Closing whitespace keeps the formation that actually exists now,
      // including an interrupted morph. Its claim shrinks on the original
      // ledger; there is no separate collapse to a centre seed at release.
      b.wvTo = b.isVoid && b.leaving
        ? old.map(p => ({ x: p.x, y: p.y, q: p.q }))
        : [{ x: 0, y: 0, q: 1 }];''')

replace('''      if (!v.isVoid) continue;
      const rv = v.formRect || v.rect;''', '''      if (!v.isVoid || v.leaving) continue;
      const rv = v.formRect || v.rect;''')

replace('''      b.subs = b.wvFrom.map(() => ({ body: b, x: 0, y: 0, w: 0, claim: 0, live: false }));''',
'''      // Existing objects carry the previous solve's weights and live flags.
      // Rebuilding them makes every scene change a cold auction, even when
      // their positions and claims have hardly moved. Only newcomers are new.
      while (b.subs.length < n) b.subs.push(makeSub(b, b.x, b.y));''')

# The single-site ancestor stored only a body's painted area. A multi-site
# void must not give that entire area to EACH entering or rescued site.
replace('''  recordAreas() {
    for (const b of this.bodies) b.paintArea = 0;
    if (this.solved) { const ar = this.solved.diagram.areas; this.solvedSubs.forEach((s, i) => { s.body.paintArea += ar[i] || 0; }); }''',
'''  sitePaint(s) {
    return this.depth === 0 && s.body.isVoid ? (s.paintArea || 0) : s.body.paintArea;
  }

  recordAreas() {
    for (const b of this.bodies) {
      b.paintArea = 0;
      for (const s of b.subs) s.paintArea = 0;
    }
    if (this.solved) { const ar = this.solved.diagram.areas; this.solvedSubs.forEach((s, i) => {
      s.paintArea = ar[i] || 0;
      s.body.paintArea += s.paintArea;
    }); }''')
replace('s.body.paintArea > 1 ? s.body.paintArea : fair',
        'this.sitePaint(s) > 1 ? this.sitePaint(s) : fair', count=2)
replace('paint: idx.map(i => active[i].body.paintArea)',
        'paint: idx.map(i => this.sitePaint(active[i]))')
replace('paint: active.map(s => s.body.paintArea)',
        'paint: active.map(s => this.sitePaint(s))')
replace('paint: idx.map(s => s.body.paintArea)',
        'paint: idx.map(s => this.sitePaint(s))')

out = Path(os.environ.get('SELVEDGE_OUT', ROOT / 'selvedge.html'))
out.write_bytes(s.encode())
print('Built', out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
print('Selvedge SHA256', hashlib.sha256(s.encode()).hexdigest())
