# Voronoi Bento Generator - Architecture & Codebase Guide

**Live site:** https://voronoi-bento.netlify.app/

An interactive web experiment exploring organic, cell-based bento-box grid layouts. Two self-contained implementations demonstrate different computational approaches to the same idea: clickable cells that respond fluidly to hover, squeeze neighbors aside, and transition between layout orientations.

---

## Repository Structure

```
Voronoi/
├── index.html        # Landing page — hub linking to both versions (137 lines)
├── voronoi.html      # Primary implementation — computed Voronoi tessellation (3,027 lines)
├── softbody.html     # Experimental implementation — constraint-based solver (911 lines)
├── netlify.toml      # Netlify deployment config (static site, security headers, caching)
└── README.md         # One-liner project description
```

**Key architectural decision:** Each HTML file is completely self-contained — all CSS and JavaScript are inline. There are zero external dependencies, no build step, no framework, and no package manager. The site deploys by pointing Netlify at the repo root.

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Vanilla JavaScript (ES6+) |
| Rendering | HTML5 Canvas 2D API |
| Styling | Inline `<style>` blocks |
| Framework | None |
| Build tool | None |
| Hosting | Netlify (static) |
| External APIs | picsum.photos (optional image loading) |

---

## The Two Implementations

### 1. Computed Voronoi (`voronoi.html`) — Primary

The main, fully polished version. Cells are positioned by computing a Voronoi tessellation from seed points, then animating those seeds when the user interacts.

**How it works at a high level:**

1. Seed points are placed inside a configurable "content zone" (a rotatable rectangular region)
2. A Voronoi diagram is computed from those seeds, producing polygonal cell boundaries
3. On hover, the hovered cell's seed inflates outward, pushing neighboring seeds away
4. The Voronoi diagram is recomputed each frame with the displaced seeds
5. Cells are rendered with rounded corners, optional images, opacity effects, and glow borders

**Key concepts:**

- **Content Zone** — A soft rectangular boundary that constrains where cells live. It can be rotated (0/45/90 degrees), positioned (offset left/right), and margined. Three presets ship out of the box: horizontal bar, vertical bar (left-aligned), and diagonal.
- **Displacement** — When you hover a cell, neighbors are pushed away. The push uses exponential distance falloff (`displaceRatio`, `displaceFalloff` params). This is what makes it feel like the hovered cell is "inflating."
- **Flock Transitions** — Switching between layout presets (horizontal -> vertical, etc.) uses boid-like flocking: cells steer toward their target positions with arrival seeking + separation avoidance, with staggered departure times for a cascading visual effect. Polygon shapes morph during transit.
- **Bleed Buffer** — Cells extend slightly beyond the content zone boundary so the hovered cell can inflate without hard-clipping at the edge.

### 2. Soft Body Physics (`softbody.html`) — Experimental

A fundamentally different approach: no Voronoi computation at all. Instead, cells are soft polygons (12 vertices each) that behave like water balloons, and tessellation *emerges* from them pressing against each other and the container walls.

**How it works at a high level:**

1. Each cell is a ring of vertices forming a closed polygon
2. An iterative constraint solver runs 20 passes per frame, enforcing:
   - **Edge length limits** — Edges can't stretch beyond 1.8x or collapse below minimum
   - **Area preservation** — Cells maintain their target area (like incompressible fluid)
   - **Convexity** — Concave vertices are pushed outward
   - **Aspect ratio** — Cells can't deform beyond 2.5:1
   - **Self-intersection** — Detected and reset to a circle
   - **Wall bounds** — Cells stay inside the container
   - **Cell-cell separation** — Cells maintain a minimum gap
3. Free-floating cells slowly return to circular shape
4. Users can drag cells around and watch them squish and settle

**Constraint solving order matters.** Each frame runs: hard constraints (convexity, self-intersection, aspect ratio) -> shape constraints (edges, area) -> cell-cell separation -> wall bounds -> hard constraints again. This two-pass approach on hard constraints ensures stability.

