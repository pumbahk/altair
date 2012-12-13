import unittest


class TransformTests(unittest.TestCase):
    def _getTarget(self):
        from ticketing.tickets.preview.transform import SVGTransformer
        return SVGTransformer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    svg = """\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="5cm" height="3cm" viewBox="0 0 5 3" version="1.1">
  <rect x=".01" y=".01" width="4.98" height="2.98" 
        fill="none" stroke="blue"  stroke-width=".03"/>
    <ellipse cx="2.5" cy="1.5" rx="2" ry="1" fill="red" />
</svg>
"""
    def test_it(self):
        from lxml import etree

        target = self._makeOne(self.svg, {"sx": "2.0", "sy": "3"})
        result = etree.tostring(target.scale_image(etree.fromstring(target.svg)))
        
        self.assertIn('width="10.0cm"', result)
        self.assertIn('height="9.0cm"', result)
        self.assertIn('viewBox="0 0 10.0 9.0"', result)
        self.assertIn('<g transform="scale(2.0, 3.0)"', result)

    def test_with_comment(self):
        from lxml import etree

        svg = u"<!-- Created with Inkscape (http://www.inkscape.org/) -->"+self.svg
        target = self._makeOne(self.svg, {"sx": "2.0", "sy": "3"})
        result = etree.tostring(target.scale_image(etree.fromstring(target.svg)))
       
        self.assertIn('width="10.0cm"', result)
        self.assertIn('height="9.0cm"', result)
        self.assertIn('viewBox="0 0 10.0 9.0"', result)
        self.assertIn('<g transform="scale(2.0, 3.0)"', result)

    def test_identity(self):
        from lxml import etree

        target = self._makeOne(self.svg)
        result = etree.tostring(target.scale_image(etree.fromstring(target.svg)))
        
        self.assertIn('width="5cm"', result)
        self.assertIn('height="3cm"', result)
        self.assertIn('viewBox="0 0 5 3"', result)
        self.assertNotIn('<g transform="scale(1.0, 1.0)"', result)

    ## find svg
    def test_find_svg_nons(self):
        from lxml import etree
        xml = "<svg/>"
        result = self._makeOne(None)._find_svg(etree.fromstring(xml))
        self.assertIn("svg", result.tag)

    def test_find_svg_ns(self):
        from lxml import etree
        xml = """<!-- Created with Inkscape (http://www.inkscape.org/) --><svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">aaa</svg>"""
        result = self._makeOne(None)._find_svg(etree.fromstring(xml))
        self.assertIn("svg", result.tag)

    def test_find_svg_ns_childelement(self):
        from lxml import etree
        xml = """<xml><!-- Created with Inkscape (http://www.inkscape.org/) --><svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg">aaa</svg></xml>"""
        result = self._makeOne(None)._find_svg(etree.fromstring(xml))
        self.assertIn("svg", result.tag)

if __name__ == "__main__":
    unittest.main()
