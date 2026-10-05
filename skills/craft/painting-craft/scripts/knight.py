import math
import numpy as np
from render3d import Mesh, tube, ellipsoid, spline, resample, unit, drape, render, push_out, ground_shadow, light_basis, SUN, VIEW

# Origin is the midpoint of Henry's hip joints: henry.py pins it to SCN.
GROUND = 9.5
PHI, LEAN = math.radians(46), math.radians(16)
HEAD_YAW, HEAD_DROOP, HEAD_LOLL = math.radians(44), math.radians(12), math.radians(19)
HS = .92
F_ = np.array([math.cos(PHI), 0, math.sin(PHI)])
R_ = np.array([-math.sin(PHI), 0, math.cos(PHI)])
U_ = np.array([0., -1, 0])
T_ = math.cos(LEAN) * U_ - math.sin(LEAN) * F_
TF = math.cos(LEAN) * F_ + math.sin(LEAN) * U_


def B(f, u, r):
    return f * F_ + u * U_ + r * R_


def Tp(h, f=0., r=0.):
    return h * T_ + f * TF + r * R_


def onto(K, L, heading, y):
    dy = y - K[1]
    hz = math.sqrt(max(L * L - dy * dy, 0))
    hd = unit(np.array([heading[0], 0, heading[2]]))
    return K + hd * hz + np.array([0, dy, 0])


def ik(S, W, l1, l2, pole):
    d = W - S
    L = min(np.linalg.norm(d), l1 + l2 - .01)
    dn = unit(d)
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L)
    p = unit(pole - (pole @ dn) * dn)
    E = S + dn * a + p * math.sqrt(max(l1 * l1 - a * a, 0))
    return E, S + dn * L


class Skel:
    def __init__(s):
        s.hipR, s.hipL = 9 * R_ + 3.5 * F_, -9 * R_ + 3.5 * F_
        s.shR, s.shL = Tp(50, -1, 18.5), Tp(50, -1, -18.5)
        s.neck = Tp(56, -1.5, 0)
        s.head = s.neck + 13.2 * unit(T_ + R_ * .27 + F_ * .08)
        s.kneeR = s.hipR + 44 * unit(B(.72, .7, .1))
        s.ankleR = onto(s.kneeR, 42, B(1, 0, -.05), GROUND - 8)
        s.kneeL = s.hipL + 44 * unit(B(.9, .3, -.4))
        s.ankleL = onto(s.kneeL, 42, unit(B(.9, 0, -.4)), GROUND - 7.5)
        s.elR, s.wrR = ik(s.shR, s.kneeR + U_ * 9.6 + B(1.5, 0, -7.5), 33, 26, R_ - U_ * .6 - F_ * .2)
        t = unit(s.kneeL - s.hipL)
        up = unit(U_ - (U_ @ t) * t)
        s.thighL_up = up
        s.elL, s.wrL = ik(s.shL, s.hipL + t * 17 + up * 11.2 - R_ * 1.5, 33, 26, -R_ - F_ * .7)


def relax(X, n):
    for _ in range(n):
        Y = X.copy()
        Y[1:-1] = (X[:-2] + X[2:] + np.roll(X, 1, 1)[1:-1] + np.roll(X, -1, 1)[1:-1]) / 4
        Y[-1] = (X[-2] * 2 + np.roll(X, 1, 1)[-1] + np.roll(X, -1, 1)[-1]) / 4
        X = X * .4 + Y * .6
    return X


def smooth_t(t):
    return t * t * (3 - 2 * t)


def lerp_prof(h, table):
    t = np.asarray(table, float)
    return [np.interp(h, t[:, 0], t[:, i]) for i in range(1, t.shape[1])]


def sect(h, th, prof, sq=2.2):
    W, D, Fc = lerp_prof(h, prof)
    c, s = np.cos(th), np.sin(th)
    ce = np.sign(c) * np.abs(c) ** (2 / sq)
    se = np.sign(s) * np.abs(s) ** (2 / sq)
    return h[..., None] * T_ + (Fc + D * ce)[..., None] * TF + (W * se)[..., None] * R_


DOUBLET = [(8, 17.5, 12.5, 0), (14, 16.4, 11.6, .4), (22, 15.6, 11.4, .8), (32, 16.6, 12.2, .8), (42, 17.8, 12, 0), (48, 18.4, 11, -.8), (52, 16.5, 9.5, -1.2), (55, 11.5, 8, -1.5), (58, 7.2, 6.6, -1.5)]
PLATE = [(16.4, 16.6, 12.8, 1), (21, 17.1, 14.2, 1.6), (27, 17.6, 14.9, 2), (33, 17.8, 14.6, 1.6), (40, 18, 13.7, .8), (46, 17.6, 12.4, -.2), (51, 16.2, 10.6, -.9), (55, 14, 9.2, -1.3)]


def plate_top(th):
    a = np.abs(np.degrees(th))
    return np.interp(a, [0, 8, 27, 34, 52, 70, 84, 110], [49.6, 50.6, 54.4, 54.6, 51.4, 44.5, 41.5, 40.5])


def plate_bot(th):
    return 16.6 + .3 * np.cos(th)


