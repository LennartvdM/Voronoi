"""Build Tell from Reel: a scroll-tell, the cells staying while a story scrolls.

The inverse of a page. The cells stay on the page, laid once beside a
reading column, and a story of short blurbs scrolls through the column like
a slide show: the wheel, a drag or a flick moves the story, and the slides
snap. Each slide names a place in the cluster, and the card nearest it (not
one of the last two slides' heroes) is the slide's hero: it swells where it
stands, its neighbours giving way, and shrinks back as the next swells,
linked to the scroll, so the cluster turns like a carousel under the text
and nothing travels after the entry. The page is a page like Portal's, one
site a cell and the column exact by the same construction. The text is set
once the entry has ended, the rules a beat after. Without the Tell button,
the tick, the picture and every drawing command are Reel's (validate.cjs).
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
raw = (ROOT / 'reel.html').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '62ca63c8af9b3a424b628ee08fd9178275714a58db14a8736f3571b233f1fcf3'
s = raw.decode()

def replace(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)

replace('<title>Reel — Hive</title>', '<title>Tell — Hive</title>')
replace('&larr; Back · Reel</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · its gallery flows: scroll, drag or flick it · click the image again for home</span>',
        '&larr; Back · Tell</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · Tell: a story scrolls, the cluster stays and its heroes swell · click the hero or Escape for home</span>')
replace('''      <button class="scene-btn" data-scene="frame">Frame</button>''',
        '''      <button class="scene-btn" data-scene="frame">Frame</button>
      <button class="scene-btn" data-scene="tell">Tell</button>''')

# --- the story's page, its heroes, its scroll and its blurbs ----------------------
replace('''const scenes = {''', '''// TELL. The inverse of a page: the cells stay, and a story of short blurbs
// scrolls through a reading column like a slide show. The cluster is laid
// once beside the column, the bento's own layout, and stays for the whole
// story: nothing travels after the entry. Each slide names a place in the
// cluster, and the card nearest it (not one of the last two slides' heroes)
// is the slide's hero: it swells where it stands, its neighbours giving way,
// and shrinks back as the next swells, linked to the scroll, so the cluster
// turns like a carousel under the text. The column is a wall once seated,
// so the whitespace stays exact under every swell.
const TELL_SLIDES = [
  { at: [0.12, 0.15], lines: [1, 0.86, 0.6] },
  { at: [0.9, 0.25],  lines: [1, 0.72, 0.9, 0.5] },
  { at: [0.5, 0.85],  lines: [0.94, 1, 0.66] },
  { at: [0.2, 0.75],  lines: [1, 0.8] },
  { at: [0.75, 0.6],  lines: [0.9, 1, 0.76, 0.58] },
  { at: [0.45, 0.2],  lines: [1, 0.68, 0.84] },
  { at: [0.95, 0.9],  lines: [0.96, 1, 0.52] },
  { at: [0.1, 0.45],  lines: [1, 0.9, 0.7] },
];
const TELL_COL = 0.25;     // the column's share of the width; of the height, as a band across the top, on a phone
const TELL_HERO = 0.2;     // a hero's share of the cluster, whatever its card's: every hero the same size
// The story's page: the column a full-height void with its corners on the
// page's edges, so the whitespace is exact by Portal's construction, and the
// cluster the bento's guillotine of the rest. A phone stacks: the column a
// band across the top, the cluster below.
function tellPage(C, R, n, W, H) {
  let column, region, rules;
  if (W < H) { const r0 = Math.max(1, Math.round(R * 0.3)); column = [0, 0, C, r0]; region = [0, r0, C, R]; rules = ['bottom']; }
  else { const c0 = Math.max(1, Math.round(C * TELL_COL)); column = [0, 0, c0, R]; region = [c0, 0, C, R]; rules = ['right']; }
  column.portalText = true; column.portalRules = rules;
  return { content: guillotine(region, n, 1), voids: [column], region };
}
const tellCache = new Map();
function tellScene(h, n) {
  const key = [h.COLS, h.ROWS, n, h.W, h.H].join('|');
  if (tellCache.has(key)) return tellCache.get(key);
  const p = tellPage(h.COLS, h.ROWS, n, h.W, h.H), sc = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);
  tellCache.set(key, sc); if (tellCache.size > 8) tellCache.delete(tellCache.keys().next().value);
  return sc;
}
// the story: its scroll (px, a page's height a slide), its speed, the slide
// it is on, the heroes chosen for its slides, and the text's clocks
let tell = null;
const tellPitch = () => H;
const TELL_SNAP = 0.25;     // s: a slow story eases onto its nearest slide in about this
const TELL_RELAX = 0.35;    // s: the story's speed eases away in this, half a reel's, so a slide arrives in about a second
function tellStart(origin) {
  reelDrop();
  portalFocus = null; portalFlip = false;
  tell = { y: 0, v: 0, k: 0, heroes: [], drag: null, enter: 0, key: '', alpha: 0, rule: 0, fullAt: -1, seen: -1 };
  portalEnter('tell', origin || { x: W / 2, y: H / 2 });
  // the heroes, from the cluster as laid: for each slide the card whose
  // place is nearest the slide's, not one of the last two slides' heroes
  const n = root.bodies.filter(b => !b.isVoid && !b.leaving && !b.isSelf).length;
  const g = tellPage(root.COLS, root.ROWS, n, W, H).region;
  const cards = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.rect);
  for (const sd of TELL_SLIDES) {
    const px = g[0] + sd.at[0] * (g[2] - g[0]), py = g[1] + sd.at[1] * (g[3] - g[1]), recent = tell.heroes.slice(-2);
    let best = null, bd = Infinity;
    for (const b of cards) { if (recent.includes(b)) continue; const d = Math.hypot((b.rect[0] + b.rect[2]) / 2 - px, (b.rect[1] + b.rect[3]) / 2 - py); if (d < bd) { bd = d; best = b; } }
    tell.heroes.push(best);
  }
  portalFocus = tell.heroes[0];
  tellSwell();
}
function tellDrop() {
  if (!tell) return;
  tell = null;
  for (const b of root.bodies) { b.tellMix = 0; if (b.rect && b.rect.reelLive) b.rect.reelLive = false; if (b.reelPinned && !reel) { b.reelPinned = false; b.reelParked = false; b.reelFade = undefined; b.pin = 0; } }   // unpinned: the next change finds the cards as a page leaves them
}
// The swell, handed. Once the entry has ended the page is authored again
// whenever a hero's share changes: Portal's construction with each hero's
// area grown by its share, the column's mirrors solved with it, and handed
// to every body at once, weights included, so the diagram is the authored
// one on the frame it changes, the column stays exact under every swell,
// and a hero grows where it stands with its neighbours giving way. A hero
// grows to a fifth of the cluster, whatever its card, so every hero is
// the same size. The first swell arrives over a third of a second once
// the cluster is in.
function tellStep(dt) {
  if (!tell || guestLeft > 0) return;
  tell.enter += (1 - tell.enter) * (1 - Math.exp(-dt / 0.35));
  if (tell.enter > 0.999) tell.enter = 1;
  const cards = root.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving && b.rect), voids = root.bodies.filter(b => b.isVoid && !b.leaving && b.rect);
  if (!cards.length || !voids.length) return;
  // the targets: a hero's from its card's area to its share of the cluster by
  // its mix, the other cards scaled to what is left, so the targets sum to the
  // cluster and a hero at rest holds its share exactly (a card's own area is
  // its rectangle's; rectArea would read the solved area a handoff left on it)
  const own = r => (r[2] - r[0]) * (r[3] - r[1]), g = tellPage(root.COLS, root.ROWS, cards.length, W, H).region, cluster = own(g);
  const m = b => (b.tellMix || 0) * tell.enter, want = b => TELL_HERO * cluster * m(b) + own(b.rect) * (1 - m(b));
  let heroSum = 0, restSum = 0; for (const b of cards) { if (m(b) > 0) heroSum += want(b); else restSum += own(b.rect); }
  const scale = restSum > 0 ? Math.max(0.05, (cluster - heroSum) / restSum) : 1;
  const swell = b => m(b) > 0 ? want(b) / own(b.rect) : scale;
  const key = cards.map(b => swell(b).toFixed(4)).join(',');
  if (key === tell.key) return;   // nothing swelled or shrank: the auction holds what it was handed
  tell.key = key;
  const rects = cards.map(b => { const r = b.rect.slice(0, 4); r.mfSwell = swell(b); return r; });
  const vr = voids.map(v => { const q = v.rect.slice(0, 4); q.portalText = v.rect.portalText; q.portalRules = v.rect.portalRules; return q; });
  const dec = portalDecorate(rects, vr, W, H, root.COLS, root.ROWS);
  dec.content.forEach((r, i) => { const b = cards[i]; reelPlace(b, r, r.mfArea); b.claim = b.claimTarget; const q = b.subs[0]; q.w = dec.weights[i]; q.live = true; });   // the solved weight: exact this frame, no auction lag
  dec.voids.forEach((r, i) => { const v = voids[i]; r.reelLive = true; v.rect = r; v.formRect = r; v.claimTarget = rectArea(r); v.claim = v.claimTarget; });
}
// the swell, linked to the scroll: slide k's hero holds a share that peaks
// on its slide and is gone a slide away, so one hero shrinks as the next
// grows and the story can be read backwards the same way
function tellSwell() {
  for (const b of root.bodies) b.tellMix = 0;
  const pos = tell.y / tellPitch();
  tell.heroes.forEach((h, k) => { if (!h) return; const w = Math.max(0, 1 - Math.abs(pos - k)); if (w > 0) h.tellMix = Math.min(1, (h.tellMix || 0) + w); });
}
// the flow of the story: a speed eases away, a slow story snaps to its slide,
// and the slide the story is on is the one nearest; its hero is the page's
// image, for the label and the click home
function tellFlow(dt) {
  if (!tell) return;
  const pitch = tellPitch(), last = (TELL_SLIDES.length - 1) * pitch;
  if (!tell.drag) {
    const snapping = Math.abs(tell.v) < 60;   // slow: the snap takes over, and what speed is left goes with it, so the story does not creep on past its slide
    tell.v *= Math.exp(-dt / (snapping ? TELL_SNAP : TELL_RELAX));
    if (Math.abs(tell.v) < 0.05) tell.v = 0;
    tell.y += tell.v * dt;
    if (tell.y < 0) { tell.y = 0; tell.v = 0; }
    if (tell.y > last) { tell.y = last; tell.v = 0; }
    if (snapping) { const target = Math.round(tell.y / pitch) * pitch; tell.y += (target - tell.y) * (1 - Math.exp(-dt / TELL_SNAP)); }
  }
  const k = Math.max(0, Math.min(TELL_SLIDES.length - 1, Math.round(tell.y / pitch)));
  if (k !== tell.k) { tell.k = k; portalFocus = tell.heroes[k]; }
  tellSwell();
}
// the wheel aims the story at the next slide: a notch, whatever its size,
// sends it one slide on (or back) at the speed whose easing carries it there,
// so a slide show turns a slide a notch and a long swipe passes slides one by one
function tellScroll(dy) {
  if (!tell) return false;
  if (tell.drag || Math.abs(dy) < 1) return true;
  const pitch = tellPitch(), aim = Math.max(0, Math.min(TELL_SLIDES.length - 1, Math.round(tell.y / pitch) + Math.sign(dy)));
  tell.v = reelClampV((aim * pitch - tell.y) / TELL_RELAX);
  return true;
}
function tellDragStart(x, y, t) { if (!tell) return false; tell.drag = { y0: tell.y, p0: y, last: y, t, v: 0 }; tell.v = 0; return true; }
function tellDragMove(x, y, t) {
  if (!tell || !tell.drag) return false;
  const d = tell.drag, dt = Math.max(1e-3, (t - d.t) / 1000), last = (TELL_SLIDES.length - 1) * tellPitch();
  tell.y = Math.max(0, Math.min(last, d.y0 + (d.p0 - y)));
  const v = (d.last - y) / dt; d.v += (v - d.v) * Math.min(1, dt / 0.05); d.last = y; d.t = t;
  return true;
}
function tellDragEnd(t) { if (!tell || !tell.drag) return false; const d = tell.drag; tell.v = t - d.t > 120 ? 0 : reelClampV(d.v); tell.drag = null; return true; }
// The blurbs, in the column, each at its place on the scroll: the slide's
// and its neighbours' as they pass, a column's height apart, a title (the
// hero's name) over its lines, fading at the column's ends. The text is set
// once the entry has ended and the column is seated, and stays: no slide
// moves the cluster; the rules along the column's side come a beat after
// the text has fully appeared.
function tellProseStep(ctx, type, dt, t) {
  if (!tell) return;
  const p = tell, gap = t - p.seen, el = p.seen < 0 || gap > 0.1 ? dt : gap;
  p.seen = t;
  let v = null;
  if (guestLeft <= 0) for (const b of root.bodies) if (b.isVoid && !b.leaving && b.rect && b.rect.portalText && b.crystal >= 0.99) v = b;
  p.alpha += ((v ? 1 : 0) - p.alpha) * (1 - Math.exp(-el / (v ? 0.30 : 0.08)));
  if (!v || p.alpha <= 0.97) p.fullAt = -1; else if (p.fullAt < 0) p.fullAt = t;
  p.rule += ((v && p.fullAt >= 0 && t - p.fullAt > 0.25 ? 1 : 0) - p.rule) * (1 - Math.exp(-el / (v ? 0.45 : 0.08)));
  if (!v || p.alpha < 0.01) return;
  const q = v.rect, r = [q[0] * root.PW, q[1] * root.PH, q[2] * root.PW, q[3] * root.PH], pad = Math.max(16, Math.min(48, 0.024 * W));
  const x0 = r[0] + pad, x1 = r[2] - pad, y0 = r[1] + pad, y1 = r[3] - pad;
  if (x1 - x0 < 90) return;
  const title = Math.round(type.num * 0.9), line = Math.max(4, Math.round(type.name * 0.55)), lead = Math.round(line * 2.1);
  ctx.save();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.globalAlpha = 0.22 * p.rule; ctx.beginPath();
  const g = Math.round(pad / 2) + 0.5;
  for (const e of v.rect.portalRules || []) {
    if (e === 'left') { ctx.moveTo(r[0] + g, r[1] + pad); ctx.lineTo(r[0] + g, r[3] - pad); }
    if (e === 'right') { ctx.moveTo(r[2] - g, r[1] + pad); ctx.lineTo(r[2] - g, r[3] - pad); }
    if (e === 'top') { ctx.moveTo(r[0] + pad, r[1] + g); ctx.lineTo(r[2] - pad, r[1] + g); }
    if (e === 'bottom') { ctx.moveTo(r[0] + pad, r[3] - g); ctx.lineTo(r[2] - pad, r[3] - g); }
  }
  ctx.stroke();
  const measure = Math.min(560, x1 - x0), pitch = tellPitch(), travel = y1 - y0;   // a slide's blurb travels the column's height, so its neighbours stand outside the column at rest
  ctx.beginPath(); ctx.moveTo(r[0], r[1]); ctx.lineTo(r[2], r[1]); ctx.lineTo(r[2], r[3]); ctx.lineTo(r[0], r[3]); ctx.closePath(); ctx.clip();
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  for (let k = tell.k - 1; k <= tell.k + 1; k++) {
    if (k < 0 || k >= TELL_SLIDES.length) continue;
    const lines = TELL_SLIDES[k].lines, hb = Math.round(title * 1.8) + lines.length * lead;
    const yk = y0 + (y1 - y0 - hb) / 2 + (k * pitch - tell.y) / pitch * travel;
    const edge = Math.min(1, Math.max(0, (yk + hb - y0) / 40), Math.max(0, (y1 - yk) / 40));
    const a = p.alpha * edge;
    if (a < 0.01) continue;
    const hero = tell.heroes[k];
    if (hero) {
      ctx.globalAlpha = 0.92 * a; ctx.font = `600 ${title}px system-ui, sans-serif`; ctx.fillText(hero.name, x0, yk);
      ctx.globalAlpha = 0.5 * a; ctx.beginPath(); ctx.moveTo(x0, yk + Math.round(title * 1.3) + 0.5); ctx.lineTo(x0 + Math.round(title * 1.6), yk + Math.round(title * 1.3) + 0.5); ctx.stroke();
    }
    ctx.globalAlpha = 0.20 * a;
    let y = yk + Math.round(title * 1.8);
    for (const f of lines) { roundedPath(ctx, [[x0, y], [x0 + measure * f, y], [x0 + measure * f, y + line], [x0, y + line]], line / 2, false); ctx.fill(); y += lead; }
  }
  ctx.restore();
}
const scenes = {''')

# --- the story's page is a page to the engine; a hero's swell is authored ------------
# the construction takes a swell: a card's target area is its rectangle's, times its swell
replace('''    const ref = idx.length === 1 ? null : solveWeights(idx.map(i => seeds[i]), idx.map(i => (rects[i][2] - rects[i][0]) * (rects[i][3] - rects[i][1])), poly, null, { maxIter: 60, tol: 1e-9 });''',
        '''    const ref = idx.length === 1 ? null : solveWeights(idx.map(i => seeds[i]), idx.map(i => (rects[i][2] - rects[i][0]) * (rects[i][3] - rects[i][1]) * (content[i].mfSwell || 1)), poly, null, { maxIter: 60, tol: 1e-9 });   // TELL: a hero's area is its card's, times its swell''')
# a card of the story bids for the whole story, so a hero can grow into it and it can give the ground back: never a wall
replace('''      if (!b.leaving && (b.reelParked || (!b.reelPinned && (b.crystal >= 1 || (b.pin > 0 && this.cellIsRect(b, r)))))) {''',
        '''      if (!b.leaving && (b.reelParked || (!b.reelPinned && !(tell && !b.isVoid && this.depth === 0) && (b.crystal >= 1 || (b.pin > 0 && this.cellIsRect(b, r)))))) {   // TELL: the story's cards bid throughout''')
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && (name in PORTAL_TEMPLATES) ? portalScene(this,name,content.length) :''',
        '''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell' ? tellScene(this, content.length) : this.depth===0 && (name in PORTAL_TEMPLATES) ? portalScene(this,name,content.length) :''')
replace('''  if (!portalFocus || !(name in PORTAL_TEMPLATES)) return;
  const k = content.indexOf(portalFocus);''', '''  if (!portalFocus || !(name in PORTAL_TEMPLATES || name === 'tell')) return;   // TELL: a story's hero takes the first slot when the page is laid again (an add, a remove, a resize)
  const k = content.indexOf(portalFocus);''')
replace('''    if (name in PORTAL_TEMPLATES) for (const b of content) { const j = b.journey, p = b.path;''',
        '''    if (name in PORTAL_TEMPLATES || name === 'tell') for (const b of content) { const j = b.journey, p = b.path;''')
replace('''    if (name in PORTAL_TEMPLATES && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''',
        '''    if ((name in PORTAL_TEMPLATES || name === 'tell') && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''')
replace('''        if (!(name in PORTAL_TEMPLATES) || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''',
        '''        if (!(name in PORTAL_TEMPLATES || name === 'tell') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''')
# the slide's hero carries no label: its name titles the blurb
replace('''    const pageT = b === portalFocus && PORTAL_TEMPLATES[config.scene];''',
        '''    const pageT = b === portalFocus && (PORTAL_TEMPLATES[config.scene] || (config.scene === 'tell' ? { text: true } : null));   // TELL: the slide's image carries no label''')

# --- the tick, the paint, the events ---------------------------------------------
replace('''  guestLeft = changeEnds(root) - simTime;
  reelFlow(dt);''', '''  guestLeft = changeEnds(root) - simTime;
  tellFlow(dt); tellStep(dt);
  reelFlow(dt);''')
replace('''  portalProseStep(ctx, type, dt, t);''', '''  portalProseStep(ctx, type, dt, t);
  tellProseStep(ctx, type, dt, t);''')
replace('''  if (b === portalFocus) { reelDrop(); portalHome({ x, y }); }
  else {
    reelDrop(b);''', '''  if (b === portalFocus) { reelDrop(); tellDrop(); portalHome({ x, y }); }
  else {
    reelDrop(b); tellDrop();''')
replace('''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && portalFocus) { reelDrop(); portalHome(); } });''',
        '''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && (portalFocus || tell)) { reelDrop(); tellDrop(); portalHome(); } });''')
replace('''canvas.addEventListener('wheel', (e) => { if (!reel) return; e.preventDefault(); reelScroll(e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? window.innerHeight : 1)); }, { passive: false });
canvas.addEventListener('pointerdown', (e) => { const [x, y] = pointerPos(e); if (reelDragStart(x, y, performance.now())) { try { canvas.setPointerCapture(e.pointerId); } catch (_) {} } });
canvas.addEventListener('pointermove', (e) => { const [x, y] = pointerPos(e); reelDragMove(x, y, performance.now()); });
canvas.addEventListener('pointerup', () => { reelDragEnd(performance.now()); });
canvas.addEventListener('pointercancel', () => { reelDragEnd(-1e9); });''',
        '''canvas.addEventListener('wheel', (e) => { const dy = e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? window.innerHeight : 1); if (tell) { e.preventDefault(); tellScroll(dy); return; } if (!reel) return; e.preventDefault(); reelScroll(dy); }, { passive: false });
canvas.addEventListener('pointerdown', (e) => { const [x, y] = pointerPos(e); if (tellDragStart(x, y, performance.now()) || reelDragStart(x, y, performance.now())) { try { canvas.setPointerCapture(e.pointerId); } catch (_) {} } });
canvas.addEventListener('pointermove', (e) => { const [x, y] = pointerPos(e); tellDragMove(x, y, performance.now()); reelDragMove(x, y, performance.now()); });
canvas.addEventListener('pointerup', () => { tellDragEnd(performance.now()); reelDragEnd(performance.now()); });
canvas.addEventListener('pointercancel', () => { tellDragEnd(-1e9); reelDragEnd(-1e9); });''')
replace('''document.querySelectorAll('.scene-btn').forEach(b => b.addEventListener('click', () => {
  reelDrop();
  portalFocus = null;                        // a scene button leaves any open page''',
        '''document.querySelectorAll('.scene-btn').forEach(b => b.addEventListener('click', () => {
  if (b.dataset.scene === 'tell') { tellStart(); return; }   // TELL: the story begins
  reelDrop(); tellDrop();
  portalFocus = null;                        // a scene button leaves any open page''')

(ROOT / 'tell.html').write_text(s)
print(hashlib.sha256(s.encode()).hexdigest())
