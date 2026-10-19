import argparse, importlib, math, os, sys
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--art', default=os.path.dirname(os.path.abspath(__file__)), help='folder holding render3d.py and the figure module')
ap.add_argument('--module', required=True, help='figure module name, e.g. knight')
ap.add_argument('--code', required=True, help='python run inside the module namespace; must assign `mesh`')
ap.add_argument('--yaws', default='0,-50,90', help='degrees about the vertical axis')
ap.add_argument('--ppcm', type=float, default=7)
ap.add_argument('--out', required=True)
a = ap.parse_args()

sys.path.insert(0, os.path.abspath(a.art))
r = importlib.import_module('render3d')
mod = importlib.import_module(a.module)
ns = dict(vars(mod))
exec(a.code, ns)
mesh = ns['mesh']
centre = np.concatenate([p['P'] for p in mesh.parts]).mean(0)
tiles = []
for deg in (float(y) for y in a.yaws.split(',')):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    Ry = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
    m2 = r.Mesh()
    for p in mesh.parts:
        q = dict(p)
        q['P'] = (p['P'] - centre) @ Ry.T
        for key in ('N', 'Pu', 'Pv'):
            q[key] = p[key] @ Ry.T
        m2.parts.append(q)
    xy, _ = r.project(np.concatenate([p['P'] for p in m2.parts]))
    lo, hi = xy.min(0) - 3, xy.max(0) + 3
    size = tuple(int(v) for v in np.ceil((hi - lo) * a.ppcm))
    img, alpha, _ = r.render(m2, a.ppcm, lo, size)
    tiles.append(img + (1 - alpha[..., None]) * .5)
h = max(t.shape[0] for t in tiles)
tiles = [np.pad(t, ((0, h - t.shape[0]), (0, 8), (0, 0)), constant_values=.5) for t in tiles]
Image.fromarray((np.clip(np.concatenate(tiles, 1), 0, 1) * 255).astype(np.uint8)).save(a.out)
print('wrote', a.out)