def rib(uv):
    u, v = uv[:, 0], uv[:, 1]
    th = u / 16
    vtip = 46.6 + np.minimum(np.abs(np.degrees(th)), 27) * .19
    d = v - vtip
    h = .32 * np.exp(-(d / .32) ** 2) * (np.abs(np.degrees(th)) < 30)
    top = plate_top(th)
    h += .3 * np.exp(-((v - (top - .55)) / .32) ** 2) - .1 * np.exp(-((v - (top - 1.3)) / .35) ** 2)
    h += .3 * np.exp(-((v - 17.3) / .3) ** 2)
    h += .1 * np.exp(-(u / 1.4) ** 2) * (v < vtip - .5)
    return h


def quilt(period=3.2, depth=.22, horiz=None):
    def f(uv):
        u = uv[:, 0] / period
        h = -depth * np.exp(-((u - np.round(u)) * period / .28) ** 2)
        if horiz:
            v = uv[:, 1] / horiz
            h += -depth * .6 * np.exp(-((v - np.round(v)) * horiz / .3) ** 2)
        return h
    return f


def bands(at, w=.35, amp=.28, axis=1):
    at = np.asarray(at, float)

    def f(uv):
        x = uv[:, axis][:, None] - at[None]
        return (amp * (np.exp(-((x + w * .5) / w) ** 2) - .6 * np.exp(-((x - w * .4) / (w * .6)) ** 2))).sum(1)
    return f


def add_torso(m, k):
    th = np.linspace(-math.pi, math.pi, 72, endpoint=False)
    h = np.linspace(DOUBLET[0][0], DOUBLET[-1][0], 30)
    P = sect(h[None, :] + 0 * th[:, None], th[:, None], DOUBLET, 2.4)
    m.grid(P, 'cloth', wrap=True, bump=quilt(3, .2), uv=np.stack(np.broadcast_arrays(th[:, None] * 15, h[None]), -1), period=2 * math.pi * 15)
    th = np.linspace(-math.radians(108), math.radians(108), 120)
    v = np.linspace(0, 1, 70)
    hb, ht = plate_bot(th), plate_top(th)
    H = hb[:, None] + (ht - hb)[:, None] * v[None]
    P = sect(H, np.broadcast_to(th[:, None], H.shape), PLATE, 2.3)
    uv = np.stack([np.broadcast_to(th[:, None] * 16, H.shape), H], -1)
    m.grid(P, 'steel', uv=uv, bump=rib, obj='plate')


def add_skirt(m, k):
    C, Rr, L, ext = 72, 26, 1.45, 3
    th = np.linspace(-math.pi, math.pi, C, endpoint=False)
    top = sect(np.full(C, 17.6), th, [(0, 16.2, 12.6, .8), (99, 16.2, 12.6, .8)], 2.3)
    out = unit(top - (17.6 * T_ + .8 * TF))
    rest = np.zeros((Rr, C, 3))
    for i in range(Rr):
        s_ = i * L
        rest[i] = top + out * s_ * .45 - T_ * s_ * .9
    tR, tL = unit(k.kneeR - k.hipR), unit(k.kneeL - k.hipL)
    cols = [('ell', Tp(5, .5), np.stack([R_, TF, T_]), np.array([17.5, 13.5, 14.])),
            ('cap', k.hipR + tR * 7, k.kneeR, 9.6), ('cap', k.hipL + tL * 7, k.kneeL, 9.6), ('floor', GROUND)]
    down = np.array([0, 1., 0])
    X0 = np.zeros_like(rest)
    X0[0] = top
    d = unit(out * .75 + down * .66)
    for i in range(1, Rr):
        hit = np.zeros(C, bool)
        X0[i] = push_out(X0[i - 1] + d * L, cols, .35, hit=hit)
        step = unit(X0[i] - X0[i - 1])
        d = np.where(hit[:, None], step, unit(step * .75 + down * .25))
    pin = np.zeros((Rr, C), bool)
    pin[0] = True
    X = drape(X0, pin, cols, steps=90, iters=6, rest=rest, wrap=True, friction=.97, bend=1.0, gravity=.03)
    X = relax(X, 2)
    u = th * 16.2
    v = np.arange(Rr) * L
    uv = np.stack(np.broadcast_arrays(u[:, None], v[None]), -1)
    Xc = np.transpose(X, (1, 0, 2))
    g = np.random.default_rng(7)
    per = 2 * math.pi * 16.2 / 17
    jit = g.normal(0, 1.1, 40)
    Lr = (Rr - 1) * L - ext

    def dags(uv):
        u, v = uv[:, 0] / per, uv[:, 1]
        i = np.floor(u).astype(int) % 40
        f = u - np.floor(u)
        end = Lr + jit[i] - 1.2 + 1.2 * np.sqrt(np.clip(1 - ((f - .43) / .43) ** 2, 0, 1))
        slit = (f > .86)
        return np.where(slit, v < Lr - 8 + jit[i], v < end)
    # Along VIEW, not the normal: the draped normal flips at folds and would lay the mail over the red.
    m.grid(Xc - VIEW * .6, 'mail', wrap=True, uv=uv, period=2 * math.pi * 16.2, line=False)
    m.grid(Xc, 'cloth', wrap=True, uv=uv, period=2 * math.pi * 16.2, cut=dags, bump=quilt(per / 2, .25))


