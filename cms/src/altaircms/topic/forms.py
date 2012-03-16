# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets

from .models import Topic


class TopicForm(form.Form):
    title = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    kind = fields.SelectField(label=u"トピックの種別", choices=[(x, x) for x in Topic.TYPE_CANDIDATES])
    publish_at = fields.DateTimeField(label=u"公開日")
    text = fields.TextField(label=u"内容", validators=[validators.Required()], widget=widgets.TextArea())
