# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, join, column_property, mapper

from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

