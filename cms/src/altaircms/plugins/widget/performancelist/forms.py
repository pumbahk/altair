# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
from . import models

class PerformancelistForm(Form):
    _choices = models.PERFORMANCELIST_KIND_CHOICES
    kind = fields.SelectField(id="kind", label=u"表示の種類", choices=_choices)
    mask_performance_date = fields.BooleanField(id="mask_performance_date", label=u"公演日時を表示しない")
    page_id = fields.IntegerField(id="page_id")
