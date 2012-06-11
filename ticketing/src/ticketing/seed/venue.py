# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from ticketing.core.models import SeatStatusEnum, VenueArea, VenueArea_group_l0_id

from .event import PerformanceEvent1Data, PerformanceEvent2Data
from .product import *
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
        drawing_url = u'file:src/ticketing/static/site-data/sample.svg'

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
        drawing_url = u'file:src/ticketing/static/site-data/sample.svg'

class TemplateVenueData(DataSet):
    class venue_orig_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = None
        site = SiteData.site_1
        organization = OrganizationData.organization_0
    class venue_orig_2:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = None
        site = SiteData.site_2
        organization = OrganizationData.organization_0

class VenueEvent1Data(DataSet):
    class venue_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceEvent1Data.performance_1
        site = SiteData.site_1
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_1
    class venue_2:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceEvent1Data.performance_2
        site = SiteData.site_1
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_1
    class venue_3:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceEvent1Data.performance_3
        site = SiteData.site_1
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_1
    class venue_4:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceEvent1Data.performance_4
        site = SiteData.site_1
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_1
    class venue_5:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）'
        sub_name = u'シルク・ドゥ・ソレイユ　シアター'
        performance = PerformanceEvent1Data.performance_5
        site = SiteData.site_1
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_1

class VenueEvent2Data(DataSet):
    class venue_1:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = PerformanceEvent2Data.performance_1
        site = SiteData.site_2
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_2
    class venue_2:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = PerformanceEvent2Data.performance_2
        site = SiteData.site_2
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_2
    class venue_3:
        name = u'ブルーマンシアター'
        sub_name = u'ブルーマンシアター'
        performance = PerformanceEvent2Data.performance_3
        site = SiteData.site_2
        organization = OrganizationData.organization_0
        original_venue = TemplateVenueData.venue_orig_2

class TemplateSeatVenue1Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a2:
        l0_id = u'A2'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a3:
        l0_id = u'A3'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a4:
        l0_id = u'A4'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a5:
        l0_id = u'A5'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a6:
        l0_id = u'A6'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a7:
        l0_id = u'A7'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a8:
        l0_id = u'A8'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_a9:
        l0_id = u'A9'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b1:
        l0_id = u'B1'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b2:
        l0_id = u'B2'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b3:
        l0_id = u'B3'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b4:
        l0_id = u'B4'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b5:
        l0_id = u'B5'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b6:
        l0_id = u'B6'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_b7:
        l0_id = u'B7'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_c1:
        l0_id = u'C1'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_c2:
        l0_id = u'C2'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_c3:
        l0_id = u'C3'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_c4:
        l0_id = u'C4'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_c5:
        l0_id = u'C5'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class seat_d1:
        l0_id = u'D1'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3078'
    class seat_d2:
        l0_id = u'D2'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3078'
    class seat_d3:
        l0_id = u'D3'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3078'
    class seat_e1:
        l0_id = u'E1'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3071'
    class seat_e2:
        l0_id = u'E2'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3071'
    class seat_e3:
        l0_id = u'E3'
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3071'

class TemplateSeatVenue2Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a2:
        l0_id = u'A2'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a3:
        l0_id = u'A3'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a4:
        l0_id = u'A4'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a5:
        l0_id = u'A5'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a6:
        l0_id = u'A6'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a7:
        l0_id = u'A7'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a8:
        l0_id = u'A8'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_a9:
        l0_id = u'A9'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b1:
        l0_id = u'B1'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b2:
        l0_id = u'B2'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b3:
        l0_id = u'B3'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b4:
        l0_id = u'B4'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b5:
        l0_id = u'B5'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b6:
        l0_id = u'B6'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_b7:
        l0_id = u'B7'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_c1:
        l0_id = u'C1'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_c2:
        l0_id = u'C2'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_c3:
        l0_id = u'C3'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_c4:
        l0_id = u'C4'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_c5:
        l0_id = u'C5'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class seat_d1:
        l0_id = u'D1'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3078'
    class seat_d2:
        l0_id = u'D2'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3078'
    class seat_d3:
        l0_id = u'D3'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3078'
    class seat_e1:
        l0_id = u'E1'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3071'
    class seat_e2:
        l0_id = u'E2'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3071'
    class seat_e3:
        l0_id = u'E3'
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3071'

class SeatEvent1Venue1Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_6
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_6
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_6
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_6
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_7
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_7
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
        stock = StockEvent1Performance1Data.stock_7
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3078'
        stock = StockEvent1Performance1Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3078'
        stock = StockEvent1Performance1Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3078'
        stock = StockEvent1Performance1Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3071'
        stock = StockEvent1Performance1Data.stock_8
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3071'
        stock = StockEvent1Performance1Data.stock_8
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3071'
        stock = StockEvent1Performance1Data.stock_8
        stock_type = StockTypeEvent1Data.stock_type_4

class SeatEvent1Venue2Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4

class SeatEvent1Venue3Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4

class SeatEvent1Venue4Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4

class SeatEvent1Venue5Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent1Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent1Data.stock_type_4

class SeatEvent2Venue1Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4

class SeatEvent2Venue2Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4

class SeatEvent2Venue3Data(DataSet):
    class seat_a1:
        l0_id = u'A1'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a2:
        l0_id = u'A2'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a3:
        l0_id = u'A3'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a4:
        l0_id = u'A4'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a5:
        l0_id = u'A5'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a6:
        l0_id = u'A6'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a7:
        l0_id = u'A7'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a8:
        l0_id = u'A8'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_a9:
        l0_id = u'A9'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_1
    class seat_b1:
        l0_id = u'B1'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b2:
        l0_id = u'B2'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b3:
        l0_id = u'B3'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b4:
        l0_id = u'B4'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b5:
        l0_id = u'B5'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b6:
        l0_id = u'B6'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_b7:
        l0_id = u'B7'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_2
    class seat_c1:
        l0_id = u'C1'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c2:
        l0_id = u'C2'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c3:
        l0_id = u'C3'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c4:
        l0_id = u'C4'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_c5:
        l0_id = u'C5'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
        stock_type = StockTypeEvent2Data.stock_type_3
    class seat_d1:
        l0_id = u'D1'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_d2:
        l0_id = u'D2'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_d3:
        l0_id = u'D3'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3078'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e1:
        l0_id = u'E1'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e2:
        l0_id = u'E2'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4
    class seat_e3:
        l0_id = u'E3'
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3071'
        stock_type = StockTypeEvent2Data.stock_type_4

