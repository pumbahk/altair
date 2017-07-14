# -*- coding: utf-8 -*-
import csv
from datetime import datetime

from altair.app.ticketing.qr.utils import build_qr_by_order, build_qr_by_token
from altair.app.ticketing.carturl.api import get_orderreview_qr_url_builder
from altair.app.ticketing.core.models import Organization
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.orders.models import OrderedProductItem
from altair.app.ticketing.orders.models import OrderedProduct
from altair.app.ticketing.payments import plugins as payments_plugins


def encode_to_cp932(data):
    if not hasattr(data, "encode"):
        return str(data)
    try:
        return data.replace('\r\n', '').encode('cp932')
    except UnicodeEncodeError:
        print 'cannot encode character %s to cp932' % data
        if data is not None and len(data) > 1:
            return ''.join([encode_to_cp932(d) for d in data])
        else:
            return '?'

def build_ticket(order, url, prt_dt=None):
    return [order.order_no,
            u'{last_name}　{first_name}（{last_name_kana}　{first_name_kana}）'.format(
                last_name=order.shipping_address.last_name ,
                first_name=order.shipping_address.first_name,
                last_name_kana = order.shipping_address.last_name_kana,
                first_name_kana = order.shipping_address.first_name_kana
            ),
            url, prt_dt]

def main(request, org_code=None, performance_id=None, from_date=None, prt_flg=None):
    organization = Organization.query.filter_by(code=org_code).one()
    request.context.organization = organization
    orders = Order.query.filter(Order.shipping_address_id.isnot(None))
    if performance_id:
        orders = orders.filter(Order.performance_id==performance_id)
    if from_date:
        orders = orders.filter(Order.created_at>=from_date)
    orders = orders.all()
    tickets = []
    url_builder = get_orderreview_qr_url_builder(request)

    for order in orders:
        qr_preferences = order.payment_delivery_pair.delivery_method.preferences.get(unicode(payments_plugins.QR_DELIVERY_PLUGIN_ID), {})
        if prt_flg:
            ordered_product = OrderedProduct.query.filter_by(order_id=order.id).one()
            order_pro_item = OrderedProductItem.query.filter_by(ordered_product_id=ordered_product.id).one()
        single_qr_mode = qr_preferences.get('single_qr_mode', False)

        if single_qr_mode:
            qr = build_qr_by_order(request, order)
            if prt_flg:
                ticket = build_ticket(order, url_builder.build(request, qr.id, qr.sign), order_pro_item.printed_at)
            else:
                ticket = build_ticket(order, url_builder.build(request, qr.id, qr.sign))
            tickets.append(ticket)
        else:
            tokens = [token for item in order.items for element in item.elements for token in element.tokens]

            for token in tokens:
                qr = build_qr_by_token(request, order.order_no, token)
                if prt_flg:
                    ticket = build_ticket(order, url_builder.build(request, qr.id, qr.sign), order_pro_item.printed_at)
                else:
                    ticket = build_ticket(order, url_builder.build(request, qr.id, qr.sign))
                tickets.append(ticket)

    filename = u'qrcode_list_{org}_{time}.csv'.format(org=request.context.organization.code, time=datetime.now().strftime('%Y%m%d%H%M%S'))

    if prt_flg:
        header = [u'予約番号', u"氏名", u"QRコード", u"印刷日付"]
    else:
        header = [u'予約番号', u"氏名", u"QRコード"]

    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
        # write header
        writer.writerow(map(encode_to_cp932, header))
        # write url information
        for ticket in tickets:
            writer.writerow(map(encode_to_cp932, ticket))