def bend_dir(a, j, b):
    return -unit(unit(a - j) + unit(b - j))


def hinge(a, j, b, away):
    h = unit(np.cross(unit(a - j), unit(b - j)))
    return h if h @ away > 0 else -h


def cap(m, c, z, x, r, h, mat, ph0=-.25, **kw):
    z, x = unit(z), unit(x - (x @ unit(z)) * unit(z))
    y = np.cross(z, x)
    return ellipsoid(m, c, np.stack([x, y, z]), (r[0], r[1], h), mat, nu=36, nv=14, ph=(ph0, math.pi / 2), **kw)


def wing(m, c, nrm, up, r, mat, dome=1.4, **kw):
    nrm, up = unit(nrm), unit(up - (up @ unit(nrm)) * unit(nrm))
    side = np.cross(nrm, up)
    a = np.linspace(-math.pi, math.pi, 48, endpoint=False)
    rr = np.linspace(.05, 1, 10)
    rad = r * (.82 + .18 * np.cos(a) - .1 * np.cos(2 * a) ** 2)
    A, Rr = np.meshgrid(a, rr, indexing='ij')
    Rad = np.broadcast_to(rad[:, None], A.shape)
    P = c + (Rad * Rr * np.cos(A))[..., None] * up + (Rad * Rr * np.sin(A))[..., None] * side + (dome * (1 - Rr ** 2))[..., None] * nrm
    uv = np.stack([A * 4, Rr * r], -1)
    fl = lambda q: .22 * np.cos(q[:, 0] / 4 * 9) * np.clip(q[:, 1] / r * 1.4 - .2, 0, 1) + .25 * np.exp(-((q[:, 1] - r * .93) / .3) ** 2)
    return m.grid(P, mat, wrap=True, uv=uv, period=2 * math.pi * 4, bump=fl, **kw)


def limb(m, a, b, t0, t1, rads, hint, mat, **kw):
    t = np.linspace(t0, t1, 24)
    r = np.asarray(rads, float).reshape(len(rads), -1)
    r = np.stack([np.interp(t, np.linspace(t0, t1, len(r)), r[:, i % r.shape[1]]) for i in range(2)], 1)
    return tube(m, a + (b - a) * t[:, None], r, hint, mat, **kw)


STEEL = dict(mat='steel')
DARK = dict(mat='steel', tint=(.74, .77, .82), gain=.9)
RED = dict(mat='cloth', albedo='#9e2218', shade='#2c0606')


def add_arm(m, k, side):
    sh, el, wr = (k.shR, k.elR, k.wrR) if side > 0 else (k.shL, k.elL, k.wrL)
    away = side * R_
    ellipsoid(m, sh + away * .2, np.stack([R_, TF, T_]), (6.1, 6.5, 5.6), **RED, bump=quilt(2.6, .18), obj='red')
    limb(m, sh, el, 0, .9, [5.9, 5.5, 5.2], away, **RED, bump=quilt(2.6, .18), obj='red')
    limb(m, sh, el, .36, .96, [6.1, 5.9, 5.7], away, **STEEL, bump=bands([.5, 12], .3, .25))
    pt, hg = bend_dir(sh, el, wr), hinge(sh, el, wr, away)
    limb(m, el, wr, .1, .97, [5.3, 5.0, 4.5, 4.1], away, **STEEL, bump=bands([1.2], .3, .2))
    cap(m, el + pt * .8, pt, hg, (6.2, 6.5), 4.6, 'steel', bump=bands([3.4], .3, .25, 1))
    wing(m, el + hg * 5.6 + pt * 1.6, hg, unit(pt + unit(sh - el) * .6), 4.8 if side > 0 else 3.6, 'steel')
    add_dags(m, k, sh, el, wr, side)


def add_dags(m, k, sh, el, wr, side):
    away = side * R_
    ax = unit(el - sh)
    n1, n2 = perp_pair(ax, away)
    C, Rr, L = 40, 15, 1.5
    th = np.linspace(-math.pi, math.pi, C, endpoint=False)
    ring = sh + ax * 3.5 + (np.cos(th)[:, None] * n1 + np.sin(th)[:, None] * n2) * 7.0
    out = unit(ring - (sh + ax * 3.5))
    rest = np.stack([ring + (out * .25 + np.array([0, 1., 0]) * .97) * L * i for i in range(Rr)])
    cols = [('cap', sh, el, 6.4), ('cap', el, wr, 5.4), ('ell', Tp(36, 1), np.stack([R_, TF, T_]), np.array([18.8, 15.6, 22.])),
            ('cap', k.kneeR - unit(k.kneeR - k.hipR) * 6, k.kneeR, 8.4), ('floor', GROUND)]
    pin = np.zeros((Rr, C), bool)
    pin[0] = True
    X = drape(rest.copy(), pin, cols, steps=160, iters=5, rest=rest, wrap=True)
    Xc = np.transpose(X, (1, 0, 2))
    per = 2 * math.pi * 7 / 9
    g = np.random.default_rng(11 + side)
    jit = g.normal(0, 1.4, 12)

    def cut(q):
        u, v = q[:, 0] / per, q[:, 1]
        i = np.floor(u).astype(int) % 12
        f = u - np.floor(u)
        end = 17.5 + jit[i] - 2 + 2 * np.sqrt(np.clip(1 - ((f - .44) / .44) ** 2, 0, 1))
        return np.where(f > .88, v < 2.5, v < end)
    uv = np.stack(np.broadcast_arrays(th[:, None] * 7, (np.arange(Rr) * L)[None]), -1)
    m.grid(Xc, **RED, wrap=True, uv=uv, period=2 * math.pi * 7, cut=cut, bump=quilt(per, .2), obj='red')



