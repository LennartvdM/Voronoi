"""Build Yinyang from Cohort: the two images swap by a rule of their own.

A change from page to page has two cells unlike the rest, and the hive knows
which before it starts: the image that closes, which will shrink to a card,
and the card that was clicked, which will balloon into the image. On Cohort
they still travelled like any other cell, on the shallow bend every path
shares, and only their sizes were timed so that they would not collide.

Here the two swap by a discrete rule.
- They swing round each other. Both paths are bent the same way about their
  chords, so the two pass side by side as yin and yang turn. The bend is the
  least that lets them pass clear at the sizes the change's clock gives them,
  and no more than a chord's length (about a half circle), nor than keeps
  both arcs on the page, since a seed cannot leave it. They turn the way that
  needs the lesser bend.
- They have right of way. While they swap they push the cards in their way
  and are not pushed back.
- Cohort's handover where they pass is taken out: the arcs keep them clear.
  The rest of Cohort's rules stand: the gallery keeps its side, an image is a
  card while it is in the gallery, and while the images change hands ground
  nobody claims is the sea's.

A slider, Breathe, lets the cards of both pages give way as well: each bids
less by that share of its size at the change's middle, on the change's own
clock (none at either rest, all of it halfway), so the swap has more room.
It is at 0 by default: at 40 (each card down to 60%) the page-to-page changes
drew more defects (see the README).

Every change that does not go from a page to a page is Cohort's to the bit.

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

replace('<title>Cohort — Hive</title>', '<title>Yinyang — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Cohort</a>', '<a class="back" href="index.html">&larr; Back · Yinyang</a>')

# the switch, and the slider
replace("""const COHORT = true;                                // COHORT: from page to page, the gallery is one body""",
"""const COHORT = true;                                // COHORT: from page to page, the gallery is one body
const YINYANG = true;                               // YINYANG: the two images swap by a rule of their own""")
replace("""  stagger: 0.30,""", """  stagger: 0.30,
  breathe: 0,              // YINYANG: the share of its size a card of both pages gives up at a swap's middle""")
replace("""    <div class="group"><span class="lbl">Stagger</span>""", """    <div class="group"><span class="lbl">Breathe</span>
      <input type="range" id="breathe" min="0" max="40" value="0"><span class="val" id="breatheVal">0</span>
    </div>
    <div class="group"><span class="lbl">Stagger</span>""")
replace("""bindSlider('swirl', v => { config.swirl = v / 100; document.getElementById('swirlVal').textContent = v; });""",
"""bindSlider('swirl', v => { config.swirl = v / 100; document.getElementById('swirlVal').textContent = v; });
bindSlider('breathe', v => { config.breathe = v / 100; document.getElementById('breatheVal').textContent = v; });   // YINYANG""")

# the arcs, laid as the change is laid: before the journeys' lengths and the pace read the paths
replace("""      this.seatBody(b, r, b.T);
      b.fieldAt = this.t + b.T; b.fieldRect = r;
    }""", """      this.seatBody(b, r, b.T);
      b.fieldAt = this.t + b.T; b.fieldRect = r;
    }
    if (YINYANG && COHORT && this.depth === 0 && name in PORTAL_TEMPLATES && portalWas && portalWas !== portalFocus && content.includes(portalWas)) portalArcs(this, portalWas, portalFocus);   // YINYANG: the two images swing round each other""")
