# -*- coding:utf-8 -*-

import unittest

class ConverterTest(unittest.TestCase):
    def assertConversionResult(self, input, expected, global_transform=None):
        from lxml import etree
        from .convert import convert_svg
        self.assertEqual(etree.tostring(convert_svg(etree.ElementTree(etree.fromstring(input)), global_transform), encoding='unicode'), expected)
        
    def test_flowRoot(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><flowRoot><flowRegion><rect x="0" y="0" width="100" height="100" /></flowRegion><flowDiv>test</flowDiv></flowRoot></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "test" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')

    def test_text(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">test</text></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "test" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')

    def test_placeholder(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">test\ufeff{{dummy}}\ufeff</text></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "test" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">\ufeff{{dummy}}\ufeff</text></svg>',
            expected=u'<TICKET><b>0.1 S</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">\ufeff{{発券日時}}\ufeff</text></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "FIXTAG04" xn sxn X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">\ufeff{{発券日時s}}\ufeff</text></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "FIXTAG04" xn sxn X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')

if __name__ == "__main__":
    unittest.main()

