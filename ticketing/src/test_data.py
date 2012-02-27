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

class PrefectureMaster(DataSet):
    class hokkaido:
        name = u'北海道'
    class aoamori:
        name = u'青森県'
    class iwate:
        name = u'岩手県'
    class miyagi:
        name = u'宮城県'
    class akita:
        name = u'秋田県'
    class yamagata:
        name = u'山形県'
    class fukuoka:
        name = u'福島県'
    class ibaraki:
        name = u'茨城県'
    class tochigi:
        name = u'栃木県'
    class gunma:
        name = u'群馬県'
    class saitama:
        name = u'埼玉県'
    class chiba:
        name = u'千葉県'
    class tokyo:
        name = u'東京都'
    class kanagawa:
        name = u'神奈川県'
    class niigata:
        name = u'新潟県'
    class toyama:
        name = u'富山県'
    class ishikawa:
        name = u'石川県'
    class fukui:
        name = u'福井県'
    class yamanashi:
        name = u'山梨県'
    class nagano:
        name = u'長野県'
    class gifu:
        name = u'岐阜県'
    class shizuoka:
        name = u'静岡県'
    class aichi:
        name = u'愛知県'
    class mie:
        name = u'三重県'
    class shiga:
        name = u'滋賀県'
    class kyoto:
        name = u'京都府'
    class osaka:
        name = u'大阪府'
    class hokkaido:
        name = u'兵庫県'
    class nara:
        name = u'奈良県'
    class wakayama:
        name = u'和歌山県'
    class tottori :
        name = u'鳥取県'
    class shimane:
        name = u'島根県'
    class okayama:
        name = u'岡山県'
    class hiroshima:
        name = u'広島県'
    class yamaguchi:
        name = u'山口県'
    class tokushima:
        name = u'徳島県'
    class kagawa:
        name = u'香川県'
    class ehime:
        name = u'愛媛県'
    class kouchi:
        name = u'高知県'
    class fukuoka:
        name = u'福岡県'
    class saga:
        name = u'佐賀県'
    class nagasaki:
        name = u'長崎県'
    class kumamoto:
        name = u'熊本県'
    class oita:
        name = u'大分県'
    class miyazaki:
        name = u'宮崎県'
    class kagoshima:
        name = u'鹿児島県'
    class okinawa:
        name = u'沖縄県'

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
    class bank_account_3:
        bank = BankData.bank_1
        account_type = 2
        account_number = u'1234567890'
        account_owner = u'Test Test3'
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class EventTicketOwnerData(DataSet):
    class event_ticket_owner_1:
        bank_account = BankAccountData.bank_account_1
        name         = 'チケットスター'
        company_name = "株式会社チケットスター"
        section_name = 'プライガイド事業部'
        zip_code     = 111-1111
        country_code = 81
        prefecture_code = PrefectureMaster.tokyo
        city = "品川区"
        address = "東五反田"
        street = "1-1-1"
        other_address = "XXXビル1F"
        tel_1 = "00-0000-0000"
        tel_2 = "00-0000-0000"
        fax = "00-0000-0000"
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class event_ticket_owner_2:
        bank_account = BankAccountData.bank_account_2
        name         = 'クライアント2'
        company_name = "株式会社クライアント2"
        section_name = 'チケット事業部'
        zip_code     = 111-1111
        country_code = 81
        prefecture_code = PrefectureMaster.tokyo
        city = "品川区"
        address = "東五反田"
        street = "1-1-1"
        other_address = "XXXビル1F"
        tel_1 = "00-0000-0000"
        tel_2 = "00-0000-0000"
        fax = "00-0000-0000"
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class event_ticket_owner_3:
        bank_account = BankAccountData.bank_account_3
        name         = 'クライアント3'
        company_name = "株式会社クライアント3"
        section_name = 'チケット事業部'
        zip_code     = 111-1111
        country_code = 81
        prefecture_code = PrefectureMaster.tokyo
        city = "品川区"
        address = "東五反田"
        street = "1-1-1"
        other_address = "XXXビル1F"
        tel_1 = "00-0000-0000"
        tel_2 = "00-0000-0000"
        fax = "00-0000-0000"
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class PermissionData(DataSet):
    class permission_cms:
        category_code = 1
        permit = 1
    class permission_backend:
        category_code = 2
        permit = Column(Integer)
    class permission_admin:
        category_code = 3
        permit = Column(Integer)

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

class ClientData(DataSet):
    class client_1:
        contract_type = 1
        name = u'チケットスター'
        event_ticket_owner = EventTicketOwnerData.event_ticket_owner_1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
    class client_2:
        contract_type = 1
        name = u'テストクライアント1'
        event_ticket_owner = EventTicketOwnerData.event_ticket_owner_2
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class OperatorData(DataSet):
    class operator_1:
        name = 'オペレーター1'
        email = 'test1@test.com'
        client_id = 1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
        login_id = 'test'
        password =  md5('test').hexdigest()
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
        login_id = 'test'
        password =  md5('test').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'

db_fixture = SQLAlchemyFixture(
     env={
         'PrefectureMaster' : Prefecture,
         'OperatorData' : Operator,
         'BankData': Bank,
         'BankAccountData' : BankAccount,
         'EventTicketOwnerData' : EventTicketOwner,
         'ClientData' : Client,
     },
     engine=engine,
     )

metadata = Base.metadata
metadata.bind = engine
metadata.drop_all()

metadata.create_all()

data = db_fixture.data(PrefectureMaster, BankData,BankAccountData, ClientData,OperatorData)
data.setup()

