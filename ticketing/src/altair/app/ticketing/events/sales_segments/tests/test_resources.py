import unittest
from pyramid import testing


class SalesSegmentEditorTests(unittest.TestCase):

    def _getTarget(self):
        from ..resources import SalesSegmentEditor
        return SalesSegmentEditor

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_init(self):
        sales_segment_group = testing.DummyModel()
        form = testing.DummyModel()

        target = self._makeOne(sales_segment_group, form)

        self.assertEqual(target.sales_segment_group, sales_segment_group)
        self.assertEqual(target.form, form)

    def test_apply_changes_use_default(self):
        from datetime import datetime
        sales_segment_group = testing.DummyModel(
            start_for_performance=lambda performance: datetime(2013, 8, 31),
        )
        form = DummyForm(
            fields=[
                testing.DummyModel(name="start_at"),
                testing.DummyModel(name="use_default_start_at", data=True),
            ],
        )

        target = self._makeOne(sales_segment_group, form)
        
        obj = testing.DummyModel(
            performance=testing.DummyModel()
        )
        result = target.apply_changes(obj)

        self.assertEqual(result, obj)
        self.assertTrue(result.use_default_start_at)
        self.assertEqual(result.start_at, datetime(2013, 8, 31))

    def test_apply_changes_use_form(self):
        from datetime import datetime
        sales_segment_group = testing.DummyModel(
        )
        form = DummyForm(
            fields=[
                testing.DummyModel(name="start_at", data=datetime(2013, 8, 31)),
                testing.DummyModel(name="use_default_start_at", data=False),
            ],
        )

        target = self._makeOne(sales_segment_group, form)
        
        obj = testing.DummyModel(
            performance=testing.DummyModel()
        )
        result = target.apply_changes(obj)

        self.assertEqual(result, obj)
        self.assertFalse(result.use_default_start_at)
        self.assertEqual(result.start_at, datetime(2013, 8, 31))

class DummyForm(dict):
    def __init__(self, fields):
        for field in fields:
            self[field.name] = field
            setattr(self, field.name, field)
        self.fields = fields

    def __iter__(self):
        return iter(self.fields)



class UpdateSalesSegmentTests(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from ..resources import update_sales_segment
        return update_sales_segment(*args, **kwargs)

    def test_update_sales_segment_use_defaults(self):
        from datetime import datetime, time
        ssg = testing.DummyModel(
            seat_choice=False,
            public=True,
            reporting=False,
            payment_delivery_method_pairs=[],
            start_at=datetime(2013, 8, 31),
            end_day_prior_to_performance=1,
            end_time=time(23, 59),
            upper_limit=10,
            order_limit=20,
            account_id=1,
            margin_ratio=150,
            refund_ratio=250,
            printing_fee=350,
            registration_fee=450,
            auth3d_notice=u"testing",
        )

        used_performances = []
        ssg.start_for_performance = lambda performance: used_performances.append(performance) or datetime(2013, 10, 11, 12, 31)
        ssg.end_for_performance = lambda performance: used_performances.append(performance) or datetime(2013, 11, 11, 12, 31)

        ss = testing.DummyModel(
            performance=testing.DummyModel(),
            use_default_seat_choice=True,
            use_default_public=True,
            use_default_reporting=True,
            use_default_payment_delivery_method_pairs=True,
            use_default_start_at=True,
            use_default_end_at=True,
            use_default_upper_limit=True,
            use_default_order_limit=True,
            use_default_account_id=True,
            use_default_margin_ratio=True,
            use_default_refund_ratio=True,
            use_default_printing_fee=True,
            use_default_registration_fee=True,
            use_default_auth3d_notice=True,
        )

        self._callFUT(ssg, ss)

        self.assertFalse(ss.seat_choice)
        self.assertTrue(ss.public)
        self.assertFalse(ss.reporting)
        self.assertEqual(ss.payment_delivery_method_pairs, [])
        self.assertEqual(ss.start_at, datetime(2013, 8, 31))
        self.assertEqual(ss.end_at, datetime(2013, 11, 11, 12, 31))
        self.assertEqual(ss.upper_limit, 10)
        self.assertEqual(ss.order_limit, 20)
        self.assertEqual(ss.account_id, 1)
        self.assertEqual(ss.margin_ratio, 150)
        self.assertEqual(ss.refund_ratio, 250)
        self.assertEqual(ss.printing_fee, 350)
        self.assertEqual(ss.registration_fee, 450)
        self.assertEqual(ss.auth3d_notice, u"testing")

    def test_update_sales_segment_use_owns(self):
        from datetime import datetime, time
        ssg = testing.DummyModel(
            seat_choice=False,
            public=True,
            reporting=False,
            payment_delivery_method_pairs=[],
            start_day_prior_to_performance=14,
            start_time=time(10, 00),
            end_day_prior_to_performance=1,
            end_time=time(23, 59),
            upper_limit=10,
            order_limit=20,
            account_id=1,
            margin_ratio=150,
            refund_ratio=250,
            printing_fee=350,
            registration_fee=450,
            auth3d_notice=u"testing",
        )

        ss = testing.DummyModel(
            use_default_seat_choice=False,
            use_default_public=False,
            use_default_reporting=False,
            use_default_payment_delivery_method_pairs=False,
            use_default_start_at=False,
            use_default_end_at=False,
            use_default_upper_limit=False,
            use_default_order_limit=False,
            use_default_account_id=False,
            use_default_margin_ratio=False,
            use_default_refund_ratio=False,
            use_default_printing_fee=False,
            use_default_registration_fee=False,
            use_default_auth3d_notice=False,
            seat_choice=True,
            public=False,
            reporting=True,
            payment_delivery_method_pairs=[testing.DummyModel()],
            start_at=datetime(2014, 10, 11, 12, 31),
            end_at=datetime(2014, 11, 11, 12, 31),
            upper_limit=110,
            order_limit=120,
            account_id=10,
            margin_ratio=1150,
            refund_ratio=1250,
            printing_fee=1350,
            registration_fee=1450,
            auth3d_notice=u"testing-own",
        )

        self._callFUT(ssg, ss)
        
        self.assertTrue(ss.seat_choice)
        self.assertFalse(ss.public)
        self.assertTrue(ss.reporting)
        self.assertEqual(len(ss.payment_delivery_method_pairs), 1)
        self.assertEqual(ss.start_at, datetime(2014, 10, 11, 12, 31))
        self.assertEqual(ss.end_at, datetime(2014, 11, 11, 12, 31))
        self.assertEqual(ss.upper_limit, 110)
        self.assertEqual(ss.order_limit, 120)
        self.assertEqual(ss.account_id, 10)
        self.assertEqual(ss.margin_ratio, 1150)
        self.assertEqual(ss.refund_ratio, 1250)
        self.assertEqual(ss.printing_fee, 1350)
        self.assertEqual(ss.registration_fee, 1450)
        self.assertEqual(ss.auth3d_notice, u"testing-own")
