# -*- coding:utf-8 -*-
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
from altaircms.plugins.base.interception import not_support_if_keyerror
from altaircms.plugins.api import get_widget_utility
from . import api

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
    salessegment_id = sa.Column(sa.Integer, sa.ForeignKey("sale.id"))
    salessegment = orm.relationship("Sale")

    def display_all_bool(self):
        return self.salessegment_id is None


    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("performances")
        bsettings.need_extra_in_scan("event")
        bsettings.need_extra_in_scan("page")
        bsettings.need_extra_in_scan("request")

        @not_support_if_keyerror("calendar widget: %(err)s")
        def calendar_render():
            ## todo あとで整理
            performances = bsettings.extra["performances"]
            event = bsettings.extra["event"]
            page = bsettings.extra["page"]
            request = bsettings.extra["request"]

            utility = get_widget_utility(request, page, self.type)

            status_impl = utility.status_impl
            calendar_status = api.get_performance_status(request, self, event, status_impl)

            template_name = utility.get_template_name(request, self)
            render_fn = utility.get_rendering_function(request, self)
            return render_fn(self, calendar_status, performances, request, template_name=template_name)
        bsettings.add(bname, calendar_render)
        self._if_tab_add_js_script(bsettings)

    def _if_tab_add_js_script(self, bsettings):
        if self.calendar_type != "tab":
            return
        ## jsを追加(一回だけ)
        if not bsettings.is_attached(self, "js_postrender"):
            def js():
                return TAB_CALENDAR_JS
            bsettings.add("js_postrender", js)
            bsettings.attach_widget(self, "js_postrender")


class CalendarWidgetResource(HandleSessionMixin,
                             UpdateDataMixin,
                             HandleWidgetMixin, 
                             RootFactory):
    WidgetClass = CalendarWidget

    def get_widget(self, widget_id):
        return self._get_or_create(CalendarWidget, widget_id)

TAB_CALENDAR_JS = u"""\
/* calendar tab widget*/
  $(".calendar-tab").click(function(){
    var selected = $(".calendar-tab.selected");
    $("#calendar_"+selected.attr("month")).addClass("hidden");
    selected.removeClass("selected");

    var new_selected = $(this);
    new_selected.addClass("selected");
    $("#calendar_"+new_selected.attr("month")).removeClass("hidden");
  });
"""
