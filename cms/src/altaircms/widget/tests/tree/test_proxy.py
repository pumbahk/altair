import json
import unittest

from altaircms.widget.tests import models
Base = models.Base
DBSession = models.DBSession
DummyWidget = models.DummyWidget

def setUpModule():
    from altaircms.testutils import create_db
    create_db(base=Base, session=DBSession)

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db(base=Base, session=DBSession)
        
class WidgetTreeProxyTest(unittest.TestCase):
    def _getPage(self):
        class page(object):
            structure = json.dumps(
                {"header": [{"name": "dummy_widget",  "pk": 1}]
                 })
        return page

    def setUp(self):
        self._getSession().remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        return DBSession

    def _getTarget(self):
        from altaircms.widgetmodels import WidgetFetcher
        return WidgetFetcher()

    def test_make_it(self):
        page = self._getPage()
        from altaircms.widget.tree.proxy import WidgetTreeProxy
        WidgetTreeProxy(page)

    def test_has_block(self):
        session = self._getSession()
        iw = DummyWidget(id=1, asset_id=10)
        session.add(iw)

        page = self._getPage()
        from altaircms.widget.tree.proxy import WidgetTreeProxy
        self.assertTrue(WidgetTreeProxy(page, session=session).blocks)

    def test_has_block_has_collect_member(self):
        session = self._getSession()
        iw = DummyWidget(id=1, asset_id=10)
        session.add(iw)

        page = self._getPage()
        from altaircms.widget.tree.proxy import WidgetTreeProxy
        blocks = WidgetTreeProxy(page, session=session).blocks
        self.assertEquals([o.asset_id for o in blocks["header"]], [10])

if __name__ == "__main__":
    unittest.main()
