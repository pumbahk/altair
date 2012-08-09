# -*- coding: utf-8 -*-
from unittest import TestCase

from ticketing.users.models import User
from ticketing.core import models as core_models

from ... import testing
from . import reporting


class ExportForStockHolderTest(TestCase):
    def setUp(self):
        # DB用意
        self.session = testing._setup_db()
        # EventとStockHolder用意
        self.account = core_models.Account()
        self.account.save()
        self.organization = core_models.Organization()
        self.organization.save()
        self.event = core_models.Event(
            account=self.account,
            organization=self.organization)
        self.event.save()
        self.performance = core_models.Performance(event=self.event)
        self.performance.save()
        self.stock_holder = core_models.StockHolder(event=self.event)
        self.stock_holder.save()

    def test_ok(self):
        result = reporting.export_for_stock_holder(self.event, self.stock_holder)
        self.assertTrue(len(result.as_string()) > 0)

    def tearDown(self):
        testing._teardown_db()


class ExportForStockHolderUnsoldTest(TestCase):
    def setUp(self):
        # DB用意
        self.session = testing._setup_db()
        # EventとStockHolder用意
        self.account = core_models.Account()
        self.account.save()
        self.organization = core_models.Organization()
        self.organization.save()
        self.event = core_models.Event(
            account=self.account,
            organization=self.organization)
        self.event.save()
        self.performance = core_models.Performance(event=self.event)
        self.performance.save()
        self.stock_holder = core_models.StockHolder(event=self.event)
        self.stock_holder.save()

    def test_ok(self):
        result = reporting.export_for_stock_holder_unsold(self.event, self.stock_holder)
        self.assertTrue(len(result.as_string()) > 0)

    def tearDown(self):
        testing._teardown_db()
