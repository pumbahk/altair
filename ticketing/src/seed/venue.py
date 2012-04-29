# -*- coding: utf-8 -*-

from datetime import datetime
from seed import DataSet

from seed.prefecture import PrefectureMaster
from seed.organization import OrganizationData

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
        organization = OrganizationData.organization_0
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
        organization = OrganizationData.organization_0

class SeatMasterData(DataSet):
    class seat_master_1:
        identifieir = u'A1'
        venue = VenueData.venue_1
    class seat_master_2:
        identifieir = u'A2'
        venue = VenueData.venue_1
    class seat_master_3:
        identifieir = u'A3'
        venue = VenueData.venue_1
    class seat_master_4:
        identifieir = u'A4'
        venue = VenueData.venue_1
    class seat_master_5:
        identifieir = u'A5'
        venue = VenueData.venue_1

class SeatTypeData(DataSet):
    class seat_type_1:
        name = u'S席'
        performance_id = 1
        status = 1
    class seat_type_2:
        name = u'A席'
        performance_id = 1
        status = 1
    class seat_type_3:
        name = u'B席'
        performance_id = 1
        status = 1
    class seat_type_4:
        name = u'C席'
        performance_id = 1
        status = 1

class SeatMasterL2Data(DataSet):
    class seat_master_l2_1:
        seat_type =SeatTypeData.seat_type_1
        seat =SeatMasterData.seat_master_1
    class seat_master_l2_2:
        seat_type =SeatTypeData.seat_type_1
        seat =SeatMasterData.seat_master_2
    class seat_master_l2_3:
        seat_type =SeatTypeData.seat_type_1
        seat =SeatMasterData.seat_master_3
    class seat_master_l2_4:
        seat_type =SeatTypeData.seat_type_1
        seat =SeatMasterData.seat_master_4
    class seat_master_l2_5:
        seat_type =SeatTypeData.seat_type_1
        seat =SeatMasterData.seat_master_5
