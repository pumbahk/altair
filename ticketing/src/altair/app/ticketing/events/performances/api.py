# coding:utf-8
from datetime import datetime
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import Event, Performance
from altair.app.ticketing.orders.models import OrderImportTask, ImportStatusEnum
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing.payments.plugins import FAMIPORT_DELIVERY_PLUGIN_ID
from altair.app.ticketing.orders.orion import make_send_to_orion_request
from altair.app.ticketing.resale.models import ResaleRequestStatus
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

    obj = dict(
        organization_code=performance.event.organization.code,
        event_code=performance.event.code,
        event_name=performance.event.title,
        code=performance.code,
        name=performance.name,
        url='',
        open_on=performance.open_on.strftime('%Y-%m-%d %H:%M:%S') if performance.open_on is not None else None,
        start_on=performance.start_on.strftime('%Y-%m-%d %H:%M:%S') if performance.start_on is not None else None,
        end_on=performance.end_on.strftime('%Y-%m-%d %H:%M:%S') if performance.end_on is not None else None,
        search_end_at='',
        site_name=performance.venue.site.name,
        resale_segment_id=resale_segment.id,
        reception_start_at = resale_segment.start_at.strftime('%Y-%m-%d %H:%M:%S') if resale_segment.start_at else None,
        reception_end_at = resale_segment.end_at.strftime('%Y-%m-%d %H:%M:%S') if resale_segment.end_at else None,
        resale_start_at=resale_segment.resale_start_at.strftime('%Y-%m-%d %H:%M:%S') if resale_segment.resale_start_at else None,
        resale_end_at=resale_segment.resale_end_at.strftime('%Y-%m-%d %H:%M:%S') if resale_segment.resale_end_at else None,
        resale_enable=1
    )

    return make_send_to_orion_request(request, obj, 'orion.resale_segment.create_or_update_url')

def _get_verbose_status(status):
    if status == ResaleRequestStatus.sold:
        verbose_status = u'sold'
    elif status == ResaleRequestStatus.back:
        verbose_status = u'not_sold'
    else:
        verbose_status = u'pending'
    return verbose_status

def send_resale_request(request, resale_request):
    obj = dict(
        id=resale_request.id,
        status=_get_verbose_status(resale_request.status),
        sold_at=resale_request.sold_at.strftime('%Y-%m-%d %H:%M:%S') if resale_request.sold_at else None
    )
    return make_send_to_orion_request(request, obj, 'orion.resale_request.feedback_url')

def send_all_resale_request(request, resale_requests):
    objs = [
        {
            'id': resale_request.id,
            'status': _get_verbose_status(resale_request.status),
            'sold_at': resale_request.sold_at.strftime('%Y-%m-%d %H:%M:%S') if resale_request.sold_at else None
        } for resale_request in resale_requests
    ]
    return make_send_to_orion_request(request, objs, 'orion.resale_request.feedback_all_url')


def get_progressing_order_import_task(request, obj):
    """
    イベント、またはパフォーマンスに紐づく進行中の予約インポートタスクを取得。
    :param request: リクエストオブジェクト
    :param obj: Event or Performance
    :return: 予約インポートタスク
    """
    slave_session = get_db_session(request, name="slave")
    query = slave_session.query(
        Performance.id.label('perf_id'),
        Performance.name.label('perf_name'),
        OrderImportTask.created_at.label('task_created_at')
    ).join(
        OrderImportTask
    ).filter(
        OrderImportTask.status.in_([
            ImportStatusEnum.Waiting.v,
            ImportStatusEnum.Importing.v
        ])
    )

    if isinstance(obj, Event):
        query = query.join(Event).filter(Event.id == obj.id)
    elif isinstance(obj, Performance):
        query = query.filter(Performance.id == obj.id)
    else:
        raise Exception('must be a instance of Event or Performance. but "obj" is {}'.format(type(obj)))

    order_import_tasks = query.all()
    return order_import_tasks
