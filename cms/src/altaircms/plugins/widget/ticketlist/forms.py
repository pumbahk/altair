# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models
from altaircms.models import Sale
from altaircms.event.models import Event
from altaircms.page.models import Page

from altaircms.seeds.saleskind import SALESKIND_CHOICES

class TicketlistChoiceForm(form.Form):
    ## todo fix
    kind = fields.SelectField(id="kind", label=u"表示するチケットの種別", choices=SALESKIND_CHOICES)
    
    def refine_kind_choices(self, page_id):
        if not page_id:
            return
        qs = Sale.query.filter(Event.id==Page.event_id).filter(Page.id==page_id).filter(Event.id==Sale.event_id)
        self.kind.choices = [(s.kind, s.jkind) for s in qs]
