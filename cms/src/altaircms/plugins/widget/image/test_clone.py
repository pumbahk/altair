# -*- coding:utf-8 -*-

##
#NoDB
from altaircms.models import DBSession

import unittest
from models import ImageWidget

config  = None
def setUpModule():
    global config
    from altaircms.lib import testutils
    testutils.create_db(force=False)
    config = testutils.config()

def tearDownModule():
    from pyramid.testing import tearDown
    tearDown()

class WidgetCloneTest(unittest.TestCase):
    """ widgetのcloneのテスト
    """
    def _makeAsset(self, id=None):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.from_dict({"id": id, "filepath": "test.jpg"})

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
        from altaircms.widget.models import Widget
        self.assertEquals(Widget.query.count(), 2)

if __name__ == "__main__":
    unittest.main()
