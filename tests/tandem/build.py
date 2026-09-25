"""Build Tandem from Cue: a page opens all at once.

Cue's pages (a cell clicked opens its page: its image, its text, its
gallery) opened in turns. The image grew on its own clock toward a
rectangle the other cells had not yet left, and the text's whitespace did
not open at all until the last cell crossing it was through, so the image
spread across the text's room up to the cluster, and only then did the
text wedge itself in between the two, the image giving back what it had
taken. Here the page's regions are held by their own: the image is never
bigger than the room its own rectangle has (with what it has still to leave
elsewhere), the text is as big as the room its rectangle has as soon as it
has it, and the text's whitespace makes way for the cells still crossing it,
as Cue's stage does for its travellers. So the cells leave, the text opens
behind them and the image fills its own room, all at once; and the ground
nobody bids for while the old page's whitespace closes faster than the new
one opens goes to the whitespace opening, not to the image.

Nothing else changes: without a page opened, the tick and every drawing
command are Cue's (validate.cjs).
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'cue.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '1a912f7b8242722a5beb29c16ab3c167998600d9b5611043c1309bf3c4769714'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Cue — Hive</title>', '<title>Tandem — Hive</title>')
replace('''&larr; Back · Cue</a>''', '''&larr; Back · Tandem</a>''')
replace(''' · Cue: the same story, every slide a scene change of the engine\'s own · click a hero or Escape for home</span>''',
        ''' · Cue: the same story, every slide a scene change of the engine\'s own · Tandem: a page opens all at once · click a hero or Escape for home</span>''')

# A PAGE'S REGIONS ARE HELD BY THEIR OWN. A page is an image, its text and its
# gallery, each a rectangle of the page, and on Cue each took its turn. The
# image grew on its own clock, its claim reaching its rectangle's area while
# the cells there had yet to leave it, and a cell growing past what its own
# room holds takes the room beside it: the image spread across the text's
# rectangle to the cluster. The text's whitespace waited for the last cell
# crossing it (so that nothing crossed it as a sliver) and then opened into
# the image, which gave back what it had taken. Now, every frame of a page's
# change, each region is measured on the diagram as it stands: the room its
# rectangle has, less what every other cell and whitespace (and every wall
# and card) covers of it. The image bids no more than the room its own
# rectangle has and what it has yet to leave elsewhere (not the text's
# rectangle, nor any whitespace opening, which gives way to it in its own
# rectangle); the text's whitespace, and any other whitespace opening on
# the page, bids at least the room its rectangle has. The room a region has
# only grows: nothing opens and closes again. The auction hands its ground
# out in proportion to the bids, so what nobody bids for (the old page's
# whitespace closing faster than the new one opens) would still go to
# everyone, the image most: it goes to the whitespace opening, eased over
# half a second, never past what that whitespace bids at rest. And the text's sites make way for the cells still crossing it, as
# Cue's whitespace does for its travellers: the sites in a cell's way give
# up their claim to the piece's sites clear of it, so the piece keeps its
# claim, and the cell crosses without being pressed into a sliver. The bids
# are the sites' own, set after every other rule has set them (the swell a
# journey adds among them), so what the auction is asked is what it hands.
replace('''const cueWay = Hive.prototype.placeSeeds;''', '''const TANDEM_EASE = 0.5;   // s: how fast the opening whitespace takes the ground nobody bids for
function tandemClip(P, r) {   // how much of a convex polygon lies in a rectangle, px²
  let o = P; const cl = (a, b, c) => { const n = []; for (let i = 0; i < o.length; i++) { const p = o[i], q = o[(i + 1) % o.length], dp = a * p[0] + b * p[1] - c, dq = a * q[0] + b * q[1] - c; if (dp <= 0) n.push(p); if (dp * dq < 0) { const t = dp / (dp - dq); n.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]); } } o = n; };
  cl(-1, 0, -r[0]); cl(1, 0, r[2]); cl(0, -1, -r[1]); cl(0, 1, r[3]);
  return o.length >= 3 ? Math.abs(ringArea(o)) : 0;
}
function tandemRooms(h) {
  const hero = portalFocus; if (h.depth !== 0 || cue || !hero || !hero.rect || !h.solved || !(config.scene in PORTAL_TEMPLATES)) return;
  const PA = h.PW * h.PH, px = r => [r[0] * h.PW, r[1] * h.PH, r[2] * h.PW, r[3] * h.PH];
  const regions = [{ b: hero, r: px(hero.rect) }];   // the image's rectangle, and every piece of whitespace opening
  for (const v of h.bodies) if (v.isVoid && !v.leaving && v.rect && v.table && v.table.mode === 'open') regions.push({ b: v, r: px(v.rect) });
  const occ = regions.map(() => 0), heroIn = regions.map(() => 0);
  const opening = b => b.isVoid && b.table && b.table.mode === 'open';
  const add = (b, pts) => regions.forEach((g, i) => { const a = tandemClip(pts, g.r); if (b === hero) heroIn[i] += a; if (b !== g.b && (b !== hero || i === 0) && !(i === 0 && opening(b))) occ[i] += a; });   // the image holds no room of the whitespace's, and the whitespace opening none of the image's
  h.solvedSubs.forEach((s, k) => { const c = h.solved.diagram.cells[k]; if (c) for (const pc of c.pieces || [c]) if (pc.pts && pc.pts.length >= 3) add(s.body, pc.pts); });
  for (const b of h.walls) { const r = b.wall; add(b, [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]]); }
  for (const b of h.holes) for (const pc of b.hole.pieces) add(b, pc);
  const total = b => b.subs.reduce((a, s) => a + s.claim, 0), scale = (b, want) => { const t = total(b); if (t > 0) for (const s of b.subs) s.claim *= want / t; };
  regions.forEach((g, i) => {
    const room = Math.max(0, (g.r[2] - g.r[0]) * (g.r[3] - g.r[1]) - occ[i]) / PA;
    if (i === 0) {   // the image no bigger than the room its own rectangle has, and what it has yet to leave elsewhere
      const outside = Math.max(0, (hero.paintArea || 0) - heroIn.reduce((a, m) => a + m, 0)) / PA, j = hero.journey || hero;
      j.tandemRoom = Math.max(j.tandemRoom || 0, room + outside);
      if (total(hero) > j.tandemRoom) scale(hero, Math.max(CLAIM_MIN, j.tandemRoom));
    } else {   // and the text as big as the room its rectangle has, once it has it
      const t = g.b.table; t.room = Math.max(t.room || 0, Math.min(g.b.claimTarget, room));
      const want = Math.min(t.room, g.b.claimTarget); if (total(g.b) < want) scale(g.b, want);   // never more than it bids at rest, which a page's change can lower
    }
  });
  // the ground nobody bids for is the opening whitespace's: the auction hands
  // its ground out in proportion to the bids, and what the bids leave over
  // would go to everyone, the image most, which grew across the text's room
  // whatever it bid. Eased, so a cell floating in the whitespace is not swept
  // aside as the whitespace takes it.
  if (h.ground && h.ground.length) {
    const pieces = h.ground, comp = pieces.length > 1 ? h.components(pieces) : null, pk = s => comp ? h.pocketOf(comp, pieces, s.x, s.y) : 0, k = pk(hero.subs[0]);
    let G = 0; pieces.forEach((p, pi) => { if (!comp || comp.groups[k].includes(pi)) G += Math.abs(ringArea(p)); }); G /= PA;
    let T = 0; for (const b of h.bodies) if (!b.hole && !b.wall) for (const s of b.subs) if (s.claim >= ACTIVE_MIN && pk(s) === k) T += s.claim;
    const open = regions.slice(1).map(g => g.b).filter(v => v.subs.some(s => pk(s) === k)), need = open.map(v => Math.max(0, v.claimTarget - total(v))), N = need.reduce((a, q) => a + q, 0);
    const slack = Math.min(N, Math.max(0, G - T));
    open.forEach((v, i) => {
      const t = v.table, want = slack > 1e-6 ? slack * need[i] / N : 0, dt = t.slackAt === undefined ? 0 : Math.max(0, h.t - t.slackAt);
      t.slack = t.slack === undefined ? 0 : t.slack + (want - t.slack) * (1 - Math.exp(-dt / TANDEM_EASE)); t.slackAt = h.t;
      t.slack = Math.min(t.slack, need[i]);   // and never more than it bids at rest
      if (t.slack > 1e-6) scale(v, total(v) + t.slack);
    });
  }
}
const cueWay = Hive.prototype.placeSeeds;''')
replace('''  if (this.depth !== 0 || !cue || config.scene !== 'cue') return;
  const movers = [];''', '''  const page = this.depth === 0 && !cue && config.scene in PORTAL_TEMPLATES;   // TANDEM: and on a page, where the text makes way for the cells crossing it
  if (!page && (this.depth !== 0 || !cue || config.scene !== 'cue')) return;
  const movers = [];''')
replace('''  if (!movers.length) return;
  for (const v of this.bodies) {''', '''  if (!movers.length) { if (page) tandemRooms(this); return; }
  for (const v of this.bodies) {''')
replace('''v.table && v.table.mode === 'open' && v.progress < 1) continue;   // a piece opening keeps its ledger's clock''',
        '''!page && v.table && v.table.mode === 'open' && v.progress < 1) continue;   // a piece opening keeps its ledger's clock (TANDEM: on a page it opens by its room, and makes way)''')
replace('''    v.subs.forEach((q, i) => { q.claim *= f[i] > 0.98 ? g : f[i]; });
  }
};''', '''    v.subs.forEach((q, i) => { q.claim *= f[i] > 0.98 ? g : f[i]; });
  }
  if (page) tandemRooms(this);   // TANDEM: a page's regions held by their own
};''')

(ROOT / 'tandem.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
