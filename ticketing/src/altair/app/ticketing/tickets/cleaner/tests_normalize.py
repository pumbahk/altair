# -*- coding:utf-8 -*-
import unittest
import os.path
from altair.app.ticketing.tickets.cleaner.normalize import LBrace, RBrace, Content
from altair.app.ticketing.testing import ElementTreeTestMixin

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


class NormalizerTestCase(unittest.TestCase, ElementTreeTestMixin):
    def check(self, fn, *args, **kwargs):
        from lxml.etree import fromstring
        from altair.app.ticketing.tickets.cleaner.normalize import normalize_etree
        import re
        lhs, rhs = re.split(ur'\s+->\s+', fn.__doc__, 1)
        tree = fromstring(lhs)
        expected = fromstring(rhs)
        result = normalize_etree(tree, *args, **kwargs)
        self.assertEqualsEtree(result.getroot(), expected, fn.__doc__)


class SVGNormalizeUnitTests(NormalizerTestCase):
    def test_it(self):
        u"""<doc>{{<flowSpan style="font-weight:bold">価格}}</flowSpan></doc> -> <doc><flowSpan style="font-weight:bold">{{価格}}</flowSpan></doc>"""
        self.check(self.test_it)

    def test_cleaned_xml0(self):
        u"""<a>{{bb}}</a> -> <a>{{bb}}</a>"""
        self.check(self.test_cleaned_xml0)

    def test_cleaned_xml1(self):
        u"""<a>{{bb}} {{c}}</a> -> <a>{{bb}} {{c}}</a>"""
        self.check(self.test_cleaned_xml1)

    def test_cleaned_xml2(self):
        u"""<doc><a>{{bb</a>}}</doc> -> <doc><a>{{bb}}</a></doc>"""
        self.check(self.test_cleaned_xml2)

    def test_cleaned_xml3(self):
        u"""<doc><a>{<b>{ff</b></a>}}</doc> -> <doc><a><b>{{ff}}</b></a></doc>"""
        self.check(self.test_cleaned_xml3)

    def test_cleaned_xml4(self):
        u"""<doc><a>{<b>{ff}}</b></a></doc> -> <doc><a><b>{{ff}}</b></a></doc>"""
        self.check(self.test_cleaned_xml4)

    def test_cleaned_xml5(self):
        u"""<doc><a>{</a>{ff}<b>}</b></doc> -> <doc><a/>{{ff}}<b/></doc>"""
        self.check(self.test_cleaned_xml5)

    def test_cleaned_xml6(self):
        u"""<doc><a>{{hhh}} --- {{ii}</a>}</doc> -> <doc><a>{{hhh}} --- {{ii}}</a></doc>"""
        self.check(self.test_cleaned_xml6)

    def test_cleaned_xml7(self):
        u"""<doc><a>{{hhh}} --- {</a>{ii}}</doc> -> <doc><a>{{hhh}} --- </a>{{ii}}</doc>"""
        self.check(self.test_cleaned_xml7)

    def test_cleaned_xml8(self):
        u"""<doc><a><b> xxx </b> {{</a>yyy}}</doc> -> <doc><a><b> xxx </b> </a>{{yyy}}</doc>"""
        self.check(self.test_cleaned_xml8)

    def test_cleaned_xml9(self):
        u"""<doc><a><b> xxx </b> {{y</a>yy}}</doc> -> <doc><a><b> xxx </b> {{yyy}}</a></doc>"""
        self.check(self.test_cleaned_xml9)

    def test_cleaned_xml10(self):
        u"""<doc><a><b> x{x}x </b> {{y</a>yy}}</doc> -> <doc><a><b> x{x}x </b> {{yyy}}</a></doc>"""
        self.check(self.test_cleaned_xml10)

    def test_cleaned_xml11(self):
        u"<doc><a><a> {{ </a> {{yyy}}</a></doc> -> <doc><a><a> {{  {{yyy}}</a></a></doc>"
        self.check(self.test_cleaned_xml11)

    def test_cleaned_xml13(self):
        u"<doc><g><a><b><c>{{</c><c>{{yyy}}</c></b></a><a><x><r/></x><b><c/><c/></b></a></g></doc> -> <doc><g><a><b><c></c><c>{{{{yyy}}</c></b></a><a><x><r></r></x><b><c></c><c></c></b></a></g></doc>"
        self.check(self.test_cleaned_xml13)

    def test_cleaned_xml14(self):
        u"<doc><g><a><b><c>{{yyy}}</c><c>}</c></b></a><a><x><r/></x><b><c/><c/></b></a></g></doc> -> <doc><g><a><b><c>{{yyy}}</c><c>}</c></b></a><a><x><r></r></x><b><c></c><c></c></b></a></g></doc>"
        self.check(self.test_cleaned_xml14)

    ## simple xml1 and simple xml2 's result are asymnetric. this is support for unmatched parensis character set e.g. (().
    def test_simple_xml1(self):
        u"<doc>{<a></a></doc> -> <doc><a></a></doc>"
        self.check(self.test_simple_xml1)

    def test_simple_xml2(self):
        u"<doc>}}<a></a></doc> -> <doc>}}<a></a></doc>"
        self.check(self.test_simple_xml2)


