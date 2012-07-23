# -*- coding:utf-8 -*-
import unittest

class DummyConfigParser(object):
    D = dict(
        values = "heading complex_heading", 
        labels = "見出し 凝った見出し ", 
        renderers = u"""
  <h2 id="%%s">%%s</h2>
  <h2 class="すごい見出し" id="%%s">%%s</h2>
"""
        )
    def items(self, k):
        return self.D.items()


class UtilityTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.plugins.widget.heading.models import HeadingWidgetUtilityDefault
        return HeadingWidgetUtilityDefault

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_parse(self):
        target = self._makeOne()
        configparser = DummyConfigParser()
        config = None
        result = target.parse_settings(config, configparser)
        
        self.assertEquals(result.choices,
                          [("heading", u"見出し"), ("complex_heading", u"凝った見出し")])

        self.assertEquals(result.renderers["heading"], u'<h2 id="%s">%s</h2>')
        self.assertEquals(result.renderers["complex_heading"], u'<h2 class="すごい見出し" id="%s">%s</h2>')

        def test_rendering(self):
            target = self._makeOne()
            configparser = DummyConfigParser()
            config = None
            result = target.parse_settings(config, configparser)

            from altaircms.plugins.widget.heading.models import HeadingWidget
            widget = HeadingWidget(kind="heading", id=10, text=u"this-is-heading-content")
            result.rendering_function(widget)

            widget = HeadingWidget(kind="complex_heading", id=10, text=u"this-is-heading-content")
            result.rendering_function(widget)


if __name__ == "__main__":
    unittest.main()