class SeatStatusEvent1Venue1Data(DataSet):
    class seat_status_v1_1:
        seat = SeatEvent1Venue1Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_2:
        seat = SeatEvent1Venue1Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v1_3:
        seat = SeatEvent1Venue1Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v1_4:
        seat = SeatEvent1Venue1Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v1_5:
        seat = SeatEvent1Venue1Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v1_6:
        seat = SeatEvent1Venue1Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v1_7:
        seat = SeatEvent1Venue1Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_8:
        seat = SeatEvent1Venue1Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_9:
        seat = SeatEvent1Venue1Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v1_10:
        seat = SeatEvent1Venue1Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_11:
        seat = SeatEvent1Venue1Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_12:
        seat = SeatEvent1Venue1Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_13:
        seat = SeatEvent1Venue1Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_14:
        seat = SeatEvent1Venue1Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_15:
        seat = SeatEvent1Venue1Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_16:
        seat = SeatEvent1Venue1Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_17:
        seat = SeatEvent1Venue1Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_18:
        seat = SeatEvent1Venue1Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_19:
        seat = SeatEvent1Venue1Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_20:
        seat = SeatEvent1Venue1Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_21:
        seat = SeatEvent1Venue1Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_22:
        seat = SeatEvent1Venue1Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_23:
        seat = SeatEvent1Venue1Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_24:
        seat = SeatEvent1Venue1Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_25:
        seat = SeatEvent1Venue1Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_26:
        seat = SeatEvent1Venue1Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_27:
        seat = SeatEvent1Venue1Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent1Venue2Data(DataSet):
    class seat_status_v2_1:
        seat = SeatEvent1Venue2Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_2:
        seat = SeatEvent1Venue2Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v2_3:
        seat = SeatEvent1Venue2Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v2_4:
        seat = SeatEvent1Venue2Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v2_5:
        seat = SeatEvent1Venue2Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v2_6:
        seat = SeatEvent1Venue2Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v2_7:
        seat = SeatEvent1Venue2Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_8:
        seat = SeatEvent1Venue2Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_9:
        seat = SeatEvent1Venue2Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v2_10:
        seat = SeatEvent1Venue2Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_11:
        seat = SeatEvent1Venue2Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_12:
        seat = SeatEvent1Venue2Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_13:
        seat = SeatEvent1Venue2Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_14:
        seat = SeatEvent1Venue2Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_15:
        seat = SeatEvent1Venue2Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_16:
        seat = SeatEvent1Venue2Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_17:
        seat = SeatEvent1Venue2Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_18:
        seat = SeatEvent1Venue2Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_19:
        seat = SeatEvent1Venue2Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_20:
        seat = SeatEvent1Venue2Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_21:
        seat = SeatEvent1Venue2Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_22:
        seat = SeatEvent1Venue2Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_23:
        seat = SeatEvent1Venue2Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_24:
        seat = SeatEvent1Venue2Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_25:
        seat = SeatEvent1Venue2Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_26:
        seat = SeatEvent1Venue2Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_27:
        seat = SeatEvent1Venue2Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent1Venue3Data(DataSet):
    class seat_status_v3_1:
        seat = SeatEvent1Venue3Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_2:
        seat = SeatEvent1Venue3Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v3_3:
        seat = SeatEvent1Venue3Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v3_4:
        seat = SeatEvent1Venue3Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v3_5:
        seat = SeatEvent1Venue3Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v3_6:
        seat = SeatEvent1Venue3Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v3_7:
        seat = SeatEvent1Venue3Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_8:
        seat = SeatEvent1Venue3Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_9:
        seat = SeatEvent1Venue3Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v3_10:
        seat = SeatEvent1Venue3Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_11:
        seat = SeatEvent1Venue3Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_12:
        seat = SeatEvent1Venue3Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_13:
        seat = SeatEvent1Venue3Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_14:
        seat = SeatEvent1Venue3Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_15:
        seat = SeatEvent1Venue3Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_16:
        seat = SeatEvent1Venue3Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_17:
        seat = SeatEvent1Venue3Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_18:
        seat = SeatEvent1Venue3Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_19:
        seat = SeatEvent1Venue3Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_20:
        seat = SeatEvent1Venue3Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_21:
        seat = SeatEvent1Venue3Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_22:
        seat = SeatEvent1Venue3Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_23:
        seat = SeatEvent1Venue3Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_24:
        seat = SeatEvent1Venue3Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_25:
        seat = SeatEvent1Venue3Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_26:
        seat = SeatEvent1Venue3Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_27:
        seat = SeatEvent1Venue3Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent1Venue4Data(DataSet):
    class seat_status_v4_1:
        seat = SeatEvent1Venue4Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_2:
        seat = SeatEvent1Venue4Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v4_3:
        seat = SeatEvent1Venue4Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v4_4:
        seat = SeatEvent1Venue4Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v4_5:
        seat = SeatEvent1Venue4Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v4_6:
        seat = SeatEvent1Venue4Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v4_7:
        seat = SeatEvent1Venue4Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_8:
        seat = SeatEvent1Venue4Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_9:
        seat = SeatEvent1Venue4Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v4_10:
        seat = SeatEvent1Venue4Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_11:
        seat = SeatEvent1Venue4Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_12:
        seat = SeatEvent1Venue4Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_13:
        seat = SeatEvent1Venue4Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_14:
        seat = SeatEvent1Venue4Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_15:
        seat = SeatEvent1Venue4Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_16:
        seat = SeatEvent1Venue4Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_17:
        seat = SeatEvent1Venue4Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_18:
        seat = SeatEvent1Venue4Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_19:
        seat = SeatEvent1Venue4Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_20:
        seat = SeatEvent1Venue4Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_21:
        seat = SeatEvent1Venue4Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_22:
        seat = SeatEvent1Venue4Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_23:
        seat = SeatEvent1Venue4Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_24:
        seat = SeatEvent1Venue4Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_25:
        seat = SeatEvent1Venue4Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_26:
        seat = SeatEvent1Venue4Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v4_27:
        seat = SeatEvent1Venue4Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent1Venue5Data(DataSet):
    class seat_status_v5_1:
        seat = SeatEvent1Venue5Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_2:
        seat = SeatEvent1Venue5Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v5_3:
        seat = SeatEvent1Venue5Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v5_4:
        seat = SeatEvent1Venue5Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v5_5:
        seat = SeatEvent1Venue5Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v5_6:
        seat = SeatEvent1Venue5Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v5_7:
        seat = SeatEvent1Venue5Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_8:
        seat = SeatEvent1Venue5Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_9:
        seat = SeatEvent1Venue5Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v5_10:
        seat = SeatEvent1Venue5Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_11:
        seat = SeatEvent1Venue5Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_12:
        seat = SeatEvent1Venue5Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_13:
        seat = SeatEvent1Venue5Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_14:
        seat = SeatEvent1Venue5Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_15:
        seat = SeatEvent1Venue5Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_16:
        seat = SeatEvent1Venue5Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_17:
        seat = SeatEvent1Venue5Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_18:
        seat = SeatEvent1Venue5Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_19:
        seat = SeatEvent1Venue5Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_20:
        seat = SeatEvent1Venue5Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_21:
        seat = SeatEvent1Venue5Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_22:
        seat = SeatEvent1Venue5Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_23:
        seat = SeatEvent1Venue5Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_24:
        seat = SeatEvent1Venue5Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_25:
        seat = SeatEvent1Venue5Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_26:
        seat = SeatEvent1Venue5Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v5_27:
        seat = SeatEvent1Venue5Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent2Venue1Data(DataSet):
    class seat_status_v1_1:
        seat = SeatEvent2Venue1Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_2:
        seat = SeatEvent2Venue1Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v1_3:
        seat = SeatEvent2Venue1Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v1_4:
        seat = SeatEvent2Venue1Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v1_5:
        seat = SeatEvent2Venue1Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v1_6:
        seat = SeatEvent2Venue1Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v1_7:
        seat = SeatEvent2Venue1Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_8:
        seat = SeatEvent2Venue1Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_9:
        seat = SeatEvent2Venue1Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v1_10:
        seat = SeatEvent2Venue1Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_11:
        seat = SeatEvent2Venue1Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_12:
        seat = SeatEvent2Venue1Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_13:
        seat = SeatEvent2Venue1Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_14:
        seat = SeatEvent2Venue1Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_15:
        seat = SeatEvent2Venue1Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_16:
        seat = SeatEvent2Venue1Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_17:
        seat = SeatEvent2Venue1Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_18:
        seat = SeatEvent2Venue1Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_19:
        seat = SeatEvent2Venue1Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_20:
        seat = SeatEvent2Venue1Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_21:
        seat = SeatEvent2Venue1Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_22:
        seat = SeatEvent2Venue1Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_23:
        seat = SeatEvent2Venue1Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_24:
        seat = SeatEvent2Venue1Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_25:
        seat = SeatEvent2Venue1Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_26:
        seat = SeatEvent2Venue1Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v1_27:
        seat = SeatEvent2Venue1Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent2Venue2Data(DataSet):
    class seat_status_v2_1:
        seat = SeatEvent2Venue2Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_2:
        seat = SeatEvent2Venue2Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v2_3:
        seat = SeatEvent2Venue2Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v2_4:
        seat = SeatEvent2Venue2Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v2_5:
        seat = SeatEvent2Venue2Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v2_6:
        seat = SeatEvent2Venue2Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v2_7:
        seat = SeatEvent2Venue2Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_8:
        seat = SeatEvent2Venue2Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_9:
        seat = SeatEvent2Venue2Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v2_10:
        seat = SeatEvent2Venue2Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_11:
        seat = SeatEvent2Venue2Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_12:
        seat = SeatEvent2Venue2Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_13:
        seat = SeatEvent2Venue2Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_14:
        seat = SeatEvent2Venue2Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_15:
        seat = SeatEvent2Venue2Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_16:
        seat = SeatEvent2Venue2Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_17:
        seat = SeatEvent2Venue2Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_18:
        seat = SeatEvent2Venue2Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_19:
        seat = SeatEvent2Venue2Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_20:
        seat = SeatEvent2Venue2Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_21:
        seat = SeatEvent2Venue2Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_22:
        seat = SeatEvent2Venue2Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_23:
        seat = SeatEvent2Venue2Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_24:
        seat = SeatEvent2Venue2Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_25:
        seat = SeatEvent2Venue2Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_26:
        seat = SeatEvent2Venue2Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v2_27:
        seat = SeatEvent2Venue2Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class SeatStatusEvent2Venue3Data(DataSet):
    class seat_status_v3_1:
        seat = SeatEvent2Venue3Data.seat_a1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_2:
        seat = SeatEvent2Venue3Data.seat_a2
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v3_3:
        seat = SeatEvent2Venue3Data.seat_a3
        status = int(SeatStatusEnum.Reserved)
    class seat_status_v3_4:
        seat = SeatEvent2Venue3Data.seat_a4
        status = int(SeatStatusEnum.InCart)
    class seat_status_v3_5:
        seat = SeatEvent2Venue3Data.seat_a5
        status = int(SeatStatusEnum.Confirmed)
    class seat_status_v3_6:
        seat = SeatEvent2Venue3Data.seat_a6
        status = int(SeatStatusEnum.Shipped)
    class seat_status_v3_7:
        seat = SeatEvent2Venue3Data.seat_a7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_8:
        seat = SeatEvent2Venue3Data.seat_a8
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_9:
        seat = SeatEvent2Venue3Data.seat_a9
        status = int(SeatStatusEnum.Ordered)
    class seat_status_v3_10:
        seat = SeatEvent2Venue3Data.seat_b1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_11:
        seat = SeatEvent2Venue3Data.seat_b2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_12:
        seat = SeatEvent2Venue3Data.seat_b3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_13:
        seat = SeatEvent2Venue3Data.seat_b4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_14:
        seat = SeatEvent2Venue3Data.seat_b5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_15:
        seat = SeatEvent2Venue3Data.seat_b6
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_16:
        seat = SeatEvent2Venue3Data.seat_b7
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_17:
        seat = SeatEvent2Venue3Data.seat_c1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_18:
        seat = SeatEvent2Venue3Data.seat_c2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_19:
        seat = SeatEvent2Venue3Data.seat_c3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_20:
        seat = SeatEvent2Venue3Data.seat_c4
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_21:
        seat = SeatEvent2Venue3Data.seat_c5
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_22:
        seat = SeatEvent2Venue3Data.seat_d1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_23:
        seat = SeatEvent2Venue3Data.seat_d2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_24:
        seat = SeatEvent2Venue3Data.seat_d3
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_25:
        seat = SeatEvent2Venue3Data.seat_e1
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_26:
        seat = SeatEvent2Venue3Data.seat_e2
        status = int(SeatStatusEnum.Vacant)
    class seat_status_v3_27:
        seat = SeatEvent2Venue3Data.seat_e3
        status = int(SeatStatusEnum.Vacant)

