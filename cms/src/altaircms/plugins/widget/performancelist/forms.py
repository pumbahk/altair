# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
from altaircms.plugins.api import get_widget_utility
from altaircms.plugins.widget.performancelist.models import PerformancelistWidget

class PerformancelistForm(Form):
    kind = fields.SelectField(id="kind", label=u"表示の種類", choices=[])
    mask_performance_date = fields.BooleanField(id="mask_performance_date", label=u"公演日時を表示しない")
    page_id = fields.IntegerField(id="page_id")

    def configure(self, request, page):
        utility = get_widget_utility(request, page, PerformancelistWidget.type)
        self.kind.choices = utility.choices
        return self
