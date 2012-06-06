#!/usr/bin/env python -S
# -*- coding: utf-8 -*-
from converter import Converter, ConverterHandler, Element, Attributes, Metadata, Metadatas
import os
import sys
import io

# convert function
class MyConverterHandler(ConverterHandler):

    def __init__(self):

        self.viewBoxAdjustRatio = 80 # %

        self.size = map(float, ["infinity",  "infinity",
                                "-infinity", "-infinity"])

    def remove_p(self, elem, metadatas):
        attr = elem.getAttribute();
        return attr.get("class") == "seat"

    def accumulateViewBox(self, elem):
        attr = elem.getAttribute();

        if elem.getTagName() == "path":
            attrd = attr.get("d")
            if attrd != None:
                s = map(float, attrd.split(" ")[1:-1])
                for (x, y) in zip(s[0::2], s[1::2]):
                    if x < self.size[0]:
                        self.size[0] = x
                    if self.size[2] < x:
                        self.size[2] = x
                    if y < self.size[1]:
                        self.size[1] = y
                    if self.size[3] < y:
                        self.size[3] = y

        attrx = attr.get("x")
        attry = attr.get("y")
        attrw = attr.get("width")
        attrh = attr.get("height")

        if attrx == None or attry == None or attrw == None or attrh == None:
            return

        left = float(attrx)
        top = float(attry)
        right  = left + float(attrw)
        bottom = top  + float(attrh)

        if left < self.size[0]:
            self.size[0] = left
        if top  < self.size[1]:
            self.size[1] = top
        if self.size[2] < right:
            self.size[2] = right
        if self.size[3] < bottom:
            self.size[3] = bottom


    def onShapeElement(self, elem, metadatas):

        if self.remove_p(elem, metadatas):
            return None

        self.accumulateViewBox(elem)
        return elem

    def getViewBox(self, left, top, width, height):

        r = self.viewBoxAdjustRatio

        width  = self.size[2] - self.size[0]
        height = self.size[3] - self.size[1]

        width  = width  / (r / 100.0)
        height = height / (r / 100.0)
        xoffset = width  * (((100.0 - r) / 2.0) / 100.0)
        yoffset = height * (((100.0 - r) / 2.0) / 100.0)
        left = self.size[0] - xoffset
        top  = self.size[1] - yoffset

        return [left, top, width, height]


def main():
    argvs = sys.argv
    argc  = len(argvs)
    src   = None
    tgt   = None

    if (argc < 2):
        print 'Usage: $ python %s sourcefile.xml targetfile.tiny.xml' % argvs[0]
        quit(1)

    if (argc < 3):
        src = argvs[1]
        fn, fx = os.path.splitext(src)
        tgt = fn + '.tiny.xml'

    else:
        src = argvs[1]
        tgt = argvs[2]

    print 'SOURCE:%s TARGET:%s' % (src, tgt)

    converter = Converter(input=src, output=tgt, indent=2, handler=MyConverterHandler())
    converter.convert()

main()
