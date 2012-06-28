# coding: utf-8
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets
from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from . import models


def disposition_query_filter(model, request, query):
    if getattr(request, "site", None):
        query = query.filter_by(site_id=request.site.id)
    return model.enable_only_query(request.user, qs=query)

class WidgetDispositionSelectForm(form.Form):
    disposition = dynamic_query_select_field_factory(
        models.WidgetDisposition, 
        dynamic_query=disposition_query_filter, 
        allow_blank=False)

class WidgetDispositionSaveForm(form.Form):
    page = fields.IntegerField(widget=widgets.HiddenInput(), validators=[validators.Required()])
    owner_id = fields.IntegerField(widget=widgets.HiddenInput())
    title = fields.TextField(label=u"保存時のwidget layout名", validators=[validators.Required()])
    is_public = fields.BooleanField(label=u"他の人に公開する")
