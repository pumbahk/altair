# -*- coding:utf-8 -*-

import unittest
from mock import patch
from pyramid import testing
from decimal import Decimal
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin
from datetime import datetime, timedelta

class FindApplicableTicketsTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.payments.plugins.sej import applicable_tickets_iter
        return applicable_tickets_iter(*args,  **kwargs)

    def test_it(self):
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
        class bundle(object):
            class sej_ticket:
                class ticket_format:
                    sej_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID)                    
                    delivery_methods = [sej_delivery_method]
            tickets = [sej_ticket]

        result = list(self._callFUT(bundle))
        self.assertEquals(len(result), 1)

    def test_with_another_ticket(self):
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
        class bundle(object):
            class sej_ticket:
                class ticket_format:
                    sej_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID)                    
                    delivery_methods = [sej_delivery_method]

            class another_ticket:
                class ticket_format:
                    another_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=-100)                    
                    delivery_methods = [another_delivery_method]
                    
            tickets = [sej_ticket, another_ticket, sej_ticket, another_ticket, sej_ticket]

        result = list(self._callFUT(bundle))
        self.assertEquals(len(result), 3)

class BuildSejArgsTest(unittest.TestCase):
    now = datetime(2013, 1, 1, 0, 0, 0)

    expectations_paid = [
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2014, 1, 1, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2014, 1, 1, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2014, 1, 1, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2014, 1, 1, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2014, 1, 1, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2014, 1, 1, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 0,
            ticket_price          = 0,
            commission_fee        = 0,
            ticketing_fee         = 0,
            payment_due_at        = None,
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        ]
    
    expectations_prepayment_only = [
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        ]

    expectations_prepayment_only = [
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 900,
            ticketing_fee         = 0,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        ]
    
    expectations_cash_on_delivery = [
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 2, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 4, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        #
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test2@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000001',
            zip_code              = '1234567',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        dict(
            order_no              = '00000001',
            user_name             = u'last_namefirst_name',
            user_name_kana        = u'last_name_kanafirst_name_kana',
            tel                   = '0300000000',
            zip_code              = u'',
            email                 = 'test1@test.com',
            total_price           = 1000,
            ticket_price          = 100,
            commission_fee        = 700,
            ticketing_fee         = 200,
            payment_due_at        = datetime(2013, 1, 4, 23, 59, 59),
            ticketing_start_at    = datetime(2013, 1, 5, 0, 0, 0),
            ticketing_due_at      = datetime(2013, 1, 8, 0, 0, 0),
            regrant_number_due_at = datetime(2013, 3, 2, 2, 3, 4),
            ),
        ]

    def setUp(self):
        self.pdmps = [
            testing.DummyModel(
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                issuing_interval_days=None,
                payment_period_days=1
                ),
            testing.DummyModel(
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_at=None,
                issuing_interval_days=None,
                payment_period_days=1
                ),
            testing.DummyModel(
                issuing_start_at=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                issuing_interval_days=3,
                payment_period_days=1
                ),
            testing.DummyModel(
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                issuing_interval_days=None,
                payment_period_days=None
                ),
            ]

        self.shipping_addresses = [
            testing.DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            testing.DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=None
                ),
            testing.DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=None,
                email_2=u'test2@test.com'
                ),
            testing.DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=None,
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            testing.DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=None,
                tel_2=u'03-0000-0001',
                zip=u'123-4567',
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            testing.DummyModel(
                first_name=u'first_name',
                last_name=u'last_name',
                first_name_kana=u'first_name_kana',
                last_name_kana=u'last_name_kana',
                tel_1=u'03-0000-0000',
                tel_2=u'03-0000-0001',
                zip=None,
                email_1=u'test1@test.com',
                email_2=u'test2@test.com'
                ),
            ]

        self.orders = [
            testing.DummyModel(
                order_no='00000001',
                shipping_address=shipping_address,
                payment_delivery_pair=payment_delivery_pair,
                total_amount=1000,
                system_fee=300,
                transaction_fee=400,
                delivery_fee=200,
                special_fee=0,
                performance=testing.DummyModel(
                    start_on=datetime(2013, 3, 1, 2, 3, 4)
                    )
                )
            for payment_delivery_pair in self.pdmps
            for shipping_address in self.shipping_addresses
            ]

    def _callFUT(self, *args, **kwargs):
        from .sej import build_sej_args
        return build_sej_args(*args, **kwargs)

    def testPaid(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_paid))
        for i, (expectation, order) in enumerate(zip(self.expectations_paid, self.orders)):
            args = self._callFUT(SejPaymentType.Paid, order, self.now)
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.performance.start_on = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.performance = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

    def testPrepaymentOnly(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_prepayment_only))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.performance.start_on = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.performance = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

    def testCashOnDelivery(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_cash_on_delivery))
        for i, (expectation, order) in enumerate(zip(self.expectations_cash_on_delivery, self.orders)):
            args = self._callFUT(SejPaymentType.CashOnDelivery, order, self.now)
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.performance.start_on = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.performance = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now)
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

