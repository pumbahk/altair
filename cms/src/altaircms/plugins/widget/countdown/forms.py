# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class CountdownChoiceForm(Form):
    kind = fields.SelectField(id="kind", label=u"期限日の種別", choices=models.CountdownWidget.KIND_MAPPING.items())
    
