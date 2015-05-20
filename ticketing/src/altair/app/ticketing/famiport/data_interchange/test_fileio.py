# encoding: utf-8
import unittest

class IntegerColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import Integer
        target = Integer(10)
        result = target.marshal(None, 10)
        self.assertEqual(result, u'10')

    def test_marshal_too_long(self):
        from .fileio import Integer
        target = Integer(2)
        with self.assertRaises(ValueError):
            target.marshal(None, 100)

    def test_marshal_none_length(self):
        from .fileio import Integer
        target = Integer(None)
        result = target.marshal(None, 10)
        self.assertEqual(result, u'10')

    def test_unmarshal_basic(self):
        from .fileio import Integer
        target = Integer(10)
        result = target.unmarshal(None, u'10')
        self.assertEqual(result, 10)

    def test_unmarshal_non_numeric(self):
        from .fileio import Integer
        target = Integer(10)
        with self.assertRaises(ValueError):
            target.unmarshal(None, u'abc')


class ZeroPaddedIntegerColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import ZeroPaddedInteger
        target = ZeroPaddedInteger(10)
        result = target.marshal(None, 10)
        self.assertEqual(result, u'0000000010')

    def test_marshal_too_long(self):
        from .fileio import ZeroPaddedInteger
        target = ZeroPaddedInteger(2)
        with self.assertRaises(ValueError):
            target.marshal(None, 100)

    def test_unmarshal_basic(self):
        from .fileio import ZeroPaddedInteger
        target = ZeroPaddedInteger(10)
        result = target.unmarshal(None, u'0000000010')
        self.assertEqual(result, 10)

    def test_unmarshal_wrong_length(self):
        from .fileio import ZeroPaddedInteger
        target = ZeroPaddedInteger(5)
        with self.assertRaises(ValueError):
            target.unmarshal(None, u'10')
        with self.assertRaises(ValueError):
            target.unmarshal(None, u'0000010')

    def test_unmarshal_non_numeric(self):
        from .fileio import ZeroPaddedInteger
        target = ZeroPaddedInteger(10)
        with self.assertRaises(ValueError):
            target.unmarshal(None, u'abc')


class ZeroPaddedNumericStringColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import ZeroPaddedNumericString
        target = ZeroPaddedNumericString(10)
        result = target.marshal(None, u'10')
        self.assertEqual(result, u'0000000010')

    def test_marshal_non_numeric(self):
        from .fileio import ZeroPaddedNumericString
        target = ZeroPaddedNumericString(10)
        with self.assertRaises(ValueError):
            target.marshal(None, u'aho')

    def test_marshal_too_long(self):
        from .fileio import ZeroPaddedNumericString
        target = ZeroPaddedNumericString(2)
        with self.assertRaises(ValueError):
            target.marshal(None, u'100')


class BooleanColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import Boolean
        target = Boolean('y', 'n')
        result = target.marshal(None, True)
        self.assertEqual(result, u'y')
        result = target.marshal(None, False)
        self.assertEqual(result, u'n')


class WideWidthStringColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import WideWidthString
        target = WideWidthString(3)
        result = target.marshal(None, u'テスト')
        self.assertEqual(result, u'テスト')


class DateTimeColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import DateTime
        from datetime import datetime
        target = DateTime(12, pytype=datetime, format=u'%Y-%m-%d')
        result = target.marshal(None, datetime(2015, 1, 1))
        self.assertEqual(result, u'2015-01-01')


