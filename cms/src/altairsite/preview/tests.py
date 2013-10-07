from datetime import datetime 
import unittest 
import mock

class DummyRequest(object):
    def __init__(self, session):
        self.session = session

class PreviewTweenTests(unittest.TestCase):
    def _getTarget(self):
        from altairsite.preview.checking import PreviewPermission
        return PreviewPermission

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_can_preview__datetime_exists(self):
        from altair.now import session_key
        request = DummyRequest({session_key: "datetime-is-exists"})
        target = self._makeOne()
        self.assertTrue(target.can_preview(request))

    def test_cannot_preview__normal(self):
        request = DummyRequest({})
        target = self._makeOne()
        self.assertFalse(target.can_preview(request))

    @mock.patch("altairsite.preview.checking._fetch_accesskey")
    def test_does_not_have_permission__accesskey_not_found(self, f):
        f.return_value = None

        request = DummyRequest({"accesskey": "this-is-access-key"})
        target = self._makeOne()

        self.assertFalse(target.has_permission_accesskey(request, request.session))
        f.assert_called_onece_with("this-is-access-key")

    @mock.patch("altairsite.preview.checking._fetch_accesskey")
    @mock.patch("altairsite.preview.checking.get_organization_from_request")
    def test_does_not_have_permission__accesskey_missmatch_organization_id(self, m, f):
        f.return_value = type("_key", (object, ), {"organization_id": 2})
        m.return_value = type("_org", (object, ), {"id": 1})

        request = DummyRequest({"accesskey": "this-is-access-key"})
        target = self._makeOne()

        self.assertFalse(target.has_permission_accesskey(request, request.session))
        f.assert_called_onece_with("this-is-access-key")

    @mock.patch("altairsite.preview.checking._fetch_accesskey")
    @mock.patch("altairsite.preview.checking.get_organization_from_request")
    def test_does_not_have_permission__already_expired(self, m, f):
        f.return_value = type("_key", (object, ), {"organization_id": 1, "expiredate": datetime(1900, 1, 1)})
        m.return_value = type("_org", (object, ), {"id": 1})

        request = DummyRequest({"accesskey": "this-is-access-key"})
        target = self._makeOne()

        self.assertFalse(target.has_permission_accesskey(request, request.session))
        f.assert_called_onece_with("this-is-access-key")

    @mock.patch("altairsite.preview.checking._fetch_accesskey")
    @mock.patch("altairsite.preview.checking.get_organization_from_request")
    def test_it(self, m, f):
        f.return_value = type("_key", (object, ), {"organization_id": 1, "expiredate": None})
        m.return_value = type("_org", (object, ), {"id": 1})

        request = DummyRequest({"accesskey": "this-is-access-key"})
        target = self._makeOne()

        self.assertTrue(target.has_permission_accesskey(request, request.session))
        f.assert_called_onece_with("this-is-access-key")

    ## scope
    @unittest.skip ("* #5609: must fix")
    @mock.patch("altairsite.preview.checking._fetch_accesskey")
    @mock.patch("altairsite.preview.checking.get_organization_from_request")
    def test_does_not_have_permission__over_the_scope(self, m, f):
        from altairsite.preview.api import set_rendered_event
        f.return_value = type("_key", (object, ), {"organization_id": 1, "expiredate": None, "event_id": 10, "scope": "onepage"})
        m.return_value = type("_org", (object, ), {"id": 1})

        request = DummyRequest({"accesskey": "this-is-access-key"})
        set_rendered_event(request, type("_event", (object, ), {"id": 1, "title": "missing-event"}))
        target = self._makeOne()

        self.assertFalse(target.has_permission_accesskey(request, request.session))
        f.assert_called_onece_with("this-is-access-key")

    @unittest.skip ("* #5609: must fix")
    @mock.patch("altairsite.preview.checking._fetch_accesskey")
    @mock.patch("altairsite.preview.checking.get_organization_from_request")
    def test_have_permission__inner_the_scope(self, m, f):
        from altairsite.preview.api import set_rendered_event
        _event_id  = 10
        f.return_value = type("_key", (object, ), {"organization_id": 1, "expiredate": None, "event_id": _event_id, "scope": "onepage"})
        m.return_value = type("_org", (object, ), {"id": 1})

        request = DummyRequest({"accesskey": "this-is-access-key"})
        set_rendered_event(request, type("_event", (object, ), {"id": _event_id, "title": "event"}))
        target = self._makeOne()

        self.assertTrue(target.has_permission_accesskey(request, request.session))
        f.assert_called_onece_with("this-is-access-key")
        


if __name__ == "__main__":
    unittest.main()
