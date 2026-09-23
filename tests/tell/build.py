"""Build Tell from Reel: a scroll-tell, the cells staying while a story scrolls.

The inverse of a page. The cells stay on the page, and a story of short
blurbs scrolls through a reading column like a slide show: the wheel, a drag
or a flick moves the story, and the slides snap. Each blurb is a slide with
a place for an image beside it, above, below, left or right of the column,
and the cluster volunteers the cell nearest that place to be the slide's
image, the rest tiling the remainder as cards. A slide is a page like
Portal's, one site a cell and the column exact by the same construction, and
a slide change is a page change with Portal's smoothness. The text is set
only once the change has ended, the rules a beat after the text. Without the
Tell button, the tick, the picture and every drawing command are Reel's
(validate.cjs).
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
        '&larr; Back · Tell</a> <span style="opacity:.55;margin-left:.6em">click a cell to open its page · Tell: a story scrolls, the cells volunteer · Escape for home</span>')
replace('''      <button class="scene-btn" data-scene="frame">Frame</button>''',
        '''      <button class="scene-btn" data-scene="frame">Frame</button>
      <button class="scene-btn" data-scene="tell">Tell</button>''')

# --- the slides, the page of a slide, and the story's state ---------------------
replace('''const scenes = {''', '''// TELL. The inverse of a page: the cells stay, and a story of short blurbs
// scrolls through a reading column like a slide show. Each blurb is a slide
// with a place for an image beside the column, and the cluster volunteers
// the cell nearest that place to be the image, the rest tiling the
// remainder as cards. A slide is a page like Portal's: one site a cell, the
// column exact by the same construction, the image pinned to the first
// slot; a slide change is a page change with Portal's smoothness.
const TELL_SLIDES = [
  { col: 'left',   side: 'right', band: [0, 0.55],    lines: [1, 0.86, 0.6] },
  { col: 'centre', side: 'left',  band: [0.22, 0.78], lines: [1, 0.72, 0.9, 0.5] },
  { col: 'right',  side: 'left',  band: [0.45, 1],    lines: [0.94, 1, 0.66] },
  { col: 'centre', side: 'right', band: [0, 0.55],    lines: [1, 0.8] },
  { col: 'left',   side: 'right', band: [0.45, 1],    lines: [0.9, 1, 0.76, 0.58] },
  { col: 'right',  side: 'left',  band: [0, 0.55],    lines: [1, 0.68, 0.84] },
  { col: 'centre', side: 'left',  band: [0.45, 1],    lines: [0.96, 1, 0.52] },
  { col: 'left',   side: 'right', band: [0.22, 0.78], lines: [1, 0.9, 0.7] },
];
const TELL_COL = { left: [0, 0.24], centre: [0.38, 0.62], right: [0.76, 1] };
// A slide's page: the column a full-height void (its corners on the page's
// edges, so the whitespace is exact), the image beside it on the slide's
// side over the slide's band of the height, the cards in the rectangles
// left: the far side of the column whole, and above and below the image.
// A phone stacks: the blurb a band across the top, the image below it on
// its side, the cards beside and below.
function tellPage(k, C, R, n, W, H) {
  const sd = TELL_SLIDES[k % TELL_SLIDES.length];
  const r6 = v => Math.round(v * 1e6) / 1e6, L = f => [r6(f[0] * C), r6(f[1] * R), r6(f[2] * C), r6(f[3] * R)];
  let hero, column, regions, rules;
  if (W < H) {
    column = [0, 0, 1, 0.28]; rules = ['bottom'];
    const left = sd.side === 'left';
    hero = left ? [0, 0.28, 0.5, 0.64] : [0.5, 0.28, 1, 0.64];
    regions = [left ? [0.5, 0.28, 1, 0.64] : [0, 0.28, 0.5, 0.64], [0, 0.64, 1, 1]];
  } else {
    const [c0, c1] = TELL_COL[sd.col], [y0, y1] = sd.band, hw = 0.38;
    column = [c0, 0, c1, 1]; rules = sd.col === 'left' ? ['right'] : sd.col === 'right' ? ['left'] : ['left', 'right'];
    const right = sd.col === 'left' || (sd.col === 'centre' && sd.side === 'right');
    const hx0 = right ? c1 : c0 - hw, hx1 = right ? c1 + hw : c0;
    hero = [hx0, y0, hx1, y1];
    regions = [sd.col === 'centre' ? (right ? [0, 0, c0, 1] : [c1, 0, 1, 1]) : sd.col === 'left' ? [c1 + hw, 0, 1, 1] : [0, 0, c0 - hw, 1]];
    if (y0 > 0) regions.push([hx0, 0, hx1, y0]);
    if (y1 < 1) regions.push([hx0, y1, hx1, 1]);
  }
  const heroL = L(hero), regs = regions.map(L), voids = [L(column)];
  voids[0].portalText = true; voids[0].portalRules = rules;
  const m = n - 1, total = regs.reduce((q, g) => q + rectArea(g), 0);
  const counts = regs.map(g => Math.max(1, Math.floor(m * rectArea(g) / total)));
  let assigned = counts.reduce((q, c) => q + c, 0);
  while (assigned < m) { let best = 0, bs = -1; regs.forEach((g, i) => { const q = rectArea(g) / counts[i]; if (q > bs) { bs = q; best = i; } }); counts[best]++; assigned++; }
  while (assigned > m) { let best = -1, bs = Infinity; regs.forEach((g, i) => { if (counts[i] > 1) { const q = rectArea(g) / counts[i]; if (q < bs) { bs = q; best = i; } } }); if (best < 0) break; counts[best]--; assigned--; }
  const cards = []; regs.forEach((g, i) => cards.push(...portalCards(g, counts[i])));
  return { content: [heroL, ...cards], voids };
}
const tellCache = new Map();
function tellScene(h, n) {
  const k = tell ? tell.k : 0, key = [k, h.COLS, h.ROWS, n, h.W, h.H].join('|');
  if (tellCache.has(key)) return tellCache.get(key);
  const p = tellPage(k, h.COLS, h.ROWS, n, h.W, h.H), sc = portalDecorate(p.content, p.voids, h.W, h.H, h.COLS, h.ROWS);
  tellCache.set(key, sc); if (tellCache.size > 24) tellCache.delete(tellCache.keys().next().value);
  return sc;
}
// the story: its scroll (px, a page's height a slide), its speed, the slide
// it is on, the cells that volunteered, and the text's clocks
let tell = null;
const tellPitch = () => H;
const TELL_SNAP = 0.25;     // s: a slow story eases onto its nearest slide in about this
const TELL_RELAX = 0.35;    // s: the story's speed eases away in this, half a reel's, so a slide arrives in about a second
function tellStart(origin) {
  reelDrop();
  tell = { y: 0, v: 0, k: -1, heroes: [], visited: [], drag: null, alpha: 0, rule: 0, fullAt: -1, seen: -1, changed: -1e9 };
  tellGo(0, origin || { x: W / 2, y: H / 2 });
}
function tellDrop() { tell = null; }
// the slide's image: the cell nearest the image's place that was not one of
// the last two images volunteers; a slide seen before keeps its image
function tellGo(k, origin) {
  if (!tell) return;
  const n = root.bodies.filter(b => !b.isVoid && !b.leaving && !b.isSelf).length;
  const page = tellPage(k, root.COLS, root.ROWS, n, W, H), hr = page.content[0];
  const cx = (hr[0] + hr[2]) / 2 * root.PW, cy = (hr[1] + hr[3]) / 2 * root.PH;
  const recent = tell.visited.slice(-2);
  let best = tell.heroes[k] && !tell.heroes[k].leaving && !recent.includes(tell.heroes[k]) ? tell.heroes[k] : null;
  if (!best) { let bd = Infinity; for (const b of root.bodies) { if (b.isVoid || b.isSelf || b.leaving || recent.includes(b)) continue; const d = Math.hypot(b.x - cx, b.y - cy); if (d < bd) { bd = d; best = b; } } }
  if (!best) return;
  tell.k = k; tell.heroes[k] = best; tell.visited.push(best); tell.changed = simTime;
  portalFocus = best; portalFlip = false;
  portalEnter('tell', origin || { x: best.x, y: best.y });
}
// the flow of the story: a speed eases away, a slow story snaps to its slide,
// and the slide the story is on is the one nearest; a change at most every
// quarter second, so a long flick passes slides without opening each
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
  if (k !== tell.k && simTime - tell.changed > 0.25) tellGo(k, null);
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
// image's name, once it has volunteered) over its lines, fading at the
// column's ends. The text is set
// only once the change has ended; the rules along the column's sides come
// a beat after the text has fully appeared.
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

# --- a Tell slide is a page to the engine ----------------------------------------
replace('''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && (name in PORTAL_TEMPLATES) ? portalScene(this,name,content.length) :''',
        '''    const spec = this.depth===0 && (name==='hero'||name==='frame') ? mfScene(this,name,content.length) : this.depth===0 && name === 'tell' ? tellScene(this, content.length) : this.depth===0 && (name in PORTAL_TEMPLATES) ? portalScene(this,name,content.length) :''')
replace('''  if (!portalFocus || !(name in PORTAL_TEMPLATES)) return;
  const k = content.indexOf(portalFocus);''', '''  if (!portalFocus || !(name in PORTAL_TEMPLATES || name === 'tell')) return;   // TELL: a slide's image takes the first slot too
  const k = content.indexOf(portalFocus);''')
replace('''    if (name in PORTAL_TEMPLATES) for (const b of content) { const j = b.journey, p = b.path;''',
        '''    if (name in PORTAL_TEMPLATES || name === 'tell') for (const b of content) { const j = b.journey, p = b.path;''')
replace('''    if (name in PORTAL_TEMPLATES && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''',
        '''    if ((name in PORTAL_TEMPLATES || name === 'tell') && portalFocus && portalFocus.journey && portalFocus.journey.t0 === this.t) {''')
replace('''        if (!(name in PORTAL_TEMPLATES) || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''',
        '''        if (!(name in PORTAL_TEMPLATES || name === 'tell') || !b.path || !b.journey || b.journey.t0 !== this.t) continue;''')
# the slide's image carries no label: its name titles the blurb
replace('''    const pageT = b === portalFocus && PORTAL_TEMPLATES[config.scene];''',
        '''    const pageT = b === portalFocus && (PORTAL_TEMPLATES[config.scene] || (config.scene === 'tell' ? { text: true } : null));   // TELL: the slide's image carries no label''')

# --- the tick, the paint, the events ---------------------------------------------
replace('''  guestLeft = changeEnds(root) - simTime;
  reelFlow(dt);''', '''  guestLeft = changeEnds(root) - simTime;
  tellFlow(dt);
  reelFlow(dt);''')
replace('''  portalProseStep(ctx, type, dt, t);''', '''  portalProseStep(ctx, type, dt, t);
  tellProseStep(ctx, type, dt, t);''')
replace('''  if (b === portalFocus) { reelDrop(); portalHome({ x, y }); }
  else {
    reelDrop(b);''', '''  if (b === portalFocus) { reelDrop(); tellDrop(); portalHome({ x, y }); }
  else {
    reelDrop(b); tellDrop();''')
replace('''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && portalFocus) { reelDrop(); portalHome(); } });''',
        '''window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && portalFocus) { reelDrop(); tellDrop(); portalHome(); } });''')
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
