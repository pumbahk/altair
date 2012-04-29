# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from seed.prefecture import PrefectureMaster
from ticketing.organizations.models import *

class OrganizationData(DataSet):
    class organization_0:
        id              = 1
        name            = u'楽天チケット（株式会社チケットスター）'
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
        status          = 1
    class organization_1:
        id              = 2
        name            = u'クライアント1'
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
        status          = 1
    class organization_2:
        id              = 3
        name            = u'クライアント2'
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
        status          = 1
    class organization_3:
        id              = 4
        name            = u'クライアント3'
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
        status          = 1
    class organization_4:
        id              = 5
        name            = u'クライアント4'
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
        status          = 1
    class organization_5:
        id              = 6
        name            = u'クライアント5'
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
        status          = 1
