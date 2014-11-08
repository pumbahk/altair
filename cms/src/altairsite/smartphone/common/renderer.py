# -*- coding: utf-8 -*-
import logging

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
    def renderAnchorlistWidget(self):
        pass
    def renderAnchorlistWidget(self):
        pass
    def renderBreadcrumbsWidget(self):
        pass
    def renderCalendarWidget(self):
        pass
    def renderCountdownWidget(self):
        pass
    def renderDetailWidget(self):
        pass
    def renderFlashWidget(self):
        pass
    def renderFreetextWidget(self):
        pass
    def renderHeadingWidget(self):
        pass
    def renderIconsetWidget(self):
        pass
    def renderImageWidget(self):
        pass
    def renderLinklistWidget(self):
        pass
    def renderMenuWidget(self):
        pass
    def renderMovieWidget(self):
        pass
    def renderPerformancelistWidget(self):
        pass
    def renderPromotionWidget(self):
        pass
    def renderPurchaseWidget(self):
        pass
    def renderRawhtmlWidget(self):
        pass
    def renderReuseWidget(self):
        pass
    def renderSummaryWidget(self):
        pass
    def renderTicketlistWidget(self):
        pass
    def renderTopcontentWidget(self):
        pass
    def renderTopicWidget(self):
        pass
    def renderTwitterWidget(self):
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
        fn = self.widget_render_map[widget['model']]

