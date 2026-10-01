"""Build Cohort from Amoeba: from page to page, the gallery is one body.

On Amoeba every page opened on the side it was clicked from, so on 48 of the
56 changes between kinds of page the gallery crossed the screen, through the
images, and its cards found their new seats among each other on the way. The
image the click opened grew on the change's clock from where it stood, in the
gallery, shoving the cards; the image it closed kept its size on the same
clock, a ball in the middle of the page that the new one had to get past.

Here a change from page to page knows what the pages share: a gallery, and an
image that changes hands.
- The gallery keeps its side. The next page opens the way that leaves its
  gallery nearest where this one's is (its seats' centroid, by area); a tie
  opens it on the side clicked, as before.
- An image is a card while it is in the gallery. The gallery is its cards'
  rectangles, each on its way from its old seat to its new one on the
  change's clock. The clicked card grows only once its card no longer
  touches them; the image it closes has shrunk to its card by the time its
  card touches them.
- The two images hand over where they pass: if they would touch at their
  closest on the way, at the sizes the clock gives them, the old image is a
  card by then and the new one grows only after.
- Each image's size runs on its window as a smooth step, so no window starts
  or stops with a step in its rate.
- While the images change hands, ground nobody claims is the sea's. The
  auction hands the ground out in proportion to the bids, so what the closing
  image gave up went back to everyone, and to the closing image most: on
  Amoeba it was drawn far bigger than it bid, a ball the opening image had to
  get past. Now every cell is drawn the size it claims, and the closing image
  is seen to give way.

Everything else is Amoeba's, and every change that does not go from a page to
a page is Amoeba's to the bit.

The header carries no captions.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'amoeba.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '74cbb39341fdbc8ec4650fa1831cc38ac7aaa90535c4729466df2e2a0e5a56b1'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Amoeba — Hive</title>', '<title>Cohort — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Amoeba</a>', '<a class="back" href="index.html">&larr; Back · Cohort</a>')

# the page before, known while the next is laid
replace("""let portalFocus = null;                             // the body a page is open on; null at home""",
"""let portalFocus = null;                             // the body a page is open on; null at home
const COHORT = true;                                // COHORT: from page to page, the gallery is one body
let portalWas = null;                               // COHORT: the body the page before was open on, while a change from page to page is laid""")
replace("""    portalFocus = b; portalEnter(portalKind(b), { x, y });""",
"""    // COHORT: from a page, the gallery is a body already: the next page opens
    // the way that leaves its gallery nearest where this one's is (its seats'
    // centroid, by area), and on the side clicked if both ways are as near
    const was = COHORT && portalFocus && config.scene in PORTAL_TEMPLATES ? portalGalleryAt(root) : null;
    if (was && W >= H) {
      const n = root.bodies.filter(q => !q.isVoid && !q.isSelf && !q.leaving).length, flip0 = portalFlip;
      const away = f => { portalFlip = f; const g = portalPage(T, root.COLS, root.ROWS, n, W, H).content.slice(1); let X = 0, Y = 0, A = 0; for (const r of g) { const a = rectArea(r); X += (r[0] + r[2]) / 2 * a; Y += (r[1] + r[3]) / 2 * a; A += a; } return Math.hypot(X / A * root.PW - was[0], Y / A * root.PH - was[1]); };
      const d0 = away(false), d1 = away(true);
      portalFlip = Math.abs(d0 - d1) < 1 ? flip0 : d1 < d0;
    }
    portalWas = portalFocus && config.scene in PORTAL_TEMPLATES ? portalFocus : null; portalFocus = b; portalEnter(portalKind(b), { x, y }); portalWas = null;""")