---

## Voronoi Implementation Deep Dive

### Main Classes

**`Cell`** — Represents a single grid cell.

Core properties:
- `baseX, baseY` — Seed position from the Voronoi diagram
- `displacedX, displacedY` — Where the seed actually renders after hover displacement
- `scale` — Current scale (1.0 = resting, >1.0 = hovered/expanding)
- `displayPolygon` — The clipped, gapped, final polygon points for rendering
- `pattern` — Canvas pattern for image fill (loaded from Unsplash)
- `hoverMix` — 0-1 float for how "hovered" this cell currently looks

Key methods:
- `update(dt, isHovered)` — Advances animation state (scale, opacity, zoom) using easing
- `render(ctx, cornerRadius)` — Draws the cell: clip path, fill/image, border, glow

**`FlockTransition`** — Manages animated layout preset switches.

When triggered, each cell becomes a "boid" that:
- Steers toward its target position (arrival seeking)
- Avoids other cells (separation)
- Departs on a staggered schedule (cascading effect)
- Morphs its polygon shape mid-flight

### Rendering Pipeline (per frame)

```
requestAnimationFrame(animate)
  │
  ├─ If transitioning between presets:
  │    └─ FlockTransition.update(dt) → FlockTransition.render()
  │
  └─ Normal mode:
       ├─ updatePhysics(dt)
       │    ├─ Set target scales (hover vs. resting)
       │    ├─ computeDisplacementTargets()  — push neighbors away
       │    ├─ cell.update(dt) × N           — animate each cell
       │    └─ updateDisplayPolygons()       — clip & gap polygons
       │
       ├─ render()
       │    ├─ Clear canvas
       │    ├─ Draw non-hovered cells (back-to-front)
       │    └─ Draw hovered cell last (always on top)
       │
       ├─ updateTooltip()
       └─ updateFpsCounter()
```

### Controls Panel

The bottom bar exposes real-time parameter tuning:

| Control | Config Key | What It Does |
|---------|-----------|--------------|
| Cells | `cellCount` | Number of Voronoi cells (1-30) |
| Gap | `gap` | Pixel spacing between cells |
| Radius | `cornerRadius` | Border radius on cell polygons |
| Expansion | `maxExpansion` | How much the hovered cell inflates |
| Push | `displaceRatio` | How strongly neighbors are displaced |
| Falloff | `displaceFalloff` | Spatial reach of displacement |
| Dim Others | `nonHoveredOpacity` | Opacity of non-hovered cells |
| Image Zoom | `nonHoverImageZoom` | Zoom level on non-hovered images |
| Layout presets | `currentPreset` | Horizontal / Vertical / Diagonal |
| Zone Margin | `contentZoneMargin` | Padding inside the content zone |
| Zone Angle | `contentZoneRotation` | Rotation of the content zone |
| Position | `contentZonePosition` | Offset perpendicular to zone orientation |
| Bleed Buffer | `bleedBuffer` | How far cells extend past zone boundary |
| Trans Speed | `transitionSpeed` | Speed of layout transitions |
| Zone toggle | `contentZoneEnabled` | Show/hide content zone boundary |
| Debug toggle | `debugMode` | Show seed points, zone outlines, etc. |
| Unsplash | — | Loads random images into cells |
| Regenerate | — | Randomizes seed positions |

### Animation System

Five easing functions are used throughout:
- `cubicBezierEase(t, p1, p2)` — Custom cubic Bezier (for hover expansion)
- `easeOut(t)` — Quadratic ease-out
- `easeIn(t)` — Quadratic ease-in
- `easeInOut(t)` — Smooth ease in/out
- `easeOutSmooth(t)` — Extra-smooth ease-out (for opacity)

All animations use delta-time (`dt`) capped at 3 frame intervals to prevent physics explosions after tab-switch lag spikes.

