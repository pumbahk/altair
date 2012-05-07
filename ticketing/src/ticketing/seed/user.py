# -*- coding: utf-8 -*-

from ticketing.seed import DataSet

from bank import BankAccountData
from prefecture import PrefectureMaster
from ticketing.models import *

class UserData(DataSet):
    class user_1:
        bank_account    = BankAccountData.bank_account_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1

class UserProfileData(DataSet):
    class user_profile_1:
        user            = UserData.user_1
        email           = u'test1@ticketstar.jp'
        nick_name       = u'ニックネーム'
        first_name      = u'名'
        last_name       = u'姓'
        first_name_kana = u'セイ'
        last_name_kana  = u'メイ'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = PrefectureMaster.tokyo
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1

class UserCredentialData(DataSet):
    class user_credential_1:
        user            = UserData.user_1
        auth_identifier = None
        auth_secret     = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
