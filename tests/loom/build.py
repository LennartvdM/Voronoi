"""Build Loom from pinned Weave, including the verified Selvedge changes.

The intermediate Selvedge blob is checked so this recipe is independent of
whether PR #259 has been merged. Prior mark files and the gallery are untouched.
LOOM_BASELINE_OUT optionally writes that intermediate page for comparison tests.
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

baseline = s.encode()
expected_baseline = '9b10a9094ba149429c36a2c36a78b35cb0e26dc1'
actual_baseline = hashlib.sha1(b'blob ' + str(len(baseline)).encode() + b'\0' + baseline).hexdigest()
if actual_baseline != expected_baseline:
    raise SystemExit(f'Selvedge reconstruction changed: {actual_baseline}')
if os.environ.get('LOOM_BASELINE_OUT'):
    Path(os.environ['LOOM_BASELINE_OUT']).write_bytes(baseline)

replace('<title>Selvedge — Hive</title>', '<title>Loom — Hive</title>')
replace('&larr; Back · Selvedge</a>', '&larr; Back · Loom</a>')

# Refined content needs the same persistent site lifecycle as whitespace.
# Its union is still one body in the renderer, including during a departure.
replace("    // A root void's sites are its current geometry. Clearing its destination", "    // A root body's sites are its current geometry. Clearing its destination")
replace('    // the void still owns area. plSeamSites places and funds these same sites', '    // the body still owns area. plSeamSites places and funds these same sites')
replace('this.depth === 0 && b.isVoid && b.plCurrent', 'this.depth === 0 && b.plCurrent')
replace('(b.isVoid && b.plCurrent)', 'b.plCurrent')
replace('this.depth === 0 && s.body.isVoid ?', 'this.depth === 0 ?')
replace('b.isVoid && b.leaving\n        ?', 'b.leaving\n        ?')
replace('if (!v.isVoid || v.leaving) continue;', 'if (!v.isVoid || v.leaving || !(v.formRect || v.rect)) continue;')
replace('const rc = c.formRect || c.rect;\n        if (', 'const rc = c.formRect || c.rect;\n        if (!rc || c.leaving) continue;\n        if (')
replace('  steer(dt, t) {', '''  // Let the existing spring settle at the shared grid coordinates. Fading
  // the ongoing wobble and circular repulsion needs no positional snap and
  // never sets the crystal/pin flags that would activate rectangular walls.
  gridArrival(b) {
    return this.depth === 0 && (this.scene === 'hero' || this.scene === 'frame') && b.rect && !b.leaving
      ? S3((b.progress - 0.7) / 0.3) : 0;
  }

  steer(dt, t) {''')
replace('const wob = 2.5 * (1 - b.crystal);', 'const wob = 2.5 * (1 - b.crystal) * (1 - this.gridArrival(b));')
replace('const f = F * (1 - Math.min(A.crystal, B.crystal)) * (1 - d / R) * dt / dn;\n          A.vx -= dx * f * (1 - A.crystal); A.vy -= dy * f * (1 - A.crystal);\n          B.vx += dx * f * (1 - B.crystal); B.vy += dy * f * (1 - B.crystal);', '''const a = Math.max(A.crystal, this.gridArrival(A)), b = Math.max(B.crystal, this.gridArrival(B));
          const f = F * (1 - Math.min(a, b)) * (1 - d / R) * dt / dn;
          A.vx -= dx * f * (1 - a); A.vy -= dy * f * (1 - a);
          B.vx += dx * f * (1 - b); B.vy += dy * f * (1 - b);''')
start = s.index('    // Pair old and new sites by order')
s = s[:start] + '''    // Sidebar's shared row centers extended through both axes. Every tile
    // has the same neighbors' row and column coordinates. At rest the power
    // diagram can therefore realize the template with area weights alone.
    // These are generators, not clips or domain pieces. The renderer unions
    // all tiles belonging to one body, including the central Frame void.
    if (this.scene === 'hero' || this.scene === 'frame') {
      const seated = live.filter(b => !b.leaving && (b.formRect || b.rect));
      const xs = [...new Set(seated.flatMap(b => { const r = b.formRect || b.rect; return [r[0], r[2]]; }))].sort((a,b) => a-b);
      const ys = [...new Set(seated.flatMap(b => { const r = b.formRect || b.rect; return [r[1], r[3]]; }))].sort((a,b) => a-b);
      for (const b of seated) {
        const r = b.formRect || b.rect, cx = (r[0]+r[2])/2, cy = (r[1]+r[3])/2;
        const target = [];
        for (let j=0;j<ys.length-1;j++) for (let i=0;i<xs.length-1;i++) {
          const x0=xs[i], x1=xs[i+1], y0=ys[j], y1=ys[j+1];
          if (x0 < r[0]-E || x1 > r[2]+E || y0 < r[1]-E || y1 > r[3]+E) continue;
          target.push({x:(x0+x1)/2-cx, y:(y0+y1)/2-cy, q:(x1-x0)*(y1-y0)});
        }
        if (target.length) b.wvTo=target;
      }
    }
''' + s[start:]
replace('  const du = (this.lastDt || 1 / 60) / WV_SITE_SLEW;', '''  const du = (this.lastDt || 1 / 60) / WV_SITE_SLEW;
  // Frame has four connected sides: refine the ring once all have arrived.
  // Hero can refine each body's column as it approaches its own destination.
  const ringReady = S3((live.filter(b => !b.leaving && b.rect)
    .reduce((p, b) => Math.min(p, b.progress), 1) - 0.999) / 0.001);''')
replace('    b.wvU = Math.min(1, (b.wvU || 0) + du);', '''    const arriving = !b.leaving && b.rect;
    const gate = arriving && this.scene === 'frame' ? ringReady
      : arriving && this.scene === 'hero' ? S3((b.progress - 0.95) / 0.05) : 1;
    // A repeated scene request may reset an arrival clock. It must never
    // rewind a formation that is already on screen.
    const previous = b.wvU || 0;
    b.wvU = Math.max(previous, Math.min(gate, previous + du));''')
out = Path(os.environ.get('LOOM_OUT', ROOT / 'loom.html'))
out.write_bytes(s.encode())
print('Built', out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
print('Loom SHA256', hashlib.sha256(s.encode()).hexdigest())
