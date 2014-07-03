# encoding: utf-8

import sys
import re
import cssutils
import logging
from lxml import etree
import numpy
import numpy.linalg
from altair.svg.constants import SVG_NAMESPACE
from altair.app.ticketing.tickets.constants import *
from altair.svg.geometry import parse_transform, I, to_matrix_string
from altair.svg.path import tokenize_path_data, parse_poly_data, PathDataScanner, PathDataEmitter


__all__ = (
    'cleanup_svg',
    )

logger = logging.getLogger(__name__)

ALIGNMENT_COMPAT_MAP = {
    u'left': u'start',
    u'center': u'middle',
    u'right': u'end',
    u'start': u'start',
    u'middle': u'middle',
    u'end': u'end',
    }

class FormatError(Exception):
    pass

def override_styles(olddecl, newdecl):
    retval = cssutils.css.CSSStyleDeclaration()
    for k in olddecl.keys():
        retval.setProperty(olddecl.getProperty(k))
    for k in newdecl.keys():
        retval.setProperty(newdecl.getProperty(k))
    return retval

def parse_style(*args, **kwargs):
    decl = cssutils.parseStyle(*args, **kwargs)
    text_align = decl.getProperty(u'text-align')
    if text_align is not None:
        text_align = text_align.value
    text_align = ALIGNMENT_COMPAT_MAP.get(text_align)
    if text_align is not None:
        decl.setProperty(u'text-align', text_align)
    else:
        decl.removeProperty(u'text-align')
    return decl

def css_text(decl):
    return re.sub(ur'\r\n|\r|\n', ' ', decl.cssText)

def set_or_remove_if_empty(elem, name, value):
    if not isinstance(value, basestring):
        value = unicode(value)
    attrib = elem.attrib
    if len(value) > 0:
        attrib[name] = value
    else:
        if name in attrib:
            del attrib[name]

def strip_common_style_properties(elems):
    common_style = cssutils.css.CSSStyleDeclaration()
    uncommons = set()
    for elem in elems:
        style_str = elem.get(u'style')
        style = parse_style(style_str, validate=False)
        commons = common_style.keys()
        for v in style.getProperties():
            cv = common_style.getProperty(v.name)
            if v.name not in uncommons:
                if cv is None:
                    common_style.setProperty(v)
                else:
                    if cv.propertyValue.cssText != v.propertyValue.cssText:
                        common_style.removeProperty(v.name)
                        uncommons.add(v.name)
        for k in commons:
            if style.getProperty(k) is None:
                common_style.removeProperty(k)
                uncommons.add(k)

    for elem in elems:
        style_str = elem.get(u'style')
        style = parse_style(style_str, validate=False)
        for k in common_style.keys():
            style.removeProperty(k)
        set_or_remove_if_empty(elem, u'style', css_text(style))

    return common_style 

def collect_flowpara_and_flowdivs(retval, style, elem):
    for child_elem in elem:
        if child_elem.tag == u'{%s}flowDiv' % SVG_NAMESPACE:
            style_str = child_elem.get(u'style')
            if style_str is not None:
                _style = override_styles(style, parse_style(style_str, validate=False))
            else:
                _style = style
            collect_flowpara_and_flowdivs(retval, _style, child_elem)
            elem.remove(child_elem)
        elif child_elem.tag == u'{%s}flowPara' % SVG_NAMESPACE:
            style_str = child_elem.get(u'style')
            if style_str is not None:
                _style = override_styles(style, parse_style(style_str, validate=False))
            else:
                _style = style
            set_or_remove_if_empty(child_elem, u'style', css_text(_style))
            retval.append(child_elem)
            elem.remove(child_elem)

def attach_fill_and_stroke_none_if_not_specified(elem):
    fill = elem.get(u'fill')
    if fill is None:
        elem.set(u'fill', u'none')
    stroke = elem.get(u'stroke')
    if stroke is None:
        elem.set(u'stroke', u'none')

def handle_flowregion(flowregion):
    first_child = flowregion[0]
    del flowregion[1:]
    first_child.set(u'style', u'fill:none; stroke:none;')
    attach_fill_and_stroke_none_if_not_specified(first_child)

def check_if_container_is_empty(n):
    tags = [tagname % SVG_NAMESPACE for tagname in (u'{%s}flowPara', u'{%s}flowDiv', u'{%s}flowSpan')]
    for cn in n:
        if cn.text or cn.tail or cn.tag not in tags or not check_if_container_is_empty(cn):
            return False
    else:
        return True