class EliminatedTagNormalizeUnitTests(NormalizerTestCase):
    def test_it(self):
        u"""<F id="1">{{<F id="2">zz</F><F id="3">}}</F></F> -> <F id="1">{{zz}}</F>"""
        self.check(self.test_it, eliminate=True)

    def test_it2(self):
        u"""<doc>{{<F id="2">zz</F><F id="3">}}</F></doc> -> <doc><F id="2">{{zz}}</F></doc>"""
        self.check(self.test_it2, eliminate=True)

    def test_it3(self):
        u"""<doc><F id="1"><F id="2">x</F>)</F></doc> -> <doc><F id="1">x</F>)</doc>"""
        self.check(self.test_it3, eliminate=True)

    def test_it4(self):
        u"""<doc><F id="1">{{<F id="2">aaa}}</F>)</F></doc> -> <doc><F id="1">{{aaa}}</F>)</doc>"""
        self.check(self.test_it4, eliminate=True)

    def test_complex(self):
        """そのまま{{}}の中の文字列をmustacheで文字列を埋め込もうとするとxmlとして不正な形式になり失敗する.normalizeした後のものはok"""

        import pystache
        from lxml.etree import fromstring, tostring, XMLSyntaxError
        from altair.app.ticketing.tickets.cleaner.normalize import normalize_etree
        from altair.svg.constants import SVG_NAMESPACE
        svg_file = open(os.path.join(os.path.dirname(__file__), "sample.svg")).read().decode("utf-8")

        ## occur xml syntax error using non normalized svg 
        render = pystache.Renderer()
        emitted = render.render(svg_file, {u"名前": u"--name--"})

        with self.assertRaises(XMLSyntaxError):
            fromstring(emitted.encode("utf-8"))

        ## normalized svg
        normalized = tostring(normalize_etree(fromstring(svg_file.encode("utf-8")), eliminate=True))

        render = pystache.Renderer()
        emitted = render.render(normalized, {u"名前": "--name--"})
        self.assertTrue("{%s}svg" % SVG_NAMESPACE, fromstring(emitted).tag)

    ## todo: move
    def test_double(self):
        """<doc><a>{{xxx}}{{yyy}}</a></doc>
        """
        from altair.app.ticketing.tickets.preview.fillvalues import template_fillvalues
        result = template_fillvalues("<doc><a>{{xxx}}</a></doc>", {"xxx": "{{xxx}}{{yyy}}"})
        self.assertEquals("<doc><a>{{xxx}}{{yyy}}{{yyy}}</a></doc>", result)


if __name__ == "__main__":
    unittest.main()
