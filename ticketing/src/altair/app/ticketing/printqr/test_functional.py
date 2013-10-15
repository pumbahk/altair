# -*- coding:utf-8 -*-
import unittest
import transaction
import sqlalchemy as sa
from .testing import (
    swap_engine, 
    setUpSwappedDB, 
    tearDownSwappedDB
)

def setUpModule():
    setUpSwappedDB()

def tearDownModule():
    tearDownSwappedDB()


class Tests(unittest.TestCase):
    def tearDown(self):
        transaction.abort()

    def test_it(self):
        from .testing import get_ordered_product_item__full_relation
        from altair.app.ticketing.models import DBSession
        get_ordered_product_item__full_relation(quantity=2, quantity_only=True)
        DBSession.flush()
        
