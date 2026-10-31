import math
import numpy as np
from scipy import ndimage

# Centimetres with x right, y down and z toward the viewer: a left-handed frame, so cross products flip.
PITCH = math.radians(14)
VIEW = np.array([0., -math.sin(PITCH), math.cos(PITCH)])
SUN = np.array([.58, -.6, .56]) / np.linalg.norm([.58, -.6, .56])


def unit(v):
    v = np.asarray(v, float)
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)


def safe(x):
    return np.where(np.abs(x) < 1e-6, 1e-6, x)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = np.asarray(t)[..., None] if np.ndim(t) else t
    return np.asarray(a) * (1 - t) + np.asarray(b) * t


def hexc(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def project(P):
    P = np.asarray(P, float)
    c, s = math.cos(PITCH), math.sin(PITCH)
    return np.stack([P[..., 0], P[..., 1] * c + P[..., 2] * s], -1), P[..., 2] * c - P[..., 1] * s


class Mesh:
    def __init__(self):
        self.parts = []

    # uv runs in centimetres along the surface: bump, cut and mail feature sizes assume it.
    def grid(self, P, mat, uv=None, wrap=False, cut=None, bump=None, obj=None, line=True, period=None, **kw):
        P = np.asarray(P, float)
        a, b = P.shape[:2]
        if uv is None:
            mid = P[:, b // 2]
            seg = np.linalg.norm(np.diff(np.concatenate([mid, mid[:1]]) if wrap else mid, axis=0), axis=1)
            u = np.concatenate([[0], np.cumsum(seg)])
            period = u[-1]
            mv = P[a // 2]
            v = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(mv, axis=0), axis=1))])
            uv = np.stack(np.broadcast_arrays(u[:a, None], v[None, :]), -1)
        uv = np.asarray(uv, float)
        if wrap:
            P = np.concatenate([P, P[:1]])
            uv = np.concatenate([uv, uv[:1] + [period, 0]])
            Pe = np.concatenate([P[-2:-1], P, P[1:2]])
            ue = np.concatenate([uv[-2:-1, :, 0] - period, uv[..., 0], uv[1:2, :, 0] + period])
            Pu, dU = Pe[2:] - Pe[:-2], ue[2:] - ue[:-2]
            a += 1
        else:
            Pu, dU = np.gradient(P, axis=0), np.gradient(uv[..., 0], axis=0)
        Pv, dV = np.gradient(P, axis=1), np.gradient(uv[..., 1], axis=1)
        N = unit(np.cross(Pu, Pv))
        if np.sum(N * (P - P.reshape(-1, 3).mean(0))) < 0: N = -N
        Pu, Pv = Pu / safe(dU)[..., None], Pv / safe(dV)[..., None]
        idx = np.arange(a * b).reshape(a, b)
        q = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
        F = np.concatenate([q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
        self.parts.append(dict(P=P.reshape(-1, 3), N=N.reshape(-1, 3), Pu=Pu.reshape(-1, 3), Pv=Pv.reshape(-1, 3), uv=uv.reshape(-1, 2),
                               F=F, mat=mat, cut=cut, bump=bump, obj=len(self.parts) if obj is None else obj, line=line, kw=kw))
        return len(self.parts) - 1

    def pack(self):
        off, out = 0, {k: [] for k in ('P', 'N', 'Pu', 'Pv', 'uv', 'F', 'part')}
        for i, p in enumerate(self.parts):
            for k in ('P', 'N', 'Pu', 'Pv', 'uv'):
                out[k].append(p[k])
            out['F'].append(p['F'] + off)
            out['part'].append(np.full(len(p['F']), i))
            off += len(p['P'])
        return {k: np.concatenate(v) for k, v in out.items()}


def raster(xy, depth, F, size, cut=None, chunk=4_000_000):
    Wd, Ht = size
    zb = np.full(Wd * Ht, -np.inf, np.float32)
    tid = np.full(Wd * Ht, -1, np.int32)
    B0 = np.zeros(Wd * Ht, np.float32)
    B1 = np.zeros(Wd * Ht, np.float32)
    T = xy[F]
    Dz = depth[F]
    x0 = np.ceil(T[..., 0].min(1) - .5).astype(np.int64)
    x1 = np.floor(T[..., 0].max(1) - .5).astype(np.int64)
    y0 = np.ceil(T[..., 1].min(1) - .5).astype(np.int64)
    y1 = np.floor(T[..., 1].max(1) - .5).astype(np.int64)
    x0, y0 = np.maximum(x0, 0), np.maximum(y0, 0)
    x1, y1 = np.minimum(x1, Wd - 1), np.minimum(y1, Ht - 1)
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    A = (T[:, 1, 0] - T[:, 0, 0]) * (T[:, 2, 1] - T[:, 0, 1]) - (T[:, 2, 0] - T[:, 0, 0]) * (T[:, 1, 1] - T[:, 0, 1])
    ok = (bw > 0) & (bh > 0) & (np.abs(A) > 1e-9)
    kw = 2 ** np.ceil(np.log2(np.maximum(bw, 1))).astype(np.int64)
    kh = 2 ** np.ceil(np.log2(np.maximum(bh, 1))).astype(np.int64)
    for w_, h_ in sorted(set(zip(kw[ok].tolist(), kh[ok].tolist()))):
        sel = np.nonzero(ok & (kw == w_) & (kh == h_))[0]
        oy, ox = np.mgrid[0:h_, 0:w_]
        ox, oy = ox.ravel(), oy.ravel()
        step = max(1, chunk // (w_ * h_))
        for c0 in range(0, len(sel), step):
            t = sel[c0:c0 + step]
            qx = x0[t, None] + ox[None]
            qy = y0[t, None] + oy[None]
            m = (qx <= x1[t, None]) & (qy <= y1[t, None])
            px, py = qx + .5, qy + .5
            p0, p1, p2 = T[t, 0], T[t, 1], T[t, 2]
            a = A[t, None]
            w0 = ((p1[:, None, 0] - px) * (p2[:, None, 1] - py) - (p2[:, None, 0] - px) * (p1[:, None, 1] - py)) / a
            w1 = ((p2[:, None, 0] - px) * (p0[:, None, 1] - py) - (p0[:, None, 0] - px) * (p2[:, None, 1] - py)) / a
            w2 = 1 - w0 - w1
            m &= (w0 >= -1e-5) & (w1 >= -1e-5) & (w2 >= -1e-5)
            ti, ki = np.nonzero(m)
            if not len(ti): continue
            w0, w1, w2 = w0[ti, ki], w1[ti, ki], w2[ti, ki]
            tri = t[ti]
            d = Dz[tri, 0] * w0 + Dz[tri, 1] * w1 + Dz[tri, 2] * w2
            pix = qy[ti, ki] * Wd + qx[ti, ki]
            if cut is not None:
                keep = cut(tri, w0, w1, w2)
                tri, w0, w1, d, pix = tri[keep], w0[keep], w1[keep], d[keep], pix[keep]
            o = np.lexsort((-d, pix))
            pix, d, tri, w0, w1 = pix[o], d[o], tri[o], w0[o], w1[o]
            first = np.ones(len(pix), bool)
            first[1:] = pix[1:] != pix[:-1]
            pix, d, tri, w0, w1 = pix[first], d[first], tri[first], w0[first], w1[first]
            win = d > zb[pix]
            pix = pix[win]
            zb[pix], tid[pix], B0[pix], B1[pix] = d[win], tri[win], w0[win], w1[win]
    return tid.reshape(Ht, Wd), B0.reshape(Ht, Wd), B1.reshape(Ht, Wd), zb.reshape(Ht, Wd)


def push_out(X, colliders, pad=.25, hit=None):
    for c in colliders:
        if c[0] == 'cap':
            _, a, b, r = c
            ab = b - a
            t = np.clip(((X - a) @ ab) / (ab @ ab), 0, 1)
            q = a + t[:, None] * ab
            d = X - q
            L = np.linalg.norm(d, axis=1)
            m = L < r + pad
            X[m] = q[m] + d[m] / np.maximum(L[m], 1e-6)[:, None] * (r + pad)
        elif c[0] == 'ell':
            _, ctr, axes, rad = c
            loc = (X - ctr) @ axes.T / rad
            L = np.linalg.norm(loc, axis=1)
            m = L < 1 + pad / rad.min()
            loc[m] = loc[m] / np.maximum(L[m], 1e-6)[:, None] * (1 + pad / rad.min())
            X[m] = ctr + (loc[m] * rad) @ axes
        elif c[0] == 'floor':
            m = X[:, 1] > c[1] - pad
            X[m, 1] = c[1] - pad
        if hit is not None: hit |= m
    return X


def drape(X0, pinned, cols, steps=260, iters=6, gravity=.06, rest=None, wrap=False, friction=.8, bend=.4):
    R, C = X0.shape[:2]
    X = X0.reshape(-1, 3).copy()
    X_rest = (X0 if rest is None else rest).reshape(-1, 3)
    Xp = X.copy()
    idx = np.arange(R * C).reshape(R, C)
    if wrap: idx = np.concatenate([idx, idx[:, :2]], 1)
    pairs = [(idx[:-1], idx[1:]), (idx[:, :-1], idx[:, 1:]), (idx[:-1, :-1], idx[1:, 1:]), (idx[:-1, 1:], idx[1:, :-1]), (idx[:-2], idx[2:]), (idx[:, :-2], idx[:, 2:])]
    I = np.concatenate([p[0].ravel() for p in pairs])
    J = np.concatenate([p[1].ravel() for p in pairs])
    K = np.concatenate([np.full(p[0].size, k) for k, p in enumerate(pairs)])
    L0 = np.linalg.norm(X_rest[J] - X_rest[I], axis=1)
    wgt = np.where(K >= 4, bend, 1.)
    free = ~pinned.ravel()
    g = np.array([0, gravity, 0])
    for _ in range(steps):
        V = (X - Xp) * .9
        Xp = X.copy()
        X[free] += V[free] + g
        hit = np.zeros(len(X), bool)
        for _ in range(iters):
            D = X[J] - X[I]
            L = np.linalg.norm(D, axis=1)
            corr = ((L - L0) / np.maximum(L, 1e-6) * wgt)[:, None] * D * .5
            acc = np.zeros_like(X)
            cnt = np.zeros(len(X))
            np.add.at(acc, I, corr)
            np.add.at(acc, J, -corr)
            np.add.at(cnt, I, wgt)
            np.add.at(cnt, J, wgt)
            X[free] += (acc / np.maximum(cnt, 1)[:, None] * 2.2)[free]
            h = np.zeros(int(free.sum()), bool)
            X[free] = push_out(X[free], cols, hit=h)
            hit[np.nonzero(free)[0][h]] = True
        Xp[hit] = X[hit] - (X[hit] - Xp[hit]) * (1 - friction)
    return X.reshape(R, C, 3)


def env(R):
    x, y, z = R[..., 0], R[..., 1], R[..., 2]
    up = -y
    right = smooth(-.3, .8, x)
    front = smooth(-.4, .9, z)
    hz = mix(hexc('#3a3028'), hexc('#c8ccc0'), front * .8)
    hz = mix(hz, hexc('#f6ead0'), right)
    sky = mix(hexc('#1c2a1a'), hexc('#c8d8ec'), np.clip(right * .9 + front * .75, 0, 1) * smooth(.92, .35, up))
    gr = mix(hexc('#262c22'), hexc('#76845a'), np.clip(right * .7 + front * .5, 0, 1))
    c = np.where((up > 0)[..., None], mix(hz, sky, smooth(.02, .45, up)), mix(hz, gr, smooth(0, .3, -up)))
    return c


def ambient(N):
    up = -N[..., 1]
    return mix(mix(hexc('#3c4636'), hexc('#5a5e3a'), smooth(-.2, .8, N[..., 0])), hexc('#6c7c88'), smooth(-.6, .9, up))


SUNC = hexc('#fff0d6') * 1.08
MATS = {}
TWO = {'cloth', 'void', 'mail', 'leather'}


def mat(fn):
    MATS[fn.__name__] = fn
    return fn


def reflect(N):
    return unit(2 * (N @ VIEW)[:, None] * N - VIEW)


@mat
def steel(c, tint=(1, 1, 1), gain=.92, base=.05, rough=0., spec=1.):
    R = reflect(c.N)
    E = env(R)
    if rough: E = mix(E, ambient(c.N) * 1.15, rough)
    s = np.clip(R @ SUN, 0, 1)
    hot = (s ** 220 * 2.4 + s ** 26 * .3) * spec * c.sun
    col = base + E * gain * np.asarray(tint)
    col = col * (.82 + .18 * c.sun)[:, None] + hot[:, None] * SUNC
    return col * mix(.5, 1, c.ao)


@mat
def cloth(c, albedo='#a8241a', shade='#3c0a0a'):
    ndl = c.N @ SUN
    wrap = np.clip((ndl + .3) / 1.3, 0, 1)
    lightv = wrap * c.sun
    A = mix(hexc(shade), hexc(albedo), smooth(-.1, .8, lightv))
    col = A * (ambient(c.N) * 1.05 * c.ao[:, None] + SUNC * lightv[:, None] * .7)
    return col + (smooth(.55, 1, lightv) * .1)[:, None] * hexc('#ffb080') * c.ao[:, None]


@mat
def leather(c, albedo='#3a2a1c', shade='#120c08', gloss=.4):
    col = cloth(c, albedo, shade)
    R = reflect(c.N)
    s = np.clip(R @ SUN, 0, 1)
    return col + ((s ** 30 * .5 + s ** 6 * .08) * gloss * c.sun)[:, None] * SUNC


@mat
def mail(c, tint=(.6, .64, .7), pitch=.62, ring=.3, wire=.13, gap='#1c1e20'):
    u, v = c.uv[:, 0], c.uv[:, 1]
    dy = pitch * .7
    best = np.full(len(u), 9.)
    du = np.zeros(len(u))
    dv = np.zeros(len(u))
    r0 = np.round(v / dy)
    for dr in (-1, 0, 1):
        r = r0 + dr
        off = (r % 2) * pitch * .5
        cc = np.round((u - off) / pitch) * pitch + off
        for dc in (-pitch, 0, pitch):
            x, y = u - (cc + dc), v - r * dy
            d = np.hypot(x, y)
            e = np.abs(d - ring)
            w = e < best
            best = np.where(w, e, best)
            du = np.where(w, x / np.maximum(d, 1e-4) * np.sign(d - ring), du)
            dv = np.where(w, y / np.maximum(d, 1e-4) * np.sign(d - ring), dv)
    cov = np.clip(1.4 - best / wire, 0, 1)
    k = np.clip(best / wire, 0, 1)
    N = unit(c.N * (1 - k * .55)[:, None] + (du[:, None] * c.TU + dv[:, None] * c.TV) * (k * 1.1)[:, None])
    c2 = c.sub(np.arange(len(u)))
    c2.N = N
    met = steel(c2, tint=tint, gain=.85, base=.04, rough=.3, spec=.9)
    return mix(hexc(gap) * (.5 + .5 * c.ao[:, None]), met, cov)


@mat
def void(c):
    return np.broadcast_to(hexc('#0a0a0c'), c.N.shape).copy()


class Ctx:
    def __init__(self, **k):
        self.__dict__.update(k)

    def sub(self, m):
        n_ = len(self.N)
        return Ctx(**{k: (v[m] if isinstance(v, np.ndarray) and v.ndim and len(v) == n_ else v) for k, v in self.__dict__.items()})


def light_basis(L=SUN):
    a = unit(np.cross([0, 1, 0], L) if abs(L[1]) < .99 else np.cross([1, 0, 0], L))
    b = np.cross(L, a)
    return a, b


def shadow_map(D, lp=3.0, L=SUN):
    a, b = light_basis(L)
    P = D['P']
    xy = np.stack([P @ a, P @ b], -1)
    lo = xy.min(0) - 4
    xy = (xy - lo) * lp
    size = tuple(int(v) + 8 for v in xy.max(0))
    tid, _, _, zb = raster(xy, P @ L, D['F'], size)
    return dict(zb=zb, lo=lo, lp=lp, a=a, b=b, L=L)


def sun_vis(sm, P, bias=.9):
    q = (np.stack([P @ sm['a'], P @ sm['b']], -1) - sm['lo']) * sm['lp']
    Ht, Wd = sm['zb'].shape
    out = np.zeros(len(P))
    d = P @ sm['L']
    for ox, oy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        ix = np.clip((q[:, 0] + ox).astype(int), 0, Wd - 1)
        iy = np.clip((q[:, 1] + oy).astype(int), 0, Ht - 1)
        out += sm['zb'][iy, ix] <= d + bias
    return out / 5


def render(mesh, ppcm, origin, size, ss=2, lines=.85, light=None):
    D = mesh.pack()
    parts = mesh.parts
    W2, H2 = size[0] * ss, size[1] * ss
    xy, dep = project(D['P'])
    sxy = (xy - origin) * ppcm * ss
    fp = D['part']
    cuts = [i for i, p in enumerate(parts) if p['cut'] is not None]

    def cut(tri, w0, w1, w2):
        keep = np.ones(len(tri), bool)
        pp = fp[tri]
        for i in cuts:
            m = pp == i
            if not m.any(): continue
            f = D['F'][tri[m]]
            uv = D['uv'][f[:, 0]] * w0[m, None] + D['uv'][f[:, 1]] * w1[m, None] + D['uv'][f[:, 2]] * w2[m, None]
            keep[m] = parts[i]['cut'](uv)
        return keep

    tid, b0, b1, zb = raster(sxy, dep, D['F'], (W2, H2), cut if cuts else None)
    vis = tid >= 0
    t = tid[vis]
    w0, w1 = b0[vis].astype(float), b1[vis].astype(float)
    w2 = 1 - w0 - w1
    f = D['F'][t]
    ip = lambda A: A[f[:, 0]] * w0[:, None] + A[f[:, 1]] * w1[:, None] + A[f[:, 2]] * w2[:, None]
    P, N, Pu, Pv, uv = ip(D['P']), unit(ip(D['N'])), ip(D['Pu']), ip(D['Pv']), ip(D['uv'])
    part = fp[t]
    inner = (N @ VIEW) < 0
    N[inner] = -N[inner]
    inner &= ~np.array([p['kw'].get('two', p['mat'] in TWO) for p in parts])[part]
    order = np.argsort(part, kind='stable')
    bounds = np.searchsorted(part[order], np.arange(len(parts) + 1))
    for i, p in enumerate(parts):
        if p['bump'] is None: continue
        m = order[bounds[i]:bounds[i + 1]]
        if not len(m): continue
        e = .03
        hu = (p['bump'](uv[m] + [e, 0]) - p['bump'](uv[m] - [e, 0])) / (2 * e)
        hv = (p['bump'](uv[m] + [0, e]) - p['bump'](uv[m] - [0, e])) / (2 * e)
        g = hu[:, None] * Pu[m] / np.maximum((Pu[m] ** 2).sum(1), 1e-6)[:, None] + hv[:, None] * Pv[m] / np.maximum((Pv[m] ** 2).sum(1), 1e-6)[:, None]
        N[m] = unit(N[m] - g * ~inner[m, None])
    sm = shadow_map(D)
    sun = sun_vis(sm, P)
    if light is not None: sun = sun * light(P)
    full = np.zeros((H2, W2))
    full[vis] = sun
    full = ndimage.gaussian_filter(full, ss * .8)
    cov = ndimage.gaussian_filter(vis.astype(float), ss * .8)
    sun = (full / np.maximum(cov, 1e-3))[vis]
    zbg = np.where(vis, zb, zb[vis].min() - 30 if vis.any() else 0)
    sig = 2.2 * ppcm * ss
    ao_full = np.clip((ndimage.gaussian_filter(zbg, sig) - zbg) / 6, 0, 1)
    ao = 1 - ao_full[vis] * .85
    col = np.zeros((len(t), 3))
    ctx = Ctx(P=P, N=N, uv=uv, inner=inner, sun=sun * ~inner, ao=ao * np.where(inner, .35, 1), TU=unit(Pu), TV=unit(Pv))
    for i, p in enumerate(parts):
        m = order[bounds[i]:bounds[i + 1]]
        if not len(m): continue
        col[m] = MATS[p['mat']](ctx.sub(m), **{k: v for k, v in p['kw'].items() if k != 'two'})
    img = np.zeros((H2, W2, 3))
    img[vis] = np.clip(col, 0, 1)
    if lines:
        names = {}
        obj = np.array([names.setdefault(p['obj'], len(names)) for p in parts])
        ln = np.array([p['line'] for p in parts])
        om = np.full((H2, W2), -1)
        om[vis] = obj[part]
        lm = np.zeros((H2, W2), bool)
        lm[vis] = ln[part]
        z = np.where(vis, zb, -1e9)
        e = np.zeros((H2, W2), bool)
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            o2 = np.roll(om, (-dy, -dx), (0, 1))
            z2 = np.roll(z, (-dy, -dx), (0, 1))
            l2 = np.roll(lm, (-dy, -dx), (0, 1))
            edge = ((om != o2) | (np.abs(z - z2) > 1.6)) & (lm | l2)
            near = z >= z2
            e |= edge & ~near & vis
            e |= np.roll(edge & near & (o2 >= 0), (dy, dx), (0, 1))
        e = ndimage.binary_dilation(e, iterations=max(1, ss // 2)) & vis
        img[e] = img[e] * (1 - lines) + hexc('#0c0e10') * lines
    a = vis.astype(float)
    img = img.reshape(size[1], ss, size[0], ss, 3).mean((1, 3))
    a = a.reshape(size[1], ss, size[0], ss).mean((1, 3))
    return img, a, dict(sm=sm, D=D)
def perp(t, hint):
    n = unit(np.asarray(hint, float) - (np.asarray(hint, float) @ t) * t)
    return n, np.cross(t, n)


def frames(S, hint):
    S = np.asarray(S, float)
    T = unit(np.gradient(S, axis=0))
    n, _ = perp(T[0], hint)
    N1 = [n]
    for i in range(1, len(S)):
        n = unit(N1[-1] - (N1[-1] @ T[i]) * T[i])
        N1.append(n)
    N1 = np.array(N1)
    return T, N1, np.cross(T, N1)


def tube(mesh, S, rad, hint, mat, nu=36, sq=2., **kw):
    S = np.asarray(S, float)
    T, N1, N2 = frames(S, hint)
    R = np.asarray(rad, float)
    if R.ndim == 1: R = np.stack([R, R], 1)
    th = np.linspace(-math.pi, math.pi, nu, endpoint=False)
    c, s = np.cos(th), np.sin(th)
    ce = np.sign(c) * np.abs(c) ** (2 / sq)
    se = np.sign(s) * np.abs(s) ** (2 / sq)
    P = S[None] + ce[:, None, None] * R[None, :, :1] * N1[None] + se[:, None, None] * R[None, :, 1:] * N2[None]
    return mesh.grid(P, mat, wrap=True, **kw)


def resample(S, k):
    S = np.asarray(S, float)
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    t = np.linspace(0, d[-1], k)
    return np.stack([np.interp(t, d, S[:, i]) for i in range(3)], 1)


def spline(pts, k=40):
    Q = np.asarray(pts, float)
    m = len(Q)
    out = []
    for i in range(m - 1):
        p0, p1, p2, p3 = Q[max(i - 1, 0)], Q[i], Q[i + 1], Q[min(i + 2, m - 1)]
        for t in np.linspace(0, 1, 12, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(Q[-1])
    return resample(out, k)


def ellipsoid(mesh, c, ax, rad, mat, nu=40, nv=24, ph=(-math.pi / 2, math.pi / 2), **kw):
    ax = np.asarray(ax, float)
    T = np.linspace(-math.pi, math.pi, nu, endpoint=False)
    Ph = np.linspace(*ph, nv)
    cp, sp = np.cos(Ph), np.sin(Ph)
    L = np.stack([np.cos(T)[:, None] * cp[None] * rad[0], np.sin(T)[:, None] * cp[None] * rad[1], np.broadcast_to(sp[None] * rad[2], (nu, nv))], -1)
    return mesh.grid(np.asarray(c, float) + L @ ax, mat, wrap=True, **kw)


def ground_shadow(info, ppcm, origin, size, G, ss=2, reach=60.):
    W2, H2 = size[0] * ss, size[1] * ss
    ys, xs = np.mgrid[0:H2, 0:W2]
    sx = origin[0] + (xs + .5) / (ppcm * ss)
    sy = origin[1] + (ys + .5) / (ppcm * ss)
    c, s = math.cos(PITCH), math.sin(PITCH)
    Z = (sy - G * c) / s
    P = np.stack([sx, np.full_like(sx, G, dtype=float), Z], -1).reshape(-1, 3)
    shade = 1 - sun_vis(info['sm'], P, bias=1.2)
    top = shadow_map(info['D'], lp=1.5, L=np.array([0., 1, 0]))
    q = (np.stack([P @ top['a'], P @ top['b']], -1) - top['lo']) * top['lp']
    Ht, Wd = top['zb'].shape
    zb = ndimage.grey_dilation(np.where(np.isfinite(top['zb']), top['zb'], -1e9), size=3)
    ix = np.clip(q[:, 0].astype(int), 0, Wd - 1)
    iy = np.clip(q[:, 1].astype(int), 0, Ht - 1)
    inside = (q[:, 0] >= 0) & (q[:, 0] < Wd) & (q[:, 1] >= 0) & (q[:, 1] < Ht)
    low = np.where(inside, zb[iy, ix], -1e9)
    occ = np.where(low > -1e8, np.exp(-np.clip(G - low, 0, None) / 9), 0)
    a = np.maximum(shade * .5, occ * .75).reshape(H2, W2)
    a = ndimage.gaussian_filter(a, 1.6 * ppcm * ss) * 1.15
    a *= np.clip(1 - np.abs(Z.reshape(H2, W2)) / reach, 0, 1)
    return np.clip(a, 0, 1).reshape(size[1], ss, size[0], ss).mean((1, 3))
