# Recipes for the parts that fail up close

A picture passes at full view and fails at 2× zoom when its hard parts were improvised from
ellipses and flat fills. These are construction recipes for the parts that fail most. Each one
starts from structure (what the thing is made of and how light meets it), because a reviewer reads
structure at zoom, not colour.

Build a hero element as a study first (SKILL.md, step 5), at the size it will be seen zoomed in.

## Contents

- Foliage and tree crowns
- Grass and ground cover
- Polished metal and plate armour
- Mail and other fine repeating texture
- Cloth
- Small faces and hands
- Windows, glass and lit facades
- Glow, lamps and light falloff
- Wet ground and water
- Distant trees, hills and haze
- Dark passages
- Light direction, checked once

## Foliage and tree crowns

The failures: a crown made of coin-shaped dabs (reads as camouflage), a crown of overlapping blobs
with blob-shaped holes (reads as clip art), branches that stop at the crown's edge.

1. **Grow a skeleton first.** Trunk, then 3–6 main limbs, then secondary branches, each thinner and
   shorter, ending at the points where leaf clumps will sit. A deciduous crown is a set of clumps
   hung on branch tips, not one cloud. Seed the angles; keep a few limbs crossing.
2. **One clump per branch tip.** Each clump is a rough dome: a lit top-side mass toward the light, a
   mid-value body, and a shadowed underside that is darker and cooler. Three values per clump,
   always, so the crown has form at any zoom.
3. **Break every silhouette edge.** A clump's outline is not a smooth curve. Displace it with
   2–3 octaves of noise at leaf scale (`feTurbulence` + `feDisplacementMap` in SVG, or noise added
   to the radius in code), then scatter small leaf marks past the edge on the lit side.
4. **Let the branches show.** Between clumps, the darker branch segments stay visible, entering
   clumps from below. Sky holes go where clumps don't overlap, irregular in size, fewer toward the
   centre.
5. **Interior shadow.** Clumps nearer the trunk and lower in the crown sit in the crown's own
   shadow: darker and less saturated than the outer, upper clumps.
6. **Vary the outline, then lose some of it.** Give each clump its own edge scale (large lobes on big outer clumps, finer breakup on small ones), so the crown doesn't read as stacked paper cutouts with one wobble size. Where two clumps of similar value meet, drop the edge between them and let them merge; keep crisp edges only against the sky and where light meets shadow.
7. **A lit clump is not one flat fill.** It grades from its lightest top toward its body, and carries a few leaf-cluster marks along its lit edge and a darker accent where it tucks under the clump above.
8. **Leaf scale sets mark size.** At painting scale, a mark is a cluster of leaves, never a single
   leaf drawn individually unless it's in the near foreground.

## Grass and ground cover

The failures: evenly spaced strokes of one length and colour; a flat green slab.

- Paint the ground as value bands first (lighter far, darker near, a darker band under the
  subject), then texture.
- Blades are clustered, not distributed: tufts of 5–15 strokes from a shared base, varied in
  length, lean and value. Density follows the ground (thinner on paths and where something
  rests).
- Blade size shrinks with distance at the depth plane's scale; beyond a few metres, blades become a
  stippled texture and then just colour.
- Lit tips: in low sun, only the tips catch warm light; the bases stay in cool shadow.
- Where an object sits on grass, let a few blades overlap its lower edge. That is the contact.

## Polished metal and plate armour

The failures: smooth grey tubes with a few scribbled lines; metal lit like plastic.

Polished metal shows its surroundings more than its own colour. Build its shading from the
environment, in bands that follow the form:

1. **Environment bands.** On a convex plate, from the side facing up to the side facing down: the
   sky colour (lightest, coolest), a sharp dark band where the horizon reflects, then the ground
   colour (warm, darker). On a cylinder (limb), the bands run along the axis.
2. **One hot specular streak** where the light source reflects, thin, along the curvature, nearly
   white. One, not several.
3. **Rim light** on the edge facing a backlight, as a thin bright line; the face toward the viewer
   then sits in reflected ground colour.
4. **Edges have thickness.** Plate edges are turned or rolled: a thin light line over a thin dark
   line. Overlapping lames each cast a small dark shadow onto the plate below.
5. **Rivets and straps** at the joints, sized from references (rivets about 6–8 mm), each with a
   highlight and a shadow.
