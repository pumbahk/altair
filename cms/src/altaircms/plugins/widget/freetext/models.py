from altaircms.interfaces import IWidget
from zope.interface import implements
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import HandleSessionMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin

import sqlalchemy as sa

class FreetextWidget(Widget):
    implements(IWidget)
    type = "freetext"

    template_name = "altaircms.plugins.widget:freetext/render.mako"    
    __tablename__ = "widget_text"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    text = sa.Column(sa.Unicode)

    def __init__(self, id=None, text=None):
        self.id = id
        self.text = text

class FreetextWidgetResource(HandleSessionMixin, 
                             UpdateDataMixin, 
                             HandleWidgetMixin):
    WidgetClass = FreetextWidget
    def __init__(self, request):
        self.request = request