def perp_pair(ax, hint):
    n1 = unit(hint - (hint @ ax) * ax)
    return n1, np.cross(ax, n1)


def finger(m, pts, r, bk, **kw):
    S = spline(pts, 22)
    seg = np.linalg.norm(np.diff(S, axis=0), axis=1)
    sarc = np.concatenate([[0], np.cumsum(seg)])
    Lf = sarc[-1]
    rad = r * np.sqrt(np.clip(1 - np.clip((sarc - (Lf - r)) / r, 0, 1) ** 2, .02, 1))
    tube(m, S, rad, bk, 'steel', nu=16, bump=bands(np.arange(.9, 12, 1.2), .22, .2), **kw)


def add_hand(m, el, wr, dorsal, side, droop=.6, curl=(.5, .7, .6), spread=.0):
    fo = unit(wr - el)
    bk = unit(dorsal - (dorsal @ fo) * fo)
    hd = unit(fo * math.cos(droop) - bk * math.sin(droop))
    bk = unit(bk * math.cos(droop) + fo * math.sin(droop))
    lat = np.cross(hd, bk) * side
    th = np.linspace(-math.pi, math.pi, 40, endpoint=False)
    S = [wr - fo * s for s in np.linspace(-.6, 9, 14)]
    rr = np.interp(np.linspace(-.6, 9, 14), [-.6, 1.5, 4, 6.5, 9], [4.4, 4.5, 5.0, 6.1, 7.0])
    cut = lambda q: q[:, 1] < 7.4 + 3.4 * np.clip(np.cos(q[:, 0] / 5), 0, 1) ** 5
    uv = np.stack(np.broadcast_arrays(th[:, None] * 5, np.linspace(0, 9.6, 14)[None]), -1)
    tube(m, S, rr, lat, 'steel', nu=40, uv=uv, period=2 * math.pi * 5, cut=cut, bump=bands([1.1, 2.2], .25, .25), obj=f'cuff{side}')
    body = [wr + hd * s - bk * .4 for s in np.linspace(-.5, 9.6, 10)]
    hw = np.stack([np.interp(np.linspace(-.5, 9.6, 10), [-.5, 3, 9.6], [3.9, 4.5, 4.6]), np.interp(np.linspace(-.5, 9.6, 10), [-.5, 5, 9.6], [2.1, 2.0, 1.6])], 1)
    tube(m, body, hw, lat, 'leather', albedo='#2e221a', sq=3, obj=f'hand{side}')
    cap(m, wr + hd * 4.6 + bk * .5, bk, hd, (5.6, 5.1), 2.3, 'steel', ph0=-.4, bump=bands([1.5, 3.0], .3, .25, 0), obj=f'hand{side}')
    tube(m, [wr + hd * 9.3 + bk * .7 + lat * x for x in np.linspace(-4.6, 4.6, 6)], [1.4] * 6, hd, 'steel', nu=16, obj=f'hand{side}')
    kn = wr + hd * 9.7
    for o, L, back in ((3.3, 9.0, 0), (1.1, 10.0, 0), (-1.1, 9.5, .2), (-3.25, 7.8, .7)):
        p = kn + lat * o - hd * back
        d = unit(hd + lat * o * spread)
        pts = [p - d * 2.0, p]
        for j, f in enumerate((.44, .32, .24)):
            d = unit(d * math.cos(curl[j]) - bk * math.sin(curl[j]))
            p = p + d * L * f
            pts.append(p)
        finger(m, pts, 1.18, bk, obj=f'hand{side}')
    tb = wr + hd * 2.6 + lat * 4.0 - bk * 1.2
    td = unit(hd * .8 + lat * .25 - bk * .55)
    finger(m, [tb - td, tb + td * 3.5, tb + td * 6.5 + hd * 1.2, tb + td * 8.2 + hd * 2.4 - bk * 1.0], 1.35, bk, obj=f'hand{side}')


