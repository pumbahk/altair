# -*- coding:utf-8 -*-

import unittest
import logging

class DummyHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)

class ConverterTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        from .convert import logger
        self.dummy_handler = DummyHandler(logging.DEBUG)
        logger.addHandler(self.dummy_handler)

    def tearDown(self):
        from .convert import logger
        logger.removeHandler(self.dummy_handler)

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

        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">test<tspan>test</tspan></text></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "testtest" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')

        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100">test<tspan style="font-weight:bold">test</tspan></text></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "test&lt;span style=\\"font-weight:bold\\"&gt;test&lt;/span&gt;" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')

    def test_text_unsupported_font(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100" style="font-family:UNSUPPORTED-FONT-FAMILY">test<tspan style="font-weight:bold">test</tspan></text></svg>',
            expected=u'<TICKET><b>0.1 S :px U :f16 hc 0 0 m 1000 1000 "test&lt;span style=\\"font-weight:bold\\"&gt;test&lt;/span&gt;" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')
        self.assertEqual(len(self.dummy_handler.records), 2)
        self.assertEqual(self.dummy_handler.records[0].levelno, logging.WARNING)
        self.assertTrue(u'UNSUPPORTED-FONT-FAMILY' in self.dummy_handler.records[0].msg)

    def test_text_unsupported_font_weight(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100" style="font-family:MS PGothic;font-weight:UNSUPPORTED-FONT-WEIGHT">test<tspan style="font-weight:bold">test</tspan></text></svg>',
            expected=u'<TICKET><b>0.1 S :px U :f16 hc 0 0 m 1000 1000 "test&lt;span style=\\"font-weight:bold\\"&gt;test&lt;/span&gt;" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')
        self.assertEqual(len(self.dummy_handler.records), 1)
        self.assertEqual(self.dummy_handler.records[0].levelno, logging.WARNING)
        self.assertTrue(u'UNSUPPORTED-FONT-WEIGHT' in self.dummy_handler.records[0].msg)

    def test_text_unsupported_anchor(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="0" width="100" height="100" style="font-family:MS PGothic;font-weight:bold;text-anchor:UNSUPPORTED-ANCHOR-TYPE">test<tspan style="font-weight:bold">test</tspan></text></svg>',
            expected=u'<TICKET><b>0.1 S :px U :b hc :f16 hc 0 0 m 1000 1000 "testtest" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')
        self.assertEqual(len(self.dummy_handler.records), 1)
        self.assertEqual(self.dummy_handler.records[0].levelno, logging.WARNING)
        self.assertTrue(u'UNSUPPORTED-ANCHOR-TYPE' in self.dummy_handler.records[0].msg)

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

    def test_singleton(self):
        self.assertConversionResult(
            input=u'<svg xmlns="http://www.w3.org/2000/svg"><flowRoot><flowRegion><rect x="0" y="0" width="100" height="100" /></flowRegion><flowDiv style="text-anchor:middle"><flowSpan>test</flowSpan><flowSpan style="font-size:13px">test</flowSpan></flowDiv></flowRoot></svg>',
            expected=u'<TICKET><b>0.1 S :px U 0 0 m 1000 1000 "&lt;div style=\\"text-align:center\\"&gt;test&lt;span style=\\"font-size:13px;line-height:13px\\"&gt;test&lt;/span&gt;&lt;/div&gt;" X</b><FIXTAG01/><FIXTAG02/><FIXTAG03/><FIXTAG04/><FIXTAG05/><FIXTAG06/></TICKET>')


if __name__ == "__main__":
    unittest.main()

