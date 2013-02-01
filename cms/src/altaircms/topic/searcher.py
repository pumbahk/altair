import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.page.models import Page, PageSet
from .models import PromotionTag

class PromotionPageListSearcher(object):
    def __init__(self, request, finder):
        self.request = request 
        self.finder = finder

    def get_objects_for_grid(self, qs):
        qs = qs.filter(PageSet.id==Page.pageset_id).filter(self.finder.widget.kind_id==PromotionTag.id)
        qs = qs.with_entities(PageSet, Page, self.finder.widget, PromotionTag)
        qs = qs.options(orm.joinedload(Page.pageset)).order_by(sa.asc(PageSet.id), sa.asc(Page.id))
        return qs


class PromotionPageDetailSearcher(object):
    def __init__(self, request, finder):
        self.request = request 
        self.finder = finder

    def get_widgets(self, page_id):
        return self.finder.widget.query.filter_by(page_id=page_id)

    def get_current_widget(self, widgets, widget_id=None):
        if widget_id:
            return widgets.filter(self.finder.widget.id==widget_id).first()
        return widgets.first()
