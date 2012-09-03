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

def collect_flowpara_and_flowdivs(retval, style, elem):
    for child_elem in elem:
        if child_elem.tag == u'{%s}flowDiv' % SVG_NAMESPACE:
            style_str = child_elem.get(u'style')
            if style_str is not None:
                _style = override_styles(style, cssutils.parseStyle(style_str, validate=False))
            else:
                _style = style
            collect_flowpara_and_flowdivs(retval, _style, child_elem)
            elem.remove(child_elem)
        elif child_elem.tag == u'{%s}flowPara' % SVG_NAMESPACE:
            style_str = child_elem.get(u'style')
            if style_str is not None:
                _style = override_styles(style, cssutils.parseStyle(style_str, validate=False))
            else:
                _style = style
            child_elem.set(u'style', re.sub(ur'\r\n|\r|\n', ' ', _style.cssText))
            retval.append(child_elem)
            elem.remove(child_elem)

def cleanup_elem(elem):
    for child_elem in elem:
        if child_elem.tag == u'{%s}flowRoot' % SVG_NAMESPACE:
            retval = [] 
            collect_flowpara_and_flowdivs(retval, cssutils.css.CSSStyleDeclaration(), child_elem)
            flowdiv = etree.Element(u'{%s}flowDiv' % SVG_NAMESPACE)
            for _elem in retval:
                flowdiv.append(_elem)
            child_elem.append(flowdiv)
        cleanup_elem(child_elem)

def cleanup_svg(svg):
    cleanup_elem(svg.getroot())

if __name__ == '__main__':
    import sys
    cleanup_svg(etree.parse(sys.stdin))    
