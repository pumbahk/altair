# -*- coding: utf-8 -*-
import logging

from altair.app.ticketing.models import DBSession
from sqlalchemy.sql.expression import desc

from .models import RakutenTvSalesData

logger = logging.getLogger(__name__)


def rakuten_tv_sales_data_to_order_paid_at(order, session=None):
    """
    指定されたorderを元にRakutenTvSalesData.paid_at(決済日時)ををセットします。
    :param order: 注文情報
    :param session: DBセッション
    """

    if session is None:
        session = DBSession

    rakuten_tv_sales_data = session.query(RakutenTvSalesData) \
        .filter(RakutenTvSalesData.order_no == order.order_no) \
        .filter(RakutenTvSalesData.performance_id == order.performance_id) \
        .filter(RakutenTvSalesData.easy_id.isnot(None)) \
        .filter(RakutenTvSalesData.paid_at.is_(None)) \
        .filter(RakutenTvSalesData.refunded_at.is_(None)) \
        .filter(RakutenTvSalesData.canceled_at.is_(None)) \
        .filter(RakutenTvSalesData.deleted_at.is_(None)) \
        .order_by(desc(RakutenTvSalesData.id)).first()

    if rakuten_tv_sales_data:
        # 決済済みにする
        RakutenTvSalesData.rakuten_tv_sales_data_paid_at(rakuten_tv_sales_data)


def rakuten_tv_sales_data_to_order_canceled_at(order, session=None):
        """
        指定されたorderを元にRakutenTvSalesData.canceled_at(キャンセル日時)をセットします。
        :param order: 注文情報
        :param session: DBセッション
        """

        if session is None:
            session = DBSession

        rakuten_tv_sales_data = session.query(RakutenTvSalesData) \
            .filter(RakutenTvSalesData.order_no == order.order_no) \
            .filter(RakutenTvSalesData.performance_id == order.performance_id) \
            .filter(RakutenTvSalesData.easy_id.isnot(None)) \
            .filter(RakutenTvSalesData.refunded_at.is_(None)) \
            .filter(RakutenTvSalesData.canceled_at.is_(None)) \
            .filter(RakutenTvSalesData.deleted_at.is_(None)) \
            .order_by(desc(RakutenTvSalesData.id)).first()

        if rakuten_tv_sales_data:
            # キャンセルにする
            RakutenTvSalesData.rakuten_tv_sales_data_canceled_at(rakuten_tv_sales_data)
