import unittest
from ticketing.testing import _setup_db, _teardown_db
from pyramid import testing
def setUpModule():
    _setup_db(modules=["ticketing.users.models", 
                       "ticketing.core.models"])

def tearDownModule():
    _teardown_db()

def dummy_request(membership_id=1):
    mdict = dict(membership_id=membership_id)
    return testing.DummyRequest(matchdict=mdict)

def create_membergroup(id=None, membership_id=None, name=None):
    from ticketing.models import DBSession
    from ticketing.users.models import MemberGroup
    import transaction   
    DBSession.add(MemberGroup(id=id, name=name, membership_id=membership_id))
    transaction.commit()
    
def delete_membergroups():
    from ticketing.models import DBSession
    from ticketing.users.models import MemberGroup
    import transaction

    DBSession.remove()
    for mg in MemberGroup.query:
        DBSession.delete(mg)
    transaction.commit()
    

class CreateLoginUserTests(unittest.TestCase):
    def _getTarget(self):
        from ticketing.members.api import UserForLoginCartBuilder
        return UserForLoginCartBuilder

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_create_user_and_membergroup(self):
        target = self._makeOne(dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result = target.build_user_for_login_cart(membergroup_name, loginname, password)

        self.assertEquals(result.member.membergroup.name, "gold")
        self.assertEquals(result.first_user_credential.auth_identifier, "foo")
        self.assertEquals(result.first_user_credential.auth_secret, "this-is-password")

    def test_create_user_with_exist_membergroup(self):
        membership_id = 1

        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        create_membergroup(id=1000, membership_id=membership_id, name=membergroup_name)

        target = self._makeOne(dummy_request(membership_id=membership_id))
        result = target.build_user_for_login_cart(membergroup_name, loginname, password)

        self.assertEquals(result.member.membergroup.name, "gold")
        self.assertEquals(result.member.membergroup.id, 1000)
        self.assertEquals(result.first_user_credential.auth_identifier, "foo")
        self.assertEquals(result.first_user_credential.auth_secret, "this-is-password")

        delete_membergroups()

    def test_duplicated_data(self):
        target = self._makeOne(dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result0 = target.build_user_for_login_cart_add_session(membergroup_name, loginname, password)
        result1 = target.build_user_for_login_cart_add_session(membergroup_name, loginname, password)

        self.assertEquals(result0.member.membergroup.name, "gold")
        self.assertEquals(result0.first_user_credential.auth_identifier, "foo")
        self.assertEquals(result0.first_user_credential.auth_secret, "this-is-password")

        self.assertEquals(result0, result1)

    def test_overwrite_password(self):
        target = self._makeOne(dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result0 = target.build_user_for_login_cart_add_session(membergroup_name, loginname, password)
        result1 = target.build_user_for_login_cart_add_session(membergroup_name, loginname, "overwrite-password")

        self.assertEquals(result1.member.membergroup.name, "gold")
        self.assertEquals(result1.first_user_credential.auth_identifier, "foo")
        self.assertEquals(result1.first_user_credential.auth_secret, "overwrite-password")

        self.assertEquals(result0, result1)


    def test_overwrite_membergroup(self):
        target = self._makeOne(dummy_request())
        membergroup_name = "gold"
        loginname = "foo"
        password = "this-is-password"

        result0 = target.build_user_for_login_cart_add_session(membergroup_name, loginname, password)
        result1 = target.build_user_for_login_cart_add_session("silver", loginname, password)

        self.assertEquals(result1.member.membergroup.name, "silver")
        self.assertEquals(result1.first_user_credential.auth_identifier, "foo")
        self.assertEquals(result1.first_user_credential.auth_secret, "this-is-password")

        self.assertEquals(result0, result1)        


if __name__ == "__main__":
    unittest.main()
