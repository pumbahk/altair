import sys
import re
import cssutils
import logging
from lxml import etree
import numpy
from ..constants import *
from ..utils import parse_transform, tokenize_path_data, parse_poly_data, PathDataScanner, I

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

class TransformApplier(object):
    def __init__(self):
        self.trans_stack = []
        self.trans = I

    def push_transform(self, mat):
        self.trans_stack.append(self.trans)
        self.trans = self.trans * mat

    def pop_transform(self):
        self.trans = self.trans_stack.pop()

    def __call__(self, elem):
        trans = I
        trans_str = elem.attrib.pop(u'transform', None)
        if trans_str is not None:
            trans = parse_transform(trans_str)
        self.push_transform(trans)

        if elem.tag == u'{%s}rect' % SVG_NAMESPACE:
            p1 = numpy.matrix([float(elem.get(u'x')), float(elem.get(u'y')), 1.]).transpose()
            p2 = p1 + numpy.matrix([float(elem.get(u'width')), float(elem.get(u'height')), 0.]).transpose()
            p1 = self.trans * p1
            p2 = self.trans * p2
            elem.set(u'x', unicode(p1[0, 0]))
            elem.set(u'y', unicode(p1[1, 0]))
            elem.set(u'width', unicode(p2[0, 0] - p1[0, 0]))
            elem.set(u'height', unicode(p2[1, 0] - p1[1, 0]))
        elif elem.tag == u'{%s}circle' % SVG_NAMESPACE:
            p1 = numpy.matrix([float(elem.get(u'cx')), float(elem.get(u'cy')), 1.]).transpose()
            p1 = self.trans * p1
            elem.set(u'cx', unicode(p1[0, 0]))
            elem.set(u'cy', unicode(p1[1, 0]))
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
