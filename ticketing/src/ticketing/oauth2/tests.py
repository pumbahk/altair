# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.oauth2.authorize import Authorizer
from ticketing.oauth2.models import Service, AccessToken
from ticketing.oauth2.models import TimestampGenerator
from ticketing.operators.models import Operator, Permission, OperatorRole
from ticketing.master.models import Bank, BankAccount

from fixture import DataSet

from ticketing.seed.operator import *
from ticketing.seed.service import *
from ticketing.seed.permission import *
from ticketing.seed.organization import *
from ticketing.seed.user import *
from ticketing.seed.bank import *

class AuthorizerTest(unittest.TestCase):

    def _getTarget(self):
        import webapi
        return webapi.DummyServer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        import sqlahelper
        from sqlalchemy import create_engine
        from fixture import SQLAlchemyFixture

        engine = create_engine("sqlite:///")
        sqlahelper.get_session().remove()
        sqlahelper.add_engine(engine)
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

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
            engine=engine
        )
        data = db_fixture.data(
            ServiceData,
            PermissionData,
            OrganizationData,
            UserData,
            OperatorData,
            BankAccountData,
            BankData
        )
        data.setup()

    def tearDown(self):
        pass

    def test_time_generator(self):
        from .models import TimestampGenerator

        time = TimestampGenerator()
        assert time is datetime

    def test_access_token_get(self):
        from .models import AccessToken
        access_token = AccessToken()
        access_token.service = Service.get(1)
        access_token.operator = Operator.get(1)
        DBSession.add(access_token)
        DBSession.flush()

        access_token = AccessToken.get(1)

        assert access_token.key is not None
        assert access_token.token is not None
        assert access_token.refresh_token is not None
        assert access_token.mac_key is not None
        assert access_token.issue is not None
        assert access_token.expire is not None
        assert access_token.refreshable is not None

    def test_access_token_get_by_key(self):

        access_token = AccessToken()
        access_token.key = 'KEY_TEST'
        access_token.service = Service.get(1)
        access_token.operator = Operator.get(1)
        DBSession.add(access_token)
        DBSession.flush()

        access_token = AccessToken.get_by_key("KEY_TEST")

        assert access_token.key is not None
        assert access_token.token is not None
        assert access_token.refresh_token is not None
        assert access_token.mac_key is not None
        assert access_token.issue is not None
        assert access_token.expire is not None
        assert access_token.refreshable is not None

    def test_auth(self):
        import sqlahelper
        DBSession = sqlahelper.get_session()

        from .models import Service

        from webob.multidict import MultiDict

        class DummyContext():
            user = Operator.get(1)
        class DummyRequest():
            params = MultiDict()

        request=DummyRequest()

        request.params.add('response_type'  ,'code')
        request.params.add('client_id'      ,'fa12a58972626f0597c2faee1454e1')
        request.params.add('redirect_uri'   ,'http://127.0.0.1:6543/auth/oauth_callback')
        request.params.add('scope'          ,'administrator')
        request.params.add('state'          ,'')

        context = DummyContext()

        authorizer = Authorizer()
        authorizer.validate(request, context)
        redirect_url = authorizer.grant_redirect()

