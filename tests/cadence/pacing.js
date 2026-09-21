  // Each travelling root cell spends its own time. There is no page deadline.
  // The same progress pays its area, the whitespace ledger and the margin.
  cadenceClock(b, dt, t) {
    const j = b.journey, p = b.path;
    if (!j.cadence) {
      // Maximum derivative of the quadratic path times the peak derivative
      // of smootherstep bounds the speed of its moving target. Unlike the
      // old 2.2 s cap, the duration continues to grow for longer paths.
      const tangent = 2 * Math.max(Math.hypot(p.cx-p.sx,p.cy-p.sy), Math.hypot(p.ex-p.cx,p.ey-p.cy));
      const speed = Math.max(160, Math.min(340, Math.hypot(this.W,this.H)*0.19));
      j.dur = Math.max(j.dur, 1.875*tangent/speed, 1.2);
      j.cadence = {u:0, rate:1, speed};
      j.cadenceSlip = 0;
    }
    const start = j.t0+j.delay+(j.hold||0), c = j.cadence;
    const activeDt = Math.max(0, t-Math.max(t-dt,start));
    if (!activeDt || c.u>=1) return c.u;
    const e=c.u*c.u*c.u*(10+c.u*(-15+6*c.u)), m=1-e;
    const x=m*m*p.sx+2*m*e*p.cx+e*e*p.ex, y=m*m*p.sy+2*m*e*p.cy+e*e*p.ey;
    // A delayed or obstructed seed may be behind its target. Ease its clock
    // down until the spring catches up; never raise the pace to repay time.
    const lag=Math.hypot(x-b.x,y-b.y), allowance=c.speed*0.24+8;
    const wanted=Math.max(0.18,Math.min(1,allowance/Math.max(allowance,lag)));
    c.rate += (wanted-c.rate)*(1-Math.exp(-activeDt/0.18));
    const spent=Math.min(activeDt*c.rate,(1-c.u)*j.dur);
    c.u=Math.min(1,c.u+spent/j.dur);
    j.cadenceSlip+=activeDt-spent;
    return c.u;
  }
