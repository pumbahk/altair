# -*- coding: utf-8 -*-
import webhelpers.paginate as paginate
import logging
from altaircms.helpers.link import get_purchase_page_from_performance

logger = logging.getLogger(__file__)

def log_debug(key, msg):
    logger.debug("*" + key + "* : " + msg)

def log_info(key, msg):
    logger.info("*" + key + "* : " + msg)

def log_warn(key, msg):
    logger.warning("*" + key + "* : " + msg)

def log_exception(key, msg):
    logger.exception("*" + key + "* : " + msg)

def log_error(key, msg):
    logger.error("*" + key + "* : " + msg)

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

    log_info("get_event_paging", "end")
    return form

def get_performances_month_unit(event):
    log_info("get_performances_month_unit", "start")
    keys = []
    month_unit = {} # performances
    for perf in event.performances:
        key =  str(perf.start_on.year) + "/" + str(perf.start_on.month)

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

def get_tickets(event):
    log_info("get_tickets", "start")
    tickets = {}
    for group in event.salessegment_groups:
        for segment in group.salessegments:
            for ticket in segment.tickets:
                tickets.update({ticket.name:ticket.price})

    log_info("get_tickets", "key num=" + str(len(tickets)))

    log_info("get_tickets", "end")
    return tickets