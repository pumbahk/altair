# -*- coding: utf-8 -*-

import fixture
from fixture import DataSet
from fixture import SQLAlchemyFixture

import sqlalchemy as sa
from sqlalchemy.orm import *

from ticketing.oauth2.models import *
from ticketing.organizations.models import *
from ticketing.events.models import *
from ticketing.master.models import *
from ticketing.oauth2.models import *
from ticketing.operators.models import *
from ticketing.orders.models import *
from ticketing.products.models import *
from ticketing.users.models import *
from ticketing.venues.models import *

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass

engine = sa.create_engine('mysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8', echo=True)
sqlahelper.add_engine(engine)

from bank import BankData, BankAccountData
from prefecture import PrefectureMaster

from service import ServiceData
from organization import OrganizationData
from account import AccountData
from permission import PermissionData
from operator import OperatorData, OperatorRoleData
from event import EventData, PerformanceData
from venue import *
from product import ProductData, ProductItemData, StockData, StockHolderData, SalesSegmentData, SeatTypeData
from user import UserData, UserProfileData, UserCredentialData
from ticketing.bookmark.tests.bookmark import BookmarkData
from ticketing.products.tests.payment_delivery_method import DeliveryMethodPluginData, PaymentMethodPluginData, DeliveryMethodData, PaymentMethodData, PaymentDeliveryMethodPairData

from ticketing.oauth2.models import Service
from ticketing.operators.models import Operator, OperatorActionHistory, OperatorRole, Permission
from ticketing.bookmark.models import Bookmark
from ticketing.products.models import PaymentMethod, DeliveryMethod, PaymentMethodPlugin, DeliveryMethodPlugin


def import_seed_data():
    db_fixture = SQLAlchemyFixture(
         env={
             'ServiceData'      : Service,
             'PrefectureMaster' : Prefecture,
             'PermissionData'   : Permission,
             'OperatorRoleData' : OperatorRole,
             'OperatorData'     : Operator,
             'BankData'         : Bank,
             'BankAccountData'  : BankAccount,
             'AccountData'      : Account,
             'OrganizationData' : Organization,
             'EventData'        : Event,
             'PerformanceData'  : Performance,
             'SiteData'         : Site,
             'TemplateVenueData': Venue,
             'VenueData'        : Venue,
             'TemplateSeatVenue1Data':Seat,
             'TemplateSeatVenue2Data':Seat,
             'SeatVenue1Data'   : Seat,
             'SeatVenue2Data'   : Seat,
             'SeatVenue3Data'   : Seat,
             'SeatVenue4Data'   : Seat,
             'SeatVenue5Data'   : Seat,
             'SeatVenue6Data'   : Seat,
             'SeatVenue7Data'   : Seat,
             'SeatVenue8Data'   : Seat,
             'SeatStatusVenue1Data': SeatStatus,
             'SeatStatusVenue2Data': SeatStatus,
             'SeatStatusVenue3Data': SeatStatus,
             'SeatStatusVenue4Data': SeatStatus,
             'SeatStatusVenue5Data': SeatStatus,
             'SeatStatusVenue6Data': SeatStatus,
             'SeatStatusVenue7Data': SeatStatus,
             'SeatStatusVenue8Data': SeatStatus,
             'TemplateSeatAttributeData': SeatAttribute,
             'SeatAttributeData': SeatAttribute,
             'SeatAdjacencySetData': SeatAdjacencySet,
             'SeatAdjacencyTemplateVenue1Count2Data': SeatAdjacency,
             'SeatAdjacencyTemplateVenue2Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue1Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue2Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue3Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue4Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue5Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue6Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue7Count2Data': SeatAdjacency,
             'SeatAdjacencyVenue8Count2Data': SeatAdjacency,
             'SeatTypeData'     : SeatType,
             'StockData'        : Stock,
             'StockHolderData'  : StockHolder,
             'SalesSegmentData' : SalesSegment,
             'ProductData'      : Product,
             'ProductItemData'  : ProductItem,
             'BookmarkData'     : Bookmark,
             'UserData'         : User,
             'UserProfileData'  : UserProfile,
             'UserCredentialData'       : UserCredential,
             'DeliveryMethodPluginData' : DeliveryMethodPlugin,
             'PaymentMethodPluginData'  : PaymentMethodPlugin,
             'DeliveryMethodData'       : DeliveryMethod,
             'PaymentMethodData'        : PaymentMethod,
             'PaymentDeliveryMethodPairData' : PaymentDeliveryMethodPair,
         },
         engine=engine,
    )

    metadata = Base.metadata
    metadata.bind = engine
#metadata.drop_all(engine)
    metadata.create_all()

    data = db_fixture.data(
        ServiceData,
        PrefectureMaster,
        PermissionData,
        BankData,
        BankAccountData,
        OperatorRoleData,
        AccountData,
        OrganizationData,
        OperatorData,
        EventData,
        PerformanceData,
        SiteData,
        TemplateVenueData,
        VenueData,
        TemplateSeatVenue1Data,
        TemplateSeatVenue2Data,
        SeatVenue1Data,
        SeatVenue2Data,
        SeatVenue3Data,
        SeatVenue4Data,
        SeatVenue5Data,
        SeatVenue6Data,
        SeatVenue7Data,
        SeatVenue8Data,
        SeatStatusVenue1Data,
        SeatStatusVenue2Data,
        SeatStatusVenue3Data,
        SeatStatusVenue4Data,
        SeatStatusVenue5Data,
        SeatStatusVenue6Data,
        SeatStatusVenue7Data,
        SeatStatusVenue8Data,
        TemplateSeatAttributeData,
        SeatAttributeData,
        SeatAdjacencySetData,
        SeatAdjacencyTemplateVenue1Count2Data,
        SeatAdjacencyTemplateVenue2Count2Data,
        SeatAdjacencyVenue1Count2Data,
        SeatAdjacencyVenue2Count2Data,
        SeatAdjacencyVenue3Count2Data,
        SeatAdjacencyVenue4Count2Data,
        SeatAdjacencyVenue5Count2Data,
        SeatAdjacencyVenue6Count2Data,
        SeatAdjacencyVenue7Count2Data,
        SeatAdjacencyVenue8Count2Data,
        SeatTypeData,
        StockData,
        StockHolderData,
        SalesSegmentData,
        ProductData,
        ProductItemData,
        BookmarkData,
        UserData,
        UserProfileData,
        UserCredentialData,
        DeliveryMethodPluginData,
        PaymentMethodPluginData,
        DeliveryMethodData,
        PaymentMethodData,
        PaymentDeliveryMethodPairData
    )
    data.setup()
