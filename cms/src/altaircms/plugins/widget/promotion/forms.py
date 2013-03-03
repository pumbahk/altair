# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.plugins.api import get_widget_utility
from . import models
from altaircms.topic.models import PromotionTag

class PromotionWidgetForm(Form):
    tag = dynamic_query_select_field_factory(
        PromotionTag, allow_blank=False, label=u"表示場所",
        get_label=lambda obj: obj.label)
    system_tag = dynamic_query_select_field_factory(
        PromotionTag, allow_blank=True, label=u"ジャンル",
        dynamic_query=lambda model, request, query: query.filter_by(organization_id=None), 
        get_label=lambda obj: obj.label)
    display_type = fields.SelectField(label=u"プロモーション表示の種類", id="display_type", choices=[])

    def configure(self, request, page):
        utility = get_widget_utility(request, page, models.PromotionWidget.type)
        self.display_type.choices = utility.choices
        return self
