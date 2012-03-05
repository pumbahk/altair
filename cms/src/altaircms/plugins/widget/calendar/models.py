from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from . import renderable
import os
here = os.path.abspath(os.path.dirname(__file__))

class CalendarWidget(Widget):
    implements(IWidget)
    type = "calendar"

    __tablename__ = "widget_calendar"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    calendar_type = sa.Column(sa.String(255))
    from_date = sa.Column(sa.Date)
    to_date = sa.Column(sa.Date)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("performances")
        bsettings.need_extra_in_scan("request")

        def block_render():
            performances = bsettings.extra["performances"]
            request = bsettings.extra["request"]
            render_fn = getattr(renderable, self.calendar_type)
            return render_fn(self, performances, request)
        bsettings.add(bname, block_render)

class CalendarWidgetResource(HandleSessionMixin,
                             UpdateDataMixin,
                             HandleWidgetMixin, 
                             RootFactory):
    WidgetClass = CalendarWidget

    def attach_form_from_widget(self, D, widget):
        form = D["form_class"](**widget.to_dict())
        D["form"] = form
        return D

    def get_widget(self, widget_id):
        return self._get_or_create(CalendarWidget, widget_id)
