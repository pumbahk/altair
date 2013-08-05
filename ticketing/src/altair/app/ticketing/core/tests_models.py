import unittest


class SalesSegmentTests(unittest.TestCase):
    def _getTarget(self):
        from .models import SalesSegment
        return SalesSegment

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_auth3d_notice_setter(self):
        target = self._makeOne(auth3d_notice=u"aa")
        self.assertEqual(target.auth3d_notice, u"aa")
        self.assertEqual(target.x_auth3d_notice, u"aa")

    def test_auth3d_notice_without_acquire(self):
        from .models import SalesSegmentGroup
        target = self._makeOne(auth3d_notice=u"aa",
                               sales_segment_group=SalesSegmentGroup(auth3d_notice=u"bb"))
        self.assertEqual(target.auth3d_notice, u"aa")
        self.assertEqual(target.x_auth3d_notice, u"aa")

    def test_auth3d_notice_acquire(self):
        from .models import SalesSegmentGroup
        target = self._makeOne(auth3d_notice=None,
                               sales_segment_group=SalesSegmentGroup(auth3d_notice=u"bb"))
        self.assertEqual(target.auth3d_notice, u"bb")
        self.assertIsNone(target.x_auth3d_notice)
