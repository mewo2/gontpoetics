from collections import namedtuple
import random


class Point(namedtuple("Point", "x y")):
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        assert not isinstance(other, Point), "Can't multiply Point * Point"
        return Point(self.x * other, self.y * other)

    def __rmul__(self, other):
        assert not isinstance(other, Point), "Can't multiply Point * Point"
        return Point(other * self.x, other * self.y)

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __str__(self):
        return "Point(%.3f, %.3f)" % self

    def __repr__(self):
        return "Point(%.3f, %.3f)" % self

    def perp(self):
        return Point(-self.y, self.x)


def normalize(a):
    return a / (a.x**2 + a.y**2)**0.5


def dist(a, b):
    return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5


def dot(a, b):
    return a.x * b.x + a.y * b.y


def ccw(a, b, c):
    return (b.y - a.y) * (c.x - a.x) < (c.y - a.y) * (b.x - a.x)


def intersect(seg1, seg2):
    a, b = seg1
    c, d = seg2
    return (ccw(a, b, c) ^ ccw(a, b, d)) and (ccw(c, d, a) ^ ccw(c, d, b))


def get_intersect(p, d, seg):
    return ray_intersect((p, d), (seg[0], seg[1] - seg[0]))


def segline_intersect(seg, line):
    a, b = seg
    c, d = line
    det = (a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x)
    if det == 0:
        return None
    inpt = Point(((a.x * b.y - a.y * b.x) * (c.x - d.x) -
                  (c.x * d.y - c.y * d.x) * (a.x - b.x)) / det,
                 ((a.x * b.y - a.y * b.x) * (c.y - d.y) -
                  (c.x * d.y - c.y * d.x) * (a.y - b.y)) / det)
    pos = dot(inpt - a, b - a) / dot(b - a, b - a)
    if pos < 0 or pos > 1:
        return None
    return inpt


def ray_intersect(ray1, ray2):
    a, b = ray1[0], ray1[0] + ray1[1]
    c, d = ray2[0], ray2[0] + ray2[1]
    det = (a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x)
    inpt = Point(((a.x * b.y - a.y * b.x) * (c.x - d.x) -
                  (c.x * d.y - c.y * d.x) * (a.x - b.x)) / det,
                 ((a.x * b.y - a.y * b.x) * (c.y - d.y) -
                  (c.x * d.y - c.y * d.x) * (a.y - b.y)) / det)
    if dot(inpt - ray1[0], ray1[1]) < 0 or dot(inpt - ray2[0], ray2[1]) < 0:
        return None
    return inpt


def signed_area(a, b, c):
    return 0.5 * ((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x))


def in_poly(pt, poly):
    wn = 0
    prev = poly[-1]
    for p in poly:
        if p.y > pt.y and prev.y <= pt.y:
            if dot(pt - prev, (p - prev).perp()) > 0:
                wn += 1
        if p.y <= pt.y and prev.y > pt.y:
            if dot(pt - prev, (p - prev).perp()) < 0:
                wn -= 1
        prev = p
    return wn != 0


def area(poly):
    a = poly[0]
    prev = poly[1]
    area = 0
    for p in poly[2:]:
        area += signed_area(a, prev, p)
        prev = p
    return area


def is_convex(poly):
    n = len(poly)
    for i in range(n):
        if not ccw(poly[i - 2], poly[i - 1], poly[i]):
            return False
    return True


def obb(poly):
    hull = convex_hull(poly)
    axes = [normalize(hull[i] - hull[i - 1]) for i in range(len(hull))]
    boxes = []
    for axis in axes:
        aperp = axis.perp()
        l = min(dot(p, axis) for p in hull)
        r = max(dot(p, axis) for p in hull)
        t = max(dot(p, aperp) for p in hull)
        b = min(dot(p, aperp) for p in hull)
        box = OrientedBox(axis, l, r, t, b)
        boxes.append(box)
    return min(boxes, key=lambda b: b.area)


def simplifypoly(poly):
    nxt = dict([(poly[i - 1], poly[i]) for i in range(len(poly))])
    prv = dict([(poly[i], poly[i - 1]) for i in range(len(poly))])

    changed = True
    while changed:
        changed = False
        pts = nxt.keys()
        for pt in pts:
            p = prv[pt]
            n = nxt[pt]
            dy = normalize(n - p).perp()
            if abs(dot(pt - p, dy)) < 1e-2:
                del prv[pt]
                del nxt[pt]
                prv[n] = p
                nxt[p] = n
                changed = True
    p, n = nxt.popitem()
    newpoly = [p]
    while n in nxt:
        p, n = n, nxt[n]
        newpoly.append(p)
    return newpoly


def centroid(poly):
    p0 = Point(0, 0)
    cntr = sum([(poly[i - 1] + poly[i]) * signed_area(p0, poly[i - 1], poly[i])
                for i in range(len(poly))], p0) / (3 * area(poly))
    assert min(p.x for p in poly) <= cntr.x <= max(p.x for p in poly)
    assert min(p.y for p in poly) <= cntr.y <= max(p.y for p in poly)
    return cntr


class OrientedBox(namedtuple("OrientedBox", "axis left right top bottom")):
    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def corners(self):
        dx = self.axis
        dy = dx.perp()
        return [
            dx * self.left + dy * self.bottom,
            dx * self.right + dy * self.bottom,
            dx * self.right + dy * self.top, dx * self.left + dy * self.top
        ]

    @property
    def edges(self):
        cs = self.corners
        return [(cs[i - 1], cs[i]) for i in range(4)]

    @property
    def area(self):
        return (self.right - self.left) * (self.top - self.bottom)

    def overlaps(self, poly):
        polyedges = [(poly[i - 1], poly[i]) for i in range(len(poly))]
        for e1 in self.edges:
            for e2 in polyedges:
                if intersect(e1, e2):
                    return True
        return False

    def splitline(self):
        dx = self.axis
        dy = dx.perp()
        alpha = (random.random() + 1) / 3
        if self.right - self.left < self.top - self.bottom:
            midp = self.top + alpha * (self.bottom - self.top)
            return dx * self.right + dy * midp, dx * self.left + dy * midp
        else:
            midp = self.left + alpha * (self.right - self.left)
            return dy * self.top + dx * midp, dy * self.bottom + dx * midp
