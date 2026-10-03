"""Build Dough from Facet: the hive wets the pan.

Since Membrane a liquid cell has kept its plan its own radius clear of the
screen, so the hive floats clear of the screen as one rounded body: its reach
can touch an edge at a point and never fills a corner. The owner sees a globule
that avoids the corners, and a waste of the screen. A well hydrated dough does
the opposite: it spreads to the pan's walls and into its corners, and its free
surface is rounded only where it faces the air.

- The screen is the pan. A liquid cell's plan goes where the layout sends it,
  to the edge if the layout does; nothing holds it a radius clear. Its reach
  is cut by the pan, and to hold its claim it grows, so a cell pressed against
  a wall spreads along it and into the corner, as dough does.
- The pan is the same with a wall in it as without. The auction's ground was
  cut from the page whenever a wall was in the frame (a reel's parked cards, on
  every page's change) and was the box the cells may overflow into otherwise,
  so cells overflowed on the home scenes and never on a page. Now it is the
  box less the walls, on every change of the page's own (a story choreographs
  its own whitespace, and keeps Facet's ground).
- The mass is conserved. From page to page the closing image shrinks exactly
  as the opening one grows, each over its whole journey, so what the cells and
  the whitespace hold adds up to the pan at every instant; nothing is free
  ground, and the two images press on each other as they pass. Cohort shrank
  the one to a card before their closest approach and grew the other only
  after, which left the page to the sea in between: at the middle of Dune to
  Jazz the cells held 13 of 96 slots.
- Scope. The page's own changes. The stories and the fields inside cells are
  Facet's.

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

replace('<title>Facet — Hive</title>', '<title>Dough — Hive</title>')
replace('<a class="back" href="index.html">&larr; Back · Facet</a>', '<a class="back" href="index.html">&larr; Back · Dough</a>')
replace("""const FACET = true;""", """const FACET = true;
const DOUGH = true;                                 // DOUGH: the hive wets the pan: nothing holds a liquid cell clear of the screen, and the ground is the box less the walls, always""")

# the swarm no longer feels the screen
replace("""        if (this.depth === 0 && b.seaLiquid > 0 && !b.isVoid && !b.reelPinned) {   // MEMBRANE: a liquid cell keeps its plan its own radius clear of the screen""",
"""        if (!DOUGH && this.depth === 0 && b.seaLiquid > 0 && !b.isVoid && !b.reelPinned) {   // MEMBRANE: a liquid cell keeps its plan its own radius clear of the screen   // DOUGH: it does not: the screen is the pan, and a cell pressed against it spreads along it""")

# the ground is the box less the walls, as it is without them
replace("""    if (!poly) pieces = rects.length ? coverRects(0, 0, this.W, this.H, rects) : [[[0, 0], [this.W, 0], [this.W, this.H], [0, this.H]]];""",
"""    const [X0, Y0, X1, Y1] = DOUGH && this.seaOpen() ? this.plBox() : [0, 0, this.W, this.H];   // DOUGH: the pan is the same with a wall in it as without: the box the cells may overflow into, less the walls (on the page's own changes; a story choreographs its own)
    if (!poly) pieces = rects.length ? coverRects(X0, Y0, X1, Y1, rects) : [[[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]];""")
replace("""    if (!pieces) pieces = [[[0, 0], [this.W, 0], [this.W, this.H], [0, this.H]]];""",
"""    if (!pieces) { const [X0, Y0, X1, Y1] = DOUGH && this.seaOpen() ? this.plBox() : [0, 0, this.W, this.H]; pieces = [[[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]]]; }   // DOUGH: as the main auction's""")

# the mass is conserved: the images hand over as they go, and nothing is free ground
replace("""function portalWindows(h, content, was, rectOf) {
  const H0 = portalWas, H1 = portalFocus, on = r => { const cx = (r[0] + r[2]) / 2, cy = (r[1] + r[3]) / 2; return cx > 0 && cx < h.COLS && cy > 0 && cy < h.ROWS; };""",
"""function portalWindows(h, content, was, rectOf) {
  const H0 = portalWas, H1 = portalFocus, on = r => { const cx = (r[0] + r[2]) / 2, cy = (r[1] + r[3]) / 2; return cx > 0 && cx < h.COLS && cy > 0 && cy < h.ROWS; };
  // DOUGH: THE MASS IS CONSERVED. The closing image shrinks exactly as the
  // opening one grows, each on its whole journey, so what the cells and the
  // whitespace hold adds up to the pan at every instant, and the two images
  // press on each other as they pass, as dough does. Cohort's windows, which
  // emptied the page between the one and the other, are not taken.
  if (DOUGH) { if (H0.journey) H0.journey.win = [0, 1]; if (H1.journey) H1.journey.win = [0, 1]; return; }""")
replace("""  seaFreeOn() { return COHORT && this.seaOpen() && this.bodies.some(b => b.journey && b.journey.win && b.progress < 1); }""",
"""  seaFreeOn() { return !DOUGH && COHORT && this.seaOpen() && this.bodies.some(b => b.journey && b.journey.win && b.progress < 1); }   // DOUGH: nothing is free ground: the bids add up to the pan""")

out = ROOT / 'dough.html'
out.write_bytes(s.encode())
print(out, hashlib.sha256(s.encode()).hexdigest())
