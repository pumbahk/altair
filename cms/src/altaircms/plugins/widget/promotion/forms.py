# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
from altaircms.helpers.formhelpers import dynamic_query_select_field_factory
from altaircms.plugins.api import get_widget_utility
from . import models
from altaircms.topic.models import PromotionTag

class PromotionWidgetForm(form.Form):
    tag = dynamic_query_select_field_factory(
        PromotionTag, allow_blank=False, label=u"表示場所",
        get_label=lambda obj: obj.label)
    _choices = [(x, x)for x in  models.PROMOTION_DISPATH.keys()]
    display_type = fields.SelectField(label=u"プロモーション表示の種類", id="display_type", choices=_choices)

    def configure(self, request, page):
        utility = get_widget_utility(request, page, models.PromotionWidget.type)
        self.display_type.choices = utility.choices
        return self
