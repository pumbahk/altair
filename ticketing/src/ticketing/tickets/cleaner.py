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
    # this is uncovered by SVG spec, but added by Inkscape...
    decl.removeProperty(u'text-align')
    return decl

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
            child_elem.set(u'style', re.sub(ur'\r\n|\r|\n', ' ', _style.cssText))
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
    attach_fill_and_stroke_none_if_not_specified(first_child)

def cleanup_elem(elem):
    for child_elem in elem:
        if child_elem.tag == u'{%s}flowRoot' % SVG_NAMESPACE:
            retval = [] 
            collect_flowpara_and_flowdivs(retval, cssutils.css.CSSStyleDeclaration(), child_elem)
            flowdiv = etree.Element(u'{%s}flowDiv' % SVG_NAMESPACE)
            for _elem in retval:
                flowdiv.append(_elem)
            child_elem.append(flowdiv)
            flowregion = child_elem.find(u'{%s}flowRegion' % SVG_NAMESPACE)
            if flowregion is not None:
                handle_flowregion(flowregion)
        cleanup_elem(child_elem)

def cleanup_svg(svg):
    cleanup_elem(svg.getroot())

if __name__ == '__main__':
    import sys
    cleanup_svg(etree.parse(sys.stdin))    
