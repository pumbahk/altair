# -*- coding:utf-8 -*-
import logging
from collections import OrderedDict
from sqlalchemy import (
    select,
    and_,
    case,
    text,
    func,
)
from altair.app.ticketing.core.models import (
    Event,
    Performance,
    SalesSegment,
    Order,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    ShippingAddress,
)
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    UserCredential,
)
from altair.app.ticketing.sej.models import SejOrder

t_event = Event.__table__
t_performance = Performance.__table__
t_sales_segment = SalesSegment.__table__
t_order = Order.__table__
t_pdmp = PaymentDeliveryMethodPair.__table__
t_payment_method = PaymentMethod.__table__
t_delivery_method = DeliveryMethod.__table__
t_shipping_address = ShippingAddress.__table__
t_user = User.__table__
t_user_profile = UserProfile.__table__
t_user_credential = UserCredential.__table__
t_sej_order = SejOrder.__table__

summary_columns = [
    t_order.c.id,
    case([(t_order.c.canceled_at!=None,
           text("'canceled'")),
          (t_order.c.delivered_at!=None,
           text("'delivered'"))],
         else_=text("'ordered'"),
    ).label('status'),
    case([(t_order.c.canceled_at!=None,
           text(u"'キャンセル'")),
          (t_order.c.delivered_at!=None,
           text(u"'配送済み'"))],
         else_=text(u"'受付済み'"),
     ).label('status_label'),
    case([(t_order.c.canceled_at!=None,
           text(u"'important'")),
          (t_order.c.delivered_at!=None,
           text("'success'"))],
         else_=text("'warning'"),
     ).label('status_class'),
    case([(and_(t_order.c.refund_id!=None,
                t_order.c.refunded_at==None),
           text("'refunding'")),
          (t_order.c.refunded_at!=None,
           text("'refunded'")),
          (t_order.c.paid_at!=None,
           text("'paid'"))],
         else_=text("'unpaid'"),
    ).label('payment_status'),
    case([(and_(t_order.c.refund_id!=None,
                t_order.c.refunded_at==None),
           #-- XXX (中止)の場合がある
           text(u"'払戻予約'")),
          (t_order.c.refunded_at!=None,
           #-- XXX (中止)の場合がある
           text(u"'払戻済み'")),
          (t_order.c.paid_at!=None,
           text(u"'入金済み'"))],
         else_=text(u"'未入金'"),
    ).label('payment_status_label'),
    case([(and_(t_order.c.refund_id!=None,
                t_order.c.refunded_at==None),
           text("'warning'")),
          (t_order.c.refunded_at!=None,
           text("'important'")),
          (t_order.c.paid_at!=None,
           text("'success'"))],
         else_=text("'inverse'"),
    ).label('payment_status_style'),
    t_order.c.order_no, #-- 予約番号
    t_order.c.created_at, #-- 予約日時
    t_order.c.total_amount, #-- 合計
    (t_shipping_address.c.last_name
     + text("' '")
     + t_shipping_address.c.first_name).label('shipping_name'), #-- 配送先氏名
    t_event.c.id.label('event_id'),
    t_event.c.title.label('event_title'), #-- イベント
    t_payment_method.c.id.label('performance_id'),
    t_performance.c.start_on.label('performance_start_on'), #-- 開演日時
    t_order.c.card_brand, # -- カードブランド
    t_order.c.card_ahead_com_code, #-- 仕向け先コード
    t_order.c.card_ahead_com_name, #-- 仕向け先名
]