class VenueArea_group_l0_idData(DataSet):
    class venue_area_group_l0_id_vo1_1_1:
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_vo1_2_1:
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_vo1_2_2:
        venue = TemplateVenueData.venue_orig_1
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_vo2_1_1:
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_vo2_2_1:
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_vo2_2_2:
        venue = TemplateVenueData.venue_orig_2
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e1_v1_1_1:
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e1_v1_2_1:
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e1_v1_2_2:
        venue = VenueEvent1Data.venue_1
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e1_v2_1_1:
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e1_v2_2_1:
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e1_v2_2_2:
        venue = VenueEvent1Data.venue_2
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e1_v3_1_1:
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e1_v3_2_1:
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e1_v3_2_2:
        venue = VenueEvent1Data.venue_3
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e1_v4_1_1:
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e1_v4_2_1:
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e1_v4_2_2:
        venue = VenueEvent1Data.venue_4
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e1_v5_1_1:
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e1_v5_2_1:
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e1_v5_2_2:
        venue = VenueEvent1Data.venue_5
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e2_v1_1_1:
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e2_v1_2_1:
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e2_v1_2_2:
        venue = VenueEvent2Data.venue_1
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e2_v2_1_1:
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e2_v2_2_1:
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e2_v2_2_2:
        venue = VenueEvent2Data.venue_2
        group_l0_id = u'g3071'
    class venue_area_group_l0_id_e2_v3_1_1:
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3835'
    class venue_area_group_l0_id_e2_v3_2_1:
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3078'
    class venue_area_group_l0_id_e2_v3_2_2:
        venue = VenueEvent2Data.venue_3
        group_l0_id = u'g3071'

class VenueAreaTemplateVenue1Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_vo1_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_vo1_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_vo1_2_2,
            ]

class VenueAreaTemplateVenue2Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_vo2_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_vo2_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_vo2_2_2,
            ]

class VenueAreaEvent1Venue1Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v1_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v1_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v1_2_2,
            ]

class VenueAreaEvent1Venue2Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v2_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v2_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v2_2_2,
            ]

class VenueAreaEvent1Venue3Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v3_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v3_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v3_2_2,
            ]

class VenueAreaEvent1Venue4Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v4_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v4_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v4_2_2,
            ]

class VenueAreaEvent1Venue5Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v5_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v5_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e1_v5_2_2,
            ]

class VenueAreaEvent2Venue1Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v1_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v1_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v1_2_2,
            ]

class VenueAreaEvent2Venue2Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v2_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v2_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v2_2_2,
            ]

class VenueAreaEvent2Venue3Data(DataSet):
    class venue_area_1:
        name = u'Aブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v3_1_1,
            ]

    class venue_area_2:
        name = u'Bブロック'
        groups = [
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v3_2_1,
            VenueArea_group_l0_idData.venue_area_group_l0_id_e2_v3_2_2,
            ]

