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


class DecimalColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import Decimal
        import decimal
        target = Decimal(precision=5, scale=3)
        result = target.marshal(None, decimal.Decimal('10000'))
        self.assertEqual(result, u'99.999')
        target = Decimal(precision=5, scale=2)
        result = target.marshal(None, decimal.Decimal('10000'))
        self.assertEqual(result, u'999.99')
        target = Decimal(precision=5, scale=1)
        result = target.marshal(None, decimal.Decimal('10000'))
        self.assertEqual(result, u'9999.9')
        target = Decimal(precision=5, scale=0)
        result = target.marshal(None, decimal.Decimal('10000'))
        self.assertEqual(result, u'10000')


class BooleanColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import Boolean
        target = Boolean('y', 'n')
        result = target.marshal(None, True)
        self.assertEqual(result, u'y')
        result = target.marshal(None, False)
        self.assertEqual(result, u'n')


class SJISStringColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import SJISString
        target = SJISString(5)
        with self.assertRaises(ValueError):
            target.marshal(None, u'テスト')
        target = SJISString(6)
        result = target.marshal(None, u'テスト')
        self.assertEqual(result, u'テスト')


class WideWidthStringColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import WideWidthString
        target = WideWidthString(3)
        result = target.marshal(None, u'テスト')
        self.assertEqual(result, u'テスト')

    def test_marshal_fail(self):
        from .fileio import WideWidthString
        target = WideWidthString(3)
        with self.assertRaises(ValueError):
            target.marshal(None, u'AAA')

    def test_marshal_conversion(self):
        from .fileio import WideWidthString
        target = WideWidthString(3, conversion=True)
        result = target.marshal(None, u'AAA')
        self.assertEqual(result, u'ＡＡＡ')


class DateTimeColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import DateTime
        from datetime import datetime
        target = DateTime(12, pytype=datetime, format=u'%Y-%m-%d')
        result = target.marshal(None, datetime(2015, 1, 1))
        self.assertEqual(result, u'2015-01-01')


class TimeColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import Time
        from datetime import time
        target = Time(5, format=u'%H:%M')
        result = target.marshal(None, time(12, 34, 56))
        self.assertEqual(result, u'12:34')

    def test_unmarshal_basic(self):
        from .fileio import Time
        from datetime import time 
        target = Time(5, format=u'%H:%M')
        result = target.unmarshal(None, u'12:34')
        self.assertEqual(result, time(12, 34, 0))


class DurationColumnSpecificationTest(unittest.TestCase):
    def test_marshal_basic(self):
        from .fileio import Duration
        from datetime import timedelta
        target = Duration(4, format=u'%H%M')
        result = target.marshal(None, timedelta(days=2, seconds=3660))
        self.assertEqual(result, u'4901')



