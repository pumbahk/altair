# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

class PromotionTagSearchTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.topic.models import Promotion
        return Promotion

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        """ tag: tag0, tag1, tag2
        """
        from altaircms.models import DBSession
        target = self._makeOne(publish_open_on=datetime(10, 10, 10))
        target.update_tag(u"tag1, tag2, tag3")
        DBSession.add(target)
        
        from altaircms.topic.models import PromotionTag
        self.assertEqual(PromotionTag.query.count(), 3)

        result = self._getTarget().matched_qs(d=datetime(1900, 1, 1), tag=u"tag1").first()
        DBSession.flush()
        self.assertEquals(result.id, target.id)


if __name__ == "__main__":
    from altaircms.topic.tests import setUpModule as S
    S()
    unittest.main()
