# -*- coding: utf-8 -*-

from datetime import datetime
from seed import DataSet

from seed.prefecture import PrefectureMaster
from seed.organization import OrganizationData


class SiteData(DataSet):
    class site_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        zip = u'151-0000'
        prefecture = u'東京都'
        city = u'目黒区'
        address = u'目黒本町'
        street = u'１−１−１'
        other_address = u''
        tel_1 = u'03-0000-0000'
        tel_2 = u'03-1111-1111'
        fax = u'03-1111-1111'
        drawing_url = u'file:sample.svg'

    class site_2:
        name = u'ブルーマンシアター'
        zip = u'151-0000'
        prefecture = u'東京都'
        city = u'目黒区'
        address = u'目黒本町'
        street = u'１−１−１'
        other_address = u''
        tel_1 = u'03-0000-0000'
        tel_2 = u'03-1111-1111'
        fax = u'03-1111-1111'
        drawing_url = u'file:sample.svg'

class VenueData(DataSet):
    class venue_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_2:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        site = SiteData.site_2
        organization = OrganizationData.organization_0

class SeatData(DataSet):
    class seat_1:
        l0_id = u'A1'
        venue = VenueData.venue_1
    class seat_2:
        l0_id = u'A2'
        venue = VenueData.venue_1
    class seat_3:
        l0_id = u'A3'
        venue = VenueData.venue_1
    class seat_4:
        l0_id = u'A4'
        venue = VenueData.venue_1
    class seat_5:
        l0_id = u'A5'
        venue = VenueData.venue_1

class SeatAttributeData(DataSet):
    class seat_attribute_1:
        seat = SeatData.seat_1
        name = u'attr1'
        value = u'seat1-test1'

    class seat_attribute_2:
        seat = SeatData.seat_1
        name = u'attr2'
        value = u'seat1-test2'

    class seat_attribute_3:
        seat = SeatData.seat_2
        name = u'attr1'
        value = u'seat2-test1'

    class seat_attribute_4:
        seat = SeatData.seat_2
        name = u'attr2'
        value = u'seat2-test2'

    class seat_attribute_5:
        seat = SeatData.seat_3
        name = u'attr1'
        value = u'seat3-test1'

    class seat_attribute_6:
        seat = SeatData.seat_3
        name = u'attr2'
        value = u'seat3-test2'

    class seat_attribute_7:
        seat = SeatData.seat_4
        name = u'attr1'
        value = u'seat4-test1'

    class seat_attribute_8:
        seat = SeatData.seat_4
        name = u'attr2'
        value = u'seat4-test2'

    class seat_attribute_9:
        seat = SeatData.seat_5
        name = u'attr1'
        value = u'seat5-test1'

    class seat_attribute_10:
        seat = SeatData.seat_5
        name = u'attr2'
        value = u'seat5-test2'

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
