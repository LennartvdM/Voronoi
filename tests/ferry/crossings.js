// Ferry: keep whitespace generators out of a departing stream. The original
// Harbor paths, springs, claim ledgers and journey durations are unchanged.
function ferryEdge(h, r) {
  if (!r || r[1] !== 0 || r[3] !== h.ROWS) return 0;
  return r[2] === h.COLS ? 1 : r[0] === 0 ? -1 : 0;
}

function ferryLedgerProgress(h, row, t) {
  if (row.body.reaped) return 1;
  if (row.body.journey === row.journey) return row.body.progress;
  if (h.depth !== 0 || !row.journey) return 1;
  // Retargeting a cell does not instantly pay off its old void ledger.
  // Finish that outstanding share on the original journey's clock, which
  // equals its last observed progress at the instant it was interrupted.
  const j=row.journey;
  return easeInOutCubic(Math.max(0, Math.min(1,
    (t-j.t0-j.delay-(j.hold || 0))/j.dur)));
}

const ferryScene = Hive.prototype.enterScene;
Hive.prototype.enterScene = function(...args) {
  const result = ferryScene.apply(this, args);
  if (this.depth !== 0) return result;
  const opening = this.bodies.find(b => b.isVoid && !b.leaving && ferryEdge(this, b.rect));
  if (!opening) return result;
  const sign = ferryEdge(this, opening.rect);
  const moving = this.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving &&
    b.path && b.journey && b.journey.t0 === this.t && sign*(b.path.ex-b.x) < -1)
    .sort((a,b) => sign*(b.x-a.x));
  // A rear cell must not launch into a leading cell that is still waiting.
  // Pull the leader's departure forward along each destination row. Never
  // delay a follower, shorten a journey, or add a catch-up deadline.
  for (let i=0; i<moving.length; i++) for (let j=i+1; j<moving.length; j++) {
    const rear=moving[i], front=moving[j];
    if (sign*(front.path.ex-rear.path.ex) >= 0 ||
        Math.abs(front.path.ey-rear.path.ey) > this.PH*.1) continue;
    front.journey.delay = Math.min(front.journey.delay, rear.journey.delay);
    front.T = front.journey.delay;
    front.fieldAt = front.journey.t0 + front.journey.delay;
  }
  return result;
};

function ferryCentroid(cell) {
  let area=0, x=0, y=0;
  for (const pc of cell.pieces || [cell]) {
    const pts=pc.pts;
    for (let i=0; i<pts.length; i++) {
      const p=pts[i], q=pts[(i+1)%pts.length], z=p[0]*q[1]-q[0]*p[1];
      area+=z; x+=(p[0]+q[0])*z; y+=(p[1]+q[1])*z;
    }
  }
  return Math.abs(area)>1e-6 ? [x/(3*area), y/(3*area)] : null;
}

const ferryPlace = Hive.prototype.placeSeeds;
Hive.prototype.placeSeeds = function() {
  ferryPlace.call(this);
  if (this.depth !== 0) return;
  const visible=this.bodies.filter(b => !b.isVoid && !b.isSelf && !b.leaving);
  const dt=this.lastDt || 1/60, W=this.W, H=this.H;
  const oldW=this.ferryW || W, oldH=this.ferryH || H;
  const indices=new Map((this.solvedSubs || []).map((s,i) => [s,i]));
  for (const v of this.bodies) {
    if (!v.isVoid) continue;
    if (v.rect && !v.leaving) {
      v.ferrySide=ferryEdge(this, v.rect);
      if (v.ferrySide) {
        const sign=v.ferrySide;
        // Never ask for more clearance than the accepted rest geometry has.
        const target=v.wvTo || [{x:0}];
        const cx=v.path ? v.path.ex : v.x;
        const edge=Math.min(...target.map(p => sign*(cx+p.x*this.PW)));
        const rest=visible.filter(b => b.path);
        const gap=rest.length ? edge-Math.max(...rest.map(b => sign*b.path.ex)) : 0;
        v.ferryGap=Math.min(.08, Math.max(0, .75*gap/W));
      }
    }
    if (v.ferrySide && visible.length) {
      const sign=v.ferrySide;
      const front=Math.max(...visible.map(b => sign*b.x));
      const nearest=Math.min(...v.subs.map(s => sign*s.x));
      const need=Math.max(0, (front+(v.ferryGap || 0)*W-nearest)/W);
      // Sites are born at the clear edge with floor area. Afterwards the
      // offset survives interruption; removal of an extreme body cannot
      // make the formation jump back inward in a single frame.
      const before=v.ferryOffset === undefined ? need : v.ferryOffset;
      v.ferryOffset=Math.max(need, before-900*dt/W);
      for (const sub of v.subs) sub.x+=sign*v.ferryOffset*W;
    } else if (v.leaving && this.solved) {
      // Interior whitespace has no outside edge to retreat along. Let each
      // existing generator follow the patch of whitespace it already owns,
      // rather than remain a stationary obstacle as its claim drains.
      // Keep every site, weight and quota; do not collapse a formation or
      // switch geometry types. The previous solve supplies only a direction.
      const speed=Math.min(500, Math.max(180, W*.27));
      for (const sub of v.subs) {
        const cell=this.solved.diagram.cells[indices.get(sub)];
        const c=cell && ferryCentroid(cell);
        if (!c) continue;
        const from=sub.ferryXY ? [sub.ferryXY[0]*W, sub.ferryXY[1]*H] : [sub.x,sub.y];
        const tx=c[0]*W/oldW, ty=c[1]*H/oldH;
        const d=Math.hypot(tx-from[0],ty-from[1]);
        const k=Math.min(1,speed*dt/Math.max(1e-9,d));
        sub.x=from[0]+(tx-from[0])*k;
        sub.y=from[1]+(ty-from[1])*k;
      }
    }
    for (const sub of v.subs) sub.ferryXY=[sub.x/W,sub.y/H];
  }
  this.ferryW=W; this.ferryH=H;
};
