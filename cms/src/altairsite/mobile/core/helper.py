# -*- coding: utf-8 -*-
import webhelpers.paginate as paginate
from altaircms.helpers.link import get_purchase_page_from_performance
from altaircms.models import SalesSegmentGroup, SalesSegment, SalesSegmentKind
from altaircms.event.models import Event
from altaircms.models import Ticket
from altairsite.smartphone.common.helper import SmartPhoneHelper
from .eventhelper import log_debug, log_info, log_warn, log_exception, log_error
from markupsafe import Markup

# umm..
def exist_value(value):

    if value is None:
        return False

    if value == "":
        return False

    if value == "0":
        return False

    if value == 0:
        return False

    return True

def get_week_map():
    return {0:u'月',1:u'火',2:u'水',3:u'木',4:u'金',5:u'土',6:u'日'}

def get_event_paging(request, form, qs):
    log_info("get_event_paging", "start")
    form.events.data = None
    form.num.data = 0
    if form.page.data == None or form.page.data == "":
        form.page.data = "1"

    if qs:
        events = qs.all()
        log_info("get_event_paging", "data exist")
        sp_helper = SmartPhoneHelper()

        if events:
            form.num.data = len(events)
            items_per_page = 10
            form.events.data = paginate.Page(
                events,
                form.page.data,
                items_per_page,
                url=paginate.PageURL_WebOb(request)
            )
            if form.num.data % items_per_page == 0:
                form.page_num.data = form.num.data / items_per_page
            else:
                form.page_num.data = form.num.data / items_per_page + 1

            deal_open = []
            deal_close = []
            for count, event in enumerate(form.events.data):
                deal_open.append(sp_helper.disp_salessegment_start_on_date_week(event))
                deal_close.append(sp_helper.disp_salessegment_end_on_date_week(event))
            form.deal_open.data = deal_open
            form.deal_close.data = deal_close

    log_info("get_event_paging", "end")
    return form

def get_performances_month_unit(event):
    log_info("get_performances_month_unit", "start")
    keys = []
    month_unit = {} # performances
    perfs = []

    for perf in event.performances:
        if perf.public:
            perfs.append(perf)

    for perf in perfs:
        key =  str(perf.start_on.year) + "/" + str(perf.start_on.month).zfill(2)

        # 新規の月
        if not key in keys:
            keys.append(key)
            month_unit.update({key:[]})

        # 対象の月に追加
        month_unit[key].append(perf)

    log_info("get_performances_month_unit", "key num=" + str(len(month_unit)))

    log_info("get_performances_month_unit", "end")
    return month_unit

def get_purchase_links(request, event):
    log_info("get_purchase_links", "start")
    links = {}
    for perf in event.performances:
        link = get_purchase_page_from_performance(request=request, performance=perf)
        links.update({perf.id:link})
    log_info("get_purchase_links", "end")
    return links

def get_tickets(request, event):
    log_info("get_tickets", "start")
    tickets = request.allowable(Ticket).join(SalesSegment, SalesSegment.id == Ticket.sale_id) \
                .join(SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.group_id) \
                .filter(SalesSegmentGroup.event_id == event.id) \
                .order_by(Ticket.display_order).all()

    log_info("get_tickets", "key num=" + str(len(tickets)))

    log_info("get_tickets", "end")
    return tickets

def get_sales_date(request, event):

    qs = request.allowable(SalesSegmentGroup)\
        .join(SalesSegmentKind, SalesSegmentKind.id == SalesSegmentGroup.id)\
        .filter(SalesSegmentGroup.event_id == event.id)\
        .filter(SalesSegmentKind.publicp == True).all()

    sales_start = None
    sales_end = None
    for segment in qs:
        # 初回
        if sales_start is None:
            sales_start = segment.start_on
        if sales_end is None:
            sales_end = segment.end_on

        # start
        if sales_start > segment.start_on:
            sales_start = segment.start_on

        # end
        if sales_end < segment.end_on:
            sales_end = segment.end_on

    return sales_start, sales_end
