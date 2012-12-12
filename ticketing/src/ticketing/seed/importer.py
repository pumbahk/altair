# -*- coding: utf-8 -*-

import fixture
from fixture import DataSet
from fixture import SQLAlchemyFixture

from sqlalchemy.orm import *
import sqlahelper

from ticketing.oauth2.models import *
from ticketing.master.models import *
from ticketing.oauth2.models import *
from ticketing.operators.models import *
from ticketing.users.models import *
from ticketing.core.models import *
from ticketing.sej.models import *

from bank import BankData, BankAccountData

from service import ServiceData
from organization import OrganizationData
from account import AccountData
from permission import PermissionData
from operator_ import OperatorData, OperatorRoleData, OperatorAuthData
from event import *
from venue import *
from product import *
from order import *
from user import UserData, UserProfileData, UserCredentialData
from ticketing.bookmark.tests.bookmark import BookmarkData
from ticketing.products.tests.payment_delivery_method import DeliveryMethodPluginData, PaymentMethodPluginData, DeliveryMethodData, PaymentMethodData, PaymentDeliveryMethodPairData
from ticketing.seed.sej import SejTicketTemplateFileData

from ticketing.oauth2.models import Service
from ticketing.operators.models import Operator, OperatorActionHistory, OperatorRole, Permission
from ticketing.bookmark.models import Bookmark
from ticketing.sej.models import SejOrder, SejTicket, SejFile, SejNotification
from ticketing.cart.models import Cart, CartedProduct, CartedProductItem
from ticketing.payments.plugins.models import ReservedNumber
from ticketing.multicheckout.models import MultiCheckoutRequestCard, MultiCheckoutResponseCard
from ticketing.checkout.models import Checkout, CheckoutItem

