# render3d: the numpy figure renderer

`prototypes/art/render3d.py` (restore with `git checkout 35a27e6 -- prototypes/art`) renders a figure in 3D and returns an RGBA image. A scene file embeds that image in its SVG. Use it for any figure whose pose foreshortens: a seated or turned body, limbs toward the viewer, armour or cloth that has to wrap a body. Flat 2D paths can't fake that. The first two Henry versions were 2D and drew the "proportions are off" note. `prototypes/art/knight.py` is the worked example; copy its structure.

## Contents
- Conventions
- Building a mesh
- Materials
- Cloth
- Posing
- Rendering and embedding
- Debugging
- Pitfalls that cost hours

## Conventions

- Units are centimetres. World axes are x right, y down, z toward the viewer. That is a left-handed frame, so a cross product points the opposite way from what you'd guess. Build body frames from explicit vectors, as knight.py does. Its `F_` is forward, `R_` is his right and `U_` is up. `B(f, u, r)` and `Tp(h, f, r)` map body-frame coordinates to world.
- The camera is orthographic and pitched down by `PITCH` (14°). `project(P)` returns screen xy (cm) and depth (larger is nearer). `VIEW` is the direction toward the camera.
- `SUN` is the light direction. Keep it consistent with the light in the painted scene. For Henry the light comes from the right and slightly toward the viewer.
- A figure's origin is its hip midpoint. The scene file pins that origin to a scene point (`SCN` in henry.py) at `S_H` scene units per cm. Real proportions come from real measurements: thigh 44, shin 42, upper arm 33, forearm 26, hip joint to shoulder joint about 50, for a 180 cm man.

## Building a mesh

Everything is a `Mesh` of parametric grids. `mesh.grid(P, mat, uv=None, wrap=False, cut=None, bump=None, obj=None, line=True, period=None, **material_kwargs)`:
- `P` has shape (a, b, 3). With `wrap=True` the first axis closes into a loop, and `period` is the u length of one turn.
- `uv` should run in centimetres along the surface. Bump widths, cut sizes and mail ring pitch all assume that. If you leave it out, it is computed as arc length.
- `cut(uv) -> keep mask` cuts holes per pixel, before the depth test. Use it for dagged hems, eye slits, breaths and pointed gauntlet cuffs.
- `bump(uv) -> height in cm` perturbs the normal. Use it for ribs, turned edges, lames, quilting, fullers and rivet rims. The helpers in knight.py are `bands(at, w, amp, axis)` for lames and `quilt(period, depth)` for quilted channels.
- `obj` groups parts for the ink outlines. Parts with the same `obj` get no line between them. `line=False` hides a part's outline, which suits small rivets and things meant to sit under another surface.
- Normals are oriented outward automatically, from the part's centroid.

Shape helpers:
- `tube(mesh, spine, radii, hint, mat, nu=36, sq=2)` builds elliptical sections along a spine. `hint` orients the first radius. `sq` above 2 makes the section boxier. The section angle runs from -π to π, starting at `hint`. Any uv-dependent bump or cut has to use the same origin.
- `ellipsoid(mesh, c, axes, radii, mat, ph=(lo, hi))`: rows of `axes` are the local x, y and z. Use `ph` for caps, as `knight.cap()` does.
- `spline(points, k)` and `resample(points, k)` make smooth spines.
- knight.py also has `limb(a, b, t0, t1, radii, hint)` for plate on a bone, `cap()` for couters and poleyns, `wing()` for fan-shaped side wings, `finger()`, `ribbon()` for straps, `sect()` for torso sections, and `ik(S, W, l1, l2, pole)` to solve a two-bone arm or leg.

## Materials

Materials are registered with `@mat` in render3d.py and take `ctx` (P, N, uv, sun, ao, TU, TV):
- `steel(tint, gain, base, rough, spec)` reflects the scene through `env(R)`. `env()` is a hand-made environment: canopy above, trunk to the left, sunlit fields to the right, meadow below. **Rewrite `env()` for each era.** Steel only looks right when it reflects the world it stands in, such as an ink-wash void, neon streets or an alien sky.
- `cloth(albedo, shade)` uses wrap-diffuse with sky and ground ambient.
- `leather(albedo, shade, gloss)` is cloth with a sheen.
- `mail(tint, pitch, ring, wire, gap)` draws procedural rings from uv. Make rings big enough (pitch about 0.86 cm) and contrasty, or the stylization pass smears them into a flat grey slab. The user zoomed in and caught exactly that.
- `void()` is near-black. Put it inside helmets so slits and breaths read as dark.
- `cloth`, `void`, `mail` and `leather` are two-sided (the `TWO` set). Steel backfaces render as dark interiors.

