# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from ticketing.venues.models import SeatStatusEnum

from .event import PerformanceData, EventData
from .product import StockData
from .organization import OrganizationData

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
        drawing_url = u'file:ticketing/static/site-data/sample.svg'

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
        drawing_url = u'file:ticketing/static/site-data/sample.svg'

class VenueData(DataSet):
    class venue_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceData.performance_1
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_2:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceData.performance_2
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_3:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceData.performance_3
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_4:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceData.performance_4
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_5:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceData.performance_5
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_6:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = PerformanceData.performance_6
        site = SiteData.site_2
        organization = OrganizationData.organization_0
    class venue_7:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = PerformanceData.performance_7
        site = SiteData.site_2
        organization = OrganizationData.organization_0
    class venue_8:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = PerformanceData.performance_8
        site = SiteData.site_2
        organization = OrganizationData.organization_0

class SeatVenue1Data(DataSet):
    class seat_v1_a1:
        l0_id = u'A1'
        venue = VenueData.venue_1
        stock = StockData.stock_1
    class seat_v1_a2:
        l0_id = u'A2'
        venue = VenueData.venue_1
        stock = StockData.stock_1
    class seat_v1_a3:
        l0_id = u'A3'
        venue = VenueData.venue_1
        stock = StockData.stock_1
    class seat_v1_a4:
        l0_id = u'A4'
        venue = VenueData.venue_1
        stock = StockData.stock_1
    class seat_v1_a5:
        l0_id = u'A5'
        venue = VenueData.venue_1
        stock = StockData.stock_1
    class seat_v1_a6:
        l0_id = u'A6'
        venue = VenueData.venue_1
        stock = StockData.stock_1
    class seat_v1_a7:
        l0_id = u'A7'
        venue = VenueData.venue_1
        stock = StockData.stock_5
    class seat_v1_a8:
        l0_id = u'A8'
        venue = VenueData.venue_1
        stock = StockData.stock_5
    class seat_v1_a9:
        l0_id = u'A9'
        venue = VenueData.venue_1
        stock = StockData.stock_5
    class seat_v1_b1:
        l0_id = u'B1'
        venue = VenueData.venue_1
        stock = StockData.stock_2
    class seat_v1_b2:
        l0_id = u'B2'
        venue = VenueData.venue_1
        stock = StockData.stock_2
    class seat_v1_b3:
        l0_id = u'B3'
        venue = VenueData.venue_1
        stock = StockData.stock_2
    class seat_v1_b4:
        l0_id = u'B4'
        venue = VenueData.venue_1
        stock = StockData.stock_6
    class seat_v1_b5:
        l0_id = u'B5'
        venue = VenueData.venue_1
        stock = StockData.stock_6
    class seat_v1_b6:
        l0_id = u'B6'
        venue = VenueData.venue_1
        stock = StockData.stock_6
    class seat_v1_b7:
        l0_id = u'B7'
        venue = VenueData.venue_1
        stock = StockData.stock_6
    class seat_v1_c1:
        l0_id = u'C1'
        venue = VenueData.venue_1
        stock = StockData.stock_3
    class seat_v1_c2:
        l0_id = u'C2'
        venue = VenueData.venue_1
        stock = StockData.stock_3
    class seat_v1_c3:
        l0_id = u'C3'
        venue = VenueData.venue_1
        stock = StockData.stock_7
    class seat_v1_c4:
        l0_id = u'C4'
        venue = VenueData.venue_1
        stock = StockData.stock_7
    class seat_v1_c5:
        l0_id = u'C5'
        venue = VenueData.venue_1
        stock = StockData.stock_7
    class seat_v1_d1:
        l0_id = u'D1'
        venue = VenueData.venue_1
        stock = StockData.stock_4
    class seat_v1_d2:
        l0_id = u'D2'
        venue = VenueData.venue_1
        stock = StockData.stock_4
    class seat_v1_d3:
        l0_id = u'D3'
        venue = VenueData.venue_1
        stock = StockData.stock_4
    class seat_v1_e1:
        l0_id = u'E1'
        venue = VenueData.venue_1
        stock = StockData.stock_8
    class seat_v1_e2:
        l0_id = u'E2'
        venue = VenueData.venue_1
        stock = StockData.stock_8
    class seat_v1_e3:
        l0_id = u'E3'
        venue = VenueData.venue_1
        stock = StockData.stock_8

class SeatVenue2Data(DataSet):
    class seat_v2_a1:
        l0_id = u'A1'
        venue = VenueData.venue_2
    class seat_v2_a2:
        l0_id = u'A2'
        venue = VenueData.venue_2
    class seat_v2_a3:
        l0_id = u'A3'
        venue = VenueData.venue_2
    class seat_v2_a4:
        l0_id = u'A4'
        venue = VenueData.venue_2
    class seat_v2_a5:
        l0_id = u'A5'
        venue = VenueData.venue_2
    class seat_v2_a6:
        l0_id = u'A6'
        venue = VenueData.venue_2
    class seat_v2_a7:
        l0_id = u'A7'
        venue = VenueData.venue_2
    class seat_v2_a8:
        l0_id = u'A8'
        venue = VenueData.venue_2
    class seat_v2_a9:
        l0_id = u'A9'
        venue = VenueData.venue_2
    class seat_v2_b1:
        l0_id = u'B1'
        venue = VenueData.venue_2
    class seat_v2_b2:
        l0_id = u'B2'
        venue = VenueData.venue_2
    class seat_v2_b3:
        l0_id = u'B3'
        venue = VenueData.venue_2
    class seat_v2_b4:
        l0_id = u'B4'
        venue = VenueData.venue_2
    class seat_v2_b5:
        l0_id = u'B5'
        venue = VenueData.venue_2
    class seat_v2_b6:
        l0_id = u'B6'
        venue = VenueData.venue_2
    class seat_v2_b7:
        l0_id = u'B7'
        venue = VenueData.venue_2
    class seat_v2_c1:
        l0_id = u'C1'
        venue = VenueData.venue_2
    class seat_v2_c2:
        l0_id = u'C2'
        venue = VenueData.venue_2
    class seat_v2_c3:
        l0_id = u'C3'
        venue = VenueData.venue_2
    class seat_v2_c4:
        l0_id = u'C4'
        venue = VenueData.venue_2
    class seat_v2_c5:
        l0_id = u'C5'
        venue = VenueData.venue_2
    class seat_v2_d1:
        l0_id = u'D1'
        venue = VenueData.venue_2
    class seat_v2_d2:
        l0_id = u'D2'
        venue = VenueData.venue_2
    class seat_v2_d3:
        l0_id = u'D3'
        venue = VenueData.venue_2
    class seat_v2_e1:
        l0_id = u'E1'
        venue = VenueData.venue_2
    class seat_v2_e2:
        l0_id = u'E2'
        venue = VenueData.venue_2
    class seat_v2_e3:
        l0_id = u'E3'
        venue = VenueData.venue_2

