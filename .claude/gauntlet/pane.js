/* THE WHITESPACE: is it the rectangle it was given?
 *   node pane.js <page.html> [vw] [vh] [count]
 *
 * plumb.js measures the CARDS and skips the whitespace outright - its sample
 * loop drops any leaf with l.isVoid - so no number this repository published
 * ever looked at a void. This does, and it does not use an angle to do it:
 * a staircase is 100% on-axis and is not a rectangle.
 *
 *   miss      the area of the symmetric difference between the drawn
 *             whitespace and its own template rect, over the rect's area,
 *             by dense sampling. 0 is exactly the rectangle.
 *   corners   vertices left once collinear points are collapsed. 4 is a
 *             rectangle; more is a staircase or a fan.
 *   sites     how many seeds the void holds, because that is the thing that
 *             decides whether one seed can draw its shape at all.
 *
 * WALL UNION CELL. A body that is a wall has b.loops set to its wall rect
 * (hive.html:3243) unless it also won an auction cell, which overwrites it.
 * A growing pane is BOTH at once, so neither alone is the whitespace; the
 * whitespace is their union, and reading either by itself reports a mark that
 * works as a mark that does nothing, or the reverse.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path'), os = require('os');
const SRC = path.resolve(process.argv[2]);
const VW = +(process.argv[3] || 1440), VH = +(process.argv[4] || 900), N = +(process.argv[5] || 0);
function instrument(src) {
  const s = fs.readFileSync(src, 'utf8');
  const i = s.lastIndexOf('})();');
  const exp = `\n window.__X = { fn: (n) => ({ W: typeof W !== 'undefined' ? W : undefined, H: typeof H !== 'undefined' ? H : undefined, root: typeof root !== 'undefined' ? root : undefined })[n], setMouse: (x, y) => { mouseX = x; mouseY = y; } };\n`;
  const dst = path.join(os.tmpdir(), 'vf-' + Buffer.from(src + VW + VH + N).toString('hex').slice(-24) + '.html');
  fs.writeFileSync(dst, s.slice(0, i) + exp + s.slice(i));
  return dst;
}
const CLOCK = `(() => { let t = 0; const q = [];
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => {}; performance.now = () => t;
  window.__advance = (n) => { for (let i = 0; i < n; i++) { t += 30; const cbs = q.splice(0); for (const cb of cbs) cb(t); } };
})();`;
(async () => {
  const dst = instrument(SRC);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: VW, height: VH } });
  await p.addInitScript(CLOCK);
  const errs = []; p.on('pageerror', e => errs.push(String(e.message || e)));
  await p.goto('file://' + dst);
  await p.waitForTimeout(300);
  const out = await p.evaluate(({ N }) => {
    const X = window.__X; X.setMouse(-1000, -1000);
    if (N) { const c = document.getElementById('count'); c.value = String(N); c.dispatchEvent(new Event('input', {bubbles:true})); }
    for (let i = 0; i < 160; i++) window.__advance(1);
    const root = X.fn('root');
    const inPoly = (x, y, lp) => { let w = false;
      for (let i = 0, j = lp.length - 1; i < lp.length; j = i++) {
        const a = lp[i], c = lp[j];
        if (((a[1] > y) !== (c[1] > y)) && (x < (c[0]-a[0]) * (y-a[1]) / (c[1]-a[1]) + a[0])) w = !w;
      } return w; };
    const inLoops = (x, y, loops) => { let n = 0; for (const lp of loops) if (inPoly(x, y, lp)) n++; return n % 2 === 1; };
    const corners = (loops) => { let n = 0;
      for (const lp of loops) { const m = lp.length;
        for (let i = 0; i < m; i++) {
          const a = lp[(i-1+m)%m], b = lp[i], c = lp[(i+1)%m];
          const v1x = b[0]-a[0], v1y = b[1]-a[1], v2x = c[0]-b[0], v2y = c[1]-b[1];
          const cr = Math.abs(v1x*v2y - v1y*v2x), l1 = Math.hypot(v1x,v1y), l2 = Math.hypot(v2x,v2y);
          if (l1 < 1 || l2 < 1) continue;
          if (cr / Math.max(l1, l2) > 1.0) n++;   // turns by more than ~1px over its length
        } }
      return n; };
    const res = {}; let cardWalls = 0;
    // A body that carries a CARD must never be a wall: that is the whole
    // licence for making whitespace one. Sampled EVERY FRAME, not once after
    // settling - a card that is a wall for six frames of a change and a bidder
    // again by the time the page is still is exactly the case a settled
    // snapshot cannot see, and the invariant is stated per frame.
    const censusWalls = () => {
      for (const bd of root.bodies) if (!bd.isVoid && !bd.isSelf && bd.wall) cardWalls++;
    };
    for (const sc of ['bento','hero','sidebar','frame']) {
      document.querySelector('.scene-btn[data-scene="'+sc+'"]').click();
      for (let i = 0; i < 260; i++) { window.__advance(1); censusWalls(); }
      const out = [];
      for (const bd of root.bodies) {
        if (!bd.isVoid || !bd.rect) continue;
        const hasGeom = (bd.loops && bd.loops.length) || bd.wall;
        if (!hasGeom) {
          // A LIVE VOID WITH NO OUTLINE IS A FINDING, NOT A SKIP. Dropping it
          // silently means a gate only notices loss when EVERY void in a scene
          // is gone - and quilt() hands surplus slots back as extra voids, so
          // one of several vanishing would leave the scene non-empty and read
          // as a pass.
          out.push({ id: bd.id, sites: bd.subs ? bd.subs.length : 0, rect: bd.rect,
                     miss: null, corners: null, bboxFill: null, noGeometry: true });
          continue;
        }
        const loops = (bd.loops && bd.loops.length) ? bd.loops : [];
        const PW = root.PW, PH = root.PH;
        const rx0 = bd.rect[0]*PW, ry0 = bd.rect[1]*PH, rx1 = bd.rect[2]*PW, ry1 = bd.rect[3]*PH;
        const w = bd.wall;
        let bx0 = rx0, by0 = ry0, bx1 = rx1, by1 = ry1;
        for (const lp of loops) for (const q of lp) { bx0=Math.min(bx0,q[0]); by0=Math.min(by0,q[1]); bx1=Math.max(bx1,q[0]); by1=Math.max(by1,q[1]); }
        if (w) { bx0=Math.min(bx0,w[0]); by0=Math.min(by0,w[1]); bx1=Math.max(bx1,w[2]); by1=Math.max(by1,w[3]); }
        const K = 260; let diff = 0, rect = 0, drawn = 0;
        let ux0 = Infinity, uy0 = Infinity, ux1 = -Infinity, uy1 = -Infinity;
        const cw = (bx1-bx0)/K, ch = (by1-by0)/K;
        const mask = new Uint8Array(K*K);
        for (let i = 0; i < K; i++) for (let j = 0; j < K; j++) {
          const x = bx0 + (i+0.5)*cw, y = by0 + (j+0.5)*ch;
          const inR = x >= rx0 && x <= rx1 && y >= ry0 && y <= ry1;
          // WALL UNION CELL, for every reading taken here. A pane is both a
          // wall and a bidder at once and computeOutlines overwrites b.loops
          // with the residual auction cell, so neither alone is the whitespace.
          const inW = !!w && x >= w[0] && x <= w[2] && y >= w[1] && y <= w[3];
          const inD = inW || (loops.length ? inLoops(x, y, loops) : false);
          if (inR) rect++;
          if (inD) { drawn++; mask[i*K+j] = 1;
            if (x < ux0) ux0 = x; if (x > ux1) ux1 = x;
            if (y < uy0) uy0 = y; if (y > uy1) uy1 = y; }
          if (inR !== inD) diff++;
        }
        // RECTANGULARITY OF THE UNION, off the same mask, because the union's
        // outline is not a polygon either input carries. A rectangle fills its
        // own bounding box; a staircase, an L or a fan does not - and a
        // staircase is 100% on-axis, which is why an angle cannot say this.
        const cells = (ux1 > ux0 && uy1 > uy0)
          ? ((ux1-ux0)/cw + 1) * ((uy1-uy0)/ch + 1) : 0;
        const bboxFill = cells > 0 ? +(drawn / cells).toFixed(4) : null;
        // corners of the union, traced on the mask: a boundary cell whose
        // 4-neighbourhood turns, counted then halved for the two runs meeting
        let turns = 0;
        const at = (i,j) => (i>=0 && j>=0 && i<K && j<K) ? mask[i*K+j] : 0;
        for (let i = 0; i < K; i++) for (let j = 0; j < K; j++) {
          if (!mask[i*K+j]) continue;
          const l = at(i-1,j), r = at(i+1,j), u = at(i,j-1), d = at(i,j+1);
          if ((l+r+u+d) === 2 && ((l!==r) && (u!==d))) turns++;
        }
        out.push({ id: bd.id, sites: bd.subs ? bd.subs.length : 0, rect: bd.rect,
                   miss: rect ? +(diff/rect).toFixed(4) : null,
                   corners: corners(loops.length ? loops : [[[w[0],w[1]],[w[2],w[1]],[w[2],w[3]],[w[0],w[3]]]]),
                   unionCorners: turns, bboxFill: bboxFill });
      }
      res[sc] = out;
    }
    res.cardWalls = cardWalls;
    return res;
  }, { N });
  await b.close();
  console.log(JSON.stringify({ src: path.basename(SRC), n: N || 'default', pageErrors: errs.length, ...out }));
})();
