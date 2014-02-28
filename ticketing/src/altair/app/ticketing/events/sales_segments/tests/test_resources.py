import unittest
from pyramid import testing
from decimal import Decimal

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
                testing.DummyModel(name="end_at", data=None),
                testing.DummyModel(name="use_default_end_at", data=None),
                testing.DummyModel(name="seat_choice", data=None),
                testing.DummyModel(name="use_default_seat_choice", data=None),
                testing.DummyModel(name="public", data=None),
                testing.DummyModel(name="use_default_public", data=None),
                testing.DummyModel(name="reporting", data=None),
                testing.DummyModel(name="use_default_reporting", data=None),
                testing.DummyModel(name="payment_delivery_method_pairs", data=[]),
                testing.DummyModel(name="use_default_payment_delivery_method_pairs", data=None),
                testing.DummyModel(name="max_quantity", data=None),
                testing.DummyModel(name="use_default_max_quantity", data=None),
                testing.DummyModel(name="max_product_quatity", data=None),
                testing.DummyModel(name="use_default_max_product_quatity", data=None),
                testing.DummyModel(name="account_id", data=None),
                testing.DummyModel(name="use_default_account_id", data=None),
                testing.DummyModel(name="margin_ratio", data=None),
                testing.DummyModel(name="use_default_margin_ratio", data=None),
                testing.DummyModel(name="refund_ratio", data=None),
                testing.DummyModel(name="use_default_refund_ratio", data=None),
                testing.DummyModel(name="printing_fee", data=None),
                testing.DummyModel(name="use_default_printing_fee", data=None),
                testing.DummyModel(name="registration_fee", data=None),
                testing.DummyModel(name="use_default_registration_fee", data=None),
                testing.DummyModel(name="auth3d_notice", data=None),
                testing.DummyModel(name="use_default_auth3d_notice", data=None),
                testing.DummyModel(name="order_limit", data=None),
                testing.DummyModel(name="use_default_order_limit", data=None),
                testing.DummyModel(name="max_quantity_per_user", data=None),
                testing.DummyModel(name="use_default_max_quantity_per_user", data=None),
                testing.DummyModel(name="disp_orderreview", data=None),
                testing.DummyModel(name="use_default_disp_orderreview", data=None),
            ],
        )

        target = self._makeOne(sales_segment_group, form)
        
        obj = testing.DummyModel(
            performance=testing.DummyModel(),
            setting=testing.DummyModel(),
            payment_delivery_method_pairs=[
                testing.DummyModel(id=1L),
                ]
        )
        result = target.apply_changes(obj)

        self.assertEqual(result, obj)
        self.assertTrue(result.use_default_start_at)
        self.assertEqual(result.start_at, datetime(2013, 8, 31))
        self.assertEqual(result.payment_delivery_method_pairs, [])

    def test_apply_changes_use_form(self):
        from datetime import datetime
        sales_segment_group = testing.DummyModel(
        )
        form = DummyForm(
            fields=[
                testing.DummyModel(name="start_at", data=datetime(2013, 8, 31)),
                testing.DummyModel(name="use_default_start_at", data=False),
                testing.DummyModel(name="refund_ratio", data=Decimal(0)),
                testing.DummyModel(name="end_at", data=None),
                testing.DummyModel(name="use_default_end_at", data=None),
                testing.DummyModel(name="seat_choice", data=None),
                testing.DummyModel(name="use_default_seat_choice", data=None),
                testing.DummyModel(name="public", data=None),
                testing.DummyModel(name="use_default_public", data=None),
                testing.DummyModel(name="reporting", data=None),
                testing.DummyModel(name="use_default_reporting", data=None),
                testing.DummyModel(name="payment_delivery_method_pairs", data=[]),
                testing.DummyModel(name="use_default_payment_delivery_method_pairs", data=None),
                testing.DummyModel(name="max_quantity", data=None),
                testing.DummyModel(name="use_default_max_quantity", data=None),
                testing.DummyModel(name="max_product_quatity", data=None),
                testing.DummyModel(name="use_default_max_product_quatity", data=None),
                testing.DummyModel(name="account_id", data=None),
                testing.DummyModel(name="use_default_account_id", data=None),
                testing.DummyModel(name="margin_ratio", data=None),
                testing.DummyModel(name="use_default_margin_ratio", data=None),
                testing.DummyModel(name="refund_ratio", data=None),
                testing.DummyModel(name="use_default_refund_ratio", data=None),
                testing.DummyModel(name="printing_fee", data=None),
                testing.DummyModel(name="use_default_printing_fee", data=None),
                testing.DummyModel(name="registration_fee", data=None),
                testing.DummyModel(name="use_default_registration_fee", data=None),
                testing.DummyModel(name="auth3d_notice", data=None),
                testing.DummyModel(name="use_default_auth3d_notice", data=None),
                testing.DummyModel(name="order_limit", data=None),
                testing.DummyModel(name="use_default_order_limit", data=None),
                testing.DummyModel(name="max_quantity_per_user", data=None),
                testing.DummyModel(name="use_default_max_quantity_per_user", data=None),
                testing.DummyModel(name="disp_orderreview", data=None),
                testing.DummyModel(name="use_default_disp_orderreview", data=None),
            ],
        )

        target = self._makeOne(sales_segment_group, form)
        
        obj = testing.DummyModel(
            performance=testing.DummyModel(),
            setting=testing.DummyModel(),
            payment_delivery_method_pairs=[
                testing.DummyModel(id=1L),
                ]
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



class SalesSegmentAccessorTest(unittest.TestCase):
    def _getTarget(self):
        from ..resources import SalesSegmentAccessor
        return SalesSegmentAccessor

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_update_sales_segment_use_defaults(self):
        from datetime import datetime, time
        ssg = testing.DummyModel(
            id=1L,
            seat_choice=False,
            public=True,
            reporting=False,
            payment_delivery_method_pairs=[],
            start_at=datetime(2013, 8, 31),
            end_day_prior_to_performance=1,
            end_time=time(23, 59),
            max_quantity=10,
            max_product_quatity=0,
            account_id=1,
            margin_ratio=150,
            refund_ratio=250,
            printing_fee=350,
            registration_fee=450,
            auth3d_notice=u"testing",
            setting=testing.DummyModel(
                order_limit=20, 
                max_quantity_per_user=40,
                disp_orderreview=True
                )
            )

        used_performances = []
        ssg.start_for_performance = lambda performance: used_performances.append(performance) or datetime(2013, 10, 11, 12, 31)
        ssg.end_for_performance = lambda performance: used_performances.append(performance) or datetime(2013, 11, 11, 12, 31)

        ss = testing.DummyModel(
            id=1L,
            sales_segment_group=ssg,
            performance=testing.DummyModel(),
            use_default_seat_choice=True,
            use_default_public=True,
            use_default_reporting=True,
            use_default_payment_delivery_method_pairs=True,
            use_default_start_at=True,
            use_default_end_at=True,
            use_default_max_quantity=True,
            use_default_order_limit=True,
            use_default_account_id=True,
            use_default_margin_ratio=True,
            use_default_refund_ratio=True,
            use_default_printing_fee=True,
            use_default_registration_fee=True,
            use_default_auth3d_notice=True,
            use_default_max_product_quatity=True,
            payment_delivery_method_pairs=[
                testing.DummyModel(id=1L),
                testing.DummyModel(id=2L),
                ],
            setting=testing.DummyModel(
                order_limit=120,
                max_quantity_per_user=43,
                disp_orderreview=False,
                use_default_order_limit=True,
                use_default_max_quantity_per_user=True,
                use_default_disp_orderreview=True
                )
            )

        target = self._makeOne()
        target.update_sales_segment(ss)

        self.assertFalse(ss.seat_choice)
        self.assertTrue(ss.public)
        self.assertFalse(ss.reporting)
        self.assertEqual(ss.payment_delivery_method_pairs, [])
        self.assertEqual(ss.start_at, datetime(2013, 10, 11, 12, 31))
        self.assertEqual(ss.end_at, datetime(2013, 11, 11, 12, 31))
        self.assertEqual(ss.max_quantity, 10)
        self.assertEqual(ss.account_id, 1)
        self.assertEqual(ss.margin_ratio, 150)
        self.assertEqual(ss.refund_ratio, 250)
        self.assertEqual(ss.printing_fee, 350)
        self.assertEqual(ss.registration_fee, 450)
        self.assertEqual(ss.auth3d_notice, u"testing")
        self.assertEqual(ss.setting.order_limit, 20)
        self.assertEqual(ss.setting.max_quantity_per_user, 40)
        self.assertEqual(ss.setting.disp_orderreview, True)

    def test_update_sales_segment_use_owns(self):
        from datetime import datetime, time
        ssg = testing.DummyModel(
            id=1L,
            seat_choice=False,
            public=True,
            reporting=False,
            payment_delivery_method_pairs=[],
            start_day_prior_to_performance=14,
            start_time=time(10, 00),
            end_day_prior_to_performance=1,
            end_time=time(23, 59),
            max_quantity=10,
            order_limit=20,
            max_product_quatity=0,            
            account_id=1,
            margin_ratio=150,
            refund_ratio=250,
            printing_fee=350,
            registration_fee=450,
            auth3d_notice=u"testing",
            setting=testing.DummyModel(
                order_limit=120,
                max_quantity_per_user=43,
                disp_orderreview=False
                )
            )

        ss = testing.DummyModel(
            id=1L,
            sales_segment_group=ssg,
            use_default_seat_choice=False,
            use_default_public=False,
            use_default_reporting=False,
            use_default_payment_delivery_method_pairs=False,
            use_default_start_at=False,
            use_default_end_at=False,
            use_default_max_quantity=False,
            use_default_account_id=False,
            use_default_margin_ratio=False,
            use_default_refund_ratio=False,
            use_default_printing_fee=False,
            use_default_registration_fee=False,
            use_default_auth3d_notice=False, 
            use_default_max_product_quatity=False,           
            use_default_disp_orderreview=False,           
            seat_choice=True,
            public=False,
            reporting=True,
            payment_delivery_method_pairs=[testing.DummyModel()],
            start_at=datetime(2014, 10, 11, 12, 31),
            end_at=datetime(2014, 11, 11, 12, 31),
            max_quantity=110,
            account_id=10,
            margin_ratio=1150,
            refund_ratio=1250,
            printing_fee=1350,
            registration_fee=1450,
            auth3d_notice=u"testing-own",
            setting=testing.DummyModel(
                order_limit=120,
                max_quantity_per_user=43,
                disp_orderreview=True,
                use_default_order_limit=False,
                use_default_max_quantity_per_user=False,
                use_default_disp_orderreview=False
                )
            )

        target = self._makeOne()
        target.update_sales_segment(ss)
        
        self.assertTrue(ss.seat_choice)
        self.assertFalse(ss.public)
        self.assertTrue(ss.reporting)
        self.assertEqual(len(ss.payment_delivery_method_pairs), 1)
        self.assertEqual(ss.start_at, datetime(2014, 10, 11, 12, 31))
        self.assertEqual(ss.end_at, datetime(2014, 11, 11, 12, 31))
        self.assertEqual(ss.max_quantity, 110)
        self.assertEqual(ss.setting.order_limit, 120)
        self.assertEqual(ss.account_id, 10)
        self.assertEqual(ss.margin_ratio, 1150)
        self.assertEqual(ss.refund_ratio, 1250)
        self.assertEqual(ss.printing_fee, 1350)
        self.assertEqual(ss.registration_fee, 1450)
        self.assertEqual(ss.auth3d_notice, u"testing-own")
        self.assertEqual(ss.setting.order_limit, 120)
        self.assertEqual(ss.setting.max_quantity_per_user, 43)
        self.assertEqual(ss.setting.disp_orderreview, True)
