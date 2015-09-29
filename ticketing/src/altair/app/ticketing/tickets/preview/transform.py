# -*- coding:utf-8 -*-

## svg transformation
import logging
logger = logging.getLogger(__name__)
import re
import ast
from lxml import etree
from altair.app.ticketing.tickets.utils import build_dict_from_product_item
from altair.app.ticketing.tickets.preview.materialize import svg_with_ticketformat
from altair.app.ticketing.tickets.preview.fillvalues import template_fillvalues
from altair.app.ticketing.tickets.preview.validators import parse, SVGTransformValidator, FillValuesFromModelsValidator

from altair.app.ticketing.tickets.preview.fillvalues import TicketPreviewFillValuesException
from . import TicketPreviewTransformException
from altair.svg.constants import SVG_NAMESPACE
from altair.svg.geometry import as_user_unit

def wrap_element(parent, tag, attrs):
    """
    >>> from lxml import etree
    >>> xmltree = etree.fromstring("<a><x>yyy</x><y></y></a>")
    >>> etree.tostring(wrap_element(xmltree, "b", {}))
    '<a><b><x>yyy</x><y/></b></a>'
    """
    e = etree.Element(tag)
    for k, v in attrs.iteritems():
        e.attrib[k] = v
    for child in parent:
        e.append(child)
    parent.append(e)
    return parent

num_rx = re.compile("([+-]?(?:\d+|\d+\.\d+))([a-z%]*)$")   
def transform_unit(fn, unit):
    """
    >>> transform_unit(lambda x:x*2,"20cm")
    '40cm'
    >>> transform_unit(lambda x:x*2,"-20.012cm")
    '-40.024cm'
    """
    def _num_repl(m):
        return str(fn(ast.literal_eval(m.group(1))))+m.group(2)
    return num_rx.sub(_num_repl, unit, 1)

def _find_svg(xmltree):
    if xmltree.tag == "{%s}svg" % SVG_NAMESPACE:
        return xmltree
    else:
        return xmltree.find("{%s}svg" % SVG_NAMESPACE)

class SVGTransformer(object):
    def __init__(self, svg, postdata=None, hide_background=None, encoding="utf-8"):
        self.svg = svg
        self.data = parse(SVGTransformValidator, postdata or {})
        self.hide_background = hide_background
        self.encoding = encoding
        self.width = None #ugg
        self.height = None

    def transform(self):
        try:
            if self.data is None:
                return self.svg
            xmltree = etree.fromstring(self.svg)
            return self.as_string(self.scale_image(self.put_pageformat(self.translate_image(xmltree))))
        except Exception, e:
            logger.exception(e)
            raise TicketPreviewTransformException(u"svgの変換に失敗しました。%s" % str(e))

    def translate_image(self, xmltree):
        svg = _find_svg(xmltree)
        ticket_format = self.data["ticket_format"]
        po = ticket_format.data.get("print_offset")
        if po:
            attrs = {"transform": "translate(%s, %s)" % (as_user_unit(po.get('x', '0')), as_user_unit(po.get('y', '0')))}
            wrap_element(svg, "{%s}g" % SVG_NAMESPACE, attrs)
        return xmltree

    def put_pageformat(self, xmltree):
        svg = _find_svg(xmltree)
        svg_with_ticketformat(svg, self.data["ticket_format"], self.hide_background)
        return xmltree

    def detect_size(self, attrib):
        if "width" in attrib:
            self.width = attrib["width"] ## this is base_width. (sx = 1.0 )
        if "height" in attrib:
            self.height = attrib["height"]
            
    def scale_image(self, xmltree):
        sx, sy = self.data["sx"], self.data["sy"]
        svg = _find_svg(xmltree)
        attrib = svg.attrib

        self.detect_size(attrib)

        if sx == sy == 1:
            return xmltree

        if "width" in attrib:
            attrib["width"] = transform_unit(lambda x : sx*x, self.width)
        if "height" in attrib:
            attrib["height"] = transform_unit(lambda y : sy*y, self.height)
        if "viewBox" in attrib:
            box_val = attrib["viewBox"].split(" ")
            box_val[2] = str(sx * ast.literal_eval(box_val[2]))
            box_val[3] = str(sy * ast.literal_eval(box_val[3]))
            attrib["viewBox"] = " ".join(box_val)

        attrs = {"transform": "scale(%s, %s)" % (self.data["sx"], self.data["sy"])}
        wrap_element(svg, "{%s}g" % SVG_NAMESPACE, attrs)
        return xmltree

    def as_string(self, xmltree):
        return etree.tostring(xmltree, encoding=self.encoding)

class FillvaluesTransformer(object):
    def __init__(self, svg, postdata=None, encoding="utf-8"):
        self.svg = svg
        self.data = parse(FillValuesFromModelsValidator, postdata or {})
        self.encoding = encoding

    def params_from_model(self):
        model_name = self.data["model_name"]
        if model_name == "ProductItem":
            return build_dict_from_product_item(self.data["model"])
        else:
            return None

    def transform(self):
        try:
            if self.data is None:
                return self.svg

            params = self.params_from_model()
            return template_fillvalues(self.svg, params)
        except TicketPreviewFillValuesException, e:
            raise TicketPreviewTransformException(e.message)
        except Exception, e:
            logger.exception(e)
            raise TicketPreviewTransformException(u"Templateへの埋込みに失敗しました。%s" % str(e))


from altair.app.ticketing.tickets.cleaner import cleanup_svg
from altair.app.ticketing.tickets.convert import convert_svg

class SEJTemplateTransformer(object):
    def __init__(self, svgio=None, global_transform=None, notation_version=1, encoding="Shift_JIS"):
        self.svgio = svgio
        self.global_transform = global_transform
        self.notation_version = notation_version
        self.encoding = encoding

        self.height = None #uggg
        self.width = None

    def _detect_size(self, xmltree):
        svg = _find_svg(xmltree)
        attrib = svg.attrib
        
        if "width" in attrib:
            self.width = attrib["width"]
        if "height" in attrib:
            self.height = attrib["height"]

    def transform(self): #todo: parse_transform
        try:
            xmltree = etree.parse(self.svgio)
            self._detect_size(xmltree.getroot())

            cleanup_svg(xmltree)
            converted = convert_svg(xmltree, global_transform=self.global_transform, notation_version=self.notation_version)

            pat = r'''encoding=(["'])Windows-31J\1'''
            rep = 'encoding="%s"'% self.encoding
            return re.sub(pat, rep, etree.tostring(converted, encoding='Windows-31J'))
        except Exception, e:
            logger.exception(e)
            raise TicketPreviewTransformException(u"SEJのリクエストへの変換に失敗しました。%s" % str(e))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
