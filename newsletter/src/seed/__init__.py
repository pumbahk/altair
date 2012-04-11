# -*- coding: utf-8 -*-

import fixture
from fixture import DataSet
from fixture import SQLAlchemyFixture

import sqlahelper
import sqlalchemy as sa
from sqlalchemy.orm import *
from datetime import datetime
from hashlib import md5

import os
import sys
from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))) + '/newsletter')
from newsletters.models import *
#from newsletter.newsletters.models import *

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass

engine = sa.create_engine('mysql://newsletter:newsletter@127.0.0.1/newsletter?use_unicode=true&charset=utf8', echo=True)
sqlahelper.add_engine(engine)

from seed.newsletter import NewsletterData

db_fixture = SQLAlchemyFixture(
    env={
         'NewsletterData' : Newsletter,
    },
    engine=engine,
)

metadata = Base.metadata
metadata.bind = engine
metadata.drop_all(engine)
metadata.create_all()

data = db_fixture.data(
    NewsletterData,
)
data.setup()

