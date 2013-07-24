# -*- coding:utf-8 -*-
import unittest

class FormTests(unittest.TestCase):
    def _getTargetClass(self):
        from altair.app.ticketing.tickets.forms import TicketTemplateForm
        return TicketTemplateForm

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def _getPostData(self, **kwargs):
        from webob.multidict import MultiDict        
        return MultiDict(**kwargs)

    def test_cleanup_has_effect(self):
        from StringIO import StringIO
        from lxml.etree import fromstring
        from .constants import SVG_NAMESPACE

        svg = u"""\
<?xml version="1.0" encoding="UTF-8" ?>
<!-- Created with Inkscape (http://www.inkscape.org/) --><svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" width="628.93701" height="230.31496" version="1.2" id="svg2" >

  <g><flowDiv id="xxxx-this-is-deleted-after-converted-xxxxxx"></flowDiv>

 </g>
</svg>
"""
        self.assertIn(u'<flowDiv id="xxxx-this-is-deleted-after-converted-xxxxxx"></flowDiv>', 
                      svg)

        class DummyFileStrage(object):
            filename="this-is-svg-file-name.svg"
            file=StringIO(svg.encode("utf-8"))

        target = self._makeOne(self._getPostData(ticket_format=1, name="this-is-ticket-format-name", 
                                                 drawing=DummyFileStrage))
        target.ticket_format.choices = [(1, 1)]

        self.assertTrue(target.validate())
        result = fromstring(target.data_value["drawing"])
        self.assertEquals(u'{%s}svg' % SVG_NAMESPACE, result.tag)
        self.assertEquals(u'{%s}g' % SVG_NAMESPACE, result[0].tag)
        self.assertEquals(u'{%s}flowDiv' % SVG_NAMESPACE, result[0][0].tag)


if __name__ == "__main__":
    unittest.main()
