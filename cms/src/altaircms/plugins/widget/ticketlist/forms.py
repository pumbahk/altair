# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.widgets as widgets
from altaircms.formhelpers import dynamic_query_select_field_factory
import wtforms.validators as validators
from altaircms.models import Performance
from altaircms.models import SalesSegment
from altaircms.helpers.event import performance_name

class TicketlistChoiceForm(Form):
    display_type = fields.SelectField(id="display_type", label=u"価格表の表示方法", choices=[])
    target_performance = dynamic_query_select_field_factory(
        Performance, 
        id="target_performance", 
        label=u"価格表を取得するパフォーマンス", 
        dynamic_query=lambda model, request, query: query.filter(Performance.event_id==request.event_id), 
        get_label= performance_name)
    target_salessegment = dynamic_query_select_field_factory(
        SalesSegment, 
        allow_blank=True, 
        blank_text=u"(指定なし)", 
        id="target_salessegment", 
        label=u"価格表を取得する販売区分", 
        dynamic_query=lambda model, request, query: query.filter(model.performance_id==Performance.id, Performance.event_id==request.event_id).options(orm.joinedload(SalesSegment.group)), 
        get_label= lambda obj: obj.group.name)
    caption = fields.TextField(id="caption", label=u"価格表の見出し", widget=widgets.TextArea())
