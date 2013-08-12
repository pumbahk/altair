# -*- coding: utf-8 -*-
from altaircms.event.models import Event
from altaircms.event.event_info import get_event_notify_info
from altaircms.plugins.extra.stockstatus import StockStatus
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.eventdetail.forms import EventDetailForm
from altairsite.mobile.core.helper import get_week_map, get_performances_month_unit, get_purchase_links\
    , get_tickets, exist_value, get_sales_date
from altairsite.mobile.core.helper import log_info, Markup
from altairsite.mobile.core.disphelper import DispHelper
from altairsite.exceptions import UsersiteException
from altairsite.smartphone.common.utils import get_stockstatus_from_event


class ValidationFailure(UsersiteException):
    pass

@mobile_site_view_config(route_name='eventdetail', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/eventdetail/eventdetail.mako')
def move_eventdetail(request):

    log_info("move_eventdetail", "start")
    form = EventDetailForm(request.GET)
    form.week.data = get_week_map()
    form.event.data = request.allowable(Event).filter(Event.id == form.event_id.data).first()

    if not exist_value(form.event.data):
        log_info("move_eventdetail", "event not found")
        raise ValidationFailure

    log_info("move_eventdetail", "detail infomation get start")
    form.purchase_links.data = get_purchase_links(request=request, event=form.event.data)
    form.month_unit.data = get_performances_month_unit(event=form.event.data)
    keys = form.month_unit.data.keys()
    keys.sort()
    form.month_unit_keys.data = keys
    form.tickets.data = get_tickets(request=request, event=form.event.data)
    form.sales_start.data, form.sales_end.data = get_sales_date(request=request, event=form.event.data)
    log_info("move_eventdetail", "detail infomation get end")
    event_info = get_event_notify_info(event=form.event.data)
    stock_status = get_stockstatus_from_event(request=request, event=form.event.data, status_impl=StockStatus)

    log_info("move_eventdetail", "end")
    return {
          'form':form
        , 'event_info':event_info
        , 'stock_status':stock_status
        , 'helper':DispHelper()
    }

@mobile_site_view_config(route_name='eventdetail', context=ValidationFailure
    , request_type="altairsite.tweens.IMobileRequest", renderer='altairsite.mobile:templates/common/error.mako')
def failed_validation(request):
    return {}
