# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup
import altaircms.helpers as helpers

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

logger = logging.getLogger(__file__)

class PluginRenderer(object):
    def __init__(self, request):
        self.request = request

    def renderAnchorlistWidget(self, model):
        pass
    def renderAnchorlistWidget(self, model):
        pass
    def renderBreadcrumbsWidget(self, model):
        pass
    def renderCalendarWidget(self, model):
        pass
    def renderCountdownWidget(self, model):
        pass
    def renderDetailWidget(self, model):
        pass
    def renderFlashWidget(self, model):
        pass
    def renderFreetextWidget(self, model):
        return Markup(model.text)
    def renderHeadingWidget(self, model):
        tag = u"<h2 class='glitter orange'>{0}</h2>".format(model.text)
        return Markup(tag)
    def renderIconsetWidget(self, model):
        pass
    def renderImageWidget(self, model):
        tag = "<img {0} src='{1}' />".format(model.html_attributes, helpers.asset.rendering_object(self.request,model.asset).filepath)
        if model.href:
            tag = "<a href={0} ><img {1} src='{2}' /></a>".format(model.href, model.html_attributes, helpers.asset.rendering_object(self.request,model.asset).filepath)
        return Markup(tag)
    def renderLinklistWidget(self, model):
        pass
    def renderMenuWidget(self, model):
        pass
    def renderMovieWidget(self, model):
        pass
    def renderPerformancelistWidget(self, model):
        pass
    def renderPromotionWidget(self, model):
        pass
    def renderPurchaseWidget(self, model):
        pass
    def renderRawhtmlWidget(self, model):
        return Markup(model.text)
    def renderReuseWidget(self, model):
        pass
    def renderSummaryWidget(self, model):
        pass
    def renderTicketlistWidget(self, model):
        pass
    def renderTopcontentWidget(self, model):
        pass
    def renderTopicWidget(self, model):
        pass
    def renderTwitterWidget(self, model):
        pass

    widget_render_map = {
        AnchorlistWidget: renderAnchorlistWidget,
        BreadcrumbsWidget: renderBreadcrumbsWidget,
        CalendarWidget: renderCalendarWidget,
        CountdownWidget: renderCountdownWidget,
        DetailWidget: renderDetailWidget,
        FlashWidget: renderFlashWidget,
        FreetextWidget: renderFreetextWidget,
        HeadingWidget: renderHeadingWidget,
        IconsetWidget: renderIconsetWidget,
        ImageWidget: renderImageWidget,
        LinklistWidget: renderLinklistWidget,
        MenuWidget: renderMenuWidget,
        MovieWidget: renderMovieWidget,
        PerformancelistWidget: renderPerformancelistWidget,
        PromotionWidget: renderPromotionWidget,
        PurchaseWidget: renderPurchaseWidget,
        RawhtmlWidget: renderRawhtmlWidget,
        ReuseWidget: renderReuseWidget,
        SummaryWidget: renderSummaryWidget,
        TicketlistWidget: renderTicketlistWidget,
        TopcontentWidget: renderTopcontentWidget,
        TopicWidget: renderTopicWidget,
        TwitterWidget: renderTwitterWidget,
    }

    def render(self, widget):
        if not widget:
            return u""
        fn = self.widget_render_map[type(widget['model'])]
        return fn(self, widget['model'])
