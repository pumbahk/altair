# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altaircms.event.models import Event
from altaircms.topic.models import Promotion, Topic
from cmsmobile.event.eventdetail.forms import EventDetailForm
from cmsmobile.core.helper import get_week_map, get_performances_month_unit, get_purchase_links\
    , get_tickets, exist_value, get_sales_date
from cmsmobile.core.helper import log_info
from altaircms.page.models import PageSet

class ValidationFailure(Exception):
    pass

@view_config(route_name='eventdetail', renderer='cmsmobile:templates/eventdetail/eventdetail.mako')
def move_eventdetail(request):

    log_info("move_eventdetail", "start")
    form = EventDetailForm(request.GET)
    form.week.data = get_week_map()
    form.event.data = request.allowable(Event).filter(Event.id == form.event_id.data).first()

    if not exist_value(form.event.data): # 検索結果からの遷移

        if exist_value(form.promotion_id.data): # ピックアップからの遷移
            log_info("move_eventdetail", "from pickup")
            form.event.data = _get_event_from_promotion(request, form.promotion_id.data)
        elif exist_value(form.attention_id.data): # 注目のイベントからの遷移
            log_info("move_eventdetail", "from attention")
            form.event.data = _get_event_from_topic(request, form.attention_id.data)
        elif exist_value(form.topic_id.data): # トピックスからの遷移
            log_info("move_eventdetail", "from topic")
            form.event.data = _get_event_from_topic(request, form.topic_id.data)

    if not exist_value(form.event.data):
        log_info("move_eventdetail", "event not found")
        raise ValidationFailure

    log_info("move_eventdetail", "detail infomation get start")
    form.purchase_links.data = get_purchase_links(request=request, event=form.event.data)
    form.month_unit.data = get_performances_month_unit(event=form.event.data)
    keys = form.month_unit.data.keys()
    keys.sort()
    form.month_unit_keys.data = keys
    form.tickets.data = get_tickets(form.event.data)
    form.sales_start.data, form.sales_end.data = get_sales_date(request=request, event=form.event.data)
    log_info("move_eventdetail", "detail infomation get end")

    log_info("move_eventdetail", "end")
    return {'form':form}

@view_config(route_name='eventdetail', context=ValidationFailure, renderer='cmsmobile:templates/common/error.mako')
def failed_validation(request):
    return {}

def _get_event_from_promotion(request, id):
    log_info("_get_event_from_promotion", "start")
    promotion = request.allowable(Promotion).filter(Promotion.id == id).first()

    if not promotion:
        log_info("_get_event_from_promotion", "promotion not found")
        return None

    event = request.allowable(Event) \
        .filter(Event.is_searchable == True) \
        .join(PageSet, Event.id == PageSet.event_id) \
        .filter(PageSet.id == promotion.linked_page_id).first()

    log_info("_get_event_from_promotion", "end")
    return event

def _get_event_from_topic(request, id):
    log_info("_get_event_from_topic", "start")
    topic = request.allowable(Topic).filter(Topic.id == id).first()

    if not topic:
        log_info("_get_event_from_topic", "topic not found")
        return None

    event = request.allowable(Event) \
        .filter(Event.is_searchable == True) \
        .join(PageSet, Event.id == PageSet.event_id) \
        .filter(PageSet.id == topic.linked_page_id).first()

    log_info("_get_event_from_topic", "end")
    return event