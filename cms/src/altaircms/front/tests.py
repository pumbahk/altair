import unittest
from pyramid import testing

class DummyOrganization(object):
    def __init__(self, id=None):
        self.id = id

class DummyAccesskey(object):
    def __init__(self, name, valid_status):
        self.name = name
        self.valid_status = valid_status
        self.hashkey = "@@@"
        self.expiredate = "@@"

class DummyPage(object):
    def __init__(self, access_key=None, 
                 organization_id=None, 
                 valid_layout_status=True):
        self.access_key = access_key
        self.organization_id = organization_id
        self.valid_layout_status = valid_layout_status
        self._called = []

    def get_access_key(self, request):
        return self.access_key

    def can_private_access(self, key=None):
        self._called.append("can_private_access")
        return self.access_key.valid_status

    def valid_layout(self):
        self._called.append("valid_layout")
        if not self.valid_layout_status:
            raise ValueError("@@")
        return self.valid_layout_status

class FrontAccessControlTests(unittest.TestCase):
    def _getTarget(self, *args):
        from altaircms.front.resources import AccessControl
        return AccessControl

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_login_same_organization_can_access(self):
        organization_id = 1
        request = testing.DummyRequest(organization=DummyOrganization(organization_id))

        page = DummyPage(organization_id=organization_id)

        target = self._makeOne(request)
        target.access_ok = True

        target._check_page_is_accessable(page, None)

        self.assertTrue(target.can_access())        
        self.assertEquals(page._called, ["valid_layout"])
        # print target.error_message


    def test_login_other_organization_cant_access(self):
        organization_id = 1
        another_organization_id = 1111111
        request = testing.DummyRequest(organization=DummyOrganization(another_organization_id))

        page = DummyPage(organization_id=organization_id)

        target = self._makeOne(request)
        target.access_ok = True
        target._check_page_is_accessable(page, None)

        self.assertFalse(target.can_access())        
        self.assertEquals(page._called, [])
        # print target.error_message

    def test_not_login_cant_access(self):
        organization_id = 1
        request = testing.DummyRequest(organization=None)

        page = DummyPage(organization_id=organization_id)

        target = self._makeOne(request)
        target.access_ok = True
        target._check_page_is_accessable(page, None)

        self.assertFalse(target.can_access())        
        self.assertEquals(page._called, [])
        # print target.error_message        

    def test_not_login_with_valid_access_key_can_access(self):
        organization_id = 1
        request = testing.DummyRequest(organization=None)

        page = DummyPage(organization_id=organization_id, 
                         access_key = DummyAccesskey("this-is-valid-access-key", True))

        target = self._makeOne(request)
        target.access_ok = True
        target._check_page_is_accessable(page, None)

        self.assertTrue(target.can_access())        
        self.assertEquals(page._called, ["can_private_access", "valid_layout"])
        # print target.error_message

    def test_not_login_with_invalid_access_key_can_access(self):
        organization_id = 1
        request = testing.DummyRequest(organization=None)

        page = DummyPage(organization_id=organization_id, 
                         access_key = DummyAccesskey("this-is-invalid-access-key-EVERYTIME-FAIL!", False))

        target = self._makeOne(request)
        target.access_ok = True
        target._check_page_is_accessable(page, None)

        self.assertFalse(target.can_access())        
        self.assertEquals(page._called, ["can_private_access"])
        # print target.error_message        

    def test_login_rendering_with_invalid_lalyout_cant_access(self):
        organization_id = 1
        request = testing.DummyRequest(organization=DummyOrganization(organization_id))

        page = DummyPage(organization_id=organization_id, 
                         valid_layout_status=False)

        target = self._makeOne(request)
        target.access_ok = True

        target._check_page_is_accessable(page, None)

        self.assertFalse(target.can_access())        
        self.assertEquals(page._called, ["valid_layout"])
        # print target.error_message

if __name__ == "__main__":
    unittest.main()

