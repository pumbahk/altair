# -*- coding:utf-8 -*-
from altaircms.event.models import Event
from altaircms.page.models import Page
from altairsite.preview.api import set_rendered_event
from altairsite.separation import get_organization_from_request

from altaircms.plugins.widget.anchorlist.models import AnchorlistWidget
from altaircms.plugins.widget.breadcrumbs.models import BreadcrumbsWidget
from altaircms.plugins.widget.calendar.models import CalendarWidget
from altaircms.plugins.widget.countdown.models import CountdownWidget
from altaircms.plugins.widget.detail.models import DetailWidget
from altaircms.plugins.widget.flash.models import FlashWidget
from altaircms.plugins.widget.freetext.models import FreetextWidget
from altaircms.plugins.widget.heading.models import HeadingWidget
from altaircms.plugins.widget.iconset.models import IconsetWidget
from altaircms.plugins.widget.image.models import ImageWidget
from altaircms.plugins.widget.linklist.models import LinklistWidget
from altaircms.plugins.widget.menu.models import MenuWidget
from altaircms.plugins.widget.movie.models import MovieWidget
from altaircms.plugins.widget.performancelist.models import PerformancelistWidget
from altaircms.plugins.widget.promotion.models import PromotionWidget
from altaircms.plugins.widget.purchase.models import PurchaseWidget
from altaircms.plugins.widget.rawhtml.models import RawhtmlWidget
from altaircms.plugins.widget.reuse.models import ReuseWidget
from altaircms.plugins.widget.summary.models import SummaryWidget
from altaircms.plugins.widget.ticketlist.models import TicketlistWidget
from altaircms.plugins.widget.topcontent.models import TopcontentWidget
from altaircms.plugins.widget.topic.models import TopicWidget
from altaircms.plugins.widget.twitter.models import TwitterWidget

widget_models = {
    'anchorlist': AnchorlistWidget,
    'breadcrumbs':BreadcrumbsWidget,
    'calendar': CalendarWidget,
    'countdown': CountdownWidget,
    'detail': DetailWidget,
    'flash': FlashWidget,
    'freetext': FreetextWidget,
    'heading': HeadingWidget,
    'iconset': IconsetWidget,
    'image': ImageWidget,
    'linklist': LinklistWidget,
    'menu': MenuWidget,
    'movie': MovieWidget,
    'performancelist': PerformancelistWidget,
    'promotion': PromotionWidget,
    'purchase': PurchaseWidget,
    'rawhtml': RawhtmlWidget,
    'reuse': ReuseWidget,
    'summary': SummaryWidget,
    'ticketlist': TicketlistWidget,
    'topcontent': TopcontentWidget,
    'topic': TopicWidget,
    'twitter': TwitterWidget,
    }

class DetailPageResource(object):

    def __init__(self, request):
        self.request = request

    def get_event(self, id):
        event = self.request.allowable(Event).filter(Event.id==id).first()
        set_rendered_event(self.request, event)
        return event

    def get_page_published(self, event_id, dt):
        page = (self.request.allowable(Page)
                .filter(Page.event_id == event_id)
                .filter(Page.published == True)
                .filter(Page.in_term(dt))
                ).first()
        return page

    def is_dynamic_page_organization(self):
        org = get_organization_from_request(request=self.request)
        return org.short_name in ['KT', 'RL']

    def get_widget_model(self, widget, widgets):
        model = None
        if widget['name'] in widget_models:
            widget_model = widget_models[widget['name']]
            model = self.request.allowable(widget_model).filter(widget_model.id == widget['pk']).first()

        widget.update({'model': model})
        return widget

    def get_header_image(self, widgets):
        for widget in widgets:
            if widget['name'] == "image":
                return widget

    def remove_header_image(self, widgets):
        header_image = self.get_header_image(widgets)
        if header_image:
            widgets.remove(header_image)
        return widgets
