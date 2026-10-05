---
name: painting-craft
description: Draw and paint scenes, figures, creatures, vehicles, buildings and landscapes in code (SVG, canvas, numpy, Blender) to a gallery standard, with a screenshot-and-zoom review loop. Use it whenever you draw, paint, illustrate or animate anything in code, and when someone pastes reference art, says a picture looks off, cheap, flat, floating, out of proportion or in the wrong depth order, or asks for armour, costume, architecture, vehicle or canon research for a picture.
---

# Painting craft

A picture made in code fails in four ways, and a reviewer names them quickly:
- **Proportion:** a horse 1.6× too long, a helmet too big, a car that "does not look like a car".
- **Aesthetic:** "it looks like a kid drew it", or the wrong art tradition for the subject.
- **Space and structure:** houses floating above a hill, a car driving in front of trees it should pass behind, a city stranded across an empty plain.
- **Accuracy:** guessed costume, the wrong armour for the cover art, a Chinese landscape for a Japanese island.

Each failure is cheap to prevent early and expensive to fix late, so this skill is ordered as a workflow. Its rules come from real reviews of real paintings. The reviewer zooms in, judges the medium before the subject, and often can't name what is wrong, only that something is.

## References

Read `recipes.md` before any picture with foliage, grass, metal, cloth, faces, windows, lights or water; then only the others the picture needs:
- `references/recipes.md`: how to build the parts that fail at zoom (foliage, grass, plate armour, mail, cloth, small faces, windows, glow, wet ground, haze) and how to fix the light direction.
- `references/anatomy.md`: human, seated, horse, dog and car measurements, pose geometry, ratios to check.
- `references/scale.md`: one scale per depth plane, bridging scales, horizon and ground, buildings, streets, trees, reflections, atmosphere.
- `references/armour.md`: European armour around 1400, layering, and how to brief costume research for any period.
- `references/render3d.md`: the numpy 3D figure renderer, for any figure whose pose foreshortens.
- `references/code-techniques.md`: SVG, seeded randomness, animated scenes and raster passes. Read it before writing the picture's code.

## Taste comes first

Two people can ask for the same picture and reject each other's result. Before a new picture, find out how this person sees art, because it decides the tradition, the finish and how hard the review will be.

1. **Look for a record.** A project may keep the person's taste in a rules file or a note its `CLAUDE.md` points to (for example `.claude/rules/painting-taste.md`). If one exists, read it and skip the questions.
2. **Otherwise ask, briefly, with examples.** Ask which artists or works they love for this kind of picture; whether they will zoom in and judge fine detail or look at the whole from a distance; whether they want a quick sketch or a finished piece; and what has disappointed them in pictures before. Offer two or three named traditions to pick from rather than an open question.
3. **Offer to save the answers** as that project's taste note, in their words, each followed by the rule it implies. Update it when a later review teaches something new, so their notes become predictable.

How much the person cares about detail sets how far to take steps 5–9 below: a sketch for someone who looks from a distance still needs a sound space and value plan, but not measured hands.

## Workflow

A picture rarely fails as a composition. It fails in its parts: a crown of blobs, armour made of tubes, grass in even strokes. Those failures are invisible at full view and obvious at 2× zoom, and patching them after the picture is composed costs round after round of review. So build and judge the hard parts on their own first, against a reference, before they go into the picture. Skip a step only when the picture has nothing it applies to, and say so.

1. **Pin the tradition and get references.** Name the art tradition with two or three named works, and fetch them: `python3 scripts/refs.py "<artist or subject>" <dir>` (Wikimedia Commons), or `--source met` for armour, costume and objects. Look at them with the Read tool. Get references for each hero element too (an oak, a 1400 harness, a 1990s sedan). An era or place names a subject, not a style.
2. **Research.** Gather canon, history and real dimensions, with sources. Mark guesses UNVERIFIED.
3. **Set up the space and the light.** Choose the horizon, the camera's height and pitch, the ground plane, and a scale in px per metre for each depth plane. Write down the light: source position, its colour, the fill colour (`recipes.md`, last section).
4. **Block in masses.** Big shapes and a value plan only, nothing detailed yet. Screenshot it: if the value plan doesn't read as a thumbnail, no detail will save it.
5. **Study the hero elements.** For each element a viewer will zoom into (the figure, the main tree, the vehicle, the building nearest the viewer), build it alone, at the pixel size it will have at 2× zoom, from its recipe in `recipes.md` and its measurements. Put it beside its reference with `scripts/compare.py` and name every structural difference: edges, value steps, shapes, how light meets it. Fix and compare again until it holds up. A study is cheap; a finished picture with a weak tree is not.
6. **Compose.** Place the studied elements at their depth planes, scaled, and fill the rest from the same recipes at lower detail.
7. **Ground everything.** Contact, cast shadows, and overlaps in depth order.
8. **Unify.** One light and one medium over everything. For a painted tradition (oil, gouache), render the composed picture to PNG and run `scripts/paintpass.py` over it (with `--focus` on the subject, and `--depth` if you have a depth mask), so every part shares the same brushwork. The pass unifies; it cannot rescue a weak drawing underneath. Flat-vector and graphic styles skip it: their finish is crisp edges and exact shapes, which brushwork smears.
   **Deliver at the zoomed size.** The viewer zooms in, so the final image is rendered at twice its display size (3200 × 2000 for a 1600 × 1000 picture), and the paint pass runs at that width with half-size brushes (`--width 3200 --brush 0.5`), so the extra pixels become finer strokes rather than the same strokes twice as big. A picture rendered at display size and scaled up goes soft exactly where the viewer looks.
