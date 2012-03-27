# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class CountdownChoiceForm(form.Form):
    kind = fields.SelectField(id="kind", label=u"期限日の種別", choices=models.CountdownWidget.KIND_MAPPING.items())
    
