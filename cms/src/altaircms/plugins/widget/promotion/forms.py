# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.helpers.formhelpers import dynamic_query_select_field_factory
from . import models
from altaircms.topic.models import Kind

class PromotionWidgetForm(form.Form):
    kind = dynamic_query_select_field_factory(
        Kind, allow_blank=False, label=u"タグ的なもの",
        get_label=lambda obj: obj.name)
    _choices = [(x, x)for x in  models.PROMOTION_DISPATH.keys()]
    display_type = fields.SelectField(label=u"プロモーション表示の種類", id="display_type", choices=_choices)

