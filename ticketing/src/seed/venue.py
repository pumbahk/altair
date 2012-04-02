# -*- coding: utf-8 -*-

from seed import DataSet
from prefecture import PrefectureMaster
from ticketing.venues.models import Venue
from datetime import datetime

class VenueData(DataSet):
    class venue_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        zip = '151-0000'
        prefecture = PrefectureMaster.tokyo
        city = u'目黒区'
        address = u'目黒本町'
        street = u'１−１−１'
        other_address = u''
        tel_1 = u'03-0000-0000'
        tel_2 = u'03-1111-1111'
        fax = u'03-1111-1111'
