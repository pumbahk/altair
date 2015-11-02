import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid import testing
    

class CreateLoginUserTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.members.builder import UserForLoginCartBuilder
        return UserForLoginCartBuilder

    def setUp(self):
        self.session = _setup_db(modules=["altair.app.ticketing.users.models", 
                           "altair.app.ticketing.core.models",
                           "altair.app.ticketing.cart.models",
                           "altair.app.ticketing.orders.models"])
        from altair.app.ticketing.users.models import Membership
        self.membership = Membership(id=1)
        self.session.add(self.membership)
        self.session.flush() 

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()
        _teardown_db()

    def dummy_request(self):
        mdict = dict(membership_id=self.membership.id)
        return testing.DummyRequest(matchdict=mdict)

    def create_membergroup(self, id=None, membership_id=None, name=None):
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.users.models import MemberGroup
        import transaction   
        self.session.add(MemberGroup(id=id, name=name, membership_id=membership_id))
        self.session.flush()
        
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_create_user_and_membergroup(self):
        target = self._makeOne(self.dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result = target.build_member_for_login_cart(membergroup_name, loginname, password)

        self.assertEquals(result.membergroup.name, "gold")
        self.assertEquals(result.auth_identifier, "foo")
        self.assertEquals(result.auth_secret, "this-is-password")

    def test_create_user_with_exist_membergroup(self):
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        self.create_membergroup(id=1000, membership_id=self.membership.id, name=membergroup_name)

        target = self._makeOne(self.dummy_request())
        result = target.build_member_for_login_cart(membergroup_name, loginname, password)

        self.assertEquals(result.membergroup.name, "gold")
        self.assertEquals(result.membergroup.id, 1000)
        self.assertEquals(result.auth_identifier, "foo")
        self.assertEquals(result.auth_secret, "this-is-password")

    def test_duplicated_data(self):
        target = self._makeOne(self.dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result0 = target.build_member_for_login_cart_add_session(membergroup_name, loginname, password)
        self.session.add(result0)
        self.session.flush()
        self.assertEquals(result0.membergroup.name, "gold")
        self.assertEquals(result0.auth_identifier, "foo")
        self.assertEquals(result0.auth_secret, "this-is-password")
        result1 = target.build_member_for_login_cart_add_session(membergroup_name, loginname, password)
        self.assertEquals(result0, result1)

    def test_overwrite_password(self):
        target = self._makeOne(self.dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result0 = target.build_member_for_login_cart_add_session(membergroup_name, loginname, password)
        result1 = target.build_member_for_login_cart_add_session(membergroup_name, loginname, "overwrite-password")

        self.assertEquals(result1.membergroup.name, "gold")
        self.assertEquals(result1.auth_identifier, "foo")
        self.assertEquals(result1.auth_secret, "overwrite-password")

        self.assertEquals(result0, result1)


    def test_overwrite_membergroup(self):
        target = self._makeOne(self.dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result0 = target.build_member_for_login_cart_add_session(membergroup_name, loginname, password)
        self.session.add(result0)
        self.session.flush()
        result1 = target.build_member_for_login_cart_add_session("silver", loginname, password)

        self.assertEquals(result1.membergroup.name, "silver")
        self.assertEquals(result1.auth_identifier, "foo")
        self.assertEquals(result1.auth_secret, "this-is-password")

        self.assertEquals(result0, result1)        


if __name__ == "__main__":
    unittest.main()
