# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.mobile.core.helper import get_week_map, get_performances_month_unit, get_purchase_links \
    , get_tickets, exist_value, get_sales_date
from altairsite.smartphone.event.search.forms import SearchForm
from .forms import DetailForm

@usersite_view_config(route_name='detail',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/detail/detail.html')
def moveDetail(context, request):
    form = DetailForm(request.GET)
    event = context.get_event(form.data['event_id'])
    purchase_links = get_purchase_links(request=request, event=event)
    month_unit = get_performances_month_unit(event=event)
    keys = month_unit.keys()
    keys.sort()
    month_unit_keys = keys
    tickets = get_tickets(request=request, event=event)
    sales_start, sales_end = get_sales_date(request=request, event=event)

    return {
          'event': event
        , 'purchase_links': purchase_links
        , 'month_unit_keys': month_unit_keys
        , 'tickets': tickets
        , 'sales_start': sales_start
        , 'sales_end': sales_end
        , 'helper': SmartPhoneHelper()
    }
