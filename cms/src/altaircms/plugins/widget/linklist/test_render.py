import unittest
from altaircms.plugins.widget.linklist.models import LinklistWidget
from altaircms.plugins.widget.linklist.models import linklist_render


def DummyFinder(*args, **kwargs):
        return ["a", "b", "c"]

class RenderTests(unittest.TestCase):
    def test_it(self):
        widget = LinklistWidget(N=7, delimiter=u"/", finder_kind=u"thisWeek")
        self.assertEquals(linklist_render(widget, DummyFinder), 
                         u'<div id="thisWeek"><p>a/b/c</p></div>')

if __name__ == "__main__":
    unittest.main()