## Cloth

`drape(X0, pinned, cols, steps, iters, gravity, rest, wrap, friction, bend)` is a Verlet sheet:
- Row 0 is pinned, and `rest` holds the pattern shape that defines rest lengths.
- Colliders are `('cap', a, b, r)`, `('ell', centre, axes, radii)` and `('floor', y)`.
- `push_out(X, cols, pad, hit)` pushes particles out of the colliders.
- `relax(X, n)` (in knight.py) smooths creases after a sim.

Recipes that worked:
- **Trace, then relax.** Build `X0` by marching each column out from its pin and calling `push_out` at every step. Follow the surface when the column hits something; otherwise drift toward gravity. Then run a short sim with high friction (0.97) and full bending. Starting from a hanging pose and animating the legs into place let the thighs pass through the cloth.
- **Colliders must match what the viewer sees.** The aventail slid under a padded shoulder until the shoulder's own ellipsoid became a collider.
- **Layer cloth along `VIEW`, not along the normal.** For mail under a dagged skirt, offset the mail backward along `VIEW`. Draped normals flip at folds and would put the mail on top.
- **Read physics as a design choice.** With a knee raised 45°, a skirt cannot climb the thigh; it covers the hip and falls aside. Accept that, or change the pose, instead of fighting the sim.

## Posing

Use a `Skel` class with named joints. Place the legs with `onto()`, which puts the ankle at a given height for a given heading. Put hands on targets with `ik()`, for example the forearm across the knee and the hand on the thigh. Check the result against the reference before dressing the figure. A greyscale mannequin of capsules and spheres takes a second to render and catches pose errors early.

Head pose: `head_frame` has yaw, droop and loll. A sleeping head turns with the body, drops its chin and lolls toward a shoulder. Watch the helmet's lower edge against the shoulders when lolling: past about 20° it sank into the doublet.

## Rendering and embedding

`render(mesh, ppcm, origin, size, ss=2, lines=.85, light=None)` returns `(premultiplied rgb, alpha, info)`. It:
- supersamples by `ss` and z-buffers the triangles
- applies cuts and bumps
- lights with a shadow map plus screen-space occlusion, and runs the optional `light(P)` multiplier (leaf dapples)
- draws ink outlines at object and depth edges

`ground_shadow(info, ppcm, origin, size, G)` gives the alpha of the cast and contact shadow on the ground plane.

Render at device resolution: `ppcm = S_H * ZOOM * SCALE`, using the scene file's constants. henry.py's `knight_layers()` shows the embed:
- three PNGs as data URIs: the paint, the ground shadow and a binary mask for the depth pass
- the mask is coloured `rgb(round(z / 100 * 255), REGION[z], 0)` so the stylization pass classifies the figure correctly
- one `<image>` box in scene units, inside `group(..., z)`
- the shadow is left out in depth mode

## Debugging

- `scripts/angles.py` renders any mesh builder from three yaw angles, for example `uv run --with numpy --with scipy --with pillow python <skill>/scripts/angles.py --module knight --code 'mesh = build()' --out angles.png`. `--module` is a module in `prototypes/art`, and `--code` runs in its namespace and must assign `mesh`. Use it for cloth that seems to vanish, armour that clips, or a helmet you want to check against front, three-quarter and side references.
- Preview at final scale: render the scene once with the figure stubbed out (`module.henry = lambda mode: ''`), composite the figure render over it, and crop. One full pipeline run costs about a minute. A preview costs about five seconds.
- The user zooms in on the final image. Check a zoomed crop of the stylized output, not only the raw render.

## Pitfalls that cost hours

- **Normal signs.** Flipping per vertex (`np.sign(..., keepdims=True)`) breaks orientation. Use one global sign per sheet.
- **Angle origins.** Any uv-dependent cut or bump on a tube has to use the tube's angle origin, which runs from -π to π starting at `hint`. A mismatch put a gauntlet's cuff point on the wrong side and sabaton lames on the sole.
- **Small triangles.** The rasterizer buckets triangles by bounding box, so keep grids fine enough that triangles stay under about 16 px. Huge triangles still work, only slowly.
- **Skin inside armour.** If the cloth sleeve's radius is larger than the plate over it, the plate disappears. Keep cloth under plate radii where they overlap.
- **Cloth under an IK limb.** When the hips move, re-trace the skirt; the old drape won't follow.
