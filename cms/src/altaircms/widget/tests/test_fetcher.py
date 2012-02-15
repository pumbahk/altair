import unittest

def setUpModule():
    from altaircms.testutils import create_db
    create_db()

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db()

class WidgetFetcherTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _getTarget(self):
        from altaircms.widget.models import WidgetFetcher
        return WidgetFetcher()

    def test_image_widget(self):
        session = self._getSession()
        from altaircms.models import ImageWidget
        iw = ImageWidget(id=1, asset_id=1)
        session.add(iw)
        
        fetcher = self._getTarget()
        self.assertEquals(fetcher.fetch("image_widget", [1]).one().asset_id, 1)
        self.assertEquals(fetcher.image_widget([1]).one().asset_id, 1)

    def test_not_found_widget(self):
        session = self._getSession()
        from altaircms.models import ImageWidget
        iw = ImageWidget(id=1, asset_id=1)
        session.add(iw)
        
        fetcher = self._getTarget()
        from altaircms.widget.models import WidgetFetchException
        self.assertRaises(WidgetFetchException, 
            lambda : fetcher.fetch("not_found_widget", [1]).one().asset_id)

if __name__ == "__main__":
    unittest.main()
