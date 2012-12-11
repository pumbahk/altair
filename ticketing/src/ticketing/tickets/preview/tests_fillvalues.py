import unittest

class CollectVarsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.preview.fillvalues import template_collect_vars
        return template_collect_vars(*args, **kwargs)

    def test_it(self):
        tmpl = "{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl)
        self.assertEquals(list(sorted(result)), ["bar", "foo", "fooo"])

class FillvaluesTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.preview.fillvalues import template_fillvalues
        return template_fillvalues(*args, **kwargs)

    def test_it(self):
        tmpl = "{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl, {"bar": "this-is-rendered"})
        self.assertEquals(result, "{{foo}} this-is-rendered {{{fooo}}} {{foo}}")

    def test_it_with_indexed(self):
        from ticketing.tickets.preview.fillvalues import IndexedVariation

        tmpl = "{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl, {"bar": "this-is-rendered"}, variation=IndexedVariation(style="fill:#afa"))
        self.assertEquals(result, u'<flowSpan style="fill:#afa">1. </flowSpan>{{foo}} this-is-rendered <flowSpan style="fill:#afa">2. </flowSpan>{{{fooo}}} <flowSpan style="fill:#afa">1. </flowSpan>{{foo}}')

    def test_it_with_indexed_emit(self):
        from ticketing.tickets.preview.fillvalues import IndexedVariation
        tmpl = "{{foo}} {{{bar}}} {{{foo}}} {{bar}}"
        result = self._callFUT(tmpl, {"bar": "<a>", "foo":"---"}, variation=IndexedVariation(style="fill:#afa"))
        self.assertEquals(result, u"--- <a> --- &lt;a&gt;")


if __name__ == "__main__":
    unittest.main()

