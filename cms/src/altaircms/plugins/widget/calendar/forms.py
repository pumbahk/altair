# -*- coding:utf-8 -*-

from wtforms.form import Form
from wtforms import fields
from altaircms.helpers.formhelpers import dynamic_query_select_field_factory
from altaircms.models import Sale
from altaircms.page.models import Page
from altaircms.event.models import Event

def selected_sale(model, request, qs):
    qs = qs.filter(Sale.event_id==Event.id).filter(Event.organization_id==request.organization.id)
    return qs.filter(Event.id==Page.id).filter(Page.id==request["page"])
    
class CalendarSelectForm(Form):
    CHOICES = [("obi", u"帯（縦長)"), ("tab", u"タブ"),]
    calendar_type = fields.SelectField(id="calendar_type", 
                                       label=u"カレンダーの種類", 
                                       choices=CHOICES,
                                       default="this_month")
    sale_choice = dynamic_query_select_field_factory(Sale, 
                                                     id="sale_choice", 
                                                     allow_blank=True,
                                                     blank_text=u"すべて", 
                                                     label=u"イベント販売条件", 
                                                     dynamic_query=selected_sale, 
                                                     get_label=lambda obj: u"%s (%s〜%s)" % (obj.name, obj.start_on, obj.end_on))

class SelectTermForm(Form):
    from_date = fields.DateField(u"開始")
    to_date = fields.DateField(u"終了")

    