def add_leg(m, hip, kn, an, side, fd, fu):
    away = side * R_
    pt, hg = bend_dir(hip, kn, an), hinge(hip, kn, an, away)
    limb(m, hip, kn, .2, .9, [(8.8, 8.4), (8.2, 7.8), (7.0, 6.8)], pt, **DARK, bump=bands([2], .3, .25))
    limb(m, hip, kn, .88, .97, [(7.3, 7.1), (7.0, 6.8)], pt, **DARK)
    cap(m, kn + pt * 1.4, pt, hg, (6.6, 6.2), 5.0, 'steel', tint=(.74, .77, .82), gain=.9, bump=bands([3.6], .3, .25, 1))
    wing(m, kn + hg * 6.2 + pt * 1.8, hg, unit(pt - unit(an - kn) * .3), 5.0, 'steel', tint=(.74, .77, .82), gain=.9)
    limb(m, kn, an, .04, .14, [(6.4, 6.3), (6.2, 6.0)], -pt, **DARK)
    limb(m, kn, an, .12, 1.03, [(5.9, 6.0), (6.6, 6.3), (6.1, 5.6), (5.0, 4.8), (4.3, 4.2), (4.3, 4.2)], -pt, **DARK, bump=bands([1.5], .3, .2))
    fd, fu = unit(fd), unit(fu - (fu @ unit(fd)) * unit(fd))
    sole = an - fu * 7.6
    xs = np.array([-6.5, -4.5, -1, 4, 9, 13, 16.5, 19.5, 22, 24])
    hh = np.array([3.4, 4.4, 5.2, 5.0, 4.0, 3.0, 2.3, 1.6, .9, .2])
    ww = np.array([3.6, 4.3, 4.6, 4.8, 5.0, 4.8, 4.0, 2.7, 1.4, .2])
    S = np.array([sole + fd * x + fu * (h * .95 if x > 0 else h * .9) for x, h in zip(xs, hh)])
    S = resample(spline(S, 40), 40)
    t = np.interp(np.linspace(0, 1, 40), np.linspace(0, 1, len(xs)), np.arange(len(xs)))
    rad = np.stack([np.interp(t, np.arange(len(xs)), ww), np.interp(t, np.arange(len(xs)), hh)], 1)
    th = np.linspace(-math.pi, math.pi, 36, endpoint=False)
    sv = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))])
    uv = np.stack(np.broadcast_arrays(th[:, None], sv[None]), -1)
    lames = bands(np.arange(9, 22, 2.6), .3, .24)
    tube(m, S, rad, unit(np.cross(fd, fu)), 'steel', **{k_: v for k_, v in DARK.items() if k_ != 'mat'}, sq=2.5, nu=36, uv=uv, period=2 * math.pi,
         bump=lambda q: lames(q) * (np.sin(q[:, 0]) < -.25))


def build(k=None):
    k = k or Skel()
    m = Mesh()
    add_torso(m, k)
    add_skirt(m, k)
    add_arm(m, k, 1)
    add_arm(m, k, -1)
    add_hand(m, k.elR, k.wrR, U_, 1, droop=.65, curl=(.55, .75, .55))
    add_hand(m, k.elL, k.wrL, unit(k.thighL_up - R_ * .25), -1, droop=.15, curl=(.3, .45, .35))
    add_leg(m, k.hipR, k.kneeR, k.ankleR, 1, unit(B(1, 0, -.08)), U_)
    add_leg(m, k.hipL, k.kneeL, k.ankleL, -1, unit(U_ * .62 + B(.55, 0, -.42)), unit(B(-.7, .55, .1)))
    H = add_bascinet(m, k)
    add_aventail(m, k, H)
    add_belts(m, k)
    add_sword(m, k)
    return m


SKULL = [(-12, 11.9, 10.6, -1.0), (-6, 11.55, 10.35, -.7), (0, 11.45, 10.25, -.6), (4, 11.2, 10.05, -.7), (7, 10.9, 9.8, -.8), (10, 10.1, 9.1, -1.1),
         (12.5, 9.0, 8.1, -1.4), (14.8, 7.6, 6.8, -1.7), (16.8, 5.9, 5.3, -2.0), (18.4, 4.0, 3.6, -2.2), (19.6, 2.2, 2.0, -2.4), (20.4, .7, .6, -2.5), (20.7, .1, .1, -2.5)]
VISOR = [(-14.8, 6.6, 3.6, 9.6), (-13, 8.3, 3.0, 12.6), (-10, 9.8, 2.4, 14.8), (-6, 10.8, 1.8, 15.6), (-2, 11.2, 1.3, 15.4), (1, 11.3, 1.0, 14.8),
         (3, 11.25, .9, 14.0), (5, 10.95, .7, 12.6), (7, 10.3, .5, 11.0)]
SLIT = (.5, 1.45, 1.2, 11.6)


def breaths():
    out = []
    for i, z in enumerate(np.arange(-2.3, -11.5, -1.55)):
        for u in np.arange(2.1 + (i % 2) * .8, 12, 1.6):
            if u < 11.2 + z * .42:
                out += [(u, z), (-u, z)]
    return out


BREATHS = breaths()


def head_frame(k, yaw=HEAD_YAW, droop=HEAD_DROOP, loll=HEAD_LOLL):
    hf = np.array([math.cos(yaw), 0, math.sin(yaw)])
    hr = np.array([-math.sin(yaw), 0, math.cos(yaw)])
    hu = U_.copy()
    hf, hu = hf * math.cos(droop) - hu * math.sin(droop), hu * math.cos(droop) + hf * math.sin(droop)
    hu, hr = hu * math.cos(loll) + hr * math.sin(loll), hr * math.cos(loll) - hu * math.sin(loll)
    return k.head, hf, hu, hr


def skull_rim(th):
    return np.interp(np.abs(np.degrees(th)), [0, 38, 58, 76, 96, 130, 180], [4.8, 4.6, -1, -10.5, -12, -11, -10.2])


