#-*- coding: utf-8 -*-
import unittest
import string

class DummyForm(dict):
    """ """
    pass

class DummyField(object):
    def __init__(self, data, raw_data=None):
        self.data = data
        self.raw_data = raw_data or [data]
        self.errors = []

    def gettext(self, *args, **kwds):
        return 'gettext string'


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


class CharsetTest(unittest.TestCase):
    def _get_target(self):
        from ..validators import Charset
        return Charset

    def _make_one(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_none(self):
        from collections import namedtuple
        x = self._make_one('ascii')
        x(None, namedtuple('_', 'data')(data=None))


class JISX0208Test(unittest.TestCase):
    VALID_CHARS = unicode(string.printable) + u'日本語'
    INVALID_CHARS = u'㈱ⅰ①⑴⒈❶'

    def _get_target(self):
        from ..validators import JISX0208
        return JISX0208

    def test_valid_by_form(self):
        checker = self._get_target()
        form = DummyForm()
        field = DummyField(self.VALID_CHARS)
        checker(form, field)

    def test_invalid_by_form(self):
        from wtforms.validators import ValidationError
        checker = self._get_target()
        form = DummyForm()
        field = DummyField(self.INVALID_CHARS)
        with self.assertRaises(ValidationError):
            checker(form, field)

    def test_input_nonunicode(self):
        checker = self._get_target()
        data = u'日本語'.encode('sjis')
        with self.assertRaises(UnicodeDecodeError):
            checker.get_error_chars(data)

    def test_get_check_chars(self):
        checker = self._get_target()
        chars = checker.get_error_chars(self.VALID_CHARS)
        self.assertEqual(chars, [])

        chars = checker.get_error_chars(self.INVALID_CHARS)
        ans = list(self.INVALID_CHARS)
        self.assertEqual(chars, ans)

    def test_generate_check_chars(self):
        checker = self._get_target()
        data = self.VALID_CHARS + self.INVALID_CHARS
        for ch in checker.generate_error_chars(data):
            self.assert_(ch in self.INVALID_CHARS,
                         'Encode Error: {0}'.format(repr(ch)))


class MultipleEmailTest(unittest.TestCase):
    def _get_target(self):
        from ..validators import MultipleEmail
        return MultipleEmail

    def _make_one(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_none(self):
        checker = self._make_one()
        form = DummyForm()
        field = DummyField(data=None)
        self.assertIsNone(checker(form, field))

    def test_space(self):
        checker = self._make_one()
        form = DummyForm()
        field = DummyField(data=u'')
        self.assertIsNone(checker(form, field))

    def test_object(self):
        from wtforms.validators import ValidationError
        checker = self._make_one()
        form = DummyForm()
        field = DummyField(data=object())
        with self.assertRaises(ValidationError):
            checker(form, field)

    def test_single(self):
        checker = self._make_one()
        form = DummyForm()

        field = DummyField(data=u'test@example.com')
        self.assertIsNone(checker(form, field))

    def test_multiple(self):
        checker = self._make_one()
        form = DummyForm()

        field = DummyField(data=u'test@example.com, hoge@example.com')
        self.assertIsNone(checker(form, field))

    def test_single_display_name(self):
        checker = self._make_one()
        form = DummyForm()

        field = DummyField(data=u'テスト <test@example.com>')
        self.assertIsNone(checker(form, field))

        field = DummyField(data=u'"テスト" <test@example.com>')
        self.assertIsNone(checker(form, field))

    def test_multiple_display_name(self):
        checker = self._make_one()
        form = DummyForm()

        field = DummyField(data=u'テスト <test@example.com>, テスト2 <hoge@example.com>')
        self.assertIsNone(checker(form, field))

        field = DummyField(data=u'"テスト" <test@example.com>, "テスト2" <hoge@example.com>')
        self.assertIsNone(checker(form, field))

    def test_single_invalid_address(self):
        from wtforms.validators import ValidationError
        checker = self._make_one()
        form = DummyForm()

        field = DummyField(data=u'test_example.com')
        with self.assertRaises(ValidationError):
            checker(form, field)

    def test_multiple_invalid_address(self):
        from wtforms.validators import ValidationError
        checker = self._make_one()
        form = DummyForm()

        field = DummyField(data=u'test_example.com, hoge@example.com')
        with self.assertRaises(ValidationError):
            checker(form, field)

        field = DummyField(data=u'test@example.com, hoge_example.com')
        with self.assertRaises(ValidationError):
            checker(form, field)

        field = DummyField(data=u'"テスト" test@example.com, hoge@example.com')
        with self.assertRaises(ValidationError):
            checker(form, field)

        field = DummyField(data=u'"テスト" <test@example.com>,, hoge@example.com')
        with self.assertRaises(ValidationError):
            checker(form, field)
