# coding: utf-8
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets
from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from . import models



class WidgetDispositionSelectForm(form.Form):
    disposition = dynamic_query_select_field_factory(
        models.WidgetDisposition, 
        allow_blank=False)

class WidgetDispositionSaveForm(form.Form):
    page = fields.IntegerField(widget=widgets.HiddenInput(), validators=[validators.Required()])
    owner_id = fields.IntegerField(widget=widgets.HiddenInput())
    title = fields.TextField(label=u"保存時のwidget layout名", validators=[validators.Required()])
    is_public = fields.BooleanField(label=u"他の人に公開する")

