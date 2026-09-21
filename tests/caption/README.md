# Caption: quieter, functional labels

Baseline: accepted Skim from PR #265, commit
`9c920afdaabcf2513a5075555415995c25a5d791`, Git blob
`82ab2447f173d707bcd690b9dcf39adb4e01ff45`.
The exact source is included as `skim.html`; the builder checks its SHA-256.

## Visible change

Numbers are centered on the largest painted component's inscribed ink polygon,
using its area centroid. They have no separate positional spring, pole hunting,
or size animation. Root numbers use 32px type, nested numbers 20px, and names
12px. Hover does not change those sizes. Smaller text has higher contrast than
Skim's oversized translucent numerals.

Names sit 27px below the centered number. A narrow cell can keep its number
while the name fades away. If the number cannot fit either, it fades too. Both
use fit hysteresis and time-based opacity easing; they retain the exact existing
ink clip, including holes. Text fitting combines containment and squared edge
distances in one pass; opacity rates are shared for the frame. Text follows the cell's changing geometry; it is not
fixed to the viewport. A centroid outside a concave component has no readable
space and suppresses the text rather than searching for another location.

No header controls were added. Footer controls, cell rendering, solver,
transitions and hover expansion remain the accepted Skim implementation.

## Preserve cell motion

Skim's label target also steered free-moving cells. Simply replacing its label
function would have changed cell motion. Caption retains that target selection
as `driftAnchorStep`, with identical arithmetic, sampling and hysteresis, and
stores it independently in `body.anchorState`. Only the old text spring and
size interpolation are removed. The new `body.caption` controls text alone.

This deliberately retains the pole searches needed by steering. Caption is a
text behaviour change, not a claim that all of the old label-search cost has
been eliminated. Skim's performance optimizations remain in place.

## Verification

The real inline tick runs against the pinned Skim source with native Canvas
calls and browser DOM writes stubbed:

- 13,506 frames have exactly equal cell/steering state, final leaf geometry and
  gap/overlap meter results, excluding measured solve duration and intended text
  state. Movement-anchor target state is also compared explicitly.
- 714,704 cell fill/stroke operations match exactly, including paths, gradients,
  opacity, stroke width and shadow blur. Text output is intentionally different.
- Covers all layouts, both void crossings, hover/release, interrupted changes,
  Organic/Grid fields, add/remove and resize, at 120 Hz, 60 Hz, 30ms and 50ms.
- All emitted text uses one of the three fixed fonts; coordinates and opacity
  are finite and bounded. Compact number-only captions occur in the real
  viewport fixtures, including narrow/mobile cells.
- At 1900x810 with 12 root cells and Fields 0%, every settled layout displays
  all 12 numbers. Hero displays 11 names; the other layouts display all 12.
  A settled cell still acquires hover and expands with its number visible.

The validation proves preservation of the cell engine, not a subjective claim
about perceived calmness. The Netlify preview is the visual evaluation.

`benchmark.json` records five alternating-order pairs per workload after two
warmups per mark. It executes the full tick and includes paint geometry and
steering anchors, while excluding native Canvas/GPU/DOM work. This is a CPU
regression check, not a browser FPS benchmark.

## Reproduce

From the repository root:

```sh
python3 tests/caption/build.py
node tests/caption/validate.cjs
node tests/caption/benchmark.cjs
```

The builder writes only `caption.html`. The gallery entry is maintained as an
ordinary `index.html` change against current main. Prior marks are unchanged.
