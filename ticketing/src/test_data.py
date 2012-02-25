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

from ticketing.models.boxoffice import *

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass

engine = sa.create_engine('mysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8', echo=True)
initialize_sql(engine)
sqlahelper.add_engine(engine)

class BankData(DataSet):
    class bank_1:
        code = '00001'
        name = u'テスト銀行'

class BankAccountData(DataSet):
    class bank_account_1:
        bank = BankData.bank_1
        account_type = 2
        account_number = u'1234567890'
        account_owner = u'Test Test'
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class bank_account_2:
        bank = BankData.bank_1
        account_type = 2
        account_number = u'1234567890'
        account_owner = u'Test Test2'
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class ClientData(DataSet):
    class client_1:
        contract_type = 1
        name = u'Test Client'
        company_name = u'Test Company'
        section_name = u'Test Section'
        zip_code = u'152-0000'
        country_code = 81
        prefecture_code = 1
        city = u'Tokyo'
        address = u'Shinagawa-ku Gotanda'
        street = u'1-1-1'
        other_address = u'Meratirion OS 7F'
        tel_1 = u'03-3333-4444'
        tel_2 = u'03-4444-5555'
        fax = u'03-5555-6666'
        bank_account = BankAccountData.bank_account_1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class OperatorData(DataSet):
    class operator_1:
        name = 'test test'
        email = 'test@test.com'
        client_id = 1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
        login_id = 'test'
        password =  md5('test').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'

db_fixture = SQLAlchemyFixture(
     env={
         'OperatorData' : Operator,
         'BankData': Bank,
         'BankAccountData' : BankAccount,
         'ClientData' : Client,
     },
     engine=engine,
     )

metadata = Base.metadata
metadata.bind = engine
metadata.drop_all()

metadata.create_all()

data = db_fixture.data(BankData,BankAccountData, ClientData,OperatorData)
data.setup()

