# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import sys
from lxml import etree
from collections import namedtuple

Region = namedtuple("Region", "width height x y")
Content = namedtuple("Content", "text attrs")


class AttrsGetter(object):
    def attrs_from_style(self, style_string):
        D = {}
        for x in style_string.split(";"):
            k, v = x.split(":")
            D[k.strip()] = v.strip()
        return D

    def get_new_attrs(self, defaults, node):
        attrs = defaults.copy()
        if "style" in node.attrib:
            attrs.update(self.attrs_from_style(node.attrib["style"]))
        attrs.update(dict(node.attrib))
        return attrs


class SimpleControl(object):
    def __init__(self, attrgetter):
        self.attrgetter = AttrsGetter()

    def get_tag(self, n):
        tag = n.tag
        return tag[tag.rfind("}")+1:]

    def get_new_attrs(self, n):
        return self.attrgetter.get_new_attrs({}, n)

    def get_region_rect(self, rect):
        attrib = rect.attrib
        return Region(
            width=attrib.get("width"), 
            height=attrib.get("height"), 
            x=attrib.get("x"), 
            y=attrib.get("y"), 
        )

    def add_content_tspan(self, contents, region, default_attrs, tspan):
        attrs = self.attrgetter.get_new_attrs(default_attrs, tspan)
        if "x" in attrs or "y" in attrs:
            region = Region(
                x=attrs.get("x", region.x),
                y=attrs.get("y", region.y),
                width=attrs.get("width", region.width),
                height=attrs.get("height", region.height),
            )
        contents.append((region, Content(text=tspan.text, attrs=attrs)))
        for c in tspan.iterchildren():
            ctag = self.get_tag(c)
            if ctag == "tspan":
                self.add_content_tspan(contents, region, attrs, c)
            else:
                logger.info("%s is not supported, c")
        return contents

    def add_content_text(self, contents, region, default_attrs, text):
        attrs = self.attrgetter.get_new_attrs(default_attrs, text)
        if text.text:
            contents.append((region, Content(text=text.text, attrs=attrs)))
        for c in text.iterchildren():
            ctag = self.get_tag(c)
            if ctag == "tspan":
                self.add_content_tspan(contents, region, attrs, c)
            else:
                logger.info("%s is not supported, c")
        return contents

    def get_region_flowregion(self, flowregion):
        children = flowregion.getchildren()
        assert len(children) == 1
        c = children[0]

        ctag = self.get_tag(c)
        if ctag == "rect":
            return self.get_region_rect(c)
        else:
            raise NotImplementedError("only support `rect` element (flowRegion)")

    def add_content_flowpara(self, contents, region, default_attrs, flowpara):
        attrs = self.attrgetter.get_new_attrs(default_attrs, flowpara)

        text = flowpara.text
        if text is None:
            logger.info("flowPara %s is empty", flowpara)
        else:
            contents.append((region, Content(text=text, attrs=attrs)))
        return contents

    def add_content_flowdiv(self, contents, region, default_attrs, flowdiv):
        attrs = self.attrgetter.get_new_attrs(default_attrs, flowdiv)

        for c in flowdiv.iterchildren():
            ctag = self.get_tag(c)
            attrib = c.attrib
            if ctag == "flowPara":
                ## flatten?
                self.add_content_flowpara(contents, region, attrs, c)
            elif ctag == "flowRegion":
                region = self.get_region_flowregion(c)
            else:
                raise NotImplementedError("only support `flowRegion`, `flowPara` element (flowPara)")
        return contents


class ElementBuilder(object):
    def build_path(self, attrs, data):
        e = etree.Element("Path")
        e.attrib["Data"] = data
        if "fill" in attrs:
            e.attrib["Fill"] = attrs["fill"]
        if "fill-opacity" in attrs:
            e.attrib["Opacity"] = attrs["fill-opacity"]

        if "fill" in attrs:
            e.attrib["Fill"] = attrs["fill"]
        return e

    def build_fixed_text_block(self, region, attrs, content):
        e = etree.Element("TextBlock")
        return self._emit_text_block_attributes(e, region, attrs, content)

    def build_flowed_text_block(self, region, attrs, content):
        e = etree.Element("TextBlock")
        e.attrib["TextWrapping"] = "Wrap"
        e.attrib["Width"] = region.width
        e.attrib["Height"] = region.height
        return self._emit_text_block_attributes(e, region, attrs, content)

    def build_span_from_text(self, text):
        text.tag = "Span"
        attrib = text.attrib
        attrib.pop("Canvas.Left", None)
        attrib.pop("Canvas.Top", None)
        attrib.pop("Height", None)
        attrib.pop("Width", None)
        attrib.pop("TextWrapping", None)
        return text 

    def _emit_text_block_attributes(self, e, region, attrs, content):
        e.attrib["Canvas.Left"] = region.x
        e.attrib["Canvas.Top"] = region.y

        if "font-size" in attrs:
            e.attrib["FontSize"] = attrs["font-size"]
        if "font-family" in attrs:
            e.attrib["FontFamily"] = attrs["font-family"]
        if "fill" in attrs:
            e.attrib["Foreground"] = attrs["fill"]
        if "font-style" in attrs:
            fontstyle = attrs["font-style"]
            if fontstyle == "normal":
                e.attrib["FontStyle"] = "Normal"
            elif fontstyle == "italic":
                e.attrib["FontStyle"] = "Italic"
            elif fontstyle == "oblique":
                e.attrib["FontStyle"] = "Oblique"
            else:
                logger.warn("fontstyle=%s is not found", fontstyle)

        if "font-weight" in attrs:
            fontweight = attrs["font-weight"]
            if fontweight == "bold":
                e.attrib["FontWeight"] = "Bold"
            elif fontweight == "normal":
                e.attrib["FontWeight"] = "Normal"
            else:
                logger.warn("fontweight=%s is not found", fontweight)
        e.text = content.text
        return e

    def build_document(self):
        nsmap = {"x": "http://schemas.microsoft.com/winfx/2006/xaml", 
                 None: "http://schemas.microsoft.com/winfx/2006/xaml/presentation"}
        doc = etree.Element("FixedDocument", nsmap=nsmap)
        return doc

    def build_pagecontent(self):
        return etree.Element("PageContent")

    def build_page(self, width, height):
        page = etree.Element("FixedPage")
        page.attrib["Width"] = width
        page.attrib["Height"] =height
        return page

    def build_canvas(self):
        return etree.Element("Canvas")