def import_seed_data():
    engine = sqlahelper.get_engine()
    db_fixture = SQLAlchemyFixture(
         env={
             'ServiceData'            : Service,
             'PermissionData'         : Permission,
             'OperatorRoleData'       : OperatorRole,
             'OperatorData'           : Operator,
             'OperatorAuthData'       : OperatorAuth,
             'BankData'               : Bank,
             'BankAccountData'        : BankAccount,
             'AccountData'            : Account,
             'OrganizationData'       : Organization,
             'EventData'              : Event,
             'PerformanceEvent1Data'  : Performance,
             'PerformanceEvent2Data'  : Performance,
             'PerformanceEvent3Data'  : Performance,
             'SiteData'               : Site,
             'TemplateVenueData'      : Venue,
             'VenueEvent1Data'        : Venue,
             'VenueEvent2Data'        : Venue,
             'VenueEvent3Data'        : Venue,
             'TemplateSeatVenue1Data' : Seat,
             'TemplateSeatVenue2Data' : Seat,
             'VenueArea_group_l0_idData': VenueArea_group_l0_id,
             'VenueAreaTemplateVenue1Data': VenueArea,
             'VenueAreaTemplateVenue2Data': VenueArea,
             'VenueAreaEvent1Venue1Data': VenueArea,
             'VenueAreaEvent1Venue2Data': VenueArea,
             'VenueAreaEvent1Venue3Data': VenueArea,
             'VenueAreaEvent1Venue4Data': VenueArea,
             'VenueAreaEvent1Venue5Data': VenueArea,
             'VenueAreaEvent2Venue1Data': VenueArea,
             'VenueAreaEvent2Venue2Data': VenueArea,
             'VenueAreaEvent2Venue3Data': VenueArea,
             'SeatEvent1Venue1Data'   : Seat,
             'SeatEvent1Venue2Data'   : Seat,
             'SeatEvent1Venue3Data'   : Seat,
             'SeatEvent1Venue4Data'   : Seat,
             'SeatEvent1Venue5Data'   : Seat,
             'SeatEvent2Venue1Data'   : Seat,
             'SeatEvent2Venue2Data'   : Seat,
             'SeatEvent2Venue3Data'   : Seat,
             'SeatStatusEvent1Venue1Data': SeatStatus,
             'SeatStatusEvent1Venue2Data': SeatStatus,
             'SeatStatusEvent1Venue3Data': SeatStatus,
             'SeatStatusEvent1Venue4Data': SeatStatus,
             'SeatStatusEvent1Venue5Data': SeatStatus,
             'SeatStatusEvent2Venue1Data': SeatStatus,
             'SeatStatusEvent2Venue2Data': SeatStatus,
             'SeatStatusEvent2Venue3Data': SeatStatus,
             'TemplateSeatAttributeData': SeatAttribute,
             'SeatAttributeData': SeatAttribute,
             'SeatAdjacencySetData': SeatAdjacencySet,
             'SeatAdjacencyTemplateVenue1Count2Data': SeatAdjacency,
             'SeatAdjacencyTemplateVenue2Count2Data': SeatAdjacency,
             'SeatAdjacencyEvent1Venue1Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent1Venue2Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent1Venue3Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent1Venue4Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent1Venue5Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent2Venue1Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent2Venue2Count2Data'  : SeatAdjacency,
             'SeatAdjacencyEvent2Venue3Count2Data'  : SeatAdjacency,
             'StockTypeEvent1Data'                  : StockType,
             'StockTypeEvent2Data'                  : StockType,
             'StockTypeEvent3Data'                  : StockType,
             'StockEvent1Performance1Data'          : Stock,
             'StockEvent1Performance2Data'          : Stock,
             'StockEvent1Performance3Data'          : Stock,
             'StockEvent1Performance4Data'          : Stock,
             'StockEvent1Performance5Data'          : Stock,
             'StockEvent2Performance1Data'          : Stock,
             'StockEvent2Performance2Data'          : Stock,
             'StockEvent2Performance3Data'          : Stock,
             'StockEvent3Performance1Data'          : Stock,
             'StockStatusEvent1Performance1Data'    : StockStatus,
             'StockStatusEvent1Performance2Data'    : StockStatus,
             'StockStatusEvent1Performance3Data'    : StockStatus,
             'StockStatusEvent1Performance4Data'    : StockStatus,
             'StockStatusEvent1Performance5Data'    : StockStatus,
             'StockStatusEvent2Performance1Data'    : StockStatus,
             'StockStatusEvent2Performance2Data'    : StockStatus,
             'StockStatusEvent2Performance3Data'    : StockStatus,
             'StockHolderEvent1'                    : StockHolder,
             'StockHolderEvent2'                    : StockHolder,
             'StockHolderEvent3'                    : StockHolder,
             'SalesSegmentEvent1Data'               : SalesSegment,
             'SalesSegmentEvent2Data'               : SalesSegment,
             'SalesSegmentEvent3Data'               : SalesSegment,
             'ProductEvent1Data'                    : Product,
             'ProductEvent2Data'                    : Product,
             'ProductEvent3Data'                    : Product,
             'ProductItemEvent1Performance1Data'    : ProductItem,
             'ProductItemEvent1Performance2Data'    : ProductItem,
             'ProductItemEvent1Performance3Data'    : ProductItem,
             'ProductItemEvent1Performance4Data'    : ProductItem,
             'ProductItemEvent1Performance5Data'    : ProductItem,
             'ProductItemEvent2Performance1Data'    : ProductItem,
             'ProductItemEvent2Performance2Data'    : ProductItem,
             'ProductItemEvent2Performance3Data'    : ProductItem,
             'ProductItemEvent3Performance1Data'    : ProductItem,
             'ShippingAddressData'                  : ShippingAddress,
             'OrderData'                            : Order,
             'OrderedProductOrder1Data'             : OrderedProduct,
             'OrderedProductOrder2Data'             : OrderedProduct,
             'OrderedProductItemOrder1Data'         : OrderedProductItem,
             'OrderedProductItemOrder2Data'         : OrderedProductItem,
             'BookmarkData'                         : Bookmark,
             'UserData'                             : User,
             'UserProfileData'                      : UserProfile,
             'UserCredentialData'                   : UserCredential,
             'DeliveryMethodPluginData'             : DeliveryMethodPlugin,
             'PaymentMethodPluginData'              : PaymentMethodPlugin,
             'DeliveryMethodData'                   : DeliveryMethod,
             'PaymentMethodData'                    : PaymentMethod,
             'PaymentDeliveryMethodPairData'        : PaymentDeliveryMethodPair,
             'SejTicketTemplateFileData'            : SejTicketTemplateFile
         },
         engine=engine
    )

    metadata = Base.metadata
    metadata.bind = engine
    #metadata.drop_all(engine)
    metadata.create_all()

    data = db_fixture.data(
        ServiceData,
        PermissionData,
        BankData,
        BankAccountData,
        OperatorRoleData,
        AccountData,
        OrganizationData,
        OperatorData,
        OperatorAuthData,
        EventData,
        PerformanceEvent1Data,
        PerformanceEvent2Data,
        PerformanceEvent3Data,
        SiteData,
        TemplateVenueData,
        VenueArea_group_l0_idData,
        VenueEvent1Data,
        VenueEvent2Data,
        VenueEvent3Data,
        VenueAreaEvent1Venue1Data,
        VenueAreaEvent1Venue2Data,
        VenueAreaEvent1Venue3Data,
        VenueAreaEvent1Venue4Data,
        VenueAreaEvent1Venue5Data,
        VenueAreaEvent2Venue1Data,
        VenueAreaEvent2Venue2Data,
        VenueAreaEvent2Venue3Data,
        VenueAreaTemplateVenue1Data,
        VenueAreaTemplateVenue2Data,
        TemplateSeatVenue1Data,
        TemplateSeatVenue2Data,
        SeatEvent1Venue1Data,
        SeatEvent1Venue2Data,
        SeatEvent1Venue3Data,
        SeatEvent1Venue4Data,
        SeatEvent1Venue5Data,
        SeatEvent2Venue1Data,
        SeatEvent2Venue2Data,
        SeatEvent2Venue3Data,
        SeatStatusEvent1Venue1Data,
        SeatStatusEvent1Venue2Data,
        SeatStatusEvent1Venue3Data,
        SeatStatusEvent1Venue4Data,
        SeatStatusEvent1Venue5Data,
        SeatStatusEvent2Venue1Data,
        SeatStatusEvent2Venue2Data,
        SeatStatusEvent2Venue3Data,
        TemplateSeatAttributeData,
        SeatAttributeData,
        SeatAdjacencySetData,
        SeatAdjacencyTemplateVenue1Count2Data,
        SeatAdjacencyTemplateVenue2Count2Data,
        SeatAdjacencyEvent1Venue1Count2Data,
        SeatAdjacencyEvent1Venue2Count2Data,
        SeatAdjacencyEvent1Venue3Count2Data,
        SeatAdjacencyEvent1Venue4Count2Data,
        SeatAdjacencyEvent1Venue5Count2Data,
        SeatAdjacencyEvent2Venue1Count2Data,
        SeatAdjacencyEvent2Venue2Count2Data,
        SeatAdjacencyEvent2Venue3Count2Data,
        StockTypeEvent1Data,
        StockTypeEvent2Data,
        StockTypeEvent3Data,
        StockEvent1Performance1Data,
        StockEvent1Performance2Data,
        StockEvent1Performance3Data,
        StockEvent1Performance4Data,
        StockEvent1Performance5Data,
        StockEvent2Performance1Data,
        StockEvent2Performance2Data,
        StockEvent2Performance3Data,
        StockEvent3Performance1Data,
        StockStatusEvent1Performance1Data,
        StockStatusEvent1Performance2Data,
        StockStatusEvent1Performance3Data,
        StockStatusEvent1Performance4Data,
        StockStatusEvent1Performance5Data,
        StockStatusEvent2Performance1Data,
        StockStatusEvent2Performance2Data,
        StockStatusEvent2Performance3Data,
        StockHolderEvent1,
        StockHolderEvent2,
        StockHolderEvent3,
        SalesSegmentEvent1Data,
        SalesSegmentEvent2Data,
        SalesSegmentEvent3Data,
        ProductEvent1Data,
        ProductEvent2Data,
        ProductEvent3Data,
        ProductItemEvent1Performance1Data,
        ProductItemEvent1Performance2Data,
        ProductItemEvent1Performance3Data,
        ProductItemEvent1Performance4Data,
        ProductItemEvent1Performance5Data,
        ProductItemEvent2Performance1Data,
        ProductItemEvent2Performance2Data,
        ProductItemEvent2Performance3Data,
        ProductItemEvent3Performance1Data,
        OrderData,
        OrderedProductOrder1Data,
        OrderedProductOrder2Data,
        OrderedProductItemOrder1Data,
        OrderedProductItemOrder2Data,
        BookmarkData,
        UserData,
        UserProfileData,
        UserCredentialData,
        DeliveryMethodPluginData,
        PaymentMethodPluginData,
        DeliveryMethodData,
        PaymentMethodData,
        PaymentDeliveryMethodPairData,
        SejTicketTemplateFileData
    )
    data.setup()
