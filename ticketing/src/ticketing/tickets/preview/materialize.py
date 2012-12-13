# -*- coding:utf-8 -*-
from lxml import etree
"""
本当は中間状態持っていて後でrenderingする形の方が良い。
scaleとかtransformとかできる。
"""
## low
class Low(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def hline(self, y, kwargs=None):
        e = etree.Element("line")
        e.attrib["x1"] = unicode(0)
        e.attrib["x2"] = unicode(self.width)
        e.attrib["y1"] = unicode(y)
        e.attrib["y2"] = unicode(y)
        if kwargs:
            for k, v in kwargs.iteritems():
                e.attrib[k] = unicode(v)
        return e

    def vline(self, x, kwargs=None):
        e = etree.Element("line")
        e.attrib["y1"] = unicode(0)
        e.attrib["y2"] = unicode(self.height)
        e.attrib["x1"] = unicode(x)
        e.attrib["x2"] = unicode(x)
        if kwargs:
            for k, v in kwargs.iteritems():
                e.attrib[k] = unicode(v)
        return e

    def rect(self, x, y, w, h, kwargs=None):
        e = etree.Element("rect")
        e.attrib["x"] = unicode(x)
        e.attrib["y"] = unicode(y)
        e.attrib["width"] = unicode(w)
        e.attrib["height"] = unicode(h)
        if kwargs:
            for k, v in kwargs.iteritems():
                e.attrib[k] = unicode(v)
        return e

## middle
class Middle(object):
    LowClass = Low
    def __init__(self, width, height):
        self.low = self.LowClass(width, height)

    def add_perforations(self, svg, data):
        option = {"stroke-dasharray":"1.5mm,1.5mm", "stroke": "red"}
        for y in data.get("horizontal"):
            svg.append(self.low.hline(y, option))
        for x in data.get("vertical", data):
            svg.append(self.low.vline(x, option))

    def add_printable_areas(self, svg, data):
        option = {"fill": "green"}
        for area in data:
            svg.append(self.low.rect(area["x"], area["y"], area["width"], area["height"], option))

def create_svg(svg):
    svg = svg or etree.Element("svg")
    if not "version" in svg.attrib:
        svg.attrib["version"] = u"1.2"
    return svg

## high
class TicketFormatMaterializer(object):
    def __init__(self, pageformat):
        self.pageformat = pageformat
        size = pageformat.data["size"]
        self.width = size["width"]
        self.height = size["height"]
        self.middle = Middle(self.width, self.height)

    def materialize(self, svg=None):
        svg = create_svg(svg)
        data = self.pageformat.data
        self.middle.add_printable_areas(svg, data["printable_areas"])
        self.middle.add_perforations(svg, data["perforations"])
        return svg

if __name__ == "__main__":
    import sys
    from pyramid.paster import bootstrap
    bootstrap(sys.argv[1])

    from ticketing.core.models import TicketFormat
    from ticketing.tickets.preview.materialize import TicketFormatMaterializer
    tf = TicketFormat.query.first()
    m = TicketFormatMaterializer(tf)
    print etree.tostring(m.materialize())