def add_bascinet(m, k):
    c, hf, hu, hr = head_frame(k)
    H = lambda f, u, r: c + (np.asarray(f)[..., None] * hf + np.asarray(u)[..., None] * hu + np.asarray(r)[..., None] * hr) * HS
    th = np.linspace(-math.pi, math.pi, 96, endpoint=False)
    v = np.linspace(0, 1, 44)
    z0 = skull_rim(th)[:, None]
    Z = z0 + (SKULL[-1][0] - z0) * (1 - (1 - v[None]) ** 1.15)
    A, Bw, Cf = lerp_prof(Z, SKULL)
    P = H(Cf + A * np.cos(th)[:, None], Z, Bw * np.sin(th)[:, None])
    keel = .45 * np.exp(-(np.minimum(np.abs(th), math.pi - np.abs(th)) / .07) ** 2)[:, None] * np.clip((Z - 4) / 4, 0, 1)
    P = H(Cf + (A + keel) * np.cos(th)[:, None], Z, (Bw + keel) * np.sin(th)[:, None])
    uv = np.stack([np.broadcast_to(th[:, None] * 11, Z.shape), Z], -1)
    m.grid(P, 'steel', wrap=True, uv=uv, period=2 * math.pi * 11, obj='skull',
           bump=lambda q: .28 * np.exp(-((q[:, 1] - skull_rim(q[:, 0] / 11) - .5) / .35) ** 2)
           + .12 * np.exp(-(np.minimum(np.abs(q[:, 0]), math.pi * 11 - np.abs(q[:, 0])) / .35) ** 2) * (q[:, 1] > 5))
    al = np.linspace(-1, 1, 70)
    zz = np.linspace(VISOR[0][0], VISOR[-1][0], 60)
    Bv, Fs, Ff = lerp_prof(zz[None], VISOR)
    s_, c_ = np.sin(al[:, None] * math.pi / 2), np.cos(al[:, None] * math.pi / 2)
    prow = np.clip((zz[None] + 13.5) / 6, 0, 1) * np.clip((6.4 - zz[None]) / 2.5, 0, 1)
    ridge = 1.7 * np.clip(1 - np.abs(al[:, None]) * 1.9, 0, 1) * prow
    F = Fs + (Ff - Fs) * c_ ** .7 + ridge
    lift = np.clip((zz[None] - 1.5) / 1.2, 0, 1) * np.clip((6.2 - zz[None]) / 2, 0, 1) * .3
    P = H(F + lift, np.broadcast_to(zz[None], F.shape), Bv * s_ * 1.0)
    uv = np.stack([np.broadcast_to(al[:, None] * 17, F.shape), np.broadcast_to(zz[None], F.shape)], -1)
    holes = BREATHS
    z0, z1, u0, u1 = SLIT

    def vcut(q):
        u, z = q[:, 0], q[:, 1]
        keep = ~((z > z0) & (z < z1) & (np.abs(u) > u0) & (np.abs(u) < u1))
        for hu_, hz in holes:
            keep &= np.hypot(u - hu_, z - hz) > .3
        return keep

    def vbump(q):
        u, z = q[:, 0], q[:, 1]
        side = (np.abs(u) > u0 - .4) & (np.abs(u) < u1 + .4)
        h = .3 * np.exp(-((z - z1 - .35) / .32) ** 2) * side + .2 * np.exp(-((z - z0 + .3) / .3) ** 2) * side
        h += .25 * np.exp(-((z - VISOR[-1][0] + .5) / .35) ** 2) + .25 * np.exp(-((np.abs(u) - 16.4) / .4) ** 2) + .14 * np.exp(-(u / .3) ** 2)
        for hu_, hz in holes:
            d = np.hypot(u - hu_, z - hz)
            h += .12 * np.exp(-((d - .42) / .12) ** 2)
        return h
    m.grid(P, 'steel', uv=uv, cut=vcut, bump=vbump, obj='visor')
    for sd in (1, -1):
        tube(m, [H(.4, z, sd * 11.75) for z in np.linspace(-.6, 5.2, 8)], [(1.0, .32)] * 8, hf, 'steel', sq=3, nu=16, obj='hinge')
        tube(m, [H(1.3, z, sd * 12.15) for z in np.linspace(-.2, 4.8, 8)], [.42] * 8, hf, 'steel', nu=12, obj='hinge')
        ellipsoid(m, H(1.3, 4.8, sd * 12.15), np.stack([hf, hr, hu]), (.6, .6, .4), 'steel', nu=14, nv=6, ph=(0, math.pi / 2), obj='hinge', line=False)
    ellipsoid(m, c - hf * .8, np.stack([hf, hr, hu]), (10.2, 9.0, 11.5), 'void', line=False)
    tb = np.linspace(math.radians(64), math.radians(296), 80)
    zr = skull_rim(tb)
    A, Bw, Cf = lerp_prof(zr, SKULL)
    band = []
    for dz in np.linspace(-.6, 2.2, 6):
        band.append(H(Cf + (A + .35) * np.cos(tb), zr + dz, (Bw + .35) * np.sin(tb)))
    m.grid(np.stack(band, 1), 'leather', albedo='#24201c', shade='#0a0806', obj='band')
    for t_ in np.linspace(math.radians(76), math.radians(284), 13):
        zr_ = skull_rim(np.array([t_]))
        A_, B_, C_ = lerp_prof(zr_ + .8, SKULL)
        p = H(C_ + (A_ + .7) * np.cos(t_), zr_ + .8, (B_ + .7) * np.sin(t_))[0]
        nrm = unit(p - (c + hu * (zr_[0] + .8)))
        ellipsoid(m, p, np.stack([np.cross(nrm, hu), hu, nrm]), (.45, .45, .3), 'steel', tint=(1, .8, .45), nu=12, nv=6, ph=(0, math.pi / 2), line=False, obj='band')
    return H


