"""Stroke-based paint pass: turns a flat render into brushwork that follows the picture's own forms.

usage: uv run --with numpy --with scipy --with pillow python paintpass.py IN.png OUT.png
         [--medium oil|gouache] [--focus x,y,w,h | --focus-mask mask.png] [--depth depth.png]
         [--width 1600] [--seed 7]

Paint everything in one pass so the whole picture shares one medium. Brushes run coarse to fine;
each layer only paints where the canvas still differs from the source, so flat areas keep big
strokes and detailed areas get small ones. The focus region gets one extra fine layer.
"""
import argparse, math, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--medium', choices=['oil', 'gouache'], default='oil')
ap.add_argument('--focus', help='x,y,w,h in source pixels: the part that gets the finest brush')
ap.add_argument('--focus-mask', help='greyscale PNG, white = focus')
ap.add_argument('--depth', help='greyscale PNG, white = far: far areas get haze and softer strokes')
ap.add_argument('--width', type=int, default=0, help='working width (default: source width)')
ap.add_argument('--seed', type=int, default=7)
ap.add_argument('--keep-lines', type=float, default=.45, help='0-1: how much of the source\'s thin lines (twigs, plate edges, rivets) survive the brushwork')
ap.add_argument('--calm', type=float, default=.6, help='0-1: how far smooth passages (sky, gradients) are glazed back to blended paint')
a = ap.parse_args()

rng = np.random.default_rng(a.seed)
img = Image.open(a.src).convert('RGB')
W = a.width or img.width
H = round(img.height * W / img.width)
S = W / 800
ref = np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
lum = lambda x: x[..., 0] * .3 + x[..., 1] * .59 + x[..., 2] * .11
blur = lambda x, s: ndimage.gaussian_filter(x, (s, s, 0) if x.ndim == 3 else s)


def noise(octaves, base):
    acc, amp = np.zeros((H, W), np.float32), 1.0
    for o in range(octaves):
        k = base * 2 ** o
        g = rng.random((int(k * H / W) + 2, k + 2)).astype(np.float32)
        acc += amp * ndimage.zoom(g, (H / (g.shape[0] - 1), W / (g.shape[1] - 1)), order=3)[:H, :W]
        amp *= .5
    return acc / 2


def load_mask(path):
    m = Image.open(path).convert('L').resize((W, H), Image.BILINEAR)
    return np.asarray(m).astype(np.float32) / 255


focus = np.zeros((H, W), bool)
if a.focus:
    x, y, w, h = (float(v) * W / img.width for v in a.focus.split(','))
    focus[int(y):int(y + h), int(x):int(x + w)] = True
if a.focus_mask:
    focus |= load_mask(a.focus_mask) > .5
depth = load_mask(a.depth) if a.depth else None

if depth is not None:
    far = np.clip((depth - .45) / .5, 0, 1)[..., None]
    sky_tint = blur(ref, 40 * S).mean(axis=(0, 1))
    ref = ref * (1 - far * .3) + sky_tint * far * .3
    ref = ref * (1 - far) + blur(ref, 1.4 * S) * far

detail = ndimage.gaussian_filter(np.hypot(ndimage.sobel(lum(ref), 1), ndimage.sobel(lum(ref), 0)), 1.5 * S)
# absolute, not relative to the picture: a gentle sky gradient must never count as detail
detail = np.clip(detail / .1, 0, 1.5)


def orientation(x, s):
    l = ndimage.gaussian_filter(lum(x), s)
    gx, gy = ndimage.sobel(l, 1), ndimage.sobel(l, 0)
    exx, eyy, exy = [ndimage.gaussian_filter(q, s * 2) for q in (gx * gx, gy * gy, gx * gy)]
    ang = .5 * np.arctan2(2 * exy, exx - eyy) + np.pi / 2
    mag = np.sqrt((exx - eyy) ** 2 + 4 * exy ** 2)
    weak = mag < np.percentile(mag, 55)
    drift = (noise(3, 10) - .5) * 1.4
    ang = np.where(weak, drift, ang)
    return np.cos(ang).astype(np.float32), np.sin(ang).astype(np.float32)


if a.medium == 'oil':
    layers = [(20, .05, 236), (11, .055, 228), (6, .06, 220), (3.4, .07, 212), (2, .085, 206)]
    max_len, jitter, impasto = 14, .03, .03
else:
    layers = [(16, .06, 250), (8, .07, 245), (4, .08, 240), (2.2, .1, 235)]
    max_len, jitter, impasto = 8, .015, .0

canvas = blur(ref, 24 * S) * .85 + ref.mean(axis=(0, 1)) * .15
cim = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8))
hmap = Image.new('L', (W, H), 0)
plan = [(max(1, round(r * S)), t, al, None) for r, t, al in layers]
if focus.any():
    plan.append((max(1, round(1.2 * S)), .06, 214, focus))