class SeatVenue3Data(DataSet):
    class seat_v3_a1:
        l0_id = u'A1'
        venue = VenueData.venue_3
    class seat_v3_a2:
        l0_id = u'A2'
        venue = VenueData.venue_3
    class seat_v3_a3:
        l0_id = u'A3'
        venue = VenueData.venue_3
    class seat_v3_a4:
        l0_id = u'A4'
        venue = VenueData.venue_3
    class seat_v3_a5:
        l0_id = u'A5'
        venue = VenueData.venue_3
    class seat_v3_a6:
        l0_id = u'A6'
        venue = VenueData.venue_3
    class seat_v3_a7:
        l0_id = u'A7'
        venue = VenueData.venue_3
    class seat_v3_a8:
        l0_id = u'A8'
        venue = VenueData.venue_3
    class seat_v3_a9:
        l0_id = u'A9'
        venue = VenueData.venue_3
    class seat_v3_b1:
        l0_id = u'B1'
        venue = VenueData.venue_3
    class seat_v3_b2:
        l0_id = u'B2'
        venue = VenueData.venue_3
    class seat_v3_b3:
        l0_id = u'B3'
        venue = VenueData.venue_3
    class seat_v3_b4:
        l0_id = u'B4'
        venue = VenueData.venue_3
    class seat_v3_b5:
        l0_id = u'B5'
        venue = VenueData.venue_3
    class seat_v3_b6:
        l0_id = u'B6'
        venue = VenueData.venue_3
    class seat_v3_b7:
        l0_id = u'B7'
        venue = VenueData.venue_3
    class seat_v3_c1:
        l0_id = u'C1'
        venue = VenueData.venue_3
    class seat_v3_c2:
        l0_id = u'C2'
        venue = VenueData.venue_3
    class seat_v3_c3:
        l0_id = u'C3'
        venue = VenueData.venue_3
    class seat_v3_c4:
        l0_id = u'C4'
        venue = VenueData.venue_3
    class seat_v3_c5:
        l0_id = u'C5'
        venue = VenueData.venue_3
    class seat_v3_d1:
        l0_id = u'D1'
        venue = VenueData.venue_3
    class seat_v3_d2:
        l0_id = u'D2'
        venue = VenueData.venue_3
    class seat_v3_d3:
        l0_id = u'D3'
        venue = VenueData.venue_3
    class seat_v3_e1:
        l0_id = u'E1'
        venue = VenueData.venue_3
    class seat_v3_e2:
        l0_id = u'E2'
        venue = VenueData.venue_3
    class seat_v3_e3:
        l0_id = u'E3'
        venue = VenueData.venue_3

class SeatVenue4Data(DataSet):
    class seat_v4_a1:
        l0_id = u'A1'
        venue = VenueData.venue_4
    class seat_v4_a2:
        l0_id = u'A2'
        venue = VenueData.venue_4
    class seat_v4_a3:
        l0_id = u'A3'
        venue = VenueData.venue_4
    class seat_v4_a4:
        l0_id = u'A4'
        venue = VenueData.venue_4
    class seat_v4_a5:
        l0_id = u'A5'
        venue = VenueData.venue_4
    class seat_v4_a6:
        l0_id = u'A6'
        venue = VenueData.venue_4
    class seat_v4_a7:
        l0_id = u'A7'
        venue = VenueData.venue_4
    class seat_v4_a8:
        l0_id = u'A8'
        venue = VenueData.venue_4
    class seat_v4_a9:
        l0_id = u'A9'
        venue = VenueData.venue_4
    class seat_v4_b1:
        l0_id = u'B1'
        venue = VenueData.venue_4
    class seat_v4_b2:
        l0_id = u'B2'
        venue = VenueData.venue_4
    class seat_v4_b3:
        l0_id = u'B3'
        venue = VenueData.venue_4
    class seat_v4_b4:
        l0_id = u'B4'
        venue = VenueData.venue_4
    class seat_v4_b5:
        l0_id = u'B5'
        venue = VenueData.venue_4
    class seat_v4_b6:
        l0_id = u'B6'
        venue = VenueData.venue_4
    class seat_v4_b7:
        l0_id = u'B7'
        venue = VenueData.venue_4
    class seat_v4_c1:
        l0_id = u'C1'
        venue = VenueData.venue_4
    class seat_v4_c2:
        l0_id = u'C2'
        venue = VenueData.venue_4
    class seat_v4_c3:
        l0_id = u'C3'
        venue = VenueData.venue_4
    class seat_v4_c4:
        l0_id = u'C4'
        venue = VenueData.venue_4
    class seat_v4_c5:
        l0_id = u'C5'
        venue = VenueData.venue_4
    class seat_v4_d1:
        l0_id = u'D1'
        venue = VenueData.venue_4
    class seat_v4_d2:
        l0_id = u'D2'
        venue = VenueData.venue_4
    class seat_v4_d3:
        l0_id = u'D3'
        venue = VenueData.venue_4
    class seat_v4_e1:
        l0_id = u'E1'
        venue = VenueData.venue_4
    class seat_v4_e2:
        l0_id = u'E2'
        venue = VenueData.venue_4
    class seat_v4_e3:
        l0_id = u'E3'
        venue = VenueData.venue_4

