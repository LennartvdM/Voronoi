"""Build Skim from the pinned, accepted Buoy mark (PR #264)."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (HERE / 'buoy.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '324510ae3880a69df7070139aa5b09ba133ac3aff040c68b64ea89c96acd9bba'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new)

replace('<title>Buoy — Hive</title>', '<title>Skim — Hive</title>')
replace('&larr; Back · Buoy</a>', '&larr; Back · Skim</a>')

start = s.index('function computeDiagram(')
end = s.index('\nconst WALL_TRI', start)
old = s[start:end]
# Geometry stays fixed for all Newton and line-search evaluations in one
# solve. Prepare buckets once; populate each ordered ring only if visited.
setup_start = old.index('  const maxDw = wmax - wmin;')
setup_end = old.index('  for (let i = 0; i < n; i++) {\n    const sx', setup_start)
buckets = old[setup_start:setup_end].replace('  const maxDw = wmax - wmin;\n', '').replace('  const cand = [];\n', '')
prepare = '''// SKIM: this object lives for ONE solve, never across frames. The seeds and
// bounds cannot move during a weight solve. Ring order, distance arithmetic,
// clipping order and pruning tests are exactly the same as Buoy's.
function prepareDiagram(seeds, boundsPts) {
  const n = seeds.length;
  const baseLabs = boundsPts.map((_, k) => -1 - k);
  let bx0 = Infinity, by0 = Infinity, bx1 = -Infinity, by1 = -Infinity;
  for (const p of boundsPts) { bx0 = Math.min(bx0, p[0]); by0 = Math.min(by0, p[1]); bx1 = Math.max(bx1, p[0]); by1 = Math.max(by1, p[1]); }
''' + buckets + '''  const rings = Array.from({ length: n }, () => []);
  const far = seeds.map(([sx, sy]) => {
    let r = 0;
    for (const p of boundsPts) r = Math.max(r, Math.hypot(p[0] - sx, p[1] - sy));
    return r;
  });
  const candidates = (i, ring) => {
    if (rings[i][ring]) return rings[i][ring];
    const sx = seeds[i][0], sy = seeds[i][1], cand = [];
    const x0 = bxi[i] - ring, x1 = bxi[i] + ring, y0 = byi[i] - ring, y1 = byi[i] + ring;
    for (let yy = Math.max(0, y0); yy <= Math.min(gh - 1, y1); yy++) {
      for (let xx = Math.max(0, x0); xx <= Math.min(gw - 1, x1); xx++) {
        if (ring > 0 && xx !== x0 && xx !== x1 && yy !== y0 && yy !== y1) continue;
        for (const j of buckets[yy * gw + xx]) if (j !== i) cand.push(j);
      }
    }
    cand.sort((a, b) => ((seeds[a][0] - sx) ** 2 + (seeds[a][1] - sy) ** 2) - ((seeds[b][0] - sx) ** 2 + (seeds[b][1] - sy) ** 2));
    return rings[i][ring] = cand.map(j => ({ j, d: Math.hypot(seeds[j][0] - sx, seeds[j][1] - sy) }));
  };
  return { baseLabs, cs, maxRing, far, candidates };
}

'''
new = old.replace('function computeDiagram(seeds, weights, boundsPts, tris) {', 'function computeDiagram(seeds, weights, boundsPts, tris, prepared) {')
new = new.replace('  const baseLabs = boundsPts.map((_, k) => -1 - k);', '  const plan = prepared || prepareDiagram(seeds, boundsPts);\n  const { baseLabs, cs, maxRing } = plan;')
new = new.replace('  let bx0 = Infinity, by0 = Infinity, bx1 = -Infinity, by1 = -Infinity;\n  for (const p of boundsPts) { bx0 = Math.min(bx0, p[0]); by0 = Math.min(by0, p[1]); bx1 = Math.max(bx1, p[0]); by1 = Math.max(by1, p[1]); }\n', '')
new = new.replace(old[setup_start:setup_end], '  const maxDw = wmax - wmin;\n')
new = new.replace('    let rFar = 0;\n    for (const p of boundsPts) rFar = Math.max(rFar, Math.hypot(p[0] - sx, p[1] - sy));', '    let rFar = plan.far[i];')
a = new.index('      cand.length = 0;')
b = new.index('        if (d / 2', a)
new = new[:a] + '      for (const { j, d } of plan.candidates(i, ring)) {\n' + new[b:]
replace(old, prepare + new)

start = s.index('function solveWeights(')
end = s.index('\n/* ============================================================== LATTICE', start)
old = s[start:end]
new = old.replace('  let evals = 0;', '  const prepared = prepareDiagram(seeds, boundsPts);\n  let evals = 0;')
assert new.count('computeDiagram(seeds, w, boundsPts, tris)') == 3
assert new.count('computeDiagram(seeds, wt, boundsPts, tris)') == 1
new = new.replace('computeDiagram(seeds, w, boundsPts, tris)', 'computeDiagram(seeds, w, boundsPts, tris, prepared)')
new = new.replace('computeDiagram(seeds, wt, boundsPts, tris)', 'computeDiagram(seeds, wt, boundsPts, tris, prepared)')
replace(old, new)

# Same S=2 grid, intersections, half-open edges and hole signs. Count runs
# between coverage changes rather than visiting every covered pixel.
replace('  const cov = new Int16Array(gw * gh);', '''  const rows = Array.from({ length: gh }, () => []);''')
replace('        for (let cx2 = c0; cx2 <= c1; cx2++) cov[ry * gw + cx2] += sign;', '''        if (c0 <= c1) rows[ry].push([c0, sign], [c1 + 1, -sign]);''')
replace('  for (let k = 0; k < cov.length; k++) { if (cov[k] <= 0) gap++; else if (cov[k] > 1) over++; }', '''  for (const row of rows) {
    row.sort((a, b) => a[0] - b[0]);
    let x = 0, coverage = 0;
    for (const [at, delta] of row) {
      if (coverage <= 0) gap += at - x;
      else if (coverage > 1) over += at - x;
      coverage += delta; x = at;
    }
    if (coverage <= 0) gap += gw - x;
    else if (coverage > 1) over += gw - x;
  }''')
replace('// Exact scanline rasterization of the picture\'s polygons, even-odd, so a\n// notched cell counts right: 0 = gap, 2+ = overlap.', '''// Exact scanline rasterization of the picture's polygons, even-odd, so a
// notched cell counts right: 0 = gap, 2+ = overlap. Skim counts constant-
// coverage runs; it uses the same sample grid and still checks every 12 frames.''')
(ROOT / 'skim.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
