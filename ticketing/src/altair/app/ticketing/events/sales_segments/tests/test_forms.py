# -*- coding:utf-8 -*-

import unittest
from webob.multidict import MultiDict
from pyramid.testing import DummyResource
from mock import Mock
from altair.app.ticketing.testing import _setup_db, _teardown_db

class SalesSegmentFormTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.cart.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.core.models",
        ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..forms import SalesSegmentForm
        return SalesSegmentForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_validate_start_at_use_default(self):
        formdata = MultiDict(
            dict(
                use_default_start_at="y",
                end_at="",
            )
        )
        context = DummyResource(
            organization=Mock(accounts=[Mock()]),
            event=Mock(sales_segment_groups=[]),
            sales_segment_group=None
            )
        target = self._makeOne(formdata=formdata, context=context)
        target.validate()
        self.assertNotIn('start_at', target.errors)

    def test_validate_start_at_use_form_invalid(self):
        formdata = MultiDict(
            dict(
                start_at="",
                use_default_start_at="on",
                end_at="",
            )
        )
        context = DummyResource(
            organization=Mock(accounts=[Mock()]),
            event=Mock(sales_segment_groups=[]),
            sales_segment_group=None
            )
        target = self._makeOne(formdata=formdata, context=context)
        target.process()

        target.validate()
        self.assertTrue(target.errors)
        self.assertIn('start_at', target.errors)
        self.assertEqual(target.errors['start_at'], [u"入力してください"])

    def test_validate_start_at_use_form(self):
        formdata = MultiDict(
            dict(
                start_at="2013-08-31 23:59",
                end_at="",
            )
        )
        context = DummyResource(
            organization=Mock(accounts=[Mock()]),
            event=Mock(sales_segment_groups=[]),
            sales_segment_group=None
            )
        target = self._makeOne(formdata=formdata, context=context)

        target.validate()
        self.assertEqual(target.errors['sales_segment_group_id'], [u'入力してください'])
        self.assertEqual(target.errors['payment_delivery_method_pairs'], [u'入力してください'])
        self.assertEqual(target.errors['account_id'], [u'選択してください'])
        self.assertNotIn('start_at', target.errors)


class validate_issuing_start_atTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.cart.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.core.models",
        ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..forms import validate_issuing_start_at
        return validate_issuing_start_at

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_validate_issuing_start_at_other_delivery_plugin(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=1,
            payment_method=DummyResource(name=u'コンビニ決済'),
            delivery_method=DummyResource(name=u'配送', delivery_plugin_id=plugins.SHIPPING_DELIVERY_PLUGIN_ID, deliver_at_store=lambda: False)
            )
        try:
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 10, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )
            self.assert_(True)
        except:
            raise
            self.fail()

    def test_validate_issuing_start_at_in_term(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=1,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        try:
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 9, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )
            self.assert_(True)
        except:
            self.fail()

    def test_validate_issuing_start_at_in_term_issuing_interval_days(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=2,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        try:
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 8, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )
            self.assert_(True)
        except:
            self.fail()

    def test_validate_issuing_start_at_in_term_with_issuing_interval_days(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        from ..exceptions import IssuingStartAtOutTermException
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=2,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        with self.assertRaises(IssuingStartAtOutTermException):
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 8, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_start_at=None,
                issuing_interval_days=3
                )

    def test_validate_issuing_start_at_in_term_with_issuing_start_at(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=2,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        try:
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 8, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_start_at=datetime(2014, 1, 9, 23, 59, 59),
                issuing_interval_days=None
                )
            self.assert_(True)
        except Exception as e:
            self.fail()

    def test_validate_issuing_start_at_out_term(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        from ..exceptions import IssuingStartAtOutTermException
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=1,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        with self.assertRaises(IssuingStartAtOutTermException):
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 10, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )

    def test_validate_issuing_start_at_out_term_issuing_interval_days(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        from ..exceptions import IssuingStartAtOutTermException
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=2,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        with self.assertRaises(IssuingStartAtOutTermException):
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=datetime(2014, 1, 9, 23, 59, 59),
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )

    def test_validate_issuing_start_at_in_term_with_sales_segment_end_at_being_none(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=0,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        try:
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=None,
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )
            self.assert_(True)
        except:
            self.fail()

    def test_validate_issuing_start_at_out_term_with_sales_segment_end_at_being_none(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins
        from altair.app.ticketing.core.models import DateCalculationBase
        pdmp = DummyResource(
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_start_at=None,
            issuing_interval_days=1,
            payment_method=Mock(name=u'コンビニ決済'),
            delivery_method=Mock(name=u'コンビニ引取', delivery_plugin_id=plugins.SEJ_DELIVERY_PLUGIN_ID)
            )
        try:
            self._callFUT(
                performance_start_on=datetime(2014, 1, 10, 0, 0, 0),
                performance_end_on=datetime(2014, 1, 10, 10, 0, 0),
                sales_segment_start_at=datetime(2014, 1, 1, 0, 0, 0),
                sales_segment_end_at=None,
                pdmp=pdmp,
                issuing_start_day_calculation_base=None,
                issuing_start_at=None,
                issuing_interval_days=None
                )
            self.fail()
        except:
            self.assert_(True)