6. **Separate the plates.** A knee or elbow is several pieces (cop, wings, lames); a gauntlet has
   finger lames. Draw the pieces, then shade each one with the bands.

For a figure in armour whose pose foreshortens, render it with `render3d.md`. Its materials already
do environment reflection.

## Mail and other fine repeating texture

- Below the pitch where rings resolve (about 4 px per ring at the zoomed size), draw mail as
  value: a mid-dark grey mass with a lighter band where light hits, and a dark edge where it
  overlaps cloth. A dot pattern at sub-resolution pitch smears into a flat slab.
- Above that pitch, draw rings in rows that follow the body's form, with highlights on the lit side
  only.
- The same rule holds for bricks, roof tiles and window grids: a pattern either resolves at the
  zoom it will be viewed at, or it is painted as value, never half-resolved.

## Cloth

- Folds start at tension points (a shoulder, a belt, a knee) and radiate from them. Free-hanging
  cloth makes long vertical pipe folds; compressed cloth makes zigzag folds.
- Each fold is lit like a cylinder: a light side, a core shadow and reflected light. Saturation is
  highest in the halftone, not in the highlight.
- A thick fabric (wool surcoat) has broad, few folds; a thin one (linen) has many small ones.
- The hem shows the cloth's thickness and has a cast shadow below it.

## Small faces and hands

- At 40–80 px tall, a face is lit planes, not features: the brow ridge's shadow over the eyes, the
  side plane of the nose, the cheekbone plane, the shadow under the lower lip and chin. Eyes are a
  dark socket shape, not drawn lids.
- Keep the head's proportions measured (`anatomy.md`), and put the darkest dark of the head where
  the planes turn away from the light.
- Hands: one mass with the thumb as a separate wedge; fingers grouped, touching. In a gauntlet,
  follow the plate recipe.

## Windows, glass and lit facades

- Lit windows at night are sparse and clustered by floor and by flat, with variety: curtains, a
  lamp's warm pool, a blue screen glow, many dark.
- Glass reflects what faces it. Each pane gets its own reflection, offset by its position; never
  stamp the same diagonal on every pane.
- Window frames have depth: a recess shadow on the top and one side, a sill catching light.
- Signage is placed so nothing important crosses it, or is deliberately cut by a near object.

## Glow, lamps and light falloff

- A light source is a small hot core, a soft halo (a radial gradient or a blur), and a pool of
  light where it lands. Brightness falls off with distance; the pool is elliptical on the ground in
  perspective.
- Light changes the colour of what it touches: sodium lamps warm everything under them; screens and
  moonlight cool it.
- Halos sit over the sky or a wall, never drawn as a hard-edged translucent shape on top of
  objects.

## Wet ground and water

- A reflection sits directly below its source, flipped, broken into horizontal streaks that thin
  and fade toward the viewer, and darker and less saturated than the source.
- Only bright sources and strong shapes reflect visibly on wet asphalt; the rest is a dark sheen.
- Puddles have edges: the reflection stops at the waterline.

## Distant trees, hills and haze

- Far trees are silhouettes grouped into hedgerows and copses, not separate lollipops on sticks.
  Their bases sit on the ground plane, partly hidden by the land in front.
- With distance: lighter, cooler, lower contrast, softer edges, less detail. The farthest plane is
  close to the sky colour.

## Dark passages

The failure: shadowed areas (the shadow side of a trunk, the underside of a crown, a dark foreground) collapse into one muddy value with no structure, and a paint pass turns them to mud.

- A dark passage still has at least two value steps and one structure: bark furrows that follow the trunk, the edges of clumps, grass tufts. Make them visible as low-contrast shapes, not as black.
- Shadows are coloured: cooler and more saturated than the lit side, with warm reflected light near the ground or near a lit surface. A neutral grey-brown shadow is what reads as mud.
- Keep the darkest dark small and placed (the deepest crevice, the contact under the figure), not spread over the whole shadow side.

## Light direction, checked once

Before shading anything, write down the light: where the sun or main source is, its colour, and
the fill colour (sky, bounce). Then, for every element, the lit side faces the source.

- **Backlight** (sun behind the subject): the subject's front is in shadow, lit by cool sky fill
  and warm ground bounce, with a bright rim on the edges facing the sun. Cast shadows come toward
  the viewer.
- **Side light** gives the strongest form; **front light** flattens it.
- A mismatch (a backlit scene whose figure is lit from the front) reads as wrong even when the
  viewer can't say why.