class SeatAttributeData(DataSet):
    class seat_attribute_1:
        seat = SeatEvent1Venue1Data.seat_a1
        name = u'attr1'
        value = u'a1-attr2'
    class seat_attribute_2:
        seat = SeatEvent1Venue1Data.seat_a1
        name = u'attr2'
        value = u'a1-attr2'
    class seat_attribute_3:
        seat = SeatEvent1Venue1Data.seat_a2
        name = u'attr1'
        value = u'a2-attr2'
    class seat_attribute_4:
        seat = SeatEvent1Venue1Data.seat_a2
        name = u'attr2'
        value = u'a2-attr2'
    class seat_attribute_5:
        seat = SeatEvent1Venue1Data.seat_a3
        name = u'attr1'
        value = u'a3-attr2'
    class seat_attribute_6:
        seat = SeatEvent1Venue1Data.seat_a3
        name = u'attr2'
        value = u'a3-attr2'
    class seat_attribute_7:
        seat = SeatEvent1Venue1Data.seat_a4
        name = u'attr1'
        value = u'a4-attr2'
    class seat_attribute_8:
        seat = SeatEvent1Venue1Data.seat_a4
        name = u'attr2'
        value = u'a4-attr2'
    class seat_attribute_9:
        seat = SeatEvent1Venue1Data.seat_a5
        name = u'attr1'
        value = u'a5-attr2'
    class seat_attribute_10:
        seat = SeatEvent1Venue1Data.seat_a5
        name = u'attr2'
        value = u'a5-attr2'
    class seat_attribute_11:
        seat = SeatEvent1Venue1Data.seat_a6
        name = u'attr1'
        value = u'a6-attr2'
    class seat_attribute_12:
        seat = SeatEvent1Venue1Data.seat_a6
        name = u'attr2'
        value = u'a6-attr2'
    class seat_attribute_13:
        seat = SeatEvent1Venue1Data.seat_a7
        name = u'attr1'
        value = u'a7-attr2'
    class seat_attribute_14:
        seat = SeatEvent1Venue1Data.seat_a7
        name = u'attr2'
        value = u'a7-attr2'
    class seat_attribute_15:
        seat = SeatEvent1Venue1Data.seat_a8
        name = u'attr1'
        value = u'a8-attr2'
    class seat_attribute_16:
        seat = SeatEvent1Venue1Data.seat_a8
        name = u'attr2'
        value = u'a8-attr2'
    class seat_attribute_17:
        seat = SeatEvent1Venue1Data.seat_a9
        name = u'attr1'
        value = u'a9-attr2'
    class seat_attribute_18:
        seat = SeatEvent1Venue1Data.seat_a9
        name = u'attr2'
        value = u'a9-attr2'
    class seat_attribute_19:
        seat = SeatEvent1Venue1Data.seat_b1
        name = u'attr1'
        value = u'b1-attr2'
    class seat_attribute_20:
        seat = SeatEvent1Venue1Data.seat_b1
        name = u'attr2'
        value = u'b1-attr2'
    class seat_attribute_21:
        seat = SeatEvent1Venue1Data.seat_b2
        name = u'attr1'
        value = u'b2-attr2'
    class seat_attribute_22:
        seat = SeatEvent1Venue1Data.seat_b2
        name = u'attr2'
        value = u'b2-attr2'
    class seat_attribute_23:
        seat = SeatEvent1Venue1Data.seat_b3
        name = u'attr1'
        value = u'b3-attr2'
    class seat_attribute_24:
        seat = SeatEvent1Venue1Data.seat_b3
        name = u'attr2'
        value = u'b3-attr2'
    class seat_attribute_25:
        seat = SeatEvent1Venue1Data.seat_b4
        name = u'attr1'
        value = u'b4-attr2'
    class seat_attribute_26:
        seat = SeatEvent1Venue1Data.seat_b4
        name = u'attr2'
        value = u'b4-attr2'
    class seat_attribute_27:
        seat = SeatEvent1Venue1Data.seat_b5
        name = u'attr1'
        value = u'b5-attr2'
    class seat_attribute_28:
        seat = SeatEvent1Venue1Data.seat_b5
        name = u'attr2'
        value = u'b5-attr2'
    class seat_attribute_29:
        seat = SeatEvent1Venue1Data.seat_b6
        name = u'attr1'
        value = u'b6-attr2'
    class seat_attribute_30:
        seat = SeatEvent1Venue1Data.seat_b6
        name = u'attr2'
        value = u'b6-attr2'
    class seat_attribute_31:
        seat = SeatEvent1Venue1Data.seat_b7
        name = u'attr1'
        value = u'b7-attr2'
    class seat_attribute_32:
        seat = SeatEvent1Venue1Data.seat_b7
        name = u'attr2'
        value = u'b7-attr2'
    class seat_attribute_33:
        seat = SeatEvent1Venue1Data.seat_c1
        name = u'attr1'
        value = u'c1-attr2'
    class seat_attribute_34:
        seat = SeatEvent1Venue1Data.seat_c1
        name = u'attr2'
        value = u'c1-attr2'
    class seat_attribute_35:
        seat = SeatEvent1Venue1Data.seat_c2
        name = u'attr1'
        value = u'c2-attr2'
    class seat_attribute_36:
        seat = SeatEvent1Venue1Data.seat_c2
        name = u'attr2'
        value = u'c2-attr2'
    class seat_attribute_37:
        seat = SeatEvent1Venue1Data.seat_c3
        name = u'attr1'
        value = u'c3-attr2'
    class seat_attribute_38:
        seat = SeatEvent1Venue1Data.seat_c3
        name = u'attr2'
        value = u'c3-attr2'
    class seat_attribute_39:
        seat = SeatEvent1Venue1Data.seat_c4
        name = u'attr1'
        value = u'c4-attr2'
    class seat_attribute_40:
        seat = SeatEvent1Venue1Data.seat_c4
        name = u'attr2'
        value = u'c4-attr2'
    class seat_attribute_41:
        seat = SeatEvent1Venue1Data.seat_c5
        name = u'attr1'
        value = u'c5-attr2'
    class seat_attribute_42:
        seat = SeatEvent1Venue1Data.seat_c5
        name = u'attr2'
        value = u'c5-attr2'
    class seat_attribute_43:
        seat = SeatEvent1Venue1Data.seat_d1
        name = u'attr1'
        value = u'd1-attr2'
    class seat_attribute_44:
        seat = SeatEvent1Venue1Data.seat_d1
        name = u'attr2'
        value = u'd1-attr2'
    class seat_attribute_45:
        seat = SeatEvent1Venue1Data.seat_d2
        name = u'attr1'
        value = u'd2-attr2'
    class seat_attribute_46:
        seat = SeatEvent1Venue1Data.seat_d2
        name = u'attr2'
        value = u'd2-attr2'
    class seat_attribute_47:
        seat = SeatEvent1Venue1Data.seat_d3
        name = u'attr1'
        value = u'd3-attr2'
    class seat_attribute_48:
        seat = SeatEvent1Venue1Data.seat_d3
        name = u'attr2'
        value = u'd3-attr2'
    class seat_attribute_49:
        seat = SeatEvent1Venue1Data.seat_e1
        name = u'attr1'
        value = u'e1-attr2'
    class seat_attribute_50:
        seat = SeatEvent1Venue1Data.seat_e1
        name = u'attr2'
        value = u'e1-attr2'
    class seat_attribute_51:
        seat = SeatEvent1Venue1Data.seat_e2
        name = u'attr1'
        value = u'e2-attr2'
    class seat_attribute_52:
        seat = SeatEvent1Venue1Data.seat_e2
        name = u'attr2'
        value = u'e2-attr2'
    class seat_attribute_53:
        seat = SeatEvent1Venue1Data.seat_e3
        name = u'attr1'
        value = u'e3-attr2'
    class seat_attribute_54:
        seat = SeatEvent1Venue1Data.seat_e3
        name = u'attr2'
        value = u'e3-attr2'
    class seat_attribute_55:
        seat = SeatEvent1Venue2Data.seat_a1
        name = u'attr1'
        value = u'a1-attr2'
    class seat_attribute_56:
        seat = SeatEvent1Venue2Data.seat_a1
        name = u'attr2'
        value = u'a1-attr2'
    class seat_attribute_57:
        seat = SeatEvent1Venue2Data.seat_a2
        name = u'attr1'
        value = u'a2-attr2'
    class seat_attribute_58:
        seat = SeatEvent1Venue2Data.seat_a2
        name = u'attr2'
        value = u'a2-attr2'
    class seat_attribute_59:
        seat = SeatEvent1Venue2Data.seat_a3
        name = u'attr1'
        value = u'a3-attr2'
    class seat_attribute_60:
        seat = SeatEvent1Venue2Data.seat_a3
        name = u'attr2'
        value = u'a3-attr2'
    class seat_attribute_61:
        seat = SeatEvent1Venue2Data.seat_a4
        name = u'attr1'
        value = u'a4-attr2'
    class seat_attribute_62:
        seat = SeatEvent1Venue2Data.seat_a4
        name = u'attr2'
        value = u'a4-attr2'
    class seat_attribute_63:
        seat = SeatEvent1Venue2Data.seat_a5
        name = u'attr1'
        value = u'a5-attr2'
    class seat_attribute_64:
        seat = SeatEvent1Venue2Data.seat_a5
        name = u'attr2'
        value = u'a5-attr2'
    class seat_attribute_65:
        seat = SeatEvent1Venue2Data.seat_a6
        name = u'attr1'
        value = u'a6-attr2'
    class seat_attribute_66:
        seat = SeatEvent1Venue2Data.seat_a6
        name = u'attr2'
        value = u'a6-attr2'
    class seat_attribute_67:
        seat = SeatEvent1Venue2Data.seat_a7
        name = u'attr1'
        value = u'a7-attr2'
    class seat_attribute_68:
        seat = SeatEvent1Venue2Data.seat_a7
        name = u'attr2'
        value = u'a7-attr2'
    class seat_attribute_69:
        seat = SeatEvent1Venue2Data.seat_a8
        name = u'attr1'
        value = u'a8-attr2'
    class seat_attribute_70:
        seat = SeatEvent1Venue2Data.seat_a8
        name = u'attr2'
        value = u'a8-attr2'
    class seat_attribute_71:
        seat = SeatEvent1Venue2Data.seat_a9
        name = u'attr1'
        value = u'a9-attr2'
    class seat_attribute_72:
        seat = SeatEvent1Venue2Data.seat_a9
        name = u'attr2'
        value = u'a9-attr2'
    class seat_attribute_73:
        seat = SeatEvent1Venue2Data.seat_b1
        name = u'attr1'
        value = u'b1-attr2'
    class seat_attribute_74:
        seat = SeatEvent1Venue2Data.seat_b1
        name = u'attr2'
        value = u'b1-attr2'
    class seat_attribute_75:
        seat = SeatEvent1Venue2Data.seat_b2
        name = u'attr1'
        value = u'b2-attr2'
    class seat_attribute_76:
        seat = SeatEvent1Venue2Data.seat_b2
        name = u'attr2'
        value = u'b2-attr2'
    class seat_attribute_77:
        seat = SeatEvent1Venue2Data.seat_b3
        name = u'attr1'
        value = u'b3-attr2'
    class seat_attribute_78:
        seat = SeatEvent1Venue2Data.seat_b3
        name = u'attr2'
        value = u'b3-attr2'
    class seat_attribute_79:
        seat = SeatEvent1Venue2Data.seat_b4
        name = u'attr1'
        value = u'b4-attr2'
    class seat_attribute_80:
        seat = SeatEvent1Venue2Data.seat_b4
        name = u'attr2'
        value = u'b4-attr2'
    class seat_attribute_81:
        seat = SeatEvent1Venue2Data.seat_b5
        name = u'attr1'
        value = u'b5-attr2'
    class seat_attribute_82:
        seat = SeatEvent1Venue2Data.seat_b5
        name = u'attr2'
        value = u'b5-attr2'
    class seat_attribute_83:
        seat = SeatEvent1Venue2Data.seat_b6
        name = u'attr1'
        value = u'b6-attr2'
    class seat_attribute_84:
        seat = SeatEvent1Venue2Data.seat_b6
        name = u'attr2'
        value = u'b6-attr2'
    class seat_attribute_85:
        seat = SeatEvent1Venue2Data.seat_b7
        name = u'attr1'
        value = u'b7-attr2'
    class seat_attribute_86:
        seat = SeatEvent1Venue2Data.seat_b7
        name = u'attr2'
        value = u'b7-attr2'
    class seat_attribute_87:
        seat = SeatEvent1Venue2Data.seat_c1
        name = u'attr1'
        value = u'c1-attr2'
    class seat_attribute_88:
        seat = SeatEvent1Venue2Data.seat_c1
        name = u'attr2'
        value = u'c1-attr2'
    class seat_attribute_89:
        seat = SeatEvent1Venue2Data.seat_c2
        name = u'attr1'
        value = u'c2-attr2'
    class seat_attribute_90:
        seat = SeatEvent1Venue2Data.seat_c2
        name = u'attr2'
        value = u'c2-attr2'
    class seat_attribute_91:
        seat = SeatEvent1Venue2Data.seat_c3
        name = u'attr1'
        value = u'c3-attr2'
    class seat_attribute_92:
        seat = SeatEvent1Venue2Data.seat_c3
        name = u'attr2'
        value = u'c3-attr2'
    class seat_attribute_93:
        seat = SeatEvent1Venue2Data.seat_c4
        name = u'attr1'
        value = u'c4-attr2'
    class seat_attribute_94:
        seat = SeatEvent1Venue2Data.seat_c4
        name = u'attr2'
        value = u'c4-attr2'
    class seat_attribute_95:
        seat = SeatEvent1Venue2Data.seat_c5
        name = u'attr1'
        value = u'c5-attr2'
    class seat_attribute_96:
        seat = SeatEvent1Venue2Data.seat_c5
        name = u'attr2'
        value = u'c5-attr2'
    class seat_attribute_97:
        seat = SeatEvent1Venue2Data.seat_d1
        name = u'attr1'
        value = u'd1-attr2'
    class seat_attribute_98:
        seat = SeatEvent1Venue2Data.seat_d1
        name = u'attr2'
        value = u'd1-attr2'
    class seat_attribute_99:
        seat = SeatEvent1Venue2Data.seat_d2
        name = u'attr1'
        value = u'd2-attr2'
    class seat_attribute_100:
        seat = SeatEvent1Venue2Data.seat_d2
        name = u'attr2'
        value = u'd2-attr2'
    class seat_attribute_101:
        seat = SeatEvent1Venue2Data.seat_d3
        name = u'attr1'
        value = u'd3-attr2'
    class seat_attribute_102:
        seat = SeatEvent1Venue2Data.seat_d3
        name = u'attr2'
        value = u'd3-attr2'
    class seat_attribute_103:
        seat = SeatEvent1Venue2Data.seat_e1
        name = u'attr1'
        value = u'e1-attr2'
    class seat_attribute_104:
        seat = SeatEvent1Venue2Data.seat_e1
        name = u'attr2'
        value = u'e1-attr2'
    class seat_attribute_105:
        seat = SeatEvent1Venue2Data.seat_e2
        name = u'attr1'
        value = u'e2-attr2'
    class seat_attribute_106:
        seat = SeatEvent1Venue2Data.seat_e2
        name = u'attr2'
        value = u'e2-attr2'
    class seat_attribute_107:
        seat = SeatEvent1Venue2Data.seat_e3
        name = u'attr1'
        value = u'e3-attr2'
    class seat_attribute_108:
        seat = SeatEvent1Venue2Data.seat_e3
        name = u'attr2'
        value = u'e3-attr2'