order_summary_joins = t_order.join(
    t_performance,
    and_(t_performance.c.id==t_order.c.performance_id,
         t_performance.c.deleted_at==None),
).join(
    t_event,
    and_(t_event.c.id==t_performance.c.event_id,
         t_event.c.deleted_at==None),
).join(
    t_sales_segment,
    and_(t_sales_segment.c.id==t_order.c.sales_segment_id,
         t_sales_segment.c.deleted_at==None),
).join(
    t_pdmp,
    and_(t_pdmp.c.id==t_order.c.payment_delivery_method_pair_id,
         t_pdmp.c.deleted_at==None),
).join(
    t_payment_method,
    and_(t_payment_method.c.id==t_pdmp.c.payment_method_id,
         t_payment_method.c.deleted_at==None),
).join(
    t_delivery_method,
    and_(t_delivery_method.c.id==t_pdmp.c.delivery_method_id,
         t_delivery_method.c.deleted_at==None),
).join(
    t_shipping_address,
    and_(t_shipping_address.c.id==t_order.c.shipping_address_id,
         t_shipping_address.c.deleted_at==None),
).outerjoin(
    t_user,
    and_(t_user.c.id==t_order.c.user_id,
         t_user.c.deleted_at==None),
).outerjoin(
    t_user_profile,
    and_(t_user_profile.c.user_id==t_user.c.id,
         t_user_profile.c.deleted_at==None),
).outerjoin(
    t_user_credential,
    and_(t_user_credential.c.user_id==t_user.c.id,
         t_user_credential.c.deleted_at==None),
).outerjoin(
    t_sej_order,
    and_(t_sej_order.c.order_id==t_order.c.order_no,
         t_sej_order.c.deleted_at==None),
)

logger = logging.getLogger(__name__)

"""


ステータス
 受付済み 配送済み キャンセル
 発券済み 未発券
 未入金 入金済み 払戻予約 払戻済み

決済 PaymentMethod.name
配送
予約番号
予約日時
合計
配送先氏名
イベント
開演日時
カードブランド
仕向け先

"""



sql = str(select(summary_columns, from_obj=[order_summary_joins]))


# Userに対してUserProfileが複数あると行数が増える可能性