class SeatVenue5Data(DataSet):
    class seat_v5_a1:
        l0_id = u'A1'
        venue = VenueData.venue_5
    class seat_v5_a2:
        l0_id = u'A2'
        venue = VenueData.venue_5
    class seat_v5_a3:
        l0_id = u'A3'
        venue = VenueData.venue_5
    class seat_v5_a4:
        l0_id = u'A4'
        venue = VenueData.venue_5
    class seat_v5_a5:
        l0_id = u'A5'
        venue = VenueData.venue_5
    class seat_v5_a6:
        l0_id = u'A6'
        venue = VenueData.venue_5
    class seat_v5_a7:
        l0_id = u'A7'
        venue = VenueData.venue_5
    class seat_v5_a8:
        l0_id = u'A8'
        venue = VenueData.venue_5
    class seat_v5_a9:
        l0_id = u'A9'
        venue = VenueData.venue_5
    class seat_v5_b1:
        l0_id = u'B1'
        venue = VenueData.venue_5
    class seat_v5_b2:
        l0_id = u'B2'
        venue = VenueData.venue_5
    class seat_v5_b3:
        l0_id = u'B3'
        venue = VenueData.venue_5
    class seat_v5_b4:
        l0_id = u'B4'
        venue = VenueData.venue_5
    class seat_v5_b5:
        l0_id = u'B5'
        venue = VenueData.venue_5
    class seat_v5_b6:
        l0_id = u'B6'
        venue = VenueData.venue_5
    class seat_v5_b7:
        l0_id = u'B7'
        venue = VenueData.venue_5
    class seat_v5_c1:
        l0_id = u'C1'
        venue = VenueData.venue_5
    class seat_v5_c2:
        l0_id = u'C2'
        venue = VenueData.venue_5
    class seat_v5_c3:
        l0_id = u'C3'
        venue = VenueData.venue_5
    class seat_v5_c4:
        l0_id = u'C4'
        venue = VenueData.venue_5
    class seat_v5_c5:
        l0_id = u'C5'
        venue = VenueData.venue_5
    class seat_v5_d1:
        l0_id = u'D1'
        venue = VenueData.venue_5
    class seat_v5_d2:
        l0_id = u'D2'
        venue = VenueData.venue_5
    class seat_v5_d3:
        l0_id = u'D3'
        venue = VenueData.venue_5
    class seat_v5_e1:
        l0_id = u'E1'
        venue = VenueData.venue_5
    class seat_v5_e2:
        l0_id = u'E2'
        venue = VenueData.venue_5
    class seat_v5_e3:
        l0_id = u'E3'
        venue = VenueData.venue_5

class SeatVenue6Data(DataSet):
    class seat_v6_a1:
        l0_id = u'A1'
        venue = VenueData.venue_6
    class seat_v6_a2:
        l0_id = u'A2'
        venue = VenueData.venue_6
    class seat_v6_a3:
        l0_id = u'A3'
        venue = VenueData.venue_6
    class seat_v6_a4:
        l0_id = u'A4'
        venue = VenueData.venue_6
    class seat_v6_a5:
        l0_id = u'A5'
        venue = VenueData.venue_6
    class seat_v6_a6:
        l0_id = u'A6'
        venue = VenueData.venue_6
    class seat_v6_a7:
        l0_id = u'A7'
        venue = VenueData.venue_6
    class seat_v6_a8:
        l0_id = u'A8'
        venue = VenueData.venue_6
    class seat_v6_a9:
        l0_id = u'A9'
        venue = VenueData.venue_6
    class seat_v6_b1:
        l0_id = u'B1'
        venue = VenueData.venue_6
    class seat_v6_b2:
        l0_id = u'B2'
        venue = VenueData.venue_6
    class seat_v6_b3:
        l0_id = u'B3'
        venue = VenueData.venue_6
    class seat_v6_b4:
        l0_id = u'B4'
        venue = VenueData.venue_6
    class seat_v6_b5:
        l0_id = u'B5'
        venue = VenueData.venue_6
    class seat_v6_b6:
        l0_id = u'B6'
        venue = VenueData.venue_6
    class seat_v6_b7:
        l0_id = u'B7'
        venue = VenueData.venue_6
    class seat_v6_c1:
        l0_id = u'C1'
        venue = VenueData.venue_6
    class seat_v6_c2:
        l0_id = u'C2'
        venue = VenueData.venue_6
    class seat_v6_c3:
        l0_id = u'C3'
        venue = VenueData.venue_6
    class seat_v6_c4:
        l0_id = u'C4'
        venue = VenueData.venue_6
    class seat_v6_c5:
        l0_id = u'C5'
        venue = VenueData.venue_6
    class seat_v6_d1:
        l0_id = u'D1'
        venue = VenueData.venue_6
    class seat_v6_d2:
        l0_id = u'D2'
        venue = VenueData.venue_6
    class seat_v6_d3:
        l0_id = u'D3'
        venue = VenueData.venue_6
    class seat_v6_e1:
        l0_id = u'E1'
        venue = VenueData.venue_6
    class seat_v6_e2:
        l0_id = u'E2'
        venue = VenueData.venue_6
    class seat_v6_e3:
        l0_id = u'E3'
        venue = VenueData.venue_6

class SeatVenue7Data(DataSet):
    class seat_v7_a1:
        l0_id = u'A1'
        venue = VenueData.venue_7
    class seat_v7_a2:
        l0_id = u'A2'
        venue = VenueData.venue_7
    class seat_v7_a3:
        l0_id = u'A3'
        venue = VenueData.venue_7
    class seat_v7_a4:
        l0_id = u'A4'
        venue = VenueData.venue_7
    class seat_v7_a5:
        l0_id = u'A5'
        venue = VenueData.venue_7
    class seat_v7_a6:
        l0_id = u'A6'
        venue = VenueData.venue_7
    class seat_v7_a7:
        l0_id = u'A7'
        venue = VenueData.venue_7
    class seat_v7_a8:
        l0_id = u'A8'
        venue = VenueData.venue_7
    class seat_v7_a9:
        l0_id = u'A9'
        venue = VenueData.venue_7
    class seat_v7_b1:
        l0_id = u'B1'
        venue = VenueData.venue_7
    class seat_v7_b2:
        l0_id = u'B2'
        venue = VenueData.venue_7
    class seat_v7_b3:
        l0_id = u'B3'
        venue = VenueData.venue_7
    class seat_v7_b4:
        l0_id = u'B4'
        venue = VenueData.venue_7
    class seat_v7_b5:
        l0_id = u'B5'
        venue = VenueData.venue_7
    class seat_v7_b6:
        l0_id = u'B6'
        venue = VenueData.venue_7
    class seat_v7_b7:
        l0_id = u'B7'
        venue = VenueData.venue_7
    class seat_v7_c1:
        l0_id = u'C1'
        venue = VenueData.venue_7
    class seat_v7_c2:
        l0_id = u'C2'
        venue = VenueData.venue_7
    class seat_v7_c3:
        l0_id = u'C3'
        venue = VenueData.venue_7
    class seat_v7_c4:
        l0_id = u'C4'
        venue = VenueData.venue_7
    class seat_v7_c5:
        l0_id = u'C5'
        venue = VenueData.venue_7
    class seat_v7_d1:
        l0_id = u'D1'
        venue = VenueData.venue_7
    class seat_v7_d2:
        l0_id = u'D2'
        venue = VenueData.venue_7
    class seat_v7_d3:
        l0_id = u'D3'
        venue = VenueData.venue_7
    class seat_v7_e1:
        l0_id = u'E1'
        venue = VenueData.venue_7
    class seat_v7_e2:
        l0_id = u'E2'
        venue = VenueData.venue_7
    class seat_v7_e3:
        l0_id = u'E3'
        venue = VenueData.venue_7

