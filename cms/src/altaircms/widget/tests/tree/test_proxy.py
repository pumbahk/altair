import json
import unittest

from altaircms.widget.tests import models
Base = models.Base
DBSession = models.DBSession
DummyWidget = models.DummyWidget

def setUpModule():
    from altaircms.testing import setup_db
    setup_db(base=Base, session=DBSession)

def tearDownModule():
    from altaircms.testing import teardown_db
    teardown_db(base=Base, session=DBSession)


class DataCleansingTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.widget.tree.proxy import page_structure_as_dict
        return page_structure_as_dict(*args, **kwargs)

    def test_simple(self):
        target = json.dumps({"main": [{"name": "image",  "pk": 1}]})
        result = self._callFUT(target)
        self.assertEquals(result["main"], [{"name": "image",  "pk": 1}])

    def test_invalid1(self):
        target = json.dumps({"main": [{"name": "image",  "pk": 1}, {"name": "dummy"}]})
        result = self._callFUT(target)
        self.assertEquals(result["main"], [{"name": "image",  "pk": 1}])

    def test_invalid2(self):
        target = json.dumps({"main": [{"name": "image",  "pk": 1}, {"name": "dummy", "pk": None}]})
        result = self._callFUT(target)
        self.assertEquals(result["main"], [{"name": "image",  "pk": 1}])

        
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
