import unittest
from collections import namedtuple

class OurSelectWidgetTest(unittest.TestCase):
    def _getTarget(self):
        from .select import OurSelectWidget
        return OurSelectWidget

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_basic(self):
        f = namedtuple('Field', ('id', 'value', 'name', 'short_name', 'iter_choices'))
        target = self._makeOne()
        r = target(f('ID', 'VALUE', 'NAME', 'SHORT_NAME', lambda: [('A', 'A', False)]))
        self.assertIsInstance(r, unicode)
        r.render_js_data_provider('var')