class SeatVenue8Data(DataSet):
    class seat_v8_a1:
        l0_id = u'A1'
        venue = VenueData.venue_8
    class seat_v8_a2:
        l0_id = u'A2'
        venue = VenueData.venue_8
    class seat_v8_a3:
        l0_id = u'A3'
        venue = VenueData.venue_8
    class seat_v8_a4:
        l0_id = u'A4'
        venue = VenueData.venue_8
    class seat_v8_a5:
        l0_id = u'A5'
        venue = VenueData.venue_8
    class seat_v8_a6:
        l0_id = u'A6'
        venue = VenueData.venue_8
    class seat_v8_a7:
        l0_id = u'A7'
        venue = VenueData.venue_8
    class seat_v8_a8:
        l0_id = u'A8'
        venue = VenueData.venue_8
    class seat_v8_a9:
        l0_id = u'A9'
        venue = VenueData.venue_8
    class seat_v8_b1:
        l0_id = u'B1'
        venue = VenueData.venue_8
    class seat_v8_b2:
        l0_id = u'B2'
        venue = VenueData.venue_8
    class seat_v8_b3:
        l0_id = u'B3'
        venue = VenueData.venue_8
    class seat_v8_b4:
        l0_id = u'B4'
        venue = VenueData.venue_8
    class seat_v8_b5:
        l0_id = u'B5'
        venue = VenueData.venue_8
    class seat_v8_b6:
        l0_id = u'B6'
        venue = VenueData.venue_8
    class seat_v8_b7:
        l0_id = u'B7'
        venue = VenueData.venue_8
    class seat_v8_c1:
        l0_id = u'C1'
        venue = VenueData.venue_8
    class seat_v8_c2:
        l0_id = u'C2'
        venue = VenueData.venue_8
    class seat_v8_c3:
        l0_id = u'C3'
        venue = VenueData.venue_8
    class seat_v8_c4:
        l0_id = u'C4'
        venue = VenueData.venue_8
    class seat_v8_c5:
        l0_id = u'C5'
        venue = VenueData.venue_8
    class seat_v8_d1:
        l0_id = u'D1'
        venue = VenueData.venue_8
    class seat_v8_d2:
        l0_id = u'D2'
        venue = VenueData.venue_8
    class seat_v8_d3:
        l0_id = u'D3'
        venue = VenueData.venue_8
    class seat_v8_e1:
        l0_id = u'E1'
        venue = VenueData.venue_8
    class seat_v8_e2:
        l0_id = u'E2'
        venue = VenueData.venue_8
    class seat_v8_e3:
        l0_id = u'E3'
        venue = VenueData.venue_8

