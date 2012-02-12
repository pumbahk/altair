import unittest
from pyramid import testing
import altaircms.testutils as u


def setUpModule():
    u.create_db()

def tearDownModule():
    u.dropall_db()

class ResourceImageAssetTest(unittest.TestCase):
    # def setUp(self):
    #     self.config = testing.setUp()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.sample.resources import UsingAssetMixin
        return UsingAssetMixin.m.ImageAsset

    def _getResource(self):
        from altaircms.sample.resources import UsingAssetMixin
        return UsingAssetMixin()
        
    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession


    def _makeOne(self, *args, **kwargs):
        target = self._getTarget()(None)
        for k, v in kwargs.items():
            setattr(target, k, v)
        return target

    def test_it(self):
        target = self._makeOne()

    def test_create(self):
        target = self._makeOne(filepath="foo/bar.jpg")
        
    def test_find(self):
        target = self._makeOne(filepath="foo/bar.jpg")

        session = self._getSession()
        session.add(target)
        query = self._getResource().get_image_asset_query()
        self.assertEqual(len(query.all()), 1)

class ResourceCreatePageTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()


    def _getResource(self):
        from altaircms.sample.core.resources import SampleCoreResource
        return SampleCoreResource(None)

    def test_create_page(self):
        context = self._getResource()
        params = {'description': u'boo',
                  'keyword': u'oo',
                  'tags': u'ooo',
                  'url': u'hohohoho',
                  'layout_id': 1,
                  'title': u'boo',
                  'structure': u'{}'
                  }
        page = context.create_page(params)        
        context.add(page)
        context.show()
        print context.get()[0].id

class ResourceLayoutTest(unittest.TestCase):
    # def setUp(self):
    #     self.config = testing.setUp()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.sample.resources import UsingLayoutMixin
        return UsingLayoutMixin.m.Layout

    def _getResource(self):
        from altaircms.sample.resources import UsingLayoutMixin
        return UsingLayoutMixin()
        
    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeOne(self, *args, **kwargs):
        target = self._getTarget()()
        for k, v in kwargs.items():
            setattr(target, k, v)
        return target

    def test_it(self):
        target = self._makeOne()

    def test_get(self):
        target = self._makeOne(title="col2", template_filename="foo/col2.css",
                               site_id=1, client_id=1)
        
        session = self._getSession()
        session.add(target)
        layout = self._getResource().get_layout_template("col2")
        self.assertTrue(layout)
        self.assertEqual(layout.title, "col2")
        
if __name__ == "__main__":
    unittest.main()
