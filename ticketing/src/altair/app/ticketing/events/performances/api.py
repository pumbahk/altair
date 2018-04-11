# coding:utf-8
from datetime import datetime
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
from altair.app.ticketing.orders.orion import make_send_to_orion_request

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

def send_resale_segment(request, performance, resale_segment):
    obj = dict()
    obj['performance'] = dict(
        id=performance.id,
        code=performance.code,
        name=performance.name,
        open_on=str(performance.open_on) if performance.open_on is not None else None,
        start_on=str(performance.start_on) if performance.start_on is not None else None,
        end_on=str(performance.end_on) if performance.end_on is not None else None
    )
    obj['resale_segment'] = dict(
        performance_id=resale_segment.performance_id,
        start_at=str(resale_segment.start_at),
        end_at=str(resale_segment.end_at)
    )
    return make_send_to_orion_request(request, obj, 'orion.resale_segment.create_or_update_url')

def send_resale_request(request, resale_request):
    obj = dict()
    obj['resale_request'] = dict(
        id=resale_request.id,
        ResaleRequestStatus=resale_request.status,
        sold_at=resale_request.sold_at
    )
    return make_send_to_orion_request(request, obj, 'orion.resale_request.feedback_url')

def send_resale_request_all(request, resale_requests):
    objs = [
        {
            'id': resale_request.id,
            'ResaleRequestStatus': resale_request.status,
            'sold_at': resale_request.sold_at
        } for resale_request in resale_requests
    ]
    return make_send_to_orion_request(request, objs, 'orion.resale_request.feedback_all_url')