# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.topic.models import Topic

class TopicChoiceForm(form.Form):
    kind = fields.SelectField(label=u"トピックの種別", choices=[(x, x) for x in Topic.TYPE_CANDIDATES])
    count_items = fields.IntegerField(label=u"表示件数", default=5, validators=[validators.Required()])
    display_global = fields.BooleanField(label=u"グローバルトピックを表示", default=True)
    display_page = fields.BooleanField(label=u"ページに関連したトピック表示", default=True)
    display_event = fields.BooleanField(label=u"イベントに関連したトピック表示", default=True)
    