### FPS Monitor

A collapsible overlay in the bottom-left shows:
- Current FPS (color-coded: green > 50, yellow > 30, red below)
- Average / Min / Max
- Frame time in ms vs. 16.7ms target
- 60-point history graph (SVG sparkline)

---

## Soft Body Implementation Deep Dive

### `SoftCell` Class

Each cell is a polygon ring:

```
constructor(x, y, radius, color)
  → verts[]: 12 vertices evenly spaced on a circle
  → targetArea: π * r² (preserved by constraint solver)
  → restLength: circumference / vertex count
```

### Constraint Solver (per frame, 20 iterations)

```
For each iteration:
  1. HARD constraints (per cell):
     - checkAndFixSelfIntersection()  → if edges cross, reset to circle
     - constrainConvexity()           → push concave verts outward
     - constrainAspectRatio()         → limit to 2.5:1
  
  2. Shape constraints (per cell):
     - constrainEdges()               → min/max edge length
     - constrainArea()                → maintain target area
     - constrainReturnToSphere()      → free cells drift toward circle
  
  3. Cell-cell constraints (all pairs):
     - constrainCells(a, b)           → maintain gap between surfaces
  
  4. Wall constraints (per cell):
     - constrainWalls()               → keep inside container
  
  5. HARD constraints again (same as step 1)
```

### Rendering

- Smooth curves via quadratic Bezier between vertices (midpoints as control points)
- Radial gradient fills (lighter center, darker edge, with color variation)
- Stroke outlines for definition

### Interaction

- Click and drag any cell — constraint solver keeps everything valid
- Add/Remove cell buttons
- Reset button (reinitialize layout)
- Real-time sliders for iterations, gap, vertex count, radius, and all constraint tuning params

---

## Landing Page (`index.html`)

Minimal hub with two cards linking to each implementation:

- **Computed Voronoi** — tagged "Current"
- **Soft Body Physics** — tagged "Experimental"

Dark theme, responsive flex layout, hover animations on cards.

---

## Deployment

**Netlify** serves the repo root as a static site with no build step.

`netlify.toml` configures:
- Security headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, strict referrer policy
- HTML: no-cache (always fresh)
- JS/CSS: 1-year immutable cache (irrelevant currently since everything is inline, but future-proofed)

---

## State Management

Both implementations use plain global variables — no stores, no reactive system, no pub/sub.

**Voronoi globals:**
- `cells[]` — Array of `Cell` objects
- `hoveredCell` — Index (-1 if none)
- `mouseX, mouseY` — Cursor position
- `config` — All tunable parameters
- `flockTransition` — `FlockTransition` instance
- `fpsHistory[]` — Performance tracking

**Soft Body globals:**
- `cells[]` — Array of `SoftCell` objects
- `draggedCell` — Currently dragged cell (null if none)
- `config` — Constraint parameters
- `container` — Bounding box `{x, y, width, height}`

---

## Performance Notes

- Target: 60 FPS on modern hardware
- Canvas-only rendering (no DOM reflow during animation)
- Delta-time capping prevents lag spikes from cascading
- Hovered cell renders last for correct z-ordering without sorting
- Soft body uses O(n²) pair-wise collision — works fine for <30 cells
- No WebGL; everything is CPU-bound through Canvas 2D

---

## Development History

113 commits across ~150 PRs (many are iterative refinements). The project evolved through:

1. Initial Voronoi bento grid
2. Hover displacement system
3. Content zone and layout presets
4. Flock transition animations
5. FPS monitoring
6. Unsplash image integration
7. Soft body experimental branch (pure constraint solver, no physics engine)
8. Iterative constraint hardening (convexity, self-intersection, aspect ratio)
9. Netlify deployment setup

Branch names suggest heavy use of Claude-assisted development (`claude/fix-*`, `claude/review-*`, `codex/audit-*`).