replace("""// COHORT: where the open page's gallery is: its cards' seats' centroid, by area""",
"""// YINYANG: the two images of a change from page to page swing round each
// other: both paths bent the same way about their chords, so the two pass
// side by side, as yin and yang turn. Bent just as wide as they must be to
// pass clear (their seeds as far apart as their two half sides, at the sizes
// the change's clock gives them), and no wider than a chord's length off it,
// about a half circle, nor than keeps both arcs on the page. They turn the way
// that needs the lesser bend. The cards of both pages are marked to
// breathe for this change (see placeSeeds).
function portalArcs(h, A, B) {
  if (!A.path || !B.path || !A.journey || !B.journey) return;
  const N = 100, U = h.PW * h.PH, size = (b, p) => Math.sqrt(Math.max(0, b.claim0 + (b.claimTarget - b.claim0) * p) * U);
  const ctl = (P, k, sg) => { const dx = P.ex - P.sx, dy = P.ey - P.sy; return [(P.sx + P.ex) / 2 - dy * k * sg, (P.sy + P.ey) / 2 + dx * k * sg]; };
  const at = (P, c, p) => { const u = 1 - p; return [u * u * P.sx + 2 * u * p * c[0] + p * p * P.ex, u * u * P.sy + 2 * u * p * c[1] + p * p * P.ey]; };
  const clear = (k, sg) => {
    const ca = ctl(A.path, k, sg), cb = ctl(B.path, k, sg); let worst = Infinity, off = 0;
    for (let i = 0; i <= N; i++) {
      const p = i / N, a = at(A.path, ca, p), b = at(B.path, cb, p);
      worst = Math.min(worst, Math.hypot(a[0] - b[0], a[1] - b[1]) - (size(A, p) + size(B, p)) / 2);
      for (const q of [a, b]) off += Math.max(0, -q[0], q[0] - h.W, -q[1], q[1] - h.H);
    }
    return { worst, off };
  };
  let best = null;
  for (const sg of [h.swirlSign, -h.swirlSign]) {
    let cap = 1;   // the arcs stay on the page: a seed cannot leave it
    if (clear(1, sg).off > 0) { let a = 0, z = 1; for (let it = 0; it < 30; it++) { const m = (a + z) / 2; if (clear(m, sg).off > 0) z = m; else a = m; } cap = a; }
    let lo = 0, hi = cap;
    if (clear(0, sg).worst >= 0) hi = 0;
    else if (clear(hi, sg).worst >= 0) for (let it = 0; it < 30; it++) { const m = (lo + hi) / 2; if (clear(m, sg).worst >= 0) hi = m; else lo = m; }
    const r = clear(hi, sg), cand = { sg, k: hi, ok: r.worst >= 0, off: r.off };
    if (!best || (cand.ok && !best.ok) || (cand.ok === best.ok && (cand.k < best.k - 1e-9 || (Math.abs(cand.k - best.k) <= 1e-9 && cand.off < best.off)))) best = cand;
  }
  for (const b of [A, B]) { if (best.k > 0) { const c = ctl(b.path, best.k, best.sg); b.path.cx = c[0]; b.path.cy = c[1]; } b.journey.yin = true; }
  for (const q of h.bodies) if (q !== A && q !== B && !q.isVoid && !q.isSelf && !q.leaving && q.rect) q.breatheAt = h.serial;
}
// COHORT: where the open page's gallery is: its cards' seats' centroid, by area""")

# no handover where they pass: the arcs keep them clear
replace("""    if (im > 0 && im < N && dm < (size(H0) + size(H1)) / 2) pm = p;""",
"""    if (!YINYANG && im > 0 && im < N && dm < (size(H0) + size(H1)) / 2) pm = p;   // YINYANG: no handover; the arcs keep them clear""")

# right of way
replace("""          const a=this.mfFreedom(A), b=this.mfFreedom(B);""",
"""          const yA = A.journey && A.journey.yin && A.progress < 1, yB = B.journey && B.journey.yin && B.progress < 1;   // YINYANG: the images swapping have right of way: they push the cards and are not pushed
          const a = yA && !yB ? 0 : this.mfFreedom(A), b = yB && !yA ? 0 : this.mfFreedom(B);""")

# breathing
replace("""      s.claim = b.wall ? 0 : b.claim * hover;""",
"""      s.claim = b.wall ? 0 : b.claim * hover * (b.breatheAt === this.serial && this.depth === 0 ? 1 - config.breathe * (this.seaE || 0) : 1);   // YINYANG: a card of both pages breathes on the change's clock, by the slider's share""")

out = ROOT / 'yinyang.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
