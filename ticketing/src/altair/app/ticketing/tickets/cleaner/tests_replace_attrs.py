# -*- coding:utf-8 -*-
import unittest

class EventsFromStringTests(unittest.TestCase):
    def _getTarget(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.normalize import ConvertXmlForTicketTemplateAttrsHook
        return ConvertXmlForTicketTemplateAttrsHook

    def test_replace_font_family__havent(self):
        attrs = dict(style="1")
        result = self._getTarget().replace_attrs(attrs)
        self.assertEquals(result, attrs)

    def test_replace_font_family__single(self):
        attrs = dict(style="font-family:Sans")
        result = self._getTarget().replace_attrs(attrs)
        self.assertEquals(result["style"], "font-family: MS PGothic;")

    def test_replace_font_family__with_other1(self):
        attrs = dict(style="font-family:Sans; color: red")
        result = self._getTarget().replace_attrs(attrs)
        self.assertEquals(result["style"], "font-family: MS PGothic; color: red")

    def test_replace_font_family__with_other2(self):
        attrs = dict(style="color: red; font-family:Sans")
        result = self._getTarget().replace_attrs(attrs)
        self.assertEquals(result["style"], "color: red; font-family: MS PGothic;")

    def test_replace_font_family__with_other3(self):
        attrs = dict(style="color: red; font-family:Sans; font-style: bold")
        result = self._getTarget().replace_attrs(attrs)
        self.assertEquals(result["style"], "color: red; font-family: MS PGothic; font-style: bold")

if __name__ == "__main__":
    unittest.main()
