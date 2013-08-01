# -*- coding:utf-8 -*-
import unittest
from pyramid import testing

class ConfigurationTests(unittest.TestCase):
    def _getTarget(self):
        from altair.findable_label import AppendHeaderElementOutput
        return AppendHeaderElementOutput

    def test_create_from_settings__success(self):
        settings = {"altair.findable_label.label": "label"}
        self._getTarget().from_settings(settings)

    def test_create_from_settings__missing(self):
        from altair.findable_label import MissingValue
        settings = {}
        with self.assertRaises(MissingValue):
            self._getTarget().from_settings(settings)


class IncludeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from altair.findable_label import includeme
        return includeme(*args, **kwargs)

    def _get_tweens(self):
        from pyramid.interfaces import ITweens
        return self.config.registry.queryUtility(ITweens)

    def test_it(self):
        self.config.registry.settings = {"altair.findable_label.label": "this-is-label-value"}
        self._callFUT(self.config)
        self.assertEquals(['pyramid.tweens.excview_tween_factory', 'altair.findable_label.findable_label_tween_factory'], 
                          self._get_tweens().names)

    def test_missing_label(self):
        self.config.registry.settings = {}
        self._callFUT(self.config)
        self.assertIsNone(self._get_tweens())
