from markupsafe import Markup
from altaircms.asset.viewhelpers import image_asset_layout
from ..rowspanlib import RowSpanGrid
from altaircms.helpers.link import get_link_from_topic
from altaircms.helpers.link import get_link_from_topic_in_cms
from altaircms.helpers.link import get_link_from_topcontent
from altaircms.helpers.link import get_link_from_topcontent_in_cms
from altaircms.helpers.link import get_link_from_promotion
from altaircms.helpers.link import get_link_from_promotion_in_cms
from altaircms.helpers.asset import rendering_object as rendering_asset

## grid
# data = (pageset, page, promotion widget)
def pageset_for_grid(data, k, changed):
    if changed:
        return data[0]
def page_for_grid(data, k, changed):
    if changed:
        return data[1]
def widget_for_grid(data, k, changed):
    return data[2]
def tag_for_grid(data, k, changed):
    return data[3]

# (pageset, page, widget, tag)
TopicGrid = RowSpanGrid()
TopicGrid.register("pageset", mapping=pageset_for_grid, keyfn=lambda data : data[0].id)
TopicGrid.register("page", mapping=page_for_grid, keyfn=lambda data : data[1].id)
TopicGrid.register("widget", mapping=widget_for_grid, keyfn=lambda data : data[2].id)
TopicGrid.register("tag", mapping=tag_for_grid, keyfn=lambda data : data[3].id)


TopcontentGrid = RowSpanGrid()
TopcontentGrid.register("pageset", mapping=pageset_for_grid, keyfn=lambda data : data[0].id)
TopcontentGrid.register("page", mapping=page_for_grid, keyfn=lambda data : data[1].id)
TopcontentGrid.register("widget", mapping=widget_for_grid, keyfn=lambda data : data[2].id)
TopcontentGrid.register("tag", mapping=tag_for_grid, keyfn=lambda data : data[3].id)

PromotionGrid = RowSpanGrid()
PromotionGrid.register("pageset", mapping=pageset_for_grid, keyfn=lambda data : data[0].id)
PromotionGrid.register("page", mapping=page_for_grid, keyfn=lambda data : data[1].id)
PromotionGrid.register("widget", mapping=widget_for_grid, keyfn=lambda data : data[2].id)
PromotionGrid.register("tag", mapping=tag_for_grid, keyfn=lambda data : data[3].id)


def _render_image(request, asset, href=None):
    return image_asset_layout(request, asset, href=href, 
                              width="", height="")

def _render_genre(topic):
    return Markup(u' '.join(u'<span class="label">%s</span>' % k.label for k in topic.topic_genres))

def _render_kind(topic):
    return Markup(u' '.join(u'<span class="label">%s</span>' % k.label for k in topic.topic_kinds))

def _render_link(href):
    return Markup(u'<a href="%s">%s</a>' % (href, href))    

class PromotionHTMLRenderer(object):
    def __init__(self, request):
        self.request = request

    def render_main_image(self, promotion):
        asset = promotion.main_image
        return _render_image(self.request, asset)

    def render_thumbnail_image(self, promotion):
        asset = promotion.main_image
        return _render_image(self.request, asset, href=rendering_asset(self.request, asset).thumbnail_path)

    def render_link(self, promotion):
        return _render_link(get_link_from_promotion(self.request, promotion))

    def render_cms_link(self, promotion):
        return _render_link(get_link_from_promotion_in_cms(self.request, promotion))
        
    def render_genre(self, topic):
        return _render_genre(topic)

    def render_kind(self, topic):
        return _render_kind(topic)

class TopcontentHTMLRenderer(object):
    def __init__(self, request):
        self.request = request

    def render_countdown_type(self, topcontent): ## todo: if each organization has individual countdown type. set via .ini
        return topcontent.COUNTDOWN_TYPE_MAPPING.get(topcontent.countdown_type, "????")

    def render_pc_image(self, topcontent):
        asset = topcontent.image_asset
        return _render_image(self.request, asset)

    def render_mobile_image(self, topcontent):
        asset = topcontent.mobile_image_asset
        return _render_image(self.request, asset)

    def render_cms_link(self, topcontent):
        return _render_link(get_link_from_topcontent_in_cms(self.request, topcontent))

    def render_genre(self, topic):
        return _render_genre(topic)

    def render_kind(self, topic):
        return _render_kind(topic)

class TopicHTMLRenderer(object):
    def __init__(self, request):
        self.request = request

    def render_cms_link(self, topic):
        return _render_link(get_link_from_topic_in_cms(self.request, topic))

    def render_genre(self, topic):
        return _render_genre(topic)

    def render_kind(self, topic):
        return _render_kind(topic)