class PluginTestBase(unittest.TestCase, CoreTestMixin, CartTestMixin):
    def setUp(self):
        from datetime import datetime
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models',
            'altair.app.ticketing.cart.models'
            ])
        self.request = testing.DummyRequest()
        testing.setUp(request=self.request, settings={ 'sej.api_key': 'XXXXX', 'sej.inticket_api_url': 'http://example.com/' })
        CoreTestMixin.setUp(self)
        self._setup_fixture()
        self.performance.start_on = datetime(2012, 4, 1, 0, 0, 0)
        self.session.flush()


    @property
    def _payment_plugin_id(self):
        from . import SEJ_PAYMENT_PLUGIN_ID
        return SEJ_PAYMENT_PLUGIN_ID

    _delivery_plugin_id = 'N/A'

    @property
    def _payment_types(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        return [
            SejPaymentType.CashOnDelivery,
            SejPaymentType.Prepayment,
            SejPaymentType.PrepaymentOnly,
            ]

    def _generate_ticket_formats(self):
        from altair.app.ticketing.core.models import TicketFormat
        yield self._create_ticket_format(delivery_methods=[
            delivery_method for delivery_method in self.delivery_methods.values()
            if delivery_method.delivery_plugin_id == self._delivery_plugin_id
            ])

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import SeatStatusEnum
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                if quantity == 0:
                    break
                quantity -= 1
                seat.status = SeatStatusEnum.InCart.v
                yield seat

    def _setup_fixture(self):
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.sej.models import SejPaymentType, SejTenant
        self.session.add(SejTenant(organization_id=1L))
        self.stock_types = self._create_stock_types(1)
        self.stock_types[0].quantity_only = False
        self.stocks = self._create_stocks(self.stock_types)
        self.seats = self._create_seats(self.stocks)
        self.products = self._create_products(self.stocks)
        for ticket in self.products[0].items[0].ticket_bundle.tickets:
            ticket.data = {u'drawing': u'''<?xml version="1.0" ?><svg xmlns="http://www.w3.org/2000/svg"><text>{{予約番号}}</text></svg>'''}
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.sales_segment = SalesSegment(performance=self.performance, sales_segment_group=self.sales_segment_group)
        self.pdmps = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.applicable_pdmps = [
            pdmp for pdmp in self.pdmps
            if self._payment_plugin_id in (None, pdmp.payment_method.payment_plugin_id) or self._delivery_plugin_id in (None, pdmp.delivery_method.delivery_plugin_id)
            ]

    def _create_order_pairs(self):
        from datetime import datetime
        order_pairs = {}
        for payment_type in self._payment_types:
            order = self._create_order(
                zip(self.products, [1]),
                sales_segment=self.sales_segment,
                pdmp=self.applicable_pdmps[0]
                )
            order.created_at = datetime(2012, 1, 1, 0, 0, 0)
            sej_order = self._create_sej_order(order, payment_type)
            self.session.add(order)
            self.session.add(sej_order)
            order_pairs[payment_type] = (order, sej_order)
        return order_pairs

    def _create_carts(self):
        from datetime import datetime
        carts = {}
        for payment_type in self._payment_types:
            cart = self._create_cart(
                zip(self.products, [1]),
                sales_segment=self.sales_segment,
                pdmp=self.applicable_pdmps[0]
                )
            cart.performance = self.performance
            cart.created_at = datetime(2012, 1, 1, 0, 0, 0)

            carts[payment_type] = cart
        return carts

    def tearDown(self):
        testing.tearDown()
        self.session.remove()
        _teardown_db()

    def _create_sej_order(self, order, payment_type):
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejPaymentType
        from datetime import datetime, timedelta
        tickets = [
            SejTicket(
                ticket_idx=(i + 1),
                ticket_type=('%d' % SejTicketType.TicketWithBarcode.v),
                barcode_number='0000%04d' % (i + 1),
                event_name=order.sales_segment.performance.event.title,
                performance_name=order.sales_segment.performance.name,
                performance_datetime=datetime(2012,8,30,19,00),
                ticket_template_id='TTTS0001',
                ticket_data_xml=u'<?xml version="1.0" encoding="Shift_JIS" ?><TICKET></TICKET>',
                product_item_id=12345
                )
            for ordered_product in order.items
            for i, ordered_product_item in enumerate(ordered_product.elements)
            ]

        return SejOrder(
            payment_type='%d' % int(payment_type),
            order_no=order.order_no,
            billing_number=u'00000001',
            total_ticket_count=len(tickets),
            ticket_count=len(tickets),
            total_price=order.total_amount,
            ticket_price=(order.total_amount - order.system_fee - order.transaction_fee - order.delivery_fee),
            commission_fee=order.system_fee,
            ticketing_fee=order.delivery_fee,
            branch_no=1,
            exchange_sheet_url=u'https://www.r1test.com/order/hi.do',
            exchange_sheet_number=u'11111111',
            exchange_number=u'22222222',
            order_at=order.created_at,
            ticketing_due_at=(order.created_at + timedelta(days=10)),
            regrant_number_due_at=(order.created_at + timedelta(days=5)),
            tickets=tickets
            )

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

class PaymentPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejPaymentPlugin
        return SejPaymentPlugin

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum

        carts = self._create_carts()
        plugin = self._makeOne()
        for payment_type, cart in carts.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_shop_order_id': cart.order_no,
                    'X_haraikomi_no': '00001001',
                    'X_hikikae_no': '00001002',
                    'X_url_info': 'http://example.com/',
                    'iraihyo_id_00': '10000000',
                    'X_goukei_kingaku': cart.total_amount,
                    'X_ticket_daikin': cart.total_amount - cart.system_fee - cart.delivery_fee - cart.transaction_fee - cart.special_fee,
                    'X_ticket_kounyu_daikin': cart.system_fee + cart.special_fee,
                    'X_hakken_daikin': cart.transaction_fee,
                    }
                order = plugin.finish(self.request, cart)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertEqual(cart.order_no, order.order_no)

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    }
                plugin.refresh(self.request, order)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)

class DeliveryPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejDeliveryPlugin
        return SejDeliveryPlugin

    _payment_plugin_id = 'N/A'

    @property
    def _delivery_plugin_id(self):
        from . import SEJ_DELIVERY_PLUGIN_ID
        return SEJ_DELIVERY_PLUGIN_ID

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.sej.models import SejOrder, SejTicket

        carts = self._create_carts()
        plugin = self._makeOne()
        for payment_type, cart in carts.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_shop_order_id': cart.order_no,
                    'X_haraikomi_no': '00001001',
                    'X_hikikae_no': '00001002',
                    'X_url_info': 'http://example.com/',
                    'iraihyo_id_00': '10000000',
                    'X_goukei_kingaku': cart.total_amount,
                    'X_ticket_daikin': cart.total_amount - cart.system_fee - cart.delivery_fee - cart.transaction_fee - cart.special_fee,
                    'X_ticket_kounyu_daikin': cart.system_fee + cart.special_fee,
                    'X_hakken_daikin': cart.transaction_fee,
                    'X_barcode_no_01': '00000001',
                    }
                plugin.finish(self.request, cart)
                self.session.flush()
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                new_sej_order = self.session.query(SejOrder).filter_by(order_no=cart.order_no).one()
                new_sej_tickets = self.session.query(SejTicket).filter_by(sej_order_id=new_sej_order.id).all()
                self.assertTrue(len(new_sej_tickets), 1)
                self.assertTrue(new_sej_tickets[0].barcode_number, '00000001')

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    'X_barcode_no_01': '00000002',
                    }
                plugin.refresh(self.request, order)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertTrue(sej_order.tickets[0].barcode_number, '00000002')

class PaymentDeliveryPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejPaymentDeliveryPlugin
        return SejPaymentDeliveryPlugin

    @property
    def _payment_plugin_id(self):
        from . import SEJ_PAYMENT_PLUGIN_ID
        return SEJ_PAYMENT_PLUGIN_ID

    @property
    def _delivery_plugin_id(self):
        from . import SEJ_DELIVERY_PLUGIN_ID
        return SEJ_DELIVERY_PLUGIN_ID

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.sej.models import SejOrder, SejTicket

        carts = self._create_carts()
        plugin = self._makeOne()
        for payment_type, cart in carts.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_shop_order_id': cart.order_no,
                    'X_haraikomi_no': '00001001',
                    'X_hikikae_no': '00001002',
                    'X_url_info': 'http://example.com/',
                    'iraihyo_id_00': '10000000',
                    'X_goukei_kingaku': cart.total_amount,
                    'X_ticket_daikin': cart.total_amount - cart.system_fee - cart.delivery_fee - cart.transaction_fee - cart.special_fee,
                    'X_ticket_kounyu_daikin': cart.system_fee + cart.special_fee,
                    'X_hakken_daikin': cart.transaction_fee,
                    'X_barcode_no_01': '00000001',
                    }
                order = plugin.finish(self.request, cart)
                self.session.flush()
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                new_sej_order = self.session.query(SejOrder).filter_by(order_no=order.order_no).one()
                new_sej_tickets = self.session.query(SejTicket).filter_by(sej_order_id=new_sej_order.id).all()
                self.assertTrue(new_sej_tickets[0].barcode_number, '00000001')

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    'X_barcode_no_01': '00000002',
                    }
                plugin.refresh(self.request, order)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertTrue(sej_order.tickets[0].barcode_number, '00000002')

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