replace("""function portalHome(origin) { portalFocus = null; portalEnter('bento', origin); }""",
"""function portalHome(origin) { portalFocus = null; portalEnter('bento', origin); }
// COHORT: where the open page's gallery is: its cards' seats' centroid, by area
function portalGalleryAt(h) {
  let X = 0, Y = 0, A = 0;
  for (const q of h.bodies) if (!q.isVoid && !q.isSelf && !q.leaving && q !== portalFocus && q.rect && !q.reelParked) { const r = q.rect, a = rectArea(r); X += (r[0] + r[2]) / 2 * a; Y += (r[1] + r[3]) / 2 * a; A += a; }
  return A > 0 ? [X / A * h.PW, Y / A * h.PH] : null;
}
// COHORT: from page to page the two images change places with a card of the
// gallery, and the gallery is a body: its cards' rectangles, each on its way
// from its old seat to its new one on the change's clock. The image the click
// opens grows only once its card no longer touches the gallery; the image it
// closes has shrunk to its card by the time its card touches it. And the two
// hand over where they pass: if they would touch at their closest on the way,
// at the sizes the clock gives them, the old image is a card by then and the
// new one grows only after. Each is a window on its journey's progress, found
// once along the paths.
function portalWindows(h, content, was, rectOf) {
  const H0 = portalWas, H1 = portalFocus, on = r => { const cx = (r[0] + r[2]) / 2, cy = (r[1] + r[3]) / 2; return cx > 0 && cx < h.COLS && cy > 0 && cy < h.ROWS; };
  const G = content.filter(b => b !== H0 && b !== H1 && was.get(b) && rectOf.get(b) && on(was.get(b)) && on(rectOf.get(b)));
  if (!G.length) return;
  const px = r => [r[0] * h.PW, r[1] * h.PH, r[2] * h.PW, r[3] * h.PH], lerp = (a, z, p) => a.map((v, i) => v + (z[i] - v) * p);
  const Gr = G.map(b => [px(was.get(b)), px(rectOf.get(b))]), E = 1e-6, N = 200;
  const at = (b, p) => { const P = b.path, u = 1 - p; return [u * u * P.sx + 2 * u * p * P.cx + p * p * P.ex, u * u * P.sy + 2 * u * p * P.cy + p * p * P.ey]; };
  const touches = (c, w, hh, p) => Gr.some(([a, z]) => { const r = lerp(a, z, p); return Math.min(c[0] + w / 2, r[2]) - Math.max(c[0] - w / 2, r[0]) > -E && Math.min(c[1] + hh / 2, r[3]) - Math.max(c[1] - hh / 2, r[1]) > -E; });
  let pm = 1;   // where the two pass: their seeds' closest approach on the change's clock
  if (H0.journey && H0.path && H1.journey && H1.path) {
    let dm = Infinity, im = 0; for (let i = 0; i <= N; i++) { const a = at(H0, i / N), c = at(H1, i / N), d = Math.hypot(a[0] - c[0], a[1] - c[1]); if (d < dm) { dm = d; im = i; } }
    const p = im / N, size = b => Math.sqrt(Math.max(0, b.claim0 + (b.claimTarget - b.claim0) * p) * h.PW * h.PH);
    if (im > 0 && im < N && dm < (size(H0) + size(H1)) / 2) pm = p;
  }
  if (H1.journey && H1.path && was.get(H1)) {
    const r = px(was.get(H1)), w = r[2] - r[0], hh = r[3] - r[1]; let i = 0;
    while (i < N && touches(at(H1, i / N), w, hh, i / N)) i++;
    H1.journey.win = [Math.max(i / N, pm < 1 ? pm : 0), 1];
  }
  if (H0.journey && H0.path && rectOf.get(H0)) {
    const r = px(rectOf.get(H0)), w = r[2] - r[0], hh = r[3] - r[1]; let i = 1;
    while (i < N && !touches(at(H0, i / N), w, hh, i / N)) i++;
    H0.journey.win = [0, Math.max(1 / N, Math.min(i / N, pm))];
  }
}""")
replace("""    const rectOf = new Map();
    content.forEach((b, k) => rectOf.set(b, spec.content[gotS[k]]));""",
"""    const rectOf = new Map(), wasRect = new Map(content.map(b => [b, b.rect]));   // COHORT: where each sat on the page before
    content.forEach((b, k) => rectOf.set(b, spec.content[gotS[k]]));""")
replace("""    for (const b of pending) this.retireBody(b, 0.8, tOf(b));
    if (name === 'cue' && cue) {""",
"""    if (COHORT && this.depth === 0 && name in PORTAL_TEMPLATES && portalWas && portalWas !== portalFocus && content.includes(portalWas)) portalWindows(this, content, wasRect, rectOf);   // COHORT: an image is a card while it is in the gallery
    for (const b of pending) this.retireBody(b, 0.8, tOf(b));
    if (name === 'cue' && cue) {""")
replace("""        b.claim = b.claim0 + (b.claimTarget - b.claim0) * b.progress;""",
"""        const w = b.journey.win, q = w ? S3((b.progress - w[0]) / Math.max(1e-6, w[1] - w[0])) : b.progress;   // COHORT: an image's size on its window, which starts and stops without a step in its rate
        b.claim = b.claim0 + (b.claimTarget - b.claim0) * q;""")

# COHORT: while the images change hands, ground nobody claims is the sea's
replace("""  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }""",
"""  seaOpen() { return this.depth === 0 && !tell && !tell2 && !cue; }
  // COHORT: WHILE THE IMAGES CHANGE HANDS, GROUND NOBODY CLAIMS IS THE SEA'S.
  // The auction hands out the ground in proportion to the bids, so what the
  // closing image gives up went back to everyone, and to the closing image
  // most: it was drawn far bigger than it bid, and the opening one had to get
  // past it. From page to page, while either image is on its way, the sea
  // claims whatever the cells and the whitespace leave unclaimed, and every
  // cell is drawn the size it claims.
  seaFreeOn() { return COHORT && this.seaOpen() && this.bodies.some(b => b.journey && b.journey.win && b.progress < 1); }""")
replace("""    let tSum = seaClaim; for (const c of claims) tSum += c;
    const seaIn = seaClaim >= ACTIVE_MIN;   // AMOEBA: a sea too small to see appear stays out, as a seed does""",
"""    const free = this.seaFreeOn() ? u => Math.max(0, u) : () => 0;   // COHORT: ground nobody claims, the sea's
    if (!(this.domainPoly && !domain)) { let c = seaClaim; for (const q of claims) c += q; seaClaim += free(domainArea / (this.PW * this.PH) - c); }
    let tSum = seaClaim; for (const c of claims) tSum += c;
    const seaIn = seaClaim >= ACTIVE_MIN;   // AMOEBA: a sea too small to see appear stays out, as a seed does""")
replace("""        const gs = idx.map(i => seeds[i]), gc = idx.map(i => claims[i]), gw = idx.map(i => active[i].w);
        const sol = idx.length === 1 && !(seaK[k] >= ACTIVE_MIN)""",
"""        const gs = idx.map(i => seeds[i]), gc = idx.map(i => claims[i]), gw = idx.map(i => active[i].w);
        seaK[k] += free(ga / (this.PW * this.PH) - seaK[k] - gc.reduce((a, q) => a + q, 0));   // COHORT: each pocket's ground nobody claims
        const sol = idx.length === 1 && !(seaK[k] >= ACTIVE_MIN)""")
replace("""      let tSum = seaK[k]; for (const s of idx) tSum += claimOf(s);""",
"""      let tSum = seaK[k]; for (const s of idx) tSum += claimOf(s);
      if (this.seaFreeOn()) { const f = Math.max(0, ga / (this.PW * this.PH) - tSum); seaK[k] += f; tSum += f; }   // COHORT: as in the main auction""")

out = ROOT / 'cohort.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
