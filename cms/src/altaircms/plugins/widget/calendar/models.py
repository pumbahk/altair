from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base import HandleSessionMixin
from altaircms.plugins.base import UpdateDataMixin

class CalendarWidget(Widget):
    implements(IWidget)
    type = "calendar"

    template_name = "altaircms.plugins.widget:calendar/render.mako"
    __tablename__ = "widget_calendar"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id


class CalendarWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          ):
    WidgetClass = CalendarWidget

    def __init__(self, request):
        self.request = request

