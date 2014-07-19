import unittest
import mock

class OurFieldTest(unittest.TestCase):
    def _getTarget(self):
        from ..fields.core import OurField
        return OurField

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_unbound_field(self):
        from wtforms.fields.core import UnboundField
        target = self._makeOne()
        self.assertTrue(isinstance(target, UnboundField))

    def test_rendering_mixin_without_override(self):
        widget = mock.Mock()
        form = mock.Mock()
        target = self._makeOne(widget=widget)
        _target = target.bind(form=form, name='example')
        _target(a=1, b=2, c=3)
        widget.called_with(a=1, b=2, c=3)

    def test_rendering_mixin_with_override(self):
        widget = mock.Mock()
        form = mock.Mock()
        target = self._makeOne(widget=widget)
        _target = target.bind(form=form, name='example')
        overriding_widget = mock.Mock()
        _target(_widget=overriding_widget, a=1, b=2, c=3)
        overriding_widget.assert_called_with_argument(a=1, b=2, c=3)
        self.assertFalse(widget.called)

    def test_mixin_init_pre(self):
        widget = mock.Mock()
        form = mock.Mock()
        target = self._makeOne(widget=widget, hide_on_new=True)
        _target = target.bind(form=form, name='example')
        overriding_widget = mock.Mock()
        self.assertTrue(_target.hide_on_new)

    def test_name_builder(self):
        widget = mock.Mock()
        form = mock.Mock()
        target = self._makeOne(widget=widget, name_builder=lambda name:'[%s]' % name)
        _target = target.bind(form=form, name='example')
        self.assertTrue(_target.name, '[example]')
        self.assertTrue(_target.short_name, 'example')
