# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.widgets as widgets

from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.helpers.formhelpers import required_field
from .models import Topic
from altaircms.page.models import Page
from altaircms.event.models import Event

def existing_pages():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    ## lib.formhelpersの中で絞り込みを追加してる。
    return Page.query.filter(Page.event_id==None)

class TopicForm(form.Form):
    title = fields.TextField(label=u"タイトル", validators=[required_field()])
    kind = fields.SelectField(label=u"トピックの種別", 
                              choices=[(x, x) for x in Topic.KIND_CANDIDATES],
                              validators=[required_field()])
    subkind = fields.TextField(label=u"サブ分類")
    is_global = fields.BooleanField(label=u"全体に公開", default=True)
    publish_open_on = fields.DateTimeField(label=u"公開開始日", validators=[required_field()])
    publish_close_on = fields.DateTimeField(label=u"公開終了日", validators=[required_field()])
    text = fields.TextField(label=u"内容", validators=[required_field()], widget=widgets.TextArea())
    
    orderno = fields.IntegerField(label=u"表示順序(1〜100)", default=50)
    is_vetoed = fields.BooleanField(label=u"公開禁止")

    page = dynamic_query_select_field_factory(Page, 
                                              label=u"イベント以外のページ",
                                              query_factory=existing_pages, 
                                              allow_blank=True, 
                                              get_label=lambda obj: obj.title or u"名前なし")
    event = dynamic_query_select_field_factory(Event, 
                                               label=u"イベント",
                                               allow_blank=True, 
                                               get_label=lambda obj: obj.title or u"名前なし")
    
    
