# -*- coding:utf-8 -*-
import unittest
import os.path
from altair.app.ticketing.tickets.cleaner.normalize import LBrace, RBrace, Content

class EventsFromStringTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.normalize import tokens_from_string
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


class SVGNormalizeUnitTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.normalize import _normalize
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

    def test_cleaned_xml10(self):
        """<a><b> xxx </b> {{y</a>yy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><b> x{x}x </b> {{y</a>yy}}</doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b> x{x}x </b> {{yyy}}</a></doc>", result.getvalue())

    def test_cleaned_xml11(self):
        """<a><b> {{ </b> {{y</a>yy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><a> {{ </a> {{yyy}}</a></doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><a> {{  {{yyy}}</a></a></doc>", result.getvalue())

    def test_cleaned_xml13(self):
        """<doc><g><a><b><c>{{</c><c>{{yyy}}</c></b></a><a><x><r/></x><b><c/><c/></b></a></g></doc>"""
        from StringIO import StringIO
        io = StringIO("<doc><g><a><b><c>{{</c><c>{{yyy}}</c></b></a><a><x><r/></x><b><c/><c/></b></a></g></doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals('<doc><g><a><b><c></c><c>{{{{yyy}}</c></b></a><a><x><r></r></x><b><c></c><c></c></b></a></g></doc>', result.getvalue())

    def test_cleaned_xml14(self):
        """<doc><g><a><b><c>{{yyy}}</c><c>}</c></b></a><a><x><r/></x><b><c/><c/></b></a></g></doc>"""
        from StringIO import StringIO
        io = StringIO("<doc><g><a><b><c>{{yyy}}</c><c>}</c></b></a><a><x><r/></x><b><c/><c/></b></a></g></doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals('<doc><g><a><b><c>{{yyy}}</c><c>}</c></b></a><a><x><r></r></x><b><c></c><c></c></b></a></g></doc>', result.getvalue())

    ## simple xml1 and simple xml2 's result are asymnetric. this is support for unmatched parensis character set e.g. (().
    def test_simple_xml1(self):
        """<doc>{<a></a></doc>"""
        from StringIO import StringIO
        io = StringIO("<doc>{<a></a></doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals('<doc><a></a></doc>', result.getvalue())

    def test_simple_xml2(self):
        """<doc>}}<a></a></doc>"""
        from StringIO import StringIO
        io = StringIO("<doc>}}<a></a></doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals('<doc>}}<a></a></doc>', result.getvalue())

       
class EliminatedTagNormalizeUnitTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.normalize import normalize
        return normalize(*args, **kwargs)

    def test_it(self):
        """<F id=1>{{<F id=2>zz</F><f id=3>}}</F></F> -> <F id=1>{{zz}}</F>"""
        from StringIO import StringIO
        io = StringIO('<F id="1">{{<F id="2">zz</F><F id="3">}}</F></F>')

        result = StringIO()
        self._callFUT(io, result, eliminate=True)
        self.assertEquals('<F id="1">{{zz}}</F>', result.getvalue())

    def test_it2(self):
        """<F id=1>{{<F id=2>zz</F><f id=3>}}</F></F> -> <F id=1>{{zz}}</F>"""
        from StringIO import StringIO
        io = StringIO('<doc>{{<F id="2">zz</F><F id="3">}}</F></doc>')

        result = StringIO()
        self._callFUT(io, result, eliminate=True)
        self.assertEquals('<doc><F id="2">{{zz}}</F></doc>', result.getvalue())

    def test_it3(self):
        from StringIO import StringIO
        """<F id=1><F id=2></F>)</F> => <F id=1><F id=2></F>)</F>"""
        io = StringIO('<doc><F id="1"><F id="2">x</F>)</F></doc>')

        result = StringIO()
        self._callFUT(io, result, eliminate=True)
        self.assertEquals('<doc><F id="1">x</F>)</doc>', result.getvalue())

    def test_it4(self):
        from StringIO import StringIO
        io = StringIO('<doc><F id="1">{{<F id="2">aaa}}</F>)</F></doc>')

        result = StringIO()
        self._callFUT(io, result, eliminate=True)
        self.assertEquals('<doc><F id="1">{{aaa}}</F>)</doc>', result.getvalue())

    def test_complex(self):
        """ そのまま{{}}の中の文字列をmustacheで文字列を埋め込もうとするとxmlとして不正な形式になり失敗する.normalizeした後のものはok
        """
        from StringIO import StringIO
        import pystache
        import lxml.etree
        svg_file = os.path.join(os.path.dirname(__file__), "sample.svg")

        ## occur xml syntax error using non normalized svg 
        render = pystache.Renderer()
        emitted = render.render(open(svg_file).read().decode("utf-8"), {u"name": "--name--"})
        io = StringIO()
        io.write(emitted.encode("utf-8"))
        io.seek(0)

        with self.assertRaises(lxml.etree.XMLSyntaxError):
            lxml.etree.parse(io)

        ## normalized svg
        io = StringIO()
        with open(svg_file) as rf:
            self._callFUT(rf, io, eliminate=True)            

        render = pystache.Renderer()
        emitted = render.render(io.getvalue().decode("utf-8"), {u"名前": "--name--"})
        io = StringIO()
        io.write(emitted.encode("utf-8"))
        io.seek(0)
        
        self.assertTrue(lxml.etree.parse(io))

    ## todo: move
    def test_double(self):
        """<doc><a>{{xxx}}{{yyy}}</a></doc>
        {{{xxx}}{{yyy}}} => {{placeholder}} # placeholder={xxx}}{{yyy}

        so. if you want to get {{xxx}}{{yyy}} from {{xxx}}. input {{{xxx}}{{yyy}}} at preview page.
        """
        from altair.app.ticketing.tickets.preview.fillvalues import template_fillvalues
        result = template_fillvalues("<doc><a>{{xxx}}</a></doc>", {"xxx": "{{{xxx}}{{yyy}}}"})
        self.assertEquals("<doc><a>{{xxx}}{{yyy}}</a></doc>", result)


if __name__ == "__main__":
    unittest.main()
