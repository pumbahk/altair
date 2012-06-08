# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models
from altaircms.seeds.saleskind import SALESKIND_CHOICES

class TicketlistChoiceForm(form.Form):
    ## todo fix
    kind = fields.SelectField(id="kind", label=u"表示するチケットの種別", choices=SALESKIND_CHOICES)
    
