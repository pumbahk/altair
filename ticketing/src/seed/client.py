# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from ticketing.models import *
from ticketing.models.boxoffice import *
from prefecture import PrefectureMaster

class ClientData(DataSet):
    class client_0:
        name            = u'楽天チケット（株式会社チケットスター）'
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
