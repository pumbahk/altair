import unittest
from pyramid import testing


class SalesSegmentGroupUpdateTests(unittest.TestCase):

    def _getTarget(self):
        from ..resources import SalesSegmentGroupUpdate
        return SalesSegmentGroupUpdate

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_update_sales_segment_use_defaults(self):
        from datetime import datetime
        ssg = testing.DummyModel(
            seat_choice=False,
            public=True,
            reporting=False,
            payment_delivery_method_pairs=[],
            start_at=datetime(2013, 10, 11, 12, 31),
            end_at=datetime(2013, 11, 11, 12, 31),
            upper_limit=10,
            order_limit=20,
            account_id=1,
            margin_ratio=150,
            refund_ratio=250,
            printing_fee=350,
            registration_fee=450,
            auth3d_notice=u"testing",
        )
        target = self._makeOne(ssg)

        ss = testing.DummyModel(
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

        target.update_sales_segment(ss)

    def test_update_sales_segment_use_owns(self):
        from datetime import datetime
        ssg = testing.DummyModel(
            seat_choice=False,
            public=True,
            reporting=False,
            payment_delivery_method_pairs=[],
            start_at=datetime(2013, 10, 11, 12, 31),
            end_at=datetime(2013, 11, 11, 12, 31),
            upper_limit=10,
            order_limit=20,
            account_id=1,
            margin_ratio=150,
            refund_ratio=250,
            printing_fee=350,
            registration_fee=450,
            auth3d_notice=u"testing",
        )
        target = self._makeOne(ssg)

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

        target.update_sales_segment(ss)
