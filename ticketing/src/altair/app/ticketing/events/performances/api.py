# coding:utf-8
from datetime import datetime
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID

from . import VISIBLE_PERFORMANCE_SESSION_KEY


def set_visible_performance(request):
    request.session[VISIBLE_PERFORMANCE_SESSION_KEY] = str(datetime.now())


def set_invisible_performance(request):
    if VISIBLE_PERFORMANCE_SESSION_KEY in request.session:
        del request.session[VISIBLE_PERFORMANCE_SESSION_KEY]


def get_no_ticket_bundles(performance):
    no_ticket_bundles = ''
    for sales_segment in performance.sales_segments:
        has_sej_delivery = sales_segment.has_that_delivery(SEJ_DELIVERY_PLUGIN_ID)
        has_famiport_delivery = sales_segment.has_that_delivery(FAMIPORT_DELIVERY_PLUGIN_ID)
        for product in sales_segment.products:
            for product_item in product.items:
                if not product_item.ticket_bundle:
                    p = product_item.product
                    if p.sales_segment is not None:
                        no_ticket_bundles += u'<div>販売区分: {}、商品名: {}</div>'.format(
                            p.sales_segment.name, p.name)
                if has_sej_delivery:
                    producer = ApplicableTicketsProducer.from_bundle(
                        product_item.ticket_bundle)
                    if not producer.any_exist(producer.sej_only_tickets()):
                        p = product_item.product
                        if p.sales_segment is not None:
                            no_ticket_bundles += u'<div>販売区分: {}、商品名: {}(SEJ券面なし)</div>'.format(
                                p.sales_segment.name, p.name)
                if has_famiport_delivery:
                    producer = ApplicableTicketsProducer.from_bundle(
                        product_item.ticket_bundle)
                    if not producer.any_exist(producer.famiport_only_tickets()):
                        p = product_item.product
                        if p.sales_segment is not None:
                            no_ticket_bundles += u'<div>販売区分: {}、商品名: {}(ファミマ券面なし)</div>'.format(
                                p.sales_segment.name, p.name)

    return no_ticket_bundles
