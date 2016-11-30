import svg
from geom import Point
import math
import random


class Glyph(object):
    def __init__(self, *points, broken=False, offset=None):
        self.points = [Point(*p) for p in points]
        self.broken = broken
        if offset is None:
            offset = (self.points[-1].x, 0)
        self.offset = Point(*offset)

    def flipped(self):
        points = [(p.x, -p.y) for p in self.points]
        offset = (self.offset.x, -self.offset.y)
        return Glyph(*points, broken=self.broken, offset=offset)


loopup = Glyph((0, 0), (0.6, 0.15), (0.5, 1), (0.3, 0.15), (1, 0))
loopdown = loopup.flipped()
hookup = Glyph((0, 0), (0.15, 0.1), (0.25, 0.6), (0.4, 0))
hookdown = hookup.flipped()
curldown = Glyph(
    (0, -0.25), (0.3, 0), (0.5, -0.75), (0.25, -0.5),
    broken=True,
    offset=(0.55, 0))
table = Glyph((0, 0), (0.25, 0.0), (0.1, 0.5), (0.5, 0.3), (0.9, 0.5),
              (0.75, 0.0), (1, 0))

eight = Glyph((0, 0), (0.1, -0.05), (0.3, 0.4), (0.1, 0.3), (0.3, -0.4),
              (0.1, -0.3), (0.3, -0.1), (0.5, 0))
up = Glyph(
    (0, 0), (0.5, -0.25), (0.4, 0.25), (0.5, 1), broken=True, offset=(0.6, 0))

bulb = Glyph(
        (0,0), (0.2, 0.6), (0.2, -0.2), (0.4, -0.2), (0.35, 0.6), (0.6, 0))

slash = Glyph(
        (0,0), (0.15, 0), (0.3, -0.7), (0.3, 0.7), (0.45, 0), (0.6, 0))
brokenslash = Glyph(
        (0,0), (0.15, 0), (0.3, -0.7), (0.3, 0.7), broken=True,
        offset=(0.4, 0))
allglyphs = [loopup, loopdown, hookup, hookdown, curldown,
        slash, table, eight, up, bulb, brokenslash]

#kink = Glyph(
#(0, -0.5),
#[(0.25, 0), (0.35, 0.5), (0.25, -0.25)],
#[(0.15, -0.5), (0.25, 0), (0.5, 0)])

#up = Glyph(
#(0,0),
#[(0.75, 0), (0.5, 0), (0.5, 1)],
#broken=True,
#offset=(0.5, 0))


def join(glyphs):
    runs = []
    offset = Point(0, 0)
    points = []
    for g in glyphs:
        pts = g.points
        if points:
            points = points[:-1]
            pts = pts[1:]
        points += [offset + p for p in pts]
        offset += g.offset
        if g.broken:
            runs.append(points)
            points = []
    if points:
        runs.append(points)
    return runs


def bestp(p2, p3, p4, tau):
    return p4 + p3 - p2 - 6 * tau * (p3 - p2)


def path(runs, tau=0.5):
    d = ''
    for run in runs:
        run = [bestp(run[0], run[1], run[2], tau)] + run + [
            bestp(run[-1], run[-2], run[-3], tau)
        ]
        d += 'M %.2f,%.2f' % run[1]
        for i in range(len(run) - 3):
            p1 = run[i]
            p2 = run[i + 1]
            p3 = run[i + 2]
            p4 = run[i + 3]
            pts = [p2 + (p3 - p1) / (6 * tau), p3 - (p4 - p2) / (6 * tau), p3]
            d += ' C'
            for pt in pts:
                d += ' %.2f,%.2f' % pt
    return svg.Path(d=d)


def mappts(runs, f):
    return [[f(p) for p in run] for run in runs]


def linear(runs, scale=100.):
    return mappts(runs, lambda p: scale * p)


def circular(runs, rscale=20., thetascale=1.):
    def f(p):
        return rscale * (1.25 + p.y) ** 0.5 * \
                Point(math.cos(thetascale * p.x),
                      math.sin(thetascale * p.x))

    return mappts(runs, f)


def noisy(cmds, r=0.):
    def f(p):
        return p + Point(random.gauss(0, r), random.gauss(0, r))

    return mappts(cmds, f)


def ring(glyphs):
    offset = Point(0, 0)
    for g in glyphs:
        offset += g.offset
    thetascale = 2 * math.pi / (offset.x + 0.5)
    return path(noisy(circular(join(glyphs), thetascale=thetascale)))


glyphdict = dict(zip('AEIOUPTKMSL'.lower(), allglyphs))


def makeglyph(word, x, y, theta, label=True):
    glyphs = [glyphdict[c] for c in word]
    g = svg.Group(
        ring(glyphs),
        transform='translate(%.2f, %.2f) rotate(%.2f)' % (x, y, theta))
    if label:
        g.append(
            svg.Group(
                svg.Text(
                    word,
                    stroke='none',
                    font_size=9,
                    font_family='sans-serif',
                    fill='black',
                    text_anchor='middle',
                    alignment_baseline='middle'),
                transform='rotate(%.2f)' % -theta))
    return g


def radius(row):
    return ((row + 1) * 2)**0.5 - 0.75


def renderglyph(word, scale=60):
    s = svg.SVG(width=scale * 1.2,
                height=scale * 1.2,
                stroke='black',
                fill='none',
                stroke_width=2)

    g = svg.Group(transform='translate(%.2f,%.2f)' %
                  (scale * 0.6, scale * 0.6))
    s.append(g)
    g.append(makeglyph(word, 0, 0, -90, label=False))
    return s


def renderpoem(poem, scale=60):
    r = radius(len(poem)) + 0.3
    s = svg.SVG(
        width=2 * r * scale,
        height=2 * r * scale,
        #viewBox='-50 -50 100 100',
        stroke='black',
        fill='none',
        stroke_width=2)

    g = svg.Group(transform='translate(%.2f,%.2f)' % (r * scale, r * scale))
    s.append(g)

    g2 = svg.Group(transform='scale(8)', stroke='lightgrey')
    g.append(g2)

    for row, line in enumerate(poem):
        r = radius(row)
        offset = 0.5 + row * 1.618
        for pos, word in enumerate(line):
            theta = (pos - 0.5 + offset % 1) * (360 / len(line)) - 90
            x = scale * r * math.cos(math.radians(theta))
            y = scale * r * math.sin(math.radians(theta))
            g.append(makeglyph(word, x, y, theta, label=False))
    return s

if __name__ == '__main__':
    for c in glyphdict:
        renderglyph(c * 6).savepdf(c + "-test.pdf")
    for word in ['lisuta', 'pekoma']:
        renderglyph(word).savepdf(word +'-test.pdf')