class XAMLFromSVG(object):
    def __init__(self, 
                 control=SimpleControl(AttrsGetter()), 
                 element_builder=ElementBuilder()
    ):
        self.element_builder = element_builder
        self.control = control
        self.width = "0"
        self.height = "0"

    def convert(self, svg_tree):
        if hasattr(svg_tree, "getroot"):
            root = svg_tree.getroot() #lxml.etree._ElementTree
        else:
            root = svg_tree #lxml.etree.Element

        attrib = root.attrib
        self.width = attrib.get("width", "0")
        self.height = attrib.get("height", "0")

        doc = self.element_builder.build_document()
        content = self.element_builder.build_pagecontent()
        page = self.element_builder.build_page(self.width, self.height)

        doc.append(content)
        content.append(page)

        self.convert_from_root(page, root)
        return doc

    def convert_from_root(self, this, root):
        for c in root.iterchildren():
            self.dispatch(this, c)
        return this

    def dispatch(self, this, n):
        m = getattr(self, "visit_{}".format(self.control.get_tag(n)), None)
        if m:
            return m(this, n)
        else:
            logger.warn("tag %s is not supported.", n.tag)
            raise NotImplementedError("dispatch for {} is not found".format(n.tag))

    def visit_defs(self, this, n):
        pass

    def visit_metadata(self, this, n):
        pass

    def visit_namedview(self, this, n):
        pass

    def visit_g(self, this, n):
        e = self.element_builder.build_canvas()
        # e.attrib["Height"] = self.height
        this.append(e)

        for c in n.iterchildren():
            self.dispatch(e, c)

    def visit_text(self, this, n):
        region = self.control.get_region_rect(n)

        contents = [] #((region, content), ....)
        default_attrs = self.control.get_new_attrs(n)
        self.control.add_content_text(contents, region, default_attrs, n)
        prev_element = None
        prev_region = None

        for region, content in contents:
            region = region
            attrs = content.attrs or default_attrs
            e = self.element_builder.build_fixed_text_block(region, attrs, content)
            if prev_region and prev_region.x == region.x and prev_region.y == region.y:
                prev_element.append(self.element_builder.build_span_from_text(e))
            else:
                this.append(e)
                prev_element = e
                prev_region = region

    def visit_rect(self, this, n):
        pass

    def visit_path(self, this, n):
        parent = n.getparent()
        attrib = parent.attrib
        X = float(attrib.get("x", "0"))
        Y = float(attrib.get("y", "0"))
        attrs = self.control.get_new_attrs(n)
        ##相対座標を取る必要がある(c=relative, C=absolute)
        e = self.element_builder.build_path(attrs, n.attrib["d"])
        this.append(e)

    def visit_flowRoot(self, this, n):
        default_region = None # default region
        contents = [] #((region, content), ....)
        default_attrs = self.control.get_new_attrs(n)

        for c in n.iterchildren():
            tag = self.control.get_tag(c)
            if tag == "flowRegion":
                default_region = self.control.get_region_flowregion(c)
            elif tag == "flowDiv":
                self.control.add_content_flowdiv(contents, default_region, default_attrs, c)
            elif tag == "flowPara":
                self.control.add_content_flowpara(contents, default_region, default_attrs, c)

        prev_element = None
        prev_region = None

        for region, content in contents:
            region = region or default_region
            attrs = content.attrs or default_attrs
            e = self.element_builder.build_flowed_text_block(region, attrs, content)
            if prev_region and prev_region.x == region.x and prev_region.y == region.y:
                linebreak = etree.SubElement(prev_element, "LineBreak")
                #linebreak.tail = e.text
                prev_element.append(self.element_builder.build_span_from_text(e))
            else:
                this.append(e)
                prev_element = e
                prev_region = region


"""
svg
	defs, g
g
	[rect,flowRoot,path]
flowRoot
	[flowRegion,flowDiv,flowPara]
flowRegion
	rect
flowDiv
	flowPara

---------
Path.d
M=absolute, m=relative
"""

def xaml_from_svg(svg, pretty_print=False):
    svg_tree = etree.fromstring(svg)
    xaml_tree = XAMLFromSVG().convert(svg_tree)
    return etree.tostring(xaml_tree, encoding="utf-8", pretty_print=pretty_print)

if __name__ == "__main__":
    if len(sys.argv) <=1:
        print("""svg_to_xaml.py <svg file>""")
    else:
        filename = sys.argv[1]
        t = etree.parse(filename)
        print(etree.tostring(XAMLFromSVG().convert(t), encoding="utf-8", pretty_print=True))