def add_aventail(m, k, H):
    c, hf, hu, hr = head_frame(k)
    hf, hu, hr = hf * HS, hu * HS, hr * HS
    C, Rr, L = 140, 27, 1.0
    th = np.linspace(-math.pi, math.pi, C, endpoint=False)
    a = np.abs(np.degrees(th))
    zr = np.where(a > 60, skull_rim(th) - .5, np.interp(a, [0, 30, 60], [-13.2, -12.8, -11.5]))
    A, Bw, Cf = lerp_prof(zr, SKULL)
    fr = np.where(a > 60, Cf + (A + .5) * np.cos(th), 3.0 + 6.6 * np.cos(th))
    top = H(fr, zr, (Bw + .5) * np.sin(th) * np.where(a > 60, 1, np.interp(a, [0, 60], [.75, 1])))
    ctr = c + hu * -12
    out = unit((top - ctr) - ((top - ctr) @ hu)[:, None] * hu)
    ax = np.stack([R_, TF, T_])
    cols = [('cap', k.neck - T_ * 6, k.head, 6.2), ('cap', k.shR, k.shL, 8.0), ('ell', Tp(40, 1.2), ax, np.array([19.5, 15.8, 17.])),
            ('cap', k.shR, k.elR, 6.8), ('cap', k.shL, k.elL, 6.8), ('ell', Tp(46, -4), ax, np.array([20.5, 12.5, 12.])),
            ('ell', k.shR + R_ * .2, ax, np.array([6.9, 7.3, 6.4])), ('ell', k.shL - R_ * .2, ax, np.array([6.9, 7.3, 6.4]))]
    rest = np.zeros((Rr, C, 3))
    X0 = np.zeros((Rr, C, 3))
    X0[0] = rest[0] = top
    d = unit(out * .9 - hu * .45)
    for i in range(1, Rr):
        rest[i] = top + d * L * i
        X0[i] = push_out(X0[i - 1] + d * L, cols, .3)
        d = unit(unit(X0[i] - X0[i - 1]) * .6 + np.array([0, 1., 0]) * .4)
    pin = np.zeros((Rr, C), bool)
    pin[0] = True
    X = drape(X0, pin, cols, steps=320, iters=6, rest=rest, wrap=True, gravity=.08)
    X = relax(X, 6)
    Xc = np.transpose(X, (1, 0, 2))
    uv = np.stack(np.broadcast_arrays(th[:, None] * 11, (np.arange(Rr) * L)[None]), -1)
    ln = lambda u: np.interp(np.abs(np.degrees(u / 11)), [0, 40, 80, 180], [17, 19, 23, 25])
    m.grid(Xc, 'mail', wrap=True, uv=uv, period=2 * math.pi * 11, cut=lambda q: q[:, 1] < ln(q[:, 0]), obj='aventail',
           pitch=.86, ring=.4, wire=.17, tint=(.72, .75, .8))


def ribbon(m, S, wdir, w, mat, thick=.25, **kw):
    S = np.asarray(S, float)
    wd = np.broadcast_to(np.asarray(wdir, float), S.shape)
    n = unit(np.cross(np.gradient(S, axis=0), wd))
    P = np.stack([S - wd * w / 2, S - wd * w / 2 + n * thick, S + wd * w / 2 + n * thick, S + wd * w / 2], 0)
    return m.grid(P, mat, **kw)