class TemplateSeatAttributeData(DataSet):
    class template_seat_attribute_1:
        seat = TemplateSeatVenue1Data.seat_a1
        name = u'attr1'
        value = u'a1-attr2'
    class template_seat_attribute_2:
        seat = TemplateSeatVenue1Data.seat_a1
        name = u'attr2'
        value = u'a1-attr2'
    class template_seat_attribute_3:
        seat = TemplateSeatVenue1Data.seat_a2
        name = u'attr1'
        value = u'a2-attr2'
    class template_seat_attribute_4:
        seat = TemplateSeatVenue1Data.seat_a2
        name = u'attr2'
        value = u'a2-attr2'
    class template_seat_attribute_5:
        seat = TemplateSeatVenue1Data.seat_a3
        name = u'attr1'
        value = u'a3-attr2'
    class template_seat_attribute_6:
        seat = TemplateSeatVenue1Data.seat_a3
        name = u'attr2'
        value = u'a3-attr2'
    class template_seat_attribute_7:
        seat = TemplateSeatVenue1Data.seat_a4
        name = u'attr1'
        value = u'a4-attr2'
    class template_seat_attribute_8:
        seat = TemplateSeatVenue1Data.seat_a4
        name = u'attr2'
        value = u'a4-attr2'
    class template_seat_attribute_9:
        seat = TemplateSeatVenue1Data.seat_a5
        name = u'attr1'
        value = u'a5-attr2'
    class template_seat_attribute_10:
        seat = TemplateSeatVenue1Data.seat_a5
        name = u'attr2'
        value = u'a5-attr2'
    class template_seat_attribute_11:
        seat = TemplateSeatVenue1Data.seat_a6
        name = u'attr1'
        value = u'a6-attr2'
    class template_seat_attribute_12:
        seat = TemplateSeatVenue1Data.seat_a6
        name = u'attr2'
        value = u'a6-attr2'
    class template_seat_attribute_13:
        seat = TemplateSeatVenue1Data.seat_a7
        name = u'attr1'
        value = u'a7-attr2'
    class template_seat_attribute_14:
        seat = TemplateSeatVenue1Data.seat_a7
        name = u'attr2'
        value = u'a7-attr2'
    class template_seat_attribute_15:
        seat = TemplateSeatVenue1Data.seat_a8
        name = u'attr1'
        value = u'a8-attr2'
    class template_seat_attribute_16:
        seat = TemplateSeatVenue1Data.seat_a8
        name = u'attr2'
        value = u'a8-attr2'
    class template_seat_attribute_17:
        seat = TemplateSeatVenue1Data.seat_a9
        name = u'attr1'
        value = u'a9-attr2'
    class template_seat_attribute_18:
        seat = TemplateSeatVenue1Data.seat_a9
        name = u'attr2'
        value = u'a9-attr2'
    class template_seat_attribute_19:
        seat = TemplateSeatVenue1Data.seat_b1
        name = u'attr1'
        value = u'b1-attr2'
    class template_seat_attribute_20:
        seat = TemplateSeatVenue1Data.seat_b1
        name = u'attr2'
        value = u'b1-attr2'
    class template_seat_attribute_21:
        seat = TemplateSeatVenue1Data.seat_b2
        name = u'attr1'
        value = u'b2-attr2'
    class template_seat_attribute_22:
        seat = TemplateSeatVenue1Data.seat_b2
        name = u'attr2'
        value = u'b2-attr2'
    class template_seat_attribute_23:
        seat = TemplateSeatVenue1Data.seat_b3
        name = u'attr1'
        value = u'b3-attr2'
    class template_seat_attribute_24:
        seat = TemplateSeatVenue1Data.seat_b3
        name = u'attr2'
        value = u'b3-attr2'
    class template_seat_attribute_25:
        seat = TemplateSeatVenue1Data.seat_b4
        name = u'attr1'
        value = u'b4-attr2'
    class template_seat_attribute_26:
        seat = TemplateSeatVenue1Data.seat_b4
        name = u'attr2'
        value = u'b4-attr2'
    class template_seat_attribute_27:
        seat = TemplateSeatVenue1Data.seat_b5
        name = u'attr1'
        value = u'b5-attr2'
    class template_seat_attribute_28:
        seat = TemplateSeatVenue1Data.seat_b5
        name = u'attr2'
        value = u'b5-attr2'
    class template_seat_attribute_29:
        seat = TemplateSeatVenue1Data.seat_b6
        name = u'attr1'
        value = u'b6-attr2'
    class template_seat_attribute_30:
        seat = TemplateSeatVenue1Data.seat_b6
        name = u'attr2'
        value = u'b6-attr2'
    class template_seat_attribute_31:
        seat = TemplateSeatVenue1Data.seat_b7
        name = u'attr1'
        value = u'b7-attr2'
    class template_seat_attribute_32:
        seat = TemplateSeatVenue1Data.seat_b7
        name = u'attr2'
        value = u'b7-attr2'
    class template_seat_attribute_33:
        seat = TemplateSeatVenue1Data.seat_c1
        name = u'attr1'
        value = u'c1-attr2'
    class template_seat_attribute_34:
        seat = TemplateSeatVenue1Data.seat_c1
        name = u'attr2'
        value = u'c1-attr2'
    class template_seat_attribute_35:
        seat = TemplateSeatVenue1Data.seat_c2
        name = u'attr1'
        value = u'c2-attr2'
    class template_seat_attribute_36:
        seat = TemplateSeatVenue1Data.seat_c2
        name = u'attr2'
        value = u'c2-attr2'
    class template_seat_attribute_37:
        seat = TemplateSeatVenue1Data.seat_c3
        name = u'attr1'
        value = u'c3-attr2'
    class template_seat_attribute_38:
        seat = TemplateSeatVenue1Data.seat_c3
        name = u'attr2'
        value = u'c3-attr2'
    class template_seat_attribute_39:
        seat = TemplateSeatVenue1Data.seat_c4
        name = u'attr1'
        value = u'c4-attr2'
    class template_seat_attribute_40:
        seat = TemplateSeatVenue1Data.seat_c4
        name = u'attr2'
        value = u'c4-attr2'
    class template_seat_attribute_41:
        seat = TemplateSeatVenue1Data.seat_c5
        name = u'attr1'
        value = u'c5-attr2'
    class template_seat_attribute_42:
        seat = TemplateSeatVenue1Data.seat_c5
        name = u'attr2'
        value = u'c5-attr2'
    class template_seat_attribute_43:
        seat = TemplateSeatVenue1Data.seat_d1
        name = u'attr1'
        value = u'd1-attr2'
    class template_seat_attribute_44:
        seat = TemplateSeatVenue1Data.seat_d1
        name = u'attr2'
        value = u'd1-attr2'
    class template_seat_attribute_45:
        seat = TemplateSeatVenue1Data.seat_d2
        name = u'attr1'
        value = u'd2-attr2'
    class template_seat_attribute_46:
        seat = TemplateSeatVenue1Data.seat_d2
        name = u'attr2'
        value = u'd2-attr2'
    class template_seat_attribute_47:
        seat = TemplateSeatVenue1Data.seat_d3
        name = u'attr1'
        value = u'd3-attr2'
    class template_seat_attribute_48:
        seat = TemplateSeatVenue1Data.seat_d3
        name = u'attr2'
        value = u'd3-attr2'
    class template_seat_attribute_49:
        seat = TemplateSeatVenue1Data.seat_e1
        name = u'attr1'
        value = u'e1-attr2'
    class template_seat_attribute_50:
        seat = TemplateSeatVenue1Data.seat_e1
        name = u'attr2'
        value = u'e1-attr2'
    class template_seat_attribute_51:
        seat = TemplateSeatVenue1Data.seat_e2
        name = u'attr1'
        value = u'e2-attr2'
    class template_seat_attribute_52:
        seat = TemplateSeatVenue1Data.seat_e2
        name = u'attr2'
        value = u'e2-attr2'
    class template_seat_attribute_53:
        seat = TemplateSeatVenue1Data.seat_e3
        name = u'attr1'
        value = u'e3-attr2'
    class template_seat_attribute_54:
        seat = TemplateSeatVenue1Data.seat_e3
        name = u'attr2'
        value = u'e3-attr2'