class SeatStatusVenue1Data(DataSet):
    class seat_status_v1_1:
        seat = SeatVenue1Data.seat_v1_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_2:
        seat = SeatVenue1Data.seat_v1_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_3:
        seat = SeatVenue1Data.seat_v1_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_4:
        seat = SeatVenue1Data.seat_v1_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_5:
        seat = SeatVenue1Data.seat_v1_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_6:
        seat = SeatVenue1Data.seat_v1_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_7:
        seat = SeatVenue1Data.seat_v1_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_8:
        seat = SeatVenue1Data.seat_v1_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_9:
        seat = SeatVenue1Data.seat_v1_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_10:
        seat = SeatVenue1Data.seat_v1_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_11:
        seat = SeatVenue1Data.seat_v1_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_12:
        seat = SeatVenue1Data.seat_v1_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_13:
        seat = SeatVenue1Data.seat_v1_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_14:
        seat = SeatVenue1Data.seat_v1_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_15:
        seat = SeatVenue1Data.seat_v1_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_16:
        seat = SeatVenue1Data.seat_v1_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_17:
        seat = SeatVenue1Data.seat_v1_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_18:
        seat = SeatVenue1Data.seat_v1_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_19:
        seat = SeatVenue1Data.seat_v1_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_20:
        seat = SeatVenue1Data.seat_v1_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_21:
        seat = SeatVenue1Data.seat_v1_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_22:
        seat = SeatVenue1Data.seat_v1_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_23:
        seat = SeatVenue1Data.seat_v1_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_24:
        seat = SeatVenue1Data.seat_v1_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_25:
        seat = SeatVenue1Data.seat_v1_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_26:
        seat = SeatVenue1Data.seat_v1_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_27:
        seat = SeatVenue1Data.seat_v1_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue2Data(DataSet):
    class seat_status_v2_1:
        seat = SeatVenue2Data.seat_v2_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_2:
        seat = SeatVenue2Data.seat_v2_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_3:
        seat = SeatVenue2Data.seat_v2_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_4:
        seat = SeatVenue2Data.seat_v2_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_5:
        seat = SeatVenue2Data.seat_v2_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_6:
        seat = SeatVenue2Data.seat_v2_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_7:
        seat = SeatVenue2Data.seat_v2_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_8:
        seat = SeatVenue2Data.seat_v2_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_9:
        seat = SeatVenue2Data.seat_v2_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_10:
        seat = SeatVenue2Data.seat_v2_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_11:
        seat = SeatVenue2Data.seat_v2_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_12:
        seat = SeatVenue2Data.seat_v2_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_13:
        seat = SeatVenue2Data.seat_v2_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_14:
        seat = SeatVenue2Data.seat_v2_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_15:
        seat = SeatVenue2Data.seat_v2_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_16:
        seat = SeatVenue2Data.seat_v2_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_17:
        seat = SeatVenue2Data.seat_v2_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_18:
        seat = SeatVenue2Data.seat_v2_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_19:
        seat = SeatVenue2Data.seat_v2_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_20:
        seat = SeatVenue2Data.seat_v2_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_21:
        seat = SeatVenue2Data.seat_v2_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_22:
        seat = SeatVenue2Data.seat_v2_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_23:
        seat = SeatVenue2Data.seat_v2_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_24:
        seat = SeatVenue2Data.seat_v2_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_25:
        seat = SeatVenue2Data.seat_v2_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_26:
        seat = SeatVenue2Data.seat_v2_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_27:
        seat = SeatVenue2Data.seat_v2_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue3Data(DataSet):
    class seat_status_v3_1:
        seat = SeatVenue3Data.seat_v3_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_2:
        seat = SeatVenue3Data.seat_v3_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_3:
        seat = SeatVenue3Data.seat_v3_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_4:
        seat = SeatVenue3Data.seat_v3_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_5:
        seat = SeatVenue3Data.seat_v3_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_6:
        seat = SeatVenue3Data.seat_v3_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_7:
        seat = SeatVenue3Data.seat_v3_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_8:
        seat = SeatVenue3Data.seat_v3_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_9:
        seat = SeatVenue3Data.seat_v3_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_10:
        seat = SeatVenue3Data.seat_v3_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_11:
        seat = SeatVenue3Data.seat_v3_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_12:
        seat = SeatVenue3Data.seat_v3_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_13:
        seat = SeatVenue3Data.seat_v3_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_14:
        seat = SeatVenue3Data.seat_v3_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_15:
        seat = SeatVenue3Data.seat_v3_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_16:
        seat = SeatVenue3Data.seat_v3_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_17:
        seat = SeatVenue3Data.seat_v3_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_18:
        seat = SeatVenue3Data.seat_v3_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_19:
        seat = SeatVenue3Data.seat_v3_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_20:
        seat = SeatVenue3Data.seat_v3_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_21:
        seat = SeatVenue3Data.seat_v3_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_22:
        seat = SeatVenue3Data.seat_v3_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_23:
        seat = SeatVenue3Data.seat_v3_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_24:
        seat = SeatVenue3Data.seat_v3_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_25:
        seat = SeatVenue3Data.seat_v3_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_26:
        seat = SeatVenue3Data.seat_v3_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_27:
        seat = SeatVenue3Data.seat_v3_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue4Data(DataSet):
    class seat_status_v4_1:
        seat = SeatVenue4Data.seat_v4_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_2:
        seat = SeatVenue4Data.seat_v4_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_3:
        seat = SeatVenue4Data.seat_v4_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_4:
        seat = SeatVenue4Data.seat_v4_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_5:
        seat = SeatVenue4Data.seat_v4_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_6:
        seat = SeatVenue4Data.seat_v4_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_7:
        seat = SeatVenue4Data.seat_v4_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_8:
        seat = SeatVenue4Data.seat_v4_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_9:
        seat = SeatVenue4Data.seat_v4_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_10:
        seat = SeatVenue4Data.seat_v4_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_11:
        seat = SeatVenue4Data.seat_v4_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_12:
        seat = SeatVenue4Data.seat_v4_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_13:
        seat = SeatVenue4Data.seat_v4_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_14:
        seat = SeatVenue4Data.seat_v4_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_15:
        seat = SeatVenue4Data.seat_v4_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_16:
        seat = SeatVenue4Data.seat_v4_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_17:
        seat = SeatVenue4Data.seat_v4_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_18:
        seat = SeatVenue4Data.seat_v4_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_19:
        seat = SeatVenue4Data.seat_v4_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_20:
        seat = SeatVenue4Data.seat_v4_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_21:
        seat = SeatVenue4Data.seat_v4_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_22:
        seat = SeatVenue4Data.seat_v4_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_23:
        seat = SeatVenue4Data.seat_v4_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_24:
        seat = SeatVenue4Data.seat_v4_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_25:
        seat = SeatVenue4Data.seat_v4_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_26:
        seat = SeatVenue4Data.seat_v4_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_27:
        seat = SeatVenue4Data.seat_v4_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue5Data(DataSet):
    class seat_status_v5_1:
        seat = SeatVenue5Data.seat_v5_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_2:
        seat = SeatVenue5Data.seat_v5_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_3:
        seat = SeatVenue5Data.seat_v5_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_4:
        seat = SeatVenue5Data.seat_v5_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_5:
        seat = SeatVenue5Data.seat_v5_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_6:
        seat = SeatVenue5Data.seat_v5_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_7:
        seat = SeatVenue5Data.seat_v5_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_8:
        seat = SeatVenue5Data.seat_v5_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_9:
        seat = SeatVenue5Data.seat_v5_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_10:
        seat = SeatVenue5Data.seat_v5_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_11:
        seat = SeatVenue5Data.seat_v5_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_12:
        seat = SeatVenue5Data.seat_v5_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_13:
        seat = SeatVenue5Data.seat_v5_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_14:
        seat = SeatVenue5Data.seat_v5_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_15:
        seat = SeatVenue5Data.seat_v5_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_16:
        seat = SeatVenue5Data.seat_v5_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_17:
        seat = SeatVenue5Data.seat_v5_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_18:
        seat = SeatVenue5Data.seat_v5_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_19:
        seat = SeatVenue5Data.seat_v5_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_20:
        seat = SeatVenue5Data.seat_v5_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_21:
        seat = SeatVenue5Data.seat_v5_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_22:
        seat = SeatVenue5Data.seat_v5_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_23:
        seat = SeatVenue5Data.seat_v5_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_24:
        seat = SeatVenue5Data.seat_v5_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_25:
        seat = SeatVenue5Data.seat_v5_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_26:
        seat = SeatVenue5Data.seat_v5_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_27:
        seat = SeatVenue5Data.seat_v5_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue6Data(DataSet):
    class seat_status_v6_1:
        seat = SeatVenue6Data.seat_v6_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_2:
        seat = SeatVenue6Data.seat_v6_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_3:
        seat = SeatVenue6Data.seat_v6_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_4:
        seat = SeatVenue6Data.seat_v6_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_5:
        seat = SeatVenue6Data.seat_v6_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_6:
        seat = SeatVenue6Data.seat_v6_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_7:
        seat = SeatVenue6Data.seat_v6_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_8:
        seat = SeatVenue6Data.seat_v6_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_9:
        seat = SeatVenue6Data.seat_v6_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_10:
        seat = SeatVenue6Data.seat_v6_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_11:
        seat = SeatVenue6Data.seat_v6_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_12:
        seat = SeatVenue6Data.seat_v6_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_13:
        seat = SeatVenue6Data.seat_v6_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_14:
        seat = SeatVenue6Data.seat_v6_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_15:
        seat = SeatVenue6Data.seat_v6_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_16:
        seat = SeatVenue6Data.seat_v6_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_17:
        seat = SeatVenue6Data.seat_v6_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_18:
        seat = SeatVenue6Data.seat_v6_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_19:
        seat = SeatVenue6Data.seat_v6_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_20:
        seat = SeatVenue6Data.seat_v6_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_21:
        seat = SeatVenue6Data.seat_v6_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_22:
        seat = SeatVenue6Data.seat_v6_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_23:
        seat = SeatVenue6Data.seat_v6_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_24:
        seat = SeatVenue6Data.seat_v6_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_25:
        seat = SeatVenue6Data.seat_v6_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_26:
        seat = SeatVenue6Data.seat_v6_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v6_27:
        seat = SeatVenue6Data.seat_v6_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue7Data(DataSet):
    class seat_status_v7_1:
        seat = SeatVenue7Data.seat_v7_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_2:
        seat = SeatVenue7Data.seat_v7_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_3:
        seat = SeatVenue7Data.seat_v7_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_4:
        seat = SeatVenue7Data.seat_v7_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_5:
        seat = SeatVenue7Data.seat_v7_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_6:
        seat = SeatVenue7Data.seat_v7_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_7:
        seat = SeatVenue7Data.seat_v7_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_8:
        seat = SeatVenue7Data.seat_v7_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_9:
        seat = SeatVenue7Data.seat_v7_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_10:
        seat = SeatVenue7Data.seat_v7_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_11:
        seat = SeatVenue7Data.seat_v7_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_12:
        seat = SeatVenue7Data.seat_v7_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_13:
        seat = SeatVenue7Data.seat_v7_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_14:
        seat = SeatVenue7Data.seat_v7_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_15:
        seat = SeatVenue7Data.seat_v7_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_16:
        seat = SeatVenue7Data.seat_v7_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_17:
        seat = SeatVenue7Data.seat_v7_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_18:
        seat = SeatVenue7Data.seat_v7_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_19:
        seat = SeatVenue7Data.seat_v7_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_20:
        seat = SeatVenue7Data.seat_v7_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_21:
        seat = SeatVenue7Data.seat_v7_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_22:
        seat = SeatVenue7Data.seat_v7_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_23:
        seat = SeatVenue7Data.seat_v7_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_24:
        seat = SeatVenue7Data.seat_v7_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_25:
        seat = SeatVenue7Data.seat_v7_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_26:
        seat = SeatVenue7Data.seat_v7_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v7_27:
        seat = SeatVenue7Data.seat_v7_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusVenue8Data(DataSet):
    class seat_status_v8_1:
        seat = SeatVenue8Data.seat_v8_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_2:
        seat = SeatVenue8Data.seat_v8_a2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_3:
        seat = SeatVenue8Data.seat_v8_a3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_4:
        seat = SeatVenue8Data.seat_v8_a4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_5:
        seat = SeatVenue8Data.seat_v8_a5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_6:
        seat = SeatVenue8Data.seat_v8_a6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_7:
        seat = SeatVenue8Data.seat_v8_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_8:
        seat = SeatVenue8Data.seat_v8_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_9:
        seat = SeatVenue8Data.seat_v8_a9
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_10:
        seat = SeatVenue8Data.seat_v8_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_11:
        seat = SeatVenue8Data.seat_v8_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_12:
        seat = SeatVenue8Data.seat_v8_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_13:
        seat = SeatVenue8Data.seat_v8_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_14:
        seat = SeatVenue8Data.seat_v8_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_15:
        seat = SeatVenue8Data.seat_v8_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_16:
        seat = SeatVenue8Data.seat_v8_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_17:
        seat = SeatVenue8Data.seat_v8_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_18:
        seat = SeatVenue8Data.seat_v8_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_19:
        seat = SeatVenue8Data.seat_v8_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_20:
        seat = SeatVenue8Data.seat_v8_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_21:
        seat = SeatVenue8Data.seat_v8_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_22:
        seat = SeatVenue8Data.seat_v8_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_23:
        seat = SeatVenue8Data.seat_v8_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_24:
        seat = SeatVenue8Data.seat_v8_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_25:
        seat = SeatVenue8Data.seat_v8_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_26:
        seat = SeatVenue8Data.seat_v8_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v8_27:
        seat = SeatVenue8Data.seat_v8_e3
        status = int(SeatStatusEnum.Vacant)

