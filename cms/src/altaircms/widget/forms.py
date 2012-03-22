# coding: utf-8
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets
import wtforms.ext.sqlalchemy.fields as extfields
from . import models

# def existing_dispositions():
#     ##本当は、client.id, site.idでfilteringする必要がある
#     ##本当は、日付などでfilteringする必要がある
#     return models.WidgetDisposition.query.all()

class WidgetDispositionSelectForm(form.Form):
    disposition = extfields.QuerySelectField(allow_blank=False)
    
    @classmethod
    def from_operator(cls, operator):
        form = cls()
        form.disposition.query = models.WidgetDisposition.enable_only_query(operator)
        return form

class WidgetDispositionSaveForm(form.Form):
    page = fields.IntegerField(widget=widgets.HiddenInput())
    title = fields.TextField(label=u"保存時のwidget layout名", validators=[validators.Required()])
    is_public = fields.BooleanField(label=u"他の人に公開する")
