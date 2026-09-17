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
    for (const sc of ['bento','hero','sidebar','frame']) {
      document.querySelector('.scene-btn[data-scene="'+sc+'"]').click();
      for (let i = 0; i < 260; i++) window.__advance(1);
      const out = [];
      // AND THE SPECIES CHECK, counted here because it is the same walk: a
      // body that carries a CARD must never be a wall. That is the whole
      // licence for this mark - whitespace draws no card, so a wall there adds
      // no second kind of card. Astra I has all thirteen as walls.
      for (const bd of root.bodies) if (!bd.isVoid && !bd.isSelf && bd.wall) cardWalls++;
      for (const bd of root.bodies) {
        if (!bd.isVoid || !bd.loops || !bd.loops.length || !bd.rect) continue;
        const PW = root.PW, PH = root.PH;
        const rx0 = bd.rect[0]*PW, ry0 = bd.rect[1]*PH, rx1 = bd.rect[2]*PW, ry1 = bd.rect[3]*PH;
        // sample over the union of rect and drawn bbox
        let bx0 = rx0, by0 = ry0, bx1 = rx1, by1 = ry1;
        for (const lp of bd.loops) for (const q of lp) { bx0=Math.min(bx0,q[0]); by0=Math.min(by0,q[1]); bx1=Math.max(bx1,q[0]); by1=Math.max(by1,q[1]); }
        const K = 260; let diff = 0, rect = 0;
        const cw = (bx1-bx0)/K, ch = (by1-by0)/K;
        for (let i = 0; i < K; i++) for (let j = 0; j < K; j++) {
          const x = bx0 + (i+0.5)*cw, y = by0 + (j+0.5)*ch;
            const inR = x >= rx0 && x <= rx1 && y >= ry0 && y <= ry1;
          // WALL UNION CELL. A body that is a wall has b.loops set to its wall
          // rect (hive.html:3243) UNLESS it also won an auction cell, which
          // overwrites it. A pane is both at once, so neither alone is the
          // whitespace; the whitespace is their union.
          const w = bd.wall;
          const inW = !!w && x >= w[0] && x <= w[2] && y >= w[1] && y <= w[3];
          const inD = inW || inLoops(x, y, bd.loops);
          if (inR) rect++;
          if (inR !== inD) diff++;
        }
        out.push({ id: bd.id, sites: bd.subs ? bd.subs.length : 0, rect: bd.rect,
                   miss: rect ? +(diff/rect).toFixed(4) : null, corners: corners(bd.loops) });
      }
      res[sc] = out;
    }
    res.cardWalls = cardWalls;
    return res;
  }, { N });
  await b.close();
  console.log(JSON.stringify({ src: path.basename(SRC), n: N || 'default', pageErrors: errs.length, ...out }));
})();
