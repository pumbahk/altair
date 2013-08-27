import unittest

class DummyForm(dict):
    """ """

class DummyField(object):
    def __init__(self, data, raw_data=None):
        self.data = data
        self.raw_data = raw_data or [data]
        self.errors = []

class SwitchOptionalTests(unittest.TestCase):

    def _getTarget(self):
        from ..validators import SwitchOptional
        return SwitchOptional

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_call_with_switch_on(self):
        from wtforms.validators import StopValidation
        form = DummyForm()
        form['use_default'] = DummyField(data=True)

        target = self._makeOne("use_default")
        try:
            target(form, DummyField(data=""))
            self.fail()
        except StopValidation:
            pass

    def test_call_with_swtich_off(self):
        form = DummyForm()
        form['use_default'] = DummyField(data=False)

        target = self._makeOne("use_default")
        target(form, DummyField(data=""))