class OrderDownload(list):

    def __init__(self, db_session, columns, condition):
        self.db_session = db_session
        self.columns = columns
        self.condition = condition

    def query_cond(self, condition, limit=None, offset=None):
        sql = ""
        params = ()
        # if 'billing_or_exchange_number' in condition:
        #     pass

        # if 'ordered_from' in condition:
        #     sql = sql + " AND `Order`.created_at >= %s"
        #     params = params + (condition['ordered_from'],)

        # if 'ordered_to' in condition:
        #     sql = sql + " AND `Order`.created_at <= %s"
        #     params = params + (condition['ordered_to'],)

        # if 'status' in condition:
        #     status_cond = []
        #     if 'ordered' in condition['status']:
        #         status_cond.append("(`Order`.canceled_at IS NULL AND `Order`.delivered_at IS NULL)")
        #     if 'delivered' in condition['status']:
        #         status_cond.append("(`Order`.canceled_at IS NULL AND `Order`.delivered_at IS NOT NULL)")
        #     if 'canceled' in condition['status']:
        #         status_cond.append("(`Order`.canceled_at IS NOT NULL)")
            
        #     if status_cond:
        #         sql = sql + " AND ( " + " OR ".join(status_cond) + " ) "

        # if 'issue_status' in condition:
        #     issue_cond = []
        #     if 'issued' in condition['issue_status']:
        #         issue_cond.append(' `Order`.issued = 1 ')
        #     if 'unissued' in condition['issue_status']:
        #         issue_cond.append(' `Order`.issued = 0 ')

        #     if issue_cond:
        #         sql = sql + " AND ( " + " OR ".join(issue_cond) + " ) "

        # if 'payment_status' in condition:
        #     # unpaid, paid, refunding, refunded
        #     payment_cond = []
        #     if 'unpaid' in condition['payment_status']:
        #         payment_cond.append("(`Order`.refunded_at IS NULL "
        #                             " AND `Order`.refund_id IS NULL "
        #                             " AND `Order`.paid_at IS NULL ) ")

        #     if 'paid' in condition['payment_status']:
        #         payment_cond.append("(`Order`.refunded_at IS NULL "
        #                             " AND `Order`.refund_id IS NULL "
        #                             " AND `Order`.paid_at IS NOT NULL ) ")

        #     if 'refunding' in condition['payment_status']:
        #         payment_cond.append("(`Order`.refunded_at IS NULL "
        #                             " AND `Order`.refund_id IS NOT NULL ) ")
        #     if 'refunded' in condition['payment_status']:
        #         payment_cond.append("(`Order`.refunded_at IS NOT NULL ) ")


        #     if payment_cond:
        #         sql = sql + " AND ( " + " OR ".join(payment_cond) + " ) "

        # if 'member_id' in condition:
        #     sql = sql + " AND UserCredential.auth_identifier = %s"
        #     params += (condition['member_id'],)

        # if 'number_of_tickets' in condition:
        #     if (condition.get('event_id') or condition.get('performance_id')):
            
        #         cond = """ AND `Order`.id in (
        #         SELECT OrderedProduct.order_id AS order_id,
        #         FROM OrderedProduct
        #         JOIN OrderedProductItem
        #         ON OrderedProduct.id = OrderedProductItem.ordered_product_id
        #         AND OrderedProductItem.deleted_at IS NULL
        #         JOIN ProductItem
        #         ON OrderedProductItem.product_item_id = ProductItem.id
        #         AND ProductItem.deleted_at IS NULL
        #         JOIN Performance
        #         ON ProductItem.performance_id = Performance.id
        #         AND Performance.deleted_at IS NULL
        #         WHERE OrderedProduct.deleted_at IS NULL
        #         """
    
        #         if condition.get('event_id'):
        #             cond = cond + " AND Performance.event_id = %s"
        #             params += (condition['event_id'],)
        #         if condition.get('performance_id'):
        #             cond = cond + " AND Performance.id = %s"
        #             params += (condition['performance_id'],)
    
    
        #         cond = cond + """
        #         GROUP BY OrderedProduct.order_id
        #         HAVING sum(ProductItem.quantity) >= %s)
        #         """
        #         params += (condition['number_of_tickets'],)
    
        #         sql = sql + cond

        # # order by
        # if 'sort' in condition:
        #     if 'direction' in condition:
        #         # asc, desc
        #         pass
        #     else:
        #         pass

        if limit is not None and offset is not None:
            sql += " LIMIT %s, %s "
            params += (offset, limit)
        elif limit is not None:
            sql += " LIMIT %s "
            params += (limit,)

        return sql, params

    def __iter__(self):
        start = 0
        stop = self.count()

        return self.execute(start, stop)


    def count(self):
        sql = select([func.count(t_order.c.id)],
                     from_obj=[order_summary_joins])

        logger.debug("sql = {0}".format(sql))
        cur = self.db_session.bind.execute(sql)
        try:
            r = cur.fetchone()
            return r[0]
        finally:
            cur.close()


    def __getslice__(self, start, stop):
        return self.execute(start, stop)

    def execute(self, start, stop):
        logger.debug("start = {0}, stop = {1}".format(start, stop))
        limit = 1000
        offset = start
        while True:
            sql = select(summary_columns, 
                         from_obj=[order_summary_joins]
            ).limit(limit
            ).offset(offset)

            logger.debug("limit = {0}, offset = {1}".format(limit, offset))
            logger.debug("sql = {0}".format(sql))
            cur = self.db_session.bind.execute(sql)
            try:
                rows = cur.fetchall()
                logger.debug('fetchall')
                if not rows:
                    break

                for row in rows:
                    yield OrderedDict(
                        row.items()
                    )
                offset = offset + limit
                limit = min(stop - offset, limit)
                if limit <= 0:
                    break
            finally:
                logger.debug('close')
                cur.close()

    def __getitem__(self, s): # for slice
        logger.debug("slice {0}".format(s))
        assert isinstance(s, slice)
        assert False
        start = s.start
        stop = s.stop
        return self.__getslice__(start, stop)

    def __len__(self):
        c = self.count()
        logger.debug("count = {0}".format(c))
        return c
