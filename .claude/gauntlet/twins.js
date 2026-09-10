/* THE CHAOS BAND, measured, before anyone ranks anything.
 *   node twins.js <hive.html> [--dt 30] [--jitter 12] [--eps 1e-12]
 *
 * This page is a chaotic system: it is a damped Newton solve whose warm start
 * is last frame's answer, driving springs that feed back into next frame's
 * problem. Two runs that differ in the last bit of one number diverge, and
 * the divergence is not small. Every number the harness prints therefore has
 * a band around it that has nothing to do with any change, and a build ranked
 * on a difference smaller than its band has been ranked on nothing.
 *
 * The perturbation is the CLOCK, not a constant in the file: the same run at
 * dt and at dt*(1 +/- 1e-12). Nothing about the file changes, so the band is
 * a property of the page rather than of whichever constant somebody chose to
 * nudge, and it can be taken on any candidate without editing it.
 *
 * Run this on YOUR candidate and on the file you are comparing it against.
 * A metric whose bands overlap is not evidence. Report the band beside every
 * number you claim, or the number is a coin toss with a decimal point.
 */
const { execFileSync } = require('child_process');
const path = require('path'), fs = require('fs');
const argv = process.argv.slice(2);
const SRC = path.resolve(argv[0] || path.join(__dirname, '..', '..', 'hive.html'));
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
const DT = +opt('--dt', 1000 / 60), JIT = +opt('--jitter', 0), EPS = +opt('--eps', 1e-12);
const SCORE = path.join(__dirname, 'score.js');

const FIELDS = ['jumps', 'reversals', 'shockPx2', 'gapMax', 'overMax', 'vanish', 'voidJumps', 'settledScenes', 'pageErrors'];

const run = (dt) => {
  const args = [SCORE, SRC, '--dt', String(dt)];
  if (JIT) args.push('--jitter', String(JIT));
  const out = execFileSync(process.execPath, args, { encoding: 'utf8', maxBuffer: 1 << 26 });
  return JSON.parse(out.split('\n')[0]);
};

const dts = [DT, DT * (1 + EPS), DT * (1 - EPS)];
const runs = dts.map(run);

const band = {};
for (const f of FIELDS) {
  const v = runs.map(r => r[f]);
  if (typeof v[0] === 'number') {
    const lo = Math.min(...v), hi = Math.max(...v);
    band[f] = { lo, hi, spread: +(hi - lo).toFixed(3), relSpread: hi ? +((hi - lo) / hi).toFixed(4) : 0, stable: hi === lo };
  } else band[f] = { values: v, stable: v.every(x => x === v[0]) };
}
console.log(JSON.stringify({
  file: SRC, clock: { dtMs: DT, jitterMs: JIT }, eps: EPS,
  // a metric that is not stable across three runs of the SAME FILE cannot
  // decide anything about a different file
  unstable: FIELDS.filter(f => !band[f].stable),
  band,
}, null, 1));
