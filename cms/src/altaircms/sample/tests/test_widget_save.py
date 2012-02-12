import unittest
import altaircms.testutils as u


def setUpModule():
    global _session
    u.create_db()

def tearDownModule():
    u.dropall_db()

class ResourceImageWidgetTest(unittest.TestCase):
    def setUp(self):
        from altaircms.asset.models import ImageAsset
        imga = ImageAsset("/static/img/samples/Abstract_Desktop_290.jpg")
        self._getSession().add(imga)
        
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getResource(self):
        from altaircms.sample.api.resources import SampleResource
        return SampleResource(None)

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def test_find_asset_in_db(self):
        resource = self._getResource()
        asset = resource.get_image_asset_query().one()
        resource.get_image_asset(asset.id)

    def test_create_widget(self):
        resource = self._getResource()
        asset = resource.get_image_asset_query().one()
        widget = resource.get_image_widget(None)
        widget = resource.update_widget(widget, dict(asset_id=asset.id))
        resource.add(widget)

    def test_create_by_view(self):
        resource = self._getResource()
        asset = resource.get_image_asset_query().one()

        from altaircms.sample.api.views import ImageWidgetView
        class request(object):
            json_body=dict(data=dict(asset_id=asset.id))
            context = resource
        r = ImageWidgetView(request).update()
        self.assertNotEqual(r["pk"], None)





if __name__ == "__main__":
    unittest.main()

