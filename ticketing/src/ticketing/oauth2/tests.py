# -*- coding:utf-8 -*-
import unittest
import datetime
from pyramid import testing

from ticketing.oauth2.authorize import Authorizer

from sqlalchemy import create_engine
from fixture import SQLAlchemyFixture


import sqlahelper

def _setup_db():
    import sqlahelper
    from sqlalchemy import create_engine

    from ticketing.operators.models import Operator, Permission, OperatorRole
    from ticketing.core.models import Organization, User
    from ticketing.oauth2.models import Service, AccessToken
    from ticketing.master.models import Bank, BankAccount

    engine = create_engine("sqlite:///")
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    return sqlahelper.get_session()

def _teardown_db():
    import transaction
    transaction.abort()

def setup_database():

    from ticketing.operators.models import Operator, Permission, OperatorRole
    from ticketing.core.models import Organization, User
    from ticketing.oauth2.models import Service, AccessToken
    from ticketing.master.models import Bank, BankAccount

    Base = sqlahelper.get_base()

    Base.metadata.create_all(sqlahelper.get_engine())

    from ticketing.seed.operator import OperatorData, OperatorRoleData
    from ticketing.seed.service import ServiceData
    from ticketing.seed.permission import PermissionData
    from ticketing.seed.organization import OrganizationData
    from ticketing.seed.user import UserData
    from ticketing.seed.bank import BankAccountData, BankData

    db_fixture = SQLAlchemyFixture(
         env={
             'ServiceData'            : Service,
             'PermissionData'         : Permission,
             'OperatorData'           : Operator,
             'OperatorRoleData'       : OperatorRole,
             'OrganizationData'       : Organization,
             'UserData'               : User,
             'BankAccountData'        : BankAccount,
             'BankData'               : Bank,

        },
        engine=sqlahelper.get_engine()
    )

    data = db_fixture.data(
        ServiceData,
        PermissionData, OperatorData, OperatorRoleData,
        OrganizationData,UserData,BankAccountData,BankData)
    data.setup()


class AccessTokenTest(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db()
        setup_database()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _getTarget(self):
        import webapi
        return webapi.DummyServer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_auth(self):

        from pyramid.httpexceptions import HTTPFound
        from ticketing.operators.models import Operator
        from .models import Service

        from webob.multidict import MultiDict

        class DummyContext():
            user = Operator.query.get(1)
        class DummyRequest():
            params = MultiDict()

        request=DummyRequest()

        request.params.add('response_type'  ,'code')
        request.params.add('client_id'      ,'fa12a58972626f0597c2faee1454e1')
        request.params.add('redirect_uri'   ,'http://127.0.0.1:6543/auth/oauth_callback')
        request.params.add('scope'          ,'administrator')
        #request.params.add('state'          ,'')

        context = DummyContext()

        authorizer = Authorizer()
        authorizer.validate(request, context)
        http_found = authorizer.grant_redirect()

        assert type(http_found) is HTTPFound
        redirect_url = getattr(http_found, 'location')
        assert redirect_url.find('http://127.0.0.1:6543/auth/oauth_callback&code=')
        code = redirect_url[len('http://127.0.0.1:6543/auth/oauth_callback&code='):]
        from ticketing.oauth2.models import AccessToken
        assert AccessToken.filter(AccessToken.key==code).count()



class AuthorizerTest_TimeGenerator(unittest.TestCase):

    def test_time_generator(self):
        from .models import TimestampGenerator
        time_generator = TimestampGenerator()
        time = time_generator()
        assert type(time) is datetime.datetime