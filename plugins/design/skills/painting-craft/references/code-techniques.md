# Painting in code

These techniques recur whatever the subject.

**SVG**
- Document order is z-order. Build each depth plane as its own group, in back-to-front order, and insert moving elements at the depth they travel at.
- `mix-blend-mode: multiply` on overlapping same-colour shapes darkens every overlap. Put each tint in one group and blend the group, so shapes merge instead of stacking.
- Tile windows, bricks or halftone with a `<pattern>` anchored to one global origin, and snap shapes' edges to its grid. Otherwise the pattern cuts its cells in half at every edge.
- Filters and gradients must be defined in the same document that renders them. A layer rasterised separately does not see the page's defs, and the page does not see the rasterised layer's.
- Use `clipPath` to stop a shape at a horizon or region instead of trusting its outline.
- Fit text to a box with `textLength` and `lengthAdjust="spacingAndGlyphs"`. Glyph-width estimates overflow.
- Put labels and signs with a placement pass. Collect obstacle boxes for every placed item and every occluder (trunks, crowns, frames), then try several positions per anchor and keep the first one that is clear.

**Randomness and iteration**
- Seed every random stream, so a picture is reproducible.
- To add random elements without moving the ones the user already approved, draw from a new seeded stream. Never insert calls into the old one. When you reorder code, keep the old stream's call order unchanged.
- Keep magic numbers as named constants in real units (px per metre, floor pitch, heights), so the next edit can reason about them.

**Animated and multi-state scenes**
- Test the in-between frames, not only the end states. Widths, heights and positions should interpolate cleanly.
- For moving objects, take several screenshots a fraction of a second apart, so each one is caught passing something.

**Raster passes and 3D figures**
- Paint the scene in 2D, where you control the style. Model posed figures in 3D, where proportion and foreshortening must be right. Then run one stylisation pass over everything. `render3d.md` covers the renderer, cloth, IK and the pitfalls that cost hours.
- Preview a figure at final scale over a cached scene before running the full pipeline.