t0 = time.time()
for li, (R, T, alpha, where) in enumerate(plan):
    refR = blur(ref, R * .4)
    cx, cy = orientation(refR, max(1, R * .6))
    cur = np.asarray(cim).astype(np.float32) / 255
    # relative to brightness, or dark passages never earn fine brushes and turn to mud
    err = ndimage.uniform_filter(np.linalg.norm(cur - refR, axis=2) / (.12 + lum(refR)) * .35, R)
    ys, xs = np.mgrid[R // 2:H:R, R // 2:W:R]
    ys, xs = ys.ravel(), xs.ravel()
    jit = rng.integers(-(R // 2), R // 2 + 1, (2, ys.size))
    ys, xs = np.clip(ys + jit[0], 0, H - 1), np.clip(xs + jit[1], 0, W - 1)
    sel = err[ys, xs] > T
    if R <= 6 * S:
        sel |= detail[ys, xs] > .3
    if where is not None:
        sel &= where[ys, xs]
    pts = np.stack([xs[sel], ys[sel]], 1)[rng.permutation(np.count_nonzero(sel))]
    d, hd = ImageDraw.Draw(cim, 'RGBA'), ImageDraw.Draw(hmap)
    for x0, y0 in pts:
        col = refR[y0, x0]
        # smooth passages (sky, gradients) get calm strokes, or the pass mottles them
        busy = min(1.0, .25 + detail[y0, x0] * 2.5)
        c = col * (1 + rng.normal(0, jitter * busy)) + rng.normal(0, .01 * busy, 3)
        L = lum(col)
        if L > .55 and rng.random() < .4 * busy:
            c = c + np.array([.04, .02, -.03]) * rng.random()
        elif L < .38 and rng.random() < .4 * busy:
            c = c + np.array([-.02, -.004, .04]) * rng.random()
        c = np.clip(c, 0, 1)
        n = max(2, int(max_len * (1 - .7 * min(1.0, detail[y0, x0]))))
        if R <= 4:
            n = max(2, n * 2 // 3)
        x, y, px, py = float(x0), float(y0), 0.0, 0.0
        line = [(x, y)]
        for i in range(n):
            ix, iy = int(x), int(y)
            if i > 1 and np.abs(refR[iy, ix] - col).sum() > .1:
                break
            dx, dy = cx[iy, ix], cy[iy, ix]
            if dx * px + dy * py < 0:
                dx, dy = -dx, -dy
            if i:
                dx, dy = .6 * dx + .4 * px, .6 * dy + .4 * py
            m = math.hypot(dx, dy) or 1
            dx, dy = dx / m, dy / m
            x, y = x + dx * R * .75, y + dy * R * .75
            if not (0 <= x < W and 0 <= y < H):
                break
            line.append((x, y))
            px, py = dx, dy
        rgba = tuple(int(q * 255) for q in c) + (alpha,)
        w = max(1, int(R * (1.6 if R > 3 else 1.4)))
        if len(line) > 1:
            d.line(line, fill=rgba, width=w, joint='curve')
        for ex, ey in (line[0], line[-1]):
            d.ellipse((ex - w / 2, ey - w / 2, ex + w / 2, ey + w / 2), fill=rgba)
        if len(line) > 1:
            hd.line(line, fill=int(rng.integers(90, 255)), width=w, joint='curve')
    print(f'[{li + 1}/{len(plan)}] brush {R}px  strokes {len(pts)}  ({time.time() - t0:.0f}s)', flush=True)

out = np.asarray(cim).astype(np.float32) / 255
if a.calm:
    smooth = ndimage.gaussian_filter(np.clip(1 - detail * 4, 0, 1), 4 * S) * a.calm * ~focus
    out = out * (1 - smooth[..., None]) + blur(ref, 1.2 * S) * smooth[..., None]
if a.keep_lines:
    # brushes wider than a twig erase it; put the source's high-frequency lines back where it has detail
    lines = ref - blur(ref, 1.5 * S)
    out = out + lines * (a.keep_lines * np.clip(detail, 0, 1))[..., None]
if impasto:
    hgt = ndimage.gaussian_filter(np.asarray(hmap).astype(np.float32) / 255, .8 * S)
    gx, gy = ndimage.sobel(hgt, 1), ndimage.sobel(hgt, 0)
    out = np.clip(out + (-gx * .6 - gy * .8)[..., None] * impasto, 0, 1)
if depth is not None:
    soft = (np.clip((depth - .6) * 2.2, 0, 1) * .45 * ~focus)[..., None]
    out = out * (1 - soft) + blur(out, 2 * S) * soft
Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)).save(a.dst)
print('painted', a.dst)
