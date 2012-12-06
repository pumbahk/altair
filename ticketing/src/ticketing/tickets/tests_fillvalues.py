import unittest

class CollectVarsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.fillvalues import template_collect_vars
        return template_collect_vars(*args, **kwargs)

    def test_it(self):
        tmpl = "{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl)
        self.assertEquals(list(sorted(result)), ["bar", "foo", "fooo"])

class FillvaluesTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.fillvalues import template_fillvalues
        return template_fillvalues(*args, **kwargs)

    def test_it(self):
        tmpl = "{{foo}} {{{bar}}} {{{fooo}}} {{foo}}"
        result = self._callFUT(tmpl, {"bar": "this-is-rendered"})
        self.assertEquals(result, "{{foo}} this-is-rendered {{fooo}} {{foo}}")


if __name__ == "__main__":
    unittest.main()

