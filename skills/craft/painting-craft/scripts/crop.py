"""Cut zoomed crops out of a screenshot so details can be judged at the size the user inspects them.

usage: uv run --with pillow python crop.py SHOT.png OUT_PREFIX x,y,w,h[:name] [x,y,w,h[:name] ...] [--scale 2] [--css 2]
Boxes are in CSS pixels of the page (what you read off a downscaled view); --css is the screenshot's device pixel ratio.
Each box is written as OUT_PREFIX-<name or index>.png, upscaled by --scale with nearest-neighbour so pixels stay honest.
"""
import sys
from PIL import Image

args, scale, css = [], 2.0, 2.0
it = iter(sys.argv[1:])
for a in it:
    if a == '--scale': scale = float(next(it))
    elif a == '--css': css = float(next(it))
    else: args.append(a)
if len(args) < 3:
    sys.exit(__doc__)
shot, prefix, boxes = Image.open(args[0]), args[1], args[2:]
for i, b in enumerate(boxes):
    spec, _, name = b.partition(':')
    x, y, w, h = (float(v) * css for v in spec.split(','))
    if x < 0 or y < 0 or x + w > shot.width or y + h > shot.height:
        sys.exit(f"box {spec} falls outside the {shot.width / css:g}x{shot.height / css:g} CSS-px shot")
    c = shot.crop((round(x), round(y), round(x + w), round(y + h)))
    c = c.resize((round(c.width * scale / css), round(c.height * scale / css)), Image.NEAREST)
    out = f"{prefix}-{name or i}.png"
    c.save(out)
    print('wrote', out, c.size)
