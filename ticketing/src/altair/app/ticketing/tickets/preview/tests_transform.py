# -*- coding:utf-8 -*-
import unittest


class TransformTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.tickets.preview.transform import SVGTransformer
        return SVGTransformer
    
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    svg = """\
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<ns0:svg xmlns:ns0="http://www.w3.org/2000/svg" width="5cm" height="3cm" viewBox="0 0 5 3" version="1.1">
  <ns0:rect x=".01" y=".01" width="4.98" height="2.98" 
        fill="none" stroke="blue"  stroke-width=".03"/>
    <ellipse cx="2.5" cy="1.5" rx="2" ry="1" fill="red" />
</ns0:svg>
"""
    def test_it(self):
        from lxml import etree

        target = self._makeOne(self.svg, {"sx": "2.0", "sy": "3"})
        result = etree.tostring(target.scale_image(etree.fromstring(target.svg)))
        
        self.assertIn('width="10.0cm"', result)
        self.assertIn('height="9.0cm"', result)
        self.assertIn('viewBox="0 0 10.0 9.0"', result)
        self.assertIn('<ns0:g transform="scale(2.0, 3.0)"', result)

    def test_with_comment(self):
        from lxml import etree

        svg = u"<!-- Created with Inkscape (http://www.inkscape.org/) -->"+self.svg
        target = self._makeOne(svg, {"sx": "2.0", "sy": "3"})
        result = etree.tostring(target.scale_image(etree.fromstring(target.svg)))
       
        self.assertIn('width="10.0cm"', result)
        self.assertIn('height="9.0cm"', result)
        self.assertIn('viewBox="0 0 10.0 9.0"', result)
        self.assertIn('<ns0:g transform="scale(2.0, 3.0)"', result)

    def test_identity(self):
        from lxml import etree

        target = self._makeOne(self.svg)
        result = etree.tostring(target.scale_image(etree.fromstring(target.svg)))
        
        self.assertIn('width="5cm"', result)
        self.assertIn('height="3cm"', result)
        self.assertIn('viewBox="0 0 5 3"', result)
        self.assertNotIn('<ns0:g transform="scale(1.0, 1.0)"', result)

    ## find width
    def test_detect_size(self):
        svg = u"""\
<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.w3.org/2000/svg" sodipodi:docname="あnew-89ers-kp3000c.svg" inkscape:label="Layer" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:svg="http://www.w3.org/2000/svg" height="230.31496" width="628.93701" version="1.2" xmlns:cc="http://creativecommons.org/ns#" xmlns:xlink="http://www.w3.org/1999/xlink" inkscape:version="0.48.2 r9819" id="svg2" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <metadata id="metadata58">
    <rdf:RDF>
      <cc:Work rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"></dc:type>
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
</svg>
"""
        from altair.app.ticketing.tickets.preview.transform import _find_svg

        from lxml import etree
        target = self._makeOne(None,  {})
        target.detect_size(_find_svg(etree.fromstring(svg)).attrib)

        self.assertEqual(target.width, "628.93701")
        self.assertEqual(target.height, "230.31496")

class FindSVGTests(unittest.TestCase):
    def _callFUT(self,  *args, **kwargs):
        from altair.app.ticketing.tickets.preview.transform import _find_svg
        return _find_svg(*args, **kwargs)

    ## find svg
    def test_find_svg_nons(self):
        from lxml import etree
        xml = "<svg/>"
        result = self._callFUT(etree.fromstring(xml))
        self.assertIsNone(result)

    def test_find_svg_ns(self):
        from lxml import etree
        xml = """<!-- Created with Inkscape (http://www.inkscape.org/) --><svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">aaa</svg>"""
        result = self._callFUT(etree.fromstring(xml))
        self.assertIn("svg", result.tag)

    def test_find_svg_ns_childelement(self):
        from lxml import etree
        xml = """<xml><!-- Created with Inkscape (http://www.inkscape.org/) --><svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">aaa</svg></xml>"""
        result = self._callFUT(etree.fromstring(xml))
        self.assertIn("svg", result.tag)


if __name__ == "__main__":
    from altair.app.ticketing.testing import _setup_db
    _setup_db(modules=[
            "altair.app.ticketing.models",
            "altair.app.ticketing.core.models",
            ])
    unittest.main()
