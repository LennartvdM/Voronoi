"""Build Apace from Cohort: the cells keep up with their plans.

A seed followed its plan on a spring damped against the page, so it trailed
its plan by about a fifth of a second of its speed. The sea closes on the
change's clock, so it closed while the cells were still on their way: they
turned crisp before they arrived, and then slid the rest of the way onto their
places and the screen's edges.

Here, on the page's own changes (where the sea is), the spring damps against
the plan's own motion, so a seed keeps up with its plan and arrives when its
clock says. The spring's stiffness, its damping and its wobble are Cohort's.

The stories and the fields inside cells are Cohort's.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cohort.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '708b554e6543d58d1f316047a06e62d0a9076a500ac224e5040bfe305e5b5b9d'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Cohort — Hive</title>', '<title>Apace — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Cohort</a>', '<a class="back" href="index.html">&larr; Back · Apace</a>')

replace("""const COHORT = true;                                // COHORT: from page to page, the gallery is one body""",
"""const COHORT = true;                                // COHORT: from page to page, the gallery is one body
const KEEPUP = true;                                // KEEP UP: on the page, a seed keeps up with its plan""")

replace("""        ax = (px + Math.sin(t * 0.6 + k * 1.7) * wob - b.x) * k1 - b.vx * k2;
        ay = (py + Math.cos(t * 0.5 + k * 2.3) * wob - b.y) * k1 - b.vy * k2;""",
"""        // KEEP UP: on the page, the spring damps against the plan's own
        // motion, not the page's, so the seed keeps up with its plan and
        // arrives when its clock says; the plan's speed is how far it moved
        // since the frame before on the same path
        const up = KEEPUP && this.depth === 0 && this.seaOpen() && b.upPath === p && dt > 0, pvx = up ? (px - b.upX) / dt : 0, pvy = up ? (py - b.upY) / dt : 0;
        if (KEEPUP) { b.upPath = p; b.upX = px; b.upY = py; }
        ax = (px + Math.sin(t * 0.6 + k * 1.7) * wob - b.x) * k1 + (pvx - b.vx) * k2;
        ay = (py + Math.cos(t * 0.5 + k * 2.3) * wob - b.y) * k1 + (pvy - b.vy) * k2;""")

out = ROOT / 'apace.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
