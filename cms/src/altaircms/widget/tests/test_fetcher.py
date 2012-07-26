import unittest

import models
Base = models.Base
DBSession = models.DBSession
DummyWidget = models.DummyWidget

def setUpModule():
    DBSession.remove()
    from altaircms.testing import create_db
    create_db(base=Base, session=DBSession)

def tearDownModule():
    from altaircms.testing import dropall_db
    dropall_db(base=Base, session=DBSession)

class WidgetFetcherTest(unittest.TestCase):
    def setUp(self):
        self._getSession().remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        return DBSession

    def _getTarget(self, session):
        from altaircms.widget.fetcher import WidgetFetcher
        return WidgetFetcher(session=session)

    def test_dummy_widget(self):
        session = self._getSession()
        iw = DummyWidget(id=1, asset_id=1)
        session.add(iw)
        
        fetcher = self._getTarget(session)
        self.assertEquals(fetcher.fetch("dummy_widget", [1]).one().asset_id, 1)
        self.assertEquals(fetcher.dummy_widget([1]).one().asset_id, 1)

    def test_not_found_widget(self):
        session = self._getSession()
        iw = DummyWidget(id=1, asset_id=1)
        session.add(iw)
        
        fetcher = self._getTarget(session)
        from altaircms.widget.fetcher import WidgetFetchException
        self.assertRaises(WidgetFetchException, 
            lambda : fetcher.fetch("not_found_widget", [1]).one().asset_id)

if __name__ == "__main__":
    unittest.main()
