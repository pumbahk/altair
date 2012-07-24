import sqlalchemy as sa
from zope.interface import implements
from datetime import datetime

from altaircms.interfaces import IWidget
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.security import RootFactory

from altaircms.auth.models import WithOrganizationMixin
from altaircms.models import Base
from pyramid.renderers import render

class FreetextDefaultBody(WithOrganizationMixin, 
                          Base):
    query = DBSession.query_property()
    __tablename__ = "freetext_default"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.UnicodeText)

    created_by_id = sa.Column(sa.Integer)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

class FreetextWidget(Widget):
    implements(IWidget)
    type = "freetext"

    template_name = "altaircms.plugins.widget:freetext/render.mako"    
    __tablename__ = "widget_text"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    text = sa.Column(sa.UnicodeText)

    def __init__(self, id=None, text=None):
        self.id = id
        self.text = text

    def merge_settings(self, bname, bsettings):
        # bsettings.need_extra_in_scan("request")
        content = render(self.template_name, {"widget": self})
        bsettings.add(bname, content)

class FreetextWidgetResource(HandleSessionMixin, 
                             UpdateDataMixin, 
                             HandleWidgetMixin, 
                             RootFactory):
    WidgetClass = FreetextWidget
