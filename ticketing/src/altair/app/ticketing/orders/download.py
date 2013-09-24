# -*- coding:utf-8 -*-
"""
予約番号	ステータス	決済ステータス	予約日時	支払日時	配送日時	キャンセル日時	合計金額	決済手数料	配送手数料	システム利用料	内手数料金額	メモ	カードブランド	仕向け先企業コード	仕向け先企業名	SEJ払込票番号	SEJ引換票番号	メールマガジン受信可否	姓	名	姓(カナ)	名(カナ)	ニックネーム	性別	会員種別名	会員グループ名	会員種別ID	配送先姓	配送先名	配送先姓(カナ)	配送先名(カナ)	郵便番号	国	都道府県	市区町村	住所1	住所2	電話番号1	電話番号2	FAX	メールアドレス1	メールアドレス2	決済方法	引取方法	イベント	公演	公演コード	公演日	会場	商品単価[0]	商品個数[0]	商品名[0]	販売区分[0]	販売手数料率[0]	商品明細名[0][0]	商品明細単価[0][0]	商品明細個数[0][0]	発券作業者[0][0]	座席名[0][0][0]

"""

import re
import logging
from collections import OrderedDict
from sqlalchemy import (
    select,
    and_,
    or_,
    case,
    text,
    func,
)
from altair.app.ticketing.core.models import (
    Organization,
    Event,
    Performance,
    Venue,
    SalesSegment,
    SalesSegmentGroup,
    Seat,
    orders_seat_table,
    Order,
    OrderedProduct,
    OrderedProductItem,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    ShippingAddress,
    Product,
    ProductItem,
)
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    UserCredential,
)
from altair.app.ticketing.sej.models import SejOrder

logger = logging.getLogger(__name__)

t_organization = Organization.__table__
t_event = Event.__table__
t_performance = Performance.__table__
t_sales_segment = SalesSegment.__table__
t_sales_segment_group = SalesSegmentGroup.__table__
t_order = Order.__table__
t_pdmp = PaymentDeliveryMethodPair.__table__
t_payment_method = PaymentMethod.__table__
t_delivery_method = DeliveryMethod.__table__
t_shipping_address = ShippingAddress.__table__
t_user = User.__table__
t_user_profile = UserProfile.__table__
t_user_credential = UserCredential.__table__
t_sej_order = SejOrder.__table__
t_seat = Seat.__table__
t_ordered_product = OrderedProduct.__table__
t_ordered_product_item = OrderedProductItem.__table__
t_product = Product.__table__
t_product_item = ProductItem.__table__
t_venue = Venue.__table__

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

