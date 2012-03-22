# coding: utf-8
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets
import wtforms.ext.sqlalchemy.fields as extfields
from . import models

def existing_dispositions():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    return models.WidgetDisposition.query.all()

class WidgetDispositionSelectForm(form.Form):
    disposition = extfields.QuerySelectField(query_factory=existing_dispositions, allow_blank=False)

class WidgetDispositionSaveForm(form.Form):
    title = fields.TextField(validators=[validators.Required()])
    page = fields.IntegerField(widget=widgets.HiddenInput())
