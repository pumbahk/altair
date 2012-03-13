# -*- coding:utf-8 -*-
import wtforms.forms as forms
import wtforms.fields as fields
import wtforms.validators as validators

class TopicForm(forms.Form):
    event = fields.SlectField(coerce=int, label=u"イベント")
    title = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    text = fields.TextField(label=u"内容", validators=[validators.Required()])


