# -*- coding: utf-8 -*-
from unittest import TestCase

from altair.app.ticketing.users.models import User
from altair.app.ticketing.core import models as core_models

from ... import testing
from . import reporting


class ExportForStockHolderTest(TestCase):
    def setUp(self):
        # DB用意
        self.session = testing._setup_db()

    def tearDown(self):
        testing._teardown_db()


    def test_stocks_ok(self):
        event, stock_holder = self._create_data()
        report_type = "stock"
        result = reporting.export_for_stock_holder(event, 
                                                   stock_holder,
                                                   report_type)
        self.assertTrue(len(result.as_string()) > 0)


    def _create_data(self):
        from datetime import datetime
        # EventとStockHolder用意
        account = core_models.Account()
        account.save()
        organization = core_models.Organization(short_name="testing")
        organization.save()
        event = core_models.Event(account=account,
                                  organization=organization)
        event.save()
        site = core_models.Site()
        venue = core_models.Venue(site=site,
                                  organization=organization)
        performance = core_models.Performance(event=event,
                                              venue=venue,
                                              start_on=datetime(2013, 3, 4))
        performance.save()
        stock_holder = core_models.StockHolder(event=event,
                                               account=account)
        stock_holder.save()
        return event, stock_holder

    def test_unsold_ok(self):
        
        event, stock_holder = self._create_data()

        result = reporting.export_for_stock_holder(event, stock_holder, 'unsold')
        self.assertTrue(len(result.as_string()) > 0)


