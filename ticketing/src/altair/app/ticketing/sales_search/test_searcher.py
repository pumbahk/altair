# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

import mock
from .util import SaleSearchUtil
from altair.app.ticketing.core.models import DateCalculationBase
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper
from markupsafe import Markup
from pyramid import testing
from .const import SalesTermEnum

from .helper import SalesSearchHelper
from .searcher import SalesSearcher


class DummySalesSegmentGroup(testing.DummyModel):
    pass


class DummySalesSegment(testing.DummyModel):
    pass


class DummyPaymentDeliveryMethodPair(testing.DummyModel):
    pass


class SearcherTest(unittest.TestCase):
    """
    販売日程管理検索の検索クラスのテスト
    ----------
    """

    def setUp(self):
        self.config = testing.setUp()
        self.target = SalesSearcher(session=None)

    def tearDown(self):
        testing.tearDown()

    def test__create_term(self):
        """
        __create_termのテスト
        ----------
        """
        pass

    def test__create_kind(self):
        kind = self.target.create_kind([])
        self.assertEqual(kind, [])

        kind = self.target.create_kind([SalesTermEnum.TODAY.v])
        self.assertEqual(kind, [])

    def test_search(self):
        """
        searchのテスト
        ----------
        """
        # @TODO DBアクセスのテストケースをあとで作成する
        pass
