# -*- coding:utf-8 -*-

import unittest

class QRCodeInsertTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.api import QRCodeEmitter
        return QRCodeEmitter(*args, **kwargs).emit()

    svg = u"""
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="744.09448819"
   height="1052.3622047"
   id="svg2"
   version="1.1"
   inkscape:version="0.48.3.1 r9886"
>
  <defs
     id="defs4" />
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1">
    <rect
       id="QR"
       width="474.28571"
       height="334.28571"
       x="148.57143"
       y="198.07646"
       inkscape:label="ここにQRの文字列" />
  </g>
</svg>
""".encode("utf-8")

    def test_it(self):
        from lxml import etree
        tree = etree.fromstring(self.svg)
        result = self._callFUT(tree)
        output = etree.tostring(result, encoding="utf-8")

        self.assertIn("qrcode", output)
        self.assertIn("content=", output)
        self.assertIn("eclevel=", output)
       # <ts:qrcode xmlns:ts="http://xmlns.ticketstar.jp/svg-extension" width="100" height="100" x="10" y="10" eclevel="h|l|m|q">This is a test</ts:qrcode>

    def test_not_qr_rect(self):
        from lxml import etree
        from altair.app.ticketing.tickets.constants import SVG_NAMESPACE

        tree = etree.fromstring(self.svg)
        for x in tree.xpath("//n:rect", namespaces={"n": SVG_NAMESPACE}):
            x.attrib["id"] = "xxxx"

        result = self._callFUT(tree)
        output = etree.tostring(result, encoding="utf-8")

        self.assertNotIn("qrcode", output)
        self.assertNotIn("content=", output)
        self.assertNotIn("eclevel=", output)

    def test_style_is_deleted(self):
        from lxml import etree
        from altair.app.ticketing.tickets.constants import SVG_NAMESPACE

        tree = etree.fromstring(self.svg)
        for x in tree.xpath("//n:rect", namespaces={"n": SVG_NAMESPACE}):
            x.attrib["style"] = "fill:#0000ff;fill-rule:evenodd;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"

        result = self._callFUT(tree)
        output = etree.tostring(result, encoding="utf-8")

        self.assertNotIn("style", output)


        

if __name__ == "__main__":
    unittest.main()
