# encoding:utf-8

import unittest

class CollectVarsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.preview.fillvalues import template_collect_vars
        return template_collect_vars(*args, **kwargs)

    def test_it(self):
        tmpl = "{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl)
        self.assertEquals(list(sorted(result)), ["bar", "foo", "fooo"])

    def test_with_expression(self):
        tmpl = u"{{aux.販売区分}}"
        result = self._callFUT(tmpl)
        self.assertEquals(list(sorted(result)), [u"aux.販売区分"])

class ConvertDictToNestedDict(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.preview.fillvalues import convert_to_nested_dict
        return convert_to_nested_dict(*args, **kwargs)

    def test_identity(self):
        D = {"abc": "1234", u"あいう": u"わをん"}
        result = self._callFUT(D)
        self.assertEqual(D, result)

    def test_with_dotted_values(self):
        D = {"aux.abc": "1234", u"あいう": u"わをん"}
        result = self._callFUT(D)
        self.assertNotEqual(D, result)
        self.assertEqual(result,{"aux.abc": "1234", u"あいう": u"わをん", "aux": {"abc": "1234"}})

    def test_with_dotted_values2(self):
        D = {"abc.xyz.abc": "1234", u"abc.abc": u"わをん"}
        result = self._callFUT(D)
        self.assertEqual(result["abc"]["xyz"]["abc"], "1234")
        self.assertEqual(result["abc"]["abc"], u"わをん")

class FillvaluesTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.preview.fillvalues import template_fillvalues
        return template_fillvalues(*args, **kwargs)

    def test_it(self):
        tmpl = u"{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl, {"bar": "this-is-rendered"})
        self.assertEquals(result, "{{foo}} this-is-rendered {{{fooo}}} {{foo}}")

    def test_it_with_indexed(self):
        from altair.app.ticketing.tickets.preview.fillvalues import IndexedVariation

        tmpl = u"{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl, {"bar": "this-is-rendered"}, variation=IndexedVariation(style="fill:#afa"))
        self.assertEquals(result, u'<flowSpan style="fill:#afa">1. </flowSpan>{{foo}} this-is-rendered <flowSpan style="fill:#afa">2. </flowSpan>{{{fooo}}} <flowSpan style="fill:#afa">1. </flowSpan>{{foo}}')

    def test_it_with_indexed_emit(self):
        from altair.app.ticketing.tickets.preview.fillvalues import IndexedVariation
        tmpl = u"{{foo}} {{{bar}}} {{{foo}}} {{bar}}"
        result = self._callFUT(tmpl, {"bar": "<a>", "foo":"---"}, variation=IndexedVariation(style="fill:#afa"))
        self.assertEquals(result, u"--- <a> --- &lt;a&gt;")

    def test_with_expression(self):
        tmpl = u"{{aux.販売区分}}"
        result = self._callFUT(tmpl, {u"aux.販売区分": u"---"})
        self.assertEquals(result, u"---")


if __name__ == "__main__":
    unittest.main()

