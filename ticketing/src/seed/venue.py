# -*- coding: utf-8 -*-

from datetime import datetime
from seed import DataSet

from prefecture import PrefectureMaster
from ticketing.venues.models import Venue

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
    class venue_2:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        zip = '151-0000'
        prefecture = PrefectureMaster.tokyo
        city = u'目黒区'
        address = u'目黒本町'
        street = u'１−１−１'
        other_address = u''
        tel_1 = u'03-0000-0000'
        tel_2 = u'03-1111-1111'
        fax = u'03-1111-1111'

class SeatTypeData(DataSet):
    class seattype_1:
        name = u'S席'
        event_id = 1
        status = 1
    class seattype_2:
        name = u'A席'
        event_id = 1
        status = 1
    class seattype_3:
        name = u'B席'
        event_id = 1
        status = 1
    class seattype_4:
        name = u'C席'
        event_id = 1
        status = 1

