# -*- coding:utf-8 -*-

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import logging
logger = logging.getLogger(__name__)

def on_order_canceled(event):
    message = create_cancel_message(event.order)
    mailer = get_mailer(event.request)
    mailer.send(message)
    logger.info("send cancel mail to %s" % message.recipients)

def create_cancel_message(order):
    product_message_format = u'{ordered_product.product.name}　' \
                           + u'{ordered_product.price:n}（円）× ' \
                           + u'{ordered_product.quantity:n}（個）\r\n'
    product_detail = ''
    for ordered_product in order.ordered_products:
        product_detail += product_message_format.format(ordered_product=ordered_product)

    message = Message(
        subject=u'ご注文キャンセルについて',
        recipients=[order.shipping_address.email],
        body=u'''
{user_profile.last_name} {user_profile.first_name} 様

「{order.ordered_products[0].product.event.title}」のご注文キャンセル手続きが
完了しましたのでご連絡させていただきます。

このキャンセル処理は、下記のような理由によりおこなっております。

(キャンセル理由の例)
　・お客様からキャンセルのご連絡があったため
　・期限内のご入金がなくキャンセル扱いとしたため
　・二重注文により、ひとつをキャンセル処理したため

ご不明な点がございましたら、{order.ordered_from.name}までお問い合わせください。

=====================================================================
■ 販売会社： {order.ordered_from.name}
■ メールアドレス: support@ticketstar.jp
=====================================================================
[受付番号]  {order.order_no}
[受付日時]  {order.created_at}
[注文者]    {user_profile.last_name} {user_profile.first_name} 様
[支払方法]  {order.payment_delivery_pair.payment_method.name}
[配送方法]  {order.payment_delivery_pair.delivery_method.name}
==========
[送付先]    {shipping_address.last_name} {shipping_address.first_name} 様
            〒 {shipping_address.zip}
            {shipping_address.prefecture} {shipping_address.city}
            {shipping_address.address_1} {shipping_address.address_2}
            (TEL) {shipping_address.tel_1}
[商品]
{order.ordered_products[0].product.event.title}
{order.ordered_products[0].ordered_product_items[0].product_item.performance.venue.name} ({order.ordered_products[0].ordered_product_items[0].product_item.performance.start_on}開演)
{product_detail}
システム利用料 {order.system_fee:n}（円）
決済手数料　　 {order.transaction_fee:n}（円）
配送手数料　　 {order.delivery_fee:n}（円）
********************************************************************
合計　　　　　 {order.total_amount:n}（円）

─────────────問い合わせ─────────────────
商品、決済・発送に関するお問い合わせ support@ticketstar.jp
楽天チケット http://ticket.rakuten.co.jp/
───────────────────────────────────
'''.format(order=order, user=order.user, user_profile=order.user.user_profile, shipping_address=order.shipping_address, product_detail=product_detail),
        sender='support@ticketstar.jp',
    )
    return message
