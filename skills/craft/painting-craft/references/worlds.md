# The Worlds paintings on cpeaustriajc.dev

The portfolio's Worlds chapter (`layouts/index.html`, section `#games`) is a scrolling sequence of painted eras, one for each group of games the site owner plays. Read this before you touch any era. It records each era's tradition, its canon and how to rebuild it.

## Contents
- How the chapter works
- The eras
- Canon the user corrected
- Rebuilding and checking

## How the chapter works

- Each era is a function in `portfolio.html` that returns `{ defs, stat, live, bind }`: `realms`, `ink`, `city` and `stars`.
- `stat` is rasterised once per layout into an image, so it is cheap. Filters it uses come from `FX(L)`, which is only included in that rasterisation.
- `live` stays as SVG and is animated by `bind`. Filters used in `live` must be defined in the era's own `defs`, or they silently do nothing.
- Eras are revealed by masks as the page scrolls. The scroll position runs through five stops; `STOPS` holds each stop's colours and label. The city era takes two stops (Los Santos at 2, Night City at 3), and `k` runs 0 to 1 between them.
- `L` holds the layout: `hw` (the half-width in scene units; the viewBox is always 1000 tall), `mobile`, the sun position `sx`/`sy` and the text card's frame. Desktop and a 390 px phone lay out differently, so check both.
- Scene randomness comes from seeded `rng(seed)` streams. To add random elements without moving the existing ones, draw from a second stream rather than inserting calls into the first.

## The eras

| Stop | Era | Games | Tradition | Function |
|---|---|---|---|---|
| 0 | Old realms | The Witcher 3, Kingdom Come: Deliverance II, Baldur's Gate 3 | A Romantic academic oil painting after Leighton's *The Accolade*, hung in a gilt frame on a lamplit wall | `realms` (shows `assets/art/henry-painting.webp`) |
| 1 | Ink and steel | Ghost of Tsushima, Sekiro, Onimusha: Way of the Sword | Japanese suibokuga ink wash after Tōhaku's *Pine Trees* and Sesshū's *Ama-no-Hashidate*, not Chinese shan shui | `ink` |
| 2-3 | The city | GTA V, then Cyberpunk 2077 | A risograph halftone poster at sunset that turns into a rainy neon night | `city` |
| 4 | The stars | No Man's Sky | A pulp paperback cover | `stars` |

Era notes:
- **Old realms.** Henry asleep against a linden above Suchdol, in the KCD2 cover-art kit under a two-sight bascinet, with Pebbles and Mutt. Henry's height has no canon source; Tom McKay's (about 183 cm) stands in. It is painted by the Python pipeline in `prototypes/art/` (see `render3d.md`), not in the page.
- **Ink and steel.** Jin Sakai on a forested hill above Tsushima's island-filled rias bay in 1274, from behind, with the Mongol fleet in the bay. Tsushima's hills are steep but forested, 500-650 m, with no needle peaks. The keep is a 1570s Ashina-style building, a stretch that is accepted because the era spans all three games. Jin's height has no canon source; Daisuke Tsuji's (about 178 cm) stands in.
- **The city.** In 2013 Maze Bank Tower (70 floors, about 300 m, modelled on the U.S. Bank Tower) is the tallest building, and the Vinewood sign stands on the hills east of the Galileo Observatory. In 2077 Arasaka Tower (620 m, 140 floors) is tallest. The scale is 1 unit = 1 m on desktop, and the skyline stands on the road's far kerb. Each era has its own car: a 2013 coupe and a 2077 wedge. UNVERIFIED: Maze Bank's in-game crown, Arasaka's silhouette and logo, and the palm species.
- **The stars.** It follows No Man's Sky's 2016 box art, which the user chose over a 1970s paperback look. The teal day sky has a huge pale planet rising out of the horizon haze, and a ring seen from below its plane, so the near arc is a dark line above the planet's centre. Three fighters fly in formation. The Traveller is seen from behind on coral-red grass, with a white fighter with a red stripe parked on the right, a striped beast, Diplos on the far plain and an orange-leaved tree. One camera: the horizon `hz` is 640 (desktop) or 540 (mobile), the focal length `F` is 1400, and the eye is 1.7 m up. Ground y is `hz + F*EYE/d`; things are drawn far to near by depth `d`. The star is off-frame to the upper right. A full-frame vignette keeps the text corner dark. Proxies: the Traveller is 1.8 m, the fighter 14 m long, the beast 2.2 m at the shoulder, Diplos 8 m (community measurements). UNVERIFIED: the exosuit's shapes and colours (taken from the cover alone), the fighter's silhouette, the moons' phases (lit from the right for one light, not crescents as on the cover).
## Canon the user corrected

- Mutt is a short-coated white dog with a chestnut head, ears and saddle and a white blaze.
- Pebbles is a dapple-grey mare.
- Wolf is Sekiro's protagonist, not an animal.
- "D&D" means Baldur's Gate 3.
- Onimusha means *Way of the Sword*.
- Tsushima is Japan: paint Japanese terrain in the Japanese ink tradition.

## Rebuilding and checking

The Henry painting. Its tooling left the tree; restore it first with `git checkout 35a27e6 -- prototypes/art prototypes/blender`:
```
uv run --with numpy --with scipy --with pillow python prototypes/art/henry.py
uv run --with numpy --with scipy --with pillow python prototypes/art/oil.py
cwebp -q 88 -m 6 prototypes/renders/henry-oil.png -o static/assets/art/henry-painting.webp
```

The page eras: run the Hugo dev server and shoot each stop with this skill's `scripts/shoot.mjs`. Stop k is `--at k/4`, the same mapping as the page's own stop buttons: Old realms 0, Ink 0.25, Los Santos 0.5, Night City 0.75, the stars 1. A value between two stops shoots the transition.
```
hugo server -p 8765 --bind 127.0.0.1    # check the port is free first
node <skill>/scripts/shoot.mjs --url http://127.0.0.1:8765/ --out shots/city --section '#games' --at 0.5 --repeat 2
uv run --with pillow python <skill>/scripts/crop.py shots/city-1600x1000-0.png shots/z 1090,860,180,70:car
```
Screenshots go in the session scratchpad, never the repo. Each era's latest commit message names the exact shots and commands it was checked with.
