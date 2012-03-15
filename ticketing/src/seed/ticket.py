# -*- coding: utf-8 -*-

from seed import DataSet
from prefecture import PrefectureMaster
from bank import BankAccountData
from datetime import datetime

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