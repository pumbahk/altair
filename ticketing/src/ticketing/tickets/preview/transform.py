## svg transformation
import logging
logger = logging.getLogger(__name__)
import re
import ast
from wtforms import Form, fields, validators
from lxml import etree
from webob.multidict import MultiDict
from .materialize import svg_with_ticketformat
from ticketing.core.models import TicketFormat #uggg

class SVGTransformValidator(Form):
    sx = fields.FloatField(default=1.0)
    sy = fields.FloatField(default=1.0)
    ticket_format = fields.IntegerField()

    def validate_ticket_format(form, field):
        ticket_format = TicketFormat.query.filter_by(id=field.data).first()
        if ticket_format is None:
            logger.warn("validation failure")
            raise validators.ValidationError("Ticket Format is not found")
        field.data = form.data["ticket_format"] = ticket_format

        
def parse(postdata):
    if not hasattr(postdata, "getlist"):
        postdata = MultiDict(postdata)
    form = SVGTransformValidator(postdata)
    return form.data if form.validate() else None

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

class SVGTransformer(object):
    def __init__(self, svg, postdata=None, encoding="utf-8"):
        self.svg = svg
        self.data = parse(postdata or {})
        self.encoding = encoding

    def transform(self):
        if self.data is None:
            return self.svg
        xmltree = etree.fromstring(self.svg)
        return self.as_string(self.scale_image(self.put_pageformat(xmltree)))

    def put_pageformat(self, xmltree):
        svg = self._find_svg(xmltree)
        svg_with_ticketformat(svg, self.data["ticket_format"])
        return xmltree

    fullsvg = etree.QName("http://www.w3.org/2000/svg", "svg")
    def _find_svg(self, xmltree):
        if xmltree.tag == "svg" or xmltree.tag == self.fullsvg:
            return xmltree
        else:
            return xmltree.find("svg") or xmltree.find(self.fullsvg)
            
    def scale_image(self, xmltree):
        sx, sy = self.data["sx"], self.data["sy"]
        if sx == sy == 1:
            return xmltree

        svg = self._find_svg(xmltree)
        attrib = svg.attrib
        
        if "width" in attrib:
            attrib["width"] = transform_unit(lambda x : sx*x, attrib["width"])
        if "height" in attrib:
            attrib["height"] = transform_unit(lambda y : sy*y, attrib["height"])
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
