# -*- coding:utf-8 -*-

import unittest
from wtforms.validators import ValidationError
from StringIO import StringIO

def get_dummy_io(string):
    return StringIO(string.encode("utf-8"))

class TemplateValidateTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.forms import get_validated_xmltree_as_opcode_source
        return get_validated_xmltree_as_opcode_source(*args, **kwargs)

    def test_simple_xml(self):
        target = get_dummy_io(u"""<a>h</a>""")
        self._callFUT(target)

    def test_not_xml(self):
        target = get_dummy_io(u"""h""")
        
        with self.assertRaises(ValidationError):
            self._callFUT(target)

        try:
            self._callFUT(target)
        except Exception as e:
            self.assertTrue( str(e).startswith("xml:"))

    template = u"""\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:ts="http://xmlns.ticketstar.jp/svg-extension"
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="627.16534"
   height="230.31496"
   version="1.2"
   id="svg2"
   inkscape:version="0.48.1 r9760"
   sodipodi:docname="sample-rt.svg">
  <ts:qrcode
     content="日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語日本語"
     x="104mm"
     y="30mm"
     width="24mm"
     height="24mm"
     fill="#000"
     stroke="none" />
%s
</svg>
    """

    def test_simple_valid_svg(self):
        target = get_dummy_io(self.template % u"""\
  <flowRoot
     transform="translate(462,100.60401)"
     id="flowRoot3177">
    <flowRegion
       id="flowRegion3179">
      <rect
         y="77.95668"
         x="78"
         height="14.5"
         width="73"
         id="rect3181" />
    </flowRegion>
    <flowDiv><flowPara>{{発券番号}}</flowPara></flowDiv>
  </flowRoot>
""")
        self._callFUT(target)

    def test_simple_invalid_svg(self):
        target = get_dummy_io(self.template % u"""\
  <flowRoot
     transform="translate(462,100.60401)"
     id="flowRoot3177">
<!-- this is typo of rect -->
    <flowRegion
       id="flowRegion3179">
      <nect
         y="77.95668"
         x="78"
         height="14.5"
         width="73"
         id="rect3181" />
    </flowRegion>
    <flowDiv><flowPara>{{発券番号}}</flowPara></flowDiv>
  </flowRoot>
""")
        with self.assertRaises(ValidationError):
            self._callFUT(target)

        try:
            self._callFUT(target)
        except Exception as e:
            self.assertTrue( str(e).startswith("opcode:"))

if __name__ == "__main__":
    unittest.main()
