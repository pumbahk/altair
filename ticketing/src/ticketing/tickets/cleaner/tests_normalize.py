# -*- coding:utf-8 -*-
import unittest
from ticketing.tickets.cleaner.normalize import LBrace, RBrace, Content

class EventsFromStringTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.cleaner.normalize import tokens_from_string
        return tokens_from_string(*args, **kwargs)

    def test_token_from_string__simple(self):
        string = "{}"
        result = self._callFUT(string)
        self.assertEquals(result, [LBrace("{"), RBrace("}")])

    def test_token_from_string__simple_with_dusty_input(self):
        string = "xx{yyy}zzz"
        result = self._callFUT(string)
        self.assertEquals(result, [Content("xx"), LBrace("{"),Content("yyy"), RBrace("}"), Content("zzz")])

    def test_token_from_string__complex(self):
        string = "{{}{}}"
        result = self._callFUT(string)
        self.assertEquals(result, [LBrace("{"), LBrace("{"), RBrace("}"), LBrace("{"), RBrace("}"), RBrace("}")])

    def test_token_from_string__complex_with_dusty_input(self):
        string = "@@@{bbb{cc}dd{}e}"
        result = self._callFUT(string)
        self.assertEquals(result, [Content("@@@"), LBrace("{"), Content("bbb"), LBrace("{"), Content("cc"), RBrace("}"), Content("dd"), LBrace("{"), RBrace("}"), Content("e"), RBrace("}")])


class BufferedConsumerUnitTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.cleaner.normalize import _normalize
        return _normalize(*args, **kwargs)

    def test_it(self):
        from StringIO import StringIO
        io = StringIO(u"""<doc>{{<flowSpan style="font-weight:bold">価格}}</flowSpan></doc>""".encode("utf-8"))

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals(u'<doc><flowSpan style="font-weight:bold">{{価格}}</flowSpan></doc>', result.getvalue().decode("utf-8"))


    def test_cleaned_xml0(self):
        """<a>{{bb}}</a> -> <a>{{bb}}</a>"""
        from StringIO import StringIO
        io = StringIO("<a>{{bb}}</a>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<a>{{bb}}</a>", result.getvalue())

    def test_cleaned_xml1(self):
        """<a>{{bb}} {{cc}}</a> -> <a>{{bb}} {{cc}}</a>"""
        from StringIO import StringIO
        io = StringIO("<a>{{bb}} {{c}}</a>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<a>{{bb}} {{c}}</a>", result.getvalue())

    def test_cleaned_xml2(self):
        """<a>{{bb</a>}} -> <a>{{bb}}</a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{{bb</a>}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a>{{bb}}</a></doc>", result.getvalue())

    def test_cleaned_xml3(self):
        """<a>{<b>{ff</b></a>}} -> <a><b>{{ff}}</b></a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{<b>{ff</b></a>}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b>{{ff}}</b></a></doc>", result.getvalue())

    def test_cleaned_xml4(self):
        """<a>{<b>{ff}}</b></a> -> <a><b>{{ff}}</b></a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{<b>{ff}}</b></a></doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b>{{ff}}</b></a></doc>", result.getvalue())

    def test_cleaned_xml5(self):
        """<a>{</a>{ff}<b>}</b> -> <a></a>{{ff}}<b></b>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{</a>{ff}<b>}</b></doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals('<doc><a></a>{{ff}}<b></b></doc>', result.getvalue())

    def test_cleaned_xml6(self):
        """<a>{{hhh}} --- {{ii}</a>} -> <a>{{hhh}} --- {{ii}}</a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{{hhh}} --- {{ii}</a>}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a>{{hhh}} --- {{ii}}</a></doc>", result.getvalue())

    def test_cleaned_xml7(self):
        """<a>{{hhh}} --- {</a>{ii}} -> <a>{{hhh}} --- </a>{{ii}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{{hhh}} --- {</a>{ii}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a>{{hhh}} --- </a>{{ii}}</doc>", result.getvalue())

    def test_cleaned_xml8(self):
        """<a><b> xxx </b> {{</a>yyy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><b> xxx </b> {{</a>yyy}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b> xxx </b> </a>{{yyy}}</doc>", result.getvalue())

    def test_cleaned_xml9(self):
        """<a><b> xxx </b> {{y</a>yy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><b> xxx </b> {{y</a>yy}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b> xxx </b> {{yyy}}</a></doc>", result.getvalue())

if __name__ == "__main__":
    unittest.main()
