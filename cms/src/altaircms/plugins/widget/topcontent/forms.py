# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from .models import TopcontentWidget
from altaircms.plugins.api import get_widget_utility
from altaircms.helpers.formhelpers import dynamic_query_select_field_factory
from altaircms.topic.models import TopcontentTag

class TopcontentChoiceForm(form.Form):
    tag = dynamic_query_select_field_factory(
        TopcontentTag, allow_blank=False, label=u"分類",
        get_label=lambda obj: obj.label)
    display_type = fields.SelectField(id="display_type", label=u"表示するトピックの種類", choices=[])
    display_count = fields.IntegerField(id="display_count", label=u"表示件数", default=5, validators=[validators.Required()])

    def configure(self, request, page):
        utility = get_widget_utility(request, page, TopcontentWidget.type)
        self.display_type.choices = utility.choices
        return self
