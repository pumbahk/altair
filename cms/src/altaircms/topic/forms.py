# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets
import wtforms.ext.sqlalchemy.fields as extfields

from altaircms.models import Event
def _existing_events():
    ## 本当はclient.id, site.idでfilterlingする必要がある
    return Event.query.all()

class TopicForm(form.Form):
    # event = fields.SelectField(coerce=int, label=u"イベント")
    event = extfields.QuerySelectField(query_factory=_existing_events, allow_blank=True, label=u"イベント")
    title = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    text = fields.TextField(label=u"内容", validators=[validators.Required()], widget=widgets.TextArea())