def check_if_flowroot_is_empty(flowroot):
    blockelems = []
    outertags = [tagname % SVG_NAMESPACE for tagname in (u'{%s}flowPara', u'{%s}flowDiv')]
    return all(check_if_container_is_empty(cn) and not cn.text and not cn.tail for cn in flowroot if cn.tag in outertags)

def cleanup_elem(elem):
    for child_elem in list(elem):
        if child_elem.tag == u'{%s}flowRoot' % SVG_NAMESPACE:
            if check_if_flowroot_is_empty(child_elem):
                elem.remove(child_elem)
            else:
                retval = [] 
                collect_flowpara_and_flowdivs(retval, cssutils.css.CSSStyleDeclaration(), child_elem)
                common_style = strip_common_style_properties(retval)
                flowdiv = etree.Element(u'{%s}flowDiv' % SVG_NAMESPACE)
                for _elem in retval:
                    flowdiv.append(_elem)
                set_or_remove_if_empty(flowdiv, u'style', css_text(common_style))
                child_elem.append(flowdiv)
                flowregion = child_elem.find(u'{%s}flowRegion' % SVG_NAMESPACE)
                if flowregion is not None:
                    handle_flowregion(flowregion)
                style_str = child_elem.get(u'style')
                if style_str is not None:
                    set_or_remove_if_empty(child_elem, u'style', css_text(parse_style(style_str, validate=False)))
        elif child_elem.tag == u'{%s}image' % SVG_NAMESPACE:
            elem.remove(child_elem)
        cleanup_elem(child_elem)

class IDStripper(object):
    def __init__(self, tags):
        self.tags = set(tags)
    
    def __call__(self, elem):
        attrib = elem.attrib
        if elem.tag in self.tags and u'id' in attrib:
            del attrib[u'id']
        for child_elem in elem:
            self(child_elem)

class PathTransformer(object):
    def __init__(self, handler, rotate, scale, translate):
        self.handler = handler
        self.rotate = rotate
        self.scale = scale
        self.translate = translate
        self.trans = self.rotate * self.translate * self.scale

    def close_path(self):
        return self.handler.close_path()

    def move_to(self, x, y):
        p = self.trans * numpy.matrix([x, y, 1.]).transpose()
        return self.handler.move_to(p[0, 0], p[1, 0])

    def line_to(self, x, y):
        p = self.trans * numpy.matrix([x, y, 1.]).transpose()
        return self.handler.line_to(p[0, 0], p[1, 0])

    def curve_to(self, x1, y1, x2, y2, x, y):
        p1 = self.trans * numpy.matrix([x1, y1, 1.]).transpose()
        p2 = self.trans * numpy.matrix([x2, y2, 1.]).transpose()
        p3 = self.trans * numpy.matrix([x,   y, 1.]).transpose()
        return self.handler.curve_to(p1[0, 0], p1[1, 0], p2[0, 0], p2[1, 0], p3[0, 0], p3[1, 0])

    def curve_to_qb(self, x1, y1, x, y):
        p1 = self.trans * numpy.matrix([x1, y1, 1.]).transpose()
        p2 = self.trans * numpy.matrix([x, y, 1.]).transpose()
        return self.handler.curve_to_qb(p1[0, 0], p1[1, 0], p2[0, 0], p2[1, 0])

    def arc(self, rx, ry, phi, largearc, sweep, x, y):
        p1 = self.scale * numpy.matrix([rx, ry, 1.]).transpose()
        p2 = self.trans * numpy.matrix([x, y]).transpose()
        phi_delta = numpy.arccos(self.rotate[0, 0])
        if numpy.arcsin(self.rotate[0, 1]) < 0:
            phi_delta = numpy.pi - phi_delta
        phi += phi_delta
        return self.handler.arc(p1[0, 0], p1[1, 0], phi, largearc, sweep, p2[0, 0], p2[1, 0])

ROTATE_180 = numpy.matrix([
    [-1.,  0., 0.],
    [ 0., -1., 0.],
    [ 0.,  0., 1.],
    ])

FLIP_Y = numpy.matrix([
    [1.,  0., 0.],
    [0., -1., 0.],
    [0.,  0., 1.],
    ])

