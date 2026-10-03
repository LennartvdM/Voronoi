"""Build Datum from Facet: the sea's gauge brackets from the first reach to touch.

With the sea, the auction's weights have one gauge: a shift of them all that
gives the sea its area. When a solve begins with no sea at all (every site's
reach covers its cell, no shore), Membrane brackets the shift between the one
at which every reach is gone (all sea) and the one at which the first reach
just touches its own cell (no sea yet), and closes the bracket by regula
falsi.

Two things were wrong with the high end.

- It was taken as the LEAST of the touching shifts, where the last reach has
  shrunk onto its cell and the sea is nearly the whole ground. Both ends of
  the bracket then drown the sites, the root is outside it, and twenty-four
  steps of regula falsi walk to the high end: every weight falls by about a
  million, most sites are left with no ground and are re-entered one at a
  time against whoever is left, and the ones buried under a later entrant sit
  the solve out (STEADY) and are not drawn that frame. The next frame repairs
  them, the one after drowns them again.
- It was taken over the cells alone, Amoeba's rule, where only a cell had a
  reach. Since Facet whitespace reaches too, as a square, and the sea appears
  in a whitespace's cell as in any other; left out of the bracket, its
  squares had let the sea in long before the first cell's reach touched.
  Likewise the least and greatest weights the bracket's low end and the
  empty-site case read were the cells' alone.

The branch runs only when the sea has vanished at a warm start, so it is rare
while the sea holds free ground and constant when the sea is small. Measured
on Facet over the chain through six pages from every other, the no-shore
gauge ran 89 times, missed the sea's area by more than a tenth of the ground
every time and by more than half 8 times; 534 sites sat a solve out.

DATUM. The bracket is taken over every site the sea cuts (a cell by its
reach, whitespace by its square), and its high end is the greatest of their
touching shifts.

Everything else is Facet's.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'facet.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '17087c3d4e4145f947614cfaa06f17d5158dc54269187053cc1f576a1e5eee6a'
s = raw.decode()

def replace(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Facet — Hive</title>', '<title>Datum — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Facet</a>', '<a class="back" href="index.html">&larr; Back · Datum</a>')

replace("""const STRIDE = true;                                // STRIDE: while the sea is in, Newton takes 8 steps a frame""",
"""const STRIDE = true;                                // STRIDE: while the sea is in, Newton takes 8 steps a frame
const DATUM = true;                                 // DATUM: the sea's gauge brackets from the first reach to touch""")

# ---- DATUM: the bracket --------------------------------------------------------------------------------------------
replace("""    let wmax = -Infinity, wmin = Infinity; for (let i = 0; i < n; i++) if (reaches(i)) { wmax = Math.max(wmax, w[i]); wmin = Math.min(wmin, w[i]); }   // AMOEBA: over the cells that reach""",
"""    // DATUM: over every site the sea cuts: a cell by its reach, and, since
    // Facet, whitespace by its square. Amoeba's bracket read the cells alone.
    const cut = i => reaches(i) || !!(sea.facet && sea.facet[i]);
    let wmax = -Infinity, wmin = Infinity; for (let i = 0; i < n; i++) if (DATUM ? cut(i) : reaches(i)) { wmax = Math.max(wmax, w[i]); wmin = Math.min(wmin, w[i]); }   // AMOEBA: over the cells that reach""")
replace("""      if (!(minOf(diag.areas) <= 0)) { hi = Infinity; diag.cells.forEach((c, i) => { if (!reaches(i)) return; const fa = sea.facet ? sea.facet[i] : 0; let R = 0; for (const pc of (c.pieces || [c])) for (const p of pc.pts) R = Math.max(R, fa ? w[i] - seaRise(w[i], p[0] - seeds[i][0], p[1] - seeds[i][1], fa) : (p[0] - seeds[i][0]) ** 2 + (p[1] - seeds[i][1]) ** 2); hi = Math.min(hi, R - w[i]); }); }""",
"""      // DATUM: THE FIRST REACH TO TOUCH, not the last. A site's reach covers
      // its cell down to the shift R - w at which it touches its farthest
      // corner, and the sea appears as soon as ONE reach has let go: at the
      // greatest of those shifts. The least of them is where the last reach
      // has shrunk onto its cell, with the sea nearly the whole ground; a
      // bracket from there to all-sea holds no root, and regula falsi walked
      // to its end, every weight down by a million, the sites drowned and
      // re-entered one by one, the buried ones sitting the solve out undrawn.
      if (!(minOf(diag.areas) <= 0)) { hi = DATUM ? -Infinity : Infinity; diag.cells.forEach((c, i) => { if (!(DATUM ? cut(i) : reaches(i))) return; const fa = sea.facet ? sea.facet[i] : 0; let R = 0; for (const pc of (c.pieces || [c])) for (const p of pc.pts) R = Math.max(R, fa ? w[i] - seaRise(w[i], p[0] - seeds[i][0], p[1] - seeds[i][1], fa) : (p[0] - seeds[i][0]) ** 2 + (p[1] - seeds[i][1]) ** 2); hi = DATUM ? Math.max(hi, R - w[i]) : Math.min(hi, R - w[i]); }); }""")

out = ROOT / 'datum.html'
out.write_text(s)
print(out, hashlib.sha256(s.encode()).hexdigest())