detail_summary_columns = summary_columns + [
    t_order.c.paid_at, #支払日時
    t_order.c.delivered_at, #配送日時
    t_order.c.canceled_at, #キャンセル日時
    t_order.c.transaction_fee, #決済手数料
    t_order.c.delivery_fee, #配送手数料
    t_order.c.system_fee, #システム利用料
    #内手数料金額 ?
    t_order.c.note, #メモ

    # SEJOrder
    t_sej_order.c.billing_number, #SEJ払込票番号
    t_sej_order.c.exchange_number, #SEJ引換票番号

    #UserProfile
    #メールマガジン受信可否
    t_user_profile.c.last_name.label('user_last_name'), #姓
    t_user_profile.c.first_name.label('user_first_name'), #名
    t_user_profile.c.last_name_kana.label('user_last_name_kana'), #姓(カナ)
    t_user_profile.c.first_name_kana.label('user_first_name_kana'), #名(カナ)
    t_user_profile.c.nick_name.label('user_nick_name'), #ニックネーム
    t_user_profile.c.sex.label('user_sex'), #性別

    # Membership
    #会員種別名
    #会員グループ名
    #会員種別ID

    # ShippingAddress
    t_shipping_address.c.last_name, #配送先姓
    t_shipping_address.c.first_name, #配送先名
    t_shipping_address.c.last_name_kana, #配送先姓(カナ)
    t_shipping_address.c.first_name_kana, #配送先名(カナ)
    t_shipping_address.c.zip, #郵便番号
    t_shipping_address.c.country, #国
    t_shipping_address.c.prefecture, #都道府県
    t_shipping_address.c.city, #市区町村
    t_shipping_address.c.address_1, #住所1
    t_shipping_address.c.address_2, #住所2
    t_shipping_address.c.tel_1, #電話番号1
    t_shipping_address.c.tel_2, #電話番号2
    t_shipping_address.c.fax, #FAX
    t_shipping_address.c.email_1, #メールアドレス1
    t_shipping_address.c.email_2, #メールアドレス2

    t_payment_method.c.name.label('payment_method.name'), #決済方法
    t_delivery_method.c.name.label('delivery_method.name'), #引取方法

    # Performance
    t_performance.c.name.label('performance_name'), #公演
    t_performance.c.code.label('performance_code'), #公演コード

    # Venue
    #会場

    # Product
    t_product.c.id.label('product_id'), # break key
    t_product.c.name.label('product_name'), #商品名[0]
    t_product.c.price.label('product_price'), #商品単価[0]
    # OrderedProduct
    t_ordered_product.c.quantity.label('product_quantity'), #商品個数[0]
    #販売区分[0]
    #販売手数料率[0]

    # ProductItem
    t_product_item.c.name.label('item_name'), #商品明細名[0][0]
    t_product_item.c.price.label('item_price'), #商品明細単価[0][0]
    # OrderedProductItem
    t_ordered_product_item.c.quantity.label('item_quantity'), #商品明細個数[0][0]
    #発券作業者[0][0]
    #座席名[0][0][0]
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
    t_organization,
    and_(t_organization.c.id==t_event.c.organization_id,
         t_organization.c.deleted_at==None),
).join(
    t_sales_segment,
    and_(t_sales_segment.c.id==t_order.c.sales_segment_id,
         t_sales_segment.c.deleted_at==None),
).join(
    t_sales_segment_group,
    and_(t_sales_segment_group.c.id==t_sales_segment.c.sales_segment_group_id,
         t_sales_segment_group.c.deleted_at==None),
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

order_product_summary_joins = order_summary_joins.join(
    t_ordered_product,
    and_(t_ordered_product.c.order_id==t_order.c.id,
         t_ordered_product.c.deleted_at==None),
).join(
    t_product,
    and_(t_product.c.id==t_ordered_product.c.product_id,
         t_product.c.deleted_at==None),
).join(
    t_ordered_product_item,
    and_(t_ordered_product_item.c.ordered_product_id==t_ordered_product.c.id,
         t_ordered_product_item.c.deleted_at==None),
).join(
    t_product_item,
    and_(t_product_item.c.id==t_ordered_product_item.c.product_item_id,
         t_product_item.c.deleted_at==None),
).join(
    t_venue,
    and_(t_venue.c.performance_id==t_performance.c.id,
         t_venue.c.deleted_at==None),
)


# Userに対してUserProfileが複数あると行数が増える可能性

class KeyBreakAdapter(object):
    def __init__(self, iter, key, child1, child1_key, child2=[]):

        self.results = []
        # 初回判定用のマーカー
        marker = object()
        last_key = marker
        last_child1_key = marker
        last_item = None
        breaked_items = []
        child1_count = 0
        child2_count = 0
        i = j = 0 # bad name
        for item in iter:

            # first key break
            if item[key] != last_key and last_key != marker:
                result = OrderedDict(last_item)
                for name, value in breaked_items:
                    result[name] = value
                for c in child1 + child2:
                    result.pop(c)
                self.results.append(result)
                breaked_items = []
                i = j = 0

            # second key break
            if item[child1_key] != last_child1_key or item[key] != last_key:
                for childitem1 in child1:
                    name = "{0}[{1}]".format(childitem1, i)
                    breaked_items.append(
                        (name,
                         item[childitem1]))
                    child1_count = max(child1_count, i)
                j = 0

            for childitem2 in child2:
                name = "{0}[{1}][{2}]".format(childitem2, i, j)
                breaked_items.append(
                    (name,
                     item[childitem2]))
                child2_count = max(child2_count, j)

            if item[child1_key] != last_child1_key:
                i += 1
            last_item = item
            last_key = item[key]
            last_child1_key = item[child1_key]
            j += 1

        # 最終アイテムにはキーブレイクが発生しないので明示的に処理する(i,jは処理済み)
        result = OrderedDict(last_item)
        for childitem1 in child1:
            name = "{0}[{1}]".format(childitem1, i)
            breaked_items.append(
                (name,
                 item[childitem1]))
            child1_count = max(child1_count, i)
            for childitem2 in child2:
                name = "{0}[{1}][{2}]".format(childitem2, i, j)
                breaked_items.append(
                    (name,
                     item[childitem2]))
                child2_count = max(child2_count, j)
        for c in child1 + child2:
            result.pop(c)

        headers = list(result)
        self.headers = headers
        for i in range(child1_count):
            for n in child1:
                self.headers.append("{0}[{1}]".format(n, i))
            for j in range(child2_count):
                for n in child2:
                    self.headers.append("{0}[{1}][{2}]".format(n, i, j))

    def __iter__(self):
        return iter(self.results)


class OrderDownload(list):

    #target = order_summary_joins
    target = order_product_summary_joins
    #columns = summary_columns
    columns = detail_summary_columns

    def __init__(self, db_session, organization_id, columns, condition):
        self.db_session = db_session
        #self.columns = columns
        self.organization_id = organization_id
        self.condition = self.query_cond(condition)

    def query_cond(self, condition):
        cond = t_organization.c.id==self.organization_id
        if condition is None:
            return cond

        # 予約番号
        if condition.order_no.data:
            value = condition.order_no.data
            if isinstance(value, basestring):
                value = re.split(ur'[ \t　]+', value)

            cond = and_(cond,
                        t_order.c.order_no.in_(value))

        # 座席番号 seat_number:
        if condition.seat_number.data:
            value = condition.seat_number.data
            subq = select([orders_seat_table.c.OrderedProductItem_id],
                          from_obj=orders_seat_table.join(
                              t_seat,
                              and_(t_seat.c.id==orders_seat_table.c.seat_id,
                                   t_seat.c.deleted_at==None),
                          ),
                          whereclause=t_seat.c.name.like('%s%%' % value))
            cond = and_(cond,
                        t_ordered_product_item.c.id.in_(subq))

        # 電話番号 tel:
        if condition.tel.data:
            value = condition.tel.data
            cond = and_(cond,
                        or_(t_shipping_address.c.tel_1==value,
                            t_shipping_address.c.tel_2==value))

        # 氏名 name:
        if condition.name.data:
            value = condition.name.data
            cond = and_(cond,
                        or_(t_shipping_address.c.last_name + " " + t_shipping_address.c.first_name == value,
                            t_shipping_address.c.last_name == value,
                            t_shipping_address.c.first_name == value,
                        ))

        # メールアドレス email:
        if condition.email.data:
            value = condition.email.data
            cond = and_(cond,
                        or_(t_shipping_address.c.email_1==value,
                            t_shipping_address.c.email_2==value,
                        ))

        # 会員番号 member_id:
        if condition.member_id.data:
            value = condition.member_id.data
            cond = and_(cond,
                        t_user_credential.c.auth_identifier == value)

        # 予約日時(開始)
        if condition.ordered_from.data:
            value = condition.ordered_from.data
            cond = and_(cond,
                        t_order.c.created_at>=value)

        # 予約日時(終了)
        if condition.ordered_to.data:
            value = condition.ordered_to.data
            cond = and_(cond,
                        t_order.c.created_at<value)

        # セブン−イレブン払込票/引換票番号
        if condition.billing_or_exchange_number.data:
            value = condition.billing_or_exchange_number.data
            cond = and_(cond,
                        or_(t_sej_order.c.exchange_number==value,
                            t_sej_order.c.billing_number==value))

        # イベント event_id
        if condition.event_id.data:
            value = condition.event_id.data
            cond = and_(cond,
                        t_event.c.id==value)

        # 公演 performance_id
        if condition.performance_id.data:
            value = condition.performance_id.data
            cond = and_(cond,
                        t_performance.c.id==value)

        # 販売区分(実際は販売区分グループ) sales_segment_group_id:
        if condition.sales_segment_group_id.data:
            value = condition.sales_segment_group_id.data
            cond = and_(cond,
                        t_sales_segment_group.c.id==value)

        # 決済方法 payment_method
        if condition.payment_method.data:
            value = condition.payment_method.data
            cond = and_(cond,
                        t_payment_method.c.id==value)

        # 引取方法 delivery_method
        if condition.delivery_method.data:
            value = condition.delivery_method.data
            cond = and_(cond,
                        t_delivery_method.c.id==value)

        # ステータス(注文)
        if condition.status.data:
            status_cond = []
            value = condition.status.data
            if 'ordered' in value:
                status_cond.append(and_(t_order.c.canceled_at==None,
                                        t_order.c.delivered_at==None))
            if 'delivered' in value:
                status_cond.append(and_(t_order.c.canceled_at==None,
                                       t_order.c.delivered_at!=None))
            if 'canceled' in value:
                status_cond.append(t_order.c.canceled_at!=None)

            if status_cond:
                cond = and_(cond,
                            or_(*status_cond))

        # ステータス(発券)
        if condition.issue_status.data:
            issue_cond = []
            value = condition.issue_status.data
            if 'issued' in value:
                issue_cond.append(t_order.c.issued==1)
            if 'unissued' in value:
                issue_cond.append(t_order.c.issued==0)

            if issue_cond:
                cond = and_(cond,
                            or_(*issue_cond))


        # ステータス(決済)
        if condition.payment_status.data:
            value = condition.payment_status.data
            # unpaid, paid, refunding, refunded
            payment_cond = []
            if 'unpaid' in value:
                payment_cond.append(and_(t_order.c.refunded_at==None,
                                         t_order.c.refund_id==None,
                                         t_order.c.paid_at==None))

            if 'paid' in value:
                payment_cond.append(and_(t_order.c.refunded_at==None,
                                         t_order.c.refund_id==None,
                                         t_order.c.paid_at!=None))

            if 'refunding' in value:
                payment_cond.append(and_(t_order.c.refunded_at==None,
                                         t_order.c.refund_id!=None))

            if 'refunded' in value:
                payment_cond.append(t_order.c.refunded_at!=None)

            if payment_cond:
                cond = and_(cond,
                            or_(*payment_cond))

        if condition.number_of_tickets.data:
            if condition.performance_id.data or condition.event_id.data:
                value = condition.number_of_tickets.data
                from_obj = t_ordered_product_item.join(
                    t_product_item,
                    and_(t_product_item.c.id==t_ordered_product_item.c.product_item_id,
                         t_product_item.c.deleted_at==None),
                ).join(
                    t_ordered_product,
                    and_(t_ordered_product.c.id==t_ordered_product_item.c.ordered_product_id,
                         t_ordered_product.c.deleted_at==None),
                ).join(
                    t_performance,
                    and_(t_performance.c.id==t_product_item.c.performance_id,
                         t_performance.c.deleted_at==None),
                )
    
                sub_cond = t_ordered_product_item.c.deleted_at==None
                if condition.event_id.data:
                     sub_cond = and_(sub_cond,
                                    t_performance.c.event_id==condition.event_id.data)
                if condition.performance_id.data:
                     sub_cond = and_(sub_cond,
                                     t_performance.c.id==condition.event_id.data)
    
                subq = select([t_ordered_product.c.order_id],
                              from_obj=from_obj,
                              whereclause=sub_cond,
                ).group_by(
                    t_ordered_product.c.order_id
                ).having(
                    func.sum(t_ordered_product_item.c.quantity)>=value
                )
    
                cond = and_(cond,
                            t_order.c.id.in_(subq))
    
        # # order by
        # if 'sort' in condition:
        #     if 'direction' in condition:
        #         # asc, desc
        #         pass
        #     else:
        #         pass

        return cond

    def __iter__(self):
        start = 0
        stop = self.count()

        return self.execute(start, stop)


    def count(self):
        sql = select([func.count(t_order.c.id)],
                     from_obj=[self.target],
                     whereclause=self.condition,
        )


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
        limit = min(1000, stop-start)
        offset = start
        while True:
            sql = select(self.columns, 
                         from_obj=[self.target],
                         whereclause=self.condition,
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