class SeatAdjacencySetData(DataSet):
    class adjacency_set_vo1_n2:
        venue = TemplateVenueData.venue_orig_1
        seat_count = 2
    class adjacency_set_vo1_n3:
        venue = TemplateVenueData.venue_orig_1
        seat_count = 3
    class adjacency_set_vo1_n4:
        venue = TemplateVenueData.venue_orig_1
        seat_count = 4
    class adjacency_set_vo2_n2:
        venue = TemplateVenueData.venue_orig_2
        seat_count = 2
    class adjacency_set_vo2_n3:
        venue = TemplateVenueData.venue_orig_2
        seat_count = 3
    class adjacency_set_vo2_n4:
        venue = TemplateVenueData.venue_orig_2
        seat_count = 4
    class adjacency_set_e1_v1_n2:
        venue = VenueEvent1Data.venue_1
        seat_count = 2
    class adjacency_set_e1_v1_n3:
        venue = VenueEvent1Data.venue_1
        seat_count = 3
    class adjacency_set_e1_v1_n4:
        venue = VenueEvent1Data.venue_1
        seat_count = 4
    class adjacency_set_e1_v2_n2:
        venue = VenueEvent1Data.venue_2
        seat_count = 2
    class adjacency_set_e1_v2_n3:
        venue = VenueEvent1Data.venue_2
        seat_count = 3
    class adjacency_set_e1_v2_n4:
        venue = VenueEvent1Data.venue_2
        seat_count = 4
    class adjacency_set_e1_v3_n2:
        venue = VenueEvent1Data.venue_3
        seat_count = 2
    class adjacency_set_e1_v3_n3:
        venue = VenueEvent1Data.venue_3
        seat_count = 3
    class adjacency_set_e1_v3_n4:
        venue = VenueEvent1Data.venue_3
        seat_count = 4
    class adjacency_set_e1_v4_n2:
        venue = VenueEvent1Data.venue_4
        seat_count = 2
    class adjacency_set_e1_v4_n3:
        venue = VenueEvent1Data.venue_4
        seat_count = 3
    class adjacency_set_e1_v4_n4:
        venue = VenueEvent1Data.venue_4
        seat_count = 4
    class adjacency_set_e1_v5_n2:
        venue = VenueEvent1Data.venue_5
        seat_count = 2
    class adjacency_set_e1_v5_n3:
        venue = VenueEvent1Data.venue_5
        seat_count = 3
    class adjacency_set_e1_v5_n4:
        venue = VenueEvent1Data.venue_5
        seat_count = 4
    class adjacency_set_e2_v1_n2:
        venue = VenueEvent2Data.venue_1
        seat_count = 2
    class adjacency_set_e2_v1_n3:
        venue = VenueEvent2Data.venue_1
        seat_count = 3
    class adjacency_set_e2_v1_n4:
        venue = VenueEvent2Data.venue_1
        seat_count = 4
    class adjacency_set_e2_v2_n2:
        venue = VenueEvent2Data.venue_2
        seat_count = 2
    class adjacency_set_e2_v2_n3:
        venue = VenueEvent2Data.venue_2
        seat_count = 3
    class adjacency_set_e2_v2_n4:
        venue = VenueEvent2Data.venue_2
        seat_count = 4
    class adjacency_set_e2_v3_n2:
        venue = VenueEvent2Data.venue_3
        seat_count = 2
    class adjacency_set_e2_v3_n3:
        venue = VenueEvent2Data.venue_3
        seat_count = 3
    class adjacency_set_e2_v3_n4:
        venue = VenueEvent2Data.venue_3
        seat_count = 4

class SeatAdjacencyTemplateVenue1Count2Data(DataSet):
    class adjacency_vo1_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a1, TemplateSeatVenue1Data.seat_a2 ]
    class adjacency_vo1_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a2, TemplateSeatVenue1Data.seat_a3 ]
    class adjacency_vo1_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a3, TemplateSeatVenue1Data.seat_a4 ]
    class adjacency_vo1_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a4, TemplateSeatVenue1Data.seat_a5 ]
    class adjacency_vo1_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a5, TemplateSeatVenue1Data.seat_a6 ]
    class adjacency_vo1_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a6, TemplateSeatVenue1Data.seat_a7 ]
    class adjacency_vo1_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a7, TemplateSeatVenue1Data.seat_a8 ]
    class adjacency_vo1_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_a8, TemplateSeatVenue1Data.seat_a9 ]
    class adjacency_vo1_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_b1, TemplateSeatVenue1Data.seat_b2 ]
    class adjacency_vo1_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_b2, TemplateSeatVenue1Data.seat_b3 ]
    class adjacency_vo1_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_b3, TemplateSeatVenue1Data.seat_b4 ]
    class adjacency_vo1_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_b4, TemplateSeatVenue1Data.seat_b5 ]
    class adjacency_vo1_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_b5, TemplateSeatVenue1Data.seat_b6 ]
    class adjacency_vo1_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_b6, TemplateSeatVenue1Data.seat_b7 ]
    class adjacency_vo1_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_c1, TemplateSeatVenue1Data.seat_c2 ]
    class adjacency_vo1_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_c2, TemplateSeatVenue1Data.seat_c3 ]
    class adjacency_vo1_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_c3, TemplateSeatVenue1Data.seat_c4 ]
    class adjacency_vo1_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_c4, TemplateSeatVenue1Data.seat_c5 ]
    class adjacency_vo1_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_d1, TemplateSeatVenue1Data.seat_d2 ]
    class adjacency_vo1_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo1_n2
        seats = [ TemplateSeatVenue1Data.seat_e1, TemplateSeatVenue1Data.seat_e2 ]

class SeatAdjacencyTemplateVenue2Count2Data(DataSet):
    class adjacency_vo2_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a1, TemplateSeatVenue2Data.seat_a2 ]
    class adjacency_vo2_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a2, TemplateSeatVenue2Data.seat_a3 ]
    class adjacency_vo2_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a3, TemplateSeatVenue2Data.seat_a4 ]
    class adjacency_vo2_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a4, TemplateSeatVenue2Data.seat_a5 ]
    class adjacency_vo2_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a5, TemplateSeatVenue2Data.seat_a6 ]
    class adjacency_vo2_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a6, TemplateSeatVenue2Data.seat_a7 ]
    class adjacency_vo2_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a7, TemplateSeatVenue2Data.seat_a8 ]
    class adjacency_vo2_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_a8, TemplateSeatVenue2Data.seat_a9 ]
    class adjacency_vo2_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_b1, TemplateSeatVenue2Data.seat_b2 ]
    class adjacency_vo2_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_b2, TemplateSeatVenue2Data.seat_b3 ]
    class adjacency_vo2_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_b3, TemplateSeatVenue2Data.seat_b4 ]
    class adjacency_vo2_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_b4, TemplateSeatVenue2Data.seat_b5 ]
    class adjacency_vo2_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_b5, TemplateSeatVenue2Data.seat_b6 ]
    class adjacency_vo2_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_b6, TemplateSeatVenue2Data.seat_b7 ]
    class adjacency_vo2_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_c1, TemplateSeatVenue2Data.seat_c2 ]
    class adjacency_vo2_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_c2, TemplateSeatVenue2Data.seat_c3 ]
    class adjacency_vo2_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_c3, TemplateSeatVenue2Data.seat_c4 ]
    class adjacency_vo2_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_c4, TemplateSeatVenue2Data.seat_c5 ]
    class adjacency_vo2_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_d1, TemplateSeatVenue2Data.seat_d2 ]
    class adjacency_vo2_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_vo2_n2
        seats = [ TemplateSeatVenue2Data.seat_e1, TemplateSeatVenue2Data.seat_e2 ]