9. **Review zoomed in,** with the screenshot loop and the checklist at the end of this file, on every viewport and every state the picture has.

## Proportion

**Measure, don't eyeball.** Build every figure, animal and vehicle from real dimensions, and write down where each number came from. Eyeballed figures came out 1.6× too long, twice. `anatomy.md` has the tables. When a character has no canon height, use a named proxy, such as the actor's height, and say so.

**Turned figures go 3D.** A figure that faces the viewer, sits, or points a limb at the camera must foreshorten, and flat 2D plates can't fake that. Model such figures in 3D (`render3d.md`) and embed the render. 2D only works for figures in near-profile.

**Pose with physics.** A pose must be reachable and carry its weight:
- Solve limbs onto their targets with two-bone IK rather than guessing angles.
- Whatever carries weight shows it. A back resting on a tree leans into it, and the shoulders settle.
- A sleeping head turns with the body, the chin drops, and the head lolls toward a shoulder.
- Check the joint heights. A vertical shin puts the knee nearly at shoulder height when seated, so an arm resting on it strains.

**Layer from the body out.** Body, padding, mail, plate, then outer cloth. Each layer is wider than the one beneath it wherever they overlap, or the outer layer vanishes into the inner one. Armour and props have real sizes; check them against museum or maker dimensions.

**Machines have anatomy too.** A vehicle is read as fast as a face. Measure it (length, height, wheelbase, wheel size), and draw the few marks that make it read: wheels in arches with dark wells, split glass, a door line, lights, and a contact shadow.

**Give hands mass.** At painting scale a hand is about 40 px. Draw it as one unit, with fingers touching and a clear cuff. Separate thin fingers read as claws.

## Aesthetic

**Name the tradition, then match it.** "Medieval" turned out to mean a Romantic academic oil painting, not a medieval manuscript. Tsushima needed Japanese ink-wash conventions and Japanese terrain, not the needle peaks of Chinese landscape painting. Paint a real place in its own culture's tradition, and confirm the tradition with the user when the brief is only an era or a place.

**Know what reads as amateur:** flat fills, even outline weight, primitive shapes, regular spacing (rows of trees, dotted clouds, a uniform grid of lit windows), no value plan, no atmospheric depth, and detail spread evenly everywhere. The fixes:
- Masses before detail. Clouds are clusters with a flat base, a lit side and a shadow side.
- A value plan. Keep the light and shadow families apart, and put the darkest dark and the lightest light at the focal point.
- Atmospheric perspective. Distance is lighter, cooler, lower in contrast and softer.
- Warm light, cool shadow.
- Varied edges, some lost and some found. A glow is a soft gradient or blur, never a hard-edged translucent rectangle.
- Organic irregularity: noise, clusters, overlaps, gaps. Lights on a night facade are sparse and clustered, and accents (neon, highlights) go on a few edges, not around every shape.
- A detail hierarchy: crisp near the subject, simplified elsewhere.

**Get materials right.** Polished metal shows its surroundings, so give it an environment that matches the scene. A saturated red needs a deep, slightly cool shadow. Fine repeating texture, such as mail rings or windows, needs a pitch the medium keeps; otherwise it smears into a flat slab.

**Match detail to the medium.** The stylisation decides the smallest readable mark: a halftone dot pitch, an oil brush, an ink bleed. Enlarge what must read, and leave out what can't. Judge a zoomed crop of the stylised output, not the raw render.

**Unify the picture.** One light lights everything, figures included. One medium pass covers everything; a 3D figure only looked painted once the same pass covered it. Keep outline weights consistent.

**A change of era or state swaps its objects.** When a scene turns between eras, seasons or day and night, every object that belongs to one state gets its own version in the other: vehicles, signs, clothing, street furniture. A recoloured 2013 car still reads as 2013 in 2077. List those objects before building, and crossfade between the versions.

## Space and structure

**One space.** Fix the horizon and camera before placing anything. Nearer ground sits lower on the canvas, and things shrink with distance at one rate. Every object stands on that ground plane, at the scale of its depth plane (`scale.md`).

