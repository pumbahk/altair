# encoding: utf-8
import re
import numpy

from .constants import SVG_NAMESPACE

I = numpy.matrix('1 0 0; 0 1 0; 0 0 1', dtype=numpy.float64)

def as_user_unit(size, rel_unit=None):
    if size is None:
        return None
    spec = re.match('(-?[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(pt|pc|mm|cm|in|px|em|%)?', size.strip().lower())
    if spec is None:
        raise Exception('Invalid length / size specifier: ' + size)
    degree = float(spec.group(1))
    unit = spec.group(2) or 'px'
    if unit == 'pt':
        return degree * 1.25
    elif unit == 'pc':
        return degree * 15
    elif unit == 'mm':
        return degree * 90 / 25.4
    elif unit == 'cm':
        return degree * 90 / 2.54
    elif unit == 'in':
        return degree * 90.
    elif unit == 'px':
        return degree
    elif unit == 'em':
        if rel_unit is None:
            raise Exception('Relative size specified where no unit size is given in the applied context')
        return rel_unit * degree
    elif unit == '%':
        if rel_unit is None:
            raise Exception('Relative size specified where no unit size is given in the applied context')
        return rel_unit * degree / 100.

def translate(x, y):
    return numpy.matrix(
        [
            [1., 0., float(x)],
            [0., 1., float(y)],
            [0., 0., 1.]
            ],
        dtype=numpy.float64)

def parse_transform(transform_str):
    for g in re.finditer(ur'\s*([A-Za-z_-][0-9A-Za-z_-]*)\s*\(\s*((?:[^\s,]+(?:\s*,\s*|\s+))*[^\s,]+)\s*\)\s*', transform_str):
        f = g.group(1)
        args = re.split(ur'\s*,\s*|\s+',g.group(2).strip())
        if f == u'matrix':
            if len(args) != 6:
                raise Exception('invalid number of arguments for matrix()')
            return numpy.matrix(
                [
                    [float(args[0]), float(args[2]), float(args[4])],
                    [float(args[1]), float(args[3]), float(args[5])],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'translate':
            if len(args) != 2:
                raise Exception('invalid number of arguments for translate()')
            return translate(args[0], args[1])
        elif f == u'scale':
            if len(args) != 2:
                raise Exception('invalid number of arguments for scale()')
            return numpy.matrix(
                [
                    [float(args[0]), 0., 0.],
                    [0., float(args[1]), 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'rotate':
            if len(args) != 1:
                raise Exception('invalid number of arguments for rotate()')
            t = float(args[0]) * numpy.pi / 180.
            c = numpy.sin(t)
            s = numpy.sin(t)
            return numpy.matrix(
                [
                    [c, -s, 0.],
                    [s, c, 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'skeyX':
            if len(args) != 1:
                raise Exception('invalid number of arguments for skewX()')
            t = float(args[0]) * numpy.pi / 180.
            ta = numpy.tan(t)
            return numpy.matrix(
                [
                    [1., ta, 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'skeyY':
            if len(args) != 1:
                raise Exception('invalid number of arguments for skewY()')
            t = float(args[0]) * numpy.pi / 180.
            ta = numpy.tan(t)
            return numpy.matrix(
                [
                    [1., 0., 0.],
                    [ta, 1., 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
