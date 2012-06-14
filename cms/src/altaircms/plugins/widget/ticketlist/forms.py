# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.widgets as widgets
import wtforms.ext.sqlalchemy.fields as extfields

import wtforms.validators as validators
from . import models

from altaircms.event.models import Event
from altaircms.page.models import Page
from altaircms.models import Performance
from altaircms.models import Sale
from altaircms.seeds.saleskind import SALESKIND_CHOICES

class TicketlistChoiceForm(form.Form):
    ## todo fix
    kind = fields.SelectField(id="kind", label=u"表示するチケットの種別", choices=SALESKIND_CHOICES)
    target_performance = extfields.QuerySelectField(id="target", label=u"価格表を取得するパフォーマンス")
    caption = fields.TextFields(id="caption", label=u"価格表の見出し", widget=widgets.TextArea)
    def refine_choices(self, page_id):
        if not page_id:
            return
        qs = Sale.query.filter(Event.id==Page.event_id).filter(Page.id==page_id).filter(Event.id==Sale.event_id)
        self.kind.choices = [(s.kind, s.jkind) for s in set(qs)]

        qs = Performance.query.filter(Performance.event_id==Page.event_id)
        self.target_performance.choices = qs

    
        