**Draw order is depth.** Decide each object's depth from where it touches the ground, not from when it was coded, and paint back to front. A row of trees on the near verge is nearer than the road, so traffic passes behind the trunks. Anything that moves crosses everything on its path; check its order against each object it passes, at both ends of the path.

**Bridge the scales.** Two depth planes at very different scales need something between them, or the gap reads as wrong even when the viewer can't say why. Fill the middle distance with things at the scales in between, close the gap with telephoto compression (put the far plane's base right behind the near plane), or explain it with water.

**Seat things on their support.** Place buildings and objects on the terrain's height function, sink foundations slightly into the ground, and give each a contact shadow. Roads climb hills and reach gates. A bough starts inside its trunk. Canopy clumps overlap their branches. Roots flare into the ground.

**Draw contact.** Anything at rest touches what holds it up, with a dark accent where the two meet: occlusion, a contact shadow, or the nearer object overlapping. A sword point is in the grass. Feet are planted at ankle height. A car sits on its tyres' contact line with a shadow under it.

**One light.** Cast shadows fall away from a single source and soften with distance from the caster. A rendered figure needs a ground shadow catcher, or it floats.

**Reflections need a surface.** Only wet, glossy or still surfaces reflect, and they reflect what is directly above them. Wet asphalt and rippled water break a reflection into horizontal streaks that thin out toward the viewer.

**Every edge is intended.** Wherever two shapes meet, the join should be deliberate. Stray lines come from overlapping paths drawn in the wrong order, and smoothed closed curves bulge past their end points. Clip shapes to the region they belong to.

**Re-check after moving the frame.** Moving the horizon, the camera or the layout moves everything placed relative to it. After any such change, re-check the labels, the placed props, the clipped regions and the overlaps.

## Accuracy

**Reference images are the spec.** Follow them closely. When several disagree, follow the majority and name the one you set aside.

**Research before drawing.** Brief a `researcher` agent for shapes and sizes, not essays: each piece's name, shape and size in centimetres or metres, the layering order, what the game's own art shows, source URLs, and guesses marked UNVERIFIED. Good sources:
- the game's cover art, key art and in-game stills; ask the user for screenshots when wikis block fetching
- museum collections, for period costume
- makers' spec pages, for sizes
- Wikipedia and survey data, for buildings and places

**Keep the date and place consistent.** Check each costume piece and each building against the setting's date and region. When a request mixes them, or canon and history disagree, say so, then do what the user asked.

**Name your proxies and your gaps.** Record every stand-in value and every UNVERIFIED shape in the commit message, so the next pass knows what to check.

## Review loop

Look at the picture the way the user will: in the real page, on desktop and on a phone, at full size and zoomed in.

1. Set up once per session in your scratchpad: `mkdir -p <scratchpad>/shot && cd <scratchpad>/shot && npm i playwright && npx playwright install chromium`. Run the scripts from that folder by their path in this skill; `shoot.mjs` loads Playwright from the current directory.
2. Serve the page (check the port is free first) and shoot it with `scripts/shoot.mjs`. It shoots each `--size` (default `1600x1000` and `390x844`) at device pixel ratio 2. `--section '#id' --at 0..1` scrolls through a sticky section, `--y` scrolls to a pixel, and `--repeat N --every ms` catches moving parts. It prints page errors; a page error means the picture is not the one you think.
3. Look at the whole frame first: tradition, value plan, space.
4. Cut 2× crops of every element with `scripts/crop.py SHOT OUT x,y,w,h:name ...` (boxes in CSS pixels; run it with `uv run --with pillow python`). Answer the checklist for each crop.
5. Fix, re-shoot, and compare against the previous shots. Keep before and after shots, and put the exact commands in the commit message so someone else can re-run the check.

## Checklist

- **Proportion.** Do figures, animals, vehicles, props and buildings match their measurements? Does every pose's reach work?
- **Pose and mood.** Does each body carry its weight the way the reference does?
- **Grounding.** Does everything touch its support, with a contact accent? Is anything hovering a few pixels off?
- **Depth order.** Does each object overlap the way its ground contact says it should, and does every moving object stay in order along its whole path?
- **Space.** Do the horizon and scale with distance agree? Is there an empty gap between two scales? Are any edges unintended?
- **Light.** Do shadows and highlights come from one source? Do reflections sit on a surface that can reflect?
- **Tradition.** Would this sit beside the reference works, or does any part read as clip-art?
- **Structure at zoom.** Does every 2× crop of a hero element show built structure (branches inside crowns, plate edges and environment bands, grass in tufts) and at least three value steps, or is it a flat shape with texture on top?
- **Medium.** Did fine detail survive the stylisation? Is any repeating texture cut, smeared or evenly spread?
- **States.** In every era, time of day and viewport, does each object belong, and do the in-between frames hold?
- **Accuracy.** Does each costume piece, building, colour and canon detail match a source? Are proxies and UNVERIFIED items named?
