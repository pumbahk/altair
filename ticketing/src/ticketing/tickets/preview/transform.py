## svg transformation
import logging
logger = logging.getLogger(__name__)
import re
import ast
from lxml import etree
from ticketing.tickets.utils import build_dict_from_product_item
from ticketing.tickets.preview.materialize import svg_with_ticketformat
from ticketing.tickets.preview.fillvalues import template_fillvalues
from ticketing.tickets.preview.validators import parse, SVGTransformValidator, FillValuesFromModelsValidator

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

fullsvg = etree.QName("http://www.w3.org/2000/svg", "svg")
def _find_svg(xmltree):
    if xmltree.tag == "svg" or xmltree.tag == fullsvg:
        return xmltree
    else:
        return xmltree.find("svg") or xmltree.find(fullsvg)

class SVGTransformer(object):
    def __init__(self, svg, postdata=None, encoding="utf-8"):
        self.svg = svg
        self.data = parse(SVGTransformValidator, postdata or {})
        self.encoding = encoding
        self.width = None #ugg
        self.height = None

    def transform(self):
        if self.data is None:
            return self.svg
        xmltree = etree.fromstring(self.svg)
        return self.as_string(self.scale_image(self.put_pageformat(xmltree)))

    def put_pageformat(self, xmltree):
        svg = _find_svg(xmltree)
        svg_with_ticketformat(svg, self.data["ticket_format"])
        return xmltree
        
    def scale_image(self, xmltree):
        sx, sy = self.data["sx"], self.data["sy"]
        if sx == sy == 1:
            return xmltree

        svg = _find_svg(xmltree)
        attrib = svg.attrib
        
        if "width" in attrib:
            self.width = attrib["width"]
            attrib["width"] = transform_unit(lambda x : sx*x, self.width)
        if "height" in attrib:
            self.height = attrib["height"]
            attrib["height"] = transform_unit(lambda y : sy*y, self.height)
        if "viewBox" in attrib:
            box_val = attrib["viewBox"].split(" ")
            box_val[2] = str(sx * ast.literal_eval(box_val[2]))
            box_val[3] = str(sy * ast.literal_eval(box_val[3]))
            attrib["viewBox"] = " ".join(box_val)
        attrs = {"transform": "scale(%s, %s)" % (self.data["sx"], self.data["sy"])}
        wrap_element(svg, "g", attrs)
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
        if self.data is None:
            return self.svg

        params = self.params_from_model()
        return template_fillvalues(self.svg, params)


from ticketing.tickets.cleaner import cleanup_svg
from ticketing.tickets.convert import convert_svg
from ticketing.tickets.utils import parse_transform

class SEJTemplateTransformer(object):
    def __init__(self, svg=None, svgio=None, encoding="Shift_JIS"):
        self.svg = svg
        self.svgio = svgio
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
        if self.svg:
            xmltree = etree.fromstring(self.svg) #xxx:
        elif self.svgio:
            xmltree = etree.parse(self.svgio)

        self._detect_size(xmltree.getroot())

        cleanup_svg(xmltree)
        global_transform = None #parse_transform(sys.argv[1]
        converted = convert_svg(xmltree, global_transform)

        pat = r'''encoding=(["'])Windows-31J\1'''
        rep = 'encoding="%s"'% self.encoding
        return re.sub(pat, rep, etree.tostring(converted, encoding='Windows-31J'))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
