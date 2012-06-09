# -*- coding: utf-8 -*-

from ticketing.seed import DataSet

from bank import BankAccountData
from prefecture import PrefectureMaster
from ticketing.core.models import *

class UserData(DataSet):
    class user_1:
        bank_account    = BankAccountData.bank_account_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_2:
        bank_account    = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_3:
        bank_account    = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_4:
        bank_account    = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_5:
        bank_account    = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_6:
        bank_account    = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_7:
        bank_account    = None
        updated_at      = datetime.now()
        created_at      = datetime.now()

class UserProfileData(DataSet):
    class user_profile_1:
        user            = UserData.user_1
        email           = u'test1@ticketstar.jp'
        nick_name       = u'楽チケ'
        first_name      = u'チケット'
        last_name       = u'楽天'
        first_name_kana = u'チケット'
        last_name_kana  = u'ラクテン'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_profile_2:
        user            = UserData.user_2
        email           = u'test2@ticketstar.jp'
        nick_name       = u'ぴあ'
        first_name      = u'あ'
        last_name       = u'ぴ'
        first_name_kana = u'ア'
        last_name_kana  = u'ピ'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_profile_3:
        user            = UserData.user_3
        email           = u'test3@ticketstar.jp'
        nick_name       = u'e+'
        first_name      = u'プラス'
        last_name       = u'イー'
        first_name_kana = u'プラス'
        last_name_kana  = u'イー'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_profile_4:
        user            = UserData.user_4
        email           = u'test4@ticketstar.jp'
        nick_name       = u'ローチケ'
        first_name      = u'チケット'
        last_name       = u'ローソン'
        first_name_kana = u'チケット'
        last_name_kana  = u'ローソン'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_profile_5:
        user            = UserData.user_5
        email           = u'test5@ticketstar.jp'
        nick_name       = u'クライアント4'
        first_name      = u'アント'
        last_name       = u'クライ'
        first_name_kana = u'アント'
        last_name_kana  = u'クライ'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_profile_6:
        user            = UserData.user_6
        email           = u'test5@ticketstar.jp'
        nick_name       = u'クライアント5'
        first_name      = u'アント'
        last_name       = u'クライ'
        first_name_kana = u'アント'
        last_name_kana  = u'クライ'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class user_profile_7:
        user            = UserData.user_7
        email           = u'test6@ticketstar.jp'
        nick_name       = u'クライアント6'
        first_name      = u'アント'
        last_name       = u'クライ'
        first_name_kana = u'アント'
        last_name_kana  = u'クライ'
        birth_day       = date(1955,1,1)
        sex             = 1
        zip             = '251-0036'
        prefecture      = u"東京都"
        city            = u'五反田'
        street          = u'１−２'
        address         = u'３４５'
        other_address   = u'その他住所'
        tel_1           = '00-0000-0000'
        tel_2           = '000-0000-0000'
        fax             = '0000-00-0000'
        updated_at      = datetime.now()
        created_at      = datetime.now()

class UserCredentialData(DataSet):
    class user_credential_1:
        user            = UserData.user_1
        auth_identifier = None
        auth_secret     = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
