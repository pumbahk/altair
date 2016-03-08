# -*- coding:utf-8 -*-
"""
予約番号	ステータス	決済ステータス	予約日時	支払日時	配送日時	キャンセル日時	合計金額	決済手数料	配送手数料	システム利用料	特別手数料	内手数料金額	メモ	特別手数料	カードブランド	仕向け先企業コード	仕向け先企業名	SEJ払込票番号	SEJ引換票番号	メールマガジン受信可否	姓	名	姓(カナ)	名(カナ)	ニックネーム	性別	会員種別名	会員グループ名	会員種別ID	配送先姓	配送先名	配送先姓(カナ)	配送先名(カナ)	郵便番号	国	都道府県	市区町村	住所1	住所2	電話番号1	電話番号2	FAX	メールアドレス1	メールアドレス2	決済方法	引取方法	イベント	公演	公演コード	公演日	会場	商品単価[0]	商品個数[0]	商品名[0]	販売区分[0]	販売手数料率[0]	商品明細名[0][0]	商品明細単価[0][0]	商品明細個数[0][0]	発券作業者[0][0]	座席名[0][0][0]

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
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    ShippingAddress,
    Product,
    ProductItem,
    TicketPrintHistory,
)
from altair.app.ticketing.orders.models import (
    orders_seat_table,
    Order,
    OrderedProduct,
    OrderedProductAttribute,
    OrderedProductItem,
    SummarizedPaymentDeliveryMethodPair,
    SummarizedPaymentMethod,
    )
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    UserCredential,
    Membership,
    MemberGroup,
)
from altair.app.ticketing.operators.models import (
    Operator,
)
from altair.app.ticketing.mailmags.models import (
    MailSubscription,
    MailMagazine,
    MailSubscriptionStatus,
)
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    )
from altair.app.ticketing.sej.models import SejOrder
from altair.app.ticketing.famiport import api as famiport_api
from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
from altair.keybreak import (
    KeyBreakCounter,
)

from .api import get_multicheckout_info

logger = logging.getLogger(__name__)

japanese_columns = {
    u'id': u"注文ID",
    u'order_no': u'予約番号',
    u'status': u'ステータス',
    u'status_label': u'ステータス',
    u'status_class': u'ステータス',
    u'payment_status': u'決済ステータス',
    u'payment_status_label': u'決済ステータス',
    u'payment_status_class': u'決済ステータス',
    u'delivery_status': u'引取ステータス',
    u'delivery_status_label': u'引取ステータス',
    u'delivery_status_class': u'引取ステータス',
    u'created_at': u'予約日時',
    u'paid_at': u'支払日時',
    u'delivered_at': u'配送日時',
    u'canceled_at': u'キャンセル日時',
    u'total_amount': u'合計金額',
    u'transaction_fee': u'決済手数料',
    u'delivery_fee': u'配送手数料',
    u'system_fee': u'システム利用料',
    u'special_fee': u'特別手数料',
    u'special_fee_name': u'特別手数料名',
    u'margin': u'内手数料金額',
    u'note': u'メモ',
    u'card_brand': u'カードブランド',
    u'card_ahead_com_code': u'仕向け先企業コード',
    u'card_ahead_com_name': u'仕向け先企業名',
    u'issuing_start_at': u'発券開始日時',
    u'issuing_end_at': u'発券期限',
    u'payment_start_at': u'支払開始日時',
    u'payment_due_at': u'支払期限',
    u'created_from_lot_entry_lot_name': u'抽選',
    u'billing_number': u'SEJ払込票番号',
    u'exchange_number': u'SEJ引換票番号',
    u'shipping_name': u'配送先名',
    u'user_last_name': u'姓',
    u'user_first_name': u'名',
    u'user_last_name_kana': u'姓(カナ)',
    u'user_first_name_kana': u'名(カナ)',
    u'user_nick_name': u'ニックネーム',
    u'user_sex': u'性別',
    u'membership_name': u'会員種別名',
    u'membergroup_name': u'会員グループ名',
    u'auth_identifier': u'会員種別ID',
    u'last_name': u'配送先姓',
    u'first_name': u'配送先名',
    u'last_name_kana': u'配送先姓(カナ)',
    u'first_name_kana': u'配送先名(カナ)',
    u'zip': u'郵便番号',
    u'country': u'国',
    u'prefecture': u'都道府県',
    u'city': u'市区町村',
    u'address_1': u'住所1',
    u'address_2': u'住所2',
    u'tel_1': u'電話番号1',
    u'tel_2': u'電話番号2',
    u'fax': u'FAX',
    u'email_1': u'メールアドレス1',
    u'email_2': u'メールアドレス2',
    u'payment_method_name': u'決済方法',
    u'delivery_method_name': u'引取方法',
    u'event_id': u'イベントID',
    u'event_title': u'イベント',
    u'performance_id': u'公演ID',
    u'performance_name': u'公演',
    u'performance_code': u'公演コード',
    u'performance_start_on': u'公演日',
    u'venue_name': u'会場',
    u'product_id': u'商品ID',
    u'product_price': u'商品単価',
    u'product_quantity': u'商品個数',
    u'product_name': u'商品名',
    u'product_sales_segment': u'販売区分',
    u'product_margin_ratio': u'販売手数料率',
    u'product_margin': u'内手数料金額',
    u'product_item_id': u'商品明細ID',
    u'item_name': u'商品明細名',
    u'item_price': u'商品明細単価',
    u'item_quantity': u'商品明細個数',
    u'seat_quantity': u'商品明細個数',
    u'item_print_histories': u'発券作業者',
    u'mail_permission': u'メールマガジン受信可否',
    u'seat_id': u'座席ID',
    u'seat_name': u'座席名',
    }


t_organization = Organization.__table__
t_event = Event.__table__
t_performance = Performance.__table__
t_sales_segment = SalesSegment.__table__
t_product_sales_segment = SalesSegment.__table__.alias()
t_sales_segment_group = SalesSegmentGroup.__table__
t_product_sales_segment_group = SalesSegmentGroup.__table__.alias()
t_order = Order.__table__
t_lot = Lot.__table__
t_lot_entry = LotEntry.__table__
t_pdmp = PaymentDeliveryMethodPair.__table__
t_payment_method = PaymentMethod.__table__
t_delivery_method = DeliveryMethod.__table__
t_shipping_address = ShippingAddress.__table__
t_user = User.__table__
t_user_profile = UserProfile.__table__
t_user_credential = UserCredential.__table__
t_sej_order = SejOrder.__table__
t_seat = Seat.__table__
t_print_hisotry = TicketPrintHistory.__table__
t_ordered_product = OrderedProduct.__table__
t_ordered_product_item = OrderedProductItem.__table__
t_ordered_product_attribute = OrderedProductAttribute.__table__
t_product = Product.__table__
t_product_item = ProductItem.__table__
t_venue = Venue.__table__
t_membership = Membership.__table__
t_member_group = MemberGroup.__table__
t_operator = Operator.__table__
t_mail_subscription = MailSubscription.__table__
t_mail_subscription_1 = t_mail_subscription.alias()
t_mail_subscription_2 = t_mail_subscription.alias()
t_mailmagazine = MailMagazine.__table__


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
    ).label('payment_status_class'),
    case([(t_order.c.delivered_at!=None,
           text("'delivered'")),
          ],
          else_=text("'undelivered'")
    ).label('delivery_status'),
    case([(t_order.c.delivered_at!=None,
           text("'success'")),
          ],
          else_=text("'inverse'")
    ).label('delivery_status_class'),
    case([(t_order.c.delivered_at!=None,
           text(u"'配送済み'")),
          ],
          else_=text(u"'未配送'")
    ).label('delivery_status_label'),
    t_order.c.order_no, #-- 予約番号
    t_order.c.created_at, #-- 予約日時
    t_lot.c.name.label('created_from_lot_entry_lot_name'),
    t_order.c.total_amount, #-- 合計
    (t_shipping_address.c.last_name
     + text("' '")
     + t_shipping_address.c.first_name).label('shipping_name'), #-- 配送先氏名
    t_event.c.id.label('event_id'),
    t_event.c.title.label('event_title'), #-- イベント
    t_performance.c.id.label('performance_id'),
    t_performance.c.start_on.label('performance_start_on'), #-- 開演日時
    text("'' AS card_brand"), # -- カードブランド
    text("'' AS card_ahead_com_code"), #-- 仕向け先コード
    text("'' AS card_ahead_com_name"), #-- 仕向け先名
    t_order.c.fraud_suspect, #-- 不正予約フラグ
    t_payment_method.c.payment_plugin_id,
]

#
t_member_group_names = select([t_member_group.c.membership_id,
                               func.group_concat(t_member_group.c.name).label('names')],
                              whereclause=t_member_group.c.deleted_at==None,
                          ).group_by(t_member_group.c.membership_id).alias()

detail_summary_columns = summary_columns + [
    t_order.c.paid_at, #支払日時
    t_order.c.delivered_at, #配送日時
    t_order.c.canceled_at, #キャンセル日時
    t_order.c.transaction_fee, #決済手数料
    t_order.c.delivery_fee, #配送手数料
    t_order.c.system_fee, #システム利用料
    t_order.c.special_fee, #特別手数料
    #(t_order.c.total_amount * t_sales_segment.c.margin_ratio / 100).label('margin'),
    # t_order.c.margin, #内手数料金額
    t_order.c.note, #メモ
    t_order.c.special_fee_name, #特別手数料名
    t_order.c.issuing_start_at,
    t_order.c.issuing_end_at,
    t_order.c.payment_start_at,
    t_order.c.payment_due_at,
    # SEJOrder
    select([t_sej_order.c.billing_number],
           whereclause=and_(
               t_sej_order.c.deleted_at==None,
               t_sej_order.c.order_no==t_order.c.order_no,
               t_sej_order.c.branch_no==select([func.max(t_sej_order.c.branch_no)],
                                              from_obj=t_sej_order,
                                              whereclause=and_(
                                                  t_sej_order.c.deleted_at==None
                                              )
                                          ).as_scalar(),
           )).label('billing_number'), #SEJ払込票番号
    select([t_sej_order.c.exchange_number],
           whereclause=and_(
               t_sej_order.c.deleted_at==None,
               t_sej_order.c.order_no==t_order.c.order_no,
               t_sej_order.c.branch_no==select([func.max(t_sej_order.c.branch_no)],
                                              from_obj=t_sej_order,
                                              whereclause=and_(
                                                  t_sej_order.c.deleted_at==None
                                              )
                                          ).as_scalar(),
               )).label('exchange_number'),  #SEJ引換票番号
    #UserProfile
    #メールマガジン受信可否
    t_user_profile.c.last_name.label('user_last_name'), #姓
    t_user_profile.c.first_name.label('user_first_name'), #名
    t_user_profile.c.last_name_kana.label('user_last_name_kana'), #姓(カナ)
    t_user_profile.c.first_name_kana.label('user_first_name_kana'), #名(カナ)
    t_user_profile.c.nick_name.label('user_nick_name'), #ニックネーム
    t_user_profile.c.sex.label('user_sex'), #性別

    # Membership
    t_membership.c.name.label('membership_name'), #会員種別名
    t_member_group_names.c.names.label('membergroup_name'), #会員グループ名
    t_user_credential.c.auth_identifier,  #会員種別ID

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

    t_payment_method.c.name.label('payment_method_name'), #決済方法
    t_delivery_method.c.name.label('delivery_method_name'), #引取方法

    # Performance
    t_performance.c.name.label('performance_name'), #公演
    t_performance.c.code.label('performance_code'), #公演コード

    # Venue
    t_venue.c.name.label('venue_name'), #会場

    # Product
    t_product.c.id.label('product_id'), # break key
    t_product.c.name.label('product_name'), #商品名[0]
    t_product.c.price.label('product_price'), #商品単価[0]
    # OrderedProduct
    t_ordered_product.c.quantity.label('product_quantity'), #商品個数[0]
    t_product_sales_segment_group.c.name.label('product_sales_segment'), #販売区分[0]
    t_product_sales_segment.c.margin_ratio.label('product_margin_ratio'), #販売手数料率[0] margin_ratio
    (t_product.c.price * t_ordered_product.c.quantity * t_product_sales_segment.c.margin_ratio / 100).label('product_margin'),
    # ProductItem
    t_product_item.c.id.label('product_item_id'), #商品明細名[0][0]
    t_product_item.c.name.label('item_name'), #商品明細名[0][0]
    t_product_item.c.price.label('item_price'), #商品明細単価[0][0]
    # OrderedProductItem
    t_ordered_product_item.c.quantity.label('item_quantity'), #商品明細個数[0][0]
    t_operator.c.name.label('item_print_histories'), #発券作業者[0][0]
    t_seat.c.id.label('seat_id'),  # 座席ID
    t_seat.c.name.label('seat_name'), #座席名[0][0][0]
    case([(t_seat.c.id!=None,
           text("1")),
          ],
          else_=t_ordered_product_item.c.quantity,
    ).label('seat_quantity'),
    t_ordered_product_attribute.c.name.label('attribute_name'),
    t_ordered_product_attribute.c.value.label('attribute_value'),
    t_mail_subscription_1.c.email.label('mail_subscription_1'),
    t_mail_subscription_2.c.email.label('mail_subscription_2'),
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
).outerjoin(
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
    t_membership,
    and_(t_membership.c.id==t_user_credential.c.membership_id,
         t_membership.c.deleted_at==None),
).outerjoin(
    t_lot_entry,
    and_(t_lot_entry.c.entry_no == t_order.c.order_no,
         t_lot_entry.c.deleted_at == None)
).outerjoin(
    t_lot,
    t_lot_entry.c.lot_id == t_lot.c.id
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
).join(
    t_product_sales_segment,
    and_(t_product_sales_segment.c.id==t_product.c.sales_segment_id,
         t_product_sales_segment.c.deleted_at==None),
).join(
    t_product_sales_segment_group,
    and_(t_product_sales_segment_group.c.id==t_product_sales_segment.c.sales_segment_group_id,
         t_product_sales_segment_group.c.deleted_at==None),
).outerjoin(
    orders_seat_table,
    t_ordered_product_item.c.id==orders_seat_table.c.OrderedProductItem_id,
).outerjoin(
    t_seat,
    and_(t_seat.c.id==orders_seat_table.c.seat_id,
         t_seat.c.deleted_at==None),
).outerjoin(
    t_print_hisotry,
    t_print_hisotry.c.seat_id==t_seat.c.id,
).outerjoin(
    t_operator,
    and_(t_operator.c.id==t_print_hisotry.c.operator_id,
         t_operator.c.deleted_at==None),
).outerjoin(
    t_member_group_names,
    t_member_group_names.c.membership_id==t_membership.c.id,
).outerjoin(
    t_ordered_product_attribute,
    and_(t_ordered_product_attribute.c.ordered_product_item_id==t_ordered_product_item.c.id,
         t_ordered_product_attribute.c.deleted_at==None),
).outerjoin(
    t_mailmagazine,
    t_mailmagazine.c.organization_id==t_organization.c.id
).outerjoin(
    t_mail_subscription_1,
    and_(t_mail_subscription_1.c.email==t_shipping_address.c.email_1,
         t_mail_subscription_1.c.segment_id==t_mailmagazine.c.id,
         t_mail_subscription_1.c.status==MailSubscriptionStatus.Subscribed.v),
).outerjoin(
    t_mail_subscription_2,
    and_(t_mail_subscription_2.c.email==t_shipping_address.c.email_2,
         t_mail_subscription_2.c.segment_id==t_mailmagazine.c.id,
         t_mail_subscription_2.c.status==MailSubscriptionStatus.Subscribed.v),
)


attr_pt = re.compile(r"attribute\[(?P<name>\w+)](\[(?P<i>\d+)\]\[(?P<j>\d+)\])?", re.UNICODE)
def attribute_cols_sort_key(a):
    m = attr_pt.match(a)
    if m is None:
        return None
    d = m.groupdict()
    if d['i'] and d['j']:
        return int(d['i']), int(d['j']), d['name']
    else:
        return d['name']


class SeatSummaryKeyBreakAdapter(object):
    def __init__(self, iter, key1, key2, childitems):
        self.results = []
        last_item = None
        breaked_items = []
        attribute_cols = set()
        margins = {}  # order_no: margin

        break_counter = KeyBreakCounter(keys=[key1, key2, 'product_id'])
        first = True
        for counter, key_changes, item in break_counter(iter):
            if (key_changes[key1] or key_changes[key2]) and not first:
                result = OrderedDict(last_item)
                for c in childitems:
                    result.pop(c)
                for name, value in breaked_items:
                    if name in result:
                        if value not in result[name].split(","):
                            result[name] = unicode(result[name]) + "," + unicode(value)
                    else:
                        result[name] = unicode(value)
                self.results.append(result)
                breaked_items = []
            if key_changes[key2] or key_changes['product_id'] or first:
                margins[item['order_no']] = margins.get(item['order_no'], 0) + item['product_margin']
            if item['attribute_name']:
                name = "attribute[{0}]".format(item['attribute_name'])
                attribute_cols.add(name)
                if item['attribute_value']:
                    breaked_items.append(
                        (name,
                         item['attribute_value']))

            for childitem in childitems:
                name = "{0}".format(childitem)
                if item[childitem]:
                    breaked_items.append(
                        (name,
                         item[childitem]))

            if item['mail_subscription_1'] or item['mail_subscription_2']:
                item['mail_permission'] = '1'
            last_item = item
            first = False

        result = OrderedDict(last_item)
        for c in childitems:
            result.pop(c)

        for name, value in breaked_items:
            if name in result:
                if value not in result[name].split(","):
                    result[name] = unicode(result[name]) + "," + unicode(value)
            else:
                result[name] = unicode(value)

        self.results.append(result)
        for row in self.results:
            row['margin'] = margins.get(row['order_no'], 0)
        headers = list(result)
        self.headers = headers
        self.extra_headers = []
        self.extra_headers += sorted(list(attribute_cols),
                                     key=attribute_cols_sort_key)

    def __iter__(self):
        return iter(self.results)


class OrderSummaryKeyBreakAdapter(object):
    def __init__(self, iter, key, child1, child1_key, child2, child2_key, child3_comma_separated, child3_indexed, child3_key):

        self.results = []
        last_item = None
        breaked_items = []
        child1_count = 0
        child2_count = {}
        child3_count = {}

        break_counter = KeyBreakCounter(keys=[key, child1_key, child2_key, child3_key])
        first = True
        margin = 0
        attribute_cols = set()
        for counter, key_changes, item in break_counter(iter):
            if key_changes[key] and not first:
                result = OrderedDict(last_item)
                for c in child1 + child2 + child3_comma_separated + child3_indexed:
                    result.pop(c)
                for name, value in breaked_items:
                    if name in result:
                        assert isinstance(result[name], basestring), "%s %s %s" % (name, type(result[name]), result)
                        if value not in result[name].split(","):
                            result[name] = unicode(result[name]) + "," + unicode(value)
                    else:
                        result[name] = value
                result['margin'] = margin
                self.results.append(result)
                breaked_items = []
                margin = 0

            # second key break
            if key_changes[key] or key_changes[child1_key] or first:
                for childitem1 in child1:
                    name = "{0}[{1}]".format(childitem1, counter[child1_key])
                    breaked_items.append(
                        (name,
                         item[childitem1]))
                    child1_count = max(child1_count, counter[child1_key])
                # breaked_items['margin'] = breaked_items.get('margin', 0) + item['product_margin']
                margin += item['product_margin']

            # third key break
            if key_changes[key] or key_changes[child1_key] or key_changes[child2_key] or first:
                for childitem2 in child2:
                    name = "{0}[{1}][{2}]".format(childitem2, counter[child1_key], counter[child2_key])
                    breaked_items.append(
                        (name,
                         item[childitem2]))
                    child2_count[counter[child1_key]] = max(child2_count.get(counter[child1_key], 0), counter[child2_key])

            if item['attribute_name']:
                name = "attribute[{0}][{1}][{2}]".format(item['attribute_name'], counter[child1_key], counter[child2_key])
                attribute_cols.add(name)
                if item['attribute_value']:
                    breaked_items.append(
                        (name,
                         item['attribute_value']))

            for childitem3 in child3_comma_separated:
                name = "{0}[{1}][{2}]".format(childitem3, counter[child1_key], counter[child2_key])
                if item[childitem3]:
                    breaked_items.append(
                        (name,
                         item[childitem3]))
            for childitem3 in child3_indexed:
                name = "{0}[{1}][{2}][{3}]".format(childitem3, counter[child1_key], counter[child2_key], counter[child3_key])
                if item[childitem3]:
                    breaked_items.append(
                        (name,
                         item[childitem3]))
                    child3_count[(counter[child1_key], counter[child2_key])] = max(child3_count.get((counter[child1_key], counter[child2_key]), 0), counter[child3_key])

            if item['mail_subscription_1'] or item['mail_subscription_2']:
                item['mail_permission'] = '1'
            last_item = item
            first = False

        result = OrderedDict(last_item)
        for c in child1 + child2 + child3_comma_separated + child3_indexed:
            result.pop(c)

        for name, value in breaked_items:
            if name in result:
                assert isinstance(result[name], basestring), result
                if value not in result[name].split(","):
                    result[name] = unicode(result[name]) + "," + unicode(value)
            else:
                result[name] = value
        result['margin'] = margin
        self.results.append(result)

        headers = list(result)
        self.headers = headers
        self.extra_headers = []
        for i in range(child1_count + 1):
            for n in child1:
                self.extra_headers.append("{0}[{1}]".format(n, i))
            for j in range(child2_count.get(i, -1) + 1):
                for n in child2:
                    self.extra_headers.append("{0}[{1}][{2}]".format(n, i, j))
                for n in child3_comma_separated:
                    self.extra_headers.append("{0}[{1}][{2}]".format(n, i, j))
                for k in range(child3_count.get((i, j), -1) + 1):
                    for n in child3_indexed:
                        self.extra_headers.append("{0}[{1}][{2}][{3}]".format(n, i, j, k))
        self.extra_headers += sorted(list(attribute_cols),
                                     key=attribute_cols_sort_key)

    def __iter__(self):
        return iter(self.results)

def header_intl(headers, col_names, ordered_product_metadata_provider_registry):
    for h in headers:
        if h.find('[') > -1:
            h, tail = h.split('[', 1)
            tail = "[" + tail
        else:
            tail = ""

        if h == "attribute":
            key, tail = tail.lstrip("[").split("]", 1)
            for provider in ordered_product_metadata_provider_registry.getProviders():
                if key in provider:
                    yield provider[key].get_display_name('ja_JP') + tail
                    break
            else:
                yield h + "[" + key + "]" + tail
        else:
            yield col_names.get(h, h) + tail


class OrderLikeWrapper(object):
    def __init__(self, organization, order_no, payment_plugin_id):
        self.organization = organization
        self.order_no = order_no
        self.payment_plugin_id = payment_plugin_id

    @property
    def payment_delivery_pair(self):
        return SummarizedPaymentDeliveryMethodPair(
            SummarizedPaymentMethod(self.payment_plugin_id, None),
            None
            )

class OrderSearchBase(list):

    def __init__(self, request, db_session, organization_id, condition):
        self.request = request
        self.db_session = db_session
        self.organization_id = organization_id
        self.organization = db_session.query(Organization).filter_by(id=organization_id).one()
        self._cond = condition
        self.condition = self.query_cond(condition)
        self.target_order_ids = []

    def order_by(self, query):
        if self._cond is None:
            return query.order_by(self.default_order)

        logger.debug('order_by {0}'.format(self._cond))
        if 'sort' in self._cond:
            sort_col = None
            if self._cond['sort'].data == 'created_at':
                sort_col = t_order.c.created_at
            elif self._cond['sort'].data == 'order_no':
                sort_col = t_order.c.order_no
            else:
                return query.order_by(self.default_order)
            logger.debug('order_by {0}'.format(sort_col))

            if 'direction' in self._cond:
                if self._cond['direction'].data == 'asc':
                    return query.order_by(sort_col.asc())
                elif self._cond['direction'].data == 'desc':
                    return query.order_by(sort_col.desc())
                else:
                    return query.order_by(self.default_order)
            else:
                return query.order_by(sort_col)
        return query.order_by(self.default_order)

    def query_cond(self, condition):
        """検索条件

        キーワード引数：
        condition -- 初期化した検索条件
        """
        cond = and_(t_organization.c.id==self.organization_id,
                    t_ordered_product.c.id==t_order.c.id,
                    t_order.c.deleted_at==None)

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
            subq = select([t_ordered_product.c.order_id],
                          from_obj=orders_seat_table.join(
                              t_seat,
                              and_(t_seat.c.id==orders_seat_table.c.seat_id,
                                   t_seat.c.deleted_at==None),
                          ).join(
                              t_ordered_product_item,
                              and_(t_ordered_product_item.c.id==orders_seat_table.c.OrderedProductItem_id,
                                   t_ordered_product_item.c.deleted_at==None),
                          ).join(
                              t_ordered_product,
                              and_(t_ordered_product.c.id==t_ordered_product_item.c.ordered_product_id,
                                   t_ordered_product.c.deleted_at==None),
                          ),
                          whereclause=t_seat.c.name.like('%s%%' % value))
            cond = and_(cond,
                        t_order.c.id.in_(subq))

        # 電話番号 tel:
        if condition.tel.data:
            value = condition.tel.data
            cond = and_(cond,
                        or_(t_shipping_address.c.tel_1==value,
                            t_shipping_address.c.tel_2==value))

        # 氏名 name:
        if condition.name.data:
            value = condition.name.data
            items = re.split(ur'[ \t　]+', value)
            for item in items:
                cond = and_(cond,
                    or_(
                        or_(t_shipping_address.c.first_name.like('%s%%' % item),
                            t_shipping_address.c.last_name.like('%s%%' % item)),
                        or_(t_shipping_address.c.first_name_kana.like('%s%%' % item),
                            t_shipping_address.c.last_name_kana.like('%s%%' % item))
                        )
                    )

        # メールアドレス email:
        if condition.email.data:
            value = condition.email.data
            cond = and_(cond,
                        or_(t_shipping_address.c.email_1==value,
                            t_shipping_address.c.email_2==value,
                        ))

        # ログインID login_id:
        if condition.login_id.data:
            value = condition.login_id.data
            cond = and_(cond,
                        t_user_credential.c.auth_identifier == value)

        # 会員番号 member_id
        if condition.member_id.data:
            value = condition.member_id.data
            cond = and_(cond,
                        t_user_credential.c.authz_identifier == value)

        # 予約日時(開始)
        if condition.ordered_from.data:
            value = condition.ordered_from.data
            cond = and_(cond,
                        t_order.c.created_at>=value)

        # 予約日時(終了)
        if condition.ordered_to.data:
            value = condition.ordered_to.data
            cond = and_(cond,
                        t_order.c.created_at<=value)

        # FM予約番号
        fm_reserve_number = condition.fm_reserve_number.data
        if fm_reserve_number:
            try:
                famiport_order = famiport_api.get_famiport_order_by_reserve_number(self.request, fm_reserve_number)
                cond = and_(cond, t_order.c.order_no==famiport_order['order_no'])
            except FamiPortAPINotFoundError:
                cond = and_(cond, Order.__table__.c.id==None) # No resullt

        # セブン−イレブン払込票/引換票番号
        if condition.billing_or_exchange_number.data:
            value = condition.billing_or_exchange_number.data
            cond = and_(cond,
                        t_order.c.order_no.in_(
                            select([t_sej_order.c.order_no],
                                   whereclause=and_(
                                       t_sej_order.c.deleted_at==None,
                                       or_(
                                           t_sej_order.c.exchange_number==value,
                                           t_sej_order.c.billing_number==value))
                               ).as_scalar()
                        ))

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
            if isinstance(value, list):
                cond = and_(cond,
                            or_(*[t_sales_segment_group.c.id==v for v in value]))
            else:
                cond = and_(cond,
                            t_sales_segment_group.c.id==value)

        # 決済方法 payment_method
        if condition.payment_method.data:
            value = condition.payment_method.data
            if isinstance(value, list):
                cond = and_(cond,
                            or_(*[t_payment_method.c.id==v for v in value]))
            else:
                cond = and_(cond,
                            t_payment_method.c.id==value)

        # 引取方法 delivery_method
        if condition.delivery_method.data:
            value = condition.delivery_method.data
            if isinstance(value, list):
                cond = and_(cond,
                            or_(*[t_delivery_method.c.id==v for v in value]))
            else:
                cond = and_(cond,
                            t_delivery_method.c.id==value)

        # 公演日時
        if condition.start_on_from.data:
            value = condition.start_on_from.data
            cond = and_(cond,
                        t_performance.c.start_on>=value)

        if condition.start_on_to.data:
            value = condition.start_on_to.data
            cond = and_(cond,
                        t_performance.c.start_on<=value)

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
                    func.sum(t_ordered_product_item.c.quantity) == value
                )

                cond = and_(cond,
                            t_order.c.id.in_(subq))

        return cond

    def __iter__(self):
        start = 0
        #stop = self.count()

        #return self.execute(start, stop)
        return self.execute(start)


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

    def count_and_total(self):
        sql = select([func.count(t_order.c.id), func.sum(t_order.c.total_amount)],
                     from_obj=[self.target],
                     whereclause=self.condition,
        )

        logger.debug("sql = {0}".format(sql))
        cur = self.db_session.bind.execute(sql)
        try:
            r = cur.fetchone()
            return r
        finally:
            cur.close()

    def total_quantity(self):
        """すべての予約枚数を返す"""
        sql = select([func.sum(t_ordered_product.c.quantity)],
                     from_obj=[self.target],
                     whereclause=self.condition,
        )

        logger.debug("sql = {0}".format(sql))
        cur = self.db_session.bind.execute(sql)
        try:
            r = cur.fetchone()
            return r
        finally:
            cur.close()

    def __getslice__(self, start, stop):
        return self.execute(start, stop)

    def retouch(self, item):
        from api import get_multicheckout_info
        olw = OrderLikeWrapper(self.organization, item['order_no'], item.pop('payment_plugin_id'))
        multicheckout_info = get_multicheckout_info(self.request, olw)
        if multicheckout_info is not None:
            item['card_ahead_com_name'] = multicheckout_info['ahead_com_name']
            item['card_ahead_com_code'] = multicheckout_info['ahead_com_cd']
            item['card_brand'] = multicheckout_info['card_brand']
        return item

    def execute(self, start, stop=None):
        #logger.debug("start = {0}, stop = {1}".format(start, stop))
        limit_span = 1000
        limit = limit_span
        if stop:
            limit = min(limit_span, stop-start)
        offset = start
        while True:
            sql = select(self.columns,
                         from_obj=[self.target],
                         whereclause=self.condition,
            ).limit(limit
            ).offset(offset)
            sql = self.order_by(sql)
            if self.target_order_ids:
                sql = sql.where(Order.id.in_(self.target_order_ids))

            logger.debug("limit = {0}, offset = {1}".format(limit, offset))
            logger.debug("sql = {0}".format(sql))
            cur = self.db_session.bind.execute(sql)
            try:
                rows = cur.fetchall()
                logger.debug('fetchall')
                if not rows:
                    break

                for row in rows:
                    item = OrderedDict(row.items())
                    item = self.retouch(item)
                    yield item
                offset = offset + limit_span
                if stop:
                    if offset > stop:
                        break
                    limit = min(limit_span, stop - offset)
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

    def init_mailsub_joins(self):
        self.columns = OrderDownload.columns + [
            case([(func.exists(select([t_mail_subscription.c.id],
                                      whereclause=t_mail_subscription.c.user_id==t_user.c.id).as_scalar()), '1'),
                  ],
                 else_='0'
            ).label('mail_permission'),
            ]

class OrderSummary(OrderSearchBase):
    target = order_summary_joins
    columns = summary_columns
    default_order = t_order.c.id.desc()


class OrderDownload(OrderSearchBase):
    target = order_product_summary_joins
    columns = detail_summary_columns
    default_order = [t_order.c.order_no.asc(),
                     t_order.c.created_at.asc(),
                     t_ordered_product.c.id,
                     t_ordered_product_item.c.id,
                     t_seat.c.id]

    def order_by(self, query):
        return query.order_by(*self.default_order)

class OrderSeatDownload(OrderSearchBase):
    target = order_product_summary_joins
    columns = detail_summary_columns
    default_order = [t_seat.c.id]

    def order_by(self, query):
        return query.order_by(*self.default_order)

class MailPermissionCache(OrderSearchBase):
    target = t_mail_subscription.join(
        t_mailmagazine,
        t_mailmagazine.c.id==t_mail_subscription.c.segment_id
        )
    columns = [t_mail_subscription.c.email]
    default_order = []

    def order_by(self, query):
        return query

    def query_cond(self, condition):
        return and_(t_mailmagazine.c.organization_id==self.organization_id,
                    t_mail_subscription.c.status==MailSubscriptionStatus.Subscribed.v)

