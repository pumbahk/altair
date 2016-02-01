# -*- coding:utf-8 -*-
import json
from .forms import DetailForm
from ..common.helper import SmartPhoneHelper
from ..common.renderer import PluginRenderer
from ..common.utils import SnsUtils
from altaircms.plugins.extra.api import get_stockstatus_summary
from altaircms.plugins.extra.stockstatus import StockStatus
from altaircms.event.event_info import get_event_notify_info
from altairsite.config import smartphone_site_view_config
from altairsite.mobile.core.helper import get_performances_month_unit, get_purchase_links \
    , get_tickets, get_sales_date
from altairsite.exceptions import UsersiteException
from altairsite.separation import selectable_renderer
from altair.now import get_now 

def enable_dynamic_page(context, request):
    return context.is_dynamic_page_organization()

class ValidationFailure(UsersiteException):
    pass

@smartphone_site_view_config(route_name='smartphone.detail',request_type="altair.mobile.interfaces.ISmartphoneRequest"
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/detail/detail.html'))
def moveDetail(context, request):
    form = DetailForm(request.GET)
    event = context.get_event(form.data['event_id'])
    now = get_now(request)
    page_published = context.get_page_published(form.data['event_id'], now)
    if not event or not page_published:
        raise ValidationFailure

    purchase_links = get_purchase_links(request=request, event=event)
    month_unit = get_performances_month_unit(event=event)
    keys = month_unit.keys()
    keys.sort()
    month_unit_keys = keys
    tickets = get_tickets(request=request, event=event)
    sales_start, sales_end = get_sales_date(request=request, event=event)
    event_info = get_event_notify_info(event=event, page=page_published)
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

@smartphone_site_view_config(route_name='smartphone.detail',request_type="altair.mobile.interfaces.ISmartphoneRequest"
             , custom_predicates=(enable_dynamic_page, ), renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/detail/detail.html'))
def moveImageDetail(context, request):
    form = DetailForm(request.GET)
    event = context.get_event(form.data['event_id'])
    now = get_now(request)
    page_published = context.get_page_published(form.data['event_id'], now)
    if not event or not page_published:
        raise ValidationFailure

    #TODO pagesetsとpageを一対一と仮定することで特定している
    structures = json.loads(page_published.structure).items()
    widgets = []
    for structure in structures:
        for widget in structure[1]:
            wg = context.get_widget_model(widget, widgets)
            if widget['pk']:
                widgets.append(wg)

    header_image = context.get_header_image(widgets)
    widgets = context.remove_header_image(widgets)

    purchase_links = get_purchase_links(request=request, event=event)
    month_unit = get_performances_month_unit(event=event)
    keys = month_unit.keys()
    keys.sort()
    month_unit_keys = keys
    tickets = get_tickets(request=request, event=event)
    sales_start, sales_end = get_sales_date(request=request, event=event)
    event_info = get_event_notify_info(event=event, page=page_published)
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
        , 'renderer': PluginRenderer(request=request)
        , 'header_image': header_image
        , 'widgets': widgets
        , 'sns':{
            'url':utils.get_sns_url(event_id=event.id),
            'title':utils.get_sns_title(event_id=event.id)
        }
    }

@smartphone_site_view_config(route_name='smartphone.detail', context=ValidationFailure
    , request_type="altair.mobile.interfaces.ISmartphoneRequest", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/common/error.html'))
def failed_validation(request):
    return {}
