# -*- coding:utf-8 -*-

import logging

from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session

from .helper import SalesSearchHelper
from .searcher import SalesSearcher

logger = logging.getLogger(__name__)


class SalesSearchResource(TicketingAdminResource):
    """
    SalesSearchのコンテキスト

    Attributes
    ----------
    request : Request
        リクエスト
    helper : SalseSearchHelper
        テンプレート側で使うヘルパー
    session : SessionMaker
        slaveセッション
    searcher : SalesSearcher
        検索用クラス
    """
    def __init__(self, request):
        """
        Parameters
        ----------
        request : Request
            リクエスト
        """
        super(SalesSearchResource, self).__init__(request)

        if not self.user:
            return

        self.request = request
        self.helper = SalesSearchHelper()
        self.session = get_db_session(request, 'slave')
        self.searcher = SalesSearcher(get_db_session(request, name="slave"))

    def search(self, sales_search_form):
        """
        販売日程管理を検索する

        Parameters
        ----------
        sales_search_form : SalesSearchForm
            Form

        Returns
        ----------
        sales_segments : list(SalesSegment)
            検索結果の販売区分
        """
        return self.searcher.search(
            self.organization.id,
            sales_search_form.sales_kind.data,
            sales_search_form.sales_term.data,
            sales_search_form.salessegment_group_kind.data,
            sales_search_form.operators.data
        )

    def get_sales_report_operators(self):
        """
        販売日程管理検索で使用するオペレータを取得する
        対象のORGで、sales_searchがONになっているオペレータ
        ----------

        Returns
        ----------
        operators : list(Operator)
            販売日程管理検索で使用するオペレータ
        """
        operators = self.session.query(Operator)\
            .filter(Operator.organization_id == self.organization.id)\
            .filter(Operator.sales_search == True)\
            .with_entities(Operator.id, Operator.name)\
            .all()
        return operators
