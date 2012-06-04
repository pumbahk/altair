# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from datetime import datetime

from prefecture import PrefectureMaster
from user import UserData
from ticketing.organizations.models import *

class OrganizationData(DataSet):
    class organization_0:
        name            = u'楽天チケット（株式会社チケットスター）'
        user            = UserData.user_1
        client_type     = OrganizationTypeEnum.Standard.v
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
    class organization_1:
        name            = u'ぴあ'
        user            = UserData.user_2
        client_type     = OrganizationTypeEnum.Standard.v
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
    class organization_2:
        name            = u'イープラス'
        user            = UserData.user_3
        client_type     = OrganizationTypeEnum.Standard.v
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
    class organization_3:
        name            = u'ローソンチケット'
        user            = UserData.user_4
        client_type     = OrganizationTypeEnum.Standard.v
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
    class organization_4:
        name            = u'クライアント4'
        user            = UserData.user_5
        client_type     = OrganizationTypeEnum.Standard.v
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
    class organization_5:
        name            = u'クライアント5'
        user            = UserData.user_6
        client_type     = OrganizationTypeEnum.Standard.v
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
    class organization_6:
        name            = u'クライアント6'
        user            = UserData.user_7
        client_type     = OrganizationTypeEnum.Standard.v
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
