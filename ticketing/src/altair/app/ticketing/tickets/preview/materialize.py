# -*- coding:utf-8 -*-
from lxml import etree
from altair.svg.constants import SVG_NAMESPACE
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
        e = etree.Element("{%s}line" % SVG_NAMESPACE)
        e.attrib["x1"] = unicode(0)
        e.attrib["x2"] = unicode(self.width)
        e.attrib["y1"] = unicode(y)
        e.attrib["y2"] = unicode(y)
        if kwargs:
            for k, v in kwargs.iteritems():
                e.attrib[k] = unicode(v)
        return e

    def vline(self, x, kwargs=None):
        e = etree.Element("{%s}line" % SVG_NAMESPACE)
        e.attrib["y1"] = unicode(0)
        e.attrib["y2"] = unicode(self.height)
        e.attrib["x1"] = unicode(x)
        e.attrib["x2"] = unicode(x)
        if kwargs:
            for k, v in kwargs.iteritems():
                e.attrib[k] = unicode(v)
        return e

    def rect(self, x, y, w, h, kwargs=None):
        e = etree.Element("{%s}rect" % SVG_NAMESPACE)
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
        option = {"stroke-dasharray":"1.5mm,1.5mm", "stroke": "#cccccc", "stroke-opacity": "1", "stroke-width": "1"}
        for y in data.get("horizontal"):
            svg.append(self.low.hline(y, option))
        for x in data.get("vertical", data):
            svg.append(self.low.vline(x, option))

    def add_printable_areas(self, svg, data):
        option = {"fill": "#ffffcc", "fill-opacity": "1",  "stroke": "#cccc88", "stroke-opacity": "1", "stroke-width": "1"}
        for area in data:
            svg.append(self.low.rect(area["x"], area["y"], area["width"], area["height"], option))

def create_svg(svg):
    svg = svg or etree.Element("{%s}svg" % SVG_NAMESPACE)
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

    def materialize(self, svg):
        data = self.pageformat.data
        self.middle.add_printable_areas(svg, data["printable_areas"])
        self.middle.add_perforations(svg, data["perforations"])
        ## todo: ticket_margin
        return svg

def svg_with_ticketformat(svg, ticketformat, hide_background):
    g = etree.Element("{%s}g" % SVG_NAMESPACE)
    if not hide_background:
        etree.tostring(TicketFormatMaterializer(ticketformat).materialize(g))
    svg.insert(0, g)
    ## width, heightの調整が必要?
    return svg

if __name__ == "__main__":
    import sys
    from pyramid.paster import bootstrap
    bootstrap(sys.argv[1])

    from altair.app.ticketing.core.models import TicketFormat
    from altair.app.ticketing.tickets.preview.materialize import TicketFormatMaterializer
    tf = TicketFormat.query.first()
    m = TicketFormatMaterializer(tf)
    print etree.tostring(m.materialize(create_svg()))
