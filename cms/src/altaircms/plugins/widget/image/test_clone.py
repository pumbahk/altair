# -*- coding:utf-8 -*-

import unittest
from altaircms.models import DBSession
from altaircms.models import Base
from models import ImageWidget

def setUpModule():
    DBSession.remove()
    from altaircms.testutils import create_db
    create_db(base=Base, session=DBSession)

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db(base=Base, session=DBSession)

class WidgetCloneTest(unittest.TestCase):
    """ widgetのcloneのテスト
    """
    def _makeAsset(self, id=None):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.from_dict({"id": id, "filepath": "test.jpg"})

    def setUp(self):
        self._getSession().remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        return DBSession

    def _makeOne(self, **kwargs):
        w = ImageWidget.from_dict(kwargs)
        self._getSession().add(w)
        return w

    def test_not_clone(self):
        asset = self._makeAsset(id=1)
        self._makeOne(memo="memo", asset=asset)

        self.assertEquals(ImageWidget.query.count(), 1)

    def _makePage(self):
        from altaircms.page.models import Page
        return Page()

    def test_it(self):
        asset = self._makeAsset(id=1)
        iw = self._makeOne(memo="memo", asset=asset)

        session = self._getSession()
        session.add(iw.clone(session, page=self._makePage()))

        self.assertEquals(ImageWidget.query.count(), 2)

if __name__ == "__main__":
    unittest.main()
