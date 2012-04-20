# -*- coding: utf-8 -*-

import fixture
from fixture import DataSet
from fixture import SQLAlchemyFixture

import sqlalchemy as sa
from sqlalchemy.orm import *
from datetime import datetime
from hashlib import md5

from ticketing.oauth2.models import *
from ticketing.clients.models import *
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

from seed.bank import BankData, BankAccountData
from seed.prefecture import PrefectureMaster

from service    import ServiceData
from client     import ClientData
from account    import AccountData
from permission import PermissionData
from operator   import OperatorData, OperatorRoleData
from event import EventData,PerformanceData
from venue import VenueData
from product import ProductData, ProductItemData
from ticketing.bookmark.tests.bookmark import BookmarkData

from ticketing.oauth2.models import Service
from ticketing.operators.models import Operator, OperatorActionHistory, OperatorRole, Permission
from ticketing.bookmark.models import Bookmark

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
         'ClientData'       : Client,
         'EventData'        : Event,
         'PerformanceData'  : Performance,
         'VenueData'        : Venue,
         'ProductData'      : Product,
         'ProductItemData'  : ProductItem,
         'BookmarkData'     : Bookmark
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
    ClientData,
    OperatorRoleData,
    OperatorData,
    EventData,
    PerformanceData,
    VenueData,
    ProductData,
    ProductItemData,
    BookmarkData
)
data.setup()

