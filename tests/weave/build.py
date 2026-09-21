"""Build Weave from Plumb: seam sites enter as a continuous formation.

Plumb already contains the successful straight-void construction behind
PL_SEAM_SITES, and records why it was disabled: replacing a void's one site
with all seam sites in one frame reintroduced the skip. Weave does not add a
wall or force a rectangular domain. It keeps the old formation as the start of
a morph, pads new sites at the old centre with negligible claim, and moves and
funds them continuously. The power diagram remains the only geometry.
"""
from pathlib import Path
import hashlib
import os

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'plumb.html'
raw = SOURCE.read_bytes()
blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
EXPECTED = '79568bd94c8ef294e72f74408f9d494a8963f101'
if blob != EXPECTED:
    raise SystemExit(f'Plumb changed: expected {EXPECTED}, found {blob}; rebaseline before rebuilding.')
s = raw.decode()


def replace(old, new, count=1):
    global s
    found = s.count(old)
    if found != count:
        raise ValueError(f'Expected {count} matches for {old[:70]!r}; found {found}')
    s = s.replace(old, new)


replace('<title>Plumb — Hive</title>', '<title>Weave — Hive</title>')
replace('&larr; Back · Plumb</a>', '&larr; Back · Weave</a>')
replace('const PL_SEAM_SITES = 0;', '''const PL_SEAM_SITES = 1;
const WV_SITE_SLEW = 0.72; // seconds from one void formation to the next
const WV_SITE_FLOOR = 1e-5;''')

start = s.index('Hive.prototype.plSeamSites = function() {')
end = s.index('\n\nconst plOldPlace = Hive.prototype.placeSeeds;', start)
new = r'''Hive.prototype.plSeamSites = function() {
  if (this.depth !== 0 || !PL_SEAM_SITES) return;
  const E = 1e-6, PW = this.PW, PH = this.PH;
  const live = [];
  for (const b of this.bodies) if (!b.isSelf && (b.formRect || b.rect)) live.push(b);
  const key = plRectsKey(live);
  if (this.plKey !== key) {
    this.plKey = key;
    for (const b of live) {
      // Preserve what the auction drew on the preceding frame. New sites are
      // born at that formation's centre with negligible share; removed sites
      // return there the same way. A changed topology therefore has no spatial
      // or area-sized event attached to the frame on which it is discovered.
      const old = b.plCurrent && b.plCurrent.length ? b.plCurrent : [{ x: 0, y: 0, q: 1 }];
      b.wvFrom = old.map(p => ({ x: p.x, y: p.y, q: p.q }));
      b.wvTo = [{ x: 0, y: 0, q: 1 }];
      b.wvU = 0;
    }
    const over = (a0, a1, b0, b1) => Math.min(a1, b1) - Math.max(a0, b0) > E;
    for (const v of live) {
      if (!v.isVoid) continue;
      const rv = v.formRect || v.rect;
      const cv = [(rv[0] + rv[2]) / 2, (rv[1] + rv[3]) / 2];
      const target = [];
      for (const c of live) {
        if (c === v || c.isVoid) continue;
        const rc = c.formRect || c.rect;
        if ((Math.abs(rc[2] - rv[0]) < E || Math.abs(rc[0] - rv[2]) < E) && over(rc[1], rc[3], rv[1], rv[3])) {
          target.push({ x: 0, y: (rc[1] + rc[3]) / 2 - cv[1], q: (rc[3] - rc[1]) * (rv[2] - rv[0]) });
        } else if ((Math.abs(rc[3] - rv[1]) < E || Math.abs(rc[1] - rv[3]) < E) && over(rc[0], rc[2], rv[0], rv[2])) {
          target.push({ x: (rc[0] + rc[2]) / 2 - cv[0], y: 0, q: (rc[2] - rc[0]) * (rv[3] - rv[1]) });
        }
      }
      if (target.length) v.wvTo = target;
    }
    // Pair old and new sites by order and pad at the weighted centre. The
    // count changes now, but every added cell begins with floor area at the
    // old formation rather than arriving fully formed at a distant seam.
    for (const b of live) {
      const n = Math.max(b.wvFrom.length, b.wvTo.length);
      while (b.wvFrom.length < n) b.wvFrom.push({ x: 0, y: 0, q: WV_SITE_FLOOR });
      while (b.wvTo.length < n) b.wvTo.push({ x: 0, y: 0, q: WV_SITE_FLOOR });
      b.subs = b.wvFrom.map(() => ({ body: b, x: 0, y: 0, w: 0, claim: 0, live: false }));
    }
  }
  const du = (this.lastDt || 1 / 60) / WV_SITE_SLEW;
  for (const b of live) {
    if (!b.wvFrom || !b.wvTo) continue;
    b.wvU = Math.min(1, (b.wvU || 0) + du);
    const u = b.wvU * b.wvU * (3 - 2 * b.wvU);
    const cur = [];
    let sum = 0;
    for (let i = 0; i < b.wvFrom.length; i++) {
      const a = b.wvFrom[i], z = b.wvTo[i];
      const q = Math.max(WV_SITE_FLOOR, a.q + (z.q - a.q) * u);
      const p = { x: a.x + (z.x - a.x) * u, y: a.y + (z.y - a.y) * u, q };
      cur.push(p); sum += q;
    }
    b.plCurrent = cur;
    for (let i = 0; i < cur.length; i++) {
      const sub = b.subs[i], p = cur[i];
      sub.x = b.x + p.x * PW;
      sub.y = b.y + p.y * PH;
      sub.claim = b.claim * p.q / sum;
    }
  }
};'''
s = s[:start] + new + s[end:]

out = Path(os.environ.get('WEAVE_OUT', ROOT / 'weave.html'))
out.write_text(s)
print('Built', out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
print('Weave SHA256', hashlib.sha256(s.encode()).hexdigest())
