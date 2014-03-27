# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from altaircms.formhelpers import Form
from altaircms.formhelpers import MaybeSelectField
from .models import TicketlistWidget
import wtforms.fields as fields
import wtforms.widgets as widgets
from altaircms.plugins.api import get_widget_utility
# from altaircms.formhelpers import dynamic_query_select_field_factory
import wtforms.validators as validators
from altaircms.models import Performance
from altaircms.models import SalesSegment
from altaircms.helpers.event import performance_name

_None = "_None"
class TicketlistChoiceForm(Form):
    display_type = fields.SelectField(id="display_type", label=u"価格表の表示方法", choices=[], coerce=unicode)
    target_performance_id = MaybeSelectField(
        id="target_performance_id", 
        label=u"価格表を取得するパフォーマンス", 
        blank_text=u"(指定なし)", 
        choices=[]
        )
    target_salessegment_id = MaybeSelectField(
        id="target_salessegment_id", 
        label=u"価格表を取得する商品", 
        blank_text=u"(指定なし)", 
        choices=[]
        )
    caption = fields.TextField(id="caption", label=u"価格表の説明", widget=widgets.TextArea())
    show_label = fields.BooleanField(id="show_label", label=u"見出しを表示する？", default=True)
    show_seattype = fields.BooleanField(id="show_seattype", label=u"席種の表示", default=False)

    def configure(self, request, page):
        if page.event_id:
            ps = Performance.query.filter(Performance.event_id==page.event_id).all()
            if ps:
                self.target_performance_id.choices = [(p.id, performance_name(p)) for p in ps]
            
                performance_id = self.data.get("target_performance_id")
                if performance_id:
                    ss = SalesSegment.query.filter(SalesSegment.performance_id==performance_id).options(orm.joinedload(SalesSegment.group)).all()
                    if ss:
                        self.target_salessegment_id.choices =  [(s.id, s.group.name) for s in ss]
        utility = get_widget_utility(request, page, TicketlistWidget.type)
        self.display_type.choices = utility.choices


class TicketChoiceForm(Form):
    display_type = fields.SelectField(id="display_type", label=u"価格表の表示方法", choices=[], coerce=unicode)
    target_salessegment_id = MaybeSelectField(
        id="target_salessegment_id", 
        label=u"価格表を取得する商品", 
        blank_text=u"(指定なし)", 
        choices=[]
        )
    def configure(self, request):
        performance_id = request.params.get("target_performance_id")
        ss = SalesSegment.query.filter(SalesSegment.performance_id==performance_id).options(orm.joinedload(SalesSegment.group)).all()
        self.target_salessegment_id.choices =  [(s.id, s.group.name) for s in ss]
        
