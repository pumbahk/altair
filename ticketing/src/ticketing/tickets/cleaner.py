import sys
import re
import cssutils
import logging
from lxml import etree
from ticketing.tickets.constants import *

__all__ = (
    'cleanup_svg',
    )

logging.basicConfig(level=logging.INFO)
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

def cleanup_elem(elem):
    for child_elem in list(elem):
        if child_elem.tag == u'{%s}flowRoot' % SVG_NAMESPACE:
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

def cleanup_svg(svg):
    cleanup_elem(svg.getroot())
    IDStripper(u'{%s}%s' % (SVG_NAMESPACE, tag_name) for tag_name in [u'flowPara', u'flowDiv', u'flowSpan', u'flowRegion'])(svg.getroot())

if __name__ == '__main__':
    import sys
    import locale
    encoding = locale.getpreferredencoding()
    tree = etree.parse(sys.stdin)
    cleanup_svg(tree)
    sys.stdout.write(etree.tostring(tree, encoding=encoding))
