# Scale, space and the built world

How to keep a scene in one believable space, and the real-world sizes of the things that most often give a scene its scale. Figures and vehicles are in `anatomy.md`. Values here are typical real-world sizes from general knowledge, not canon. Replace them with a canon or survey source when the subject has one, and say which you used.

## Contents
- One scale per depth plane
- Bridging two scales
- Horizon and ground
- Buildings
- Streets
- Trees and plants
- Water, wet ground and reflections
- Atmosphere

## One scale per depth plane

Give every depth plane a scale in pixels per metre, and draw everything in that plane at it. Write the number down as a named constant: the next edit will need it, and an object drawn "about right" in the wrong plane is how proportion errors start.
- In perspective, through one camera, apparent size is proportional to 1 / distance. A plane at 28 px/m is 28 times nearer than one at 1 px/m.
- Two objects that touch, or stand side by side, share a plane, so they share a scale. A car beside a palm and a person at a door all read against each other.
- Pick the scale from something with a canon size when the scene has one: a tower's real height, a character's height. Then derive the floor pitch, window size and so on from it, so the counts come out right (a 300 m tower at about 4.3 m per floor has 70 floors).

## Bridging two scales

A near plane and a far plane at very different scales need something between them. When the gap is empty, the eye reads it as short and bare, and the far plane looks stranded, even when the viewer can't say what is wrong. Two fixes:
- **Fill the middle distance** with things at the scales in between: lower buildings, trees, a far bank of the river, rows of rooftops that grow toward the viewer. Each row sits a little lower on the canvas and a little larger than the one behind it.
- **Close the gap with telephoto compression.** A long lens flattens depth. Set the far plane's base directly behind the near plane's far edge, so the skyline rises right behind the road, as in long-lens photographs of palms against a downtown. Nothing shows between them, so nothing reads as missing.

Water is a third option. A bay or river between the planes explains the gap, and it gives lights a surface to reflect in.

## Horizon and ground

- The horizon is at the camera's height. For a standing viewer, every standing adult's eyes sit near the horizon, whatever their distance.
- Below the horizon, nearer ground is lower on the canvas. An object's base sets its depth, so place objects by where they touch the ground, then size them for that depth.
- Draw order follows the same rule: the object whose base is lower on the canvas is nearer, so it is drawn later. A thing that moves passes behind everything whose base is lower than its own.
- On sloped terrain, place objects with the terrain's height function rather than a fixed y. Sink foundations slightly below the surface and give each a contact shadow.

## Buildings

| Item | Typical size |
|---|---|
| Storey, floor to floor, homes | 3.0-3.3 m |
| Storey, offices and towers | 3.8-4.4 m |
| Ground-floor shops | 4.5-6 m |
| Medieval or pre-modern timber house storey | 2.4-3 m |
| Door | 2.0-2.1 m high, 0.9 m wide |
| Window sill | about 0.9 m above the floor |
| Tower, width to height | 1:5 to 1:8 is common; 1:10 to 1:20 only for "pencil" towers |
| Supertall | over 300 m, with setbacks and a crown |

- Window grids should match the floor pitch. A grid that is too coarse makes a skyscraper look like a ten-storey block.
- Towers in a skyline vary in height, width and crown. The tallest one is usually a landmark with a canon or real model; find it rather than making it random.
- A building that grows taller over time also widens, or it turns into a needle.
- Lights on a facade at night are sparse and clustered, not one lit window per cell. Whole floors go dark, and colours vary between warm and cool.

## Streets

| Item | Typical size |
|---|---|
| Traffic lane | 3.0-3.7 m |
| Pavement | 1.5-4 m |
| Kerb | about 15 cm high |
| US lane dash, gap | 3 m, 9 m |
| Streetlight pole | 8-12 m |
| Traffic signal | 4-6 m |
| Telephone or power pole | 9-12 m |

A road seen side-on is a band whose height comes from the camera's pitch, with kerbs and lane edges as its readable marks. A car on it sits on its tyres' contact line, with a contact shadow.

## Trees and plants

| Item | Typical size |
|---|---|
| Mexican fan palm (Washingtonia robusta) | 15-25 m tall, trunk 30-40 cm, crown about 4 m across |
| Linden or oak, mature | 20-30 m tall, canopy 0.6-0.8 of the height |
| Japanese black pine, coastal | 10-20 m, leaning and windswept |
| Shrub | 1-3 m |

- A bough starts inside its trunk. Canopy clumps overlap the branches that carry them. Roots flare into the ground.
- Trees in a row along a road stand on the verge, so they are nearer than the road and in front of the traffic on it.

## Water, wet ground and reflections

- A reflection needs a surface under its source: still or wet water, polished stone, wet asphalt, glass. Dry ground and grass reflect nothing.
- In still water, a point at height h above the water line reflects h below it, straight down.
- Rough surfaces stretch a reflection vertically and break it up. On wet asphalt or rippled water, draw broken horizontal streaks that thin out and fade toward the viewer, not a solid block.
- A reflection is darker and less saturated than its source, and soft-edged.

## Atmosphere

- Each step back in depth is lighter, cooler and lower in contrast, with softer edges. Give each depth plane its own value step.
- The darkest dark and the lightest light belong at the focal point, not in the distance.
- At night, haze at the base of a lit city glows with the city's colour and softens the bases of the towers more than their tops.
