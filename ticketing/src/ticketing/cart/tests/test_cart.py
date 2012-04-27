# -*- coding:utf-8 -*-
import unittest
import commands

import fixture
from fixture import DataSet
from fixture import SQLAlchemyFixture
import sqlalchemy as sa
from sqlalchemy.orm import *
import datetime
import transaction

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

from ticketing.orders.models import *
from ticketing.products.models import *

from seed.bank import BankData, BankAccountData
from seed.prefecture import PrefectureMaster
from seed.service    import ServiceData
from seed.organization     import OrganizationData
from seed.ticket     import TicketerData
from seed.account    import AccountData
from seed.permission import PermissionData
from seed.operator   import OperatorData, OperatorRoleData
from seed.event import EventData,PerformanceData
from seed.venue import VenueData

from ticketing.oauth2.models import Service
from ticketing.operators.models import Operator, OperatorActionHistory, OperatorRole, Permission

from seattype import SeatTypeData
from seatmaster import SeatMasterData
from seatmasterl2 import SeatMasterL2Data
from price import PriceData
from paymentmethod import PaymentMethodData
from deliverymethod import DeliveryMethodData
from paymentdeliverymethodpair import PaymentDeliveryMethodPairData
from salessegment import SalesSegmentData
from salessegmentset import SalesSegmentSetData
from productitem import ProductItemData
from stockholder import StockHolderData
from stock import StockData
from seatstock import SeatStockData
from product import ProductData

from ticketing.cart.models import SimpleCart

def setUpModule():
    try:
        print commands.getstatusoutput('''echo 'drop database ticketing;' | mysql -u ticketing --password='ticketing' ''')
        print commands.getstatusoutput('''echo 'create database ticketing charset=utf8;' | mysql -u ticketing --password='ticketing' ''')
        print commands.getstatusoutput('''echo 'grant all on ticketing.* to ticketing@localhost identified by "ticketing";' | mysql -u root --password='' ''')
    except:
        pass

def tearDownModule():
    pass

class CartBaseTest(unittest.TestCase):
                    
    def setUp(self):
        import pymysql_sa
        pymysql_sa.make_default_mysql_dialect()
        print 'Using PyMySQL'
        engine = sa.create_engine('mysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8', echo=True)
        sqlahelper.add_engine(engine)
        metadata = Base.metadata
        metadata.bind = engine
#metadata.drop_all(engine)
        metadata.create_all()
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
                'TicketerData'     : Ticketer,
                'ClientData'       : Organization,
                'EventData'        : Event,
                'PerformanceData'  : Performance,
                'VenueData'        : Venue,
                'SeatTypeData'     : SeatType,
                'SeatMasterData'   : SeatMaster,
                'SeatMasterL2Data' : SeatMasterL2,
                'PriceData'                     : Price,
                'PaymentMethodData'             : PaymentMethod,
                'DeliveryMethodData'            : DeliveryMethod,
                'ProductData'                   : Product,
                'ProductItemData'               : ProductItem,
                'SalesSegmentSetData'           : SalesSegmentSet,
                'SalesSegmentData'              : SalesSegment,
                'PaymentDeliveryMethodPairData' : PaymentDeliveryMethodPair,
                'StockHolderData'               : StockHolder,
                'StockData'                     : Stock,
                'SeatStockData'                 : SeatStock
            },
             engine=engine,
        )
        data = db_fixture.data(
            ServiceData,
            PrefectureMaster,
            PermissionData,
            BankData,
            BankAccountData,
            OperatorRoleData,
            AccountData,
            TicketerData,
            OrganizationData,
            OperatorRoleData,
            OperatorData,
            EventData,
            PerformanceData,
            VenueData,
            SeatTypeData,
            SeatMasterData,
            SeatMasterL2Data,
            PriceData,
            PaymentMethodData,
            DeliveryMethodData,
            ProductData,
            ProductItemData,
            SalesSegmentSetData,
            SalesSegmentData,
            PaymentDeliveryMethodPairData,
            StockHolderData,
            StockData,
            SeatStockData
        )
        data.setup()
        from ticketing import main
        app = main({}, **{"sqlalchemy.url": "mysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8", 
                          "mako.directories": "ticketing:templates", 
                          "auth.secret": "SDQGxGIhVqSr3zJWV8KvHqHtJujhJj", 
                          "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI"}) 
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        transaction.commit()
        
    def test_crud(self):
        product = Product.get(1)
        cart = SimpleCart()
        cart.add(product)
        self.assertEquals(len(cart.list()), 1)
        cart.commit()
        self.assertEquals(cart.list()[0].order_id, 1)

if __name__ == "__main__":
    unittest.main()
