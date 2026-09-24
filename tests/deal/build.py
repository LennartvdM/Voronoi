"""Build Deal from Cue: the cells are dealt to the stage as cards, and the pen closes over the gap.

Cue's story, stage, blurb and flights, less the niche. On Cue a cell that went
out to the stage held its slot of the pen open, a niche of whitespace, until
it came home; with the cells flying as cards the niche did nothing for the
flight, and a dark gap in the pen asked what went there. On Deal the pen is
always whole. Its slots are still laid once for the story, one for every cell,
by the bento's halving; a slot whose cell is out is taken by its sibling in
that halving, the half beside it stretched over both, so only the cells beside
the gap move, and only across it. When the card comes home the half gives its
ground back. Everything else is Cue's.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cue.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'e23ede652562c50bb7fddc7c53bc00a81bcaf2fe0d7357e1f733941780fa48ef'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

def replace_span(start, end, new):
    """Replace the text from `start` through `end` (both unique, end after start)."""
    global s
    assert s.count(start) == 1 and s.count(end) == 1, (start[:60], end[:60])
    i = s.index(start); j = s.index(end, i) + len(end)
    s = s[:i] + new + s[j:]

replace('<title>Cue — Hive</title>', '<title>Deal — Hive</title>')
replace('''&larr; Back · Cue</a>''', '''&larr; Back · Deal</a>''')
replace(''' · Cue: the same story, every slide a scene change of the engine's own · click a hero or Escape for home</span>''',
        ''' · Deal: the same story, the cells dealt to the stage as cards · click a hero or Escape for home</span>''')
replace('''      <button class="scene-btn" data-scene="cue">Cue</button>''',
        '''      <button class="scene-btn" data-scene="cue">Deal</button>''')

# --- the pen: always whole ------------------------------------------------------
replace('''// them: nobody is told where to go. The cluster is a revolver in a pen. Its
// slots are laid once for the story, a slot for every cell, and a cell that
// goes out holds its slot open, a niche of whitespace in the pen; a cell
// coming back takes the open niche nearest it, and every other cell of the
// cluster keeps its slot. So a cell comes and goes through a gap, the cells
// around it give a little as the gap opens and closes, and nothing else in
// the pen moves. A cell on the stage''', '''// them: nobody is told where to go. The cluster is a revolver in a pen. Its
// slots are laid once for the story, a slot for every cell, and the pen is
// always whole: a slot whose cell is out is taken by the cells beside it
// (see cuePen), and given back when the cell comes home, to its own slot.
// Every other cell of the cluster keeps its slot. A cell on the stage''')

replace('''function cueSlots(C, R, n, W, H) { return cueBento(cueLattice(C, R)(W < H ? TELL2_PHONE.cluster : CUE_CLUSTER), n, W / C, H / R); }''',
        '''function cueSlots(C, R, n, W, H) { return cueBento(cueLattice(C, R)(W < H ? TELL2_PHONE.cluster : CUE_CLUSTER), n, W / C, H / R); }
// DEAL: THE PEN CLOSES OVER THE GAP. The bento again, with only the slots
// whose cells are home: at a halving with one half empty, the other half takes
// the whole, its own halvings stretched across it as they were, so the cells
// that close the gap are the ones beside it, and they only stretch. A slot
// that is out is null. A cell of the pen is seated at its own slot's heart,
// whatever its rectangle: it grows into a gap and gives it back where it
// stands, and nothing in the pen travels (cueSeated).
function cuePen(r, n, sx, sy, home, id = 1, at = 0) {
  if (n <= 0) return [];
  if (n === 1) return [home(at) ? r : null];
  const r6 = v => Math.round(v * 1e6) / 1e6, a = Math.max(1, Math.min(n - 1, Math.round(n * (0.38 + 0.24 * hash01(id, 61))))), f = Math.max(0.2, Math.min(0.8, a / n + 0.16 * (hash01(id, 62) - 0.5)));
  const across = (r[2] - r[0]) * sx >= (r[3] - r[1]) * sy, cut = across ? r6(r[0] + (r[2] - r[0]) * f) : r6(r[1] + (r[3] - r[1]) * f);
  const A = across ? [r[0], r[1], cut, r[3]] : [r[0], r[1], r[2], cut], B = across ? [cut, r[1], r[2], r[3]] : [r[0], cut, r[2], r[3]];
  const any = (lo, m) => { for (let s = lo; s < lo + m; s++) if (home(s)) return true; return false; };
  const stretch = (q, from) => q && [r6(r[0] + (q[0] - from[0]) * (r[2] - r[0]) / (from[2] - from[0])), r6(r[1] + (q[1] - from[1]) * (r[3] - r[1]) / (from[3] - from[1])), r6(r[0] + (q[2] - from[0]) * (r[2] - r[0]) / (from[2] - from[0])), r6(r[1] + (q[3] - from[1]) * (r[3] - r[1]) / (from[3] - from[1]))];
  const inA = any(at, a), inB = any(at + a, n - a);
  if (inA && !inB) return cuePen(A, a, sx, sy, home, 2 * id, at).map(q => stretch(q, A)).concat(new Array(n - a).fill(null));
  if (inB && !inA) return new Array(a).fill(null).concat(cuePen(B, n - a, sx, sy, home, 2 * id + 1, at + a).map(q => stretch(q, B)));
  return cuePen(A, a, sx, sy, home, 2 * id, at).concat(cuePen(B, n - a, sx, sy, home, 2 * id + 1, at + a));
}
function cueSeated(pen, slots) { return pen.map((q, s) => { if (!q) return null; const r = q.slice(), o = slots[s]; r.reelSeed = [(o[0] + o[2]) / 2, (o[1] + o[3]) / 2]; return r; }); }''')

replace('''// the pen, cut along their edges (Tell II's cut). An empty place is a piece
// of its own, and so is an open niche, so a slide changes only the pieces a
// cell lands in or leaves.''', '''// the pen, cut along their edges (Tell II's cut). An empty place is a piece
// of its own, so a slide changes only the pieces a cell lands in or leaves.''')

replace_span('''// A slide's page with the niches it names (by default the last slots): the''',
             '''cast: stage.length, slots, niches: open };
}''', '''// A slide's page with the slots it names out (by default the last): the
// stage's places first, then the pen's cells that are home, closed over the
// slots that are out, then the whitespace
function cuePage(k, C, R, n, W, H, out) {
  const places = cuePlaces(k).slice(0, Math.max(0, n - 1)), L = cueLattice(C, R), stage = places.map(p => L(tell2Place(p, W, H))), slots = cueSlots(C, R, n, W, H);
  const gone = out || slots.map((r, s) => s).slice(slots.length - places.length), pen = cueSeated(cuePen(L(W < H ? TELL2_PHONE.cluster : CUE_CLUSTER), n, W / C, H / R, s => !gone.includes(s)), slots);
  return { content: stage.concat(pen.filter(Boolean)), voids: cueWhitespace(C, R, W, H, places, n), cast: stage.length, slots, out: gone, pen };
}''')

replace('''// left take the nearest cells not benched; a cell in (or bound for) a slot
// keeps it; and the cells left, the ones coming home, go to their own
// niches. A cell is bound for its rectangle, so a change interrupted
// is planned from where everyone was going.''', '''// left take the nearest cells not benched; a cell of the pen keeps its slot;
// and the cells left, the ones coming home, go to their own slots. A cell is
// bound for its rectangle, so a change interrupted is planned from where
// everyone was going.''')
replace('''  slots.forEach((r, s) => { const b = cells.find(b => !used.has(b) && bound(b, r)); if (b) { slot[s] = b; used.add(b); } });
  // a cell coming home goes to its own niche, held open for it since it left
  // (at the front of the pen, where the nearest cell goes out from); a cell
  // whose niche is gone takes the open niche nearest it
  let home = cells.filter(b => !used.has(b));
  for (const b of home) if (b.cueHome !== undefined && b.cueHome < slots.length && !slot[b.cueHome]) slot[b.cueHome] = b;
  home = home.filter(b => !slot.includes(b));''', '''  // a cell of the pen, and a cell coming home, has its own slot, the one it
  // was dealt from; a cell that has none (the story's first slide) takes the
  // free slot nearest it
  for (const b of cells) if (!used.has(b) && b.cueHome !== undefined && b.cueHome < slots.length && !slot[b.cueHome]) { slot[b.cueHome] = b; used.add(b); }
  const home = cells.filter(b => !used.has(b));''')
replace('''  slot.forEach((b, s) => { if (b) b.cueHome = s; });   // its niche, for when it goes out''',
        '''  slot.forEach((b, s) => { if (b) b.cueHome = s; });   // its slot, for when it comes home''')

replace_span('''// THE PEN IS SOLVED WHOLE, AND A NICHE IS HELD FROM ITS EDGES.''',
             '''  return { content: page.content, voids: page.voids, cast: cast.length };
}''', '''// THE PAGE: the stage's places, the pen closed over the slots that are out,
// and the whitespace, held the way Portal holds it. The pen is one pocket, its
// cells solved together as a cell of the pen always is.
const cueCache = new Map();
function cueScene(h, n) {
  if (!cue) return null;
  const cells = h.bodies.filter(b => !b.isVoid && !b.leaving && !b.isSelf), p = cuePlan(h, cue.k, cells);
  const cast = p.place.map((b, j) => j).filter(j => p.place[j]), places = cast.map(j => p.names[j]);
  const pen = cueSeated(cuePen(cueLattice(h.COLS, h.ROWS)(h.W < h.H ? TELL2_PHONE.cluster : CUE_CLUSTER), n, h.W / h.COLS, h.H / h.ROWS, s => !!p.slot[s]), p.slots);
  const key = [h.COLS, h.ROWS, h.W, h.H, n, places.join(','), pen.map(q => q ? 1 : 0).join('')].join('|');
  let page = cueCache.get(key);
  if (!page) {
    page = portalDecorate(cast.map(j => p.stage[j]).concat(pen.filter(Boolean)), cueWhitespace(h.COLS, h.ROWS, h.W, h.H, places, n), h.W, h.H, h.COLS, h.ROWS);
    page.diag = computeDiagram(page.seeds, page.weights, [[0, 0], [h.W, 0], [h.W, h.H], [0, h.H]]);
    cueCache.set(key, page); if (cueCache.size > 24) cueCache.delete(cueCache.keys().next().value);
  }
  const owner = cast.map(j => p.place[j]).concat(p.slot.filter(Boolean));
  cue.prevOn = cue.on.slice();
  for (const b of cells) b.cueFrom = b.rect ? b.rect.slice(0, 4) : null;   // where it was, for the size a flight starts at
  cue.homeCell = new Map(); owner.forEach((b, i) => { if (i < cast.length) return; const c = page.diag.cells[i]; if (c && c.pts && c.pts.length >= 3) cue.homeCell.set(b, c.pts); });   // the cell of the pen a cell coming home melts into
  cue.slotOf = new Map(owner.map((b, i) => [b, i])); cue.on = cast.map(j => p.place[j]);
  cue.penWas = cue.pen; cue.pen = pen.filter(Boolean);   // the pen's rectangles, this page's and the last
  for (const b of cells) b.cueStay = p.kept.has(b) || b.pin > 0;   // the cast that stays holds still, and so does a card in the pen whose rectangle stays
  return { content: page.content, voids: page.voids, cast: cast.length };
}''')

# THE PEN CLOSES AT THE PACE OF THE CARD. A cell of the pen that closes a gap
# grows into it as the card that left it clears it, and a cell that gives a
# slot back holds it until the card coming home is within reach of it and
# gives it back as the card comes in: Cue's niche opened and closed on the
# card's ledger in just this way. On the engine's own clock the cell grew
# round a card still in the slot and was flung as the card let go.
replace('''function cueFlyers(h, content) {''', '''// the card a cell of the pen closes the gap of, or gives a slot back to: the
// card whose slot in the pen overlaps most of what the cell's rectangle gains
// or loses; the cell's journey is then paced by where that card is
function cueTies(h, content) {
  const cards = content.filter(b => b.cueFly && !b.cueFly.stretch && b.path);
  const meet = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
  for (const b of content) {
    delete b.cueTie;
    if (b.cueFly || cue.on.includes(b) || !b.path || !b.journey || b.journey.t0 !== h.t || !b.cueFrom || rectsEqual(b.cueFrom, b.rect)) continue;
    let best = null, most = 1e-9;
    for (const c of cards) {
      const leave = c.cueFly.toCard, slot = leave ? c.cueFrom : c.rect;
      if (!slot) continue;
      const m = meet(leave ? b.rect : b.cueFrom, slot);
      if (m > most) { most = m; best = { card: c, grow: leave, at: leave ? cueClearOf(h, c, slot) : cueNear(h, c, slot) }; }
    }
    if (best) b.cueTie = best;
    // it changes size as a card: out of the auction, from the rectangle it
    // is drawn at to its new one, and pinned there, a wall, as it gets there
    const px = r => [r[0] * h.PW, r[1] * h.PH, r[2] * h.PW, r[3] * h.PH];
    b.cueFly = { stretch: true, from: b.cueStretchCur || px(b.cueFrom), to: px(b.rect) };
  }
}
// how far a tied cell is on its journey: by where its card is on its path
function cueTieProgress(b, u) {
  const t = b.cueTie, c = t.card, p = c.path;
  if (!p || c.leaving) return easeInOutCubic(u);
  const dS = Math.hypot(c.x - p.sx, c.y - p.sy), dE = Math.hypot(c.x - p.ex, c.y - p.ey), e = !c.journey && dE < 0.5 ? 1 : dS + dE > 1e-6 ? dS / (dS + dE) : 1;
  const q = t.grow ? Math.min(1, e / Math.max(0.05, t.at)) : Math.max(0, Math.min(1, (e - t.at) / Math.max(0.05, 1 - t.at)));
  return q * q * (3 - 2 * q);
}
function cueFlyers(h, content) {''')
replace('''cueAvoid(this, content); cueFlyers(this, content); for (const [v, r] of cueSeat)''',
        '''cueAvoid(this, content); cueFlyers(this, content); cueTies(this, content); for (const [v, r] of cueSeat)''')
replace('''        b.progress = easeInOutCubic(u);
        this.updateCrystal(b, t);
        // a free body's journey is only its clock: once run, it drifts on
        if (!b.leaving && !b.table && u >= 1 && b.crystal === 0) b.journey = null;''',
        '''        b.progress = b.cueTie ? cueTieProgress(b, u) : easeInOutCubic(u);   // DEAL: a cell closing a gap goes at its card's pace
        this.updateCrystal(b, t);
        // a free body's journey is only its clock: once run, it drifts on
        if (!b.leaving && !b.table && u >= 1 && b.progress >= 1 && b.crystal === 0) b.journey = null;''')

# A CARD COMING HOME LANDS A WALL, AS A CARD ON THE STAGE DOES. On Cue a card
# coming home melted into its cell of the pen, and the niche it flew into
# held the cells round it off the slot until it did. With no niche, the cell
# that gave the slot back reached right through it under the card (under a
# card a cell's weight answers to nothing), and the card, joining the
# auction, found its ground outside the pen. So it flies home to its
# rectangle of the pen, the rectangle carried with its seed, and lands
# pinned on it, a wall; the cells round it bid against its edges. It melts
# again when a change stretches it over a gap, as any wall melts before it
# goes.
replace('''  if (done && f.toCard) { b.pin = 1; b.cueFly = null; return null; }   // landed: pinned on its place, drawn as its card, it is a wall from this frame (see computeWalls)
  if (done) { b.cueFly = null; return null; }   // melted into the pen''',
        '''  if (done) { b.pin = 1; b.cueFly = null; b.cueCard = true; return null; }   // landed: pinned on its place or its rectangle of the pen, drawn as its card, it is a wall from this frame (see computeWalls)''')
replace('''  const home = f.home ? f.home.map(q => [q[0] + b.x - p.ex, q[1] + b.y - p.ey]) : null;   // carried with it too, so the blend is centred on its seed and is its home cell exactly as it arrives''',
        '''  const home = f.home ? f.home.map(q => [q[0] + b.x - p.ex, q[1] + b.y - p.ey]) : null;   // carried with it too, so the blend is centred on its seed and is its rectangle of the pen exactly as it arrives''')
replace('''  cue.homeCell = new Map(); owner.forEach((b, i) => { if (i < cast.length) return; const c = page.diag.cells[i]; if (c && c.pts && c.pts.length >= 3) cue.homeCell.set(b, c.pts); });   // the cell of the pen a cell coming home melts into''',
        '''  cue.homeCell = new Map(); owner.forEach((b, i) => { if (i < cast.length) return; const r = page.content[i], x0 = r[0] * h.PW, y0 = r[1] * h.PH, x1 = r[2] * h.PW, y1 = r[3] * h.PH; cue.homeCell.set(b, [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]); });   // the rectangle of the pen a card coming home lands on''')

# A card that has landed is its rectangle, and a wall from that frame: the
# engine makes a pinned cell a wall once its outline is its rectangle to 3%,
# and a card landing among cards still in flight is clipped by them past
# that (Tide, on the entry, by 426 px² in 419), and was left bidding for good.
# Until its next journey, it is its card.
replace('''(b.crystal >= 1 || (b.pin > 0 && this.cellIsRect(b, r)))))) {   // TELL: the story's cards bid throughout''',
        '''(b.crystal >= 1 || (b.pin > 0 && (b.cueCard || this.cellIsRect(b, r))))))) {   // CUE: a card landed is its rectangle   // TELL: the story's cards bid throughout''')
replace('''  for (const b of content) {
    const p = b.path, j = b.journey;
    if (!p || !j || j.t0 !== h.t) continue;
    const L = Math.hypot(p.ex - p.sx, p.ey - p.sy), out = cue.on.includes(b), was = b.cueFly ? cueFlyC(h, b) : 0;''',
        '''  for (const b of content) {
    const p = b.path, j = b.journey;
    if (!p || !j || j.t0 !== h.t) continue;
    delete b.cueCard;   // on its way again: a card only if it flies as one
    const L = Math.hypot(p.ex - p.sx, p.ey - p.sy), out = cue.on.includes(b), was = b.cueFly ? cueFlyC(h, b) : 0;''')

# A card of the pen that closes a gap, or gives one back, changes size as a
# card: its rectangle eases from the one it is drawn at to its new one, at its
# card's pace, out of the auction, and it is pinned there, a wall, as it gets
# there. Bidding, it wandered a few px on every change after, and the page's
# weights, which hold a pen of bidders, did not hold a bidder among walls.
replace('''function cueFlyShape(h, b) {
  const f = b.cueFly, p = b.path;''', '''function cueFlyShape(h, b) {
  const f = b.cueFly, p = b.path;
  if (f.stretch) {   // DEAL: a card of the pen changing size where it stands
    const q = Math.max(0, Math.min(1, b.progress || 0)), r = f.from.map((v, i) => v + (f.to[i] - v) * q);
    if (q >= 1 && !b.journey) { b.pin = 1; b.cueFly = null; b.cueCard = true; delete b.cueStretchCur; return null; }
    b.cueStretchCur = r;
    const pts = [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]];
    return { pieces: [pts], planes: [convexPlanes(pts)], rect: r, pts, raw: [pts] };
  }''')
replace('''    const L = Math.hypot(p.ex - p.sx, p.ey - p.sy), out = cue.on.includes(b), was = b.cueFly ? cueFlyC(h, b) : 0;''',
        '''    const L = Math.hypot(p.ex - p.sx, p.ey - p.sy), out = cue.on.includes(b), was = b.cueFly && !b.cueFly.stretch ? cueFlyC(h, b) : 0;''')

# a cell coming into the pen from off it flies: off the pen as it was, so a
# cell of the pen that stretches or shrinks where it stands does not
replace('''    const crossing = !out && b.cueFrom && !cue.slots.some(r => rectsEqual(r, b.cueFrom));   // coming into the pen from off its slots: from the stage, or from the page the story began on''',
        '''    const crossing = !out && b.cueFrom && !cue.penWas.some(r => rectsEqual(r, b.cueFrom));   // coming into the pen from off it: from the stage, or from the page the story began on''')
replace('''function cueDrop() { if (!cue) return; cue = null; for (const b of root.bodies) { delete b.cueStay; delete b.cueFly; delete b.cueFrom; delete b.cueHome; } }''',
        '''function cueDrop() { if (!cue) return; cue = null; for (const b of root.bodies) { delete b.cueStay; delete b.cueFly; delete b.cueFrom; delete b.cueHome; delete b.cueTie; delete b.cueCard; delete b.cueStretchCur; } }''')
replace('''cue = { y: 0, v: 0, k: 0, on: [], prevOn: [], slots: [], homeCell: new Map(),''',
        '''cue = { y: 0, v: 0, k: 0, on: [], prevOn: [], pen: [], penWas: [], homeCell: new Map(),''')

(ROOT / 'deal.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