def add_belts(m, k):
    th = np.linspace(-math.radians(112), math.radians(112), 90)
    rows = []
    for h in np.linspace(16.2, 19.8, 5):
        p = sect(np.full_like(th, h), th, PLATE, 2.3)
        ctr = h * T_ + 1.0 * TF
        rows.append(p + unit(p - ctr) * .45)
    m.grid(np.stack(rows, 1), 'leather', albedo='#2a2420', shade='#0a0806', gloss=.6, obj='belt')
    bq = math.radians(14)
    p = sect(np.array([18.0]), np.array([bq]), PLATE, 2.3)[0]
    nrm = unit(p - (18 * T_ + TF))
    side = np.cross(T_, nrm)
    fr = [p + nrm * .7 + side * x + T_ * y for x, y in ((-1.8, 2.4), (1.8, 2.4), (1.8, -2.4), (-1.8, -2.4), (-1.8, 2.4))]
    tube(m, resample(fr, 24), [.42] * 24, nrm, 'steel', tint=(1, .82, .5), gain=.95, nu=10, obj='buckle')
    strap = [p + nrm * .9 - T_ * 1, p + nrm * 2.4 - T_ * 4.5 + TF * .5, p + nrm * 4.5 - T_ * 8 + TF * 3, p + nrm * 6 - T_ * 11 + TF * 6.5 + R_ * 1, p + nrm * 6.4 - T_ * 13 + TF * 10 + R_ * 1.5]
    S = spline(strap, 26)
    ribbon(m, S, side, 3.0, 'leather', albedo='#2a2420', shade='#0a0806', gloss=.6, obj='strap')
    e = S[-1]
    d = unit(S[-1] - S[-3])
    tube(m, [e - d * .3, e + d * 3.2], [(1.7, .45), (1.4, .4)], side, 'steel', tint=(1, .82, .5), gain=.95, nu=16, obj='strap')
    th = np.linspace(-math.radians(130), math.radians(130), 90)
    h = 9 + 3.5 * np.sin(th)
    rows = []
    for dh in np.linspace(-1.8, 1.8, 4):
        q = h[:, None] * T_ + (2.0 + 15.6 * np.cos(th))[:, None] * TF + (19.4 * np.sin(th))[:, None] * R_ + T_ * dh
        rows.append(q)
    rows = np.stack(rows, 1)
    for _ in range(3):
        flat = push_out(rows.reshape(-1, 3).copy(), [('cap', k.hipR, k.kneeR, 10.4), ('cap', k.hipL, k.kneeL, 10.4)], .1)
        rows = flat.reshape(rows.shape)
    m.grid(rows, 'leather', albedo='#6a4426', shade='#1e1008', gloss=.5, obj='hipbelt')


def add_sword(m, k):
    tip = B(4, 0, 36) + np.array([0, GROUND - .5, 0])
    ax = unit(U_ * .95 - F_ * .28 + R_ * .1)
    wd = unit(np.cross(ax, VIEW))
    fl = np.cross(wd, ax)
    cr = tip + ax * 89
    s = np.linspace(0, 89, 60)
    w = np.interp(s, [0, 30, 60, 80, 86.5, 89], [5.3, 4.6, 3.5, 2.4, 1.0, .05]) / 2
    t = np.interp(s, [0, 60, 89], [.8, .55, .2]) / 2
    lat = np.linspace(-1, 1, 21)
    fuller = lambda q: -.15 * np.exp(-(q[:, 0] / .6) ** 4) * smooth_t(np.clip((q[:, 1] - 1) / 3, 0, 1)) * smooth_t(np.clip((34 - q[:, 1]) / 6, 0, 1))
    for sgn in (1, -1):
        P = cr[None, None] - ax * s[None, :, None] + wd * (lat[:, None] * w[None])[..., None] + fl * (sgn * (1 - np.abs(lat[:, None]) ** 1.4) * t[None])[..., None]
        uv = np.stack(np.broadcast_arrays(lat[:, None] * w[None], s[None]), -1)
        m.grid(P, 'steel', uv=uv, bump=fuller, obj='sword', gain=.86, tint=(.94, .96, 1))
    arc = [cr + wd * x - ax * (2.4 * (abs(x) / 12) ** 2.2) for x in np.linspace(-12.2, 12.2, 9)]
    tube(m, spline(arc, 30), np.stack([np.interp(np.linspace(0, 1, 30), [0, .1, .5, .9, 1], [.95, .75, .85, .75, .95]), np.full(30, .8)], 1), fl, 'steel', sq=2.6, nu=16, obj='sword')
    g0 = cr + ax * .6
    tube(m, [g0 + ax * x for x in np.linspace(0, 22, 12)], np.interp(np.linspace(0, 22, 12), [0, 11, 22], [1.55, 1.4, 1.3]), wd, 'leather', albedo='#3a2216', shade='#100804', gloss=.5, nu=18,
         bump=lambda q: .1 * np.cos(q[:, 1] * 2 * math.pi / .9 + q[:, 0] * 1.2), obj='grip')
    pc = g0 + ax * 24.6
    tube(m, [pc - fl * x for x in np.linspace(-1.35, 1.35, 8)], np.interp(np.linspace(-1.35, 1.35, 8), [-1.35, -1, 0, 1, 1.35], [2.2, 2.9, 3.0, 2.9, 2.2]), wd, 'steel', nu=30, obj='pommel')
    for sgn in (-1, 1):
        cap(m, pc + fl * 1.3 * sgn, fl * sgn, wd, (1.4, 1.4), .7, 'steel', obj='pommel')


def leaves(P):
    a, b = light_basis(SUN)
    q1, q2 = P @ a, P @ b
    v = np.sin(q1 * .23 + 1.3) * np.sin(q2 * .19 + .4) + .6 * np.sin(q1 * .11 - q2 * .13 + 2) + .4 * np.sin(q1 * .37 + q2 * .29)
    hole = np.clip((v - .05) / .45, 0, 1)
    high = np.clip((-P[:, 1] - 30) / 45, 0, 1)
    return 1 - high * .75 * hole


def render_knight(ppcm, ss=2):
    k = Skel()
    m = build(k)
    o = np.array([-80., -126.])
    size = (int(math.ceil(196 * ppcm)), int(math.ceil(150 * ppcm)))
    img, a, info = render(m, ppcm, o, size, ss=ss, light=leaves)
    sh = ground_shadow(info, ppcm, o, size, GROUND, ss=ss)
    return img, a, sh, o, np.array(size) / ppcm
