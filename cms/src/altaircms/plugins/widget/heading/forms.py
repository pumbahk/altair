# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class HeadingForm(Form):
    _choices = []
    kind = fields.SelectField(id="kind", label=u"見出しの種類", choices=_choices)
    text = fields.TextField(id="widget_text", label=u"内容")
