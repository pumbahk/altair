# -*- coding:utf-8 -*-

import unittest
import mock
from pyramid import testing
from decimal import Decimal
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin
from zope.interface import implementer
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
            ),
        ]

    expectations_prepayment = [
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
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
            ticketing_start_at    = None,
            ticketing_due_at      = None,
            regrant_number_due_at = datetime(2014, 1, 1, 0, 0, 0),
            ),
        ]

    def setUp(self):
        from altair.app.ticketing.core.models import CartMixin, DateCalculationBase
        class DummyCart(CartMixin):
            def __init__(self, sales_segment, payment_delivery_pair, created_at):
                self.sales_segment = sales_segment
                self.payment_delivery_pair = payment_delivery_pair
                self.created_at = created_at

        self.pdmps = [
            testing.DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_interval_days=None,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None
                ),
            testing.DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_interval_days=None,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=None,
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None
                ),
            testing.DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                issuing_interval_days=3,
                issuing_start_at=None,
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=1,
                payment_due_at=None
                ),
            testing.DummyModel(
                issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_start_at=datetime(2013, 1, 5, 0, 0, 0),
                issuing_interval_days=None,
                issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                issuing_end_in_days=None,
                issuing_end_at=datetime(2013, 1, 8, 0, 0, 0),
                payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_start_in_days=0,
                payment_start_at=None,
                payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                payment_period_days=3,
                payment_due_at=None
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

        orders = []
        for payment_delivery_pair in self.pdmps:
            for shipping_address in self.shipping_addresses:
                sales_segment = testing.DummyModel(
                    performance=testing.DummyModel(
                        start_on=datetime(2013, 3, 1, 1, 2, 3),
                        end_on=datetime(2013, 3, 1, 2, 3, 4)
                        )
                    )
                cart = DummyCart(sales_segment, payment_delivery_pair, self.now)
                orders.append(
                    testing.DummyModel(
                        order_no='00000001',
                        shipping_address=shipping_address,
                        payment_delivery_pair=payment_delivery_pair,
                        total_amount=1000,
                        system_fee=300,
                        transaction_fee=400,
                        delivery_fee=200,
                        special_fee=0,
                        issuing_start_at=cart.issuing_start_at,
                        issuing_end_at=cart.issuing_end_at,
                        payment_start_at=cart.payment_start_at,
                        payment_due_at=cart.payment_due_at,
                        sales_segment=sales_segment
                        )
                    )
        self.orders = orders

    def _callFUT(self, *args, **kwargs):
        from .sej import build_sej_args
        return build_sej_args(*args, **kwargs)

    def testPaid(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_paid))
        for i, (expectation, order) in enumerate(zip(self.expectations_paid, self.orders)):
            args = self._callFUT(SejPaymentType.Paid, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_paid, self.orders)):
            order.sales_segment.performance.end_on = None
            args = self._callFUT(SejPaymentType.Paid, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    start_on = self.now + timedelta(days=365)
                    self.assertEqual(start_on, args[k], '[%d].%s: %s != %s' % (i, k, start_on, args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_paid, self.orders)):
            order.sales_segment.performance.start_on = None
            args = self._callFUT(SejPaymentType.Paid, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_paid, self.orders)):
            order.sales_segment.performance = None
            args = self._callFUT(SejPaymentType.Paid, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

    def testPrepayment(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_prepayment))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment, self.orders)):
            args = self._callFUT(SejPaymentType.Prepayment, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment, self.orders)):
            order.sales_segment.performance.end_on = None
            args = self._callFUT(SejPaymentType.Prepayment, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    start_on = self.now + timedelta(days=365)
                    self.assertEqual(start_on, args[k], '[%d].%s: %s != %s' % (i, k, start_on, args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment, self.orders)):
            order.sales_segment.performance.start_on = None
            args = self._callFUT(SejPaymentType.Prepayment, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment, self.orders)):
            order.sales_segment.performance = None
            args = self._callFUT(SejPaymentType.Prepayment, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

    def testPrepaymentOnly(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_prepayment_only))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.sales_segment.performance.end_on = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    start_on = self.now + timedelta(days=365)
                    self.assertEqual(start_on, args[k], '[%d].%s: %s != %s' % (i, k, start_on, args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.sales_segment.performance.start_on = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_prepayment_only, self.orders)):
            order.sales_segment.performance = None
            args = self._callFUT(SejPaymentType.PrepaymentOnly, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

    def testCashOnDelivery(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        self.assertEqual(len(self.orders), len(self.expectations_cash_on_delivery))
        for i, (expectation, order) in enumerate(zip(self.expectations_cash_on_delivery, self.orders)):
            args = self._callFUT(SejPaymentType.CashOnDelivery, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_cash_on_delivery, self.orders)):
            order.sales_segment.performance.end_on = None
            args = self._callFUT(SejPaymentType.CashOnDelivery, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    start_on = self.now + timedelta(days=365)
                    self.assertEqual(start_on, args[k], '[%d].%s: %s != %s' % (i, k, start_on, args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_cash_on_delivery, self.orders)):
            order.sales_segment.performance.start_on = None
            args = self._callFUT(SejPaymentType.CashOnDelivery, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
        for i, (expectation, order) in enumerate(zip(self.expectations_cash_on_delivery, self.orders)):
            order.sales_segment.performance = None
            args = self._callFUT(SejPaymentType.CashOnDelivery, order, self.now, self.now + timedelta(days=365))
            for k, v in expectation.items():
                if k != 'regrant_number_due_at':
                    self.assertEqual(expectation[k], args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))
                else:
                    self.assertEqual(self.now + timedelta(days=365), args[k], '[%d].%s: %s != %s' % (i, k, expectation[k], args[k]))

class IsSameSejOrderTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .sej import is_same_sej_order
        return is_same_sej_order(*args, **kwargs)

    def test_same_cash_on_delivery(self):
        from altair.app.ticketing.sej.models import SejPaymentType, SejTicketType
        sej_order = testing.DummyModel(
            payment_type=SejPaymentType.CashOnDelivery.v,
            order_no='XX0000000000',
            user_name='user_name',
            user_name_kana='user_name_kana',
            tel='0300000000',
            zip_code='0000000',
            email='test@example.com',
            total_price=12000,
            ticket_price=10000,
            commission_fee=1000,
            ticketing_fee=1000,
            payment_due_at=None,
            ticketing_start_at=datetime(2014, 1, 1, 0, 0, 0),
            ticketing_due_at=datetime(2014, 1, 8, 0, 0, 0),
            regrant_number_due_at=datetime(2015, 12, 31, 0, 0, 0),
            tickets=[
                testing.DummyModel(
                    ticket_idx=0,
                    ticket_type=SejTicketType.TicketWithBarcode.v,
                    event_name='event_name',
                    performance_name='performance_name',
                    performance_datetime=datetime(2014, 8, 1, 0, 0, 0),
                    ticket_template_id=1,
                    product_item_id=1,
                    ticket_data_xml='<xml />'
                    )
                ]
            )
        args_dict = dict(
            payment_type=SejPaymentType.CashOnDelivery.v,
            order_no='XX0000000000',
            user_name='user_name',
            user_name_kana='user_name_kana',
            tel='0300000000',
            zip_code='0000000',
            email='test@example.com',
            total_price=12000,
            ticket_price=10000,
            commission_fee=1000,
            ticketing_fee=1000,
            payment_due_at=None,
            ticketing_start_at=datetime(2014, 1, 1, 0, 0, 0),
            ticketing_due_at=datetime(2014, 1, 8, 0, 0, 0),
            regrant_number_due_at=datetime(2015, 12, 31, 0, 0, 0)
            )
        ticket_dicts = [
            dict(
                ticket_idx=0,
                ticket_type=SejTicketType.TicketWithBarcode.v,
                event_name='event_name',
                performance_name='performance_name',
                performance_datetime=datetime(2014, 8, 1, 0, 0, 0),
                ticket_template_id=1,
                product_item_id=1,
                xml='<xml />'
                )
            ]
        self.assertTrue(self._callFUT(sej_order, args_dict, ticket_dicts))

    def test_different_cash_on_delivery(self):
        from altair.app.ticketing.sej.models import SejPaymentType, SejTicketType

        for k in ['payment_type', 'order_no', 'user_name', 'user_name_kana', 'tel', 'zip_code', 'email', 'total_price', 'ticket_price', 'commission_fee', 'ticketing_fee', 'payment_due_at', 'ticketing_start_at', 'ticketing_due_at', 'regrant_number_due_at']:
            sej_order = testing.DummyModel(
                payment_type=SejPaymentType.CashOnDelivery.v,
                order_no='XX0000000000',
                user_name='user_name',
                user_name_kana='user_name_kana',
                tel='0300000000',
                zip_code='0000000',
                email='test@example.com',
                total_price=12000,
                ticket_price=10000,
                commission_fee=1000,
                ticketing_fee=1000,
                payment_due_at=datetime(2014, 1, 2, 0, 0, 0),
                ticketing_start_at=datetime(2014, 1, 1, 0, 0, 0),
                ticketing_due_at=datetime(2014, 1, 8, 0, 0, 0),
                regrant_number_due_at=datetime(2015, 12, 31, 0, 0, 0),
                tickets=[
                    testing.DummyModel(
                        ticket_idx=0,
                        ticket_type=SejTicketType.TicketWithBarcode.v,
                        event_name='event_name',
                        performance_name='performance_name',
                        performance_datetime=datetime(2014, 8, 1, 0, 0, 0),
                        ticket_template_id=1,
                        product_item_id=1,
                        ticket_data_xml='<xml />'
                        )
                    ]
                )
            args_dict = dict(
                payment_type=SejPaymentType.CashOnDelivery.v,
                order_no='XX0000000000',
                user_name='user_name',
                user_name_kana='user_name_kana',
                tel='0300000000',
                zip_code='0000000',
                email='test@example.com',
                total_price=12000,
                ticket_price=10000,
                commission_fee=1000,
                ticketing_fee=1000,
                payment_due_at=datetime(2014, 1, 2, 0, 0, 0),
                ticketing_start_at=datetime(2014, 1, 1, 0, 0, 0),
                ticketing_due_at=datetime(2014, 1, 8, 0, 0, 0),
                regrant_number_due_at=datetime(2015, 12, 31, 0, 0, 0)
                )
            ticket_dicts = [
                dict(
                    ticket_idx=0,
                    ticket_type=SejTicketType.TicketWithBarcode.v,
                    event_name='event_name',
                    performance_name='performance_name',
                    performance_datetime=datetime(2014, 8, 1, 0, 0, 0),
                    ticket_template_id=1,
                    product_item_id=1,
                    xml='<xml />'
                    )
                ]
            v = getattr(sej_order, k)
            if v is None:
                continue
            elif isinstance(v, basestring):
                v += '*'
            elif isinstance(v, datetime):
                v += timedelta(days=1)
            elif isinstance(v, (int, long, Decimal)):
                v += 1
            setattr(sej_order, k, v)
            self.assertFalse(self._callFUT(sej_order, args_dict, ticket_dicts))


    def test_same_prepayment_only(self):
        from altair.app.ticketing.sej.models import SejPaymentType, SejTicketType
        sej_order = testing.DummyModel(
            payment_type=SejPaymentType.PrepaymentOnly.v,
            order_no='XX0000000000',
            user_name='user_name',
            user_name_kana='user_name_kana',
            tel='0300000000',
            zip_code='0000000',
            email='test@example.com',
            total_price=12000,
            ticket_price=10000,
            commission_fee=1000,
            ticketing_fee=1000,
            payment_due_at=datetime(2014, 1, 1, 0, 0, 0),
            ticketing_start_at=None,
            ticketing_due_at=None,
            regrant_number_due_at=datetime(2015, 12, 31, 0, 0, 0),
            tickets=[]
            )
        args_dict = dict(
            payment_type=SejPaymentType.PrepaymentOnly.v,
            order_no='XX0000000000',
            user_name='user_name',
            user_name_kana='user_name_kana',
            tel='0300000000',
            zip_code='0000000',
            email='test@example.com',
            total_price=12000,
            ticket_price=10000,
            commission_fee=1000,
            ticketing_fee=1000,
            payment_due_at=datetime(2014, 1, 1, 0, 0, 0),
            ticketing_start_at=None,
            ticketing_due_at=None,
            regrant_number_due_at=datetime(2015, 12, 31, 0, 0, 0)
            )
        ticket_dicts = [
            dict(
                ticket_idx=0,
                ticket_type=SejTicketType.TicketWithBarcode.v,
                event_name='event_name',
                performance_name='performance_name',
                performance_datetime=datetime(2014, 8, 1, 0, 0, 0),
                ticket_template_id=1,
                product_item_id=1,
                xml='<xml />'
                )
            ]
        self.assertTrue(self._callFUT(sej_order, args_dict, ticket_dicts))

class ValidateOrderLikeTest(unittest.TestCase):
    def _getTarget(self):
        from .sej import validate_order_like
        return validate_order_like

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_shipping_address_ok(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1='00000000000',
                tel_2=None,
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='email@example.com',
                email_2=None
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        try:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
            self.assertTrue(True)
        except OrderLikeValidationFailure as e:
            self.fail(e)

    def test_shipping_address_no_tel(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='email@example.com',
                email_2=None
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.tel_1')

    def test_shipping_address_no_zip(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='',
                email_1='',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        try:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
            self.assertTrue(True)
        except OrderLikeValidationFailure as e:
            self.fail(e)

    def test_shipping_address_invalid_zip(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='aaaaaaa',
                email_1='',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.zip')

        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='000000',
                email_1='',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.zip')

    def test_shipping_address_no_email(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        try:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
            self.assertTrue(True)
        except OrderLikeValidationFailure as e:
            self.fail(e)

    def test_shipping_address_invalid_email(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='*' * 65,
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.email_1')

    def test_shipping_address_invalid_name(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'♨',
                first_name=u'♨',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='test@example.com',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.last_name')

    def test_shipping_address_name_too_long(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓' * 40,
                first_name=u'名',
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='test@example.com',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.last_name')

        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名' * 40,
                last_name_kana=u'セイ',
                first_name_kana=u'メイ',
                zip='0000000',
                email_1='test@example.com',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.last_name')

    def test_shipping_address_invalid_name_kana(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=mock.Mock(
                tel_1=u'00000000000',
                tel_2=u'',
                last_name=u'姓',
                first_name=u'名',
                last_name_kana=u'ヹ',
                first_name_kana=u'ヹ',
                zip='0000000',
                email_1='test@example.com',
                email_2='',
                ),
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        with self.assertRaises(OrderLikeValidationFailure) as e:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
        self.assertEquals(e.exception.path, 'shipping_address.last_name_kana')

    def test_no_shipping_address(self):
        from . import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        from ..exceptions import OrderLikeValidationFailure 
        current_date = datetime.now()
        order_like = mock.Mock(
            shipping_address=None,
            issuing_end_at=current_date + timedelta(seconds=1),
            payment_due_at=current_date + timedelta(seconds=1),
            total_amount=1,
            payment_delivery_pair=mock.Mock(
                payment_method=mock.Mock(
                    payment_plugin_id=SEJ_PAYMENT_PLUGIN_ID
                    ),
                delivery_method=mock.Mock(
                    delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID
                    )
                )
            )
        try:
            self._callFUT(testing.DummyRequest(), current_date, order_like, ticketing=False)
            self.assertTrue(True)
        except OrderLikeValidationFailure as e:
            self.fail(e)

class PluginTestBase(unittest.TestCase, CoreTestMixin, CartTestMixin):
    def setUp(self):
        from datetime import datetime
        from altair.app.ticketing.sej.interfaces import ISejPaymentAPICommunicator, ISejPaymentAPICommunicatorFactory
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.sej.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.lots.models',
            ])
        self.request = testing.DummyRequest()
        config = testing.setUp(request=self.request, settings={
            'altair.sej.api_key': 'XXXXX',
            'altair.sej.inticket_api_url': 'http://example.com/',
            'altair.sej.shop_id': '30520',
        })
        config.include('altair.app.ticketing.sej')
        config.include('altair.app.ticketing.sej.userside_impl')
        config.include('altair.app.ticketing.formatter')
        self.result = {}
        self.dummy_communicator_called = False
        @implementer(ISejPaymentAPICommunicator)
        class DummySejPaymentAPICommunicator(object):
            def request(_self, params, retry_flg=False):
                self.dummy_communicator_called = True
                return self.result

            def __init__(_self, tenant, path):
                pass
        config.registry.registerUtility(DummySejPaymentAPICommunicator, ISejPaymentAPICommunicatorFactory)
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.cart.models import CartSetting
        self.cart_setting = CartSetting(type='standard')
        self.session.add(self.cart_setting)
        self.session.add(self.organization)
        self.session.add(self.event)
        self._setup_fixture()
        self.performance.start_on = datetime(2012, 4, 1, 0, 0, 0)
        self.session.flush()

    def tearDown(self):
        testing.tearDown()
        self.session.remove()
        from altair.app.ticketing.sej.api import remove_default_session
        remove_default_session()
        _teardown_db()

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
        assert stock in self.stocks

        result = []
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                result.append(seat)
                if len(result) == quantity:
                    break
        else:
            assert False, 'len(result) < quantity'
        return result

    def _setup_fixture(self):
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.sej.models import SejPaymentType, SejTicketTemplateFile, _session
        from altair.app.ticketing.core.models import SejTenant
        _session.add(SejTicketTemplateFile(template_id='TTTS000001', notation_version=2))
        _session.commit()
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
            order.order_no=self.new_order_no()
            order.created_at = datetime(2012, 1, 1, 0, 0, 0)
            order.payment_due_at = datetime(2012, 1, 5, 0, 0, 0)
            sej_order = self._create_sej_order(order, payment_type)
            self.session.add(order)
            order_pairs[payment_type] = (order, sej_order)
        return order_pairs

    def _create_carts(self):
        from datetime import datetime
        carts = {}
        for payment_type in self._payment_types:
            cart = self._create_cart(
                zip(self.products, [1]),
                sales_segment=self.sales_segment,
                cart_setting=self.cart_setting,
                pdmp=self.applicable_pdmps[0]
                )
            cart.performance = self.performance
            cart.created_at = datetime(2012, 1, 1, 0, 0, 0)

            carts[payment_type] = cart
        return carts

    def _create_sej_order(self, order, payment_type):
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejPaymentType
        from altair.app.ticketing.sej.models import _session
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
                ticket_data_xml=u'<TICKET></TICKET>',
                product_item_id=12345
                )
            for ordered_product in order.items
            for i, ordered_product_item in enumerate(ordered_product.elements)
            ]

        retval = SejOrder(
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
            regrant_number_due_at=(order.created_at + timedelta(days=5)),
            shop_id='30520',
            tickets=tickets
            )
        if int(payment_type) != SejPaymentType.Prepayment.v:
            retval.payment_due_at = order.created_at + timedelta(days=10)
        if int(payment_type) != SejPaymentType.PrepaymentOnly.v:
            retval.ticketing_start_at = order.created_at
            retval.ticketing_due_at = order.created_at + timedelta(days=10)
        _session.add(retval)
        _session.commit()
        return retval

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
            self.result = {
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
            self.assertEqual(cart.order_no, order.order_no)

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order) in order_pairs.items():
            self.result = {
                'X_shop_order_id': sej_order.order_no,
                'X_haraikomi_no': sej_order.billing_number,
                'X_hikikae_no': sej_order.exchange_number,
                'X_url_info': sej_order.exchange_sheet_url,
                'iraihyo_id_00': sej_order.exchange_sheet_number,
                'X_ticket_cnt': sej_order.total_ticket_count,
                'X_ticket_hon_cnt': sej_order.ticket_count,
                'X_goukei_kingaku': sej_order.total_price,
                'X_ticket_daikin': sej_order.ticket_price,
                'X_ticket_kounyu_daikin': sej_order.commission_fee,
                'X_hakken_daikin': sej_order.ticketing_fee,
                }
            plugin.refresh(self.request, order)
            self.assertTrue(self.dummy_communicator_called)

    def test_refresh_fail_without_sej_order(self):
        from altair.app.ticketing.orders.models import Order
        from .sej import SejPluginFailure
        plugin = self._makeOne()
        order = Order(order_no='XX0000000000', organization_id=self.organization.id)
        with self.assertRaises(SejPluginFailure) as c:
            plugin.refresh(self.request, order)
        self.assertEqual(c.exception.message, 'no corresponding SejOrder found')
        self.assertEqual(c.exception.order_no, order.order_no)

    def test_refresh_fail_already_paid(self):
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.sej.models import SejPaymentType
        from .sej import SejPluginFailure
        plugin = self._makeOne()
        order = Order(
            order_no='XX0000000000',
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=self.sales_segment,
            total_amount=100,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            special_fee=0,
            created_at=datetime.now(),
            paid_at=datetime.now()
            )
        sej_order = self._create_sej_order(order, SejPaymentType.PrepaymentOnly.v)
        order.total_amount = 200
        with self.assertRaises(SejPluginFailure) as c:
            plugin.refresh(self.request, order)
        self.assertEqual(c.exception.message, 'already paid')
        self.assertEqual(c.exception.order_no, order.order_no)

    @mock.patch('altair.app.ticketing.payments.plugins.sej.is_same_sej_order')
    def test_refresh_success_already_paid_same_amount(self, is_same_sej_order):
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.sej.models import SejPaymentType
        from .sej import SejPluginFailure
        plugin = self._makeOne()
        order = Order(
            order_no='XX0000000000',
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=self.sales_segment,
            total_amount=100,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            special_fee=0,
            created_at=datetime.now(),
            paid_at=datetime.now()
            )
        sej_order = self._create_sej_order(order, SejPaymentType.PrepaymentOnly.v)
        is_same_sej_order.return_value = True
        try:
            plugin.refresh(self.request, order)
            self.assertTrue(True)
        except Exception as e:
            self.fail(e)

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
            self.result = {
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
            new_sej_order = self.session.query(SejOrder).filter_by(order_no=cart.order_no).one()
            new_sej_tickets = self.session.query(SejTicket).filter_by(sej_order_id=new_sej_order.id).all()
            self.assertTrue(len(new_sej_tickets), 1)
            self.assertTrue(new_sej_tickets[0].barcode_number, '00000001')

    def test_refresh(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            self.result = {
                'X_shop_order_id': sej_order.order_no,
                'X_haraikomi_no': sej_order.billing_number,
                'X_hikikae_no': sej_order.exchange_number,
                'X_url_info': sej_order.exchange_sheet_url,
                'iraihyo_id_00': sej_order.exchange_sheet_number,
                'X_ticket_cnt': sej_order.total_ticket_count,
                'X_ticket_hon_cnt': sej_order.ticket_count,
                'X_goukei_kingaku': sej_order.total_price,
                'X_ticket_daikin': sej_order.ticket_price,
                'X_ticket_kounyu_daikin': sej_order.commission_fee,
                'X_hakken_daikin': sej_order.ticketing_fee,
                }
            if payment_type != SejPaymentType.PrepaymentOnly:
                self.result.update({
                    'X_barcode_no_01': '00000002',
                    })
            plugin.refresh(self.request, order)
            self.assertTrue(self.dummy_communicator_called)
            self.assertTrue(sej_order.tickets[0].barcode_number, '00000002')

    def test_refresh_fail_already_delivered(self):
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.sej.models import SejPaymentType
        from .sej import SejPluginFailure
        plugin = self._makeOne()
        now = datetime.now()
        order = Order(
            order_no='XX0000000000',
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=self.sales_segment,
            total_amount=100,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            special_fee=0,
            payment_due_at=now + timedelta(days=5),
            created_at=now,
            delivered_at=now
            )
        sej_order = self._create_sej_order(order, SejPaymentType.Prepayment.v)
        with self.assertRaises(SejPluginFailure) as c:
            plugin.refresh(self.request, order)
        self.assertEqual(c.exception.message, 'already delivered')
        self.assertEqual(c.exception.order_no, order.order_no)

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
            self.result = {
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
            with mock.patch('altair.app.ticketing.payments.plugins.sej.datetime') as m:
                m.now.return_value = datetime(2012, 1, 1, 0, 0, 0)
                order = plugin.finish(self.request, cart)
            self.session.flush()
            new_sej_order = self.session.query(SejOrder).filter_by(order_no=order.order_no).one()
            new_sej_tickets = self.session.query(SejTicket).filter_by(sej_order_id=new_sej_order.id).all()
            self.assertTrue(new_sej_tickets[0].barcode_number, '00000001')

    def test_refresh(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            self.result = {
                'X_shop_order_id': sej_order.order_no,
                'X_haraikomi_no': sej_order.billing_number,
                'X_hikikae_no': sej_order.exchange_number,
                'X_url_info': sej_order.exchange_sheet_url,
                'iraihyo_id_00': sej_order.exchange_sheet_number,
                'X_ticket_cnt': sej_order.total_ticket_count,
                'X_ticket_hon_cnt': sej_order.ticket_count,
                'X_goukei_kingaku': sej_order.total_price,
                'X_ticket_daikin': sej_order.ticket_price,
                'X_ticket_kounyu_daikin': sej_order.commission_fee,
                'X_hakken_daikin': sej_order.ticketing_fee,
                }
            if int(sej_order.payment_type) != int(SejPaymentType.PrepaymentOnly):
                self.result.update({
                    'X_barcode_no_01': '00000002',
                    })
            plugin.refresh(self.request, order)
            self.assertTrue(self.dummy_communicator_called)
            self.assertTrue(sej_order.tickets[0].barcode_number, '00000002')

    def test_refresh_success_already_paid(self):
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.sej.models import SejPaymentType
        from .sej import SejPluginFailure
        plugin = self._makeOne()
        now = datetime.now()
        order = Order(
            order_no='XX0000000000',
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=self.sales_segment,
            total_amount=100,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            special_fee=0,
            payment_due_at=now + timedelta(days=5),
            created_at=now,
            paid_at=now
            )
        sej_order = self._create_sej_order(order, SejPaymentType.Prepayment.v)
        self.result = {
            'X_shop_order_id': sej_order.order_no,
            'X_haraikomi_no': sej_order.billing_number,
            'X_hikikae_no': sej_order.exchange_number,
            'X_url_info': sej_order.exchange_sheet_url,
            'iraihyo_id_00': sej_order.exchange_sheet_number,
            'X_ticket_cnt': sej_order.total_ticket_count,
            'X_ticket_hon_cnt': sej_order.ticket_count,
            'X_goukei_kingaku': sej_order.total_price,
            'X_ticket_daikin': sej_order.ticket_price,
            'X_ticket_kounyu_daikin': sej_order.commission_fee,
            'X_hakken_daikin': sej_order.ticketing_fee,
            }
        try:
            plugin.refresh(self.request, order)
            self.assertTrue(True)
        except Exception as e:
            raise
            self.fail()

    def test_refresh_fail_already_delivered(self):
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.sej.models import SejPaymentType
        from .sej import SejPluginFailure
        plugin = self._makeOne()
        now = datetime.now()
        order = Order(
            order_no='XX0000000000',
            organization_id=self.organization.id,
            shipping_address=self._create_shipping_address(),
            sales_segment=self.sales_segment,
            total_amount=100,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            special_fee=0,
            payment_due_at=now + timedelta(days=5),
            created_at=now,
            delivered_at=now
            )
        sej_order = self._create_sej_order(order, SejPaymentType.Prepayment.v)
        with self.assertRaises(SejPluginFailure) as c:
            plugin.refresh(self.request, order)
        self.assertEqual(c.exception.message, 'already delivered')
        self.assertEqual(c.exception.order_no, order.order_no)

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