class TransformApplier(object):
    def __init__(self):
        self.trans_stack = []
        self.trans = I
        self._rotate = I
        self._scale = I
        self._skew = I
        self._translate = I

    def push_transform(self, mat):
        self.trans_stack.append(self.trans)
        self.trans = self.trans * mat
        self._populate_rotate_scale_skew_translate()

    def pop_transform(self):
        self.trans = self.trans_stack.pop()
        self._populate_rotate_scale_skew_translate()

    def _populate_rotate_scale_skew_translate(self):
        _translate = self.trans[..., 2].copy()
        _rotate, m2 = numpy.linalg.qr(self.trans)

        if numpy.sign(_rotate[0, 1] * _rotate[1, 0]) > 0.:
            _rotate *= FLIP_Y
            m2 = FLIP_Y * m2
        if m2[0, 0] < 0. and m2[1, 1] < 0.:
            _rotate *= ROTATE_180
            m2 = ROTATE_180 * m2
        s1 = numpy.sign(m2[0, 0])
        s2 = numpy.sign(m2[1, 1])
        assert numpy.abs(s1) > 0 and numpy.abs(s2) > 0, repr(self.trans) + "\n" + repr(m2)
        self._rotate = _rotate
        self._scale = numpy.matrix([
            [ m2[0, 0] / s1,             0.,        0.],
            [             0., m2[1, 1] / s2,        0.],
            [             0.,            0.,        1.],
            ])
        self._skew = numpy.matrix([
            [       s1, m2[0, 1] / m2[1, 1] ,       0.],
            [       0.,                   s2,       0.],
            [       0.,                   0.,       1.],
            ])
        self._translate = numpy.matrix([
            [       1.,        0.,  m2[0, 2]],
            [       0.,        1.,  m2[1, 2]],
            [       0.,        0.,        1.]
            ])

    def __call__(self, elem):
        trans = I
        trans_str = elem.attrib.pop(u'transform', None)
        if trans_str is not None:
            trans = parse_transform(trans_str)
        self.push_transform(trans)

        if elem.tag == u'{%s}rect' % SVG_NAMESPACE:
            _rotate_and_skew = self._rotate * self._skew
            if numpy.allclose(_rotate_and_skew, I):
                _translate_and_scale = self._translate * self._scale
                p1 = numpy.matrix([float(elem.get(u'x')), float(elem.get(u'y')), 1.]).transpose()
                p2 = p1 + numpy.matrix([float(elem.get(u'width')), float(elem.get(u'height')), 0.]).transpose()
                p1 = _translate_and_scale * p1
                p2 = _translate_and_scale * p2
                elem.set(u'x', unicode(p1[0, 0]))
                elem.set(u'y', unicode(p1[1, 0]))
                elem.set(u'width', unicode(p2[0, 0] - p1[0, 0]))
                elem.set(u'height', unicode(p2[1, 0] - p1[1, 0]))
            else:
                elem.set(u'transform', to_matrix_string(self.trans))
        elif elem.tag == u'{%s}circle' % SVG_NAMESPACE:
            _scale = self._scale
            rm = _scale[1, 1]
            _deformation = numpy.matrix([
                [_scale[0, 0] / rm, 0., 0.],
                [               0., 1., 0.],
                [               0., 0., 1.],
                ])
            no_deformation = numpy.allclose(_deformation[0, 0], 1.)
            if numpy.allclose(self._skew, I) and (no_deformation or numpy.allclose(self._rotate, I)):
                r = float(elem.get(u'r')) * rm
                p1 = numpy.matrix([float(elem.get(u'cx')), float(elem.get(u'cy')), 1.]).transpose()
                p1 = self._rotate * self._translate * _scale * p1
                if no_deformation:
                    elem.set(u'cx', unicode(p1[0, 0]))
                    elem.set(u'cy', unicode(p1[1, 0]))
                    elem.set(u'r', unicode(r))
                else:
                    elem.tag = 'ellipse'
                    elem.set(u'cx', unicode(p1[0, 0]))
                    elem.set(u'cy', unicode(p1[1, 0]))
                    p2 = numpy.matrix([r, r, 1.]).transpose()
                    p2 = _deformation * p2
                    elem.set(u'rx', unicode(p2[0, 0]))
                    elem.set(u'ry', unicode(p2[1, 0]))
            else:
                elem.set(u'transform', to_matrix_string(self.trans))
        elif elem.tag == u'{%s}ellipse' % SVG_NAMESPACE:
            _rotate_and_skew = self._rotate * self._skew
            if numpy.allclose(_rotate_and_skew, I):
                _translate_and_scale = self._translate * self._scale
                p1 = numpy.matrix([float(elem.get(u'cx')), float(elem.get(u'cy')), 1.]).transpose()
                p1 = _translate_and_scale * p1
                p2 = numpy.matrix([float(elem.get(u'rx')), float(elem.get(u'ry')), 1.]).transpose()
                p2 = _translate_and_scale * p2
                elem.set(u'cx', unicode(p1[0, 0]))
                elem.set(u'cy', unicode(p1[1, 0]))
                elem.set(u'rx', unicode(p2[0, 0]))
                elem.set(u'ry', unicode(p2[1, 0]))
            else:
                elem.set(u'transform', to_matrix_string(self.trans))
        elif elem.tag == u'{%s}line' % SVG_NAMESPACE:
            p1 = numpy.matrix([float(elem.get(u'x1')), float(elem.get(u'y1')), 1.]).transpose()
            p2 = numpy.matrix([float(elem.get(u'x2')), float(elem.get(u'y2')), 1.]).transpose()
            p1 = self.trans * p1
            p2 = self.trans * p2
            elem.set(u'x1', unicode(p1[0, 0]))
            elem.set(u'y1', unicode(p1[1, 0]))
            elem.set(u'x2', unicode(p2[0, 0]))
            elem.set(u'y2', unicode(p2[1, 0]))
        elif elem.tag in (u'{%s}polyline' % SVG_NAMESPACE, u'{%s}polygon' % SVG_NAMESPACE):
            _points = list(parse_poly_data(elem.get(u'points')))
            points = numpy.ndarray(shape=(3, len(_points)), dtype=numpy.float64)
            for i, coord_pair in enumerate(_points):
                points[:,i] = coord_pair[0], coord_pair[1], 1.

            points = self.trans * points
            elem.set(u'points', u' '.join(u"%g,%g" % (x, y) for x, y, _ in points.transpose().getA()))
        elif elem.tag == u'{%s}path' % SVG_NAMESPACE:
            emitter = PathDataEmitter()
            handler = PathTransformer(emitter, self._rotate, self._scale, self._translate)
            PathDataScanner(tokenize_path_data(elem.get('d')), handler)()
            elem.set(u'd', emitter.get_result())
            if not numpy.allclose(self._skew, I):
                elem.set(u'transform', to_matrix_string(self._skew))
        elif elem.tag in (u'{%s}text' % SVG_NAMESPACE, u'{%s}tspan' % SVG_NAMESPACE):
            _rotate_scale_and_skew = self._rotate * self._scale * self._skew
            transform_needed = not numpy.allclose(_rotate_scale_and_skew, I)
            _translate = self._translate
            if transform_needed:
                inv = numpy.linalg.inv(_rotate_scale_and_skew)
                self.trans = _translate = inv * _translate * _rotate_scale_and_skew
                elem.set(u'transform', to_matrix_string(_rotate_scale_and_skew))
            p1 = _translate * numpy.matrix([float(elem.get(u'x')), float(elem.get(u'y')), 1.]).transpose()
            elem.set(u'x', unicode(p1[0, 0]))
            elem.set(u'y', unicode(p1[1, 0]))
        elif elem.tag == '{%s}flowRoot' % SVG_NAMESPACE:
            _rotate_scale_and_skew = self._rotate * self._scale * self._skew
            if not numpy.allclose(_rotate_scale_and_skew, I):
                elem.set(u'transform', to_matrix_string(_rotate_scale_and_skew))
                self.trans = numpy.linalg.inv(_rotate_scale_and_skew) * self._translate * _rotate_scale_and_skew

        for child_elem in elem:
            self(child_elem)

        self.pop_transform()

def cleanup_svg(svg):
    cleanup_elem(svg.getroot())
    IDStripper(u'{%s}%s' % (SVG_NAMESPACE, tag_name) for tag_name in [u'flowPara', u'flowDiv', u'flowSpan', u'flowRegion'])(svg.getroot())
    TransformApplier()(svg.getroot())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    import locale
    encoding = locale.getpreferredencoding()
    tree = etree.parse(sys.stdin)
    cleanup_svg(tree)
    sys.stdout.write(etree.tostring(tree, encoding=encoding))
