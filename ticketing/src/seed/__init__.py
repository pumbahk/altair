# -*- coding: utf-8 -*-

import fixture
from fixture import DataSet
from fixture import SQLAlchemyFixture

import sqlalchemy as sa
from sqlalchemy.orm import *
from datetime import datetime
from hashlib import md5

from ticketing.models import *
from ticketing.models.boxoffice import *

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass

engine = sa.create_engine('mysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8', echo=True)
sqlahelper.add_engine(engine)

from seed.bank import BankData, BankAccountData
from seed.prefecture import PrefectureMaster

class ClientData(DataSet):
    class ticketstar:
        name            = u'チケットスター'
        client_type     = ClientTypeEnum.Standard.v
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class client_1:
        name            = u'クライアント1'
        client_type     = ClientTypeEnum.Standard.v
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class client_2:
        name            = u'クライアント2'
        client_type     = ClientTypeEnum.Standard.v
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class client_3:
        name            = u'クライアント3'
        client_type     = ClientTypeEnum.Standard.v
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class client_4:
        name            = u'クライアント4'
        client_type     = ClientTypeEnum.Standard.v
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class client_5:
        name            = u'クライアント5'
        client_type     = ClientTypeEnum.Standard.v
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1

class PermissionData(DataSet):
    class permission_cms:
        category_name = 'cms'
        permit = 1
    class permission_backend:
        category_name = 'backend'
        permit = 1
    class permission_admin:
        category_name = 'admin'
        permit = 1

class OperatorRoleData(DataSet):
    class role_admin_admin:
        name = 'admin'
        permissions = [
            PermissionData.permission_cms,
            PermissionData.permission_backend,
            PermissionData.permission_admin
        ]
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class role_admin_superuser:
        name = 'super'
        permissions = [
            PermissionData.permission_cms,
            PermissionData.permission_backend
        ]
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class role_admin_backend_staff:
        name = 'staff_backend_staff'
        permissions = [
            PermissionData.permission_backend
        ]
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class role_admin_cms_staff:
        name = 'staff_cms'
        permissions = [
            PermissionData.permission_cms
        ]
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class TicketerData(DataSet):
    class ticketstar:
        name            = u'チケットスター'
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
        bank_account    = BankAccountData.bank_account_1

    class ticketer_1:
        name            = u'プロモーター1'
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
        bank_account    = BankAccountData.bank_account_1
    class ticketer_2:
        name            = u'プロモーター2'
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
        bank_account    = BankAccountData.bank_account_1
    class ticketer_3:
        name            = u'プロモーター3'
        prefecture      = PrefectureMaster.tokyo
        city            = u"品川区"
        address         = u"東五反田"
        street          = u"1-1-1"
        other_address   = u"XXXビル1F"
        tel_1           = u'00-0000-0000'
        tel_2           = u'00-0000-0000'
        fax             = u'00-0000-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
        bank_account    = BankAccountData.bank_account_1

class AccountData(DataSet):
    class ticketstar:
        account_type    = AccountTypeEnum.Playguide.v
        user            = None
        ticketer        = TicketerData.ticketstar
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_1:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        ticketer        = TicketerData.ticketer_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_2:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        ticketer        = TicketerData.ticketer_2
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_3:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        ticketer        = TicketerData.ticketer_3
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1

class OperatorData(DataSet):
    class operator_1:
        name = 'オペレーター1'
        email = 'test1@test.com'
        client_id = 1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
        login_id = 'test'
        password =  md5('testtest').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'
    class operator_2:
        name = 'オペレーター2'
        email = 'tes2t@test.com'
        client_id = 1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
        login_id = 'testtest'
        password =  md5('test').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'


db_fixture = SQLAlchemyFixture(
     env={
         'PrefectureMaster' : Prefecture,
         'PermissionData' : Permission,
         'OperatorRoleData' : OperatorRole,
         'OperatorData' : Operator,
         'BankData': Bank,
         'BankAccountData' : BankAccount,
         'AccountData' : Account,
         'TicketerData' : Ticketer,
         'ClientData' : Client,
     },
     engine=engine,
     )

metadata = Base.metadata
metadata.bind = engine
metadata.drop_all()

metadata.create_all()



data = db_fixture.data(
    PrefectureMaster,
    PermissionData,
    BankData,
    BankAccountData,
    OperatorRoleData,
    AccountData,
    TicketerData,
    ClientData,
    OperatorRoleData,
    OperatorData,

)
data.setup()

