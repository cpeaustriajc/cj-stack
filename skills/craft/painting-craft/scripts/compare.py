"""Put a reference beside your own crop at the same height, so differences show at a glance.

usage: uv run --with pillow python compare.py OUT.png REF.png[:x,y,w,h] MINE.png[:x,y,w,h] [--height 700]

Boxes are in each image's own pixels. Look at the result with the Read tool and name every
difference in structure (edges, values, shapes), not just colour.
"""
import argparse
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('out'); ap.add_argument('ref'); ap.add_argument('mine')
ap.add_argument('--height', type=int, default=700)
a = ap.parse_args()


def load(spec):
    path, _, box = spec.partition(':')
    im = Image.open(path).convert('RGB')
    if box:
        x, y, w, h = map(int, box.split(','))
        im = im.crop((x, y, x + w, y + h))
    return im.resize((round(im.width * a.height / im.height), a.height), Image.LANCZOS)


left, right = load(a.ref), load(a.mine)
gap = 12
out = Image.new('RGB', (left.width + gap + right.width, a.height + 28), (24, 24, 24))
out.paste(left, (0, 28)); out.paste(right, (left.width + gap, 28))
d = ImageDraw.Draw(out)
d.text((6, 8), 'reference', fill=(230, 230, 230)); d.text((left.width + gap + 6, 8), 'mine', fill=(230, 230, 230))
out.save(a.out)
print('wrote', a.out)
