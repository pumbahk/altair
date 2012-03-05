import sqlalchemy as sa
from zope.interface import implements

from altaircms.interfaces import IWidget
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.security import RootFactory


from pyramid.renderers import render

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

    def merge_settings(self, bname, bsettings):
        # ctx = {"widget": self}
        # bsettings.add(bname, render())
        bsettings.add(bname, "text:%s" % self.id)

class FreetextWidgetResource(HandleSessionMixin, 
                             UpdateDataMixin, 
                             HandleWidgetMixin, 
                             RootFactory):
    WidgetClass = FreetextWidget