class SeatAttributeData(DataSet):
    class seat_attribute_1:
        seat = SeatVenue1Data.seat_v1_a1
        name = u'attr1'
        value = u'a1-attr2'

    class seat_attribute_2:
        seat = SeatVenue1Data.seat_v1_a1
        name = u'attr2'
        value = u'a1-attr2'

    class seat_attribute_3:
        seat = SeatVenue1Data.seat_v1_a2
        name = u'attr1'
        value = u'a2-attr2'

    class seat_attribute_4:
        seat = SeatVenue1Data.seat_v1_a2
        name = u'attr2'
        value = u'a2-attr2'

    class seat_attribute_5:
        seat = SeatVenue1Data.seat_v1_a3
        name = u'attr1'
        value = u'a3-attr2'

    class seat_attribute_6:
        seat = SeatVenue1Data.seat_v1_a3
        name = u'attr2'
        value = u'a3-attr2'

    class seat_attribute_7:
        seat = SeatVenue1Data.seat_v1_a4
        name = u'attr1'
        value = u'a4-attr2'

    class seat_attribute_8:
        seat = SeatVenue1Data.seat_v1_a4
        name = u'attr2'
        value = u'a4-attr2'

    class seat_attribute_9:
        seat = SeatVenue1Data.seat_v1_a5
        name = u'attr1'
        value = u'a5-attr2'

    class seat_attribute_10:
        seat = SeatVenue1Data.seat_v1_a5
        name = u'attr2'
        value = u'a5-attr2'

    class seat_attribute_11:
        seat = SeatVenue1Data.seat_v1_a6
        name = u'attr1'
        value = u'a6-attr2'

    class seat_attribute_12:
        seat = SeatVenue1Data.seat_v1_a6
        name = u'attr2'
        value = u'a6-attr2'

    class seat_attribute_13:
        seat = SeatVenue1Data.seat_v1_a7
        name = u'attr1'
        value = u'a7-attr2'

    class seat_attribute_14:
        seat = SeatVenue1Data.seat_v1_a7
        name = u'attr2'
        value = u'a7-attr2'

    class seat_attribute_15:
        seat = SeatVenue1Data.seat_v1_a8
        name = u'attr1'
        value = u'a8-attr2'

    class seat_attribute_16:
        seat = SeatVenue1Data.seat_v1_a8
        name = u'attr2'
        value = u'a8-attr2'

    class seat_attribute_17:
        seat = SeatVenue1Data.seat_v1_a9
        name = u'attr1'
        value = u'a9-attr2'

    class seat_attribute_18:
        seat = SeatVenue1Data.seat_v1_a9
        name = u'attr2'
        value = u'a9-attr2'

    class seat_attribute_19:
        seat = SeatVenue1Data.seat_v1_b1
        name = u'attr1'
        value = u'b1-attr2'

    class seat_attribute_20:
        seat = SeatVenue1Data.seat_v1_b1
        name = u'attr2'
        value = u'b1-attr2'

    class seat_attribute_21:
        seat = SeatVenue1Data.seat_v1_b2
        name = u'attr1'
        value = u'b2-attr2'

    class seat_attribute_22:
        seat = SeatVenue1Data.seat_v1_b2
        name = u'attr2'
        value = u'b2-attr2'

    class seat_attribute_23:
        seat = SeatVenue1Data.seat_v1_b3
        name = u'attr1'
        value = u'b3-attr2'

    class seat_attribute_24:
        seat = SeatVenue1Data.seat_v1_b3
        name = u'attr2'
        value = u'b3-attr2'

    class seat_attribute_25:
        seat = SeatVenue1Data.seat_v1_b4
        name = u'attr1'
        value = u'b4-attr2'

    class seat_attribute_26:
        seat = SeatVenue1Data.seat_v1_b4
        name = u'attr2'
        value = u'b4-attr2'

    class seat_attribute_27:
        seat = SeatVenue1Data.seat_v1_b5
        name = u'attr1'
        value = u'b5-attr2'

    class seat_attribute_28:
        seat = SeatVenue1Data.seat_v1_b5
        name = u'attr2'
        value = u'b5-attr2'

    class seat_attribute_29:
        seat = SeatVenue1Data.seat_v1_b6
        name = u'attr1'
        value = u'b6-attr2'

    class seat_attribute_30:
        seat = SeatVenue1Data.seat_v1_b6
        name = u'attr2'
        value = u'b6-attr2'

    class seat_attribute_31:
        seat = SeatVenue1Data.seat_v1_b7
        name = u'attr1'
        value = u'b7-attr2'

    class seat_attribute_32:
        seat = SeatVenue1Data.seat_v1_b7
        name = u'attr2'
        value = u'b7-attr2'

    class seat_attribute_33:
        seat = SeatVenue1Data.seat_v1_c1
        name = u'attr1'
        value = u'c1-attr2'

    class seat_attribute_34:
        seat = SeatVenue1Data.seat_v1_c1
        name = u'attr2'
        value = u'c1-attr2'

    class seat_attribute_35:
        seat = SeatVenue1Data.seat_v1_c2
        name = u'attr1'
        value = u'c2-attr2'

    class seat_attribute_36:
        seat = SeatVenue1Data.seat_v1_c2
        name = u'attr2'
        value = u'c2-attr2'

    class seat_attribute_37:
        seat = SeatVenue1Data.seat_v1_c3
        name = u'attr1'
        value = u'c3-attr2'

    class seat_attribute_38:
        seat = SeatVenue1Data.seat_v1_c3
        name = u'attr2'
        value = u'c3-attr2'

    class seat_attribute_39:
        seat = SeatVenue1Data.seat_v1_c4
        name = u'attr1'
        value = u'c4-attr2'

    class seat_attribute_40:
        seat = SeatVenue1Data.seat_v1_c4
        name = u'attr2'
        value = u'c4-attr2'

    class seat_attribute_41:
        seat = SeatVenue1Data.seat_v1_c5
        name = u'attr1'
        value = u'c5-attr2'

    class seat_attribute_42:
        seat = SeatVenue1Data.seat_v1_c5
        name = u'attr2'
        value = u'c5-attr2'

    class seat_attribute_43:
        seat = SeatVenue1Data.seat_v1_d1
        name = u'attr1'
        value = u'd1-attr2'

    class seat_attribute_44:
        seat = SeatVenue1Data.seat_v1_d1
        name = u'attr2'
        value = u'd1-attr2'

    class seat_attribute_45:
        seat = SeatVenue1Data.seat_v1_d2
        name = u'attr1'
        value = u'd2-attr2'

    class seat_attribute_46:
        seat = SeatVenue1Data.seat_v1_d2
        name = u'attr2'
        value = u'd2-attr2'

    class seat_attribute_47:
        seat = SeatVenue1Data.seat_v1_d3
        name = u'attr1'
        value = u'd3-attr2'

    class seat_attribute_48:
        seat = SeatVenue1Data.seat_v1_d3
        name = u'attr2'
        value = u'd3-attr2'

    class seat_attribute_49:
        seat = SeatVenue1Data.seat_v1_e1
        name = u'attr1'
        value = u'e1-attr2'

    class seat_attribute_50:
        seat = SeatVenue1Data.seat_v1_e1
        name = u'attr2'
        value = u'e1-attr2'

    class seat_attribute_51:
        seat = SeatVenue1Data.seat_v1_e2
        name = u'attr1'
        value = u'e2-attr2'

    class seat_attribute_52:
        seat = SeatVenue1Data.seat_v1_e2
        name = u'attr2'
        value = u'e2-attr2'

    class seat_attribute_53:
        seat = SeatVenue1Data.seat_v1_e3
        name = u'attr1'
        value = u'e3-attr2'

    class seat_attribute_54:
        seat = SeatVenue1Data.seat_v1_e3
        name = u'attr2'
        value = u'e3-attr2'

    class seat_attribute_55:
        seat = SeatVenue2Data.seat_v2_a1
        name = u'attr1'
        value = u'a1-attr2'

    class seat_attribute_56:
        seat = SeatVenue2Data.seat_v2_a1
        name = u'attr2'
        value = u'a1-attr2'

    class seat_attribute_57:
        seat = SeatVenue2Data.seat_v2_a2
        name = u'attr1'
        value = u'a2-attr2'

    class seat_attribute_58:
        seat = SeatVenue2Data.seat_v2_a2
        name = u'attr2'
        value = u'a2-attr2'

    class seat_attribute_59:
        seat = SeatVenue2Data.seat_v2_a3
        name = u'attr1'
        value = u'a3-attr2'

    class seat_attribute_60:
        seat = SeatVenue2Data.seat_v2_a3
        name = u'attr2'
        value = u'a3-attr2'

    class seat_attribute_61:
        seat = SeatVenue2Data.seat_v2_a4
        name = u'attr1'
        value = u'a4-attr2'

    class seat_attribute_62:
        seat = SeatVenue2Data.seat_v2_a4
        name = u'attr2'
        value = u'a4-attr2'

    class seat_attribute_63:
        seat = SeatVenue2Data.seat_v2_a5
        name = u'attr1'
        value = u'a5-attr2'

    class seat_attribute_64:
        seat = SeatVenue2Data.seat_v2_a5
        name = u'attr2'
        value = u'a5-attr2'

    class seat_attribute_65:
        seat = SeatVenue2Data.seat_v2_a6
        name = u'attr1'
        value = u'a6-attr2'

    class seat_attribute_66:
        seat = SeatVenue2Data.seat_v2_a6
        name = u'attr2'
        value = u'a6-attr2'

    class seat_attribute_67:
        seat = SeatVenue2Data.seat_v2_a7
        name = u'attr1'
        value = u'a7-attr2'

    class seat_attribute_68:
        seat = SeatVenue2Data.seat_v2_a7
        name = u'attr2'
        value = u'a7-attr2'

    class seat_attribute_69:
        seat = SeatVenue2Data.seat_v2_a8
        name = u'attr1'
        value = u'a8-attr2'

    class seat_attribute_70:
        seat = SeatVenue2Data.seat_v2_a8
        name = u'attr2'
        value = u'a8-attr2'

    class seat_attribute_71:
        seat = SeatVenue2Data.seat_v2_a9
        name = u'attr1'
        value = u'a9-attr2'

    class seat_attribute_72:
        seat = SeatVenue2Data.seat_v2_a9
        name = u'attr2'
        value = u'a9-attr2'

    class seat_attribute_73:
        seat = SeatVenue2Data.seat_v2_b1
        name = u'attr1'
        value = u'b1-attr2'

    class seat_attribute_74:
        seat = SeatVenue2Data.seat_v2_b1
        name = u'attr2'
        value = u'b1-attr2'

    class seat_attribute_75:
        seat = SeatVenue2Data.seat_v2_b2
        name = u'attr1'
        value = u'b2-attr2'

    class seat_attribute_76:
        seat = SeatVenue2Data.seat_v2_b2
        name = u'attr2'
        value = u'b2-attr2'

    class seat_attribute_77:
        seat = SeatVenue2Data.seat_v2_b3
        name = u'attr1'
        value = u'b3-attr2'

    class seat_attribute_78:
        seat = SeatVenue2Data.seat_v2_b3
        name = u'attr2'
        value = u'b3-attr2'

    class seat_attribute_79:
        seat = SeatVenue2Data.seat_v2_b4
        name = u'attr1'
        value = u'b4-attr2'

    class seat_attribute_80:
        seat = SeatVenue2Data.seat_v2_b4
        name = u'attr2'
        value = u'b4-attr2'

    class seat_attribute_81:
        seat = SeatVenue2Data.seat_v2_b5
        name = u'attr1'
        value = u'b5-attr2'

    class seat_attribute_82:
        seat = SeatVenue2Data.seat_v2_b5
        name = u'attr2'
        value = u'b5-attr2'

    class seat_attribute_83:
        seat = SeatVenue2Data.seat_v2_b6
        name = u'attr1'
        value = u'b6-attr2'

    class seat_attribute_84:
        seat = SeatVenue2Data.seat_v2_b6
        name = u'attr2'
        value = u'b6-attr2'

    class seat_attribute_85:
        seat = SeatVenue2Data.seat_v2_b7
        name = u'attr1'
        value = u'b7-attr2'

    class seat_attribute_86:
        seat = SeatVenue2Data.seat_v2_b7
        name = u'attr2'
        value = u'b7-attr2'

    class seat_attribute_87:
        seat = SeatVenue2Data.seat_v2_c1
        name = u'attr1'
        value = u'c1-attr2'

    class seat_attribute_88:
        seat = SeatVenue2Data.seat_v2_c1
        name = u'attr2'
        value = u'c1-attr2'

    class seat_attribute_89:
        seat = SeatVenue2Data.seat_v2_c2
        name = u'attr1'
        value = u'c2-attr2'

    class seat_attribute_90:
        seat = SeatVenue2Data.seat_v2_c2
        name = u'attr2'
        value = u'c2-attr2'

    class seat_attribute_91:
        seat = SeatVenue2Data.seat_v2_c3
        name = u'attr1'
        value = u'c3-attr2'

    class seat_attribute_92:
        seat = SeatVenue2Data.seat_v2_c3
        name = u'attr2'
        value = u'c3-attr2'

    class seat_attribute_93:
        seat = SeatVenue2Data.seat_v2_c4
        name = u'attr1'
        value = u'c4-attr2'

    class seat_attribute_94:
        seat = SeatVenue2Data.seat_v2_c4
        name = u'attr2'
        value = u'c4-attr2'

    class seat_attribute_95:
        seat = SeatVenue2Data.seat_v2_c5
        name = u'attr1'
        value = u'c5-attr2'

    class seat_attribute_96:
        seat = SeatVenue2Data.seat_v2_c5
        name = u'attr2'
        value = u'c5-attr2'

    class seat_attribute_97:
        seat = SeatVenue2Data.seat_v2_d1
        name = u'attr1'
        value = u'd1-attr2'

    class seat_attribute_98:
        seat = SeatVenue2Data.seat_v2_d1
        name = u'attr2'
        value = u'd1-attr2'

    class seat_attribute_99:
        seat = SeatVenue2Data.seat_v2_d2
        name = u'attr1'
        value = u'd2-attr2'

    class seat_attribute_100:
        seat = SeatVenue2Data.seat_v2_d2
        name = u'attr2'
        value = u'd2-attr2'

    class seat_attribute_101:
        seat = SeatVenue2Data.seat_v2_d3
        name = u'attr1'
        value = u'd3-attr2'

    class seat_attribute_102:
        seat = SeatVenue2Data.seat_v2_d3
        name = u'attr2'
        value = u'd3-attr2'

    class seat_attribute_103:
        seat = SeatVenue2Data.seat_v2_e1
        name = u'attr1'
        value = u'e1-attr2'

    class seat_attribute_104:
        seat = SeatVenue2Data.seat_v2_e1
        name = u'attr2'
        value = u'e1-attr2'

    class seat_attribute_105:
        seat = SeatVenue2Data.seat_v2_e2
        name = u'attr1'
        value = u'e2-attr2'

    class seat_attribute_106:
        seat = SeatVenue2Data.seat_v2_e2
        name = u'attr2'
        value = u'e2-attr2'

    class seat_attribute_107:
        seat = SeatVenue2Data.seat_v2_e3
        name = u'attr1'
        value = u'e3-attr2'

    class seat_attribute_108:
        seat = SeatVenue2Data.seat_v2_e3
        name = u'attr2'
        value = u'e3-attr2'

