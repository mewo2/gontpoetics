import cairosvg
import re
from geom import Point, normalize, dist


class Element(object):
    _defaults = {}

    def __init__(self, *args, **kwargs):
        self._contents = list(args)
        for k, v in self._defaults.items():
            setattr(self, k, v)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        s = '<%s' % self._element
        attrs = [a for a in vars(self) if not a.startswith('_')]
        for a in attrs:
            s += ' %s="%s"' % (re.sub('_', '-', a), str(getattr(self, a)))
        if self._contents:
            s += '>\n'
            for c in self._contents:
                s += str(c)
            s += '</%s>\n' % self._element
        else:
            s += '/>\n'
        return s

    def append(self, x):
        self._contents.append(x)

    def save(self, filename):
        with open(filename, "w") as f:
            f.write(str(self))

    def savepdf(self, filename):
        cairosvg.svg2pdf(
            bytestring=str(self).encode("utf8"), write_to=filename)


class SVG(Element):
    _element = 'svg'
    _defaults = {
        "xmlns": "http://www.w3.org/2000/svg",
        "stroke_linecap": "round",
        "stroke_linejoin": "round"
    }


class Group(Element):
    _element = 'g'


class Circle(Element):
    _element = 'circle'


class Rect(Element):
    _element = 'rect'


class Line(Element):
    _element = 'line'


class Path(Element):
    _element = 'path'


class Text(Element):
    _element = 'text'


class Comment(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return "<!-- %s -->\n" % self.text


def towards(p0, p1, d):
    d = min(dist(p1, p0) / 2, d)
    return p0 + normalize(p1 - p0) * d


def polypath(*polys, **kwargs):
    d = ''
    for poly in polys:
        poly = [Point(p[0], p[1]) for p in poly]

        pts = [(towards(poly[i], poly[i - 1], 1e-2), poly[i],
                towards(poly[i], poly[(i + 1) % len(poly)], 1e-2))
               for i in range(len(poly))]
        started = False
        for p0, p1, p2 in pts:
            d += '%s%f,%f Q%f,%f %f,%f' % ('L' if started else 'M', p0.x, p0.y,
                                           p1.x, p1.y, p2.x, p2.y)
            started = True
        d += 'z'
    return Path(d=d, **kwargs)
