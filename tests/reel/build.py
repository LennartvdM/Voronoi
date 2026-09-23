"""Build Reel from Portal: a page's gallery is an endless strip to scroll.

The gallery region a page gives its cards becomes a window on a strip of
slots that runs on its own, an upward waterfall: the wheel pushes the flow
along or holds it back, a drag takes the strip in hand and a flick sends it
on, the speed easing back to the flow's. The visible bands of the strip are
the page's own layout; the bands beyond it follow a pattern that keeps the
cards varied.
Every card is a root cell as before, one site: its rectangle is its slot
clipped by the region, so a card leaves as a sliver and arrives as one, and
the page's rest diagram is authored again at every scroll step and handed to
every body at once, weights included, so the auction has nothing to chase
and the whitespace's mirrors follow the cards without a slew. The strip's
cards hold a window of consecutive slots that always covers the bands under
the region; a card past one end takes the slot beyond the other. As many
cards as the widest window needs beyond the page's own are made up for the
page and wait as specks in a sliver at the strip's end no whitespace
touches; they retire on the next change, so the page keeps its count.
Without a click, the tick, the picture and every drawing command are
Portal's (validate.cjs).
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'portal.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '63bc171f373b706256b916dcb20fec25ba060eeeda5de1a3bc07492040eda550'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Portal — Hive</title>', '<title>Reel — Hive</title>')
replace('&larr; Back · Portal</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · click the image again for home</span>',
        '&larr; Back · Reel</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · its gallery flows: scroll, drag or flick it · click the image again for home</span>')

# --- the strip: a page's gallery cards are the visible bands of an endless strip
replace('''  const cards = [];
  regions.forEach((g, i) => cards.push(...portalCards(g, counts[i])));
  const voids = [];
  if (T.text) { const t = L(T.text); t.portalText = true; t.portalRules = T.rules; voids.push(t); }
  for (const f of T.margins || []) voids.push(L(f));
  return { content: [hero, ...cards], voids };
}''', '''  const cards = [], strips = regions.map((g, i) => reelStrip(g, counts[i], W, H, C, R));
  for (const st of strips) for (let p = 0; p < st.k; p++) cards.push(st.rect(st.slot(p), 0));
  const voids = [];
  if (T.text) { const t = L(T.text); t.portalText = true; t.portalRules = T.rules; voids.push(t); }
  for (const f of T.margins || []) voids.push(L(f));
  return { content: [hero, ...cards], voids, strips };
}
// REEL. A page's gallery is a strip of slots sliding under the region it was
// given: bands of cards along the strip, the visible bands the page's own
// layout, the bands beyond it a pattern that keeps the cards varied. A
// strip runs down a tall region and across a wide one. Indices 0.. run down
// the strip from the region's start and -1.. up it; a card's slot is its
// band and its place across the band.
function reelStrip(g, k, W, H, C, R) {
  const PW = W / C, PH = H / R, wpx = (g[2] - g[0]) * PW, hpx = (g[3] - g[1]) * PH;
  const vertical = hpx >= 0.8 * wpx;
  const U = vertical ? g[2] - g[0] : g[3] - g[1], L = vertical ? g[3] - g[1] : g[2] - g[0];
  const uPx = vertical ? PW : PH, tPx = vertical ? PH : PW;
  // the visible bands: k cards in bands along the strip, the band count for
  // the squarest card, the first bands a card wider where the count is uneven
  let bands = 1, bs = Infinity;
  for (let n = 1; n <= k; n++) { const per = Math.ceil(k / n), score = Math.abs(Math.log((U * uPx / per) / (L * tPx / n))) + 0.1 * (n * per - k); if (score < bs) { bs = score; bands = n; } }
  const base = Math.floor(k / bands), extra = k - base * bands, visible = [];
  for (let i = 0; i < bands; i++) visible.push({ m: base + (i < extra ? 1 : 0), t0: L * i / bands, t1: L * (i + 1) / bands });
  const c = visible[0].m, h0 = L / bands;
  const pattern = [{ m: c, h: 1 }, { m: Math.max(1, c - 1), h: 1.25 }, { m: c, h: 0.9 }, { m: c + (c > 1 ? 1 : 0), h: 1.1 }];
  const band = r => {
    if (r >= 0 && r < bands) return visible[r];
    if (r >= bands) { let t = L, i = bands; for (;;) { const p = pattern[(i - bands) % pattern.length]; if (i === r) return { m: p.m, t0: t, t1: t + h0 * p.h }; t += h0 * p.h; i++; } }
    let t = 0, i = -1; for (;;) { const p = pattern[(-i - 1) % pattern.length]; if (i === r) return { m: p.m, t0: t - h0 * p.h, t1: t }; t -= h0 * p.h; i--; }
  };
  const place = p => {
    if (p >= 0) { let r = 0, q = p; for (;;) { const b = band(r); if (q < b.m) return { i: q, b }; q -= b.m; r++; } }
    let r = -1, q = -p - 1; for (;;) { const b = band(r); if (q < b.m) return { i: b.m - 1 - q, b }; q -= b.m; r--; }
  };
  const slot = p => { const { i, b } = place(p); return { u0: U * i / b.m, u1: U * (i + 1) / b.m, t0: b.t0, t1: b.t1 }; };
  const r6 = v => Math.round(v * 1e6) / 1e6;
  const rect = (sl, s) => vertical ? [r6(g[0] + sl.u0), r6(g[1] + sl.t0 - s), r6(g[0] + sl.u1), r6(g[1] + sl.t1 - s)]
                                    : [r6(g[0] + sl.t0 - s), r6(g[1] + sl.u0), r6(g[0] + sl.t1 - s), r6(g[1] + sl.u1)];
  // the most cards the region can need at once: the bands are not all one
  // height, so a window the region's length can lie across more bands than
  // the page shows, some a card wider
  let need = 0;
  const period = h0 * pattern.reduce((q, p) => q + p.h, 0);
  for (let s = -period; s <= L + period; s += h0 / 16) {
    let n = 0;
    for (let r = -3 * pattern.length; ; r++) { const b = band(r); if (b.t0 >= s + L - 1e-9) break; if (b.t1 > s + 1e-9) n += b.m; }
    need = Math.max(need, n);
  }
  return { g, vertical, U, L, tPx, k, bands, slot, rect, need, maxAcross: Math.max(c + 1, ...pattern.map(p => p.m)) };
}
// the reel: the open page's strips, their cards and their scroll
let reel = null;
function reelPlace(b, r, claim) {
  r.mfRest = true; if (r.mfArea === undefined) r.mfArea = claim;
  b.rect = r; b.formRect = r;
  const [ex, ey] = root.rectCenter(r);
  b.path = { sx: ex, sy: ey, ex, ey, cx: ex, cy: ey };
  b.journey = null; b.progress = 1; b.pin = 1; b.leaving = false; b.table = null; b.reelPinned = true; b.reelParked = false;   // pinned: its seed holds its rectangle's centre; never a wall (see computeWalls)
  b.claimTarget = Math.max(CLAIM_MIN, claim);
}
// A parked card leaves the page: a wall at a rectangle off the page's top
// left, which cuts nothing from the ground, bids nothing and draws nothing.
// The page keeps its count and the page's tiling owes it no sliver.
function reelPark(b, i) {
  const r = [-2 - 1.5 * i, -2, -1 - 1.5 * i, -1];
  r.mfRest = true; r.mfArea = 1;
  b.rect = r; b.formRect = r;
  b.path = { sx: b.x, sy: b.y, ex: b.x, ey: b.y, cx: b.x, cy: b.y };
  b.journey = null; b.progress = 1; b.pin = 1; b.leaving = false; b.table = null; b.reelPinned = true; b.reelParked = true;
  b.claimTarget = CLAIM_MIN;
}
function reelEnter() {
  reel = null;
  if (!portalFocus || !(config.scene in PORTAL_TEMPLATES)) return;
  const n = root.bodies.filter(b => !b.isVoid && !b.leaving && !b.isSelf).length;
  const spec = portalScene(root, config.scene, n);
  if (!spec.strips || !spec.strips.length) return;
  const strips = []; let offset = 1;
  for (const st of spec.strips) {
    const cards = [];
    for (let p = 0; p < st.k; p++) { const r = spec.content[offset + p]; const b = root.bodies.find(q => !q.isVoid && !q.isSelf && !q.leaving && rectsEqual(q.rect, r)); if (b) cards.push({ b, p, parked: false }); }
    offset += st.k;
    // which ends of the strip are the page's edges: there a card keeps its
    // whole slot and runs off the page; at a divider it is clipped
    const g = st.g, C = root.COLS, R = root.ROWS;
    const S = { def: st, cards, s: 0, v: reelDrift, drag: null, M: st.k,
      pageT0: st.vertical ? g[1] < 1e-6 : g[0] < 1e-6, pageT1: st.vertical ? Math.abs(g[3] - R) < 1e-6 : Math.abs(g[2] - C) < 1e-6 };
    // the cards made up for the page: as many as the widest window the
    // region can lie across needs beyond the page's own, parked out of sight
    const extra = Math.max(st.maxAcross + 1, st.need - st.k);
    for (let i = 0; i < extra; i++) { const b = root.newBody(); b.fresh = false; b.reelSlack = true; b.kindRoll = 1; root.bodies.push(b); S.cards.push({ b, p: S.M + i, parked: true }); }
    S.cards.forEach((c, i) => { c.slot = i; });   // each card's off-page parking place
    S.M += extra;
    strips.push(S);
  }
  reel = { strips, serial: root.serial, scene: config.scene, spec, fresh: true, moved: false, settled: false };
}
// THE FLOW. The strip runs on its own, an upward waterfall: every card rises
// at a walking pace and comes round again. The wheel is a push along it, or
// against it, and the speed eases back to the flow's own within a second; a
// drag takes the strip in hand, its travel the pointer's, and a flick sends
// it on at the hand's speed. Nothing is stepped: the strip has a speed, and
// the page is authored again wherever that speed has carried it each frame.
const REEL_DRIFT = 28;      // px/s along the strip: the flow's own pace
const REEL_RELAX = 0.7;     // s: a push eases back to the flow's pace in about this
const REEL_WHEEL = 4;       // px/s of speed for each px of wheel
const REEL_VMAX = 2400;     // px/s, the most a push or a flick can give
let reelDrift = REEL_DRIFT;
const reelClampV = v => Math.max(-REEL_VMAX, Math.min(REEL_VMAX, v));
function reelFlow(dt) {
  if (!reel || guestLeft > 0) return;
  for (const S of reel.strips) {
    if (S.drag) continue;
    S.v += (reelDrift - S.v) * (1 - Math.exp(-dt / REEL_RELAX));
    if (Math.abs(S.v - reelDrift) < 0.05) S.v = reelDrift;
    const step = S.v * dt;
    if (!step) continue;
    S.s += step / S.def.tPx; reel.moved = true;
  }
}
function reelScroll(dy) {   // the wheel: a push along the flow
  if (!reel || guestLeft > 0) return false;
  for (const S of reel.strips) if (!S.drag) S.v = reelClampV(S.v + dy * REEL_WHEEL);
  return true;
}
function reelMove(dy) {     // a plain displacement of the strip, for the tests
  if (!reel || guestLeft > 0) return false;
  for (const S of reel.strips) S.s += dy / S.def.tPx;
  reel.moved = true;
  return true;
}
function reelStripAt(x, y) {
  if (!reel) return null;
  for (const S of reel.strips) { const g = S.def.g; if (x >= g[0] * root.PW && x <= g[2] * root.PW && y >= g[1] * root.PH && y <= g[3] * root.PH) return S; }
  return null;
}
function reelDragStart(x, y, t) {
  if (!reel || guestLeft > 0) return false;
  const S = reelStripAt(x, y); if (!S) return false;
  const pos = S.def.vertical ? y : x;
  S.drag = { s0: S.s, p0: pos, last: pos, t, v: 0 }; S.v = 0;
  return true;
}
function reelDragMove(x, y, t) {
  if (!reel) return false;
  let any = false;
  for (const S of reel.strips) {
    const d = S.drag; if (!d) continue;
    const pos = S.def.vertical ? y : x, dt = Math.max(1e-3, (t - d.t) / 1000);
    S.s = d.s0 + (d.p0 - pos) / S.def.tPx;
    const v = (d.last - pos) / dt;                       // the hand's speed, smoothed over the last 50 ms
    d.v += (v - d.v) * Math.min(1, dt / 0.05);
    d.last = pos; d.t = t; reel.moved = true; any = true;
  }
  return any;
}
function reelDragEnd(t) {
  if (!reel) return false;
  let any = false;
  for (const S of reel.strips) {
    const d = S.drag; if (!d) continue;
    S.v = t - d.t > 120 ? 0 : reelClampV(d.v);           // a hand that had stopped lets go still
    S.drag = null; any = true;
  }
  return any;
}
// every scroll step: the window of slots the region needs, the cards' slots
// clipped by it, the thin ones parked; the page's rest diagram authored
// again for what is under the region, and handed to every body at once
function reelStep() {
  if (!reel) return;
  if (root.serial !== reel.serial || !portalFocus || config.scene !== reel.scene) { reelDrop(null, true); return; }
  if (reel.fresh) {
    // the made-up cards are parked off the page at once, before the page's
    // first auction with them in it
    reel.fresh = false;
    for (const S of reel.strips) for (const c of S.cards) if (c.b.reelSlack) { c.parked = true; reelPark(c.b, c.slot); }
  }
  if (guestLeft > 0) return;
  // once the page has settled, and at every scroll step after, the page's
  // rest diagram is authored again for what is under the region
  if (!reel.moved && reel.settled) return;
  reel.moved = false; reel.settled = true;
  const rects = [portalFocus.rect.slice()], bodies = [portalFocus];
  for (const S of reel.strips) {
    const d = S.def, s = S.s, len = d.L;
    // THE WINDOW. The strip's cards hold M consecutive slots; the region
    // needs the slots of every band under it, from the first whose end is
    // past the region's start to the last whose start is before its end,
    // never more than M (the strip was given enough). The window shifts
    // only when it must, a card at a time: the card past one end takes the
    // slot beyond the other, and no slot under the region is ever empty.
    let w0 = Infinity; for (const c of S.cards) w0 = Math.min(w0, c.p);
    let lo = w0; if (d.slot(lo).t1 - s > 1e-9) { while (d.slot(lo - 1).t1 - s > 1e-9) lo--; } else { while (d.slot(lo).t1 - s <= 1e-9) lo++; }
    let hi = w0 + S.M - 1; if (d.slot(hi).t0 - s < len - 1e-9) { while (d.slot(hi + 1).t0 - s < len - 1e-9) hi++; } else { while (d.slot(hi).t0 - s >= len - 1e-9) hi--; }
    let n0 = w0; if (hi > w0 + S.M - 1) n0 = hi - S.M + 1; else if (lo < w0) n0 = lo;
    for (const c of S.cards) {
      while (c.p < n0) c.p += S.M; while (c.p >= n0 + S.M) c.p -= S.M;
      const sl = d.slot(c.p);
      c.sl = sl; c.t0 = Math.max(0, sl.t0 - s); c.t1 = Math.min(len, sl.t1 - s); c.parked = false;
    }
    // THE TILING UNDER THE REGION. A band with less than twice the claim
    // floor under the region is parked, its band with it (the auction would
    // draw its cards larger than authored), and the bands nearest each end
    // reach the end, so the region is tiled whatever is parked. At an end
    // that is the page's edge a card OVERFLOWS: its rectangle is still cut
    // at the page, but its seed is its whole slot's centre, off the page if
    // need be, so it slides in and out as itself, its seams with its
    // neighbours unchanged, instead of squeezing in as a sliver. At an end
    // that is a divider (whitespace or the image) it is clipped, seed and
    // all: nothing overflows into the whitespace.
    for (let guard = 0; guard < 64; guard++) {
      const vis = S.cards.filter(c => !c.parked);
      let thin = false;
      for (const c of vis) if ((c.t1 - c.t0) * (c.sl.u1 - c.sl.u0) < CLAIM_MIN * 2) { c.parked = true; thin = true; }
      if (thin) continue;
      if (!vis.length) break;
      let tMin = Infinity, tMax = -Infinity;
      for (const c of vis) { tMin = Math.min(tMin, c.t0); tMax = Math.max(tMax, c.t1); }
      for (const c of vis) { if (c.t0 - tMin < 1e-9) c.t0 = 0; if (tMax - c.t1 < 1e-9) c.t1 = len; }
      break;
    }
    for (const c of S.cards) {
      if (c.parked) { reelPark(c.b, c.slot); continue; }
      const r = d.rect({ u0: c.sl.u0, u1: c.sl.u1, t0: c.t0 + s, t1: c.t1 + s }, s);
      // the seed: the slot's centre along the strip, clipped only at a divider
      const a = S.pageT0 ? c.sl.t0 - s : Math.max(0, c.sl.t0 - s), z = S.pageT1 ? c.sl.t1 - s : Math.min(len, c.sl.t1 - s);
      const tm = (a + z) / 2, um = (c.sl.u0 + c.sl.u1) / 2;
      r.reelSeed = d.vertical ? [d.g[0] + um, d.g[1] + tm] : [d.g[0] + tm, d.g[1] + um];
      rects.push(r); bodies.push(c.b);
    }
  }
  const voids = reel.spec.voids.map(v => { const q = v.slice(); q.portalText = v.portalText; q.portalRules = v.portalRules; return q; });
  const dec = portalDecorate(rects, voids, W, H, root.COLS, root.ROWS);
  // handed to every body at once: the diagram is the rest state now, not a
  // target to ease toward, since the rectangles moved continuously
  dec.content.forEach((r, i) => { reelPlace(bodies[i], r, r.mfArea); bodies[i].claim = bodies[i].claimTarget; const q = bodies[i].subs[0]; q.w = dec.weights[i]; q.live = true; });   // the solved weight: exact this frame, no auction lag
  const vb = root.bodies.filter(b => b.isVoid && !b.leaving && b.rect);
  for (const r of dec.voids) { const v = vb.find(q => rectsEqual(q.rect, r)); if (!v) continue; r.reelLive = true; v.rect = r; v.formRect = r; v.claimTarget = rectArea(r); v.claim = v.claimTarget; }
}
// the next change: the made-up cards retire, so the page keeps its count; a
// made-up card kept as the next image takes an original's place
function reelDrop(keep, relayout) {
  if (!reel) return;
  const r = reel; reel = null;
  for (const v of root.bodies) { if (v.rect && v.rect.reelLive) v.rect.reelLive = false; if (v.reelPinned) { v.reelPinned = false; v.reelParked = false; v.pin = 0; } }   // unpinned: the next change finds them as Portal's page leaves them
  let owed = 0;
  for (const S of r.strips) for (const c of S.cards) {
    if (c.b === keep) { if (c.b.reelSlack) { c.b.reelSlack = false; owed++; } continue; }
    if (c.b.reelSlack && !c.b.leaving) root.retireBody(c.b, 0.6);
  }
  if (owed) {
    const originals = [];
    for (const S of r.strips) for (const c of S.cards) if (!c.b.reelSlack && c.b !== keep && !c.b.leaving) originals.push(c);
    originals.sort((a, b) => (b.parked ? 1 : 0) - (a.parked ? 1 : 0));
    for (let i = 0; i < owed && i < originals.length; i++) root.retireBody(originals[i].b, 0.6);
  }
  if (relayout) root.enterScene(config.scene);
}''')
replace('''  const p = portalPage(PORTAL_TEMPLATES[name], h.COLS, h.ROWS, n, h.W, h.H), s = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);''',
        '''  const p = portalPage(PORTAL_TEMPLATES[name], h.COLS, h.ROWS, n, h.W, h.H), s = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);
  s.strips = p.strips;''')

# --- the solved weights ride along: the diagram is exact the frame it changes ---
replace('''    for (let i = owned[k][0]; i < owned[k][1]; i++) if (d.areas[i] > 1e-6) q.mfSites.push({ x: allSeeds[i][0] / PW - cx, y: allSeeds[i][1] / PH - cy, q: d.areas[i] / (PW * PH) });''', '''    q.mfW = [];   // REEL: each site's solved weight, handed to the live auction when the page scrolls
    for (let i = owned[k][0]; i < owned[k][1]; i++) if (d.areas[i] > 1e-6) { q.mfSites.push({ x: allSeeds[i][0] / PW - cx, y: allSeeds[i][1] / PH - cy, q: d.areas[i] / (PW * PH) }); q.mfW.push(allWeights[i]); }''')
replace('''      sub.claim = budget * p.q / sum;
    }''', '''      sub.claim = budget * p.q / sum;
      if (b.rect && b.rect.reelLive && b.rect.mfW && i < b.rect.mfW.length) { sub.w = b.rect.mfW[i]; sub.live = true; }   // REEL: a scrolling page's whitespace bids at its solved weight
    }''')
# --- a reel's body is pinned but never a wall ------------------------------------
# A pinned body whose cell is its rectangle leaves the auction as a wall. On a
# reel every cell bids, the image included: the authored diagram gives each
# one site, and a wall in its place would cut the seams beside it straight
# where the diagram has them organic, so the auction would find its areas by
# moving the whitespace's seams instead.
replace("""      if (!b.leaving && (b.crystal >= 1 || (b.pin > 0 && this.cellIsRect(b, r)))) {""",
        """      if (!b.leaving && (b.reelParked || (!b.reelPinned && (b.crystal >= 1 || (b.pin > 0 && this.cellIsRect(b, r)))))) {   // REEL: a reel's body bids; a parked one is a wall off the page""")

# --- a made-up card on its way out is not a passage for the change -------------
# The change spreads over the bodies' contacts. A page's contacts are read
# from this frame's tessellation for bodies on their way out, and a retiring
# speck touching a card would take the card's place in the chain the change
# follows, so the cards beyond it get the change a hop late.
replace("""            if (B && B !== A && (loose(A) || loose(B))) touch(A, B, L / 2, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2);""",
        """            if (B && B !== A && (loose(A) || loose(B)) && !(A.reelSlack && A.leaving) && !(B.reelSlack && B.leaving)) touch(A, B, L / 2, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2);   // REEL: a retiring made-up card is no passage""")

# --- a reel's seed may stand off the page: a card at the page's edge keeps its
# slot's centre as its seed, so it slides in and out as itself
replace("""      {
        const box = this.plBox();
        b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
        b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));""",
        """      if (!b.reelPinned) {   // REEL: a reel's seed may stand off the page
        const box = this.plBox();
        b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
        b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));""")
replace("""        {
          const box = this.plBox();
          b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
          b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));""",
        """        if (!b.reelPinned) {   // REEL: a reel's seed may stand off the page
          const box = this.plBox();
          b.x = Math.min(box[2] - SEED_MARGIN, Math.max(box[0] + SEED_MARGIN, b.x));
          b.y = Math.min(box[3] - SEED_MARGIN, Math.max(box[1] + SEED_MARGIN, b.y));""")
# --- the authored diagram takes a card's seed where the reel puts it -------------
replace("""  const seeds = rects.map(r => [(r[0] + r[2]) / 2, (r[1] + r[3]) / 2]), weights = new Array(n).fill(0);""",
        """  const seeds = content.map((c, i) => c.reelSeed ? [c.reelSeed[0] * PW, c.reelSeed[1] * PH] : [(rects[i][0] + rects[i][2]) / 2, (rects[i][1] + rects[i][3]) / 2]), weights = new Array(n).fill(0);   // REEL: a card at the page's edge seeds from its whole slot""")

# --- the tick: the reel places its cards before the page steps ------------------
replace('''  guestLeft = changeEnds(root) - simTime;

  // 1-5. the page, and every hive inside it
  root.step(dt, simTime);''', '''  guestLeft = changeEnds(root) - simTime;
  reelFlow(dt);
  reelStep();

  // 1-5. the page, and every hive inside it
  root.step(dt, simTime);''')

# --- a live void's mirrors follow the cards without a slew ---------------------
replace('''    b.wvU = Math.min(1, (b.wvU || 0) + du);''', '''    b.wvU = b.rect && b.rect.reelLive ? 1 : Math.min(1, (b.wvU || 0) + du);   // REEL: a scrolling page's whitespace follows its cards at once''')
# a reel void's sites are exactly its authored ones: no padding site at its
# centre is left over from a formation that had more, since a leftover keeps a
# weight from where it stood and can own a swathe of the page for a frame
replace('''      while (b.subs.length < n) b.subs.push(makeSub(b, b.x, b.y));
    }''', '''      while (b.subs.length < n) b.subs.push(makeSub(b, b.x, b.y));
      if (b.isVoid && b.rect && b.rect.reelLive && b.rect.mfSites) { b.wvTo = b.rect.mfSites.map(p => ({ ...p })); b.wvFrom = b.wvTo.map(p => ({ ...p })); b.subs.length = b.wvTo.length; }   // REEL
    }''')

# --- a made-up card's going does not re-lay the page --------------------------
replace('''    const contentGone = gone.find(b => !b.isVoid);''', '''    const contentGone = gone.find(b => !b.isVoid && !b.reelSlack);   // REEL: a made-up card's going is no change''')

# --- the click, home and the scene buttons drop the reel first -----------------
replace('''  if (b === portalFocus) portalHome({ x, y });
  else {
    // the page opens on the side the click came from: the template is
    // mirrored when its image slot is nearer the click that way
    const T = PORTAL_TEMPLATES[portalKind(b)], hx = (T.hero[0] + T.hero[2]) / 2 * W;
    portalFlip = W >= H && Math.abs(x - (W - hx)) < Math.abs(x - hx) - 1;
    portalFocus = b; portalEnter(portalKind(b), { x, y });
  }
  return true;''', '''  if (b === portalFocus) { reelDrop(); portalHome({ x, y }); }
  else {
    reelDrop(b);
    // the page opens on the side the click came from: the template is
    // mirrored when its image slot is nearer the click that way
    const T = PORTAL_TEMPLATES[portalKind(b)], hx = (T.hero[0] + T.hero[2]) / 2 * W;
    portalFlip = W >= H && Math.abs(x - (W - hx)) < Math.abs(x - hx) - 1;
    portalFocus = b; portalEnter(portalKind(b), { x, y });
    reelEnter();
  }
  return true;''')
replace('''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && portalFocus) portalHome(); });''',
        '''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && portalFocus) { reelDrop(); portalHome(); } });
// REEL: the wheel pushes the open page's gallery along its flow; a drag takes it in hand
canvas.addEventListener('wheel', (e) => { if (!reel) return; e.preventDefault(); reelScroll(e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? window.innerHeight : 1)); }, { passive: false });
canvas.addEventListener('pointerdown', (e) => { const [x, y] = pointerPos(e); if (reelDragStart(x, y, performance.now())) { try { canvas.setPointerCapture(e.pointerId); } catch (_) {} } });
canvas.addEventListener('pointermove', (e) => { const [x, y] = pointerPos(e); reelDragMove(x, y, performance.now()); });
canvas.addEventListener('pointerup', () => { reelDragEnd(performance.now()); });
canvas.addEventListener('pointercancel', () => { reelDragEnd(-1e9); });''')
replace('''  portalFocus = null;                        // a scene button leaves any open page''', '''  reelDrop();
  portalFocus = null;                        // a scene button leaves any open page''')


(ROOT / 'reel.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
