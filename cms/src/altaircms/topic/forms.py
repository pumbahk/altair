# -*- coding:utf-8 -*-
import wtforms.ext.sqlalchemy.fields as extfields
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets

from .models import Topic

def existing_pages():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    from altaircms.page.models import Page
    return Page.query.filter(Page.event_id==None)

def existing_events():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    from altaircms.models import Event
    return Event.query.all()

class TopicForm(form.Form):
    title = fields.TextField(label=u"タイトル", validators=[validators.Required()])
    kind = fields.SelectField(label=u"トピックの種別", choices=[(x, x) for x in Topic.TYPE_CANDIDATES])
    is_global = fields.BooleanField(label=u"全体に公開", default=True)
    publish_open_on = fields.DateTimeField(label=u"公開開始日")
    publish_close_on = fields.DateTimeField(label=u"公開終了日")
    text = fields.TextField(label=u"内容", validators=[validators.Required()], widget=widgets.TextArea())
    
    orderno = fields.IntegerField(label=u"表示順序", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    page = extfields.QuerySelectField(
        label=u"イベント以外のページ", query_factory=existing_pages, allow_blank=True)
    event = extfields.QuerySelectField(
        label=u"イベント", query_factory=existing_events, allow_blank=True)
    
    
