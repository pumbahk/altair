# -*- coding:utf-8 -*-
from .forms import DetailForm
from ..common.helper import SmartPhoneHelper
from ..common.utils import SnsUtils
from altaircms.plugins.extra.api import get_stockstatus_summary
from altaircms.plugins.extra.stockstatus import StockStatus
from altaircms.event.event_info import get_event_notify_info
from altairsite.config import smartphone_site_view_config
from altairsite.mobile.core.helper import get_performances_month_unit, get_purchase_links \
    , get_tickets, get_sales_date
from altairsite.exceptions import UsersiteException

class ValidationFailure(UsersiteException):
    pass
from altairsite.front.cache import with_smartphone_cache
@smartphone_site_view_config(route_name='smartphone.detail',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/detail/detail.html'
             , decorator=with_smartphone_cache)
def moveDetail(context, request):
    form = DetailForm(request.GET)
    event = context.get_event(form.data['event_id'])
    if not event:
        raise ValidationFailure

    purchase_links = get_purchase_links(request=request, event=event)
    month_unit = get_performances_month_unit(event=event)
    keys = month_unit.keys()
    keys.sort()
    month_unit_keys = keys
    tickets = get_tickets(request=request, event=event)
    sales_start, sales_end = get_sales_date(request=request, event=event)
    event_info = get_event_notify_info(event=event)
    utils = SnsUtils(request=request)
    stock_status = get_stockstatus_summary(request=request, event=event, status_impl=StockStatus)

    return {
          'event': event
        , 'purchase_links': purchase_links
        , 'month_unit_keys': month_unit_keys
        , 'tickets': tickets
        , 'sales_start': sales_start
        , 'sales_end': sales_end
        , 'event_info': event_info
        , 'stock_status': stock_status
        , 'helper': SmartPhoneHelper()
        , 'sns':{
            'url':utils.get_sns_url(event_id=event.id),
            'title':utils.get_sns_title(event_id=event.id)
        }
    }

@smartphone_site_view_config(route_name='smartphone.detail', context=ValidationFailure
    , request_type="altairsite.tweens.ISmartphoneRequest", renderer='altairsite.smartphone:templates/common/error.html')
def failed_validation(request):
    return {}