class SeatAdjacencyEvent1Venue1Count2Data(DataSet):
    class adjacency_e1_v1_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a1, SeatEvent1Venue1Data.seat_a2 ]
    class adjacency_e1_v1_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a2, SeatEvent1Venue1Data.seat_a3 ]
    class adjacency_e1_v1_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a3, SeatEvent1Venue1Data.seat_a4 ]
    class adjacency_e1_v1_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a4, SeatEvent1Venue1Data.seat_a5 ]
    class adjacency_e1_v1_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a5, SeatEvent1Venue1Data.seat_a6 ]
    class adjacency_e1_v1_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a6, SeatEvent1Venue1Data.seat_a7 ]
    class adjacency_e1_v1_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a7, SeatEvent1Venue1Data.seat_a8 ]
    class adjacency_e1_v1_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_a8, SeatEvent1Venue1Data.seat_a9 ]
    class adjacency_e1_v1_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_b1, SeatEvent1Venue1Data.seat_b2 ]
    class adjacency_e1_v1_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_b2, SeatEvent1Venue1Data.seat_b3 ]
    class adjacency_e1_v1_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_b3, SeatEvent1Venue1Data.seat_b4 ]
    class adjacency_e1_v1_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_b4, SeatEvent1Venue1Data.seat_b5 ]
    class adjacency_e1_v1_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_b5, SeatEvent1Venue1Data.seat_b6 ]
    class adjacency_e1_v1_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_b6, SeatEvent1Venue1Data.seat_b7 ]
    class adjacency_e1_v1_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_c1, SeatEvent1Venue1Data.seat_c2 ]
    class adjacency_e1_v1_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_c2, SeatEvent1Venue1Data.seat_c3 ]
    class adjacency_e1_v1_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_c3, SeatEvent1Venue1Data.seat_c4 ]
    class adjacency_e1_v1_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_c4, SeatEvent1Venue1Data.seat_c5 ]
    class adjacency_e1_v1_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_d1, SeatEvent1Venue1Data.seat_d2 ]
    class adjacency_e1_v1_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v1_n2
        seats = [ SeatEvent1Venue1Data.seat_e1, SeatEvent1Venue1Data.seat_e2 ]

class SeatAdjacencyEvent1Venue2Count2Data(DataSet):
    class adjacency_e1_v2_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a1, SeatEvent1Venue2Data.seat_a2 ]
    class adjacency_e1_v2_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a2, SeatEvent1Venue2Data.seat_a3 ]
    class adjacency_e1_v2_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a3, SeatEvent1Venue2Data.seat_a4 ]
    class adjacency_e1_v2_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a4, SeatEvent1Venue2Data.seat_a5 ]
    class adjacency_e1_v2_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a5, SeatEvent1Venue2Data.seat_a6 ]
    class adjacency_e1_v2_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a6, SeatEvent1Venue2Data.seat_a7 ]
    class adjacency_e1_v2_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a7, SeatEvent1Venue2Data.seat_a8 ]
    class adjacency_e1_v2_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_a8, SeatEvent1Venue2Data.seat_a9 ]
    class adjacency_e1_v2_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_b1, SeatEvent1Venue2Data.seat_b2 ]
    class adjacency_e1_v2_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_b2, SeatEvent1Venue2Data.seat_b3 ]
    class adjacency_e1_v2_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_b3, SeatEvent1Venue2Data.seat_b4 ]
    class adjacency_e1_v2_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_b4, SeatEvent1Venue2Data.seat_b5 ]
    class adjacency_e1_v2_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_b5, SeatEvent1Venue2Data.seat_b6 ]
    class adjacency_e1_v2_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_b6, SeatEvent1Venue2Data.seat_b7 ]
    class adjacency_e1_v2_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_c1, SeatEvent1Venue2Data.seat_c2 ]
    class adjacency_e1_v2_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_c2, SeatEvent1Venue2Data.seat_c3 ]
    class adjacency_e1_v2_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_c3, SeatEvent1Venue2Data.seat_c4 ]
    class adjacency_e1_v2_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_c4, SeatEvent1Venue2Data.seat_c5 ]
    class adjacency_e1_v2_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_d1, SeatEvent1Venue2Data.seat_d2 ]
    class adjacency_e1_v2_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v2_n2
        seats = [ SeatEvent1Venue2Data.seat_e1, SeatEvent1Venue2Data.seat_e2 ]

class SeatAdjacencyEvent1Venue3Count2Data(DataSet):
    class adjacency_e1_v3_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a1, SeatEvent1Venue3Data.seat_a2 ]
    class adjacency_e1_v3_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a2, SeatEvent1Venue3Data.seat_a3 ]
    class adjacency_e1_v3_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a3, SeatEvent1Venue3Data.seat_a4 ]
    class adjacency_e1_v3_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a4, SeatEvent1Venue3Data.seat_a5 ]
    class adjacency_e1_v3_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a5, SeatEvent1Venue3Data.seat_a6 ]
    class adjacency_e1_v3_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a6, SeatEvent1Venue3Data.seat_a7 ]
    class adjacency_e1_v3_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a7, SeatEvent1Venue3Data.seat_a8 ]
    class adjacency_e1_v3_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_a8, SeatEvent1Venue3Data.seat_a9 ]
    class adjacency_e1_v3_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_b1, SeatEvent1Venue3Data.seat_b2 ]
    class adjacency_e1_v3_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_b2, SeatEvent1Venue3Data.seat_b3 ]
    class adjacency_e1_v3_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_b3, SeatEvent1Venue3Data.seat_b4 ]
    class adjacency_e1_v3_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_b4, SeatEvent1Venue3Data.seat_b5 ]
    class adjacency_e1_v3_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_b5, SeatEvent1Venue3Data.seat_b6 ]
    class adjacency_e1_v3_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_b6, SeatEvent1Venue3Data.seat_b7 ]
    class adjacency_e1_v3_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_c1, SeatEvent1Venue3Data.seat_c2 ]
    class adjacency_e1_v3_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_c2, SeatEvent1Venue3Data.seat_c3 ]
    class adjacency_e1_v3_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_c3, SeatEvent1Venue3Data.seat_c4 ]
    class adjacency_e1_v3_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_c4, SeatEvent1Venue3Data.seat_c5 ]
    class adjacency_e1_v3_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_d1, SeatEvent1Venue3Data.seat_d2 ]
    class adjacency_e1_v3_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v3_n2
        seats = [ SeatEvent1Venue3Data.seat_e1, SeatEvent1Venue3Data.seat_e2 ]

class SeatAdjacencyEvent1Venue4Count2Data(DataSet):
    class adjacency_e1_v4_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a1, SeatEvent1Venue4Data.seat_a2 ]
    class adjacency_e1_v4_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a2, SeatEvent1Venue4Data.seat_a3 ]
    class adjacency_e1_v4_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a3, SeatEvent1Venue4Data.seat_a4 ]
    class adjacency_e1_v4_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a4, SeatEvent1Venue4Data.seat_a5 ]
    class adjacency_e1_v4_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a5, SeatEvent1Venue4Data.seat_a6 ]
    class adjacency_e1_v4_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a6, SeatEvent1Venue4Data.seat_a7 ]
    class adjacency_e1_v4_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a7, SeatEvent1Venue4Data.seat_a8 ]
    class adjacency_e1_v4_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_a8, SeatEvent1Venue4Data.seat_a9 ]
    class adjacency_e1_v4_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_b1, SeatEvent1Venue4Data.seat_b2 ]
    class adjacency_e1_v4_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_b2, SeatEvent1Venue4Data.seat_b3 ]
    class adjacency_e1_v4_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_b3, SeatEvent1Venue4Data.seat_b4 ]
    class adjacency_e1_v4_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_b4, SeatEvent1Venue4Data.seat_b5 ]
    class adjacency_e1_v4_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_b5, SeatEvent1Venue4Data.seat_b6 ]
    class adjacency_e1_v4_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_b6, SeatEvent1Venue4Data.seat_b7 ]
    class adjacency_e1_v4_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_c1, SeatEvent1Venue4Data.seat_c2 ]
    class adjacency_e1_v4_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_c2, SeatEvent1Venue4Data.seat_c3 ]
    class adjacency_e1_v4_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_c3, SeatEvent1Venue4Data.seat_c4 ]
    class adjacency_e1_v4_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_c4, SeatEvent1Venue4Data.seat_c5 ]
    class adjacency_e1_v4_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_d1, SeatEvent1Venue4Data.seat_d2 ]
    class adjacency_e1_v4_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v4_n2
        seats = [ SeatEvent1Venue4Data.seat_e1, SeatEvent1Venue4Data.seat_e2 ]

