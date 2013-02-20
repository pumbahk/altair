# -*- coding:utf-8 -*-

from altaircms.formhelpers import Form
from wtforms import fields
from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.plugins.api import get_widget_utility
from altaircms.models import SalesSegment
from altaircms.page.models import Page
from altaircms.event.models import Event
from altaircms.auth.api import fetch_correct_organization
from . models import CalendarWidget

def selected_sale(model, request, qs):
    qs = qs.filter(SalesSegment.event_id==Event.id).filter(Event.organization_id==fetch_correct_organization(request).id)
    qs = qs.filter(Event.id==Page.event_id).filter(Page.id==request.GET["page"])
    return qs
    
class CalendarSelectForm(Form):
    calendar_type = fields.SelectField(id="calendar_type", 
                                       label=u"カレンダーの種類", 
                                       choices=[],
                                       default="this_month")
    sale_choice = dynamic_query_select_field_factory(SalesSegment, 
                                                     id="sale_choice", 
                                                     allow_blank=True,
                                                     blank_text=u"すべて", 
                                                     label=u"イベント販売条件", 
                                                     dynamic_query=selected_sale, 
                                                     get_label=lambda obj: u"%s (%s〜%s)" % (obj.name, obj.start_on, obj.end_on))
    def configure(self, request, page):
        utility = get_widget_utility(request, page, CalendarWidget.type)
        self.calendar_type.choices = utility.choices

class SelectTermForm(Form):
    from_date = fields.DateField(u"開始")
    to_date = fields.DateField(u"終了")

    
