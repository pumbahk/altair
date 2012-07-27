# -*- coding:utf-8 -*-
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.helpers.formhelpers import dynamic_query_select_field_factory
from . import models

class FreetextBodyForm(Form):
    name = fields.TextField(u'タイトル', validators=[validators.Required()])
    text = fields.TextField(u'定型文', validators=[validators.Required()], widget=widgets.TextArea(), id="text")
    __display_fields__ = ["name", "text"]

class FreeTextChoiceForm(Form):
    default_text = dynamic_query_select_field_factory(
        models.FreetextDefaultBody, allow_blank=False, 
        id = "freetext_default_choices", 
        label=u"保存された定型文",
        get_label=lambda obj: obj.name)