class SeatAdjacencyEvent1Venue5Count2Data(DataSet):
    class adjacency_e1_v5_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a1, SeatEvent1Venue5Data.seat_a2 ]
    class adjacency_e1_v5_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a2, SeatEvent1Venue5Data.seat_a3 ]
    class adjacency_e1_v5_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a3, SeatEvent1Venue5Data.seat_a4 ]
    class adjacency_e1_v5_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a4, SeatEvent1Venue5Data.seat_a5 ]
    class adjacency_e1_v5_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a5, SeatEvent1Venue5Data.seat_a6 ]
    class adjacency_e1_v5_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a6, SeatEvent1Venue5Data.seat_a7 ]
    class adjacency_e1_v5_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a7, SeatEvent1Venue5Data.seat_a8 ]
    class adjacency_e1_v5_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_a8, SeatEvent1Venue5Data.seat_a9 ]
    class adjacency_e1_v5_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_b1, SeatEvent1Venue5Data.seat_b2 ]
    class adjacency_e1_v5_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_b2, SeatEvent1Venue5Data.seat_b3 ]
    class adjacency_e1_v5_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_b3, SeatEvent1Venue5Data.seat_b4 ]
    class adjacency_e1_v5_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_b4, SeatEvent1Venue5Data.seat_b5 ]
    class adjacency_e1_v5_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_b5, SeatEvent1Venue5Data.seat_b6 ]
    class adjacency_e1_v5_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_b6, SeatEvent1Venue5Data.seat_b7 ]
    class adjacency_e1_v5_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_c1, SeatEvent1Venue5Data.seat_c2 ]
    class adjacency_e1_v5_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_c2, SeatEvent1Venue5Data.seat_c3 ]
    class adjacency_e1_v5_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_c3, SeatEvent1Venue5Data.seat_c4 ]
    class adjacency_e1_v5_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_c4, SeatEvent1Venue5Data.seat_c5 ]
    class adjacency_e1_v5_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_d1, SeatEvent1Venue5Data.seat_d2 ]
    class adjacency_e1_v5_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e1_v5_n2
        seats = [ SeatEvent1Venue5Data.seat_e1, SeatEvent1Venue5Data.seat_e2 ]

class SeatAdjacencyEvent2Venue1Count2Data(DataSet):
    class adjacency_e2_v1_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a1, SeatEvent2Venue1Data.seat_a2 ]
    class adjacency_e2_v1_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a2, SeatEvent2Venue1Data.seat_a3 ]
    class adjacency_e2_v1_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a3, SeatEvent2Venue1Data.seat_a4 ]
    class adjacency_e2_v1_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a4, SeatEvent2Venue1Data.seat_a5 ]
    class adjacency_e2_v1_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a5, SeatEvent2Venue1Data.seat_a6 ]
    class adjacency_e2_v1_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a6, SeatEvent2Venue1Data.seat_a7 ]
    class adjacency_e2_v1_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a7, SeatEvent2Venue1Data.seat_a8 ]
    class adjacency_e2_v1_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_a8, SeatEvent2Venue1Data.seat_a9 ]
    class adjacency_e2_v1_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_b1, SeatEvent2Venue1Data.seat_b2 ]
    class adjacency_e2_v1_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_b2, SeatEvent2Venue1Data.seat_b3 ]
    class adjacency_e2_v1_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_b3, SeatEvent2Venue1Data.seat_b4 ]
    class adjacency_e2_v1_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_b4, SeatEvent2Venue1Data.seat_b5 ]
    class adjacency_e2_v1_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_b5, SeatEvent2Venue1Data.seat_b6 ]
    class adjacency_e2_v1_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_b6, SeatEvent2Venue1Data.seat_b7 ]
    class adjacency_e2_v1_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_c1, SeatEvent2Venue1Data.seat_c2 ]
    class adjacency_e2_v1_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_c2, SeatEvent2Venue1Data.seat_c3 ]
    class adjacency_e2_v1_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_c3, SeatEvent2Venue1Data.seat_c4 ]
    class adjacency_e2_v1_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_c4, SeatEvent2Venue1Data.seat_c5 ]
    class adjacency_e2_v1_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_d1, SeatEvent2Venue1Data.seat_d2 ]
    class adjacency_e2_v1_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v1_n2
        seats = [ SeatEvent2Venue1Data.seat_e1, SeatEvent2Venue1Data.seat_e2 ]

class SeatAdjacencyEvent2Venue2Count2Data(DataSet):
    class adjacency_e2_v2_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a1, SeatEvent2Venue2Data.seat_a2 ]
    class adjacency_e2_v2_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a2, SeatEvent2Venue2Data.seat_a3 ]
    class adjacency_e2_v2_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a3, SeatEvent2Venue2Data.seat_a4 ]
    class adjacency_e2_v2_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a4, SeatEvent2Venue2Data.seat_a5 ]
    class adjacency_e2_v2_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a5, SeatEvent2Venue2Data.seat_a6 ]
    class adjacency_e2_v2_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a6, SeatEvent2Venue2Data.seat_a7 ]
    class adjacency_e2_v2_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a7, SeatEvent2Venue2Data.seat_a8 ]
    class adjacency_e2_v2_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_a8, SeatEvent2Venue2Data.seat_a9 ]
    class adjacency_e2_v2_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_b1, SeatEvent2Venue2Data.seat_b2 ]
    class adjacency_e2_v2_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_b2, SeatEvent2Venue2Data.seat_b3 ]
    class adjacency_e2_v2_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_b3, SeatEvent2Venue2Data.seat_b4 ]
    class adjacency_e2_v2_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_b4, SeatEvent2Venue2Data.seat_b5 ]
    class adjacency_e2_v2_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_b5, SeatEvent2Venue2Data.seat_b6 ]
    class adjacency_e2_v2_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_b6, SeatEvent2Venue2Data.seat_b7 ]
    class adjacency_e2_v2_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_c1, SeatEvent2Venue2Data.seat_c2 ]
    class adjacency_e2_v2_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_c2, SeatEvent2Venue2Data.seat_c3 ]
    class adjacency_e2_v2_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_c3, SeatEvent2Venue2Data.seat_c4 ]
    class adjacency_e2_v2_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_c4, SeatEvent2Venue2Data.seat_c5 ]
    class adjacency_e2_v2_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_d1, SeatEvent2Venue2Data.seat_d2 ]
    class adjacency_e2_v2_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v2_n2
        seats = [ SeatEvent2Venue2Data.seat_e1, SeatEvent2Venue2Data.seat_e2 ]

class SeatAdjacencyEvent2Venue3Count2Data(DataSet):
    class adjacency_e2_v3_n2_1:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a1, SeatEvent2Venue3Data.seat_a2 ]
    class adjacency_e2_v3_n2_2:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a2, SeatEvent2Venue3Data.seat_a3 ]
    class adjacency_e2_v3_n2_3:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a3, SeatEvent2Venue3Data.seat_a4 ]
    class adjacency_e2_v3_n2_4:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a4, SeatEvent2Venue3Data.seat_a5 ]
    class adjacency_e2_v3_n2_5:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a5, SeatEvent2Venue3Data.seat_a6 ]
    class adjacency_e2_v3_n2_6:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a6, SeatEvent2Venue3Data.seat_a7 ]
    class adjacency_e2_v3_n2_7:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a7, SeatEvent2Venue3Data.seat_a8 ]
    class adjacency_e2_v3_n2_8:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_a8, SeatEvent2Venue3Data.seat_a9 ]
    class adjacency_e2_v3_n2_9:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_b1, SeatEvent2Venue3Data.seat_b2 ]
    class adjacency_e2_v3_n2_10:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_b2, SeatEvent2Venue3Data.seat_b3 ]
    class adjacency_e2_v3_n2_11:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_b3, SeatEvent2Venue3Data.seat_b4 ]
    class adjacency_e2_v3_n2_12:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_b4, SeatEvent2Venue3Data.seat_b5 ]
    class adjacency_e2_v3_n2_13:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_b5, SeatEvent2Venue3Data.seat_b6 ]
    class adjacency_e2_v3_n2_14:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_b6, SeatEvent2Venue3Data.seat_b7 ]
    class adjacency_e2_v3_n2_15:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_c1, SeatEvent2Venue3Data.seat_c2 ]
    class adjacency_e2_v3_n2_16:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_c2, SeatEvent2Venue3Data.seat_c3 ]
    class adjacency_e2_v3_n2_17:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_c3, SeatEvent2Venue3Data.seat_c4 ]
    class adjacency_e2_v3_n2_18:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_c4, SeatEvent2Venue3Data.seat_c5 ]
    class adjacency_e2_v3_n2_19:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_d1, SeatEvent2Venue3Data.seat_d2 ]
    class adjacency_e2_v3_n2_20:
        adjacency_set = SeatAdjacencySetData.adjacency_set_e2_v3_n2
        seats = [ SeatEvent2Venue3Data.seat_e1, SeatEvent2Venue3Data.seat_e2 ]

